from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


PLAYWRIGHT_INSTALL_HINT = (
    "Playwright is required for --with-browser. "
    "Install with: pip install playwright; python -m playwright install chromium"
)


class BrowserSmokeError(RuntimeError):
    pass


@dataclass(frozen=True)
class BrowserSmokeResult:
    status: str
    url: str
    checks: tuple[str, ...]


def run_dashboard_browser_smoke(
    html_path: str | Path,
    playwright_factory: Callable[[], Any] | None = None,
) -> BrowserSmokeResult:
    target = Path(html_path)
    if not target.exists():
        raise BrowserSmokeError(f"dashboard.html does not exist: {target}")
    if not target.read_text(encoding="utf-8").strip():
        raise BrowserSmokeError("dashboard.html is empty")

    factory = playwright_factory or _load_playwright()
    url = target.resolve().as_uri()
    console_errors: list[str] = []
    page_errors: list[str] = []

    try:
        with factory() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.on("console", lambda message: _record_console_error(message, console_errors))
                page.on("pageerror", lambda error: page_errors.append(str(error)))
                page.goto(url, wait_until="domcontentloaded")
                body_text = page.locator("body").inner_text(timeout=5000).strip()
                title = page.title()
            finally:
                browser.close()
    except BrowserSmokeError:
        raise
    except Exception as exc:
        raise BrowserSmokeError(f"browser smoke failed: {exc}. {PLAYWRIGHT_INSTALL_HINT}") from exc

    if not body_text:
        raise BrowserSmokeError("dashboard body is empty")
    if "Schema: 1.0" not in body_text and "schema version" not in body_text.lower():
        raise BrowserSmokeError("dashboard is missing schema version text")
    if "Daily Market Radar" not in body_text and "Status" not in body_text and "Daily Market Radar" not in title:
        raise BrowserSmokeError("dashboard is missing core title or status text")
    if "Signal Overview" not in body_text and "Signal List" not in body_text and "summary" not in body_text.lower():
        raise BrowserSmokeError("dashboard is missing summary or signal area")
    if console_errors:
        raise BrowserSmokeError(f"dashboard console errors: {'; '.join(console_errors)}")
    if page_errors:
        raise BrowserSmokeError(f"dashboard page errors: {'; '.join(page_errors)}")

    return BrowserSmokeResult(
        status="passed",
        url=url,
        checks=(
            "file_exists",
            "body_non_empty",
            "schema_version_visible",
            "title_or_status_visible",
            "summary_or_signal_visible",
            "no_console_errors",
        ),
    )


def _load_playwright() -> Callable[[], Any]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise BrowserSmokeError(PLAYWRIGHT_INSTALL_HINT) from exc
    return sync_playwright


def _record_console_error(message: Any, errors: list[str]) -> None:
    if getattr(message, "type", "") == "error":
        errors.append(str(getattr(message, "text", "")))
