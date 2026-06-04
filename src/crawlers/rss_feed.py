"""RSS feed scraper with autodiscovery.

Used for forums that expose RSS but no structured API:
OdForce (Invision Community), SideFX Forums, GIMP Forum (MyBB).
"""

import logging
import time
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

from bs4 import BeautifulSoup

from src.crawlers.base import MAX_BODY_CHARS

log = logging.getLogger(__name__)

# RSS content:encoded namespace
_CONTENT_NS = "http://purl.org/rss/1.0/modules/content/"


def _discover_feed_url(session, base_url: str) -> str | None:
    """Find the first RSS feed URL from a page's <link> tags."""
    try:
        resp = session.get(base_url, timeout=12)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        link = soup.find("link", type="application/rss+xml")
        if link and link.get("href"):
            href = str(link["href"])
            if href.startswith("http"):
                return href
            return base_url.rstrip("/") + "/" + href.lstrip("/")
    except Exception as e:
        log.warning("RSS autodiscovery failed for %s: %s", base_url, e)
    return None


_ATOM_NS = "http://www.w3.org/2005/Atom"


def _parse_rss(content: bytes) -> list[dict]:
    """Parse RSS 2.0 or Atom 1.0 XML into a list of {title, body, date} dicts."""
    posts: list[dict] = []
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        log.warning("RSS XML parse error: %s", e)
        return posts

    # Atom 1.0: root tag is {http://www.w3.org/2005/Atom}feed
    if root.tag == f"{{{_ATOM_NS}}}feed":
        for entry in root.iter(f"{{{_ATOM_NS}}}entry"):
            title_el = entry.find(f"{{{_ATOM_NS}}}title")
            summary_el = entry.find(f"{{{_ATOM_NS}}}summary")
            content_el = entry.find(f"{{{_ATOM_NS}}}content")
            published_el = entry.find(f"{{{_ATOM_NS}}}published")
            updated_el = entry.find(f"{{{_ATOM_NS}}}updated")

            title = (title_el.text or "").strip() if title_el is not None else ""
            raw_body = ""
            if content_el is not None and content_el.text:
                raw_body = content_el.text
            elif summary_el is not None and summary_el.text:
                raw_body = summary_el.text

            if raw_body and "<" in raw_body:
                body = BeautifulSoup(raw_body, "html.parser").get_text()[:MAX_BODY_CHARS].strip()
            else:
                body = raw_body[:MAX_BODY_CHARS].strip()

            date_el = published_el if published_el is not None else updated_el
            date = date_el.text[:10] if date_el is not None and date_el.text else None

            link_el = entry.find(f"{{{_ATOM_NS}}}link")
            url = link_el.get("href") if link_el is not None else None

            if title:
                posts.append({"title": title, "body": body, "date": date, "url": url})
        return posts

    # RSS 2.0: root contains <channel><item>...</item></channel>
    for item in root.iter("item"):
        title_el = item.find("title")
        desc_el = item.find("description")
        content_el = item.find(f"{{{_CONTENT_NS}}}encoded")

        title = (title_el.text or "").strip() if title_el is not None else ""
        raw_body = ""
        if content_el is not None and content_el.text:
            raw_body = content_el.text
        elif desc_el is not None and desc_el.text:
            raw_body = desc_el.text

        if raw_body and "<" in raw_body:
            body = BeautifulSoup(raw_body, "html.parser").get_text()[:MAX_BODY_CHARS].strip()
        else:
            body = raw_body[:MAX_BODY_CHARS].strip()

        pub_el = item.find("pubDate")
        dc_el = item.find("{http://purl.org/dc/elements/1.1/}date")
        date = None
        if pub_el is not None and pub_el.text:
            try:
                date = parsedate_to_datetime(pub_el.text).strftime("%Y-%m-%d")
            except Exception:
                pass
        elif dc_el is not None and dc_el.text:
            date = dc_el.text[:10]

        link_el = item.find("link")
        url = link_el.text.strip() if link_el is not None and link_el.text else None

        if title:
            posts.append({"title": title, "body": body, "date": date, "url": url})

    return posts


def fetch_rss(session, source: dict, polite_delay: float = 6.0) -> list[dict]:
    """Return raw {title, body} posts from an RSS feed.

    source fields:
      feed_url  — direct RSS URL (optional; triggers autodiscovery if absent)
      base_url  — homepage used for autodiscovery when feed_url is absent
      name      — human label for logging
      pages     — how many pages to attempt via ?page=N (default 1)

    RSS servers vary in pagination support. If page N returns no new titles
    compared to the previous page, pagination stops early.
    """
    feed_url = source.get("feed_url")
    base_url = source.get("base_url", "")
    name = source.get("name", base_url)
    pages = source.get("pages", 1)

    if not feed_url and base_url:
        log.info("Autodiscovering RSS feed for %s", name)
        feed_url = _discover_feed_url(session, base_url)
        if feed_url:
            time.sleep(polite_delay)

    if not feed_url:
        log.warning("No RSS feed found for %s — skipping", name)
        return []

    seen_titles: set[str] = set()
    all_posts: list[dict] = []

    for page in range(pages):
        url = feed_url if page == 0 else f"{feed_url}?page={page}"
        try:
            resp = session.get(url, timeout=15)
            resp.raise_for_status()
            posts = _parse_rss(resp.content)
        except Exception as e:
            log.warning("RSS fetch failed for %s page %d (%s): %s", name, page, url, e)
            break

        new_posts = [p for p in posts if p["title"] not in seen_titles]
        if not new_posts:
            log.info("RSS %s: no new posts on page %d — stopping", name, page)
            break
        for p in new_posts:
            seen_titles.add(p["title"])
        all_posts.extend(new_posts)

        if page < pages - 1:
            time.sleep(polite_delay)

    log.info("RSS %s: fetched %d posts", name, len(all_posts))
    return all_posts
