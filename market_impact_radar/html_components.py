from __future__ import annotations

import html
from typing import Any, Iterable


PAGE_NAV_CSS = """
    .page-nav { padding: 10px 28px; background: #ffffff; border-bottom: 1px solid var(--line); display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }
    .page-nav-title { color: var(--muted); font-size: 12px; font-weight: 700; margin-right: 4px; text-transform: uppercase; }
    .page-nav a, .page-nav span { border: 1px solid var(--line); border-radius: 999px; padding: 5px 10px; text-decoration: none; color: var(--text); background: #ffffff; }
    .page-nav a.active, .page-nav span.active { border-color: var(--watch); color: var(--watch); background: #eaf1ff; font-weight: 700; }
    .page-nav span.muted { color: var(--muted); background: #f8fafc; }
"""

NavItem = tuple[str, str, str | None]


def html_escape(value: Any) -> str:
    if value is None:
        return "unknown"
    return html.escape(str(value))


def relative_output_href(value: Any) -> str | None:
    if value in (None, ""):
        return None
    text = str(value).replace("\\", "/")
    if "://" in text:
        return text
    if "/" in text:
        return text.rstrip("/").split("/")[-1]
    return text


def render_output_link(label: str, href: str | None, *, current: bool = False) -> str:
    label_html = html_escape(label)
    if not href:
        return f"<span class='muted'>{label_html} unavailable</span>"
    active = " class='active'" if current else ""
    aria = " aria-current='page'" if current else ""
    return f"<a href='{html.escape(str(href), quote=True)}'{active}{aria}>{label_html}</a>"


def render_page_nav(
    items: Iterable[NavItem],
    *,
    current_key: str | None = None,
    title: str = "Daily Report",
) -> str:
    rendered = []
    for key, label, href in items:
        rendered.append(render_output_link(label, href, current=key == current_key))
    return (
        "<nav class='page-nav' aria-label='Daily report navigation'>"
        f"<span class='page-nav-title'>{html_escape(title)}</span>"
        f"{''.join(rendered)}"
        "</nav>"
    )
