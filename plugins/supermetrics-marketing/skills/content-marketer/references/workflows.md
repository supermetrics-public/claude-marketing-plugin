# Content marketing workflows

Seven workflow patterns for content marketing analysis: from diagnosing landing pages and choosing promotion budget through SEO audits, content attribution, email/video content reviews, and competitive content gap analysis.

## Workflow 1: Landing page performance diagnosis

**When to use:** the user wants to find which content pages get traffic but fail to convert it, and document the fixes for the web/dev team.

**Platforms typically involved:** Google Analytics 4 (mandatory).

### Step 1 — Pull page-level data
> Pull the top 20 landing pages by traffic volume from Google Analytics 4 over the last 30 days, including bounce rate, average engagement time, and key events (or session key event rate).

Default to top 20 — that's the right unit for "where is the leak?" because it weights toward pages where fixes will have visible impact. Expand if the user wants a deeper audit.

### Step 2 — Identify underperformers
Use `scripts/landing_page_diagnoser.py` (columns: `page_path`, `sessions`, `bounce_rate` and `conversion_rate` as percentages, `avg_time_on_page` in seconds; it accepts `conversions` instead of a rate). Default thresholds are 70% bounce rate and 1% conversion rate, with a 500-session minimum. Ask the user about their baselines — these vary by industry (a B2B SaaS landing page should convert higher than a blog post).

### Step 3 — Visualize the diagnosis
The question the chart needs to answer: **which pages should the web team fix first, and why?**

The most useful visualization for this is usually a quadrant chart: sessions on the x-axis, conversion rate on the y-axis. The bottom-right quadrant (high traffic, low conversion) is the priority. The top-right is winners worth studying. Pages get sized or colored by lost-opportunity score (sessions × conversion gap) so the user sees impact at a glance.

When the user wants a ranked list rather than a quadrant view, a sorted horizontal bar chart of lost-opportunity score works well — bars sorted descending, top 5 highlighted as priority.

Reference lines on either chart for the conversion target and bounce-rate threshold make the cut-offs visible without explanation.

### Step 4 — Diagnose likely causes
For each priority page, list 2–3 specific reasons it might be underperforming based on standard UX principles:
- Slow page load, especially on mobile
- Confusing or missing primary CTA
- Headline doesn't match search intent or ad copy driving the traffic
- Form too long or asking for too much info
- Above-the-fold content doesn't deliver on the page title's promise
- Mobile experience broken (form fields too small, buttons cut off)
- No social proof or trust indicators near the CTA
- Above-the-fold ads or popups that interrupt
- Search intent vs page intent mismatch

Pick fixes appropriate to the page type — a blog post needs different fixes than a product landing page.

### Step 5 — Build the web team doc
Use `assets/web_team_doc.md` for structure. The doc needs to be a checklist the web team can act on: page URL, current state, proposed fix, estimated effort, expected impact.

Default delivery: build it as a Word doc with the `docx` skill — the web team will print or share it. If the user prefers Drive, save it there if Google Drive is connected. If they want a spreadsheet to track checkboxes, use the `xlsx` skill instead.

### Common variations
- **CMS or HubSpot tracks conversions, not GA4** — same workflow shape; pull form views and submissions from HubSpot Marketing Forms (`HSMF`) or page data from HubSpot Content Analytics (`HSCA`) if connected, then join to the GA4 page list by URL.
- **Just blog posts, not landing pages** — filter URLs containing `/blog/` (or the user's blog path) in step 1.
- **Mobile only** — re-pull GA4 data with device category as a filter.

---

## Workflow 2: Paid promotion content analysis

**When to use:** the user is deciding which content assets deserve the majority of next quarter's paid promotion budget. Usually triggered by quarterly planning or after a batch of new content has accumulated data.

**Platforms typically involved:** LinkedIn Ads and Facebook Ads primarily. Google Ads sometimes if promoting content in search.

### Step 1 — Pull the data
> Pull the last 60 days of LinkedIn Ads and Facebook Ads campaigns promoting downloadable content, filtered to campaigns containing [the user's naming convention — Content_, Whitepaper_, Ebook_, etc.].

Ask the user about the naming convention if it's unclear. Data should be at the ad / asset level, not just campaign level.

### Step 2 — Rank the assets
Use `scripts/content_promotion_ranker.py` (columns: `asset_name`, `platform`, `spend`, `clicks`, `impressions`, optional `leads`; `--min-spend` defaults to 100). The script ranks by composite engagement (CPC + CTR + lead rate where available) and outputs a sorted list.

A note on metrics: CPC and CTR are engagement metrics, not conversion metrics. They tell you the audience is interested. Whether the asset converts that interest into a lead is a separate question. For ranking which assets to put paid behind, engagement is the right framing.

### Step 3 — Visualize the ranking
The question the chart needs to answer: **which assets are worth more paid budget, and why?**

A sorted horizontal bar chart of the composite promotion score works well as the primary visualization, with bars colored by asset type (whitepaper, ebook, guide, report) so format trends are visible.

If the user wants the multi-dimensional view, a grouped bar chart with one cluster per asset showing CPC, CTR, and lead rate side-by-side surfaces the trade-offs — an asset might win on CTR but lose on lead rate.

### Step 4 — Qualitative read on the winners
> Identify the top two best-performing assets and explain why their messaging is likely resonating with the target audience.

This is the most useful part of the output for next-quarter content planning. Look at the winning assets and identify the actual angle — pain point, social proof, transformation, status, ROI. Use `assets/content_promotion_brief.md` to structure the deliverable. When the user picks which assets to fund, the `campaign-management` skill can apply the budget changes with their approval.

### Step 5 — Output
Default: markdown inline. If the user wants a doc to share with leadership for next-quarter planning, use the `docx` skill.

### Common variations
- **Organic vs paid** — different workflow; organic and paid content perform on different signals. Suggest running paid first, then a separate organic audit.
- **Include cost per lead, not just engagement** — if the user has lead-volume data per asset, the ranker accepts it. But sample sizes get small fast at the asset level for leads; CPC/CTR usually has more reliable signal.

---

## Workflow 3: Organic content and SEO performance audit

**When to use:** the user wants to understand which content is winning vs decaying in organic search. Identifies posts to expand, posts to update, and posts to sunset.

**Platforms typically involved:** Google Search Console (`GW`, mandatory) + Google Analytics 4 (`GAWA`, for engagement on top of impressions/clicks). Optional: Ahrefs (`AHRF2`) or Semrush (`SR`) for keyword positions and backlink data, Bing Webmaster Tools (`BW`) for Bing coverage.

### Step 1 — Pull search performance over time
> Pull the last 6-12 months of Search Console performance by page (and query if needed): impressions, clicks, average position, CTR, split by month. Search Console keeps 16 months of data.

For posts published in the last 6 months, the trend captures the launch curve (newer posts haven't matured yet). For older posts, the trend captures growth vs decay.

### Step 2 — Pull on-page engagement
> Pull GA4 data for the same pages (landing page): sessions, engaged sessions, average engagement time, key events.

If GA4 has key events on the relevant actions (form fills, newsletter signups, demo bookings), pull those per page. Search Console reports full URLs while GA4's `landingPage` is a path; normalize before joining.

### Step 3 — Classify each page
Use `scripts/seo_audit.py` (columns: `page`, `month` as YYYY-MM, `impressions`, `clicks`, `average_position`, optional `sessions`, `engaged_sessions`, `conversions`). The script classifies each page into:
- **Growing**: impressions and clicks trending up
- **Stable**: predictable monthly volume
- **Decaying**: impressions or clicks trending down significantly (often signals stale content)
- **Stuck on page 2-3**: average position 11-30 (fixable with on-page work)
- **Underperforming**: engagement rate under 30% despite traffic (content-quality issue; needs the GA4 columns)

### Step 4 — Visualize the portfolio
The question the chart needs to answer: **which pages are growing, which are at risk, and where should I focus content effort?**

A scatter plot works well: x-axis = monthly impressions trend (% change), y-axis = monthly clicks trend. Dots sized by current monthly clicks, colored by classification. The user sees at a glance which pages are climbing and which are slipping.

A secondary view: top 20 decaying pages ranked by absolute click loss vs peak month. These are the urgent updates.

### Step 5 — Build the audit report
Use `assets/seo_audit_report.md` (offer a live Studio dashboard via the `studio-dashboards` skill if the user wants to track this monthly). The recommendations should split into:
- **Update now** (decaying pages with high historical traffic)
- **Refresh** (stable pages that could grow with a content refresh)
- **Sunset** (low-traffic, low-quality pages dragging average performance)
- **Expand** (growing pages where related content could capture additional queries)

### Common variations
- **Add backlink context** — if Ahrefs is connected, pages with strong backlinks deserve preservation effort; pages with no backlinks may be sunset candidates.
- **Compare to competitors** — if Semrush or Ahrefs is connected, surface which competitor pages outrank the user's on key queries; gives a roadmap for what the user's pages need to address.
- **Branded vs non-branded** — separate branded query performance from non-branded. Branded performance is a vanity metric for content; non-branded is the real test.

---

## Workflow 4: Content-to-conversion attribution

**When to use:** the user wants to credit specific content pieces with influencing conversions — not just direct-conversion attribution, but the broader "what content moved this person closer to converting" question.

**Platforms typically involved:** Google Analytics 4 (content engagement) + CRM (HubSpot, Salesforce) for the conversion side when available.

### Step 1 — Pull content engagement
> Pull GA4 data for content URLs: sessions, engaged sessions, average engagement time, scrolled users (90% scroll, if enhanced measurement is on), and key events.

For pages that aren't conversion targets (blog posts, resource pages, podcast pages), engagement signals matter more than conversions.

### Step 2 — Pull touch data
GA4 path explorations and conversion paths are UI-only; the GA4 API doesn't return page-level paths. Use what the API does give:
- **First touch:** GA4 `landingPage` with key events, or HubSpot contact `first_page_seen` / `first_conversion` (`HSCON`).
- **Last touch:** HubSpot contact `recent_conversion` (the last form and page before converting).
- **Middle touch:** only from the CRM's page-view history or an export the user provides. If unavailable, say so and score on first and last touch only.

### Step 3 — Compute the content attribution table
Use `scripts/content_attribution.py` (columns: `content_url`, `sessions`, `engaged_sessions`, optional `avg_engagement_time_seconds`, `first_touch_conversions`, `middle_touch_conversions`, `last_touch_conversions`). Outputs per content piece:
- Total sessions
- Engaged sessions (sessions meeting the engagement threshold)
- Conversions where this content was the first touch
- Conversions where this content was a touch in the path
- Influence score (composite of presence in conversion paths)

### Step 4 — Visualize content influence
The question the chart needs to answer: **which content pieces show up most often in conversion paths, even when they're not the last touch?**

A bar chart of "conversions influenced" (presence in conversion path) per content piece, with bars shaded by share of those that were first-touch vs middle-touch vs last-touch. Often surprising — long blog posts appear in many paths as middle-touch even when they're never the last touch.

### Step 5 — Build the attribution summary
Use `assets/content_attribution_summary.md`. The audience is typically the content team + their marketing leadership counterpart.

### Common variations
- **Time-to-conversion by content type** — does engaging with this content type accelerate the conversion timeline? Pull average days from first content engagement to conversion per content type.
- **Per-persona content paths** — if persona data is available, the same content may have very different attribution patterns per persona.
- **Repurposing signals** — if a top-converting content piece is in a single format (e.g. long blog post), surface "convert this to a webinar / podcast / video" as a recommendation.

---

## Workflow 5: Newsletter and email content performance

**When to use:** the user runs a content-driven newsletter or email program and wants to understand which content types, topics, and formats drive the most engagement and downstream conversion.

**Platforms typically involved:** an email marketing platform (Mailchimp, Klaviyo, Brevo, HubSpot Marketing Email, Campaign Monitor, Omnisend, ActiveCampaign). CRM for downstream conversion if available. Treat open rates with care: Apple Mail Privacy Protection inflates opens, so lean on clicks and click-to-open.

### Step 1 — Pull campaign performance
> Pull the last 30-60 email campaigns from [email platform]: subject line, send date, list segment, opens, open rate, clicks, click-through rate, unsubscribes.

If the user can tag campaigns by content type (newsletter, promotional, educational, product update), pull the tag too. Otherwise, ask whether they can provide one.

### Step 2 — Pull list growth and segment data
> Pull the same period's list-growth data: new subscribers per day/week, segments they joined, source if available.

Net list growth (new subscribers − unsubscribes) is often more informative than open rates for content programs.

### Step 3 — Analyze patterns
Use `scripts/newsletter_performance.py` (columns: `campaign_name`, `send_date`, `subject_line`, `recipients`, `opens`, `clicks`, `unsubscribes`, optional `segment`, `content_type`, `conversions`, `revenue`). The script:
- Computes engagement metrics per campaign type
- Tags subject line features (length class, question, number, emoji) so you can compare open rates by pattern
- Carries the segment through so you can compare segments
- Flags campaigns with anomalously high unsubscribe rates (signal of poor content fit)

### Step 4 — Visualize the patterns
The question the chart needs to answer: **what kinds of newsletters does my audience actually engage with?**

A bar chart of open rate by content type works as a starting point. A second view: a scatter plot with subject line length on the x-axis and open rate on the y-axis, sized by send volume, colored by content type. Surfaces whether length correlates with open in this audience.

For unsubscribe analysis: a horizontal bar chart of campaigns ranked by unsubscribe rate — campaigns at the top are losing list members fastest and deserve attention.

### Step 5 — Build the review doc
Use `assets/newsletter_review.md`. The audience is the user themselves or their content team. For a monthly review, offer a live Studio dashboard (`studio-dashboards` skill).

### Common variations
- **Subject line A/B testing analysis** — if the user runs A/B tests, surface which variants won and what patterns emerge.
- **Send-time analysis** — different audiences open at different times; surface the best send time by segment.
- **Content-to-conversion** — combine with CRM data: of subscribers who engaged with the newsletter regularly, what % became customers vs the non-engaged segment?

---

## Workflow 6: Video content performance

**When to use:** the user produces video content and wants to understand cross-platform performance — what's working on YouTube vs TikTok vs Instagram Reels vs LinkedIn — and where to invest more production effort.

**Platforms typically involved:** YouTube (`YT2`) + organic social platforms (TikTok Organic `TIKBA`, Instagram Insights `IGI` via the `instagram_insights` tool, LinkedIn Pages, Pinterest Organic, X Organic, Threads Insights). For paid video: ad platforms.

### Step 1 — Pull cross-platform video data
> Pull video performance from [connected platforms] for the last 60-90 days: views, watch time, completion rate, engagement (likes/comments/shares), and follower/subscriber growth.

Each platform reports metrics differently — YouTube has average view duration and average view percentage, TikTok has average view time and completion rate, Instagram reports views and reach. Normalize as best as possible; document where direct comparison isn't possible.

### Step 2 — Pull downstream data if available
For videos with click-through (CTAs to landing pages), pull session data from GA4. For videos that drive subscribers, pull email-list-growth data if relevant.

### Step 3 — Rank by composite engagement
Use `scripts/video_content_ranker.py` (columns: `title`, `platform`, `publish_date`, `views`, `completion_rate`, `engagement_rate`, optional `clicks`, `conversions`). Composite engagement combines:
- Views (volume signal)
- Completion or retention rate (quality signal — % of viewers who finish)
- Engagement rate (likes + comments + shares / views)
- Clicks and conversions are carried through in the output but not scored

The script scores each video by percentile within its own platform (so a TikTok with 50k views isn't compared directly to a LinkedIn video with 500) and ranks videos within each platform. Compare across platforms by these within-platform scores.

### Step 4 — Visualize the portfolio
The question the chart needs to answer: **which content themes and formats are working, and where?**

A grouped bar chart with the user's top 10 videos per platform works well for platform-by-platform review. For cross-platform: a scatter plot with views on the x-axis and completion rate on the y-axis, dots colored by platform and sized by engagement.

### Step 5 — Build the performance report
Use `assets/video_content_report.md`. The output should surface:
- Which themes win across platforms (universal-appeal content)
- Which themes are platform-specific
- Which format-platform combinations are highest-leverage
- Production recommendations (length, structure, hook patterns) based on the winners

### Common variations
- **Hook analysis** — for short-form video specifically, the first 3 seconds determine retention. Pull only the top performers and surface what their hooks have in common.
- **Posting cadence vs performance** — does posting daily produce better aggregate results than posting weekly? Cross-reference posting frequency with average performance.
- **YouTube long-form vs Shorts** — separate analysis. Different audiences, different success criteria.

---

## Workflow 7: Content gap analysis

**When to use:** the user is planning the next quarter or year of content and wants to identify topic gaps — queries the audience is searching for that the user's content doesn't address, or where competitors outrank.

**Platforms typically involved:** Google Search Console (`GW`, user's own queries) + Ahrefs (`AHRF2`) or Semrush (`SR`) for competitor keywords. Google Trends (`GT`) and Google Ads Keyword Planner (`GAKEY`) for query volume and trend.

### Step 1 — Pull the user's ranking keywords
> Pull all keywords the user's site ranks for from [Search Console / Ahrefs / Semrush]: keyword, current position, monthly search volume, current URL.

### Step 2 — Pull competitor or industry benchmark keywords
Ask the user: which 3-5 competitors should be in scope?

> Pull ranking keywords for [competitor 1, competitor 2, ...] from [Ahrefs / Semrush]. For each competitor: keyword, position, URL.

### Step 3 — Compute the gap
Use `scripts/content_gap_analyzer.py` (columns: `keyword`, `monthly_volume`, `user_position`, `competitor_position` or one `competitor_<name>_position` column per competitor, optional `search_intent`). The script keeps keywords where:
- a competitor ranks in the top 10 (`--competitor-top`)
- the user ranks below position 30 (`--user-threshold`) or not at all
- monthly volume is at least 100 (`--min-volume`)

Outputs ranked keyword gaps with: keyword, monthly volume, best competitor position, user status (position or "not ranking"), and a suggested content type from the `search_intent` column. Remove competitor brand terms yourself; the script doesn't filter them, and it doesn't use Google Trends data.

### Step 4 — Visualize the opportunity
The question the chart needs to answer: **what's the volume of search demand we're not capturing, and how concentrated is the opportunity?**

A horizontal bar chart of the top 30 gap keywords by monthly search volume works as the primary view. Color-code by suggested content type (informational, commercial, etc.) so the user can plan content programs by theme.

A secondary view: cumulative-volume curve — the top 10 gap keywords represent how much of the total gap volume? Often 70-80%, meaning a small number of content pieces can capture most of the opportunity.

### Step 5 — Build the content brief
Use `assets/content_gap_brief.md`. The output should be production-ready: each prioritized keyword should have a suggested content format (blog post, landing page, video) and a 2-sentence content angle.

### Common variations
- **Topic clustering** — instead of keyword-by-keyword, cluster the gaps into topic clusters and recommend pillar pages.
- **Quick wins** — surface keywords where the user already ranks page 2-3 but a content update could push to page 1. These are faster than net-new content.
- **Featured snippets and PAA** — if the data is available, surface queries where competitors win featured snippets or People Also Ask boxes. These are higher-leverage than position-only competitions.

---

## Ad hoc analysis

For one-off content questions outside these seven workflows ("which referral source has the highest engagement on our top blog post?", "is there a relationship between word count and bounce rate?", "which CTA variant on our pricing page is converting best?"), write fresh analysis code. The "Choosing the right visualization" framework in the SKILL.md tells you which chart family fits.

---

## A note on content metrics ladders

When the deliverable is going to a non-content audience (executives, finance), frame metrics as a ladder rather than absolute numbers: engagement (CTR, time-on-page) → consumption (downloads, video completion) → conversion (form fills, demo requests) → revenue (pipeline created, deals influenced). Different content lives at different rungs and should be measured accordingly. A blog post measured on direct revenue attribution will always look like a failure; measured on engagement and consumption, it can be the highest-leverage piece in the portfolio.
