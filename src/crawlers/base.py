"""Shared utilities for all DCC forum scrapers."""

import copy
import re
import time
from collections import defaultdict

import requests

MAX_BODY_CHARS = 500
MAX_SAMPLE_TITLES = 3

BASE_EXCLUDED_FLAIRS = {
    "showcase", "artwork", "meme", "memes", "humor",
    "render", "finished project", "demo reel",
}

BASE_OPPORTUNITY_SIGNALS: dict[str, list] = {
    "question": [re.compile(r"\?")],
    "how_to": [
        re.compile(r"\bhow\s+(do|can|to|would)\b", re.IGNORECASE),
        re.compile(r"\bis\s+there\s+a\s+way\b", re.IGNORECASE),
    ],
    "plugin_addon": [
        re.compile(r"\bplugin\b", re.IGNORECASE),
        re.compile(r"\badd[- ]?on\b", re.IGNORECASE),
    ],
    "workflow_pain": [
        re.compile(r"\bworkflow\b", re.IGNORECASE),
        re.compile(r"\bfrustrating\b", re.IGNORECASE),
        re.compile(r"\bpain\s*point\b", re.IGNORECASE),
        re.compile(r"\bstruggling\b", re.IGNORECASE),
    ],
    "feature_request": [
        re.compile(r"\bfeature\s+request\b", re.IGNORECASE),
        re.compile(r"\bwish\s+(there\s+was|it)\b", re.IGNORECASE),
    ],
    "help_needed": [
        re.compile(r"\bhelp\b", re.IGNORECASE),
        re.compile(r"\bany\s+(way|tool|script)\b", re.IGNORECASE),
    ],
    "bug_workaround": [
        re.compile(r"\bbug\b", re.IGNORECASE),
        re.compile(r"\bworkaround\b", re.IGNORECASE),
    ],
}


def build_signals(dcc_config: dict | None) -> dict:
    signals = copy.deepcopy(BASE_OPPORTUNITY_SIGNALS)
    if not dcc_config:
        return signals

    for term in dcc_config.get("plugin_terms", []):
        signals["plugin_addon"].append(
            re.compile(r"\b" + re.escape(term) + r"\b", re.IGNORECASE)
        )

    dcc_names = dcc_config.get("feature_request_dcc_names", [])
    if dcc_names:
        alt = "|".join(re.escape(n) for n in dcc_names)
        signals["feature_request"].append(
            re.compile(r"\bwish\s+(there\s+was|" + alt + r"|it)\b", re.IGNORECASE)
        )

    return signals


def build_excluded_flairs(dcc_config: dict | None) -> set:
    flairs = set(BASE_EXCLUDED_FLAIRS)
    if dcc_config:
        flairs.update(f.lower() for f in dcc_config.get("excluded_flairs", []))
    return flairs


def classify_signals(title: str, body: str, signals: dict | None = None) -> set[str]:
    if signals is None:
        signals = BASE_OPPORTUNITY_SIGNALS
    combined = f"{title} {body}"
    return {
        name
        for name, patterns in signals.items()
        if any(p.search(combined) for p in patterns)
    }


def build_digest(posts: list[dict]) -> dict[str, dict]:
    result: dict[str, dict] = defaultdict(lambda: {"count": 0, "sample_titles": []})
    for post in posts:
        for signal in post.get("signals", []):
            result[signal]["count"] += 1
            if len(result[signal]["sample_titles"]) < MAX_SAMPLE_TITLES:
                result[signal]["sample_titles"].append(post["title"])
    return dict(result)


def make_session(user_agent: str) -> requests.Session:
    session = requests.Session()
    session.headers["User-Agent"] = user_agent
    return session


def polite_sleep(delay: float) -> None:
    if delay > 0:
        time.sleep(delay)
