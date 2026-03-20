"""Reddit crawler for r/blender plugin opportunities.

Uses the public .json endpoints — no OAuth or API approval required.
"""

import argparse
import json
import logging
import re
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import requests

from src.config import Config, load_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

BASE_URL = "https://www.reddit.com"

EXCLUDED_FLAIRS = {
    "showcase", "artwork", "meme", "memes", "humor",
    "render", "finished project", "demo reel",
}

OPPORTUNITY_SIGNALS = {
    "question": [re.compile(r"\?")],
    "how_to": [
        re.compile(r"\bhow\s+(do|can|to|would)\b", re.IGNORECASE),
        re.compile(r"\bis\s+there\s+a\s+way\b", re.IGNORECASE),
    ],
    "plugin_addon": [
        re.compile(r"\bplugin\b", re.IGNORECASE),
        re.compile(r"\badd[- ]?on\b", re.IGNORECASE),
    ],
    "workflow_pain": [
        re.compile(r"\bworkflow\b", re.IGNORECASE),
        re.compile(r"\bfrustrating\b", re.IGNORECASE),
        re.compile(r"\bpain\s*point\b", re.IGNORECASE),
        re.compile(r"\bstruggling\b", re.IGNORECASE),
    ],
    "feature_request": [
        re.compile(r"\bfeature\s+request\b", re.IGNORECASE),
        re.compile(r"\bwish\s+(there\s+was|blender|it)\b", re.IGNORECASE),
    ],
    "help_needed": [
        re.compile(r"\bhelp\b", re.IGNORECASE),
        re.compile(r"\bany\s+(way|tool|script)\b", re.IGNORECASE),
    ],
    "bug_workaround": [
        re.compile(r"\bbug\b", re.IGNORECASE),
        re.compile(r"\bworkaround\b", re.IGNORECASE),
    ],
}

MAX_SAMPLE_TITLES = 3
MAX_BODY_CHARS = 500  # truncate body to keep raw posts file manageable


def make_session(user_agent: str) -> requests.Session:
    """Create a requests session with the given User-Agent header."""
    session = requests.Session()
    session.headers["User-Agent"] = user_agent
    return session


def is_excluded_flair(flair: str | None) -> bool:
    """Check if a post flair indicates non-opportunity content."""
    if not flair:
        return False
    return flair.strip().lower() in EXCLUDED_FLAIRS


def classify_signals(title: str, selftext: str) -> set[str]:
    """Return the set of opportunity signal names that match."""
    combined = f"{title} {selftext}"
    return {
        name
        for name, patterns in OPPORTUNITY_SIGNALS.items()
        if any(p.search(combined) for p in patterns)
    }


def is_opportunity(title: str, selftext: str) -> bool:
    """Check if a post matches any opportunity signal."""
    return bool(classify_signals(title, selftext))


def build_digest(posts: list[dict]) -> dict[str, dict]:
    """Build signal breakdown from categorized posts.

    Args:
        posts: list of dicts with keys title, body, signals

    Returns:
        dict mapping signal name to {count, sample_titles}
    """
    signals: dict[str, dict] = defaultdict(lambda: {"count": 0, "sample_titles": []})
    for post in posts:
        for signal in post["signals"]:
            signals[signal]["count"] += 1
            if len(signals[signal]["sample_titles"]) < MAX_SAMPLE_TITLES:
                signals[signal]["sample_titles"].append(post["title"])
    return dict(signals)


def _fetch_listing(session: requests.Session, url: str, params: dict) -> list[dict]:
    """Fetch one page of posts from a Reddit .json listing endpoint."""
    resp = session.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return [child["data"] for child in resp.json()["data"]["children"]]


def fetch_opportunities(
    session: requests.Session, config: Config
) -> tuple[list[dict], int]:
    """Fetch posts, filter, and classify into opportunity signals.

    Returns (categorized_posts, total_scanned) where each categorized post
    is a dict with keys: title, body, signals. No author or URL retained.
    """
    base = f"{BASE_URL}/r/{config.subreddit}"
    sources = [
        (f"{base}/new.json", {"limit": config.crawl_limit}),
        (f"{base}/search.json", {"q": "?", "sort": "new", "t": "day", "limit": 50, "restrict_sr": 1}),
    ]

    seen_ids: set[str] = set()
    seen_flairs: set[str] = set()
    categorized: list[dict] = []

    for url, params in sources:
        log.info("Fetching %s", url)
        posts = _fetch_listing(session, url, params)
        for post in posts:
            post_id = post["id"]
            if post_id in seen_ids:
                continue
            seen_ids.add(post_id)

            flair = post.get("link_flair_text")
            if flair:
                seen_flairs.add(flair)

            if is_excluded_flair(flair):
                continue

            signals = classify_signals(post["title"], post.get("selftext") or "")
            if signals:
                categorized.append({
                    "title": post["title"],
                    "body": (post.get("selftext") or "")[:MAX_BODY_CHARS],
                    "signals": list(signals),
                })

        time.sleep(config.polite_delay)

    log.info("Flairs seen this crawl: %s", sorted(seen_flairs))
    log.info("Kept %d opportunity posts from %d unique posts", len(categorized), len(seen_ids))
    return categorized, len(seen_ids)


def crawl(config: Config) -> tuple[dict, Path]:
    """Crawl subreddit, save raw posts and aggregate digest.

    Returns (digest, raw_posts_path). The raw posts file is temporary —
    pass it to the digest agent which will delete it after classification.
    """
    session = make_session(config.reddit_user_agent)
    categorized, total_scanned = fetch_opportunities(session, config)

    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y-%m-%dT%H-%M-%SZ")

    # Save raw posts (temp — digest agent will delete after classification)
    raw_dir = config.data_dir.parent / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f"raw_{config.subreddit}_{ts}.json"
    raw_path.write_text(json.dumps(categorized, indent=2))
    log.info("Raw posts saved to %s", raw_path)

    # Save aggregate digest
    digest = {
        "subreddit": config.subreddit,
        "crawled_at": now.isoformat(),
        "total_scanned": total_scanned,
        "opportunities_found": len(categorized),
        "signals": build_digest(categorized),
    }
    config.data_dir.mkdir(parents=True, exist_ok=True)
    digest_path = config.data_dir / f"digest_{config.subreddit}_{ts}.json"
    digest_path.write_text(json.dumps(digest, indent=2))
    log.info("Digest saved to %s", digest_path)

    return digest, raw_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl r/blender for plugin opportunities")
    parser.parse_args()

    config = load_config()
    digest, raw_path = crawl(config)
    print(json.dumps(digest, indent=2))
    print(f"\nRaw posts: {raw_path}", flush=True)


if __name__ == "__main__":
    main()
