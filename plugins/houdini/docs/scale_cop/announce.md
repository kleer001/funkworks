# Announcement Copy — Scale COP

## Short (Twitter / Mastodon / LinkedIn)

Houdini's Resample COP only stretches. Scale COP adds letterbox, fill, crop, tiling, and size-reference input — in one free node.

https://github.com/kleer001/funkworks/releases/tag/scale_cop-v0.1.99

#Houdini #VFX #Compositing #COP #SideFX

---

## Medium (SideFX Forums / OdForce)

**Scale COP — free Houdini node for fit modes, tiling, and canvas resize (letterbox, fill, crop)**

Houdini's built-in Resample COP only does Stretch. If you want a letterboxed fit, a fill that crops to the canvas edge, or a tiled repeat with mirroring, you're chaining nodes and computing UV offsets by hand — and redoing that math every time a resolution changes.

Scale COP is a free HDA that wraps the whole thing in one node. Pick a target resolution (preset, explicit, or pulled from a size-reference input), choose a fit mode, optionally tile, pick a filter. Done. No manual offset math.

**Fit modes:** Distort, Fit (letterbox), Fill (crop to fill), Width, Height, None (1:1 pixel)
**Tile modes:** None, Repeat, Mirror X, Mirror Y, Mirror Both (with UV offset)
**Filters:** Point, Bilinear, Box, Bartlett, Catmull-Rom, Mitchell, B-Spline, Auto

Free download: https://github.com/kleer001/funkworks/releases/tag/scale_cop-v0.1.99

Houdini 20+, any edition. FX users: a build script is included so you can compile the HDA under your own license and avoid the Indie/Apprentice flag.

First Houdini release from Funkworks — a small open-source collection of free DCC tools built from real workflow problems. Feedback and bug reports welcome.

---

## Long (Blog / Newsletter)

**The Houdini COP I got tired of rebuilding from scratch**

Every time I needed to fit an image into a canvas in Houdini — letterbox a 4:3 source into a 16:9 output, tile a texture with mirroring, or just scale something to a specific resolution without distorting it — I'd rebuild the same node chain. A Resample in Stretch mode to hit the target resolution, a Transform to position the content, a Merge to composite it over a background, maybe a second Resample to handle tiling math. Then when the resolution changed, redo the offsets.

Resample COP is fast and solid but it only does Stretch. The fit mode logic — the part that says "scale until the source fits inside the canvas, preserve the aspect ratio, fill the rest with black" — isn't there.

So I built Scale COP: a single Copernicus node with six fit modes (Distort, Fit, Fill, Width, Height, None), five tile modes (with UV offset), eight reconstruction filters, and a size-reference input so the output resolution can be driven by any upstream node. The fit math runs in a VEX wrangle so it stays exact regardless of resolution.

It's free. It's one node.

Download it free: https://github.com/kleer001/funkworks/releases/tag/scale_cop-v0.1.99

Houdini 20+, any edition. FX users get a build script to compile the HDA clean under their own license.

First Houdini release from Funkworks — a small open-source collection of free DCC tools I'm building from real workflow friction. Already shipping Blender addons; this is the first node for Houdini. If something's broken or missing, please say so.
