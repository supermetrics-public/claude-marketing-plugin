---
name: content-marketer
description: Battle-tested workflows for content marketing managers diagnosing landing page performance and analyzing paid promotion of content assets via the Supermetrics connector. Use whenever the user is analyzing content engagement, page-level conversion, content asset ROI, or paid content promotion efficiency. Trigger on phrases like "which landing pages are leaking traffic," "high bounce rate on my top pages," "content audit," "which ebook is converting," "should I put more budget behind this whitepaper," "rank our gated content by engagement," "the web team needs a list of pages to fix," "content ROI by asset." This skill helps content marketers prove the ROI of expensive content and document the fixes their web/UX team needs to make.
---

# Supermetrics workflows for the content marketing manager

This skill helps content marketing managers prove the ROI of expensive content (writer time, designer time, sometimes agency spend) and document the specific fixes their web/UX team needs to make. The two recurring problems: pages with high traffic but no conversion, and the question of which content assets deserve paid promotion.

## Required: the Supermetrics connector

These workflows rely on the **Supermetrics connector for Claude**, primarily for Google Analytics 4 (landing page diagnosis) and ad platforms like LinkedIn Ads and Facebook Ads (paid promotion analysis).

Before running anything, check that the connector is active — look for Supermetrics tools (`data_query`, `accounts_discovery`, etc.). If they aren't present, prompt the user:

> This workflow needs the Supermetrics connector for Claude. Install it at https://claude.ai/directory/connectors/cc599e7b-8c59-4e89-9bf0-36d47bb9ec80
>
> For landing page diagnosis, connect Google Analytics 4. For paid promotion analysis, connect at least one ad platform (LinkedIn Ads, Facebook Ads).

## Core principles

Three principles apply throughout every workflow:

1. **Two-step pattern: pull, then diagnose.** Pull the asset-level data first. Confirm what you got. Then run diagnosis. The diagnosis depends on knowing what's actually in the data.

2. **Be explicit about what counts as a conversion.** "Conversion rate" on a content landing page can mean form fill, content download, demo request, newsletter signup, or page-to-page click-through. Ask the user which one matters for the page being analyzed.

3. **Show, don't tell.** Content audits are dense with page-level data; visualizations make underperformers immediately legible. See "Choosing the right visualization" below.

## Choosing the right visualization

This skill doesn't prescribe specific charts. Decide based on what the data and the question actually are.

### Step 1 — What is the user trying to see?

| Question type | Visualization family |
|---|---|
| Ranking pages by lost-opportunity (traffic × conversion gap) | Sorted horizontal bar chart |
| Pages plotted by two metrics (e.g. traffic vs conversion rate) | Scatter / quadrant chart |
| Trend in page performance over time | Line chart, optionally multi-series for the top pages |
| Content asset comparison (engagement + conversion across assets) | Grouped bar chart or small multiples |
| Distribution of bounce rate or time-on-page across pages | Histogram or box plot |
| Funnel from impression to conversion for a single asset | Funnel chart or descending stacked bars |

The landing-page diagnosis workflow is the prime case for a **quadrant chart**: sessions on the x-axis, conversion rate on the y-axis. Pages in the bottom-right (high traffic, low conversion) are the priority fixes. Pages in the top-right are the winners worth studying. Pages in the bottom-left aren't worth the team's time.

### Step 2 — What's the headline?

Before building, name the single thing the chart should make obvious. "Three top-10 traffic pages convert below 0.5% — fixing them is the highest-leverage move" is a headline. "Page performance data" is not.

Make the headline land within two seconds:
- **Sort by lost-opportunity** (traffic × conversion gap), not by traffic alone or conversion rate alone
- **Highlight the priority pages** in a contrasting color
- **Add reference lines** for the conversion-rate target and the minimum-traffic threshold
- **Annotate the worst offender** with its URL directly on the chart

### Step 3 — Build as inline artifact

For data visualizations in chat, build a React component using Recharts.

### Standard color palette

- **Good / improving / positive direction:** `#10b981` (green)
- **Bad / declining / negative direction:** `#ef4444` (red)
- **Neutral / baseline / no-direction comparison:** `#6366f1` (indigo)
- **Flagged / warning / attention:** `#f59e0b` (amber)
- **Gridlines:** `#f3f4f6`
- **Text:** `#374151`

Color by *business meaning*. Bounce rate at 80% is red (bad), conversion rate at 4% is green (good).

### Skip the chart when

- The output is the web team fix doc (chart goes inside the doc, not in chat — though a thumbnail summary chart is fine)
- The user just wants a sorted list of pages to fix (markdown table is fine)
- The data has fewer than 4 items worth comparing

### Ad hoc analysis

For one-off questions ("which referral sources have the lowest bounce rate on our blog?", "what's the correlation between time-on-page and conversion rate?", "which days of the week drive the highest-engagement traffic to our top pages?"), write fresh analysis code.

## Other Claude capabilities to leverage

**Built-in document skills.** When the deliverable is a file:
- Word documents (the web team fix doc is the prime case) → use the `docx` skill at `/mnt/skills/public/docx/SKILL.md`
- Spreadsheets (page-by-page audit lists the web team can check off) → use the `xlsx` skill at `/mnt/skills/public/xlsx/SKILL.md`
- Slide decks (content marketing reviews) → use the `pptx` skill at `/mnt/skills/public/pptx/SKILL.md`

Read the relevant SKILL.md before building.

**Other connectors when they're available.** If the user has Google Drive connected, the fix doc can land directly in Drive. If Slack is connected, a short version of the priority list can be posted to the relevant channel. If a CRM connector (HubSpot) is active, pages can be cross-referenced with downstream MQL data to identify which low-CVR pages are actually low-quality-lead generators.

**Web search.** Useful for current bounce-rate and conversion-rate benchmarks by content type, recent SEO/UX research, or industry-specific norms.

**Clarifying questions.** Use `ask_user_input_v0` for multiple-choice clarifications — which conversion event matters, which page types to include or exclude, what bounce-rate threshold to flag.

## When to use the bundled workflows

The `references/workflows.md` file contains the prompt sequences for seven core scenarios:

- **Landing page performance diagnosis** — identifying high-traffic, low-conversion pages and producing a documented fix list. Triggered by "which landing pages need fixing," "high bounce rate," "content audit," "underperforming pages."
- **Paid promotion content analysis** — determining which content assets perform best when ad dollars are put behind them. Triggered by "which content should I promote," "best-performing gated content."
- **Organic content and SEO performance audit** — when SEO connectors are available, audit which posts grow vs decay, what topics to expand or sunset. Triggered by "SEO audit," "organic content performance," "which posts are decaying."
- **Content-to-conversion attribution** — which content pieces influence conversions beyond direct attribution. Triggered by "content attribution," "which blog posts drive leads," "content ROI."
- **Newsletter and email content performance** — when email platform is connected, which content drives subscriber engagement. Triggered by "newsletter performance," "which emails drive clicks," "subject line tests."
- **Video content performance** — cross-platform performance of video assets. Triggered by "YouTube performance," "video content ROI," "which videos retain viewers."
- **Content gap analysis** — what competitors rank for, what queries the user's content misses. Triggered by "content gaps," "keyword gaps," "what should I write about next."

Read `references/workflows.md` when the user's request matches.

## Bundled scripts

- `scripts/landing_page_diagnoser.py` — filters GA4 page-level data to find pages exceeding configurable bounce-rate and traffic thresholds while underperforming on conversion rate.
- `scripts/content_promotion_ranker.py` — ranks promoted content assets by composite engagement score (CPC, CTR, lead rate).
- `scripts/seo_audit.py` — analyzes Search Console + GA4 data to surface growing vs decaying organic pages, identifies topics worth expanding.
- `scripts/content_attribution.py` — joins content engagement (sessions, time-on-page) with conversion data to surface content-to-conversion influence.
- `scripts/newsletter_performance.py` — analyzes email campaign performance by content type, subject line patterns, and segment.
- `scripts/video_content_ranker.py` — ranks video assets across platforms by composite engagement (views, watch time, conversion).
- `scripts/content_gap_analyzer.py` — compares user's ranking keywords with competitor or industry benchmarks to find content gaps.

## Bundled templates

- `assets/web_team_doc.md` — structured doc the content marketer sends to the web/dev team listing underperforming pages and proposed UX fixes.
- `assets/content_promotion_brief.md` — recommendation brief for which content assets should receive paid promotion budget.
- `assets/seo_audit_report.md` — SEO audit findings with prioritized recommendations.
- `assets/content_attribution_summary.md` — content attribution doc surfacing which content drives the most pipeline.
- `assets/newsletter_review.md` — newsletter performance review with content-type breakdown.
- `assets/video_content_report.md` — video performance report ranked by composite engagement.
- `assets/content_gap_brief.md` — content gap analysis with prioritized topic recommendations.

## Things to watch for

**"High bounce rate" isn't always bad.** A blog post with 75% bounce rate where readers spent 4 minutes on the page is performing exactly as intended — they read it, got what they came for, left. Bounce paired with low time-on-page is the actual signal. Surface both metrics together.

**Sample size matters for content.** A page with 50 visits in 30 days and a 0% conversion rate doesn't tell you much. The landing page diagnoser has a minimum-traffic filter (default 500 sessions); don't lower it without reason.

**Content has long tails.** A blog post converting at 0.3% with 100k monthly visitors generates more leads than a page converting at 5% with 800 visitors. Rank by absolute lost-opportunity (sessions × conversion gap), not by conversion rate alone.

**Paid promotion of content has different success criteria than direct response.** A whitepaper ad with 12% CTR but 0.5% lead form completion is *probably* engaging the right audience — the lead form is where the friction lives, not the ad. Don't dismiss high-engagement / low-conversion content ads without checking the post-click experience.

**Attribution for gated content is messy.** A user might download a whitepaper today and book a demo six weeks later via a different channel. Most attribution models won't credit the content. Ask the user what conversion event they're measuring against — content's value is often in leading indicators (downloads, time-on-page, subscriber growth) rather than direct attribution.
