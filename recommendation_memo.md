# Recommendation — Vastra Returns Redesign

**To:** CFO, CX Head, Warehouse Ops, Product  
**From:** Business Analyst  
**Date:** 2026-10-08

## Recommendation

Based on the cost and process analysis, I would not recommend a blanket return fee. The return problem is coming from different customer and operational behaviours, so the policy should be targeted rather than applied to everyone.

I recommend the following changes:

1. **Make exchange-first the default return option** and make the exchange confirmation immediate. The current model assumes that 25% of fit/remorse returns can be converted to exchanges.
2. **Charge ₹49 from the second return in a calendar quarter.** This is intended to address repeat-return and gaming behaviour without making genuine quality or damage returns paid.
3. **Allow instant refunds for high-trust customers** (trust score ≥ 80), subject to item-value caps and velocity checks.
4. **Fix the return process at the same time:** move QC from the current Monday-batch pattern to a daily flow, introduce a 24-hour courier pickup SLA with a ₹50 penalty for excess failed pickups above the 10% threshold, and send proactive notifications when a refund is delayed.

The important point is that the policy and process changes should be treated as one problem. A better policy will not help much if refunds continue to take 10+ days, and faster refunds are less valuable if the underlying return economics are not addressed.

## What the analysis showed

The first number that changed the way I looked at the problem was the fully-loaded return cost. Vastra was using about **₹88 as the perceived cost**, but the analysis puts the fully-loaded cost at about **₹511 per return**, or roughly **₹18.2 crore a year** on the current return volume.

The ₹511 breaks down into:

| Cost component | ₹ per return |
|---|---:|
| Reverse shipping | 88 |
| Wasted forward shipping | 72 |
| QC | 35 |
| Refurbishment | 33 |
| Support tickets | 11 |
| Dead inventory days | 7 |
| Write-offs | 265 |
| **Total** | **511** |

The cost analysis also showed that returns are not one uniform problem. Around **26% were classified as genuine quality/damage-related returns**, but that group accounts for about **62% of the money**. Fit/remorse is a high-volume but lower-cost problem, while bracketing and questionable damage claims are more relevant to policy controls.

There was another useful finding: the **top 20% of customers account for about 50% of return cost**. That is the main reason I would avoid charging every customer the same fee.

## Process problem

The cost analysis alone was not enough. I then looked at the return journey to understand why refunds are taking so long.

The biggest bottleneck is QC. Average QC time is about **4.1 days**, and returns that breach the refund SLA spend about **5.1 days in QC compared with 2.9 days for clean returns**.

The customer impact is visible in support data as well. Clean returns generate about **4.4 WISMO tickets per 100 returns**, compared with **14.0 for breached returns** — around **3.2× higher**. The analysis estimates about **5,180 agent hours and ₹12.4L of support cost** associated with breached returns.

The backlog pattern also suggests that this is not simply a headcount problem. There is a standing QC backlog of roughly **1,500–2,300 units**, with work arriving throughout the week but QC activity clustering around Monday. That points more toward scheduling and flow design than immediately adding staff.

Pickup performance is another issue. **XpressBees shows a 17.8% reattempt rate versus 10.3% for Delhivery**, so the courier SLA should be tightened rather than treating every failed pickup as an internal warehouse issue.

## Economics of the recommended policy

The policy scenarios are modelled in `excel/policy_scenarios.xlsx`. They are not measured business results.

| Modelled impact | ₹ / year |
|---|---:|
| Targeted fee revenue | +29L |
| Reduced gaming / bracketing | +104L |
| Margin retained from exchange conversions | +236L |
| Conversion loss | −6L |
| Abuse provision | −15L |
| **Modelled net benefit** | **+₹3.48 cr** |

The largest number in this model comes from exchange conversion, so I would treat that as the assumption that needs the earliest validation. The current data does not directly measure future exchange behaviour; it is a scenario assumption.

The same applies to the fee-determent and abuse assumptions. I would validate them through a controlled pilot rather than presenting them as proven outcomes.

## What I would approve first

I would start with a **5% traffic pilot** for the targeted fee and the exchange-first flow. At the same time, one warehouse should move to daily QC for 30 days so the process impact can be measured separately from the policy impact.

The pilot should track:

- net margin after returns
- cost per return
- refund median days and SLA attainment
- WISMO tickets per 100 returns
- exchange rate
- repeat purchase after a return
- abuse / exception rate

If the fee creates a larger conversion or CX impact than expected, the fee policy should be adjusted before wider rollout. If daily QC does not reduce breach rates as expected, the process model should be revisited rather than assuming more headcount will solve it.

## Decision requested

1. Approve the **segmented returns policy** and BRD v1.0.
2. Approve the **₹6.5L one-time rebuild estimate** and a 30-day daily-QC pilot at one warehouse.
3. Authorize renegotiation of the **courier pickup SLA** around the 10% failure threshold and penalty terms.
4. Run the **5% pilot** before moving to a full rollout.

## Important assumptions

The recommendation depends on several assumptions that are currently unvalidated, including demand elasticity, fee deterrence, exchange conversion, instant-refund abuse, QC throughput and the share of returns affected by the new policy. These are documented in `docs/assumptions.md` and should be re-run against live data before implementation.

The dataset used for this project is synthetic, so the numbers above are best treated as an analytical demonstration of how I would approach the decision rather than as Vastra's real financial performance.
