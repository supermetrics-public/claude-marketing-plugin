---
name: business-profile
description: Save and reuse the team's marketing targets and context — target CPA/ROAS/CPL, monthly budgets, business type, KPIs, fiscal calendar, naming conventions, brand rules, and "known context" like intentionally paused campaigns or tracking changes. Use when the user states a goal or target, says "remember that…", explains why a number looks odd, asks to set up their profile or targets, or before any analysis that judges performance against goals.
---

# Business profile

Supermetrics stores durable team context with `manage_business_context`. It's shared with everyone on the team and works in every client (Claude, ChatGPT and others), so save context there rather than in local files.

## Read it before analysis

At the start of any performance analysis, call `manage_business_context` with `action: get` (team level). If the analysis focuses on one platform or account, also get it at that scope (`ds_id`, plus `account_id`). Apply what you find:
- Judge results against the saved targets, not generic benchmarks.
- Don't report items listed under known context as problems (for example "PMax paused on purpose during the migration").
- Use the saved currency, fiscal calendar, naming conventions and reporting preferences.

If nothing is saved and the analysis depends on a target, ask **one** question (for example "What CPA are you aiming for?"), use the answer, then offer to save it.

## Set up or update the profile

When the user runs `/supermetrics-marketing:set-targets` or asks for setup, ask briefly and only about what's missing:
1. Business type: ecommerce, B2B lead gen, app, or agency managing clients.
2. Primary KPI and its target (CPA, ROAS, CPL, MER), plus monthly budget per channel if they pace spend.
3. Known context Claude should not flag: launches, intentional pauses, tracking changes, seasonality.
4. Reporting preferences: currency, week start, level of detail.

Save with `action: save`, `mode: replace`, and one tagged entry per topic so each can change on its own:
- `targets` (KPIs, targets, budgets)
- `known-context` (dated items, so stale ones can be pruned)
- `data-analysis` (reporting conventions)

Put account-specific targets at account scope. Confirm what you saved in one line.

When the user explains an anomaly mid-analysis ("that spike was the Black Friday preview"), offer to add it to `known-context` with `mode: append`.
