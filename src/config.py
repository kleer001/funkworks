"""Configuration loading from environment variables."""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    reddit_user_agent: str
    subreddit: str = "blender"
    crawl_limit: int = 100
    data_dir: Path = Path("data/digests")
    polite_delay: float = 6.0
    dcc_config_path: Path | None = None


def load_dcc_config(path: Path) -> dict:
    """Load and return a DCC config JSON file."""
    return json.loads(path.read_text())


def load_config() -> Config:
    """Load config from .env file and environment variables.

    Raises ValueError if REDDIT_USER_AGENT is missing.
    """
    load_dotenv()

    user_agent = os.environ.get("REDDIT_USER_AGENT", "")
    if not user_agent:
        raise ValueError("Missing required environment variable: REDDIT_USER_AGENT")

    subreddit = os.environ.get("FUNKWORKS_SUBREDDIT", "blender")

    # Auto-resolve DCC config from data/dcc_configs/<subreddit>.json if it exists
    dcc_config_path: Path | None = None
    candidate = Path("data/dcc_configs") / f"{subreddit.lower()}.json"
    if candidate.exists():
        dcc_config_path = candidate

    return Config(
        reddit_user_agent=user_agent,
        subreddit=subreddit,
        crawl_limit=int(os.environ.get("FUNKWORKS_CRAWL_LIMIT", "100")),
        data_dir=Path(os.environ.get("FUNKWORKS_DATA_DIR", "data/digests")),
        polite_delay=float(os.environ.get("FUNKWORKS_POLITE_DELAY", "6.0")),
        dcc_config_path=dcc_config_path,
    )
