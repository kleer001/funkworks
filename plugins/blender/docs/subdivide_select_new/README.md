# Subdivide Select New

Subdivide a mesh and immediately operate on the new geometry — without hunting through Checker Deselect tricks to isolate it.

## The Problem

Run **Subdivide** on a face, edge loop, or face ring and Blender leaves the original selection intact: the new midpoint vertices and inner edges are added, but they're now mixed in with everything you already had selected. If your next move is to bevel, scale, slide, or extrude *only the new geometry*, you have to isolate it manually.

The standard workarounds are imperfect:

- **Checker Deselect** depends on traversal order and rarely lands on exactly the new edges.
- **Select Less** strips the boundary, not the interior.
- **Select Inverse** then re-fixing the selection is a five-step dance.

It's a small papercut, but it shows up every time you cut a panel loop, add detail to a subdivision, or refine a topology pass.

## The Solution

Run **Subdivide (Select New)** instead. It does exactly what Subdivide does, then deselects the original geometry and selects only the vertices and edges that were just created. Your next operator acts on the new cuts and nothing else.

The operator lives in the **Mesh menu** and the **right-click context menu** in Edit Mode, and is searchable via **F3**. The redo panel exposes the same `Number of Cuts` and `Smoothness` parameters as the standard Subdivide.

## Installation

1. Download `subdivide_select_new.py`
2. In Blender: **Edit > Preferences > Add-ons > Install**
3. Select the downloaded file and enable the addon

## Usage

1. Enter Edit Mode and select the geometry you want to cut (faces, edge loops, etc.)
2. **Mesh menu → Subdivide (Select New)** — or right-click → Subdivide (Select New)
3. Adjust **Number of Cuts** / **Smoothness** in the redo panel if needed
4. The new vertices and edges are now your active selection — apply the next operator

## Compatibility

- Blender 4.0+
- Uses `bmesh` element tags (stable since Blender 2.7x) and `bpy.ops.mesh.subdivide`

## Notes

- The active selection mode (vertex / edge / face) is preserved. Selection is flushed across modes so the new geometry shows up correctly whichever mode you're in.
- Works with multi-face selections, edge loops, and face rings — anything `Subdivide` itself accepts.
- Full undo support via `bl_options = {'REGISTER', 'UNDO'}`.
