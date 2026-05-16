# Daily Report Bundle Checkpoint

This checkpoint makes the daily market impact radar usable as a stable static report bundle with local and CI quality gates.

## Goal

Provide a merge-ready baseline for the daily pipeline, dashboard data contract, static report pages, browser smoke checks, CI artifacts, and manual Pages preview.

This checkpoint is a reporting and verification layer. It does not change financial signal rules, scoring rules, or knowledge graph mappings.

## Completed Capabilities

- `run-daily` orchestration command.
- Standard daily output directory under `reports/daily/YYYY-MM-DD/`.
- Stable `dashboard_data.json` v1 contract with `schema_version = "1.0"`.
- Static `dashboard.html` rendered from `dashboard_data.json`.
- Static `knowledge_review.html` for read-only knowledge graph review.
- Static `run_diagnostics.html` for read-only pipeline diagnostics.
- Static `reports/daily/index.html` and `index.json` for daily run history.
- Shared navigation between daily bundle pages.
- Local `pre-release-check` quality gate.
- Optional Playwright browser smoke check for the whole daily report bundle.
- GitHub Actions baseline CI.
- CI artifacts for report preview downloads.
- Manual GitHub Pages preview workflow.

## Generated Daily Outputs

Each daily run can generate:

- `run_summary.json`
- `dashboard_data.json`
- `dashboard.html`
- `knowledge_review.html`
- `run_diagnostics.html`
- `report.md`, when available

The history index under `reports/daily/` can generate:

- `index.json`
- `index.html`

## Daily Report Bundle Pages

- `index.html`: daily run history and links to each run.
- `dashboard.html`: daily signals, candidates, market context, risks, and output links.
- `knowledge_review.html`: read-only knowledge graph check status, issues, and fix suggestions.
- `run_diagnostics.html`: run status, pipeline steps, warnings, errors, and outputs.

All pages use relative links so the bundle works from local files, GitHub Actions artifacts, and GitHub Pages preview.

## dashboard_data.json v1

`dashboard_data.json` is the stable contract consumed by `dashboard.html`.

Top-level fields:

- `schema_version`
- `run`
- `market_context`
- `summary`
- `signals`
- `knowledge`
- `outputs`

The dashboard displays these fields but does not recompute financial signals.

## Quality Gates

`pre-release-check` runs:

- unittest suite
- sample `run-daily`
- required output checks
- `dashboard_data.json` schema checks
- static HTML smoke checks

With `--with-browser`, it opens and verifies:

- `index.html`
- `dashboard.html`
- `knowledge_review.html`
- `run_diagnostics.html`

## GitHub Actions Workflows

- `pre-release-check.yml`: push / PR baseline quality gate.
- `browser-smoke-check.yml`: manual Playwright browser smoke workflow.
- `pages-preview.yml`: manual static sample Pages preview deployment.

## Pages Preview

The Pages Preview workflow deploys only `reports/daily/pre-release-check/`.

This is a sample preview for inspecting static report output. It is not a production deployment and does not contain live production market data.

## Explicitly Out of Scope

- Real production deployment.
- Automatic trading.
- Guaranteed investment predictions.
- Buy / sell instructions.
- Online knowledge graph editing.
- Automatic modification of `data/mappings.json`.
- Live market data access in CI.
- Changes to financial scoring or mapping logic.

## Merge Readiness Checklist

- [ ] Working tree is clean.
- [ ] Branch is `feature-a-share-data-calendar`.
- [ ] Latest local commit is pushed.
- [ ] `python -m unittest discover -s tests` passes.
- [ ] `python -m market_impact_radar pre-release-check` passes.
- [ ] `python -m market_impact_radar pre-release-check --with-browser` passes locally when Playwright is available.
- [ ] Pre-release Check GitHub Action passes on the pushed commit.
- [ ] Browser Smoke Check manual workflow passes.
- [ ] Pages Preview manual workflow passes.
- [ ] `daily-report-preview` artifact is downloadable.
- [ ] Pages `index.html` opens and links to dashboard, knowledge review, and diagnostics pages.
