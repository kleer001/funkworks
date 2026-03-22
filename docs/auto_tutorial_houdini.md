# Auto-Tutorial Pipeline — Houdini

> DCC-specific reference for the [Auto-Tutorial Pipeline](auto_tutorial_pipeline.md).

---

## Screenshot API

| Task | Houdini Python API |
|------|-------------------|
| Screenshot desktop/pane | `hou.ui.savePaneTabsScreenshot(filepath)` |
| Set viewport shading | `viewport.settings().displaySet(hou.displaySetType.SceneObject)` |
| Set camera/view angle | `viewport.homeAll()` or set camera transform |
| Navigate to frame | `hou.setFrame(N)` |
| Select objects | `node.setSelected(True)` |
| Open network editor / pane tab | `pane.setCurrentTab(tab)` |

---

## Scene File Format

`.hip` / `.hiplc` — opened via `hou.hipFile.load(filepath)`, reset via `hou.hipFile.clear()`.

---

## Plugin Installation (Tutorial Template)

```markdown
1. Download the HDA or shelf tool from [GitHub Releases](link)
2. Copy to your Houdini preferences directory, or:
3. In Houdini: **File > Install Digital Asset Library** (for HDAs)
```

## Plugin Install via Runner

`hou.hda.installFile(filepath)` for HDAs. Shelf tools loaded via `hou.shelves.loadFile(filepath)`.

---

## Headless Screenshot Capture

```bash
xvfb-run -a -s "-screen 0 1920x1080x24" hython screenshot_runner.py
```

Note: `hython` is Houdini's headless Python interpreter. For UI screenshots, a full Houdini session with `xvfb` is needed instead.

---

## Source Code Metadata Mapping

| Source Code Element | Tutorial Content |
|--------------------|-----------------|
| HDA `TypeProperties` (label, icon, help) | Title, "Find the plugin at **[shelf/tab]**" |
| Parameter template definitions | Options table |
| Input/output connectors | Prerequisites ("Connect a SOP network first") |
| `hou.NodeWarning` / status messages | Expected feedback messages |

---

## Example Screenshot Manifest

```json
{
  "dcc": "houdini",
  "plugin": "example_hda",
  "scene_file": "tutorial_scenes/example_demo.hip",
  "screenshots": [
    {
      "id": "01_network",
      "description": "Network editor showing the HDA node wired into a SOP chain",
      "setup": [
        "hou.setFrame(1)",
        "node = hou.node('/obj/geo1/example_hda1')",
        "node.setSelected(True)"
      ],
      "capture": {
        "method": "savePaneTabsScreenshot",
        "pane_type": "NetworkEditor",
        "filepath": "plugins/houdini/docs/images/example_hda/01_network.png"
      }
    }
  ]
}
```

---

## Failure Recovery (Houdini-Specific)

| Failure | Recovery |
|---------|----------|
| Screenshot blank or wrong pane | Retry after setting pane tab explicitly via `pane.setCurrentTab()` |
| HDA not installed | Re-install via `hou.hda.installFile()` before retrying |
| Unexpected UI state | Reset via `hou.hipFile.load()` to reload the demo scene |
