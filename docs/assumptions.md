# Assumptions & Validation Notes

Some parts of the recommendation come directly from the analysis. Others are inputs to the policy and process models that I could not validate from the synthetic dataset alone.

I have kept those assumptions separate rather than presenting the model output as a measured business result. Each one has a validation owner and a clear indication of what would change if the assumption turns out to be wrong.

## Assumptions log

| ID | Assumption | Status | How I would validate it | What changes if it is wrong |
|----|------------|--------|-------------------------|------------------------------|
| A-GM1 | Gross margin is 35% (₹630/order) | UNVALIDATED | Confirm with Finance controller | Policy-model net benefit scales with the actual margin, so the model needs to be rerun |
| A-ELAS | Demand elasticity is −0.3, with a sensitivity range of −0.1 to −0.5 | UNVALIDATED | Compare with past promotions and Marketing data | Estimated conversion loss changes; the sensitivity grid shows the range |
| A-DET | A ₹49 fee deters 50% of bracketing and 60% of fake damage claims | UNVALIDATED | Run an A/B test on 5% of traffic | Fee deterrence is one of the biggest unknowns, so the pilot should come before a full rollout |
| A-EXCH | 25% of fit/remorse returns convert to an exchange under exchange-first | UNVALIDATED | Test the flow with Product and measure actual conversion | The exchange benefit is the largest modelled upside, so this assumption needs early validation |
| A-ABUSE | Instant-refund abuse provision is ₹15L/year, assuming abuse stays at or below 2% | UNVALIDATED | Validate with Risk/Finance using velocity and trust-score rules | Tighten the trust-score gate or reduce instant-refund eligibility if abuse is higher |
| A-QC | One QC agent can process 60 units/day | UNVALIDATED | Conduct a warehouse time study | The expected backlog burn-down time changes |
| A-ATTR | 65% of the policy upside requires the system rebuild | UNVALIDATED | Confirm scope and dependencies with Engineering | The business-case payback period changes; it remains below two months at a 40% realization level |
| A-SEGN | About 95K returns/year are a customer's 2nd or later return in a quarter | UNVALIDATED | Recompute the segment using live quarterly return data | Expected fee revenue moves by roughly ±20% |
| A-SLA | Moving QC to daily processing reduces breach rate from 56.8% to 30% | UNVALIDATED | Run a daily-QC pilot at one warehouse | WISMO and refund-SLA savings scale with the actual breach reduction |

### What came directly from the analysis

These are **calculated, not assumed**: ₹511 cost per return, ₹18.16 cr annual return cost, 56.8% breach rate, the return-reason triangulation splits, the customer concentration curve, journey-stage timings, and courier pickup failure rates.

Those figures come from the SQL analyses in `sql/00–13` on the synthetic dataset. They are analytical outputs from the project data, not real Vastra financials.

## Stakeholder pushback: worked example

One requirement I would expect Finance to challenge is **FR-01: the auto-refund rules engine**, which allows instant refunds for high-trust customers without a manual review.

### Likely Finance objection

> "Auto-approval could increase fraudulent refunds. A customer could claim damage, receive the refund immediately, and still keep the item. How do we control that risk?"

I would not dismiss the concern. The better approach is to put limits around the rule and make the risk measurable.

### Controls I would propose

1. **Refund cap:** instant refund applies only to items worth ₹2,000 or less (RULE-02), which limits the maximum exposure per transaction.
2. **Trust gate:** require `trust_score >= 80` and no fee history. This targets the higher-trust segment rather than opening the rule to every customer.
3. **Velocity check:** more than 2 instant refunds in 30 days automatically goes to manual review, regardless of the customer's trust score.
4. **QC backstop:** the refund is initiated immediately, but the return is still reconciled at QC. When the item is not received, the next order is held and the case moves to risk review.
5. **Abuse provision:** the model already includes a ₹15L/year provision for refund abuse (A-ABUSE). If the real rate is above the assumed level, the rule should be tightened before scaling it.

### Fallback option

There is also a lower-risk version of the flow if Finance is not comfortable with instant credit.

Instead of crediting immediately, Vastra can **initiate the refund when the pickup is scanned and credit it after QC**. That should bring the process down to roughly 24–48 hours after pickup while avoiding most of the fraud exposure of a fully instant refund.

The point is not to force one solution through. The process should still deliver a large part of the WISMO benefit even if the most aggressive refund rule is rejected.
