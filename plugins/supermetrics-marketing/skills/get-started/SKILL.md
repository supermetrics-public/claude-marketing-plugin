---
name: get-started
description: First-run onboarding for the Supermetrics connector. Use when the user has just installed the plugin, asks how to get started, wants to connect Google Ads / Meta / GA4 / LinkedIn or another marketing platform, asks what data they can access, or when a Supermetrics tool call fails because they aren't signed in or a data source isn't connected.
---

# Get started with Supermetrics

Take the user from install to their first real answer in as few turns as possible. Do each step only if the previous one succeeded.

## 1. Check sign-in

Call `manage_user_and_team` with `action: get_info`.

- **Tool not available or auth error:** the bundled `supermetrics` connector isn't signed in. Tell the user:
  > Run `/mcp`, select **plugin:supermetrics-marketing:supermetrics** and sign in with your Supermetrics account. No account? Signing in creates one with a 14-day free trial, no credit card needed.
  >
  > In claude.ai chat, add the connector from https://claude.ai/directory/cc599e7b-8c59-4e89-9bf0-36d47bb9ec80 instead.

  Then stop and wait for them. Never ask for an API key or password in chat.
- **Signed in, but `license` holds an error, or a tool returns a license or trial error:** don't loop on sign-in. Say so plainly and follow the note in the response; buying is at https://supermetrics.com/pricing, and the plan must include the AI Chats destination. For details, call `supermetrics_guide` with `mode: license_and_trials`.
- **Success:** greet them by name and team in one line.

## 2. See what's connected

Call `data_source_discovery` with `compress: true`; each source's `authentication_status` shows what's connected. Then call `accounts_discovery` for the connected platforms the user cares about. Summarise in one short list: connected platforms and account counts. Don't dump every source.

If nothing relevant is connected, ask which platform they want first (Google Ads, Meta Ads, GA4, LinkedIn Ads, TikTok Ads, Microsoft Ads, Shopify, HubSpot…) and call `manage_user_and_team` with `action: login_data_source` and its `ds_id`. Give them the login link and wait. Never describe clicking through menus; hand over the link. For platform-specific connection help, call `supermetrics_guide` with `mode: connect_data_source`.

## 3. First answer

Once at least one account is connected, run one small useful report straight away — last 7 days vs the previous 7 for spend, clicks, conversions and cost per conversion (or sessions and conversions for GA4) — and show it as a compact chart or table.

## 4. Save their goals

Ask what they're optimizing for (target CPA, ROAS or monthly budget). Save it with the `business-profile` skill so later analyses judge results against it. Skip this if a profile already exists.

## 5. Point to what's next

Suggest three questions tailored to what they connected. Mention `/supermetrics-marketing:daily-check` (which can be scheduled), `/supermetrics-marketing:wasted-spend` and `/supermetrics-marketing:briefing`. If they manage several clients, mention the portfolio analyst ("how are all my accounts doing?"). Also say Claude can launch and edit campaigns with their approval (`/supermetrics-marketing:launch-campaign`) and publish any analysis as a live Studio dashboard (`/supermetrics-marketing:share-dashboard`).
