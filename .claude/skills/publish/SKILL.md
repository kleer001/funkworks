---
name: publish
description: >-
  Publish a completed, tested DCC plugin to GitHub Releases and prepare
  announcement copy. TRIGGER when the user asks to publish, release, or ship
  any plugin (Blender addon, Houdini HDA, etc.).
argument-hint: "[dcc/plugin-name]  e.g. blender/selective_edge_split or houdini/scale_cop"
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

Publish the plugin **$ARGUMENTS** to GitHub Releases.

Parse `$ARGUMENTS` as `<dcc>/<plugin-name>` (e.g. `houdini/scale_cop`).
Set `$DCC` and `$NAME` from those two parts. If only one part is given, ask
the user which DCC before proceeding.

## Before You Start

If `src/publishing/PUBLISH_BEST_PRACTICES.md` exists, read it now. It contains
lessons from previous publish runs — blocked gh commands, asset quirks, announce
copy pitfalls, etc. Apply them before hitting the same problems.

---

## Step 1: Preflight

Verify everything is in place before touching GitHub.

**Common to all DCCs:**
- [ ] Plugin source file(s) exist under `plugins/$DCC/src/`
- [ ] `plugins/$DCC/docs/$NAME/README.md` — user-facing docs
- [ ] `plugins/$DCC/docs/$NAME/listing.md` — used as GitHub release body
- [ ] `plugins/$DCC/docs/$NAME/announce.md` — announcement copy
- [ ] Tutorial or docs page exists under `docs/` (filename may use hyphens)

**Blender-specific:**
- [ ] `plugins/blender/src/$NAME.py` — single-file source
- [ ] Tutorial screenshots present under `docs/images/$NAME/`
- [ ] Extract version from `bl_info` in the source file. This is the canonical version.

**Houdini-specific:**
- [ ] `plugins/houdini/src/$NAME.hda` — compiled HDA
- [ ] `plugins/houdini/src/build_$NAME.py` — build script (if it exists, include as release asset)
- [ ] Extract version from `_git_version()` logic in the build script: `v0.1.<commit-count>`.
  Run `git rev-list --count HEAD` and `git rev-parse --short HEAD` to compute it.

If anything is missing, stop and tell the user what's needed. Do not proceed.

---

## Step 2: Package

**Blender:**
```bash
mkdir -p plugins/blender/releases
cd plugins/blender && zip releases/$NAME.zip src/$NAME.py
```
The zip contains only the single source file.

**Houdini:**
No zip needed — the HDA and build script are the distributables. Collect asset paths:
- `plugins/houdini/src/$NAME.hda`
- `plugins/houdini/src/build_$NAME.py` (if it exists)

---

## Step 3: Create the GitHub Release

**Blender:**
```bash
gh release create $NAME-v{VERSION} \
  --title "{Plugin Display Name} v{VERSION}" \
  --notes-file plugins/blender/docs/$NAME/listing.md \
  plugins/blender/releases/$NAME.zip
```

**Houdini:**
```bash
gh release create $NAME-v{VERSION} \
  --title "{Node Display Name} v{VERSION}" \
  --notes-file plugins/houdini/docs/$NAME/listing.md \
  plugins/houdini/src/$NAME.hda \
  plugins/houdini/src/build_$NAME.py
```

- Tag format: `$NAME-v{VERSION}` (e.g. `scale_cop-v0.1.99`)
- Title: human-readable display name + version
- Notes: `listing.md` long description (already written for this purpose)

If `gh` fails with a connection error, retry up to 3 times with a few seconds between attempts.

---

## Step 4: Update Plugin Registries

Two files list every plugin and must be updated for every release:

**`README.md`** — the GitHub repo homepage. Add a row to the single plugins table if the
plugin is not already listed:
```
| DCC Name | [Display Name](plugins/$DCC/docs/$NAME/) | One-line description |
```

**`docs/index.md`** — the GitHub Pages homepage. Add an entry under the correct DCC section:
```markdown
### [Display Name](page-slug)

One-line description. Key capability or differentiator.

**DCC Version+** · Free

---
```
If this is the first plugin for a new DCC, add a new `## DCC Name` section.

---

## Step 5: Patch announce.md

Read `plugins/$DCC/docs/$NAME/announce.md`. Replace all placeholder URLs
(`[link]`, `https://github.com/.../releases/tag/PLACEHOLDER`) with the real release URL:

```
https://github.com/kleer001/funkworks/releases/tag/$NAME-v{VERSION}
```

Confirm the URL resolves by checking `gh release view $NAME-v{VERSION}`.

---

## Step 6: Output Announcement Copy

Before printing, audit the copy for factual accuracy first:

- **No false claims.** Every sentence must be verifiable from the source, docs, or git history. If you wrote it, ask: "how do I know this is true?" If the answer is "it sounds right," cut it.
- **Ordinal claims** ("first release", "first Houdini release", etc.) require checking `gh release list` to confirm. Don't assert firsts without looking.

Then check tone and completeness:

**Blender:** Title must include "addon". No unanswered questions.
**Houdini:** Title must include "HDA" or "node". Mention the build script for FX users.
**Both:** Read as a first-time reader. Fill any gaps before outputting.

Every medium and long tier must end with this CTA (after the closing line):

```
🐜 More free tools at https://github.com/kleer001/funkworks
```

Print the announcement tiers clearly labelled for their target communities:

**Blender:**
```
=== MEDIUM (BlenderArtists / Reddit r/blender) ===
[copy]

=== LONG (BlenderNation / Blog) ===
[copy]
```

**Houdini:**
```
=== MEDIUM (SideFX Forums / OdForce) ===
[copy]

=== LONG (Blog / Newsletter) ===
[copy]
```

Note for both: Reddit/forum posting is manual. Tell the user where to post and to paste
the medium-form copy. Remind them the RSS feed at
`https://kleer001.github.io/funkworks/feed.xml` updates automatically once the docs
page is on `main`.

---

## Step 7: Retrospective

After the publish completes (or if you hit a significant blocker and solved it),
update `src/publishing/PUBLISH_BEST_PRACTICES.md`:

- If the file doesn't exist, create it with a `# Publish Best Practices` header
  and a `## Blender` / `## Houdini` section structure.
- Add any new gotcha, workaround, or confirmed-good pattern under the relevant DCC section.
- Remove or correct anything that turned out to be wrong.
- Keep entries concise: one problem, one solution, one code snippet if needed.

This file is read at the start of every `/publish` run. Keep it accurate and lean.
