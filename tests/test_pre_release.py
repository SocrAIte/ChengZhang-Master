from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from market_impact_radar.daily_runner import DailyRunOptions
from market_impact_radar.dashboard_contract import DASHBOARD_SCHEMA_VERSION
from market_impact_radar.pre_release import (
    PreReleaseCheckError,
    PreReleaseCheckOptions,
    check_dashboard_data,
    check_dashboard_html,
    check_knowledge_review_html,
    check_required_outputs,
    check_run_diagnostics_html,
    run_pre_release_check,
)


def _write_valid_outputs(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "run_summary.json").write_text(
        json.dumps(
            {
                "status": "ok",
                "outputs": {
                    "dashboard_data": str(output_dir / "dashboard_data.json"),
                    "dashboard_html": str(output_dir / "dashboard.html"),
                    "knowledge_review_html": str(output_dir / "knowledge_review.html"),
                    "run_diagnostics_html": str(output_dir / "run_diagnostics.html"),
                },
            }
        ),
        encoding="utf-8",
    )
    (output_dir / "dashboard_data.json").write_text(
        json.dumps(
            {
                "schema_version": DASHBOARD_SCHEMA_VERSION,
                "run": {},
                "summary": {},
                "signals": [],
                "knowledge": {},
                "outputs": {},
            }
        ),
        encoding="utf-8",
    )
    (output_dir / "dashboard.html").write_text(
        "<html><body><h1>Daily Market Radar</h1><p>Schema: 1.0</p><p>Status</p><a href='knowledge_review.html'>knowledge_review.html</a><a href='run_diagnostics.html'>run_diagnostics.html</a></body></html>",
        encoding="utf-8",
    )
    (output_dir / "knowledge_review.html").write_text(
        "<html><body><h1>Knowledge Graph Review</h1><p>skipped</p></body></html>",
        encoding="utf-8",
    )
    (output_dir / "run_diagnostics.html").write_text(
        "<html><body><h1>Run Diagnostics</h1><p>ok</p></body></html>",
        encoding="utf-8",
    )


class PreReleaseCheckTest(unittest.TestCase):
    def test_run_pre_release_check_happy_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            calls = {"tests": 0, "daily": 0, "browser": 0}

            def fake_tests(project_root: Path) -> dict:
                calls["tests"] += 1
                return {"status": "passed"}

            def fake_daily(options: DailyRunOptions) -> dict:
                calls["daily"] += 1
                output_dir = Path(options.output_root) / str(options.run_date)
                _write_valid_outputs(output_dir)
                return {"status": "ok", "output_dir": str(output_dir)}

            summary = run_pre_release_check(
                PreReleaseCheckOptions(date="2026-05-15", output_dir=tmpdir),
                test_runner=fake_tests,
                daily_runner=fake_daily,
                browser_smoke=lambda path: calls.__setitem__("browser", calls["browser"] + 1),
            )

        self.assertEqual(summary["status"], "passed")
        self.assertEqual(calls, {"tests": 1, "daily": 1, "browser": 0})
        self.assertTrue(any(check["name"] == "dashboard_data.json" for check in summary["checks"]))
        self.assertTrue(any(check["name"] == "knowledge_review.html" for check in summary["checks"]))
        self.assertTrue(any(check["name"] == "run_diagnostics.html" for check in summary["checks"]))

    def test_with_browser_calls_browser_smoke(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            calls = {"browser": 0}

            def fake_daily(options: DailyRunOptions) -> dict:
                output_dir = Path(options.output_root) / str(options.run_date)
                _write_valid_outputs(output_dir)
                return {"status": "ok", "output_dir": str(output_dir)}

            def fake_browser(path: Path) -> None:
                calls["browser"] += 1

            summary = run_pre_release_check(
                PreReleaseCheckOptions(date="2026-05-15", output_dir=tmpdir, skip_tests=True, with_browser=True),
                daily_runner=fake_daily,
                browser_smoke=fake_browser,
            )

        self.assertEqual(calls["browser"], 1)
        self.assertTrue(any(check["name"] == "browser smoke" for check in summary["checks"]))

    def test_browser_smoke_failure_fails_pre_release(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:

            def fake_daily(options: DailyRunOptions) -> dict:
                output_dir = Path(options.output_root) / str(options.run_date)
                _write_valid_outputs(output_dir)
                return {"status": "ok", "output_dir": str(output_dir)}

            def failing_browser(path: Path) -> None:
                from market_impact_radar.browser_smoke import BrowserSmokeError

                raise BrowserSmokeError("console errors")

            with self.assertRaisesRegex(PreReleaseCheckError, "browser smoke failed"):
                run_pre_release_check(
                    PreReleaseCheckOptions(date="2026-05-15", output_dir=tmpdir, skip_tests=True, with_browser=True),
                    daily_runner=fake_daily,
                    browser_smoke=failing_browser,
                )

    def test_skip_tests_does_not_call_test_runner(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:

            def fail_if_called(project_root: Path) -> dict:
                raise AssertionError("test runner should not be called")

            def fake_daily(options: DailyRunOptions) -> dict:
                output_dir = Path(options.output_root) / str(options.run_date)
                _write_valid_outputs(output_dir)
                return {"status": "ok", "output_dir": str(output_dir)}

            summary = run_pre_release_check(
                PreReleaseCheckOptions(date="2026-05-15", output_dir=tmpdir, skip_tests=True),
                test_runner=fail_if_called,
                daily_runner=fake_daily,
            )

        self.assertIn({"name": "tests", "status": "skipped"}, summary["checks"])

    def test_missing_run_summary_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            _write_valid_outputs(output_dir)
            (output_dir / "run_summary.json").unlink()

            with self.assertRaisesRegex(PreReleaseCheckError, "missing required outputs"):
                check_required_outputs(output_dir)

    def test_missing_dashboard_data_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            _write_valid_outputs(output_dir)
            (output_dir / "dashboard_data.json").unlink()

            with self.assertRaisesRegex(PreReleaseCheckError, "missing required outputs"):
                check_required_outputs(output_dir)

    def test_missing_knowledge_review_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            _write_valid_outputs(output_dir)
            (output_dir / "knowledge_review.html").unlink()

            with self.assertRaisesRegex(PreReleaseCheckError, "missing required outputs"):
                check_required_outputs(output_dir)

    def test_missing_run_diagnostics_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            _write_valid_outputs(output_dir)
            (output_dir / "run_diagnostics.html").unlink()

            with self.assertRaisesRegex(PreReleaseCheckError, "missing required outputs"):
                check_required_outputs(output_dir)

    def test_empty_knowledge_review_html_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "knowledge_review.html"
            path.write_text("", encoding="utf-8")

            with self.assertRaisesRegex(PreReleaseCheckError, "empty"):
                check_knowledge_review_html(path)

    def test_empty_run_diagnostics_html_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "run_diagnostics.html"
            path.write_text("", encoding="utf-8")

            with self.assertRaisesRegex(PreReleaseCheckError, "empty"):
                check_run_diagnostics_html(path)

    def test_dashboard_html_without_knowledge_review_link_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "dashboard.html"
            path.write_text(
                "<html><body><h1>Daily Market Radar</h1><p>Schema: 1.0</p><p>Status</p></body></html>",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(PreReleaseCheckError, "knowledge review link"):
                check_dashboard_html(path)

    def test_dashboard_html_without_run_diagnostics_link_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "dashboard.html"
            path.write_text(
                "<html><body><h1>Daily Market Radar</h1><p>Schema: 1.0</p><p>Status</p><a href='knowledge_review.html'>knowledge_review.html</a></body></html>",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(PreReleaseCheckError, "run diagnostics link"):
                check_dashboard_html(path)

    def test_bad_dashboard_schema_version_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "dashboard_data.json"
            path.write_text(
                json.dumps(
                    {
                        "schema_version": "0.9",
                        "run": {},
                        "summary": {},
                        "signals": [],
                        "knowledge": {},
                        "outputs": {},
                    }
                ),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(PreReleaseCheckError, "schema_version"):
                check_dashboard_data(path)

    def test_empty_dashboard_html_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "dashboard.html"
            path.write_text("", encoding="utf-8")

            with self.assertRaisesRegex(PreReleaseCheckError, "empty"):
                check_dashboard_html(path)

    def test_failing_test_runner_raises_clear_error(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:

            def failing_tests(project_root: Path) -> dict:
                raise PreReleaseCheckError("tests failed")

            def fake_daily(options: DailyRunOptions) -> dict:
                raise AssertionError("daily runner should not run after failed tests")

            with self.assertRaisesRegex(PreReleaseCheckError, "tests failed"):
                run_pre_release_check(
                    PreReleaseCheckOptions(date="2026-05-15", output_dir=tmpdir),
                    test_runner=failing_tests,
                    daily_runner=fake_daily,
                )


if __name__ == "__main__":
    unittest.main()
