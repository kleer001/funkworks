# Funkworks — Where We Are

_Last updated: 2026-03-26_

---

## Fluid Domain Visibility

**Status: Complete — tutorial page published with screenshots**

### Done
- `plugins/blender/src/fluid_domain_visibility.py` — addon code, tested live in Blender 4.2.5
- `plugins/blender/docs/fluid_domain_visibility/README.md` — user-facing docs
- `plugins/blender/docs/fluid_domain_visibility/listing.md` — marketplace copy
- `plugins/blender/docs/fluid_domain_visibility/announce.md` — announcement copy (placeholders remain)
- `docs/fluid-domain-visibility.md` — tutorial page with screenshots, live on GitHub Pages

### To Do
- [ ] Package as zip for distribution
- [ ] Choose distribution platform (Blender Market, Gumroad, etc.)
- [ ] Upload and fill in `[link]` placeholders in announce.md
- [ ] Post announcements
- `/publish` skill is planned but not yet built

---

## Auto-Tutorial Screenshot Pipeline

**Status: Fully automated — all shots working with no human input**

### Done
- `src/tutorials/screenshot_runner.py` — generic, app-agnostic runner; reads a manifest, connects to Blender via MCP, executes setup code, captures + crops screenshots
- `src/tutorials/BLENDER_SCREENSHOT_BEST_PRACTICES.md` — canonical reference for Blender screenshot gotchas, MCP rules, area management, capture methods, code snippets. Updated by the `/tutorial` skill when new gotchas are solved.
- `.claude/skills/tutorial/SKILL.md` — updated to include full screenshot pipeline; reads BEST_PRACTICES.md before generating setup code
- Manifests are ephemeral (gitignored, regenerated each run); setup code is generated fresh by Claude, not stored as an artifact
- Fluid Domain Visibility tutorial proven end-to-end: all 4 shots automated, images live

### Architecture Notes
- Manifests: Claude generates `screenshot_manifest.json` per run; not committed
- Setup code: generated fresh from BEST_PRACTICES.md context each session
- Crop pass: Pillow-based, confidence-gated; low-confidence shots flagged
- Blender MCP: `localhost:9334`

### To Do
- [ ] Run the pipeline on a second plugin (proves generality beyond FDV)
- [ ] Build `/publish` skill: package zip → GitHub Release → patch announce.md → post to Reddit
