# Plugin Factory: Research Agent Team

## Philosophy

The goal is a continuous, low-noise signal about what real users in real production environments actually need. Three agent tiers, each feeding the next. The output of the whole system is a prioritized opportunity queue — not a pile of forum posts.

The research side answers one question: **"What should we build next?"** It does this by listening to communities at scale, filtering noise, and surfacing genuine gaps where a plugin would solve a real problem.

---

## Architecture Overview

```
Sources (Forums, Reddit, Discord)
    ↓
Tier 1 — Crawlers (always on, collect raw posts)
    ↓
Raw Post Queue (structured JSON, one entry per post)
    ↓
Tier 2 — Digest Agents (daily batch, classify and filter)
    ↓
Cleaned Opportunity List (tagged, scored, deduplicated)
    ↓
Tier 3 — Synthesis Agent (weekly, cluster and rank)
    ↓
Weekly Opportunity Report (5–10 ranked items per app)
    ↓
Human Rating (Build This / Watch / Discard)
```

---

## Tier 1 — Crawlers (Always On)

These agents run continuously and do nothing but collect. They monitor a fixed list of sources and write raw findings to a queue. No summarizing, no scoring — just harvest.

### Sources per Application

**Blender:**

| Source | Type | Access Method | Notes |
|--------|------|---------------|-------|
| [r/blender](https://reddit.com/r/blender) | Reddit (~1.4M members) | Reddit API (OAuth, free tier) | Largest Blender community online |
| [Blender Artists](https://blenderartists.org) | Forum (Discourse) | RSS / scraping | Primary dedicated Blender forum, very active |
| [Blender Stack Exchange](https://blender.stackexchange.com) | Q&A | Stack Exchange API (free) | Strong signal — users describe specific problems |
| [Blender Dev Talk](https://devtalk.blender.org) | Forum (Discourse) | RSS / scraping | Developer-facing; good for API gap discovery |
| YouTube comment sections | Comments | YouTube Data API v3 | Top tutorial channels (Blender Guru, CG Cookie, etc.) |

**After Effects:**

| Source | Type | Access Method | Notes |
|--------|------|---------------|-------|
| [r/AfterEffects](https://reddit.com/r/AfterEffects) | Reddit (~175K members) | Reddit API (OAuth, free tier) | Most active AE community |
| [aescripts.com forums](https://aescripts.com/forums/) | Forum | Scraping | Product discussions; restructured in recent years — comments moved from product pages to a separate forums area |
| [Adobe Community AE Forum](https://community.adobe.com/t5/after-effects/ct-p/ct-after-effects) | Forum | Scraping | Official Adobe support forum; high volume, mixed signal |
| [Creative COW AE Forum](https://creativecow.net/forums/) | Forum | Scraping | Legacy resource, declining activity — still has archival value and occasional posts |
| [School of Motion Community](https://www.schoolofmotion.com/) | Forum / Course community | Scraping | Professional motion design focus |

**Houdini:**

| Source | Type | Access Method | Notes |
|--------|------|---------------|-------|
| [SideFX Forums](https://www.sidefx.com/forum/) | Forum (Houdini Lounge, Technical Discussion) | Scraping | Official and very active |
| [r/Houdini](https://reddit.com/r/Houdini) | Reddit (~7K members) | Reddit API (OAuth, free tier) | Smaller but active |
| [od\|force](https://forums.odforce.net/) | Forum | Scraping | Long-running independent Houdini community; highly technical |
| Houdini Discord (unofficial) | Discord | Discord bot / API | Community-run servers (e.g., Think Procedural); not an official SideFX server |

**Nuke:**

| Source | Type | Access Method | Notes |
|--------|------|---------------|-------|
| [Foundry Community Forum](https://community.foundry.com/discuss/nuke) | Forum | Scraping | Official Nuke forum (Nuke Users, Nuke Dev sections) |
| [r/vfx](https://reddit.com/r/vfx) | Reddit (~58K members) | Reddit API, filtered for Nuke mentions | Mixed VFX discussion; requires keyword filtering |
| Nuke Facebook Groups | Facebook | Facebook Graph API / scraping | "The Foundry Nuke" and "The Foundry Nuke Artists" groups |
| Compositor Discord servers | Discord | Discord bot / API | Scattered across multiple servers (Hugo's Desk, etc.); no single canonical group |

### What Crawlers Capture

Each raw post is stored as a structured record:

```json
{
  "source_url": "https://...",
  "source_name": "r/blender",
  "timestamp": "2026-03-15T14:22:00Z",
  "software_tag": "blender",
  "post_type": "question",
  "title": "Is there a way to batch rename UV maps across multiple objects?",
  "body": "I have 200+ objects imported from...",
  "author": "username",
  "engagement": {
    "upvotes": 47,
    "comments": 12
  }
}
```

**Capture criteria:** Anything that looks like a question, complaint, feature request, workflow friction, or "does anyone know how to..." post. The crawler does not judge relevance — that's Tier 2's job.

### Schedule and Rate Limits

**Target cadence:** Every 6–12 hours per source, respecting rate limits.

**Reddit API constraints (as of 2023+):**
- Free tier: 100 requests/minute (OAuth), 10 requests/minute (unauthenticated)
- Free tier is restricted to **non-commercial use only**
- Commercial use requires an enterprise agreement ($12,000+/year as of 2024)
- Pushshift (historical Reddit data archive) was shut down by Reddit in 2024
- **Implication for this project:** The free tier is sufficient for low-frequency polling of a handful of subreddits. This is a non-commercial open-source project, so the free tier applies. Monitor usage to stay within limits.

**Other APIs:**
- Stack Exchange API: Free, generous rate limits (300 requests/day unauthenticated, 10,000/day with API key)
- YouTube Data API v3: Free tier with 10,000 units/day quota (a search costs 100 units, a comment list costs ~3 units) — sufficient for daily polling of specific channels
- Forum scraping: Most forums have no API; use RSS feeds where available, fall back to polite scraping with 5–10 second delays between requests
- Discord: Requires a bot account in each server; check each server's rules about bots before deploying

---

## Tier 2 — Digest Agents (Daily Batch)

Once per day, a digest agent processes the previous day's raw queue. For each item it assigns:

### Classification Schema

| Field | Values | Purpose |
|-------|--------|---------|
| **Type** | Pain point / Feature request / Workflow gap / Bug (upstream) | Distinguishes things we can solve from things only the app vendor can fix |
| **Software** | AE / Blender / Houdini / Nuke / Cross-host | Route to the correct build pipeline |
| **Complexity** | Trivial / Moderate / Hard / Research-required | Scoping for build agents; "Research-required" means the host API may not support this |
| **Novelty** | Novel / Competitive opportunity / Already solved | If a free or paid solution exists, either discard or flag — building a better version of an existing tool is valid but different from filling a gap |
| **Specificity** | High / Medium / Low | Is this person describing an actual production problem with enough detail to spec a solution, or venting generally? |

### Filtering Rules

Items are **dropped** if:
- Specificity is Low (vague complaints with no actionable detail)
- Novelty is "Already solved" AND the existing solution is free and widely known
- Type is "Bug (upstream)" with no plugin-based workaround possible

Items are **kept but deprioritized** if:
- Novelty is "Competitive opportunity" (existing paid solution exists, but a free or better one would have value)
- Complexity is "Research-required" (may not be feasible, but worth tracking)

### Output

A JSON list of tagged opportunities, target 20–30 items per day per application. Most days will yield fewer. Each item includes the original source URL, all classification fields, and a one-sentence summary generated by the LLM.

### Implementation Notes

The digest agent is an LLM call (Claude API) with structured output. The prompt includes:
- The classification schema above
- 10–15 few-shot examples of correctly classified items
- Instructions to be conservative — when in doubt, keep the item rather than discard it

Batch processing keeps costs predictable. At ~30 items/day across 4 applications, this is roughly 120 LLM calls/day — well within standard API budgets.

---

## Tier 3 — Synthesis Agent (Weekly)

Once per week, the synthesis agent looks across the daily digests and clusters related items. "I wish I could batch rename UV maps" appearing across 8 different posts in Blender forums over 3 weeks is a different signal than one person asking once.

### Clustering Approach

The synthesis agent groups items by semantic similarity using embedding-based clustering:

1. Embed all items from the past 7 daily digests
2. Cluster by cosine similarity (threshold tuned empirically, start at 0.82)
3. For each cluster, identify the core request and count unique sources

Single-occurrence items are kept but ranked lower unless they have high engagement (upvotes/comments) on their source post.

### Scoring

Each cluster (or standalone item) is scored on four dimensions:

| Dimension | Weight | Measurement |
|-----------|--------|-------------|
| **Frequency** | 30% | Number of unique posts/users expressing the same need |
| **Recency** | 20% | Items from the last 30 days weighted 2x; items older than 60 days decay to 0.5x |
| **Specificity** | 25% | Can this be solved with a plugin? Does the host API support it? |
| **Feasibility** | 25% | Given known API limitations, how hard is this to build? (Inverse of complexity — Trivial scores highest) |

### Weekly Opportunity Report

The output is a ranked list: **5–10 opportunities per application**, each containing:

- **Rank and score** (composite of the four dimensions)
- **One-paragraph summary** of the need
- **Source count** (how many independent posts/users)
- **Representative source links** (3–5 URLs)
- **Feasibility note** (what API surfaces are needed, any known blockers)
- **Existing solutions** (if any, with links — so you can evaluate competitive positioning)

**This is what lands in your queue for rating.**

---

## Rating Layer

### MVP (Manual)

You read the Weekly Opportunity Report and flag each item as:

- **Build This** — Goes to the Plugin Factory pipeline (Roadmap 2)
- **Watch** — Stays in the queue; if it appears again next week with higher frequency, reconsider
- **Discard** — Removed from the queue permanently

### Future (Automated Pre-Filter)

After 8–12 weeks of manual rating, you'll have enough labeled data to train a rating agent. The agent learns your taste — which types of opportunities you approve, which you consistently discard — and pre-filters the report so only candidates you're likely to approve reach your inbox.

The rating agent should **never auto-approve** — it pre-filters to reduce your review burden, but the human checkpoint remains. The value of this system is that it captures your judgment, not that it replaces it.

---

## Report Schedule Summary

| Cadence | Agent | Output | Estimated Volume |
|---------|-------|--------|-----------------|
| Every 6–12 hours | Crawlers | Raw post queue | 50–200 posts/day across all sources |
| Daily | Digest agents | Cleaned, tagged opportunity list | 20–30 items/day/app (after filtering) |
| Weekly | Synthesis agent | Ranked Opportunity Report | 5–10 items/app (your inbox) |
| Monthly (optional) | Trend agent | Cross-application trend summary | 1 report covering all 4 apps |

---

## What to Build First

**The crawler tier is the MVP.** Even a simple Python script hitting Reddit's API and a few forum RSS feeds, dumping results to a structured JSON file you read manually, proves the concept before any AI is involved.

### Suggested MVP Build Order

1. **Week 1:** Single Python script polling r/blender via Reddit API (OAuth, free tier). Store results as JSON. Read manually.
2. **Week 2:** Add Blender Artists and Blender Stack Exchange (RSS + Stack Exchange API). Still reading manually.
3. **Week 3:** Write the digest agent prompt and run it against accumulated data. Evaluate whether the LLM classifications are useful.
4. **Week 4:** If classifications are good, wire up the full daily batch. Add one more application's sources (Houdini, since the SideFX forums are active and well-structured).
5. **Weeks 5–8:** Build the synthesis agent. Run weekly reports. Start rating.

**Validate that the signal is real before building the digest and synthesis layers.** If the raw crawl data is mostly noise (memes, showcase posts, off-topic), the downstream agents won't help. The crawl data quality is the foundation.

### MVP Tech Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Crawler | Python + `praw` (Reddit) + `requests` (forums) + `feedparser` (RSS) | Simple, well-documented libraries |
| Storage | JSON files on disk, one per day | No database needed for MVP; migrate to SQLite or Postgres if volume grows |
| Digest agent | Claude API with structured output | Single prompt call per batch |
| Synthesis agent | Claude API + embedding model for clustering | `voyage-3` or similar for embeddings; Claude for summary generation |
| Report delivery | Markdown file generated weekly | Read in any editor; upgrade to email or Slack notification later |

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Reddit API rate limits or policy changes | Lose largest data source | Diversify sources early; Reddit is important but not sole source |
| Forum scraping breaks on layout changes | Missed data for days/weeks | Use RSS where available; monitor for scrape failures; alert on zero-result days |
| LLM classification drift | Bad filtering (good items dropped, noise kept) | Weekly spot-check of 10 random digest items; retune prompt if accuracy drops below 80% |
| Low signal-to-noise ratio | System produces noise, not insight | Start with manual review of raw data to validate the concept before investing in automation |
| Community source goes offline | Lose coverage for one app | CGTalk shut down in Jan 2024; Video Copilot forums went offline years ago — sources disappear. Maintain a backup list of alternative sources per app |
