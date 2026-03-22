# DCC Extension Systems Research

## Community Activity Rankings

Software in each category sorted by size and activity of the plugin/extension-building community (most active first).

### 3D DCC Tools

1. **Unreal Engine** — Massive marketplace, huge open-source community, Blueprints lower the barrier to entry
2. **Unity** — Enormous Asset Store ecosystem, tens of thousands of editor extensions and packages
3. **Blender** — Exploding open-source community, thousands of add-ons on Superhive (formerly Blender Market), GitHub, and Gumroad
4. **Maya** — Decades of studio pipeline scripts, massive MEL/Python library, Autodesk App Store
5. **Houdini** — No central marketplace (Orbolt is dead), active HDA-sharing via GitHub/Gumroad/SideFX Labs, deep technical users
6. **3ds Max** — Large legacy plugin base (especially archviz), ScriptSpot community
7. **Godot** — Fast-growing open-source community, Asset Library with thousands of plugins
8. **Substance 3D Designer / Painter** — Active material-sharing community on Substance Share, growing plugin ecosystem
9. **Rhino / Grasshopper** — Strong architectural/parametric community, Food4Rhino marketplace with thousands of plugins
10. **SketchUp** — Extension Warehouse with thousands of Ruby plugins, large hobbyist + archviz base
11. **Cinema 4D** — Solid plugin scene, smaller than Maya/Max but dedicated (e.g., Rocket Lasso, Nitroman)
12. **ZBrush** — Moderate ZScript community, most extensions are brushes/alphas rather than code plugins
13. **Modo** — Small but dedicated community, kits shared on forums
14. **Marvelous Designer** — Very limited scripting community
15. **SideFX Solaris / USD** — Emerging ecosystem, mostly pipeline TDs at large studios

### 2D / Compositing / Motion Graphics

1. **After Effects** — Largest motion graphics plugin ecosystem by far (aescripts.com, Red Giant, Video Copilot, hundreds of script authors)
2. **Photoshop** — Massive plugin/action/script ecosystem spanning decades, UXP modernizing it
3. **Nuke** — Nukepedia has thousands of gizmos/scripts, studio pipeline scripts everywhere
4. **DaVinci Resolve / Fusion** — Rapidly growing due to free tier, active Fuse and script community on Reactor package manager
5. **GIMP** — Large open-source plugin registry, Script-Fu and Python-Fu communities
6. **Krita** — Growing open-source community, Python plugin ecosystem expanding
7. **TouchDesigner** — Active real-time/installation art community, lots of shared components and toxes
8. **Toon Boom Harmony** — Moderate scripting community, mostly studio-internal tools
9. **Clip Studio Paint** — Assets store is huge for brushes; code plugin community is smaller
10. **Figma** — Massive plugin community (thousands), but primarily UI/UX not traditional DCC
11. **Processing** — Large creative-coding library ecosystem, academic + art community
12. **Cavalry** — Small but growing motion-design community
13. **Flame** — Niche, high-end VFX — small community of pipeline TDs at major studios
14. **Natron** — Small open-source community, limited but dedicated
15. **OpenToonz** — Small community, mostly Japanese studio users
16. **Inkscape** — Moderate extension community, Python-based
17. **Notch** — Very small, niche real-time VFX community
18. **Motion (Apple)** — Minimal third-party plugin development
19. **Affinity Photo/Designer** — No plugin API yet, macros only

### Game-Adjacent / CAD / Other

1. **AutoCAD** — Decades of LISP/ARX plugins, Autodesk App Store, huge enterprise user base
2. **Figma** — Thousands of community plugins, very active TypeScript/JS developer scene
3. **Revit** — Large add-in ecosystem (pyRevit, Autodesk App Store), active BIM community
4. **Inkscape** — Moderate Python extension community

---

## Detailed Extension Systems Reference

### 3D DCC Tools

| Software | Extension Name | Language(s) | How It Works |
|---|---|---|---|
| **Blender** | Add-ons | Python | Python scripts registering Operator/Panel classes via `bl_info` dict. Installed as `.py` or `.zip`. |
| **Maya** | Plugins / MEL Scripts / Python Scripts | C++, MEL, Python | C++ plugins loaded via `MFnPlugin`. MEL/Python scripts run in the built-in script editor or `userSetup`. |
| **Houdini** | HDAs (Houdini Digital Assets), VEX, Python Scripts | VEX, Python, C++ (HDK) | HDAs are packaged node networks (`.hda`). VEX runs per-point/prim in wrangles. HDK is the C++ SDK for deep extensions. |
| **3ds Max** | Plugins / MAXScript / Python Scripts | C++, MAXScript, Python | C++ DLL plugins for geometry/modifiers. MAXScript is the built-in scripting language. Python support added later. |
| **Cinema 4D** | Plugins | C++, Python | C++ plugins via the Cinema 4D SDK. Python scripting via Script Manager and Python Generator/Effector objects. |
| **Modo** | Kits / Plugins / Scripts | C++, Python, Lua | Kits bundle commands, scripts, and configs. Python/Lua for scripting, C++ SDK for deep integration. |
| **ZBrush** | ZScripts / Plugins | ZScript | ZScript is a proprietary language controlling the UI and tool behavior. Plugins are packaged ZScript files. |
| **Substance 3D Designer** | Nodes / Plugins | C++, Python, MDL | Custom nodes via the SDK. Python API for automation. MDL for material definitions. |
| **Substance 3D Painter** | Plugins / Scripts | Python, JavaScript | JavaScript plugins for UI panels. Python scripting for pipeline automation. |
| **Unreal Engine** | Plugins / Blueprints | C++, Blueprints (visual) | C++ plugins via `.uplugin` descriptors. Blueprints are visual scripts. Editor utility widgets for tooling. |
| **Unity** | Packages / Editor Extensions | C# | Editor scripts in `Assets/Editor/`. Packages distributed via Package Manager or `.unitypackage`. |
| **Godot** | Plugins / GDExtensions | GDScript, C#, C++ | `addons/` folder with `plugin.cfg`. GDExtension allows C/C++ libraries loaded at runtime. |
| **Marvelous Designer** | Scripts | Python | Limited Python scripting API for automation. |
| **SketchUp** | Extensions / Plugins | Ruby | Ruby scripts packaged as `.rbz` files, installed via Extension Warehouse. |
| **Rhino / Grasshopper** | Plugins / GHA Components | C#, Python, RhinoScript (VBScript) | `.rhp` plugins via RhinoCommon SDK. Grasshopper components (`.gha`) for visual programming. Python via RhinoScriptSyntax. |
| **SideFX Solaris / USD** | Schemas / Plugins | C++, Python | USD plugin system for custom schemas, file format plugins, and render delegates. |

### 2D / Compositing / Motion Graphics

| Software | Extension Name | Language(s) | How It Works |
|---|---|---|---|
| **After Effects** | Scripts / Expressions / Plugins | ExtendScript (JS), C/C++ (AEGP SDK) | Scripts automate via ExtendScript. Expressions are per-property JS. C++ plugins for effects/formats via the AEGP SDK. |
| **Nuke** | Gizmos / Plugins / Python Scripts | Python, C++ (NDK), TCL | Gizmos are packaged node groups (`.gizmo`). Python for scripting. C++ NDK for custom nodes. Community shares on Nukepedia. |
| **DaVinci Resolve / Fusion** | Fuses / Scripts / Plugins | Lua, Python, C++ | Fuses are Lua-based custom nodes. Fusion scripting in Lua/Python. OpenFX plugins in C++. |
| **Natron** | PyPlugs / OFX Plugins | Python, C++ (OpenFX) | PyPlugs are grouped node presets saved as `.py`. Supports the OpenFX C++ plugin standard. |
| **Flame** | Plugins / Python Scripts | Python, C++ (Spark) | Spark API for C++ effects. Python hooks for pipeline integration and custom menus. |
| **Toon Boom Harmony** | Scripts | JavaScript (QTScript) | Scripts automate drawing/compositing tasks. Scripting toolbar runs JS in the built-in editor. |
| **OpenToonz** | Plugins / Scripts | C++, Lua | C++ plugin interface for effects. Lua scripting for automation. |
| **Clip Studio Paint** | Auto Actions / Plugins | JavaScript | Auto Actions for recorded macros. JS-based plugin API for custom tools and filters. |
| **Photoshop** | Plugins / Scripts / Actions | C++ (Filter SDK), JavaScript (UXP), ExtendScript | UXP is the modern JS plugin framework. Actions record/replay steps. Generator plugins for asset pipelines. |
| **Krita** | Plugins / Scripts | Python | Python plugins for custom dockers, filters, and tools. Installed via the Plugin Manager. |
| **GIMP** | Plugins / Script-Fu / Python-Fu | C, Python, Script-Fu (Scheme) | C plugins via `libgimp`. Script-Fu is a Scheme dialect. Python-Fu wraps the same PDB (Procedure Database) API. |
| **Affinity Photo/Designer** | Macros | Built-in macro recorder | Record-and-replay macros. No traditional plugin API (yet). |
| **Motion (Apple)** | Templates / Behaviors | FxPlug (ObjC/Swift) | FxPlug SDK for custom effects usable in Motion and FCPX. Behaviors are built-in procedural animation blocks. |
| **Cavalry** | Scripts / Expressions | JavaScript | JS expressions on any attribute. Scripting API for custom nodes and automation. |
| **Processing** | Libraries | Java, Python (Processing.py) | Community libraries installed via the Contribution Manager. Extend drawing, physics, data, etc. |
| **TouchDesigner** | Custom Operators / Extensions | Python, C++, GLSL | Python extensions on any component. C++ custom operators via the CPlusPlus TOP/CHOP/SOP API. GLSL for shader-based ops. |
| **Notch** | Nodes / Plugins | C++, GLSL | Custom effect nodes. GLSL for shader blocks. Designed for real-time VFX. |

### Game-Adjacent / CAD / Other

| Software | Extension Name | Language(s) | How It Works |
|---|---|---|---|
| **Revit** | Add-ins | C#, Python (pyRevit) | `.addin` manifest points to a .NET DLL. pyRevit wraps the API for quick Python scripts. |
| **AutoCAD** | Plugins / LISP / .NET | AutoLISP, C#/.NET, C++ (ObjectARX) | AutoLISP scripts are the classic extension. .NET and ObjectARX for heavier plugins. |
| **Figma** | Plugins / Widgets | TypeScript/JavaScript | Plugins run in a sandboxed iframe, access the Figma document API. Distributed via Community. |
| **Inkscape** | Extensions | Python | Python scripts conforming to the Inkscape extension API (INX descriptor + `.py` script). |

---

## Common Patterns

- **Python** is the most universal scripting language across DCCs — Blender, Maya, Houdini, Nuke, Substance, Krita, GIMP, TouchDesigner all support it.
- **C/C++ SDKs** exist for deep/performance-critical extensions in nearly every major tool.
- **Node-based tools** (Houdini, Nuke, Fusion, Natron) often let you package node groups as reusable assets (HDAs, Gizmos, Fuses, PyPlugs).
- **JavaScript/TypeScript** dominates in the 2D/web-adjacent tools (After Effects, Figma, Clip Studio, Cavalry).

---

## Where People Actually Get Plugins & Addons (March 2026)

Research date: 2026-03-22. Focused on where communities are *actually active*, not where they theoretically could be. Goal: identify the right venues for building community and reputation through free tools.

### Blender — Best Ecosystem for Community Building

Blender has the richest, most accessible plugin distribution ecosystem of any DCC tool.

| Venue | Type | Activity | Notes |
|---|---|---|---|
| **extensions.blender.org** | Official, free/GPL only | Growing fast | Built into Blender since 4.2 LTS. Drag-and-drop install. **Best venue for free community addons.** |
| **Superhive** (formerly Blender Market) | Paid marketplace | 62k+ products | Rebranded May 2025 (Blender Foundation trademark enforcement). Same team as CG Cookie. Dominant paid marketplace. |
| **Gumroad** | Paid + free | Very active | Popular with solo devs. Low friction. Cross-listing with Superhive is common. |
| **GitHub** | Free/open-source | Thousands of repos | `blender-addon` topic is huge. Distribute via Releases as .zip. Official blender-addons repo archived May 2025 (moved to projects.blender.org). |
| **BlenderKit** | In-Blender library | Growing | Expanded into addon distribution Feb 2026. Free tier available. |
| **itch.io** | Free + cheap | Small but real | Niche — procedural generators, retro shaders, game pipeline tools. |
| **FlippedNormals** | Was a marketplace | **Closing March 31, 2026** | Purchases transferring to Superhive. |

**Community hubs:**
- **r/blender** — 1.4M members. Massive. Primary discovery channel for free tools.
- **Blender Community Discord** — ~197k members. Very active Q&A and sharing.
- **BlenderArtists.org** — Active forums, Python scripting support section.
- **devtalk.blender.org** — Addon developer collaboration.
- **BlenderNation** — News/aggregation. Left Twitter/X in Nov 2024, now on Bluesky.

**Key trend:** AI-assisted addon creation (using Claude/ChatGPT to generate Python scripts) is a visible trend. Users generate and share scripts for tedious tasks.

**Recommendation for funkworks:** Post free addons on **extensions.blender.org** (widest organic reach, built into Blender) + **GitHub** (credibility, open source cred). Announce on **r/blender** and **BlenderArtists**. This is the highest-ROI community for reputation building.

**Ease of Entry — Ranked by Friction:**

1. **GitHub** — Easiest. Push a repo, tag a release as `.zip`, done. Zero gatekeeping.
2. **Gumroad** — Easy. Create account, upload `.zip`, set price (or free). Live in minutes.
3. **itch.io** — Easy. Similar to Gumroad, slightly more indie-game audience.
4. **r/blender / BlenderArtists / Discord** — Easy. Just post. Large audiences. Moderation is light.
5. **extensions.blender.org** — Moderate. Must pass review (GPL-compatible license, metadata requirements, basic quality checks). Review queue can take days. But once listed, the addon is installable directly from Blender's preferences — unbeatable distribution.
6. **Superhive** — Moderate. Seller application + review process. ~25% commission. Best for paid addons.
7. **BlenderKit** — Moderate. Requires account setup and asset approval. Free tier available.

---

### Houdini — Fragmented, No Central Marketplace

Orbolt is effectively dead. The ecosystem is scattered but the community is technically deep and generous.

| Venue | Type | Activity | Notes |
|---|---|---|---|
| **Orbolt** | Was the marketplace | **Dead in practice** | Still technically online but login is broken, no updates since 2022, not tracking current Houdini features. Nobody uses it. |
| **SideFX Labs** | Official, free | Active | Free community-driven HDAs maintained by SideFX. Installable via Houdini Launcher or GitHub. Includes Project Dryad, Vitruvius, Biome Tools. |
| **Gumroad** | Paid + free | **De facto commercial marketplace** | Modeler 2025, Soft Boolean, AI Assistant, terrain tools all sell here. This is where the money changes hands. |
| **GitHub** | Free/open-source | Growing | SideFX Labs repo is here. Community tools like MOPs, HNanoSolver, Simple Tree Tools. |
| **ArtStation Marketplace** | Paid | Growing | HDAs at $1–$20 price points. Cloud generators, building tools, hair cards. |
| **od|force forums** | Free sharing | Active (12 pages of tools) | Camera HDAs, slider tools, VEX builders. Recent posts Jan 2026. |

**Community hubs:**
- **SideFX Forums** — Official. Active for announcements and discussion, not primary download venue.
- **Think Procedural Discord** — Main unofficial Houdini server. Extremely generous community — post a question with a HIP file, get multiple solutions.
- **Official SideFX Discord** — Growing, Labs updates here.
- **CGWiki Discord** (Matt Estela's) — Patreon-supported, masterclasses.
- **r/Houdini** — ~7k subscribers. Small, niche, professional.

**Snippet culture:** Houdini has the strongest VEX snippet-sharing culture of any DCC. CGWiki (tokeru.com/cgwiki) is the beloved community resource. VEX snippets are core workflow.

**Key trend:** SideFX Project Skylark (mid-2025) released free HIP/HDA files for procedural environments. Houdini AI Assistant addon appeared on Gumroad (multi-provider: GPT, Claude, DeepSeek, Ollama).

**Recommendation for funkworks:** Houdini community is small but deeply technical. Share HDAs on **GitHub** + announce on **SideFX forums** and **Think Procedural Discord**. Sell premium tools on **Gumroad**. Skip Orbolt entirely.

**Ease of Entry — Ranked by Friction:**

1. **GitHub** — Easiest. Push HDAs/HIP files, done. Standard for free Houdini tools.
2. **Gumroad** — Easy. Upload HDA `.zip`, set price. De facto paid marketplace since Orbolt died.
3. **Think Procedural Discord / SideFX Forums / od|force** — Easy. Post and share. Small but generous community — you'll get feedback fast.
4. **ArtStation Marketplace** — Low-moderate. Account setup + listing. Low price points ($1–$20) common for HDAs.
5. **SideFX Labs** — Hard. Must be accepted by SideFX team as a contribution. High quality bar, code review, must fit their curation. But the payoff is massive — ships with Houdini Launcher.
6. **Orbolt** — Don't bother. Dead.

---

### Maya — Studio-Centric, Less Open

Maya plugin distribution is more institutional than community-driven.

| Venue | Type | Activity | Notes |
|---|---|---|---|
| **Autodesk App Store** | Official marketplace | Active (~141 plugins) | Small catalog. Publishers must target Maya 2026 for new submissions. |
| **Highend3D** (formerly CreativeCrash) | Free + paid | Alive, rocky history | Went offline for a period, came back. Long-term reliability uncertain. Scripts updated through Nov 2025. |
| **Gumroad** | Paid + free | Significant | Indie TDs sell here. Tiny Tools, Smart Layer, Mel Script bundles. Active through 2026. |
| **GitHub** | Free/open-source | Moderate | GT Tools (182 stars), maya-usd (official), mGear rigging framework. Less open-source culture than Blender. |
| **ArtStation Marketplace** | Paid | Emerging | Maya script listings with ratings/reviews. |

**Community hubs:**
- **Autodesk Community Forums** — Most active Maya discussion venue.
- **Autodesk Maya Discord** — ~12.5k members.
- **Tech-Artists.org** — Exists but modest activity. Maya tech discussions have shifted to Autodesk forums.

**Open-source pipeline tools** are a major trend: AYON/OpenPype, Tik Manager 4, Prism Pipeline, Plex — studios sharing pipeline infrastructure publicly.

**Recommendation for funkworks:** Maya community is harder to break into for community building. The audience is mostly studio TDs, not hobbyists. Lower priority unless targeting pipeline tools.

**Ease of Entry — Ranked by Friction:**

1. **GitHub** — Easiest. Push scripts/plugins. Less open-source culture than Blender, but still the path of least resistance.
2. **Gumroad** — Easy. Upload and sell. Indie TDs use this.
3. **ArtStation Marketplace** — Low-moderate. Listing + review.
4. **Highend3D** — Moderate. Account + upload. Has gone offline before — don't rely on it as sole distribution.
5. **Autodesk App Store** — Hardest. Must target current Maya version (2026), pass Autodesk review, follow their packaging requirements. Small catalog (~141 plugins) but official visibility.
6. **Autodesk Forums / Maya Discord** — Easy for announcements, but the audience is smaller and more studio-oriented. Less viral potential than Blender communities.

---

### 3ds Max — Legacy but Active

| Venue | Type | Activity | Notes |
|---|---|---|---|
| **ScriptSpot** | Free + paid | Active | New scripts submitted as recently as March 2026 (PixPatch AI). The primary community hub for Max scripts. |
| **MAXPlugins.de** | Database/directory | Active (maintained through March 2026) | Comprehensive database of all known freeware and commercial Max plugins. |
| **Autodesk App Store** | Official (~122 plugins) | Active | Publishers must target Max 2026. Forest Pack Lite (free) is notable. |
| **ArtStation Marketplace** | Paid | Growing | Scripts like "Align Pivot" (104 ratings, 5.0 stars). |
| **Gumroad** | Paid | Moderate | Archviz-focused tools. |

**Community:** Archviz-heavy. ScriptSpot is the heartbeat. Smaller indie/hobbyist scene than Blender.

**Ease of Entry — Ranked by Friction:**

1. **ScriptSpot** — Easiest. Create account, upload script. The community home base. Active moderation but low barrier.
2. **GitHub** — Easy. Standard for open-source Max tools.
3. **Gumroad** — Easy. Archviz tools sell well here.
4. **ArtStation Marketplace** — Low-moderate. Listing + review.
5. **Autodesk App Store** — Hardest. Same review process as Maya. Must target Max 2026. ~122 plugins in catalog.
6. **MAXPlugins.de** — Not a distribution platform, but getting listed in this directory gives visibility. Submit your plugin info.

---

### Cinema 4D — No Central Marketplace

Cinema 4D is the most fragmented of the major DCCs. Maxon does not operate any centralized marketplace.

| Venue | Type | Activity | Notes |
|---|---|---|---|
| **Direct from developers** | Paid | Active | INSYDIUM Fused/X-Particles, Greyscalegorilla, Redshift — all sold directly. This is the primary model. |
| **Gumroad** | Paid | Moderate | Indie developers (Plugins 4D, etc.). |
| **Toolfarm** | Third-party retailer | Active | Carries major C4D plugins. |
| **Nitro4D** | Free + paid | Active | All plugins updated for C4D 2026. |
| **developers.maxon.net** | Dev forums | Active | PluginCafe forums migrated here Nov 2023. Plugin ID registration only at plugincafe.maxon.net now. |
| **Cineversity Forums** | Official community | Active | Dedicated Cinema 4D Assets & Plugins section. |

**Community:** Tight-knit motion graphics community. Plugin developers like Rocket Lasso, Nitroman have loyal followings. Core 4D and C4Dzone are independent community forums. Plugin discovery is harder here than any other major DCC due to lack of central marketplace.

**Ease of Entry — Ranked by Friction:**

1. **Gumroad** — Easiest for paid tools. Upload and sell. Indie C4D devs use this.
2. **GitHub** — Easy for free/open-source. Less common in C4D culture but growing.
3. **Nitro4D** — Moderate. Independent developer site; if you're contributing free tools, community is receptive.
4. **developers.maxon.net (PluginCafe)** — Moderate. Register plugin IDs here. Forum is the dev community hub. Not a marketplace but essential for visibility among plugin developers.
5. **Cineversity Forums** — Low friction for sharing. Official community space.
6. **Direct website** — The dominant model for serious C4D plugins (INSYDIUM, Greyscalegorilla). High friction — you need your own site, payment processing, marketing. But it's how the established players operate.
7. **Toolfarm** — Hard. Third-party retailer. You'd need a relationship/business arrangement. Only for established commercial plugins.

---

### Nuke — Nukepedia is King

| Venue | Type | Activity | Notes |
|---|---|---|---|
| **Nukepedia** | Free community hub | Very active (2,000+ tools, 900k+ users) | 15 years old. **Nukepedia 2.0 rebuild announced** around SIGGRAPH 2025. |
| **nuBridge** | In-Nuke browser | New ($5/mo) | Browse and install all 2,000+ Nukepedia tools from inside Nuke. |
| **GitHub** | Free | Healthy | Nuke Survival Toolkit, SpinVFX gizmos, jedypod configs all actively maintained through Feb 2026. |
| **Foundry Community Forums** | Official | Active | Discussion venue. Nuke 17.0 released Feb 2026 (Gaussian Splats, USD-based 3D). |

**Key trend:** Foundry acquired Griptape (Feb 2026) for AI integration across VFX pipelines. Subscription-only licensing announced for 2027.

**Ease of Entry — Ranked by Friction:**

1. **GitHub** — Easiest. Push gizmos/scripts. Nuke Survival Toolkit model.
2. **Nukepedia** — Easy-moderate. Create account, submit tool. Light review process. Once listed, you reach 900k+ users. The canonical venue.
3. **nuBridge** — Pulls from Nukepedia. Get on Nukepedia and you're automatically discoverable in-app for $5/mo subscribers.
4. **Foundry Forums** — Easy for announcements. Not a distribution platform.

---

### DaVinci Resolve / Fusion — Reactor + We Suck Less

| Venue | Type | Activity | Notes |
|---|---|---|---|
| **Reactor** | Package manager | Very active (400k+ weekly users) | **Reactor Standalone** released — critical because Resolve Free v19.1+ removed scripting/GUI access, breaking the in-app installer. |
| **We Suck Less** (steakunderwater.com) | Community forum | Very active (54k posts, 32k members) | Primary independent Fusion community. Peak 47k concurrent users Jul 2025. Patreon-funded. |
| **Blackmagic Forums** | Official | Active | Master Plugins & Templates List thread. |
| **Codeberg/GitHub** | Free | Small | Individual fuse collections. |

**Key trend:** Resolve 20.0 (May 2025) was a massive release. The Reactor Standalone workaround for Resolve Free is important community infrastructure.

**Ease of Entry — Ranked by Friction:**

1. **GitHub/Codeberg** — Easiest. Push fuse collections.
2. **We Suck Less (steakunderwater.com)** — Easy. Create account, post in the forum, share fuses. The community is welcoming and active (54k posts, 32k members).
3. **Reactor** — Moderate. Submit a PR to the Reactor package list. Must follow packaging conventions. But once accepted, your tool reaches 400k+ weekly users via the in-app package manager.
4. **Blackmagic Forums** — Easy for announcements. Official but less technical than WSL.

---

### After Effects — aescripts Dominates

| Venue | Type | Activity | Notes |
|---|---|---|---|
| **aescripts.com** | Dominant marketplace | Very active | The #1 destination for AE scripts and plugins. Both paid and free. |
| **Gumroad** | Paid + free | Active | Indie script developers. |
| **GitHub** | Free | Moderate | Some open-source tools. |

**Community:** Massive motion graphics community. aescripts.com is the undisputed hub.

**Ease of Entry — Ranked by Friction:**

1. **GitHub** — Easiest. Push scripts/expressions.
2. **Gumroad** — Easy. Upload and sell.
3. **aescripts.com** — Moderate. Must apply as a developer and pass review. But this is *the* marketplace — if you're serious about AE tools, you need to be here. They handle distribution, licensing, and marketing.

---

### Substance 3D — Substance 3D Community Assets (formerly Substance Share)

| Venue | Type | Activity | Notes |
|---|---|---|---|
| **Substance 3D Community Assets** (formerly Substance Share) | Official free sharing | Active | Rebranded. Materials, smart materials, filters, generators. |
| **Adobe Community Forums** | Official | Active | Discussion and sharing. GDC 2026 presence. |
| **Gumroad/ArtStation** | Paid | Moderate | Custom nodes and material packs. |
| **GitHub** | Free | Small | `substance-designer` topic. Python tools, node packs. |

**Key trend:** Adobe gave all Substance 3D subscribers unmetered (unlimited) access to the full premium asset library (20k+ assets) as of Jan 2025. Designer 16.0 previewed at GDC 2026 with SDF-based shape scattering. 95%+ of AAA game projects use Substance 3D.

**Ease of Entry — Ranked by Friction:**

1. **GitHub** — Easiest. Push node packs and Python tools.
2. **Substance 3D Community Assets** — Easy-moderate. Upload materials, filters, generators to the official sharing platform (formerly Substance Share). Free sharing only.
3. **Gumroad/ArtStation** — Easy. Sell custom nodes and material packs.
4. **Adobe Community Forums** — Easy for announcements. Not a distribution platform.

---

## Cross-DCC Distribution Patterns (2026)

### What Actually Works for Community Building

1. **GitHub + Official Platform** is the winning combo for free tools. GitHub for credibility and open-source discoverability, official platform (extensions.blender.org, SideFX Labs, Nukepedia) for organic reach to actual users.

2. **Gumroad** has become the universal indie marketplace across all DCCs. It's where solo developers sell regardless of which DCC they target. No curation, low friction.

3. **Reddit** matters for Blender (1.4M members) but is negligible for Houdini (~7k) and Maya. For Houdini, use Discord (Think Procedural) and SideFX forums instead.

4. **Discord** is the real-time community heartbeat. Blender Community (~197k), Think Procedural (Houdini), Maya Discord (~12.5k). This is where people ask "what addon does X?" and get answers.

5. **Twitter/X is dead for DCC communities.** BlenderNation, Blender Artists, and conference speakers have moved to Bluesky, Threads, and LinkedIn. Nobody lists Twitter anymore.

6. **itch.io** is a minor but real channel for Blender. Negligible for other DCCs.

7. **ArtStation Marketplace** is emerging as a paid channel, especially for Houdini HDAs at low price points.

8. **YouTube** matters for discovery — tutorial creators who bundle free tools in video descriptions drive significant addon adoption. Not a distribution platform per se, but an important marketing channel.

### Emerging Platforms

- **Fab** (Epic Games) — Unifying 2.5M assets from Unreal Marketplace, ArtStation, Sketchfab, and Quixel into one storefront. 88% royalty. Anti-AI-training policy. The biggest marketplace consolidation in DCC tools. ArtStation marketplace assets migrating into Fab.
- **D5 Works** — New 3D marketplace with 0% commission.

### YouTube as Discovery Channel

YouTube is a critical addon discovery channel, especially for Blender. Channels like InspirationTuts produce regular "addons you missed" roundup videos covering 10–15 addons with timestamps and download links. These function as curated addon discovery — creators link to GitHub, Superhive, or Gumroad in descriptions. For Houdini, YouTube is more education-focused (Entagma, Junichiro Horikawa, SideFX HIVE recordings). Maya addon discovery via YouTube is minimal.

### Dead or Stale Venues (Do NOT Waste Time Here)

- **Orbolt** — Dead. Login broken, no updates since 2022.
- **FlippedNormals Marketplace** — Closing March 31, 2026.
- **Twitter/X** — DCC communities have migrated away (BlenderNation left Nov 2024, conference speakers list Bluesky/Threads/LinkedIn now).
- **Highend3D** — Alive but unreliable. Has gone offline before.

### Where to Post for Maximum Community Impact (by DCC)

| DCC | Primary | Secondary | Announce On |
|---|---|---|---|
| **Blender** | extensions.blender.org | GitHub | r/blender, BlenderArtists, Blender Discord |
| **Houdini** | GitHub | Gumroad (paid) | SideFX forums, Think Procedural Discord, od|force |
| **Maya** | GitHub | Autodesk App Store | Autodesk forums, Maya Discord |
| **Nuke** | Nukepedia | GitHub | Foundry forums |
| **Resolve/Fusion** | Reactor (via We Suck Less) | GitHub | Blackmagic forums, WSL forum |
| **After Effects** | aescripts.com | GitHub | AE community forums |
