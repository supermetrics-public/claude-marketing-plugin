---
name: google-search-console
description: Google Search Console and SEO analysis through Supermetrics — organic clicks, impressions, CTR and average position by query, page, device and country, branded vs non-branded search, pages losing traffic, and quick-win keywords. Use for SEO audits, "why did organic traffic drop", "which queries rank on page 2", and Search Console reporting.
---

# Google Search Console and SEO

Answer organic search questions with live Search Console data. If the Supermetrics tools aren't available in this session, follow the `get-started` skill first.

## Data source

- `ds_id`: `GW` (Google Search Console). Accounts are sites: `sc-domain:example.com` covers the whole domain; URL-prefix properties such as `https://example.com/` cover only that prefix. Prefer the domain property when both exist.
- A date range is required. Search Console data lags about 2–3 days, so end comparisons on the latest complete day rather than today.

## Fields that answer most questions

| Need | Field IDs |
|---|---|
| Core metrics | `clicks`, `impressions`, `ctr`, `position` |
| What people searched | `query`, `branded_vs_nonbranded` (set the `brand_keywords` setting, for example `acme\|acme corp`) |
| Where they landed | `page`, `pathlevel1`, `page_title_tag` |
| Segments | `Date`, `Yearweekiso`, `device`, `countryname`, `searchType` |

Confirm IDs with `field_discovery` (`ds_id: GW`) before building unusual queries.

## Workflows

1. **Traffic drop.** Compare clicks for the last 28 days with the previous 28 by `page`, then by `query` for the pages that fell most. Separate "lost rankings" (`position` worse) from "lost demand" (`impressions` down at a stable position) from "lost CTR" (stable position and impressions, fewer clicks: often a title or snippet change).
2. **Quick wins.** Queries with average `position` between 8 and 20 and impressions in the top quartile. These are page-two terms where a content or internal-link improvement moves the most clicks.
3. **Low CTR pages.** Pages with high `impressions` and CTR well below others at a similar position. Pull `page_title_tag` and suggest rewritten titles.
4. **Branded vs non-branded.** Split clicks with `branded_vs_nonbranded` to show how much organic growth comes from people who already know the brand.
5. **Organic and paid together.** For "are we paying for clicks we'd get anyway", compare top non-branded queries here with Google Ads search terms (`ds_id: AW`).

## Pitfalls

- `ctr` and `position` are averages Google calculates. Never sum or average them across rows; request the grouping you need in the query instead.
- Totals split by query don't add up to site totals, because Google hides rare (anonymised) queries. Say so when the user compares numbers with the Search Console interface.
- Fewer than about 100 impressions per row is noise; don't draw conclusions from it.

Finish with the answer first, then the evidence. For a recurring SEO report, offer a live dashboard (see `studio-dashboards`).
