Publish a completed, tested Blender addon to GitHub Releases and announce it.

**Prerequisites:** Plugin must already be tested in Blender by the developer before running this command.

## Steps

1. **Package the zip** — create `dist/$ARGUMENTS.zip` containing `plugins/$ARGUMENTS.py`.

2. **Create a GitHub Release** using `gh release create`:
   - Tag: `$ARGUMENTS-v<version>` (read version from `bl_info` in the plugin file)
   - Title: the plugin's display name (read from `bl_info["name"]`)
   - Body: the short description from `plugins/$ARGUMENTS/listing.md`
   - Attach `dist/$ARGUMENTS.zip`

3. **Patch announce.md** — replace all `[link]` placeholders in `plugins/$ARGUMENTS/announce.md` with the GitHub Release URL returned by step 2.

4. **Post to Reddit** — post the medium-length announcement copy from `announce.md` to r/blender using PRAW. Requires `REDDIT_USER_AGENT`, `REDDIT_CLIENT_ID`, and `REDDIT_CLIENT_SECRET` in `.env`.

## Conventions

- Never run this command without confirmation that the developer has tested the plugin in Blender
- The `dist/` directory is ephemeral — do not commit zip files
- Reddit posting (step 4) requires `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` in `.env` in addition to `REDDIT_USER_AGENT`; if any are missing, fail and report what's needed
