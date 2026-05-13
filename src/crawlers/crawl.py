"""Multi-source crawl orchestrator.

Reads sources from a DCC config dict, dispatches each to the appropriate
scraper, deduplicates, applies signal classification, and writes raw JSON.
"""

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path

from src.config import Config
from src.crawlers.base import (
    build_digest,
    build_excluded_flairs,
    build_signals,
    classify_signals,
    make_session,
    polite_sleep,
)
from src.crawlers.discourse import fetch_discourse
from src.crawlers.html_scraper import fetch_html
from src.crawlers.khoros import fetch_khoros
from src.crawlers.reddit import fetch_reddit
from src.crawlers.rightclickselect import fetch_rightclickselect
from src.crawlers.rss_feed import fetch_rss
from src.crawlers.stackexchange import fetch_stackexchange

log = logging.getLogger(__name__)


def _dispatch(session, source: dict, config: Config, signals: dict, excluded: set) -> list[dict]:
    """Route a source config entry to its scraper. Returns raw {title, body} dicts."""
    t = source.get("type")
    d = config.polite_delay
    if t == "reddit":
        return fetch_reddit(session, source, config, signals, excluded)
    if t == "discourse":
        return fetch_discourse(session, source, d)
    if t == "stackexchange":
        return fetch_stackexchange(session, source, d)
    if t == "rss":
        return fetch_rss(session, source, d)
    if t == "khoros":
        return fetch_khoros(session, source, d)
    if t == "html":
        return fetch_html(session, source, d)
    if t == "rightclickselect":
        return fetch_rightclickselect(session, source, d)
    log.warning("Unknown source type '%s' — skipping", t)
    return []


def crawl_all(config: Config, dcc_config: dict | None) -> tuple[dict, Path]:
    """Crawl all sources in dcc_config, write raw + digest files.

    Returns (digest_dict, raw_posts_path).
    """
    signals = build_signals(dcc_config)
    excluded = build_excluded_flairs(dcc_config)
    session = make_session(config.reddit_user_agent)

    dcc_name = (dcc_config or {}).get("name", config.subreddit)
    sources = (dcc_config or {}).get("sources", [])
    if not sources:
        sources = [{"type": "reddit", "subreddit": config.subreddit}]

    all_raw: list[dict] = []
    seen: set[str] = set()

    for i, source in enumerate(sources):
        log.info("Source %d/%d: %s", i + 1, len(sources), source.get("name", source.get("type")))
        raw = _dispatch(session, source, config, signals, excluded)
        for post in raw:
            key = post["title"].strip().lower()
            if key and key not in seen:
                seen.add(key)
                all_raw.append(post)
        if i < len(sources) - 1:
            polite_sleep(config.polite_delay)

    # Apply signal classification
    categorized: list[dict] = []
    for post in all_raw:
        matched = classify_signals(post["title"], post.get("body", ""), signals)
        if matched:
            entry = {
                "title": post["title"],
                "body": post.get("body", ""),
                "signals": list(matched),
                "date": post.get("date"),
            }
            for field in ("replies", "views", "score"):
                if field in post:
                    entry[field] = post[field]
            categorized.append(entry)

    log.info(
        "Total: %d raw posts → %d with opportunity signals",
        len(all_raw), len(categorized),
    )

    # Write raw posts
    now = datetime.now(timezone.utc)
    ts = now.strftime("%Y-%m-%dT%H-%M-%SZ")
    raw_dir = config.data_dir.parent / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    raw_path = raw_dir / f"raw_{dcc_name}_{ts}.json"
    raw_path.write_text(json.dumps(categorized, indent=2))
    log.info("Raw posts → %s", raw_path)

    # Write aggregate digest
    digest = {
        "dcc": dcc_name,
        "crawled_at": now.isoformat(),
        "total_scanned": len(all_raw),
        "opportunities_found": len(categorized),
        "signals": build_digest(categorized),
    }
    config.data_dir.mkdir(parents=True, exist_ok=True)
    digest_path = config.data_dir / f"digest_{dcc_name}_{ts}.json"
    digest_path.write_text(json.dumps(digest, indent=2))
    log.info("Digest → %s", digest_path)

    return digest, raw_path
