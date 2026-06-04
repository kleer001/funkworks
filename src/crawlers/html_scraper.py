"""HTML scrapers for forums with no API or RSS.

Currently supports: Nukepedia (Nuke gizmo/plugin repository).
Add new named scrapers here and register them in crawl.py's dispatcher.
"""

import logging
import time
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from src.crawlers.base import MAX_BODY_CHARS

log = logging.getLogger(__name__)


def _fetch_nukepedia(session, source: dict, polite_delay: float) -> list[dict]:
    """Scrape recent Nuke gizmo/plugin listings from Nukepedia.

    Nukepedia is a tool repository — scraping it tells us what already exists
    in the ecosystem and surfaces user discussion threads.

    source fields:
      base_url   — "https://www.nukepedia.com"
      list_path  — path to recent listings (default "/gizmos/")
    """
    base_url = source["base_url"].rstrip("/")
    list_path = source.get("list_path", "/gizmos/")

    try:
        resp = session.get(f"{base_url}{list_path}", timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
    except Exception as e:
        log.warning("Nukepedia listing fetch failed: %s", e)
        return []

    posts: list[dict] = []

    # Nukepedia uses a Drupal-based layout; tool listings are in .views-row or similar
    # Try multiple selector patterns in order of specificity
    selectors = [
        ".views-row",
        "article",
        ".tool-item",
        ".node-teaser",
    ]
    items = []
    for sel in selectors:
        items = soup.select(sel)
        if items:
            break

    for item in items:
        title_el = item.select_one("h2 a, h3 a, .title a, .field-content a")
        desc_el = item.select_one(".field-body, .description, .field-content p, p")
        if title_el:
            title = title_el.get_text(strip=True)
            body = desc_el.get_text(strip=True)[:MAX_BODY_CHARS] if desc_el else ""
            if title:
                href = title_el.get("href")
                url = urljoin(base_url, href) if href else None
                posts.append({"title": title, "body": body, "date": None, "url": url})

    # Also try to get recent discussion threads if a forum section exists
    time.sleep(polite_delay)
    try:
        forum_resp = session.get(f"{base_url}/forum/", timeout=15)
        if forum_resp.status_code == 200:
            forum_soup = BeautifulSoup(forum_resp.text, "html.parser")
            for thread in forum_soup.select(".views-row, tr.odd, tr.even")[:30]:
                t_el = thread.select_one("a, td.views-field-title")
                if t_el:
                    a_el = t_el if t_el.name == "a" else t_el.find("a")
                    href = a_el.get("href") if a_el else None
                    url = urljoin(base_url, href) if href else None
                    posts.append({"title": t_el.get_text(strip=True), "body": "", "date": None, "url": url})
    except Exception:
        pass  # forum section may not exist

    log.info("Nukepedia: fetched %d items", len(posts))
    return posts


_SCRAPERS: dict[str, callable] = {
    "nukepedia": _fetch_nukepedia,
}


def fetch_html(session, source: dict, polite_delay: float = 6.0) -> list[dict]:
    """Dispatch to the appropriate HTML scraper based on source name."""
    name = source.get("name", "").lower()
    for key, fn in _SCRAPERS.items():
        if key in name:
            return fn(session, source, polite_delay)
    log.warning("No HTML scraper implemented for: %s", source.get("name"))
    return []
