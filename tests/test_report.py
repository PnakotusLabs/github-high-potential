from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from github_high_potential.models import Item, ScoredItem
from github_high_potential.report import write_report


class ReportTest(unittest.TestCase):
    def test_write_report_creates_halfday_markdown(self) -> None:
        item = Item(
            source="github",
            external_id="repo-1",
            title="example/agent",
            url="https://github.com/example/agent",
            summary="Agent workflow toolkit",
            published_at=datetime.now(timezone.utc),
            authors=["example"],
            tags=["agent"],
            metrics={"stars": 42},
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            report_dir = Path(tmpdir)
            path = write_report([ScoredItem(item=item, score=88.5, reasons=["AI relevance"])], report_dir, 12, 5)

            text = path.read_text(encoding="utf-8")
            self.assertEqual(path.parent, report_dir)
            self.assertIn("入库候选：1", text)
            self.assertIn("#### example/agent", text)
            self.assertIn("- 分数：88.5", text)


if __name__ == "__main__":
    unittest.main()
