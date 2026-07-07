---
name: digest
description: >-
  Classify raw DCC forum posts into plugin/addon/HDA opportunities using Claude Haiku agents.
  Reads the latest raw posts file (or a specified path), classifies each post with Haiku,
  clusters kept entries by underlying need, and writes a deduplicated opportunities JSON.
argument-hint: "[raw_posts.json] (optional — defaults to latest in data/raw/)"
allowed-tools: Read, Glob, Write, Bash, Agent, WebSearch
---

Classify raw DCC forum posts into plugin/addon/HDA opportunities.

## Step 1: Locate the raw posts file

If `$ARGUMENTS` is provided and points to an existing file, use it.
Otherwise find the most recently modified file in `data/raw/` matching `raw_*.json`.

## Step 2: Determine DCC context

The raw filename encodes the DCC and source info. Extract the DCC name from the segment
between `raw_` and the timestamp. Examples:
- `raw_Houdini_2026-04-17T22-48-41Z.json` → DCC name: `Houdini`
- `raw_Blender_2026-04-18T10-00-00Z.json` → DCC name: `Blender`

Read `data/dcc_configs/{dcc_name_lowercase}.json` if it exists. Use:
- `dcc_name` = `name` field (e.g. `"Houdini"`)
- `api_name` = `api_name` field (e.g. `"Houdini Python/VEX API"`)
- `plugin_label` = first entry in `plugin_terms` (e.g. `"hda"`, `"addon"`)
- `sources` = list of forum sources this data was collected from

If no config exists, default `dcc_name` to the extracted name, `api_name` to
`"{dcc_name} scripting API"`, and `plugin_label` to `"plugin"`.

Note: the raw posts file contains posts aggregated from **all configured forum sources**
(which may include Reddit, Discourse forums, RSS feeds, Stack Exchange, etc.) — not just
one forum. Treat all posts equally regardless of their origin.

## Step 3: Ensure data is recent (less than 7 days)

If the raw file's mtime is older than 7 days, or no raw file was found, trigger a fresh
crawl across all configured sources by running:

```
python3 -m src.crawlers
```

(The `FUNKWORKS_SUBREDDIT` env var selects the DCC; it is set in `.env` or defaults to
`blender`. For other DCCs, set it before running.) Wait for completion and use the
newly written raw file.

## Step 4: Read the raw posts file

The file is a JSON array of objects with keys: `title`, `body`, `signals`, and
optionally `replies`, `views`, `score`, `date`, `url` (the permalink to the
source post — carry it through to the output so origin records can cite it).
Note the total count.

## Step 5: Split into batches of 50

Divide the array into batches of up to 50 posts each.

## Step 6: Classify each batch in parallel using Haiku

For each batch, spawn an Agent with **model: "haiku"** and this prompt (substitute
`{dcc_name}`, `{api_name}`, `{plugin_label}` with the Step 2 values, and fill in the
numbered posts — include `replies`, `views`, `score` when present):

---
You are a plugin opportunity analyst for the {dcc_name} community. You are filtering for
a very specific kind of plugin: small, focused tools that automate one repetitive mechanical
workflow step using only the {dcc_name} native scripting API.

Target examples of the RIGHT kind of plugin:
- "Auto-insert visibility keyframes to hide the fluid domain box before simulation start" (3 keyframes, 1 button, 110 lines)
- "Split only edges tagged as panel gaps, leave render-sharp edges untouched" (1 operator, 220 lines)
- "Resize and fit an image into a canvas with letterbox/fill/crop modes, replacing a multi-node chain" (1 node, no external deps)

These posts come from various {dcc_name} forums and discussion boards. Classify each one
for its potential as a new {dcc_name} {plugin_label}/tool.

Return a JSON array containing ONLY the posts worth keeping (keep=true). Omit all others entirely.
Each object in the array:
- `index`: the 1-based position of this post in the input list
- `type`: "pain_point" | "feature_request" | "workflow_gap" | "bug_upstream"
- `complexity`: "trivial" | "moderate" | "hard" | "research_required"
  ("research_required" = unclear if the {api_name} supports this)
- `novelty`: "novel" | "competitive_opportunity" | "already_solved"
- `specificity`: "high" | "medium" | "low"
- `summary`: one sentence in the form "Automate [specific mechanical action] for [workflow context]"

Include a post ONLY if ALL of these hold:
- The post describes a step the artist must perform manually every time for a specific workflow (not a one-time setup, not a creative choice)
- The step is fully mechanical — no artistic judgment is needed to execute it
- A single operator using only the {dcc_name} native API (~50–300 lines) could replace the manual steps
- The problem is NOT obviously solved by an existing built-in feature or widely-known free plugin

Omit the post (do not include it) if ANY of these apply:
- Post is about achieving a visual aesthetic, look, or rendering style ("how do I make it look like X")
- Solving it requires artistic iteration or per-case human judgment — can't be deterministically automated
- The scope implies a multi-tool suite rather than one focused operator
- Commercial software (ZBrush, Substance Painter, dedicated retopo apps, etc.) handles this as core functionality
- The friction is inside the DCC's renderer, compiler, or simulation solver — an upstream bug with no plugin workaround
- specificity is "low"
- post is a showcase, artwork, render, or announcement with no tool need
- post is a general beginner question with no tool angle
- post describes user confusion with a standard documented feature — skill issue, not a tool gap
- post is about hardware, career advice, courses, or software installation

If no posts in the batch qualify, return an empty array [].
No prose. Return ONLY the raw JSON array starting with [ and ending with ].

Posts:
[NUMBERED POST LIST — include engagement data if present, e.g. "replies: 42, score: 180"]
---

Collect the JSON array result from each agent.

## Step 7: Merge kept entries

Each batch result contains only the posts Haiku judged worth keeping, each with an `index`
field (1-based position within that batch). Use `index` to look up the corresponding source
post and carry forward: `title` (from source), `type`, `complexity`, `novelty`,
`specificity`, `summary`, the source `url` (for provenance — keep it even when
null), and any engagement fields present in the source post
(`replies`, `views`, `score`, `date`).

## Step 7.5: Verify each candidate is real, buildable, and unclaimed

Before clustering, kill any kept entry that fails verification. Run all three checks below,
cheapest-authoritative first. The classifier over-rates novelty — it has no addon-ability
check and no view of the paid market, so most entries that reach here are already dead.
Verify **every** kept entry, including those marked `novel`. When any check is uncertain,
drop — a re-implemented or impossible tool costs the portfolio more than a missed gap.

### 7.5a — Addon-ability + native probe (headless, authoritative)

A web search cannot tell you whether a Python {plugin_label} can *actually* build the tool,
or whether a native operator already does it. The DCC's own headless interpreter can — this
is the most reliable check and catches false positives that survive web search.

For each candidate, write a short probe that lists the relevant operators / RNA enums / API
methods for the candidate's action, then run it headless:

- **Blender:** `blender --background --factory-startup --python <probe.py>`
- **Houdini:** `hython <probe.py>`
- Other DCCs: the app's headless script interpreter.

Have the probe print two answers:
1. **Already native?** Does a built-in operator — with the needed parameters / enum values —
   already perform this action? If yes → drop (already solved).
2. **Addon-reachable?** Is the capability exposed to the scripting API at all, or is it
   C-side only (fixed enums the API can't extend, DNA-only flags with no RNA, missing API
   methods, solver/renderer-internal behavior)? If the only path is a core/C change a
   {plugin_label} cannot make → drop (not addon-able, however novel).

C-side-only asks a probe exposes: new snap-target enum values, F9/redo-panel pins,
file-browser default paths, modifier-internal name flipping, absent bpy API methods.

### 7.5b — Market check, paid AND free

1. `WebSearch` for `"{dcc_name} addon [core action from summary]"` — **no "free" qualifier**,
   so paid Gumroad / Superhive / Orbolt competitors surface too. A saturated paid market
   means no differentiation even for a free portfolio piece.
2. `WebSearch` for `"{dcc_name} addon [core action] free"` to catch free/maintained tools.
3. If either search shows a tool covering the use case: drop the entry.

### 7.5c — "Abandoned free plugin" is a signal to investigate, not a green light

When 7.5b finds a free tool that's abandoned or stalled, find out *why* before treating the
space as open — the cause of death decides viability:
- **Went native** — the DCC bundled the feature; the addon was redundant before its last
  commit → DEAD, don't rebuild.
- **API-break maintenance tax** — killed by a breaking API change, not infeasibility; the
  niche is still open but a rebuild inherits the same recurring maintenance cost →
  viable-but-flagged.
- **Plain repo rot** — developer disinterest, never replaced natively, API still supports it
  → clean rebuild, a real pick.

Only plain repo rot is a clean pick.

Run probes and searches in parallel across candidates when practical — batch independent
headless probes into one script, and issue independent `WebSearch` calls in one message.

## Step 8: Cluster by underlying need using Haiku

Spawn one Agent with **model: "haiku"** passing the full list of kept summaries (numbered).
Prompt:

---
You are grouping plugin opportunity summaries by the specific automatable action they describe.
Many differently-worded posts may be asking for the same one-button tool.

Group the numbered summaries below into clusters. Each cluster = one specific mechanical action
a plugin could automate. Do NOT group posts just because they share a broad problem domain —
only group posts that describe the exact same repeatable workflow step.
Summaries that don't share an automatable action with any other go into a singleton cluster.

Return a JSON array of cluster objects, each with:
- `need`: one crisp sentence phrased as "Automate X when doing Y" or "One-click [action] for [workflow]" — name the specific mechanical step that would be eliminated, not the broad problem
- `posts`: array of original post indices (1-based) in this cluster
- `count`: number of posts in this cluster
- `best_summary`: the single summary from the cluster that is most actionable
- `type`: majority `type` across posts in the cluster
- `complexity`: majority `complexity` across posts in the cluster

Sort by `count` descending. No prose. Return ONLY the raw JSON array.

Summaries:
[NUMBERED SUMMARY LIST]
---

## Step 9: Drop singletons, merge engagement signals

From the cluster list:
- Drop any cluster where `count == 1` (one-off, no corroborating signal)
- For each surviving cluster, sum the `replies`, `views`, and `score` across all its
  member posts (use 0 for missing fields). Add these as `total_replies`, `total_views`,
  `total_score` on the cluster object.
- Sort surviving clusters by `total_replies` descending (deepest threads first).

## Step 10: Write output

Path: `data/digests/opportunities_{dcc_name_lowercase}_{YYYY-MM-DD}.json`

Write the surviving clusters as a JSON array. Each entry:
```json
{
  "need": "...",
  "count": 3,
  "total_replies": 94,
  "total_views": 1200,
  "total_score": 47,
  "type": "pain_point",
  "complexity": "moderate",
  "best_summary": "...",
  "posts": [
    {"title": "title A", "url": "https://..."},
    {"title": "title B", "url": "https://..."},
    {"title": "title C", "url": null}
  ]
}
```

Each `posts` entry carries the source `title` and `url` from the merged kept
entries (Step 7). Keep `url` as `null` when the source post had none — never
drop the field. This is what lets `/new-plugin` write real `source_url` values
into origin records instead of retroactive null stubs.

## Step 11: Delete the raw file

Delete the raw posts file — temporary, contains unvetted user data.

## Step 12: Report

Print: total posts classified → kept after filtering → clusters after dedup → singletons dropped.
Show surviving clusters sorted by `total_replies`, each with `need`, `count`, and `total_replies`.
