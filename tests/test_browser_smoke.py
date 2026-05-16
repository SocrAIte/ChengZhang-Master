from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from market_impact_radar.browser_smoke import BrowserSmokeError, run_daily_bundle_browser_smoke, run_dashboard_browser_smoke


class _FakeMessage:
    type = "log"
    text = ""


class _FakeLocator:
    def __init__(self, text: str, count: int = 1) -> None:
        self._text = text
        self._count = count

    def inner_text(self, timeout: int = 0) -> str:
        return self._text

    def count(self) -> int:
        return self._count


class _FakePage:
    def __init__(self, body_text: str, title: str = "Daily Market Radar", selector_counts: dict[str, int] | None = None) -> None:
        self._body_text = body_text
        self._title = title
        self._selector_counts = selector_counts or {}
        self.url = ""

    def on(self, event: str, callback) -> None:
        if event == "console":
            callback(_FakeMessage())

    def goto(self, url: str, wait_until: str = "") -> None:
        self.url = url

    def locator(self, selector: str) -> _FakeLocator:
        if selector == "body":
            return _FakeLocator(self._body_text)
        return _FakeLocator("", self._selector_counts.get(selector, 0))

    def title(self) -> str:
        return self._title


class _FakeBrowser:
    def __init__(self, page: _FakePage | list[_FakePage]) -> None:
        self._page = page

    def new_page(self) -> _FakePage:
        if isinstance(self._page, list):
            return self._page.pop(0)
        return self._page

    def close(self) -> None:
        return None


class _FakeChromium:
    def __init__(self, page: _FakePage | list[_FakePage]) -> None:
        self._page = page

    def launch(self, headless: bool = True) -> _FakeBrowser:
        return _FakeBrowser(self._page)


class _FakePlaywright:
    def __init__(self, page: _FakePage | list[_FakePage]) -> None:
        self.chromium = _FakeChromium(page)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


def _factory(body_text: str):
    return lambda: _FakePlaywright(_FakePage(body_text))


def _bundle_factory():
    pages = [
        _FakePage("Daily Runs 2026-05-15 dashboard.html knowledge_review.html run_diagnostics.html", "Daily Runs"),
        _FakePage(
            "Daily Market Radar Status Signal Overview Signal List Schema: 1.0 knowledge_review.html run_diagnostics.html",
            "Daily Market Radar",
            {"#signal-search": 1},
        ),
        _FakePage("Knowledge Graph Review skipped", "Knowledge Graph Review"),
        _FakePage("Run Diagnostics Pipeline Steps Outputs Warnings / Errors", "Run Diagnostics"),
    ]
    return lambda: _FakePlaywright(pages)


def _write_bundle(root: Path) -> None:
    run_dir = root / "2026-05-15"
    run_dir.mkdir(parents=True, exist_ok=True)
    (root / "index.html").write_text("<html>Daily Runs 2026-05-15 dashboard.html knowledge_review.html run_diagnostics.html</html>", encoding="utf-8")
    (run_dir / "dashboard.html").write_text(
        "<html>Daily Market Radar Status Signal Overview Schema: 1.0 knowledge_review.html run_diagnostics.html <input id='signal-search'></html>",
        encoding="utf-8",
    )
    (run_dir / "knowledge_review.html").write_text("<html>Knowledge Graph Review skipped</html>", encoding="utf-8")
    (run_dir / "run_diagnostics.html").write_text("<html>Run Diagnostics Pipeline Steps Outputs Warnings / Errors</html>", encoding="utf-8")


class BrowserSmokeTest(unittest.TestCase):
    def test_browser_smoke_happy_path_with_fake_browser(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "dashboard.html"
            path.write_text("<html><body>Daily Market Radar Status Signal List Schema: 1.0</body></html>", encoding="utf-8")

            result = run_dashboard_browser_smoke(
                path,
                playwright_factory=_factory("Daily Market Radar Status Signal List Schema: 1.0"),
            )

        self.assertEqual(result.status, "passed")
        self.assertIn("schema_version_visible", result.checks)

    def test_missing_dashboard_html_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaisesRegex(BrowserSmokeError, "does not exist"):
                run_dashboard_browser_smoke(Path(tmpdir) / "missing.html", playwright_factory=_factory(""))

    def test_empty_dashboard_html_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "dashboard.html"
            path.write_text("", encoding="utf-8")

            with self.assertRaisesRegex(BrowserSmokeError, "empty"):
                run_dashboard_browser_smoke(path, playwright_factory=_factory(""))

    def test_playwright_missing_message_is_clear(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "dashboard.html"
            path.write_text("<html><body>Daily Market Radar Status Signal List Schema: 1.0</body></html>", encoding="utf-8")

            def missing_playwright():
                raise BrowserSmokeError("Playwright is required for --with-browser")

            with self.assertRaisesRegex(BrowserSmokeError, "Playwright is required"):
                run_dashboard_browser_smoke(path, playwright_factory=missing_playwright)

    def test_daily_bundle_browser_smoke_happy_path_with_fake_browser(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_bundle(root)

            result = run_daily_bundle_browser_smoke(root, playwright_factory=_bundle_factory())

        self.assertEqual(result.status, "passed")
        self.assertEqual(result.pages_checked, 4)
        self.assertEqual(result.checks, ("index.html", "dashboard.html", "knowledge_review.html", "run_diagnostics.html"))

    def test_daily_bundle_missing_index_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_bundle(root)
            (root / "index.html").unlink()

            with self.assertRaisesRegex(BrowserSmokeError, "index.html does not exist"):
                run_daily_bundle_browser_smoke(root, playwright_factory=_bundle_factory())

    def test_daily_bundle_missing_dashboard_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_bundle(root)
            (root / "2026-05-15" / "dashboard.html").unlink()

            with self.assertRaisesRegex(BrowserSmokeError, "dashboard.html does not exist"):
                run_daily_bundle_browser_smoke(root, playwright_factory=_bundle_factory())

    def test_daily_bundle_missing_knowledge_review_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_bundle(root)
            (root / "2026-05-15" / "knowledge_review.html").unlink()

            with self.assertRaisesRegex(BrowserSmokeError, "knowledge_review.html does not exist"):
                run_daily_bundle_browser_smoke(root, playwright_factory=_bundle_factory())

    def test_daily_bundle_missing_run_diagnostics_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_bundle(root)
            (root / "2026-05-15" / "run_diagnostics.html").unlink()

            with self.assertRaisesRegex(BrowserSmokeError, "run_diagnostics.html does not exist"):
                run_daily_bundle_browser_smoke(root, playwright_factory=_bundle_factory())


if __name__ == "__main__":
    unittest.main()
