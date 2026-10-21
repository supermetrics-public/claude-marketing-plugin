# Supermetrics for Claude: marketing data and analytics workflows

**Ask Claude about your marketing performance, act on it, and share it.** This plugin connects Claude to Google Ads, Meta Ads, GA4, LinkedIn Ads, TikTok Ads, Microsoft Ads, Shopify, HubSpot and 150+ other marketing platforms through [Supermetrics](https://supermetrics.com). It adds 42 analysis workflows built by marketers, campaign management on seven ad platforms, and live Supermetrics Studio dashboards you can share.

The Supermetrics connector is included: install the plugin, sign in once, and start asking.

## Install

```
/plugin marketplace add supermetrics-public/claude-marketing-plugin
/plugin install supermetrics-marketing@supermetrics
```

On Claude Code 2.1.275 or later you can do both in one step: `/plugin install supermetrics-marketing --marketplace supermetrics-public/claude-marketing-plugin`.

Then run `/supermetrics-marketing:setup`. It signs you in to Supermetrics with OAuth (new users get an account with a 14-day free trial, no credit card needed), shows which platforms are connected, helps you connect one, and runs your first report.

> Using claude.ai or the Claude desktop app's chat? Add the [Supermetrics connector](https://claude.ai/directory/cc599e7b-8c59-4e89-9bf0-36d47bb9ec80) from the connector directory.

## Try asking

- "Compare last week's Facebook Ads performance to the week before. What changed and why?"
- "Which Google Ads search terms spent money last month without converting?"
- "Are we on track to hit this month's paid media budget?"
- "Which of our Meta ads are fatiguing and need new creative?"
- "Rank our channels by ROAS for the last 90 days and recommend where to move budget."
- "Our ad platforms report 400 conversions but GA4 shows 250. Where's the gap?"
- "Build a 90-day marketing performance overview for our leadership deck."
- "Did our San Francisco event lift branded search and traffic in the Bay Area?"
- "Which landing pages get traffic but don't convert?"
- "What's our blended ROAS by day of week across Google and Meta?"
- "Which of my clients need attention this week?"
- "Launch a paused Google Ads search campaign for our spring sale with a 50 EUR daily budget."
- "Pause the ads with CPA over 2x target after showing me the list."
- "Turn this weekly report into a live Studio dashboard I can share with my client."

## Slash commands

| Command | What it does |
|---|---|
| `/supermetrics-marketing:setup` | Sign in, check connected platforms, connect one, run a first report |
| `/supermetrics-marketing:set-targets` | Save your KPIs, targets, budgets and known context; every analysis then uses them |
| `/supermetrics-marketing:daily-check` | Morning check: yesterday vs the 7-day average, pacing, tracking breaks. Can be scheduled |
| `/supermetrics-marketing:briefing` | Weekly cross-channel briefing: the one priority, what's working, what to ignore |
| `/supermetrics-marketing:weekly-performance` | Week-over-week review with prioritised actions |
| `/supermetrics-marketing:wasted-spend` | Non-converting campaigns, search terms, products and regions, with the estimated saving |
| `/supermetrics-marketing:ad-fatigue` | Ads with rising frequency and falling CTR |
| `/supermetrics-marketing:budget-pacing` | Month-to-date pacing and a month-end forecast per channel |
| `/supermetrics-marketing:roas-report` | Blended and per-channel ROAS with day-of-week patterns |
| `/supermetrics-marketing:tracking-check` | Can you trust your conversions? Ad platforms vs GA4 vs store or CRM, plus UTM checks |
| `/supermetrics-marketing:funnel-audit` | Reconcile what ad platforms report with what GA4 saw |
| `/supermetrics-marketing:launch-check` | Pre-launch QA: UTMs, landing page speed, redirects, copy length limits |
| `/supermetrics-marketing:exec-summary` | 90-day cross-channel overview, ready for a deck |
| `/supermetrics-marketing:share-dashboard` | Turn an analysis into a live Supermetrics Studio dashboard link |
| `/supermetrics-marketing:launch-campaign` | Plan and launch a paused campaign on Google, Meta, Microsoft, TikTok or LinkedIn, with your approval at each step |

**Managing several clients?** Ask "how are all my accounts doing?" The portfolio analyst sweeps every connected account and returns one table with the accounts that need attention listed first.

**It remembers your goals.** Targets and context you save, such as "PMax is paused on purpose", are stored with your Supermetrics team. Every teammate's analysis uses them, in Claude or any other AI assistant connected to Supermetrics.

You don't need to remember any of these. Describe what you want and Claude picks the right workflow.

## Workflows by role

| Skill | For | Workflows |
|---|---|---|
| `performance-marketer` | Paid media managers | WoW optimization · Ad fatigue · Creative testing · Daily standup · Search terms / negatives · Attribution comparison · Budget reallocation |
| `marketing-leader` | CMOs, heads of marketing, analysts | 90-day exec overview · Budget pacing · ROAS benchmarking · Annual planning · New channel case · Efficiency vs goals · CAC and LTV |
| `demand-gen` | B2B demand gen | Traffic-to-conversion audit · Lead-gen efficiency · Pipeline by channel · MQL-to-SQL · ABM · Email + ads funnel · Webinar funnel |
| `content-marketer` | Content and SEO | Landing page diagnosis · Paid promotion · SEO audit · Content attribution · Newsletter · Video · Content gaps |
| `field-marketer` | Events and field | Pre-event ROI · Post-event geo-lift · Event portfolio · Event pipeline · Account engagement · Webinar deep dive · Partner events |
| `ecommerce-marketer` | Ecommerce acquisition | Blended ROAS · Promo anomalies · SKU performance · New vs returning ROAS · AOV and basket · Retention cohorts · Promo planning |

Four more skills work alongside these:

| Skill | What it does |
|---|---|
| `campaign-management` | Create and edit campaigns, budgets, bids, targeting and ads on Google Ads, Meta Ads, Microsoft Advertising, TikTok Ads, LinkedIn Ads, Snapchat and ChatGPT Ads |
| `studio-dashboards` | Publish any analysis as a live Supermetrics Studio dashboard that updates itself |
| `business-profile` | Saves your targets, budgets and known context, and applies them to every analysis |
| `get-started` | First-run sign-in, connecting a platform and a first report |

Each workflow pulls data first and then analyzes it. Results come back as charts that colour each change by whether it's good or bad for the business. You can also get a Word doc, spreadsheet or deck when you need something to share.

## Supported platforms

**Paid media:** Google Ads, Meta Ads (Facebook and Instagram), LinkedIn Ads, TikTok Ads, Microsoft Advertising, Amazon Ads, Snapchat, Pinterest, Reddit, X Ads, ChatGPT Ads, DV360, Criteo and more.
**Analytics and SEO:** Google Analytics 4, Search Console, Adobe Analytics, Semrush, YouTube.
**Social:** Facebook and Instagram insights, LinkedIn Pages, TikTok organic.
**Ecommerce and CRM:** Shopify, HubSpot, Salesforce, Klaviyo, Mailchimp.

[See all 150+ sources →](https://supermetrics.com/connectors)

## Privacy and safety

- **Analysis only recommends.** Reports, audits and checks never change campaigns, budgets or settings in your ad accounts.
- **Campaign changes happen only when you ask.** Claude shows the exact change and waits for your approval. Writes work only on ad accounts where the person who connected them has turned writes on in the [Supermetrics Hub](https://hub.supermetrics.com/write-settings), where they can also require a separate sign-off before budget changes or campaigns going live. New campaigns are always created paused, and every change is logged in [campaign history](https://hub.supermetrics.com/campaign-history).
- **Your data goes only to Supermetrics and your Claude session.** Supermetrics fetches it with your own platform logins, and the plugin adds no telemetry or hooks.
- **You choose what's connected.** Remove a platform connection at any time on the [Data sources page](https://hub.supermetrics.com/token-management) of the Supermetrics Hub.

See the [privacy policy](https://supermetrics.com/privacy-policy) and [terms](https://supermetrics.com/terms-of-service).

## Pricing

Supermetrics is a paid product. Signing in for the first time creates an account with a 14-day free trial, no credit card needed. To keep using Supermetrics in Claude afterwards, your subscription needs the AI Chats destination. See [pricing](https://supermetrics.com/pricing).

## Support

- Plugin issues: [open an issue](https://github.com/supermetrics-public/claude-marketing-plugin/issues)
- Account, connector or data questions: [Supermetrics support](https://supermetrics.com/support), or ask Claude to "contact Supermetrics support".

## For contributors

Test locally without installing:

```
claude --plugin-dir ./plugins/supermetrics-marketing
```

Each skill has the same layout: a `SKILL.md` (when to trigger, principles, chart framework), `references/workflows.md` (step-by-step prompts), `scripts/` (Python helpers that take a CSV and return a table) and `assets/` (deliverable templates). Slash commands are in `commands/`, agents in `agents/`, and the bundled connector is defined in `.mcp.json`.

Run `claude plugin validate --strict .` before opening a PR. CI runs it too.

## License

MIT
