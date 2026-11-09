---
name: linkedin-pages
description: LinkedIn company page analytics through Supermetrics — follower growth and demographics by job function, seniority, industry and country, post impressions, clicks, engagement rate, top posts, page views and video views. Use for "LinkedIn page analytics", "LinkedIn follower growth", "best LinkedIn posts" and organic LinkedIn reporting.
---

# LinkedIn company page analytics

Answer organic LinkedIn questions with live data. If the Supermetrics tools aren't available in this session, follow the `get-started` skill first. Publishing posts and replying to comments is covered by the `social-media-publishing` skill; LinkedIn Ads results belong to `performance-marketer`.

## Data source

- `ds_id`: `LIP` (LinkedIn Company Pages). Accounts are company pages; list them with `accounts_discovery`. A date range is required.
- There is no report type to set, but every field in one query must belong to the same group. Followers, follower demographics, post statistics, page views and video views are separate groups, so build one query per question rather than mixing them.

## Fields that answer most questions

| Need | Field IDs |
|---|---|
| Current followers and demographics | `follower_count`, `follower_count_organic` with `follower_function`, `follower_seniority`, `follower_industry`, `follower_company_size`, `follower_country`, `follower_region` |
| Follower growth over time | `followers_gain_total`, `followers_gain_organic`, `followers_gain_paid` with `date` or `yearMonth` |
| Post statistics | `page_impressions`, `page_clicks`, `page_likes`, `page_comments`, `page_shares`, `page_engagements`, `page_engagement_rate` |
| Individual posts | `update_id`, `update_share_comment` (post text), `update_url`, `update_share_media_category` with the post statistics above |
| Page views | `page_views`, `unique_page_views` by `date`; `total_page_views` with `page_views_by_function`, `page_views_by_seniority`, `page_views_by_industry`, `page_views_by_country` |
| Video | `ugc_text`, `ugc_video_created`, `ugc_video_views`, `ugc_video_time_watched_for_views` (milliseconds) |

Confirm IDs with `field_discovery` (`ds_id: LIP`) before building unusual queries.

## Workflows

1. **Monthly page report.** New followers (organic and paid) by `yearMonth`, post impressions, engagements and `page_engagement_rate` by `yearMonth`, and the current `follower_count`, each as its own query.
2. **Top posts.** Posts with `update_id`, `update_share_comment` and `update_url` ranked by `page_engagements`, with impressions and `page_engagement_rate` alongside so a post with high reach isn't mistaken for a highly engaging one.
3. **Are we reaching the right people.** `follower_count` by `follower_function` and `follower_seniority`, then by `follower_industry`. Compare with the target buyer profile and with page views by the same attributes.
4. **Content format.** Group the post list by `update_share_media_category` and compare average impressions and engagement rate per post.

## Pitfalls

- `follower_count` and `follower_count_organic` are current totals and cannot be split by a date dimension. For a trend, use the `followers_gain_*` fields.
- `page_engagement_rate` and `total_share_engagement_rate` are calculated by LinkedIn. Never sum or average them across rows; request the grouping you need instead.
- Demographic splits cover followers as they are now, not as they were during the selected date range.

Finish with the answer first, then the evidence. For a recurring LinkedIn report, offer a live dashboard (see `studio-dashboards`).
