from __future__ import annotations

import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .html_components import PAGE_NAV_CSS, render_page_nav
from .io import write_text


def render_knowledge_review_html(
    knowledge_check: dict[str, Any] | None,
    suggestions: dict[str, Any] | list[Any] | None = None,
    nav_links: dict[str, str | None] | None = None,
) -> str:
    check = _safe_dict(knowledge_check)
    status = _status(check)
    issues = [_safe_dict(item) for item in _as_list(check.get("issues"))]
    suggestion_rows = _suggestions(suggestions, check)
    counts = _severity_counts(check, issues)
    generated_at = _first_text(
        check.get("generated_at"),
        check.get("verified_at"),
        check.get("fetched_at"),
        _safe_dict(check.get("source_summary")).get("generated_at"),
        _safe_dict(check.get("source_summary")).get("fetched_at"),
        _now_iso(),
    )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Knowledge Graph Review</title>
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
    .ok, .clean, .low {{ color: var(--strong); background: #e8f6f0; }}
    .skipped, .not_available, .unknown {{ color: var(--watch); background: #eaf1ff; }}
    .partial, .medium {{ color: var(--weak); background: #fff4d6; }}
    .failed, .error, .high, .issues {{ color: var(--risk); background: #fee4e2; }}
    table {{ width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }}
    th, td {{ padding: 9px 10px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; }}
    th {{ background: #eef2f6; font-size: 12px; color: #344054; }}
    tr:last-child td {{ border-bottom: 0; }}
    .num {{ text-align: right; white-space: nowrap; }}
{PAGE_NAV_CSS}
  </style>
</head>
<body>
  <header>
    <h1>Knowledge Graph Review</h1>
    <p>Generated at {html.escape(generated_at)}</p>
  </header>
  {_knowledge_nav(nav_links)}
  <main>
    {_overview_html(status, counts, generated_at)}
    {_state_html(status, counts)}
    {_issues_html(issues)}
    {_suggestions_html(suggestion_rows)}
  </main>
</body>
</html>
"""


def write_knowledge_review_html(
    output_dir: str | Path,
    knowledge_check: dict[str, Any] | None,
    suggestions: dict[str, Any] | list[Any] | None = None,
) -> Path:
    root = Path(output_dir)
    path = Path(output_dir) / "knowledge_review.html"
    write_text(path, render_knowledge_review_html(knowledge_check, suggestions, _nav_links(root)))
    return path


def _knowledge_nav(nav_links: dict[str, str | None] | None = None) -> str:
    links = nav_links or {}
    items = (
        ("daily_runs", "Back to Daily Runs", "../index.html"),
        ("dashboard", "Dashboard", "dashboard.html"),
        ("knowledge_review", "Knowledge Review", "knowledge_review.html"),
        ("run_diagnostics", "Run Diagnostics", "run_diagnostics.html"),
        ("knowledge_check", "knowledge_check.json", links.get("knowledge_check_json")),
        ("knowledge_fix_suggestions", "knowledge_fix_suggestions.json", links.get("knowledge_fix_suggestions_json")),
    )
    return render_page_nav(items, current_key="knowledge_review")


def _nav_links(output_dir: Path) -> dict[str, str | None]:
    return {
        "knowledge_check_json": "knowledge_check.json" if (output_dir / "knowledge_check.json").exists() else None,
        "knowledge_fix_suggestions_json": (
            "knowledge_fix_suggestions.json" if (output_dir / "knowledge_fix_suggestions.json").exists() else None
        ),
    }


def _overview_html(status: str, counts: dict[str, int], generated_at: str) -> str:
    return f"""<section>
  <h2>Review Overview</h2>
  <div class="grid">
    <div class="card"><h3>Status</h3><p><span class="pill {html.escape(status)}">{html.escape(status)}</span></p></div>
    <div class="card"><h3>High Issues</h3><p>{counts["high"]}</p></div>
    <div class="card"><h3>Medium Issues</h3><p>{counts["medium"]}</p></div>
    <div class="card"><h3>Low Issues</h3><p>{counts["low"]}</p></div>
    <div class="card"><h3>Total Issues</h3><p>{counts["total"]}</p></div>
    <div class="card"><h3>Timestamp</h3><p>{html.escape(generated_at)}</p></div>
  </div>
</section>"""


def _state_html(status: str, counts: dict[str, int]) -> str:
    if status == "skipped":
        return """<section><div class="card"><h2>Skipped</h2><p>Knowledge verification was skipped for this daily run.</p></div></section>"""
    if status == "not_available":
        return """<section><div class="card"><h2>Not Available</h2><p>Knowledge check data is not available for this daily run.</p></div></section>"""
    if counts["total"] == 0:
        return """<section><div class="card"><h2>Clean</h2><p>Knowledge graph is clean.</p></div></section>"""
    return ""


def _issues_html(issues: list[dict[str, Any]]) -> str:
    sections = []
    for severity in ("high", "medium", "low"):
        grouped = [issue for issue in issues if _severity(issue) == severity]
        rows = "".join(_issue_row(issue) for issue in grouped)
        if not rows:
            rows = "<tr><td colspan='9'>No issues in this severity group.</td></tr>"
        sections.append(
            f"""<section>
  <h2>{html.escape(severity.title())} Issues</h2>
  <table><thead><tr><th>Severity</th><th>Category</th><th>Theme</th><th>Asset</th><th>Ticker / Code</th><th>Message</th><th>Path</th><th>Suggestion</th><th>Source</th></tr></thead><tbody>{rows}</tbody></table>
</section>"""
        )
    unknown = [issue for issue in issues if _severity(issue) not in {"high", "medium", "low"}]
    if unknown:
        rows = "".join(_issue_row(issue) for issue in unknown)
        sections.append(
            f"""<section>
  <h2>Unknown Severity Issues</h2>
  <table><thead><tr><th>Severity</th><th>Category</th><th>Theme</th><th>Asset</th><th>Ticker / Code</th><th>Message</th><th>Path</th><th>Suggestion</th><th>Source</th></tr></thead><tbody>{rows}</tbody></table>
</section>"""
        )
    return "".join(sections)


def _issue_row(issue: dict[str, Any]) -> str:
    category = _first_text(issue.get("category"), issue.get("type"), issue.get("kind"))
    ticker = _first_text(issue.get("ticker"), issue.get("code"), issue.get("symbol"))
    return (
        "<tr>"
        f"<td>{_cell(_severity(issue))}</td>"
        f"<td>{_cell(category)}</td>"
        f"<td>{_cell(issue.get('theme'))}</td>"
        f"<td>{_cell(issue.get('asset'))}</td>"
        f"<td>{_cell(ticker)}</td>"
        f"<td>{_cell(issue.get('message'))}</td>"
        f"<td>{_cell(issue.get('path'))}</td>"
        f"<td>{_cell(issue.get('suggestion'))}</td>"
        f"<td>{_cell(issue.get('source'))}</td>"
        "</tr>"
    )


def _suggestions_html(suggestions: list[dict[str, Any]]) -> str:
    rows = "".join(_suggestion_row(item) for item in suggestions)
    if not rows:
        rows = "<tr><td colspan='7'>No fix suggestions available.</td></tr>"
    return f"""<section>
  <h2>Fix Suggestions</h2>
  <table><thead><tr><th>Target</th><th>Action</th><th>Reason</th><th>Suggested Value</th><th>Confidence</th><th>Source</th><th>Warning</th></tr></thead><tbody>{rows}</tbody></table>
</section>"""


def _suggestion_row(item: dict[str, Any]) -> str:
    action = _first_text(item.get("action"), item.get("kind"), item.get("type"))
    return (
        "<tr>"
        f"<td>{_cell(item.get('target'))}</td>"
        f"<td>{_cell(action)}</td>"
        f"<td>{_cell(item.get('reason'))}</td>"
        f"<td>{_cell(item.get('suggested_value'))}</td>"
        f"<td>{_cell(item.get('confidence'))}</td>"
        f"<td>{_cell(item.get('source'))}</td>"
        f"<td>{_cell(item.get('warning'))}</td>"
        "</tr>"
    )


def _status(check: dict[str, Any]) -> str:
    if not check:
        return "not_available"
    explicit = str(check.get("status") or "").strip()
    if explicit:
        return explicit
    counts = _severity_counts(check, [_safe_dict(item) for item in _as_list(check.get("issues"))])
    return "clean" if counts["total"] == 0 else "issues"


def _severity_counts(check: dict[str, Any], issues: list[dict[str, Any]]) -> dict[str, int]:
    provided = _safe_dict(check.get("quality_counts"))
    if provided:
        high = _as_int(provided.get("high"))
        medium = _as_int(provided.get("medium"))
        low = _as_int(provided.get("low"))
        total = _as_int(provided.get("total"))
        return {"high": high, "medium": medium, "low": low, "total": total if total else high + medium + low}
    high = sum(1 for issue in issues if _severity(issue) == "high")
    medium = sum(1 for issue in issues if _severity(issue) == "medium")
    low = sum(1 for issue in issues if _severity(issue) == "low")
    return {"high": high, "medium": medium, "low": low, "total": len(issues)}


def _suggestions(value: dict[str, Any] | list[Any] | None, check: dict[str, Any]) -> list[dict[str, Any]]:
    source: Any = value
    if source is None:
        source = check.get("suggestions")
    if isinstance(source, dict) and isinstance(source.get("suggestions"), list):
        source = source["suggestions"]
    if isinstance(source, list):
        return [_safe_dict(item) for item in source]
    if isinstance(source, dict):
        return [source]
    return []


def _severity(issue: dict[str, Any]) -> str:
    return str(issue.get("severity") or "unknown").lower()


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


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()
