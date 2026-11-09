---
name: email-marketing
description: Email and SMS marketing performance through Supermetrics across Klaviyo, Mailchimp, HubSpot marketing emails, ActiveCampaign and Brevo — opens, clicks, unsubscribes, revenue per recipient, flows vs campaigns, list growth. Use for "Klaviyo flows vs campaigns", "which subject lines work", "Mailchimp open rate", "email revenue" and newsletter reports.
---

# Email and SMS marketing

Answer email and SMS questions with live data from the user's email platform. If the Supermetrics tools aren't available in this session, follow the `get-started` skill first.

## Data sources

| Platform | `ds_id` | Notes |
|---|---|---|
| Klaviyo | `KLAV` | Email and SMS, campaigns and flows, attributed store revenue |
| Mailchimp | `MC` | Campaigns, automations, lists and list growth |
| HubSpot Marketing Email | `HSME` | Setting `HUBSPOT_DATE_SETTING` picks emails by created date (default) or by sent date: `publishDate\|publishedAfter\|publishedBefore` |
| ActiveCampaign | `ACT` | Choose a report type, for example `settings={"report_type": "campaigns"}` |
| Brevo | `SIB` | |

Also available: Omnisend (`OMNSD`), Campaign Monitor (`CM`), Braze (`BRAZE`), Marketo / Adobe Engage (`MARK`) and Eloqua (`ELOQ`). A date range is required for all of them. Klaviyo and Mailchimp pick the report from the fields you request, so no report type is needed; for the others, check `data_source_discovery` and `field_discovery` with the `ds_id` before querying.

## Klaviyo fields

| Need | Field IDs |
|---|---|
| Campaign or flow | `campaign_name`, `campaign_subject`, `campaign_send_date`, `flow_name`, `list_name` |
| Engagement | `klaviyo_received_email`, `klaviyo_opened_email_unique`, `klaviyo_open_rate`, `klaviyo_clicked_email_unique`, `klaviyo_click_rate`, `klaviyo_bounce_rate`, `klaviyo_spam_rate`, `klaviyo_unsubscribed_from_list` |
| SMS | `klaviyo_received_sms`, `klaviyo_clicked_sms`, `klaviyo_unsubscribed_from_sms` |
| Revenue (Shopify store) | `shopify_placed_order`, `shopify_placed_order_value`, `shopify_revenue_per_recipient` (`magento_` and `woocommerce_` versions exist) |

Set `fetch_attributed` to count only orders Klaviyo attributes to its messages; `exclude_campaigns_out_of_daterange` limits results to campaigns sent within the date range.

## Mailchimp fields

| Need | Field IDs |
|---|---|
| Campaign | `campaign_name`, `subject_line`, `campaign_last_sent_date`, `list_name` |
| Engagement | `emails_sent`, `emails_delivered`, `unique_opens`, `open_rate`, `unique_clicks`, `click_rate`, `unsubscribes`, `bounce_rate` |
| Revenue | `ecommerce_total_orders`, `ecommerce_total_revenue` |
| Automations | `automation_name`, `automation_open_rate`, `automation_click_rate` |
| Benchmarks and lists | `industry_open_rate`, `industry_click_rate`; list growth with `subscribed`, `unsubscribed`, `cleaned` by `yearmonth` |

Confirm IDs with `field_discovery` before building unusual queries.

## Workflows

1. **Flows vs campaigns (Klaviyo).** Query `flow_name` with `shopify_placed_order_value` and `shopify_revenue_per_recipient`, then `campaign_name` with the same metrics, and show each one's share of email revenue. Pull engagement (received, clicks) in a separate query if a combination is refused: all fields in one query must share a report type.
2. **Subject lines.** Campaigns by `campaign_subject` (Klaviyo) or `subject_line` (Mailchimp) with click rate and revenue per recipient. Rank by clicks, not opens.
3. **List health.** Unsubscribes, bounces and spam complaints over time; flag rising spam or bounce rates before they hurt deliverability.
4. **Email in the channel mix.** Compare email revenue with paid channels or GA4 (`ds_id: GAWA`) for the same period.

## Pitfalls

- Open rates are inflated by mail apps that preload images (for example Apple Mail Privacy Protection). Judge content on clicks and revenue.
- Rate fields (`klaviyo_open_rate`, `open_rate`, `click_rate`, and similar) are pre-calculated. Never sum or average them across rows; request the grouping you need instead.
- Email platforms credit revenue with their own attribution windows, so their revenue won't match GA4 or the store. Say so when comparing.

Finish with the answer first, then the evidence. For a recurring email report, offer a live dashboard (see `studio-dashboards`).
