from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from market_impact_radar.web_api import DailyReportApi

ROOT = Path(__file__).resolve().parents[1]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _write_run(root: Path, run_date: str = "2026-05-15", signals: list[dict] | None = None) -> Path:
    run_dir = root / run_date
    run_dir.mkdir(parents=True, exist_ok=True)
    signal_payload = signals if signals is not None else [{"theme": "storage chips"}]
    (run_dir / "dashboard_data.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "run": {"date": run_date, "status": "ok", "generated_at": "2026-05-15T01:00:00+00:00"},
                "summary": {"strong_signals": 1},
                "signals": signal_payload,
                "knowledge": {"status": "skipped"},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return run_dir


class _ForbiddenTerm:
    """Helper to distinguish positive feature use from disclaimer/negative context."""

    POSITIVE_PHRASES = [
        "buy list",
        "must buy",
        "sell signal",
        "target price",
        "win rate",
        "guaranteed rise",
        "profit target",
        "trading signal",
        "entry point",
        "必涨",
        "保证收益",
    ]

    NEGATIVE_PHRASES = [
        "not a trading",
        "not trading",
        "not buy",
        "not sell",
        "does not",
        "no trading",
        "not represent trading",
        "no buy/sell",
        "does not provide",
        "avoids certainty",
        "prohibited terms",
    ]

    @classmethod
    def has_positive_feature(cls, text: str) -> list[str]:
        lower = text.lower()
        violations = []
        for phrase in cls.POSITIVE_PHRASES:
            start = 0
            while True:
                idx = lower.find(phrase, start)
                if idx == -1:
                    break
                window = lower[max(0, idx - 40):idx + len(phrase)]
                has_negation = any(neg in window for neg in cls.NEGATIVE_PHRASES)
                if not has_negation:
                    violations.append(phrase)
                    break
                start = idx + len(phrase)
        return violations


def _extract_readme_main_path(text: str) -> str:
    """Extract README content from top to the first Legacy section."""
    idx = text.find("## Legacy Research Utilities")
    if idx == -1:
        idx = text.find("## Legacy")
    if idx == -1:
        return text
    return text[:idx]


def _extract_readme_已实现_section(text: str) -> str:
    """Extract the '已实现' section content between '## 已实现' and the next '## ' heading."""
    start = text.find("## 已实现")
    if start == -1:
        return ""
    after = text[start + len("## 已实现"):]
    next_heading = after.find("\n## ")
    if next_heading == -1:
        return after
    return after[:next_heading]




class ForbiddenTermMultiOccurrenceTest(unittest.TestCase):
    """Regression: _ForbiddenTerm must check all occurrences, not just the first."""

    def test_disclaimer_then_positive_feature_detected(self) -> None:
        text = (
            "This product is not a trading signal. "
            "Later in the docs: the console provides a trading signal overview."
        )
        violations = _ForbiddenTerm.has_positive_feature(text)
        self.assertIn("trading signal", violations)

    def test_only_disclaimer_no_violation(self) -> None:
        text = "This is not a trading signal and does not provide a buy list."
        violations = _ForbiddenTerm.has_positive_feature(text)
        self.assertEqual(violations, [])

    def test_positive_without_disclaimer_detected(self) -> None:
        text = "The platform offers a buy list for investors."
        violations = _ForbiddenTerm.has_positive_feature(text)
        self.assertIn("buy list", violations)

    def test_chinese_trading_promise_detected(self) -> None:
        text = "这个页面承诺主题必涨。"
        violations = _ForbiddenTerm.has_positive_feature(text)
        self.assertIn("必涨", violations)


class ReadmeProductBoundariesTest(unittest.TestCase):
    def test_readme_exists(self) -> None:
        path = ROOT / "README.md"
        self.assertTrue(path.exists(), "README.md should exist")

    def test_readme_declares_readonly_research_positioning(self) -> None:
        text = _read_text(ROOT / "README.md")
        self.assertIn("只读研究", text, "README should declare readonly research positioning")
        self.assertIn("不是交易系统", text, "README should declare it is not a trading system")

    def test_readme_main_path_does_not_present_backtest_as_primary_feature(self) -> None:
        text = _read_text(ROOT / "README.md")
        已实现 = _extract_readme_已实现_section(text)
        self.assertNotIn("回测统计", 已实现, "已实现主列表不应把回测作为正向能力")
        self.assertNotIn("回测和边际分", 已实现, "已实现主列表不应把批量回测作为正向能力")
        self.assertNotIn("回测结果写回", 已实现, "已实现主列表不应把回测写回作为正向能力")
        self.assertNotIn("胜率", 已实现, "已实现主列表不应把胜率作为正向能力")

    def test_readme_legacy_section_exists(self) -> None:
        text = _read_text(ROOT / "README.md")
        self.assertIn("## Legacy Research Utilities", text, "README should have a Legacy Research Utilities section")

    def test_readme_legacy_terms_are_labeled_as_legacy(self) -> None:
        text = _read_text(ROOT / "README.md")
        main_path = _extract_readme_main_path(text)
        # In the main path (before Legacy section), backtest/回测 should not appear
        self.assertNotIn("backtest", main_path.lower(), "README main path should not contain backtest before Legacy section")
        self.assertNotIn("回测", main_path, "README main path should not contain 回测 before Legacy section")

    def test_readme_does_not_make_trading_promises(self) -> None:
        text = _read_text(ROOT / "README.md")
        # These English-only terms should never appear as promises
        for term in ["guaranteed rise", "profit target", "must buy"]:
            self.assertNotIn(term, text.lower(), f"README should not contain: {term}")
        # Chinese "必涨" should not appear
        self.assertNotIn("必涨", text, "README should not promise guaranteed rise")


class ProductBoundariesDocsTest(unittest.TestCase):
    def test_product_boundaries_doc_exists(self) -> None:
        path = ROOT / "docs" / "PRODUCT_BOUNDARIES.md"
        self.assertTrue(path.exists(), "docs/PRODUCT_BOUNDARIES.md should exist")

    def test_product_boundaries_contains_readonly定位(self) -> None:
        text = _read_text(ROOT / "docs" / "PRODUCT_BOUNDARIES.md")
        self.assertIn("只读", text)
        self.assertIn("研究", text)
        self.assertIn("observation", text.lower())
        self.assertIn("research", text.lower())

    def test_product_boundaries_declares_not_trading_system(self) -> None:
        text = _read_text(ROOT / "docs" / "PRODUCT_BOUNDARIES.md")
        self.assertIn("不是交易系统", text)
        self.assertIn("不是荐股系统", text)

    def test_legacy_research_utilities_doc_exists(self) -> None:
        path = ROOT / "docs" / "LEGACY_RESEARCH_UTILITIES.md"
        self.assertTrue(path.exists(), "docs/LEGACY_RESEARCH_UTILITIES.md should exist")

    def test_legacy_doc_lists_backtest_module(self) -> None:
        text = _read_text(ROOT / "docs" / "LEGACY_RESEARCH_UTILITIES.md")
        self.assertIn("backtest.py", text)
        self.assertIn("review_feedback.py", text)
        self.assertIn("Legacy internal", text)

    def test_legacy_doc_states_not_trading_system(self) -> None:
        text = _read_text(ROOT / "docs" / "LEGACY_RESEARCH_UTILITIES.md")
        self.assertIn("不构成交易系统", text)


class ApiDocsBoundariesTest(unittest.TestCase):
    def test_api_docs_no_positive_trading_feature(self) -> None:
        text = _read_text(ROOT / "docs" / "API.md")
        violations = _ForbiddenTerm.has_positive_feature(text)
        self.assertEqual(
            violations,
            [],
            f"API.md should not use trading terms as positive features: {violations}",
        )

    def test_api_docs_uses_disclaimer_language(self) -> None:
        text = _read_text(ROOT / "docs" / "API.md").lower()
        self.assertIn("not trading", text)
        self.assertIn("does not", text)
        self.assertIn("no trading", text)


class ConsoleBoundariesTest(unittest.TestCase):
    def test_console_html_contains_research_language(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_run(Path(tmpdir))
            response = DailyReportApi(tmpdir).handle_get("/console")

        html = response.payload.lower()
        self.assertIn("research", html)
        self.assertIn("observation", html)
        self.assertIn("console usage guide", html)
        self.assertIn("research review queue", html)
        self.assertIn("research notes composer", html)

    def test_console_html_no_positive_trading_expression(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_run(Path(tmpdir))
            response = DailyReportApi(tmpdir).handle_get("/console")

        html = response.payload.lower()
        for forbidden in ["buy list", "must buy", "sell signal", "guaranteed rise", "profit target"]:
            self.assertNotIn(forbidden, html, f"/console should not contain '{forbidden}' as positive feature")

    def test_console_html_daily_brief_has_disclaimer(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_run(Path(tmpdir))
            response = DailyReportApi(tmpdir).handle_get("/console")

        html = response.payload.lower()
        self.assertIn("research and observation only", html)


class WebApiNoPostTest(unittest.TestCase):
    def test_no_post_routes(self) -> None:
        handler_source = _read_text(ROOT / "market_impact_radar" / "web_api.py")
        self.assertNotIn("do_POST", handler_source)
        self.assertNotIn("do_PUT", handler_source)
        self.assertNotIn("do_DELETE", handler_source)


class WebApiEndpointsTest(unittest.TestCase):
    def test_health_endpoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            response = DailyReportApi(tmpdir).handle_get("/api/health")
        self.assertEqual(response.status_code, 200)
        self.assertIn("status", response.payload)

    def test_version_endpoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            response = DailyReportApi(tmpdir).handle_get("/api/version")
        self.assertEqual(response.status_code, 200)
        self.assertIn("api_version", response.payload)

    def test_history_compare_endpoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_run(Path(tmpdir), "2026-05-14")
            _write_run(Path(tmpdir), "2026-05-15")
            response = DailyReportApi(tmpdir).handle_get("/api/history/compare?from=2026-05-14&to=2026-05-15")
        self.assertEqual(response.status_code, 200)
        self.assertIn("schema_version", response.payload)

    def test_history_themes_endpoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_run(Path(tmpdir))
            response = DailyReportApi(tmpdir).handle_get("/api/history/themes")
        self.assertEqual(response.status_code, 200)

    def test_history_candidates_endpoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_run(Path(tmpdir))
            response = DailyReportApi(tmpdir).handle_get("/api/history/candidates")
        self.assertEqual(response.status_code, 200)

    def test_history_data_quality_endpoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_run(Path(tmpdir))
            response = DailyReportApi(tmpdir).handle_get("/api/history/data-quality")
        self.assertEqual(response.status_code, 200)

    def test_history_sources_endpoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_run(Path(tmpdir))
            response = DailyReportApi(tmpdir).handle_get("/api/history/sources")
        self.assertEqual(response.status_code, 200)

    def test_history_theme_source_matrix_endpoint(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_run(Path(tmpdir))
            response = DailyReportApi(tmpdir).handle_get("/api/history/theme-source-matrix")
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
