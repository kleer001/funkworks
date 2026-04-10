---
name: digest
description: >-
  Classify raw Reddit posts into Blender plugin opportunities using Claude agents.
  Reads the latest raw posts file (or a specified path), classifies each post,
  writes a cleaned opportunities JSON, and deletes the raw file.
argument-hint: "[raw_posts.json] (optional — defaults to latest in data/raw/)"
allowed-tools: Read, Glob, Write, Bash, Agent
---

Classify raw Blender Reddit posts into plugin opportunities.

## Step 1: Locate the raw posts file

If `$ARGUMENTS` is provided and points to an existing file, use it.
Otherwise, find the most recently modified file matching `data/raw/raw_blender_*.json`.

Read the file. It is a JSON array of objects with keys: `title`, `body`, `signals`.

## Step 2: Split into batches of 20

Divide the posts array into batches of up to 20 posts each.

## Step 3: Classify each batch in parallel

For each batch, spawn a general-purpose agent with this prompt (fill in the numbered posts):

---
You are a plugin opportunity analyst for the Blender 3D community.

Classify each post below for its potential as a new Blender addon/plugin.

For each post return a JSON object with these exact fields:
- `type`: one of `"pain_point"`, `"feature_request"`, `"workflow_gap"`, `"bug_upstream"`
- `complexity`: one of `"trivial"`, `"moderate"`, `"hard"`, `"research_required"`
- `novelty`: one of `"novel"`, `"competitive_opportunity"`, `"already_solved"`
- `specificity`: one of `"high"`, `"medium"`, `"low"`
- `summary`: one sentence describing the actionable plugin need, or null
- `keep`: true or false

Set `keep=false` if any of:
- specificity is "low"
- post is a showcase, artwork, or render with no plugin need
- type is "bug_upstream" with no obvious plugin-based workaround
- novelty is "already_solved" AND the solution is free and widely known
- post is a general beginner question with no plugin angle

Return a JSON array of exactly N objects (one per post, same order). No prose, just JSON.

Posts:
[NUMBERED POST LIST]
---

Collect the JSON array result from each agent.

## Step 4: Merge and filter

From the combined results (paired back with their source posts by index):
- Keep only entries where `keep` is true
- For each kept entry, output: `title` (from source post), `type`, `complexity`, `novelty`, `specificity`, `summary`

## Step 5: Write output

Derive the output path:
- If a specific input path was given: `data/digests/opportunities_<timestamp>.json`
- Use today's date in `YYYY-MM-DD` format for the timestamp

Write the kept opportunities as a JSON array to that path.

Print a summary: total posts classified, opportunities kept, output path.

## Step 6: Delete the raw file

Delete the raw posts file — it is temporary and contains unvetted user data.

## Step 7: Report

Show the final list of kept opportunities, grouped by `type`, with their `summary` lines.
