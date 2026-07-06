from __future__ import annotations

import unittest
from datetime import datetime, timedelta, timezone

from github_high_potential.models import Item
from github_high_potential.scoring import score_item, score_items


def make_item(**overrides: object) -> Item:
    values = {
        "source": "github",
        "external_id": "1",
        "title": "Open source coding agent for local LLM workflows",
        "url": "https://github.com/example/agent",
        "summary": "A developer tool for agent automation and RAG.",
        "published_at": datetime.now(timezone.utc) - timedelta(hours=1),
        "authors": ["example"],
        "tags": ["agent", "developer-tool"],
        "metrics": {"stars": 250, "forks": 20},
    }
    values.update(overrides)
    return Item(**values)


class ScoringTest(unittest.TestCase):
    def test_score_item_rewards_relevance_and_traction(self) -> None:
        scored = score_item(make_item())

        self.assertGreater(scored.score, 60)
        self.assertTrue(any("AI relevance" in reason for reason in scored.reasons))
        self.assertTrue(any("GitHub traction" in reason for reason in scored.reasons))

    def test_score_items_sorts_highest_first(self) -> None:
        low = make_item(external_id="low", title="Small CSS utility", summary="", tags=[], metrics={})
        high = make_item(external_id="high")

        scored = score_items([low, high])

        self.assertEqual(scored[0].item.external_id, "high")

    def test_score_item_handles_non_numeric_metrics(self) -> None:
        scored = score_item(make_item(metrics={"stars": "unknown", "forks": None}))

        self.assertGreaterEqual(scored.score, 0)
        self.assertFalse(any("GitHub traction" in reason for reason in scored.reasons))


if __name__ == "__main__":
    unittest.main()
