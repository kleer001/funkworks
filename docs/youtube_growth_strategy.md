# YouTube Growth Strategy — Funkworks

## Why YouTube

YouTube is the only platform where Blender tutorials have **compounding discoverability**. A Reddit post dies in 48 hours. A YouTube video answering "how do I hide fluid domain in Blender" gets searched for years. Every plugin we ship has a natural video counterpart — and that video becomes a permanent acquisition channel for the plugin.

YouTube also closes the loop with the research pipeline: the comment sections on our own videos become a direct signal source for new plugin ideas.

---

## Content Pillars

Three types of video, each serving a different stage of the growth engine:

| Pillar | Format | Length | Purpose |
|--------|--------|--------|---------|
| **Pain-Point Shorts** | "This annoyed me, so I fixed it" | 30–60s | Reach — algorithmic discovery, hooks viewers who share the frustration |
| **Plugin Walkthrough** | Install → use → result | 3–8 min | Conversion — turns viewers into plugin users |
| **Workflow Deep Dive** | Full workflow showing the problem + manual workaround + plugin solution | 10–20 min | Authority — establishes Funkworks as the "tools that fix real problems" channel |

Every plugin ships with all three. The Shorts drive impressions, the Walkthrough drives downloads, the Deep Dive drives subscribers.

---

## The Growth Engine (Feedback Loops)

### Loop 1: Plugin → Video → Plugin Users → Comments → Next Plugin

```
Ship plugin
    ↓
Publish video (walkthrough + short)
    ↓
Video comment section fills with:
  - "Can you make one that does X?"
  - "This is great but I also need Y"
  - "Does this work with Z workflow?"
    ↓
Feed comments into Research Pipeline
(same as Reddit/forum crawling — new signal source)
    ↓
Build next plugin addressing the most-requested need
    ↓
Repeat
```

**Why this compounds:** Each plugin video creates a surface area for discovering the *next* plugin idea. The audience is pre-qualified — they're already Blender users who install addons. Their requests are high-signal.

### Loop 2: Search → Video → Plugin → Subscriber → Catalog

```
User searches "blender fluid domain visibility problem"
    ↓
Finds our video (SEO-optimized title + description)
    ↓
Installs the free plugin
    ↓
Subscribes ("this channel makes tools I actually need")
    ↓
Sees future plugin releases in their feed
    ↓
Uses those too — without needing to search again
```

**Why this compounds:** Every video is a permanent search entry point. The subscriber base grows monotonically. Each new subscriber sees every future release automatically. Distribution cost per plugin drops toward zero as the channel grows.

### Loop 3: Shorts → Algorithm → Walkthrough → Deep Dive (Content Ladder)

```
Short goes viral-ish (30s pain-point demo)
    ↓
Viewer clicks channel → watches walkthrough
    ↓
Walkthrough end-screen links to deep dive
    ↓
Deep dive viewer is now a subscriber + plugin user
    ↓
They share the short with colleagues
    ↓
Repeat
```

**Why this compounds:** Shorts are the top-of-funnel. They cost almost nothing to produce (screen recording + voiceover of the pain point). Even modest view counts (1K–5K) on Shorts drive qualified traffic to the longer content.

### Loop 4: Community → Content → Community (Flywheel)

```
Blender community posts about a pain point
    ↓
Research pipeline detects it
    ↓
We build the plugin + video
    ↓
We post the video back to the community thread
    ↓
Community shares it — we're solving THEIR stated problem
    ↓
More community members follow the channel
    ↓
They post more pain points (in our comments now)
    ↓
Repeat
```

**Why this compounds:** We're not inventing demand. We're responding to stated demand with a solution and linking it back to the people who asked. This makes every launch feel organic, not promotional.

---

## Content-to-Pipeline Integration

### Research Pipeline Additions

The existing crawler monitors Reddit. Extend it to also monitor:

| Source | Signal | Implementation |
|--------|--------|---------------|
| **Our YouTube comments** | Direct feature requests from plugin users | YouTube Data API v3 — poll comment threads on our videos |
| **Competitor tutorial comments** | "I wish there was a plugin for this" | YouTube Data API v3 — monitor comments on top Blender tutorial channels |
| **Our YouTube Analytics** | Which search terms bring traffic; which videos have high retention | YouTube Studio API — feed search terms into opportunity scoring |

These feed into the same Research Queue alongside Reddit signals.

### Plugin Launch Checklist (Updated)

Each plugin release now includes:

- [ ] Plugin code + smoke tests (existing pipeline)
- [ ] Written docs + announcement copy (existing pipeline)
- [ ] **Short video** — 30–60s screen recording of the pain point + one-click fix
- [ ] **Walkthrough video** — 3–8 min install-to-result tutorial
- [ ] **Deep dive video** — 10–20 min (optional for simple plugins, required for complex ones)
- [ ] **YouTube description** with plugin download link, timestamps, related videos
- [ ] **Pinned comment** with FAQ and link to GitHub Issues
- [ ] Post short + walkthrough link to the original community threads that inspired the plugin

---

## Channel Identity

Derived from existing branding:

| Element | Decision |
|---------|----------|
| **Channel name** | Funkworks |
| **Tagline** | *Built because we needed it too.* |
| **Mascot presence** | Red Ant Foreman appears in thumbnails, lower-third, end-screen |
| **Thumbnail style** | Before/after split: left = frustration (red tint, cluttered viewport), right = solution (green tint, clean result) |
| **Voice/tone** | Practical, no-hype, slightly dry. "Here's a thing that's annoying. Here's the fix. Here's how to install it." |
| **Intro** | No intro. Start with the problem. First 3 seconds = the pain point. |
| **Outro** | 5s end-screen: "More tools like this → subscribe" + plugin link |

---

## Metrics That Matter

Vanity metrics (total views, subscriber count) are less important than loop health:

| Metric | What It Tells You | Target (First 6 Months) |
|--------|-------------------|------------------------|
| **Comments with feature requests** | Loop 1 is working — audience is telling us what to build next | 5+ actionable requests per video |
| **Plugin downloads per video view** | Conversion — videos are driving adoption | >2% click-through to download link |
| **Search impression share** | Loop 2 is working — videos are ranking for pain-point queries | Top 10 for "[problem] blender" queries we target |
| **Subscriber-to-view ratio on new videos** | Returning audience — subscribers are watching new releases | >30% of views from subscribers |
| **Shorts → Walkthrough click-through** | Loop 3 is working — content ladder is functional | >5% click-through from Short to Walkthrough |
| **Community thread engagement** | Loop 4 is working — community shares our solutions | Positive reception when posting back to original threads |

---

## Production Pipeline

Keep it minimal. The videos are not the product — the plugins are. Videos serve the plugins.

### Equipment / Setup

- Screen recording: OBS (free)
- Audio: Any USB mic, room tone is fine — this isn't ASMR
- Editing: DaVinci Resolve (free) or even just cut in OBS
- Thumbnails: Blender viewport screenshot + text overlay in GIMP/Figma

### Per-Video Workflow

```
1. Screen-record the pain point (30s of "watch how annoying this is")
2. Screen-record the plugin solving it (30s of "now watch this")
3. Screen-record the full walkthrough (install → configure → use → result)
4. Record voiceover (or type captions for Shorts)
5. Cut together in DaVinci Resolve
6. Export: Short (vertical 9:16), Walkthrough (16:9), Deep Dive (16:9)
7. Upload all three, schedule Shorts first, Walkthrough 24h later, Deep Dive 48h later
8. Post links to community threads
```

Estimated time per plugin: 2–4 hours of video production. This is the only manual step that the agent pipeline doesn't handle (yet).

---

## Phasing

| Phase | When | Focus |
|-------|------|-------|
| **Phase 0** | Now | Create channel, upload banner/avatar (Red Ant Foreman), write channel description |
| **Phase 1** | First plugin launch | Ship walkthrough + short for Fluid Domain Auto-Visibility. Gauge response. |
| **Phase 2** | Plugins 2–5 | Establish the three-pillar pattern. Start monitoring our own comments for Loop 1. |
| **Phase 3** | Plugins 6–10 | Integrate YouTube comments into the research pipeline (automated). First deep dive video. |
| **Phase 4** | 10+ plugins | Compilation videos ("10 Blender annoyances we fixed"), community spotlights, behind-the-pipeline deep dives |

---

## Risks

| Risk | Mitigation |
|------|------------|
| Video production becomes a bottleneck that slows plugin output | Keep videos minimal. A screen recording with captions is fine. Don't let production quality delay plugin launches. |
| Low initial views are demoralizing | The strategy is search-based, not viral-based. Early videos may get 50–200 views but those are *searchers with the exact problem*. Quality of viewer > quantity. |
| Comments are mostly spam or low-signal | Moderate early. Pin a comment asking specific questions ("What Blender workflow annoys you most?"). Delete spam aggressively. |
| YouTube algorithm changes tank reach | Shorts are the algorithm-dependent piece. Walkthroughs and Deep Dives are search-dependent, which is more stable. Don't over-index on Shorts. |
| Someone else makes the same plugins + videos | Speed advantage: our pipeline can ship a plugin + video faster than a solo developer. Community goodwill advantage: we're building what they asked for, publicly. |
