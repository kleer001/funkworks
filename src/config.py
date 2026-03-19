"""Configuration loading from environment variables."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    reddit_user_agent: str
    subreddit: str = "blender"
    crawl_limit: int = 100
    data_dir: Path = Path("data/digests")
    polite_delay: float = 2.0


def load_config() -> Config:
    """Load config from .env file and environment variables.

    Raises ValueError if REDDIT_USER_AGENT is missing.
    """
    load_dotenv()

    user_agent = os.environ.get("REDDIT_USER_AGENT", "")
    if not user_agent:
        raise ValueError("Missing required environment variable: REDDIT_USER_AGENT")

    return Config(
        reddit_user_agent=user_agent,
        subreddit=os.environ.get("FUNKWORKS_SUBREDDIT", "blender"),
        crawl_limit=int(os.environ.get("FUNKWORKS_CRAWL_LIMIT", "100")),
        data_dir=Path(os.environ.get("FUNKWORKS_DATA_DIR", "data/digests")),
        polite_delay=float(os.environ.get("FUNKWORKS_POLITE_DELAY", "2.0")),
    )
