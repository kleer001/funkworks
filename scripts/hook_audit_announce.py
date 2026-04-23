#!/usr/bin/env python3
"""
Claude Code PostToolUse hook.
Fires after Write or Edit tool use; audits the file if it is an announce.md.

Claude Code passes the tool event as JSON on stdin:
  { "tool_name": "Write"|"Edit", "tool_input": { "file_path": "..." }, ... }

Exit 0 always — this hook warns but never blocks.
"""

import sys
import json
import subprocess
from pathlib import Path

def main():
    try:
        event = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    file_path = event.get("tool_input", {}).get("file_path", "")
    if not file_path.endswith("announce.md"):
        sys.exit(0)

    script = Path(__file__).parent / "audit_announce.py"
    subprocess.run([sys.executable, str(script), file_path])
    # Always exit 0 — we warn in output but never block the tool use.
    sys.exit(0)


if __name__ == "__main__":
    main()
