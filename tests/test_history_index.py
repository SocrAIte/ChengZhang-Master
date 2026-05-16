from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from market_impact_radar.history_index import (
    build_daily_history_index,
    render_daily_history_index_html,
    write_daily_history_index,
)


ROOT = Path(__file__).resolve().parents[1]


def _write_run(
    reports_dir: Path,
    run_date: str,
    *,
    status: str = "ok",
    generated_at: str = "2026-05-15T01:00:00+00:00",
    dashboard_data: bool = True,
    run_summary: bool = True,
) -> Path:
    run_dir = reports_dir / run_date
    run_dir.mkdir(parents=True, exist_ok=True)
    if run_summary:
        (run_dir / "run_summary.json").write_text(
            json.dumps(
                {
                    "run_date": run_date,
                    "generated_at": generated_at,
                    "status": status,
                    "warnings": ["sample warning"],
                    "outputs": {},
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
    if dashboard_data:
        (run_dir / "dashboard_data.json").write_text(
            json.dumps(
                {
                    "schema_version": "1.0",
                    "run": {"date": run_date, "generated_at": generated_at, "status": status},
                    "summary": {
                        "strong_signals": 2,
                        "confirmed": 1,
                        "downgraded": 0,
                        "failed": 0,
                        "missing_data": 1,
                        "knowledge_issues": 3,
                    },
                    "signals": [],
                    "knowledge": {},
                    "outputs": {},
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
    (run_dir / "dashboard.html").write_text("<html>dashboard</html>", encoding="utf-8")
    (run_dir / "report.md").write_text("# report", encoding="utf-8")
    return run_dir


class DailyHistoryIndexTest(unittest.TestCase):
    def test_build_index_from_multiple_daily_dirs_sorted_desc(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            reports_dir = Path(tmpdir)
            _write_run(reports_dir, "2026-05-14", status="partial")
            _write_run(reports_dir, "2026-05-15", status="ok")

            index = build_daily_history_index(reports_dir)

        self.assertEqual(index["schema_version"], "1.0")
        self.assertEqual([run["date"] for run in index["runs"]], ["2026-05-15", "2026-05-14"])
        self.assertEqual(index["runs"][0]["summary"]["strong_signals"], 2)
        self.assertEqual(index["runs"][0]["outputs"]["dashboard_html"], "2026-05-15/dashboard.html")

    def test_missing_run_summary_does_not_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            reports_dir = Path(tmpdir)
            _write_run(reports_dir, "2026-05-15", run_summary=False)

            index = build_daily_history_index(reports_dir)

        self.assertEqual(index["runs"][0]["status"], "partial")
        self.assertIn("missing run_summary.json", index["runs"][0]["warnings"])

    def test_missing_dashboard_data_does_not_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            reports_dir = Path(tmpdir)
            _write_run(reports_dir, "2026-05-15", dashboard_data=False)

            index = build_daily_history_index(reports_dir)

        self.assertEqual(index["runs"][0]["status"], "partial")
        self.assertIn("missing dashboard_data.json", index["runs"][0]["warnings"])

    def test_empty_html_renders_empty_state(self) -> None:
        html = render_daily_history_index_html({"schema_version": "1.0", "generated_at": "now", "runs": []})

        self.assertIn("Daily Runs", html)
        self.assertIn("No daily runs found.", html)

    def test_html_contains_links_and_escapes_text(self) -> None:
        html = render_daily_history_index_html(
            {
                "schema_version": "1.0",
                "generated_at": "<bad>",
                "runs": [
                    {
                        "date": "2026-05-15",
                        "status": "<script>",
                        "generated_at": "2026-05-15T01:00:00+00:00",
                        "summary": {},
                        "warnings": ["<warning>"],
                        "outputs": {
                            "dashboard_html": "2026-05-15/dashboard.html",
                            "dashboard_data_json": "2026-05-15/dashboard_data.json",
                            "run_summary_json": "2026-05-15/run_summary.json",
                            "report_md": "2026-05-15/report.md",
                        },
                    }
                ],
            }
        )

        self.assertIn("2026-05-15", html)
        self.assertIn("dashboard.html", html)
        self.assertIn("dashboard_data.json", html)
        self.assertIn("run_summary.json", html)
        self.assertIn("report.md", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)

    def test_write_daily_history_index_writes_json_and_html(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            reports_dir = Path(tmpdir)
            _write_run(reports_dir, "2026-05-15")

            outputs = write_daily_history_index(reports_dir)

            self.assertTrue(outputs["index_json"].exists())
            self.assertTrue(outputs["index_html"].exists())
            index = json.loads(outputs["index_json"].read_text(encoding="utf-8"))

        self.assertEqual(index["runs"][0]["date"], "2026-05-15")

    def test_cli_build_history_index_generates_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            reports_dir = Path(tmpdir)
            _write_run(reports_dir, "2026-05-15")
            command = [
                sys.executable,
                "-m",
                "market_impact_radar",
                "build-history-index",
                "--reports-dir",
                str(reports_dir),
            ]
            completed = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=60)

            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue((reports_dir / "index.json").exists())
            self.assertTrue((reports_dir / "index.html").exists())


if __name__ == "__main__":
    unittest.main()
