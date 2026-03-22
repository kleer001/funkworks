# Auto-Tutorial Pipeline

## Goal

When a plugin passes smoke tests, automatically generate a complete tutorial document with real screenshots — no human screenshotting, no placeholder images. The Doc Agent writes the text, the MCP captures the screenshots, and the output is a publish-ready markdown page with images.

---

## Architecture

```
Plugin passes smoke tests (Stage 3)
    ↓
Tutorial Agent receives:
  - Plugin brief (from Stage 1)
  - Plugin source code
  - Acceptance criteria + test results
    ↓
Tutorial Agent writes:
  - Tutorial markdown (text)
  - Screenshot script (Blender Python commands for MCP)
    ↓
Screenshot Runner executes via MCP:
  - Sets up scene state for each screenshot
  - Captures viewport / UI at each step
  - Saves images to docs/images/<plugin>/
    ↓
Tutorial Agent inserts image references into markdown
    ↓
Output: docs/<plugin>/tutorial.md + docs/images/<plugin>/*.png
```

---

## Screenshot Automation via Blender MCP

### How Blender Screenshots Work

Blender exposes everything needed through its Python API:

| Task | Blender Python API |
|------|-------------------|
| Render viewport to image | `bpy.ops.render.opengl(write_still=True)` — renders the active viewport |
| Save screenshot of full window | `bpy.ops.screen.screenshot(filepath=...)` — captures the entire Blender window |
| Save screenshot of a specific area | `bpy.ops.screen.screenshot_area(filepath=...)` — captures just the active area (3D viewport, Properties panel, etc.) |
| Set viewport shading | `context.space_data.shading.type = 'SOLID'` / `'MATERIAL'` / `'RENDERED'` |
| Set camera/view angle | `bpy.ops.view3d.view_axis(type='FRONT')` or set `region_3d.view_rotation` |
| Navigate to a specific frame | `context.scene.frame_set(N)` |
| Select objects | `obj.select_set(True)` / `context.view_layer.objects.active = obj` |
| Open a specific editor/panel | `bpy.ops.screen.area_type_set(type='PROPERTIES')`, navigate to tab |

### MCP Screenshot Commands

The Screenshot Runner sends Python commands to Blender through MCP. Each screenshot is a sequence:

```python
# Example: capture the plugin's panel in the Properties editor

# 1. Set up the scene state
bpy.ops.wm.open_mainfile(filepath="/tmp/tutorial_scene.blend")
domain = bpy.data.objects["Fluid Domain"]
bpy.context.view_layer.objects.active = domain
domain.select_set(True)

# 2. Navigate to the correct UI location
# (ensure Properties editor is visible, Physics tab is active)

# 3. Capture
bpy.ops.screen.screenshot_area(filepath="/path/to/docs/images/plugin/panel.png")
```

### Screenshot Script Format

The Tutorial Agent generates a JSON screenshot manifest alongside the tutorial markdown:

```json
{
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
        "filepath": "docs/images/fluid_domain_visibility/01_problem.png"
      }
    },
    {
      "id": "02_panel",
      "description": "Auto-Visibility panel in Properties editor",
      "setup": [
        "domain = bpy.data.objects['Fluid Domain']",
        "bpy.context.view_layer.objects.active = domain",
        "domain.select_set(True)"
      ],
      "capture": {
        "method": "screenshot_area",
        "area_type": "PROPERTIES",
        "filepath": "docs/images/fluid_domain_visibility/02_panel.png"
      }
    },
    {
      "id": "03_click",
      "description": "Panel showing frame preview before clicking the button",
      "setup": [],
      "capture": {
        "method": "screenshot_area",
        "area_type": "PROPERTIES",
        "filepath": "docs/images/fluid_domain_visibility/03_click.png"
      }
    },
    {
      "id": "04_result",
      "description": "Viewport at sim start frame — domain now visible",
      "setup": [
        "bpy.ops.fluid.auto_keyframe_visibility()",
        "bpy.context.scene.frame_set(24)"
      ],
      "capture": {
        "method": "screenshot_area",
        "area_type": "VIEW_3D",
        "filepath": "docs/images/fluid_domain_visibility/04_result.png"
      }
    },
    {
      "id": "05_hidden",
      "description": "Viewport at frame 1 — domain now hidden",
      "setup": [
        "bpy.context.scene.frame_set(1)"
      ],
      "capture": {
        "method": "screenshot_area",
        "area_type": "VIEW_3D",
        "filepath": "docs/images/fluid_domain_visibility/05_hidden.png"
      }
    }
  ]
}
```

### Screenshot Runner (Python Script)

The runner is a small Python script that:

1. Reads the screenshot manifest JSON
2. Opens the scene file via MCP (`bpy.ops.wm.open_mainfile`)
3. Installs and enables the plugin via MCP
4. For each screenshot entry:
   - Executes the `setup` commands in sequence
   - Executes the `capture` command
   - Verifies the output file exists and is non-empty
5. Reports success/failure per screenshot

```
src/tutorials/screenshot_runner.py
    ↓ reads
data/tutorial_manifests/<plugin>.json
    ↓ executes via MCP
Blender session
    ↓ writes
plugins/blender/docs/images/<plugin>/*.png
```

If a screenshot fails (Blender error, empty file, wrong area type), the runner logs the error and continues. The Tutorial Agent can retry failed screenshots with adjusted setup commands.

---

## Tutorial Scene Files

Each plugin needs a demonstration scene — a `.blend` file that shows the problem the plugin solves.

### Scene Requirements

| Requirement | Why |
|-------------|-----|
| Minimal — only what's needed to demonstrate the plugin | Small file size, fast to load, no distractions in screenshots |
| Deterministic — opens to the same state every time | Screenshots are reproducible across runs |
| Named objects — descriptive names, not "Cube.003" | Setup commands reference objects by name |
| Pre-configured viewport — camera angle, shading mode set | Less setup needed per screenshot |

### Scene Generation

Two approaches, depending on plugin complexity:

**Simple plugins:** The Tutorial Agent generates the scene programmatically via MCP.

```python
# Create a demo scene for Fluid Domain Auto-Visibility
bpy.ops.wm.read_homefile(use_empty=True)
bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
domain = bpy.context.active_object
domain.name = "Fluid Domain"
bpy.ops.object.modifier_add(type='FLUID')
domain.modifiers["Fluid"].fluid_type = 'DOMAIN'
domain.modifiers["Fluid"].domain_settings.cache_frame_start = 24
bpy.ops.wm.save_as_mainfile(filepath="/path/to/tutorial_scenes/fluid_domain_demo.blend")
```

**Complex plugins:** A manually created `.blend` file stored in the repo under `plugins/blender/docs/<plugin>/demo.blend`. Some plugins require scene setups that are hard to script (specific geometry, materials, animation curves).

### Storage

```
plugins/blender/docs/
├── <plugin>/
│   ├── tutorial.md          ← generated by Tutorial Agent
│   ├── demo.blend           ← tutorial scene (generated or manual)
│   └── screenshot_manifest.json  ← generated by Tutorial Agent
└── images/
    └── <plugin>/
        ├── 01_problem.png   ← captured by Screenshot Runner
        ├── 02_panel.png
        └── ...
```

---

## Tutorial Markdown Template

The Tutorial Agent generates markdown following this structure. Image references use relative paths to the captured screenshots.

```markdown
# [Plugin Name] — Tutorial

> [One-sentence summary of what problem this solves.]

## The Problem

[2-3 sentences. Describe the manual workflow.]

![The problem in action](../images/<plugin>/01_problem.png)
*[Caption describing what the screenshot shows.]*

## Installation

1. Download `[filename].py` from [GitHub Releases](link)
2. In Blender: **Edit > Preferences > Add-ons > Install**
3. Select the downloaded file and enable the addon

## Using [Plugin Name]

### Step 1: [Setup]

[What the user needs to do first.]

![Panel location](../images/<plugin>/02_panel.png)
*[Caption.]*

### Step 2: [Action]

[What the user clicks / configures.]

![Before clicking](../images/<plugin>/03_click.png)
*[Caption.]*

### Step 3: [Result]

[What happens after the plugin runs.]

![After — problem solved](../images/<plugin>/04_result.png)
*[Caption.]*

## Verification

[How the user can confirm it worked.]

![Verification screenshot](../images/<plugin>/05_hidden.png)
*[Caption.]*

## Notes

- [Edge case or limitation]
- [Undo behavior]
- [Compatibility note]
```

---

## Tutorial Agent Prompt

The Tutorial Agent receives:

1. **Plugin brief** — problem statement, solution description, UI location, edge cases
2. **Plugin source code** — reads `bl_info`, operator/panel classes, property definitions
3. **Smoke test results** — confirms which features work

From these, the agent produces:

- `tutorial.md` — the tutorial text with image placeholders (`![alt](path)`)
- `screenshot_manifest.json` — the screenshot script (setup commands + capture instructions)
- Optionally: scene generation script (if the demo scene can be created programmatically)

### What the Agent Infers from Source Code

| Source Code Element | Tutorial Content It Generates |
|--------------------|------------------------------|
| `bl_info["location"]` | "Find the plugin at **[location]**" |
| `bl_info["blender"]` | Compatibility requirements |
| Panel class with `bl_space_type`, `bl_region_type`, `bl_context` | Screenshot area type + navigation instructions |
| Operator `poll()` method | Prerequisites ("Select a fluid domain object first") |
| Operator properties (e.g., `bpy.props.EnumProperty`) | Options table in the tutorial |
| `self.report()` calls | Expected feedback messages |
| `bl_options = {'REGISTER', 'UNDO'}` | "You can undo this with Ctrl+Z" |

This means the tutorial is derived directly from the code, not from a human writing documentation separately. When the code changes, re-running the pipeline produces updated docs.

---

## Pipeline Integration

### Where This Fits in the Plugin Factory

```
Stage 3 — Test Agent (smoke tests pass)
    ↓
Stage 4 — Tutorial Agent (THIS PIPELINE)
  ├── Writes tutorial.md
  ├── Writes screenshot_manifest.json
  ├── Screenshot Runner captures images via MCP
  └── Tutorial Agent verifies images and finalizes markdown
    ↓
Stage 5 — Publish
  ├── GitHub Release (plugin .py)
  ├── Docs site (tutorial.md + images)
  ├── YouTube (video — still manual for now)
  └── Announcements (announce.md — existing template)
```

### Relationship to Existing Doc Agent

The `plugin_factory_build_pipeline.md` defines a Stage 4 "Doc Agent" that writes a tutorial page. This auto-tutorial pipeline replaces that with a more specific design: same role, but now it also generates screenshots.

The Doc Agent from the build pipeline doc becomes the Tutorial Agent here. Same stage, upgraded capability.

---

## Execution Requirements

| Requirement | Status |
|-------------|--------|
| Blender MCP (send Python commands to running Blender) | **Required — critical path** (same as Build/Test agents) |
| `bpy.ops.screen.screenshot_area` support via MCP | Needs verification — MCP must be able to capture from specific editor areas |
| Headless Blender for CI | Optional — screenshots need a display. Use `xvfb` (virtual framebuffer) on Linux for headless screenshot capture |
| Tutorial Agent prompt | To be written when first plugin reaches this stage |
| Screenshot Runner script | To be written — straightforward once MCP is working |

### Headless Screenshot Capture

For CI/automated runs where no display is available:

```bash
# Linux: use xvfb to provide a virtual display
xvfb-run -a -s "-screen 0 1920x1080x24" blender --python screenshot_runner.py
```

This gives Blender a virtual screen to render into. Screenshots capture from this virtual display. Resolution is configurable via the `-screen` argument.

---

## Failure Handling

| Failure | Recovery |
|---------|----------|
| Screenshot is blank or wrong area captured | Runner retries with explicit area focus (`bpy.context.area.type = 'VIEW_3D'`) |
| Scene file missing or corrupt | Tutorial Agent generates scene programmatically as fallback |
| Plugin not installed correctly | Runner re-installs via `bpy.ops.preferences.addon_install` before retrying |
| MCP connection lost mid-capture | Runner reconnects and resumes from the last successful screenshot |
| Screenshot shows unexpected UI state (wrong panel open, etc.) | Runner resets to a clean state (`bpy.ops.wm.revert_mainfile()`) and retries the full sequence |
| All retries exhausted | Flag for manual screenshot capture; tutorial.md ships with `[screenshot pending]` placeholders |

---

## Future Extensions

| Extension | When | What |
|-----------|------|------|
| **Animated GIF capture** | Phase 2 | Capture short viewport animations (5-10 frames → GIF) showing before/after. More compelling than static screenshots. |
| **Video clip capture** | Phase 3 | Record 10-30s viewport clips via `bpy.ops.render.opengl(animation=True)`. These become raw material for YouTube Shorts. |
| **Multi-DCC support** | Phase 3+ | Houdini MCP already exists — same pattern. Screenshot via `hou.ui.saveScreenshot()`. Nuke via `nuke.screenshot()`. |
| **Auto-thumbnail generation** | Phase 2 | Composite before/after screenshots into a split-screen thumbnail for YouTube and docs site. |
| **Tutorial diffing** | Phase 3 | When a plugin updates, re-run the pipeline and diff the screenshots. Flag visual regressions. |
