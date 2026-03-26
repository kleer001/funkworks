# Funkworks Growth Strategy

## The Core Thesis

Every plugin we ship creates surface area across multiple channels. Each channel feeds signal back into the research pipeline. The system compounds: more plugins → more surface area → more signal → better plugins → more surface area.

This document maps the full growth engine — all channels, all feedback loops, and how they connect.

---

## Growth Axes

Funkworks grows in five directions simultaneously. Each axis reinforces the others.

| Axis | What It Means | Primary Channel |
|------|---------------|-----------------|
| **Catalog depth** | More plugins per DCC app | Plugin factory pipeline |
| **Catalog breadth** | More DCC apps supported | Houdini, AE, Nuke expansion |
| **Audience reach** | More people know we exist | YouTube, Reddit, forums, SEO |
| **Audience trust** | People who know us believe we ship useful tools | GitHub activity, docs quality, community responsiveness |
| **Pipeline speed** | Time from "someone complained" to "here's a free plugin" shrinks | Automation, MCP, auto-tutorials |

Growth on any axis accelerates the others. A faster pipeline means more plugins. More plugins mean more reach. More reach means more signal. More signal means better plugins.

---

## Channel Map

### 1. GitHub Repository

**Role:** Home base. Source of truth. Trust signal.

| Function | How It Grows Funkworks |
|----------|----------------------|
| Plugin source code | Open-source builds trust; contributors may appear |
| GitHub Releases | Zero-friction distribution — `.py` download, no account needed |
| GitHub Issues | Direct bug reports and feature requests from users |
| Stars / forks | Social proof visible to anyone evaluating the project |
| Commit history | Shows the project is alive and actively maintained |
| README + docs | SEO — GitHub pages rank well for "[problem] blender addon" queries |

**Feedback loop:**

```
User finds plugin via any channel
    ↓
Visits GitHub to download
    ↓
Stars the repo (social proof for next visitor)
    ↓
Opens an Issue ("could you also do X?")
    ↓
Issue feeds into Research Pipeline
    ↓
We build X → new release → new star → repeat
```

### 2. YouTube

**Role:** Evergreen discovery engine. Permanent search entry points.

Detailed strategy in [youtube_growth_strategy.md](youtube_growth_strategy.md).

**Key feedback loops:**
- Plugin → video → comments → next plugin idea
- Search → video → plugin download → subscriber → sees all future releases
- Shorts (algorithmic reach) → walkthrough (conversion) → deep dive (authority)

### 3. Reddit & Forums

**Role:** Ground-level signal source and launch pad for each plugin.

| Forum | Function |
|-------|----------|
| r/blender (1.4M) | Largest Blender community; primary signal source and launch audience |
| BlenderArtists | Dedicated forum; long-form discussions, higher signal-to-noise than Reddit |
| Blender Stack Exchange | Q&A format; extremely specific problems = extremely specific plugin ideas |
| r/Houdini, SideFX forums, od\|force | Houdini expansion signal sources |
| r/AfterEffects, aescripts forums | AE expansion signal sources |

**Feedback loop:**

```
Community post describes a pain point
    ↓
Research pipeline detects it (crawler)
    ↓
We build the plugin
    ↓
We post the solution back to the original thread
    ↓
Thread upvotes/shares it (we solved THEIR stated problem)
    ↓
Other readers discover Funkworks
    ↓
They post their own pain points (some in our spaces now)
    ↓
Repeat
```

**Why posting back matters:** We're not self-promoting. We're answering a question that was already asked. The community thread is the proof that demand existed before we built anything.

### 4. Blender Extensions Platform

**Role:** In-app discovery. Frictionless install.

| Factor | Detail |
|--------|--------|
| Reach | Every Blender user sees the Extensions browser by default |
| Trust | Official platform = implicit endorsement |
| Friction | One-click install from inside Blender — no file download, no manual addon install |
| Requirements | GPL license, review process, `blender_manifest.toml` |

**Feedback loop:**

```
User discovers plugin in Extensions browser
    ↓
Installs with one click
    ↓
Extension ratings/reviews visible to next user
    ↓
Positive review → more installs → higher ranking in browser
    ↓
More users → more feedback → better plugins
```

**When to pursue:** After 3–5 plugins are stable and tested. The review process adds overhead — batch submissions rather than submitting each plugin individually.

### 5. Plugin Documentation Site

**Role:** SEO surface area. Self-service support. Trust through thoroughness.

Each plugin gets a documentation page (auto-generated — see [auto_tutorial_pipeline.md](auto_tutorial_pipeline.md)) that ranks for search queries like "blender batch rename UV maps addon."

**Feedback loop:**

```
User searches "[problem] blender"
    ↓
Finds our tutorial/doc page (SEO)
    ↓
Downloads plugin → problem solved
    ↓
Bookmarks site / subscribes to RSS
    ↓
Sees future plugin docs when published
    ↓
Each new doc page adds another search entry point
```

The docs site is a **compounding asset** — every plugin adds a page, every page is a permanent search entry point. Unlike social media posts, documentation pages don't decay.

### 6. Email / Newsletter (Later)

**Role:** Owned audience. Not subject to algorithm changes.

| Phase | What to Send |
|-------|-------------|
| Early (plugins 1–5) | Don't bother. Focus on making good plugins. |
| Mid (plugins 6–15) | Monthly digest: new plugins, upcoming ideas, one "behind the scenes" of the pipeline |
| Mature (15+ plugins) | Weekly or biweekly. Feature requests poll. Early access to new plugins for subscribers. |

**Feedback loop:**

```
User signs up (from docs site, YouTube description, or GitHub README)
    ↓
Receives new plugin announcements directly
    ↓
Replies with feature requests (high-signal — they opted in)
    ↓
Requests feed Research Pipeline
    ↓
We build what they asked for → announce via email → they share it
```

Email is the only channel where you own the distribution. YouTube can change the algorithm. Reddit can change the API. Your email list is yours.

---

## Cross-Channel Feedback Loops

The real power isn't any single channel — it's the connections between them.

### The Master Loop

```
Community pain point (Reddit / forums / YouTube comments / GitHub Issues)
    ↓
Research Pipeline detects and scores it
    ↓
Plugin Factory builds the plugin
    ↓
Auto-Tutorial Pipeline generates docs + screenshots
    ↓
Launch simultaneously across all channels:
  ├── GitHub Release (download)
  ├── Docs site page (SEO)
  ├── YouTube video (discovery)
  ├── Reddit/forum post back to original thread (community)
  ├── Blender Extensions (in-app discovery, when ready)
  └── Email to subscribers (owned audience)
    ↓
Each channel generates new signal:
  ├── GitHub Issues → direct feature requests
  ├── YouTube comments → "can you also do X?"
  ├── Reddit replies → related pain points
  ├── Docs site search analytics → what people are looking for
  └── Email replies → high-intent requests
    ↓
All signal feeds back into Research Pipeline
    ↓
Next plugin
```

### The Trust Flywheel

```
Ship free, useful plugin
    ↓
Users trust Funkworks a little more
    ↓
They try the next plugin without hesitation
    ↓
They recommend us to colleagues
    ↓
New users arrive pre-trusting ("my friend uses their tools")
    ↓
Lower barrier to adoption for every subsequent plugin
    ↓
Funkworks becomes the default answer to "is there a plugin for that?"
```

**Everything is free, always.** The plugins are free. The source is open. The tutorials are free. This isn't a freemium funnel — it's the mission. We build tools because the community needs them, not because we need revenue from them.

### The Pipeline Speed Loop

```
Faster pipeline (better MCP, auto-tutorials, automated testing)
    ↓
More plugins per month
    ↓
More surface area across all channels
    ↓
More signal from more users
    ↓
Better plugin ideas (higher-signal input)
    ↓
Higher-quality plugins
    ↓
More trust per plugin shipped
    ↓
Each plugin does more growth work per unit of effort
```

Pipeline speed isn't just an efficiency gain — it compounds through every other loop.

---

## Signal Source Priority

Not all feedback channels are equal. Ranked by signal quality:

| Priority | Source | Why |
|----------|--------|-----|
| 1 | GitHub Issues on our repos | User already installed the plugin, hit a real problem, took time to file |
| 2 | Email replies from subscribers | Opted in, engaged, high intent |
| 3 | YouTube comments on our videos | Watching our content = already in our audience |
| 4 | Reddit/forum replies to our launch posts | Engaged with our specific plugin |
| 5 | Blender Extensions reviews | Used the plugin, left feedback |
| 6 | General Reddit/forum crawl | Broad signal, lower specificity — but highest volume |
| 7 | YouTube comments on competitor tutorials | Relevant audience, but not ours yet |

The Research Pipeline should weight signals accordingly. A GitHub Issue requesting a feature is worth 10 random Reddit complaints about the same topic.

---

## Growth Phases

### Phase 0 — Foundation (Now)

- [x] Research pipeline (Reddit crawler + digest agent)
- [x] First plugin (Fluid Domain Auto-Visibility)
- [x] Branding (Red Ant Foreman, tagline, tone)
- [x] Plugin template (README, listing, announce)
- [ ] YouTube channel created
- [ ] Docs site scaffolded (GitHub Pages or static site)
- [ ] GitHub repo README polished for visitors

### Phase 1 — First Launch (Plugin 1)

- [ ] Publish Fluid Domain Auto-Visibility to GitHub Releases
- [ ] Generate tutorial docs with screenshots (auto-tutorial pipeline)
- [ ] Record + publish YouTube walkthrough + short
- [ ] Post to r/blender and BlenderArtists
- [ ] Measure: downloads, stars, comments, community reception

### Phase 2 — Establish the Loop (Plugins 2–5)

- [ ] Ship 4 more plugins through the full pipeline
- [ ] Each launch hits all channels simultaneously
- [ ] Start monitoring our own YouTube comments + GitHub Issues as signal sources
- [ ] Refine the auto-tutorial pipeline based on first runs
- [ ] Submit first batch to Blender Extensions Platform

### Phase 3 — Expand and Accelerate (Plugins 6–15)

- [ ] Integrate all signal sources into a unified Research Pipeline dashboard
- [ ] Launch email newsletter
- [ ] First Houdini plugin (MCP already exists)
- [ ] Compilation content ("10 Blender annoyances we fixed")
- [ ] Measure pipeline speed: days from opportunity detection to published plugin

### Phase 4 — Scale (15+ plugins)

- [ ] AE and Nuke expansion based on accumulated signal
- [ ] Community contributors submitting plugin ideas via structured templates
- [ ] Pipeline fully autonomous: opportunity → plugin → docs → publish with minimal human checkpoints

---

## Metrics Dashboard

### Loop Health Metrics

| Metric | Measures | Healthy Target |
|--------|----------|---------------|
| **Signal-to-plugin ratio** | How many detected opportunities result in shipped plugins | >10% of "Build This" rated items ship within 30 days |
| **Plugin-to-channel coverage** | Does every plugin launch hit all active channels | 100% — no plugin ships without docs, announcement, and at least one video |
| **Time to first feedback** | How quickly the first substantive comment/issue arrives after launch | <48 hours (if longer, distribution isn't reaching the right people) |
| **Feedback-to-pipeline rate** | What fraction of user feedback enters the Research Pipeline | >80% of actionable requests get logged |
| **Cross-channel referral** | Do users find us through multiple channels | >20% of GitHub visitors come from YouTube or docs site |

### Growth Metrics (Per Phase)

| Phase | Key Metric | Target |
|-------|-----------|--------|
| 1 | First plugin downloaded by a stranger | 1 download from someone who isn't you |
| 2 | Repeat users | >10% of plugin 1 users also install plugin 2+ |
| 3 | Inbound signal exceeds outbound research | More ideas from our audience than from crawling |
| 4 | Community self-sustaining | More plugin ideas come from our audience than from crawling |

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Spreading too thin across channels | Nothing done well | Phase gates enforce focus — don't start email until Phase 3, don't add new DCCs until Phase 4 |
| Plugin quality drops as speed increases | Trust flywheel reverses — users stop installing | Smoke tests are a hard gate. No plugin ships without passing. Manual spot-check every 5th plugin. |
| Single-DCC dependency (Blender only) | Vulnerable to Blender API changes or community shifts | Expand to Houdini in Phase 3 (MCP exists). Architecture already supports multi-DCC. |
| Community perceives us as extractive (mining forums for ideas) | Reputation damage | Everything is free and open-source. We solve problems people stated publicly. We post solutions back to the threads. Transparent, not extractive. |
| GitHub goes down / changes terms | Lose distribution hub | Docs site is independent. Blender Extensions is independent. Don't put all distribution on one platform. |
