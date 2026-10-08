# Business Requirements Document — Returns Module Rebuild (Vastra)
**Version:** 1.0 · **Date:** 2026-10-08 · **Author:** Business Analyst (self-directed project)
**Status:** Draft for stakeholder review

> Data honesty: all quantitative claims derive from the synthetic Vastra dataset
> (see `data/DATA_DICTIONARY.md`). Assumption IDs (A-xxx) are logged in
> `docs/assumptions.md`; every requirement traces to a Phase 1/2 finding.

## 1. Purpose
Rebuild the returns flow in the new order-management system so that (a) the
segmented returns policy can actually be enforced by software, not slides, and
(b) refund SLAs are met through designed SLAs and automation instead of
manual chasing.

## 2. Business objectives (measurable)
| ID | Objective | Baseline → Target | Source |
|----|-----------|-------------------|--------|
| BO-1 | Reduce fully-loaded cost per return | ₹511 → ≤ ₹430 | sql/01 |
| BO-2 | Cut SLA breach rate (14-day) | 56.8% → ≤ 30% | refunds |
| BO-3 | Cut WISMO tickets per 100 returns | 14.0 (breached) → ≤ 7 | sql/11 |
| BO-4 | Lift exchange share of returns | ~6% → ≥ 20% | sql/07 proxy |
| BO-5 | Eliminate QC standing backlog | 1,500–2,300 units → ~0 | sql/12 |

## 3. Scope
**In:** returns initiation → pickup → QC → refund/exchange decision → payout;
fee engine; auto-refund rules; proactive notifications; courier SLA tracking;
QC prioritization queue.
**Out:** forward-logistics changes; product quality fixes at sourcing (separate
program, fed by the toxic-SKU list); payment-gateway renegotiation.

## 4. Business requirements (testable)
| ID | Requirement | Traces to | Acceptance |
|----|-------------|-----------|------------|
| BR-01 | Refunds shall credit within 5 days of QC completion for ≥ 95% of returns | BO-2; sql/10 (QC is the breach driver) | Measured over trailing 30 days |
| BR-02 | Overall return-to-credit SLA shall be ≤ 14 days for ≥ 70% of returns (from 43.2%) | BO-2 | Monthly SLA report |
| BR-03 | A ₹49 fee shall apply automatically from the customer's 2nd return in a calendar quarter | BO-1; sql/04 (13,535 bracketeers) | Fee engine log audit: 100% of qualifying returns charged |
| BR-04 | Genuine quality/damage returns (QC-confirmed) shall NEVER attract a fee | BO-1; fairness guardrail | Zero fee lines on QC=damaged/defective returns |
| BR-05 | Exchange shall be offered before refund at initiation, with instant exchange confirmation | BO-4; sql/07 | ≥ 20% exchange uptake within 90 days |
| BR-06 | High-trust customers (trust_score ≥ 80, no fee history) get instant refunds on initiation | BO-3; abuse provision ₹15L/yr (A-ABUSE) | Abuse rate ≤ 2% of instant refunds |
| BR-07 | Every journey stage shall carry a contractual/internal SLA with an owner | BO-2; sql/09/13 | SLA register published; breaches auto-escalated |
| BR-08 | QC shall run as daily flow, not weekly batch | BO-5; sql/12 | Standing backlog = 0 for 30 consecutive days |
| BR-09 | Courier pickup SLA (24h) with ₹50 penalty per excess failed pickup over 10% fail rate | sql/13 (17.8% vs 10.3%) | Quarterly courier scorecard |
| BR-10 | Customers shall receive proactive delay notifications before they need to ask | BO-3 | WISMO/100 ≤ 7 |

## 5. Functional requirements
| ID | Requirement | Traces to |
|----|-------------|-----------|
| FR-01 | **Auto-refund rules engine:** evaluate (trust_score, item value, QC result, fee history) → auto-approve refund OR route to manual review | BR-01, BR-06 |
| FR-02 | **Bracketeer fee engine:** count returns/customer/quarter in real time; auto-apply ₹49 from 2nd return; exempt QC-confirmed damage/defect | BR-03, BR-04 |
| FR-03 | **Exchange-first checkout:** at return initiation, present exchange (same SKU, different size) as the default path with instant confirmation | BR-05 |
| FR-04 | **Proactive notification triggers:** on pickup delay > 48h, QC wait > 72h, or projected SLA breach → SMS/WhatsApp to customer + CX dashboard flag | BR-10 |
| FR-05 | **QC prioritization queue:** order QC work by (breach-risk × item value), not FIFO-by-arrival | BR-01, BR-08 |
| FR-06 | **Pickup SLA tracking:** per-courier pickup attempt log; auto-flag fail-rate > 10% weekly | BR-09 |
| FR-07 | **Journey audit trail:** immutable timestamp per stage per return (fixes the 30% missing-scan gap by contract, not hope) | BR-07; data-quality finding |
| FR-08 | **Fee transparency:** show applicable fee BEFORE the customer confirms the return, with the reason ("3rd return this quarter") | BR-03; backlash mitigation |

## 6. Non-functional requirements
| ID | Requirement |
|----|-------------|
| NFR-01 | Every journey-stage event persisted with server timestamp; no nullable timestamps on courier handoff (contractual scan requirement) |
| NFR-02 | Pincode-level pickup SLA tracking (courier × pincode × week) |
| NFR-03 | Fee-engine decisions explainable per return (rule ID logged) for dispute handling |
| NFR-04 | Refund/payout idempotency: duplicate return requests (app retries, ~0.4%) must never double-pay |
| NFR-05 | Dashboards refresh daily; SLA breach alerts within 1 hour of breach |

## 7. Business rules catalogue
| ID | Rule |
|----|------|
| RULE-01 | IF returns_this_quarter ≥ 2 AND qc_result NOT IN ('damaged','defective') THEN fee = ₹49 |
| RULE-02 | IF trust_score ≥ 80 AND item_value ≤ ₹2,000 AND no fee history THEN instant refund on initiation |
| RULE-03 | IF qc_result IN ('damaged','defective') THEN fee = ₹0 AND route to sourcing-quality review |
| RULE-04 | IF pickup_attempts ≥ 3 THEN escalate to CX + offer customer self-drop option |
| RULE-05 | IF projected_credit_date > SLA THEN notify customer proactively AND flag CX dashboard |
| RULE-06 | IF courier weekly fail-rate > 10% THEN raise contract-penalty claim |

## 8. Assumptions & dependencies
See `docs/assumptions.md` (A-xxx log). Key dependencies: courier contract
renegotiation (external), warehouse ops roster change for daily QC, payment
gateway support for instant refunds.

## 9. Acceptance criteria (program)
1. Policy model reconciles to finance's margin within 2% on baseline inputs.
2. Every TO-BE step traces to a bottleneck found in journey data (`docs/rca.md`) — no invented steps.
3. UAT cases in `docs/uat.md` all pass; BR-01…BR-10 measurable in production dashboards.

## 10. Version history
| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-10-08 | Initial draft from Phase 1–3 findings |
| 1.0 | 2026-10-08 | Draft issued for stakeholder review |
