---
name: data-dashboard-ui
description: Use this skill when designing or modifying market radar, financial dashboard, ETF candidate, stock candidate, signal ranking, cross-market mapping, or investment research UI.
---

# Data Dashboard UI

## Goal

Build financial dashboard UI that is clear, evidence-based, sortable, and useful for decision support.

The UI should help users understand:

- What happened.
- Why it matters.
- Which A-share sectors, ETFs, or stocks may be affected.
- How strong the signal is.
- What the risks are.
- When the signal was generated.

## Core principles

- Signal clarity is more important than decoration.
- Do not make predictions look certain.
- Every recommendation must show reasoning.
- Every data point should show time context.
- Use compact but readable information density.
- Prefer structured tables, badges, scores, and explanations over long paragraphs.

## Required fields for candidate rows

When showing ETF or stock candidates, include as many of these as the available data supports:

- Name
- Ticker / code
- Category / sector
- Signal score
- Trigger source
- External market source
- Mapping reason
- Confidence level
- Risk level
- Latest relevant change
- Timestamp
- Suggested watch action, not guaranteed buy instruction

## Signal explanation

Each signal should explain:

1. External trigger
   Example: Micron, NVIDIA, TSMC, gold futures, Nikkei semiconductor equipment stocks.

2. A-share mapping
   Example: storage chips, semiconductor equipment, CPO, PCB, liquid cooling, gold ETF.

3. Transmission logic
   Explain why the external move may affect the local sector.

4. Strength
   Use a score, rank, or badge.

5. Risk
   Include uncertainty, crowding, overnight gap risk, policy risk, and liquidity risk when relevant.

## UI patterns

Prefer:

- Sortable tables
- Filter chips
- Signal cards
- Ranking lists
- Badges for strength and risk
- Expandable reasoning panels
- Clear timestamps
- Source labels
- Empty states
- Loading states
- Error states

Avoid:

- Long unstructured text blocks.
- Overconfident wording.
- Hiding risk notes.
- Mixing stale data with fresh data without labels.
- Showing a candidate without explaining why it appears.
- Making the UI look like direct financial advice.

## Copywriting rules

Use cautious language:

- "candidate"
- "watchlist"
- "signal"
- "possible transmission"
- "risk"
- "confidence"
- "requires confirmation"

Avoid certainty language:

- "must buy"
- "guaranteed"
- "will rise"
- "safe"
- "no risk"

## Validation

Before completing the task:

1. Check that the main table or list is scannable.
2. Check that every recommendation has a reason.
3. Check that signal strength and risk are visible.
4. Check that timestamps or data freshness are visible.
5. Check that the UI does not imply guaranteed investment outcomes.
