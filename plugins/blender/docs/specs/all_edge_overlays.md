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
│ Palette           [ Colourblind-Safe ▾ ] │   ← preset: Colourblind / Blender Native
│ Quality           [ Auto ▾ ]             │   ← Auto / Fast / Balanced / Accurate
│ Line Width        [ 2.0 px ]             │
│ Dash Scale        [ 8.0 px ]             │
│ Fade Weak Marks   [ ☑ ]                  │   ← opacity ∝ value for Crease/Bevel
│ Occlude (depth)   [ ☐ ]                   │   ← default off (x-ray)
└──────────────────────────────────────────┘
```

- **Show** master toggle gates the whole overlay (one fast boolean check at the top of the
  draw callback).
- Each channel row: enable checkbox, color swatch, and a non-interactive dash-pattern
  preview so the legend lives in the panel itself.
- The **Palette** preset switches all four channel colours at once: *Colourblind-Safe*
  (Okabe-Ito, the default) or *Blender Native* (read live from the active theme's edge-mark
  hues — crease, bevel, seam, sharp — so it matches any custom theme). Each swatch stays
  individually editable after a preset is chosen.

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

- **Coordinate space:** the draw handler is registered in `'POST_VIEW'`, so vertex positions
  are world-space and the GPU depth test works against the scene depth buffer. Local vert
  coords are multiplied by `object.matrix_world` per frame.
- **Shader:** the builtin `'POLYLINE_FLAT_COLOR'` shader (per-vertex RGBA, `lineWidth`,
  `viewportSize`). It is available on every GPU backend Blender supports, which maximizes
  reach. Every channel's dash segments — across all objects — are accumulated into one
  vertex/colour stream and drawn in a **single batch**: per-edge batching is O(edges) draw
  calls and does not scale. Per-vertex colour carries both the channel hue and the per-edge
  fade alpha, so one draw covers all channels at once.
- **Dashing (two CPU paths, tier-selected):** there is no builtin dashed-polyline shader, so
  dashes are CPU-subdivided. The **screen-accurate** path subdivides in screen space and maps
  each dash point back to a world point at the edge's depth via
  `bpy_extras.view3d_utils.region_2d_to_location_3d` — pixel-stable dashes and a pixel-exact
  parallel offset that still depth-test correctly. The **fast** path uses a single per-edge
  world/pixel ratio for offset and dash sizing (no per-segment unproject), trading a little
  accuracy for ~4× lower per-frame cost on dense selections.
- **Parallel offset for coincident marks:** each edge's screen-space normal offsets channel
  *k* by `(slot − 1.5) · width · 1.5` pixels, turning coincident marks from an unreadable
  overdraw into legible parallel lines. Constant in pixels at any zoom.
- **Depth / Occlude:** when "Occlude" is on, `gpu.state.depth_test_set('LESS_EQUAL')` plus a
  small per-point depth bias toward the camera **along the view axis** (a nudge toward the
  camera *point* barely moves edges that recede from it). The bias clears the coplanar
  z-fight on visible-edge marks while marks genuinely behind geometry stay hidden; tuned to
  ~0.04 of view distance. When off, the depth test is disabled (x-ray). Always
  `gpu.state.blend_set('ALPHA')` for the value-fade.

### Performance tiers

`scene.edge_overlays.quality` selects **Fast / Balanced / Accurate**, or **Auto** (default),
which resolves the tier from the total marked-edge count against a 16 ms (60 fps) frame
budget. Measured live: the screen-accurate path costs ~0.020 ms/marked-edge (holds budget to
~500 marked edges); the fast path ~0.0047 ms/marked-edge (to ~2500). Auto uses the
screen-accurate path at/below the cutover and the fast path above it. Accurate and Balanced
currently share the screen-accurate path; the GPU-dashing Accurate backend below will split
them and lift the Accurate ceiling.

### Caching

Per object, the **mark read** (iterating edge attributes) is cached as a list of
local-space `(channel, v0, v1, value)` tuples, invalidated by a `depsgraph_update_post`
handler that drops entries for objects whose mesh changed. The active edit object is read
live from the edit bmesh each frame. Because marks are stored in **local space** and
multiplied by `matrix_world` per frame, object transforms never invalidate the cache.

This cache removes the attribute-read cost, but the dash subdivision and projection are
view-dependent and still run every frame on the CPU paths — so camera navigation rebuilds
the dash geometry each frame. The GPU-dashing Accurate backend (below) is what makes
navigation cheap: it bakes world arc length once and dashes in the fragment shader, leaving
only a GPU draw per frame.

### GPU-dashing Accurate backend (planned)

A custom `gpu.types.GPUShader` carrying per-vertex cumulative world arc length as an
attribute, discarding fragments where `fract(arclen / dash_size)` lands in the channel's
"off" interval. Zoom-stable, GPU-side, and — paired with the per-object cache — cheap on
camera navigation, which is what lets it scale to large marked-edge counts. It is
lazy-compiled inside a `try/except`; on any backend-compile failure the addon permanently
falls back to the screen-accurate builtin path, so reach is never sacrificed for the
optimization.

### State storage

A `PropertyGroup` (`EdgeOverlaySettings`) registered as `Scene.edge_overlays`, holding the
master toggle, a `quality` enum (Auto/Fast/Balanced/Accurate), a `palette` enum (Colourblind-
Safe / Blender Native), and for each channel an enable bool and `FloatVectorProperty(
subtype='COLOR')`, plus global line width, dash scale, fade, and occlude. The palette enum's
`update=` callback writes the four channel colours — from the active theme's edge-mark hues
for Native, from the Okabe-Ito constants for Colourblind-Safe — while leaving each swatch
individually editable. Storing on `Scene` persists the configuration in the .blend file.
Settings changes tag the viewport for redraw via an `update=` callback that calls
`tag_redraw` on all VIEW_3D areas.

### GPU path validation status

The edge-mark data path and the builtin-shader draw path are both **validated live on
4.2.5**: register/unregister round-trip, the four distinct channels with colour + dash
patterns, the parallel offset on coincident marks, value-fade, per-channel toggles, the
master toggle, edit-mode live update, occlude on/off (verified against per-edge
camera-visibility ground truth), both palette presets, and the Fast and screen-accurate
tiers. The **GPU-dashing Accurate backend remains the one unbuilt piece** — its custom
shader must be confirmed against a running viewport, and its compile-failure fallback to the
builtin path exercised, when it is added. Headless/background Blender has no GPU context
(`gpu.shader.from_builtin` raises "GPU functions for drawing are not available in background
mode"), so that work is live-only.

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
