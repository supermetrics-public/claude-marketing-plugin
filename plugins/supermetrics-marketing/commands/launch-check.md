---
description: Pre-launch QA for a campaign — UTM tagging, landing page speed and links, ad copy length limits, domain safety
argument-hint: "<landing page URLs and/or ad copy>"
---

Run pre-launch QA on: $ARGUMENTS. Use `marketing_utilities`, which works without a subscription or connected data source:

1. `utm_parse` on every destination URL: missing or inconsistent UTMs, checked against the team's naming conventions in `manage_business_context` if saved. Offer corrected URLs via `utm_build`.
2. `link_check`: confirm each URL resolves and that UTMs and click IDs survive redirects.
3. `pagespeed_check` (MOBILE) on the landing pages. Flag a performance score under 50, and LCP over 2.5s.
4. `char_limits` on any headlines and primary text, for the target platforms (Google Ads, Meta, LinkedIn and X are supported).
5. `safety_check` on the landing domains (malware flags, certificate or domain expiry).
6. `link_preview` if the URL will be shared on social.

Output a checklist marked pass, warning or fail, with the exact fix for each failure.
