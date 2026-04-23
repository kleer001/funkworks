# Zoom / Radial Blur COP

Zoom blur and spin blur in one Houdini Copernicus node — switch between radial scale and arc modes, place the center anywhere, tune sample count for quality vs. speed.

## The Problem

Getting a zoom blur or spin blur in Houdini Copernicus means writing your own wrangle: figuring out the aspect-ratio-corrected `@P` coordinate space, implementing the radial sampling loop, converting pixel coordinates to image space, and threading the alpha channel through `volumesamplep` without losing it. Every comp that needs this effect starts from scratch.

## The Solution

Zoom / Radial Blur COP wraps both blur modes in a single node. Connect a source image, pick a mode, set the reach or arc angle, and optionally move the center. The node handles the `@P` math and alpha preservation internally.

Find it in any COP network under the tab menu: **Zoom / Radial Blur COP**.

## Inputs

| # | Name | Description |
|---|------|-------------|
| 0 | Source | Image to blur |

## Parameters

**Blur Mode** — which blur to apply:

| Mode | Description |
|------|-------------|
| Zoom Blur | Samples radially outward from center — creates a scale/explosion streak |
| Radial Blur | Samples along an arc at constant distance from center — creates a spin/rotation smear |

**Samples** — number of samples along the blur path. More samples = smoother result, slower cook. 20 for layout, 60–80 for finals.

**Blur Pixels** _(Zoom Blur only)_ — radial reach of the blur in pixels. Hidden when Radial Blur is active.

**Blur Angle** _(Radial Blur only)_ — arc angle in degrees for the spin blur. Hidden when Zoom Blur is active.

**Center Space** — coordinate system for the blur center:

| Mode | Description |
|------|-------------|
| Screen Space | Normalized −1..1 on X (0 = image center). Y is aspect-corrected. |
| Pixels | Absolute pixel coordinates. (0, 0) = bottom-left corner. |

**Center X / Center Y** — blur center in screen space (hidden in Pixel mode).

**Center X (px) / Center Y (px)** — blur center in pixels (hidden in Screen Space mode).

## Installation

1. Download `zoom_blur_cop.hda` from the [latest GitHub release](https://github.com/kleer001/funkworks/releases/latest)
2. In Houdini: **Assets > Install Asset Library**
3. Select `zoom_blur_cop.hda` and click **Install**
4. The node appears in any COP network as **Zoom / Radial Blur COP**

> **License notice.** The pre-built HDA was compiled under a Houdini Indie/Apprentice license. Loading it in a full Houdini FX session will flag the scene as limited-commercial. FX users should build from source — see below.

## Building from Source

1. Download `build_zoom_blur_cop.py` from the [latest GitHub release](https://github.com/kleer001/funkworks/releases/latest)
2. Run with hython:
   ```bash
   hython build_zoom_blur_cop.py
   ```
3. The script writes `zoom_blur_cop.hda` alongside itself

Requires Houdini 20.5+ (any edition).

## Compatibility

- Houdini 20.5+
- Copernicus (COP) networks
- Any edition: Apprentice, Indie, Core, FX

## Notes

- `@P` coordinate space inside the wrangle: `@P.x ∈ [−1, +1]`, `@P.y ∈ [−h/w, +h/w]` (aspect-corrected, not clamped on Y).
- Alpha is preserved by sampling `"C"` via `volumesamplep` (returns `vector4`) — `"A"` is not a separate layer in Copernicus.
- Pixel mode Y=0 is bottom-left. To target a point N px from the top of an H-tall image, set Center Y (px) to H − N.
- The pre-built HDA carries an Indie/Apprentice compilation flag. FX users should build from source.
