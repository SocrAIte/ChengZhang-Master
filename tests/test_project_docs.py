from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ProjectDocsTest(unittest.TestCase):
    def test_process_docs_exist(self) -> None:
        for path in (
            ROOT / "docs" / "RUN_DAILY.md",
            ROOT / "docs" / "DEVELOPMENT_PROCESS.md",
            ROOT / "docs" / "CHECKLIST.md",
            ROOT / "docs" / "CHECKPOINT_DAILY_REPORT_BUNDLE.md",
            ROOT / "docs" / "PR_DAILY_REPORT_BUNDLE.md",
        ):
            self.assertTrue(path.exists(), f"{path} should exist")

    def test_run_daily_doc_has_core_terms(self) -> None:
        text = (ROOT / "docs" / "RUN_DAILY.md").read_text(encoding="utf-8")

        for term in ("run-daily", "dashboard_data.json", "schema_version", "run_summary.json"):
            self.assertIn(term, text)


if __name__ == "__main__":
    unittest.main()
