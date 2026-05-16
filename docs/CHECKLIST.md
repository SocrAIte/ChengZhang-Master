# Minimal Acceptance Checklist

Use this checklist for daily pipeline or dashboard data contract changes.

## Pre-release Check

Run the local quality gate before release-oriented changes:

```powershell
python -m market_impact_radar pre-release-check
```

The command performs:

- [ ] `python -m unittest discover -s tests`.
- [ ] Sample `run-daily` with local sample data.
- [ ] Required output validation.
- [ ] `dashboard_data.json` schema check.
- [ ] `dashboard.html` smoke check.
- [ ] `knowledge_review.html` fixed-output check.
- [ ] `run_diagnostics.html` fixed-output check.

Browser smoke check is optional:

```powershell
python -m market_impact_radar pre-release-check --with-browser
```

By default, `pre-release-check` does not start a browser. `--with-browser` opens the generated daily report bundle with Playwright and performs a minimal browser smoke check across:

- [ ] `index.html`
- [ ] `2026-05-15/dashboard.html`
- [ ] `2026-05-15/knowledge_review.html`
- [ ] `2026-05-15/run_diagnostics.html`

Install Playwright inside the project conda environment:

```powershell
python -m pip install --no-user playwright
python -m playwright install chromium
```

Windows conda setup:

```powershell
conda activate market_impact_radar
python -c "import sys; print(sys.executable)"
```

If PowerShell does not switch to the target environment Python, use `conda run` for every command instead:

```powershell
conda run -n market_impact_radar python -c "import sys; print(sys.executable)"
conda run -n market_impact_radar python -m pip install --no-user playwright
conda run -n market_impact_radar python -m playwright install chromium
conda run -n market_impact_radar python -m market_impact_radar pre-release-check
conda run -n market_impact_radar python -m market_impact_radar pre-release-check --with-browser
```

Default `pre-release-check` does not require Playwright. Chromium installation may download browser binaries, so it can require network access.

## CI Gate

GitHub Actions runs the same baseline checks on pull requests and pushes to `master` or `feature-a-share-data-calendar`:

- [ ] `python -m unittest discover -s tests`.
- [ ] `python -m market_impact_radar pre-release-check --skip-tests`.

CI uses `actions/setup-python` with Python 3.11 and installs the project with `python -m pip install -e .`. It does not use the local Windows conda environment.

Pre-release Check uploads a CI preview artifact named `daily-report-preview` from `reports/daily/pre-release-check/`. It includes the generated daily index and sample run outputs for inspection:

- [ ] `index.html`
- [ ] `index.json`
- [ ] `2026-05-15/dashboard.html`
- [ ] `2026-05-15/dashboard_data.json`
- [ ] `2026-05-15/run_summary.json`
- [ ] `2026-05-15/knowledge_review.html`
- [ ] `2026-05-15/run_diagnostics.html`

Browser smoke CI is a separate manual workflow:

- [ ] Trigger `Browser Smoke Check` from GitHub Actions `workflow_dispatch`.
- [ ] It installs Playwright and Chromium with `python -m playwright install --with-deps chromium`.
- [ ] It runs `python -m market_impact_radar pre-release-check --with-browser`.
- [ ] It checks the daily report bundle pages: index, dashboard, knowledge review, and run diagnostics.
- [ ] It uploads `browser-smoke-daily-report-preview` from `reports/daily/pre-release-check/`.

Artifacts can be downloaded from the workflow run to inspect `index.html`, `dashboard.html`, `dashboard_data.json`, `run_summary.json`, `knowledge_review.html`, and `run_diagnostics.html`. These artifacts are CI previews, not formal deployment; GitHub Pages can be handled separately later. Browser smoke is not part of the default push / PR gate because Playwright and Chromium make the job heavier. Locally, continue to use `conda run -n market_impact_radar ...` for browser smoke checks on Windows.

GitHub Pages Preview is a separate manual workflow:

- [ ] Trigger `Pages Preview` from GitHub Actions `workflow_dispatch`.
- [ ] It runs the sample `pre-release-check --skip-tests`.
- [ ] It deploys only `reports/daily/pre-release-check/` to GitHub Pages.
- [ ] The Pages root opens `index.html`, with relative links to `2026-05-15/dashboard.html`, `dashboard_data.json`, `run_summary.json`, `knowledge_review.html`, and `run_diagnostics.html`.
- [ ] This is a sample preview, not production data.
- [ ] Default push / PR workflows do not deploy Pages.
- [ ] The GitHub repository must allow GitHub Actions to deploy Pages.

## Daily Pipeline

- [ ] `python -m unittest discover -s tests` passes.
- [ ] Sample `run-daily` command completes.
- [ ] `reports/daily/YYYY-MM-DD/run_summary.json` exists.
- [ ] `reports/daily/YYYY-MM-DD/dashboard_data.json` exists.
- [ ] `dashboard_data.json` contains `schema_version`.
- [ ] `reports/daily/YYYY-MM-DD/dashboard.html` exists.
- [ ] `reports/daily/YYYY-MM-DD/knowledge_review.html` exists.
- [ ] `reports/daily/YYYY-MM-DD/run_diagnostics.html` exists.
- [ ] `dashboard.html`, `knowledge_review.html`, and `run_diagnostics.html` can return to `../index.html`.
- [ ] `dashboard.html`, `knowledge_review.html`, and `run_diagnostics.html` link to each other with relative paths.
- [ ] `knowledge_review.html` shows clean, issues, skipped, or not available state correctly.
- [ ] `run_diagnostics.html` shows steps, warnings, errors, outputs, and data source health.
- [ ] `run_summary.json` status is reasonable for the run.
- [ ] Warnings are visible and not silently dropped.
- [ ] `skipped` is not displayed as `failed`.
- [ ] `partial` is not treated as a clean pass.

## History Index

- [ ] `reports/daily/index.json` exists.
- [ ] `reports/daily/index.html` exists.
- [ ] `index.html` shows at least one daily run after a sample run.
- [ ] Date links open the corresponding `dashboard.html`.
- [ ] Date links show `knowledge_review.html` when present.
- [ ] Date links show `run_diagnostics.html` when present.
- [ ] `index.html` shows Dashboard, Knowledge Review, and Run Diagnostics links for each run.
- [ ] Missing `dashboard_data.json` or `run_summary.json` is shown as partial or missing, not as a clean pass.

## Dashboard Data Contract

- [ ] `schema_version` is present.
- [ ] `run` exists.
- [ ] `market_context` exists.
- [ ] `summary` exists.
- [ ] `signals` is a list.
- [ ] `knowledge` exists.
- [ ] `outputs` exists.
- [ ] Missing signal `intraday_status` defaults to `not_checked`.
- [ ] Missing signal `risk_level` defaults to `unknown`.

## Dashboard Rendering

- [ ] Dashboard renders from `dashboard_data.json`.
- [ ] Dashboard displays the schema version.
- [ ] Dashboard displays run status and warnings.
- [ ] Dashboard displays signal rows when present.
- [ ] Dashboard handles empty signals without crashing.
- [ ] Dashboard handles missing knowledge data without crashing.
- [ ] Dashboard links to `knowledge_review.html` when available.
- [ ] Dashboard links to `run_diagnostics.html` when available.
- [ ] Dashboard links back to the Daily Runs index.
- [ ] Dashboard does not recompute financial signals.
- [ ] Dashboard avoids certainty or direct-buy language.
