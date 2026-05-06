# Marketplace Listing — Subdivide Select New

## Short Description (160 chars)
Subdivide and immediately operate on the new geometry. No Checker Deselect tricks — only the new vertices and edges are left selected.

## Long Description

Blender's Subdivide leaves your original selection intact. If your next move is to bevel, slide, or extrude only the new midpoint geometry, you have to isolate it by hand: Checker Deselect, Select Less, Invert — none of them land cleanly.

**How it works:**
- Select faces or edges in Edit Mode
- Mesh menu → **Subdivide (Select New)** (or right-click)
- The new vertices and edges are now your active selection — run your next operator

Same `Number of Cuts` and `Smoothness` parameters as the built-in Subdivide. Full undo support. The active vert/edge/face selection mode is preserved.

## Features

- One-click subdivide that leaves only the new geometry selected
- Same parameters as built-in Subdivide (`Number of Cuts`, `Smoothness`)
- Lives in the Mesh menu and right-click context menu — also searchable via F3
- Preserves vert / edge / face selection mode
- Full undo support

## Requirements

- Blender 4.0 or later

## Tags

modeling, mesh, subdivide, edit-mode, topology, workflow
