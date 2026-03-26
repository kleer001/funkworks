---
name: new-plugin
description: >-
  Build and document a new Blender addon plugin end-to-end.
  TRIGGER when: code imports `bpy`, or user asks to create, build, or scaffold
  a new Blender plugin/addon.
  DO NOT TRIGGER when: user asks to edit an existing plugin or write a tutorial.
argument-hint: "[plugin-name]"
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

1. **Write the addon** at `plugins/blender/src/$ARGUMENTS.py` following the patterns in existing plugins (single-file, `bl_info` header, `register`/`unregister`, `bl_options = {'REGISTER', 'UNDO'}`).

2. **Create the docs folder** at `plugins/blender/docs/$ARGUMENTS/` by copying the structure from `plugins/blender/_template/`:
   - `README.md` — GitHub-facing docs: the problem, the solution, install steps, usage, compatibility, edge cases
   - `listing.md` — Marketplace copy: 160-char short description, long description, features list, requirements, tags
   - `announce.md` — Two tiers of announcement copy: medium (BlenderArtists/Reddit), long (BlenderNation/blog)

3. **Update the root README** — add a row to the plugins table:
   ```
   | [Plugin Display Name](plugins/blender/docs/$ARGUMENTS/) | One-line description |
   ```

## Conventions

- Plugin file name and docs folder name are the same `snake_case` identifier
- Lead all copy with the user's pain, not the feature
- Listing short description must be ≤ 160 characters
- Announce copy leaves `[link]` as a placeholder — do not invent URLs
