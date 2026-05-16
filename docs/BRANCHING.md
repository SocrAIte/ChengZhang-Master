# Branching Strategy

This repository currently uses `feature-a-share-data-calendar` as the remote default branch and the active mainline checkpoint.

## Current Remote Branch State

- Remote default branch: `feature-a-share-data-calendar`
- Remote `master`: not present
- Remote `main`: not present
- Local `master`: present but older than the current remote checkpoint

Do not push the old local `master` branch to the remote repository without an explicit branch strategy decision.

## Current Mainline Checkpoint

The daily report bundle v1 checkpoint is completed on:

```text
feature-a-share-data-calendar
```

This checkpoint includes the daily pipeline, static report bundle, dashboard data v1 contract, local quality gates, CI artifacts, browser smoke workflow, and Pages preview workflow.

## Development Flow

For new work, branch from the current mainline:

```powershell
git switch feature-a-share-data-calendar
git pull
git switch -c <new-feature-branch>
```

Keep each new branch focused on one task.

## Future main / master Migration

If the repository later adopts a conventional `main` or `master` branch:

- Create it from the current `feature-a-share-data-calendar` HEAD.
- Do not use the old local `master` commit as the remote mainline.
- Confirm the default branch policy in GitHub before creating or switching the default branch.
- Run the full merge-readiness checks before changing the default branch.

## Required Checks Before Mainline Updates

Before updating the current mainline checkpoint, run:

```powershell
python -m unittest discover -s tests
python -m market_impact_radar pre-release-check
python -m market_impact_radar pre-release-check --with-browser
```

Remote checks before considering a checkpoint stable:

- GitHub Actions Pre-release Check
- Browser Smoke Check workflow
- Pages Preview workflow
- CI artifact inspection when report preview output changes
