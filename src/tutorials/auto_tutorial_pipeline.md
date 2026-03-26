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

### Capture Resolution

All screenshots are captured at **1920×1080** (HD / 2K). This is the pipeline's standard resolution — every DCC session used for screenshot capture must run at this size, regardless of the host machine's native display.

**Why 1920×1080:**
- Standard resolution that most users will recognize and find readable
- Large enough for crisp UI detail after cropping, small enough to keep file sizes reasonable
- Deterministic — crop coordinates from Claude are valid across any machine running the pipeline, because the source image is always the same size
- The MVP test machine is 4K native; capturing at native resolution would produce oversized images and make crop coordinates non-portable

**How to enforce it:**

| Environment | Method |
|-------------|--------|
| Headless (CI, xvfb) | Set the virtual framebuffer to 1920×1080: `xvfb-run -a -s "-screen 0 1920x1080x24"` |
| Windowed (local dev) | Launch the DCC at a fixed window size. Blender: `blender --window-geometry 0 0 1920 1080`. Other DCCs have equivalent flags. |
| High-DPI / Retina | Disable display scaling for the DCC process so 1920×1080 means 1920×1080 pixels, not logical points. On Linux: `QT_SCALE_FACTOR=1` / `GDK_SCALE=1` as needed. |

### Workspace Standardization

The DCC must launch with its **factory default workspace**, not the user's saved layout. Area sizes within the 1920×1080 window depend on which workspace is active and how panels are arranged — if the user has customized their layout, area captures will be different sizes and crop coordinates won't transfer between machines.

**For Blender**, this means launching with `--factory-startup`, which bypasses the user's saved preferences and startup file. The factory default "Layout" workspace has four areas:

| Area | Position | Contents |
|------|----------|----------|
| 3D Viewport | Top-left (largest) | Scene view — most screenshot subjects live here |
| Outliner | Top-right | Object hierarchy |
| Properties | Bottom-right | Plugin panels, modifiers, physics settings |
| Timeline | Bottom | Animation timeline, keyframe display |

Since `area.width` and `area.height` are **read-only** in Blender's Python API, you cannot resize areas programmatically after launch. The factory startup is the only reliable way to get deterministic area sizes.

**Standard Blender launch command for the Runner:**

```bash
# Windowed (local dev)
blender --factory-startup --window-geometry 0 0 1920 1080 --python screenshot_runner.py

# Headless (CI)
xvfb-run -a -s "-screen 0 1920x1080x24" \
  blender --factory-startup --window-geometry 0 0 1920 1080 --python screenshot_runner.py
```

Other DCCs should use their equivalent "ignore user prefs" flags. See the per-DCC docs for details.

The manifest records this at the top level so downstream tools know what they're working with:

```json
{
  "dcc": "blender",
  "resolution": [1920, 1080],
  "plugin": "fluid_domain_visibility",
  ...
}
```

If the DCC window doesn't match the expected 1920×1080 resolution (e.g. the launch flags were wrong or display scaling interfered), the Runner should detect this before proceeding to captures. In Blender, check with `bpy.context.window.width` and `bpy.context.window.height`.

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
  "resolution": [1920, 1080],
  "plugin": "fluid_domain_visibility",
  "scene_file": "plugins/blender/docs/fluid_domain_visibility/demo.blend",
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
      "crop_subject": "The plugin's sub-panel within Properties",
      "setup": ["<DCC-specific setup commands>"],
      "capture": {
        "method": "<DCC-specific capture method>",
        "area_type": "PROPERTIES",
        "filepath": "plugins/blender/docs/images/fluid_domain_visibility/02_panel_detail.png"
      },
      "crop": {
        "method": "pending"
      }
    }
  ]
}
```

**Crop methods:**

| Method | Behavior |
|--------|----------|
| `area_only` | Use the DCC's area-level screenshot — no further cropping. Suitable when an entire editor area *is* the subject. Phase 2 is skipped. |
| `pending` | Phase 1 placeholder — the entry has a `crop_subject` but no coordinates yet. The Runner will upload the full-area capture to Claude (Phase 2) to get a `bbox` region. After Phase 2, this becomes `bbox`. |
| `bbox` | Post-capture crop to `[x, y, width, height]` pixels. Set by Claude in Phase 2, not by the Tutorial Agent. The runner uses Pillow (`PIL.Image.crop`). Coordinates are relative to the captured area image, not the full screen. |

### Screenshot Runner (Python Script)

The runner is a small Python script that:

1. Reads the screenshot manifest JSON
2. Selects the correct MCP adapter based on `dcc` field
3. Launches the DCC with factory defaults at 1920×1080 (see [Workspace Standardization](#workspace-standardization))
4. Opens the scene file via MCP — **once, at the start**
5. Installs and enables the plugin via MCP
6. For each screenshot entry **in manifest order**:
   - Executes the `setup` commands in sequence
   - Executes the `capture` command
   - Uploads to Claude for crop coordinates (Phase 2) if `crop.method` is `pending`
   - Applies crop (Pillow) and runs automated QA checks
   - Verifies the output file exists and is non-empty
7. Reports success/failure per screenshot

**Ordering matters.** Screenshots are executed in the order they appear in the manifest. The scene is loaded once at the start and **not reset between screenshots** — each entry's `setup` commands build on the state left by the previous entry. This allows the tutorial to show a progression (e.g. screenshot 01 shows the problem, 02 shows clicking the button, 03 shows the result).

If a screenshot needs a clean scene state, its `setup` commands must explicitly reset it (e.g. `bpy.ops.wm.revert_mainfile()` in Blender). The Tutorial Agent should note this in the manifest when generating it. The default assumption is: state accumulates.

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

## Crop Decision Workflow

Cropping is a two-phase process: **capture wide, then ask Claude where to cut**. The Tutorial Agent does *not* guess crop coordinates up front — it captures the full UI area first, uploads the uncropped image to Claude, and Claude returns precise crop coordinates based on what it actually sees.

### Phase 1 — Intent (Tutorial Agent, before capture)

When generating the screenshot manifest, the agent records *what* to crop to, but not *where* (no pixel coordinates yet):

```
1. What is this screenshot illustrating?
   → A tutorial step always has a subject: a panel, a result, a control, a menu.

2. What is the minimum UI region that shows the subject in context?
   → The subject must be clearly visible.
   → Enough surrounding context to orient the reader (where am I in the app?).
   → Nothing else. No unrelated panels, no timeline, no toolbar clutter.

3. Write the description and crop_subject fields.
   → description: what the reader should see in the final image.
   → crop_subject: what Claude should look for when deciding where to crop.
```

At this stage the manifest entry has no `crop.region` — just the intent:

```json
{
  "id": "02_panel",
  "description": "The Auto-Visibility toggle in the Physics tab of the Properties sidebar",
  "crop_subject": "The Physics sub-panel containing the Auto-Visibility toggle button",
  "setup": ["..."],
  "capture": {
    "method": "screenshot_area",
    "area_type": "PROPERTIES",
    "filepath": "plugins/blender/docs/images/fluid_domain_visibility/02_panel_full.png"
  },
  "crop": {
    "method": "pending"
  }
}
```

### Phase 2 — Crop Coordinates (Claude, after capture)

After the Screenshot Runner captures each full-area image, the pipeline uploads it to Claude with the `crop_subject` and asks for coordinates:

```
Prompt to Claude:

  Here is a screenshot of [area_type] from [dcc].
  The tutorial step is: "[description]"

  I need to crop this image to show only: "[crop_subject]"

  Return the crop bounding box as [x, y, width, height] in pixels.
  Include enough context that the reader can orient themselves
  (e.g. keep the panel header visible, keep surrounding labels),
  but exclude unrelated UI elements.

  Also return:
  - rationale: one sentence explaining why you chose these bounds.
  - confidence: high / medium / low.
    Use "low" if the subject isn't clearly visible or the crop is ambiguous.
```

Claude returns:

```json
{
  "region": [12, 108, 310, 185],
  "rationale": "Cropped to the Physics sub-panel header through the Auto-Visibility toggle. Excluded Modifiers and Object panels above and below.",
  "confidence": "high"
}
```

The pipeline writes this back into the manifest and performs the crop:

```json
{
  "id": "02_panel",
  "crop": {
    "method": "bbox",
    "region": [12, 108, 310, 185],
    "rationale": "Cropped to the Physics sub-panel header through the Auto-Visibility toggle. Excluded Modifiers and Object panels above and below.",
    "confidence": "high"
  }
}
```

**If confidence is "low"**, the screenshot is flagged for manual review rather than auto-cropped — Claude is saying "I'm not sure I'm looking at the right thing."

### API Integration

The crop pass is a vision API call using the Anthropic Python SDK. The Runner sends the uncropped image as a base64-encoded image content block alongside the text prompt, and parses structured JSON from the response.

```python
import anthropic
import base64
import json

client = anthropic.Anthropic()

def get_crop_coordinates(image_path: str, entry: dict, dcc: str) -> dict:
    """Upload a full-area screenshot to Claude and get crop coordinates."""
    with open(image_path, "rb") as f:
        image_data = base64.standard_b64encode(f.read()).decode("utf-8")

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=512,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",
                        "data": image_data,
                    },
                },
                {
                    "type": "text",
                    "text": (
                        f'This is a screenshot of {entry["capture"]["area_type"]} '
                        f'from {dcc}.\n'
                        f'The tutorial step is: "{entry["description"]}"\n\n'
                        f'Crop this image to show only: "{entry["crop_subject"]}"\n\n'
                        f'Return JSON with:\n'
                        f'- "region": [x, y, width, height] in pixels\n'
                        f'- "rationale": one sentence\n'
                        f'- "confidence": "high" / "medium" / "low"'
                    ),
                },
            ],
        }],
    )
    return json.loads(response.content[0].text)
```

**Notes:**
- Uses Sonnet for the crop pass (fast, cheap, vision is strong enough for UI element detection). Opus is overkill here.
- The `ANTHROPIC_API_KEY` env var must be set. This is the same key used by the Digest Agent.
- The response is parsed as raw JSON. A future refinement could use a Pydantic model for validation, but for MVP the structure is simple enough to parse directly.

### Why This Order

| Approach | Problem |
|----------|---------|
| Guess coordinates before capture | DCC layouts vary by screen size, user prefs, and panel state. Guesses are wrong more often than right. |
| Hardcode coordinates per DCC | Brittle. Breaks when the user resizes anything or a DCC update shifts the UI. |
| **Capture wide → ask Claude → crop** | Claude sees the *actual* rendered UI. Coordinates are precise. Works regardless of layout. |

### Crop Target Examples

| Tutorial step | Subject | crop_subject sent to Claude | Expected crop |
|---------------|---------|----------------------------|---------------|
| "Find the panel in the sidebar" | Plugin's panel | "The [Plugin Name] panel in the sidebar" | Just the plugin's panel section with its header |
| "Click the Toggle button" | A single button/control | "The Toggle button and its label" | Tight crop: button + label + panel header for context |
| "The domain box is now hidden" | Viewport result | *(area_only — no Claude crop needed, full viewport is the target)* | 3D viewport area as captured |
| "Select your fluid domain object" | Object in viewport | *(area_only — spatial context matters)* | Full 3D viewport |
| "Open Edit > Preferences" | A menu | "The Edit menu dropdown" | Menu dropdown + enough menu bar to show origin |

Note: when the full captured area *is* the crop target (e.g. viewport screenshots), `crop.method` stays `area_only` and Phase 2 is skipped — no point asking Claude to crop an image to itself.

---

## Screenshot QA/QC

After capture and cropping, the pipeline validates each screenshot before the tutorial is finalized. QA has two tiers: automated checks by the Runner, then visual review by the Tutorial Agent.

### Automated Checks (Screenshot Runner)

These run immediately after each capture and crop, before moving to the next screenshot:

| Check | How | Fail action |
|-------|-----|-------------|
| **File exists and non-empty** | `os.path.exists()` + `os.path.getsize() > 0` | Retry capture (up to 2 retries) |
| **Minimum dimensions** | Image width and height ≥ 100px after crop | Retry with wider crop region |
| **Not mostly blank** | Pixel variance check — reject images that are >95% single color | Retry with scene reset (the DCC may not have rendered) |
| **Aspect ratio sanity** | Width/height ratio between 0.3 and 4.0 | Flag — likely a bad crop region |
| **Crop confidence** | Check Claude's confidence from Phase 2 | If "low", skip auto-crop and flag for manual review |

### Agent Review (Tutorial Agent)

After all screenshots pass automated checks, the Tutorial Agent reviews each image against its manifest entry:

```
For each screenshot:
  1. Read the image.
  2. Compare to the description field in the manifest.
  3. Answer three questions:
     a. Does the image show what the description says it should show?
     b. Is the subject clearly visible and not cut off by the crop?
     c. Is there excessive irrelevant UI visible that should be cropped tighter?
  4. Verdict: pass, retry (with adjusted crop/setup), or flag for manual review.
```

The agent can adjust crop coordinates and re-run the Screenshot Runner for specific entries — it doesn't need to redo the entire manifest.

### QA Verdicts

| Verdict | What happens |
|---------|--------------|
| **Pass** | Image is used in the final tutorial |
| **Retry — adjust crop** | Agent updates `crop.region` in the manifest and re-runs that one screenshot |
| **Retry — adjust setup** | Agent updates `setup` commands (e.g. wrong frame, wrong selection) and re-captures |
| **Flag for manual review** | Image is kept with a `[needs review]` annotation in the manifest; tutorial ships with the image but it's marked for human check |

### QA Limits

- Maximum 3 retry cycles per screenshot (to avoid infinite loops on fundamentally broken setups)
- If >50% of screenshots fail QA after retries, the entire tutorial is flagged — something is wrong with the scene file or MCP connection, not individual crops
- The agent logs every QA decision (verdict + reasoning) to `data/tutorial_logs/<plugin>_qa.json` for debugging

---

## Pipeline Integration

### Where This Fits in the Plugin Factory

```
Stage 3 — Test Agent (smoke tests pass)
    ↓
Stage 4 — Tutorial Agent (THIS PIPELINE)
  ├── Writes tutorial.md
  ├── Writes screenshot_manifest.json (crop intent — no coordinates yet)
  ├── Screenshot Runner captures full-area images via MCP
  ├── Claude crop pass: upload each full image → get crop coordinates
  ├── Runner crops images and runs automated QA checks
  ├── Tutorial Agent visual QA (image matches description? crop tight enough?)
  ├── Retry loop for failed screenshots (up to 3 cycles)
  └── Tutorial Agent finalizes markdown with verified images
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

For CI/automated runs where no display is available, use `xvfb` to provide a virtual framebuffer at the pipeline's standard 1920×1080 resolution (see [Capture Resolution](#capture-resolution)):

```bash
# Generic pattern — substitute the DCC launch command
# Always use factory-startup (or equivalent) to bypass user prefs
xvfb-run -a -s "-screen 0 1920x1080x24" <dcc-command> --factory-startup <args>

# Blender example
xvfb-run -a -s "-screen 0 1920x1080x24" \
  blender --factory-startup --window-geometry 0 0 1920 1080 --python screenshot_runner.py

# Houdini example
xvfb-run -a -s "-screen 0 1920x1080x24" hython screenshot_runner.py

# Nuke example
xvfb-run -a -s "-screen 0 1920x1080x24" nuke -t screenshot_runner.py
```

This gives the DCC a virtual screen to render into. The framebuffer size must match the pipeline's standard resolution, and the factory startup must be used to get deterministic area sizes. See [Workspace Standardization](#workspace-standardization) for details.

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
