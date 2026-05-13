"""Transform the RCS historical sweep into a standard raw-posts file.

Reads data/rcs_top_open_ideas.json (output of scripts/rcs_historical_sweep.py),
filters by net score, and writes data/raw/raw_Blender_<ts>.json in the shape
the /digest skill expects.

Usage:
    python3 scripts/rcs_sweep_to_raw.py
    python3 scripts/rcs_sweep_to_raw.py --min-score 30
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SWEEP = Path("data/rcs_top_open_ideas.json")
RAW_DIR = Path("data/raw")
DEFAULT_MIN_SCORE = 50


def transform(entry: dict) -> dict:
    raw_date = entry.get("datePublished") or ""
    return {
        "title": entry["title"],
        "body": entry.get("body", ""),
        "date": raw_date[:10] if raw_date else None,
        "replies": entry.get("commentsCount", 0),
        "score": entry["score"],
        "url": entry["url"],
        "category": entry.get("category", ""),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--min-score", type=int, default=DEFAULT_MIN_SCORE)
    args = ap.parse_args()

    sweep = json.loads(SWEEP.read_text())
    kept = [transform(e) for e in sweep if e.get("score", 0) >= args.min_score]

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    out = RAW_DIR / f"raw_Blender_{ts}.json"
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(kept, indent=2))

    print(f"sweep entries: {len(sweep)}")
    print(f"kept (score >= {args.min_score}): {len(kept)}")
    print(f"wrote: {out}")


if __name__ == "__main__":
    main()
