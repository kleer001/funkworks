# Spec: Right-Click Select Historical Sweep

## Purpose

One-time deep crawl of the entire Right-Click Select archive to produce a
permanent reference dataset of high-vote, unimplemented Blender feature
requests. This is the long-tail goldmine the routine crawler can't reach:
ideas posted years ago, accumulated significant vote totals, and never
addressed by core devs — exactly what an addon can fill.

The routine `rightclickselect` source crawls only the most recent ~30 pages.
This sweep walks all 1,050 pages once, then we maintain the resulting
shortlist by hand or via occasional re-runs.

## Source

- API: `https://blender.community/api/rightclickselect/ideas/?page=N`
- Detail: `https://blender.community/api/rightclickselect/ideas/{hashId}/`
- Total entries at time of writing: **16,794** across **~1,050 pages** (16/page)
- No auth, no rate-limit headers documented, no working `ordering=` parameter

## Politeness contract

The CLAUDE.md rule is **6-second minimum between requests to the same host,
no exceptions**. The sweep must respect this rigidly. blender.community is
a small community-funded site; we are not entitled to fast crawls.

- 6s sleep between every request, including detail fetches
- Single connection, no concurrency
- Resume-from-checkpoint so a connection drop doesn't re-hit pages we already have
- `User-Agent: funkworks/0.1 (https://github.com/kleer001/funkworks; portfolio research)` so the operator can identify and block us if needed
- If any request returns 429 / 5xx, back off (60s, then 300s, then abort)
- Do not run during typical EU/US daytime hours; schedule for ~02:00–08:00 UTC

## Time budget

- 1,050 list pages × 6s = 105 minutes baseline for the index pass alone
- Detail bodies are the expensive part. Two strategies:
  - **(a) Index-only pass first** (~1.75 hours), then a second pass that fetches
    detail bodies *only for entries above a vote threshold* (e.g. `score >= 10`).
    With ~500 such entries (rough estimate), that's another ~50 minutes.
    Total: ~2.5 hours, ~1,500 requests.
  - **(b) Fetch every detail inline** — 1,050 + 16,794 = 17,844 requests × 6s
    = ~30 hours. Rejected. Disrespectful and wasteful.
- Strategy (a) is the plan.

## Output

Two files, both checked in (small, valuable, non-PII):

1. `data/rcs_index_full.json` — flat array of all 16,794 entries with the list-API
   fields only (no body): `hashId`, `title`, `categories`, `developmentStatus`,
   `votesPositiveCount`, `votesNegativeCount`, `commentsCount`, `likesCount`,
   `datePublished`, `absoluteUrl`. ~3-4 MB.

2. `data/rcs_top_open_ideas.json` — filtered shortlist of high-signal entries
   with full body. Filter:
   - `developmentStatus == "open"`
   - `votesPositiveCount - votesNegativeCount >= 10` (tunable)
   - Sorted by net votes descending
   Each entry adds `body` (HTML stripped to text, capped at 2000 chars) and
   `url` (absolute). Expected size: a few hundred entries, ~500 KB.

## Resume / checkpoint

`scripts/rcs_historical_sweep.py` writes incremental state to
`/tmp/rcs_sweep_state.json`:

```json
{
  "phase": "index" | "detail",
  "last_page_done": 73,
  "index": [ ... entries collected so far ... ],
  "detail_done_hash_ids": ["abc123", ...]
}
```

On startup, if state file exists and is < 7 days old, resume from the next page
or next un-fetched detail. Delete the state file on successful completion.

## Script outline

```python
# scripts/rcs_historical_sweep.py
#
# usage:
#   python3 scripts/rcs_historical_sweep.py            # run from scratch
#   python3 scripts/rcs_historical_sweep.py --resume   # continue from /tmp state
#
# Writes:
#   data/rcs_index_full.json
#   data/rcs_top_open_ideas.json

import argparse, json, logging, sys, time
from pathlib import Path
from bs4 import BeautifulSoup
from src.crawlers.base import make_session

API = "https://blender.community/api/rightclickselect/ideas/"
DELAY = 6.0          # politeness floor
MIN_VOTES_FOR_BODY = 10
STATE = Path("/tmp/rcs_sweep_state.json")
INDEX_OUT = Path("data/rcs_index_full.json")
TOP_OUT = Path("data/rcs_top_open_ideas.json")

# Phase 1: walk pages 1..N until results empty, save list-API fields only.
# Sleep DELAY between every request. Persist state every 10 pages.
# Backoff: on 429/5xx, sleep 60s then retry; if it fails twice, sleep 300s then abort.

# Phase 2: from index, filter open + score >= MIN_VOTES_FOR_BODY,
# fetch each detail (sleep DELAY between), strip HTML body, append to TOP_OUT.

# On any abort, ensure STATE is fresh so --resume works.
```

## Operator runbook

1. Confirm we are off-peak (UTC 02:00–08:00). Don't kick off at 14:00 EU time.
2. `python3 scripts/rcs_historical_sweep.py` in a tmux/screen session, or
   `nohup python3 ... &` with output redirected to a log file.
3. Walk away. The sweep takes ~2.5 hours uninterrupted.
4. On return, check `data/rcs_top_open_ideas.json` exists and has reasonable
   size (~hundreds of entries). Spot-check a few to confirm body extraction
   is clean.
5. `git add data/rcs_index_full.json data/rcs_top_open_ideas.json` if happy.

## Re-runs

Don't re-run unless you specifically want updated vote counts. The sweep is
expensive on the host. Plan: run once now, run again no more than every
6 months.

## Failure modes

- **Cloudflare bot challenge**: blender.community sits behind Cloudflare. If
  responses start returning HTML challenges instead of JSON, abort immediately
  and reconsider. Adding a real browser User-Agent string and slower delays
  may help; consider Playwright as a last resort. Do not try to circumvent.
- **API schema change**: detect by missing `results` key in list response or
  missing `content` field in detail. Log loudly and stop; we'll patch.
- **Site goes read-only / shut down**: nothing to do. We have whatever index
  we got via checkpoint state.
