# Announcement Copy — Scale COP

## Short (Twitter / Mastodon / LinkedIn)

Houdini's Resample COP only stretches. Scale COP adds letterbox, fill, crop, tiling, and size-reference input — in one free node.

https://github.com/kleer001/funkworks/releases/tag/scale_cop-v0.1.99

#Houdini #VFX #Compositing #COP #SideFX

---

## Medium (SideFX Forums / OdForce)

**Scale COP — free Houdini node for fit modes, tiling, and canvas resize (letterbox, fill, crop)**

Houdini's built-in Resample COP only does Stretch. If you want a letterboxed fit, a fill that crops to the canvas edge, or a tiled repeat with mirroring, you're chaining nodes and computing UV offsets by hand — and redoing that math every time a resolution changes.

Scale COP is a free HDA that wraps the whole thing in one node. Pick a target resolution, choose a fit mode, optionally tile, pick a filter. Done. No manual offset math.

**Fit modes:** Distort, Fit (letterbox), Fill (crop to fill), Width, Height, None (1:1 pixel)
**Tile modes:** None, Repeat, Mirror X, Mirror Y, Mirror Both (with UV offset)
**Filters:** Point, Bilinear, Box, Bartlett, Catmull-Rom, Mitchell, B-Spline, Auto
**Size reference input:** connect any upstream node to drive the output resolution automatically — no manual width/height entry when your canvas size changes

Free download: https://github.com/kleer001/funkworks/releases/tag/scale_cop-v0.1.99

Houdini 20+, any edition. FX users: a build script is included so you can compile the HDA under your own license and avoid the Indie/Apprentice flag.

First Houdini release from Funkworks — a small open-source collection of free DCC tools built from real workflow problems. Feedback and bug reports welcome.

🐜 More free tools at https://github.com/kleer001/funkworks

---

## Long (Blog / Newsletter)

**Scale COP: the fit modes and tiling that Houdini's Resample COP doesn't have**

Houdini's Resample COP only does Stretch. To letterbox a 4:3 source into a 16:9 canvas, fill without distorting, or tile with mirroring, you're chaining Resample + Transform + Merge and computing UV offsets by hand. When the resolution changes, you redo the math.

Scale COP fills that gap. It's one node.

So I built Scale COP: a single Copernicus node with six fit modes (Distort, Fit, Fill, Width, Height, None), five tile modes (with UV offset), and eight reconstruction filters. There's also a second input — connect any node and enable "Use Size Reference" to pull the output resolution directly from that image. No more manually updating width and height when your pipeline's canvas size changes upstream.

It's free. It's one node.

Download it free: https://github.com/kleer001/funkworks/releases/tag/scale_cop-v0.1.99

Houdini 20+, any edition. FX users get a build script to compile the HDA clean under their own license.

First Houdini release from Funkworks — a small open-source collection of free DCC tools I'm building from real workflow friction. Already shipping Blender addons; this is the first node for Houdini. If something's broken or missing, please say so.

🐜 More free tools at https://github.com/kleer001/funkworks
