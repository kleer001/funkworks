# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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

### Data Flow

```
Reddit → crawler → raw JSON → digest agent → Claude → opportunities JSON
                                                            ↓
                                                   developer picks idea
                                                            ↓
                                                   plugins/<dcc>/src/<name>.py
```
