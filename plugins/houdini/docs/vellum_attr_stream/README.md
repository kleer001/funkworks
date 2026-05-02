# Vellum Animated Attribute Streamer

A Houdini DOP HDA that streams animated SOP point attributes into a live Vellum simulation each substep — instead of letting Vellum freeze them at frame 1.

## The Problem

Vellum's solver reads SOP attributes once, when the simulation initialises. After that, the sim runs in the DOP context and has no automatic link back to the source SOP. If you painted a sweeping `Cd` mask, animated a stiffness ramp, or keyframed a per-point pin weight upstream of the Vellum Solver, the values are silently dropped from frame 2 onward. Every frame after the first uses whatever the geometry looked like the very first time it cooked into the solver.

The standard workarounds — bundling attributes into a separate cache and authoring a `Geometry Wrangle` DOP, hand-rolling a popwrangle microsolver, learning that microsolvers don't run on the creation frame — are 100+ lines of plumbing for a feature most users assume already works.

## The Solution

Vellum Animated Attribute Streamer wraps that plumbing in one HDA plus a one-click setup script. It uses the same `popwrangle-in-Pre-Solve` pattern SideFX uses internally for `muscleupdatevellum`:

1. A DOP HDA (`vellum_attr_stream`) drops a popwrangle microsolver into the Vellum Solver's `popsolver` Pre-Solve chain. It fires every substep and copies listed attributes from the upstream SOP onto the live sim points.
2. A SOP-level Attribute Wrangle (`vellum_attr_stream_init`) sits upstream of the Vellum Solver and seeds frame 1, because microsolvers don't run on the creation frame in Houdini. Its parameters channel-reference the DOP streamer's parameters, so editing one updates both.

The setup script handles all the wiring automatically — unlocking the Vellum Solver wrapper, diving to the right popsolver, finding the right merge node, inserting both wrangles, and selecting the streamer for editing.

## Workflow

1. Build a Vellum cloth/grain/hair setup with an upstream SOP that animates a point attribute (`Cd`, a custom float, a stiffness mask, etc.).
2. Select the **Vellum Solver** SOP.
3. **File > Run Script...** and pick `vellum_attr_stream_setup.cmd`.
4. Open the inserted streamer DOP, set the **Attributes** parm to a space-separated list of attribute names (default: `Cd`), and pick a match mode.
5. Play the timeline. The listed attributes update on the simulated cloth every substep.

## Parameters (on the inserted streamer DOP)

**Animated SOP** — path to the upstream SOP that produces the time-varying attribute. The setup script pre-fills this from the Vellum Solver's input.

**Attributes** — space-separated list of point attribute names to copy. Default: `Cd`. Add more separated by spaces, e.g. `Cd stiffness pinmask`.

**Match Points By** — `id` (matches points by the `id` point attribute, survives upstream topology shuffles) or `ptnum` (matches by point number — only safe when both geometries have identical point order).

The SOP-level init wrangle reads its parameters from the streamer DOP via channel references. Edit them in one place; both stay in sync.

## Supported Attribute Types

| Type | Size | Supported |
|------|------|-----------|
| Float scalar | 1 | ✓ |
| Float vector | 3 | ✓ |
| Float vector4 | 4 | ✓ |
| Integer scalar | 1 | ✓ |
| String | — | ✗ |
| Matrix3/4 | — | ✗ |
| Primitive / vertex / detail attributes | — | ✗ |

Point-to-point matching is the common case the plugin targets.

## Installation

1. Download `vellum_attr_stream_setup.cmd`, `vellum_attr_stream_setup.py`, and `vellum_attr_stream.hda` from the [latest GitHub release](https://github.com/kleer001/funkworks/releases/latest)
2. Save all three files into the **same folder** anywhere on disk
3. In Houdini: select a Vellum Solver SOP, then **File > Run Script...** and pick `vellum_attr_stream_setup.cmd`

The `.cmd` is a one-line HScript dispatcher that finds the `.py` and `.hda` next to itself via `$arg0`. There's nothing to copy into Houdini prefs, no restart, no shelf install.

> **Why .cmd?** Houdini's File > Run Script menu maps to HScript's `source` command, which only accepts `.cmd` files. Picking a `.py` directly fails with cryptic parse errors. The `.cmd` is a one-line dispatcher that exec's the readable `.py` next to it.

> **License notice.** The pre-built HDA was compiled under a Houdini Indie/Apprentice license. Loading it in a full Houdini FX session will flag the scene as limited-commercial. FX users should build from source — see below.

## Building from Source

1. Download `build_vellum_attr_stream.py` from the [latest GitHub release](https://github.com/kleer001/funkworks/releases/latest)
2. Run with hython:
   ```bash
   hython build_vellum_attr_stream.py
   ```
3. The script writes `vellum_attr_stream.hda` alongside itself

Requires Houdini 19.5+ (any edition).

## Compatibility

- Houdini 19.5+
- Any Vellum Solver SOP (cloth, grain, hair — anything that wraps a popsolver internally)
- Any edition: Apprentice, Indie, Core, FX

## Notes

- **Why a microsolver.** Putting the streamer inside the popsolver's Pre-Solve chain is the same pattern SideFX uses internally for `muscleupdatevellum`. Microsolvers run every substep, which is exactly the cadence needed for time-varying attributes.
- **Why a SOP-level init wrangle.** Microsolvers do not execute on the creation frame in Houdini. Without the upstream wrangle, frame 1 of the simulation would always show whatever was on the geometry the very first time it was cooked into the solver. The init wrangle makes frame 1 deterministic.
- **`id` matching is preferred.** It survives upstream topology changes (resampled meshes, point-order shuffles). Use `ptnum` only when you control both sides and know point order is stable.
- **Re-running the setup is safe.** The script detects an existing streamer DOP and selects it instead of duplicating it.
