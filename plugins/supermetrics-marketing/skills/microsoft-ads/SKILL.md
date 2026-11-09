---
name: microsoft-ads
description: Microsoft Advertising (Bing Ads) analysis and changes through Supermetrics — campaign, keyword and search term performance, negative keyword candidates, impression share lost to budget, Bing vs Google Ads comparison, and budget, status, bid and keyword updates. Use for "Bing Ads report", "wasted search spend on Bing", "add negative keywords".
---

# Microsoft Advertising (Bing Ads)

Answer Microsoft Advertising questions with live data, and make campaign changes when asked. If the Supermetrics tools aren't available in this session, follow the `get-started` skill first.

## Data source

- `ds_id`: `AC` (Microsoft Advertising). Accounts are ad accounts; list them with `accounts_discovery`. A date range is required.
- There is no report type to choose: the fields you request decide the report. For example, `SearchQuery` returns the search query report, and `QualityScore` the keyword report.
- Set `exclude_invalid_accounts: true` in `settings` when querying many accounts, so a disabled account doesn't fail the query.

## Fields that answer most questions

| Need | Field IDs |
|---|---|
| Core metrics | `Impressions`, `Clicks`, `Spend`, `Conversions`, `Revenue`, `Ctr`, `Cpc`, `CostPerConversion`, `ROAS` |
| Structure | `CampaignName`, `CampaignStatus`, `AdGroupName`, `Keyword`, `BidMatchType`, `DeliveredMatchType` |
| What people searched | `SearchQuery` (with `Keyword` to see which keyword matched it) |
| Lost reach | `ImpressionSharePercent`, `ImpressionLostToBudgetPercent`, `ImpressionLostToRankAggPercent` |
| Keyword quality | `QualityScore`, `ExpectedCtr`, `AdRelevance`, `LandingPageExperience` |
| Segments | `Date`, `YearWeekIso`, `DeviceType`, `Network`, `CurrencyCode` |

Confirm IDs with `field_discovery` (`ds_id: AC`) before building unusual queries. Use `Spend_usd` or `Spend_eur` when accounts use different currencies.

## Workflows

1. **Search term audit.** Pull `SearchQuery`, `Keyword`, `Spend`, `Clicks`, `Conversions` for the last 30 days. Queries with meaningful spend and no conversions, or clearly off-topic wording, are negative keyword candidates. Group them by theme and propose match types.
2. **Budget-limited campaigns.** Rank campaigns by `ImpressionLostToBudgetPercent` alongside `CostPerConversion`. A campaign losing reach to budget at a good cost per conversion is the first place to add budget; one losing to rank needs bids or quality work instead.
3. **Bing vs Google.** Run the same fields on `AC` and Google Ads (`ds_id: AW`) for the same dates and compare cost per conversion, CPC and conversion rate by campaign theme. Microsoft volume is usually smaller, so judge it on cost per conversion rather than volume.
4. **Make changes.** For budgets, status, bids, keywords and negative keywords, read the campaign first with `campaign_and_resource_get`, then use `manage_campaign` (`ds_id: AC`). Use `ad_groups[].add_keywords` / `remove_keywords` to change keywords without touching the rest, and `targeting.negative_keywords` for negatives. Follow the `campaign-management` skill for approval and safety rules.
5. **Keyword research.** `campaign_and_resource_get` with `resource_type` `keyword_ideas` or `keyword_volumes` suggests new keywords and estimates search volume; `recommendations` and `history` show Microsoft's suggestions and recent account changes.

## Pitfalls

- `Ctr`, `Cpc`, `ConversionRate`, `ROAS` and impression share fields are calculated by Microsoft. Never sum or average them across rows; request the grouping you need instead.
- `Conversions` counts only the goals the account includes in conversions; `AllConversions` includes the rest. Say which one you report, and use the same definition when comparing with Google Ads.
- Search query data hides low-volume queries, so query totals won't match campaign totals.

Finish with the answer first, then the evidence. For a recurring Microsoft Advertising report, offer a live dashboard (see `studio-dashboards`).
