# Assumptions Log + Stakeholder Pushback Appendix

## Assumptions log
Every unvalidated item is marked as such, with the owner who must validate it
and what breaks if it's wrong.

| ID | Assumption | Status | Validate with | If wrong |
|----|------------|--------|---------------|----------|
| A-GM1 | Gross margin 35% (→ ₹630/order) | UNVALIDATED | Finance controller | Policy-model net scales linearly — re-run model |
| A-ELAS | Demand elasticity −0.3 (sensitivity −0.1…−0.5) | UNVALIDATED | Marketing + past promo data | Conversion-loss estimate moves; sensitivity grid covers it |
| A-DET | Fee deters 50% bracketing / 60% fake claims @₹49 | UNVALIDATED | Pilot: A/B fee on 5% traffic | Deterrence is the highest-leverage unknown — pilot before full rollout |
| A-EXCH | 25% of fit/remorse → exchange under exchange-first | UNVALIDATED | Product: prototype test | Exchange upside is the biggest modeled number — validate early |
| A-ABUSE | Instant-refund abuse provision ₹15L/yr (≤2% abuse) | UNVALIDATED | Risk/finance: velocity rules | Tighten trust-score gate if exceeded |
| A-QC | QC throughput 60 units/agent/day | UNVALIDATED | Warehouse ops time study | Backlog burn-down timeline shifts |
| A-ATTR | 65% of policy upside needs the system rebuild | UNVALIDATED | Eng: scope review | Business-case payback moves (still <2 mo at 40%) |
| A-SEGN | ~95K returns/yr are 2nd+ in quarter | UNVALIDATED | Recompute quarterly from live data | Fee-revenue line moves ±20% |
| A-SLA | QC fix cuts breach 56.8% → 30% | UNVALIDATED | Pilot daily flow at 1 warehouse | WISMO savings scale with actual breach reduction |

**Calculated (not assumed):** ₹511 cost/return, ₹18.16 cr/yr, 56.8% breach,
triangulation splits, concentration curve, journey stage times, courier fail
rates — all from `sql/00–13` on the synthetic dataset.

## Appendix: stakeholder pushback — worked example

**Requirement under challenge:** FR-01 auto-refund rules engine (instant refunds
for high-trust customers, no manual review).

**Finance objection:** *"Auto-approval will increase fraudulent refunds.
A customer could claim damage, get an instant refund, and keep the item.
We're writing blank cheques to anyone with a good history."*

**Analyst response (documented mitigation):**
1. **Caps:** instant refunds only for item value ≤ ₹2,000 (RULE-02) — worst-case exposure per incident is bounded.
2. **Trust gate:** trust_score ≥ 80 AND zero fee history — the segment with the lowest observed abuse in the data (top trust decile).
3. **Velocity checks:** >2 instant refunds in 30 days auto-routes to manual review, whatever the score.
4. **QC backstop:** the refund is *initiated* instantly but reconciled at QC — if QC finds no item received, the next order is held and the case goes to risk review.
5. **Provisioned cost:** ₹15L/yr abuse provision (A-ABUSE) is already inside the segmented policy's net — the recommendation survives 2% abuse.

**Outcome if objection stands:** fall back to "initiate on pickup scan, credit on QC" (24–48h, still 3× faster than today) — 80% of the WISMO benefit, ~0% of the fraud surface. The program does not depend on winning this argument.
