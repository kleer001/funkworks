# Fluid Domain Auto-Visibility

A Blender addon that eliminates the manual keyframing required to hide a fluid simulation domain before the simulation begins.

## The Problem

When a fluid simulation starts after frame 1, the domain object is visible as an empty box during all the frames before the simulation begins. Fixing this requires manually adding visibility keyframes every time you set up a sim.

## The Solution

Select your fluid domain, go to **Properties > Physics > Fluid > Auto-Visibility**, and click **Auto-Keyframe Visibility**. One click inserts all the keyframes needed.

The panel previews exactly what will happen before you click:

```
Hidden at frame: 23
Visible at frame: 24
[Auto-Keyframe Visibility]
```

## Installation

1. Download `fluid_domain_visibility.py`
2. In Blender: **Edit > Preferences > Add-ons > Install**
3. Select the downloaded file and enable the addon

## Usage

1. Select your fluid domain object
2. Open **Properties > Physics > Fluid > Auto-Visibility**
3. Confirm the preview shows the correct frames
4. Click **Auto-Keyframe Visibility**

The addon reads the simulation start frame directly from the fluid modifier — no manual input required. Undo (Ctrl+Z) removes all inserted keyframes in one step.

## Compatibility

- Blender 4.0+

## Notes

- Works regardless of whether the simulation is baked
- Running it twice on the same object overwrites the existing keyframes at those frames — no duplicates
- Multiple fluid domains on a scene: run once per domain
