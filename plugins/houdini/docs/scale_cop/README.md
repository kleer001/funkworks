# Scale COP

Resize and reposition an image within a target canvas, with independent control over fit mode, tiling, and resampling filter — all inside a single Houdini Copernicus node.

## The Problem

Houdini's built-in Resample COP only offers Stretch mode: it always distorts the source to fill the output canvas. Getting a letterboxed fit, a cropped fill, or a pixel-accurate 1:1 placement requires manually chaining multiple nodes and computing offsets by hand — and recalculating everything when the resolution changes.

## The Solution

Scale COP wraps that workflow into one node. Connect a source image, pick a target resolution and fit mode, and the node handles the math. A second optional input accepts a size reference image so the output canvas always matches another node in the network.

Find it in any COP network under the tab menu: **Scale COP**.

## Inputs

| # | Name | Description |
|---|------|-------------|
| 0 | Source | Image to scale |
| 1 | Size Reference | Optional. When **Use Size Reference** is enabled, sets the output canvas resolution |

## Parameters

**Scale Mode** — how the output canvas size is determined: Preset (standard resolutions), Explicit (width × height), Uniform (single multiplier), or Non-Uniform (independent X/Y).

**Fit Mode** — how the source is placed inside the canvas:

| Mode | Behaviour |
|------|-----------|
| Distort | Stretch to fill, ignoring aspect ratio |
| Fit | Scale to fit inside canvas; letterbox with Background Color |
| Fill | Scale to fill canvas; crop excess |
| Width | Match canvas width; letterbox top/bottom |
| Height | Match canvas height; letterbox left/right |
| None | 1:1 pixel scale, centered |

**Tile Mode** — repeat the source beyond its placed bounds: None, Repeat, Mirror X, Mirror Y, Mirror Both.

**Filter** — reconstruction filter: Auto, Point, Bilinear, Box, Bartlett, Catmull-Rom, Mitchell, B-Spline.

## Installation

1. Download `scale_cop.hda` from the [latest GitHub release](https://github.com/kleer001/funkworks/releases/latest)
2. In Houdini: **Assets > Install Asset Library**
3. Select `scale_cop.hda` and click **Install**
4. The node appears in any COP network as **Scale COP**

> **License notice.** The pre-built HDA was compiled under a Houdini Indie/Apprentice license. Loading it in a full Houdini FX session will flag the scene as limited-commercial. If you need an unencumbered HDA, build from source — see below.

## Building from Source

If you need a clean HDA compiled under your own license:

1. Download `build_scale_cop.py` from the [latest GitHub release](https://github.com/kleer001/funkworks/releases/latest)
2. Run with hython:
   ```bash
   hython build_scale_cop.py
   ```
3. The script writes `scale_cop.hda` alongside itself

Requires Houdini 20+ (any edition).

## Compatibility

- Houdini 20.0+ (Copernicus / COP2 networks)
- Any edition: Apprentice, Indie, Core, FX

## Notes

- The pre-built HDA carries an Indie/Apprentice compilation flag. FX users should build from source.
- `@xres` / `@yres` are always 0 inside COP wrangle context — Scale COP uses hidden spare parameters to pass resolution to VEX.
- Tiling uses voxel-center correction to avoid bilinear bleed at tile boundaries.
