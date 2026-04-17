# Selective Edge Split

You mark sharp edges for rendering. You mark sharp edges for panel gaps. Blender treats them the same — and Edge Split can't tell them apart.

## The Problem

Hard-surface artists routinely carry two kinds of sharp edges: edges that control smooth shading, and edges that define physical panel gaps between body panels. When you need a panel gap split, you're stuck: Blender's Edge Split modifier acts on every sharp edge globally.

The workaround is destructive. Clear all sharps, mark only the panel gap edges, apply Edge Split, then manually re-mark every render sharp you just erased. On a vehicle mesh with 80 render sharp loops, one panel gap adjustment means 100+ manual actions and a lost modifier stack position.

## The Solution

Tag your panel gap edges once with **Ctrl+E → Mark Panel Gap**. When you're ready to commit the cut, run **Apply Panel Gap Split** from the N-panel. Only the tagged edges are split. Every render sharp stays exactly where it was.

The tag lives as a boolean edge attribute (`panel_gap`) on your mesh — it survives Edit Mode / Object Mode transitions, file saves, and Undo. It's removed automatically after apply, so you can never accidentally double-split.

## Installation

1. Download `selective_edge_split.py`
2. In Blender: **Edit > Preferences > Add-ons > Install**
3. Select the downloaded file and enable the addon

## Usage

**Tagging panel gap edges:**

1. Enter Edit Mode, select the edges that form panel gaps
2. `Ctrl+E` → **Mark Panel Gap**
3. Repeat for all panel gap edges across the mesh

**Applying the split:**

1. Return to Object Mode
2. Open the N-panel (**N key**) → **Item** tab → **Panel Gap** section
3. Verify the tagged edge count, then click **Apply Panel Gap Split**

**Removing tags without splitting:**

- Select edges in Edit Mode → `Ctrl+E` → **Clear Panel Gap**

All three operators are also searchable via **F3**.

## Distribution

- **GitHub Releases** — primary distribution; download the `.py` file directly from the latest release

## Compatibility

- Blender 4.0+
- Uses `bmesh.ops.split_edges()` (stable since Blender 2.7x) and EDGE-domain boolean attributes (introduced in Blender 3.2)

## Notes

- **Destructive by design.** Apply Panel Gap Split changes mesh topology. There is no live preview. This is intentional — the Geometry Nodes Split Edges alternative carries confirmed crash bugs and breaks backward compatibility on every minor version.
- **One object at a time.** The apply operator acts on the active object only.
- **Modifier stack safe.** The split operates on the base mesh. Solidify, Bevel, Armature, and other modifiers are unaffected and re-evaluate on the new topology.
- **Armature rigs.** New vertices created by the split inherit weights (averaged from the original edge's two vertices). Correct for most rigs; precise deformation targets may need a manual weight touch-up.
