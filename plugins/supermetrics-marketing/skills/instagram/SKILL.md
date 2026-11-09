---
name: instagram
description: Instagram analytics through Supermetrics — follower growth, reach, engagement, top posts and reels, stories, best time to post and follower demographics, plus competitor benchmarking on public profiles and hashtags. Use for "Instagram insights", "reels performance", "follower growth" and competitor comparisons.
---

# Instagram analytics

Answer Instagram questions with live data. If the Supermetrics tools aren't available in this session, follow the `get-started` skill first. Publishing or scheduling posts and replying to comments is covered by the `social-media-publishing` skill.

## Data sources

- `ds_id`: `IGI` (Instagram Insights) for accounts the user manages. Accounts are profiles; list them with `accounts_discovery`. A date range is required. There is no report type to set, but every field in one query must share a report type, so query profile-level and post-level fields separately.
- `ds_id`: `IGPD2` (Instagram Public Data) for any public business or creator profile. Pass the username as `ds_accounts` and set the report type: `{"report_type": "BusinessDiscoveryAccount"}` (profile info, no date range), `BusinessDiscoveryMedia` (profile posts, date range required) or `HashtagSearchMedia` (post search by hashtag; `result_type` is `recent_media` or `top_media`).
- The `instagram_insights` tool takes the same parameters as `data_query` and is a convenient entry point for these sources; `data_query` works equally well.

## Fields that answer most questions (IGI)

| Need | Field IDs |
|---|---|
| Profile totals | `followers_count`, `follows_count`, `media_count` |
| Growth and reach over time | `follower_count` (new followers), `reach`, `profile_views`, `accounts_engaged`, `date` |
| Post performance | `media_id`, `timestamp`, `media_product_type`, `media_permalink`, `media_caption`, `media_views`, `media_reach`, `interactions`, `media_like_count`, `media_comments_count`, `media_saved`, `media_shares` |
| Reels | `media_reel_avg_watch_time`, `media_reels_skip_rate`, `media_reel_total_interactions`, `media_reel_shares` |
| Stories | `media_story_views`, `media_story_reach`, `media_story_replies`, `media_story_taps_forward`, `media_story_exits` |
| Audience | `audience_age`, `audience_gender`, `audience_country_dim`, `audience_city_only_dim` with `followers_count`; `online_followers` by `hour` |

Public profiles (IGPD2): `followers`, `total_post_count`, `username` for profile info; `post_likes`, `post_comments`, `post_views` (reels), `likes_per_post`, `post_type`, `post_permalink` for posts. Confirm IDs with `field_discovery` before building unusual queries.

## Workflows

1. **Monthly performance.** Profile reach, views and new followers by `date` for this month and last, then the top 10 posts by `interactions` with `media_product_type` to show which formats carried the month.
2. **Reels review.** Reels by `media_views`, `media_reel_avg_watch_time` and `media_reels_skip_rate`. A high skip rate points to a weak opening; low watch time with a low skip rate points to length or pacing.
3. **Best time to post.** `online_followers` split by `dayOfWeekName` and `hour` for the last 30 days; recommend the two or three strongest windows.
4. **Competitor benchmark.** For each competitor username, IGPD2 `BusinessDiscoveryAccount` for followers, then `BusinessDiscoveryMedia` for `posts`, `likes_per_post` and `comments_per_post` over the same period. Compare with your own IGI figures, using likes and comments only, since public data has no reach.
5. **Who the audience is.** Follower age and gender, then top countries and cities. Compare with the target customer before suggesting content changes.

## Pitfalls

- `follower_count` (new followers) covers only the last 30 days and never the current day. `followers_count` is the current total, not a history.
- `reach`, `accounts_engaged` and the reels averages are calculated by Instagram. Never sum or average them across rows; request the grouping you need instead.
- `online_followers` covers the last 30 days only, needs 100 or more followers, and the latest one or two days may be missing.
- Public data shows only what Instagram exposes publicly: no reach, views of non-reel posts or demographics for other accounts.

Finish with the answer first, then the evidence. For a recurring Instagram report, offer a live dashboard (see `studio-dashboards`).
