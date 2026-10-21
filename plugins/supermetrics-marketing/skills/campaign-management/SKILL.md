---
name: campaign-management
description: Create and update ad campaigns from Claude on Google Ads, Meta Ads, Microsoft Advertising, TikTok Ads, LinkedIn Ads, Snapchat and ChatGPT Ads through Supermetrics — with shared safety rules (read before write, created paused, approval levels, per-field targeting updates, check write_status). Use when the user wants to launch a campaign, change a budget or bid, pause or enable ads, edit targeting or manage creatives on ChatGPT Ads or Snapchat, when writing across several platforms at once, or alongside a connector skill for Google Ads, Meta Ads, Microsoft Advertising, TikTok Ads or LinkedIn Ads.
---

# Campaign management with Supermetrics

These tools spend real money. Treat every write as consequential.

## Before writing anything

1. Campaign writes must be enabled per advertising account at
   [hub.supermetrics.com/write-settings](https://hub.supermetrics.com/write-settings), where the
   account owner also sets an approval level: no human approval, going live, budget + going live,
   or all live changes. If a write fails with a permissions error, that is usually why.
2. Read before you write. `campaign_and_resource_get` shows current state — campaigns,
   ad groups, ads, keywords, audiences, budgets. Never update a campaign you have not read.
3. Check business context with `manage_business_context` (`action="get"`, plus `ds_id`
   and `account_id`). Naming conventions, budget ceilings and excluded campaigns live there.

## Safety rules

- **New campaigns are always created paused.** This is enforced by the platform layer;
  do not try to work around it.
- **Only set `status: "ENABLED"` when the user has explicitly approved that specific
  campaign going live.** Enabling starts spend immediately.
- **Google Performance Max**: enabling the campaign is not enough — its asset groups are
  paused too. Enabling those is a second, separately approved step.
- **`targeting` updates per field.** On update, omitted targeting fields are kept; each field
  you send replaces that whole list, so send its complete value (all locations, all
  interests), and `[]` clears it (not on Snapchat). For Google and Microsoft keywords,
  `ad_groups[].add_keywords` / `remove_keywords` append and remove without touching the rest.
  TikTok and LinkedIn: target existing ad groups through `ad_groups[].targeting`.
- **Confirm budgets in writing** before submitting. State the amount, the currency and
  whether it is daily or lifetime.

## Creating a campaign

Use `manage_campaign` without a `campaign_id`. `budget_amount` is required. Structure:

- Campaign level: name, budget, bidding strategy, dates, campaign-level targeting.
- `ad_groups[]`: ad sets or ad groups. Omit `id` to create, include `id` to update.
- `ad_groups[].ads[]`: each needs a name and a `creative` (headlines, descriptions,
  `final_urls`). Meta ads additionally require `page_id` in the ad's `platform_settings`.

Creatives accept, in order of preference: `asset_url` (a public URL), `asset_id` (already
in the ad account — find them via `campaign_and_resource_get` with
`resource_type="assets"`), or `upload_ref` from `creative_picker`. If the user has no
creative yet, open `creative_picker` to browse, upload, AI-generate or import one.

Platform quirks worth knowing before you build the payload:

- **Google Ads**: 3–15 headlines (30 chars), 2–4 descriptions (90 chars), `final_urls`
  required. Performance Max images must be 1.91:1, 1:1 or 4:5 — 16:9 and 9:16 are rejected.
- **Meta**: budget sits on the campaign under CBO, on each ad set under ABO. Carousels use
  `carousel_cards`, not `assets`.
- **TikTok**: video creatives must use `asset_id`; a URL will not work.
- **LinkedIn**: single image only.

## Updating

Pass `campaign_id` to update. Only the fields you send change. Campaign type and objective
are fixed at creation and cannot be changed afterwards.

Partial success is possible on multi-entity writes. Always check `write_status` and
`failures` in the response — do not assume success and do not blindly retry, which can
create duplicates.

When adding Google Ads keywords, read the response notes: a keyword that wasn't added is named
there with the reason. Report those to the user rather than assuming every keyword landed.

## After writing

Every change is logged at
[hub.supermetrics.com/campaign-history](https://hub.supermetrics.com/campaign-history).
Re-read with `campaign_and_resource_get` to confirm the final state, and tell the user
exactly what was created or changed, including which entities are paused.

## From analysis to action

The analysis workflows in this plugin only recommend changes, for example `/supermetrics-marketing:wasted-spend` or a budget reallocation. When the user wants to act on a recommendation, apply it here: list the exact changes, get explicit approval for each one, write it, then re-read to confirm.

## Forecasting and research

Before committing spend, `campaign_and_resource_get` also offers `resource_type` values
for planning: `forecast` (estimated performance at a given budget), `keyword_ideas` and
`keyword_volumes`, `reach_estimate`, `targeting_search`, `audiences` and `recommendations`.
