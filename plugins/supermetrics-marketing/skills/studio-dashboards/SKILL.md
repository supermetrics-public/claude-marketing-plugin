---
name: studio-dashboards
description: Turn any analysis into a live, shareable Supermetrics Studio dashboard that re-queries the data on every view. Use when the user wants a dashboard, a report link to share with a client, boss or team, a recurring view they can reopen, or asks "can I share this", "make this live", "build a dashboard", "send this to my client". Also offer it at the end of any multi-chart analysis.
---

# Live dashboards in Supermetrics Studio

A chat chart is a snapshot. A Studio dashboard is a link that always shows current numbers, because it re-queries the user's Supermetrics data each time someone opens it. That makes it the right deliverable for clients, leadership and recurring reviews.

## When to offer it

- The user asks for a dashboard, a shareable report or a link.
- An analysis produced two or more charts the user will want to see again, for example a weekly performance review, budget pacing, an executive overview or a client report.
- An agency user is reporting to a client.

Offer it once, in one line, after showing the analysis: "Want this as a live Studio dashboard you can share? It updates itself."

## How

Use `manage_dashboards` and follow its rules:
1. Show a **static inline preview** first, with the data you already fetched hard-coded, and get the user's OK.
2. Upload the **live version**, which fetches with `smQuery` instead of the hard-coded preview data, then return the share link.
3. To change an existing dashboard, `list` or `get` it first, then `edit` with patches rather than re-uploading.

Keep the plugin's colour meanings: green means improving, red declining, indigo neutral, amber flagged. Title the dashboard after its audience and purpose, for example "Acme — Paid Media Weekly".
