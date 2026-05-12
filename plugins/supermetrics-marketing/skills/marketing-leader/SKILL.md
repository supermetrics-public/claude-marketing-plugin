---
name: marketing-leader
description: Battle-tested workflows for marketing analytics and leadership work — quarterly executive overviews, multi-channel budget pacing and forecasting, and cross-platform ROAS benchmarking — using the Supermetrics connector. Use whenever the user is doing macro-level marketing analysis or executive reporting rather than daily campaign work. Trigger on phrases like "90-day overview," "quarterly review," "budget pacing," "are we on track to hit our spend target," "forecast month-end conversions," "ROAS by platform," "which channel deserves more budget," "deck for the CMO," "executive summary," "marketing performance report." Also trigger when the user mentions building a presentation, slide deck, or board-ready document from marketing data, even if they don't say "Supermetrics" — these are leadership deliverables that benefit from the structured workflows in this skill.
---

# Supermetrics workflows for marketing analytics and leadership

This skill helps marketing leaders and analysts produce macro-level cross-channel analysis: the quarterly review, the budget pacing forecast, the cross-platform ROAS comparison. The output of these workflows lands in front of CMOs, finance partners, and boards — so the workflows are tuned for "decision-ready" outputs, not data dumps.

## Required: the Supermetrics connector

These workflows rely on the **Supermetrics connector for Claude**, which pulls live data from connected ad platforms. Before running anything, check that the connector is active — look for Supermetrics tools in this session (`data_query`, `accounts_discovery`, etc.).

If they aren't present, prompt the user:

> This workflow needs the Supermetrics connector for Claude. Install it at https://claude.ai/directory/connectors/cc599e7b-8c59-4e89-9bf0-36d47bb9ec80
>
> Once it's installed, authenticate and connect the ad platforms you want covered in the analysis.

Don't fabricate placeholder data. Executive decisions get made on real numbers.

## Core principles

Three principles apply throughout every workflow:

1. **Two-step pattern: pull, then analyze.** Don't combine retrieval and synthesis into a single tool call. Pull the data, confirm what you got with a one-line summary, then run the analysis. Leadership deliverables especially benefit from this — if the data is wrong, the recommendations built on it are wrong, and the leader won't catch it until the meeting.

2. **Show, don't tell.** Leadership audiences scan deliverables; they don't read them line by line. When the analysis produces numbers worth comparing — across channels, across time, across budget scenarios — build a visual. See "Choosing the right visualization" below.

3. **One serious query at a time.** Multi-channel pulls over 60–90 days can be heavy. Sequence the queries.

## Choosing the right visualization

This skill doesn't prescribe specific charts for specific workflows. Instead, decide visualization based on what the data and the question actually are.

### Step 1 — What is the user trying to see?

| Question type | Visualization family |
|---|---|
| Channel performance side-by-side (spend, ROAS, conversions) | Grouped bars or small multiples — one mini-chart per channel |
| Trend over time (spend, conversions, ROAS week-by-week) | Line chart, optionally with a reference line for target |
| Budget pacing vs target | Line chart with cumulative spend and a dashed target line; shade gap red or green |
| Ranking channels by efficiency | Sorted horizontal bar chart |
| Part-to-whole when there are few channels (<6) | Stacked bar (not pie) — and only when share matters, not just totals |
| Two-dimensional categorical comparison | Heatmap (e.g. ROAS by channel × month) |
| Quarter-over-quarter comparison | Side-by-side bars or slopegraph |
| Forecast vs actual | Line chart with actuals as solid line, forecast as dashed line |

### Step 2 — What's the headline?

Before building, name the single thing the chart should make obvious. "Spend climbed but conversions held flat — efficiency is sliding" is a headline. "Q3 marketing metrics" is not.

Make the headline land within two seconds of looking at the chart:
- **Sort by the metric of interest** (alphabetical order hides the answer)
- **Highlight one bar or one segment** in a contrasting color when there's a clear standout
- **Add a reference line** for target, baseline, or last-period value
- **Annotate the winner or the worst offender** directly on the chart

If you can't name the headline, the chart isn't ready. Often that means the analysis isn't ready either.

### Step 3 — Build it as an inline artifact

For data visualizations in chat, build a React component using Recharts (available in the artifact environment). For visualizations destined for a slide deck or document, embed them inside the file using the relevant built-in skill (see below).

### Standard color palette

For consistency across charts in the same conversation:
- **Good / improving / positive direction:** `#10b981` (green)
- **Bad / declining / negative direction:** `#ef4444` (red)
- **Neutral / baseline / no-direction comparison:** `#6366f1` (indigo)
- **Flagged / warning / attention:** `#f59e0b` (amber)
- **Gridlines:** `#f3f4f6`
- **Text:** `#374151`

Color by *business meaning*, not by sign. If spend is +30%, the bar is red if that's overspend, green if it's a deliberate scale-up.

### Skip the chart when

- The answer is 1–3 numbers (just state them in headline form)
- The deliverable is a narrative document where prose is more appropriate
- The user explicitly asked for a table or a spreadsheet

### Ad hoc analysis

For one-off questions the bundled scripts weren't designed for ("what's the spend concentration across channels — top 3 vs the rest?", "is there a launch-month effect on new campaigns?"), write fresh analysis code in chat. Pull the data, compute the answer, build the visualization that fits the question.

## Other Claude capabilities to leverage

**Built-in document skills.** When the deliverable is a file:
- Slide decks (the executive overview is the prime case) → use the `pptx` skill at `/mnt/skills/public/pptx/SKILL.md`
- Word documents (handouts, memos, board reports) → use the `docx` skill at `/mnt/skills/public/docx/SKILL.md`
- Spreadsheets (pacing tables, channel comparisons) → use the `xlsx` skill at `/mnt/skills/public/xlsx/SKILL.md`

Read the relevant SKILL.md *before* building any file. The slide-deck workflow especially depends on this — slides have visual rules that don't apply to docs.

**Other connectors when they're available.** If the user has Google Drive connected, the executive deck or memo can land directly in Drive in a chosen folder. If Gmail is connected, the CMO email can become a draft. If Slack is connected, a short version of the headline can be posted to a leadership channel. These are opportunistic — only use them when they're already available.

**Web search.** Useful for industry benchmarks (CPA / ROAS norms for the user's category), recent platform changes that might explain anomalies, or context for board-level narratives.

**Clarifying questions.** When you need a multiple-choice answer to proceed (which attribution model, which time window, which currency conversion approach), use the `ask_user_input_v0` tool. Cleaner than asking in prose on mobile.

## When to use the bundled workflows

The `references/workflows.md` file contains the prompt sequences for seven core scenarios:

- **90-day executive overview** — quarterly or near-quarterly cross-channel review, typically delivered as a slide deck plus a printable handout. Triggered by "quarterly review," "QBR," "executive summary of Q[N]," "CMO deck."
- **Budget pacing and financial forecasting** — mid-month or mid-quarter check on whether spend is on track, with a forecast to period end. Triggered by "pacing," "forecast," "are we going to overspend," "month-end projection."
- **Cross-channel ROAS benchmarking** — defensible ranking of channels by efficiency, used to justify budget allocation in planning. Triggered by "which channel deserves more budget," "ROAS by platform," "should I shift budget from X to Y."
- **Annual planning support** — pulls 12+ months across all channels, surfaces stable performers vs. volatile channels, and models scenarios for next year's budget mix. Triggered by "annual plan," "next year's budget," "marketing plan for FY[N]."
- **New channel investment case** — builds the analytical case for whether to launch on a new platform (Reddit, TikTok, Pinterest, retail media). Combines saturation signals from current channels with research on the new channel. Triggered by "should we add [platform]," "investment case for [platform]," "new channel evaluation."
- **Marketing efficiency vs goals tracking** — tracks committed KPIs (CAC, payback period, MER) against targets, surfaces where reality diverges. Triggered by "are we hitting our targets," "CAC vs goal," "MER tracking," "payback period."
- **CAC and LTV unit economics** — when CRM and ecommerce/payments connectors are available, computes blended and channel-level CAC and LTV. The finance-team view of marketing. Triggered by "unit economics," "CAC by channel," "LTV:CAC ratio," "customer payback."

Read `references/workflows.md` when the user's request matches.

## Bundled scripts

- `scripts/budget_pacing.py` — projects period-end spend and conversions at current run rate, flags channels pacing more than ±15% off target.
- `scripts/roas_ranker.py` — ranks channels by ROAS over a configurable window, outputs a budget-reallocation recommendation with the standard diminishing-returns caveat.
- `scripts/exec_summary_builder.py` — produces a slide-ready text outline from a channel-level CSV, matching the executive overview deck structure.
- `scripts/annual_planner.py` — analyzes 12+ months of channel-level data, classifies channels by stability and growth, models budget scenarios for next period.
- `scripts/channel_investment_case.py` — given current channel saturation signals and reference benchmarks, builds the analytical case for adding a new channel.
- `scripts/efficiency_tracker.py` — tracks CAC, payback period, MER, and other committed KPIs against targets; surfaces gaps.
- `scripts/unit_economics.py` — computes blended and channel-level CAC and LTV from ad-platform spend + CRM/ecommerce revenue data.

## Bundled templates

- `assets/exec_deck_outline.md` — slide-by-slide structure for the 90-day executive deck.
- `assets/cmo_email.md` — short summary email template for the CMO.
- `assets/budget_reallocation_memo.md` — one-page memo justifying a cross-platform budget shift.
- `assets/annual_plan_doc.md` — structured doc for the annual plan output, with scenario comparison and recommended mix.
- `assets/new_channel_business_case.md` — business case template for proposing a new channel investment.
- `assets/efficiency_dashboard_doc.md` — structured doc for the marketing efficiency review.

## Things to watch for

**Attribution is political.** Last-click ROAS on Facebook, data-driven ROAS in Google Ads, and a multi-touch model the company runs separately will all show different numbers. When the user asks "which channel has the best ROAS," surface the attribution model behind the comparison before recommending shifts.

**Run rates lie when spend is lumpy.** A campaign launched mid-month and just hitting full pace will under-forecast with a naive daily-average. The pacing script handles this with daily data, but flag the assumption explicitly.

**Quarterly reviews need a "what we tried" section.** The temptation is to report only what worked. Leaders trust analysts more when the review names what was tested that didn't work and what was learned. Include this when the data supports it.

**Currency normalization.** When aggregating across markets, convert to a single currency before computing ROAS or ranking. Surface the conversion approach (period-average, end-of-period, FX-fixed for planning) — don't assume.

**Budget-shift recommendations need guardrails.** A naive "shift 30% from the worst channel to the best" can backfire because channels often have diminishing returns above their current spend ceiling. Default to 15–20% and explicitly call out that the recommendation assumes the destination has remaining capacity.
