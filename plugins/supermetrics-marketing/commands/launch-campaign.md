---
description: Plan and launch a paused campaign on Google Ads, Meta Ads, Microsoft Ads, TikTok Ads or LinkedIn Ads, with your approval at each step
argument-hint: "<platform, goal, budget, landing page>"
---

Plan and launch a campaign for: $ARGUMENTS. Follow the `campaign-management` skill.

1. Confirm the platform and ad account, then check write access: if a write fails with a permissions error, send the user to https://hub.supermetrics.com/write-settings.
2. Load naming conventions and budget limits with `manage_business_context`, and current campaigns with `campaign_and_resource_get`.
3. Propose the plan: objective, budget (amount, currency, daily or lifetime), targeting, ad groups and ad copy. Check the URLs and copy with `marketing_utilities` (`utm_parse`, `link_check`, `char_limits`). Wait for the user's OK.
4. Create the campaign. It is created paused. Show what was created and how to review it.
5. Enable it only if the user explicitly approves that campaign going live.
