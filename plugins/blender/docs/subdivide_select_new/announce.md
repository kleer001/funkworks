# Announcement Copy — Subdivide Select New

## Medium (BlenderArtists / Reddit r/blender)

**Free addon: Subdivide that leaves only the new geometry selected**

Small papercut: when you subdivide an edge loop or face ring, you must manually isolate the new midpoint verts and inner edges before you can bevel, slide, or extrude them. Checker Deselect selects every other element on a face ring regardless of whether it's new or original. Select Less strips the boundary. Invert requires multiple manual steps to isolate the new geometry.

**Subdivide (Select New)** does what Subdivide does, then leaves only the new vertices and edges selected. Mesh menu, right-click menu, or F3. The redo panel exposes the same parameters as the built-in Subdivide.

Free download: https://kleer001.github.io/funkworks/subdivide_select_new

Works on Blender 4.0+. Full undo support. Preserves vert/edge/face selection mode.

More free tools at https://github.com/kleer001/funkworks

---

## Long (Newsletter / Blog post intro)

**The Subdivide papercut**

When you run Subdivide, the midpoint verts and inner edges are there. If you want to bevel, slide, or extrude them, Blender's *original* selection is still active, with the new geometry mixed in. The new geometry has to be isolated by hand before any follow-up operator will act only on it.

Checker Deselect depends on traversal order; on a face ring it grabs every other element regardless of whether it's new or original. Select Less peels off the boundary, which doesn't isolate the new geometry. Select Inverse requires re-selecting the new geometry manually. Each step requires manual filtering or re-selection.

**Subdivide (Select New)** does the same subdivide, then deselects the original geometry and selects only the vertices and edges that were just created. Your next operator acts on the new cuts and nothing else.

It lives in the Mesh menu and the right-click context menu in Edit Mode, and it's searchable via F3. The redo panel exposes the same full parameter set as the standard Subdivide — Number of Cuts, Smoothness, Create N-Gons, Quad Corner Type, Fractal, Along Normal, Random Seed. The vert/edge/face selection mode you were in is preserved.

It's free and open source. ~80 lines.

Download it free: https://kleer001.github.io/funkworks/subdivide_select_new

More free tools at https://github.com/kleer001/funkworks
