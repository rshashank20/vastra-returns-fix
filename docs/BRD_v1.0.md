# Business Requirements Document — Returns Module Rebuild (Vastra)
**Version:** 1.0 · **Date:** 2026-10-08 · **Author:** Business Analyst (self-directed project)  
**Status:** Draft for stakeholder review

> **Data note:** Vastra's dataset is synthetic. The figures in this document come from
> the project analysis unless explicitly marked as a proxy or modelled assumption.
> Assumptions are recorded in `docs/assumptions.md`. The requirements below were
> written from the Phase 1 cost analysis and Phase 2 process analysis.

## 1. Why this document exists

The returns problem turned out to be both a **cost problem** and a **process problem**.
The analysis showed that Vastra's current return process is expensive, refund delays are
linked to QC delays, and a blanket return fee would affect customers very differently.

This BRD translates those findings into requirements for the new order-management
system. The aim is to make the recommended policy enforceable in the product and to
remove the operational gaps that are slowing refunds.

## 2. Business objectives

| ID | Objective | Baseline → Target | Source |
|----|-----------|-------------------|--------|
| BO-1 | Reduce fully-loaded cost per return | ₹511 → ≤ ₹430 | `sql/01_cost_per_return.sql` |
| BO-2 | Reduce 14-day SLA breaches | 56.8% → ≤ 30% | `refunds` |
| BO-3 | Reduce WISMO tickets | 14.0 per 100 breached returns → ≤ 7 | `sql/11_wismo.sql` |
| BO-4 | Increase exchange share of returns | ~6% → ≥ 20% | `sql/07_exchange_economics.sql` (proxy) |
| BO-5 | Remove the standing QC backlog | 1,500–2,300 units → ~0 | `sql/12_qc_backlog.sql` |

> **Important:** BO-4 uses an exchange proxy from the available data. It is a target
> for the redesigned process, not a claim that the existing dataset already proves
> a 20% exchange rate is achievable.

## 3. Scope

### In scope

- Return initiation
- Pickup scheduling and tracking
- QC queue and prioritisation
- Refund vs exchange decision
- Refund/payout processing
- Return-fee rules
- Instant-refund eligibility
- Proactive customer notifications
- Courier SLA tracking
- Journey-stage audit trail

### Out of scope

- Forward-logistics redesign
- Product-quality correction at sourcing (the toxic-SKU analysis will feed that work)
- Payment-gateway commercial renegotiation

## 4. Business requirements

| ID | Requirement | Traces to | Acceptance |
|----|-------------|-----------|------------|
| BR-01 | Refunds should be credited within 5 days of QC completion for at least 95% of returns. | BO-2; `sql/10_breach_anatomy.sql` | Measure over a trailing 30-day period. |
| BR-02 | At least 70% of returns should meet the overall 14-day return-to-credit SLA. | BO-2 | Report monthly using the defined SLA logic. |
| BR-03 | Starting with a customer's 2nd return in a calendar quarter, a ₹49 fee should be applied automatically, unless an exemption rule applies. | BO-1; `sql/04_bracketing.sql` | Audit shows 100% of qualifying returns received the correct fee. |
| BR-04 | QC-confirmed damaged or defective returns must not be charged a return fee. | BO-1; fairness guardrail | No fee on returns where QC result is `damaged` or `defective`. |
| BR-05 | Exchange should be shown before refund at return initiation, with immediate exchange confirmation. | BO-4; `sql/07_exchange_economics.sql` | Track exchange uptake; target ≥ 20% within 90 days. |
| BR-06 | Customers with `trust_score ≥ 80` and no fee history should be eligible for an instant refund on initiation. | BO-3; `A-ABUSE` | Abuse rate should remain ≤ 2% of instant-refund transactions. |
| BR-07 | Each return-journey stage must have an SLA and an accountable owner. | BO-2; `sql/09_journey_bottleneck.sql`, `sql/13_pickup_failures.sql` | SLA register is published and breaches are escalated automatically. |
| BR-08 | QC should operate as a daily queue rather than a periodic batch. | BO-5; `sql/12_qc_backlog.sql` | Standing backlog remains at ~0 for 30 consecutive days. |
| BR-09 | Courier pickup should have a 24-hour SLA, with a ₹50 penalty for excess failed pickups when the weekly failure rate is above 10%. | `sql/13_pickup_failures.sql` | Include performance in the quarterly courier scorecard. |
| BR-10 | Customers should be notified before a return is expected to miss its SLA. | BO-3 | WISMO target ≤ 7 tickets per 100 returns. |

## 5. Functional requirements

| ID | Requirement | Traces to |
|----|-------------|-----------|
| FR-01 | **Refund rules engine:** use `trust_score`, item value, QC result and fee history to decide whether a refund can be auto-approved or needs manual review. | BR-01, BR-06 |
| FR-02 | **Quarterly return-fee engine:** count qualifying returns by customer and quarter, apply the ₹49 fee from the 2nd return, and ignore QC-confirmed damage/defect returns. | BR-03, BR-04 |
| FR-03 | **Exchange-first return flow:** show exchange as the first option at initiation, including the option to change size for the same SKU, and confirm the exchange immediately. | BR-05 |
| FR-04 | **Delay notifications:** trigger customer communication when pickup is delayed >48 hours, QC wait exceeds 72 hours, or the projected credit date is likely to miss SLA. Also flag the case in the CX view. | BR-10 |
| FR-05 | **QC prioritisation queue:** rank work using breach risk and item value instead of only FIFO by arrival time. | BR-01, BR-08 |
| FR-06 | **Pickup SLA tracking:** record each courier attempt and flag weekly courier failure rates above 10%. | BR-09 |
| FR-07 | **Journey audit trail:** store a timestamp for every return stage so that missing handoff scans can be identified and investigated. | BR-07; data-quality finding |
| FR-08 | **Fee transparency:** show the customer the applicable fee before the return is confirmed, including the rule that caused the fee. | BR-03 |

## 6. Non-functional requirements

| ID | Requirement |
|----|-------------|
| NFR-01 | Every journey-stage event must be stored with a server timestamp. Courier handoff events should not be left without a timestamp. |
| NFR-02 | Pickup performance should be reportable by courier, pincode and week. |
| NFR-03 | Every fee-engine decision must store the rule ID used so CX can explain or dispute the charge. |
| NFR-04 | Refund and payout operations must be idempotent so duplicate return requests (including app-retry rows) cannot create duplicate payments. |
| NFR-05 | Operational dashboards should refresh daily, with SLA-breach alerts reaching the relevant team within 1 hour. |

## 7. Business rules

| ID | Rule |
|----|------|
| RULE-01 | **IF** qualifying returns in the current quarter ≥ 2 **AND** QC result is not `damaged` or `defective` **THEN** fee = ₹49. |
| RULE-02 | **IF** `trust_score ≥ 80` **AND** item value ≤ ₹2,000 **AND** customer has no fee history **THEN** allow instant refund on initiation. |
| RULE-03 | **IF** QC result is `damaged` or `defective` **THEN** fee = ₹0 **AND** route the case to sourcing-quality review. |
| RULE-04 | **IF** pickup attempts ≥ 3 **THEN** escalate to CX and offer the self-drop option. |
| RULE-05 | **IF** projected credit date is beyond the SLA **THEN** notify the customer and flag the case for CX. |
| RULE-06 | **IF** courier weekly failure rate > 10% **THEN** raise the contractual penalty claim. |

## 8. Assumptions and dependencies

The detailed assumption log is in `docs/assumptions.md`.

The main dependencies are:

- courier agreement changes for pickup SLAs and penalties
- a warehouse operating model that supports daily QC
- payment infrastructure that supports the proposed instant-refund path

These are implementation dependencies rather than findings from the SQL analysis.

## 9. Acceptance criteria for the rebuild

1. The policy model reconciles to Finance's baseline margin within 2%.
2. Every TO-BE step can be linked back to a problem or bottleneck found in the analysis in `docs/rca.md`.
3. UAT cases in `docs/uat.md` pass for the agreed release scope.
4. BR-01 through BR-10 can be measured from production data after rollout.

## 10. Traceability note

The intent of this BRD is to keep the chain visible:

**Analysis finding → business decision → requirement → acceptance test → KPI.**

For example, the analysis found that breached returns spent more time in QC than clean
returns. That finding is carried into BR-01, FR-05 and the QC operating change in BR-08,
then measured through refund SLA attainment and backlog.

## 11. Version history

| Version | Date | Change |
|---------|------|--------|
| 0.1 | 2026-10-08 | Initial draft from Phase 1–3 findings |
| 1.0 | 2026-10-08 | Rewritten for stakeholder review; clarified assumptions, targets and traceability |
