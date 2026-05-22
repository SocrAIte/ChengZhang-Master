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
http://127.0.0.1:8000/console?date=2026-05-15&search=nvidia&risk=high&status=confirmed&sort=score_desc&view=grouped&compare=storage%20chips,CPO
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
- show Source Reliability for current run source coverage, evidence freshness, fallback use, weak evidence signals, and historical data quality trend
- support Source Detail from Source Breakdown, Weak Evidence Signals, and Signal Detail Panel
- show Theme x Source Matrix, Matrix Summary, Cell Detail, and Weak Evidence Cells for theme-source evidence review
- show Source Breakdown grouped by current run `source` / `sources`
- show Weak Evidence Signals that need verification because source, fetched time, fallback, or data status metadata is incomplete
- show Workspace Navigation with stable section anchors for Morning Brief, controls, source reliability, the theme-source matrix, comparison, history, signal explorer, detail panels, and artifacts
- support hash anchors such as `#theme-source-matrix` and `#source-detail` without clearing query state
- organize major sections with short descriptions, collapsible long sections, empty states, and Back to top links
- use consistent section cards, compact tables, and semantic status badges for risk, intraday status, data quality, weak evidence, and unknown values
- build a Daily Research Brief from the current browser state, visible signals, watch themes, evidence chains, observation candidates, risks, and data quality notes
- switch the Daily Research Brief between English and Chinese output templates
- switch the Daily Research Brief between Full Brief and Compact Brief
- enable or disable brief sections before copying
- copy the Daily Research Brief as Markdown or plain text in the browser without saving it to the server
- show a Research Review Queue that consolidates weak evidence, source gaps, freshness gaps, theme-source matrix gaps, and date-compare notes into a read-only review checklist
- compose browser-local Research Notes from review items, evidence gaps, date-over-date changes, candidate pool notes, data quality notes, open questions, follow-up checks, and optional manual notes
- show a Console Usage Guide with a recommended workflow: Morning Brief, Research Review Queue, Theme x Source Matrix, Date Compare, Research Notes, and detail panels
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
- preserve selected source state with the `source` query parameter for shareable source detail views
- preserve selected matrix cell with `matrixTheme` and `matrixSource` query parameters
- preserve compared theme state with the `compare` query parameter for shareable compare views
- compare two local daily runs with Date Compare and the `compareFrom` / `compareTo` query parameters
- include Date-over-Date Changes in the Daily Research Brief when comparison data is available
- show run status, summary fields, signals, candidates, risks, and raw `dashboard_data.json`
- show Dashboard, Knowledge Review, Run Diagnostics, and raw JSON artifact availability

The URL state is only a browser-side view preference. It makes a filtered observation view easier to share, but it does not call `run-daily`, write files, fetch live market data, edit the knowledge graph, compute new financial signals, or provide trading instructions.

The console information architecture is read-only. Workspace Navigation jumps between local page anchors and does not call write endpoints or rerun analysis. Long historical and artifact sections may be collapsed with native browser controls, while the primary observation sections remain visible.

The console readability layer uses lightweight static HTML and CSS only. Section Cards separate major research areas, Status Badges label evidence and risk metadata, Collapsible Sections keep long history and artifact content scannable, and Back to Top links help navigate the long page. These visual cues do not create trading actions or change the underlying analysis data.

Daily Research Brief Builder is a browser-local summary tool. It uses the already loaded run data, current filters, selected theme, compared themes, selected source, review queue items, history summaries, source reliability data, and theme-source matrix metadata to generate a copyable research note. It supports English / Chinese templates, Full / Compact modes, section toggles, Copy as Markdown, and Copy as Plain Text. The `briefLang` and `briefMode` query parameters can restore a shared brief view. The builder does not save content, call write APIs, trigger `run-daily`, fetch live market data, or produce trading instructions.

Console Usage Guide is a lightweight navigation aid for the research workspace. It suggests a daily workflow: read Morning Brief, check Research Review Queue, review Theme x Source Matrix, use Date Compare, generate Research Notes, and then drill into Theme / Source / Signal Detail when needed. It is informational only and does not trigger `run-daily`, fetch live market data, save notes, or provide market instructions.

Research Review Queue is a browser-local review checklist. It derives items from already loaded signals, source reliability metadata, weak evidence reasons, theme-source matrix weak cells, and date-compare summaries. It supports severity, category, and scope filters with `reviewSeverity`, `reviewCategory`, and `reviewScope` URL state. The default display shows the top 10 review items to keep first-pass review manageable. Review items are research follow-up prompts only; they do not create tasks on the server, modify data, or recommend market actions.

Research Notes Composer is a browser-local working note area for review workflow. It can include context, watch themes, review items, evidence gaps, date-over-date changes, candidate pool notes, data quality notes, open questions, follow-up checks, and optional manual notes entered in the page. Manual notes are kept only in the current browser view and are included when copying research notes; they are not saved to the server. Notes can be copied as Markdown or plain text. They do not trigger `run-daily`, do not fetch live market data, and are not a market action plan.

Historical Review is a research view over existing daily report files. It does not calculate entry points, exits, or pricing claims.

Supported query parameters:

- `date`: selected daily run date.
- `search`: signal search text.
- `risk`: `low`, `medium`, `high`, or `unknown`; `all` is treated as the default empty filter.
- `status`: `confirmed`, `downgraded`, `missing_data`, `failed`, `not_checked`, or `unknown`; `all` is treated as the default empty filter.
- `sort`: `default`, `score_desc`, `risk_level`, `intraday_status`, or `theme`.
- `view`: `grouped` or `flat`.
- `theme`: selected theme for Theme Detail Drilldown.
- `source`: selected source for Source Detail.
- `matrixTheme`: selected theme for Theme x Source Matrix Cell Detail.
- `matrixSource`: selected source for Theme x Source Matrix Cell Detail.
- `compare`: comma-separated themes for Theme Compare, capped at 3 themes.
- `compareFrom`: baseline run date for Date Compare.
- `compareTo`: current run date for Date Compare.
- `briefLang`: `en` or `zh` for the Daily Research Brief language.
- `briefMode`: `full` or `compact` for the Daily Research Brief length.
- `reviewSeverity`: `high`, `medium`, `low`, or `info` for Research Review Queue filtering.
- `reviewCategory`: review queue category such as `weak_evidence`, `missing_source`, `missing_fetched_at`, `stale_or_partial_data`, `fallback_used`, `high_risk_with_weak_data`, `date_compare_change`, `candidate_pool_change`, or `theme_source_gap`.
- `reviewScope`: `visible` for the current filtered signal set or `all` for the current run plus history-derived review items.
- `notesLang`: `en` or `zh` for Research Notes Composer language.
- `notesMode`: `full` or `compact` for Research Notes Composer length.

Unknown query values fall back to safe defaults. Empty/default values are omitted from the URL when controls change.

Theme Detail Drilldown combines the selected run's visible signals with historical theme and candidate summaries. It shows current signals, historical observation counts, risk/status/data quality distributions, recent dates, external trigger summaries, and ETF / stock observation pools. It remains a research view and does not show trading performance, entry, exit, or pricing metrics.

Insight Workspace v2 adds Morning Brief, Theme Compare, and Candidate Pool Comparison. These views are rule-based summaries over existing local JSON outputs and read-only history APIs. They show signal counts, status distributions, risk distributions, data quality labels, external trigger summaries, and observation pool overlap. They do not call external models, trigger `run-daily`, fetch live market data, or change mappings.

Source Reliability adds a dedicated data quality review. It summarizes current run `data_status`, `source` / `sources`, `fetched_at`, fallback metadata, weak evidence signals, and historical data quality observations from `GET /api/history/data-quality`. Source Detail uses `GET /api/history/sources` to show source coverage, dates, example signals, source-level distributions, and conservative reliability notes. These are evidence quality hints only, not trading signals.

Theme x Source Matrix uses `GET /api/history/theme-source-matrix` to show which sources support which themes, where evidence metadata is missing, and which theme-source cells need review. Matrix cells expose source coverage, data status counts, missing `fetched_at`, fallback counts, recent dates, and example signals. The matrix is an evidence review view and does not decide whether a theme is investable.

Date Compare uses `GET /api/history/compare` to compare two local daily runs. It highlights new watch themes, themes no longer present in the current watch list, changed signal scores, risk/status/data-quality changes, observation candidate changes, and source coverage changes. Score delta is only a signal score change; it is not a return, performance, or pricing metric.

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

### GET /api/history/data-quality

Returns a read-only summary of data quality metadata observed across local `reports/daily/YYYY-MM-DD/dashboard_data.json` files.

It reports `data_status_counts`, `source_counts`, missing source count, missing `fetched_at` count, fallback count, and themes with weak data metadata. Missing sources are grouped under `Unknown Source`.

This endpoint only reads local daily report files. It does not treat data quality as a trading signal and does not fetch live data or run `run-daily`.

### GET /api/history/sources

Returns read-only source detail summaries from local daily report files.

Each source row includes signal count, covered themes, covered dates, recent dates, last seen date, latest `fetched_at`, data status counts, risk counts, intraday status counts, fallback count, missing source count, missing `fetched_at` count, weak signal count, and a small set of recent example signals. Missing source metadata is grouped under `Unknown Source`.

This endpoint is for source coverage and evidence quality review. It does not fetch live data, trigger `run-daily`, edit mappings, or provide trading guidance.

### GET /api/history/theme-source-matrix

Returns a read-only theme-source evidence matrix from local daily report files.

The response includes theme summaries, source summaries, matrix cells, and weak evidence cells. Each cell reports signal count, data status counts, missing `fetched_at`, fallback count, weak signal count, recent dates, last seen date, latest `fetched_at`, and up to 3 recent example signals.

Missing themes are grouped under `Unknown Theme`, and missing sources are grouped under `Unknown Source`. Weak cells mean the evidence metadata needs review; they do not represent trading signals or performance metrics.

### GET /api/history/compare

Returns a read-only date-over-date comparison between two local daily runs.

Example:

```text
GET /api/history/compare?from=2026-05-14&to=2026-05-15
```

If `from` is omitted, the API uses the closest earlier local run before `to`. If either side is unavailable, the response returns `available = false` with notes instead of failing.

The response includes:

- `summary`: signal counts, new/removed/changed theme counts, new observation candidate counts, and data-quality change counts.
- `themes`: new, removed, and changed watch themes with score, risk, intraday status, and data status changes.
- `candidates`: ETF and stock observation candidate changes grouped as new, removed, and repeated.
- `data_quality`: `data_status` counts, missing source delta, missing `fetched_at` delta, fallback delta, and themes with weaker or improved evidence metadata.
- `sources`: new, removed, and repeated source names.

This endpoint only reads local `dashboard_data.json` files. It does not fetch live data, trigger `run-daily`, change mappings, or report trading performance.

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
- No trading performance, entry, exit, or pricing-metric reporting.
