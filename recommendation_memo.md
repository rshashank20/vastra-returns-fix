# RECOMMENDATION — Vastra Returns Redesign

**To:** CFO, CX Head, Warehouse Ops, Product · **From:** Business Analyst · **Date:** 2026-10-08

## Decision

Adopt a **segmented returns policy** and rebuild the returns flow to enforce it:

1. **Exchange-first** as the default return path. An estimated 25% of fit/remorse returns become retained sales instead of refunds.
2. **₹49 fee from the 2nd return in a calendar quarter.** This targets the ~6% of customers who bracket sizes and game damage claims. Genuine quality and damage returns stay free, always.
3. **Instant refunds for high-trust customers** (score ≥ 80), with caps and velocity checks.
4. **Fix the process:** QC moves from a Monday batch to daily flow. 24-hour courier pickup SLA with a ₹50 penalty per failed pickup above 10%. Proactive delay notifications so customers stop asking where their refund is.

## The math (modeled, assumptions in `excel/`)

| | ₹/yr |
|---|---|
| Fee revenue (targeted, not blanket) | +₹29L |
| Deterred gaming (bracketing down ~50%, fake claims down ~60%) | +₹104L |
| Exchange margin retained | +₹236L |
| Conversion loss (fee touches 6% of customers, not 100%) | −₹6L |
| Abuse provision | −₹15L |
| **Net** | **+₹3.48 cr/yr** |

Flat-fee alternatives net less (₹2.2–3.2cr) at much higher CX risk. They punish
every customer for the behavior of 6%. The rebuild costs **₹6.5L one-time**
(3 eng-months + 1 PM-month), so payback is **under one month**. The QC
daily-flow change pays for itself in ~10 months on ticket and holding
savings alone.

## Why this, why now

Returns cost **₹511 each, not ₹88**. That's ₹18.2cr a year, the single
biggest margin lever in the P&L. Only 26% of returns are genuine
quality or damage, yet they consume 62% of the money. The rest is fit
issues, bracketing, and fake damage claims. Four different problems,
so one blanket policy can't fix them.

Meanwhile refunds take 10+ days because QC works in a weekly batch, and
every late refund creates 3.2x the support tickets. Cost and process have
to be fixed together: slow refunds kill exchanges, and exchanges are the
path that saves the margin.

## Ask

1. **Approve** the segmented policy and BRD v1.0.
2. **Fund** the ₹6.5L rebuild, plus a 30-day QC daily-flow pilot at one warehouse to burn down the backlog.
