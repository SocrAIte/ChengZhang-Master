from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from market_impact_radar.knowledge_review import render_knowledge_review_html, write_knowledge_review_html


class KnowledgeReviewTest(unittest.TestCase):
    def test_clean_knowledge_check_renders_clean_state(self) -> None:
        html = render_knowledge_review_html({"status": "ok", "quality_counts": {"total": 0}, "issues": []})

        self.assertIn("Knowledge graph is clean.", html)
        self.assertIn("Total Issues", html)

    def test_issues_group_by_severity(self) -> None:
        html = render_knowledge_review_html(
            {
                "issues": [
                    {"severity": "high", "category": "missing_code", "theme": "AI compute", "message": "high item"},
                    {"severity": "medium", "type": "unverified", "asset": "MU", "message": "medium item"},
                    {"severity": "low", "kind": "metadata", "ticker": "NVDA", "message": "low item"},
                ]
            }
        )

        self.assertIn("High Issues", html)
        self.assertIn("Medium Issues", html)
        self.assertIn("Low Issues", html)
        self.assertIn("high item", html)
        self.assertIn("medium item", html)
        self.assertIn("low item", html)

    def test_fix_suggestions_render(self) -> None:
        html = render_knowledge_review_html(
            {"quality_counts": {"total": 1}},
            {
                "suggestions": [
                    {
                        "target": "storage chips",
                        "action": "add_stock_code",
                        "reason": "candidate lacks code",
                        "suggested_value": {"code": "688000"},
                        "confidence": "medium",
                        "source": "sample",
                        "warning": "manual review required",
                    }
                ]
            },
        )

        self.assertIn("Fix Suggestions", html)
        self.assertIn("storage chips", html)
        self.assertIn("add_stock_code", html)
        self.assertIn("688000", html)
        self.assertIn("manual review required", html)

    def test_missing_knowledge_check_renders_not_available(self) -> None:
        html = render_knowledge_review_html(None)

        self.assertIn("not_available", html)
        self.assertIn("Knowledge check data is not available", html)

    def test_skipped_knowledge_renders_skipped(self) -> None:
        html = render_knowledge_review_html({"status": "skipped", "quality_counts": {"total": 0}})

        self.assertIn("skipped", html)
        self.assertIn("Knowledge verification was skipped", html)

    def test_escapes_visible_text(self) -> None:
        html = render_knowledge_review_html(
            {"issues": [{"severity": "high", "message": "<script>alert(1)</script>"}]},
            [{"target": "<b>bad</b>", "action": "review"}],
        )

        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertIn("&lt;b&gt;bad&lt;/b&gt;", html)
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertNotIn("<b>bad</b>", html)

    def test_write_knowledge_review_html(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = write_knowledge_review_html(Path(tmpdir), {"status": "skipped"})

            self.assertTrue(path.exists())
            self.assertIn("Knowledge Graph Review", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
