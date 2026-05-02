# Announcement Copy — Vellum Animated Attribute Streamer

## Short (Twitter / Mastodon / LinkedIn)

Vellum freezes SOP attributes at frame 1 — animated colors, masks, and weights painted upstream all stop updating. Vellum Animated Attribute Streamer is the HDA that fixes it.

New free Houdini DOP HDA: stream any animated point attribute into a live Vellum sim each substep.

https://kleer001.github.io/funkworks/vellum_attr_stream

#Houdini #VFX #Vellum #SideFX

---

## Medium (OdForce / Reddit r/Houdini — Markdown)

**Vellum Animated Attribute Streamer — free Houdini HDA for streaming animated SOP attributes into a live Vellum sim**

Vellum reads SOP point attributes once at sim init, then runs entirely in DOP space with no link back to the source SOP. Animated `Cd`, animated stiffness masks, time-varying pin weights — all silently dropped from frame 2 onward. The standard fixes (hand-rolled popwrangle microsolver, separate cache + Geometry Wrangle DOP, learning that microsolvers don't run on the creation frame) are nontrivial plumbing.

This HDA is that plumbing in one click. Same `popwrangle-in-Pre-Solve` pattern SideFX uses internally for `muscleupdatevellum`.

**What it does:**
- DOP HDA inserts a popwrangle microsolver into the Vellum Solver's popsolver Pre-Solve chain — fires every substep, copies listed point attributes from the upstream SOP onto the live sim points
- SOP-level init wrangle seeds frame 1 (microsolvers skip the creation frame in Houdini)
- Channel-referenced parms keep the SOP wrangle and DOP streamer in sync — edit one, both update

**Setup:** select Vellum Solver, **File > Run Script...**, pick the `.cmd`. Three files (`.cmd`, `.py`, `.hda`) sit in one folder. No shelf install, no copying into prefs, no restart.

**Supported attribute types:** float scalar/vec3/vec4 and integer scalar. Match by `id` (topology-safe) or `ptnum`.

Free download: https://kleer001.github.io/funkworks/vellum_attr_stream

Houdini 19.5+, any edition. FX users: a build script is included to compile the HDA clean under your own license.

🐜 More free tools at https://github.com/kleer001/funkworks

---

## Medium (SideFX Forums — BBCode)

[b]Vellum Animated Attribute Streamer — free Houdini HDA for streaming animated SOP attributes into a live Vellum sim[/b]

Vellum reads SOP point attributes once at sim init, then runs entirely in DOP space with no link back to the source SOP. Animated [code]Cd[/code], animated stiffness masks, time-varying pin weights — all silently dropped from frame 2 onward. The standard fixes (hand-rolled popwrangle microsolver, separate cache + Geometry Wrangle DOP, learning that microsolvers don't run on the creation frame) are nontrivial plumbing.

This HDA is that plumbing in one click. Same [code]popwrangle-in-Pre-Solve[/code] pattern SideFX uses internally for [code]muscleupdatevellum[/code].

[b]What it does:[/b]
[list]
[*]DOP HDA inserts a popwrangle microsolver into the Vellum Solver's popsolver Pre-Solve chain — fires every substep, copies listed point attributes from the upstream SOP onto the live sim points
[*]SOP-level init wrangle seeds frame 1 (microsolvers skip the creation frame in Houdini)
[*]Channel-referenced parms keep the SOP wrangle and DOP streamer in sync — edit one, both update
[/list]

[b]Setup:[/b] select Vellum Solver, [b]File > Run Script...[/b], pick the [code].cmd[/code]. Three files ([code].cmd[/code], [code].py[/code], [code].hda[/code]) sit in one folder. No shelf install, no copying into prefs, no restart.

[b]Supported attribute types:[/b] float scalar/vec3/vec4 and integer scalar. Match by [code]id[/code] (topology-safe) or [code]ptnum[/code].

Free download: [url=https://kleer001.github.io/funkworks/vellum_attr_stream]https://kleer001.github.io/funkworks/vellum_attr_stream[/url]

Houdini 19.5+, any edition. FX users: a build script is included to compile the HDA clean under your own license.

🐜 More free tools at [url=https://github.com/kleer001/funkworks]https://github.com/kleer001/funkworks[/url]

---

## Long (Blog / Newsletter)

**Vellum Animated Attribute Streamer: stop letting Vellum freeze your animated attributes**

Here's a Vellum behavior that catches people when they try to art-direct a cloth sim with animated attributes: you paint a bright animated `Cd` mask onto a grid, run it through Vellum Constraints into a Vellum Solver, hit play, and the color is locked to whatever it was on frame 1. Every frame after that, it stays put. Same for animated stiffness, animated pin weights, animated thickness — anything you put on a SOP-level point attribute that varies over time.

This isn't a bug. Vellum's solver reads SOP attributes exactly once, when the simulation initialises. After that the sim runs in the DOP context with no automatic link back to whatever SOP produced the cloth. The values are silently dropped from frame 2 onward. There's no warning. The Geometry Spreadsheet on the upstream wrangle shows the attribute changing per frame; the Geometry Spreadsheet on the solver output shows it frozen.

The standard fixes are all real, none of them are great:

- Hand-roll a popwrangle microsolver inside the Vellum Solver's `dopnet1/vellumsolver1/popsolver`, wire it into the Pre-Solve merge, write VEX that reads from a SOP via `op:` reference and matches points by id or ptnum.
- Cache the animated attributes to disk and use a Geometry Wrangle DOP to read them back. (Now your sim depends on a per-frame cache.)
- Discover that microsolvers don't run on the creation frame in Houdini, so frame 1 still shows the wrong thing even after the microsolver works on every later frame, and you have to add a SOP-level wrangle upstream to seed it.

This HDA is all of that plumbing in one HDA plus a one-click setup script. The pattern is the same one SideFX uses internally for `muscleupdatevellum` — a popwrangle inside the popsolver's Pre-Solve chain, sampling an upstream SOP every substep via `op:` reference.

**What gets inserted.** The setup script unlocks the Vellum Solver SOP, dives down to `dopnet1/vellumsolver1/popsolver`, finds the merge node feeding the Pre-Solve input, and attaches a `vellum_attr_stream` DOP HDA to a free input. That HDA contains the popwrangle. Then it goes back up to the SOP level and inserts an Attribute Wrangle (`vellum_attr_stream_init`) upstream of the Vellum Solver, with the same VEX, which seeds frame 1.

**Why two wrangles.** The microsolver inside the popsolver Pre-Solve chain runs every substep — that's what you want for streaming animated values into the live sim. But Houdini's microsolvers don't fire on the creation frame, so frame 1 of the simulation would still show whatever happened to be on the geometry the very first time it cooked into the solver. The SOP-level wrangle handles that frame-1 case. Its parameters are channel-referenced from the DOP streamer, so editing one updates both — no bookkeeping.

**Setup.** The plugin ships as three files: `vellum_attr_stream_setup.cmd`, `vellum_attr_stream_setup.py`, and `vellum_attr_stream.hda`. Save them all in one folder. Select your Vellum Solver, File > Run Script, pick the `.cmd`. The `.cmd` is a one-line HScript dispatcher that finds the `.py` and `.hda` next to itself via `$arg0` and exec's the Python with `__file__` set. There's nothing to install into Houdini prefs. There's no shelf to maintain. The setup script auto-installs the HDA if it isn't already loaded, and it's idempotent — re-running on an already-set-up solver selects the existing streamer instead of duplicating it.

**Supported attributes.** Float scalar, float vector (3), float vector4 (4), and integer scalar. Strings, matrices, primitive/vertex/detail attributes are out of scope — point-to-point matching is the common case the plugin targets. Match by `id` (survives upstream topology shuffles) or `ptnum` (when both sides have identical point order).

Free download: https://kleer001.github.io/funkworks/vellum_attr_stream

Houdini 19.5+, any edition. FX users get a build script (`build_vellum_attr_stream.py`) to compile the HDA clean under their own license and avoid the Indie/Apprentice flag.

🐜 More free tools at https://github.com/kleer001/funkworks
