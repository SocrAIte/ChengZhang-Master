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
    query_checks = (
        ("default", "", {}),
        ("search", "?search=nvidia", {"#signal-search": "nvidia"}),
        ("grouped", "?view=grouped", {"#view-mode": "grouped"}),
        ("flat", "?view=flat", {"#view-mode": "flat"}),
        ("sort", "?sort=score_desc", {"#sort-select": "score_desc"}),
        ("filters", "?risk=high&status=confirmed", {"#risk-filter": "high", "#status-filter": "confirmed"}),
        ("theme", "?theme=Unknown%20Theme", {}),
        ("compare", "?compare=Unknown%20Theme", {}),
        ("theme_compare", "?theme=Unknown%20Theme&compare=Unknown%20Theme&view=grouped", {"#view-mode": "grouped"}),
        ("source", "?source=Unknown%20Source", {}),
        ("source_theme_compare", "?source=Unknown%20Source&theme=Unknown%20Theme&compare=Unknown%20Theme", {}),
        ("matrix", "?matrixTheme=Unknown%20Theme&matrixSource=Unknown%20Source", {}),
        ("matrix_hash", "#theme-source-matrix", {}),
        ("source_hash_state", "?theme=Unknown%20Theme&source=Unknown%20Source#source-detail", {}),
        ("research_brief_hash", "#daily-research-brief", {}),
        ("research_brief_state", "?theme=Unknown%20Theme&source=Unknown%20Source#daily-research-brief", {}),
        ("research_brief_options", "?briefLang=zh&briefMode=compact#daily-research-brief", {"#brief-language-select": "zh", "#brief-mode-select": "compact"}),
        ("review_queue_hash", "#research-review-queue", {}),
        ("review_queue_state", "?reviewSeverity=high&reviewCategory=weak_evidence&reviewScope=all#research-review-queue", {"#review-severity-filter": "high", "#review-category-filter": "weak_evidence", "#review-scope-select": "all"}),
        ("research_notes_hash", "#research-notes-composer", {}),
        ("research_notes_state", "?notesLang=zh&notesMode=compact#research-notes-composer", {"#notes-language-select": "zh", "#notes-mode-select": "compact"}),
        ("research_export_hash", "#research-export-package", {}),
        ("research_export_state", "?exportLang=zh&exportFormat=json#research-export-package", {"#export-language-select": "zh", "#export-format-select": "json"}),
        ("english_ui_state", "?uiLang=en#console-usage-guide", {}),
        ("usage_guide_hash", "#console-usage-guide", {}),
        ("date_compare_hash", "#date-compare", {}),
        ("date_compare_state", "?compareFrom=2026-05-14&compareTo=2026-05-15#date-compare", {"#compare-from-select": "2026-05-14", "#compare-to-select": "2026-05-15"}),
    )
    checked_pages = 0
    try:
        try:
            with factory() as playwright:
                browser = playwright.chromium.launch(headless=True)
                try:
                    body_text = ""
                    title = ""
                    for label, query, expected_values in query_checks:
                        page = browser.new_page()
                        page.on("console", lambda message, label=label: _record_console_error(message, console_errors, f"console {label}"))
                        page.on("pageerror", lambda error, label=label: page_errors.append(f"console {label}: {error}"))
                        page.goto(f"{url}{query}", wait_until="networkidle")
                        page_body = page.locator("body").inner_text(timeout=5000).strip()
                        page_title = page.title()
                        _assert_console_controls(page)
                        _assert_console_query_state(page, expected_values)
                        if label == "default":
                            _assert_console_text(page_body, page_title, date)
                        elif not page_body:
                            raise BrowserSmokeError(f"console {label} body is empty")
                        checked_pages += 1
                        if label == "default":
                            body_text = page_body
                            title = page_title
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
            "url_query_state_visible",
            "no_console_errors",
        ),
        pages_checked=checked_pages,
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
        "跨市场热点研究控制台",
        "工作台导航",
        "English",
        "使用引导",
        "先看今日摘要",
        "返回顶部",
        "每日研究摘要",
        "研究复核清单",
        "研究笔记工作区",
        "笔记语言",
        "笔记模式",
        "人工补充笔记",
        "人工补充笔记仅保留在当前浏览器页面中",
        "研究包导出",
        "导出内容",
        "导出预览",
        "下载 Markdown",
        "下载纯文本",
        "下载 JSON 元信息",
        "复核清单摘要",
        "严重程度",
        "复核类型",
        "范围",
        "日期对比",
        "对比起始日期",
        "对比目标日期",
        "日期对比摘要",
        "摘要语言",
        "中文",
        "复制 Markdown",
        "复制纯文本",
        "摘要模式",
        "包含小节",
        "Daily 运行记录",
        "Dashboard 数据",
        date,
        "运行日期",
        "刷新运行记录",
        "搜索信号",
        "风险筛选",
        "状态筛选",
        "信号排序",
        "按主题分组",
        "平铺信号列表",
        "主题热榜",
        "今日观察摘要",
        "数据来源可靠性",
        "来源详情",
        "来源汇总",
        "弱证据信号",
        "历史数据质量趋势",
        "主题 × 来源矩阵",
        "矩阵摘要",
        "单元格详情",
        "需要复核的主题-来源组合",
        "主题对比",
        "候选池对比",
        "主题详情",
        "信号详情",
        "证据链",
        "数据质量",
        "ETF 观察池",
        "个股观察池",
        "产物链接",
        "历史复盘",
        "API:",
        "API 版本:",
        "Dashboard 页面",
        "知识图谱复核",
        "运行诊断",
    )
    for text in required:
        if text not in visible_text:
            raise BrowserSmokeError(f"console missing required text: {text}")


def _assert_console_controls(browser_page: Any) -> None:
    for selector in (
        "#run-select",
        "#ui-language-toggle",
        "#refresh-runs",
        "#signal-search",
        "#risk-filter",
        "#status-filter",
        "#sort-select",
        "#view-mode",
        "#compare-theme-select",
        "#brief-language-select",
        "#brief-mode-select",
        "#review-severity-filter",
        "#review-category-filter",
        "#review-scope-select",
        "#notes-language-select",
        "#notes-mode-select",
        "#manual-research-notes",
        "#export-language-select",
        "#export-format-select",
        "#export-preview",
        "#compare-from-select",
        "#compare-to-select",
    ):
        try:
            count = browser_page.locator(selector).count()
        except Exception as exc:
            raise BrowserSmokeError(f"console selector check failed for {selector}: {exc}") from exc
        if count < 1:
            raise BrowserSmokeError(f"console missing selector: {selector}")


def _assert_console_query_state(browser_page: Any, expected_values: dict[str, str]) -> None:
    for selector, expected in expected_values.items():
        try:
            actual = browser_page.locator(selector).input_value(timeout=5000)
        except TypeError:
            actual = browser_page.locator(selector).input_value()
        except Exception as exc:
            raise BrowserSmokeError(f"console query state check failed for {selector}: {exc}") from exc
        if actual != expected:
            raise BrowserSmokeError(f"console query state mismatch for {selector}: expected {expected}, got {actual}")
