# Funkworks — Where We Are

_Last updated: 2026-03-20_

---

## Fluid Domain Auto-Visibility

**Status: MVP complete, tested, ready to publish**

### Done
- `plugins/blender/src/fluid_domain_visibility.py` — addon code, tested live in Blender 4.2.5
  - Operator inserts `hide_viewport` + `hide_render` keyframes anchored at scene start frame, frame before sim start, and sim start frame
  - Edge case handled: sim starts at frame 1 (keyframes at 0 and 1, warning issued)
  - Full undo support via `bl_options = {'REGISTER', 'UNDO'}`
- `plugins/blender/docs/fluid_domain_visibility/README.md` — user-facing docs
- `plugins/blender/docs/fluid_domain_visibility/listing.md` — marketplace copy (short + long description, tags)
- `plugins/blender/docs/fluid_domain_visibility/announce.md` — announcement copy (Twitter, BlenderArtists/Reddit, newsletter)

### To Do
- [ ] Package as zip for distribution
- [ ] Choose distribution platform (Blender Market, Gumroad, etc.)
- [ ] Upload and fill in `[link]` placeholders in announce.md
- [ ] Post announcements
