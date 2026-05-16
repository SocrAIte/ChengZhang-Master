from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .html_components import PAGE_NAV_CSS, render_page_nav
from .io import write_text


HISTORY_INDEX_SCHEMA_VERSION = "1.0"
_DATE_DIR_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def build_daily_history_index(reports_dir: str | Path) -> dict[str, Any]:
    root = Path(reports_dir)
    runs = [_build_run_entry(path) for path in _date_dirs(root)]
    runs.sort(key=lambda item: str(item.get("date") or ""), reverse=True)
    return {
        "schema_version": HISTORY_INDEX_SCHEMA_VERSION,
        "generated_at": _now_iso(),
        "runs": runs,
    }


def render_daily_history_index_html(index_data: dict[str, Any] | None) -> str:
    data = index_data if isinstance(index_data, dict) else {}
    runs = data.get("runs") if isinstance(data.get("runs"), list) else []
    latest_status = _text(runs[0].get("status") if runs and isinstance(runs[0], dict) else "unknown")
    latest_dashboard = _latest_dashboard_href(runs)
    rows = "".join(_run_row(_safe_dict(run)) for run in runs)
    if not rows:
        rows = "<tr><td colspan='11'>No daily runs found.</td></tr>"
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Daily Runs</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --text: #17202a;
      --muted: #667085;
      --line: #d8dde6;
      --strong: #0f7b5f;
      --weak: #8a5a00;
      --risk: #b42318;
      --watch: #1d5fd1;
    }}
    body {{ margin: 0; background: var(--bg); color: var(--text); font: 14px/1.55 "Segoe UI", Arial, sans-serif; }}
    header {{ padding: 22px 28px; background: #101828; color: white; }}
    header h1 {{ margin: 0; font-size: 22px; letter-spacing: 0; }}
    header p {{ margin: 6px 0 0; color: #cbd5e1; }}
    main {{ padding: 22px 28px 36px; max-width: 1440px; margin: 0 auto; }}
    .grid {{ display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); margin-bottom: 18px; }}
    .card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 14px; box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04); }}
    .card h2 {{ margin: 0 0 8px; font-size: 15px; }}
    .muted {{ color: var(--muted); }}
    .pill {{ display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 12px; font-weight: 600; }}
    .ok, .pass {{ color: var(--strong); background: #e8f6f0; }}
    .partial, .unknown {{ color: var(--weak); background: #fff4d6; }}
    .failed, .error, .missing {{ color: var(--risk); background: #fee4e2; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }}
    th, td {{ padding: 9px 10px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ background: #eef2f6; font-size: 12px; color: #344054; }}
    tr:last-child td {{ border-bottom: 0; }}
    .num {{ text-align: right; white-space: nowrap; }}
    .links a {{ display: inline-block; margin-right: 8px; }}
{PAGE_NAV_CSS}
  </style>
</head>
<body>
  <header>
    <h1>Daily Runs</h1>
    <p>Generated at {html.escape(_text(data.get('generated_at') or 'unknown'))} &middot; Schema: {html.escape(_text(data.get('schema_version') or 'unknown'))}</p>
  </header>
  {_history_nav(latest_dashboard)}
  <main>
    <section class="grid">
      <div class="card"><h2>Runs</h2><p>{len(runs)}</p></div>
      <div class="card"><h2>Latest Status</h2><p><span class="pill {html.escape(latest_status)}">{html.escape(latest_status)}</span></p></div>
      <div class="card"><h2>Latest Run</h2><p>{_latest_run_link(latest_dashboard)}</p></div>
    </section>
    <section>
      <table>
        <thead><tr>
          <th>Date</th><th>Status</th><th>Generated At</th>
          <th class="num">Strong</th><th class="num">Confirmed</th><th class="num">Downgraded</th>
          <th class="num">Failed</th><th class="num">Missing Data</th><th class="num">Knowledge Issues</th>
          <th class="num">Warnings</th><th>Links</th>
        </tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""


def write_daily_history_index(reports_dir: str | Path) -> dict[str, Path]:
    root = Path(reports_dir)
    root.mkdir(parents=True, exist_ok=True)
    index_data = build_daily_history_index(root)
    index_json = root / "index.json"
    index_html = root / "index.html"
    write_text(index_json, json.dumps(index_data, ensure_ascii=False, indent=2))
    write_text(index_html, render_daily_history_index_html(index_data))
    return {"index_json": index_json, "index_html": index_html}


def _history_nav(latest_dashboard: str | None) -> str:
    items = (
        ("daily_runs", "Daily Runs", "index.html"),
        ("latest_run", "Latest Run", latest_dashboard),
    )
    return render_page_nav(items, current_key="daily_runs")


def _latest_dashboard_href(runs: list[Any]) -> str | None:
    if not runs or not isinstance(runs[0], dict):
        return None
    outputs = _safe_dict(runs[0].get("outputs"))
    value = outputs.get("dashboard_html")
    return str(value) if value else None


def _latest_run_link(latest_dashboard: str | None) -> str:
    if not latest_dashboard:
        return "<span class='muted'>unavailable</span>"
    return f"<a href='{html.escape(latest_dashboard, quote=True)}'>Open latest dashboard</a>"


def _date_dirs(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(
        (path for path in root.iterdir() if path.is_dir() and _DATE_DIR_RE.match(path.name)),
        key=lambda path: path.name,
    )


def _build_run_entry(run_dir: Path) -> dict[str, Any]:
    warnings: list[str] = []
    run_summary_path = run_dir / "run_summary.json"
    dashboard_data_path = run_dir / "dashboard_data.json"
    run_summary = _load_json_object(run_summary_path, warnings)
    dashboard_data = _load_json_object(dashboard_data_path, warnings)
    if not run_summary_path.exists():
        warnings.append("missing run_summary.json")
    if not dashboard_data_path.exists():
        warnings.append("missing dashboard_data.json")

    dashboard_run = _safe_dict(dashboard_data.get("run"))
    status = _run_status(run_summary, dashboard_run, run_summary_path.exists(), dashboard_data_path.exists())
    summary = _summary(dashboard_data.get("summary"))
    warnings.extend(_as_text_list(run_summary.get("warnings")))
    warnings.extend(_as_text_list(dashboard_run.get("warnings")))

    return {
        "date": run_dir.name,
        "status": status,
        "generated_at": run_summary.get("generated_at") or dashboard_run.get("generated_at"),
        "summary": summary,
        "warnings": _dedupe(warnings),
        "outputs": _outputs(run_dir),
    }


def _run_status(
    run_summary: dict[str, Any],
    dashboard_run: dict[str, Any],
    has_run_summary: bool,
    has_dashboard_data: bool,
) -> str:
    if not has_run_summary and not has_dashboard_data:
        return "missing"
    status = str(run_summary.get("status") or dashboard_run.get("status") or "unknown")
    if status == "ok" and (not has_run_summary or not has_dashboard_data):
        return "partial"
    return status


def _summary(value: Any) -> dict[str, int]:
    source = _safe_dict(value)
    return {
        "strong_signals": _as_int(source.get("strong_signals")),
        "confirmed": _as_int(source.get("confirmed")),
        "downgraded": _as_int(source.get("downgraded")),
        "failed": _as_int(source.get("failed")),
        "missing_data": _as_int(source.get("missing_data")),
        "knowledge_issues": _as_int(source.get("knowledge_issues")),
    }


def _outputs(run_dir: Path) -> dict[str, str | None]:
    date_prefix = run_dir.name
    files = {
        "dashboard_html": run_dir / "dashboard.html",
        "knowledge_review_html": run_dir / "knowledge_review.html",
        "run_diagnostics_html": run_dir / "run_diagnostics.html",
        "dashboard_data_json": run_dir / "dashboard_data.json",
        "run_summary_json": run_dir / "run_summary.json",
        "report_md": run_dir / "report.md",
    }
    return {
        key: f"{date_prefix}/{path.name}" if path.exists() else None
        for key, path in files.items()
    }


def _run_row(run: dict[str, Any]) -> str:
    summary = _safe_dict(run.get("summary"))
    warnings = run.get("warnings") if isinstance(run.get("warnings"), list) else []
    return f"""<tr>
  <td>{html.escape(_text(run.get('date') or 'unknown'))}</td>
  <td><span class="pill {html.escape(_text(run.get('status') or 'unknown'))}">{html.escape(_text(run.get('status') or 'unknown'))}</span></td>
  <td>{html.escape(_text(run.get('generated_at') or 'unknown'))}</td>
  <td class="num">{_as_int(summary.get('strong_signals'))}</td>
  <td class="num">{_as_int(summary.get('confirmed'))}</td>
  <td class="num">{_as_int(summary.get('downgraded'))}</td>
  <td class="num">{_as_int(summary.get('failed'))}</td>
  <td class="num">{_as_int(summary.get('missing_data'))}</td>
  <td class="num">{_as_int(summary.get('knowledge_issues'))}</td>
  <td class="num">{len(warnings)}</td>
  <td class="links">{_links(_safe_dict(run.get('outputs')))}</td>
</tr>"""


def _links(outputs: dict[str, Any]) -> str:
    labels = (
        ("dashboard_html", "Dashboard"),
        ("knowledge_review_html", "Knowledge Review"),
        ("run_diagnostics_html", "Run Diagnostics"),
        ("dashboard_data_json", "dashboard_data.json"),
        ("run_summary_json", "run_summary.json"),
        ("report_md", "report.md"),
    )
    links = []
    for key, label in labels:
        target = outputs.get(key)
        if target:
            links.append(f"<a href='{html.escape(str(target), quote=True)}'>{html.escape(label)}</a>")
        else:
            links.append(f"<span class='muted'>{html.escape(label)} missing</span>")
    return " ".join(links)


def _load_json_object(path: Path, warnings: list[str]) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        warnings.append(f"{path.name} unreadable: {exc}")
        return {}
    return payload if isinstance(payload, dict) else {}


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_text_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if item not in (None, "")]
    return []


def _dedupe(values: list[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _as_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _text(value: Any) -> str:
    if value is None:
        return "unknown"
    return str(value)


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
