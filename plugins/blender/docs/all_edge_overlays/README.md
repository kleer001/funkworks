# All Edge Overlays

See Crease, Bevel Weight, Seam, and Sharp edge marks at the same time — each in its own colour and dash pattern.

## The Problem

Blender can display edge-mark overlays — Crease, Bevel Weight, Seam, and Sharp — but only one at a time. The Overlays dropdown exposes them as mutually exclusive toggles. A modeler who marks the same mesh several ways — seams for UVs, creases and bevel weights for the subdivision and bevel passes, sharps for shading — has to flip overlays back and forth to compare them, holding the picture in their head.

On a hard-surface mesh that gap costs work. A seam that lands on a creased edge, or a sharp that should carry a bevel weight and doesn't, stays out of sight until something downstream breaks.

## The Solution

Enable the addon, press **N** in the viewport, open the **View** tab, and click **Show** under **Edge Overlays**. All four mark types draw at once across every visible mesh, each with its own colour and dash pattern. Where one edge carries more than one mark, the channels draw as parallel offset lines instead of stacking, so the overlap reads directly.

The addon only reads edge attributes and draws lines. It never changes mesh data, pushes an undo step, or appears in a render.

## Installation

1. Download `all_edge_overlays.py`
2. In Blender: **Edit > Preferences > Add-ons > Install**
3. Select the downloaded file and enable the addon

## Usage

1. Mark edges as usual — **Ctrl+E** for Seam and Sharp, the Edge Data transforms for Crease and Bevel Weight
2. Press **N** → **View** tab → **Edge Overlays** → **Show**
3. Use the per-channel checkboxes to isolate a question — for example, turn off everything except Seam and Crease to see only where those two meet
4. Switch **Palette** between Colourblind-Safe and Blender Native, or click a swatch to recolour one channel
5. **Occlude** is on by default, hiding marks behind front-facing geometry; turn it off to see every mark x-ray style

## Distribution

- **GitHub Releases** — primary distribution; download the `.py` file directly from the latest release

## Compatibility

- Blender 4.2 LTS or later
- Reads crease and bevel weight as EDGE-domain float attributes (`crease_edge`, `bevel_weight_edge`, the model introduced in Blender 4.0) and seam/sharp as edge booleans
- Draws through the `gpu` module on a live viewport; no effect in background renders

## Notes

- **Pure visualization.** No mesh data is modified, no undo step is pushed, and the overlay never shows up in a render.
- **Coincident marks draw parallel.** Channels are offset perpendicular to the edge so two or three marks on one edge read as separate lines.
- **Value fade.** For Crease and Bevel Weight, line opacity scales with the mark's value, so a weak crease reads fainter than a strong one. Toggle it off with **Fade Weak Marks**.
- **Base-cage marks.** Marks are drawn on the base mesh, matching Blender's native Edit-Mode overlays, not the post-modifier result.
- **Three quality tiers.** **Auto** picks Balanced (crisp, screen-stable dashes) on lighter meshes and a cached Accurate tier on heavy ones, where the overlay is built once and redrawn each frame so navigation stays smooth as the marked-edge count grows. **Fast** is a manual option for the weakest hardware.
- **Settings persist.** Configuration is stored on the Scene and saved with the .blend file.
