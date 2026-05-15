# Development Process

This project separates market signal logic, data contracts, and presentation. Keep changes small and verifiable.

## Branching

- Do not work directly on `main` or `master`.
- Create or use a feature branch before implementation.
- Keep one branch focused on one purpose.

## Patch Discipline

- Keep each change small.
- Do not mix financial logic, UI rendering, data contracts, refactors, and formatting in one large patch.
- Do not modify unrelated files.
- Do not reformat files unless formatting is the explicit task.
- Do not hide uncertainty. Record assumptions in the change summary when needed.

## Separation Rules

- Financial signal logic belongs in the pipeline/scoring domain, not in CLI, docs, or UI.
- UI rendering must display existing data only.
- Dashboard rendering must not recompute financial signals.
- Dashboard data shape changes belong in the dashboard contract layer.
- Knowledge graph mapping changes must be reviewed separately from pipeline or UI changes.

## Daily Pipeline Changes

Any change to the daily pipeline must check:

- `run_summary.json`
- `dashboard_data.json`
- `dashboard.html`

`dashboard_data.json` field changes must also update:

- `schema_version`, when the contract is incompatible
- dashboard contract normalization
- dashboard contract validation
- contract tests

## Required Verification

Before committing code or process changes, run:

```powershell
python -m unittest discover -s tests
```

For daily pipeline work, also run the sample command:

```powershell
python -m market_impact_radar run-daily --date 2026-05-15 --external data\sample_external_snapshot.json --context data\sample_a_share_context.json --scoring-rules data\scoring_rules.json --a-share-snapshot data\a_share_snapshot.sample.json --skip-knowledge
```

## Risk Language

The product is a decision-support radar, not a trade execution system.

Do not use certainty language in dashboard or reports:

- must buy
- guaranteed
- will rise
- safe
- no risk
- certain opportunity

Prefer cautious language:

- candidate
- watchlist
- signal
- confidence
- risk
- possible transmission
- requires confirmation

## Data Quality Rules

- Do not treat partial data as confirmed signal.
- Do not treat skipped checks as failed checks.
- Do not silently drop warnings.
- Do not convert missing intraday validation into confirmed status.
- Do not ignore stale, missing, or divergent external quote records.
