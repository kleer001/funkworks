# Auto-Tutorial Pipeline — Blender

> DCC-specific reference for the [Auto-Tutorial Pipeline](auto_tutorial_pipeline.md).

---

## Screenshot API

| Task | Blender Python API |
|------|-------------------|
| Render viewport to image | `bpy.ops.render.opengl(write_still=True)` |
| Screenshot full window | `bpy.ops.screen.screenshot(filepath=...)` |
| Screenshot specific area | `bpy.ops.screen.screenshot_area(filepath=...)` |
| Set viewport shading | `context.space_data.shading.type = 'SOLID'` / `'MATERIAL'` / `'RENDERED'` |
| Set camera/view angle | `bpy.ops.view3d.view_axis(type='FRONT')` or set `region_3d.view_rotation` |
| Navigate to frame | `context.scene.frame_set(N)` |
| Select objects | `obj.select_set(True)` / `context.view_layer.objects.active = obj` |
| Open editor/panel | `bpy.ops.screen.area_type_set(type='PROPERTIES')` |

### Cropping Strategy

Always use `screenshot_area` (not `screenshot`) — it captures a single editor area instead of the full Blender window. For tighter crops (e.g. a single sub-panel within Properties), the Screenshot Runner post-crops with Pillow using the `crop.region` from the manifest.

Blender's `screenshot_area` captures the entire area including headers and sidebars. To crop to just a sub-panel or specific control, estimate pixel coordinates from the area's layout. These coordinates are relative to the captured area image, not the full screen.

---

## Scene File Format

`.blend` — opened via `bpy.ops.wm.open_mainfile(filepath=...)`, reset via `bpy.ops.wm.revert_mainfile()`.

---

## Plugin Installation (Tutorial Template)

```markdown
1. Download `[filename].py` from [GitHub Releases](link)
2. In Blender: **Edit > Preferences > Add-ons > Install**
3. Select the downloaded file and enable the addon
```

## Plugin Install via Runner

`bpy.ops.preferences.addon_install(filepath=...)` + `bpy.ops.preferences.addon_enable(module=...)`

---

## Headless Screenshot Capture

```bash
xvfb-run -a -s "-screen 0 1920x1080x24" blender --python screenshot_runner.py
```

---

## Source Code Metadata Mapping

| Source Code Element | Tutorial Content |
|--------------------|-----------------|
| `bl_info["location"]` | "Find the plugin at **[location]**" |
| `bl_info["blender"]` | Compatibility requirements |
| Panel class `bl_space_type`, `bl_region_type`, `bl_context` | Screenshot area type + navigation instructions |
| Operator `poll()` method | Prerequisites |
| `bpy.props.*Property` definitions | Options table |
| `self.report()` calls | Expected feedback messages |
| `bl_options = {'REGISTER', 'UNDO'}` | "You can undo this with Ctrl+Z" |

---

## Example Screenshot Manifest

```json
{
  "dcc": "blender",
  "plugin": "fluid_domain_visibility",
  "scene_file": "tutorial_scenes/fluid_domain_demo.blend",
  "screenshots": [
    {
      "id": "01_problem",
      "description": "Viewport showing domain box visible before sim starts",
      "setup": [
        "bpy.context.scene.frame_set(1)",
        "bpy.ops.view3d.view_axis(type='FRONT')",
        "bpy.context.space_data.shading.type = 'SOLID'"
      ],
      "capture": {
        "method": "screenshot_area",
        "area_type": "VIEW_3D",
        "filepath": "plugins/blender/docs/images/fluid_domain_visibility/01_problem.png"
      },
      "crop": { "method": "area_only" }
    },
    {
      "id": "02_panel",
      "description": "Close-up of Auto-Visibility toggle in Properties panel",
      "setup": [
        "domain = bpy.data.objects['Fluid Domain']",
        "bpy.context.view_layer.objects.active = domain",
        "domain.select_set(True)"
      ],
      "capture": {
        "method": "screenshot_area",
        "area_type": "PROPERTIES",
        "filepath": "plugins/blender/docs/images/fluid_domain_visibility/02_panel.png"
      },
      "crop": {
        "method": "bbox",
        "region": [0, 120, 320, 280],
        "comment": "Crop to just the plugin's sub-panel within the full Properties area"
      }
    }
  ]
}
```

---

## Example Scene Generation

```python
bpy.ops.wm.read_homefile(use_empty=True)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
domain = bpy.context.active_object
domain.name = "Fluid Domain"
bpy.ops.object.modifier_add(type='FLUID')
domain.modifiers["Fluid"].fluid_type = 'DOMAIN'
domain.modifiers["Fluid"].domain_settings.cache_frame_start = 24
bpy.ops.wm.save_as_mainfile(filepath="/path/to/tutorial_scenes/fluid_domain_demo.blend")
```

---

## Failure Recovery (Blender-Specific)

| Failure | Recovery |
|---------|----------|
| Screenshot blank or wrong area | Retry with `bpy.context.area.type = 'VIEW_3D'` to force area focus |
| Plugin not installed | Re-install via `bpy.ops.preferences.addon_install` before retrying |
| Unexpected UI state | Reset via `bpy.ops.wm.revert_mainfile()` and retry full sequence |
