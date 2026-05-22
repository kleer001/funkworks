# Announcement Copy — Scene Time Shader Node

## Medium (BlenderArtists / Reddit r/blender)

**Free addon: Scene Time node for the Shader Editor (Frame + Seconds, same math as Compositor)**

The Compositor and Geometry Nodes editors have a built-in **Scene Time** node — two outputs, current Frame and current Seconds. The Shader Editor does not. Driving a time-dependent shader has meant either writing a `#frame` driver on a Value node by hand, or building a Math chain that divides `frame_current` by `render.fps`. Both have to be redone for every material that needs them.

**Scene Time Shader Node** adds the same node to the Shader Editor's **Add > Input** menu. Selecting it drops a node group with two driver-backed Value outputs: **Seconds** (`frame * fps_base / fps`, correctly handling NTSC 23.976) and **Frame** (`frame_current`). On first invocation it creates a single shared node group; every later invocation instances the same group, so the driver setup is paid once per .blend.

Drivers are first-class scene data, so files saved with Scene Time nodes open correctly on machines that don't have the addon installed — the addon is only required to add *new* Scene Time nodes, not to use existing ones.

Free download: https://kleer001.github.io/funkworks/scene_time_shader

Validated on Blender 4.2 LTS, declared compatible with 4.0+. No new node class, no C extension — just a `ShaderNodeTree` group with two driven Value nodes.

More free tools at https://github.com/kleer001/funkworks

---

## Long (Newsletter / Blog post intro)

**Of Blender's three main node editors, only the Shader Editor lacks a Scene Time node**

The Compositor and Geometry Nodes each have a built-in **Scene Time** node — two outputs, current Frame and current Seconds. The Shader Editor doesn't. The omission has stood since the Compositor's Scene Time node landed; the [highest-ranked Right-Click-Select request on the topic](https://blender.community/c/rightclickselect/Y599/) has 65 net votes, 7 replies, and no resolution.

If you want a time-driven shader — a UV scroll that moves with the timeline, a hue cycle, a pulsing emission, a frame-locked transition — you either right-click a Value node and type `#frame` as a driver expression, or you build a Math chain that divides `frame_current` by `render.fps` by hand. Both work. Both have to be done for every new material that needs them, and the Math-chain approach silently breaks under NTSC because it ignores `fps_base`.

**Scene Time Shader Node** ports the existing Scene Time node into the Shader Editor under the same Add-menu location and with the same outputs. The computation is identical to the Compositor and Geometry Nodes versions: `Seconds = frame_current * fps_base / fps`, so NTSC frame rates (24000/1001 = 23.976 fps) behave correctly without a manual fps-base correction.

On first invocation the addon creates a shared `Scene Time` node group containing two driver-backed Value nodes. Every later invocation instances the same group, so the driver wiring happens once per .blend and every node group instance is just a reference. Because drivers are part of scene data, the file opens correctly on machines that don't have the addon installed; the addon is only required to add *new* Scene Time nodes, not to use ones already in the file.

The full node-group + driver setup is in a single 155-line file and uses only stock Blender API. No custom node class, no C extension, no preferences UI, no opinionated defaults.

Download it free: https://kleer001.github.io/funkworks/scene_time_shader

More free tools at https://github.com/kleer001/funkworks
