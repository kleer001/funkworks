# Marketplace Listing — Subdivide Select New

## Short Description (160 chars)
Subdivide and immediately operate on the new geometry. No Checker Deselect tricks — only the new vertices and edges are left selected.

## Long Description

Blender's Subdivide leaves your original selection intact. If your next move is to bevel, slide, or extrude only the new midpoint geometry, you have to isolate it by hand: Checker Deselect, Select Less, Invert — none of them land cleanly.

**How it works:**
- Select faces or edges in Edit Mode
- Mesh menu → **Subdivide (Select New)** (or right-click)
- The new vertices and edges are now your active selection — run your next operator

Exposes the full parameter set of the built-in Subdivide (Number of Cuts, Smoothness, Create N-Gons, Quad Corner Type, Fractal, Along Normal, Random Seed). Full undo support. The active vert/edge/face selection mode is preserved.

## Features

- One-click subdivide that leaves only the new geometry selected
- Same full parameter set as built-in Subdivide (Number of Cuts, Smoothness, Create N-Gons, Quad Corner Type, Fractal, Along Normal, Random Seed)
- Lives in the Mesh menu and right-click context menu — also searchable via F3
- Preserves vert / edge / face selection mode
- Full undo support

## Requirements

- Blender 4.0 or later

## Tags

modeling, mesh, subdivide, edit-mode, topology, workflow
