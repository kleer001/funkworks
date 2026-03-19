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


def build_digest(posts: list[tuple[str, set[str]]]) -> dict[str, dict]:
    """Build signal breakdown from categorized posts.

    Args:
        posts: list of (title, signal_names) tuples

    Returns:
        dict mapping signal name to {count, sample_titles}
    """
    signals: dict[str, dict] = defaultdict(lambda: {"count": 0, "sample_titles": []})
    for title, matched_signals in posts:
        for signal in matched_signals:
            signals[signal]["count"] += 1
            if len(signals[signal]["sample_titles"]) < MAX_SAMPLE_TITLES:
                signals[signal]["sample_titles"].append(title)
    return dict(signals)


def _fetch_listing(session: requests.Session, url: str, params: dict) -> list[dict]:
    """Fetch one page of posts from a Reddit .json listing endpoint."""
    resp = session.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return [child["data"] for child in resp.json()["data"]["children"]]


def fetch_opportunities(
    session: requests.Session, config: Config
) -> tuple[list[tuple[str, set[str]]], int]:
    """Fetch posts, filter, and classify into opportunity signals.

    Returns (categorized_posts, total_scanned) where categorized_posts
    is a list of (title, signal_names) tuples.
    """
    base = f"{BASE_URL}/r/{config.subreddit}"
    sources = [
        (f"{base}/new.json", {"limit": config.crawl_limit}),
        (f"{base}/search.json", {"q": "?", "sort": "new", "t": "day", "limit": 50}),
    ]

    seen_ids: set[str] = set()
    seen_flairs: set[str] = set()
    categorized: list[tuple[str, set[str]]] = []

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
                categorized.append((post["title"], signals))

        time.sleep(config.polite_delay)

    log.info("Flairs seen this crawl: %s", sorted(seen_flairs))
    log.info("Kept %d opportunity posts from %d unique posts", len(categorized), len(seen_ids))
    return categorized, len(seen_ids)


def crawl(config: Config) -> dict:
    """Crawl subreddit, digest opportunities, save aggregate digest."""
    session = make_session(config.reddit_user_agent)
    categorized, total_scanned = fetch_opportunities(session, config)

    now = datetime.now(timezone.utc)
    digest = {
        "subreddit": config.subreddit,
        "crawled_at": now.isoformat(),
        "total_scanned": total_scanned,
        "opportunities_found": len(categorized),
        "signals": build_digest(categorized),
    }

    config.data_dir.mkdir(parents=True, exist_ok=True)
    ts = now.strftime("%Y-%m-%dT%H-%M-%SZ")
    filepath = config.data_dir / f"digest_{config.subreddit}_{ts}.json"
    filepath.write_text(json.dumps(digest, indent=2))
    log.info("Digest saved to %s", filepath)

    return digest


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl r/blender for plugin opportunities")
    parser.parse_args()

    config = load_config()
    digest = crawl(config)
    print(json.dumps(digest, indent=2))


if __name__ == "__main__":
    main()
