#!/usr/bin/env python3
"""
Audit an announce.md for fabricated or unverifiable claims.

Uses the `claude` CLI so no API key management is needed.

Exit codes:
  0 — clean (no issues)
  1 — issues found (printed to stdout)
  2 — usage error or claude CLI not found

Usage:
  python3 scripts/audit_announce.py <path/to/announce.md>
"""

import sys
import subprocess
from pathlib import Path

PROMPT_TEMPLATE = """\
Audit this announce.md for honesty. Apply exactly four tests:

1. FIRST-PERSON EXPERIENCE — Flag "I", "I've", "Every time I", "I always", "I kept \
having to", etc. These are fabricated unless verifiably true from external evidence. \
"So I built X" is OK if X demonstrably exists.

2. READER ASSUMPTION — Flag assertions that the reader has ACTUALLY done or experienced \
something specific: "you've written this five times", "you know how painful this is", \
"every developer has had to do this". Do NOT flag hypothetical or illustrative \
second-person scene-setting that walks through a workflow as a possibility ("you select \
a few objects and reach for the button", "here's a workflow you might run into", "the \
button you'd reach for") — that is ordinary copy, not a claim about the reader's real \
history. The test is whether the sentence asserts the reader's past as fact, not whether \
it uses the word "you".

3. ORDINAL / SUPERLATIVE — Flag "first", "only", "most", "best", "the definitive" \
unless the claim is a documented fact.

4. RHETORICAL FILLER — Flag "finally", "at last", "the way it should be", "which \
feels right", "now you can stop". These add sentiment without information.

Output format — one block per flagged item:
LINE: [exact quote]
PROBLEM: [test number and reason]
FIX: [honest replacement, or "cut it"]

If nothing is flagged, output exactly: NO ISSUES FOUND
No preamble. No sign-off. Only the flagged blocks or NO ISSUES FOUND.

---

{content}\
"""


def find_claude() -> str:
    for candidate in [
        "/home/menser/Dropbox/ai/code/ccwork/bin/claude",
        "claude",
    ]:
        result = subprocess.run(
            ["which", candidate] if candidate == "claude" else ["test", "-x", candidate],
            capture_output=True,
        )
        if result.returncode == 0:
            return candidate
    return "claude"


def audit(path: str) -> int:
    content = Path(path).read_text()
    prompt = PROMPT_TEMPLATE.format(content=content)

    claude = find_claude()
    result = subprocess.run(
        [claude, "-p", prompt, "--model", "claude-haiku-4-5-20251001"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"[honest-copy] claude CLI error:\n{result.stderr}", file=sys.stderr)
        return 2

    output = result.stdout.strip()
    if output == "NO ISSUES FOUND":
        print(f"[honest-copy] {path}: clean")
        return 0
    else:
        print(f"[honest-copy] {path}: issues found\n")
        print(output)
        return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: audit_announce.py <announce.md>", file=sys.stderr)
        sys.exit(2)
    sys.exit(audit(sys.argv[1]))
