# Announcement Copy — Zoom / Radial Blur COP

## Short (Twitter / Mastodon / LinkedIn)

Every Copernicus zoom blur starts from scratch — aspect-corrected @P math, radial sampling, alpha through volumesamplep. Not anymore.

New free Houdini HDA: Zoom / Radial Blur COP. Two blur modes, moveable center, tunable samples.

https://github.com/kleer001/funkworks/releases/tag/zoom_blur_cop-v0.1.117

#Houdini #VFX #Compositing #COP #SideFX

---

## Medium (SideFX Forums / OdForce)

**Zoom / Radial Blur COP — free Houdini node for zoom and spin blur in Copernicus**

Every time I need a zoom blur or spin blur in a COP network I end up writing the same wrangle: work out the aspect-corrected `@P` coordinate space, build the radial sampling loop, use `volumesamplep` so alpha doesn't drop. It's 30 lines of boilerplate to get a result that should be a single node.

Zoom / Radial Blur COP is that node. Connect an image, pick a mode, done.

**Blur modes:** Zoom Blur (radial scale streaks from center) or Radial Blur (spin/arc smear at constant radius)
**Center control:** Screen Space (−1..1, 0 = image center) or Pixels (absolute coordinates, Y=0 at bottom-left)
**Samples:** 1–256, slider with strict minimum — raise for finals, lower for layout speed

Both modes share the same center controls. Switching modes hides the irrelevant parameter (Blur Pixels vs. Blur Angle). Alpha is preserved throughout via `volumesamplep`.

Free download: https://github.com/kleer001/funkworks/releases/tag/zoom_blur_cop-v0.1.117

Houdini 20.5+, any edition. FX users: a build script is included to compile the HDA clean under your own license.

🐜 More free tools at https://github.com/kleer001/funkworks

---

## Long (Blog / Newsletter)

**Zoom / Radial Blur COP: the boilerplate wrangle you've written five times**

Every time I need a zoom blur or spin blur in Houdini Copernicus, the workflow is the same. Open a Wrangle COP, write the sampling loop, remember that `@P.x` runs −1 to +1 across the width but Y is aspect-corrected and not clamped, remember that `volumesample` drops alpha so you have to use `volumesamplep` and manually split the `vector4` result, add a center offset, add a pixel-coordinate conversion branch for when you need exact placement. Then save it in a digital asset before you lose it.

It's 30–40 lines of setup code for something that should be a single node.

So I built Zoom / Radial Blur COP. It ships two modes:

**Zoom Blur** samples radially outward from a center point — the classic explosion or scale-rush streak. Blur Pixels controls the radial reach in image pixels, so the effect is resolution-aware: 600 px on a 1920-wide image is about a third of the frame.

**Radial Blur** samples along an arc at constant radius — a true spin or rotation smear. Blur Angle controls the arc in degrees. Pixels close to center appear nearly sharp; distant pixels show longer arcs because the arc length grows with radius.

Both modes share the same center controls. Center Space toggles between Screen Space (normalized −1..1, 0=center, aspect-corrected on Y) and Pixels (absolute coordinates, Y=0 at bottom-left). Switching modes hides the irrelevant blur parameter so the interface stays clean.

Samples is a straight quality knob: more samples = smoother result, slower cook. 20 works fine for layout. 60–80 for most final renders. The math scales linearly so there are no hidden gotchas.

Alpha is preserved. The wrangle uses `volumesamplep` which returns `vector4` — the alpha rides in the `.w` component of the color layer and is written back to `@A` explicitly. Nothing disappears on compositing.

Download it free: https://github.com/kleer001/funkworks/releases/tag/zoom_blur_cop-v0.1.117

Houdini 20.5+, any edition. FX users get a build script (`build_zoom_blur_cop.py`) to compile the HDA clean under their own license and avoid the Indie/Apprentice flag.

🐜 More free tools at https://github.com/kleer001/funkworks
