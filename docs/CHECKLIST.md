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
