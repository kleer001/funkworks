"""Scraper for Right-Click Select (blender.community) via its JSON API.

Right-Click Select is Blender's community feature-request board. The site is a
Vue SPA that calls /api/rightclickselect/ideas/ for paginated lists and
/api/rightclickselect/ideas/{hashId}/ for full detail (HTML body).

The API has no working ordering parameters; results come date-desc only.
Vote counts are returned per-item, so high-vote ideas are surfaced via
client-side filtering after the fetch.
"""

import logging
import time

from bs4 import BeautifulSoup

from src.crawlers.base import MAX_BODY_CHARS

log = logging.getLogger(__name__)

API_BASE = "https://blender.community"
LIST_PATH = "/api/rightclickselect/ideas/"


def fetch_rightclickselect(session, source: dict, polite_delay: float = 6.0) -> list[dict]:
    """Return raw posts from Right-Click Select.

    source fields:
      pages           — number of list pages to fetch (default 30, 16 ideas/page)
      min_votes       — skip ideas with fewer net upvotes (default 0)
      include_closed  — if False, skip developmentStatus != "open" (default False)
      fetch_bodies    — if True, hit detail endpoint for each kept idea (default True)
    """
    pages = source.get("pages", 30)
    min_votes = source.get("min_votes", 0)
    include_closed = source.get("include_closed", False)
    fetch_bodies = source.get("fetch_bodies", True)

    posts: list[dict] = []
    seen: set[str] = set()

    for page in range(1, pages + 1):
        try:
            resp = session.get(
                f"{API_BASE}{LIST_PATH}",
                params={"page": page},
                headers={"Accept": "application/json"},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            log.warning("RCS list page %d failed: %s", page, e)
            break

        results = data.get("results", [])
        if not results:
            break

        for item in results:
            hash_id = item.get("hashId")
            if not hash_id or hash_id in seen:
                continue
            seen.add(hash_id)

            if not include_closed and item.get("developmentStatus") != "open":
                continue

            up = item.get("votesPositiveCount", 0)
            down = item.get("votesNegativeCount", 0)
            net = up - down
            if net < min_votes:
                continue

            title = (item.get("title") or "").strip()
            if not title:
                continue

            raw_date = item.get("datePublished", "")
            date = raw_date[:10] if raw_date else None
            url = API_BASE + item.get("absoluteUrl", "")
            category = item.get("categories") or ""

            body = ""
            if fetch_bodies:
                detail_url = API_BASE + item.get("urlApiDetailView", "")
                try:
                    time.sleep(polite_delay)
                    dr = session.get(
                        detail_url,
                        headers={"Accept": "application/json"},
                        timeout=15,
                    )
                    dr.raise_for_status()
                    detail = dr.json()
                    body_html = detail.get("content") or ""
                    body = BeautifulSoup(body_html, "html.parser").get_text(" ", strip=True)[:MAX_BODY_CHARS]
                except Exception as e:
                    log.debug("RCS detail %s failed: %s", hash_id, e)

            posts.append({
                "title": title,
                "body": body,
                "date": date,
                "replies": item.get("commentsCount", 0),
                "score": net,
                "url": url,
                "category": category,
            })

        if page < pages:
            time.sleep(polite_delay)

    log.info("RCS: fetched %d posts across %d pages", len(posts), page)
    return posts
