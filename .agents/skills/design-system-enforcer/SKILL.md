---
name: design-system-enforcer
description: Use this skill when modifying or creating frontend UI. It enforces existing components, design tokens, styling conventions, and project UI patterns. Use before visual polish or large UI changes.
---

# Design System Enforcer

## Goal

Keep UI changes consistent with the existing project design system.

## Before editing

1. Search for existing components that solve the same problem.
2. Identify the component library and styling conventions.
3. Reuse existing components, tokens, variants, utilities, and naming patterns.
4. Avoid introducing new UI primitives unless necessary.

## Rules

- Prefer existing Button, Card, Input, Badge, Table, Dialog, Select, Tabs, Dropdown, Tooltip, and layout components.
- Do not create duplicate UI primitives if the project already has them.
- Do not hardcode colors unless the project already uses hardcoded values.
- Prefer CSS variables, Tailwind theme values, design tokens, or existing utility classes.
- Keep spacing, radius, shadows, typography, and icon style consistent with nearby UI.
- Keep component APIs consistent with existing components.
- Preserve business logic and data flow unless the task explicitly asks to change them.
- Support loading, empty, error, disabled, hover, focus, and active states when relevant.
- Do not introduce a new dependency without explaining why it is needed.

## Validation

After changing UI:

1. Run the project's typecheck command if available.
2. Run lint if available.
3. Run tests if available.
4. Run build if the change touches routes, shared UI, or data display.
5. Summarize what existing patterns were reused.
