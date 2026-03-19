"""Reddit crawler for r/blender plugin opportunities.

Fetches posts, filters for opportunity signals, produces an aggregate
digest with zero individual user data retained.
"""

import argparse
import json
import logging
import re
import time
from collections import defaultdict
from datetime import datetime, timezone

import praw

from src.config import Config, load_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

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


def make_reddit(config: Config) -> praw.Reddit:
    """Create a read-only praw Reddit instance."""
    return praw.Reddit(
        client_id=config.reddit_client_id,
        client_secret=config.reddit_client_secret,
        user_agent=config.reddit_user_agent,
    )


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


def fetch_opportunities(
    reddit: praw.Reddit, config: Config
) -> tuple[list[tuple[str, set[str]]], int]:
    """Fetch posts, filter, and classify into opportunity signals.

    Returns (categorized_posts, total_scanned) where categorized_posts
    is a list of (title, signal_names) tuples.
    """
    subreddit = reddit.subreddit(config.subreddit)
    seen_ids: set[str] = set()
    seen_flairs: set[str] = set()
    categorized: list[tuple[str, set[str]]] = []

    sources = [
        ("new", subreddit.new(limit=config.crawl_limit)),
        ("search:questions", subreddit.search("?", sort="new", time_filter="day", limit=50)),
    ]

    for source_name, listings in sources:
        log.info("Fetching from %s/%s", config.subreddit, source_name)
        for submission in listings:
            if submission.id in seen_ids:
                continue
            seen_ids.add(submission.id)

            flair = submission.link_flair_text
            if flair:
                seen_flairs.add(flair)

            if is_excluded_flair(flair):
                continue

            title = submission.title
            selftext = submission.selftext or ""
            signals = classify_signals(title, selftext)
            if signals:
                categorized.append((title, signals))

        time.sleep(config.polite_delay)

    log.info("Flairs seen this crawl: %s", sorted(seen_flairs))
    log.info("Kept %d opportunity posts from %d unique posts", len(categorized), len(seen_ids))
    return categorized, len(seen_ids)


def crawl(config: Config) -> dict:
    """Crawl subreddit, digest opportunities, save aggregate digest."""
    reddit = make_reddit(config)
    categorized, total_scanned = fetch_opportunities(reddit, config)

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
