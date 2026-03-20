"""Tests for config loading."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest

from src.config import Config, load_config


REQUIRED_ENV = {
    "REDDIT_USER_AGENT": "test_agent",
}


class TestConfig:
    def test_defaults(self):
        cfg = Config(reddit_user_agent="agent")
        assert cfg.subreddit == "blender"
        assert cfg.crawl_limit == 100
        assert cfg.data_dir == Path("data/digests")
        assert cfg.polite_delay == 2.0

    def test_frozen(self):
        cfg = Config(reddit_user_agent="agent")
        with pytest.raises(AttributeError):
            cfg.subreddit = "other"


class TestLoadConfig:
    @patch.dict(os.environ, REQUIRED_ENV, clear=False)
    def test_loads_from_env(self):
        cfg = load_config()
        assert cfg.reddit_user_agent == "test_agent"

    @patch("src.config.load_dotenv")
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_raises(self, _mock_dotenv):
        with pytest.raises(ValueError, match="REDDIT_USER_AGENT"):
            load_config()

    @patch.dict(os.environ, {**REQUIRED_ENV, "FUNKWORKS_SUBREDDIT": "houdini"}, clear=False)
    def test_optional_overrides(self):
        cfg = load_config()
        assert cfg.subreddit == "houdini"

    @patch.dict(os.environ, {**REQUIRED_ENV, "FUNKWORKS_CRAWL_LIMIT": "50"}, clear=False)
    def test_crawl_limit_override(self):
        cfg = load_config()
        assert cfg.crawl_limit == 50
