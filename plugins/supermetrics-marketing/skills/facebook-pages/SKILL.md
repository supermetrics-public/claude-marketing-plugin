---
name: facebook-pages
description: Organic Facebook Page analytics through Supermetrics — page followers, views, visits, post engagement, reactions, top posts, video and reels performance. Use for "Facebook Insights", "Facebook page performance", "which posts did best on Facebook" and organic social reporting. Paid Meta Ads results belong to the performance-marketer skill.
---

# Facebook Page analytics

Answer organic Facebook Page questions with live data. If the Supermetrics tools aren't available in this session, follow the `get-started` skill first.

## Data source

- `ds_id`: `FB` (Facebook Insights). Accounts are Pages; list them with `accounts_discovery`. A date range is required; there is no report type to set.
- This source covers organic Page activity only. Ad spend, ad reach and conversions come from Meta Ads (`ds_id: FA`), covered by the `performance-marketer` skill.
- Optional settings: `include_all_published_posts` (checkbox) and `localization` for multi-language posts.

## Fields that answer most questions

| Need | Field IDs |
|---|---|
| Audience size | `page_followers` |
| Page visibility | `page_media_view`, `page_media_view_organic`, `page_media_view_paid`, `page_total_media_view_unique`, `page_views_total` (profile visits) |
| Page engagement | `page_post_engagements`, `page_post_reactions_total` |
| Post performance | `post_ID`, `post_message`, `post_type`, `post_linkto`, `post_media_views`, `post_total_media_views_unique`, `post_reactions_total`, `post_comments_on_post`, `post_shares_on_post`, `post_link_clicks` |
| Video and reels | `page_video_views`, `page_video_complete_views_30s`, `avg_post_video_view_time`, `reel_video_total_plays`, `reel_video_avg_time_watched` |
| Time | `Date`, `WeekISO`, `Yearmonth` |

Meta now reports views (`page_media_view`, `post_media_views`) in place of the older impressions and reach metrics; `page_total_media_view_unique` is the count of unique viewers. Confirm IDs with `field_discovery` (`ds_id: FB`) before building unusual queries.

## Workflows

1. **Monthly page report.** `page_followers`, `page_media_view`, `page_total_media_view_unique` and `page_post_engagements` by `Yearmonth` for the last three full months. Split views into organic and paid to show how much reach was bought.
2. **Top posts.** Posts from the period ranked by `post_reactions_total`, `post_comments_on_post` and `post_shares_on_post`, with `post_type` and `post_media_views`. Calculate engagements per view to compare posts of different reach.
3. **Content format review.** Group the post list by `post_type` and compare average engagement per post. Add reels plays and average watch time when video is a large share of output.
4. **Organic plus paid view.** For "is our organic reach falling while we spend more", put `page_media_view_organic` by `Date` next to Meta Ads spend for the same Page (`ds_id: FA`).

## Pitfalls

- `post_reactions_total`, `post_comments_on_post` and `post_likes_on_post` require a post-level dimension such as `post_ID` in the same query.
- `page_total_media_view_unique` is available only at daily, weekly or monthly granularity; split by month, the date range must cover full calendar months. Never sum unique counts across rows.
- Averages and rates such as `avg_post_video_view_time` are calculated by Meta. Request the grouping you need rather than averaging rows.

Finish with the answer first, then the evidence. For a recurring Facebook report, offer a live dashboard (see `studio-dashboards`).
