---
name: google-business-profile
description: Google Business Profile (formerly Google My Business) local analytics through Supermetrics — calls, direction requests, website clicks, Maps and Search views, search terms, reviews and star ratings by location. Use for local SEO, multi-location comparisons, "how many calls did we get", review monitoring, and posting or review replies.
---

# Google Business Profile

Answer local-presence questions with live Google Business Profile data. If the Supermetrics tools aren't available in this session, follow the `get-started` skill first.

## Data source

- `ds_id`: `GMB` (Google Business Profile, formerly Google My Business). Accounts are locations; get them with `accounts_discovery`. Query several locations at once and split with `location_name` to compare them.
- A date range is required. There is no report type to choose: Supermetrics picks it from the fields, so keep each query within one group from the table below (performance, search terms, reviews, posts or media).
- The `exclude_invalid_accounts` setting skips disabled or inaccessible locations instead of failing the query.

## Fields that answer most questions

| Need | Field IDs |
|---|---|
| Customer actions | `actions_total`, `actions_phone`, `actions_driving_directions`, `actions_website`, `actions_messages`, `actions_bookings`, `actions_food_orders`, `actions_food_menu_clicks` |
| Profile views | `views_total`, `views_search`, `views_maps` (each also `_desktop` and `_mobile`, for example `views_maps_mobile`) |
| Search terms | `search_keywords`, `search_impressions` (monthly) |
| Reviews in the period | `review_total_count`, `review_avg_star_rating`, `review_reply_response_time`, plus `review_star_rating`, `review_comment`, `review_reply_comment`, `review_create_date` |
| Lifetime review totals | `total_review_count`, `total_review_star_rating` |
| Posts | `post_count`, `post_summary`, `post_topic_type`, `post_state`, `post_create_time` |
| Location and time | `location_name`, `location_id`, `location_address_locality`, `location_category_name`, `date`, `yearMonth`, `yearWeekIso` |

Confirm IDs with `field_discovery` (`ds_id: GMB`) before building unusual queries.

## Workflows

1. **Location scorecard.** `location_name` with `views_total`, `actions_total`, `actions_phone`, `actions_driving_directions` and `actions_website` for the last 30 days against the previous 30. Rank locations by actions per view to find profiles that are seen but not acted on.
2. **Where people find you.** Compare `views_search` with `views_maps`, and mobile with desktop. A high Maps share means people already searching nearby; a high Search share means brand or category searches.
3. **Search terms.** `search_keywords` by `search_impressions`, by month. Separate brand names from category terms ("dentist near me") to show discovery demand.
4. **Review health.** `review_total_count`, `review_avg_star_rating` and `review_reply_response_time` by location and month. List recent low-star reviews with `review_comment` and whether `review_reply_comment` is empty.
5. **Act on it.** To publish a post or reply to reviews, use the `social-media-publishing` skill (`manage_social_media` with `ds_id: GMB`, one location at a time). Draft review replies for the user to approve; never post them unapproved.

## Pitfalls

- `review_avg_star_rating` and `total_review_star_rating` are averages; don't sum or average them across rows. Request the grouping you need instead.
- Performance data lags about 4–5 days and the latest days come back as 0, not missing. End comparisons on the last day with data.
- `search_impressions` is monthly; don't split it by day or week. Low-volume terms can show 0 because Google reports them only as below a threshold.
- Phone, direction and website actions are taps on the profile, not completed calls, visits or sales.

Finish with the answer first, then the evidence. For a recurring multi-location report, offer a live dashboard (see `studio-dashboards`).
