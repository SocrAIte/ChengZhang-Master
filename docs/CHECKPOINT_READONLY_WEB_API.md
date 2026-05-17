# Read-only Web API Checkpoint

## Goal

This checkpoint turns the static daily report bundle into a small read-only web service that a future frontend console can consume.

It keeps the current architecture conservative:

- existing daily pipeline still generates files
- the API only reads generated files
- the console only calls read-only API endpoints
- no database, login, write API, or live market data request is introduced

## Branch

Current feature branch:

```text
feat-readonly-web-api
```

This branch was started from the current mainline checkpoint branch:

```text
feature-a-share-data-calendar
```

## Completed Capabilities

- `serve-api` command starts a local read-only HTTP API.
- `GET /api/health` returns lightweight service health.
- `GET /api/version` returns API and dashboard contract metadata.
- `GET /api` returns endpoint discovery metadata.
- `GET /api/openapi.json` returns a minimal OpenAPI 3.1 document.
- `GET /api/runs` lists daily runs from `reports/daily`.
- `GET /api/runs/{date}/dashboard-data` returns normalized `dashboard_data.json`.
- `GET /api/runs/{date}/run-summary` returns `run_summary.json`.
- `GET /api/runs/{date}/knowledge-review` returns `knowledge_review.html` content.
- `GET /api/runs/{date}/diagnostics` returns `run_diagnostics.html` content.
- `GET /api/runs/{date}/artifacts` returns available output files and API links.
- `/console` serves a minimal static read-only console.
- `/` serves the same console shell.
- `console-smoke-check` opens the console with Playwright and verifies the main read-only sections.

## Read-only Console

The console is intentionally small and framework-free. It reads:

- `GET /api/runs`
- `GET /api/runs/{date}/dashboard-data`
- `GET /api/runs/{date}/artifacts`

It displays:

- run list
- selected run summary
- signals
- ETF and stock candidates
- risks
- raw `dashboard_data.json`
- artifact availability for dashboard, diagnostics, knowledge review, and raw JSON files

## Non-goals

This checkpoint does not include:

- `POST /api/run-daily`
- online knowledge graph editing
- authentication or authorization
- database persistence
- React, Vue, Next.js, or another frontend framework
- live quote fetching from the API layer
- financial signal recomputation in the API or console
- automatic trading or investment advice

## Quality Gates

Local checks used for this checkpoint:

```powershell
conda run -n market_impact_radar python -m unittest tests.test_web_api
conda run -n market_impact_radar python -m unittest tests.test_browser_smoke
conda run -n market_impact_radar python -m unittest discover -s tests
conda run -n market_impact_radar python -m market_impact_radar pre-release-check
conda run -n market_impact_radar python -m market_impact_radar pre-release-check --with-browser
conda run -n market_impact_radar python -m market_impact_radar console-smoke-check --reports-dir reports/daily/pre-release-check --date 2026-05-15
```

Remote check:

- GitHub Actions Pre-release Check on `feat-readonly-web-api`

## Merge Readiness Checklist

- [ ] Working tree is clean.
- [ ] Branch is `feat-readonly-web-api`.
- [ ] Full unittest suite passes.
- [ ] `pre-release-check` passes.
- [ ] `pre-release-check --with-browser` passes.
- [ ] `console-smoke-check` passes locally when Playwright is installed.
- [ ] GitHub Actions Pre-release Check passes on the latest commit.
- [ ] API remains read-only.
- [ ] `dashboard_data.json` v1 required structure is unchanged.
- [ ] No financial signal, scoring, knowledge graph, or daily pipeline logic was changed.

## Follow-up Work

- Add a small refresh button and date selector to `/console`.
- Add a dedicated API console CI workflow if the team wants browser smoke coverage in GitHub Actions.
- Add CORS only when a separate frontend origin exists.
- Consider a typed API client only after the API surface stabilizes.
