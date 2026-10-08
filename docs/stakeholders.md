# Stakeholders + RACI — Vastra Returns Redesign

I mapped the stakeholders after the first round of analysis because the numbers alone do not tell me who has to act on each finding.

The main people involved are the teams that own margin, customer experience, warehouse operations, the returns system, courier performance, and product quality.

## Stakeholder map

| # | Stakeholder | What they own in this project | What they care about | Influence | How I would involve them |
|---|---|---|---|---|---|
| 1 | CFO / Finance Head | Return economics, policy decision and rebuild budget | The estimated ₹18.16 cr/year return-cost bleed and net margin | High | Main decision-maker for the policy and business case |
| 2 | CX Head | Refund SLA and customer-support impact | WISMO volume, service levels and customer experience; estimated ₹15.4L/year support cost | Medium | Involve in the TO-BE service design and SLA decision |
| 3 | Warehouse Ops (Delhi + Mumbai) | Pickup handling, QC and returned inventory flow | Daily workload and the standing QC backlog | Medium | Work with Ops on the daily QC flow instead of treating the finding as a headcount-only problem |
| 4 | Product / Engineering | Returns-module changes | Scope, feasibility and delivery effort | High | Use the BRD and flows as the basis for feasibility and build discussions |
| 5 | Courier partners (Delhivery, XpressBees, EcomExpress) | Pickup execution | Their operational performance and contract terms | Medium | Use pickup-failure data in the SLA and penalty discussion |
| 6 | Sourcing / Category (especially Dresses) | Product quality and toxic-SKU decisions | Return-heavy products and the cost of quality-related returns | Medium | Review the top return-toxic SKUs and decide whether to fix, re-price or delist them |
| 7 | Marketing | Customer acquisition and communication | Possible conversion or customer reaction to return fees | Low–Medium | Keep Marketing involved when policy changes are communicated to customers |

## What each stakeholder needs to decide

| Stakeholder | Decision I need from them |
|---|---|
| Finance | Which return-policy option is financially acceptable and what budget is available for the process/system changes |
| CX | What refund SLA should be the service target and how delay communications should work |
| Warehouse Ops | Whether the proposed daily QC process is workable with the existing operation and what capacity changes are actually needed |
| Product / Engineering | Which requirements are feasible for the returns-module rebuild and in what sequence they can be delivered |
| Couriers | Whether pickup SLA and penalty terms can be agreed and measured |
| Sourcing / Category | Which high-return SKUs need a product, sourcing or pricing intervention |
| Marketing | How the policy change should be communicated without creating unnecessary customer backlash |

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
| Rollout + communications | I | **A/R** | C | C | I | — |

**R** = Responsible (does the work)  
**A** = Accountable (owns the outcome)  
**C** = Consulted  
**I** = Informed

## Where the interests can conflict

### Finance vs Marketing

Finance has a strong reason to reduce return cost, while Marketing will be concerned about what a fee does to customer conversion and perception.

The reason I prefer a segmented policy instead of a blanket fee is that the fee is aimed at the smaller group of customers showing repeat-return behaviour. The worked example in `assumptions.md` uses roughly 6% of customers rather than applying the fee to everyone.

### Warehouse Ops vs the QC recommendation

The analysis points to scheduling and batching as a major reason for the QC delay. That does not automatically mean more people should be hired.

So I would involve Warehouse Ops in the redesign itself. They are the team that has to make the daily QC flow work, and ignoring their operating constraints would make the recommendation difficult to implement.

### Courier partners

Courier performance is partly an external contract issue. For example, XpressBees shows a higher pickup-failure rate than Delhivery in the analysis (17.8% vs 10.3%).

I would use Delhivery as the benchmark when discussing the SLA with XpressBees. The ₹50/excess-failed-pickup term is a proposed contract lever, not an internal operating rule, so it still needs agreement with the courier.

## How I would run the stakeholder discussion

I would not start the conversation with the solution. I would first show each stakeholder the part of the analysis that affects their area, confirm that the finding matches how the process works today, and then use the agreed finding to define the change.

That keeps the project grounded in the actual problem rather than turning the stakeholder map into a formal document that no one uses.
