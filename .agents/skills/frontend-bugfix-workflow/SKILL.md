---
name: frontend-bugfix-workflow
description: Use this skill when fixing frontend bugs, UI regressions, broken interactions, state issues, rendering errors, TypeScript errors, failed tests, or build failures.
---

# Frontend Bugfix Workflow

## Goal

Fix frontend bugs with the smallest safe change.

## Workflow

1. Understand the bug.
2. Reproduce the issue if possible.
3. Identify the root cause.
4. Make the smallest necessary change.
5. Avoid unrelated refactors.
6. Verify the fix.
7. Summarize the cause and fix.

## Rules

- Do not rewrite large parts of the app unless the bug requires it.
- Do not change public APIs unless necessary.
- Do not change business logic unless the bug is in business logic.
- Do not introduce new dependencies for simple bugs.
- Prefer local fixes over architectural changes.
- Preserve existing behavior not mentioned in the bug report.
- If there are tests, add or update a focused regression test.
- If the bug is visual or interaction-related, verify it in a browser.

## Debug checklist

Check:

- Component props
- State initialization
- Derived state
- useEffect dependencies
- Async loading states
- Error boundaries
- Event handlers
- Conditional rendering
- Form state
- Table sorting/filtering logic
- Data formatting
- API response shape
- TypeScript types
- CSS class conflicts
- z-index and overlay behavior

## Validation

Run available commands, depending on the project:

- typecheck
- lint
- tests
- build

If a command fails, report the exact failure and whether it is related to the bug.

## Output

Return:

- Root cause
- Files changed
- Fix summary
- Verification performed
- Remaining risks
