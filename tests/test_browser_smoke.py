from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from market_impact_radar.browser_smoke import BrowserSmokeError, run_dashboard_browser_smoke


class _FakeMessage:
    type = "log"
    text = ""


class _FakeLocator:
    def __init__(self, text: str) -> None:
        self._text = text

    def inner_text(self, timeout: int = 0) -> str:
        return self._text


class _FakePage:
    def __init__(self, body_text: str, title: str = "Daily Market Radar") -> None:
        self._body_text = body_text
        self._title = title
        self.url = ""

    def on(self, event: str, callback) -> None:
        if event == "console":
            callback(_FakeMessage())

    def goto(self, url: str, wait_until: str = "") -> None:
        self.url = url

    def locator(self, selector: str) -> _FakeLocator:
        return _FakeLocator(self._body_text)

    def title(self) -> str:
        return self._title


class _FakeBrowser:
    def __init__(self, page: _FakePage) -> None:
        self._page = page

    def new_page(self) -> _FakePage:
        return self._page

    def close(self) -> None:
        return None


class _FakeChromium:
    def __init__(self, page: _FakePage) -> None:
        self._page = page

    def launch(self, headless: bool = True) -> _FakeBrowser:
        return _FakeBrowser(self._page)


class _FakePlaywright:
    def __init__(self, page: _FakePage) -> None:
        self.chromium = _FakeChromium(page)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False


def _factory(body_text: str):
    return lambda: _FakePlaywright(_FakePage(body_text))


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


if __name__ == "__main__":
    unittest.main()
