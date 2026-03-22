# Auto-Tutorial Pipeline — Nuke

> DCC-specific reference for the [Auto-Tutorial Pipeline](auto_tutorial_pipeline.md).

---

## Screenshot API

| Task | Nuke Python API |
|------|----------------|
| Screenshot viewer | `nuke.activeViewer().capture(filepath)` or widget grab |
| Set viewer state | `nuke.activeViewer().node().knob('channels').setValue(...)` |
| Navigate to frame | `nuke.frame(N)` |
| Select nodes | `node.setSelected(True)` |
| Open Properties panel | `nuke.show(node)` |

---

## Scene File Format

`.nk` — opened via `nuke.scriptOpen(filepath)`, reset via `nuke.scriptClear()`.

---

## Plugin Installation (Tutorial Template)

```markdown
1. Download `[filename].py` or `[filename].gizmo` from [GitHub Releases](link)
2. Place in your `.nuke` directory
3. Add to your `menu.py` or `init.py` to register
```

## Plugin Install via Runner

Copy plugin file to the Nuke plugin path, then `nuke.pluginAddPath()` if needed. Gizmos loaded via `nuke.load()`.

---

## Headless Screenshot Capture

```bash
xvfb-run -a -s "-screen 0 1920x1080x24" nuke -t screenshot_runner.py
```

Note: `-t` runs Nuke in terminal mode. For UI screenshots, a full Nuke session with `xvfb` is needed instead (drop the `-t` flag).

---

## Source Code Metadata Mapping

| Source Code Element | Tutorial Content |
|--------------------|-----------------|
| Gizmo knob definitions | Options table |
| Menu registration (`menu.addCommand`) | "Find the plugin at **[menu path]**" |
| `nuke.message()` / `nuke.alert()` calls | Expected feedback messages |

---

## Example Screenshot Manifest

```json
{
  "dcc": "nuke",
  "plugin": "example_gizmo",
  "scene_file": "tutorial_scenes/example_demo.nk",
  "screenshots": [
    {
      "id": "01_node_graph",
      "description": "Node graph showing the gizmo wired into the comp",
      "setup": [
        "nuke.frame(1)",
        "node = nuke.toNode('ExampleGizmo1')",
        "node.setSelected(True)",
        "nuke.show(node)"
      ],
      "capture": {
        "method": "widget_grab",
        "panel": "DAG",
        "filepath": "plugins/nuke/docs/images/example_gizmo/01_node_graph.png"
      }
    }
  ]
}
```

---

## Failure Recovery (Nuke-Specific)

| Failure | Recovery |
|---------|----------|
| Screenshot blank or wrong panel | Retry after `nuke.show(node)` to force panel focus |
| Plugin not loaded | Re-load via `nuke.load()` or `nuke.pluginAddPath()` before retrying |
| Unexpected UI state | Reset via `nuke.scriptOpen()` to reload the demo scene |
