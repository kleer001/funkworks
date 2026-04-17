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

(no entries yet)
