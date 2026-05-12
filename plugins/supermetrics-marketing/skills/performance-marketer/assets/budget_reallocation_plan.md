# Budget reallocation plan template

The concise plan output from the budget reallocation modeler. Audience: the user themselves and whoever approves budget shifts (usually a marketing leader or finance partner).

The constraint that shapes this doc: it has to be defensible. The model is just math; the defense lies in surfacing assumptions and naming the checkpoint where the assumptions get tested.

---

## Budget reallocation plan — [Date]
**Period:** [Next month / next quarter / specific dates]
**Total target spend:** $[X] (vs current $[Y], [+/-Z%])

### Recommendation

| Channel | Current | Proposed | Shift | Why |
|---|---|---|---|---|
| [Channel] | $[X] | $[Y] | [+Z%] | [ROAS Nx, lower dampening — has headroom] |
| [Channel] | $[X] | $[Y] | [+Z%] | [Same structure] |
| [Channel] | $[X] | $[Y] | [-Z%] | [ROAS Nx, near saturation per dampening signal] |
| [Channel] | $[X] | $[Y] | [-Z%] | [Same structure] |

**Projected revenue impact:** $[current revenue] → $[projected revenue] ([+Z%])

### Assumptions

The model is built on these assumptions. Each one can be challenged independently:

- **ROAS holds with dampening at proposed spend levels.** The model applies a dampening factor per channel (range 0.5–1.0) based on observed ROAS variance at higher daily spend. Channels showing ROAS compression at peak-spend days get more aggressive dampening; channels with stable ROAS get less. The dampening factor for each channel is listed in the model output.
- **No structural changes to the channels.** The model doesn't account for major platform changes (new ad units launching, attribution model changes, policy shifts) that could shift baseline economics.
- **Audience supply doesn't constrain.** For channels getting a budget increase, the model assumes there's incremental audience to acquire at the dampened ROAS. This breaks down at very high spend on narrow audiences.
- **Attribution holds.** If the current ROAS numbers are based on platform-reported conversions and the user moves to a different attribution model, the model's projections need to be re-run.

### What the model is NOT

- Not a prediction. It's a "given these assumptions, here's the math" exercise.
- Not optimized for diversification or risk. The model maximizes projected revenue; if the user wants to maintain channel diversity for risk reasons, that's a separate constraint to add.
- Not a substitute for incrementality testing or media mix modeling. Those are the right tools for true causal attribution; this is operational budget planning.

### Checkpoint

Review actual performance vs projected on [date — typically 2 weeks after the shift starts]. Specifically check:

- Is the high-shift channel still producing ROAS within 10% of its current rate?
- Is the low-shift channel's ROAS holding (since it now has fewer competing dollars)?
- Has total spend held to the target, or did the algorithm fail to spend the proposed amount on the increased channels?

If actuals diverge from projection by more than 15% on revenue or ROAS, re-run the model with the new data.

---

## Tone notes

- The "What the model is NOT" section is the most credibility-building part of this doc. Marketers who acknowledge model limitations get more autonomy than those who don't.
- "Projected" is the right word everywhere a number from the model appears. Not "expected", not "forecasted" — "projected" carries the right level of conditional certainty.
- The checkpoint date is non-negotiable. Without it, the plan becomes a one-way decision; with it, it's an experiment.
- Length: this doc should be readable in 90 seconds. If a finance partner needs more detail, they can ask.
