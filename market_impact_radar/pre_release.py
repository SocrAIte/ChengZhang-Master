from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from .daily_runner import DailyRunOptions, run_daily
from .dashboard_contract import DASHBOARD_SCHEMA_VERSION, validate_dashboard_data


DEFAULT_CHECK_DATE = "2026-05-15"
DEFAULT_OUTPUT_DIR = "reports/daily/pre-release-check"


class PreReleaseCheckError(RuntimeError):
    pass


@dataclass(frozen=True)
class PreReleaseCheckOptions:
    date: str = DEFAULT_CHECK_DATE
    output_dir: str | Path = DEFAULT_OUTPUT_DIR
    skip_tests: bool = False
    project_root: str | Path = "."


def run_pre_release_check(
    options: PreReleaseCheckOptions,
    test_runner: Callable[[Path], dict[str, Any]] | None = None,
    daily_runner: Callable[[DailyRunOptions], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    root = Path(options.project_root)
    checks: list[dict[str, Any]] = []

    if options.skip_tests:
        checks.append({"name": "tests", "status": "skipped"})
    else:
        test_result = (test_runner or run_unit_tests)(root)
        checks.append({"name": "tests", "status": test_result.get("status", "passed")})

    summary = (daily_runner or run_daily)(
        DailyRunOptions(
            run_date=options.date,
            output_root=options.output_dir,
            external_path=root / "data" / "sample_external_snapshot.json",
            context_path=root / "data" / "sample_a_share_context.json",
            scoring_rules_path=root / "data" / "scoring_rules.json",
            a_share_snapshot_path=root / "data" / "a_share_snapshot.sample.json",
            skip_knowledge=True,
        )
    )
    if summary.get("status") not in {"ok", "partial"}:
        raise PreReleaseCheckError(f"run-daily failed with status {summary.get('status', 'unknown')}")
    checks.append({"name": "run-daily", "status": "passed", "daily_status": summary.get("status")})

    output_dir = Path(summary.get("output_dir") or (Path(options.output_dir) / options.date))
    paths = check_required_outputs(output_dir)
    checks.append({"name": "required outputs", "status": "passed"})

    run_summary = check_run_summary(paths["run_summary"])
    checks.append({"name": "run_summary.json", "status": "passed", "daily_status": run_summary.get("status")})

    dashboard_data = check_dashboard_data(paths["dashboard_data"])
    checks.append(
        {
            "name": "dashboard_data.json",
            "status": "passed",
            "schema_version": dashboard_data.get("schema_version"),
        }
    )

    check_dashboard_html(paths["dashboard_html"])
    checks.append({"name": "dashboard.html", "status": "passed"})

    return {
        "status": "passed",
        "date": options.date,
        "output_dir": str(output_dir),
        "checks": checks,
    }


def run_unit_tests(project_root: Path) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests"],
        cwd=project_root,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        message = "tests failed"
        if completed.stdout:
            message += f"\nstdout:\n{completed.stdout}"
        if completed.stderr:
            message += f"\nstderr:\n{completed.stderr}"
        raise PreReleaseCheckError(message)
    return {"status": "passed", "stdout": completed.stdout, "stderr": completed.stderr}


def check_required_outputs(output_dir: str | Path) -> dict[str, Path]:
    root = Path(output_dir)
    paths = {
        "run_summary": root / "run_summary.json",
        "dashboard_data": root / "dashboard_data.json",
        "dashboard_html": root / "dashboard.html",
    }
    missing = [str(path) for path in paths.values() if not path.exists()]
    if missing:
        raise PreReleaseCheckError(f"missing required outputs: {', '.join(missing)}")
    return paths


def check_dashboard_data(path: str | Path) -> dict[str, Any]:
    payload = _load_json(path)
    if not isinstance(payload, dict):
        raise PreReleaseCheckError("dashboard_data.json must contain a JSON object")
    if payload.get("schema_version") != DASHBOARD_SCHEMA_VERSION:
        raise PreReleaseCheckError(
            f"dashboard_data.json schema_version must be {DASHBOARD_SCHEMA_VERSION}, got {payload.get('schema_version')}"
        )
    issues = validate_dashboard_data(payload)
    errors = [issue for issue in issues if issue.get("level") == "error"]
    if errors:
        raise PreReleaseCheckError(f"dashboard_data.json contract errors: {errors}")
    return payload


def check_run_summary(path: str | Path) -> dict[str, Any]:
    payload = _load_json(path)
    if not isinstance(payload, dict):
        raise PreReleaseCheckError("run_summary.json must contain a JSON object")
    status = payload.get("status")
    if not status:
        raise PreReleaseCheckError("run_summary.json missing status")
    if status in {"failed", "error"}:
        raise PreReleaseCheckError(f"run_summary.json status is {status}")
    outputs = payload.get("outputs")
    if not isinstance(outputs, dict):
        raise PreReleaseCheckError("run_summary.json outputs must be a dict")
    if not (outputs.get("dashboard_data") or outputs.get("dashboard_data_json")):
        raise PreReleaseCheckError("run_summary.json outputs missing dashboard_data")
    if not outputs.get("dashboard_html"):
        raise PreReleaseCheckError("run_summary.json outputs missing dashboard_html")
    return payload


def check_dashboard_html(path: str | Path) -> None:
    target = Path(path)
    if not target.exists():
        raise PreReleaseCheckError(f"dashboard.html missing: {target}")
    text = target.read_text(encoding="utf-8")
    if not text.strip():
        raise PreReleaseCheckError("dashboard.html is empty")
    if "Schema: 1.0" not in text and "schema version" not in text.lower():
        raise PreReleaseCheckError("dashboard.html missing schema version display")
    if "Daily Market Radar" not in text and "Status" not in text:
        raise PreReleaseCheckError("dashboard.html missing dashboard title or status")


def format_pre_release_summary(summary: dict[str, Any]) -> str:
    lines = ["Pre-release check passed"]
    for check in summary.get("checks", []):
        name = check.get("name", "unknown")
        status = check.get("status", "unknown")
        if name == "dashboard_data.json":
            lines.append(f"- {name}: schema_version {check.get('schema_version', 'unknown')}")
        else:
            lines.append(f"- {name}: {status}")
    return "\n".join(lines)


def _load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))
