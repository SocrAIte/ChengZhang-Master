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

`dashboard.html` is rendered from `dashboard_data.json` by the existing dashboard module. The HTML displays the daily run summary, signal overview, market context, signal evidence, ETF and stock candidates, knowledge graph status, and output links. It also includes local-only search, filter chips, field filters, sorting, and visible signal counts for browsing rendered signals. It only presents existing data and does not recompute financial signals.

## Skip Options

- `--skip-a-share`: Skip A-share snapshot loading/fetching and intraday validation. Signals should display `not_checked` rather than confirmed or failed.
- `--skip-knowledge`: Skip knowledge graph verification. The dashboard should display knowledge status as not checked.

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
