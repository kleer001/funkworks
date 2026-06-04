# Plugin Spec: All Edge Overlays

## Problem Statement

Blender's viewport can display edge-mark overlays — Crease, Bevel Weight, Seam, and Sharp —
but only **one at a time**. The Overlays dropdown exposes them as mutually exclusive
toggles, so a modeler who marks the same mesh several ways (seams for UVs, creases and
bevel weights for the subdivision/bevel pass, sharps for shading) cannot see where those
marks overlap or conflict without flipping overlays back and forth and holding the picture
in their head.

On a hard-surface mesh this matters: a seam that accidentally lands on a creased edge, or a
sharp that should have a bevel weight and doesn't, is invisible until something downstream
breaks. The request — open on Right-Click-Select with a corroborating second thread — is to
show all four marks **simultaneously**, distinguished by per-property color *and* dash
pattern, so overlaps read at a glance.

Native Blender cannot do this through any operator or overlay setting. This is a genuine
new capability, not a relocation of an existing one.

References:
- https://blender.community/c/rightclickselect/nPbbbc/ (primary)
- https://blender.community/c/rightclickselect/vydbbc/ (independent second signal)

## Proposed Solution

A viewport overlay, drawn by a `gpu`-module draw handler registered on `SpaceView3D`, that
renders every marked edge of visible mesh objects as a dashed line, color- and
pattern-coded by property. Four independent channels (Crease, Bevel Weight, Seam, Sharp),
each toggleable, each with its own color and dash pattern. When one edge carries more than
one mark, the channels are drawn with a small perpendicular screen-space offset so they
appear as **parallel** dashed lines rather than overlapping into one — the overlap is the
whole point, so it must never be hidden.

For the two value properties (Crease and Bevel Weight, both 0–1), line opacity scales with
the value, so weak vs. strong marks are readable without opening the N-panel.

No mesh data is modified. The addon is pure visualization: it reads edge attributes and
draws. There is no operator that changes the scene.

## Host Application

- Application: Blender
- Minimum version: **4.2 LTS** (validated baseline). The data model this relies on — crease
  and bevel weight as generic edge-domain float attributes — was introduced in 4.0; 4.2 LTS
  is the conservative shippable floor.
- API surfaces used:
  - `bpy.types.SpaceView3D.draw_handler_add` / `draw_handler_remove` — the overlay draw
    callback, space `'WINDOW'`, region type `'POST_VIEW'` (world-space line coordinates)
  - `gpu` + `gpu_extras.batch.batch_for_shader` — line batches
  - `gpu.shader` — either a builtin polyline shader or a small custom GLSL shader for
    screen-space dashing (see Technical Implementation Notes)
  - `gpu.state` — depth test and alpha blend configuration
  - `bmesh.from_edit_mesh` — live read of marks while in Edit Mode
  - `bpy.types.Mesh.attributes` — read of marks in Object Mode
  - `bpy.types.PropertyGroup` on `Scene` — per-channel enable/color/width/dash settings
  - `bpy.types.Panel` — N-panel controls in the View tab
  - `bpy.app.handlers.depsgraph_update_post` — invalidate the geometry cache on mesh edits

## User Interface

### N-panel — View tab, "Edge Overlays" section

```
┌──────────────────────────────────────────┐
│ Edge Overlays                    [ Show ] │   ← master toggle
│ ──────────────────────────────────────── │
│ ☑ Crease        [colour]  ▓▓ ── ── ──    │   ← per-channel: on, colour, dash preview
│ ☑ Bevel Weight  [colour]  ▓▓ ─ ─ ─ ─     │
│ ☑ Seam          [colour]  ▓▓ · · · ·     │
│ ☑ Sharp         [colour]  ▓▓ ─·─·─·      │
│ ──────────────────────────────────────── │
│ Line Width        [ 2.0 px ]             │
│ Dash Scale        [ 8.0 px ]             │
│ Fade Weak Marks   [ ☑ ]                  │   ← opacity ∝ value for Crease/Bevel
│ Occlude (depth)   [ ☑ ]                   │
└──────────────────────────────────────────┘
```

- **Show** master toggle gates the whole overlay (one fast boolean check at the top of the
  draw callback).
- Each channel row: enable checkbox, color swatch, and a non-interactive dash-pattern
  preview so the legend lives in the panel itself.
- Defaults echo Blender's own edge-mark theme hues so the overlay feels native:
  Crease violet, Bevel Weight blue, Seam red, Sharp cyan.

### Header / Overlays dropdown (optional, phase 2)

A single "Edge Overlays" checkbox could be mirrored into the viewport Overlays popover for
discoverability. Not required for v1.

## Inputs and Outputs

### Input
- All visible mesh objects in the active view layer (object mode), or the active edited mesh
  (edit mode).
- Per-channel settings from `scene.edge_overlays`.

### Output
- GPU lines drawn into the 3D viewport every redraw. No persistent output.

### Side effects
- None on mesh data. The addon registers a draw handler and a depsgraph handler at
  `register()` and removes both at `unregister()`. No undo steps are ever pushed.

## Workflow

```
1. Enable the addon → "Edge Overlays" appears in the N-panel View tab, master toggle off
2. Mark edges as usual (Mark Seam, Mark Sharp, Edge Crease, Bevel Weight)
3. Toggle "Show" → all four marks render at once, parallel where they coincide
4. Toggle individual channels to isolate, e.g., "where do seams cross creases?"
5. Continues to update live as marks are edited in Edit Mode
```

## Technical Implementation Notes

### Verified edge-mark data model (probed on Blender 4.2.5)

The pre-4.0 access paths are **gone** and must not be used:
- `MeshEdge.crease` and `MeshEdge.bevel_weight` → `AttributeError` (removed in 4.0)
- `bmesh.types.BMLayerAccessEdge.crease` / `.bevel_weight` → `AttributeError` (removed)

Current paths, confirmed by round-trip probe:

| Mark | Storage | Edit Mode read | Object Mode read |
|------|---------|----------------|------------------|
| Crease | `crease_edge` FLOAT, EDGE domain | `bm.edges.layers.float.get("crease_edge")` | `me.attributes["crease_edge"].data[i].value` |
| Bevel Weight | `bevel_weight_edge` FLOAT, EDGE domain | `bm.edges.layers.float.get("bevel_weight_edge")` | `me.attributes["bevel_weight_edge"].data[i].value` |
| Seam | `.uv_seam` BOOLEAN, EDGE domain | `bm_edge.seam` | `MeshEdge.use_seam` |
| Sharp | `sharp_edge` BOOLEAN, EDGE domain | `not bm_edge.smooth` | `MeshEdge.use_edge_sharp` |

**All four attributes are lazy** — they do not exist on a mesh until a value is set. The
read code must treat a missing layer/attribute as "no edges marked for this channel" (the
`.get()` returns `None`; skip the channel). Never call `attributes["crease_edge"]` without a
presence check.

For value channels, only edges with `value > 0` are drawn; for boolean channels, only edges
with the flag set. This keeps the batch small on meshes where most edges are unmarked.

### Drawing

- **Coordinate space:** register the draw handler in `'POST_VIEW'` so vertex positions are
  world-space; multiply local vert coords by `object.matrix_world` once per object when
  building the batch.
- **Shader / dashing:** there is no builtin dashed-polyline shader. Two options, in
  preference order:
  1. **Custom GLSL shader** (`gpu.types.GPUShader`) that takes a per-vertex cumulative
     screen-space arc length and discards fragments where `fract(arclen / dash_scale)` falls
     in the "off" half of the channel's pattern. Gives zoom-stable dashes and lets each
     channel define its own on/off pattern (dot, dash, dash-dot). This is the intended path.
  2. Fallback for prototyping only: builtin `'POLYLINE_UNIFORM_COLOR'` (supports
     `lineWidth` + `viewportSize`) with CPU-subdivided dash segments drawn as `'LINES'`.
     Simpler, but dash length is computed per-frame and is heavier on big selections.
- **Parallel offset for coincident marks:** compute each edge's screen-space normal
  (perpendicular to the edge direction in the view plane) and offset channel *k* by
  `k * width * 1.5` pixels along it. This is what turns "four marks on one edge" from an
  unreadable overdraw into four legible parallel lines. The offset is applied in the vertex
  shader using `viewportSize` so it stays constant in pixels at any zoom.
- **Depth:** when "Occlude" is on, `gpu.state.depth_test_set('LESS_EQUAL')` and draw against
  the existing depth buffer so back-facing marks are hidden; when off, draw with depth test
  disabled (x-ray style). Always `gpu.state.blend_set('ALPHA')` for the value-fade.

### Caching

The draw callback runs every redraw, so it must not rebuild geometry from scratch each
frame. Cache, per object, the built vertex/color/arclen arrays keyed by
`(object.name, mesh-update-token)`. Invalidate via a `depsgraph_update_post` handler that
clears cache entries for objects whose mesh changed, and (in Edit Mode) rebuild from the
edit bmesh each time the edit mesh reports a change. Object matrix changes only require
re-uploading positions, not re-reading marks.

### State storage

A `PropertyGroup` (`EdgeOverlaySettings`) registered as `Scene.edge_overlays`, holding the
master toggle, and for each channel an enable bool, `FloatVectorProperty(subtype='COLOR')`,
plus global line width, dash scale, fade, and occlude. Storing on `Scene` persists the
configuration in the .blend file. Settings changes tag the viewport for redraw via an
`update=` callback that calls `tag_redraw` on all VIEW_3D areas.

### GPU path validation status

The edge-mark **data path above is probe-verified** on 4.2.5. The **GPU draw path is
designed but not yet validated on a live GL context** — headless/background Blender has no
GPU context (`gpu.shader.from_builtin` raises "GPU functions for drawing are not available
in background mode"), so the custom dash shader, the parallel-offset math, and depth
behavior must be confirmed against a running viewport during implementation. This is the
primary build risk and the first thing the build should exercise.

## Edge Cases

- **No marks anywhere:** every channel layer is absent; draw callback builds an empty batch
  and returns fast. No error.
- **Object hidden / not in view layer:** skipped; only visible mesh objects are drawn.
- **Non-mesh objects:** skipped at the type check.
- **Edit Mode on object A, object B also marked:** A is read live from the edit bmesh; other
  visible meshes are read from their evaluated attributes. Both draw.
- **Mesh with a modifier that changes topology (e.g. Mirror, Subdivision):** marks live on
  the base mesh; v1 draws marks on the **base** cage geometry, consistent with how Blender's
  native edge overlays behave in Edit Mode. Drawing on the modified result is out of scope.
- **Very dense mesh (>100k marked edges):** batch size scales with marked edges only; if it
  becomes a bottleneck, the cache keeps it to upload-only per frame. A hard cap with a
  status note is a fallback only if profiling shows a real problem — not added speculatively.
- **Crease/Bevel value exactly 0:** treated as unmarked (not drawn), matching Blender, which
  shows nothing for a 0 value.
- **Undo of a mark change:** depsgraph fires, cache invalidates, overlay reflects the undone
  state on next redraw. The addon itself pushes no undo steps.

## Known Limitations

- **Base-cage only:** marks are drawn on the unmodified mesh, not the post-modifier result.
  This matches native behavior and avoids evaluating heavy modifier stacks every redraw.
- **Viewport only:** overlays are a viewport aid and do not appear in renders (consistent
  with all Blender overlays).
- **One view layer:** draws the objects in the active view layer of the area being drawn.
- **No per-object override:** channel settings are scene-global, not per-object. Per-object
  visibility is deliberately out of scope for v1 (YAGNI).

## Acceptance Criteria

1. Addon installs and enables without error on Blender 4.2 LTS.
2. "Edge Overlays" section appears in the 3D viewport N-panel View tab.
3. With the master toggle off, no overlay draws and the draw callback early-returns.
4. On a cube with one seam, one sharp, one creased, and one bevel-weighted edge, enabling
   the overlay draws four distinct dashed lines, each matching its channel color and pattern.
5. An edge carrying two marks renders as two parallel offset dashed lines, both legible.
6. Disabling a single channel removes only that channel's lines; others persist.
7. Crease at 0.2 vs 0.9 renders at visibly different opacity when "Fade Weak Marks" is on.
8. Editing a mark in Edit Mode updates the overlay within one redraw (no manual refresh).
9. A mesh with zero marks produces no draw output and no error (lazy-attribute safety).
10. "Occlude" on hides marks behind front geometry; off shows them through (x-ray).
11. Settings persist across save/reload (stored on Scene).
12. Disabling the addon removes the draw handler and depsgraph handler cleanly; no lingering
    overlay, no traceback on viewport redraw.
13. Switching objects, entering/leaving Edit Mode, and transforming objects never throw.
14. Headless smoke test: the addon registers, the `EdgeOverlaySettings` group and panel
    class appear in `bpy.types`, register/unregister round-trips cleanly. (GPU draw itself is
    validated interactively, not in the headless test.)
```
