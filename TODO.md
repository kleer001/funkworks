# TODO

## Build the Vellum Animated SOP Attr Streamer HDA

Next queued Houdini plugin. Selected from the April sweep after the Alembic
prim-attr promoter idea was dropped (Maya-side bottleneck, not addressable
in an HDA).

**Spec:** `spec_houdini_vellum_animated_attr.md`

**Scope:** ~120-line SOP-Solver-wrangle HDA inside a Vellum Solver. Streams
animated point attributes (`Cd`, mass, pintoanimation, stiffness, etc.)
into the live sim every frame instead of locking them at start-frame. Two
forum threads as engagement signal (9 replies total).

**Kick off with:** `/new-plugin vellum_animated_attr_stream`

## Run the Right-Click Select historical sweep

One-time deep crawl of all 16,794 RCS ideas to surface high-vote unimplemented
feature requests — the long-tail goldmine the routine crawler can't reach.

**When:** off-peak UTC (02:00–08:00). Don't kick off during EU/US daytime.

**How:**
```bash
tmux new -s rcs   # or screen
python3 scripts/rcs_historical_sweep.py
# detach: Ctrl-b d
```

**Time:** ~2.5 hours unattended. Strict 6s between every request.

**Outputs (will appear when done):**
- `data/rcs_index_full.json` — flat index of all entries (~3-4 MB)
- `data/rcs_top_open_ideas.json` — open ideas with net votes ≥ 10, full body, sorted (~500 KB)

**Resume if interrupted:**
```bash
python3 scripts/rcs_historical_sweep.py --resume
```
State checkpoint lives at `/tmp/rcs_sweep_state.json`.

**Spec:** `spec_rcs_historical_sweep.md`
