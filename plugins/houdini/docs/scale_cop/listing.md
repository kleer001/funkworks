# Release Notes — Scale COP v0.1.99

## Short Description

Free Houdini COP node: scale, reposition, and fit images into any canvas with letterbox, fill, crop, and tiling — in a single node.

## What It Does

Houdini's built-in Resample COP only stretches. Getting a letterboxed fit, a cropped fill, or a tiled repeat means chaining nodes and hand-computing offsets — and redoing it whenever the resolution changes.

Scale COP replaces that chain with one node:

- Connect a source image and pick a target resolution (preset, explicit, or by reference from another node)
- Choose a fit mode: **Distort**, **Fit** (letterbox), **Fill** (crop to fill), **Width**, **Height**, or **None** (1:1 pixel)
- Optionally tile: Repeat, Mirror X, Mirror Y, or Mirror Both
- Pick a reconstruction filter: Bilinear, Catmull-Rom, Mitchell, and more

Resolution, fit, tiling, and filtering all update non-destructively. No manual offset math.

## Features

- **6 fit modes** — Distort, Fit (letterbox), Fill (crop), Width, Height, None (1:1)
- **5 tile modes** — None, Repeat, Mirror X, Mirror Y, Mirror Both, with UV offset control
- **Size reference input** — drive output resolution from any upstream node
- **8 reconstruction filters** — Point through B-Spline, with an Auto mode

## Requirements

- Houdini 20.0 or later (any edition)
- Works in Copernicus (COP2) networks

## Assets

- `scale_cop.hda` — pre-built HDA, ready to install via **Assets > Install Asset Library**
- `build_scale_cop.py` — build script for compiling under your own Houdini license (required for FX users who need an unencumbered HDA)

## Tags

houdini, cop, image, compositing, resize, scale, fit, letterbox, tiling, vex
