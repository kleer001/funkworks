"""Scraper for Stack Exchange sites via the public REST API v2.3.

Anonymous quota: 300 req/day. Register a free key at stackapps.com for 10k/day.
Responses are gzip-compressed; requests handles this automatically.
"""

import logging
from datetime import datetime, timezone

from bs4 import BeautifulSoup

from src.crawlers.base import MAX_BODY_CHARS

log = logging.getLogger(__name__)

SE_API = "https://api.stackexchange.com/2.3/questions"


def fetch_stackexchange(session, source: dict, polite_delay: float = 6.0) -> list[dict]:
    """Return raw {title, body} posts from a Stack Exchange site.

    source fields:
      site      — e.g. "blender" (for blender.stackexchange.com)
      tags      — list of tags to filter; joined with | (OR logic)
      api_key   — optional registered key (raises daily quota to 10k)
    """
    site = source["site"]
    tags = source.get("tags", [])
    key = source.get("api_key")

    params: dict = {
        "site": site,
        "sort": "creation",
        "order": "desc",
        "pagesize": 100,
        "filter": "withbody",
    }
    if tags:
        params["tagged"] = "|".join(tags)
    if key:
        params["key"] = key

    try:
        resp = session.get(SE_API, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        log.warning("Stack Exchange fetch failed (%s): %s", site, e)
        return []

    remaining = data.get("quota_remaining")
    if remaining is not None:
        log.info("Stack Exchange quota remaining: %d", remaining)
        if remaining < 10:
            log.warning("Stack Exchange quota nearly exhausted (%d left)", remaining)

    posts: list[dict] = []
    for item in data.get("items", []):
        title = item.get("title", "").strip()
        body_html = item.get("body", "")
        body = BeautifulSoup(body_html, "html.parser").get_text()[:MAX_BODY_CHARS] if body_html else ""
        creation_date = item.get("creation_date")  # Unix timestamp
        date = (
            datetime.fromtimestamp(creation_date, tz=timezone.utc).strftime("%Y-%m-%d")
            if creation_date else None
        )
        if title:
            posts.append({
                "title": title,
                "body": body,
                "date": date,
                "replies": item.get("answer_count", 0),
                "views": item.get("view_count", 0),
                "score": item.get("score", 0),
                "url": item.get("link"),
            })

    log.info("Stack Exchange %s: fetched %d posts", site, len(posts))
    return posts
