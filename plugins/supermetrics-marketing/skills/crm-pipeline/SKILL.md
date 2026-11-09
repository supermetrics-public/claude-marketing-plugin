---
name: crm-pipeline
description: Connect ad spend to CRM outcomes through Supermetrics — HubSpot, Salesforce, Pipedrive and Zoho CRM leads, MQLs, deals, pipeline and revenue by source or campaign, combined with ad platform spend for cost per MQL, cost per opportunity and pipeline ROAS. Use for "HubSpot deals by source", "Salesforce opportunities by campaign", "cost per MQL".
---

# CRM pipeline and ad spend

Answer "which marketing spend turns into pipeline and revenue" by pairing CRM data with ad platform spend. For broader B2B workflows (lead quality, GA4 reconciliation, budget updates for sales leadership), use the `demand-gen` skill. If the Supermetrics tools aren't available in this session, follow the `get-started` skill first.

## Data sources

All four need a date range. Each has a setting that decides which date the range filters on; pick it deliberately.

- `HS` (HubSpot). No report type to choose. Dates: `contact_date_field` (`lifecycle_state_changed` or `contact_created`) and `deal_date_field` (`deal_closed`, `deal_created` or `deal_last_modified`).
- `SF` (Salesforce). No report type to choose. Dates: `lead_date_field` (`lead_created`, `lead_converted`, `lead_last_modified`) and `deal_date_field` for opportunities. `convert_to_default_currency: true` for multi-currency orgs.
- `PIPE` (Pipedrive). `settings={"report_type": "deals"}` or `"leads"`, with `PIPE_DATA_SETTING` `add_time` or `update_time`.
- `ZOHO` (Zoho CRM). `settings={"report_type": "deals", "ZOHO_TIME_SETTING": "Created_Time"}` (also `leads`, `contacts`, `accounts`; `Modified_Time`). The time setting is required.

## Fields that answer most questions

| CRM | Volume and value | Source and stage |
|---|---|---|
| `HS` | `contact_lead_count`, `contact_marketing_qualified_lead_count`, `contact_opportunity_count`, `contact_customer_count`, `deal_total_count`, `deal_amount`, `deal_closed_won`, `deal_amount_closed_won` | `original_source`, `original_source_data_1`, `original_source_data_2`, `contact_first_touch_converting_campaign`, `deal_stage`, `deal_pipeline` |
| `SF` | `lead_count`, `opportunity_count`, `opportunity_amount`, `opportunity_amount_closed_won`, `campaign_number_of_leads`, `campaign_number_of_opportunities`, `campaign_amount_won_opportunities` | `lead_source`, `lead_is_converted`, `opportunity_lead_source`, `opportunity_stage_name`, `opportunity_is_won`, `campaign_name` |
| `PIPE` | `leads`, `lead_value`, `deals`, `deal_value` | `lead_source_name`, `lead_channel`, `deal_channel`, `deal_status`, `stage_id`, `pipeline_id` |
| `ZOHO` | `leads`, `deals`, `amount`, `expected_revenue` | `lead_source`, `lead_status`, `deal_lead_source`, `deal_stage`, `campaign_source_id` |

Ad spend comes from the ad platforms: `Cost` (Google Ads, `AW`), `cost` (Meta Ads, `FA`), `spend` (LinkedIn Ads, `LIA`), `Spend` (Microsoft Advertising, `AC`). Confirm IDs with `field_discovery` before unusual queries; CRMs often add custom fields.

## Workflows

1. **Pipeline by source.** Pull deals or opportunities created in the period, grouped by the source field, with count and amount. In HubSpot, `original_source` shows the channel (for example paid search or paid social) and `original_source_data_1` / `_2` drill into it.
2. **Cost per MQL and per opportunity.** Sum spend per channel from each ad platform for the same dates, then divide by CRM MQLs (`HS`) or opportunities. Map ad platforms to CRM source values explicitly and show that mapping in the answer.
3. **Campaign-level ROI.** Where the CRM records the campaign (Salesforce campaigns, HubSpot `contact_first_touch_converting_campaign`, Zoho `campaign_source_id`), match on campaign names or IDs from the ad platform and report pipeline and won revenue per unit of spend.
4. **Funnel conversion.** Leads to MQL to opportunity to won, by source. A channel with cheap leads but low opportunity rates is buying volume, not pipeline.

## Pitfalls

- The date setting changes the answer. Deals filtered by close date answer "revenue won this quarter"; by create date, "pipeline created this quarter". Spend should be compared with pipeline created in the same period, allowing for the sales cycle.
- Source values come from each CRM's own tracking. "Offline", "Direct traffic" or empty sources hide paid traffic whose tracking was lost; call out their share instead of ignoring them.
- Pipedrive returns stage and pipeline as IDs (`stage_id`, `pipeline_id`), not names. Ask the user what they map to.
- Salesforce campaign cost fields reflect what was entered in Salesforce, not live ad spend. Use ad platform spend for cost metrics.

Finish with the answer first, then the evidence. For a recurring pipeline report, offer a live dashboard (see `studio-dashboards`).
