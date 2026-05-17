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

The console also supports shareable query state, for example:

```text
http://127.0.0.1:8000/console?date=2026-05-15&search=nvidia&risk=high&status=confirmed&sort=score_desc&view=grouped&compare=存储芯片,光模块
```

Run a real browser smoke check for the console with:

```powershell
python -m market_impact_radar console-smoke-check --reports-dir reports/daily/pre-release-check --date 2026-05-15
```

This starts a temporary local API server, opens `/console` with Playwright, and checks that runs, dashboard data, and artifacts render. It is optional and not part of the default pre-release check.

## Read-only Console

The console is a static HTML page served by the same process.

It uses the existing API endpoints to:

- list available daily runs from `GET /api/runs`
- load dashboard data from `GET /api/runs/{date}/dashboard-data`
- discover run output availability from `GET /api/runs/{date}/artifacts`
- select a run date and refresh the run list
- search signals and filter them by risk or intraday status
- group signals by theme and switch back to a flat signal list
- sort signals by default order, score, risk, intraday status, or theme name
- preserve console state in the URL for `date`, `search`, `risk`, `status`, `sort`, and `view`
- show a Morning Brief with current run counts, strongest visible themes, risk notes, data quality notes, recurring themes, and recurring observation candidates
- show a Theme Hotlist based on the currently visible signals
- compare up to 3 themes side by side in Theme Compare
- show Candidate Pool Comparison for repeated ETF and stock observation candidates across compared themes
- show a Signal Detail Panel for the selected visible signal
- explain the Evidence Chain from external triggers to A-share mapping, candidate pools, risk notes, and data quality
- show Data Quality / Freshness labels from existing `data_status`, `sources`, `fetched_at`, and fallback metadata
- render ETF observation pool and Stock observation pool tables from the existing candidate fields
- show an API status strip with health, API version, dashboard schema version, selected run, signal counts, and generated time
- show Artifact Links for available report outputs
- show Historical Review for recurring themes, observation candidates, and data quality trend from existing daily runs
- support Theme Detail Drilldown from Theme Hotlist, Historical Theme Trends, signal cards, and grouped theme headers
- preserve selected theme state with the `theme` query parameter for shareable theme views
- preserve compared theme state with the `compare` query parameter for shareable compare views
- show run status, summary fields, signals, candidates, risks, and raw `dashboard_data.json`
- show Dashboard, Knowledge Review, Run Diagnostics, and raw JSON artifact availability

The URL state is only a browser-side view preference. It makes a filtered observation view easier to share, but it does not call `run-daily`, write files, fetch live market data, edit the knowledge graph, compute new financial signals, or provide trading instructions.

Historical Review is a research view over existing daily report files. It does not calculate returns, profit, win rate, alpha, entry points, exits, or target prices.

Supported query parameters:

- `date`: selected daily run date.
- `search`: signal search text.
- `risk`: `low`, `medium`, `high`, or `unknown`; `all` is treated as the default empty filter.
- `status`: `confirmed`, `downgraded`, `missing_data`, `failed`, `not_checked`, or `unknown`; `all` is treated as the default empty filter.
- `sort`: `default`, `score_desc`, `risk_level`, `intraday_status`, or `theme`.
- `view`: `grouped` or `flat`.
- `theme`: selected theme for Theme Detail Drilldown.
- `compare`: comma-separated themes for Theme Compare, capped at 3 themes.

Unknown query values fall back to safe defaults. Empty/default values are omitted from the URL when controls change.

Theme Detail Drilldown combines the selected run's visible signals with historical theme and candidate summaries. It shows current signals, historical observation counts, risk/status/data quality distributions, recent dates, external trigger summaries, and ETF / stock observation pools. It remains a research view and does not show return, profit, win-rate, alpha, entry, exit, or target-price metrics.

Insight Workspace v2 adds Morning Brief, Theme Compare, and Candidate Pool Comparison. These views are rule-based summaries over existing local JSON outputs and read-only history APIs. They show signal counts, status distributions, risk distributions, data quality labels, external trigger summaries, and observation pool overlap. They do not call external models, trigger `run-daily`, fetch live market data, or change mappings.

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

### GET /api/history/themes

Returns a read-only summary of themes observed across local `reports/daily/YYYY-MM-DD/dashboard_data.json` files.

It reports observation counts such as `signal_count`, `runs_seen`, `avg_score`, `max_score`, risk counts, intraday status counts, data status counts, external triggers, candidate counts, and recent dates. Missing themes are grouped under `Unknown Theme`.

This endpoint skips missing or invalid `dashboard_data.json` files. It does not fetch live data, run `run-daily`, recompute financial signals, or report trading performance.

### GET /api/history/candidates

Returns read-only frequency summaries for ETF and stock observation candidates seen in local daily runs.

It supports candidates represented as strings or objects, and reports `appearances`, related `themes`, recent dates, and last seen date. It is an observation-pool summary, not a recommendation list.

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
- No return, profit, win-rate, alpha, entry, exit, or target-price reporting.
