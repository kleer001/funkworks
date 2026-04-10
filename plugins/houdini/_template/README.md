# [Node Name]

[One sentence: what pain does this solve in Houdini?]

## The Problem

[2-3 sentences describing the manual workflow users are stuck doing today — what nodes they're chaining, what they're computing by hand, what breaks when something changes.]

## The Solution

[How this HDA fixes it. Where to find it in Houdini's tab menu. What the user does instead.]

## Inputs

| # | Name | Description |
|---|------|-------------|
| 0 | [Name] | [What it expects] |

## Parameters

[Key parameters grouped by function. Table or bullet list. Focus on what the user needs to know, not an exhaustive dump.]

## Installation

1. Download `[name].hda` from the [latest GitHub release](https://github.com/kleer001/funkworks/releases/latest)
2. In Houdini: **Assets > Install Asset Library**
3. Select `[name].hda` and click **Install**
4. The node appears in [network type] as **[Node Label]**

> **License notice.** The pre-built HDA was compiled under a Houdini Indie/Apprentice license. Loading it in a full Houdini FX session will flag the scene as limited-commercial. FX users should build from source — see below.

## Building from Source

1. Download `build_[name].py` from the [latest GitHub release](https://github.com/kleer001/funkworks/releases/latest)
2. Run with hython:
   ```bash
   hython build_[name].py
   ```
3. The script writes `[name].hda` alongside itself

Requires Houdini [X.Y]+ (any edition).

## Compatibility

- Houdini [X.Y]+
- [Network type]: [COP2 / SOP / LOP / etc.]
- Any edition: Apprentice, Indie, Core, FX

## Notes

- [License caveat if applicable]
- [Edge case or quirk worth calling out]
- [Another note if needed]
