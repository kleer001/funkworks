# Announcement Copy — Bevel Modifier Presets

## Medium (BlenderArtists / Reddit r/blender)

**Free addon: save Bevel modifier parameters as named presets**

The Bevel modifier has no preset system. Typical tuning involves Width, Segments, Profile, and Shading flags; in multi-project workflows these values reset to defaults each time the file changes. Copy-paste between files is a common workaround, but it requires per-project setup.

**Bevel Modifier Presets** adds a panel to the Properties Editor's Modifier tab, visible whenever a Bevel modifier is active. A **[+]** button saves the current parameter set as a named preset. The dropdown picks any saved preset and applies it to the active Bevel modifier. Presets are written to Blender's standard preset directory, so they persist across .blend files and across Blender restarts.

All 22 writable properties of the Bevel modifier are captured on Blender 4.2 LTS, including `affect`, `offset_type`, `limit_method`, `profile_type`, `miter_inner` / `miter_outer`, `harden_normals`, and the vertex-group and material slots. Custom Profile curve points are not stored; Blender's existing **Save Profile As** mechanism handles those.

Free download: https://kleer001.github.io/funkworks/bevel_presets

Validated on Blender 4.2 LTS. No new UI patterns — uses Blender's built-in `AddPresetBase`, the same machinery as Render and Cycles presets.

More free tools at https://github.com/kleer001/funkworks

---

## Long (Newsletter / Blog post intro)

**The Bevel modifier has no preset system**

The Bevel modifier exposes 22 writable properties in Blender 4.2 LTS. Typical tuning covers Width, Segments, Profile, the two Miter modes, the Limit Method, and the Shading flags. In multi-project workflows these values reset to defaults each time, so the tuning repeats.

Copy-paste-modifier moves a Bevel between objects in the same file, but not across files. Append from an old .blend pulls the modifier in along with the object that carries it, which is too coarse. Writing the values down works exactly once.

**Bevel Modifier Presets** plugs the gap. It registers a **Bevel Presets** panel in the Properties Editor's Modifier tab. The panel appears whenever the active modifier is a Bevel and is hidden otherwise. Inside the panel, a **[+]** saves the active modifier's current parameter set as a named preset. The dropdown lists every saved preset; clicking one applies it to the active modifier. A **[-]** removes the selected preset.

Presets are written as `.py` files into `scripts/presets/bevel_modifier/` under Blender's user config directory — the same location Blender uses for Render and Cycles presets. They survive .blend changes, Blender restarts, and travel between machines via a single file copy.

The addon captures all 22 writable properties of the Bevel modifier on Blender 4.2 LTS: `affect`, `angle_limit`, `face_strength_mode`, `harden_normals`, `invert_vertex_group`, `limit_method`, `loop_slide`, `mark_seam`, `mark_sharp`, `material`, `miter_inner`, `miter_outer`, `offset_type`, `profile`, `profile_type`, `segments`, `spread`, `use_clamp_overlap`, `vertex_group`, `vmesh_method`, `width`, `width_pct`. Custom Profile control points are intentionally excluded — they don't serialize as single assignments, and Blender already has a **Save Profile As** mechanism in the Custom Profile widget for curve persistence.

Implementation is short and uses Blender's standard infrastructure: `bl_operators.presets.AddPresetBase` for save and delete, `Menu.draw_preset` for the dropdown rendering.

It's free and open source.

Download it free: https://kleer001.github.io/funkworks/bevel_presets

More free tools at https://github.com/kleer001/funkworks
