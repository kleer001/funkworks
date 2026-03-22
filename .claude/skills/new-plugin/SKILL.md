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

## Steps

1. **Write the addon** at `plugins/blender/src/$ARGUMENTS.py` following the patterns in existing plugins (single-file, `bl_info` header, `register`/`unregister`, `bl_options = {'REGISTER', 'UNDO'}`).

2. **Create the docs folder** at `plugins/blender/docs/$ARGUMENTS/` by copying the structure from `plugins/blender/_template/`:
   - `README.md` — GitHub-facing docs: the problem, the solution, install steps, usage, compatibility, edge cases
   - `listing.md` — Marketplace copy: 160-char short description, long description, features list, requirements, tags
   - `announce.md` — Three tiers of announcement copy: short (tweet/toot), medium (BlenderArtists/Reddit), long (newsletter/blog intro)

3. **Update the root README** — add a row to the plugins table:
   ```
   | [Plugin Display Name](plugins/blender/docs/$ARGUMENTS/) | One-line description |
   ```

## Conventions

- Plugin file name and docs folder name are the same `snake_case` identifier
- Lead all copy with the user's pain, not the feature
- Listing short description must be ≤ 160 characters
- Announce copy leaves `[link]` as a placeholder — do not invent URLs
