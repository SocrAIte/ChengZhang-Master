# feat: add read-only web API and console

## Summary

Adds a small read-only Web API and minimal static console for the existing daily report bundle.

This turns the generated daily files into a local HTTP-readable service while keeping the current pipeline and financial logic unchanged.

## Key Features

- Adds `serve-api` for local read-only HTTP access.
- Adds health and version endpoints.
- Adds API discovery and a lightweight OpenAPI document.
- Adds run list and per-run JSON/HTML artifact endpoints.
- Adds a static `/console` page that reads existing API data.
- Adds an artifact index endpoint for dashboard, diagnostics, knowledge review, and raw output files.
- Adds optional Playwright console smoke verification.

## API Endpoints

- `GET /api`
- `GET /api/health`
- `GET /api/version`
- `GET /api/openapi.json`
- `GET /api/runs`
- `GET /api/runs/{date}/dashboard-data`
- `GET /api/runs/{date}/run-summary`
- `GET /api/runs/{date}/knowledge-review`
- `GET /api/runs/{date}/diagnostics`
- `GET /api/runs/{date}/artifacts`

## Console

The console is available at:

```text
/console
/
```

It displays:

- daily run list
- selected run summary
- signal list
- ETF and stock candidates
- risks
- artifact availability
- raw `dashboard_data.json`

## Quality Gates

Local checks:

- `python -m unittest tests.test_web_api`
- `python -m unittest tests.test_browser_smoke`
- `python -m unittest discover -s tests`
- `python -m market_impact_radar pre-release-check`
- `python -m market_impact_radar pre-release-check --with-browser`
- `python -m market_impact_radar console-smoke-check --reports-dir reports/daily/pre-release-check --date 2026-05-15`

Remote checks:

- GitHub Actions Pre-release Check on `feat-readonly-web-api`

## Non-goals

- No `POST /api/run-daily`.
- No automatic trading.
- No guaranteed investment advice.
- No production deployment.
- No authentication or authorization.
- No database.
- No online knowledge graph editing.
- No live quote fetching from the API layer.
- No changes to financial signal, scoring, knowledge graph, or daily pipeline logic.
- No changes to the required `dashboard_data.json` v1 structure.

## Risks

- The console is intentionally minimal and static; it is not a full frontend app.
- The API serves local generated files and depends on daily report outputs already existing.
- `console-smoke-check` requires Playwright and Chromium in the local environment.
- CORS is not configured because there is not yet a separate frontend origin.

## Follow-up Work

- Add date selector and refresh controls to `/console`.
- Add clearer empty/error states to the console.
- Add a manual GitHub Actions workflow for console smoke if browser coverage is needed remotely.
- Add CORS only when a separate frontend app is introduced.
