---
name: demand-gen
description: Battle-tested workflows for B2B demand generation managers connecting ad platform spend to website behavior and pipeline outcomes via the Supermetrics connector. Use whenever the user is analyzing the bridge between top-of-funnel ad spend and bottom-of-funnel leads — including traffic-to-conversion audits, GA4 + ad-platform reconciliation, lead quality analysis, cost-per-lead comparisons across LinkedIn vs Facebook vs Google, and B2B lead generation campaign efficiency. Trigger on phrases like "are we buying real leads or just clicks," "compare cost per lead across platforms," "which channel drives engaged traffic," "GA4 says X but Facebook says Y," "VP of Sales wants a budget update," "lead gen efficiency," "MQL cost by channel." This skill handles the analyses demand gen managers run to justify budget to sales leadership.
---

# Supermetrics workflows for the demand generation manager

This skill helps B2B demand generation managers connect top-of-funnel ad spend to bottom-of-funnel outcomes. The core analytical move is reconciliation: ad platforms report one thing, web analytics report another, and the truth is usually somewhere in between.

## Required: the Supermetrics connector

These workflows rely on the **Supermetrics connector for Claude** and specifically need both ad platform data (LinkedIn Ads, Facebook Ads, Google Ads) and web analytics (Google Analytics 4) to be connected. Demand gen analysis falls apart without both.

Before running anything, check that the connector is active — look for Supermetrics tools in this session (`data_query`, `accounts_discovery`, etc.). If they aren't present, prompt the user:

> This workflow needs the Supermetrics connector for Claude to pull both your ad platform data and Google Analytics 4. Install it at https://claude.ai/directory/connectors/cc599e7b-8c59-4e89-9bf0-36d47bb9ec80
>
> Connect at least one ad platform AND Google Analytics 4 — the comparison between what ad platforms reported and what GA4 saw is the whole point.

If only one side is connected, surface that immediately. Most of the value in these workflows is in the comparison.

## Core principles

Three principles apply throughout every workflow:

1. **Two-step pattern: pull, then compare.** Pull the ad platform data, confirm it. Pull the GA4 data, confirm it. Then reconcile. Catching data issues before the analysis (a missing UTM parameter, a renamed conversion event) prevents the whole comparison from being misleading.

2. **Always name the attribution model.** Facebook "purchases" with 7-day-click attribution is not GA4 "purchases" with data-driven attribution is not CRM "MQLs." When producing comparison tables or charts, label every metric with its source. Demand gen credibility lives or dies on this.

3. **Show, don't tell.** Reconciliation analysis is dense with numbers; visualizations make divergences immediately legible. See "Choosing the right visualization" below.

## Choosing the right visualization

This skill doesn't prescribe specific charts. Decide based on what the data and the question actually are.

### Step 1 — What is the user trying to see?

| Question type | Visualization family |
|---|---|
| Funnel drop-off across stages (impressions → clicks → sessions → leads → MQLs) | Funnel chart or descending stacked bars |
| Two metric systems disagreeing on the same channels | Paired bars (side-by-side per channel) or slopegraph |
| Cost-per-lead comparison across platforms | Sorted horizontal bar chart |
| Tracking health (clicks vs sessions gap per channel) | Diverging bar chart with zero as baseline |
| Lead-to-MQL conversion rate by source | Sorted bar chart with reference line for blended average |
| Trend in lead quality over time | Line chart with multiple series (one per source) |

### Step 2 — What's the headline?

Before building, name the single thing the chart should make obvious. "LinkedIn buys clicks that don't show up in GA4 — likely a UTM issue" is a headline. "Channel comparison data" is not.

Make the headline land within two seconds:
- **Sort by the metric of interest**
- **Highlight the divergent channel** (the one that disagrees most between the two data sources)
- **Add a reference line** for blended average or industry benchmark
- **Annotate UTM-flagged channels** directly on the chart

### Step 3 — Build as inline artifact

For data visualizations in chat, build a React component using Recharts.

### Standard color palette

- **Good / improving / positive direction:** `#10b981` (green)
- **Bad / declining / negative direction:** `#ef4444` (red)
- **Neutral / baseline / no-direction comparison:** `#6366f1` (indigo)
- **Flagged / warning / attention:** `#f59e0b` (amber)
- **Gridlines:** `#f3f4f6`
- **Text:** `#374151`

For paired-bar comparisons (platform-reported vs GA4-measured), use indigo for the ad platform series and a contrasting color for GA4. Pick colors so the user can tell which bar represents which data source without having to consult the legend.

### Skip the chart when

- The reconciliation answer is binary ("yes, tracking is healthy" / "no, LinkedIn has a UTM problem")
- The user just wants the dollar figures (CPL is $X)
- The deliverable is going into an email or a document where the chart goes inside the file

### Ad hoc analysis

For one-off questions outside the two bundled workflows (e.g. "do leads coming through landing page A have different MQL rates than leads from landing page B?", "is there a day-of-week effect on lead quality?"), write fresh analysis code in chat.

## Other Claude capabilities to leverage

**Built-in document skills.** When the deliverable is a file:
- Word documents (the sales leadership update is often this) → use the `docx` skill at `/mnt/skills/public/docx/SKILL.md`
- Spreadsheets (channel-level reconciliation tables, lead-source breakdowns) → use the `xlsx` skill at `/mnt/skills/public/xlsx/SKILL.md`
- Slide decks (when this becomes a planning input) → use the `pptx` skill at `/mnt/skills/public/pptx/SKILL.md`

Read the relevant SKILL.md *before* building the file.

**Other connectors when they're available.** If the user has HubSpot or Salesforce connected, you can pull MQL conversion rate and deal-size data by source — this is the single most valuable join in demand gen, because it answers "are we buying real leads or just clicks?" with actual pipeline data, not just form-fill counts. If Gmail is connected, sales-leadership emails can become drafts. If Slack is connected, short updates can be posted to the right channel.

**Web search.** Useful for industry CPL benchmarks, recent platform changes (e.g. iOS 14.5+ effects on Facebook attribution that might explain a measurement drop), or fresh research on B2B lead-quality patterns.

**Clarifying questions.** Use `ask_user_input_v0` for multiple-choice clarifications — attribution model preference, time window, which lead definition counts.

## When to use the bundled workflows

The `references/workflows.md` file contains the prompt sequences for seven core scenarios:

- **Traffic-to-conversion audit** — reconciling ad platform clicks/spend with GA4 sessions/conversions. Triggered by "Facebook CPA differs from GA4," "is my traffic engaged," "which channel converts on-site."
- **Lead generation efficiency comparison** — comparing CPL and lead conversion rate across B2B platforms. Triggered by "cost per lead by platform," "B2B lead gen efficiency."
- **Pipeline contribution by channel** — when CRM connectors are available, joining ad spend to pipeline created. Triggered by "which channels drive pipeline," "marketing-sourced pipeline," "ad spend to opportunity attribution."
- **MQL-to-SQL conversion rate by source** — quality measurement beyond CPL. Triggered by "lead quality by channel," "which leads convert," "MQL rate by source."
- **ABM campaign performance** — for B2B teams running target account lists. Triggered by "ABM campaign," "target account engagement," "named account analysis."
- **Email + ads integrated funnel** — how email nurture interacts with paid acquisition. Triggered by "email + paid attribution," "nurture funnel," "ad-to-email-to-sales path."
- **Webinar / gated content funnel analysis** — full funnel from paid promotion through registration, attendance, and downstream behavior. Triggered by "webinar funnel," "gated content attribution," "ebook download to MQL."

Read `references/workflows.md` when the user's request matches.

## Bundled scripts

- `scripts/funnel_reconciler.py` — joins ad platform with GA4 data, surfaces divergence per channel.
- `scripts/lead_efficiency.py` — compares CPL and lead conversion rate across platforms.
- `scripts/pipeline_attribution.py` — joins channel spend with CRM pipeline data to compute cost-per-opportunity and pipeline ROAS.
- `scripts/mql_quality.py` — computes MQL conversion rate and downstream metrics by source.
- `scripts/abm_engagement.py` — computes coverage and engagement metrics across a defined target account list.
- `scripts/email_paid_funnel.py` — builds the integrated funnel view across email + paid touchpoints.
- `scripts/gated_content_funnel.py` — full paid → form fill → MQL funnel for downloadable content.

## Bundled templates

- `assets/sales_leadership_email.md` — email template for budget reallocation updates.
- `assets/lead_efficiency_summary.md` — structured summary for lead-gen efficiency comparison.
- `assets/pipeline_attribution_report.md` — pipeline contribution report for sales leadership.
- `assets/lead_quality_diagnostic.md` — MQL quality findings doc with channel-level recommendations.
- `assets/abm_engagement_report.md` — target account coverage and engagement report.
- `assets/integrated_funnel_summary.md` — narrative summary of how email + paid interact.

## Things to watch for

**UTM hygiene is everything.** A campaign with missing UTM parameters will look like "(direct) / (none)" in GA4 even when it generated thousands of clicks. Before any reconciliation, check that ad platform clicks roughly match GA4 sessions from that source. If they're more than ~25% apart, the issue is tagging, not performance.

**Attribution window mismatch is a trap.** Facebook defaults to 7-day click / 1-day view; GA4 defaults to data-driven. These will never match exactly. Frame comparisons as "directional, not exact."

**Pipeline data lives in the CRM, not in Supermetrics.** For MQL-to-SQL conversion rates, the user needs a CRM connector (HubSpot, Salesforce). Ask before assuming.

**Bot traffic skews B2B clicks heavily.** Especially on LinkedIn Ads. A campaign showing 12% CTR and 0.1% conversion rate is more likely bot traffic than bad creative. Flag it before recommending action.

**"Cost per lead" is ambiguous.** A LinkedIn Lead Gen Forms "lead" is auto-filled and lightly qualified; a Google Ads form-submission "lead" has at least typed an email; a CRM "lead" has been scored. Always name which kind of lead is being counted.
