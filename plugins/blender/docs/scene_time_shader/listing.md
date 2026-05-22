# Marketplace Listing — Scene Time Shader Node

## Short Description (160 chars)
Adds the missing Scene Time node to the Shader Editor — same Frame and Seconds outputs as the Compositor and Geometry Nodes versions, identical math.

## Long Description

The Compositor and Geometry Nodes editors have a built-in **Scene Time** node. The Shader Editor doesn't — so driving a UV scroll, hue cycle, or pulsing emission means writing a `#frame` driver on a Value node by hand, every new material.

**How it works:**
- Adds **Scene Time** to **Shader Editor > Add > Input**
- Outputs **Seconds** (`frame * fps_base / fps`, NTSC-correct) and **Frame** (`frame_current`)
- Created as a shared node group on first invocation; later invocations instance the same group
- Drivers travel with the .blend, so files open correctly on machines without the addon installed

No new UI patterns. If you've used Scene Time in the Compositor or Geometry Nodes, you already know how this works.

## Features

- Identical math and identical Add-menu location to Blender's built-in Scene Time
- Two outputs (Seconds, Frame) — direct float inputs to any shader socket
- Single shared node group per .blend; one driver setup serves every Scene Time instance
- Read-only design — offsets are applied with downstream Math nodes, not by editing the group
- Survives save / reload / linking without the addon present

## Requirements

- Blender 4.0 or later (validated on 4.2 LTS)

## Tags

shader, node, time, animation, driver, scene-time, frame, seconds
