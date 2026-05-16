from __future__ import annotations

import unittest

from market_impact_radar.dashboard import render_dashboard_from_data
from market_impact_radar.dashboard_contract import (
    DASHBOARD_SCHEMA_VERSION,
    normalize_dashboard_data,
    validate_dashboard_data,
)


class DashboardDataContractTest(unittest.TestCase):
    def test_normalize_dashboard_data_fills_defaults(self) -> None:
        normalized = normalize_dashboard_data({})

        self.assertEqual(normalized["schema_version"], DASHBOARD_SCHEMA_VERSION)
        self.assertEqual(normalized["run"]["status"], "unknown")
        self.assertEqual(normalized["summary"]["strong_signals"], 0)
        self.assertEqual(normalized["signals"], [])
        self.assertEqual(normalized["knowledge"]["status"], "unknown")
        self.assertIsNone(normalized["outputs"]["dashboard_html"])
        self.assertIsNone(normalized["outputs"]["knowledge_review_html"])
        self.assertIsNone(normalized["outputs"]["run_diagnostics_html"])

    def test_validate_dashboard_data_finds_missing_schema_version(self) -> None:
        issues = validate_dashboard_data(
            {
                "run": {},
                "summary": {},
                "signals": [],
                "knowledge": {},
                "outputs": {},
            }
        )

        self.assertTrue(any(issue["field"] == "schema_version" for issue in issues))

    def test_validate_dashboard_data_finds_bad_signals_type(self) -> None:
        issues = validate_dashboard_data(
            {
                "schema_version": DASHBOARD_SCHEMA_VERSION,
                "run": {},
                "summary": {},
                "signals": {},
                "knowledge": {},
                "outputs": {},
            }
        )

        self.assertTrue(any(issue["level"] == "error" and issue["field"] == "signals" for issue in issues))

    def test_validate_dashboard_data_warns_on_signal_missing_fields(self) -> None:
        issues = validate_dashboard_data(
            {
                "schema_version": DASHBOARD_SCHEMA_VERSION,
                "run": {},
                "summary": {},
                "signals": [{}],
                "knowledge": {},
                "outputs": {},
            }
        )

        fields = {issue["field"] for issue in issues}
        self.assertIn("signals[0].theme", fields)
        self.assertIn("signals[0].intraday_status", fields)
        self.assertIn("signals[0].risk_level", fields)


class DashboardDataRenderTest(unittest.TestCase):
    def test_dashboard_data_renders_signal_fields(self) -> None:
        html = render_dashboard_from_data(
            {
                "schema_version": DASHBOARD_SCHEMA_VERSION,
                "run": {
                    "date": "2026-05-15",
                    "generated_at": "2026-05-15T01:00:00+00:00",
                    "status": "ok",
                    "warnings": [],
                },
                "market_context": {
                    "a_share_trading_day": "2026-05-15",
                    "is_a_share_trading_day": True,
                    "sources": ["sample-context"],
                    "fetched_at": "2026-05-15T09:00:00+08:00",
                    "foreign_market_context": [
                        {
                            "market": "US",
                            "session_date": "2026-05-14",
                            "is_market_trading_day": True,
                            "mapped_a_share_trade_day": "2026-05-15",
                        }
                    ],
                },
                "summary": {
                    "strong_signals": 1,
                    "confirmed": 1,
                    "downgraded": 0,
                    "failed": 0,
                    "missing_data": 0,
                    "knowledge_issues": 1,
                },
                "signals": [
                    {
                        "theme": "storage chips",
                        "strength": 88,
                        "score": 91,
                        "external_triggers": ["MU"],
                        "a_share_mapping_reason": ["possible transmission from memory chain"],
                        "etf_candidates": ["chip ETF"],
                        "stock_candidates": ["memory leader"],
                        "intraday_status": "confirmed",
                        "risk_level": "watch",
                        "risks": ["gap risk"],
                        "data_status": "ok",
                        "sources": ["sample/yahoo"],
                        "fetched_at": ["2026-05-14T07:30:00+08:00"],
                    }
                ],
                "knowledge": {
                    "status": "issues",
                    "issues": [{"severity": "medium", "kind": "theme_stock_unverified", "target": "storage chips"}],
                    "suggestions": [{"kind": "add_stock_code_or_fix_name", "target": "storage chips", "confidence": "medium"}],
                },
                "outputs": {
                    "report_md": "report.md",
                    "dashboard_html": "dashboard.html",
                    "knowledge_review_html": "reports/daily/2026-05-15/knowledge_review.html",
                    "run_diagnostics_html": "reports/daily/2026-05-15/run_diagnostics.html",
                },
            }
        )

        self.assertIn("Schema: 1.0", html)
        self.assertIn("Signal Overview", html)
        self.assertIn("Market Context", html)
        self.assertIn("id=\"signal-search\"", html)
        self.assertIn("id=\"filter-strength\"", html)
        self.assertIn("id=\"filter-intraday-status\"", html)
        self.assertIn("id=\"filter-risk-level\"", html)
        self.assertIn("id=\"filter-data-status\"", html)
        self.assertIn("data-quick-filter=\"confirmed\"", html)
        self.assertIn("data-quick-filter=\"high-risk\"", html)
        self.assertIn("visible-signal-count", html)
        self.assertIn("2026-05-15", html)
        self.assertIn("storage chips", html)
        self.assertIn("Risk Level", html)
        self.assertIn("chip ETF", html)
        self.assertIn("memory leader", html)
        self.assertIn("gap risk", html)
        self.assertIn("sample/yahoo", html)
        self.assertIn("sample-context", html)
        self.assertIn("Output Links", html)
        self.assertIn("Back to Daily Runs", html)
        self.assertIn("href='../index.html'", html)
        self.assertIn("aria-current='page'>Dashboard</a>", html)
        self.assertIn("href='dashboard_data.json'", html)
        self.assertIn("href='run_summary.json'", html)
        self.assertIn("report.md", html)
        self.assertIn("knowledge_review.html", html)
        self.assertIn("href='knowledge_review.html'", html)
        self.assertIn("run_diagnostics.html", html)
        self.assertIn("href='run_diagnostics.html'", html)
        self.assertIn("Mapping Suggestions", html)
        self.assertIn("data-signal-card", html)
        self.assertIn("data-intraday-status=\"confirmed\"", html)
        self.assertIn("data-risk-level=\"watch\"", html)
        self.assertIn("data-data-status=\"ok\"", html)

    def test_render_dashboard_data_handles_minimal_input(self) -> None:
        html = render_dashboard_from_data({"run": {"date": "2026-05-15"}})

        self.assertIn("2026-05-15", html)
        self.assertIn("id=\"signal-search\"", html)
        self.assertIn("0</span> / <span id=\"total-signal-count\">0</span> signals visible", html)
        self.assertIn("No signals available.", html)
        self.assertIn("Knowledge Graph", html)
        self.assertIn("not_checked", html)
        self.assertIn("External context not provided.", html)
        self.assertIn("report.md unavailable", html)
        self.assertNotIn("href='report.md'", html)

    def test_candidate_fields_accept_string_and_dict_values(self) -> None:
        html = render_dashboard_from_data(
            {
                "schema_version": DASHBOARD_SCHEMA_VERSION,
                "run": {"date": "2026-05-15"},
                "signals": [
                    {
                        "theme": "AI compute",
                        "etf_candidates": "AI ETF",
                        "stock_candidates": [{"name": "optical leader", "code": "300000", "risk": "high"}],
                        "risk_level": "high",
                    }
                ],
            }
        )

        self.assertIn("AI compute", html)
        self.assertIn("AI ETF", html)
        self.assertIn("optical leader 300000", html)
        self.assertIn("risk: high", html)
        self.assertIn("No risk notes provided.", html)
        self.assertIn("data-strength=\"unknown\"", html)
        self.assertIn("data-risk-level=\"high\"", html)

    def test_empty_candidates_show_empty_state(self) -> None:
        html = render_dashboard_from_data(
            {
                "schema_version": DASHBOARD_SCHEMA_VERSION,
                "run": {"date": "2026-05-15"},
                "signals": [{"theme": "gold", "risk_level": "watch"}],
            }
        )

        self.assertIn("No ETF candidates available.", html)
        self.assertIn("No stock candidates available.", html)

    def test_filter_data_attributes_escape_values(self) -> None:
        html = render_dashboard_from_data(
            {
                "schema_version": DASHBOARD_SCHEMA_VERSION,
                "run": {"date": "2026-05-15"},
                "signals": [
                    {
                        "theme": "quote test",
                        "external_triggers": ['MU" onclick="bad'],
                        "risk_level": '" high',
                    }
                ],
            }
        )

        self.assertIn("data-search=", html)
        self.assertIn("&quot; onclick=&quot;bad", html)
        self.assertNotIn('onclick="bad', html)

    def test_dashboard_data_escapes_visible_values(self) -> None:
        html = render_dashboard_from_data(
            {
                "schema_version": DASHBOARD_SCHEMA_VERSION,
                "run": {"date": "2026-05-15"},
                "signals": [{"theme": "<script>alert(1)</script>", "risk_level": "watch"}],
            }
        )

        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertNotIn("<script>alert(1)</script>", html)

    def test_render_dashboard_data_accepts_legacy_shape(self) -> None:
        html = render_dashboard_from_data(
            {
                "run_date": "2026-05-15",
                "status": "partial",
                "scored_themes": [{"theme": "legacy theme", "score": 70}],
            }
        )

        self.assertIn("Schema: 1.0", html)
        self.assertIn("legacy theme", html)


if __name__ == "__main__":
    unittest.main()
