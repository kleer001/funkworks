# Funkworks — Where We Are

_Last updated: 2026-03-22_

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

---

## Auto-Tutorial Pipeline

**Status: Design doc drafted, not yet implemented**

### Done
- `docs/auto_tutorial_pipeline.md` — DCC-agnostic pipeline design
- `docs/auto_tutorial_blender.md` — Blender-specific API details (screenshot_area, crop methods)
- `docs/auto_tutorial_houdini.md` — Houdini-specific API details
- `docs/auto_tutorial_nuke.md` — Nuke-specific API details
- Crop decision workflow: two-phase capture-wide-then-ask-Claude approach
- Screenshot QA/QC process: automated checks + agent visual review

### Next Steps (MVP — Blender only)

1. **Write the Tutorial Agent prompt**
   - The agent receives plugin source + brief + smoke test results
   - Outputs `tutorial.md` + `screenshot_manifest.json` with `crop_subject` fields (no coordinates yet)
   - Start with Fluid Domain Visibility as the first test case

2. **Build the Screenshot Runner**
   - Python script that reads a manifest, connects to Blender via MCP, runs setup commands, calls `bpy.ops.screen.screenshot_area()`
   - Saves full-area captures to the paths specified in the manifest

3. **Implement the Claude crop pass**
   - After each full-area capture, upload the image to Claude with the `crop_subject`
   - Parse the returned `[x, y, width, height]` + confidence
   - Crop the image (Pillow) and write the final file
   - Skip crop + flag for manual review if confidence is "low"

4. **Wire up automated QA checks**
   - File exists / non-empty, minimum dimensions, blank detection, aspect ratio
   - Confidence gate from the crop pass

5. **Run the full pipeline end-to-end on Fluid Domain Visibility**
   - Tutorial Agent → manifest → Runner → crop pass → QA → final tutorial.md with images
   - This is the proof-of-concept: one plugin, one DCC, real screenshots

6. **Agent visual QA review**
   - Tutorial Agent reads each cropped image, compares to manifest description
   - Pass / retry-adjust-crop / retry-adjust-setup / flag for manual review
   - Wire retry loop (max 3 cycles per screenshot)

### Blocked On
- MCP adapter for Blender — must be able to send Python commands to a running Blender session and capture screenshots. This is the critical-path dependency for everything after step 1.
