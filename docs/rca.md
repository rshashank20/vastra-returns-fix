# Root-Cause Analysis — The Returns Fix (Vastra)

Two threads, one conclusion. Every claim below traces to a Phase 1/2 query;
file references are given so any step can be re-run.

---

## Thread 1 — Cost: the policy problem is a SEGMENTATION problem

**Observation.** Returns cost ₹18.16 cr/yr at ₹511 apiece — 5.8× the ₹88
reverse-shipping figure leadership was using. (`sql/01`)

**Why?** Triangulating customer claims × QC findings × ordering patterns
(`sql/03`):
- Only ~26% of returns are genuine quality failures or real transit damage —
  but at ~₹1,195 each they consume **~62% of the money**.
- 47.6% are fit/remorse at ₹258 each — high volume, cheap per unit.
- 10.2% are **fake damage claims** (claimed "damaged", QC found resellable) —
  customers gaming free pickup.
- 8.0% is bracketing — 13,535 customers buying 3 sizes, keeping 1 (`sql/04`).

**Why does that matter?** The top 20% of customers drive 49.9% of the cost
(`sql/05`), and return rates are flat across acquisition channels (`sql/08`) —
marketing is not buying this problem. A blanket fee punishes the 94% of
customers who behave normally for the sins of ~6% who game the system.

**Root cause (cost thread).** There is no single "returns problem". There are
four: (a) quality failures concentrated in a few Dress SKUs at 40–47% return
rates (`sql/06` — a sourcing/product problem); (b) bracketing by a small,
identifiable segment (a policy problem); (c) fake damage claims enabled by a
pickup-pricing loophole (a process-design problem); (d) fit/remorse volume
(a product-information problem). **One blanket policy cannot fix four
different problems — hence segmentation.**

## Thread 2 — Process: the problem is BATCHING + missing SLAs, not headcount

**Observation.** Refunds take ~10.2 days initiated→refund_issued; 56.8% breach
the 14-day SLA. (`sql/09`, refunds)

**Why? 5 Whys on the breach driver** (`sql/10`):
1. Why do refunds breach? QC stage takes 5.1 days on breached refunds vs 2.9 on clean ones — the largest stage gap.
2. Why is QC slow? `qc_done` timestamps cluster on Mondays — QC runs as a weekly batch.
3. Why does batching hurt? Arrivals ≈ completions on average, yet a permanent standing backlog of 1,500–2,300 units exists (`sql/12`) — batching guarantees a queue even at adequate staffing.
4. Why do pickups add delay? No pickup SLA in courier contracts; XpressBees fails 17.8% of pickups vs 10.3% for Delhivery (`sql/13`), and geography is irrelevant — it's vendor performance.
5. Why does slowness cost more than time? Breached refunds generate 14.0 WISMO tickets/100 vs 4.4 clean — 3.2× (`sql/11`); 5,180 agent-hours (₹12.43L/yr) burn on "where is my refund".

**Root cause (process thread).** Weekly-batch QC scheduling + absent courier
handoff SLAs. Not headcount: the backlog math proves staffing is adequate for
a daily cadence.

## The combined conclusion

You cannot fix the cost without fixing the process, and you cannot justify
the process rebuild without the cost quantification:

- **Slow refunds suppress exchanges** — the margin-saving path. Only 6.3% of
  returns are followed by a reorder within 14 days (`sql/07`, directional
  proxy); nobody waits two weeks for an exchange. Exchange-first policy is
  worthless on top of a 10-day process.
- **The fee that fixes bracketing needs the system to enforce it** — a
  "fee from 2nd return/quarter" rule requires the rules engine in the BRD;
  without it, the segmented policy is a slide, not a control.
- **The process fix needs the cost case to get funded** — daily-flow QC costs
  ₹9.5L in Year 1; it pays back in ~10 months on WISMO + holding savings
  alone (`excel/capacity_model.xlsx`), but nobody funds "faster refunds"
  without the ₹18.16 cr context.

**Therefore:** one program, two workstreams — (1) segmented policy
(exchange-first + fee from 2nd return/quarter + instant refunds for high-trust),
(2) process rebuild (daily-flow QC, courier pickup SLAs, auto-refund rules,
proactive delay notifications) — quantified at **₹3.48 cr/yr net**
(`excel/policy_scenarios.xlsx`, modeled), payback under a month
(`excel/business_case.xlsx`, modeled).
