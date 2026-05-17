from __future__ import annotations

from dataclasses import dataclass
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
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
    pages_checked: int = 1


def run_daily_bundle_browser_smoke(
    preview_dir: str | Path,
    playwright_factory: Callable[[], Any] | None = None,
) -> BrowserSmokeResult:
    root = Path(preview_dir)
    pages = (
        _PageCheck(
            label="index.html",
            path=root / "index.html",
            required_text=("Daily Runs", "2026-05-15", "Dashboard", "Knowledge Review", "Run Diagnostics"),
        ),
        _PageCheck(
            label="dashboard.html",
            path=root / "2026-05-15" / "dashboard.html",
            required_text=("Back to Daily Runs", "knowledge_review.html", "run_diagnostics.html"),
            any_text=(("Schema: 1.0", "schema version"), ("Daily Market Radar", "Status"), ("Signal Overview", "Signal List", "summary")),
            selectors=("#signal-search",),
        ),
        _PageCheck(
            label="knowledge_review.html",
            path=root / "2026-05-15" / "knowledge_review.html",
            required_text=("Knowledge Graph Review", "Dashboard", "Run Diagnostics"),
            any_text=(("clean", "skipped", "issues", "not available", "not_available"),),
        ),
        _PageCheck(
            label="run_diagnostics.html",
            path=root / "2026-05-15" / "run_diagnostics.html",
            required_text=("Run Diagnostics", "Dashboard", "Knowledge Review", "Pipeline Steps", "Outputs"),
            any_text=(("Warnings / Errors", "No warnings or errors"),),
        ),
    )
    for page_check in pages:
        _check_static_file(page_check.path, page_check.label)
    factory = playwright_factory or _load_playwright()
    console_errors: list[str] = []
    page_errors: list[str] = []
    checked: list[str] = []

    try:
        with factory() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                for page_check in pages:
                    page = browser.new_page()
                    page.on("console", lambda message, label=page_check.label: _record_console_error(message, console_errors, label))
                    page.on("pageerror", lambda error, label=page_check.label: page_errors.append(f"{label}: {error}"))
                    page.goto(page_check.path.resolve().as_uri(), wait_until="domcontentloaded")
                    body_text = page.locator("body").inner_text(timeout=5000).strip()
                    title = page.title()
                    _assert_page_text(page_check, body_text, title)
                    _assert_selectors(page_check, page)
                    checked.append(page_check.label)
            finally:
                browser.close()
    except BrowserSmokeError:
        raise
    except Exception as exc:
        raise BrowserSmokeError(f"browser bundle smoke failed: {exc}. {PLAYWRIGHT_INSTALL_HINT}") from exc

    if console_errors:
        raise BrowserSmokeError(f"browser console errors: {'; '.join(console_errors)}")
    if page_errors:
        raise BrowserSmokeError(f"browser page errors: {'; '.join(page_errors)}")

    return BrowserSmokeResult(
        status="passed",
        url=root.resolve().as_uri(),
        checks=tuple(checked),
        pages_checked=len(checked),
    )


def run_dashboard_browser_smoke(
    html_path: str | Path,
    playwright_factory: Callable[[], Any] | None = None,
) -> BrowserSmokeResult:
    target = Path(html_path)
    _check_static_file(target, "dashboard.html")

    factory = playwright_factory or _load_playwright()
    url = target.resolve().as_uri()
    console_errors: list[str] = []
    page_errors: list[str] = []

    try:
        with factory() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                page = browser.new_page()
                page.on("console", lambda message: _record_console_error(message, console_errors, "dashboard.html"))
                page.on("pageerror", lambda error: page_errors.append(f"dashboard.html: {error}"))
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


def run_console_browser_smoke(
    reports_dir: str | Path,
    date: str = "2026-05-15",
    playwright_factory: Callable[[], Any] | None = None,
) -> BrowserSmokeResult:
    root = Path(reports_dir)
    run_dir = root / date
    if not run_dir.exists():
        raise BrowserSmokeError(f"console smoke run directory does not exist: {run_dir}")
    if not (run_dir / "dashboard_data.json").exists():
        raise BrowserSmokeError(f"console smoke missing dashboard_data.json: {run_dir / 'dashboard_data.json'}")

    factory = playwright_factory or _load_playwright()
    console_errors: list[str] = []
    page_errors: list[str] = []

    from .web_api import make_handler

    server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(root))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}/console"
    try:
        try:
            with factory() as playwright:
                browser = playwright.chromium.launch(headless=True)
                try:
                    page = browser.new_page()
                    page.on("console", lambda message: _record_console_error(message, console_errors, "console"))
                    page.on("pageerror", lambda error: page_errors.append(f"console: {error}"))
                    page.goto(url, wait_until="networkidle")
                    body_text = page.locator("body").inner_text(timeout=5000).strip()
                    title = page.title()
                finally:
                    browser.close()
        except BrowserSmokeError:
            raise
        except Exception as exc:
            raise BrowserSmokeError(f"console browser smoke failed: {exc}. {PLAYWRIGHT_INSTALL_HINT}") from exc
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)

    _assert_console_text(body_text, title, date)
    if console_errors:
        raise BrowserSmokeError(f"console browser console errors: {'; '.join(console_errors)}")
    if page_errors:
        raise BrowserSmokeError(f"console browser page errors: {'; '.join(page_errors)}")

    return BrowserSmokeResult(
        status="passed",
        url=url,
        checks=(
            "console_loaded",
            "runs_visible",
            "dashboard_data_visible",
            "artifacts_visible",
            "no_console_errors",
        ),
        pages_checked=1,
    )


def _load_playwright() -> Callable[[], Any]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise BrowserSmokeError(PLAYWRIGHT_INSTALL_HINT) from exc
    return sync_playwright


@dataclass(frozen=True)
class _PageCheck:
    label: str
    path: Path
    required_text: tuple[str, ...] = ()
    any_text: tuple[tuple[str, ...], ...] = ()
    selectors: tuple[str, ...] = ()


def _check_static_file(path: Path, label: str) -> None:
    if not path.exists():
        raise BrowserSmokeError(f"{label} does not exist: {path}")
    if not path.read_text(encoding="utf-8").strip():
        raise BrowserSmokeError(f"{label} is empty")


def _assert_page_text(page: _PageCheck, body_text: str, title: str) -> None:
    if not body_text:
        raise BrowserSmokeError(f"{page.label} body is empty")
    visible_text = f"{body_text}\n{title}"
    for text in page.required_text:
        if text not in visible_text:
            raise BrowserSmokeError(f"{page.label} missing required text: {text}")
    for group in page.any_text:
        if not any(text in visible_text or text.lower() in visible_text.lower() for text in group):
            raise BrowserSmokeError(f"{page.label} missing one of: {', '.join(group)}")


def _assert_selectors(page: _PageCheck, browser_page: Any) -> None:
    for selector in page.selectors:
        try:
            count = browser_page.locator(selector).count()
        except Exception as exc:
            raise BrowserSmokeError(f"{page.label} selector check failed for {selector}: {exc}") from exc
        if count < 1:
            raise BrowserSmokeError(f"{page.label} missing selector: {selector}")


def _record_console_error(message: Any, errors: list[str], label: str = "page") -> None:
    if getattr(message, "type", "") == "error":
        errors.append(f"{label}: {getattr(message, 'text', '')}")


def _assert_console_text(body_text: str, title: str, date: str) -> None:
    if not body_text:
        raise BrowserSmokeError("console body is empty")
    visible_text = f"{body_text}\n{title}"
    required = (
        "Market Impact Radar Console",
        "Daily Runs",
        "Dashboard Data",
        date,
        "Artifacts",
        "Dashboard",
        "Knowledge Review",
        "Run Diagnostics",
    )
    for text in required:
        if text not in visible_text:
            raise BrowserSmokeError(f"console missing required text: {text}")
