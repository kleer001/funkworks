#!/usr/bin/env bash
# Install git hooks for this repo. Run once after cloning.
set -e
REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
HOOKS_DIR="$REPO_ROOT/.git/hooks"

cat > "$HOOKS_DIR/pre-commit" << 'EOF'
#!/usr/bin/env bash
# Audit any staged announce.md files before committing.
REPO_ROOT="$(git rev-parse --show-toplevel)"
STAGED=$(git diff --cached --name-only --diff-filter=ACM | grep 'announce\.md$')
if [ -z "$STAGED" ]; then
    exit 0
fi
FAILED=0
for f in $STAGED; do
    python3 "$REPO_ROOT/scripts/audit_announce.py" "$REPO_ROOT/$f"
    if [ $? -ne 0 ]; then
        FAILED=1
    fi
done
if [ $FAILED -ne 0 ]; then
    echo ""
    echo "[pre-commit] announce.md audit failed. Fix the issues above or use git commit --no-verify to override."
    exit 1
fi
EOF

chmod +x "$HOOKS_DIR/pre-commit"
echo "Installed pre-commit hook → $HOOKS_DIR/pre-commit"
