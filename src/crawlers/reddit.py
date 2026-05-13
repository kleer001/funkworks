"""Reddit crawler — reads r/<subreddit> via public .json endpoints."""

import json
import logging
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

from src.config import Config, load_dcc_config
from src.crawlers.base import (
    MAX_BODY_CHARS,
    BASE_EXCLUDED_FLAIRS,
    BASE_OPPORTUNITY_SIGNALS,
    build_digest,
    build_excluded_flairs,
    build_signals,
    classify_signals,
    make_session,
)

log = logging.getLogger(__name__)
BASE_URL = "https://www.reddit.com"


# --- backward-compat wrappers (used by tests) ---

def is_excluded_flair(flair: str | None, excluded: set | None = None) -> bool:
    if not flair:
        return False
    if excluded is None:
        excluded = BASE_EXCLUDED_FLAIRS
    return flair.strip().lower() in excluded


def is_opportunity(title: str, selftext: str, signals: dict | None = None) -> bool:
    return bool(classify_signals(title, selftext, signals))


# re-export so tests can import build_digest from here
build_digest = build_digest  # noqa: F811


# --- source handler (used by orchestrator) ---

def fetch_reddit(
    session,
    source: dict,
    config: Config,
    signals: dict | None = None,
    excluded_flairs: set | None = None,
) -> list[dict]:
    """Fetch raw {title, body} posts from one Reddit source config entry.

    Paginates /new up to `pages` pages (default 10) then adds a /search
    supplement with a monthly window to catch posts outside /new order.
    Applies keyword filtering if source has a 'keywords' list.
    """
    subreddit = source.get("subreddit", config.subreddit)
    keywords = [k.lower() for k in source.get("keywords", [])]
    pages = source.get("pages", 10)
    base = f"{BASE_URL}/r/{subreddit}"
    if excluded_flairs is None:
        excluded_flairs = BASE_EXCLUDED_FLAIRS

    seen_ids: set[str] = set()
    raw: list[dict] = []

    def _absorb(post: dict) -> None:
        post_id = post["id"]
        if post_id in seen_ids:
            return
        seen_ids.add(post_id)
        flair = post.get("link_flair_text")
        if is_excluded_flair(flair, excluded_flairs):
            return
        title = post["title"]
        body = (post.get("selftext") or "")[:MAX_BODY_CHARS]
        if keywords:
            combined = f"{title} {body}".lower()
            if not any(kw in combined for kw in keywords):
                return
        created_utc = post.get("created_utc")
        date = (
            datetime.fromtimestamp(created_utc, tz=timezone.utc).strftime("%Y-%m-%d")
            if created_utc else None
        )
        raw.append({
            "title": title,
            "body": body,
            "date": date,
            "replies": post.get("num_comments", 0),
            "score": post.get("score", 0),
        })

    # Paginate /new
    after = None
    for _ in range(pages):
        params: dict = {"limit": config.crawl_limit}
        if after:
            params["after"] = after
        try:
            resp = session.get(f"{base}/new.json", params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()["data"]
        except Exception as e:
            log.warning("Reddit /new fetch failed: %s", e)
            break
        for child in data["children"]:
            _absorb(child["data"])
        after = data.get("after")
        if not after:
            break
        time.sleep(config.polite_delay)

    # Search supplement: catches posts not surfaced by recency order
    try:
        time.sleep(config.polite_delay)
        resp = session.get(
            f"{base}/search.json",
            params={"q": "?", "sort": "new", "t": "month", "limit": 100, "restrict_sr": 1},
            timeout=10,
        )
        resp.raise_for_status()
        for child in resp.json()["data"]["children"]:
            _absorb(child["data"])
    except Exception as e:
        log.warning("Reddit search failed: %s", e)
    time.sleep(config.polite_delay)

    return raw


# --- legacy interface (used by existing tests) ---

def fetch_opportunities(
    session,
    config: Config,
    dcc_config: dict | None = None,
) -> tuple[list[dict], int]:
    """Fetch, filter, and classify posts from a single subreddit.

    Returns (categorized_posts, total_scanned). Kept for test compatibility.
    """
    sigs = build_signals(dcc_config)
    excluded = build_excluded_flairs(dcc_config)

    # Determine subreddit
    subreddit = config.subreddit
    if dcc_config:
        for src in dcc_config.get("sources", []):
            if src.get("type") == "reddit":
                subreddit = src["subreddit"]
                break

    base = f"{BASE_URL}/r/{subreddit}"
    url_sources = [
        (f"{base}/new.json", {"limit": config.crawl_limit}),
        (f"{base}/search.json", {"q": "?", "sort": "new", "t": "day", "limit": 50, "restrict_sr": 1}),
    ]

    seen_ids: set[str] = set()
    seen_flairs: set[str] = set()
    categorized: list[dict] = []

    for url, params in url_sources:
        resp = session.get(url, params=params, timeout=10)
        resp.raise_for_status()
        posts = [child["data"] for child in resp.json()["data"]["children"]]

        for post in posts:
            post_id = post["id"]
            if post_id in seen_ids:
                continue
            seen_ids.add(post_id)

            flair = post.get("link_flair_text")
            if flair:
                seen_flairs.add(flair)
            if is_excluded_flair(flair, excluded):
                continue

            matched = classify_signals(post["title"], post.get("selftext") or "", sigs)
            if matched:
                created_utc = post.get("created_utc")
                date = (
                    datetime.fromtimestamp(created_utc, tz=timezone.utc).strftime("%Y-%m-%d")
                    if created_utc else None
                )
                categorized.append({
                    "title": post["title"],
                    "body": (post.get("selftext") or "")[:MAX_BODY_CHARS],
                    "signals": list(matched),
                    "date": date,
                    "replies": post.get("num_comments", 0),
                    "score": post.get("score", 0),
                })

        time.sleep(config.polite_delay)

    log.info("Flairs seen: %s", sorted(seen_flairs))
    log.info("Kept %d posts from %d unique", len(categorized), len(seen_ids))
    return categorized, len(seen_ids)


def crawl(config: Config) -> tuple[dict, Path]:
    """Single-subreddit crawl — delegates to multi-source orchestrator if DCC config present."""
    from src.crawlers.crawl import crawl_all

    dcc_config = load_dcc_config(config.dcc_config_path) if config.dcc_config_path else None
    return crawl_all(config, dcc_config)
