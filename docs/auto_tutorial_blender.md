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

Blender's `screenshot_area` captures the entire area including headers and sidebars. For tighter crops (e.g. a single sub-panel within Properties), the Runner uploads the full-area capture to Claude, which returns precise crop coordinates based on the `crop_subject` field in the manifest. See [Crop Decision Workflow](auto_tutorial_pipeline.md#crop-decision-workflow) for the full Phase 1 → Phase 2 flow. Coordinates are relative to the captured area image, not the full screen.

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

## Launch Command

Always launch Blender with `--factory-startup` to bypass user preferences and get the deterministic factory "Layout" workspace. Combined with `--window-geometry` this gives consistent area sizes for cropping.

```bash
# Windowed (local dev)
blender --factory-startup --window-geometry 0 0 1920 1080 --python screenshot_runner.py

# Headless (CI)
xvfb-run -a -s "-screen 0 1920x1080x24" \
  blender --factory-startup --window-geometry 0 0 1920 1080 --python screenshot_runner.py
```

**Why `--factory-startup`:** Blender's `area.width` and `area.height` are read-only in the Python API — you cannot resize areas after launch. If the user's saved layout has different panel sizes, area-level captures will be the wrong dimensions and crop coordinates from one machine won't work on another. Factory startup is the only reliable way to get deterministic areas.

### Factory Default "Layout" Workspace Areas

| Area | Type constant | Position |
|------|--------------|----------|
| 3D Viewport | `VIEW_3D` | Top-left (largest) |
| Outliner | `OUTLINER` | Top-right |
| Properties | `PROPERTIES` | Bottom-right |
| Timeline | `DOPESHEET_EDITOR` | Bottom |

To verify area sizes at runtime (useful for debugging):
```python
for area in bpy.context.screen.areas:
    print(area.type, area.x, area.y, area.width, area.height)
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

This example follows the two-phase crop flow from the [main pipeline doc](auto_tutorial_pipeline.md#crop-decision-workflow). Phase 1 records `crop_subject` with `"method": "pending"` — no pixel coordinates yet. Phase 2 (the Claude crop pass) fills in the coordinates after the full-area capture.

```json
{
  "dcc": "blender",
  "resolution": [1920, 1080],
  "plugin": "fluid_domain_visibility",
  "scene_file": "plugins/blender/docs/fluid_domain_visibility/demo.blend",
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
      "crop_subject": "The Physics sub-panel containing the Auto-Visibility toggle button",
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
        "method": "pending"
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
bpy.ops.wm.save_as_mainfile(filepath="plugins/blender/docs/fluid_domain_visibility/demo.blend")
```

---

## Failure Recovery (Blender-Specific)

| Failure | Recovery |
|---------|----------|
| Screenshot blank or wrong area | Retry with `bpy.context.area.type = 'VIEW_3D'` to force area focus |
| Plugin not installed | Re-install via `bpy.ops.preferences.addon_install` before retrying |
| Unexpected UI state | Reset via `bpy.ops.wm.revert_mainfile()` and retry full sequence |
