# Blender Screenshot Best Practices

Reference for Claude Code when generating `setup[]` and `pre_run` commands in tutorial
screenshot manifests. Read this before writing any Blender Python setup code.

When you find and overcome a new gotcha, add it here before moving on.

---

## MCP Connection

**Port:** 9334 (configured in blender-mcp addon preferences)

**Protocol:** On connect the server sends a handshake JSON — consume it, then send your
command, then read the response. The runner's `BlenderMCPClient` handles this automatically.

**Commands used by the runner:**

| Command | params | Notes |
|---------|--------|-------|
| `execute_python` | `{"code": "..."}` | Run Python in Blender's main thread |
| `capture_viewport` | `{"filepath": "..."}` | OpenGL render of 3D viewport (reliable) |
| `frame_all` | `{}` | Zoom 3D viewport to fit all objects |

---

## execute_python Rules

**Namespace:** `{"bpy": bpy, "mathutils": mathutils, "result": None}`
Regular imports work (`import bmesh, os, pathlib, time`). Set `result = value` to return.

**Blocked patterns** (raise `RuntimeError` — do not use):
- `__import__` — use regular `import` statements instead
- `subprocess`, `socket`, `urllib`, `requests`, `http.client`
- `os.remove`, `os.unlink`, `os.rmdir`, `shutil.rmtree`, `shutil.move`
- `os.system`, `os.popen`
- `bpy.ops.wm.quit_blender`, `sys.exit`, `exit(`, `quit(`

**Variable scope:** All commands in a shot's `setup[]` array are joined with `\n` and sent
as a single `execute_python` call. Variables defined in one list item are available in
subsequent items within the same shot. Variables do NOT persist between shots.

---

## Environment: FUNKWORKS_ROOT

`FUNKWORKS_ROOT` is not set in Blender's process environment. The runner injects it
automatically before `pre_run` runs:

```python
import os; os.environ['FUNKWORKS_ROOT'] = '/path/to/funkworks'
```

In `pre_run` and `setup[]` commands, reference the addon path like this:

```python
import os, pathlib
plugin_path = str(pathlib.Path(os.environ['FUNKWORKS_ROOT']) / 'plugins/blender/src/my_addon.py')
bpy.ops.preferences.addon_install(filepath=plugin_path)
bpy.ops.preferences.addon_enable(module='my_addon')
```

---

## Capture Methods

### 3D Viewport — use `capture_viewport`

The runner sends the `capture_viewport` MCP command. Uses OpenGL render internally.
Set render resolution in `pre_run`:

```python
bpy.context.scene.render.resolution_x = 1920
bpy.context.scene.render.resolution_y = 1080
bpy.context.scene.render.resolution_percentage = 100
```

### All Other Areas — use xwd window capture

The runner calls `xwd -id <win_id> -silent | convert xwd:- output.png` via `capture_window()`.
This captures the full Blender window at its logical X11 pixel size (~1921×1011 on a 2K display).

**Why xwd, not screenshot_area or Spectacle:**
- `bpy.ops.screen.screenshot_area` requires `DRAW_WIN_SWAP` redraw which blocks indefinitely
  in some contexts
- Spectacle `-a` (active window) hangs on KDE and steals mouse/tablet input — do not use
- Spectacle `-f` (full screen) captures at physical HiDPI resolution (3840×2160) — too large
- xwd reads the X11 window at logical pixels, giving a clean ~1920×1011 capture

**Setup before a window capture:** Make the relevant area large and in the correct state
*before* the runner calls `capture_window()`. The capture is of the whole Blender window —
make sure the UI element you want to show dominates the frame.

---

## Area Management

### Changing area type — force a redraw before using the new space

After `area.type = 'PROPERTIES'` (or any type change), Blender hasn't initialized the new
space yet. Calling `space.context = 'PHYSICS'` immediately will fail with
`enum "PHYSICS" not found in ()`. Fix:

```python
props_area.type = 'PROPERTIES'
bpy.ops.wm.redraw_timer(type='DRAW_WIN', iterations=1)  # initialize the space
for space in props_area.spaces:
    if space.type == 'PROPERTIES':
        space.context = 'PHYSICS'
        break
```

Use `type='DRAW_WIN'`, not `type='DRAW_WIN_SWAP'` — DRAW_WIN_SWAP blocks indefinitely.

### Always convert a large area, not an existing sidebar

Finding an existing `PROPERTIES` area will give you the narrow sidebar (~300px). Always
convert the main VIEW_3D (largest area) to get a panel wide enough to read:

```python
screen = bpy.context.window_manager.windows[0].screen
view3d_areas = [a for a in screen.areas if a.type == 'VIEW_3D']
target = max(view3d_areas, key=lambda a: a.width * a.height) if view3d_areas \
         else max(screen.areas, key=lambda a: a.width * a.height)
target.type = 'PROPERTIES'
bpy.ops.wm.redraw_timer(type='DRAW_WIN', iterations=1)
```

### _get_view3d() uses the FIRST VIEW_3D found

Both `frame_all` and `capture_viewport` in blender-mcp use the first `VIEW_3D` in
`bpy.context.screen.areas`. If a stray thin VIEW_3D exists (e.g. a panel accidentally left
as VIEW_3D), captures will target the wrong area. Before viewport capture, ensure there is
only one VIEW_3D, or that the main one appears first.

### Exiting fullscreen before setup

If a previous shot used `screen_full_area`, always call this at the start of the next shot's
setup:

```python
try:
    bpy.ops.screen.back_to_previous()
except:
    pass
```

---

## Properties Panel Screenshots

To scroll to the bottom of a long Properties panel (e.g. Fluid domain with many sub-panels):

```python
window = bpy.context.window_manager.windows[0]
screen = window.screen
# Convert main VIEW_3D to PROPERTIES for a large panel
view3d_areas = [a for a in screen.areas if a.type == 'VIEW_3D']
props_area = max(view3d_areas, key=lambda a: a.width * a.height) if view3d_areas \
             else max(screen.areas, key=lambda a: a.width * a.height)
props_area.type = 'PROPERTIES'
bpy.ops.wm.redraw_timer(type='DRAW_WIN', iterations=1)
# Set context
for space in props_area.spaces:
    if space.type == 'PROPERTIES':
        space.context = 'PHYSICS'  # or 'OBJECT', 'MODIFIER', 'RENDER', etc.
        break
# Scroll to bottom — 500 iterations needed for deeply nested panels
props_region = next(r for r in props_area.regions if r.type == 'WINDOW')
for _ in range(500):
    with bpy.context.temp_override(window=window, area=props_area, region=props_region):
        bpy.ops.view2d.scroll_down(deltay=9999)
```

500 iterations is not a typo. The Fluid domain panel (with all sub-panels expanded) requires
this many scroll steps to reach content injected at the very bottom.

---

## Action Editor / Dope Sheet Screenshots

**Area and space type string** — both are `'DOPESHEET_EDITOR'`, not `'DOPESHEET'`.

**Use the TIMELINE area** (full-width bottom strip) for readable channel names. Converting
a narrow VIEW_3D gives ~330px width where channel labels are truncated:

```python
screen = bpy.context.window_manager.windows[0].screen
timeline_areas = [a for a in screen.areas if a.type == 'TIMELINE']
dope_area = max(timeline_areas, key=lambda a: a.width) if timeline_areas \
            else max((a for a in screen.areas if a.type not in ('PROPERTIES', 'OUTLINER')),
                     key=lambda a: a.width * a.height)
dope_area.type = 'DOPESHEET_EDITOR'
```

**Use ACTION mode, not DOPESHEET mode.** In DOPESHEET mode, per-channel rows can't be
reliably expanded programmatically:

```python
for space in dope_area.spaces:
    if space.type == 'DOPESHEET_EDITOR':
        space.mode = 'ACTION'
        space.action = obj.animation_data.action
        space.dopesheet.show_only_selected = True  # note: NOT space.show_only_selected
        break
```

**Expand channels and zoom to fit:**

```python
dope_region = next(r for r in dope_area.regions if r.type == 'WINDOW')
window = bpy.context.window_manager.windows[0]
with bpy.context.temp_override(window=window, area=dope_area, region=dope_region):
    bpy.ops.anim.channels_expand(all=True)  # required — channels are collapsed by default
    bpy.ops.action.select_all(action='SELECT')
    bpy.ops.action.view_all()
```

---

## Typical pre_run Structure

```python
[
    "import bmesh, os, pathlib",
    # Clear scene
    "for obj in list(bpy.data.objects): bpy.data.objects.remove(obj, do_unlink=True)",
    # Build demo objects
    "...",
    # Install and enable addon
    "plugin_path = str(pathlib.Path(os.environ['FUNKWORKS_ROOT']) / 'plugins/blender/src/<name>.py')\nbpy.ops.preferences.addon_install(filepath=plugin_path)\nbpy.ops.preferences.addon_enable(module='<name>')",
    # Set render resolution
    "bpy.context.scene.render.resolution_x = 1920\nbpy.context.scene.render.resolution_y = 1080\nbpy.context.scene.render.resolution_percentage = 100"
]
```

---

## What NOT to Do

| Don't | Why | Do instead |
|-------|-----|------------|
| `__import__('os')` | Blocked by MCP | `import os` |
| `bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', ...)` | Blocks indefinitely | `type='DRAW_WIN'` |
| Use Spectacle `-a` | Hangs KDE, steals input | xwd window capture |
| Use Spectacle `-f` | Captures at HiDPI physical pixels (3840×2160) | xwd window capture |
| `next(a for a in areas if a.type == 'PROPERTIES')` | Gets narrow sidebar | Convert largest VIEW_3D |
| Set `space.context` immediately after `area.type =` | Space not initialized | `redraw_timer(DRAW_WIN)` first |
| `space.show_only_selected` | Wrong attribute path | `space.dopesheet.show_only_selected` |
| Use `DOPESHEET` mode for channel rows | Can't expand channels | Use `ACTION` mode |
| Skip `channels_expand` | Channels collapsed, labels hidden | Always call `bpy.ops.anim.channels_expand(all=True)` |
| < 500 scroll iterations for deep panels | Doesn't reach injected sub-panels at bottom | 500 iterations minimum |
