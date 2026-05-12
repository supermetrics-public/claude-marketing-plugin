---
name: field-marketer
description: Battle-tested workflows for field marketing managers running localized events and campaigns on tight timelines via the Supermetrics connector. Use whenever the user is doing event-related marketing analysis — pre-event channel efficiency comparisons, registration cost analysis, geo-targeted campaign measurement, post-event regional lift attribution. Trigger on phrases like "cost per registration," "event campaign performance," "which channel is driving event signups," "compare LinkedIn vs Google for our webinar," "did our SF event move the needle locally," "geo-targeted campaign analysis," "regional sales team update," "field event ROI." This skill handles the time-pressured analyses field marketers run before, during, and after events.
---

# Supermetrics workflows for the field marketing manager

This skill helps field marketing managers running localized events — webinars, in-person events, regional roadshows, conference activations — make data-driven decisions on tight timelines. The data needs to inform action this week, often today.

## Required: the Supermetrics connector

These workflows rely on the **Supermetrics connector for Claude**. Pre-event analysis needs ad platform data (LinkedIn Ads, Google Ads, Facebook Ads). Post-event geo analysis additionally benefits from geo-targeting being set up so regional data is available.

Before running anything, check that the connector is active — look for Supermetrics tools (`data_query`, `accounts_discovery`, etc.). If they aren't present, prompt the user:

> This workflow needs the Supermetrics connector for Claude. Install it at https://claude.ai/directory/connectors/cc599e7b-8c59-4e89-9bf0-36d47bb9ec80
>
> Connect at least one ad platform (LinkedIn Ads, Google Ads, or Facebook Ads). For geo-targeted analysis, make sure campaigns have location targeting so the data is available at the regional level.

## Core principles

Three principles apply throughout every workflow:

1. **Two-step pattern: pull, then analyze.** Even on tight timelines, don't combine retrieval and analysis. Event campaign data is often messy (inconsistent UTMs, registration tracking split between ad platforms and event platforms). Catching issues early matters more on a short timeline, not less.

2. **Communicate uncertainty.** Field marketing analysis is shaped by small sample sizes — a regional event might have 80 total registrations. The difference between "$45 per registration on LinkedIn" and "$52 per registration on Google" might be statistical noise. When analysis drives budget shifts on a short timeline, name when conclusions are tentative.

3. **Show, don't tell.** Even with small samples, visualizations make trade-offs and trends immediately legible. See "Choosing the right visualization" below.

## Choosing the right visualization

This skill doesn't prescribe specific charts. Decide based on what the data and the question actually are.

### Step 1 — What is the user trying to see?

| Question type | Visualization family |
|---|---|
| Cost-per-registration comparison across channels | Sorted horizontal bar chart |
| Registration pacing vs target as the event approaches | Line chart with cumulative registrations and dashed target line |
| Regional performance vs national baseline | Paired bars (target region vs rest-of-country) per metric |
| Trend in registrations over time, broken out by channel | Line chart, one series per channel |
| Day-by-day spend vs registrations during event run-up | Dual-axis bar/line chart |
| Geo-targeted ad performance across multiple regions | Sorted bar chart by region, or a small map if locations matter visually |

### Step 2 — What's the headline?

Before building, name the single thing the chart should make obvious. "Google Ads is generating registrations 18% cheaper than LinkedIn, but with smaller sample size" is a headline. "Channel comparison" is not.

Make the headline land within two seconds:
- **Sort by the metric of interest**
- **Highlight the winning channel** in a contrasting color
- **Add a reference line** for the registration target or the national baseline
- **Annotate sample-size caveats** directly on the chart (e.g. "Google: only 18 registrations — directional")

### Step 3 — Build as inline artifact

For data visualizations in chat, build a React component using Recharts.

### Standard color palette

- **Good / improving / positive direction:** `#10b981` (green)
- **Bad / declining / negative direction:** `#ef4444` (red)
- **Neutral / baseline / no-direction comparison:** `#6366f1` (indigo)
- **Flagged / warning / attention:** `#f59e0b` (amber)
- **Gridlines:** `#f3f4f6`
- **Text:** `#374151`

When sample sizes are small, low-confidence comparisons should be visually distinguished (lower opacity, hatched bars, or a "low confidence" badge) so they don't look like high-conviction findings.

### Skip the chart when

- The reconciliation is just a number ("Google CPL was $45, LinkedIn was $52")
- The deliverable is a quick Slack message to the regional team
- The sample size is so small the chart would imply confidence the data doesn't support

### Ad hoc analysis

For one-off questions outside the bundled workflows ("did email-driven signups outperform ad-driven signups for this event?", "which job titles in the registration list came from which channel?", "what's the no-show rate by channel?"), write fresh analysis code.

## Other Claude capabilities to leverage

**Built-in document skills.** When the deliverable is a file:
- Word documents (post-event summaries, ROI memos) → use the `docx` skill at `/mnt/skills/public/docx/SKILL.md`
- Spreadsheets (registration tracking, channel breakdowns) → use the `xlsx` skill at `/mnt/skills/public/xlsx/SKILL.md`
- Slide decks (post-event leadership readouts) → use the `pptx` skill at `/mnt/skills/public/pptx/SKILL.md`

Read the relevant SKILL.md before building.

**Other connectors when they're available.** If the user has Slack connected, regional team updates can be posted to the right channel — this is often the natural delivery for field marketing communication. If Gmail is connected, sales-team updates can become drafts. If Google Calendar is connected, you can look up the event date directly rather than asking.

**Web search.** Useful for industry event-marketing benchmarks (CPR norms by event type), competitive intelligence on what other companies are doing in the same region, or recent platform changes affecting geo-targeting accuracy.

**Clarifying questions.** Use `ask_user_input_v0` for multiple-choice — which event platform's registration count is the source of truth, which channels to compare, what counts as the "region" for geo analysis (city, metro, state).

## When to use the bundled workflows

The `references/workflows.md` file contains the prompt sequences for seven core scenarios:

- **Pre-event channel ROI** — comparing cost-per-registration across channels before an event. Triggered by "cost per registration," "which channel is driving signups."
- **Post-event geo-targeted measurement** — measuring whether a physical event drove regional digital lift. Triggered by "did the SF event move the needle," "regional lift."
- **Multi-event portfolio analysis** — comparing 10-30 events across a quarter to identify which event types produce the best ROI. Triggered by "event portfolio review," "which events are worth running again."
- **Event-driven pipeline tracking** — when CRM is connected, tracking pipeline created by attendees over 30/60/90 days. Triggered by "event-sourced pipeline," "did the event drive deals."
- **Account engagement scoring** — for B2B events, scoring engagement across target accounts at the event. Triggered by "which target accounts attended," "account-level event ROI."
- **Webinar funnel deep dive** — full webinar funnel from registration through attendance through downstream behavior. Triggered by "webinar funnel," "webinar performance review."
- **Partner / co-marketing event ROI** — measuring outcomes from events run with sponsors or co-marketing partners. Triggered by "partner event ROI," "co-marketing event," "sponsorship value."

Read `references/workflows.md` when the user's request matches.

## Bundled scripts

- `scripts/registration_cost_compare.py` — compares cost per registration across channels with sample-size flagging.
- `scripts/geo_lift_analyzer.py` — compares target region performance against baseline ex-region.
- `scripts/event_portfolio.py` — ranks events across a quarter by composite ROI score (cost per attendee, downstream conversions, pipeline if available).
- `scripts/event_pipeline_tracker.py` — joins event attendees with CRM pipeline data over 30/60/90 day windows.
- `scripts/account_engagement.py` — scores target account engagement using event attendance + ad signals + activity data.
- `scripts/webinar_funnel.py` — full webinar funnel analysis with cohort breakdown by registration source.
- `scripts/partner_event_roi.py` — partner event ROI analysis accounting for sponsorship costs, co-marketing reach, and pipeline.

## Bundled templates

- `assets/regional_team_update.md` — short update message for the regional sales team.
- `assets/post_event_lift_summary.md` — geo-lift summary doc.
- `assets/event_portfolio_review.md` — quarterly event portfolio review doc.
- `assets/event_pipeline_report.md` — event-attributed pipeline doc for sales leadership.
- `assets/account_engagement_brief.md` — target-account engagement brief from an event.
- `assets/webinar_funnel_summary.md` — webinar funnel doc.
- `assets/partner_event_recap.md` — partner/co-marketing event recap with shared metrics.

## Things to watch for

**Registration tracking is often split.** Ad platforms report "form submissions," event platforms report "registrations." These rarely match. Ask the user which is the source of truth.

**UTM tagging on event campaigns is unusually error-prone** — event campaigns get spun up quickly with copy-pasted tagging. Before treating data as gospel, verify that ad-platform registration counts match the event platform's by more than ~15%. If not, surface the tagging issue first.

**Geo data has lag.** Some platforms report regional breakdowns with 24–48 hour additional lag beyond standard reporting. Surface the latency if the user is asking about yesterday's regional numbers.

**National averages aren't really national — they include the target region.** When measuring regional lift, exclude the target region from the baseline calculation. The geo_lift_analyzer script handles this.

**Sample sizes are small.** A regional event with 80 registrations has limited statistical power. A 20% gap between channels at this scale could easily be noise. Respect the sample-size flag in the recommendation.

**Post-event lift is hard to attribute.** Did the event drive the lift? Or the targeted ads that supported it? Or general regional growth? When reporting lift, note what's confounded and resist the urge to claim the event caused all of it.
