# Negative keyword recommendations template

The structured doc proposing negative keywords for upload to the ad platform. Audience: the user themselves (or the paid search specialist they hand it to). The doc needs to be precise enough that someone can take the list and bulk-upload it without further analysis.

The shape:
- Summary: how much waste, how many negatives proposed
- The recommendations table
- Notes on rollout (which campaigns, which match types)

---

## Negative keyword recommendations — [Date]

**Summary**

Audited [N] search terms from [Google Ads / Microsoft Ads] over the last [time window]. Identified [N] terms costing $[total] without converting. Proposing [N] negative keywords across [N] campaigns. Estimated savings if applied: ~$[amount]/month based on current pace.

### Recommendations

| Search term | Cost | Clicks | Conv | Proposed negative | Match type | Apply to |
|---|---|---|---|---|---|---|
| [exact query] | $[X] | [N] | [N] | [keyword] | [exact/phrase/broad] | [campaign or "All search campaigns"] |
| [exact query] | $[X] | [N] | [N] | [keyword] | [match type] | [campaign] |

### Match type guidance

- **Exact match** `[keyword]` — for single, specific irrelevant queries the user is unlikely to repeat the exact phrasing of (e.g. specific competitor names, specific job titles).
- **Phrase match** `"keyword"` — for groups of queries that share a 2-3 word irrelevant phrase (e.g. "free download", "jobs at").
- **Broad match** `+keyword` — for single irrelevant words that should never appear (e.g. "salary", "wikipedia"). Use sparingly — broad negatives can over-exclude.

### Rollout

1. **Test first**: apply the highest-cost 5-10 negatives at campaign level and monitor for 5-7 days. If volume drops more than expected on related (legitimate) queries, the negative is too broad — refine before continuing.
2. **Account-level negatives**: terms that are universally irrelevant (e.g. "free", "jobs", competitor names) can go in an account-level negative keyword list rather than per-campaign.
3. **Re-audit**: run the search term audit again in 30 days to catch new wasteful terms that appear after this cleanup.

### What's not in this list

- Terms with cost below $[threshold] — not enough waste to justify the rollout overhead
- Terms with at least one conversion — might still be lower-intent than ideal but aren't pure waste
- Terms matching keywords the user is actively bidding on — those need keyword-level changes (lower bids or pause), not negatives

---

## Tone notes

- This doc should be uploadable as-is. Match types in the right column, target campaigns specified, rationale only where it would help an unfamiliar reader.
- The "test first" rollout note is the most important part. Bulk-applying 50 negatives without testing can cratering volume.
- If the user has a negative keyword list already, the script should be re-run excluding those terms so the doc doesn't propose duplicates.
- For Google Ads, the file format that uploads cleanly is CSV with columns: Match type, Negative keyword, Campaign. Match the structure if delivering as XLSX.
