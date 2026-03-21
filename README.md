<div align="center">

<img src="docs/images/mascot.png" alt="Funkworks Mascot" width="200">

# Funkworks

**Addons built from real problems.**<br>
*Small tools. Big difference.*

Free addons that eliminate repetitive workflow steps for digital artists.

Starting with Blender and r/blender, the goal is to expand across DCC tools (Houdini, Maya, Cinema 4D, etc.) and artist communities — automatically surfacing pain points and shipping targeted solutions wherever artists are struggling.

---

</div>

## Plugins

| Plugin | Description |
|--------|-------------|
| [Fluid Domain Auto-Visibility](plugins/fluid_domain_visibility/) | One-click visibility keyframing for fluid simulation domains |

## Research Pipeline

Plugin ideas are sourced from r/blender using a two-stage pipeline:

```bash
# 1. Crawl Reddit for pain points (requires .env with REDDIT_USER_AGENT)
python -m src.crawlers.reddit

# 2. Classify raw posts with Claude to find plugin opportunities
python -m src.digest.agent data/raw/<raw_file>.json data/digests/<output>.json
```

Output lands in `data/digests/` as JSON files with classified opportunities.

### Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env — set REDDIT_USER_AGENT=funkworks/0.1 by u/YOUR_USERNAME
```

### Running Tests

```bash
pytest
```

## Adding a New Plugin

1. Write the addon: `plugins/[plugin_name].py`
2. Copy `plugins/_template/` to `plugins/[plugin_name]/`
3. Fill in `README.md`, `listing.md`, and `announce.md`
4. Add a row to the table above
