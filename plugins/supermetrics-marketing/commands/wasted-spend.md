---
description: Find ad spend that isn't converting — zero-conversion campaigns, ads, search terms, products and regions — and estimate the saving
argument-hint: "[platform or date range, optional]"
---

Using the performance-marketer skill, find non-converting spend for: $ARGUMENTS (default: all connected ad platforms, last 30 days). Load targets with `manage_business_context` first. Ignore items with under 1,000 impressions.

Flag:
- **Dead weight:** spend with no conversions in the last 14 days.
- **Expensive:** CPA more than 2x the account average, or more than 2x the saved target.
- **Budget traps:** campaigns taking over 30% of spend while delivering under 15% of conversions.
- **Search terms** (Google Ads, Microsoft Ads): zero-conversion terms with meaningful spend. Leave out brand terms and terms already matching a keyword, then propose negatives. Follow the "Search term audit and negative keywords" workflow.
- **Geography and products**, where the data has them: regions or products with a CPA over 2x the account's own average.

Output a table of the items, the monthly saving if each one is cut, and the proposed action. This is analysis only: change nothing in the ad accounts. At the end, offer once to apply the cuts (pauses, negatives, budget moves) with the campaign-management skill, after the user approves each change.
