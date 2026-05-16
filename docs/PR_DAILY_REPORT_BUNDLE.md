# PR Draft: Daily Report Bundle

## Title

feat: add daily report bundle and quality gates

## Summary

This PR adds a stable static daily report bundle for the cross-market radar workflow. It introduces a daily orchestration command, a versioned dashboard data contract, static report pages, local quality gates, CI preview artifacts, and optional browser smoke validation.

This is a reporting and verification checkpoint. It does not add automatic trading, guaranteed investment recommendations, or production deployment.

## Key Features

- Adds `python -m market_impact_radar run-daily`.
- Writes daily outputs under `reports/daily/YYYY-MM-DD/`.
- Defines `dashboard_data.json` schema version `1.0`.
- Renders a static `dashboard.html` from `dashboard_data.json`.
- Adds read-only `knowledge_review.html`.
- Adds read-only `run_diagnostics.html`.
- Adds `reports/daily/index.html` and `index.json` as the history entry point.
- Adds shared navigation across the daily report bundle.
- Adds `python -m market_impact_radar pre-release-check`.
- Adds optional Playwright browser smoke check with `--with-browser`.

## Generated Outputs

Sample daily run output:

- `run_summary.json`
- `dashboard_data.json`
- `dashboard.html`
- `knowledge_review.html`
- `run_diagnostics.html`
- `report.md`, when available

History output:

- `reports/daily/index.json`
- `reports/daily/index.html`

## Quality Gates

Local baseline:

```powershell
python -m unittest discover -s tests
python -m market_impact_radar pre-release-check
```

Optional browser smoke:

```powershell
python -m market_impact_radar pre-release-check --with-browser
```

The browser smoke check covers:

- `index.html`
- `dashboard.html`
- `knowledge_review.html`
- `run_diagnostics.html`

## CI / Pages Preview

- `pre-release-check.yml` runs unittest and `pre-release-check --skip-tests`.
- `browser-smoke-check.yml` is a manual Playwright browser smoke workflow.
- `pages-preview.yml` is a manual sample static Pages preview workflow.
- CI uploads daily report preview artifacts for inspection.

The Pages preview deploys only the sample `reports/daily/pre-release-check/` bundle. It is not production data or a production deployment.

## Tests

Covered areas include:

- daily runner outputs
- dashboard data schema normalization and validation
- dashboard rendering
- history index generation
- knowledge review rendering
- run diagnostics rendering
- pre-release checks
- browser smoke check behavior
- project process docs

## Risks

- Remote workflow status must be checked on the pushed commit before merging.
- Browser smoke depends on Playwright / Chromium in the environment where it runs.
- The report bundle is static and sample-driven in CI; it does not validate live market data availability.
- Pages Preview is a sample preview, not production deployment.

## Follow-up Work

- Push the latest branch and verify GitHub Actions on the current commit.
- Open a PR after Pre-release Check passes.
- Run Browser Smoke Check manually before merge.
- Run Pages Preview manually and inspect the static report.
- Later, consider production deployment separately from this checkpoint.
