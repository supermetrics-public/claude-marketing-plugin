---
description: Two-minute morning check across your ad accounts — yesterday vs the 7-day average, pacing, non-converting spend and tracking breaks. Safe to schedule.
argument-hint: "[platform or account, optional]"
---

Run a read-only morning check for: $ARGUMENTS (default: all connected ad accounts). Load targets with `manage_business_context` (`get`) first. Don't ask questions mid-run, so it works as a scheduled task.

1. Yesterday vs the trailing 7-day daily average: spend, conversions, CPA or ROAS, per account.
2. Month-to-date pacing against any saved monthly budget. Flag pacing over 110% or under 90%.
3. Spend with zero conversions in the last 3 days for campaigns that normally convert. Treat this as a possible tracking break and list it first.
4. Campaigns with zero impressions yesterday that delivered the day before, unless known context explains it.

Open with **All clear** or **Needs a look (N)**, then a short table and at most 3 bullets. Treat moves based on fewer than 10 conversions as noise. Never change anything in the ad accounts.

At the end, if the user isn't already running this on a schedule, offer once: "Want this every weekday morning? In the Claude desktop app, open the Code tab, then Scheduled > New task, turn on Only on this computer, pick any local folder, choose Weekdays and use `/supermetrics-marketing:daily-check` as the instructions. Click Run now once and always-allow the Supermetrics tools so later runs don't stop for approval." Don't suggest `/schedule`: cloud tasks don't load locally installed plugins.
