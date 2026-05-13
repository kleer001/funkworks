"""
Create a Buttondown draft from the Long section of an announce.md file.

Usage:
    python -m src.newsletter.send plugins/blender/docs/selective_edge_split/announce.md
"""

import os
import re
import sys

import requests
from dotenv import load_dotenv

BUTTONDOWN_API = "https://api.buttondown.email/v1/emails"

DISCUSSION_BLOCK = """
---

**Questions for you:**

[Add 2–3 discussion questions here before sending.]
"""


def extract_long_section(text: str) -> str:
    match = re.search(r"^## Long \(Newsletter.*?\)\s*\n", text, re.MULTILINE)
    if not match:
        print("ERROR: '## Long (Newsletter ...)' section not found in announce.md", file=sys.stderr)
        sys.exit(1)
    return text[match.end():].strip()


def extract_subject(body: str) -> str:
    match = re.search(r"\*\*(.+?)\*\*", body)
    if not match:
        print("ERROR: No **bold headline** found in Long section", file=sys.stderr)
        sys.exit(1)
    return match.group(1).strip()


def create_draft(subject: str, body: str, api_key: str) -> str:
    resp = requests.post(
        BUTTONDOWN_API,
        headers={"Authorization": f"Token {api_key}"},
        json={"subject": subject, "body": body, "status": "draft"},
        timeout=15,
    )
    if not resp.ok:
        print(f"ERROR: Buttondown API returned {resp.status_code}", file=sys.stderr)
        print(resp.text, file=sys.stderr)
        sys.exit(1)
    data = resp.json()
    email_id = data.get("id")
    if not email_id:
        print(f"ERROR: Unexpected API response (no 'id'): {data}", file=sys.stderr)
        sys.exit(1)
    return f"https://buttondown.com/emails/{email_id}"


def main() -> None:
    load_dotenv()

    if len(sys.argv) != 2:
        print("Usage: python -m src.newsletter.send <path/to/announce.md>", file=sys.stderr)
        sys.exit(1)

    announce_path = sys.argv[1]

    api_key = os.environ.get("BUTTONDOWN_API_KEY")
    if not api_key:
        print("ERROR: BUTTONDOWN_API_KEY not set in environment", file=sys.stderr)
        sys.exit(1)

    try:
        text = open(announce_path).read()
    except FileNotFoundError:
        print(f"ERROR: File not found: {announce_path}", file=sys.stderr)
        sys.exit(1)

    long_body = extract_long_section(text)
    subject = extract_subject(long_body)
    full_body = long_body + DISCUSSION_BLOCK

    url = create_draft(subject, full_body, api_key)
    print(f"Draft created: {url}")


if __name__ == "__main__":
    main()
