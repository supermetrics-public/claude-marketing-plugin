---
name: youtube
description: YouTube channel analytics through Supermetrics — views, watch time, subscribers, top videos, Shorts vs long-form, audience retention, traffic sources, demographics and geography, plus public stats for any channel or video. Use for "YouTube analytics", "top videos", "subscriber growth", "Shorts performance" and competitor channel comparisons.
---

# YouTube analytics

Answer YouTube questions with live data. If the Supermetrics tools aren't available in this session, follow the `get-started` skill first.

## Data sources

- `ds_id`: `YT2` (YouTube) for channels the user owns. Accounts are channels; list them with `accounts_discovery`. A date range is required and a report type must be set, for example `settings={"report_type": "LatestVideos"}`. Report types: `ChannelTotals` (channel overview), `LatestVideos` (videos performance), `VideoTotals` (one video; set `video_id`), `TrafficSources`, `Geo`, `Demographic`, `Device` and `AdPerformance`.
- `ds_id`: `YTPD` (YouTube Public Data) for any public channel or video. No account list and no date range; the target goes in settings: `{"report_type": "channels", "YOUTUBE_CHANNEL_ID": "UC…"}` (up to 49 comma-separated `UC…` IDs), `channel` (one channel's videos), `video` (`YOUTUBE_VIDEO_ID`, up to 49), or `search_channels` / `search_videos` (`SEARCH_QUERY`) to find IDs by name.

## Fields that answer most questions (YT2)

| Need | Field IDs |
|---|---|
| Channel trend (`ChannelTotals`) | `date`, `views`, `estimatedMinutesWatched`, `subscribersGained`, `subscribersLost`, `likes`, `shares` |
| Channel lifetime totals (`ChannelTotals`) | `channel_subscribers`, `channel_videos` |
| Per video (`LatestVideos`) | `video`, `video_title`, `video_published_date`, `views`, `engaged_views`, `estimatedMinutesWatched`, `averageViewDuration_seconds`, `averageViewPercentage`, `likes`, `comments`, `subscribersGained` |
| Shorts vs long-form | `creatorContentType` with `views` and `estimatedMinutesWatched` |
| Where views come from | `insightTrafficSourceType` (`TrafficSources`), `country` (`Geo`), `deviceType` (`Device`), `ageGroup` and `gender` with `viewerPercentage` (`Demographic`) |
| Retention for one video (`VideoTotals`) | `elapsedVideoTimeRatio` with `audienceWatchRatio` or `relativeRetentionPerformance` |

Public data (YTPD): `channels__channel_name`, `channels__subscribers`, `channels__views`, `channels__video_count`; for a channel's videos `channel__videos__details__video_title`, `channel__videos__publish_date`, `channel__videos__details__views`, `channel__videos__details__likes`, `channel__videos__details__comments`. Confirm IDs with `field_discovery` before building unusual queries.

## Workflows

1. **Channel health.** `ChannelTotals` by `yearMonth_channel_totals` (the month field for this report) for views, watch time and net subscribers (`subscribersGained` minus `subscribersLost`) over the last six months.
2. **Top videos.** `LatestVideos` for the period ranked by `views`, with `averageViewPercentage` and `subscribersGained`. Videos with high retention but few views are candidates for better titles and thumbnails.
3. **Shorts vs long-form.** Split views, watch time and subscribers gained by `creatorContentType` to show what each format contributes.
4. **Why a video dropped off.** `VideoTotals` with `video_id` set, `elapsedVideoTimeRatio` and `audienceWatchRatio`, to find the moment viewers leave.
5. **Competitor channels.** YTPD `search_channels` to find channel IDs, then `channels` with up to 49 IDs for subscribers, views and video counts, and `channel` for each rival's recent videos.

## Pitfalls

- `channel_subscribers`, `channel_views` and `channel_videos` are lifetime snapshots and cannot be split by a date dimension; `channel_subscribers` is rounded down to three significant figures. For a trend, use `subscribersGained` and `subscribersLost`.
- `audienceWatchRatio` and `relativeRetentionPerformance` need the `VideoTotals` report with the `video_id` setting and cannot be combined with other metrics; a Video ID filter is not enough.
- Averages and percentages (`averageViewPercentage`, `viewerPercentage`) are calculated by YouTube. Never sum or average them across rows.
- Public data has no watch time, retention or audience details; compare competitors on views, likes, comments and subscribers only.

Finish with the answer first, then the evidence. For a recurring YouTube report, offer a live dashboard (see `studio-dashboards`).
