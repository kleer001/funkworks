bl_info = {
    "name": "All Edge Overlays",
    "author": "Funkworks",
    "version": (0, 1, 0),
    "blender": (4, 2, 0),
    "location": "View3D > Sidebar > View > Edge Overlays",
    "description": "Show Crease, Bevel Weight, Seam and Sharp edge marks at once, "
                   "each with its own colour and dash pattern",
    "category": "3D View",
}

import bpy
import bmesh
import gpu
from bpy.app.handlers import persistent
from bpy_extras import view3d_utils
from gpu_extras.batch import batch_for_shader
from mathutils import Vector

# Each channel: settings key, label, whether it carries a 0..1 value (for fade),
# colourblind-safe default colour (Okabe-Ito), dash pattern in screen pixels
# (alternating on/off), and a fixed slot index that sets the parallel offset order.
CHANNELS = [
    {"key": "crease", "label": "Crease",       "value": True,
     "color": (0.80, 0.47, 0.65), "dash": [18, 10],     "slot": 0},
    {"key": "bevel",  "label": "Bevel Weight", "value": True,
     "color": (0.34, 0.71, 0.91), "dash": [9, 9],       "slot": 1},
    {"key": "seam",   "label": "Seam",         "value": False,
     "color": (0.84, 0.37, 0.00), "dash": [2, 7],       "slot": 2},
    {"key": "sharp",  "label": "Sharp",         "value": False,
     "color": (0.00, 0.62, 0.45), "dash": [14, 5, 2, 5], "slot": 3},
]
_BY_KEY = {c["key"]: c for c in CHANNELS}

# Theme attribute on ThemeView3D that holds each mark's native colour, for the
# "Blender Native" palette preset. Verified attribute names on 4.2 LTS.
_NATIVE_THEME_ATTR = {
    "crease": "edge_crease",
    "bevel":  "edge_bevel",
    "seam":   "edge_seam",
    "sharp":  "edge_sharp",
}

# Auto-tier thresholds on total marked-edge count, against a 16 ms (60 fps) frame
# budget. Measured live on a marked grid at this build: the screen-accurate path
# (_balanced_points, per-segment unproject) costs ~0.020 ms/marked-edge, so ~500
# marked edges spends ~10 ms — the AUTO cutover to the cheaper _fast_points path,
# which costs ~0.0047 ms/marked-edge (good to ~2500 marked edges before it too
# exceeds budget). ACCURATE and BALANCED currently share _balanced_points, so AUTO
# uses the accurate path at/below the cutover and Fast above it; BALANCED is a
# manual alias until the GPU-dashing Accurate backend lands and lifts its ceiling.
_TIER_ACCURATE_MAX = 500
_TIER_BALANCED_MAX = 500

_shader = None    # builtin POLYLINE_FLAT_COLOR, compiled lazily (needs a GPU context)
_handle = None    # draw-handler reference
_cache = {}       # obj.name -> list[(key, local_v0, local_v1, value)] for non-edit objects


# --- mark reading (local space, cached) -------------------------------------

def _read_marks_object(obj):
    """List (key, local_v0, local_v1, value) for every marked edge, object mode.

    Crease and Bevel Weight live as lazy EDGE-domain float attributes (4.0+);
    Seam and Sharp are booleans on MeshEdge. Missing attribute == nothing marked.
    Coordinates are LOCAL — the draw step multiplies by matrix_world per frame so
    object transforms never invalidate the cache.
    """
    me = obj.data
    verts = me.vertices
    crease = me.attributes.get("crease_edge")
    bevel = me.attributes.get("bevel_weight_edge")
    out = []
    for i, edge in enumerate(me.edges):
        a, b = edge.vertices
        va = verts[a].co.copy()
        vb = verts[b].co.copy()
        cv = crease.data[i].value if crease else 0.0
        if cv > 0.0:
            out.append(("crease", va, vb, cv))
        bv = bevel.data[i].value if bevel else 0.0
        if bv > 0.0:
            out.append(("bevel", va, vb, bv))
        if edge.use_seam:
            out.append(("seam", va, vb, 1.0))
        if edge.use_edge_sharp:
            out.append(("sharp", va, vb, 1.0))
    return out


def _read_marks_edit(obj):
    """Same as above but read live from the edit bmesh (never cached)."""
    me = obj.data
    bm = bmesh.from_edit_mesh(me)
    crease = bm.edges.layers.float.get("crease_edge")
    bevel = bm.edges.layers.float.get("bevel_weight_edge")
    out = []
    for edge in bm.edges:
        va = edge.verts[0].co.copy()
        vb = edge.verts[1].co.copy()
        cv = edge[crease] if crease else 0.0
        if cv > 0.0:
            out.append(("crease", va, vb, cv))
        bv = edge[bevel] if bevel else 0.0
        if bv > 0.0:
            out.append(("bevel", va, vb, bv))
        if edge.seam:
            out.append(("seam", va, vb, 1.0))
        if not edge.smooth:
            out.append(("sharp", va, vb, 1.0))
    return out


def _marks_for(obj, edit_obj):
    """Cached marks for obj; the active edit object is always read live."""
    if obj == edit_obj:
        return _read_marks_edit(obj)
    cached = _cache.get(obj.name)
    if cached is None:
        cached = _read_marks_object(obj)
        _cache[obj.name] = cached
    return cached


# --- screen-space helpers ---------------------------------------------------

def _project(mvp, co, w, h):
    """World coord -> region pixel Vector, or None if behind the view plane."""
    v = mvp @ Vector((co.x, co.y, co.z, 1.0))
    if v.w <= 0.0:
        return None
    return Vector((((v.x / v.w) * 0.5 + 0.5) * w, ((v.y / v.w) * 0.5 + 0.5) * h))


def _dash_params(length, pattern, scale):
    """Yield (d0, d1) screen-distance spans for the 'on' pieces of the pattern."""
    if length <= 0.0:
        return
    dist = 0.0
    idx = 0
    while dist < length:
        seg = pattern[idx % len(pattern)] * scale
        nd = min(dist + seg, length)
        if idx % 2 == 0:  # 'on' piece
            yield dist, nd
        dist = nd
        idx += 1


def _balanced_points(region, rv3d, p0, p1, wa, wb, pattern, scale, offset_px):
    """Screen-accurate dashing: each dash point is unprojected back to a world
    point at the source edge's depth, so dashes/offset are pixel-exact AND the
    GPU depth test occludes correctly. Returns flat world-point list for LINES."""
    d = p1 - p0
    length = d.length
    if length == 0.0:
        return []
    t = d / length
    n = Vector((-t.y, t.x))
    seg = wb - wa
    pts = []
    for d0, d1 in _dash_params(length, pattern, scale):
        s0 = p0 + t * d0 + n * offset_px
        s1 = p0 + t * d1 + n * offset_px
        ref0 = wa + seg * (d0 / length)
        ref1 = wa + seg * (d1 / length)
        w0 = view3d_utils.region_2d_to_location_3d(region, rv3d, s0, ref0)
        w1 = view3d_utils.region_2d_to_location_3d(region, rv3d, s1, ref1)
        pts.append(w0)
        pts.append(w1)
    return pts


def _fast_points(rv3d, p0, p1, wa, wb, pattern, scale, offset_px):
    """Cheap world-space dashing: a single per-edge world/pixel ratio drives the
    offset and dash sizing — no per-segment unproject. Slight depth-span error,
    far cheaper on dense meshes."""
    d = p1 - p0
    slen = d.length
    if slen == 0.0:
        return []
    t = d / slen
    n = Vector((-t.y, t.x))
    seg = wb - wa
    wlen = seg.length
    if wlen == 0.0:
        return []
    world_per_px = wlen / slen
    rot = rv3d.view_rotation
    right = rot @ Vector((1.0, 0.0, 0.0))
    up = rot @ Vector((0.0, 1.0, 0.0))
    off = (right * n.x + up * n.y) * (offset_px * world_per_px)
    a = wa + off
    pts = []
    for d0, d1 in _dash_params(slen, pattern, scale):
        pts.append(a + seg * (d0 / slen))
        pts.append(a + seg * (d1 / slen))
    return pts


# --- occlusion depth bias ---------------------------------------------------

# Mark lines lie coplanar with the mesh faces they bound, so a plain depth test
# z-fights and culls marks on visible edges. Nudge each point toward the camera
# ALONG THE VIEW AXIS (the depth axis) by a small fraction of its view distance:
# this reduces depth uniformly regardless of edge orientation (a nudge toward the
# camera *point* barely moves edges that recede from the camera). Coplanar marks
# clear the test; marks genuinely behind other geometry (much deeper) stay hidden.
# Tuned live on a marked cube: visible-edge marks need ~0.03 to clear self
# z-fighting; back-edge marks (>=1 unit deeper) stay hidden until ~0.2, so 0.04
# sits with margin on both sides.
_OCCLUDE_BIAS = 0.04


def _bias_toward_camera(pts, rv3d):
    to_cam = rv3d.view_rotation @ Vector((0.0, 0.0, 1.0))  # +Z view = toward camera
    if rv3d.is_perspective:
        cam = rv3d.view_matrix.inverted().translation
        return [p + to_cam * ((p - cam).length * _OCCLUDE_BIAS) for p in pts]
    step = to_cam * (rv3d.view_distance * _OCCLUDE_BIAS)
    return [p + step for p in pts]


# --- tier resolution --------------------------------------------------------

def _resolve_tier(quality, marked_count):
    if quality != 'AUTO':
        return quality
    if marked_count <= _TIER_ACCURATE_MAX:
        return 'ACCURATE'
    if marked_count <= _TIER_BALANCED_MAX:
        return 'BALANCED'
    return 'FAST'


# --- draw -------------------------------------------------------------------

def _draw():
    global _shader
    context = bpy.context
    st = context.scene.edge_overlays
    if not st.show:
        return
    region = context.region
    rv3d = context.region_data
    if region is None or rv3d is None:
        return

    enabled = {c["key"]: c for c in CHANNELS if getattr(st, "show_" + c["key"])}
    if not enabled:
        return

    if _shader is None:
        _shader = gpu.shader.from_builtin('POLYLINE_FLAT_COLOR')

    w, h = region.width, region.height
    mvp = rv3d.perspective_matrix
    view_layer = context.view_layer
    edit_obj = context.edit_object

    objects = [o for o in view_layer.objects
               if o.type == 'MESH' and o.visible_get()]

    # Effective tier from total marked-edge count (cheap; uses the cache).
    marked_total = sum(len(_marks_for(o, edit_obj)) for o in objects)
    tier = _resolve_tier(st.quality, marked_total)

    # Accumulate every channel's segments into one vertex/colour stream and draw
    # in a SINGLE batch — per-edge batching is O(edges) draw calls and does not
    # scale. Per-vertex colour (incl. fade alpha) lets one draw carry all channels.
    verts = []
    cols = []
    for obj in objects:
        mw = obj.matrix_world
        for key, lv0, lv1, value in _marks_for(obj, edit_obj):
            ch = enabled.get(key)
            if ch is None:
                continue
            wa = mw @ lv0
            wb = mw @ lv1
            p0 = _project(mvp, wa, w, h)
            p1 = _project(mvp, wb, w, h)
            if p0 is None or p1 is None:
                continue
            offset_px = (ch["slot"] - 1.5) * st.line_width * 1.5
            if tier == 'FAST':
                pts = _fast_points(rv3d, p0, p1, wa, wb, ch["dash"],
                                   st.dash_scale, offset_px)
            else:
                # ACCURATE falls back to the screen-accurate builtin path until
                # the GLSL backend lands (plan step 4).
                pts = _balanced_points(region, rv3d, p0, p1, wa, wb, ch["dash"],
                                       st.dash_scale, offset_px)
            if not pts:
                continue
            if st.occlude:
                pts = _bias_toward_camera(pts, rv3d)
            col = getattr(st, "color_" + key)
            alpha = value if (ch["value"] and st.fade_weak) else 1.0
            rgba = (col[0], col[1], col[2], alpha)
            verts.extend(pts)
            cols.extend([rgba] * len(pts))

    if not verts:
        return

    gpu.state.blend_set('ALPHA')
    if st.occlude:
        gpu.state.depth_test_set('LESS_EQUAL')
        gpu.state.depth_mask_set(False)
    else:
        gpu.state.depth_test_set('NONE')

    _shader.bind()
    _shader.uniform_float("viewportSize", (w, h))
    _shader.uniform_float("lineWidth", st.line_width)
    batch_for_shader(_shader, 'LINES', {"pos": verts, "color": cols}).draw(_shader)

    gpu.state.depth_test_set('NONE')
    gpu.state.depth_mask_set(True)
    gpu.state.blend_set('NONE')


# --- cache invalidation -----------------------------------------------------

@persistent
def _on_depsgraph(scene, depsgraph):
    """Drop cached marks for objects whose mesh changed. Transforms don't
    invalidate (marks are stored in local space)."""
    for upd in depsgraph.updates:
        idd = upd.id
        if isinstance(idd, bpy.types.Object):
            if upd.is_updated_geometry:
                _cache.pop(idd.name, None)
        elif isinstance(idd, bpy.types.Mesh):
            _cache.clear()  # rare; a mesh datablock edit can affect any user
            return


# --- settings ---------------------------------------------------------------

def _redraw(self, context):
    for area in context.screen.areas:
        if area.type == 'VIEW_3D':
            area.tag_redraw()


def _apply_palette(self, context):
    if self.palette == 'NATIVE':
        tv = context.preferences.themes[0].view_3d
        for c in CHANNELS:
            col = getattr(tv, _NATIVE_THEME_ATTR[c["key"]])
            setattr(self, "color_" + c["key"], (col[0], col[1], col[2]))
    else:  # CB — colourblind-safe Okabe-Ito defaults
        for c in CHANNELS:
            setattr(self, "color_" + c["key"], c["color"])
    _redraw(self, context)


def _make_settings():
    ann = {
        "show": bpy.props.BoolProperty(
            name="Show", description="Master toggle for all edge overlays",
            default=False, update=_redraw),
        "quality": bpy.props.EnumProperty(
            name="Quality",
            description="Draw tier; Auto picks one from the marked-edge count",
            items=[
                ('AUTO', "Auto", "Pick a tier from the marked-edge count"),
                ('FAST', "Fast", "Cheapest; world-space dashing for weak machines"),
                ('BALANCED', "Balanced", "Screen-accurate dashing"),
                ('ACCURATE', "Accurate", "Highest fidelity (GPU dashing where available)"),
            ],
            default='AUTO', update=_redraw),
        "palette": bpy.props.EnumProperty(
            name="Palette",
            description="Preset channel colours; you can still edit each swatch",
            items=[
                ('CB', "Colourblind-Safe", "Okabe-Ito palette"),
                ('NATIVE', "Blender Native", "Match the active theme's edge-mark colours"),
            ],
            default='CB', update=_apply_palette),
        "line_width": bpy.props.FloatProperty(
            name="Line Width", default=2.0, min=1.0, max=8.0, update=_redraw),
        "dash_scale": bpy.props.FloatProperty(
            name="Dash Scale", default=8.0, min=1.0, max=32.0, update=_redraw),
        "fade_weak": bpy.props.BoolProperty(
            name="Fade Weak Marks",
            description="Scale opacity by value for Crease and Bevel Weight",
            default=True, update=_redraw),
        "occlude": bpy.props.BoolProperty(
            name="Occlude",
            description="Hide marks behind front geometry (off = see-through)",
            default=False, update=_redraw),
    }
    for c in CHANNELS:
        ann["show_" + c["key"]] = bpy.props.BoolProperty(
            name=c["label"], default=True, update=_redraw)
        ann["color_" + c["key"]] = bpy.props.FloatVectorProperty(
            name=c["label"], subtype='COLOR', size=3, min=0.0, max=1.0,
            default=c["color"], update=_redraw)
    return type("EdgeOverlaySettings", (bpy.types.PropertyGroup,),
                {"__annotations__": ann})


EdgeOverlaySettings = _make_settings()


class VIEW3D_PT_edge_overlays(bpy.types.Panel):
    bl_label = "Edge Overlays"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "View"

    def draw(self, context):
        st = context.scene.edge_overlays
        layout = self.layout
        layout.prop(st, "show", toggle=True)
        col = layout.column(align=True)
        col.active = st.show
        for c in CHANNELS:
            row = col.row(align=True)
            row.prop(st, "show_" + c["key"], text="")
            row.prop(st, "color_" + c["key"], text=c["label"])
        layout.prop(st, "palette")
        layout.prop(st, "quality")
        layout.prop(st, "line_width")
        layout.prop(st, "dash_scale")
        layout.prop(st, "fade_weak")
        layout.prop(st, "occlude")


_CLASSES = [EdgeOverlaySettings, VIEW3D_PT_edge_overlays]


def register():
    global _handle
    for cls in _CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.Scene.edge_overlays = bpy.props.PointerProperty(type=EdgeOverlaySettings)
    _handle = bpy.types.SpaceView3D.draw_handler_add(_draw, (), 'WINDOW', 'POST_VIEW')
    if _on_depsgraph not in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.append(_on_depsgraph)


def unregister():
    global _handle, _shader
    if _on_depsgraph in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(_on_depsgraph)
    if _handle is not None:
        bpy.types.SpaceView3D.draw_handler_remove(_handle, 'WINDOW')
        _handle = None
    _shader = None
    _cache.clear()
    del bpy.types.Scene.edge_overlays
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
