# Read-only Daily Report API

The first web API checkpoint serves existing daily report bundle files through a small read-only HTTP API.

It does not run the daily pipeline, fetch market data, edit the knowledge graph, create a database, or provide trading advice.

## Start the API

```powershell
python -m market_impact_radar serve-api --host 127.0.0.1 --port 8000 --reports-dir reports/daily
```

The API reads from `reports/daily/` by default.

## Endpoints

### GET /api/runs

Returns the available daily runs discovered under `reports/daily/YYYY-MM-DD/`.

Each run includes status, generated time, summary, warnings, output metadata, and API links.

### GET /api/runs/{date}/dashboard-data

Returns normalized `dashboard_data.json` for the given date.

The response preserves the `dashboard_data.json` v1 contract and includes `schema_version = "1.0"`.

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
