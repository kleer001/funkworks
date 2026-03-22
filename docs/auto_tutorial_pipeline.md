# Auto-Tutorial Pipeline

## Goal

When a plugin passes smoke tests, automatically generate a complete tutorial document with real screenshots — no human screenshotting, no placeholder images. The Tutorial Agent writes the text, the Screenshot Runner captures the images via MCP, and the output is a publish-ready markdown page. This pipeline is DCC-agnostic: the architecture is the same regardless of target application, with only the screenshot API and scene file format varying per DCC.

---

## Architecture

```
Plugin passes smoke tests (Stage 3)
    ↓
Tutorial Agent receives:
  - Plugin brief (from Stage 1)
  - Plugin source code
  - Acceptance criteria + test results
  - DCC target identifier (blender, houdini, nuke, etc.)
    ↓
Tutorial Agent writes:
  - Tutorial markdown (text)
  - Screenshot manifest (DCC-specific Python commands for MCP)
    ↓
Screenshot Runner executes via MCP:
  - Connects to the running DCC session
  - Sets up scene state for each screenshot
  - Captures viewport / UI at each step
  - Saves images to plugins/<dcc>/docs/images/<plugin>/
    ↓
Tutorial Agent inserts image references into markdown
    ↓
Output: plugins/<dcc>/docs/tutorials/<plugin>.md + plugins/<dcc>/docs/images/<plugin>/*.png
```

---

## Screenshot Automation via MCP

### How It Works

Each DCC exposes a Python API that the Screenshot Runner uses to set up scenes and capture images. The runner sends commands through an MCP connection to a running DCC session. The specific API calls differ per application, but the pattern is always the same:

1. **Open/reset** the demo scene
2. **Set up** the viewport state (camera angle, frame, selection, panel focus)
3. **Capture** a screenshot of a specific UI area
4. **Crop** to just the relevant region — never ship a full-workspace screenshot
5. **Verify** the output file exists and is non-empty

### Crop, Don't Dump

Screenshots must show only the relevant context for the tutorial step — not the entire application workspace. A full-window screenshot is noisy and unhelpful: it buries the subject in toolbars, timelines, and unrelated panels.

**What to crop to depends on the step:**

| Tutorial step is about... | Crop to... |
|--------------------------|------------|
| A panel or sidebar widget | Just that panel, with enough frame to show where it lives |
| A viewport result (before/after) | The 3D viewport area only, no surrounding editors |
| A menu or dialog | The menu/dialog plus minimal surrounding context |
| A specific property or control | Tight crop around the control, include the label |

The Screenshot Runner handles cropping in one of two ways, depending on what the DCC supports:

1. **Area-level capture** — some DCCs can screenshot a single editor area (e.g. Blender's `screenshot_area`). This is the minimum; it avoids full-window captures but may still include more than needed.
2. **Post-capture crop** — the runner crops the captured image to a bounding box specified in the manifest. This handles cases where even an area-level capture is too wide (e.g. cropping a Properties panel to just the plugin's sub-panel).

Both approaches can be combined: capture an area, then crop further. The manifest's `crop` field (see below) controls this.

DCC-specific API details are in the per-DCC docs:

- [Blender](auto_tutorial_blender.md)
- [Houdini](auto_tutorial_houdini.md)
- [Nuke](auto_tutorial_nuke.md)

### Screenshot Manifest Format

The Tutorial Agent generates a JSON screenshot manifest alongside the tutorial markdown. The manifest is DCC-agnostic in structure — only the `setup` commands and `capture.method` values are DCC-specific.

```json
{
  "dcc": "blender",
  "plugin": "fluid_domain_visibility",
  "scene_file": "tutorial_scenes/fluid_domain_demo.blend",
  "screenshots": [
    {
      "id": "01_problem",
      "description": "Viewport showing domain box visible before sim starts",
      "setup": ["<DCC-specific setup commands>"],
      "capture": {
        "method": "<DCC-specific capture method>",
        "area_type": "VIEW_3D",
        "filepath": "plugins/blender/docs/images/fluid_domain_visibility/01_problem.png"
      },
      "crop": {
        "method": "area_only"
      }
    },
    {
      "id": "02_panel_detail",
      "description": "Close-up of the Auto-Visibility toggle in the Properties panel",
      "setup": ["<DCC-specific setup commands>"],
      "capture": {
        "method": "<DCC-specific capture method>",
        "area_type": "PROPERTIES",
        "filepath": "plugins/blender/docs/images/fluid_domain_visibility/02_panel_detail.png"
      },
      "crop": {
        "method": "bbox",
        "region": [x, y, width, height],
        "comment": "Crop to just the plugin's sub-panel within Properties"
      }
    }
  ]
}
```

**Crop methods:**

| Method | Behavior |
|--------|----------|
| `area_only` | Use the DCC's area-level screenshot — no further cropping. Suitable when an entire editor area *is* the subject. |
| `bbox` | Post-capture crop to `[x, y, width, height]` pixels. The runner uses Pillow (`PIL.Image.crop`). Coordinates are relative to the captured image, not the full screen. |
| `auto` | *(future)* The runner uses edge detection or UI element recognition to auto-crop to the relevant widget. Not yet implemented. |

### Screenshot Runner (Python Script)

The runner is a small Python script that:

1. Reads the screenshot manifest JSON
2. Selects the correct MCP adapter based on `dcc` field
3. Opens the scene file via MCP
4. Installs and enables the plugin via MCP
5. For each screenshot entry:
   - Executes the `setup` commands in sequence
   - Executes the `capture` command
   - Applies `crop` if specified (bbox crop via Pillow)
   - Verifies the output file exists and is non-empty
6. Reports success/failure per screenshot

```
src/tutorials/screenshot_runner.py
    ↓ reads
data/tutorial_manifests/<plugin>.json
    ↓ selects adapter for
<dcc> MCP session
    ↓ writes
plugins/<dcc>/docs/images/<plugin>/*.png
```

If a screenshot fails (DCC error, empty file, wrong area type), the runner logs the error and continues. The Tutorial Agent can retry failed screenshots with adjusted setup commands.

---

## Tutorial Scene Files

Each plugin needs a demonstration scene — a file in the DCC's native format that shows the problem the plugin solves.

### Scene Requirements

| Requirement | Why |
|-------------|-----|
| Minimal — only what's needed to demonstrate the plugin | Small file size, fast to load, no distractions in screenshots |
| Deterministic — opens to the same state every time | Screenshots are reproducible across runs |
| Named objects — descriptive names, not defaults like "Cube.003" or "geo1" | Setup commands reference objects by name |
| Pre-configured viewport — camera angle, shading mode set | Less setup needed per screenshot |

### Scene Generation

Two approaches, depending on plugin complexity:

**Simple plugins:** The Tutorial Agent generates the scene programmatically via MCP using the DCC's Python API.

**Complex plugins:** A manually created scene file stored in the repo under `plugins/<dcc>/docs/<plugin>/demo.<ext>`. Some plugins require scene setups that are hard to script (specific geometry, materials, animation curves).

### Storage

```
plugins/<dcc>/docs/
├── <plugin>/
│   ├── tutorial.md                ← generated by Tutorial Agent
│   ├── demo.<ext>                 ← tutorial scene (generated or manual)
│   └── screenshot_manifest.json   ← generated by Tutorial Agent
└── images/
    └── <plugin>/
        ├── 01_problem.png         ← captured by Screenshot Runner
        ├── 02_panel.png
        └── ...
```

Scene file extensions by DCC: `.blend` (Blender), `.hip`/`.hiplc` (Houdini), `.nk` (Nuke), `.ma`/`.mb` (Maya).

---

## Tutorial Markdown Template

The Tutorial Agent generates markdown following this structure. Image references use relative paths to the captured screenshots. The installation section adapts to the DCC's plugin installation workflow.

```markdown
# [Plugin Name] — Tutorial

> [One-sentence summary of what problem this solves.]

## The Problem

[2-3 sentences. Describe the manual workflow.]

![The problem in action](../images/<plugin>/01_problem.png)
*[Caption describing what the screenshot shows.]*

## Installation

[DCC-specific installation steps — see per-DCC doc for template.]

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
2. **Plugin source code** — reads DCC-specific metadata, operator/panel classes, property definitions
3. **Smoke test results** — confirms which features work
4. **DCC target** — determines which API patterns and installation instructions to use

From these, the agent produces:

- `tutorial.md` — the tutorial text with image placeholders (`![alt](path)`)
- `screenshot_manifest.json` — the screenshot script (setup commands + capture instructions)
- Optionally: scene generation script (if the demo scene can be created programmatically)

### What the Agent Infers from Source Code

The specific metadata fields vary by DCC. See the per-DCC docs for detailed mappings. The general pattern:

| Source Code Element | Tutorial Content It Generates |
|--------------------|------------------------------|
| Plugin metadata (name, version, location) | Title, compatibility requirements, "Find it at **[location]**" |
| UI registration (panel/shelf/menu) | Screenshot area type + navigation instructions |
| Guard/validation logic (poll methods, callbacks) | Prerequisites ("Select a domain object first") |
| User-facing properties (enums, sliders, toggles) | Options table in the tutorial |
| Status/feedback messages | Expected feedback messages |
| Undo registration | "You can undo this with Ctrl+Z" |

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
  ├── GitHub Release (plugin source)
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
| DCC MCP adapter (send Python commands to running DCC session) | **Required — critical path** (one adapter per DCC) |
| Screenshot capture support via MCP | Needs verification per DCC — MCP must be able to capture from specific UI areas |
| Headless mode for CI | Optional — screenshots need a display. Use `xvfb` on Linux for headless capture |
| Tutorial Agent prompt | To be written when first plugin reaches this stage |
| Screenshot Runner script | To be written — straightforward once MCP is working |

### Headless Screenshot Capture

For CI/automated runs where no display is available, use `xvfb` to provide a virtual framebuffer on Linux (Ubuntu/KDE):

```bash
# Generic pattern — substitute the DCC launch command
xvfb-run -a -s "-screen 0 1920x1080x24" <dcc-command> <args>

# Blender example
xvfb-run -a -s "-screen 0 1920x1080x24" blender --python screenshot_runner.py

# Houdini example
xvfb-run -a -s "-screen 0 1920x1080x24" hython screenshot_runner.py

# Nuke example
xvfb-run -a -s "-screen 0 1920x1080x24" nuke -t screenshot_runner.py
```

This gives the DCC a virtual screen to render into. Screenshots capture from this virtual display. Resolution is configurable via the `-screen` argument.

---

## Failure Handling

| Failure | Recovery |
|---------|----------|
| Screenshot is blank or wrong area captured | Runner retries with explicit area focus (DCC-specific reset command) |
| Scene file missing or corrupt | Tutorial Agent generates scene programmatically as fallback |
| Plugin not installed correctly | Runner re-installs via DCC's plugin install API before retrying |
| MCP connection lost mid-capture | Runner reconnects and resumes from the last successful screenshot |
| Screenshot shows unexpected UI state | Runner resets to a clean state (revert scene file) and retries the full sequence |
| All retries exhausted | Flag for manual screenshot capture; tutorial.md ships with `[screenshot pending]` placeholders |

---

## Future Extensions

| Extension | When | What |
|-----------|------|------|
| **Animated GIF capture** | Phase 2 | Capture short viewport animations (5-10 frames to GIF) showing before/after. More compelling than static screenshots. |
| **Video clip capture** | Phase 3 | Record 10-30s viewport clips for YouTube Shorts raw material. |
| **Auto-thumbnail generation** | Phase 2 | Composite before/after screenshots into a split-screen thumbnail for YouTube and docs site. |
| **Tutorial diffing** | Phase 3 | When a plugin updates, re-run the pipeline and diff the screenshots. Flag visual regressions. |

---

## DCC-Specific References

Each supported DCC has its own doc covering screenshot APIs, scene file formats, plugin installation templates, source code metadata mappings, and example manifests:

- [Blender](auto_tutorial_blender.md)
- [Houdini](auto_tutorial_houdini.md)
- [Nuke](auto_tutorial_nuke.md)

When adding a new DCC target, create `docs/auto_tutorial_<dcc>.md` following the same structure.
