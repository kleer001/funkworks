"""Digest agent: classifies raw Blender posts into plugin opportunities via Claude API.

Reads a raw posts JSON file (produced by the crawler), calls Claude to classify
each post, writes a cleaned opportunity list, then deletes the raw file.
No individual user data is retained in the output.
"""

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Literal

import anthropic
from pydantic import BaseModel

log = logging.getLogger(__name__)

BATCH_SIZE = 20

SYSTEM_PROMPT = """You are a plugin opportunity analyst for the Blender 3D software community.

Classify each Blender forum post for its potential as a new addon/plugin opportunity.

Classification schema:

type:
- "pain_point" — user is frustrated with existing behavior
- "feature_request" — user wants something Blender doesn't have
- "workflow_gap" — user is manually doing something a script could automate
- "bug_upstream" — a Blender bug the user is working around

complexity:
- "trivial" — a ~50-line script could handle this
- "moderate" — meaningful but buildable plugin
- "hard" — significant engineering effort
- "research_required" — unclear if the Blender Python API supports this

novelty:
- "novel" — no known addon addresses this
- "competitive_opportunity" — a paid solution exists; a free/better one would have value
- "already_solved" — a well-known free addon already does this

specificity:
- "high" — real production problem with enough detail to write a spec
- "medium" — identifiable need but vague on details
- "low" — vague complaint or general discussion

summary: One sentence describing the actionable plugin need. Set to null if not an opportunity.
keep: true if worth tracking as a potential plugin build opportunity.

Set keep=false if any of:
- specificity is "low"
- post is a showcase, artwork, or "look at my render" with no plugin need
- type is "bug_upstream" with no obvious plugin-based workaround
- novelty is "already_solved" AND the solution is free and widely known
- post is a general beginner question with no plugin angle (e.g. "how do I use nodes")"""


class PostClassification(BaseModel):
    type: Literal["pain_point", "feature_request", "workflow_gap", "bug_upstream"]
    complexity: Literal["trivial", "moderate", "hard", "research_required"]
    novelty: Literal["novel", "competitive_opportunity", "already_solved"]
    specificity: Literal["high", "medium", "low"]
    summary: str | None = None
    keep: bool


class BatchResult(BaseModel):
    classifications: list[PostClassification]


def classify_batch(client: anthropic.Anthropic, posts: list[dict]) -> list[dict]:
    """Classify a batch of posts. Returns only the kept opportunities."""
    numbered = "\n\n".join(
        f"[{i + 1}] Title: {p['title']}\nBody: {p['body'][:300] or '(no body)'}"
        for i, p in enumerate(posts)
    )

    response = client.messages.parse(
        model="claude-opus-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": (
                f"Classify these {len(posts)} Blender forum posts for plugin opportunity "
                f"potential. Return one classification per post in the same order.\n\n"
                f"{numbered}"
            ),
        }],
        output_format=BatchResult,
    )

    results = response.parsed_output.classifications
    opportunities = []
    for post, classification in zip(posts, results):
        if classification.keep:
            opportunities.append({
                "title": post["title"],
                "type": classification.type,
                "complexity": classification.complexity,
                "novelty": classification.novelty,
                "specificity": classification.specificity,
                "summary": classification.summary,
            })
    return opportunities


def run_digest(
    raw_posts_path: Path,
    output_path: Path,
    client: anthropic.Anthropic | None = None,
) -> int:
    """Classify posts in raw_posts_path, write opportunities to output_path.

    Deletes raw_posts_path after processing. Returns number of opportunities kept.
    """
    if client is None:
        client = anthropic.Anthropic()

    posts = json.loads(raw_posts_path.read_text())
    log.info("Classifying %d posts from %s", len(posts), raw_posts_path)

    opportunities = []
    total_batches = max(1, (len(posts) + BATCH_SIZE - 1) // BATCH_SIZE)
    for i in range(0, len(posts), BATCH_SIZE):
        batch = posts[i:i + BATCH_SIZE]
        kept = classify_batch(client, batch)
        opportunities.extend(kept)
        log.info(
            "Batch %d/%d: kept %d/%d",
            (i // BATCH_SIZE) + 1, total_batches, len(kept), len(batch),
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(opportunities, indent=2))
    log.info("Wrote %d opportunities to %s", len(opportunities), output_path)

    raw_posts_path.unlink()
    log.info("Deleted raw posts file %s", raw_posts_path)

    return len(opportunities)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    parser = argparse.ArgumentParser(description="Classify raw posts into plugin opportunities")
    parser.add_argument("raw_posts", type=Path, help="Path to raw posts JSON file")
    parser.add_argument("output", type=Path, help="Path to write opportunities JSON")
    args = parser.parse_args()

    if not args.raw_posts.exists():
        print(f"Error: {args.raw_posts} does not exist", file=sys.stderr)
        sys.exit(1)

    n = run_digest(args.raw_posts, args.output)
    print(f"Kept {n} opportunities → {args.output}")


if __name__ == "__main__":
    main()
