# Announcement Copy — All Edge Overlays

## Short (Twitter / Mastodon / LinkedIn)

New free Blender addon: All Edge Overlays. Show Crease, Bevel Weight, Seam, and Sharp edge marks at once — colour- and dash-coded, parallel where they overlap.

https://kleer001.github.io/funkworks/all_edge_overlays

#Blender #b3d #hardsurface #gamedev

---

## Medium (BlenderArtists / Reddit r/blender)

**Free addon: see all four edge-mark types at once — Crease, Bevel Weight, Seam, Sharp**

Blender shows its edge-mark overlays one at a time. Crease, Bevel Weight, Seam, and Sharp are mutually exclusive toggles in the Overlays dropdown, so comparing them means flipping back and forth. A seam sitting on a creased edge, or a sharp edge missing its bevel weight, doesn't show up until the subdivision, bevel, or UV unwrap downstream goes wrong.

All Edge Overlays draws all four at once. Press N, open the View tab, and click Show under Edge Overlays. Each mark type gets its own colour and dash pattern, and where one edge carries more than one mark the channels draw as parallel lines, so the overlap reads directly. It reads edge attributes and draws lines — no mesh changes, no undo steps, nothing in renders.

It also carries two palettes (a colourblind-safe preset and one read from your active theme), an Occlude toggle for depth-aware hiding, and an Auto quality mode that caches the overlay on heavily-marked meshes so camera navigation doesn't rebuild it every frame.

Free download: https://kleer001.github.io/funkworks/all_edge_overlays

Works on Blender 4.2 LTS+. Viewport-only overlay; your mesh is never touched.

Reply if you'll use this. Upvote if it sounds useful — it helps me prioritise what to ship next.

More free tools at https://github.com/kleer001/funkworks

---

## Long (Newsletter / Blog post intro)

**Comparing edge marks means flipping the overlays one kind at a time**

Blender's viewport can show you where your edge marks sit — Crease, Bevel Weight, Seam, and Sharp — but only one kind at a time. The Overlays dropdown treats them as mutually exclusive. So when a mesh carries several kinds of marks at once — seams for UVs, creases and bevel weights for the subdivision and bevel passes, sharps for shading — comparing them means switching overlays back and forth and remembering what you saw between switches.

On a hard-surface model that gap has a cost. A seam that lands on a creased edge, or a sharp edge that should carry a bevel weight and doesn't, stays out of sight until the subdivision, the bevel, or the UV unwrap downstream goes wrong — and then you're tracing it back by hand.

All Edge Overlays draws all four mark types at once. Enable the addon, press N, open the View tab, and click Show under Edge Overlays. Every marked edge on every visible mesh draws in its own colour and dash pattern. Where one edge carries more than one mark, the channels offset into parallel lines instead of stacking, so an overlap reads as two distinct strokes. For Crease and Bevel Weight, opacity tracks the mark's value, so a weak crease reads fainter than a strong one.

It reads edge attributes and draws lines. No mesh data is modified, no undo step is pushed, and nothing appears in a render. There are two palettes — a colourblind-safe Okabe-Ito preset and one read live from your active theme — and an Occlude toggle that hides marks behind front-facing geometry when you want depth, or shows everything x-ray when you don't. On heavily-marked meshes an Auto quality mode caches the overlay and redraws it each frame, so navigation does not rebuild the dash geometry from scratch as the marked-edge count grows.

It's free and open source.

Download it free: https://kleer001.github.io/funkworks/all_edge_overlays

Hit reply if comparing edge marks is part of your modeling routine — knowing how many people bump into this helps me prioritise what to ship next.

More free tools at https://github.com/kleer001/funkworks
