---
name: publish
description: >-
  Publish a completed, tested DCC plugin to GitHub Releases and prepare
  announcement copy. TRIGGER when: the user asks to publish, release, or ship
  any plugin (Blender addon, Houdini HDA, etc.); OR when announce.md,
  listing.md, or README.md files are being written for a plugin for the first
  time; OR when the user is doing release steps manually (GitHub release,
  docs/index.md card, plugins table row) without having invoked /publish.
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
(`[link]`, `https://github.com/.../releases/tag/PLACEHOLDER`) with the **tutorial
page URL** on GitHub Pages — not the release tag or zip:

```
https://kleer001.github.io/funkworks/$TUTORIAL_SLUG
```

`$TUTORIAL_SLUG` is the filename (without `.md`) of the tutorial under `docs/`
— it may use hyphens instead of underscores (e.g. `fluid-domain-visibility`).
Announcements send readers to the tutorial page, which has context and a
download button; never link directly to the release zip or `releases/tag/...`.

Confirm the release itself exists with `gh release view $NAME-v{VERSION}` and
that `docs/$TUTORIAL_SLUG.md` is present.

---

## Step 6: Output Announcement Copy

Before printing, run `/honest-copy plugins/$DCC/docs/$NAME/announce.md` and resolve
every flagged item. Do not output announcement copy until the honest-copy audit
passes clean.

Then check tone and completeness:

**Blender:** Title must include "addon". No unanswered questions.
**Houdini:** Title must include "HDA" or "node". Mention the build script for FX users.
**Both:** Read as a first-time reader. Fill any gaps before outputting.

Every medium and long tier must end with this CTA (after the closing line):

```
More free tools at https://github.com/kleer001/funkworks
```

**No emoji anywhere in announcement copy.** odforce silently chokes on them, and they read as unprofessional on dev forums. Strip emoji from all tiers (short, medium, long), including any inherited from earlier templates.

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
=== MEDIUM (OdForce / Reddit r/Houdini — Markdown) ===
[copy]

=== MEDIUM (SideFX Forums — BBCode) ===
[copy converted to BBCode]

=== LONG (Blog / Newsletter) ===
[copy]
```

SideFX Forums use BBCode, not Markdown. Produce the BBCode medium tier by
converting the Markdown medium tier with these rules (do not rewrite the copy):

- `**bold**` → `[b]bold[/b]`
- `*italic*` / `_italic_` → `[i]italic[/i]`
- `[text](url)` → `[url=url]text[/url]`
- Bare URLs stay bare (forum auto-links them)
- Markdown bullet list with 2+ items → `[list][*]item[*]item[/list]` (one `[*]` per item, no closing `[/*]`)
- Markdown numbered list with 2+ items → `[list=1][*]item[*]item[/list]`
- `> quote` → `[quote]quote[/quote]`
- Fenced code blocks → `[code]...[/code]`; VEX blocks → `[code vex]...[/code]`
- Headings (`#`, `##`) → bold on their own line: `[b]Heading[/b]`
- Horizontal rules (`---`) → drop, or a blank line

**Be conservative with BBCode. Tags are not free.** A noisy post with tags around every token reads worse than plain prose.

- **Inline `[code]` only for multi-token expressions, paths, or snippets with punctuation** (e.g. `op:/obj/...`, `ch("../parm")`, `popwrangle in Pre-Solve`). Single bareword identifiers — attribute names like `Cd`, file extensions like `.cmd`, function names like `muscleupdatevellum`, parm names like `id`/`ptnum` — leave bare. They read fine without monospace.
- **Never emit a single-item `[list]`.** If you have one bullet, write it as a sentence.
- **Don't wrap every technical term.** If in doubt, leave it bare.

**SideFX forum topic title is capped at 60 characters.** The body's first heading is usually too long. Above the BBCode body, output a separate labeled line so the user knows what to paste into the title field:

```
Topic title (≤60 chars): <short title>
```

Pick a title that names the plugin and signals "free" or "HDA". Examples: `Vellum Animated Attribute Streamer — free HDA` (46), `Free HDA: Scale COP for Houdini` (31). Count characters before emitting; if over 60, shorten.

Note for both: Reddit/forum posting is manual. Tell the user where to post and to paste
the medium-form copy. Remind them the RSS feed at
`https://kleer001.github.io/funkworks/feed.xml` updates automatically once the docs
page is on `main`.

---

## Step 7: Create Newsletter Draft

Check whether `BUTTONDOWN_API_KEY` is set in `.env`. If it is:

```bash
python -m src.newsletter.send plugins/$DCC/docs/$NAME/announce.md
```

This creates a **draft** in Buttondown using the Long-form copy. It does not send.
Open the printed URL, add your discussion questions in the "Questions for you" block,
review the full email, then manually click Send in the Buttondown dashboard.

If `BUTTONDOWN_API_KEY` is not set, skip this step and remind the user to:
1. Create a Buttondown account at buttondown.com
2. Enable "Use Buttondown's mailing address" in Settings (handles CAN-SPAM/CASL)
3. Generate an API key and add `BUTTONDOWN_API_KEY=<key>` to `.env`

---

## Step 8: Retrospective

After the publish completes (or if you hit a significant blocker and solved it),
update `src/publishing/PUBLISH_BEST_PRACTICES.md`:

- If the file doesn't exist, create it with a `# Publish Best Practices` header
  and a `## Blender` / `## Houdini` section structure.
- Add any new gotcha, workaround, or confirmed-good pattern under the relevant DCC section.
- Remove or correct anything that turned out to be wrong.
- Keep entries concise: one problem, one solution, one code snippet if needed.

This file is read at the start of every `/publish` run. Keep it accurate and lean.
