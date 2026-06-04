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

# AUTO cutover on total marked-edge count, against a 16 ms (60 fps) frame budget.
# Measured live on a marked grid: the per-frame screen-accurate path (_balanced_points,
# per-segment unproject) costs ~0.020 ms/marked-edge, so ~500 marked edges spends ~10 ms.
# At/below the cutover AUTO uses BALANCED (per-frame, crisp screen-stable dashes); above
# it AUTO uses ACCURATE, whose cached world-space batch makes camera navigation cheap
# regardless of count (only a mesh edit rebuilds it), at the cost of world-stable dashes.
_TIER_AUTO_CUTOVER = 500

# ACCURATE bake fractions of the object's bbox diagonal, so dashes, the parallel offset,
# and the occlude lift scale with model size (a fixed world size would mis-scale on tiny or
# huge meshes). Dashes and offset are world-space so the batch can be cached; the
# outward-normal lift is view-independent so occlusion stays correct after the camera moves.
# Tuned to reproduce the validated cube look (dimensions 2, diagonal ~3.46).
_ACCEL_DASH_FRAC = 0.006     # dash length per pattern unit, at dash_scale 8
_ACCEL_OFFSET_FRAC = 0.006   # parallel channel separation per (slot · line_width)
_ACCEL_LIFT_FRAC = 0.001     # outward lift to clear the occlude z-fight from any angle

_shader = None    # builtin POLYLINE_FLAT_COLOR, compiled lazily (needs a GPU context)
_handle = None    # draw-handler reference
_cache = {}       # obj.name -> list[(key, local_v0, local_v1, value)] for non-edit objects
_accel_cache = {} # obj.name -> cached ACCURATE GPUBatch (None when object has no marks)


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
    return 'BALANCED' if marked_count <= _TIER_AUTO_CUTOVER else 'ACCURATE'


# --- ACCURATE: cached world-space batch -------------------------------------

def _edge_outward_normals(me):
    """Per-edge averaged adjacent-face normal (local space). Lets the cached batch
    offset marks along the surface (parallel separation) and lift them outward (a
    view-independent occlude bias that survives camera moves)."""
    en = [Vector((0.0, 0.0, 0.0)) for _ in me.edges]
    ekey = {tuple(sorted(e.vertices)): i for i, e in enumerate(me.edges)}
    for poly in me.polygons:
        n = poly.normal
        vs = poly.vertices
        for k in range(len(vs)):
            i = ekey.get(tuple(sorted((vs[k], vs[(k + 1) % len(vs)]))))
            if i is not None:
                en[i] += n
    return en


def _build_accel(obj, st, enabled):
    """Build the ACCURATE tier's cached batch: world-space, dash-subdivided, with a
    world-surface parallel offset and an outward lift. Returns a GPUBatch, or None
    when the object carries no enabled marks. Rebuilt only on mesh edit or a settings
    change — never on camera move, which is what makes navigation cheap at scale."""
    me = obj.data
    mw = obj.matrix_world
    nmat = mw.inverted().transposed().to_3x3()
    crease = me.attributes.get("crease_edge")
    bevel = me.attributes.get("bevel_weight_edge")
    en = _edge_outward_normals(me)
    diag = obj.dimensions.length or 1.0
    dash_world = (st.dash_scale / 8.0) * diag * _ACCEL_DASH_FRAC
    lift = diag * _ACCEL_LIFT_FRAC
    verts = []
    cols = []
    for i, edge in enumerate(me.edges):
        chans = []
        cv = crease.data[i].value if crease else 0.0
        if cv > 0.0 and "crease" in enabled:
            chans.append(("crease", cv))
        bv = bevel.data[i].value if bevel else 0.0
        if bv > 0.0 and "bevel" in enabled:
            chans.append(("bevel", bv))
        if edge.use_seam and "seam" in enabled:
            chans.append(("seam", 1.0))
        if edge.use_edge_sharp and "sharp" in enabled:
            chans.append(("sharp", 1.0))
        if not chans:
            continue
        wa = mw @ me.vertices[edge.vertices[0]].co
        wb = mw @ me.vertices[edge.vertices[1]].co
        seg = wb - wa
        if seg.length == 0.0:
            continue
        nrm = nmat @ en[i]
        nrm = nrm.normalized() if nrm.length > 0.0 else Vector((0.0, 0.0, 1.0))
        perp = seg.normalized().cross(nrm)
        perp = perp.normalized() if perp.length > 0.0 else Vector((0.0, 0.0, 0.0))
        for key, value in chans:
            ch = _BY_KEY[key]
            off = (perp * ((ch["slot"] - 1.5) * st.line_width * _ACCEL_OFFSET_FRAC * diag)
                   + nrm * lift)
            a = wa + off
            col = getattr(st, "color_" + key)
            alpha = value if (ch["value"] and st.fade_weak) else 1.0
            rgba = (col[0], col[1], col[2], alpha)
            length = seg.length
            d = 0.0
            idx = 0
            pat = ch["dash"]
            while d < length:
                s = pat[idx % len(pat)] * dash_world
                nd = min(d + s, length)
                if idx % 2 == 0:
                    verts.append(a + seg * (d / length))
                    verts.append(a + seg * (nd / length))
                    cols.append(rgba)
                    cols.append(rgba)
                d = nd
                idx += 1
    if not verts:
        return None
    return batch_for_shader(_shader, 'LINES', {"pos": verts, "color": cols})


# --- draw -------------------------------------------------------------------

def _set_gpu_state(occlude):
    gpu.state.blend_set('ALPHA')
    if occlude:
        gpu.state.depth_test_set('LESS_EQUAL')
        gpu.state.depth_mask_set(False)
    else:
        gpu.state.depth_test_set('NONE')


def _restore_gpu_state():
    gpu.state.depth_test_set('NONE')
    gpu.state.depth_mask_set(True)
    gpu.state.blend_set('NONE')


def _collect_segments(obj, st, enabled, tier, rv3d, region, mvp, w, h, verts, cols):
    """Per-frame point building for the FAST and BALANCED tiers (appends to
    verts/cols). Screen-dependent, so it runs every redraw."""
    mw = obj.matrix_world
    for key, lv0, lv1, value in _marks_for(obj, bpy.context.edit_object):
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
            pts = _fast_points(rv3d, p0, p1, wa, wb, ch["dash"], st.dash_scale, offset_px)
        else:
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

    marked_total = sum(len(_marks_for(o, edit_obj)) for o in objects)
    tier = _resolve_tier(st.quality, marked_total)

    if tier == 'ACCURATE':
        # Cached world-space batches for static objects (cheap nav); the active edit
        # object is rebuilt per frame via the screen-accurate path so live edits show.
        batches = []
        for obj in objects:
            if obj == edit_obj:
                continue
            b = _accel_cache.get(obj.name, 'MISS')
            if b == 'MISS':
                b = _build_accel(obj, st, enabled)
                _accel_cache[obj.name] = b
            if b is not None:
                batches.append(b)
        edit_verts, edit_cols = [], []
        if edit_obj in objects:
            _collect_segments(edit_obj, st, enabled, 'BALANCED', rv3d, region, mvp,
                              w, h, edit_verts, edit_cols)
        if not batches and not edit_verts:
            return
        _set_gpu_state(st.occlude)
        _shader.bind()
        _shader.uniform_float("viewportSize", (w, h))
        _shader.uniform_float("lineWidth", st.line_width)
        for b in batches:
            b.draw(_shader)
        if edit_verts:
            batch_for_shader(_shader, 'LINES', {"pos": edit_verts, "color": edit_cols}).draw(_shader)
        _restore_gpu_state()
        return

    # FAST / BALANCED — accumulate one vertex/colour stream, draw in a single batch.
    verts, cols = [], []
    for obj in objects:
        _collect_segments(obj, st, enabled, tier, rv3d, region, mvp, w, h, verts, cols)
    if not verts:
        return
    _set_gpu_state(st.occlude)
    _shader.bind()
    _shader.uniform_float("viewportSize", (w, h))
    _shader.uniform_float("lineWidth", st.line_width)
    batch_for_shader(_shader, 'LINES', {"pos": verts, "color": cols}).draw(_shader)
    _restore_gpu_state()


# --- cache invalidation -----------------------------------------------------

@persistent
def _on_depsgraph(scene, depsgraph):
    """Drop cached marks (and the ACCURATE batch) for objects whose mesh changed.
    Transforms don't invalidate — marks are stored in local space."""
    for upd in depsgraph.updates:
        idd = upd.id
        if isinstance(idd, bpy.types.Object):
            if upd.is_updated_geometry:
                _cache.pop(idd.name, None)
                _accel_cache.pop(idd.name, None)
        elif isinstance(idd, bpy.types.Mesh):
            _cache.clear()  # rare; a mesh datablock edit can affect any user
            _accel_cache.clear()
            return


# --- settings ---------------------------------------------------------------

def _redraw(self, context):
    # Settings bake into the ACCURATE batch (colour, width, dash, fade, channel
    # enables), so any change invalidates it; the per-frame tiers ignore the cache.
    _accel_cache.clear()
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
                ('FAST', "Fast", "Per-frame, world-approx dashing — lowest overhead"),
                ('BALANCED', "Balanced", "Per-frame, crisp screen-stable dashing"),
                ('ACCURATE', "Accurate", "Cached batch — cheap navigation, scales to big meshes"),
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
    _accel_cache.clear()
    del bpy.types.Scene.edge_overlays
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
