# Marketplace Listing — Fluid Domain Auto-Visibility

## Short Description (160 chars)
One-click visibility keyframing for fluid simulation domains. Automatically hides the domain box before your sim starts.

## Long Description

Stop manually adding visibility keyframes every time you set up a fluid simulation.

When a fluid sim starts after frame 1, the domain object sits in your scene as a visible empty box during all the pre-simulation frames. The fix is always the same: hide it one frame before the sim starts, show it on the start frame. This addon does exactly that in one click.

**How it works:**
- Select your fluid domain object
- Open Properties > Physics > Fluid > Auto-Visibility
- The panel shows you exactly which frames will be keyframed before you commit
- Click Auto-Keyframe Visibility — done

Reads the simulation start frame directly from the modifier. No manual input, no guesswork. Full undo support.

## Features

- One-click visibility keyframing for fluid domain objects
- Live preview of target frames in the panel before you click
- Sets both viewport and render visibility keyframes
- Single undo step reverses all changes
- Works on baked and unbaked simulations
- Safe to run multiple times — no duplicate keyframes

## Requirements

- Blender 4.0 or later

## Tags

fluid, simulation, keyframe, visibility, animation, domain, physics
