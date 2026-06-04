"""Scraper for Khoros (formerly Lithium) Community forums via the REST API v2.

Used for: Adobe Community (After Effects, etc.)
Public posts are queryable without authentication via LiQL.

LiQL reference: https://developer.khoros.com/khoroscommunitydevdocs/docs/query-language-reference
"""

import logging

from bs4 import BeautifulSoup

from src.crawlers.base import MAX_BODY_CHARS

log = logging.getLogger(__name__)


def fetch_khoros(session, source: dict, polite_delay: float = 6.0) -> list[dict]:
    """Return raw {title, body} posts from a Khoros community board.

    source fields:
      base_url  — e.g. "https://community.adobe.com"
      board_id  — Khoros board ID slug, e.g. "after-effects"
      limit     — max posts to fetch (default 50)
    """
    base_url = source["base_url"].rstrip("/")
    board_id = source["board_id"]
    limit = source.get("limit", 50)

    query = (
        f"SELECT subject, body, post_time, kudos_sum, views, replies_count, view_href "
        f"FROM messages "
        f"WHERE board.id = '{board_id}' AND depth = 0 "
        f"ORDER BY post_time DESC LIMIT {limit}"
    )

    try:
        resp = session.get(
            f"{base_url}/api/2.0/search",
            params={"q": query, "format": "json"},
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        log.warning("Khoros fetch failed (%s board=%s): %s", base_url, board_id, e)
        return []

    items = data.get("data", {}).get("items", [])
    posts: list[dict] = []

    for item in items:
        subject = (item.get("subject") or "").strip()
        body_raw = item.get("body", "")
        if isinstance(body_raw, dict):
            body_raw = body_raw.get("value", "")
        body_raw = str(body_raw)

        if body_raw and "<" in body_raw:
            body = BeautifulSoup(body_raw, "html.parser").get_text()[:MAX_BODY_CHARS].strip()
        else:
            body = body_raw[:MAX_BODY_CHARS].strip()

        # post_time is an ISO 8601 string like "2026-04-17T14:22:00.000+0000"
        post_time = item.get("post_time", "")
        date = post_time[:10] if post_time else None

        if subject:
            posts.append({
                "title": subject,
                "body": body,
                "date": date,
                "replies": item.get("replies_count", 0),
                "views": item.get("views", 0),
                "score": item.get("kudos_sum", 0),
                "url": item.get("view_href"),
            })

    log.info("Khoros %s/%s: fetched %d posts", base_url, board_id, len(posts))
    return posts
