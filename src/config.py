"""Configuration loading from environment variables."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    reddit_client_id: str
    reddit_client_secret: str
    reddit_user_agent: str
    subreddit: str = "blender"
    crawl_limit: int = 100
    data_dir: Path = Path("data/digests")
    polite_delay: float = 2.0


def load_config() -> Config:
    """Load config from .env file and environment variables.

    Raises ValueError if required Reddit credentials are missing.
    """
    load_dotenv()

    client_id = os.environ.get("REDDIT_CLIENT_ID", "")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")
    user_agent = os.environ.get("REDDIT_USER_AGENT", "")

    missing = []
    if not client_id:
        missing.append("REDDIT_CLIENT_ID")
    if not client_secret:
        missing.append("REDDIT_CLIENT_SECRET")
    if not user_agent:
        missing.append("REDDIT_USER_AGENT")

    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    return Config(
        reddit_client_id=client_id,
        reddit_client_secret=client_secret,
        reddit_user_agent=user_agent,
        subreddit=os.environ.get("FUNKWORKS_SUBREDDIT", "blender"),
        crawl_limit=int(os.environ.get("FUNKWORKS_CRAWL_LIMIT", "100")),
        data_dir=Path(os.environ.get("FUNKWORKS_DATA_DIR", "data/digests")),
        polite_delay=float(os.environ.get("FUNKWORKS_POLITE_DELAY", "2.0")),
    )
