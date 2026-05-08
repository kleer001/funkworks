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

3. **Create the docs folder** at `plugins/blender/docs/$ARGUMENTS/` by copying the structure from `plugins/blender/_template/`:
   - `README.md` — GitHub-facing docs: the problem, the solution, install steps, usage, compatibility, edge cases
   - `listing.md` — Marketplace copy: 160-char short description, long description, features list, requirements, tags
   - `announce.md` — Two tiers of announcement copy: medium (BlenderArtists/Reddit), long (BlenderNation/blog)

4. **Generate the banner image** at `docs/images/banners/$ARGUMENTS_banner.png` (1456×672):
   - Check if image_gen is running: `imggen status` (sources `~/.bash_aliases.sh` first if needed). Start if stopped: `imggen` — starts ComfyUI (port 8188) + MCP server (port 9000), takes ~30s
   - Read `/media/menser/fauna/image_gen/INDEX.md` for available models and LoRA trigger words
   - Draft 5 distinct prompt options (different metaphors / visual angles for the plugin's core action). No approval step — generate immediately.
   - Save all 5 candidate prompts to `data/banner_prompts/$ARGUMENTS_v{1..5}.txt`
   - **Generate all 5 by hitting ComfyUI directly at `http://127.0.0.1:8188/prompt`.** Do NOT call the MCP server at port 9000 — it crashes on the local UI-format workflows (see `reference_banner_generation` memory). Use the API-format Flux workflow built in code; reference: `/tmp/gen_subdivide_banners.py` (no-LoRA) or session 2af77ffa from Apr 23 (LoRA variant). Output lands in `/media/menser/fauna/image_gen/comfyui/output/<prefix>_NNNNN_.png`. Target size: 1456×672.
   - Build a comparison gallery `/tmp/$ARGUMENTS_gallery.html` with all 5 images (label, full-width img, light background per the user's vision preference)
   - Serve via `python3 -m http.server 8765 --directory /tmp` (run in background; port 8765 — pick another if taken). Open `http://localhost:8765/$ARGUMENTS_gallery.html` in Firefox. **Do not link `file:///tmp/...` directly — Firefox is sandboxed via flatpak portal and rewrites those paths to `/run/user/1000/doc/<hash>/...`, which is non-obvious for the user.**
   - Once the user picks one, copy the chosen prompt to `data/banner_prompts/$ARGUMENTS.txt`, copy the chosen image to `docs/images/banners/$ARGUMENTS_banner.png`, and clean up the `_v{1..5}.txt` candidate files

5. **Update the root README** — add a row to the plugins table:
   ```
   | [Plugin Display Name](plugins/blender/docs/$ARGUMENTS/) | One-line description |
   ```

## Conventions

- Plugin file name and docs folder name are the same `snake_case` identifier
- Lead all copy with the user's pain, not the feature
- Listing short description must be ≤ 160 characters
- Announce copy leaves `[link]` as a placeholder — do not invent URLs. At publish time `[link]` is replaced with the GitHub Pages tutorial URL (`https://kleer001.github.io/funkworks/<tutorial-slug>`), never the release zip or tag URL
- **Wrapping a native operator carries all of its parameters.** When a plugin extends or replaces a built-in DCC operator (Blender op, Houdini SOP/COP, Nuke node, etc.), expose every parameter the host exposes, with the same defaults, and forward them through. Users who reach for the wrapped version should never lose functionality they had before. Look up the full operator signature in the host's API/docs before defining the addon's properties — do not eyeball the redo panel or parameter pane.
