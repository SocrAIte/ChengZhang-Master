# Daily Pipeline Runbook

`run-daily` is the project checkpoint command for the daily cross-market radar workflow. It gathers or loads market snapshots, runs the existing signal pipeline, writes standard JSON outputs, and renders a static dashboard for review.

It does not change financial scoring logic, knowledge graph mappings, or signal rules.

## Basic Command

```powershell
python -m market_impact_radar run-daily
```

By default, outputs are written to:

```text
reports/daily/YYYY-MM-DD/
```

The historical entry point is:

```text
reports/daily/index.html
```

## Sample Command

Use this sample-data command for local verification:

```powershell
python -m market_impact_radar run-daily --date 2026-05-15 --external data\sample_external_snapshot.json --context data\sample_a_share_context.json --scoring-rules data\scoring_rules.json --a-share-snapshot data\a_share_snapshot.sample.json --skip-knowledge
```

## Inputs

- `--date`: Run date used for the output directory. If omitted, local today is used.
- `--external`: Existing external market snapshot JSON. If omitted, live external quotes are fetched.
- `--context`: Optional A-share context JSON used by the scoring pipeline.
- `--historical-edges`: Optional historical transmission edge JSON.
- `--scoring-rules`: Scoring rule JSON, normally `data\scoring_rules.json`.
- `--a-share-watchlist`: Watchlist used when fetching A-share snapshots.
- `--a-share-snapshot`: Existing A-share intraday snapshot JSON. If omitted, live A-share data is fetched.
- `--generated-dir`: Knowledge verification cache directory.
- `--sources`: External quote sources, comma-separated.
- `--symbols`: External symbols, comma-separated.
- `--proxy`: Optional HTTP/HTTPS proxy.

## Outputs

Each run writes:

```text
reports/daily/YYYY-MM-DD/
  run_summary.json
  dashboard_data.json
  dashboard.html
  knowledge_review.html
  run_diagnostics.html
```

`run-daily` also refreshes:

```text
reports/daily/index.json
reports/daily/index.html
```

### run_summary.json

`run_summary.json` is the operational run log. It records:

- run date
- generated time
- overall status
- step status for external data, pipeline, A-share data, intraday validation, knowledge checks, and dashboard contract checks
- warnings
- output file paths

### dashboard_data.json

`dashboard_data.json` is the stable data contract consumed by the dashboard. It uses:

```json
{
  "schema_version": "1.0"
}
```

The top-level v1 fields are:

- `schema_version`
- `run`
- `market_context`
- `summary`
- `signals`
- `knowledge`
- `outputs`

Fields may be `null`, empty arrays, `0`, or `"unknown"` when data is unavailable. Missing fields are normalized before writing.

### dashboard.html

`dashboard.html` is rendered from `dashboard_data.json` by the existing dashboard module. The HTML displays the daily run summary, signal overview, market context, signal evidence, ETF and stock candidates, knowledge graph status, and output links. It also links to `knowledge_review.html` when available. It includes local-only search, filter chips, field filters, sorting, and visible signal counts for browsing rendered signals. It only presents existing data and does not recompute financial signals.

### knowledge_review.html

`knowledge_review.html` is a fixed read-only knowledge graph review entry for every daily run. It renders the existing knowledge check and mapping fix suggestions into a static HTML view.

It shows:

- review status and high / medium / low / total issue counts
- issues grouped by severity
- fix suggestions, confidence, source, and warnings when present
- a clean state when no issues are present
- a skipped or not available state when knowledge verification was skipped or missing

This page does not automatically modify `data/mappings.json` and does not provide online editing. It is generated even when `--skip-knowledge` is used; skipped runs should show a skipped or not available state instead of omitting the page.

The page is discoverable from:

- the Knowledge Graph section in `dashboard.html`
- each daily row in `reports/daily/index.html`
- the `daily-report-preview` CI artifact
- the `browser-smoke-daily-report-preview` CI artifact
- the manual GitHub Pages preview deployment

### run_diagnostics.html

`run_diagnostics.html` is a read-only run diagnostics page rendered from `run_summary.json`.

It is used to inspect:

- daily run status, date, generated time, output directory, and warning count
- pipeline step status, including `ok`, `partial`, `skipped`, `failed`, and `unknown`
- data source health for foreign quotes, A-share snapshots, signals, intraday validation, and knowledge checks when those fields are present
- top-level and step-level warnings / errors
- generated output file links

This page is a diagnostic view only. It does not recompute signals, modify data sources, or repair any failures.

### History Index

`reports/daily/index.html` is a static list of available daily runs. It links to each date's `dashboard.html`, `knowledge_review.html`, `run_diagnostics.html`, `dashboard_data.json`, `run_summary.json`, and `report.md` when present.

You can rebuild it manually:

```powershell
python -m market_impact_radar build-history-index --reports-dir reports/daily
```

If automatic history index refresh fails during `run-daily`, the daily run still keeps its core outputs and records the index warning in `run_summary.json`.

## Skip Options

- `--skip-a-share`: Skip A-share snapshot loading/fetching and intraday validation. Signals should display `not_checked` rather than confirmed or failed.
- `--skip-knowledge`: Skip knowledge graph verification. The dashboard should display knowledge status as not checked, and `knowledge_review.html` should show a skipped or not available state rather than being missing.

## Status Meanings

- `ok`: The step completed with usable data.
- `partial`: The step completed but some data was missing, stale, divergent, or otherwise degraded.
- `skipped`: The step was intentionally skipped by command options.
- `error` or `failed`: The step could not complete.

Do not treat `partial` as a clean pass. Do not show `skipped` as `failed`.

## Troubleshooting

- If live quote requests fail, rerun with sample snapshots to isolate network issues.
- If A-share data is empty, check proxy settings and whether A-share markets are open.
- If `dashboard_data.json` is missing `schema_version`, run tests and inspect the dashboard contract path.
- If a run is `partial`, inspect `run_summary.json.warnings`.
- If `dashboard.html` renders but signals are empty, inspect `dashboard_data.json.signals`.
- If knowledge graph is skipped, this is expected when `--skip-knowledge` is used.
