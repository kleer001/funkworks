# Release Notes — Zoom / Radial Blur COP v0.1.117

## Short Description

Free Houdini COP node: zoom blur and spin blur in one node, with moveable center and tunable sample count.

## What It Does

Every comp that needs a zoom or spin blur in Copernicus requires writing a wrangle from scratch — working out the aspect-corrected `@P` space, sampling along the radial direction, preserving alpha through `volumesamplep`. It's the same boilerplate every time.

Zoom / Radial Blur COP replaces that with one node:

- Connect a source image and choose **Zoom Blur** (radial scale streaks) or **Radial Blur** (spin/arc smear)
- Set the reach in pixels or the arc angle in degrees
- Place the center in screen space (−1..1) or exact pixel coordinates
- Raise **Samples** for smooth finals, lower for fast layout previews

**Blur modes:** Zoom Blur (explosion/scale), Radial Blur (spin/arc)
**Center:** Screen Space (normalized) or Pixels (absolute, Y=0 at bottom-left)
**Sample count:** 1–256, linear cook-time scaling

All parameters are non-destructive. Switching modes hides irrelevant controls.

## Features

- **2 blur modes** — Zoom Blur (radial scale) and Radial Blur (spin arc), switchable without re-wiring
- **Moveable center** — screen space or pixel coordinate mode with conditional parameter visibility
- **Alpha-safe sampling** — uses `volumesamplep` to preserve the full RGBA vector; alpha is never dropped
- **Tunable quality** — Samples parameter from 1 to 256, shown in a slider with strict minimum

## Requirements

- Houdini 20.5 or later (any edition)
- Works in Copernicus (COP) networks

## Assets

- `zoom_blur_cop.hda` — pre-built HDA, ready to install via **Assets > Install Asset Library**
- `build_zoom_blur_cop.py` — build script for compiling under your own Houdini license (required for FX users who need an unencumbered HDA)

## Tags

houdini, cop, copernicus, image, compositing, blur, zoom-blur, radial-blur, vex, hda
