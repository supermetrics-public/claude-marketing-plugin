# Performance marketer workflows

Seven workflow patterns for the most common performance marketing analysis tasks. Each follows the same shape: pull data, run analysis, visualize the answer, produce a deliverable.

## Workflow 1: Week-over-week campaign optimization

**When to use:** the user wants to spot efficiency decline (rising CPC, dropping conversion rate, climbing CPA) before it eats the monthly budget. Common phrasings: "compare last week to the week before," "is performance dropping," "what changed in the campaign."

**Platforms typically involved:** LinkedIn Ads, Facebook Ads, Google Ads. Confirm if the user has specific platforms in mind.

### Step 1 — Clarify the comparison (only if ambiguous)
If the user hasn't specified the time window or scope, use `ask_user_input_v0` to clarify:
- Time window: rolling 7-day, calendar week, last 30 days, etc.
- Scope: campaign level, ad set level, or ad level

Skip if the user's phrasing already makes it obvious.

### Step 2 — Pull the data
> Pull performance data for the [campaign name] running on [platforms] for [current period] and [prior period]. Include spend, impressions, clicks, CTR, CPC, conversions, and CPA.

If the user mentioned specific KPIs (ROAS, leads, video views), include those too.

### Step 3 — Run the comparison
Use `scripts/wow_comparison.py` to compute the deltas. The script flags metrics that moved more than ±10% by default.

### Step 4 — Visualize the changes
Build an inline chart. The question the chart needs to answer: **what changed, and by how much?**

Decide the chart based on what's being compared:
- Comparing the same metrics across two time periods, one campaign at a time → horizontal bar chart of percentage changes, one bar per metric, color by business meaning (improvement vs decline)
- Comparing multiple campaigns side-by-side → grouped bars or small multiples (one mini-chart per campaign)
- Trend over many weeks rather than two snapshots → line chart with a reference line for the baseline period

Whatever you build, sort by the metric of interest (don't leave alphabetical), highlight flagged metrics with an outline or marker, and name the headline above the chart ("CTR dropped on 4 of 5 campaigns this week" — not "Performance data").

### Step 5 — Recommendations
> Generate recommendations: which specific ads to pause, where to shift the remaining budget, and what demographic segments are overperforming.

Build from `assets/optimization_doc.md`. Be specific: name ads, give dollar amounts, identify segments by their actual labels (age 25–34, mobile, iOS).

### Step 6 — Package the deliverable
Default delivery is inline markdown — fast, no friction. If the user asks for something they can share or save, the right tool depends on what they want:
- A Word doc to send around → use the `docx` skill
- A spreadsheet to sort and filter → use the `xlsx` skill
- A message to post in Slack (if a Slack connector is available) → adapt the recommendation to Slack tone (shorter, no formal greeting)

Don't overwhelm the user with options up front. Pick the sensible default and let them redirect.

### Common variations
- **By ad set instead of campaign** — re-run step 2 with `ad_set_name` as the grouping dimension.
- **Just one platform** — drop the cross-channel framing in step 4.
- **Compare to last month instead** — swap the time windows in step 2; the rest is identical.
- **Add lead quality from a CRM** — if a HubSpot or Salesforce connector is active, pull MQL conversion rate by source and join with the ad-platform CPA. The combined view ("$50 ad CPA but only 8% become MQLs vs another channel's $80 ad CPA with 35% MQLs") is more useful than ad-platform CPA alone. Skip if the CRM connector isn't available.

---

## Workflow 2: Ad fatigue and frequency check

**When to use:** the user suspects ad creatives are burning out — previously strong ads losing CTR, climbing frequency, rising CPC. Often ends with notifying the creative team about which ads need refresh.

**Platforms typically involved:** Facebook Ads (frequency is a Facebook-native metric), Google Ads. LinkedIn Ads has its own frequency concept when available.

### Step 1 — Pull the data
> Pull the last 30 days of performance data grouped by ad name, with impressions, frequency, CTR, and CPC.

Include `ad_id` if the user will need to act on this in-platform.

### Step 2 — Identify fatigued ads
Use `scripts/ad_fatigue_detector.py`. Default thresholds: frequency >3.5 and CTR decline >20% week-over-week. If the user wants different thresholds, accept them and pass to the script.

### Step 3 — Visualize the fatigue landscape
The question the chart needs to answer: **which ads are fatigued, how severely, and how much spend is exposed to the problem?**

The most informative visualization for this is usually a scatter plot — frequency on the x-axis, recent CTR on the y-axis, dot size weighted by spend, dot color encoding a third dimension (CPC trend, or simply flagged vs not). Shade or label the fatigue zone explicitly. The user sees at a glance which ads are in trouble and which are still healthy.

Alternative when the user has few ads (under 10): a horizontal bar chart ranking ads by severity, with spend annotated next to each bar.

Whichever you pick, name the worst offender explicitly when surfacing the chart — don't make the user visually scan.

### Step 4 — Refresh recommendations
For each flagged ad, state what's happening (frequency X, CTR down Y%, CPC up Z%) and what to do (pause, refresh creative, refresh copy only, swap thumbnail). Prioritize by spend impact — the $5k/week ad needs attention before the $50/week one.

### Step 5 — Notify the creative team
Build the email body using `assets/creative_refresh_email.md`. The default delivery is markdown inline so the user can review and send themselves. If the user wants it as a doc, use the `docx` skill. If Gmail is connected and the user wants it as a draft, offer to save it there.

### Common variations
- **No frequency threshold known** — use 3.5 as a sensible default or compute +1 standard deviation above the account's typical range.
- **Just top 10 fatigued ads** — limit the script output and the chart to top N by spend or severity.

---

## Workflow 3: Creative concept testing and iteration

**When to use:** the user is running a creative test (multiple variants of an ad in the same campaign) and wants to identify winners and generate new variations.

**Platforms typically involved:** Facebook Ads, LinkedIn Ads, sometimes TikTok Ads.

### Step 1 — Pull the data
> Pull the last 14 days for [campaign name] across [platforms], broken down by individual ad name and ad format.

`ad_format` matters here — is video beating static? Include thumbnail/preview links if Supermetrics returns them.

### Step 2 — Rank by efficiency
Use `scripts/cpa_ranker.py` with `--group-by ad_format` to get both: top ads by CPA and the format-level comparison.

### Step 3 — Visualize the results
Two questions to answer here, often best as two charts rather than one crowded one:
- **Which ads are winning?** A ranked horizontal bar chart sorted by CPA ascending, with format encoded as bar color.
- **Which format wins on average?** A small comparison chart with format on the x-axis and the efficiency metrics (CPA, CTR, conversion rate) on the y-axis.

The user often needs both views — "video has 18% better CPA on average, but the single best ad is a static" is a real and important finding that one chart alone can miss.

### Step 4 — Write new variations
Use `assets/ad_copy_variations.md`. Identify what's working in the winners (the hook, the angle, the audience tilt — not just the words) and preserve that. Vary CTA, framing, or proof point. Don't synonym-swap.

### Step 5 — Output the variations
Default delivery is inline markdown. If the user wants a spreadsheet they can hand to ops for upload, use the `xlsx` skill with columns for headline, body, CTA, target audience, and hypothesis.

### Common variations
- **Rank by ROAS instead of CPA** — pass `--metric roas` to the ranker.
- **New audiences vs lookalikes** — re-run with `audience` as the grouping dimension.
- **Headlines only, not body copy** — the variations template has both sections; pick the relevant one.
- **Industry benchmark CTR** — if the user wants context for whether their numbers are good, use web search to find recent industry benchmark data and overlay as a reference line on the chart.

---

## Workflow 4: Daily morning standup check

**When to use:** the user wants a quick scan of what happened yesterday across all paid channels — anomalies, wins, things to investigate. The most common "I just got to my desk, give me the headlines" workflow.

**Platforms typically involved:** all connected ad platforms (Google Ads, Facebook Ads, LinkedIn Ads, TikTok Ads, Microsoft Ads, etc.).

### Step 1 — Pull yesterday and the trailing baseline
> Pull yesterday's spend, impressions, clicks, conversions, CPA, and ROAS across all connected ad platforms. Also pull the trailing 7-day average for the same metrics, excluding yesterday.

The baseline matters — yesterday in isolation is meaningless. The comparison to the trailing average is what surfaces anomalies.

### Step 2 — Run the daily check
Use `scripts/daily_check.py`. The script computes yesterday-vs-baseline ratios per channel and per campaign, and flags anomalies on:
- Spend ±25% off the daily baseline (over- or under-pacing)
- CPA ±30% off (cost spike)
- Zero conversions on a campaign that normally produces conversions (tracking issue suspected)
- ROAS down >20% (efficiency drop)

### Step 3 — Visualize the morning view
The question the chart needs to answer: **what's normal, what's not, and what needs my attention?**

A horizontal bar chart of percent-deviation-from-baseline per channel works as the primary visualization, with three color zones: green within ±10%, amber ±10–25%, red beyond ±25%. The user scans for red bars first.

When the user has many channels (8+), a small-multiples grid — one mini bar chart per metric (spend, CPA, ROAS) with channels on the y-axis — surfaces patterns by metric rather than by channel.

### Step 4 — Action list
Build from `assets/daily_standup_summary.md`. The summary has three sections: **what happened** (the headline), **what to act on today** (specific campaigns or ad sets, with the action), **what to watch** (early signals that aren't yet actionable).

### Step 5 — Output
Default delivery: inline markdown. If the user wants this delivered as a recurring Slack message and a Slack connector is active, format it for Slack tone (shorter, no formal greeting) and offer to post.

### Common variations
- **Just one platform** — filter to a single platform in step 1.
- **Weekly instead of daily** — swap the time windows: pull last 7 days and compare to the prior 7-day average.
- **Custom anomaly thresholds** — pass `--spend-threshold`, `--cpa-threshold`, `--roas-threshold` to the script.

---

## Workflow 5: Search term audit and negative keywords

**When to use:** the user runs Google Ads or Microsoft Ads search campaigns and wants to find wasted spend on irrelevant queries, building a negative keyword list to upload to the platform.

**Platforms typically involved:** Google Ads (search campaigns), Microsoft Ads. This workflow doesn't apply to social platforms.

### Step 1 — Pull the search term report
> Pull the search term report from [Google Ads / Microsoft Ads] for the last 30 days, including search term, matched keyword, campaign, ad group, clicks, cost, and conversions.

The search term report is the granular log of actual user queries that triggered the ads — distinct from the keyword list, which is what the user bid on. Mismatch between intent and actual query is where waste lives.

### Step 2 — Audit the terms
Use `scripts/search_term_auditor.py`. The script flags queries that:
- Cost more than $X (configurable) with zero conversions
- Have CPC more than 2x the campaign average
- Match obvious irrelevance patterns (competitor brand names, "free", "jobs", "career", "wikipedia" depending on the user's industry context)

The user provides the irrelevance patterns; the script doesn't guess them. If the user doesn't have a list, suggest a starter set based on their industry and confirm.

### Step 3 — Visualize the waste
The question the chart needs to answer: **how much money are these terms costing, and which patterns are the worst?**

A horizontal bar chart of cost-per-term (top 20 worst offenders) is the most useful primary visualization. If the user has clearly grouped patterns (competitor names vs informational queries vs unrelated terms), a stacked bar chart by pattern type surfaces where the largest categories of waste live.

A pie chart or treemap of cost by pattern type works only if there are ≤5 clear categories.

### Step 4 — Build the negative keyword list
Use `assets/negative_keyword_recommendations.md`. For each proposed negative keyword, the doc includes the match type recommendation (exact / phrase / broad), the rationale (cost incurred, related queries impacted), and the campaigns where the negative should be applied.

### Step 5 — Output
Default delivery: the table as a spreadsheet ready for ad-platform upload, using the `xlsx` skill. Most ad platforms accept negative keyword bulk uploads in CSV/XLSX format. If the user prefers, deliver markdown inline.

### Common variations
- **Just one campaign** — filter to a single campaign in step 1.
- **Conservative thresholds** — start with $50 wasted-spend threshold instead of $200, to surface smaller wins.
- **Already-running negatives** — if the user provides their current negative keyword list, exclude those terms from the recommendations.

---

## Workflow 6: Cross-channel attribution comparison

**When to use:** the user is reconciling different views of conversion data — Facebook's pixel says one thing, GA4 says another, the platform's data-driven attribution says a third. Common before any cross-channel budget decision.

**Platforms typically involved:** Google Ads, Facebook Ads, LinkedIn Ads + GA4 (mandatory for the comparison). Mobile attribution platforms (AppsFlyer, Adjust, Branch) if the user has mobile apps.

### Step 1 — Pull each view
> Pull the last 30 days of conversion counts per channel from [Google Ads, Facebook Ads, LinkedIn Ads] using each platform's default attribution. Then pull the same channels' conversions from Google Analytics 4 using GA4's default attribution.

Confirm with the user what each platform's attribution setting is — Facebook's 7-day-click / 1-day-view is the default; Google's is data-driven; GA4 defaults to data-driven. If the user has customized any of these, note it explicitly.

### Step 2 — Reconcile
Use `scripts/attribution_comparator.py`. The script joins on channel name and computes the divergence between each platform's self-reported conversions and GA4's view. Flags channels where the gap exceeds ±25%.

### Step 3 — Visualize the disagreement
The question the chart needs to answer: **which channels disagree most between platform-reported and GA4-measured views, and how does this affect ROAS?**

A paired bar chart per channel works well: two bars per channel, one for platform-reported conversions and one for GA4-measured. Big gaps between the pairs are the story. Color the gaps amber when they exceed the 25% threshold.

A secondary visualization useful here: a slopegraph showing how each channel's *rank* changes between the two views. Facebook might be the #1 channel by Facebook's own attribution but the #3 channel by GA4. This rank-change view is more useful for budget decisions than absolute numbers.

### Step 4 — Frame the implication
The point of this analysis isn't to declare one view correct. It's to make the disagreement visible before a budget decision. The deliverable names what the user can and can't conclude:
- Comparing channels using each platform's own attribution → invalid (apples to oranges)
- Comparing channels using a single attribution lens (GA4 or a third-party MMM) → valid
- Estimating "true" conversion contribution → requires more than these two views; suggest incrementality testing or media mix modeling if the stakes warrant

### Step 5 — Output
Default: chart + framing inline as markdown. If the deliverable is going to a finance or leadership audience, use the `docx` skill for a clean memo.

### Common variations
- **Add mobile attribution** — if AppsFlyer, Adjust, or Branch is connected, add their view as a third comparison column.
- **Include a third-party MMM result** — if the user has results from a media mix model, layer those as a fourth view to show the spread.
- **Per-conversion-type breakdown** — if the user tracks multiple conversion events (purchases, leads, signups), run the comparison per type. Sometimes one type tracks cleanly across platforms and another doesn't.

---

## Workflow 7: Budget reallocation modeler

**When to use:** the user has current ROAS by channel and wants to model the optimal budget shift for next period, accounting for the reality that more spend on a winner doesn't produce the same ROAS at higher volume.

**Platforms typically involved:** all connected ad platforms with meaningful spend.

### Step 1 — Pull current performance
> Pull the last 30-60 days of spend and revenue (or conversions × value) by channel from [the connected ad platforms]. Include daily breakdown to surface diminishing-returns signals.

Daily granularity matters — the script needs it to detect whether ROAS holds at higher spend or compresses.

### Step 2 — Get the target spend
Ask the user (via `ask_user_input_v0` if needed): what's the total budget for next period? Same as current, ±10%, or a specific number?

### Step 3 — Run the optimizer
Use `scripts/budget_optimizer.py`. The script:
1. Computes current channel ROAS and spend
2. Estimates a diminishing-returns dampening factor per channel from the daily data (channels with higher spend variance and stable ROAS get dampened less; channels with ROAS that already shows compression get dampened more)
3. Models reallocation toward higher-ROAS channels, but applies the dampening so the model doesn't naively dump all budget into the single winner
4. Outputs proposed spend per channel and projected total revenue

This is a model, not a prediction. The script's output is "given these assumptions, here's the math" — not "this will happen."

### Step 4 — Visualize the recommendation
The question the chart needs to answer: **what's the proposed shift, and what's the projected impact?**

Two visualizations work well together:
- A paired bar chart per channel: current spend vs proposed spend. Sorted by absolute shift magnitude.
- A waterfall chart showing the projected revenue impact: starting from current total revenue, adding contributions from spend increases and subtractions from spend decreases, ending at projected new total.

### Step 5 — Frame the assumptions
Build from `assets/budget_reallocation_plan.md`. The plan must include:
- Specific dollar amounts per channel (current vs proposed)
- Projected revenue impact with the assumption disclosure
- The dampening logic (so finance can challenge the model intelligently)
- A 2-week checkpoint date — when to verify whether the projection is tracking

### Step 6 — Output
Default delivery: chart + plan inline as markdown. If the deliverable is going to finance for approval, use the `docx` skill.

### Common variations
- **Constrained channels** — if some channels have fixed budgets (e.g. a contracted minimum spend on a platform), pass them as `--locked` to the script. The optimizer will only reallocate the unconstrained portion.
- **Aggressive vs conservative shifts** — pass `--max-shift-pct` (default 25%) to cap how much any single channel can move. Conservative finance teams want smaller shifts.
- **Goal: total conversions, not revenue** — pass `--metric cpa`. The optimizer flips to minimizing CPA-weighted spend rather than maximizing revenue.

---

## Ad hoc analysis

The bundled scripts handle the repeatable patterns above. When the user asks something the scripts weren't designed for — "is there a time-of-day effect on this campaign?", "does ad copy length correlate with CPA?", "what's the spend distribution across ad sets — concentrated or spread?" — write fresh analysis code, run it, and build whatever visualization fits the question.

The "Choosing the right visualization" framework in the SKILL.md gives you the decision tree for which chart family fits which type of question. Apply it case by case.

---

## A note on data freshness

Supermetrics returns data with a few hours of latency depending on the platform. Facebook can be near-real-time; LinkedIn often lags 24 hours; Google Ads conversions can keep updating for up to 72 hours. When the user is making same-day decisions, surface this latency so they know what "yesterday's data" actually means.
