<table>
<tr>
<td><img src="docs/images/mascot.png" alt="Funkworks Mascot" width="180"/></td>
<td>
<h1>Funkworks</h1>
<p><strong>Addons built from real problems.</strong><br>
<em>Small tools. Big difference.</em></p>
</td>
</tr>
</table>

![License](https://img.shields.io/github/license/kleer001/funkworks)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![Platform](https://img.shields.io/badge/platform-Linux%20|%20macOS%20|%20Windows-lightgrey)
![Blender](https://img.shields.io/badge/Blender-4.2+-orange?logo=blender)
![Tests](https://img.shields.io/github/actions/workflow/status/kleer001/funkworks/test.yml?label=tests)
![GitHub stars](https://img.shields.io/github/stars/kleer001/funkworks)
![GitHub forks](https://img.shields.io/github/forks/kleer001/funkworks)
![GitHub last commit](https://img.shields.io/github/last-commit/kleer001/funkworks)
![GitHub repo size](https://img.shields.io/github/repo-size/kleer001/funkworks)
![Contains Ants](https://img.shields.io/badge/Contains-🐜%20Ants-red)
![Works on my machine](https://img.shields.io/badge/Works%20on-my%20machine-success)
![Blender Addons](https://img.shields.io/badge/🎨-Blender%20Addons-blue)
![WIP](https://img.shields.io/badge/Status-WIP%20🚧-yellow)
![Badges](https://img.shields.io/badge/Badges-14-ff69b4)

Free addons that eliminate repetitive workflow steps for digital artists.

Starting with Blender and r/blender, the goal is to expand across DCC tools (Houdini, Maya, Cinema 4D, etc.) and artist communities — automatically surfacing pain points and shipping targeted solutions wherever artists are struggling.

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
