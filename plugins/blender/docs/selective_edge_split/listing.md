# Marketplace Listing — Selective Edge Split

## Short Description (160 chars)

Split only your panel gap edges — not your render sharps. Tag edges with Ctrl+E, apply when ready. Modifier stack and sharp marks untouched.

## Long Description

Hard-surface modelers carry two kinds of sharp edges: edges for smooth shading and edges for panel gap cuts. Blender's Edge Split modifier can't tell them apart, forcing a destructive workaround: clear all sharps, mark panel gaps only, apply the split, then painstakingly re-mark every render sharp you just erased. On a complex mesh, one panel gap adjustment costs 100+ manual steps.

**How it works:**

1. Select panel gap edges in Edit Mode
2. Ctrl+E → Mark Panel Gap (tags them with a `panel_gap` boolean attribute)
3. Repeat across the mesh — tags survive mode switches and file saves
4. Object Mode → N-panel → Apply Panel Gap Split

Only the tagged edges are split. Every render sharp stays exactly where it was. The tag is removed automatically after apply — no double-split risk.

Full undo support. No setup. Works alongside Solidify, Bevel, and Armature modifiers.

## Features

- **Scoped split** — tags panel gap edges independently of sharp marks; only tagged edges are split
- **Non-destructive tagging** — the `panel_gap` attribute survives Edit/Object mode switches, file saves, and Undo until you're ready to apply
- **Live edge count** — the N-panel shows how many edges are currently tagged; Apply button greys out when there's nothing to split
- **Ctrl+E integration** — Mark Panel Gap and Clear Panel Gap slot in beside the built-in Mark/Clear Sharp entries
- **Modifier-safe** — operates on the base mesh; Solidify, Bevel, Armature, and other modifiers re-evaluate cleanly on the new topology
- **One undo step** — both tag operations and the apply each register as a single Ctrl+Z

## Requirements

- Blender 4.0 or later

## Tags

mesh, modeling, hard-surface, edge-split, panel-gap, workflow, non-destructive
