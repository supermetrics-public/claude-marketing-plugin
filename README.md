# Supermetrics for Claude — Marketplace

A Claude Code [plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces) distributing marketing analytics workflows built on top of the [Supermetrics connector for Claude](https://claude.ai/directory/connectors/cc599e7b-8c59-4e89-9bf0-36d47bb9ec80).

## What's in this marketplace

One plugin: **`supermetrics-marketing`**.

It bundles six persona-aligned skill sets totaling **42 workflows**, with **42 helper scripts** and **39 deliverable templates**:

| Skill | Persona | 7 workflows |
|---|---|---|
| `/supermetrics-marketing:performance-marketer` | Performance marketer | WoW optimization · Ad fatigue · Creative testing · Daily standup · Search term audit / negative keywords · Cross-channel attribution comparison · Budget reallocation modeler |
| `/supermetrics-marketing:marketing-leader` | Marketing analytics & leadership | 90-day executive overview · Budget pacing · ROAS benchmarking · Annual planning · New channel investment case · Efficiency vs goals · CAC and LTV unit economics |
| `/supermetrics-marketing:demand-gen` | B2B demand generation | Traffic-to-conversion audit · Lead-gen efficiency · Pipeline contribution by channel · MQL-to-SQL by source · ABM campaign performance · Email + ads integrated funnel · Webinar / gated content funnel |
| `/supermetrics-marketing:content-marketer` | Content marketing | Landing page diagnosis · Paid promotion analysis · Organic / SEO audit · Content-to-conversion attribution · Newsletter performance · Video content performance · Content gap analysis |
| `/supermetrics-marketing:field-marketer` | Field & event marketing | Pre-event channel ROI · Post-event geo-lift · Multi-event portfolio · Event-driven pipeline · Account engagement scoring · Webinar funnel deep dive · Partner event ROI |
| `/supermetrics-marketing:ecommerce-marketer` | Ecommerce paid acquisition | Blended ROAS + day-of-week · Promotional anomaly detection · SKU-level performance · New vs returning customer ROAS · AOV and basket composition · Subscription retention cohorts · Pre-promo planning model |

Skills are model-invoked — Claude picks them up automatically when the user describes a matching task ("compare last week's Facebook performance to the week before", "did our SF event move the needle locally?", "which landing pages are leaking traffic?"). Users don't need to memorize skill names.

## Install

```
/plugin marketplace add supermetrics-public/claude-marketing-plugin
/plugin install supermetrics-marketing@supermetrics
```

The plugin needs the Supermetrics connector to actually pull data. If it's not already connected, each skill prompts the user to install it from the [connector directory](https://claude.ai/directory/connectors/cc599e7b-8c59-4e89-9bf0-36d47bb9ec80).

## Local testing

Without installing, point Claude Code at the plugin directly:

```
claude --plugin-dir ./plugins/supermetrics-marketing
```

Or test the full marketplace flow against the local repo:

```
/plugin marketplace add ./
/plugin install supermetrics-marketing@supermetrics
```

Then try invoking a skill: `/supermetrics-marketing:performance-marketer` (after which Claude reads the SKILL.md and the user describes their actual question). Most users will never type the skill name — they'll just describe what they want and Claude will load the right skill automatically.

## What's inside each skill

Every skill follows the same shape:

```
skills/<persona>/
├── SKILL.md              # When to trigger, principles, viz framework, capability index
├── references/
│   └── workflows.md      # 7 workflow patterns with full prompt sequences
├── scripts/              # 7 Python helper scripts (CSV in, table out)
└── assets/               # 6–7 markdown templates for the final deliverables
```

The SKILL.md descriptions use natural trigger phrasings — they fire on "my Facebook campaign is underperforming" or "did our SF event move the needle," not just literal mentions of "Supermetrics."

Each SKILL.md contains a **dynamic visualization framework** — a decision table from question type to chart family. Claude reasons about which chart fits the data and the question rather than following a fixed recipe.

When a workflow produces a file, the skill chains to a built-in skill (`pptx` for decks, `docx` for Word docs, `xlsx` for spreadsheets). When other connectors are available (CRM, Gmail, Drive, Slack, Calendar), workflows use them opportunistically — never assumed.

## Standard visualization palette

All charts across all skills use the same palette:

- Green `#10b981` — improving / positive
- Red `#ef4444` — declining / negative
- Indigo `#6366f1` — neutral / baseline
- Amber `#f59e0b` — flagged / warning

Color is applied by business meaning, not by sign. CPC up 20% is red (bad), CPA down 15% is green (good).

## Core principles shared across all skills

1. **Pull, then analyze.** Don't combine data retrieval and complex analysis in one tool call.
2. **Show, don't tell.** When numbers are worth comparing, build a chart, not a table.
3. **One serious query at a time.** Sequence heavy queries rather than batching them.

## Validation

The marketplace catalog and plugin manifest pass `claude plugin validate`. Each skill's `SKILL.md` and bundled scripts have been tested with synthetic data.

## Repository structure

```
.
├── .claude-plugin/
│   └── marketplace.json          # Marketplace catalog
├── plugins/
│   └── supermetrics-marketing/
│       ├── .claude-plugin/
│       │   └── plugin.json       # Plugin manifest
│       └── skills/               # Six persona-aligned skill sets
│           ├── performance-marketer/
│           ├── marketing-leader/
│           ├── demand-gen/
│           ├── content-marketer/
│           ├── field-marketer/
│           └── ecommerce-marketer/
└── README.md
```

## License

MIT.

## Support

Issues with the plugin: file an issue on this repo.
Issues with the Supermetrics connector itself: contact support@supermetrics.com.
