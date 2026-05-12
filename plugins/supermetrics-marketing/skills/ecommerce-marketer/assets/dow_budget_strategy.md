# Day-of-week budget weighting strategy template

The recommendation doc that comes out of the blended ROAS / day-of-week analysis workflow. Audience is the ecommerce marketer themselves or their direct lead — internal planning document, not a leadership deliverable.

The point of this doc isn't to explain the data — it's to commit to a specific scheduling change and define what would cause us to back out of it.

---

## Day-of-week budget weighting strategy
**Period analyzed:** [Date range]
**Platforms:** [Google Ads, Facebook Ads, etc.]
**Period type:** [Non-promo / mixed / excluded-promo]

### Recommendation

Apply a day-of-week budget weighting starting [start date]:

| Day | Weighting | Rationale |
|---|---|---|
| Monday | [flat / +X% / -Y%] | [Brief] |
| Tuesday | [flat / +X% / -Y%] | [Brief] |
| Wednesday | [flat / +X% / -Y%] | [Brief] |
| Thursday | [flat / +X% / -Y%] | [Brief] |
| Friday | [flat / +X% / -Y%] | [Brief] |
| Saturday | [flat / +X% / -Y%] | [Brief] |
| Sunday | [flat / +X% / -Y%] | [Brief] |

Net effect: total weekly spend stays constant; allocation shifts toward the best-performing days.

### What the data showed

Over the period analyzed:
- **Best ROAS days:** [Day 1] at [X]x and [Day 2] at [Y]x
- **Worst ROAS days:** [Day 1] at [X]x and [Day 2] at [Y]x
- **Spread between best and worst:** [N]%
- **Pattern consistency:** [Strong / moderate / weak — based on whether the same days won across multiple weeks]

[Brief paragraph on what's driving the pattern — if known. E.g. "The Tuesday/Wednesday strength likely reflects our category's research-purchase cycle: customers research midweek, complete purchase Thursday-Saturday. The current flat schedule under-spends during the research window where intent is being formed."]

### How the schedule shift will be implemented

**Platform-specific approach:**
- **Google Ads:** [Use campaign-level ad schedule with bid adjustments. Reach the +X% target via day-of-week bid multipliers on the relevant campaigns.]
- **Facebook Ads:** [Either dayparting at the ad-set level (limited control) or daily budget changes via a scheduled rules / external tool, depending on platform setup.]

**Rollout:**
- Implement on [date]
- Run for 4 weeks before evaluating
- Don't apply during [list of any known promo periods in the window]

### What would invalidate this strategy

- **Promo period launches.** During BFCM, holiday sales, or flash sales, normal day-of-week patterns scramble. Revert to flat weighting (or promo-specific weighting) for the duration.
- **Sustained pattern change.** If after 4 weeks the day-of-week ranking has shifted — e.g. what was the best day is now mid-pack — that's a sign customer behavior has changed (seasonality, demographic shift, new product mix). Re-run the analysis before continuing the schedule.
- **Inventory constraints.** If concentrating spend on the top days drives traffic that exceeds inventory or fulfillment capacity, back off. The math assumes elastic supply.

### Checkpoint

Re-run the blended ROAS analysis on [date — 4 weeks after start]. Specifically check:
- Did the weighted-up days continue to outperform, or did concentrating spend compress ROAS on those days?
- Is the spread between best and worst day larger, smaller, or unchanged?
- Has total weekly ROAS improved as expected, declined, or stayed flat?

If weighted-up days are showing material ROAS compression (>15%), reduce the weighting toward flat. The pattern can be real and still have diminishing returns.

---

## Tone notes

- This is an operational doc, not a strategic narrative. Tables and bullets beat prose.
- The "what would invalidate this strategy" section is the most important part. It converts a one-way decision into a measurable experiment with clear exit criteria.
- "Pattern consistency" matters more than headline spread. A 30% best-to-worst spread that varies wildly week to week is not actionable; a 15% spread that's stable across 4+ weeks is.
- The checkpoint date is non-negotiable. Day-of-week strategies tend to drift if not actively re-validated, because customer behavior shifts and inventory mixes change.
- This doc is short by design. It's a recipe, not a research paper.
