# Plugin Spec: Selective Edge Split

## Problem Statement

Blender's Edge Split modifier acts globally on all marked sharp edges. Hard-surface modelers
routinely mark sharp edges for two distinct purposes: smooth normal rendering, and panel gap
geometry cuts. There is no native way to scope Edge Split to one category of sharp edge only.

The workaround — clear all sharps, mark only panel gap edges, apply Edge Split, then manually
re-mark every render sharp — is destructive, tedious, and scales badly. On a complex vehicle mesh
with 80 render sharp loops, a single panel gap adjustment requires 100+ manual actions and loses
modifier stack position every time.

This addon eliminates that cycle. Users tag panel gap edges once with a Ctrl+E menu entry
(matching the existing Mark Sharp / Mark Seam pattern), then apply a scoped edge split that
touches only those edges. Render sharps are never disturbed.

## Proposed Solution

Three operators, registered in the Edit Mode `Ctrl+E` Edge menu and the N-panel:

1. **Mark Panel Gap** — tags selected edges with a custom boolean mesh attribute (`panel_gap`)
2. **Clear Panel Gap** — removes the tag from selected edges
3. **Apply Panel Gap Split** — Object Mode operator; calls `bmesh.ops.split_edges()` on only the
   edges where `panel_gap = True`, leaving all other edges, sharp marks, and modifier stack intact

No Geometry Nodes. No live modifier. Applies once, non-ambiguously, with a single undo step.

## Host Application

- Application: Blender
- Minimum version: Blender 4.0+ (conservative LTS baseline; EDGE-domain boolean attributes
  exist from 3.2, but behaviour on 3.x is untested — 4.0 LTS is the first version this addon
  has been validated against)
- API surfaces used:
  - `bpy.types.Operator` — all three operators
  - `bpy.types.Panel` — N-panel entry in the Item tab (Edit Mode and Object Mode)
  - `bpy.ops.mesh.mark_panel_gap` / `clear_panel_gap` — Edit Mode operators
  - `bpy.ops.object.apply_panel_gap_split` — Object Mode operator
  - `bmesh` / `bmesh.ops.split_edges()` — core split operation
  - `bpy.types.Mesh.attributes` — reading and writing the `panel_gap` BOOLEAN EDGE attribute
  - `bpy.types.Menu` — appending entries to `VIEW3D_MT_edit_mesh_edges` (the Ctrl+E menu)

## User Interface

### Edit Mode — Ctrl+E menu

Appended below "Mark Sharp" and "Clear Sharp":

```
Ctrl+E →
  Mark Sharp          (Blender built-in)
  Clear Sharp         (Blender built-in)
  ─────────────────
  Mark Panel Gap      ← new
  Clear Panel Gap     ← new
```

No dialog, no properties. Runs immediately on the current edge selection. Reports count
of edges tagged/untagged in the status bar.

### Edit Mode — N-panel (Item tab)

A collapsible section "Panel Gap" with two buttons side by side:

```
┌──────────────────────────────────┐
│ Panel Gap                        │
│  [Mark Panel Gap] [Clear Panel Gap] │
└──────────────────────────────────┘
```

### Object Mode — N-panel (Item tab)

```
┌──────────────────────────────────┐
│ Panel Gap                        │
│  Tagged edges: 14                │
│  [Apply Panel Gap Split]         │
└──────────────────────────────────┘
```

"Tagged edges: N" reads the `panel_gap` attribute on the active object's mesh and displays
the count live. If no edges are tagged, the count shows 0 and the button is greyed out.

### F3 Search

All three operators are searchable:
- "Mark Panel Gap"
- "Clear Panel Gap"
- "Apply Panel Gap Split"

## Inputs and Outputs

### Mark Panel Gap / Clear Panel Gap
- **Input:** current edge selection in Edit Mode on the active mesh object
- **Output:** `panel_gap` boolean attribute written to the EDGE domain of the mesh; True for
  marked edges, False for cleared edges; attribute created on first use if absent
- **Side effects:** one undo step; does not alter any other mesh data

### Apply Panel Gap Split
- **Input:** active object in Object Mode; must be a mesh with at least one `panel_gap = True`
  edge
- **Output:** edges where `panel_gap = True` are split (vertices duplicated along those edges,
  geometry separated); the `panel_gap` attribute is removed from the mesh after application
  (it is no longer meaningful once topology has changed)
- **Side effects:** one undo step; modifies mesh topology; does not touch vertex groups, sharp
  marks, seams, UV maps, materials, or modifier stack

## Workflow

```
1. Edit Mode: mark render sharps as usual (Ctrl+E → Mark Sharp)
2. Edit Mode: select edges intended for panel gaps
3. Ctrl+E → Mark Panel Gap
4. Repeat 2–3 for all panel gap edges across the mesh
5. Object Mode: N-panel → Apply Panel Gap Split
6. Continue: add Solidify, Bevel modifiers as normal
```

For subsequent additions (more panel gaps needed later):

```
1. Edit Mode: select new panel gap edges
2. Ctrl+E → Mark Panel Gap
3. Object Mode: N-panel → Apply Panel Gap Split
   (only the newly tagged edges are split; previously split geometry is unaffected)
```

## Technical Implementation Notes

### The `panel_gap` attribute

- Domain: EDGE
- Data type: BOOLEAN
- Created lazily on first Mark Panel Gap call; absent on objects that have never been tagged
- Survives Edit Mode / Object Mode transitions, file save, and Undo
- Removed by Apply Panel Gap Split after the operation (topology change makes it invalid)
- Not a vertex group — an edge-domain attribute is semantically correct; vertex groups are
  vertex-domain and require the two-vertex membership workaround

### The split operation

```python
# Read tagged indices from RNA *before* entering bmesh.
# In Blender 4.x, BOOLEAN edge attributes do not appear in bmesh edge layers
# (layers.int / layers.float are both empty for RNA boolean attributes).
# RNA indexing is the correct access path.
tagged = sorted(
    i for i, e in enumerate(obj.data.attributes["panel_gap"].data) if e.value
)

bm = bmesh.new()
bm.from_mesh(obj.data)
bm.edges.ensure_lookup_table()

bmesh.ops.split_edges(bm, edges=[bm.edges[i] for i in tagged])

bm.to_mesh(obj.data)
bm.free()
obj.data.attributes.remove(obj.data.attributes["panel_gap"])
```

### Sharp mark behaviour on split edges (verified by probe)

`bmesh.ops.split_edges()` **inherits** the `sharp_edge` mark onto newly created boundary edges.
After a split, panel gap edges become boundary edges (1 linked face only). Blender's auto-smooth
and custom normals system only evaluates sharp marks at edges shared by 2+ faces — boundary edges
have no neighbour face to interpolate against, so the inherited mark is stored but never evaluated.
Visual result: **no impact**. Unsplit interior (render sharp) edges retain their marks exactly.

### Stability rationale

`bmesh.ops.split_edges()` is a low-level BMesh operator that has been stable since Blender 2.7x.
Custom mesh attributes (EDGE domain, BOOLEAN type) were introduced in Blender 3.2 and are
first-class mesh data. Neither surface is subject to the version churn that affects Geometry
Nodes. This approach will run identically on Blender 4.0, 4.2 LTS, 4.5 LTS, and 5.x without
modification.

A Geometry Nodes implementation was evaluated and rejected: the `GeometryNodeSplitEdges` node
carries confirmed crash bugs (#110005, #110672) and material loss issues (#102711) in the 3.6–4.x
range; and the GN API has broken backward compatibility at every major minor version since 3.0.
For a modifier meant to ship to end users, the stable bmesh path is the correct choice.

## Edge Cases

- **No edges tagged:** Apply Panel Gap Split button is greyed out (poll fails); no error
- **No mesh selected / non-mesh object:** all operators poll-fail silently; buttons greyed out
- **Mark Panel Gap on edges already tagged:** idempotent — re-marking has no effect, count
  is unchanged
- **Apply with Solidify or Bevel already in stack:** the bmesh operation works on the base
  mesh (pre-modifier); the modifier stack is unaffected and re-evaluates on the new topology
- **Apply with Armature modifier:** safe — armature deforms the evaluated mesh, not the base;
  vertex weights are indexed to base mesh vertices; split edges create new vertices that
  inherit weights from the original edge vertices via the bmesh operation's default behavior
- **Applying twice:** second apply finds no `panel_gap` attribute (removed by first apply)
  and poll-fails; no double-split hazard
- **Undo after apply:** single undo step restores original mesh topology and the `panel_gap`
  attribute; Ctrl+Z works as expected
- **Object with no materials:** safe; split operation does not touch material indices
- **Object with multiple materials:** safe; `bmesh.ops.split_edges()` preserves per-face
  material indices; no material reassignment occurs

## Known Limitations

- **Destructive:** Apply Panel Gap Split changes mesh topology and cannot be live-previewed.
  This is intentional — the alternatives (Geometry Nodes modifier) carry known crash risks
  and version instability not appropriate for a shipped addon.
- **One object at a time:** the operator runs on the active object only. Users with multi-object
  panel gap workflows must run it once per object.
- **No angle fallback:** the addon does not implement angle-based edge scoping. The vertex
  selection defines scope entirely. This is by design (YAGNI — the community asked for
  vertex group / selection scope, not angle range).
- **Armature weight inheritance:** new vertices created by the split inherit weights via
  bmesh defaults (average of edge's two original vertices). This is correct for most rigs
  but may require manual weight adjustment on very precise deformation targets.
- **Minimum Blender version:** 4.0 (conservative validated baseline). The underlying API
  (EDGE-domain boolean attributes, `bmesh.ops.split_edges`) exists from Blender 3.2, but
  no testing has been done on 3.x builds.

## Acceptance Criteria

1. Addon installs without error on Blender 4.0+
2. "Mark Panel Gap" and "Clear Panel Gap" appear in the Ctrl+E edge menu in Edit Mode
3. Selecting 5 edges and running Mark Panel Gap sets `panel_gap = True` on those 5 edges;
   mesh attribute is readable via `obj.data.attributes["panel_gap"]`
4. Clear Panel Gap on 3 of those edges sets them to `False`; remaining 2 stay `True`
5. Object Mode N-panel shows correct tagged edge count (matches attribute query)
6. Apply Panel Gap Split button is greyed out when tagged edge count is 0
7. Apply Panel Gap Split on a cube with 4 tagged edges produces a mesh with 12 vertices
   (8 original + 4 split) and no change to untagged edges
8. After apply, the `panel_gap` attribute no longer exists on the mesh
9. Sharp marks on untagged edges are identical before and after apply
10. Materials on all faces are identical before and after apply
11. Ctrl+Z after apply restores original topology and the `panel_gap` attribute in one step
12. Running Apply twice in succession: second invocation is greyed out (poll fails), no crash
13. Operator appears in F3 search under all three names
14. With Solidify modifier present above the operator's effect: stack re-evaluates correctly
    on the post-split base mesh; no crash
