"""Tests for digest agent (mocked Anthropic client)."""

import json
from pathlib import Path
from unittest.mock import MagicMock

from src.digest.agent import BatchResult, PostClassification, classify_batch, run_digest


def _mock_client(classifications: list[PostClassification]) -> MagicMock:
    client = MagicMock()
    mock_response = MagicMock()
    mock_response.parsed_output = BatchResult(classifications=classifications)
    client.messages.parse.return_value = mock_response
    return client


def _classification(**kwargs) -> PostClassification:
    defaults = {
        "type": "workflow_gap",
        "complexity": "trivial",
        "novelty": "novel",
        "specificity": "high",
        "summary": "A useful plugin opportunity.",
        "keep": True,
    }
    return PostClassification(**{**defaults, **kwargs})


class TestClassifyBatch:
    def test_keeps_high_specificity_opportunity(self):
        client = _mock_client([_classification(summary="Need batch UV rename tool.")])
        posts = [{"title": "How do I batch rename UV maps?", "body": "", "signals": ["how_to"]}]

        result = classify_batch(client, posts)

        assert len(result) == 1
        assert result[0]["title"] == "How do I batch rename UV maps?"
        assert result[0]["type"] == "workflow_gap"
        assert result[0]["summary"] == "Need batch UV rename tool."

    def test_filters_low_specificity(self):
        client = _mock_client([_classification(specificity="low", summary=None, keep=False)])
        posts = [{"title": "Blender is frustrating", "body": "", "signals": ["workflow_pain"]}]

        result = classify_batch(client, posts)

        assert result == []

    def test_returns_only_kept(self):
        client = _mock_client([
            _classification(summary="Opportunity.", keep=True),
            _classification(specificity="low", summary=None, keep=False),
        ])
        posts = [
            {"title": "How to automate X?", "body": "", "signals": ["how_to"]},
            {"title": "Check my render", "body": "", "signals": []},
        ]

        result = classify_batch(client, posts)

        assert len(result) == 1
        assert result[0]["title"] == "How to automate X?"

    def test_output_has_no_author_or_url(self):
        client = _mock_client([_classification()])
        posts = [{"title": "How do I do X?", "body": "body text", "signals": ["how_to"]}]

        result = classify_batch(client, posts)

        assert len(result) == 1
        assert "author" not in result[0]
        assert "url" not in result[0]
        assert "body" not in result[0]

    def test_output_fields(self):
        client = _mock_client([_classification(
            type="feature_request",
            complexity="moderate",
            novelty="competitive_opportunity",
            specificity="high",
            summary="Need a batch export tool.",
        )])
        posts = [{"title": "Any tool for batch export?", "body": "", "signals": ["plugin_addon"]}]

        result = classify_batch(client, posts)

        assert result[0]["type"] == "feature_request"
        assert result[0]["complexity"] == "moderate"
        assert result[0]["novelty"] == "competitive_opportunity"
        assert result[0]["specificity"] == "high"
        assert result[0]["summary"] == "Need a batch export tool."


class TestRunDigest:
    def test_processes_and_deletes_raw_file(self, tmp_path):
        raw_posts = [{"title": "How to batch rename UVs?", "body": "", "signals": ["how_to"]}]
        raw_path = tmp_path / "raw_blender.json"
        raw_path.write_text(json.dumps(raw_posts))
        output_path = tmp_path / "opportunities.json"

        client = _mock_client([_classification(summary="Need UV renaming tool.")])

        n = run_digest(raw_path, output_path, client=client)

        assert n == 1
        assert not raw_path.exists()
        assert output_path.exists()
        opportunities = json.loads(output_path.read_text())
        assert len(opportunities) == 1
        assert opportunities[0]["title"] == "How to batch rename UVs?"

    def test_empty_posts_writes_empty_output(self, tmp_path):
        raw_path = tmp_path / "raw_blender.json"
        raw_path.write_text(json.dumps([]))
        output_path = tmp_path / "opportunities.json"

        client = _mock_client([])

        n = run_digest(raw_path, output_path, client=client)

        assert n == 0
        assert not raw_path.exists()
        assert json.loads(output_path.read_text()) == []

    def test_batches_large_input(self, tmp_path):
        # 25 posts → 2 batches (20 + 5)
        raw_posts = [
            {"title": f"How do I do thing {i}?", "body": "", "signals": ["how_to"]}
            for i in range(25)
        ]
        raw_path = tmp_path / "raw_blender.json"
        raw_path.write_text(json.dumps(raw_posts))
        output_path = tmp_path / "opportunities.json"

        client = MagicMock()
        # First batch: 20 posts, keep all
        batch1_response = MagicMock()
        batch1_response.parsed_output = BatchResult(
            classifications=[_classification() for _ in range(20)]
        )
        # Second batch: 5 posts, keep all
        batch2_response = MagicMock()
        batch2_response.parsed_output = BatchResult(
            classifications=[_classification() for _ in range(5)]
        )
        client.messages.parse.side_effect = [batch1_response, batch2_response]

        n = run_digest(raw_path, output_path, client=client)

        assert n == 25
        assert client.messages.parse.call_count == 2
