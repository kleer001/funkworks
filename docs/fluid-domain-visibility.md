---
title: Fluid Domain Auto-Visibility
layout: page
---

# Fluid Domain Auto-Visibility

One-click visibility keyframing for fluid simulation domains.

[Download](https://github.com/kleer001/funkworks/raw/main/plugins/fluid_domain_visibility.py){: .btn} &nbsp; [Back to all addons](.)

---

## The Problem

When a fluid simulation starts after frame 1, the domain object sits in your scene as a **visible empty box** during all the pre-simulation frames. The fix is always the same: hide it one frame before the sim starts, show it on the start frame.

This means manually adding visibility keyframes every time you set up a fluid sim. This addon does it in one click.

---

## Installation

1. Download [`fluid_domain_visibility.py`](https://github.com/kleer001/funkworks/raw/main/plugins/fluid_domain_visibility.py)
2. In Blender: **Edit > Preferences > Add-ons > Install**
3. Select the downloaded file
4. Enable **Fluid Domain Auto-Visibility** in the list

---

## Usage

1. Select your fluid domain object
2. Open **Properties > Physics > Fluid**
3. Find the **Auto-Visibility** panel at the bottom
4. The panel previews exactly what will happen:

   ```
   Hidden at frame: 23
   Visible at frame: 24
   [Auto-Keyframe Visibility]
   ```

5. Click **Auto-Keyframe Visibility**

That's it. Both viewport and render visibility keyframes are inserted in one step.

**Undo:** Ctrl+Z removes all inserted keyframes in a single step.

---

## Notes

- Works whether or not the simulation is baked
- Running it twice overwrites the existing keyframes — no duplicates
- If your sim starts at frame 1, keyframes are placed at frames 0 and 1, and a warning is issued
- Multiple fluid domains in a scene: run once per domain

---

## Requirements

- Blender 4.0 or later

---

[Back to all addons](.) &middot; [GitHub](https://github.com/kleer001/funkworks)
