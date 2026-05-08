# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

Funkworks is a **portfolio piece**. It exists to demonstrate expertise, care, and work ethic to prospective employers and partners. Every artifact in this repo — code, docs, commit history, architecture decisions — should reflect that. Quality matters more than speed. Thoughtfulness matters more than volume. Everything is free and open-source as a matter of principle, not as a business strategy. There is no monetization layer and never will be.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run a single test file
pytest tests/test_reddit_crawler.py

# Run a single test
pytest tests/test_reddit_crawler.py::TestFetchOpportunities::test_filters_and_deduplicates

# Run with coverage
pytest --cov

# Run the crawler (requires REDDIT_USER_AGENT in .env)
python -m src.crawlers.reddit

# Run the digest agent on crawler output
python -m src.digest.agent <raw_posts.json> <output.json>
```

No build or lint steps are configured.

## Architecture

Funkworks has two independent components: a **research pipeline** for identifying Blender addon ideas, and the **addon deliverables** themselves.

### Research Pipeline

Two-stage pipeline: crawl → classify.

**Stage 1 — Reddit Crawler** (`src/crawlers/reddit.py`):
- Hits public Reddit `.json` endpoints (no OAuth)
- Filters out showcase/art flairs, deduplicates by post ID
- Regex-classifies posts into signal types (`question`, `how_to`, `plugin_addon`, `workflow_pain`, etc.)
- Writes two files: `data/raw/raw_blender_<ts>.json` (posts) and `data/digests/digest_blender_<ts>.json` (summary counts)
- Entry point: `crawl(config) → (digest_dict, raw_posts_path)`

**Stage 2 — Digest Agent** (`src/digest/agent.py`):
- Reads raw posts JSON, calls Claude (`claude-opus-4-6`) in batches of 20
- Claude returns structured `PostClassification` (Pydantic) per post: `type`, `complexity`, `novelty`, `specificity`, `summary`, `keep`
- Writes `data/digests/digest_<ts>.json` with only `keep=True` entries
- Deletes the raw posts file after processing
- Entry point: `run_digest(raw_posts_path, output_path, client=None) → int`

**Config** (`src/config.py`): Frozen dataclass, loaded from `.env` via `python-dotenv`. `REDDIT_USER_AGENT` is the only required env var.

### DCC Plugins

Plugins are organized by target application under `plugins/<dcc>/`:

```
plugins/
└── blender/
    ├── src/              # distributable single-file .py addons
    ├── docs/
    │   ├── <name>/       # per-plugin docs: README.md, listing.md, announce.md
    │   ├── specs/        # design specs for planned plugins
    │   ├── tutorials/
    │   └── images/
    └── _template/        # copy when creating a new plugin
```

Future DCC targets (Houdini, Nuke, etc.) follow the same layout under `plugins/<dcc>/`.

Blender plugins register an `Operator` class and a `Panel` class, following standard Blender addon conventions. Use `plugins/blender/_template/` when creating a new one.

The GitHub Pages tutorial for each plugin lives at `docs/<name>.md` (problem, install, step-by-step usage, notes).

### Provenance

Origin records for shipped plugins live at `data/origins/origins.jsonl` (gitignored — internal tool, not published). Append-only JSONL, one record per originating post. A plugin can have multiple records when several posts converged on the same need.

```json
{"plugin_id": "zoom_blur_cop", "captured_at": "2026-04-22", "source_url": "https://reddit.com/r/Houdini/comments/abc/...", "venue": "reddit:r/Houdini", "post_date": "2026-04-15", "tags": ["radial", "blur", "cop"], "notes": "asker wanted action-zoom effect"}
```

Field rules:
- `tags` — 5–10 short keywords; candidate `must_any` terms for the future engagement matcher.
- `notes` — short prose; quoting the post directly is fine since the file is internal.
- `captured_at_retroactively: true` and `source_url: null` — flag for entries reconstructed after the fact, when no originating post could be located. Omit the flag when false.

The `/new-plugin` skill captures one or more origin records as its first step. No silent skips.

### Skills

Claude Code skills live in `.claude/skills/`. Each skill is a directory with a `SKILL.md` file.

| Skill | Invocation | Purpose |
|-------|-----------|---------|
| `new-plugin` | `/new-plugin <name>` | Build and document a new Blender addon end-to-end |
| `tutorial` | `/tutorial <plugin-name>` | Write a step-by-step tutorial for an existing plugin |
| `digest` | `/digest [raw.json]` | Classify raw Reddit posts into plugin opportunities using Claude agents (no API key needed) |

### Data Flow

```
Reddit → crawler → raw JSON → digest agent → Claude → opportunities JSON
                                                            ↓
                                                   developer picks idea
                                                            ↓
                                                   /new-plugin command
                                                   (addon + docs + tutorial page)
                                                            ↓
                                                   developer tests in Blender
                                                            ↓
                                                   /publish command (planned)
                                                   - package zip
                                                   - GitHub Release + attach zip
                                                   - patch [link] in announce.md
                                                   - post to Reddit
                                                            ↓
                                                   kleer001.github.io/funkworks
```
