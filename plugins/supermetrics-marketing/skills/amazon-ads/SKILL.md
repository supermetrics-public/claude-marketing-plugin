---
name: amazon-ads
description: Amazon Ads reporting through Supermetrics — Sponsored Products, Sponsored Brands and Sponsored Display spend, sales, ACoS and ROAS by campaign, keyword, search term and ASIN, plus Seller Central sales for TACoS and Amazon DSP results. Use for "Amazon ACoS by campaign", "wasted Sponsored Products search terms", "total ACoS".
---

# Amazon Ads

Answer Amazon advertising questions with live data. This is reporting only: Supermetrics cannot create or change Amazon campaigns, so give recommendations the user applies in Amazon. If the Supermetrics tools aren't available in this session, follow the `get-started` skill first.

## Data source

- `ds_id`: `AA` (Amazon Ads). A report type is required: `settings={"report_type": "SponsoredProduct"}`, `"SponsoredBrand"` or `"SponsoredDisplay"`. Run one query per ad type and combine the results.
- `ds_id`: `ASELL` (Amazon Seller Central) for total store sales and traffic: `settings={"report_type": "sales_and_traffic_by_date"}`, `"sales_and_traffic_by_asin"` or `"orders"`. Accounts are marketplaces.
- `ds_id`: `ADSP` (Amazon DSP) for programmatic display and video: `settings={"report_type": "campaign"}` (also `inventory`, `audience`, `product`). DSP field IDs carry the report type as a prefix, for example `campaign__total_cost`.
- A date range is required for all three. Amazon queries can be slow to finish; that is on Amazon's side.

## Fields that answer most questions

| Need | Field IDs |
|---|---|
| Core ad metrics (`AA`) | `impressions`, `clicks`, `cost`, `sales`, `orders`, `acos`, `roas`, `cpc`, `ctr`, `conversionRate` |
| Structure (`AA`) | `campaignName`, `keywordText`, `matchType`, `query` (search term, Sponsored Products only), `asin` (Sponsored Products and Display) |
| New-to-brand (`AA`) | `attributedOrdersNewToBrand14d`, `attributedSalesNewToBrand14d` (Sponsored Brands and Display) |
| Store totals (`ASELL`) | `ordered_product_sales`, `units_ordered`, `sessions`, `page_views`, `unit_session_percentage`, `buy_box_percentage`, `date`, `child_asin` |
| DSP (`ADSP`) | `campaign__order_name`, `campaign__line_item_name`, `campaign__total_cost`, `campaign__impressions`, `campaign__purchases_14d`, `campaign__total_sales_14d`, `campaign__total_roas_14d` |

Confirm IDs with `field_discovery` (for example `ds_id: AA`, filter `acos`) before building unusual queries. `AA` also offers fixed attribution windows such as `ACOS7day` and `attributedSales14d`.

## Workflows

1. **ACoS by campaign.** Pull `campaignName`, `cost`, `sales`, `acos`, `orders` per ad type for the last 30 days. Compare each campaign's ACoS with the user's target margin; flag high-spend campaigns well above it.
2. **Search term audit.** With `report_type` `SponsoredProduct`, pull `query`, `keywordText`, `matchType`, `cost`, `clicks`, `orders`. Search terms with clicks and spend but no orders are negative keyword candidates; converting terms not yet targeted are candidates for exact-match keywords.
3. **TACoS (total ACoS).** Sum `cost` across all three ad types and divide by `ordered_product_sales` from `ASELL` for the same dates and marketplace. A falling TACoS with steady ACoS means organic sales are growing alongside ads.
4. **Product view.** Join ad `cost` and `sales` by `asin` with `ASELL` `sales_and_traffic_by_asin` (`child_asin`, `ordered_product_sales`, `sessions`, `buy_box_percentage`). Products that lost the buy box convert poorly regardless of ad spend.
5. **DSP alongside sponsored ads.** Report `ADSP` total cost and total ROAS separately from sponsored ads; DSP includes view-through purchases, so its ROAS is not comparable one-to-one.

## Pitfalls

- `acos`, `roas`, `cpc`, `ctr` and conversion rates are ratios. Never average them across rows; recalculate from summed `cost` and `sales`.
- Amazon attributes sales to ads for days after the click, so the last one to two weeks keep growing. Don't call a recent drop until the attribution window has closed.
- `sales` can include other products bought after an ad click; `salesSameSKU` covers only the advertised product. Say which you report.

Finish with the answer first, then the evidence. For a recurring Amazon report, offer a live dashboard (see `studio-dashboards`).
