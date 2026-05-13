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
optionally `replies`, `views`, `score`, `date`.
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
`specificity`, `summary`, and any engagement fields present in the source post
(`replies`, `views`, `score`, `date`).

## Step 7.5: Verify novelty via web search

Before clustering, drop any kept entry where a free, actively maintained solution already
exists OR the workflow is already covered by a built-in feature. Verify **all** kept
entries — including those marked `novel`. The classifier does not have full visibility
into the addon ecosystem or recent built-in operators.

For each kept entry, regardless of its `novelty` field:

1. `WebSearch` for `"{dcc_name} addon [core action from summary] free"`.
2. If results show a free, maintained plugin covering the use case: drop the entry.
3. If `novelty` is `"novel"`, run a second `WebSearch` for
   `"{dcc_name} [core action] built-in"` to surface native operators.
4. If a built-in operator or documented native workflow covers it: drop the entry.

Maximum two searches per candidate. When uncertain, drop — the cost of a re-implementation
in the portfolio outweighs the cost of missing a real gap.

Run searches in parallel (one message, multiple `WebSearch` calls) when verifying
multiple candidates.

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
  "posts": ["title A", "title B", "title C"]
}
```

## Step 11: Delete the raw file

Delete the raw posts file — temporary, contains unvetted user data.

## Step 12: Report

Print: total posts classified → kept after filtering → clusters after dedup → singletons dropped.
Show surviving clusters sorted by `total_replies`, each with `need`, `count`, and `total_replies`.
