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
        self.assertIn("Source Reliability", response.payload)
        self.assertIn("Source Detail Panel", response.payload)
        self.assertIn("Source Breakdown", response.payload)
        self.assertIn("Weak Evidence Signals", response.payload)
        self.assertIn("Historical Data Quality Trend", response.payload)
        self.assertIn("Theme Compare", response.payload)
        self.assertIn("Candidate Pool Comparison", response.payload)
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
