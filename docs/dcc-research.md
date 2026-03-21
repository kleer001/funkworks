# DCC Extension Systems Research

## Community Activity Rankings

Software in each category sorted by size and activity of the plugin/extension-building community (most active first).

### 3D DCC Tools

1. **Unreal Engine** — Massive marketplace, huge open-source community, Blueprints lower the barrier to entry
2. **Unity** — Enormous Asset Store ecosystem, tens of thousands of editor extensions and packages
3. **Blender** — Exploding open-source community, thousands of add-ons on Superhive (formerly Blender Market), GitHub, and Gumroad
4. **Maya** — Decades of studio pipeline scripts, massive MEL/Python library, Autodesk App Store
5. **Houdini** — Orbolt marketplace, very active HDA-sharing community, deep technical users
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
