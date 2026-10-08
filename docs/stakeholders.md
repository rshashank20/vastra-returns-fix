# Stakeholder Map + RACI — Returns Redesign Program (Vastra)

## Stakeholder map

| # | Stakeholder | Role in program | Interest | Influence | Engagement |
|---|-------------|-----------------|----------|-----------|------------|
| 1 | CFO / Finance head | Funds the rebuild; owns margin | High — ₹18.16 cr/yr bleed | High — budget gate | Decision-maker on policy + business case |
| 2 | CX Head | SLA owner; owns WISMO cost (₹15.4L/yr) | High — ticket volume, CSAT | Medium | Co-owner of TO-BE service design |
| 3 | Warehouse Ops (Delhi + Mumbai) | Runs QC/pickup; owns backlog | High — daily workload | Medium | Must co-design daily-flow QC (not have it imposed) |
| 4 | Product / Engineering | Builds the returns module | Medium — scope, timelines | High — build capacity | BRD approver (feasibility) |
| 5 | Courier partners (Delhivery, XpressBees, EcomExpress) | External; pickup execution | Low–Medium | Medium — contract leverage | Renegotiation target (SLA + penalties) |
| 6 | Sourcing / Category (Dresses) | Owns toxic-SKU quality failures | Medium | Medium | Fix-or-delist decisions on top-30 toxic SKUs |
| 7 | Marketing | Acquisition; fears fee backlash | Medium — conversion | Low–Medium | Consulted on fee communication |

## RACI — redesign workstreams

| Workstream / Activity | Finance | CX Head | Warehouse Ops | Product/Eng | Couriers | Sourcing |
|---|---|---|---|---|---|---|
| Policy design (fee levels, segments) | **A** | C | I | C | — | I |
| Policy sign-off | **A** | R | I | I | — | I |
| Process redesign (QC daily flow) | I | C | **A/R** | C | — | — |
| BRD approval | A | R | R | **A** | — | I |
| Returns-module build | I | C | C | **A/R** | — | — |
| Courier SLA renegotiation | A | I | R | — | **R** | — |
| UAT sign-off | A | **A** | R | R | — | — |
| Rollout + comms | I | **A/R** | C | C | I | — |

**R** = Responsible (does it), **A** = Accountable (owns the outcome — exactly one per row),
**C** = Consulted, **I** = Informed.

## Key stakeholder tensions (managed, not ignored)
- **Finance vs Marketing** on fees: resolved by the segmented policy — fee touches ~6% of customers, not 100% (see `assumptions.md` pushback appendix for the worked example).
- **Warehouse Ops vs the QC finding:** the analysis says scheduling, not headcount — Ops must co-own the daily-flow design or the recommendation dies in implementation. Mitigation: Ops leads workstream 3 (R/A above).
- **Couriers:** external — the SLA + ₹50/excess-failed-pickup term is a contract negotiation, not an internal mandate; Delhivery (10.3% fail) is the benchmark XpressBees (17.8%) is held to.
