# Scene Time Shader Node

Adds the missing Scene Time node to the Shader Editor — the same Frame and Seconds outputs already in the Compositor and Geometry Nodes editors.

## The Problem

The Compositor and Geometry Nodes editors each have a built-in **Scene Time** node with two outputs: current Frame, and current Seconds. The Shader Editor does not. Driving a time-dependent shader — a UV scroll, a hue cycle, a pulsing emission, a frame-locked transition — means writing a `#frame` driver on a Value node by hand, or building a Math chain that divides `frame_current` by `render.fps`. Both have to be redone for every new material.

## The Solution

Register a **Scene Time** entry under **Add > Input** in the Shader Editor. Selecting it drops a node group with two driver-backed Value outputs:

- **Seconds** = `frame_current * fps_base / fps` (correctly handles NTSC 23.976)
- **Frame** = `frame_current`

The first invocation creates a shared `Scene Time` node group; every later invocation instances the same group, so the driver setup is paid once per .blend.

## Installation

1. Download `scene_time_shader.py`
2. In Blender: **Edit > Preferences > Add-ons > Install**
3. Select the downloaded file and enable the addon

## Usage

1. Open the **Shader Editor** on a material with **Use Nodes** on
2. Press **Shift+A**, navigate to **Input > Scene Time**
3. Drag the **Seconds** or **Frame** output into any float input
4. Scrub the timeline — the connected value updates live in Material Preview / Rendered shading

## Compatibility

- Blender 4.0+ (validated on 4.2 LTS)
- Uses `ShaderNodeTree` group + driver-backed Value nodes — no custom node class, no C extension

## Notes

- **Read-only.** The internal Value nodes are driver-controlled. To offset time, wire a Math node between Scene Time and the destination input rather than editing the group.
- **Drivers tick only when the group is reachable from the depsgraph.** A Scene Time group instance in a material assigned to a visible mesh updates per frame. A group sitting in a material assigned to no object, or to an object hidden in render, returns 0.0. This matches Blender's general driver-evaluation rules.
- **Survives save/reload and linking.** Drivers are first-class scene data; opening the .blend on a machine without this addon still works — the addon is only required to add *new* Scene Time nodes, not to use existing ones.
- **One group per .blend, many instances.** The group is created on first add and reused thereafter.
