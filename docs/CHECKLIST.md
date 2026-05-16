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

Browser smoke check is optional:

```powershell
python -m market_impact_radar pre-release-check --with-browser
```

By default, `pre-release-check` does not start a browser. `--with-browser` opens the generated `dashboard.html` with Playwright and performs a minimal browser smoke check. Install Playwright inside the project conda environment:

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

Browser smoke CI is a separate manual workflow:

- [ ] Trigger `Browser Smoke Check` from GitHub Actions `workflow_dispatch`.
- [ ] It installs Playwright and Chromium with `python -m playwright install --with-deps chromium`.
- [ ] It runs `python -m market_impact_radar pre-release-check --with-browser`.

Browser smoke is not part of the default push / PR gate because Playwright and Chromium make the job heavier. Locally, continue to use `conda run -n market_impact_radar ...` for browser smoke checks on Windows.

## Daily Pipeline

- [ ] `python -m unittest discover -s tests` passes.
- [ ] Sample `run-daily` command completes.
- [ ] `reports/daily/YYYY-MM-DD/run_summary.json` exists.
- [ ] `reports/daily/YYYY-MM-DD/dashboard_data.json` exists.
- [ ] `dashboard_data.json` contains `schema_version`.
- [ ] `reports/daily/YYYY-MM-DD/dashboard.html` exists.
- [ ] `run_summary.json` status is reasonable for the run.
- [ ] Warnings are visible and not silently dropped.
- [ ] `skipped` is not displayed as `failed`.
- [ ] `partial` is not treated as a clean pass.

## History Index

- [ ] `reports/daily/index.json` exists.
- [ ] `reports/daily/index.html` exists.
- [ ] `index.html` shows at least one daily run after a sample run.
- [ ] Date links open the corresponding `dashboard.html`.
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
- [ ] Dashboard does not recompute financial signals.
- [ ] Dashboard avoids certainty or direct-buy language.
