---
name: performance-marketer
description: Battle-tested workflows for performance marketers running paid campaigns on Google Ads, Facebook Ads, LinkedIn Ads, TikTok Ads, and Microsoft Ads via the Supermetrics connector. Use whenever the user is doing campaign-level analysis, optimization, or reporting work — including week-over-week performance comparisons, ad fatigue and frequency audits, creative testing, CPA/CTR/CPC analysis, budget shifting between channels, ad copy iteration, and drafting refresh emails to creative teams. Trigger this even when the user doesn't say "Supermetrics" explicitly — phrases like "my Facebook campaign is underperforming," "compare last week vs this week on LinkedIn," "which ads should I pause," "ad fatigue," "creative refresh," or "rank my ads by CPA" all signal performance marketing work that benefits from these structured workflows.
---

# Supermetrics workflows for the performance marketer

This skill helps performance marketers analyze paid campaigns across Google Ads, Facebook Ads, LinkedIn Ads, TikTok Ads, and Microsoft Ads. The workflows are designed to produce decisions a media buyer can act on today — not dashboards that need to be interpreted.

## Required: the Supermetrics connector

These workflows rely on the **Supermetrics connector for Claude**, which pulls live data from connected ad platforms. Before running anything, check that the connector is active — look for Supermetrics tools in this session (e.g. `data_query`, `accounts_discovery`, `field_discovery`).

If they aren't present, the user doesn't have the connector installed yet. Stop and prompt them:

> This workflow needs the Supermetrics connector for Claude to pull your live ad data. You can install it at https://claude.ai/directory/connectors/cc599e7b-8c59-4e89-9bf0-36d47bb9ec80
>
> Once it's installed, authenticate and connect at least one ad platform (Google Ads, Facebook Ads, LinkedIn Ads, etc.).

Don't fabricate placeholder data, and don't ask the user to paste a CSV unless they explicitly prefer that route.

## Core principles

Three principles apply throughout every workflow:

1. **Two-step pattern: pull, then analyze.** Don't combine data retrieval and complex analysis into a single tool call. Pull the raw data first, confirm what was returned, then run analysis as a separate step. This catches data issues early.

2. **Show, don't tell.** When the analysis produces numbers worth comparing — across time periods, channels, ads, or anything else — build a visual. The user's time-to-decision is shorter with a chart than with prose. See "Choosing the right visualization" below.

3. **One serious query at a time.** Don't fire several heavy queries in parallel. Sequence the work.

## Choosing the right visualization

This skill doesn't prescribe specific charts for specific workflows. Instead, decide visualization based on what the data and the question actually are. Use this framework:

### Step 1 — What is the user trying to see?

| Question type | Visualization family |
|---|---|
| Comparison across discrete items (campaigns, ads, channels) | Bar chart (horizontal if the labels are long) |
| Change over time | Line chart (or area if showing accumulation) |
| Relationship between two metrics (e.g. frequency vs CTR) | Scatter plot |
| Distribution of a single metric across many items | Histogram or sorted bar chart |
| Two-dimensional categorical breakdown (e.g. day-of-week × hour) | Heatmap |
| Part-to-whole when there are few parts (<6) | Stacked bar — avoid pie charts |
| Ranking with magnitude | Sorted horizontal bars |
| Trend with target/threshold | Line chart with a reference line |

### Step 2 — What's the headline?

Before building, name the single thing the chart should make obvious. "CTR is dropping on every campaign except one" is a headline. "Performance data" is not.

The chart's design should make the headline land within two seconds of looking at it. Techniques that help:
- **Sort by the metric of interest** (don't leave alphabetical order)
- **Highlight one bar or one point** in a contrasting color when there's a clear standout
- **Add a reference line** for the baseline, target, or account average
- **Annotate the worst offender or the winner** directly on the chart

If you can't name the headline, the visualization isn't ready — the analysis probably isn't either.

### Step 3 — Build it as an inline artifact

For data visualizations in chat, build a React component using Recharts (available in the artifact environment). Inline artifacts are the right default — they render immediately and the user doesn't have to leave the conversation.

For one-off conceptual visuals (e.g. funnel diagrams, flowcharts) that aren't strictly chart-able, use the `visualize:show_widget` tool instead.

### Standard color palette

For consistency across charts in the same conversation, use this palette:
- **Good / improving / positive direction:** `#10b981` (green)
- **Bad / declining / negative direction:** `#ef4444` (red)
- **Neutral / baseline / no-direction comparison:** `#6366f1` (indigo)
- **Flagged / warning / attention:** `#f59e0b` (amber)
- **Gridlines:** `#f3f4f6`
- **Text:** `#374151`

Color by *business meaning*, not by sign. If CPC is up 20%, the bar is red because CPC up is bad — even though the number is positive. If CPA is down 15%, the bar is green for the same reason.

### Skip the chart when

- The answer is 1–3 numbers (just state them: "Total spend: $12k, conversions: 240, CPA: $50")
- The data is text-heavy (ad copy, recommendations) — those are prose or markdown
- The output is going into a Word doc or slide deck where the chart will live inside the file, not in chat

### Ad hoc analysis

The bundled scripts handle repeatable patterns. For one-off questions ("does ad copy length correlate with CPA in this dataset?" or "is there a time-of-day effect on weekend traffic?"), write fresh analysis code in the chat — pull the data, compute the answer, build the right visualization for it. Don't force a one-off question through a script that wasn't designed for it.

## Other Claude capabilities to leverage

**Built-in document skills.** When a workflow's final step is a file deliverable:
- Word documents (optimization reports, recommendations) → use the `docx` skill at `/mnt/skills/public/docx/SKILL.md`
- Spreadsheets (campaign performance tables for sorting/filtering) → use the `xlsx` skill at `/mnt/skills/public/xlsx/SKILL.md`
- Slide decks (creative review presentations) → use the `pptx` skill at `/mnt/skills/public/pptx/SKILL.md`

Read the relevant SKILL.md *before* writing any code or building any file.

**Other connectors when they're available.** If the user has CRM connectors active (HubSpot, Salesforce), you can pull lead-quality data and join it with ad-platform CPA — answering "are we buying real leads or just clicks?" If they have Gmail, you can save email drafts directly. If they have Slack, you can post update messages to the right channel. These are opportunistic moves — only use them when they're already available in the session, never assume they exist.

**Web search.** Useful for industry benchmarks, recent platform policy changes (e.g. "new Meta attribution defaults"), or competitive context. Don't over-use it — most performance marketing answers come from the user's own data.

**Clarifying questions.** When a multiple-choice question would resolve ambiguity (attribution window, time period, scope), use the `ask_user_input_v0` tool. It renders tappable buttons rather than asking the user to type — much faster on mobile.

## When to use the bundled workflows

The `references/workflows.md` file contains the prompt sequences for seven core scenarios:

- **Week-over-week campaign optimization** — spotting efficiency decline before the monthly budget gets drained. Triggered by "compare last week," "what changed," "is performance declining."
- **Ad fatigue and frequency audit** — finding creatives that are burning out. Triggered by "ad fatigue," "frequency check," "which ads need refresh."
- **Creative concept testing and iteration** — identifying winners from a creative test and generating new variations. Triggered by "which creative is winning," "rank by CPA," "write new ad copy."
- **Daily morning standup check** — single-pull cross-platform overview surfacing anomalies that need action today. Triggered by "what happened yesterday," "morning check," "anything broken overnight."
- **Search term audit and negative keywords** — finding wasted spend on irrelevant queries in Google Ads or Microsoft Ads, building a negative keyword list. Triggered by "wasted search spend," "negative keywords," "search term report."
- **Cross-channel attribution comparison** — comparing how different attribution models credit channels differently. Triggered by "last-click vs data-driven," "why does Facebook claim more conversions than GA4 sees," "attribution comparison."
- **Budget reallocation modeler** — given current ROAS by channel and a target spend, model the optimal reallocation accounting for diminishing returns. Triggered by "where should I shift budget," "optimal budget mix," "reallocation model."

Read `references/workflows.md` when the user's request matches.

## Bundled scripts

- `scripts/wow_comparison.py` — compute week-over-week deltas (absolute and percentage) for any metric, flagging changes outside a configurable threshold.
- `scripts/ad_fatigue_detector.py` — identify ads exceeding a frequency threshold with declining CTR over a configurable window.
- `scripts/cpa_ranker.py` — rank ads by cost per acquisition with optional grouping by ad format, placement, or campaign.
- `scripts/daily_check.py` — cross-platform daily overview with automatic anomaly flagging on CPC, CPA, conversion volume, and spend pacing.
- `scripts/search_term_auditor.py` — analyzes a Google Ads or Microsoft Ads search term report; identifies high-cost low-conversion queries and proposes negative keywords.
- `scripts/attribution_comparator.py` — compares conversion counts across platform-reported and GA4-measured views, surfaces divergence per channel.
- `scripts/budget_optimizer.py` — given channel-level ROAS data and a target spend, models a recommended reallocation with diminishing-returns dampening.

Each script takes CSV input and produces a clean table — which you then turn into an inline chart for the chat.

## Bundled templates

- `assets/creative_refresh_email.md` — template for notifying the creative team about ad refresh recommendations.
- `assets/optimization_doc.md` — structure for a week-over-week optimization recommendation doc.
- `assets/ad_copy_variations.md` — framework for writing new ad copy variations off a winning creative.
- `assets/daily_standup_summary.md` — short morning summary template — what happened, what to act on, what to watch.
- `assets/negative_keyword_recommendations.md` — structured doc of proposed negative keywords with rationale per term, for upload to the ad platform.
- `assets/budget_reallocation_plan.md` — concise plan output for the budget reallocation workflow, naming source/destination channels with specific dollar amounts.

## Things to watch for

**Naming conventions vary.** When a user references a campaign by name, search broadly. If multiple campaigns match, list them and let the user pick.

**Time windows matter.** "Last 7 days" can mean rolling 7-day or calendar week. When ambiguous, ask once, then remember the convention.

**Recommendations should be specific.** "Pause underperforming ads" is not a recommendation. "Pause ad ABC123 (CPA $84, 3.2x account average) and shift its $200/day to ad XYZ789 (CPA $19)" is. Always aim for the second version.

**Currency and timezone.** Supermetrics returns data in the account's currency and timezone. For users working across multiple markets, surface this before computing aggregates.

**When data looks suspicious.** A sudden zero-conversion day or 10x CPC spike is more often a tracking break than a real performance issue. Flag anomalies before recommending action — the right next step might be to fix tracking, not to pause spend.
