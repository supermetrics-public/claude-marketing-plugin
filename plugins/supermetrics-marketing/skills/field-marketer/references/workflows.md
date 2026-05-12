# Field marketing workflows

Seven workflow patterns field marketers run across the event lifecycle: from pre-event acquisition through post-event measurement, multi-event portfolio review, pipeline tracking, account engagement scoring, webinar funnel analysis, and partner event ROI.

## Workflow 1: Pre-event channel ROI

**When to use:** the user is days or weeks from an event, wants to know where to put the remaining promotion budget, and needs to update the regional team on the plan.

**Platforms typically involved:** LinkedIn Ads and Google Ads most commonly. Facebook Ads occasionally.

### Step 1 — Pull the data
> Pull the last 30 days of performance data for campaigns containing [user's event naming convention — Event_, Webinar_, etc.] across [LinkedIn Ads, Google Ads, etc.].

Ask the user about the naming convention if unclear. Look for spend, clicks, and registrations (sometimes called conversions depending on platform setup).

If ad-platform registration numbers diverge significantly from the event platform (Zoom, Hopin, Eventbrite, On24), flag the discrepancy before proceeding — the comparison is misleading otherwise.

### Step 2 — Compare cost per registration
Use `scripts/registration_cost_compare.py`. The script warns when conclusions are based on fewer than 30 registrations per channel — the threshold below which CPR differences are likely noise.

### Step 3 — Visualize the comparison
The question the chart needs to answer: **which channel is generating registrations more efficiently, and how confident are we?**

A sorted horizontal bar chart of cost-per-registration works as the primary visualization, with bars sorted ascending (cheapest first). When sample sizes are small for one or more channels, distinguish those bars visually — lower opacity, a hatched pattern, or a "low confidence" badge next to the label — so the user doesn't over-trust low-N comparisons.

For richer context, a paired bar chart per channel showing CPR + registration rate side-by-side surfaces the trade-offs (sometimes the cheaper channel also has lower-quality engagement).

If the user is tracking pacing toward a registration target, a line chart of cumulative registrations vs target trajectory makes the gap visible.

### Step 4 — Recommend budget shift
The recommendation should be concrete: dollar amount, source channel, destination channel, expected lift in registrations. If sample size is low, recommend a smaller hedged shift (e.g. 15% rather than 50%) and explain why.

### Step 5 — Update the regional team
Use `assets/regional_team_update.md`. The message is short — Slack-length even if delivered as email.

If a Slack connector is active, the update typically goes there directly to the regional team's channel. If not, default to inline markdown the user can copy.

### Common variations
- **"What if we extend the campaign?"** — model expected additional registrations at current CPR. The script accepts a `--projected-days` flag.
- **Paid vs organic separately** — if the user has tagging that separates them, run the comparison separately rather than averaging.
- **Add cost per attendee** — needs post-event attendance data, which doesn't exist yet pre-event. If the user has historical attendance rates by channel, model expected attendees but state the assumption.

---

## Workflow 2: Post-event geo-targeted follow-up

**When to use:** the user just ran an in-person event in a specific region and wants to quantify whether it drove digital engagement lift locally.

**Platforms typically involved:** Facebook Ads, LinkedIn Ads at minimum. Google Ads if search campaigns ran. Campaigns need geo-targeting configured.

### Step 1 — Pull the regional data
> Pull the performance data from the last 14 days for the [Facebook Ads, LinkedIn Ads] campaigns geographically targeted to [region].

Be specific about the region's definition — city, metro, state. Facebook and LinkedIn handle geo-targeting differently. If unclear, check the campaign-level geo settings via the connector.

### Step 2 — Compare to national baseline
Use `scripts/geo_lift_analyzer.py`. The script normalizes regional metrics against a national baseline that excludes the target region (so the comparison isn't diluted by including the target in the baseline).

### Step 3 — Visualize the lift
The question the chart needs to answer: **did the event drive measurable digital lift in the region, and how big is the effect?**

A paired bar chart per metric (CTR, conversion rate, CPC) with two bars per group — target region vs rest-of-country — makes the lift immediately visible. Color the target region in indigo and the baseline in a lighter shade so they read as two views of the same data.

When the user wants to see the magnitude of lift as a single number, a horizontal bar chart of percent-lift per metric (CTR +44%, conversion rate +24%, CPC -41%) is faster to read. Color by direction of lift relative to what's good (CTR up is green, CPC down is green).

### Step 4 — Verdict
The script returns one of three verdicts: measurable lift / no detectable lift / insufficient data. Use this verdict explicitly in the deliverable — don't soften it. Field marketing measurement is more credible when the analyst names "we can't tell" rather than overclaiming.

### Step 5 — Build the post-event summary
Use `assets/post_event_lift_summary.md`. The doc should include the verdict, the data, what's confounded (paid promotion that ran in the region, simultaneous events), and what to do differently next time for cleaner measurement.

Default delivery: build as a Word doc with the `docx` skill if the user wants it as a leadership readout. Otherwise inline markdown.

### Common variations
- **Compare to same region last quarter, not to national** — different baseline, same workflow shape. Often a stronger test of "did the event do something."
- **Include earned media metrics** — usually outside Supermetrics. The user may have a PR or social listening tool with this data.
- **Project the pipeline impact** — risky. Pipeline attribution to a single event is fragile. If the user wants this, frame as a model with stated assumptions, not a measurement.

---

## Workflow 3: Multi-event portfolio analysis

**When to use:** the user has run 10-30 events over a quarter (or year) and wants to identify which event types and formats produce the best ROI. Used for next-period event planning and budget allocation.

**Platforms typically involved:** ad platforms (for promotion costs) + event platform / form platform for registration data + CRM for downstream pipeline (if available).

### Step 1 — Pull the event roster
> Pull the list of events held in [period]: event name, type (in-person / webinar / virtual conference / dinner / workshop), location, date, total spend (promotion + venue + production).

If the user maintains this in a spreadsheet or project tool, they may need to provide it directly rather than via Supermetrics.

### Step 2 — Pull registrations and attendance
> For each event, pull registrations and attendance counts. From the CRM (if connected), pull MQLs created within 30 days of the event from attendees.

### Step 3 — Compute composite ROI
Use `scripts/event_portfolio.py`. The script computes per event:
- Cost per registration
- Cost per attendee (CPA)
- Attendance rate
- MQL conversion rate from attendees (if CRM data available)
- Cost per MQL via the event
- Composite ROI score (normalized within event type)

### Step 4 — Visualize the portfolio
The question the chart needs to answer: **which event types and locations consistently produce the best outcomes?**

A scatter plot works: x-axis = cost per attendee, y-axis = MQL conversion rate (or pipeline value if available). Dots colored by event type, sized by total attendees. The user sees the best-ROI quadrant immediately.

A secondary view: bar chart of average composite ROI by event type, sorted descending. Surfaces which formats deserve more investment.

### Step 5 — Build the portfolio review
Use `assets/event_portfolio_review.md`. The doc should split into:
- **Best performers** (continue running)
- **Underperformers** (need improvement or sunset)
- **Experiments worth repeating** (one-off events with promising signals)
- **Recommended next-period mix** (specific event types and counts)

### Common variations
- **By region** — break out the portfolio by region to see whether the best-performing event types differ geographically.
- **By persona** — if attendee data includes job titles, cluster by target persona and see which event types attract which personas.
- **Sponsorship vs hosted** — separately analyze events the user hosted vs sponsored. The economics are different.

---

## Workflow 4: Event-driven pipeline tracking

**When to use:** the user has run an event and wants to track the pipeline created by attendees over 30, 60, and 90 day windows. The deliverable usually goes to sales leadership to justify event investment.

**Platforms typically involved:** event platform for attendee list + CRM (HubSpot, Salesforce, Pipedrive) for pipeline tracking.

### Step 1 — Get the attendee list
> Pull the attendee list for [event] including email addresses, company names, and job titles.

### Step 2 — Match attendees to CRM contacts
> For each attendee, find their CRM contact record. Pull: any opportunities created within 30/60/90 days of the event date, opportunity stage, opportunity amount.

Matching is usually by email but may need company-name fuzzy matching for attendees who used personal emails.

### Step 3 — Track pipeline progression
Use `scripts/event_pipeline_tracker.py`. The script computes:
- Total attendees
- Attendees matched to CRM contacts
- New opportunities created (in each 30/60/90 day window)
- Total pipeline value per window
- Closed-won deals (if any have closed)
- Cost per pipeline dollar (event cost / pipeline value)

### Step 4 — Visualize the conversion timing
The question the chart needs to answer: **how does pipeline from this event accumulate over time?**

A cumulative line chart works well: x-axis = days since event, y-axis = cumulative pipeline value. Mark the 30/60/90 day milestones. Shows whether the event produced fast-moving pipeline or slow-developing pipeline.

A secondary view: funnel chart from attendees → matched → opp created → closed-won, with the conversion rate at each step.

### Step 5 — Build the report
Use `assets/event_pipeline_report.md`. Audience: VP of Sales or CRO + the marketing leader who approved the event budget.

### Common variations
- **Compare events** — same workflow, multiple events. Surface which events drove the most pipeline relative to investment.
- **Include net-new contacts** — for accounts not previously in CRM that came in via the event. These are pure event acquisition; existing accounts that attended are influence vs acquisition.
- **Per-persona pipeline** — if event attendees include multiple personas (e.g. CMO, VP Marketing, Director), break out pipeline by attending persona to see which roles convert.

---

## Workflow 5: Account engagement scoring

**When to use:** the user runs B2B events where the goal is to deepen relationships with target accounts (vs raw lead capture). Specifically for ABM-aligned events.

**Platforms typically involved:** event platform for attendee data + CRM for target account list + LinkedIn Ads (if ABM ads were running) + GA4 for site behavior (if company-level identification is available).

### Step 1 — Define the target account list
Ask the user (via `ask_user_input_v0` if needed): which accounts are the priority for this event? Usually a tier-1 ABM list of 50-200 accounts.

### Step 2 — Compile engagement signals per account
For each target account, gather signals from the period spanning the event (e.g. 2 weeks before through 2 weeks after):
- Number of attendees from the account
- Seniority of attendees (CEO/VP/Director/IC)
- Pre-event ad impressions and clicks via LinkedIn account targeting
- Post-event website visits
- Sales activities logged (meetings booked, emails exchanged)

### Step 3 — Score engagement per account
Use `scripts/account_engagement.py`. The script computes per account:
- Engagement score (0-100, composite of all signals)
- Tier classification (engaged / warming / aware / cold)
- Whether the account is in active pipeline
- Last meaningful touchpoint

### Step 4 — Visualize the program-level outcome
The question the chart needs to answer: **how many target accounts did the event meaningfully engage, and which are ready for sales follow-up?**

A funnel chart works: target accounts → reached pre-event → attended → engaged post-event → in active pipeline. Each tier showing conversion rate.

A secondary view: the top 20 most-engaged accounts not yet in pipeline. This is the hand-off list for sales.

### Step 5 — Build the brief
Use `assets/account_engagement_brief.md`. Audience: B2B marketing + sales counterparts.

### Common variations
- **Tier-specific KPIs** — Tier 1 accounts may need a different success bar than Tier 2 (e.g. attendance + meeting booked for Tier 1; attendance alone for Tier 2).
- **Compare to non-target attendees** — separate engagement metrics for target-account attendees vs general attendees. Often the program optimizes for general count when the actual goal is target account depth.
- **Per-persona engagement** — track whether multiple personas from the same account attended (the C-suite + VP combination is often a stronger signal than two ICs).

---

## Workflow 6: Webinar funnel deep dive

**When to use:** the user runs webinars regularly and wants a detailed performance review — not just registration cost but the full funnel through attendance, engagement, and downstream behavior.

**Platforms typically involved:** webinar platform (Zoom, ON24, Webex, GoToWebinar — usually outside Supermetrics, so the user provides the attendance data) + form platform (HubSpot Marketing Forms or similar) + CRM for downstream tracking + ad platforms for promotion attribution.

### Step 1 — Pull the full funnel
> For [webinar], gather: total registrations by source, attendees (live and on-demand), average watch time, poll/Q&A participation rate, post-webinar email engagement, and MQLs created within 30 days of attendance.

### Step 2 — Cohort by registration source
Use `scripts/webinar_funnel.py`. The script breaks out funnel performance by registration source (LinkedIn Ads, Google Ads, Email, Organic, Partner referral, etc.):
- Registration count
- Attendance rate (live)
- On-demand attendance rate (post-event watch)
- Engagement rate (Q&A participation, poll responses)
- MQL conversion rate
- Cost per MQL via webinar (where promotion cost is allocable)

### Step 3 — Visualize where each source drops off
The question the chart needs to answer: **which registration sources produce the highest-quality webinar audience, not just the cheapest registrations?**

A horizontal grouped bar chart per source, with bars for each funnel stage (register, attend live, attend total, engage, MQL), colored consistently. Surfaces patterns like "LinkedIn Ads registers fewer but attends at 2x the rate" or "Email registers most but engages least."

### Step 4 — Build the summary
Use `assets/webinar_funnel_summary.md`. The most-useful content is the source-level cost-per-MQL comparison and the engagement-rate breakdown.

### Common variations
- **Live vs on-demand split** — many webinars deliver more value on-demand than live. Surface the on-demand performance separately; it's often the dominant funnel.
- **Speaker analysis** — if the user runs multiple webinars with different speakers, compare attendance and engagement by speaker. Some speakers consistently drive better outcomes.
- **Topic clustering** — if the user has run 5+ webinars in a quarter, cluster by topic to see which themes drive engagement.

---

## Workflow 7: Partner / co-marketing event ROI

**When to use:** the user runs events with sponsorship partners or co-marketing partners (e.g. a joint webinar with a complementary vendor, a sponsored conference appearance). The ROI math is different because costs and audience reach are shared.

**Platforms typically involved:** ad platforms + event platform / form platform + CRM for pipeline. Partner-shared metrics may need to come from the partner directly.

### Step 1 — Define the shared and unshared costs
Ask the user (via `ask_user_input_v0` if needed):
- Sponsorship fee or co-marketing commitment ($)
- The user's own promotion spend on top of the sponsorship
- Estimated value of the partner's promotion reach (use only if partner shared the number)
- The user's production/staff costs

### Step 2 — Pull attribution data
> Pull registrations and form fills tagged with the [partner event] campaign source. From the CRM, pull MQLs and opportunities created from these contacts.

### Step 3 — Compute partner-specific ROI
Use `scripts/partner_event_roi.py`. The script computes:
- Total cost (the user's investment, not shared cost)
- Net-new contacts acquired (not previously in CRM)
- Cost per net-new contact
- Pipeline created within 60 days
- Pipeline ROAS

If the user provided partner-side numbers (registrations from partner's audience, opportunities the partner is tracking), the script can compute "blended" and "user-only" views separately.

### Step 4 — Frame the partner-specific lens
A pure "registrations" view undersells partner events because much of the value is being in front of the partner's audience for brand awareness — hard to measure but real. The visualization should show both:
- The measurable outcomes (registrations, MQLs, pipeline) as bar charts
- The strategic outcomes (audience reach, partner relationship, content reuse) as qualitative notes

The chart on its own won't answer "was the partnership worth it" — the doc has to frame it.

### Step 5 — Build the recap
Use `assets/partner_event_recap.md`. Often shared with the partner as a joint debrief; tone should be collaborative.

### Common variations
- **Sponsored conference** — different shape than joint webinars. Booth traffic, badge scans, on-site meetings booked all matter.
- **Renewal decision** — if the user is deciding whether to renew a sponsorship, the recap doc is the input. Add an explicit renew/decline section with the decision criteria.
- **New partner test** — if this was a first-time partnership, surface what worked operationally (lead handoff, content creation, audience access) in addition to numbers. Often the operational fit matters more than the first-event numbers.

---

## Ad hoc analysis

For one-off questions outside these seven workflows ("which job titles registered through which channel?", "what's the no-show rate by referring source?", "did social shares correlate with registration spikes?"), write fresh analysis code. The "Choosing the right visualization" framework in the SKILL.md tells you which chart family fits.

---

## A note on the field marketing audience

Field marketers communicate sideways — to regional sales reps, local partners, event ops — more than upward to leadership. The tone is faster and less formal than what marketing leadership produces. Match that tone: short, specific, no preamble. A "regional team update" is closer to a Slack message than a memo, even when delivered as email.
