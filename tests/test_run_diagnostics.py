from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from market_impact_radar.run_diagnostics import render_run_diagnostics_html, write_run_diagnostics_html


class RunDiagnosticsTest(unittest.TestCase):
    def test_run_summary_renders_diagnostics(self) -> None:
        html = render_run_diagnostics_html(
            {
                "run_date": "2026-05-15",
                "generated_at": "2026-05-15T01:00:00+00:00",
                "status": "partial",
                "output_dir": "reports/daily/2026-05-15",
                "warnings": ["external completed with partial data"],
                "steps": {
                    "external": {"status": "partial", "path": "external_snapshot.json"},
                    "pipeline": {"status": "ok", "scored_themes": 3},
                    "intraday": {"status": "ok", "summary": {"confirmed": 1, "missing_data": 2}},
                    "knowledge": {"status": "ok", "quality_counts": {"high": 0, "medium": 1, "low": 2, "total": 3}},
                },
                "outputs": {
                    "dashboard_html": "dashboard.html",
                    "run_diagnostics_html": "run_diagnostics.html",
                },
            }
        )

        self.assertIn("Run Diagnostics", html)
        self.assertIn("Pipeline Steps", html)
        self.assertIn("Data Source Health", html)
        self.assertIn("external completed with partial data", html)
        self.assertIn("dashboard.html", html)
        self.assertIn("run_diagnostics.html", html)

    def test_missing_sections_do_not_crash(self) -> None:
        html = render_run_diagnostics_html({"run_date": "2026-05-15"})

        self.assertIn("2026-05-15", html)
        self.assertIn("No pipeline steps available.", html)
        self.assertIn("No warnings or errors.", html)
        self.assertIn("foreign_quotes", html)
        self.assertIn("knowledge", html)

    def test_warnings_errors_and_step_errors_render(self) -> None:
        html = render_run_diagnostics_html(
            {
                "warnings": ["top warning"],
                "errors": ["top error"],
                "steps": {"external": {"status": "failed", "warnings": ["step warning"], "error": "step error"}},
            }
        )

        self.assertIn("top warning", html)
        self.assertIn("top error", html)
        self.assertIn("step warning", html)
        self.assertIn("step error", html)

    def test_outputs_render_unavailable_state(self) -> None:
        html = render_run_diagnostics_html({"outputs": {"dashboard_html": "dashboard.html"}})

        self.assertIn("dashboard.html", html)
        self.assertIn("unavailable", html)

    def test_escapes_visible_text(self) -> None:
        html = render_run_diagnostics_html(
            {
                "run_date": "<script>alert(1)</script>",
                "steps": {"<b>bad</b>": {"status": "ok", "error": "<img src=x>"}},
                "warnings": ["<warning>"],
            }
        )

        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertIn("&lt;b&gt;bad&lt;/b&gt;", html)
        self.assertIn("&lt;warning&gt;", html)
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertNotIn("<b>bad</b>", html)

    def test_write_run_diagnostics_from_summary_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            summary_path = root / "run_summary.json"
            summary_path.write_text(json.dumps({"run_date": "2026-05-15"}), encoding="utf-8")

            output = write_run_diagnostics_html(root, run_summary_path=summary_path)

            self.assertTrue(output.exists())
            self.assertIn("2026-05-15", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
