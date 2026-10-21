---
description: Check whether conversion tracking can be trusted — ad platforms vs GA4 vs your store or CRM, implausible CPAs and broken UTMs
argument-hint: "[date range, optional]"
---

Check measurement health for: $ARGUMENTS (default: last 30 days). Run this before trusting any optimisation advice, because a tracking problem invalidates every other finding.

1. Daily conversions per ad platform against GA4 conversions from the same source/medium, and against backend truth if connected (Shopify or other store orders, HubSpot/Salesforce deals, Stripe). Report the gap per source. Over 20% is a problem.
2. Find days where spend continued but conversions fell to zero.
3. Sanity-check CPA by business type, using saved targets from `manage_business_context` if present. A CPA far below what the business could plausibly pay (for example B2B SaaS under 10 per "lead") usually means a soft event such as a page view or scroll is counted as the conversion. Say so.
4. Pull landing-page URLs from active ads and run `marketing_utilities` `utm_parse` and `link_check` on them, to catch missing or stripped UTMs and redirects that drop tracking parameters.

Output: a verdict (**Trustworthy**, **Use with caution** or **Broken**), a table of the gaps, and the fixes in priority order. Read-only.
