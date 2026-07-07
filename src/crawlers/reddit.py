"""Reddit crawler — reads r/<subreddit> via public .json endpoints."""

import json
import logging
import os
import random
import shutil
import sqlite3
import tempfile
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from glob import glob
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

# Anonymous reddit .json now 403s; the logged-in Firefox session cookie authorizes
# the crawl. State files gate each run to posts newer than the last high-water mark.
STATE_DIR = Path("data/crawl_state")
_GATE_OVERLAP_SEC = 2 * 24 * 3600  # re-fetch a 2-day sliver under the high-water mark
_SINCE_FLOOR_DEFAULT = "2026-05-20"  # first-run floor (last good pre-block crawl was 2026-05-22)

_FIREFOX_COOKIE_GLOBS = (
    "~/snap/firefox/common/.mozilla/firefox/*/cookies.sqlite",
    "~/.mozilla/firefox/*/cookies.sqlite",
    "~/.var/app/org.mozilla.firefox/.mozilla/firefox/*/cookies.sqlite",
)


def firefox_reddit_cookies() -> dict[str, str]:
    """Read logged-in reddit.com cookies from Firefox, newest profile wins.

    Fails loudly if no logged-in Reddit session exists — the fix is to log into
    reddit.com in Firefox, not to fall back to anonymous (which 403s anyway).
    Set REDDIT_COOKIE_DB to point at a specific cookies.sqlite.
    """
    override = os.environ.get("REDDIT_COOKIE_DB")
    if override:
        candidates = [Path(override).expanduser()]
    else:
        candidates = [
            Path(p)
            for pat in _FIREFOX_COOKIE_GLOBS
            for p in glob(str(Path(pat).expanduser()))
        ]

    best: dict[str, str] = {}
    best_mtime = -1.0
    for db in candidates:
        if not db.exists():
            continue
        with tempfile.NamedTemporaryFile(suffix=".sqlite") as tmp:
            shutil.copy2(db, tmp.name)  # copy dodges the live-Firefox write lock
            con = sqlite3.connect(tmp.name)
            try:
                rows = con.execute(
                    "SELECT name, value FROM moz_cookies WHERE host LIKE '%reddit.com'"
                ).fetchall()
            finally:
                con.close()
        if rows and db.stat().st_mtime > best_mtime:
            best_mtime = db.stat().st_mtime
            best = {name: value for name, value in rows}

    if not best:
        raise RuntimeError(
            "No logged-in Reddit session found in Firefox. Log into reddit.com in "
            "Firefox and retry (or set REDDIT_COOKIE_DB to a cookies.sqlite path)."
        )
    return best


def _state_path(subreddit: str) -> Path:
    return STATE_DIR / f"reddit_{subreddit}.json"


def _load_gate(source: dict, subreddit: str) -> tuple[float, str]:
    """Return (gate_utc, reason). Posts older than gate_utc are ignored; /new
    pagination stops once it crosses the gate."""
    p = _state_path(subreddit)
    if p.exists():
        st = json.loads(p.read_text())
        gate = float(st["newest_created_utc"]) - _GATE_OVERLAP_SEC
        return gate, f"high-water {st.get('newest_date')} −2d overlap"
    since = source.get("since", _SINCE_FLOOR_DEFAULT)
    dt = datetime.strptime(since, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return dt.timestamp(), f"since-floor {since}"


def _save_state(subreddit: str, newest_utc: float | None) -> None:
    if newest_utc is None:
        return  # nothing newer seen — keep the prior high-water mark
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    d = datetime.fromtimestamp(newest_utc, tz=timezone.utc)
    _state_path(subreddit).write_text(json.dumps({
        "newest_created_utc": newest_utc,
        "newest_date": d.strftime("%Y-%m-%d"),
        "updated": datetime.now(timezone.utc).isoformat(),
    }, indent=2))


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

    cookies = firefox_reddit_cookies()  # raises if no logged-in session
    gate, gate_reason = _load_gate(source, subreddit)
    log.info("r/%s gate: %s (skipping older posts)", subreddit, gate_reason)

    seen_ids: set[str] = set()
    raw: list[dict] = []
    newest_utc: float | None = None

    def _absorb(post: dict) -> None:
        nonlocal newest_utc
        post_id = post["id"]
        if post_id in seen_ids:
            return
        seen_ids.add(post_id)
        created_utc = post.get("created_utc")
        if created_utc and created_utc < gate:
            return  # older than the high-water mark — already have it
        if created_utc and (newest_utc is None or created_utc > newest_utc):
            newest_utc = created_utc
        flair = post.get("link_flair_text")
        if is_excluded_flair(flair, excluded_flairs):
            return
        title = post["title"]
        body = (post.get("selftext") or "")[:MAX_BODY_CHARS]
        if keywords:
            combined = f"{title} {body}".lower()
            if not any(kw in combined for kw in keywords):
                return
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
            "url": BASE_URL + post["permalink"],
        })

    def _sleep() -> None:
        # Jitter the delay above the polite floor — metronomic timing is a bot tell.
        time.sleep(config.polite_delay + random.uniform(0, 2.5))

    def _get(url: str, params: dict):
        return session.get(url, params=params, cookies=cookies, timeout=15)

    # Paginate /new, newest-first, until the pages cap or the gate — whichever first.
    after = None
    stop = "pages cap"
    for _ in range(pages):
        params: dict = {"limit": config.crawl_limit}
        if after:
            params["after"] = after
        try:
            resp = _get(f"{base}/new.json", params)
            resp.raise_for_status()
            data = resp.json()["data"]
        except Exception as e:
            log.warning("Reddit /new fetch failed: %s", e)
            stop = "fetch error"
            break
        children = data["children"]
        for child in children:
            _absorb(child["data"])
        after = data.get("after")
        oldest = min(
            (c["data"].get("created_utc") or float("inf")) for c in children
        ) if children else None
        if oldest is not None and oldest < gate:
            stop = "reached gate"
            break
        if not after:
            stop = "end of listing"
            break
        _sleep()
    log.info("r/%s /new stopped: %s — %d kept", subreddit, stop, len(raw))

    # Search supplement: catches posts not surfaced by recency order (gate still applies)
    try:
        _sleep()
        resp = _get(
            f"{base}/search.json",
            {"q": "?", "sort": "new", "t": "month", "limit": 100, "restrict_sr": 1},
        )
        resp.raise_for_status()
        for child in resp.json()["data"]["children"]:
            _absorb(child["data"])
    except Exception as e:
        log.warning("Reddit search failed: %s", e)
    _sleep()

    _save_state(subreddit, newest_utc)
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
                    "url": BASE_URL + post["permalink"],
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
