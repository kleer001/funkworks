# Marketplace Listing — All Edge Overlays

## Short Description (160 chars)

See Crease, Bevel Weight, Seam, and Sharp marks at once — colour- and dash-coded, parallel where they overlap. Blender shows them one at a time; this shows all four.

## Long Description

Blender displays its edge-mark overlays — Crease, Bevel Weight, Seam, and Sharp — as mutually exclusive toggles, one at a time. A modeler who marks a mesh several ways has to flip overlays back and forth to compare them. Overlaps and conflicts — a seam on a creased edge, a sharp that should have a bevel weight — stay out of sight until something downstream breaks.

This addon draws all four mark types at once.

**How it works:**

1. Enable the addon and press N in the viewport
2. Open the View tab and click Show under Edge Overlays
3. Every marked edge draws in its own colour and dash pattern; coincident marks draw as parallel lines
4. Toggle channels, switch palette, or turn on Occlude as needed

It reads edge attributes and draws lines — no mesh data is modified, no undo step is pushed, and nothing appears in a render. Settings are stored on the Scene and saved with the file.

## Features

- **All four at once** — Crease, Bevel Weight, Seam, and Sharp drawn together, each with a distinct colour and dash pattern
- **Parallel where they coincide** — channels offset perpendicular to the edge, so two or three marks on one edge read as separate lines instead of a single muddy stroke
- **Value fade** — Crease and Bevel Weight opacity scales with the mark's value, so weak marks read fainter than strong ones
- **Two palettes** — a Colourblind-Safe Okabe-Ito preset and a Blender Native preset read from the active theme; each swatch stays individually editable
- **Depth occlusion** — an Occlude toggle hides marks behind front-facing geometry; off by default for x-ray visibility
- **Scales to dense meshes** — an Auto quality mode caches the overlay on heavy meshes so camera navigation stays smooth as the marked-edge count grows

## Requirements

- Blender 4.2 LTS or later

## Tags

mesh, modeling, hard-surface, edge-marks, overlay, viewport, seam, crease
