from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from .html_components import PAGE_NAV_CSS, relative_output_href, render_page_nav
from .io import write_text


def render_run_diagnostics_html(run_summary: dict[str, Any] | None) -> str:
    summary = _safe_dict(run_summary)
    warnings = _as_list(summary.get("warnings"))
    errors = _as_list(summary.get("errors"))
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Run Diagnostics</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f6f7f9;
      --panel: #ffffff;
      --text: #17202a;
      --muted: #667085;
      --line: #d8dde6;
      --strong: #0f7b5f;
      --watch: #1d5fd1;
      --weak: #8a5a00;
      --risk: #b42318;
    }}
    body {{ margin: 0; background: var(--bg); color: var(--text); font: 14px/1.55 "Segoe UI", Arial, sans-serif; }}
    header {{ padding: 22px 28px; background: #101828; color: white; }}
    header h1 {{ margin: 0; font-size: 22px; letter-spacing: 0; }}
    header p {{ margin: 6px 0 0; color: #cbd5e1; }}
    main {{ padding: 22px 28px 36px; max-width: 1440px; margin: 0 auto; }}
    section {{ margin-bottom: 22px; }}
    h2 {{ font-size: 17px; margin: 0 0 12px; }}
    h3 {{ font-size: 15px; margin: 0 0 8px; }}
    .grid {{ display: grid; gap: 12px; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }}
    .card {{ background: var(--panel); border: 1px solid var(--line); border-radius: 8px; padding: 14px; box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04); }}
    .muted {{ color: var(--muted); }}
    .pill {{ display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 12px; font-weight: 600; }}
    .ok, .pass {{ color: var(--strong); background: #e8f6f0; }}
    .skipped, .unknown {{ color: var(--watch); background: #eaf1ff; }}
    .partial {{ color: var(--weak); background: #fff4d6; }}
    .failed, .error, .missing {{ color: var(--risk); background: #fee4e2; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }}
    th, td {{ padding: 9px 10px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ background: #eef2f6; font-size: 12px; color: #344054; }}
    tr:last-child td {{ border-bottom: 0; }}
    .num {{ text-align: right; white-space: nowrap; }}
    .note-list {{ margin: 8px 0 0 18px; padding: 0; }}
    .links a {{ display: inline-block; margin-right: 8px; }}
{PAGE_NAV_CSS}
  </style>
</head>
<body>
  <header>
    <h1>Run Diagnostics</h1>
    <p>{html.escape(_text(summary.get("run_date") or "unknown"))} &middot; status {html.escape(_text(summary.get("status") or "unknown"))}</p>
  </header>
  {_diagnostics_nav(summary)}
  <main>
    {_run_summary_html(summary, warnings)}
    {_steps_html(summary)}
    {_data_source_health_html(summary)}
    {_warnings_errors_html(summary, warnings, errors)}
    {_outputs_html(summary)}
  </main>
</body>
</html>
"""


def write_run_diagnostics_html(
    output_dir: str | Path,
    run_summary: dict[str, Any] | None = None,
    run_summary_path: str | Path | None = None,
) -> Path:
    payload = run_summary if isinstance(run_summary, dict) else _load_summary(run_summary_path)
    path = Path(output_dir) / "run_diagnostics.html"
    write_text(path, render_run_diagnostics_html(payload))
    return path


def _diagnostics_nav(summary: dict[str, Any]) -> str:
    outputs = _safe_dict(summary.get("outputs"))
    report_href = relative_output_href(outputs.get("report_md"))
    items = (
        ("daily_runs", "Back to Daily Runs", "../index.html"),
        ("dashboard", "Dashboard", "dashboard.html"),
        ("knowledge_review", "Knowledge Review", "knowledge_review.html"),
        ("run_diagnostics", "Run Diagnostics", "run_diagnostics.html"),
        ("run_summary", "run_summary.json", "run_summary.json"),
        ("dashboard_data", "dashboard_data.json", "dashboard_data.json"),
        ("report", "report.md", report_href),
    )
    return render_page_nav(items, current_key="run_diagnostics")


def _run_summary_html(summary: dict[str, Any], warnings: list[Any]) -> str:
    status = _text(summary.get("status") or "unknown")
    return f"""<section>
  <h2>Run Summary</h2>
  <div class="grid">
    <div class="card"><h3>Date</h3><p>{_cell(summary.get("run_date"))}</p></div>
    <div class="card"><h3>Generated At</h3><p>{_cell(summary.get("generated_at"))}</p></div>
    <div class="card"><h3>Status</h3><p><span class="pill {html.escape(status)}">{html.escape(status)}</span></p></div>
    <div class="card"><h3>Output Dir</h3><p>{_cell(summary.get("output_dir"))}</p></div>
    <div class="card"><h3>Warnings Count</h3><p>{len(warnings)}</p></div>
  </div>
</section>"""


def _steps_html(summary: dict[str, Any]) -> str:
    steps = _safe_dict(summary.get("steps"))
    rows = "".join(_step_row(name, _safe_dict(step)) for name, step in steps.items())
    if not rows:
        rows = "<tr><td colspan='5'>No pipeline steps available.</td></tr>"
    return f"""<section>
  <h2>Pipeline Steps</h2>
  <table><thead><tr><th>Name</th><th>Status</th><th>Output</th><th>Warnings</th><th>Error</th></tr></thead><tbody>{rows}</tbody></table>
</section>"""


def _step_row(name: str, step: dict[str, Any]) -> str:
    status = _text(step.get("status") or "unknown")
    output = _first_text(step.get("output"), step.get("path"), step.get("output_path"))
    warnings = _join_text(_as_list(step.get("warnings")))
    errors = _join_text(_as_list(step.get("errors")) + _as_list(step.get("error")))
    return (
        "<tr>"
        f"<td>{_cell(name)}</td>"
        f"<td><span class='pill {html.escape(status)}'>{html.escape(status)}</span></td>"
        f"<td>{_cell(output)}</td>"
        f"<td>{_cell(warnings)}</td>"
        f"<td>{_cell(errors)}</td>"
        "</tr>"
    )


def _data_source_health_html(summary: dict[str, Any]) -> str:
    steps = _safe_dict(summary.get("steps"))
    external = _safe_dict(steps.get("external") or steps.get("foreign_quotes"))
    a_share = _safe_dict(steps.get("a_share") or steps.get("a_share_snapshot"))
    pipeline = _safe_dict(steps.get("pipeline") or steps.get("signals"))
    intraday = _safe_dict(steps.get("intraday") or steps.get("intraday_validation"))
    knowledge = _safe_dict(steps.get("knowledge"))
    return f"""<section>
  <h2>Data Source Health</h2>
  <table><thead><tr><th>Area</th><th>Status</th><th>Metric</th><th>Value</th></tr></thead><tbody>
    {_health_rows("foreign_quotes", external, (("count", _quote_count(external)), ("strong_signal_eligible_count", external.get("strong_signal_eligible_count", 0))))}
    {_health_rows("a_share_snapshot", a_share, (("source", _first_text(a_share.get("source"), _safe_dict(_safe_dict(a_share.get("quality")).get("source_summary")).get("source"), a_share.get("mode"))), ("fallback_used", a_share.get("fallback_used", "unknown"))))}
    {_health_rows("signals", pipeline, (("total", _first_text(pipeline.get("total"), pipeline.get("scored_themes"), pipeline.get("events"), 0)), ("strong", pipeline.get("strong", 0)), ("medium", pipeline.get("medium", 0)), ("weak", pipeline.get("weak", 0))))}
    {_health_rows("intraday_validation", intraday, _intraday_metrics(intraday))}
    {_health_rows("knowledge", knowledge, _knowledge_metrics(knowledge))}
  </tbody></table>
</section>"""


def _health_rows(area: str, payload: dict[str, Any], metrics: tuple[tuple[str, Any], ...]) -> str:
    status = _text(payload.get("status") or "unknown")
    return "".join(
        f"<tr><td>{html.escape(area)}</td><td><span class='pill {html.escape(status)}'>{html.escape(status)}</span></td><td>{_cell(label)}</td><td>{_cell(value)}</td></tr>"
        for label, value in metrics
    )


def _intraday_metrics(payload: dict[str, Any]) -> tuple[tuple[str, Any], ...]:
    summary = _safe_dict(payload.get("summary"))
    return (
        ("confirmed", _first_text(summary.get("confirmed"), summary.get("confirmed_count"), 0)),
        ("downgraded", _first_text(summary.get("downgraded"), summary.get("downgraded_count"), 0)),
        ("failed", _first_text(summary.get("failed"), summary.get("failed_count"), 0)),
        ("missing_data", _first_text(summary.get("missing_data"), summary.get("missing_count"), 0)),
    )


def _knowledge_metrics(payload: dict[str, Any]) -> tuple[tuple[str, Any], ...]:
    counts = _safe_dict(payload.get("quality_counts"))
    return (
        ("high", counts.get("high", 0)),
        ("medium", counts.get("medium", 0)),
        ("low", counts.get("low", 0)),
        ("total", counts.get("total", 0)),
    )


def _warnings_errors_html(summary: dict[str, Any], warnings: list[Any], errors: list[Any]) -> str:
    step_notes = []
    for name, step in _safe_dict(summary.get("steps")).items():
        row = _safe_dict(step)
        for item in _as_list(row.get("warnings")):
            step_notes.append(f"{name}: {item}")
        for item in _as_list(row.get("errors")) + _as_list(row.get("error")):
            step_notes.append(f"{name}: {item}")
    notes = warnings + errors + step_notes
    if not notes:
        body = "<p class='muted'>No warnings or errors.</p>"
    else:
        body = "<ul class='note-list'>" + "".join(f"<li>{_cell(item)}</li>" for item in notes) + "</ul>"
    return f"""<section>
  <h2>Warnings / Errors</h2>
  <div class="card">{body}</div>
</section>"""


def _outputs_html(summary: dict[str, Any]) -> str:
    outputs = _safe_dict(summary.get("outputs"))
    labels = (
        (("dashboard_html",), "dashboard.html"),
        (("dashboard_data", "dashboard_data_json"), "dashboard_data.json"),
        (("run_summary", "run_summary_json"), "run_summary.json"),
        (("run_diagnostics_html",), "run_diagnostics.html"),
        (("report_md",), "report.md"),
        (("knowledge_review_html",), "knowledge_review.html"),
        (("knowledge_check_json",), "knowledge_check.json"),
        (("knowledge_fix_suggestions_json",), "knowledge_fix_suggestions.json"),
        (("history_index_html",), "index.html"),
    )
    items = []
    for keys, label in labels:
        target = next((outputs.get(key) for key in keys if outputs.get(key)), None)
        items.append(f"<li><strong>{html.escape(label)}:</strong> {_path_link(target)}</li>")
    return f"""<section>
  <h2>Outputs</h2>
  <div class="card"><ul class="note-list">{''.join(items)}</ul></div>
</section>"""


def _quote_count(step: dict[str, Any]) -> Any:
    quality = _safe_dict(step.get("quality"))
    counts = _safe_dict(quality.get("quality_counts"))
    total = step.get("count") or quality.get("count") or counts.get("total")
    if total is not None:
        return total
    return sum(_as_int(value) for value in counts.values())


def _path_link(value: Any) -> str:
    if value in (None, ""):
        return "<span class='muted'>unavailable</span>"
    text = _text(value)
    escaped = html.escape(text)
    normalized = text.replace("\\", "/")
    href_target = normalized
    if "://" not in normalized and "/" in normalized:
        href_target = normalized.rstrip("/").split("/")[-1]
    href = html.escape(href_target, quote=True)
    return f"<a href='{href}'>{escaped}</a>"


def _load_summary(path: str | Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _as_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _first_text(*values: Any) -> str:
    for value in values:
        text = _text(value)
        if text != "unknown":
            return text
    return "unknown"


def _join_text(values: list[Any]) -> str:
    clean = [_text(value) for value in values if _text(value) != "unknown"]
    return "; ".join(clean) if clean else "unknown"


def _cell(value: Any) -> str:
    return html.escape(_text(value))


def _text(value: Any) -> str:
    if value in (None, ""):
        return "unknown"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)
