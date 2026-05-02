# Publish Best Practices

## Blender

### Registry files may already be populated
README.md and docs/index.md are sometimes updated before /publish runs (e.g. during
plugin development). Always grep for the plugin name before adding rows — don't
duplicate entries.

### announce.md may have two `[link]` placeholders
Both the medium and long tiers end with a download link. Search and replace both
occurrences when patching the release URL.

### Zip contains only the src file
`zip releases/$NAME.zip src/$NAME.py` — the zip path is `src/$NAME.py`, not just
`$NAME.py`. Blender installs single-file addons directly from this.

## Houdini

### Multi-file install plugins ship more than 2 release assets
The skill template assumes the standard Houdini release attaches `<name>.hda`
plus `build_<name>.py`. Some plugins (e.g. `vellum_attr_stream`) ship a `.cmd`
dispatcher + `.py` setup script + `.hda` trio because Houdini's File > Run Script
only accepts `.cmd`. Attach all four files to the `gh release create` invocation
so users get the complete install bundle, not just the HDA. Listing.md should
enumerate every asset under "Assets" so users know what to download.

### Version-bump commit creates a one-commit lag in the HDA
`build_<name>.py::_git_version()` reads `git rev-list --count HEAD` at build
time. So if you rebuild → commit (which bumps count) → tag, the HDA's embedded
version parm is one count behind the release tag. Two options:
- Live with it (the embedded parm is informational only — users see release tag).
- Use a two-commit dance: bump count somehow first (empty commit), then rebuild
  and commit, so the HDA build sees the final count. Usually not worth the
  ceremony — option 1 is fine.

### Honest-copy pre-commit hook is strict about ordinals
The `[honest-copy]` pre-commit hook on `announce.md` files flags any ordinal
claim including subtle ones like "the first time" or "users always". If a
commit fails on it, fix the copy (don't `--no-verify`) — these are real
audit catches. If the hook itself is unhelpful for a specific case, fix the
audit script, not the commit.

### Banner image is a separate user-driven step
The plugin card on `docs/index.md` references a banner at
`images/banners/<name>_banner.png`. Per the project convention (5 prompt
options, user picks, then generate), don't auto-generate banners during
/publish. Add the card with the banner-path reference and call out that
the banner is missing as a follow-up. Card renders broken-image until
the banner lands but the page still works.
