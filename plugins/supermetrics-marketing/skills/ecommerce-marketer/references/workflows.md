# Ecommerce marketer workflows

Seven workflow patterns for ecommerce paid acquisition: from daily cross-platform ROAS through SKU-level analysis, new-vs-returning customer economics, AOV and basket composition, retention cohorts, and pre-promo planning.

## Workflow 1: Cross-platform ROAS and purchase behavior

**When to use:** the user is doing a periodic (usually monthly) review of paid acquisition efficiency across their main ecommerce platforms, and wants to surface day-of-week patterns to inform bid strategy.

**Platforms typically involved:** Google Ads and Facebook Ads at minimum. Sometimes TikTok Ads, Pinterest Ads, Snapchat Ads, Amazon Ads.

### Step 1 — Pull the data
> Pull the last 30 days of daily ad spend and purchase conversion value from [Google Ads, Facebook Ads, etc.].

Daily granularity matters — day-of-week analysis requires it. Make sure data has conversion value (revenue), not just count. If conversion value isn't populated, this workflow can't run as designed; surface that and offer the count-based version instead.

### Step 2 — Compute blended ROAS
Use `scripts/blended_roas.py`. The script computes blended ROAS daily, weekly, and by day-of-week. Mention the double-count caveat once when introducing the number, not repeatedly.

### Step 3 — Visualize the trend and patterns
Two questions worth surfacing, often as two charts:

**"Is ROAS trending up, down, or stable?"** A line chart of daily blended ROAS over the 30-day window, with a horizontal reference line at the period average. The chart makes drift visible — ROAS that's volatile day-over-day tells a different story than ROAS drifting in one direction.

**"Which days of the week perform best?"** This is the prime case for a heatmap: rows = day of week (Monday-Sunday), columns = a single column if data is daily-only, or hour columns if hourly data is available. Cell color = ROAS or conversion rate, with a diverging red-to-green scale centered on the period average. Above-average days appear green, below-average appear red, intensity shows magnitude.

If a heatmap is overkill for the user's data shape, a sorted horizontal bar chart of average ROAS by day of week works as the fallback.

### Step 4 — Budget weighting recommendation
> Build a strategic plan for adjusting weekly budget allocation to weight spending more heavily toward the days demonstrating the strongest purchase intent.

Use `assets/dow_budget_strategy.md`. The recommendation should propose a weighting (e.g. Tuesday +20%, Friday -15%) and explicitly flag what would invalidate the strategy — usually a promo period scrambling normal patterns.

### Step 5 — Output
Default delivery: charts in chat plus a markdown recommendation. If the user wants a Word doc to share with the team, use the `docx` skill.

### Common variations
- **Add TikTok, Pinterest** — same workflow, expand the platform list. Watch for platforms with low spend producing noisy daily numbers.
- **Compare to prior 30-day period** — pull a second window and overlay both lines on the trend chart.
- **Break down by product category** — needs product-level data from Shopping/catalog feeds. Available if the user runs Shopping campaigns; not available if they run purely image/video.

---

## Workflow 2: Promotional campaign anomaly detection

**When to use:** the user is running a high-stakes promo (BFCM, holiday sale, flash sale) and wants to catch cost-per-purchase anomalies before they burn the day's budget.

**Platforms typically involved:** Facebook Ads most often (BFCM spend concentrates there for many DTC brands). Google Ads where applicable.

### Step 1 — Pull yesterday's promo data
> Pull yesterday's data for the [promo campaign filter — e.g. campaigns containing "BFCM" or "Black Friday"] on Facebook Ads. Include cost, impressions, and total purchases per ad set.

Use the user's actual filter convention. Confirm if unclear. Ad-set granularity matters — a campaign-level 3x spike might be driven by one bad ad set, not the whole campaign.

### Step 2 — Pull the baseline
Get the prior 6 days of data for the same campaigns. The script computes the rolling-average baseline.

### Step 3 — Flag the anomaly
Use `scripts/anomaly_detector.py`. Default threshold: yesterday's cost-per-purchase >3x the trailing 6-day average. The script identifies which ad sets are responsible and flags candidate causes (tracking failure vs real performance issue).

If no anomaly is detected, surface that clearly. "No anomaly, performance within expected range" is a valid and useful answer.

### Step 4 — Visualize the spike (if one exists)
The question the chart needs to answer: **which ad sets are anomalous, by how much, and what's the likely cause?**

A line chart showing the trailing 7 days of cost-per-purchase per anomalous ad set works well — most days sit in a horizontal band, then yesterday's value spikes upward. The spike day gets highlighted in amber. A reference line at the baseline average makes the deviation visible.

When multiple ad sets are anomalous, a sorted horizontal bar chart of yesterday's CPP-to-baseline ratio surfaces which are the worst — the user fixes the biggest bleeders first.

For non-anomalous ad sets, no chart is needed — just the headline.

### Step 5 — Verify before alerting
Before drafting any alert email: verify the spike is real, not a tracking issue. The most common causes of an apparent 3x spike are pixel failures, renamed events, or deduplication issues — not real performance failures. The script's candidate-cause column points at likely explanations; investigation is on the user.

### Step 6 — Draft the urgent alert
Use `assets/media_buyer_alert_email.md`. The email needs to be short, specific (named ad sets), and recommend a concrete action.

Default delivery: markdown inline so the user reviews before sending. If Gmail is connected, offer to save as a draft. If the user prefers Slack and a Slack connector is available, post the alert to the relevant channel instead — often faster during a promo when the media buying team is fielding many messages per hour.

### Common variations
- **Baseline isn't 6 days, it's same-promo-week-last-year** — pass a baseline CSV via `--baseline-csv`. The script accepts it.
- **Monitor ROAS, not cost per purchase** — same workflow, swap the metric. Pass `--metric roas`.
- **Hourly granularity, not daily** — supported on Facebook and Google but noise floor is high. Use only for high-spend ($50k+/day) campaigns.

---

## Workflow 3: Product / SKU-level performance

**When to use:** the user wants to know which specific products are driving paid-acquisition revenue, not just which campaigns. Used to inform creative direction, inventory planning, and bid strategy.

**Platforms typically involved:** an ecommerce backend (Shopify, BigCommerce, WooCommerce, Adobe Commerce, Squarespace, Wix, PrestaShop, Centra, Ecwid, Amazon Seller Central, TikTok Shop) + ad platforms with product-level reporting (Google Shopping, Meta Catalog ads, TikTok Shop ads).

### Step 1 — Pull product-level sales
> Pull the last 30-60 days of product-level sales from [Shopify / BigCommerce / WooCommerce]: SKU, product name, units sold, revenue, gross margin if available.

### Step 2 — Pull ad-driven attribution
> Pull product-level performance from [Google Shopping / Meta product catalog / TikTok Shop ads]: SKU, impressions, clicks, spend, attributed purchases, attributed revenue.

### Step 3 — Join and rank
Use `scripts/sku_performance.py`. The script:
- Joins ad-driven attribution with total sales
- Computes the % of each SKU's revenue that came from paid ads
- Surfaces high-margin SKUs underspending on ads (opportunity)
- Surfaces low-margin SKUs overspending on ads (cut candidates)
- Flags SKUs with high return rates if return data is available

### Step 4 — Visualize the SKU portfolio
The question the chart needs to answer: **which products deserve more ad investment, which deserve less?**

A scatter plot works well: x-axis = total revenue, y-axis = ad ROAS for that SKU. Dots colored by margin tier (high/medium/low margin), sized by units sold. The user sees the high-revenue, high-ROAS, high-margin winners immediately.

A secondary view: top 20 SKUs by ad-attributed revenue, with bars colored by margin tier. Surfaces concentration — often 5-10 SKUs drive 80% of ad revenue.

### Step 5 — Build the report
Use `assets/sku_performance_report.md`. The doc should recommend specific products for:
- **Scale up** — high ROAS, high margin, inventory available
- **Hold** — performing as expected
- **Cut from ads** — low ROAS or low margin, ad spend not earning
- **Add to ads** — strong organic sales, not yet promoted, high margin

### Common variations
- **Add inventory levels** — if an inventory feed is available, surface SKUs with low stock to avoid promoting out-of-stock products.
- **By collection or category** — instead of SKU-by-SKU, group into categories for higher-level decisions.
- **Seasonal SKUs** — for seasonal products, surface the year-over-year same-period comparison.

---

## Workflow 4: New vs returning customer ROAS by channel

**When to use:** the user wants to know whether their ad spend is acquiring new customers or just re-converting existing ones. Different channels often have very different splits.

**Platforms typically involved:** ad platforms + ecommerce backend with customer-type segmentation (Shopify, BigCommerce, etc.) + GA4 if available (for the customer-type dimension on conversions).

### Step 1 — Pull channel-level spend
> Pull the last 30-60 days of spend by channel from [ad platforms].

### Step 2 — Pull purchases segmented by customer type
> Pull purchases segmented into "new customer" (first-time buyer) and "returning customer" (repeat) from [Shopify / GA4]. Break out by channel.

If GA4 has the customer-type dimension available on conversions, prefer that source — it stitches across channels. If only the ecommerce backend has it, use that.

### Step 3 — Compute split ROAS
Use `scripts/customer_type_roas.py`. Outputs per channel:
- Total ROAS
- New-customer ROAS (revenue from new buyers / spend)
- Returning-customer ROAS
- % of revenue from new customers
- Cost per new customer (CAC)

### Step 4 — Visualize the split
The question the chart needs to answer: **which channels acquire new customers, and which mostly serve repeat buyers?**

A stacked bar chart per channel works well: each bar shows the channel's total revenue, split into new and returning customer revenue. Surfaces channels that are mostly retargeting vs mostly acquisition.

A secondary view: paired bars per channel showing new-customer-CAC and returning-customer-CAC side by side. Some channels acquire new customers at $X but the channel's apparent ROAS is inflated by returning-customer revenue.

### Step 5 — Build the brief
Use `assets/customer_acquisition_brief.md`. The interesting finding usually centers on which channels are real acquisition vs which are retargeting in disguise.

### Common variations
- **Compare to organic** — many ecommerce businesses get more new customers via organic than paid. Surface organic for context.
- **Subscription / repeat purchase business** — the workflow becomes "first-purchase ROAS" vs "subsequent-purchase ROAS" where channels driving subsequent purchases are particularly valuable.
- **By acquisition cohort** — track new customers acquired this month by their first-purchase channel; see how they behave over the next 90 days.

---

## Workflow 5: AOV and basket composition

**When to use:** the user wants to understand average order value (AOV) and items-per-order patterns, often as a precursor to upsell, cross-sell, or free-shipping-threshold decisions.

**Platforms typically involved:** ecommerce backend (Shopify, BigCommerce, WooCommerce, etc.) + ad platforms for channel-level breakdown.

### Step 1 — Pull order-level data
> Pull the last 30-90 days of order-level data from [ecommerce backend]: order value, item count, products, channel attribution if available.

If channel attribution isn't on the order data, join with ad-platform purchase data by date/customer.

### Step 2 — Compute AOV and basket patterns
Use `scripts/aov_analyzer.py`. Outputs:
- AOV by channel
- AOV trend over the period
- Items per order distribution
- AOV percentiles (P25, P50, P75, P90) to understand the distribution shape
- Free-shipping-threshold proximity (% of orders just under common thresholds like $50, $75, $100)

### Step 3 — Visualize the patterns
The question the chart needs to answer: **what does the basket look like, and where's the upsell opportunity?**

A box plot of AOV by channel surfaces both central tendency and distribution. A complementary histogram of order values with vertical reference lines at common free-shipping thresholds shows the upsell opportunity.

A bar chart of items-per-order distribution (1, 2, 3, 4+ items) by channel shows which channels drive single-item vs basket-building purchases.

### Step 4 — Build the summary
Use `assets/aov_summary.md`. The most-useful section is usually the free-shipping-threshold analysis — if a meaningful % of orders are just under the threshold, raising or lowering it has predictable effects.

### Common variations
- **Pre/post threshold change** — if the user has changed their free-shipping threshold recently, compare AOV distributions pre/post.
- **Promotional vs non-promotional periods** — AOV typically rises during promos (people buy more to hit discount thresholds). Surface the contrast.
- **First-time-buyer AOV vs repeat-buyer AOV** — repeat buyers usually have higher AOV. The size of the gap tells you how much retention is worth.

---

## Workflow 6: Subscription / retention cohort analysis

**When to use:** the user runs a subscription business (Recharge on Shopify, native subscription products) or a repeat-purchase ecommerce business and wants to track retention by acquisition cohort.

**Platforms typically involved:** subscription platform (Recharge), payments (Stripe), or ecommerce backend with subscription/repeat-purchase data + ad platforms for cohort acquisition cost.

### Step 1 — Pull cohort data
> Pull customers grouped by acquisition month for the last 12 months. For each cohort, pull monthly revenue or active subscriber count for each month since acquisition.

### Step 2 — Pull acquisition costs
> Pull marketing spend per month over the same period. If channel-level CAC is available, pull that too.

### Step 3 — Compute retention metrics
Use `scripts/subscription_cohorts.py`. Outputs:
- Cohort retention curve (% of cohort still active by month-since-acquisition)
- Cohort cumulative revenue per customer
- Time-to-payback (months for cumulative revenue per customer to exceed CAC)
- Cohort LTV at 3/6/12/24 month horizons

### Step 4 — Visualize the cohort behavior
The question the chart needs to answer: **how does customer behavior change with cohort age, and are recent cohorts behaving like older ones?**

Two complementary visualizations:
- **Retention curves**: line chart with one line per cohort. X-axis = months since acquisition, Y-axis = % of cohort still active or % of cohort generating revenue. Steeper curves = worse retention; flatter curves = better retention. Overlapping curves means recent cohorts behave like older ones; diverging curves (with newer cohorts lower) is a warning sign.
- **Cumulative cohort revenue per customer**: line chart with one line per cohort showing $ revenue per customer over time. Reach to CAC level marks the payback moment.

### Step 5 — Build the report
Use `assets/retention_cohort_report.md`. The audience is typically the marketing leader and possibly the CFO — retention numbers feed unit economics decisions.

### Common variations
- **By acquisition channel** — different channels often produce cohorts with very different retention. The cheapest CAC channel often has the worst retention.
- **By acquisition campaign or promo** — heavy promo cohorts (50% off first month) typically have worse retention than full-price cohorts. Worth surfacing.
- **By product mix on first purchase** — for ecommerce, the first product purchased often predicts retention. Subscription-product-first vs one-time-product-first cohorts behave very differently.

---

## Workflow 7: Pre-promo planning model

**When to use:** the user is planning a high-stakes promotional period (BFCM, summer sale, etc.) and needs to set budget, AOV, and ROAS targets based on historical performance.

**Platforms typically involved:** ad platforms + ecommerce backend, both showing prior promo periods.

### Step 1 — Pull prior promo data
> Pull spend, purchases, revenue, AOV, and ROAS from the equivalent promo period last year (and the year before if available) across all relevant channels.

Use the actual promo dates, not "last November" — promos have specific date windows that matter.

### Step 2 — Pull baseline data
> Pull the same metrics from the trailing 30 days before the prior promo started. Used to compute the promo lift over baseline.

### Step 3 — Model the upcoming promo
Use `scripts/promo_planner.py`. Inputs:
- Last year's promo numbers (auto-derived from the pulled data)
- Year-over-year growth assumption (user provides)
- Planned budget for the upcoming promo

Outputs:
- Projected purchases, revenue, AOV, ROAS for the upcoming promo
- Per-channel projected spend and outcomes
- Stretch and conservative scenarios

### Step 4 — Visualize the plan
A bar chart comparing prior year actuals vs proposed plan for each metric (spend, purchases, revenue, AOV, ROAS) makes the proposal scannable.

A second chart projects daily spend over the promo period — useful for media buyers planning the pacing.

### Step 5 — Build the plan
Use `assets/promo_plan_doc.md`. The plan must include:
- Targets per metric (with stretch and conservative bands)
- Per-channel allocation
- Daily pacing
- Anomaly thresholds (when to alert the team mid-promo)
- Post-promo measurement plan

### Common variations
- **First-time-running-this-promo** — no prior data. Use industry benchmarks from web search; surface the higher uncertainty explicitly.
- **Different mix this year** — if the channel mix differs from prior year (e.g. adding TikTok), the prior-year model needs adjustment. Surface what's being assumed.
- **Multi-week promo** — model per-week pacing if the promo runs more than 3-4 days. Customer behavior often differs early-promo vs late-promo.

---

## Ad hoc analysis

For one-off questions outside these seven workflows ("what's the AOV distribution across our top SKUs in this campaign?", "is there an LTV difference between Facebook and Google traffic?", "did this discount code drive incremental purchases or cannibalize existing demand?"), write fresh analysis code. The "Choosing the right visualization" framework in the SKILL.md tells you which chart family fits.

---

## A note on promo-period analysis

Normal-period and promo-period analysis behave differently:

- **Conversion rates spike during promos** because intent is high. Day-of-week patterns from non-promo periods don't predict promo behavior.
- **CPMs spike during promos** because everyone is bidding harder. Cost-per-purchase increases during BFCM aren't always efficiency loss — it might be competitive pressure.
- **Pixels and tracking break more during promos** because traffic volume is higher and edge cases get exposed. Before alerting on an anomaly, verify tracking is healthy.

When the user is doing post-promo analysis, frame as "vs. last year's same period" rather than "vs. last month" — same-period comparison removes the seasonal confound.
