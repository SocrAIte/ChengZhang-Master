from __future__ import annotations

import json
import re
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from importlib import metadata
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from .dashboard_contract import DASHBOARD_SCHEMA_VERSION, normalize_dashboard_data
from .history_index import build_daily_history_index


SERVICE_NAME = "market_impact_radar"
READONLY_API_VERSION = "v1"
PACKAGE_NAME = "market-impact-radar"
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class WebApiError(RuntimeError):
    def __init__(self, status_code: int, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message


@dataclass(frozen=True)
class ApiResponse:
    status_code: int
    payload: dict[str, Any]


class DailyReportApi:
    def __init__(self, reports_dir: str | Path = "reports/daily") -> None:
        self.reports_dir = Path(reports_dir)

    def handle_get(self, raw_path: str) -> ApiResponse:
        path = urlparse(raw_path).path
        parts = [unquote(part) for part in path.strip("/").split("/") if part]
        try:
            if parts == ["api"]:
                return ApiResponse(200, self.index())
            if parts == ["api", "health"]:
                return ApiResponse(200, self.health())
            if parts == ["api", "openapi.json"]:
                return ApiResponse(200, self.openapi_spec())
            if parts == ["api", "version"]:
                return ApiResponse(200, self.version())
            if parts == ["api", "runs"]:
                return ApiResponse(200, self.list_runs())
            if len(parts) == 4 and parts[:2] == ["api", "runs"]:
                date = self._validate_date(parts[2])
                endpoint = parts[3]
                if endpoint == "dashboard-data":
                    return ApiResponse(200, self.dashboard_data(date))
                if endpoint == "run-summary":
                    return ApiResponse(200, self.run_summary(date))
                if endpoint == "knowledge-review":
                    return ApiResponse(200, self.html_artifact(date, "knowledge_review.html", "knowledge_review"))
                if endpoint == "diagnostics":
                    return ApiResponse(200, self.html_artifact(date, "run_diagnostics.html", "diagnostics"))
            raise WebApiError(404, "API route not found")
        except WebApiError as exc:
            return ApiResponse(exc.status_code, {"error": exc.message, "status": exc.status_code})

    def health(self) -> dict[str, Any]:
        return {
            "status": "ok",
            "service": SERVICE_NAME,
            "api": "readonly",
            "version": READONLY_API_VERSION,
        }

    def index(self) -> dict[str, Any]:
        return {
            "service": SERVICE_NAME,
            "api": "readonly",
            "api_version": READONLY_API_VERSION,
            "dashboard_schema_version": DASHBOARD_SCHEMA_VERSION,
            "readonly_api": True,
            "endpoints": _endpoint_catalog(),
            "openapi": "/api/openapi.json",
        }

    def openapi_spec(self) -> dict[str, Any]:
        date_parameter = {
            "name": "date",
            "in": "path",
            "required": True,
            "schema": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"},
            "description": "Daily run date in YYYY-MM-DD format.",
        }
        return {
            "openapi": "3.1.0",
            "info": {
                "title": "Market Impact Radar Read-only API",
                "version": READONLY_API_VERSION,
            },
            "x-readonly": True,
            "paths": {
                "/api": {"get": {"summary": "List read-only API endpoints."}},
                "/api/health": {"get": {"summary": "Check API process health."}},
                "/api/version": {"get": {"summary": "Return API and dashboard contract versions."}},
                "/api/openapi.json": {"get": {"summary": "Return this lightweight OpenAPI document."}},
                "/api/runs": {"get": {"summary": "List available daily report runs."}},
                "/api/runs/{date}/dashboard-data": {
                    "get": {
                        "summary": "Return normalized dashboard_data.json for a run.",
                        "parameters": [date_parameter],
                    }
                },
                "/api/runs/{date}/run-summary": {
                    "get": {
                        "summary": "Return run_summary.json for a run.",
                        "parameters": [date_parameter],
                    }
                },
                "/api/runs/{date}/knowledge-review": {
                    "get": {
                        "summary": "Return knowledge_review.html metadata and HTML content.",
                        "parameters": [date_parameter],
                    }
                },
                "/api/runs/{date}/diagnostics": {
                    "get": {
                        "summary": "Return run_diagnostics.html metadata and HTML content.",
                        "parameters": [date_parameter],
                    }
                },
            },
        }

    def version(self) -> dict[str, Any]:
        return {
            "service": SERVICE_NAME,
            "api_version": READONLY_API_VERSION,
            "dashboard_schema_version": DASHBOARD_SCHEMA_VERSION,
            "readonly_api": True,
            "package_version": _package_version(),
        }

    def list_runs(self) -> dict[str, Any]:
        index = build_daily_history_index(self.reports_dir)
        runs = []
        for item in index.get("runs", []):
            run = item if isinstance(item, dict) else {}
            date = str(run.get("date") or "")
            outputs = run.get("outputs") if isinstance(run.get("outputs"), dict) else {}
            runs.append(
                {
                    "date": date,
                    "status": run.get("status") or "unknown",
                    "generated_at": run.get("generated_at"),
                    "summary": run.get("summary") if isinstance(run.get("summary"), dict) else {},
                    "warnings": run.get("warnings") if isinstance(run.get("warnings"), list) else [],
                    "outputs": outputs,
                    "links": self._api_links(date) if self._is_valid_date(date) else {},
                }
            )
        return {
            "schema_version": "1.0",
            "reports_dir": str(self.reports_dir),
            "runs": runs,
        }

    def dashboard_data(self, date: str) -> dict[str, Any]:
        return normalize_dashboard_data(self._load_json(date, "dashboard_data.json"))

    def run_summary(self, date: str) -> dict[str, Any]:
        return self._load_json(date, "run_summary.json")

    def html_artifact(self, date: str, file_name: str, artifact_type: str) -> dict[str, Any]:
        path = self._run_dir(date) / file_name
        if not path.exists():
            raise WebApiError(404, f"{file_name} not found for run {date}")
        try:
            html = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise WebApiError(500, f"failed to read {file_name}: {exc}") from exc
        return {
            "date": date,
            "artifact_type": artifact_type,
            "file_name": file_name,
            "html_available": True,
            "html_path": str(path),
            "html": html,
        }

    def _load_json(self, date: str, file_name: str) -> dict[str, Any]:
        path = self._run_dir(date) / file_name
        if not path.exists():
            raise WebApiError(404, f"{file_name} not found for run {date}")
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise WebApiError(500, f"{file_name} is not valid JSON: {exc}") from exc
        except OSError as exc:
            raise WebApiError(500, f"failed to read {file_name}: {exc}") from exc
        if not isinstance(payload, dict):
            raise WebApiError(500, f"{file_name} must contain a JSON object")
        return payload

    def _run_dir(self, date: str) -> Path:
        return self.reports_dir / self._validate_date(date)

    def _validate_date(self, date: str) -> str:
        if not self._is_valid_date(date):
            raise WebApiError(404, "run date must use YYYY-MM-DD")
        return date

    def _is_valid_date(self, date: str) -> bool:
        return bool(_DATE_RE.match(date))

    def _api_links(self, date: str) -> dict[str, str]:
        return {
            "dashboard_data": f"/api/runs/{date}/dashboard-data",
            "run_summary": f"/api/runs/{date}/run-summary",
            "knowledge_review": f"/api/runs/{date}/knowledge-review",
            "diagnostics": f"/api/runs/{date}/diagnostics",
        }


def make_handler(reports_dir: str | Path = "reports/daily") -> type[BaseHTTPRequestHandler]:
    api = DailyReportApi(reports_dir)

    class DailyReportApiHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            response = api.handle_get(self.path)
            body = json.dumps(response.payload, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(response.status_code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: Any) -> None:
            return None

    return DailyReportApiHandler


def serve_api(host: str = "127.0.0.1", port: int = 8000, reports_dir: str | Path = "reports/daily") -> None:
    server = ThreadingHTTPServer((host, port), make_handler(reports_dir))
    try:
        print(f"Daily report API serving {Path(reports_dir)} at http://{host}:{port}")
        server.serve_forever()
    finally:
        server.server_close()


def _package_version() -> str:
    try:
        return metadata.version(PACKAGE_NAME)
    except metadata.PackageNotFoundError:
        return "unknown"


def _endpoint_catalog() -> list[dict[str, str]]:
    return [
        {"method": "GET", "path": "/api", "description": "Read-only API endpoint index."},
        {"method": "GET", "path": "/api/health", "description": "Lightweight API health check."},
        {"method": "GET", "path": "/api/version", "description": "API and dashboard contract versions."},
        {"method": "GET", "path": "/api/openapi.json", "description": "Lightweight OpenAPI description."},
        {"method": "GET", "path": "/api/runs", "description": "Available daily report runs."},
        {"method": "GET", "path": "/api/runs/{date}/dashboard-data", "description": "Dashboard data JSON."},
        {"method": "GET", "path": "/api/runs/{date}/run-summary", "description": "Run summary JSON."},
        {"method": "GET", "path": "/api/runs/{date}/knowledge-review", "description": "Knowledge review HTML payload."},
        {"method": "GET", "path": "/api/runs/{date}/diagnostics", "description": "Run diagnostics HTML payload."},
    ]
