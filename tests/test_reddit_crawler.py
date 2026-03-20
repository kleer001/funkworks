"""Tests for reddit crawler (mocked requests session)."""

from unittest.mock import MagicMock

from src.config import Config
from src.crawlers.reddit import (
    build_digest,
    classify_signals,
    fetch_opportunities,
    is_excluded_flair,
    is_opportunity,
)


def _test_config():
    return Config(reddit_user_agent="test", polite_delay=0.0)


def _make_post(id="abc", title="Test post", selftext="", flair=None) -> dict:
    return {"id": id, "title": title, "selftext": selftext, "link_flair_text": flair}


def _mock_response(posts: list[dict]) -> MagicMock:
    """Build a mock requests.Response for a Reddit .json listing."""
    resp = MagicMock()
    resp.json.return_value = {
        "data": {"children": [{"kind": "t3", "data": p} for p in posts]}
    }
    return resp


class TestIsExcludedFlair:
    def test_none_flair(self):
        assert not is_excluded_flair(None)

    def test_showcase(self):
        assert is_excluded_flair("Showcase")

    def test_artwork(self):
        assert is_excluded_flair("Artwork")

    def test_case_insensitive(self):
        assert is_excluded_flair("MEME")

    def test_allowed_flair(self):
        assert not is_excluded_flair("Question")

    def test_whitespace(self):
        assert is_excluded_flair("  render  ")


class TestIsOpportunity:
    def test_question_mark_in_title(self):
        assert is_opportunity("How do I UV unwrap?", "")

    def test_how_do_i(self):
        assert is_opportunity("How do I rig a character", "")

    def test_plugin_mention(self):
        assert is_opportunity("Best plugin for architecture", "")

    def test_addon_mention(self):
        assert is_opportunity("Looking for an addon", "")

    def test_workflow_in_body(self):
        assert is_opportunity("My process", "I need a better workflow")

    def test_frustrating(self):
        assert is_opportunity("This is frustrating", "")

    def test_no_match(self):
        assert not is_opportunity("Check out my render", "Look at this cool thing")

    def test_wish_pattern(self):
        assert is_opportunity("I wish there was a way to batch export", "")

    def test_help(self):
        assert is_opportunity("Need help with nodes", "")


class TestClassifySignals:
    def test_question_mark(self):
        assert "question" in classify_signals("How?", "")

    def test_how_to(self):
        assert "how_to" in classify_signals("How do I bevel", "")

    def test_plugin(self):
        assert "plugin_addon" in classify_signals("Best plugin", "")

    def test_addon_hyphenated(self):
        assert "plugin_addon" in classify_signals("Best add-on", "")

    def test_multiple_signals(self):
        signals = classify_signals("How do I find an addon?", "")
        assert "question" in signals
        assert "how_to" in signals
        assert "plugin_addon" in signals

    def test_no_match(self):
        assert classify_signals("My cool render", "Look at this") == set()

    def test_body_match(self):
        assert "workflow_pain" in classify_signals("Title", "this workflow is bad")

    def test_bug_workaround(self):
        signals = classify_signals("Found a workaround for this bug", "")
        assert "bug_workaround" in signals


class TestBuildDigest:
    def test_counts_and_samples(self):
        posts = [
            {"title": "How do I bevel?", "body": "", "signals": ["question", "how_to"]},
            {"title": "Any addon for retopo?", "body": "", "signals": ["question", "plugin_addon"]},
        ]
        digest = build_digest(posts)
        assert digest["question"]["count"] == 2
        assert digest["how_to"]["count"] == 1
        assert digest["plugin_addon"]["count"] == 1

    def test_sample_title_limit(self):
        posts = [{"title": f"Question {i}?", "body": "", "signals": ["question"]} for i in range(10)]
        digest = build_digest(posts)
        assert digest["question"]["count"] == 10
        assert len(digest["question"]["sample_titles"]) == 3

    def test_empty(self):
        assert build_digest([]) == {}

    def test_sample_titles_preserved(self):
        posts = [{"title": "How do I bevel?", "body": "", "signals": ["question"]}]
        digest = build_digest(posts)
        assert digest["question"]["sample_titles"] == ["How do I bevel?"]


class TestFetchOpportunities:
    def test_filters_and_deduplicates(self):
        opportunity = _make_post(id="q1", title="How do I bevel?")
        showcase = _make_post(id="s1", title="My render", flair="Showcase")
        irrelevant = _make_post(id="i1", title="Check this out", selftext="Cool thing")
        duplicate = _make_post(id="q1", title="How do I bevel?")

        session = MagicMock()
        session.get.side_effect = [
            _mock_response([opportunity, showcase, irrelevant]),
            _mock_response([duplicate]),
        ]

        categorized, total_scanned = fetch_opportunities(session, _test_config())

        assert len(categorized) == 1
        assert categorized[0]["title"] == "How do I bevel?"
        assert "question" in categorized[0]["signals"]
        assert total_scanned == 3

    def test_keeps_multiple_opportunities(self):
        posts = [
            _make_post(id="q1", title="How do I UV unwrap?"),
            _make_post(id="q2", title="Any addon for retopology?"),
            _make_post(id="q3", title="Plugin recommendation?"),
        ]

        session = MagicMock()
        session.get.side_effect = [
            _mock_response(posts),
            _mock_response([]),
        ]

        categorized, total_scanned = fetch_opportunities(session, _test_config())
        assert len(categorized) == 3
        assert total_scanned == 3

    def test_empty_subreddit(self):
        session = MagicMock()
        session.get.side_effect = [
            _mock_response([]),
            _mock_response([]),
        ]

        categorized, total_scanned = fetch_opportunities(session, _test_config())
        assert categorized == []
        assert total_scanned == 0

    def test_post_dict_has_expected_keys(self):
        session = MagicMock()
        session.get.side_effect = [
            _mock_response([_make_post(id="q1", title="How do I bevel?", selftext="Some body")]),
            _mock_response([]),
        ]

        categorized, _ = fetch_opportunities(session, _test_config())
        post = categorized[0]
        assert "title" in post
        assert "body" in post
        assert "signals" in post
        assert isinstance(post["signals"], list)
