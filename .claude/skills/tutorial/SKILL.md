---
name: tutorial
description: >-
  Write a step-by-step tutorial for a Funkworks DCC plugin. Use when a plugin
  exists at plugins/<dcc>/src/<name>.py and needs a tutorial written for
  plugins/<dcc>/docs/tutorials/<name>.md. TRIGGER when the user asks to write,
  create, or draft a tutorial for a plugin.
argument-hint: "[plugin-name]"
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

Write a tutorial for the plugin **$ARGUMENTS**.

Parse `$ARGUMENTS` as `<dcc>/<plugin-name>` (e.g. `blender/selective_edge_split` or
`houdini/scale_cop`). Set `$DCC` and `$NAME` from those two parts. If only a plugin name
is given without a DCC prefix, ask the user which DCC before proceeding.

## Before You Write

1. **Read the plugin source** at `plugins/$DCC/src/$NAME.*` to understand every parameter and operator.
2. **Read the plugin docs** at `plugins/$DCC/docs/$NAME/README.md` for the stated problem, solution, and usage steps.
3. **Read the spec** at `plugins/$DCC/docs/specs/$NAME.md` if it exists, for edge cases and acceptance criteria.
4. **Check the images directory** at `plugins/$DCC/docs/images/` for any existing screenshots to reference.

---

## Step 1: Write the Tutorial Page

Write the tutorial to `docs/$ARGUMENTS.md` (the public Jekyll page) using this structure:

```markdown
# [Plugin Display Name]

[One sentence: what the reader will be able to do by the end of this tutorial.]

## Prerequisites

- Blender [version]+ installed
- [Plugin name] addon installed and enabled (see [installation guide](#installation))
- [Any scene setup needed]

## What You'll Learn

- [Outcome 1 — a concrete capability, not a feature name]
- [Outcome 2]
- [Outcome 3 if applicable]

## Step 1: [Set Up the Scene / Starting Point]

[Ground the reader in a concrete starting state they can verify.]

> **Checkpoint:** [How the reader knows they're in the right place.]

![alt text]({{ "/images/$ARGUMENTS/01_shot_name.png" | relative_url }})

## Step N: [Continue as needed]

## Result

[Describe what the reader just built. Contrast with the manual workflow.]

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|

## Notes

- [Any caveats, limitations, or tips]
```

Image references use the Jekyll `relative_url` filter — required for correct paths with the site's baseurl:
```markdown
![alt]({{ "/images/$ARGUMENTS/shot_name.png" | relative_url }})
```

### Writing Principles

- **Lead with the destination.** Show or describe the final result before diving into steps.
- **One action per step.** Each numbered step = one decision or click.
- **Name UI elements exactly.** Use **bold** for every UI label. Use `Menu > Submenu > Item` format.
- **Checkpoints, not assumptions.** After every state-changing step, add `> **Checkpoint:**`.
- **Explain the why.** Only where the what isn't self-evident.
- **No filler.** No "simply" or "just." Write for someone competent but new to this tool.
- **Troubleshooting is not optional.** Mine `poll()` methods and spec edge cases.

---

## Step 2: Generate the Screenshot Manifest

For every screenshot referenced in the tutorial, create an entry in
`data/tutorial_manifests/$ARGUMENTS.json`.

Read these two files before writing any setup code:
- `src/tutorials/screenshot_runner.py` — manifest format and runner behaviour
- `src/tutorials/BLENDER_SCREENSHOT_BEST_PRACTICES.md` — blocked MCP patterns, area
  management, capture methods, scroll gotchas, and ready-to-use code snippets

**When you hit a new gotcha and solve it, add it to `BLENDER_SCREENSHOT_BEST_PRACTICES.md`
before moving on.** This keeps the document current for the next Claude Code instance.

### Manifest structure

```json
{
  "tutorial": "$ARGUMENTS",
  "app": "blender",
  "app_window": "Blender",
  "pre_run": [
    // Python commands executed once before all shots:
    // - clear the scene
    // - create the demo objects (mesh, modifiers, etc.)
    // - install and enable the addon
    // - set render resolution to 1920x1080
  ],
  "screenshots": [
    {
      "id": "01_shot_name",
      "description": "One sentence — what this image shows in the tutorial",
      "prompt": "Exact instructions for a human: what panel to have open, what to select, what scroll position, what state the addon should be in",
      "mode": "auto | manual",
      "setup": ["Python commands to reach this state (auto shots only)"],
      "capture": {
        "method": "viewport | window",
        "filepath": "docs/images/$ARGUMENTS/01_shot_name.png"
      },
      "crop": { "method": "area_only" }
    }
  ]
}
```

### Choosing mode

| Use `auto` when | Use `manual` when |
|---|---|
| Capturing the 3D viewport (pure geometry, no UI panels) | Showing a specific UI panel or scroll position |
| The state can be reached with 2–3 Blender Python calls | The UI requires scrolling, hovering, or precise layout |
| The capture is `method: viewport` (OpenGL render) | The capture is `method: window` (full window screenshot) |

When in doubt, prefer `manual` — a clear `prompt` is more reliable than fragile setup code.

### Writing `pre_run`

`pre_run` must leave Blender in a clean, known state before any shots run:
- Remove all default objects first
- Create only what the tutorial needs
- Install and enable the addon
- Set `bpy.context.scene.render.resolution_x/y = 1920/1080`

### Writing `setup` for auto shots

- Keep setup minimal — 3–5 commands max
- Ensure VIEW_3D exists: `if not any(a.type == 'VIEW_3D' for a in screen.areas): max(screen.areas, ...).type = 'VIEW_3D'`
- Set frame, selection, and camera angle explicitly
- Use `mathutils.Quaternion` for view rotation (not operators)

### Writing `prompt` for manual shots

The `prompt` is shown to the human operator at capture time. Write it as a direct instruction:
- Name the exact panel, tab, and sub-panel
- Describe the required scroll position or expanded/collapsed state
- State what the addon's output should show (e.g., "so that 'Hidden at frame: 23' is visible")

---

## Step 3: Run the Screenshot Pipeline

With Blender open and the MCP plugin active:

```bash
python -m src.tutorials.screenshot_runner data/tutorial_manifests/$ARGUMENTS.json
```

- **Auto shots** capture without interaction.
- **Manual shots** print the `prompt` and wait for Enter. The human sets up Blender, confirms, and the runner captures.

To retake a single shot after a manual fix (skips `pre_run`):

```bash
python -m src.tutorials.screenshot_runner data/tutorial_manifests/$ARGUMENTS.json --shot <shot_id>
```

After each run, read the output images directly to verify each one shows what it's supposed to show. If a shot is wrong, describe the problem to the user and ask them to set up Blender for a retake.

---

## Step 4: Human Review

After the pipeline completes, present the work for review:

1. List every screenshot with a one-line description of what it shows.
2. Give the path to the published tutorial page (`docs/$ARGUMENTS.md`).
3. Explicitly ask:

> "Please review the tutorial page and screenshots. Name any images that need a retake and describe what's wrong, or any sections that need rewriting. I'll wait."

Then stop and wait for the human's response.

When feedback arrives:
- **Image retake:** Ask the human to set up the app to the correct state, then use `--shot <id>` to retake just that image. Read the result and confirm it's right before moving on.
- **Text fix:** Edit the tutorial page directly.
- **Multiple fixes:** Work through them one at a time, confirming each before starting the next.

Repeat until the human approves.

---

## Final Checks

1. Verify every UI element name against the plugin source.
2. Verify the Blender version matches `bl_info["blender"]` in the plugin.
3. Confirm all image paths in the tutorial match the `filepath` values in the manifest.
4. If a spec exists, verify every acceptance criterion is covered by at least one tutorial step.
