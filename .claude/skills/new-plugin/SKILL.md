---
name: new-plugin
description: >-
  Build and document a new Blender addon plugin end-to-end.
  TRIGGER when: code imports `bpy`, or user asks to create, build, or scaffold
  a new Blender plugin/addon.
  DO NOT TRIGGER when: user asks to edit an existing plugin or write a tutorial.
argument-hint: "[plugin-name] [--origin <url>]..."
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

Build and document a new Blender addon plugin end-to-end.

## Before You Build

Answer these three questions before writing a line of code:

1. **Is there demand?** Use the research pipeline (crawler + digest agent) output to confirm people are actually asking for this. Don't build speculatively.
2. **Does a similar addon exist?** If so, what makes this one different? Name the difference explicitly — it'll drive all the copy.
3. **Is it easy to use without reading docs?** If the workflow requires more than 2–3 steps or a manual, reconsider the UX. The most important thing Blender addon users want: easy to use and saves time.

If you can't answer all three, stop and ask the user before proceeding.

---

## Steps

1. **Capture origin records** to `data/origins/origins.jsonl` (gitignored). One record per originating post — append, don't overwrite. If the user passed `--origin <url>` (one or more), use those URLs. If none were passed, prompt for them: "What post(s) motivated this plugin? Paste URLs, one per line, or press Enter to record retroactively." For each URL, derive `venue` from the host, `post_date` from the post if known, `tags` (5–10 keywords from the ask), and `notes` (one-line paraphrase of what the asker wanted). If the user has no URLs at all, write a single retroactive record with `captured_at_retroactively: true`, `source_url: null`, and ask for `tags` + `notes`. Do not silently skip — every plugin gets at least one record. Schema: see `Provenance` section in `CLAUDE.md`.

2. **Write the addon** at `plugins/blender/src/$ARGUMENTS.py` following the patterns in existing plugins (single-file, `bl_info` header, `register`/`unregister`, `bl_options = {'REGISTER', 'UNDO'}`).

3. **Headless smoke test.** Run Blender in `--background --factory-startup --python <smoke_test.py>` mode to verify the addon registers cleanly, every operator/menu/panel class appears in `bpy.types` under its conventional name (`<NAMESPACE>_OT_*`, `<NAMESPACE>_MT_*`, `<EDITOR>_PT_*`), `poll()` gates correctly, and any roundtrip behaviour (save/load/serialise) actually works. The smoke test must FAIL the build if registration is dirty — do not move on to manual verification with a broken module. This step exists to catch class-naming mismatches and broken RNA paths before the human ever installs the addon.

4. **Write the tutorial page** at `docs/$ARGUMENTS.md` (Jekyll, GitHub Pages) BEFORE writing README / listing / announce. The tutorial doubles as the manual-verification script: the steps the user clicks through in a real Blender session to confirm the addon does what the addon says it does. Walk through it in a running Blender (preferably via the Blender MCP if available) and capture screenshots into `docs/images/$ARGUMENTS/`. Update the tutorial when reality diverges from the spec — that's the point of doing it first. See the `/tutorial` skill for full Jekyll page conventions, banner reference, image-path patterns, and the screenshot manifest format if you need automated captures. Banner image generation (step 6 below) is decoupled from this step — leave the banner `![]` line as a placeholder reference until step 6 completes.

5. **Create the docs folder** at `plugins/blender/docs/$ARGUMENTS/` by copying the structure from `plugins/blender/_template/`. Write these AFTER the tutorial walkthrough, so the copy reflects verified behaviour rather than spec-stage intent:
   - `README.md` — GitHub-facing docs: the problem, the solution, install steps, usage, compatibility, edge cases
   - `listing.md` — Marketplace copy: 160-char short description, long description, features list, requirements, tags
   - `announce.md` — Two tiers of announcement copy: medium (BlenderArtists/Reddit), long (BlenderNation/blog)

6. **Generate the banner image** at `docs/images/banners/$ARGUMENTS_banner.png` (1456×672):
   - Check if image_gen is running: `imggen status` (sources `~/.bash_aliases.sh` first if needed). Start if stopped: `imggen` — starts ComfyUI (port 8188) + MCP server (port 9000), takes ~30s
   - Read `/media/menser/fauna/image_gen/INDEX.md` for available models and LoRA trigger words
   - Draft 5 distinct prompt options (different metaphors / visual angles for the plugin's core action). No approval step — generate immediately.
   - Save all 5 candidate prompts to `data/banner_prompts/$ARGUMENTS_v{1..5}.txt`
   - **Generate all 5 by hitting ComfyUI directly at `http://127.0.0.1:8188/prompt`.** Do NOT call the MCP server at port 9000 — it crashes on the local UI-format workflows (see `reference_banner_generation` memory). Use the API-format Flux workflow built in code; reference: `/tmp/gen_subdivide_banners.py` (no-LoRA) or session 2af77ffa from Apr 23 (LoRA variant). Output lands in `/media/menser/fauna/image_gen/comfyui/output/<prefix>_NNNNN_.png`. Target size: 1456×672.
   - Build a comparison gallery `/tmp/$ARGUMENTS_gallery.html` with all 5 images (label, full-width img, light background per the user's vision preference)
   - Serve via `python3 -m http.server 8765 --directory /tmp` (run in background; port 8765 — pick another if taken). Open `http://localhost:8765/$ARGUMENTS_gallery.html` in Firefox. **Do not link `file:///tmp/...` directly — Firefox is sandboxed via flatpak portal and rewrites those paths to `/run/user/1000/doc/<hash>/...`, which is non-obvious for the user.**
   - Once the user picks one, copy the chosen prompt to `data/banner_prompts/$ARGUMENTS.txt`, copy the chosen image to `docs/images/banners/$ARGUMENTS_banner.png`, and clean up the `_v{1..5}.txt` candidate files

7. **Update the root README** — add a row to the plugins table:
   ```
   | [Plugin Display Name](plugins/blender/docs/$ARGUMENTS/) | One-line description |
   ```

8. **Preview the rendered tutorial.** Run `scripts/preview-latest.sh` — it starts a Jekyll container (Docker) on `localhost:4000/funkworks/`, waits until it responds, and opens the newest tutorial page (`docs/$ARGUMENTS.md`) in the default browser. Confirm: banner renders, problem section reads cleanly, screenshots load, download button points at the right path. Tell the user the URL and what you verified. Don't stop the container — leaving it running means the next iteration of `/new-plugin` or a re-edit of the tutorial picks up live without a rebuild.

## Conventions

- Plugin file name and docs folder name are the same `snake_case` identifier
- Lead all copy with the user's pain, not the feature
- Listing short description must be ≤ 160 characters
- **Card description on `docs/index.md`: hard 3-line ceiling.** Each plugin card has `height: 160px` + `overflow: hidden`, and the body column fits descriptions at ~470px wide / 0.92rem. Anything wrapping to 4 lines silently clips the "Tutorial & Download / Source" link row. Empirical cliff: 183 chars renders 3 lines, 195 chars renders 4. Author target: **≤170 chars** to keep margin for word-break luck. The rule is *lines*, not chars — char count is a guide that breaks for long phrases like parenthetical lists. After adding the card, hard-reload `http://localhost:4000/funkworks/` and confirm the link row is visible
- Announce copy leaves `[link]` as a placeholder — do not invent URLs. At publish time `[link]` is replaced with the GitHub Pages tutorial URL (`https://kleer001.github.io/funkworks/<tutorial-slug>`), never the release zip or tag URL
- **Wrapping a native operator carries all of its parameters.** When a plugin extends or replaces a built-in DCC operator (Blender op, Houdini SOP/COP, Nuke node, etc.), expose every parameter the host exposes, with the same defaults, and forward them through. Users who reach for the wrapped version should never lose functionality they had before. Look up the full operator signature in the host's API/docs before defining the addon's properties — do not eyeball the redo panel or parameter pane.
