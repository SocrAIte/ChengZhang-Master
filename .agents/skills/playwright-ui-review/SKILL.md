---
name: playwright-ui-review
description: Use this skill after frontend UI changes to verify the page in a real browser with Playwright. It checks rendering, interactions, screenshots, console errors, and basic user flows.
---

# Playwright UI Review

## Goal

Verify frontend changes in a real browser instead of assuming the code works.

## When to use

Use this skill after:

- Creating or modifying a page.
- Changing UI components.
- Changing dashboard tables, filters, forms, charts, or dialogs.
- Fixing UI bugs.
- Applying visual polish.

## Review steps

1. Start the dev server using the project's documented command.
2. Open the target page in a browser.
3. Check for runtime errors and console errors.
4. Verify the page renders without broken layout.
5. Test the main user flow affected by the change.
6. Test buttons, filters, tabs, dropdowns, forms, dialogs, and table interactions that were modified.
7. Capture screenshots when useful.
8. Compare the result against the task goal.

## Rules

- Do not rely only on static code inspection for visual changes.
- Do not mark a UI task complete until the page has been opened successfully.
- If the app cannot start, report the exact command and error.
- If an interaction fails, identify the likely root cause before changing more code.
- Prefer small fixes and re-check the page after each fix.

## Output

Return:

- What page was checked.
- What flow was tested.
- Any visual or interaction problems found.
- What was fixed.
- Remaining risks, if any.
