# Read-only Daily Report API

The first web API checkpoint serves existing daily report bundle files through a small read-only HTTP API.

It does not run the daily pipeline, fetch market data, edit the knowledge graph, create a database, or provide trading advice.

## Start the API

```powershell
python -m market_impact_radar serve-api --host 127.0.0.1 --port 8000 --reports-dir reports/daily
```

The API reads from `reports/daily/` by default.

Open the minimal read-only console at:

```text
http://127.0.0.1:8000/console
```

The root path `/` serves the same console shell.

## Read-only Console

The console is a static HTML page served by the same process.

It uses the existing API endpoints to:

- list available daily runs from `GET /api/runs`
- load dashboard data from `GET /api/runs/{date}/dashboard-data`
- discover run output availability from `GET /api/runs/{date}/artifacts`
- show run status, summary fields, signals, candidates, risks, and raw `dashboard_data.json`

The console does not call `run-daily`, write files, fetch live market data, edit the knowledge graph, or compute new financial signals.

## Endpoints

### GET /api

Returns a lightweight endpoint index for the read-only API:

```json
{
  "service": "market_impact_radar",
  "api": "readonly",
  "api_version": "v1",
  "dashboard_schema_version": "1.0",
  "readonly_api": true,
  "endpoints": [
    {
      "method": "GET",
      "path": "/api/runs",
      "description": "Available daily report runs."
    }
  ],
  "openapi": "/api/openapi.json",
  "console": "/console"
}
```

This endpoint is for service discovery. It does not inspect market data, run the daily pipeline, or mutate files.

### GET /api/health

Returns a lightweight service health response:

```json
{
  "status": "ok",
  "service": "market_impact_radar",
  "api": "readonly",
  "version": "v1"
}
```

This endpoint only confirms that the API process can respond. It does not run `run-daily`, read live market data, or contact external quote sources.

### GET /api/version

Returns API and dashboard contract metadata:

```json
{
  "service": "market_impact_radar",
  "api_version": "v1",
  "dashboard_schema_version": "1.0",
  "readonly_api": true,
  "package_version": "0.1.0"
}
```

If the installed package version is unavailable, `package_version` is returned as `"unknown"` instead of failing the request.

### GET /api/openapi.json

Returns a minimal OpenAPI 3.1 document for the read-only endpoints.

This is intended as a lightweight contract for a future frontend console. It is not a generated client SDK and does not add any write capability.

### GET /api/runs

Returns the available daily runs discovered under `reports/daily/YYYY-MM-DD/`.

Each run includes status, generated time, summary, warnings, output metadata, and API links.

### GET /api/runs/{date}/dashboard-data

Returns normalized `dashboard_data.json` for the given date.

The response preserves the `dashboard_data.json` v1 contract and includes `schema_version = "1.0"`.

### GET /api/runs/{date}/artifacts

Returns a read-only file index for the run output directory:

```json
{
  "date": "2026-05-15",
  "run_dir": "reports/daily/2026-05-15",
  "artifacts": [
    {
      "key": "dashboard_data_json",
      "file_name": "dashboard_data.json",
      "kind": "json",
      "api": "/api/runs/2026-05-15/dashboard-data",
      "exists": true,
      "relative_path": "2026-05-15/dashboard_data.json",
      "size_bytes": 1234
    }
  ]
}
```

This endpoint only checks local output file availability. It does not read artifact contents, run the daily pipeline, or create missing files.

### GET /api/runs/{date}/run-summary

Returns `run_summary.json` for the given date.

### GET /api/runs/{date}/knowledge-review

Returns metadata and HTML content from `knowledge_review.html` for the given date.

### GET /api/runs/{date}/diagnostics

Returns metadata and HTML content from `run_diagnostics.html` for the given date.

## Date Format

`{date}` must use:

```text
YYYY-MM-DD
```

Invalid dates and path traversal attempts return a JSON 404 response.

## Non-goals

- No `POST /api/run-daily`.
- No online knowledge graph editing.
- No login system.
- No database.
- No frontend framework.
- No live market data requests.
- No financial signal recomputation in the API layer.
