# Lead quality diagnostic template

The doc surfacing lead quality findings from the MQL-to-SQL workflow. Audience: marketing operations, demand gen leadership, possibly sales leadership.

The shape:
- Headline (which sources produce quality, which produce volume-without-quality)
- Quality scorecard per source
- Diagnosis for low-quality sources (3 possible causes)
- Recommendations

---

# Lead quality diagnostic — [Period]
**Submitted by:** [Marketing leader name]
**Date:** [Date]
**Cohort:** [Leads created between specific dates]

## Headline

[One sentence: "Of [N] leads from the period, [%] reached MQL and [%] reached SQL. LinkedIn Ads converts at [X]% lead-to-SQL — [N]x our average — but only generates [Y]% of total volume. Facebook Ads is the inverse: [X]% of volume, [Y]% lead-to-SQL conversion."]

## Quality scorecard

| Source | Leads | MQLs | SQLs | Lead → MQL | MQL → SQL | Lead → SQL | Median days to MQL | Cost per MQL |
|---|---|---|---|---|---|---|---|---|
| [Source] | [N] | [N] | [N] | [%] | [%] | [%] | [N] | $[X] |
| [Source] | [N] | [N] | [N] | [%] | [%] | [%] | [N] | $[X] |
| [Source] | [N] | [N] | [N] | [%] | [%] | [%] | [N] | $[X] |

## Diagnosis for low-quality sources

[Include this section only for sources with materially below-average MQL conversion. Skip otherwise.]

### [Source name]: [%] lead-to-MQL conversion (vs [%] average)

The low MQL rate could have three causes. Each one implies a different fix.

**Possible cause 1: Lead targeting** — the source brings in the wrong audience.
- Check: do leads from this source have job titles matching the ICP?
- Check: do they come from companies in the target size/industry?
- If yes → not a targeting issue.

**Possible cause 2: Lead nurture** — the leads are ICP-fit but aren't being touched effectively.
- Check: are these leads enrolled in nurture sequences?
- Check: open and click rates on nurture emails for this cohort vs average?
- Check: time from lead-creation to first sales touch?

**Possible cause 3: MQL definition** — the MQL bar may be misaligned.
- Check: do leads from this source convert at higher rates in stages *after* MQL (i.e. they skip the MQL definition but become customers)?
- Check: have any of these leads been manually flagged by sales as good despite missing MQL criteria?

We'd recommend pulling 20-30 specific leads from this source and reviewing them with sales to determine which cause is dominant. Without that step, fixing the wrong cause wastes effort.

### [Next low-quality source, same structure if there is one]

## Recommendations

### Immediate (this period)
- [Source]: [Specific action — "pause net-new spend pending review"]
- [Source]: [Specific action — "shift budget toward LinkedIn Ads which converts at [X]x"]

### Diagnostic work (this period)
- Pull 20-30 leads from [low-quality source] and review with sales
- Compare nurture engagement rates for [source] vs blended average

### Possible follow-up analyses
- Deal-source connection: for sources where leads convert to customers, what's the average deal size?
- Cohort trend: are conversion rates improving or declining month-over-month per source?
- Paid vs organic: blended organic conversion rates are typically higher; how does paid compare?

---

## Tone notes

- The headline must include the spread between best and worst source. That's the story.
- The diagnostic framework (3 causes) is the highest-value part of this doc. Without it, "low MQL rate" doesn't lead anywhere.
- Recommendations should split between "act now" and "investigate before acting." Avoid over-acting on noisy data.
- Length: 1-3 pages depending on number of sources analyzed.
