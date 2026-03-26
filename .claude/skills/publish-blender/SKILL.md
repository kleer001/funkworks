---
name: publish-blender
description: >-
  Publish a completed, tested Blender addon to GitHub Releases and prepare
  announcement copy. TRIGGER when the user asks to publish, release, or ship
  a Blender plugin.
argument-hint: "[plugin-name]"
allowed-tools: Read, Glob, Grep, Write, Edit, Bash, Agent
---

Publish the Blender addon **$ARGUMENTS** to GitHub Releases.

## Before You Start

If `src/publishing/PUBLISH_BEST_PRACTICES.md` exists, read it now. It contains
lessons from previous publish runs — blocked gh commands, zip quirks, announce
copy pitfalls, etc. Apply them before hitting the same problems.

---

## Step 1: Preflight

Verify everything is in place before touching GitHub:

- [ ] `plugins/blender/src/$ARGUMENTS.py` — source file exists
- [ ] `plugins/blender/docs/$ARGUMENTS/README.md` — user-facing docs
- [ ] `plugins/blender/docs/$ARGUMENTS/listing.md` — marketplace copy (used as release body)
- [ ] `plugins/blender/docs/$ARGUMENTS/announce.md` — announcement copy
- [ ] Tutorial page exists under `docs/` (filename may use hyphens: `$ARGUMENTS` with `_` → `-`)
- [ ] Tutorial screenshots present under `docs/images/$ARGUMENTS/`

Extract the version number from `bl_info` in the source file. This is the canonical version — do not invent one.

If anything is missing, stop and tell the user what's needed. Do not proceed.

---

## Step 2: Package

Create the release zip:

```bash
mkdir -p plugins/blender/releases
cd plugins/blender && zip releases/$ARGUMENTS.zip src/$ARGUMENTS.py
```

The zip contains only the single source file. Blender installs single-file addons directly.

---

## Step 3: Create the GitHub Release

```bash
gh release create $ARGUMENTS-v{VERSION} \
  --title "{Plugin Display Name} v{VERSION}" \
  --notes-file plugins/blender/docs/$ARGUMENTS/listing.md \
  plugins/blender/releases/$ARGUMENTS.zip
```

- Tag format: `$ARGUMENTS-v{VERSION}` (e.g. `fluid_domain_visibility-v1.0.0`)
- Title: human-readable display name from `bl_info["name"]` + version
- Notes: `listing.md` long description (already written for this purpose)
- Attach the zip as the release asset

If `gh` fails with a connection error, retry up to 3 times with a few seconds between attempts.

---

## Step 4: Patch announce.md

Read `plugins/blender/docs/$ARGUMENTS/announce.md`. Replace any placeholder URLs
(e.g. `[link]`, `https://github.com/.../releases/tag/PLACEHOLDER`) with the real
release URL:

```
https://github.com/kleer001/funkworks/releases/tag/$ARGUMENTS-v{VERSION}
```

Confirm the URL resolves by checking `gh release view $ARGUMENTS-v{VERSION}`.

---

## Step 5: Output Announcement Copy

Before printing, audit the announce.md copy against these two checks:

- **Title includes "addon"** — people search for "addon", not "plugin" or "tool". The post title must include the word "addon".
- **No unanswered questions** — read the medium-form copy as a first-time reader. Ask: "what questions would I still have?" Fill any gaps before outputting.

Then print the three tiers, clearly labelled:

```
=== SHORT (Twitter / Mastodon / LinkedIn) ===
[copy]

=== MEDIUM (BlenderArtists / Reddit r/blender) ===
[copy]

=== LONG (Newsletter / Blog) ===
[copy]
```

Reddit's API is closed to new personal scripts — posting is manual.
Tell the user: open Reddit, go to r/blender, paste the medium-form copy.
Remind them the RSS feed at `https://kleer001.github.io/funkworks/feed.xml`
will update automatically once the tutorial page is on `main`.

---

## Step 6: Retrospective

After the publish completes (or if you hit a significant blocker and solved it),
update `src/publishing/PUBLISH_BEST_PRACTICES.md`:

- If the file doesn't exist, create it with a `# Blender Publish Best Practices` header.
- Add any new gotcha, workaround, or confirmed-good pattern you encountered.
- Remove or correct anything in the file that turned out to be wrong.
- Keep entries concise: one problem, one solution, one code snippet if needed.

This file is read at the start of every `/publish-blender` run. Keep it accurate
and lean — it compounds across every future release.
