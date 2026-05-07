# Announcement Copy — Subdivide Select New

## Medium (BlenderArtists / Reddit r/blender)

**Free addon: Subdivide that leaves only the new geometry selected**

Small papercut, but it adds up: when you subdivide an edge loop or face ring, you must manually isolate the new midpoint verts and inner edges before you can bevel, slide, or extrude them. Checker Deselect rarely lands right. Select Less strips the boundary. Invert requires multiple manual steps to isolate the new geometry.

**Subdivide (Select New)** does what Subdivide does, then leaves only the new vertices and edges selected. Mesh menu, right-click menu, or F3. The redo panel exposes the same parameters as the built-in Subdivide.

Free download: [link]

Works on Blender 4.0+. Full undo support. Preserves vert/edge/face selection mode.

More free tools at https://github.com/kleer001/funkworks

---

## Long (Newsletter / Blog post intro)

**The Subdivide papercut**

You ran Subdivide. The midpoint verts and inner edges are there. Now you want to bevel them, or slide them, or extrude them — and Blender kept your *original* selection active, with the new geometry mixed in. So before you can do anything, you have to isolate what was just added.

The usual workarounds don't work cleanly. Checker Deselect depends on traversal order; on a face ring it grabs every other element regardless of whether it's new or original. Select Less peels off the boundary, which doesn't isolate the new geometry. Select Inverse requires re-selecting the new geometry manually. The workflow becomes tedious.

**Subdivide (Select New)** does the same subdivide, then deselects the original geometry and selects only the vertices and edges that were just created. Your next operator acts on the new cuts and nothing else.

It lives in the Mesh menu and the right-click context menu in Edit Mode, and it's searchable via F3. The redo panel exposes the same full parameter set as the standard Subdivide — Number of Cuts, Smoothness, Create N-Gons, Quad Corner Type, Fractal, Along Normal, Random Seed. The vert/edge/face selection mode you were in is preserved.

It's free and open source. ~80 lines.

Download it free: [link]

More free tools at https://github.com/kleer001/funkworks
