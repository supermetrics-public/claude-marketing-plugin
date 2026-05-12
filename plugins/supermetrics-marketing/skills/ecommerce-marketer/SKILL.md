---
name: ecommerce-marketer
description: Battle-tested workflows for ecommerce marketers running paid acquisition campaigns where direct revenue attribution is the whole point — blended ROAS analysis across Google Ads and Facebook Ads, day-of-week purchase pattern analysis, and promotional campaign anomaly detection during high-stakes sales periods like Black Friday — via the Supermetrics connector. Use whenever the user is doing ecommerce paid media analysis or running a high-stakes promotional campaign that needs daily monitoring. Trigger on phrases like "blended ROAS," "purchase conversion value," "which day of week converts best," "Black Friday performance," "BFCM," "cost per purchase is spiking," "ad set anomaly," "Q4 promo campaign," "ROAS dropped overnight," "alert the media buying team." This skill handles the analyses that have to happen daily during a promo, and the post-mortem analyses after.
---

# Supermetrics workflows for the ecommerce marketer

This skill helps ecommerce marketers whose campaigns tie directly to revenue. Conversions are purchases (not leads), and the analytical questions are quantitative: which day of the week converts best, what's blended ROAS across platforms, is yesterday's cost-per-purchase spike a real problem or just noise.

The stakes spike around promotional campaigns — Black Friday, Cyber Monday, holiday sales, flash sales. During these periods, a 3x cost-per-purchase spike that goes uncaught for hours can blow a meaningful share of the campaign budget. The anomaly detection workflow exists for that scenario.

## Required: the Supermetrics connector

These workflows rely on the **Supermetrics connector for Claude**. Both workflows specifically need Google Ads and Facebook Ads at minimum, with purchase conversion tracking properly configured (conversion value populated, not just purchase count).

Before running anything, check that the connector is active — look for Supermetrics tools (`data_query`, `accounts_discovery`, etc.). If they aren't present, prompt the user:

> This workflow needs the Supermetrics connector for Claude. Install it at https://claude.ai/directory/connectors/cc599e7b-8c59-4e89-9bf0-36d47bb9ec80
>
> Connect at least Google Ads and Facebook Ads with purchase conversion tracking set up. These workflows depend on revenue data, not just purchase counts.

If purchase tracking is misconfigured (conversion values missing or zeroed), surface this immediately — ROAS analysis without conversion values is meaningless.

## Core principles

Three principles apply throughout every workflow:

1. **Two-step pattern: pull, then analyze.** Even during a promo when speed matters, pull data first, confirm it, then analyze. A 3x cost-per-purchase spike skipped through verification might be a tracking issue, not a performance issue — the 30 seconds spent confirming is worth it.

2. **Be explicit about attribution and value.** Facebook "purchases" with default 7-day-click / 1-day-view attribution won't match Google "conversions" with data-driven attribution. When computing blended ROAS, name the attribution settings — or the comparison is suspect.

3. **Show, don't tell.** Day-of-week patterns, anomaly detection, ROAS trends — all of these are dramatically easier to read as visuals than as tables. See "Choosing the right visualization" below.

## Choosing the right visualization

This skill doesn't prescribe specific charts. Decide based on what the data and the question actually are.

### Step 1 — What is the user trying to see?

| Question type | Visualization family |
|---|---|
| Day-of-week × hour-of-day patterns | Heatmap (the canonical visualization for two-dimensional categorical data) |
| Day-of-week comparison on a single metric | Sorted bar chart with days on the x-axis |
| Daily trend of cost-per-purchase or ROAS | Line chart with a reference line for the baseline average |
| Anomaly detection (spike vs baseline window) | Line chart with the spike day highlighted, plus a shaded baseline band |
| Blended ROAS by platform | Sorted bar chart or paired bars |
| Per-campaign breakdown during a promo | Sorted horizontal bar chart with anomalous campaigns highlighted |
| Spend vs revenue trajectory | Dual-axis chart, spend as bars and revenue as a line |

Day-of-week analysis is the **prime case for a heatmap** in this skill: rows = days of week, columns = hours (if hourly data is available) or simply a single-row colored bar (if daily). Cells colored by ROAS or conversion rate.

### Step 2 — What's the headline?

Before building, name the single thing the chart should make obvious. "Saturdays convert 40% better than Sundays — and we're spending equally on both" is a headline. "Day-of-week analysis" is not.

Make the headline land within two seconds:
- **Sort by the metric of interest** when ordering matters (e.g. days ranked by ROAS), or preserve calendar order when continuity matters (e.g. trend over a month)
- **Highlight the spike, the winner, or the worst offender** in a contrasting color
- **Add reference lines** for the baseline average, the target ROAS, or the anomaly threshold
- **Annotate anomalies** with their cause directly on the chart (e.g. "Pixel failure suspected")

### Step 3 — Build as inline artifact

For data visualizations in chat, build a React component using Recharts.

### Standard color palette

- **Good / improving / positive direction:** `#10b981` (green)
- **Bad / declining / negative direction:** `#ef4444` (red)
- **Neutral / baseline / no-direction comparison:** `#6366f1` (indigo)
- **Flagged / warning / attention / anomaly:** `#f59e0b` (amber)
- **Gridlines:** `#f3f4f6`
- **Text:** `#374151`

For heatmaps, use a diverging red-to-green scale where the midpoint is the metric's average. Below-average cells trend red; above-average cells trend green. This makes "worse than usual" and "better than usual" instantly readable.

### Skip the chart when

- The output is a single anomaly alert (just state which ad sets and what the ratios are)
- The user just wants the headline number (blended ROAS = 3.2x)
- The deliverable is an urgent email to the media buying team — the email itself is the deliverable, not a chart

### Ad hoc analysis

For one-off questions outside the two bundled workflows ("what's the AOV distribution across our top SKUs in this campaign?", "is there a customer-LTV difference between Facebook and Google traffic?", "how does promo-period purchase intent vary by audience segment?"), write fresh analysis code.

## Other Claude capabilities to leverage

**Built-in document skills.** When the deliverable is a file:
- Word documents (post-promo retrospectives, day-of-week strategy memos) → use the `docx` skill at `/mnt/skills/public/docx/SKILL.md`
- Spreadsheets (daily promo monitoring sheets, campaign-by-campaign breakdowns) → use the `xlsx` skill at `/mnt/skills/public/xlsx/SKILL.md`
- Slide decks (post-Black-Friday leadership readouts) → use the `pptx` skill at `/mnt/skills/public/pptx/SKILL.md`

Read the relevant SKILL.md before building.

**Other connectors when they're available.** If the user has Slack connected, anomaly alerts can be posted directly to the media buying team's channel — often the fastest way to get attention during a promo. If Gmail is connected, urgent emails can become drafts. If Google Calendar is connected, you can confirm the promo's start/end dates rather than asking.

**Web search.** Useful for recent platform changes affecting attribution (e.g. iOS 14.5+ effects on Facebook), industry promo benchmarks (typical BFCM ROAS lift), or fresh research on cart abandonment / returns trends that explain anomalies.

**Clarifying questions.** Use `ask_user_input_v0` for multiple-choice — attribution model preference, baseline window for anomaly detection (rolling 6-day vs same-week-last-year), which campaigns count as the promo set.

## When to use the bundled workflows

The `references/workflows.md` file contains the prompt sequences for seven core scenarios:

- **Cross-platform ROAS and purchase behavior** — 30-day cross-platform look with day-of-week breakdown. Triggered by "blended ROAS," "which day converts best."
- **Promotional campaign anomaly detection** — daily monitoring during high-stakes promos, flagging anomalies and drafting alerts. Triggered by "is yesterday's spike real," "BFCM anomaly," "cost per purchase way up."
- **Product/SKU-level performance** — when an ecommerce backend (Shopify, BigCommerce, WooCommerce) is connected, ranking SKUs by ad-driven contribution. Triggered by "which products should I scale," "SKU-level ROAS," "best-selling product analysis."
- **New vs returning customer ROAS by channel** — separating acquisition from repurchase to know where each channel actually wins. Triggered by "are we acquiring new customers," "new vs returning ROAS," "customer acquisition by channel."
- **AOV and basket composition** — analyzing order value and items per order to find upsell opportunities. Triggered by "average order value," "basket size by channel," "upsell analysis."
- **Subscription / retention cohort analysis** — when subscriptions or payments connectors are available, tracking retention and revenue cohorts. Triggered by "churn rate," "retention curve," "subscriber LTV."
- **Pre-promo planning model** — modeling budget, AOV, and ROAS targets for a planned promotional period. Triggered by "BFCM plan," "promo budget plan," "what should our targets be for the spring sale."

Read `references/workflows.md` when the user's request matches.

## Bundled scripts

- `scripts/blended_roas.py` — blended ROAS across platforms with day-of-week breakdown.
- `scripts/anomaly_detector.py` — flags cost-per-purchase spikes against rolling baseline.
- `scripts/sku_performance.py` — ranks SKUs by ad-driven contribution and surfaces inventory considerations.
- `scripts/customer_type_roas.py` — splits ROAS by new vs returning customer to isolate acquisition efficiency.
- `scripts/aov_analyzer.py` — analyzes AOV and items-per-order patterns by channel and time.
- `scripts/subscription_cohorts.py` — computes retention curves and cohort revenue for subscription/repeat businesses.
- `scripts/promo_planner.py` — models pre-promo targets given historical performance.

## Bundled templates

- `assets/media_buyer_alert_email.md` — urgent email template for cost-per-purchase spikes.
- `assets/dow_budget_strategy.md` — day-of-week budget weighting doc.
- `assets/sku_performance_report.md` — SKU performance report with action recommendations.
- `assets/customer_acquisition_brief.md` — new-vs-returning customer ROAS brief.
- `assets/aov_summary.md` — AOV and basket composition summary.
- `assets/retention_cohort_report.md` — retention cohort analysis doc.
- `assets/promo_plan_doc.md` — pre-promo planning doc with targets and assumptions.

## Things to watch for

**Attribution windows materially affect ROAS.** Facebook with 7-day-click / 1-day-view will credit more purchases than Google's data-driven attribution. Blended ROAS = sum_revenue / sum_spend has known double-counting risk. Surface this caveat.

**iOS 14.5+ degraded Facebook attribution.** If Facebook ROAS looks substantially lower than historical, that's partially measurement degradation, not real decline. Mention Conversions API (CAPI) as a measurement improvement if the user hasn't moved to it.

**Purchases data has return lag.** A purchase recorded today might be refunded next week, but most platforms don't retroactively update. Build a small mental buffer (5–10% for apparel; lower for many other categories) when making decisions on yesterday's ROAS during a promo.

**Day-of-week effects can be confounded by ad schedule effects.** If campaigns run on a dayparting schedule that puts more spend on Saturdays, the apparent "Saturday is great" finding might be because the algorithm has more budget to optimize. Pull data on a per-dollar-spent basis (ROAS, conversion rate) rather than absolute volume.

**A 3x cost-per-purchase spike is often a tracking issue, not a performance issue.** The anomaly detector flags candidates; verify before alerting. Common causes: pixel firing failure, conversion event renamed, deduplication issue. The script's candidate-cause column flags likely explanations.

**During promo periods, normal patterns become unstable.** Conversion rates spike because intent is high; CPMs spike because everyone bids harder. A cost-per-purchase increase during BFCM isn't always efficiency loss — it might be competitive pressure. When the user is in a promo, use comparable-period baselines (same promo last year, the rest of this promo week) rather than the trailing 6 days.
