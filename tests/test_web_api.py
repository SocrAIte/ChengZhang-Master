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


def _write_run(root: Path, run_date: str = "2026-05-15") -> Path:
    run_dir = root / run_date
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "dashboard_data.json").write_text(
        json.dumps(
            {
                "schema_version": "1.0",
                "run": {"date": run_date, "status": "ok", "generated_at": "2026-05-15T01:00:00+00:00"},
                "summary": {"strong_signals": 1},
                "signals": [{"theme": "storage chips"}],
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
    def test_list_runs_returns_history_entries_with_api_links(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            _write_run(Path(tmpdir))
            response = DailyReportApi(tmpdir).handle_get("/api/runs")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.payload["schema_version"], "1.0")
        self.assertEqual(response.payload["runs"][0]["date"], "2026-05-15")
        self.assertEqual(response.payload["runs"][0]["links"]["dashboard_data"], "/api/runs/2026-05-15/dashboard-data")

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
        self.assertEqual(payload["runs"][0]["links"]["run_summary"], "/api/runs/2026-05-15/run-summary")


if __name__ == "__main__":
    unittest.main()
