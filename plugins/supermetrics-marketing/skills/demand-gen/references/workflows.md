# Demand generation workflows

Seven workflow patterns demand gen managers run regularly: from reconciling ad platforms with web analytics through full-funnel B2B attribution including CRM-connected pipeline contribution.

## Workflow 1: The traffic-to-conversion audit

**When to use:** the user wants to see which channels drive engaged traffic that actually converts on-site, not just cheap clicks. The output usually ends with an update to sales leadership justifying a budget reallocation.

**Platforms typically involved:** Google Ads, LinkedIn Ads, and Google Analytics 4. GA4 is mandatory — without it this workflow can't run.

### Step 1 — Pull ad platform data, then GA4
> Pull the last 30 days of spend and click data from the Google Ads and LinkedIn Ads accounts. Then pull session and goal conversion data for the same period from Google Analytics 4.

Two separate pulls. Do ad platforms first, confirm the data, then GA4 with matching channel grouping. If GA4 isn't connected, stop and tell the user this workflow requires it.

### Step 2 — Reconcile
Use `scripts/funnel_reconciler.py`. The script joins by channel name and computes the divergence between platform-reported and GA4-measured outcomes. Channels where the click-to-session gap exceeds 25% get flagged as likely UTM/tracking issues.

### Step 3 — Visualize the reconciliation
The question the chart needs to answer: **where's the leak — is each channel converting the traffic it bought, or losing it somewhere?**

For a small number of channels (3–5), a paired bar chart per channel works well: one bar for the ad platform metric (e.g. platform-reported CPA), one bar for the GA4 measurement of the same thing (GA4-measured CPA). Big gaps between the pairs are the story. Channels with tracking flags get an amber outline.

When the user wants the funnel view explicitly, a descending bar chart showing impressions → clicks → sessions → conversions makes drop-off rates visible at each stage.

Whichever you build, name the headline above the chart — "Two of four channels have tracking issues" or "Facebook traffic doesn't convert post-click" — don't make the user infer the story.

### Step 4 — Recommendation
> Write a short paragraph recommending how budget should be reallocated next period to prioritize the channel driving the highest-quality website traffic.

The recommendation should name a specific dollar amount, a source channel, a destination channel, and the expected impact on **GA4-measured** conversions (not just ad-platform conversions — that's the whole point).

### Step 5 — Update sales leadership
Build from `assets/sales_leadership_email.md`. Default delivery is markdown inline. If the user wants it as a Word doc, use the `docx` skill. If Gmail is connected, offer to save as a draft.

### Common variations
- **Adobe Analytics instead of GA4** — same workflow shape; Supermetrics has Adobe Analytics support, ask whether it's connected.
- **Use last-click instead of GA4's default attribution** — GA4's default is data-driven; switching changes which channels look good. Ask the user which view they want and note the choice in the deliverable.
- **Join with CRM lead-quality data** — if HubSpot or Salesforce is connected, pull MQL conversion rate by source and join with the reconciliation. The combined view ("$50 ad CPA + 8% MQL rate" vs "$80 ad CPA + 35% MQL rate") changes the recommendation entirely.

---

## Workflow 2: Lead generation efficiency comparison

**When to use:** the user is comparing efficiency of B2B advertising platforms for lead capture, typically LinkedIn vs Facebook. Output is usually a one-page summary for the demand gen team or a leadership recommendation.

**Platforms typically involved:** LinkedIn Ads and Facebook Ads primarily. Sometimes Google Ads for B2B search.

### Step 1 — Pull the data with campaign filter
> Pull the last 60 days of campaign performance from LinkedIn Ads and Facebook Ads, filtered to campaigns containing the phrase [Lead Gen / LG_ / MQL_ / whatever the user's convention is].

The filter phrase is specific to the user's naming convention. Ask if unclear. The data needs to be at the ad / asset level, not just campaign level — different assets in the same campaign often perform very differently.

### Step 2 — Compare CPL and lead conversion rate
Use `scripts/lead_efficiency.py`. Outputs platform-level CPL, lead-to-click ratio, CTR, and a comparison summary.

### Step 3 — Visualize the comparison
The question the chart needs to answer: **which platform is more efficient, and by how much?**

A simple sorted bar chart of CPL by platform works as the primary visualization. If the user wants the multi-dimensional view, a small dashboard-style group (CPL, lead conversion rate, CTR, total leads) with the platforms side-by-side makes the trade-offs visible — sometimes the cheaper platform produces fewer leads, or the lower-CPL platform has worse lead quality. Name the trade-off explicitly when surfacing the visualization.

If the user has tagged the ad creatives, a secondary chart ranking individual ads by efficiency (across both platforms) surfaces the actual winners, which is often more useful than the platform-level average.

### Step 4 — Identify what's working in the winners
> Identify the top two best-performing ad creatives across both platforms based on conversion rate, and explain why their messaging is likely resonating with the target audience.

This is the qualitative step. Look at the winning ad copy and identify the actual angle — pain point, social proof, status, ROI claim. The output is a brief on what's resonating, which the user can take into the next round of creative.

Use `assets/lead_efficiency_summary.md` to structure the final deliverable.

### Step 5 — Output
Default delivery is markdown inline. If the user wants a Word doc, use the `docx` skill.

### Common variations
- **Add Google Ads search to the comparison** — search and social lead gen aren't directly comparable on raw CPL. Frame as "intent-driven (search) vs interruption-driven (social)" rather than head-to-head.
- **Cost per MQL, not cost per lead** — needs CRM data. If a HubSpot or Salesforce connector is active, pull MQL counts by source. Without one, ask the user how they'll get the data.
- **Compare to last quarter** — re-run for the prior 60-day window and overlay both periods on the chart.

---

## Workflow 3: Pipeline contribution by channel

**When to use:** the user is in B2B and wants to credit marketing channels with the pipeline they actually create — not just leads. This is the single most-requested demand gen analysis when a CRM connector is available.

**Platforms typically involved:** ad platforms (LinkedIn Ads, Google Ads, Facebook Ads) + a CRM connector (HubSpot, Salesforce, Pipedrive, Zoho, Close, Odoo).

### Step 1 — Pull spend and pipeline
> Pull the last 90 days of ad spend by channel from [ad platforms]. Then pull opportunities created in the same period from [CRM], including opportunity amount, stage, and source/first-touch channel.

Confirm with the user how their CRM attributes channels to opportunities — most common patterns:
- **First-touch:** the channel that brought the contact in
- **Last-touch:** the channel of the activity immediately before opportunity creation
- **Multi-touch:** weighted across all touchpoints

State the attribution method explicitly in the output.

### Step 2 — Compute cost per opportunity and pipeline ROAS
Use `scripts/pipeline_attribution.py`. Outputs per channel:
- Total spend
- Number of opportunities attributed
- Total pipeline value (sum of opportunity amounts)
- Cost per opportunity (CPO)
- Pipeline ROAS (pipeline value / spend)

### Step 3 — Visualize the credit
The question the chart needs to answer: **which channels create the pipeline, and at what cost?**

A useful primary visualization is a paired bar chart per channel: spend (one bar) and pipeline created (second bar, often on a secondary axis since the scales differ). Channels where the pipeline bar is much taller than spend are the leverage channels.

A secondary view: stacked bar of pipeline value by channel, sorted by total. Surfaces which channels concentrate vs spread their pipeline contribution.

### Step 4 — Frame caveats
This view has limitations that need to be surfaced:
- It's not closed-won revenue, it's pipeline. Some pipeline will close; some won't.
- The attribution method shapes the rankings. First-touch credits top-of-funnel channels; last-touch credits bottom-of-funnel channels.
- Opportunities can sit in pipeline for months. The 90-day window captures opps created, not opps closed.

### Step 5 — Build the report
Use `assets/pipeline_attribution_report.md`. The audience is typically the VP of Sales or CRO; tone should be data-forward with explicit acknowledgment of attribution choices.

### Common variations
- **Closed-won, not pipeline** — re-run for opportunities with `stage = closed-won`. Smaller numbers, longer time lag, but more defensible. Best for quarterly reviews.
- **Win rate by channel** — additional column: of opps from this channel, what % closed? Some channels generate lots of low-quality pipeline; this surfaces it.
- **Deal size by channel** — average opportunity amount per channel. Often the highest-CPO channels generate the largest deals.

---

## Workflow 4: MQL-to-SQL conversion rate by source

**When to use:** the user needs lead quality measurement, not just lead volume. CPL is the cheap version of this question; MQL-to-SQL conversion rate is the real answer.

**Platforms typically involved:** ad platforms + CRM (HubSpot, Salesforce). Marketing automation (Marketo, HubSpot Marketing Email) if lead nurture is part of the journey.

### Step 1 — Pull leads, MQLs, and SQLs by source
> Pull the last 90 days of leads created from [CRM], grouped by lead source. For each lead, include whether they reached MQL status and SQL status, and the dates of each transition.

The 90-day window matters — leads need time to progress through the funnel. Pulling last week's data won't show conversion rates because leads haven't had time to convert.

### Step 2 — Compute conversion rates per source
Use `scripts/mql_quality.py`. Outputs per source:
- Total leads
- MQL conversion rate (% of leads that became MQLs)
- SQL conversion rate (% of MQLs that became SQLs)
- Lead-to-SQL conversion rate (% of leads that became SQLs)
- Time-to-MQL (median days)

### Step 3 — Visualize quality vs volume
The question the chart needs to answer: **which sources produce high-quality leads, and which produce volume without quality?**

A scatter plot works well here: x-axis = lead volume, y-axis = MQL conversion rate. Bubble size = total spend on the source. Sources in the top-right (high volume + high quality) are the keepers; bottom-right (high volume + low quality) are the spend-too-much candidates.

A secondary view: funnel chart per source — leads → MQLs → SQLs. Visualizes where the drop-off happens per source.

### Step 4 — Diagnose
For sources with low MQL conversion, the question is whether the issue is:
- **Lead targeting** (the source brings in wrong-fit leads)
- **Lead nurture** (the leads aren't getting touched, or the nurture doesn't resonate)
- **MQL definition** (the bar is set too high)

The script doesn't diagnose this automatically — surface the question for the user to investigate.

### Step 5 — Output
Use `assets/lead_quality_diagnostic.md`. Audience: marketing operations or demand gen leadership.

### Common variations
- **Add deal-source connection** — for sources where SQLs convert, what's the average deal size? Quality has multiple dimensions.
- **Cohort by month** — recent-cohort conversion rates may differ from older cohorts. Plot trend.
- **Compare paid vs organic sources** — paid sources should have higher CPL but often have lower MQL rates because of intent quality.

---

## Workflow 5: ABM campaign performance

**When to use:** the user runs account-based marketing (ABM) and needs to measure coverage and engagement across a defined target account list.

**Platforms typically involved:** LinkedIn Ads (the primary ABM ad platform) + CRM with target account list + GA4 or web analytics for engaged-session data.

### Step 1 — Get the target account list
Ask the user (via `ask_user_input_v0` if needed): is the target account list maintained in the CRM (as an account property or list membership) or elsewhere? How many accounts are on it?

### Step 2 — Pull engagement signals
For each target account, gather available engagement signals:
- **From LinkedIn Ads:** impressions and clicks to accounts on the target list (LinkedIn supports account-list-based targeting)
- **From the CRM:** activities logged against the target account, meetings booked, opportunities created
- **From GA4 (if available):** sessions from companies on the target list (some teams use Clearbit Reveal or similar for company identification)

### Step 3 — Compute account-level coverage and engagement
Use `scripts/abm_engagement.py`. Outputs per account:
- Coverage (have we reached them at all)
- Engagement score (composite from impressions, clicks, site visits, activities)
- Pipeline status (opportunity / no opportunity)
- Last meaningful touchpoint

Aggregated:
- % of target accounts reached
- % of target accounts engaged
- % of target accounts in active pipeline

### Step 4 — Visualize the funnel
The question the chart needs to answer: **of our target accounts, how many are at each stage of engagement?**

A funnel chart works: target list size → reached → engaged → opportunities → closed-won. Each tier showing the absolute count and the conversion rate.

A secondary view: a list view (top 20 most-engaged target accounts that aren't yet in pipeline), since those are the highest-value follow-up targets for sales.

### Step 5 — Build the report
Use `assets/abm_engagement_report.md`. Audience: B2B marketing leader + sales counterparts running the ABM program together.

### Common variations
- **Tier the target accounts** — Tier 1 (top 50) vs Tier 2 (next 200) may need different KPIs. Higher tiers should show deeper engagement.
- **Compare ABM-touched vs untouched** — for accounts on the target list, do those that received ABM touches close at higher rates than those that didn't?
- **Persona reach within accounts** — coverage isn't just account-level; it's persona-level within accounts. The CMO and the VP of Engineering need different messaging. Pull persona-level engagement from LinkedIn if the data supports it.

---

## Workflow 6: Email + ads integrated funnel

**When to use:** the user runs both paid acquisition and email nurture and wants to see how they interact — does email nurture make paid clicks convert better? Does paid acquisition feed the email list usefully?

**Platforms typically involved:** ad platforms + email marketing platforms (HubSpot Marketing Email, Marketo, Mailchimp, Klaviyo, Brevo, Campaign Monitor, ActiveCampaign, Omnisend) + CRM for the conversion data.

### Step 1 — Pull the email side
> Pull the last 90 days of email campaign performance from [email platform]: campaigns sent, opens, clicks, conversions, and revenue attributed.

Also pull list growth: how many new subscribers were added in the period, and from which sources (paid sign-up, organic site, in-app, etc.).

### Step 2 — Pull the paid side
> Pull the last 90 days of paid acquisition data, focusing on conversions that include both "purchase" / "lead" type and "newsletter signup" / "email subscription" type.

### Step 3 — Join the views
Use `scripts/email_paid_funnel.py`. The script:
- Computes paid-to-email-subscriber rate (of paid clicks, how many turned into email subscribers)
- Computes email-to-conversion rate (of nurtured subscribers, how many converted within the period)
- Identifies the channels that subscribe-then-convert at high rates (efficient acquisition through nurture) vs convert directly (efficient acquisition without nurture)

### Step 4 — Visualize the interaction
The question the chart needs to answer: **does our email nurture amplify paid acquisition, or is it a separate channel?**

A Sankey-style flow diagram is ideal here — paid channels on the left, "Subscribed", "Direct converted", or "Lost" in the middle, "Converted via email", "Converted directly", "Still nurturing" on the right. The flow widths show volume.

If a Sankey is too complex, a stacked bar per paid channel showing the split (% direct converted, % subscribed and later converted, % subscribed and still nurturing, % lost) works as a simpler alternative.

### Step 5 — Build the narrative
Use `assets/integrated_funnel_summary.md`. The interesting finding is usually one of:
- "Email amplifies acquisition — paid channels with the highest subscribe rate also have the highest eventual conversion rate via nurture"
- "Email and paid are separate channels — subscribers convert at similar rates regardless of paid source"
- "Paid acquisition is bypassing email — high direct-conversion rates mean email is mostly serving repeat business"

### Common variations
- **Per-segment email performance** — if the email platform supports segmentation, surface which segments (e.g. newsletter subscribers vs free-trial users) convert at higher rates.
- **First purchase vs repeat** — for ecommerce, separate first-purchase email influence from repeat-purchase email influence. Often very different patterns.
- **Welcome series performance specifically** — the welcome series is the highest-leverage email touchpoint. Pull its open and click rates separately.

---

## Workflow 7: Webinar / gated content funnel analysis

**When to use:** the user runs webinars, ebooks, whitepapers, or other gated content as part of demand gen, and wants to measure the full funnel from paid promotion through registration, attendance/download, and downstream MQL behavior.

**Platforms typically involved:** ad platforms + HubSpot Marketing Forms (or whichever form platform captures registrations) + CRM for downstream tracking + email platform for the registration confirmation and follow-up.

### Step 1 — Pull paid promotion data
> Pull the last 30-60 days of paid ad performance for campaigns promoting the specific content asset (webinar, ebook, etc.). Include spend, clicks, and platform-reported conversions.

### Step 2 — Pull registrations
> Pull form submissions for [content asset] from [form platform / CRM], including UTM source for each registration.

### Step 3 — Pull downstream behavior
For each registration, pull from the CRM:
- Did they attend / download?
- Did they become an MQL within 30 days?
- Did they enter pipeline within 60 days?

### Step 4 — Compute the funnel per channel
Use `scripts/gated_content_funnel.py`. Outputs per paid channel:
- Spend
- Clicks
- Registrations (and registration rate from clicks)
- Attendees/downloaders (and rate from registrations)
- MQLs within 30 days (and rate from registrations)
- Cost per MQL via this content

### Step 5 — Visualize the funnel
The question the chart needs to answer: **which paid channels generate the highest-quality registrations for this content?**

A grouped horizontal bar chart per channel, with bars for each funnel stage (register, attend, MQL within 30 days) sized by conversion rate, surfaces where the drop-off happens per channel. Sometimes a channel has high registration rates but low attendance — the content didn't deliver against expectations. Other times the inverse.

A secondary view: cost-per-MQL bar chart per channel via this content asset, compared to the user's overall cost-per-MQL baseline. Surfaces whether this content is more or less efficient than the user's blended acquisition.

### Step 6 — Output
Use `assets/integrated_funnel_summary.md` (same template — the structure works for both Workflow 6 and 7). For high-stakes content (annual flagship report, major webinar), the doc may justify the `pptx` skill for a recap deck.

### Common variations
- **Multi-asset analysis** — instead of one content asset, compare 5-10 across the same time period. Which content assets are the highest-converting?
- **By topic or persona** — group content by topic or target persona; see which themes resonate at the highest conversion rates.
- **Live vs on-demand webinar** — many webinars have a live event then an on-demand version. The on-demand conversion rate tends to be different (and is often where the volume actually comes from). Surface both.

---

## Ad hoc analysis

For one-off questions outside these seven workflows ("do leads from landing page A have different MQL rates than from B?", "is there a day-of-week effect on lead quality?", "which landing pages are the highest-MQL-converting destinations for paid traffic?"), write fresh analysis code. The "Choosing the right visualization" framework in the SKILL.md tells you which chart family fits which type of question.

---

## A note on the demand gen audience

Demand gen sits between marketing and sales — two audiences with different vocabularies. Marketing leaders want efficiency framed as CPA and ROAS; sales leaders want it framed as cost per MQL, cost per opp, pipeline contribution. When the deliverable is for sales, translate up the funnel. When it's for marketing, platform-level metrics are fine.
