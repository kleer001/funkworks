# Plugin Spec: Scene Time Node for Shader Editor

## Problem Statement

The Shader Editor lacks a Scene Time node. The Compositor and Geometry Nodes editors
both expose Scene Time (current frame and current seconds), but shader graphs that
need time-driven values must use a workaround: an unconnected Value node with a manual
`#frame` driver, or a hand-built Math chain dividing `#frame` by `scene.render.fps`.

This is a small but real inconsistency — RCS "Include Scene Time Node in Shader Editor"
has 65 net votes and 7 replies, and the gap is still present in Blender 5.1.

This addon adds a Scene Time node to the Shader Editor with the same Frame and Seconds
outputs that the Compositor and Geometry Nodes versions provide. No core Blender changes
required; the node is registered as a shader node group whose internal Value nodes carry
the standard time drivers.

## Proposed Solution

Register a built-in shader node group called "Scene Time" with two output sockets:

- **Seconds** (float) — `scene.frame_current / scene.render.fps`
- **Frame** (float) — `scene.frame_current`

Both outputs are driven by drivers attached to internal Value nodes inside the group.
The node appears in the Shader Editor under **Add → Input → Scene Time**, matching
the menu location of the existing Compositor / Geometry Nodes versions.

The node is read-only and stateless. Users drop it into any shader graph and connect
Frame or Seconds to whatever they want time-driven: a wave, a UV offset, a noise W
coordinate, a mix factor.

## Host Application

- Application: Blender
- Minimum version: Blender 4.0+ (Shader Editor custom group registration and drivers
  on internal Value nodes have been stable since 2.9x; conservative validated baseline)
- API surfaces used:
  - `bpy.types.ShaderNodeTree` — the group node tree (`type='SHADER'`)
  - `bpy.types.NodeGroupOutput` / `NodeGroupInput` — internal group sockets
  - `bpy.types.ShaderNodeValue` — internal driven values
  - Driver API — `data_path = "outputs[0].default_value"`, expression `frame` or
    `frame / fps`; variable wired to `scene.frame_current` and `scene.render.fps`
  - `bpy.types.NODE_MT_category_SH_NEW_INPUT` (or modern equivalent for 5.x asset-menu
    architecture) — append the menu entry
  - `bpy.app.handlers.load_post` — re-create or re-attach the node group if a .blend
    is opened that doesn't have it (asset-shelf model in 5.x makes this simpler)

## User Interface

### Add menu

```
Shader Editor → Shift+A → Add
  Input ▸
    Value
    RGB
    ...
    Scene Time          ← new
```

Same icon and label as the Compositor / GN versions for visual consistency.

### Node appearance

```
┌─────────────────┐
│ Scene Time      │
│         Seconds ●
│         Frame   ●
└─────────────────┘
```

No input sockets. No properties. Two output sockets.

### F3 Search

- "Add Scene Time Node"

## Inputs and Outputs

### Scene Time node
- **Inputs:** none
- **Outputs:**
  - `Seconds` (float) — current frame divided by scene frame rate
  - `Frame` (float) — current frame as a float
- **Side effects:** the node group ships with drivers attached to its internal Value
  nodes; the depsgraph re-evaluates the drivers on every frame change

## Workflow

```
1. Open Shader Editor on any material
2. Shift+A → Input → Scene Time
3. Wire Frame or Seconds into a Math, Mapping, Wave Texture, or Mix node
4. Scrub the timeline — the shader updates per frame
```

## Technical Implementation Notes

### Why a node group, not a `ShaderNodeCustomGroup` Python class

`ShaderNodeCustomGroup` requires a Python class registered at addon load and a custom
`update()` method. Drivers on a registered shader node group survive .blend save/load,
copy-paste, append, and link without any Python at evaluation time — they are
first-class scene data. The custom-group route adds runtime dependency on the addon
for every file that uses the node; the driven-group route does not.

### Driver setup

```python
ntree = bpy.data.node_groups.new("Scene Time", "ShaderNodeTree")
ntree.interface.new_socket("Seconds", in_out="OUTPUT", socket_type="NodeSocketFloat")
ntree.interface.new_socket("Frame",   in_out="OUTPUT", socket_type="NodeSocketFloat")

out = ntree.nodes.new("NodeGroupOutput")
sec = ntree.nodes.new("ShaderNodeValue")
frm = ntree.nodes.new("ShaderNodeValue")

ntree.links.new(sec.outputs[0], out.inputs["Seconds"])
ntree.links.new(frm.outputs[0], out.inputs["Frame"])

# Seconds driver
d = sec.outputs[0].driver_add("default_value").driver
d.expression = "frame / fps"
v1 = d.variables.new(); v1.name = "frame"; v1.type = "SINGLE_PROP"
v1.targets[0].id_type = "SCENE"; v1.targets[0].id = bpy.context.scene
v1.targets[0].data_path = "frame_current"
v2 = d.variables.new(); v2.name = "fps"; v2.type = "SINGLE_PROP"
v2.targets[0].id_type = "SCENE"; v2.targets[0].id = bpy.context.scene
v2.targets[0].data_path = "render.fps"

# Frame driver — analogous, expression "frame"
```

### Menu registration

Append a single operator that inserts the group node:

```python
def draw_menu(self, context):
    self.layout.operator("node.add_scene_time", text="Scene Time")

bpy.types.NODE_MT_category_SH_NEW_INPUT.append(draw_menu)  # 4.x
# 5.x asset-shelf path may differ; verify on 5.1 target
```

The operator creates a `ShaderNodeGroup` node, sets its `node_tree` to the registered
"Scene Time" group, and places it at the cursor.

### Multi-scene safety

The group's drivers target `bpy.context.scene` at creation time, which would freeze the
group to one scene. Fix: rewrite the driver targets at file load via `load_post` to
point at the current scene, OR use `id_type='SCENE'` with `id=None` plus
`data_path = "scene.frame_current"` — needs verification on the target Blender version.

## Edge Cases

- **No active node tree (Shader Editor empty):** Add menu still works; node is created
  in the default world / material as Blender normally handles
- **Linked .blend depending on the addon:** the group is regular scene data; if the addon
  is not installed on the receiving end, the group still works (drivers re-evaluate from
  scene fields), only the Add menu entry is missing
- **Negative frame numbers:** Frame and Seconds go negative; correct behaviour (matches
  Compositor / GN Scene Time)
- **Render time vs. viewport time:** drivers evaluate per frame in both render and
  viewport; no special handling needed
- **FPS base != 1 (e.g., 23.976 fps NTSC):** `scene.render.fps / scene.render.fps_base`
  is the true frame rate; the driver should use this divisor to match Compositor behaviour
- **Two scenes with different FPS in the same file:** depsgraph evaluates drivers against
  the scene that owns the depsgraph; behaviour matches built-in Scene Time

## Known Limitations

- **Read-only:** users cannot edit the internal Value nodes through the group's interface;
  to override time, they wire their own value before the group's output (standard pattern)
- **No "Absolute Time" option:** Blender's Compositor Scene Time has only Seconds and
  Frame; matching parity is the goal, not extending it
- **Cycles vs. EEVEE:** both evaluate node trees on the same frame-change signal; no
  divergence expected, but Cycles GPU may exhibit minor latency on viewport scrub —
  matches built-in shader behaviour, not specific to this addon

## Acceptance Criteria

1. Addon installs without error on Blender 4.0+ (verify on 4.2 LTS and 5.1)
2. Shift+A → Input → Scene Time appears in Shader Editor add menu
3. Inserting Scene Time creates a node group with Frame and Seconds outputs and no inputs
4. Connecting Frame to a Math node (Add 0) and changing the current frame in the timeline
   causes the Math node output to track frame value 1:1
5. Connecting Seconds at 24 fps with frame_current=48 produces 2.0
6. Changing scene.render.fps from 24 to 30 with frame_current=60 causes Seconds to
   change from 2.5 to 2.0 (depsgraph re-evaluation)
7. Saving the .blend, restarting Blender, reopening — the node still drives correctly
8. Linking the material into a second .blend that does NOT have the addon installed —
   the node group still drives (data is in the linked tree)
9. F3 Search finds "Add Scene Time Node"
10. NTSC frame rate (24000/1001 → 23.976) produces Seconds correctly to within float epsilon

## Origin

- Source: https://blender.community/c/rightclickselect/Y599/ — "Include Scene Time Node in Shader Editor"
- Votes: 65 net, 7 replies
- Status verified: 2026-05-05 — gap still present in Blender 5.1
