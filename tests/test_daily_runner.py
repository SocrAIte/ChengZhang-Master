from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from market_impact_radar.daily_runner import DailyRunOptions, run_daily
from market_impact_radar.dashboard_contract import DASHBOARD_SCHEMA_VERSION


ROOT = Path(__file__).resolve().parents[1]


def _base_options(tmpdir: str) -> DailyRunOptions:
    return DailyRunOptions(
        run_date="2026-05-15",
        output_root=tmpdir,
        mapping_path=ROOT / "data" / "mappings.json",
        external_path=ROOT / "data" / "sample_external_snapshot.json",
        context_path=ROOT / "data" / "sample_a_share_context.json",
        scoring_rules_path=ROOT / "data" / "scoring_rules.json",
    )


class DailyRunnerTest(unittest.TestCase):
    def test_run_daily_writes_standard_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = run_daily(
                DailyRunOptions(
                    **{
                        **_base_options(tmpdir).__dict__,
                        "a_share_snapshot_path": ROOT / "data" / "a_share_snapshot.sample.json",
                        "skip_knowledge": True,
                    }
                )
            )

            output_dir = Path(tmpdir) / "2026-05-15"
            run_summary_path = output_dir / "run_summary.json"
            dashboard_data_path = output_dir / "dashboard_data.json"
            dashboard_html_path = output_dir / "dashboard.html"
            knowledge_review_path = output_dir / "knowledge_review.html"
            index_json_path = Path(tmpdir) / "index.json"
            index_html_path = Path(tmpdir) / "index.html"
            persisted_summary = json.loads(run_summary_path.read_text(encoding="utf-8"))
            dashboard_data = json.loads(dashboard_data_path.read_text(encoding="utf-8"))
            dashboard_html = dashboard_html_path.read_text(encoding="utf-8")
            knowledge_review_html = knowledge_review_path.read_text(encoding="utf-8")
            history_index = json.loads(index_json_path.read_text(encoding="utf-8"))

            self.assertEqual(summary["status"], "ok")
            self.assertTrue(run_summary_path.exists())
            self.assertTrue(dashboard_data_path.exists())
            self.assertTrue(dashboard_html_path.exists())
            self.assertTrue(knowledge_review_path.exists())
            self.assertTrue(index_json_path.exists())
            self.assertTrue(index_html_path.exists())
            self.assertEqual(history_index["runs"][0]["date"], "2026-05-15")
            self.assertEqual(history_index["runs"][0]["outputs"]["knowledge_review_html"], "2026-05-15/knowledge_review.html")
            self.assertEqual(dashboard_data["schema_version"], DASHBOARD_SCHEMA_VERSION)
            self.assertEqual(dashboard_data["outputs"]["knowledge_review_html"], str(knowledge_review_path))
            self.assertIn("knowledge_review_html", persisted_summary["outputs"])
            self.assertIn("history_index_html", persisted_summary["outputs"])
            self.assertEqual(persisted_summary["steps"]["pipeline"]["status"], "ok")
            self.assertEqual(persisted_summary["steps"]["knowledge"]["status"], "skipped")
            self.assertEqual(dashboard_data["run"]["status"], "ok")
            self.assertTrue(dashboard_data["signals"])
            self.assertIn("2026-05-15", dashboard_html)
            self.assertIn("Schema: 1.0", dashboard_html)
            self.assertIn("Signal List", dashboard_html)
            self.assertIn(dashboard_data["signals"][0]["theme"], dashboard_html)
            self.assertIn(dashboard_data["signals"][0]["etf_candidates"][0], dashboard_html)
            self.assertIn("Risks", dashboard_html)
            self.assertIn("knowledge_review.html", dashboard_html)
            self.assertIn("Knowledge verification was skipped", knowledge_review_html)

    def test_cli_entry_can_skip_a_share_and_knowledge(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            command = [
                sys.executable,
                "-m",
                "market_impact_radar",
                "run-daily",
                "--date",
                "2026-05-15",
                "--output-root",
                tmpdir,
                "--mapping",
                str(ROOT / "data" / "mappings.json"),
                "--external",
                str(ROOT / "data" / "sample_external_snapshot.json"),
                "--context",
                str(ROOT / "data" / "sample_a_share_context.json"),
                "--scoring-rules",
                str(ROOT / "data" / "scoring_rules.json"),
                "--skip-a-share",
                "--skip-knowledge",
            ]
            completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=60)
            output_dir = Path(tmpdir) / "2026-05-15"
            summary = json.loads((output_dir / "run_summary.json").read_text(encoding="utf-8"))
            dashboard_data = json.loads((output_dir / "dashboard_data.json").read_text(encoding="utf-8"))
            dashboard_html = (output_dir / "dashboard.html").read_text(encoding="utf-8")
            knowledge_review_html = (output_dir / "knowledge_review.html").read_text(encoding="utf-8")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(summary["steps"]["a_share"]["status"], "skipped")
        self.assertEqual(summary["steps"]["intraday"]["status"], "skipped")
        self.assertEqual(summary["steps"]["knowledge"]["status"], "skipped")
        self.assertEqual(dashboard_data["schema_version"], DASHBOARD_SCHEMA_VERSION)
        self.assertTrue(all(signal["intraday_status"] == "not_checked" for signal in dashboard_data["signals"]))
        self.assertIn("not_checked", dashboard_html)
        self.assertIn("skipped", knowledge_review_html)

    def test_run_daily_runs_knowledge_check_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = run_daily(
                DailyRunOptions(
                    **{
                        **_base_options(tmpdir).__dict__,
                        "generated_dir": Path(tmpdir) / "generated",
                        "skip_a_share": True,
                    }
                )
            )
            dashboard_data = json.loads(
                (Path(tmpdir) / "2026-05-15" / "dashboard_data.json").read_text(encoding="utf-8")
            )
            knowledge_review_html = (Path(tmpdir) / "2026-05-15" / "knowledge_review.html").read_text(encoding="utf-8")

        self.assertIn(summary["steps"]["knowledge"]["status"], {"ok", "partial"})
        self.assertIn(dashboard_data["knowledge"]["status"], {"ok", "issues"})
        self.assertIn("issues", dashboard_data["knowledge"])
        self.assertIn("Knowledge Graph Review", knowledge_review_html)

    def test_partial_a_share_data_marks_run_partial(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            snapshot = json.loads((ROOT / "data" / "a_share_snapshot.sample.json").read_text(encoding="utf-8"))
            snapshot["source_summary"]["quality_counts"] = {"ok": 7, "partial": 1}
            snapshot["source_summary"]["errors"] = ["market_breadth: sample failure"]
            snapshot["market_breadth"]["data_status"] = "missing"
            partial_snapshot = Path(tmpdir) / "partial_a_share.json"
            partial_snapshot.write_text(json.dumps(snapshot, ensure_ascii=False), encoding="utf-8")

            summary = run_daily(
                DailyRunOptions(
                    **{
                        **_base_options(tmpdir).__dict__,
                        "a_share_snapshot_path": partial_snapshot,
                        "skip_knowledge": True,
                    }
                )
            )
            dashboard_data = json.loads(
                (Path(tmpdir) / "2026-05-15" / "dashboard_data.json").read_text(encoding="utf-8")
            )

        self.assertEqual(summary["status"], "partial")
        self.assertEqual(summary["steps"]["a_share"]["status"], "partial")
        self.assertEqual(dashboard_data["run"]["status"], "partial")
        self.assertTrue(dashboard_data["signals"])

    def test_history_index_failure_records_warning_without_failing_daily_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with patch("market_impact_radar.daily_runner.write_daily_history_index", side_effect=RuntimeError("boom")):
                summary = run_daily(
                    DailyRunOptions(
                        **{
                            **_base_options(tmpdir).__dict__,
                            "a_share_snapshot_path": ROOT / "data" / "a_share_snapshot.sample.json",
                            "skip_knowledge": True,
                        }
                    )
                )
            persisted_summary = json.loads(
                (Path(tmpdir) / "2026-05-15" / "run_summary.json").read_text(encoding="utf-8")
            )

        self.assertEqual(summary["status"], "ok")
        self.assertIn("history index update failed: boom", summary["warnings"])
        self.assertIn("history index update failed: boom", persisted_summary["warnings"])


if __name__ == "__main__":
    unittest.main()
