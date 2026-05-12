# Media buyer alert email template

The urgent email to the media buying team when an anomaly is detected during a high-stakes promotional campaign. The audience is fielding many messages per hour during BFCM; this email has to be readable in 15 seconds and clear about what they should do next.

The shape:
- Subject signals urgency without false alarm — name the campaign and the metric
- Top of email: the number and the comparison
- Middle: which specific ad sets are responsible
- Bottom: the recommended action (concrete — pause, adjust bid, switch strategy)
- Note about verification (a polite version of "we think this is real, but check the pixel before pausing")

---

**Subject:** 🚨 [Campaign name] — cost per purchase [Nx] baseline yesterday, action needed

Hi team,

Yesterday's cost per purchase on [campaign name] came in at $[X] — that's [N]x the average from the prior [N] days ($[Y]). At current spend pace, this is roughly $[lost amount] of additional cost per day vs. expected.

**Ad sets driving the spike:**

| Ad set | Yesterday CPP | Baseline CPP | Ratio | Likely cause |
|---|---|---|---|---|
| [Ad set name] | $[X] | $[Y] | [N]x | [Tracking issue / real perf / mixed signal] |
| [Ad set name] | $[X] | $[Y] | [N]x | [Cause] |

**What I'd recommend, in order:**

1. **First, verify the pixel.** A 3x+ spike often points to a tracking issue rather than real performance decline. Check [Facebook Events Manager / Google Tag Assistant] for any failures or drops on yesterday's date. If the pixel was healthy, proceed to step 2.

2. **If pixel is healthy:** pause [specific ad set names] immediately. They're the biggest contributors and the cause flag suggests real performance issues.

3. **For the ambiguous ones** ([list]): switch bid strategy to manual CPC at $[X] for the next 24 hours rather than pausing — we want to test whether the issue is the algorithm overbidding into a saturated audience, not necessarily creative fatigue.

I'll re-run the comparison tomorrow morning to verify whichever actions you take had the intended effect.

Thanks for the fast turnaround — appreciate it.

[Sender name]

---

## Tone notes

- The subject line decides whether this gets opened in the next 5 minutes vs. the next 5 hours. The emoji + dollar-comparison framing is intentional — it signals urgency without sounding panicked.
- Lead with the number, not the analysis. Media buyers want to know "how bad" before "why."
- The "first, verify the pixel" step is non-negotiable. Most 3x CPP spikes during promo periods are tracking failures, not performance failures. Pausing ad sets because of a tracking glitch will cost real revenue.
- Recommend specific ad sets to pause, not "consider pausing underperformers." Media buyers will follow precise instructions; they'll resist vague ones (rightly).
- Mentioning the re-check tomorrow closes the loop. Without it, the media buying team takes action and never hears whether it worked, which makes future alerts less trusted.
- Keep the email body under one phone screen. The table can be wider; the prose has to be tight.
- If sent via Gmail draft connector, save as draft — the user will want to verify the numbers themselves before sending.
