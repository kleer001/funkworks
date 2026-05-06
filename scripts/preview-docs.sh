#!/usr/bin/env bash
# Serve docs/ locally with the same Jekyll/minima stack GitHub Pages uses.
# Open http://localhost:4000/funkworks/ — pages auto-rebuild on save.
#
# Requires Docker. First run pulls ~600 MB; subsequent runs are instant.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOCS_DIR="$REPO_ROOT/docs"

if ! command -v docker >/dev/null 2>&1; then
  echo "docker not found — install Docker or use 'bundle exec jekyll serve' natively." >&2
  exit 1
fi

echo "Serving $DOCS_DIR at http://localhost:4000/funkworks/"
echo "Tutorial pages: http://localhost:4000/funkworks/subdivide_select_new"
echo "Ctrl-C to stop."
echo

DOCKER_TTY="-it"
[ -t 0 ] || DOCKER_TTY=""

exec docker run --rm $DOCKER_TTY \
  --name funkworks-docs-preview \
  -v "$DOCS_DIR":/srv/jekyll \
  -p 4000:4000 \
  jekyll/jekyll:4.2.2 \
  sh -c "gem install webrick --silent --no-document && jekyll serve --watch --force_polling --baseurl /funkworks --host 0.0.0.0"
