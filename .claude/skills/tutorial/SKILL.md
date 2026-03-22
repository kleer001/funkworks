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

## Before You Write

1. **Read the plugin source** at `plugins/blender/src/$ARGUMENTS.py` to understand every operator, panel, and parameter.
2. **Read the plugin docs** at `plugins/blender/docs/$ARGUMENTS/README.md` for the stated problem, solution, and usage steps.
3. **Read the spec** at `plugins/blender/docs/specs/$ARGUMENTS.md` if it exists, for edge cases and acceptance criteria.
4. **Check the images directory** at `plugins/blender/docs/images/` for any existing screenshots to reference.

## Tutorial Structure

Write the tutorial to `plugins/blender/docs/tutorials/$ARGUMENTS.md` using this structure:

```markdown
# Tutorial: [Plugin Display Name]

[One sentence: what the reader will be able to do by the end of this tutorial.]

## Prerequisites

- Blender [version]+ installed
- [Plugin name] addon installed and enabled (see [installation guide](../[plugin-name]/README.md#installation))
- [Any scene setup needed, e.g., "A scene with a fluid simulation domain"]

## What You'll Learn

- [Outcome 1 — a concrete capability, not a feature name]
- [Outcome 2]
- [Outcome 3 if applicable]

## Step 1: [Set Up the Scene / Starting Point]

[Describe where the user should be before touching the addon. What should
their scene look like? What panel should they have open? Ground the reader
in a concrete starting state they can verify.]

> **Checkpoint:** [How the reader knows they're in the right place.]

## Step 2: [First Addon Interaction]

[Walk through the first meaningful action. Name every button, menu, and
panel exactly as it appears in Blender's UI — use **bold** for UI labels.
Describe what happens after each click so the reader can verify.]

> **Checkpoint:** [Observable result the reader should see.]

## Step N: [Continue as needed]

[Each step should be one logical action. Avoid combining multiple clicks
or decisions into a single step. If a step has sub-actions, use a
numbered sub-list.]

## Result

[Describe and celebrate what the reader just built. Reference the final
state of the scene. If possible, contrast it with the manual workflow
from the README's "The Problem" section — make the payoff tangible.]

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| [Thing that might go wrong] | [Why] | [What to do] |

## Next Steps

- [Link to related plugin or technique]
- [Suggestion for extending what they just learned]
```

## Writing Principles

These are drawn from best practices in creative-software education. Follow them closely.

### Lead with the destination
Show or describe the final result before diving into steps. Readers of
creative-tool tutorials want to know what they're building. If the plugin
produces a visible change in the viewport, describe that change up front.

### One action per step
Each numbered step should involve exactly one decision or click. Complex
steps lose readers. If a step feels long, split it.

### Name UI elements exactly
Use **bold** for every Blender UI label (panel names, button text, menu
paths). A reader scanning the tutorial should be able to follow by bold
text alone. Use the format `Menu > Submenu > Item` for menu paths.

### Checkpoints, not assumptions
After every step that changes state, add a `> **Checkpoint:**` block
describing what the reader should see. This is how self-directed learners
debug without a teacher.

### Explain the "why" for non-obvious steps
If a step's purpose isn't self-evident, add a one-sentence explanation.
Don't over-explain obvious actions. The rule: explain the _why_ when
the _what_ isn't enough.

### Ground in the real workflow
Reference the manual workflow this plugin replaces. The README's
"The Problem" section is your source. Readers connect with tutorials
that acknowledge their existing frustration.

### Troubleshooting is not optional
Creative software has unpredictable state — unbaked simulations, missing
objects, wrong contexts. Mine the plugin's `poll()` method and edge-case
notes from the spec for common failure modes.

### Keep the tone practical and respectful
No filler, no hype, no "simply" or "just." Write for someone competent
who hasn't used this specific tool yet. Portfolio-quality prose:
clear, direct, confident.

## After Writing

1. Verify every UI element name against the plugin source code.
2. Verify the Blender version matches `bl_info["blender"]` in the plugin.
3. Confirm all internal links resolve (README, installation section).
4. If the plugin has a spec, verify that every acceptance criterion is
   covered by at least one tutorial step.
