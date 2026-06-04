"""Scraper for Discourse-based forums via the public JSON API.

Discourse exposes /latest.json (paginated) without authentication.
Tag-filtered: /tag/{tag}/l/latest.json
"""

import logging
import time

log = logging.getLogger(__name__)

from src.crawlers.base import MAX_BODY_CHARS


def fetch_discourse(session, source: dict, polite_delay: float = 6.0) -> list[dict]:
    """Return raw {title, body} posts from a Discourse forum.

    source fields:
      base_url  — e.g. "https://blenderartists.org"
      tag       — optional tag slug to filter by (e.g. "gimp")
      pages     — number of pages to fetch (default 2, ~30 topics/page)
      categories — ignored (tag filtering is preferred; category IDs not stable)
    """
    base_url = source["base_url"].rstrip("/")
    tag = source.get("tag")
    pages = source.get("pages", 2)
    posts: list[dict] = []

    for page in range(pages):
        if tag:
            url = f"{base_url}/tag/{tag}/l/latest.json"
        else:
            url = f"{base_url}/latest.json"

        try:
            resp = session.get(url, params={"page": page}, timeout=15)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            log.warning("Discourse %s page %d failed: %s", base_url, page, e)
            break

        topics = data.get("topic_list", {}).get("topics", [])
        if not topics:
            break

        for topic in topics:
            title = topic.get("title", "").strip()
            body = topic.get("excerpt", "")[:MAX_BODY_CHARS].strip()
            # Discourse returns ISO 8601 in "created_at" or "bumped_at"
            raw_date = topic.get("created_at", "")
            date = raw_date[:10] if raw_date else None  # "YYYY-MM-DD"
            if title:
                posts.append({
                    "title": title,
                    "body": body,
                    "date": date,
                    "replies": max(0, topic.get("posts_count", 1) - 1),
                    "views": topic.get("views", 0),
                    "url": f"{base_url}/t/{topic['slug']}/{topic['id']}",
                })

        if page < pages - 1:
            time.sleep(polite_delay)

    log.info("Discourse %s: fetched %d posts", source.get("name", base_url), len(posts))
    return posts
