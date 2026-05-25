from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread

from market_impact_radar.web_api import DailyReportApi, make_handler


ROOT = Path(__file__).resolve().parents[1]


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
                "outputs": {},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (run_dir / "run_summary.json").write_text(
        json.dumps(
            {
                "run_date": run_date,
                "status": "ok",
                "generated_at": "2026-05-15T01:00:00+00:00",
                "outputs": {"dashboard_data_json": str(run_dir / "dashboard_data.json")},
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    (run_dir / "dashboard.html").write_text("<html>Dashboard</html>", encoding="utf-8")
    (run_dir / "knowledge_review.html").write_text("<html>Knowledge Graph Review</html>", encoding="utf-8")
    (run_dir / "run_diagnostics.html").write_text("<html>Run Diagnostics</html>", encoding="utf-8")
    return run_dir


class WebApiTest(unittest.TestCase):
    def test_api_index_lists_readonly_endpoints_without_file_access(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            api = DailyReportApi(Path(tmpdir) / "missing-reports")
            response = api.handle_get("/api")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.payload["service"], "market_impact_radar")
        self.assertTrue(response.payload["readonly_api"])
        self.assertEqual(response.payload["openapi"], "/api/openapi.json")
        self.assertEqual(response.payload["console"], "/console")
        paths = {endpoint["path"] for endpoint in response.payload["endpoints"]}
        self.assertIn("/api/runs", paths)
        self.assertIn("/api/history/themes", paths)
        self.assertIn("/api/history/candidates", paths)
        self.assertIn("/api/history/data-quality", paths)
        self.assertIn("/api/history/sources", paths)
        self.assertIn("/api/history/theme-source-matrix", paths)
        self.assertIn("/api/history/compare", paths)
        self.assertIn("/api/runs/{date}/artifacts", paths)
        self.assertIn("/api/runs/{date}/dashboard-data", paths)

    def test_console_endpoint_returns_static_readonly_shell_without_file_access(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            api = DailyReportApi(Path(tmpdir) / "missing-reports")
            response = api.handle_get("/console")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "text/html; charset=utf-8")
        self.assertIsInstance(response.payload, str)
        self.assertIn("Market Impact Radar Console", response.payload)
        self.assertIn("Read-only daily report viewer", response.payload)
        self.assertIn("Workspace Navigation", response.payload)
        for anchor in (
            "#console-usage-guide",
            "#morning-brief",
            "#daily-research-brief",
            "#research-review-queue",
            "#research-notes-composer",
            "#research-export-package",
            "#date-compare",
            "#console-controls",
            "#theme-hotlist",
            "#source-reliability",
            "#theme-source-matrix",
            "#theme-compare",
            "#historical-review",
            "#signal-explorer",
            "#signal-detail",
            "#theme-detail",
            "#source-detail",
            "#artifact-links",
        ):
            self.assertIn(anchor, response.payload)
        self.assertIn('fetchJson("/api/runs")', response.payload)
        self.assertIn("/api/runs/${date}/dashboard-data", response.payload)
        self.assertIn("/api/runs/${date}/artifacts", response.payload)
        self.assertIn("Artifacts", response.payload)
        self.assertIn("Knowledge Review", response.payload)
        self.assertIn("Run Diagnostics", response.payload)
        self.assertIn("Run Date", response.payload)
        self.assertIn("Refresh Runs", response.payload)
        self.assertIn("Signal Search", response.payload)
        self.assertIn("Risk Filter", response.payload)
        self.assertIn("Status Filter", response.payload)
        self.assertIn("Sort Signals", response.payload)
        self.assertIn("Grouped by theme", response.payload)
        self.assertIn("Flat signal list", response.payload)
        self.assertIn("Theme Hotlist", response.payload)
        self.assertIn("Morning Brief", response.payload)
        self.assertIn("Console Usage Guide", response.payload)
        self.assertIn("Recommended workflow", response.payload)
        self.assertIn("Read Morning Brief", response.payload)
        self.assertIn("Check Research Review Queue", response.payload)
        self.assertIn("Review Theme × Source Matrix", response.payload)
        self.assertIn("Use Date Compare", response.payload)
        self.assertIn("Generate Research Notes", response.payload)
        self.assertIn("Daily Research Brief", response.payload)
        self.assertIn("Research Review Queue", response.payload)
        self.assertIn("Showing top 10 review items", response.payload)
        self.assertIn("Research Notes Composer", response.payload)
        self.assertIn("research-notes-composer", response.payload)
        self.assertIn("Notes language", response.payload)
        self.assertIn("Notes mode", response.payload)
        self.assertIn("Full Notes", response.payload)
        self.assertIn("Compact Notes", response.payload)
        self.assertIn("Manual Research Notes", response.payload)
        self.assertIn("manual-research-notes", response.payload)
        self.assertIn("Manual notes are only kept in this browser view", response.payload)
        self.assertIn("notesLang", response.payload)
        self.assertIn("notesMode", response.payload)
        self.assertIn("notes-language-select", response.payload)
        self.assertIn("notes-mode-select", response.payload)
        self.assertIn("Research Export Package", response.payload)
        self.assertIn("research-export-package", response.payload)
        self.assertIn("Export sections", response.payload)
        self.assertIn("Export Preview", response.payload)
        self.assertIn("Download Markdown", response.payload)
        self.assertIn("Download Plain Text", response.payload)
        self.assertIn("Download JSON Metadata", response.payload)
        self.assertIn("exportLang", response.payload)
        self.assertIn("exportFormat", response.payload)
        self.assertIn("export-language-select", response.payload)
        self.assertIn("export-format-select", response.payload)
        self.assertIn("export-preview", response.payload)
        self.assertIn("Review Queue Summary", response.payload)
        self.assertIn("Review Severity", response.payload)
        self.assertIn("Review Category", response.payload)
        self.assertIn("Review Scope", response.payload)
        self.assertIn("research-review-queue", response.payload)
        self.assertIn("reviewSeverity", response.payload)
        self.assertIn("reviewCategory", response.payload)
        self.assertIn("reviewScope", response.payload)
        self.assertIn("review-severity-filter", response.payload)
        self.assertIn("review-category-filter", response.payload)
        self.assertIn("review-scope-select", response.payload)
        self.assertIn("Date Compare", response.payload)
        self.assertIn("date-compare", response.payload)
        self.assertIn("compareFrom", response.payload)
        self.assertIn("compareTo", response.payload)
        self.assertIn("From date", response.payload)
        self.assertIn("To date", response.payload)
        self.assertIn("Date-over-Date Changes", response.payload)
        self.assertIn("daily-research-brief", response.payload)
        self.assertIn("Copy as Markdown", response.payload)
        self.assertIn("Copy as Plain Text", response.payload)
        self.assertIn("Brief Language", response.payload)
        self.assertIn("中文", response.payload)
        self.assertIn("Brief Mode", response.payload)
        self.assertIn("Full Brief", response.payload)
        self.assertIn("Compact Brief", response.payload)
        self.assertIn("Section toggles", response.payload)
        self.assertIn("briefLang", response.payload)
        self.assertIn("briefMode", response.payload)
        self.assertIn("brief-language-select", response.payload)
        self.assertIn("brief-mode-select", response.payload)
        self.assertIn("generated locally", response.payload)
        self.assertIn("not saved", response.payload)
        self.assertIn("research and observation only", response.payload.lower())
        self.assertIn("Source Reliability", response.payload)
        self.assertIn("Source Detail Panel", response.payload)
        self.assertIn("Source Breakdown", response.payload)
        self.assertIn("Weak Evidence Signals", response.payload)
        self.assertIn("Historical Data Quality Trend", response.payload)
        self.assertIn("Theme × Source Matrix", response.payload)
        self.assertIn("Matrix Summary", response.payload)
        self.assertIn("Cell Detail", response.payload)
        self.assertIn("Weak Evidence Cells", response.payload)
        self.assertIn("Theme Compare", response.payload)
        self.assertIn("Candidate Pool Comparison", response.payload)
        self.assertIn("Back to top", response.payload)
        self.assertIn("section-card", response.payload)
        self.assertIn("section-description", response.payload)
        self.assertIn("collapsible-section", response.payload)
        self.assertIn("badge-risk", response.payload)
        self.assertIn("badge-status", response.payload)
        self.assertIn("badge-data", response.payload)
        self.assertIn("badge-warning", response.payload)
        self.assertIn("badge-unknown", response.payload)
        self.assertIn("compare-theme-select", response.payload)
        self.assertIn("createCompareButton", response.payload)
        self.assertIn("Theme Detail", response.payload)
        self.assertIn("theme-button", response.payload)
        self.assertIn("Signal Detail Panel", response.payload)
        self.assertIn("Evidence Chain", response.payload)
        self.assertIn("Data Quality / Freshness", response.payload)
        self.assertIn("ETF observation pool", response.payload)
        self.assertIn("Stock observation pool", response.payload)
        self.assertIn("Historical Review", response.payload)
        self.assertIn("Historical Theme Trends", response.payload)
        self.assertIn("Recurring Observation Candidates", response.payload)
        self.assertIn("Data Quality Trend", response.payload)
        self.assertIn("API status and version", response.payload)
        self.assertIn("Artifact Links", response.payload)
        self.assertIn("No signals match the current filters.", response.payload)
        self.assertIn("signal-count", response.payload)
        self.assertIn("readConsoleStateFromUrl", response.payload)
        self.assertIn("normalizeConsoleState", response.payload)
        self.assertIn("updateQueryState", response.payload)
        self.assertIn('params.get("date")', response.payload)
        self.assertIn('params.get("search")', response.payload)
        self.assertIn('params.get("risk")', response.payload)
        self.assertIn('params.get("status")', response.payload)
        self.assertIn('params.get("sort")', response.payload)
        self.assertIn('params.get("view")', response.payload)
        self.assertIn('params.get("theme")', response.payload)
        self.assertIn('params.get("source")', response.payload)
        self.assertIn('params.get("compare")', response.payload)
        self.assertIn('params.get("reviewSeverity")', response.payload)
        self.assertIn('params.get("reviewCategory")', response.payload)
        self.assertIn('params.get("reviewScope")', response.payload)
        self.assertIn('params.get("notesLang")', response.payload)
        self.assertIn('params.get("notesMode")', response.payload)
        self.assertIn("selectedTheme", response.payload)
        self.assertIn("selectedSource", response.payload)
        self.assertIn("source-button", response.payload)
        self.assertIn("compareThemes", response.payload)
        self.assertNotIn("POST /api/run-daily", response.payload)
        self.assertNotIn("buy list", response.payload.lower())
        self.assertNotIn("must buy", response.payload.lower())
        self.assertNotIn("sell signal", response.payload.lower())
        self.assertNotIn("target price", response.payload.lower())
        self.assertNotIn("guaranteed", response.payload.lower())
        self.assertNotIn("win rate", response.payload.lower())
        self.assertNotIn("profit", response.payload.lower())
        self.assertNotIn("alpha", response.payload.lower())

    def test_root_endpoint_returns_console_shell(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            response = DailyReportApi(Path(tmpdir) / "missing-reports").handle_get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content_type, "text/html; charset=utf-8")
        self.assertIn("Daily Runs", response.payload)

    def test_openapi_json_describes_public_readonly_paths_without_file_access(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            api = DailyReportApi(Path(tmpdir) / "missing-reports")
            response = api.handle_get("/api/openapi.json")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.payload["openapi"], "3.1.0")
        self.assertTrue(response.payload["x-readonly"])
        self.assertEqual(response.payload["info"]["version"], "v1")
        paths = response.payload["paths"]
        self.assertIn("/api/health", paths)
        self.assertIn("/api/history/themes", paths)
        self.assertIn("/api/history/candidates", paths)
        self.assertIn("/api/history/data-quality", paths)
        self.assertIn("/api/history/sources", paths)
        self.assertIn("/api/history/theme-source-matrix", paths)
        self.assertIn("/api/history/compare", paths)
        self.assertIn("/api/runs/{date}/artifacts", paths)
        self.assertIn("/api/runs/{date}/diagnostics", paths)

    def test_health_endpoint_returns_ok_without_file_access(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            api = DailyReportApi(Path(tmpdir) / "missing-reports")
            response = api.handle_get("/api/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.payload["status"], "ok")
        self.assertEqual(response.payload["service"], "market_impact_radar")
        self.assertEqual(response.payload["api"], "readonly")
        self.assertEqual(response.payload["version"], "v1")

    def test_version_endpoint_returns_contract_metadata_without_file_access(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            api = DailyReportApi(Path(tmpdir) / "missing-reports")
            response = api.handle_get("/api/version")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.payload["service"], "market_impact_radar")
        self.assertEqual(response.payload["api_version"], "v1")
        self.assertEqual(response.payload["dashboard_schema_version"], "1.0")
        self.assertTrue(response.payload["readonly_api"])
        self.assertIn("package_version", response.payload)

    def test_list_runs_returns_history_entries_with_api_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_run(Path(tmpdir))
            response = DailyReportApi(tmpdir).handle_get("/api/runs")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.payload["schema_version"], "1.0")
        self.assertEqual(response.payload["runs"][0]["date"], "2026-05-15")
        self.assertEqual(response.payload["runs"][0]["links"]["artifacts"], "/api/runs/2026-05-15/artifacts")
        self.assertEqual(response.payload["runs"][0]["links"]["dashboard_data"], "/api/runs/2026-05-15/dashboard-data")

    def test_history_themes_returns_theme_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_run(
                Path(tmpdir),
                "2026-05-14",
                [
                    {
                        "theme": "AI hardware",
                        "score": 80,
                        "strength": "strong",
                        "risk_level": "watch",
                        "intraday_status": "confirmed",
                        "data_status": "ok",
                        "external_triggers": ["NVDA"],
                        "etf_candidates": ["AI ETF"],
                        "stock_candidates": ["ServerCo"],
                    }
                ],
            )
            _write_run(
                Path(tmpdir),
                "2026-05-15",
                [
                    {
                        "theme": "AI hardware",
                        "score": 60,
                        "risk_level": "missing",
                        "intraday_status": "missing_data",
                        "data_status": "partial",
                    }
                ],
            )
            (Path(tmpdir) / "2026-05-16").mkdir()

            response = DailyReportApi(tmpdir).handle_get("/api/history/themes")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.payload["schema_version"], "1.0")
        self.assertEqual(response.payload["runs_count"], 2)
        self.assertEqual(response.payload["date_range"], {"start": "2026-05-14", "end": "2026-05-15"})
        theme = response.payload["themes"][0]
        self.assertEqual(theme["theme"], "AI hardware")
        self.assertEqual(theme["signal_count"], 2)
        self.assertEqual(theme["runs_seen"], 2)
        self.assertEqual(theme["avg_score"], 70.0)
        self.assertEqual(theme["max_score"], 80.0)
        self.assertEqual(theme["intraday_status_counts"]["confirmed"], 1)
        self.assertEqual(theme["data_status_counts"]["partial"], 1)

    def test_history_themes_uses_unknown_theme_for_missing_theme(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_run(Path(tmpdir), signals=[{"score": 10, "intraday_status": "downgraded"}])

            response = DailyReportApi(tmpdir).handle_get("/api/history/themes")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.payload["themes"][0]["theme"], "Unknown Theme")

    def test_history_candidates_counts_string_and_dict_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_run(
                Path(tmpdir),
                signals=[
                    {
                        "theme": "CPO",
                        "etf_candidates": ["通信ETF", {"name": "AI ETF", "code": "159000"}],
                        "stock_candidates": ["OpticsCo", {"name": "BoardCo", "ticker": "600001"}],
                    }
                ],
            )

            response = DailyReportApi(tmpdir).handle_get("/api/history/candidates")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.payload["schema_version"], "1.0")
        etfs = {item["name"]: item for item in response.payload["etf_candidates"]}
        stocks = {item["name"]: item for item in response.payload["stock_candidates"]}
        self.assertEqual(etfs["通信ETF"]["appearances"], 1)
        self.assertEqual(etfs["AI ETF"]["code"], "159000")
        self.assertEqual(stocks["OpticsCo"]["themes"], ["CPO"])
        self.assertEqual(stocks["BoardCo"]["code"], "600001")

    def test_history_data_quality_summarizes_sources_and_weak_data(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_run(
                Path(tmpdir),
                "2026-05-14",
                [
                    {
                        "theme": "AI hardware",
                        "data_status": "ok",
                        "sources": ["yahoo"],
                        "fetched_at": "2026-05-14T01:00:00+00:00",
                    },
                    {
                        "theme": "storage chips",
                        "data_status": "partial",
                        "fallback_used": True,
                    },
                ],
            )
            _write_run(
                Path(tmpdir),
                "2026-05-15",
                [
                    {
                        "theme": "storage chips",
                        "data_status": "stale",
                        "source": "eastmoney",
                    }
                ],
            )
            (Path(tmpdir) / "2026-05-16").mkdir()

            response = DailyReportApi(tmpdir).handle_get("/api/history/data-quality")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.payload["schema_version"], "1.0")
        self.assertEqual(response.payload["runs_count"], 2)
        self.assertEqual(response.payload["data_status_counts"]["partial"], 1)
        self.assertEqual(response.payload["data_status_counts"]["stale"], 1)
        self.assertEqual(response.payload["source_counts"]["yahoo"], 1)
        self.assertEqual(response.payload["source_counts"]["Unknown Source"], 1)
        self.assertEqual(response.payload["missing_source_count"], 1)
        self.assertEqual(response.payload["missing_fetched_at_count"], 2)
        self.assertEqual(response.payload["fallback_count"], 1)
        weak = {item["theme"]: item for item in response.payload["themes_with_weak_data"]}
        self.assertEqual(weak["storage chips"]["weak_signal_count"], 2)

    def test_history_sources_summarizes_source_detail(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_run(
                Path(tmpdir),
                "2026-05-14",
                [
                    {
                        "theme": "AI hardware",
                        "strength": "strong",
                        "score": 88,
                        "risk_level": "medium",
                        "intraday_status": "confirmed",
                        "data_status": "ok",
                        "sources": ["yahoo"],
                        "fetched_at": "2026-05-14T01:00:00+00:00",
                    },
                    {
                        "theme": "storage chips",
                        "risk_level": "high",
                        "data_status": "partial",
                        "fallback_used": True,
                    },
                ],
            )
            _write_run(
                Path(tmpdir),
                "2026-05-15",
                [
                    {
                        "theme": "AI hardware",
                        "data_status": "stale",
                        "source": "yahoo",
                    }
                ],
            )
            (Path(tmpdir) / "2026-05-16").mkdir()
            (Path(tmpdir) / "2026-05-17").mkdir()
            (Path(tmpdir) / "2026-05-17" / "dashboard_data.json").write_text("{bad json", encoding="utf-8")

            response = DailyReportApi(tmpdir).handle_get("/api/history/sources")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.payload["schema_version"], "1.0")
        self.assertEqual(response.payload["runs_count"], 2)
        sources = {item["source"]: item for item in response.payload["sources"]}
        self.assertEqual(sources["yahoo"]["signal_count"], 2)
        self.assertEqual(sources["yahoo"]["themes"], ["AI hardware"])
        self.assertEqual(sources["yahoo"]["missing_fetched_at_count"], 1)
        self.assertEqual(sources["yahoo"]["data_status_counts"]["stale"], 1)
        self.assertEqual(sources["Unknown Source"]["missing_source_count"], 1)
        self.assertEqual(sources["Unknown Source"]["fallback_count"], 1)
        self.assertLessEqual(len(sources["yahoo"]["example_signals"]), 5)

    def test_history_theme_source_matrix_summarizes_evidence_cells(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_run(
                Path(tmpdir),
                "2026-05-14",
                [
                    {
                        "theme": "AI hardware",
                        "strength": "strong",
                        "score": 88,
                        "risk_level": "medium",
                        "intraday_status": "confirmed",
                        "data_status": "ok",
                        "sources": ["yahoo"],
                        "fetched_at": "2026-05-14T01:00:00+00:00",
                    },
                    {
                        "risk_level": "high",
                        "data_status": "partial",
                        "fallback_used": True,
                    },
                ],
            )
            _write_run(
                Path(tmpdir),
                "2026-05-15",
                [
                    {
                        "theme": "AI hardware",
                        "data_status": "stale",
                        "source": "yahoo",
                    }
                ],
            )
            (Path(tmpdir) / "2026-05-16").mkdir()
            (Path(tmpdir) / "2026-05-17").mkdir()
            (Path(tmpdir) / "2026-05-17" / "dashboard_data.json").write_text("{bad json", encoding="utf-8")

            response = DailyReportApi(tmpdir).handle_get("/api/history/theme-source-matrix")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.payload["schema_version"], "1.0")
        self.assertEqual(response.payload["runs_count"], 2)
        self.assertIn("themes", response.payload)
        self.assertIn("sources", response.payload)
        self.assertIn("matrix", response.payload)
        self.assertIn("weak_cells", response.payload)
        themes = {item["theme"]: item for item in response.payload["themes"]}
        sources = {item["source"]: item for item in response.payload["sources"]}
        cells = {(item["theme"], item["source"]): item for item in response.payload["matrix"]}
        self.assertIn("Unknown Theme", themes)
        self.assertIn("Unknown Source", sources)
        self.assertEqual(themes["Unknown Theme"]["missing_source_count"], 1)
        self.assertEqual(cells[("Unknown Theme", "Unknown Source")]["missing_fetched_at_count"], 1)
        self.assertEqual(cells[("Unknown Theme", "Unknown Source")]["data_status_counts"]["partial"], 1)
        self.assertLessEqual(len(cells[("AI hardware", "yahoo")]["example_signals"]), 3)
        self.assertTrue(any(item["theme"] == "Unknown Theme" and item["source"] == "Unknown Source" for item in response.payload["weak_cells"]))

    def test_history_compare_returns_unavailable_when_missing_dates(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            response = DailyReportApi(tmpdir).handle_get("/api/history/compare?to=2026-05-15")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.payload["schema_version"], "1.0")
        self.assertFalse(response.payload["available"])
        self.assertIn("notes", response.payload)

    def test_history_compare_identifies_theme_candidate_and_quality_changes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_run(
                Path(tmpdir),
                "2026-05-14",
                [
                    {
                        "theme": "Storage",
                        "score": 60,
                        "strength": "medium",
                        "risk_level": "medium",
                        "intraday_status": "confirmed",
                        "data_status": "ok",
                        "sources": ["Yahoo"],
                        "fetched_at": "2026-05-14T01:00:00+00:00",
                        "etf_candidates": ["Chip ETF"],
                        "stock_candidates": ["OldCo"],
                    },
                    {
                        "theme": "Removed Theme",
                        "score": 50,
                        "data_status": "ok",
                        "source": "OldSource",
                        "fetched_at": "2026-05-14T01:10:00+00:00",
                    },
                ],
            )
            _write_run(
                Path(tmpdir),
                "2026-05-15",
                [
                    {
                        "theme": "Storage",
                        "score": 80,
                        "strength": "strong",
                        "risk_level": "high",
                        "intraday_status": "downgraded",
                        "data_status": "partial",
                        "sources": ["Yahoo", "Eastmoney"],
                        "fallback_used": True,
                        "etf_candidates": ["Chip ETF", {"name": "New ETF", "code": "159001"}],
                        "stock_candidates": ["NewCo"],
                    },
                    {
                        "theme": "New Theme",
                        "score": 70,
                        "data_status": "unknown",
                    },
                ],
            )
            (Path(tmpdir) / "2026-05-16").mkdir()
            (Path(tmpdir) / "2026-05-17").mkdir()
            (Path(tmpdir) / "2026-05-17" / "dashboard_data.json").write_text("{bad json", encoding="utf-8")

            response = DailyReportApi(tmpdir).handle_get("/api/history/compare?from=2026-05-14&to=2026-05-15")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.payload["available"])
        self.assertEqual(response.payload["from_date"], "2026-05-14")
        self.assertEqual(response.payload["to_date"], "2026-05-15")
        self.assertIn("New Theme", response.payload["themes"]["new"])
        self.assertIn("Removed Theme", response.payload["themes"]["removed"])
        changed = {item["theme"]: item for item in response.payload["themes"]["changed"]}
        self.assertEqual(changed["Storage"]["changes"]["score_delta"], 20.0)
        self.assertTrue(changed["Storage"]["changes"]["risk_changed"])
        self.assertTrue(changed["Storage"]["changes"]["data_status_changed"])
        self.assertEqual(response.payload["summary"]["new_themes_count"], 1)
        self.assertEqual(response.payload["summary"]["removed_themes_count"], 1)
        self.assertEqual(response.payload["summary"]["changed_themes_count"], 1)
        self.assertEqual(response.payload["candidates"]["etf"]["new"][0]["name"], "New ETF")
        self.assertEqual(response.payload["candidates"]["etf"]["repeated"][0]["name"], "Chip ETF")
        self.assertEqual(response.payload["candidates"]["stock"]["new"][0]["name"], "NewCo")
        self.assertEqual(response.payload["data_quality"]["missing_fetched_at_delta"], 2)
        self.assertGreaterEqual(response.payload["summary"]["weaker_data_quality_count"], 1)
        self.assertIn("Eastmoney", response.payload["sources"]["new"])
        self.assertIn("Yahoo", response.payload["sources"]["repeated"])

    def test_history_compare_defaults_from_to_previous_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_run(Path(tmpdir), "2026-05-14", [{"theme": "Storage"}])
            _write_run(Path(tmpdir), "2026-05-15", [{"theme": "Storage", "score": 2}])

            response = DailyReportApi(tmpdir).handle_get("/api/history/compare?to=2026-05-15")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.payload["available"])
        self.assertEqual(response.payload["from_date"], "2026-05-14")
        self.assertEqual(response.payload["to_date"], "2026-05-15")

    def test_history_compare_candidate_sort_with_none_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_run(
                Path(tmpdir),
                "2026-05-14",
                [
                    {
                        "theme": "Storage",
                        "etf_candidates": ["Chip ETF"],
                        "stock_candidates": [{"name": "OldCo", "code": None}],
                    },
                ],
            )
            _write_run(
                Path(tmpdir),
                "2026-05-15",
                [
                    {
                        "theme": "Storage",
                        "etf_candidates": [{"name": "Chip ETF", "code": "159995"}],
                        "stock_candidates": [{"name": "NewCo", "code": "000001"}],
                    },
                ],
            )

            response = DailyReportApi(tmpdir).handle_get("/api/history/compare?from=2026-05-14&to=2026-05-15")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.payload["available"])
        etf = response.payload["candidates"]["etf"]
        self.assertEqual(len(etf["new"]), 1)
        self.assertEqual(etf["new"][0]["name"], "Chip ETF")
        self.assertEqual(etf["new"][0]["code"], "159995")
        self.assertEqual(len(etf["removed"]), 1)
        self.assertEqual(etf["removed"][0]["name"], "Chip ETF")
        self.assertIsNone(etf["removed"][0]["code"])
        stock = response.payload["candidates"]["stock"]
        self.assertEqual(len(stock["new"]), 1)
        self.assertEqual(stock["new"][0]["name"], "NewCo")
        self.assertEqual(len(stock["removed"]), 1)
        self.assertEqual(stock["removed"][0]["name"], "OldCo")

    def test_artifacts_endpoint_returns_output_file_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_run(Path(tmpdir))
            response = DailyReportApi(tmpdir).handle_get("/api/runs/2026-05-15/artifacts")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.payload["date"], "2026-05-15")
        artifacts = {item["key"]: item for item in response.payload["artifacts"]}
        self.assertTrue(artifacts["dashboard_html"]["exists"])
        self.assertTrue(artifacts["dashboard_data_json"]["exists"])
        self.assertEqual(artifacts["dashboard_data_json"]["api"], "/api/runs/2026-05-15/dashboard-data")
        self.assertEqual(artifacts["run_diagnostics_html"]["relative_path"], "2026-05-15/run_diagnostics.html")
        self.assertIsInstance(artifacts["run_summary_json"]["size_bytes"], int)
        self.assertFalse(artifacts["report_md"]["exists"])
        self.assertIsNone(artifacts["report_md"]["size_bytes"])

    def test_dashboard_data_endpoint_returns_normalized_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_run(Path(tmpdir))
            response = DailyReportApi(tmpdir).handle_get("/api/runs/2026-05-15/dashboard-data")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.payload["schema_version"], "1.0")
        self.assertEqual(response.payload["run"]["date"], "2026-05-15")
        self.assertEqual(response.payload["signals"][0]["theme"], "storage chips")

    def test_run_summary_endpoint_returns_summary_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_run(Path(tmpdir))
            response = DailyReportApi(tmpdir).handle_get("/api/runs/2026-05-15/run-summary")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.payload["run_date"], "2026-05-15")
        self.assertEqual(response.payload["status"], "ok")

    def test_knowledge_review_endpoint_returns_html_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_run(Path(tmpdir))
            response = DailyReportApi(tmpdir).handle_get("/api/runs/2026-05-15/knowledge-review")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.payload["html_available"])
        self.assertEqual(response.payload["artifact_type"], "knowledge_review")
        self.assertIn("Knowledge Graph Review", response.payload["html"])

    def test_diagnostics_endpoint_returns_html_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_run(Path(tmpdir))
            response = DailyReportApi(tmpdir).handle_get("/api/runs/2026-05-15/diagnostics")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.payload["artifact_type"], "diagnostics")
        self.assertIn("Run Diagnostics", response.payload["html"])

    def test_missing_run_returns_404(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            response = DailyReportApi(tmpdir).handle_get("/api/runs/2026-05-15/dashboard-data")

        self.assertEqual(response.status_code, 404)
        self.assertIn("not found", response.payload["error"])

    def test_artifacts_endpoint_missing_run_returns_404(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            response = DailyReportApi(tmpdir).handle_get("/api/runs/2026-05-15/artifacts")

        self.assertEqual(response.status_code, 404)
        self.assertIn("not found", response.payload["error"])

    def test_invalid_date_blocks_path_traversal(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            api = DailyReportApi(tmpdir)
            response = api.handle_get("/api/runs/../dashboard-data")
            encoded = api.handle_get("/api/runs/2026-05-15%2F../dashboard-data")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(encoded.status_code, 404)

    def test_unknown_route_returns_404(self) -> None:
        response = DailyReportApi("reports/daily").handle_get("/api/unknown")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.payload["error"], "API route not found")

    def test_cli_exposes_serve_api_help(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-m", "market_impact_radar", "serve-api", "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("--reports-dir", completed.stdout)
        self.assertIn("--port", completed.stdout)

    def test_cli_exposes_console_smoke_help(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-m", "market_impact_radar", "console-smoke-check", "--help"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("--reports-dir", completed.stdout)
        self.assertIn("--date", completed.stdout)

    def test_http_api_smoke_serves_runs_route(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_run(Path(tmpdir))
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(tmpdir))
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                connection = HTTPConnection("127.0.0.1", server.server_port, timeout=5)
                connection.request("GET", "/api/runs")
                response = connection.getresponse()
                payload = json.loads(response.read().decode("utf-8"))
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertEqual(response.status, 200)
        self.assertEqual(payload["runs"][0]["date"], "2026-05-15")
        self.assertEqual(payload["runs"][0]["links"]["artifacts"], "/api/runs/2026-05-15/artifacts")
        self.assertEqual(payload["runs"][0]["links"]["run_summary"], "/api/runs/2026-05-15/run-summary")

    def test_http_api_smoke_serves_health_route(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(tmpdir))
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                connection = HTTPConnection("127.0.0.1", server.server_port, timeout=5)
                connection.request("GET", "/api/health")
                response = connection.getresponse()
                payload = json.loads(response.read().decode("utf-8"))
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertEqual(response.status, 200)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["version"], "v1")

    def test_http_api_smoke_serves_console_html(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(tmpdir))
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                connection = HTTPConnection("127.0.0.1", server.server_port, timeout=5)
                connection.request("GET", "/console")
                response = connection.getresponse()
                content_type = response.getheader("Content-Type")
                body = response.read().decode("utf-8")
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertEqual(response.status, 200)
        self.assertEqual(content_type, "text/html; charset=utf-8")
        self.assertIn("Market Impact Radar Console", body)
        self.assertIn("/api/runs", body)


if __name__ == "__main__":
    unittest.main()
