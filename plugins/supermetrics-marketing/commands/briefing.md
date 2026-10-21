---
description: Cross-channel weekly briefing — the one thing to fix this week, what's working, and what to ignore
argument-hint: "[focus, optional]"
---

Produce a weekly cross-channel briefing for: $ARGUMENTS (default: everything connected, last 7 days vs the previous 7). Load targets and known context with `manage_business_context` first.

Pull each connected area separately: paid ads, GA4, Search Console, and store or CRM if connected. Then look for connections a single-channel report misses:
- CPA falling while order value, lead quality or retention falls, meaning cheaper but worse customers
- paid search spend on queries where the site already ranks in the top 3 organically (Search Console)
- platform-reported conversions rising while backend orders or deals stay flat, meaning a tracking issue that outranks everything else
- a channel's share of spend rising faster than its share of conversions

Output:
1. **The one priority this week:** the single highest-impact action, its expected effect, and the evidence behind it.
2. **What's working:** two or three items to protect or scale.
3. **What to ignore this week:** movements that look alarming but are noise, known context or under 10 conversions.
4. A compact chart of spend and conversions by channel.

End with "How I got this", one line per data pull.
