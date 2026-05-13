#!/usr/bin/env bash
# Open the newest plugin's rendered tutorial page.
# Starts the Jekyll preview container in the background if it isn't already running,
# waits for it to respond, then opens the page in the default browser.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCS_DIR="$REPO_ROOT/docs"
URL_BASE="http://localhost:4000/funkworks"
CONTAINER="funkworks-docs-preview"

latest_slug() {
  # Newest *.md in docs/ that isn't index.md, returned as bare slug.
  find "$DOCS_DIR" -maxdepth 1 -name '*.md' ! -name 'index.md' -printf '%T@ %f\n' \
    | sort -rn | head -1 | awk '{print $2}' | sed 's/\.md$//'
}

slug="$(latest_slug)"
if [ -z "$slug" ]; then
  echo "No plugin pages found in $DOCS_DIR" >&2
  exit 1
fi
url="$URL_BASE/$slug"

if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
  echo "Starting Jekyll preview container..."
  docker run --rm -d \
    --name "$CONTAINER" \
    -v "$DOCS_DIR":/srv/jekyll \
    -p 4000:4000 \
    jekyll/jekyll:4.2.2 \
    sh -c "gem install webrick --silent --no-document && jekyll serve --watch --force_polling --baseurl /funkworks --host 0.0.0.0" \
    >/dev/null

  echo -n "Waiting for server"
  for _ in $(seq 1 60); do
    if curl -fsS "$URL_BASE/" -o /dev/null 2>&1; then
      echo " ready."
      break
    fi
    echo -n "."
    sleep 1
  done
fi

echo "Opening $url"
xdg-open "$url" >/dev/null 2>&1 &
