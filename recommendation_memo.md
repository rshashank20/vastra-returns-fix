# RECOMMENDATION — Vastra Returns Redesign

**To:** CFO, CX Head, Warehouse Ops, Product · **From:** Business Analyst · **Date:** 2026-10-08

## Decision
Adopt the **segmented returns policy** and rebuild the returns flow to enforce it:

1. **Exchange-first** as the default return path (instant confirmation) — converts an estimated 25% of fit/remorse returns into retained sales.
2. **₹49 fee from the 2nd return in a calendar quarter** — targets the ~6% of customers who bracket and game damage claims; genuine quality/damage returns stay free, always.
3. **Instant refunds for high-trust customers** (score ≥ 80) — with caps and velocity checks.
4. **Process fixes:** QC moves from Monday-batch to daily flow; 24h courier pickup SLA with ₹50 penalty per excess failed pickup over 10%; proactive delay notifications.

## Math (modeled, assumptions documented in `excel/`)
| | ₹/yr |
|---|---|
| Fee revenue (targeted, not blanket) | +₹29L |
| Deterred gaming (bracketing ↓50%, fake claims ↓60%) | +₹104L |
| Exchange margin retained (42K conversions × ₹558) | +₹236L |
| Conversion loss (fee touches 6% of customers only) | −₹6L |
| Abuse provision | −₹15L |
| **NET** | **+₹3.48 cr/yr** |

Flat-fee alternatives net less (₹2.2–3.2 cr) at far higher CX risk — they punish 100% of customers for the behaviour of 6%. The rebuild costs **₹6.5L one-time** (3 eng-months + 1 PM-month); payback is **under one month**. QC daily-flow pays back in ~10 months on WISMO + holding savings alone.

## Why this, why now
Returns cost **₹511 each, not ₹88** — ₹18.2 cr/yr, the largest margin lever in the P&L. Only 26% are genuine quality/damage (but eat 62% of the money); the rest is fit/remorse, bracketing, and fake damage claims — four different problems that one blanket policy cannot fix. Meanwhile refunds take 10+ days because QC batches weekly, and every breach generates 3.2× the support tickets. Cost and process must be fixed together: slow refunds kill exchanges, which are the margin-saving path.

## Ask
1. **Approve** the segmented policy and BRD v1.0 (attached).
2. **Fund** the ₹6.5L rebuild + QC daily-flow pilot at one warehouse (30-day backlog burn-down).
3. **Authorize** courier SLA renegotiation (10% fail-rate threshold, penalty terms).
4. **Pilot** the fee on 5% traffic to validate deterrence assumptions before full rollout.

*All figures modeled under stated assumptions (`excel/policy_scenarios.xlsx` →
Assumptions sheet). Nothing presented as measured until the pilot reads out.*
