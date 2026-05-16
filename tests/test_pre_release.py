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
    check_required_outputs,
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
        "<html><body><h1>Daily Market Radar</h1><p>Schema: 1.0</p><p>Status</p></body></html>",
        encoding="utf-8",
    )


class PreReleaseCheckTest(unittest.TestCase):
    def test_run_pre_release_check_happy_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            calls = {"tests": 0, "daily": 0}

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
            )

        self.assertEqual(summary["status"], "passed")
        self.assertEqual(calls, {"tests": 1, "daily": 1})
        self.assertTrue(any(check["name"] == "dashboard_data.json" for check in summary["checks"]))

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
