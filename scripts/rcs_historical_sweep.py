"""One-time deep crawl of the Right-Click Select archive.

Walks all pages of /api/rightclickselect/ideas/, then fetches detail bodies
for high-vote open ideas. Produces:

  data/rcs_index_full.json     — every entry, list-API fields only
  data/rcs_top_open_ideas.json — open ideas with net score >= MIN_VOTES_FOR_BODY,
                                  full body text, sorted by votes desc

Politeness:
  - 6s sleep between every request (CLAUDE.md rule)
  - Single connection, no concurrency
  - Backoff on 429/5xx
  - Identified User-Agent so the operator can block us if needed
  - Resume-from-checkpoint via /tmp/rcs_sweep_state.json

Usage:
    python3 scripts/rcs_historical_sweep.py            # run from scratch
    python3 scripts/rcs_historical_sweep.py --resume   # continue
"""

import argparse
import json
import logging
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bs4 import BeautifulSoup  # noqa: E402

from src.crawlers.base import make_session  # noqa: E402

API_BASE = "https://blender.community"
LIST_PATH = "/api/rightclickselect/ideas/"
DELAY = 6.0
MIN_VOTES_FOR_BODY = 10
MAX_BODY_CHARS = 2000
USER_AGENT = (
    "funkworks/0.1 (+https://github.com/kleer001/funkworks; portfolio research)"
)

STATE_PATH = Path(__file__).resolve().parent.parent / "tmp" / "rcs_sweep_state.json"
INDEX_OUT = Path("data/rcs_index_full.json")
TOP_OUT = Path("data/rcs_top_open_ideas.json")

LIST_FIELDS = (
    "hashId", "title", "categories", "developmentStatus",
    "votesPositiveCount", "votesNegativeCount",
    "commentsCount", "likesCount",
    "datePublished", "absoluteUrl",
)

log = logging.getLogger("rcs_sweep")


def load_state() -> dict:
    if STATE_PATH.exists():
        return json.loads(STATE_PATH.read_text())
    return {
        "phase": "index",
        "last_page_done": 0,
        "index": [],
        "detail_done_hash_ids": [],
        "top": [],
    }


def save_state(state: dict) -> None:
    STATE_PATH.write_text(json.dumps(state))


def polite_get(session, url: str, params: dict | None = None) -> dict | None:
    """GET with 6s pre-sleep and 60s/300s backoff. Returns parsed JSON or None on hard fail."""
    time.sleep(DELAY)
    for backoff in (0, 60, 300):
        if backoff:
            log.warning("Backing off %ds before retry of %s", backoff, url)
            time.sleep(backoff)
        try:
            resp = session.get(
                url,
                params=params,
                headers={"Accept": "application/json"},
                timeout=20,
            )
            if resp.status_code in (429, 500, 502, 503, 504):
                log.warning("HTTP %d on %s", resp.status_code, url)
                continue
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            log.warning("Request to %s failed: %s", url, e)
    return None


def index_phase(session, state: dict) -> None:
    """Walk all list pages, append slim entries to state['index'], persist every 10 pages."""
    page = state["last_page_done"] + 1
    while True:
        data = polite_get(session, API_BASE + LIST_PATH, params={"page": page})
        if data is None:
            log.error("Aborting index phase at page %d (state preserved)", page)
            save_state(state)
            sys.exit(1)
        results = data.get("results") or []
        next_page = data.get("nextPageNumber")
        for item in results:
            slim = {k: item.get(k) for k in LIST_FIELDS}
            state["index"].append(slim)
        state["last_page_done"] = page
        log.info("Page %d: +%d (total %d)", page, len(results), len(state["index"]))
        if not results or next_page is None:
            log.info("Index phase complete at page %d (nextPageNumber=None)", page)
            break
        if page % 10 == 0:
            save_state(state)
        page += 1
    seen: dict = {}
    for e in state["index"]:
        seen[e["hashId"]] = e
    deduped = list(seen.values())
    if len(deduped) != len(state["index"]):
        log.info("Deduped index: %d -> %d", len(state["index"]), len(deduped))
        state["index"] = deduped
    state["phase"] = "detail"
    save_state(state)


def detail_phase(session, state: dict) -> None:
    """Fetch detail body for open ideas above MIN_VOTES_FOR_BODY. Persist every 25 details."""
    candidates = [
        e for e in state["index"]
        if e.get("developmentStatus") == "open"
        and (e.get("votesPositiveCount", 0) - e.get("votesNegativeCount", 0)) >= MIN_VOTES_FOR_BODY
    ]
    candidates.sort(
        key=lambda e: e.get("votesPositiveCount", 0) - e.get("votesNegativeCount", 0),
        reverse=True,
    )
    log.info("Detail phase: %d candidates above %d net votes", len(candidates), MIN_VOTES_FOR_BODY)

    done = set(state["detail_done_hash_ids"])
    fetched = 0
    for entry in candidates:
        hash_id = entry["hashId"]
        if hash_id in done:
            continue
        url = f"{API_BASE}{LIST_PATH}{hash_id}/"
        data = polite_get(session, url)
        if data is None:
            log.error("Aborting detail phase at %s (state preserved)", hash_id)
            save_state(state)
            sys.exit(1)
        body_html = data.get("content") or ""
        body = BeautifulSoup(body_html, "html.parser").get_text(" ", strip=True)[:MAX_BODY_CHARS]
        net = entry.get("votesPositiveCount", 0) - entry.get("votesNegativeCount", 0)
        state["top"].append({
            "hashId": hash_id,
            "title": entry.get("title"),
            "category": entry.get("categories"),
            "developmentStatus": entry.get("developmentStatus"),
            "score": net,
            "votesPositiveCount": entry.get("votesPositiveCount", 0),
            "votesNegativeCount": entry.get("votesNegativeCount", 0),
            "commentsCount": entry.get("commentsCount", 0),
            "likesCount": entry.get("likesCount", 0),
            "datePublished": entry.get("datePublished"),
            "url": API_BASE + (entry.get("absoluteUrl") or ""),
            "body": body,
        })
        done.add(hash_id)
        state["detail_done_hash_ids"] = list(done)
        fetched += 1
        if fetched % 25 == 0:
            save_state(state)
            log.info("Detail progress: %d/%d", fetched, len(candidates))
    log.info("Detail phase complete: %d entries fetched", fetched)


def write_outputs(state: dict) -> None:
    INDEX_OUT.parent.mkdir(parents=True, exist_ok=True)
    INDEX_OUT.write_text(json.dumps(state["index"], indent=2))
    log.info("Wrote %s (%d entries)", INDEX_OUT, len(state["index"]))
    top_sorted = sorted(state["top"], key=lambda e: e["score"], reverse=True)
    TOP_OUT.write_text(json.dumps(top_sorted, indent=2))
    log.info("Wrote %s (%d entries)", TOP_OUT, len(top_sorted))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--resume", action="store_true", help="resume from saved state")
    parser.add_argument("--skip-to-detail", action="store_true",
                        help="dedupe current index and jump straight to detail phase (implies --resume)")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )

    if args.resume or args.skip_to_detail:
        if not STATE_PATH.exists():
            log.error("No state file at %s — nothing to resume", STATE_PATH)
            sys.exit(2)
        state = load_state()
        log.info("Resuming: phase=%s last_page=%d index=%d details_done=%d",
                 state["phase"], state["last_page_done"],
                 len(state["index"]), len(state["detail_done_hash_ids"]))
    else:
        if STATE_PATH.exists():
            log.error("State file %s exists. Pass --resume or remove it.", STATE_PATH)
            sys.exit(2)
        state = load_state()

    if args.skip_to_detail:
        seen: dict = {}
        for e in state["index"]:
            seen[e["hashId"]] = e
        if len(seen) != len(state["index"]):
            log.info("Deduped index: %d -> %d", len(state["index"]), len(seen))
            state["index"] = list(seen.values())
        state["phase"] = "detail"
        save_state(state)
        log.info("Forced phase=detail (index has %d unique entries)", len(state["index"]))

    session = make_session(USER_AGENT)

    if state["phase"] == "index":
        index_phase(session, state)
    if state["phase"] == "detail":
        detail_phase(session, state)

    write_outputs(state)
    STATE_PATH.unlink(missing_ok=True)
    log.info("Sweep complete. State file removed.")


if __name__ == "__main__":
    main()
