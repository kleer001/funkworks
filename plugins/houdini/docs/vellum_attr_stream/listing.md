# Release Notes — Vellum Animated Attribute Streamer v0.1.128

## Short Description

Free Houdini DOP HDA: stream animated SOP point attributes (color, weight, stiffness mask, anything) into a live Vellum simulation each substep, defeating Vellum's default behavior of freezing SOP attributes at frame 1.

## What It Does

Vellum reads SOP attributes once when the sim initializes, then runs entirely in the DOP context with no automatic link back to the source SOP. Animated values painted upstream — a sweeping color mask, a time-varying pin weight, a stiffness ramp — are silently dropped from frame 2 onward.

Vellum Animated Attribute Streamer fixes that. A popwrangle microsolver inside the Vellum Solver's popsolver Pre-Solve chain samples the upstream SOP every substep and copies listed point attributes onto the live sim points. A SOP-level init wrangle seeds frame 1 (microsolvers don't run on the creation frame in Houdini).

The setup is one click: select the Vellum Solver, **File > Run Script...**, pick `vellum_attr_stream_setup.cmd`. Three files (`.cmd`, `.py`, `.hda`) sit in one folder. No shelf install, no copying into `$HOUDINI_USER_PREF_DIR`, no restart.

**Supported attribute types:** float scalar, float vector (3), float vector4 (4), integer scalar
**Match modes:** by `id` (survives upstream topology shuffles) or by `ptnum` (when point order is identical)
**Pattern:** same `popwrangle-in-Pre-Solve` structure SideFX uses internally for `muscleupdatevellum`

## Features

- **Per-substep streaming** — popwrangle microsolver runs every substep, not just every frame
- **Frame-1 init wrangle** — SOP-level seed wrangle ensures the first cooked frame already reflects the source (microsolvers skip the creation frame)
- **Channel-referenced parms** — the SOP init wrangle's parms link to the DOP streamer's parms, so editing one updates both
- **Idempotent setup** — re-running the script on an already-configured solver is a no-op; it selects the existing streamer
- **Single-file install path** — `.cmd` dispatcher resolves siblings via `$arg0`; works wherever you drop the trio

## Requirements

- Houdini 19.5 or later (any edition)
- Works in any Vellum Solver SOP (cloth, grain, hair — anything wrapping a popsolver)

## Assets

- `vellum_attr_stream_setup.cmd` — File > Run Script entry point (Houdini's Run Script only accepts `.cmd`)
- `vellum_attr_stream_setup.py` — setup logic (the .cmd's only job is to dispatch to this)
- `vellum_attr_stream.hda` — the DOP HDA itself, ready to install via Asset Manager if you prefer
- `build_vellum_attr_stream.py` — build script for compiling the HDA under your own Houdini license (required for FX users who need an unencumbered HDA)

## Tags

houdini, vellum, dop, sop, attribute-streaming, microsolver, popwrangle, simulation, hda
