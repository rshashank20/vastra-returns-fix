# PROJECT PLAN — The Returns Fix (Vastra)
**Goal:** settle the returns-policy debate with data + deliver the rebuild package (BRD, flows, stories, UAT).
**Method:** two tracks (cost/policy, process) → synthesis → BA package → visualization → closeout.
**Rule:** no phase starts until the previous phase's deliverable exists. Dashboards come last, not first.

---

## Phase 0 — Foundation ✅ DONE
| # | Task | Deliverable | Status |
|---|------|-------------|--------|
| 0.1 | Read & understand the spec | Shared understanding of the two-track problem | ✅ |
| 0.2 | Synthetic dataset | `data_generator.py` + 9 CSVs + `DATA_DICTIONARY.md` | ✅ |
| 0.3 | Analytical database | `vastra.db` (SQLite, indexed) | ✅ |

## Phase 1 — Cost analytics (current)
*Question: what does each return really cost, and where does the money go?*
| # | Analysis (maps to spec §7) | SQL file | Deliverable |
|---|---------------------------|----------|-------------|
| 1.1 | Fully-loaded cost per return (headline) | `sql/01_cost_per_return.sql` | ✅ Avg ₹512 vs ₹88 perceived; ₹18.2 cr/yr |
| 1.2 | ✅ Cost by reason × category | `sql/02_cost_by_reason_category.sql` | Top-bleed segments table |
| 1.3 | ✅ True-reason triangulation (customer reason × QC × bracketing) | `sql/03_true_reason.sql` | Triangulation matrix; % genuine vs bracket vs remorse |
| 1.4 | ✅ Bracketing detection (same cust + SKU + 3 sizes / 7 days) | `sql/04_bracketing.sql` | Bracketeer segment + its cost share |
| 1.5 | ✅ Cost concentration by customer decile | `sql/05_concentration.sql` | Concentration curve (expect ~10% → 50%+) |
| 1.6 | ✅ SKU return-toxicity ranking | `sql/06_toxicity.sql` | Toxic SKU list (delist / fix size chart) |
| 1.7 | ✅ Exchange-vs-refund economics | `sql/07_exchange_economics.sql` | Margin retained per exchange vs refund |
| 1.8 | ✅ Cohort analysis (return rate by acquisition cohort/channel) | `sql/08_cohorts.sql` | Do paid-acquired customers return more? |

**Phase 1 done =** ✅ 2026-10-08 — a one-page "cost story": headline number, top 3 bleed drivers, triangulation result, concentration finding. Written, not just queried.

## Phase 2 — Process analytics
*Question: where does the refund journey stall, and why?*
| # | Analysis (maps to spec §7) | SQL file | Deliverable |
|---|---------------------------|----------|-------------|
| 2.1 | ✅ Journey bottleneck: median days per stage × warehouse × courier | `sql/09_journey_bottleneck.sql` | Bottleneck stage + driver |
| 2.2 | ✅ SLA breach anatomy: which stage delay predicts breach | `sql/10_breach_anatomy.sql` | Breach driver ranking |
| 2.3 | ✅ WISMO tickets per 100 returns by breach bucket | `sql/11_wismo.sql` | Cost of slowness in CX terms |
| 2.4 | ✅ QC backlog dynamics: arrivals vs completions/day | `sql/12_qc_backlog.sql` | Backlog age distribution |
| 2.5 | ✅ Pickup-failure analysis by courier × pincode tier | `sql/13_pickup_failures.sql` | Courier scorecard input |

**Phase 2 done =** ✅ 2026-10-08 — a one-page "process story": the bottleneck (expected: QC batching + courier handoff), breach drivers, CX cost of delay.

## Phase 3 — Synthesis (Excel)
*Question: what should Vastra DO?*
| # | Model | Deliverable |
|---|-------|-------------|
| 3.1 | ✅ Policy scenario model: fee ₹0/49/99 × elasticity → net margin | `excel/policy_scenarios.xlsx` — the decision engine |
| 3.2 | ✅ Process capacity model: pickup/QC throughput vs arrival rate | `excel/capacity_model.xlsx` — what staffing/scheduling closes the backlog |
| 3.3 | ✅ Business case: rebuild cost vs margin recovery + CX savings | `excel/business_case.xlsx` — payback |
| 3.4 | ✅ RCA write-up (two threads → one conclusion) | `docs/rca.md` |

**Phase 3 done =** ✅ 2026-10-08 — the recommendation is quantified and the RCA is written down.

## Phase 4 — BA package (§16 of spec)
*Question: what exactly gets built?*
| # | Artifact | Deliverable |
|---|----------|-------------|
| 4.1 | ✅ Stakeholder map + RACI | `docs/stakeholders.md` |
| 4.2 | ✅ BRD (business + functional + non-functional reqs) | `docs/BRD_v1.0.md` |
| 4.3 | ✅ AS-IS / TO-BE swimlane flows | `docs/flows/` (draw.io) |
| 4.4 | ✅ User stories + acceptance criteria | `docs/user_stories.md` |
| 4.5 | ✅ UAT cases | `docs/uat.md` |
| 4.6 | ✅ Assumptions log + stakeholder-pushback appendix | `docs/assumptions.md` |

**Phase 4 done =** ✅ 2026-10-08 — an engineering team could rebuild the returns flow from your docs alone.

## Phase 5 — Visualization (Power BI, LAST)
4 pages per spec §9: (1) The bleed, (2) The journey, (3) Who & why, (4) Policy & process lab.
**Done =** every chart traces to an analysis from Phase 1–2; no orphan visuals.

## Phase 6 — Closeout
| # | Deliverable |
|---|-------------|
| 6.1 | 1-page policy + process recommendation memo (executive tone) |
| 6.2 | README (problem → decision → impact on first screen; data-honesty statement) |
| 6.3 | GitHub repo (versioned files: `BRD_v1.0`, not `final_final`) |
| 6.4 | Resume bullets (numbers filled in from real outputs) |

**Project done =** ✅ 2026-10-08 — the 60-second test: a recruiter sees problem, decision, impact on the first screen.

---

## Milestones & rough timing (evenings)
- M1: Phase 1 complete — cost story written (~1 week)
- M2: Phase 2 complete — process story written (~1 week)
- M3: Phase 3 complete — recommendation quantified (~1 week)
- M4: Phase 4 complete — BA package done (~1 week)
- M5: Ship — PBI + memo + repo (~1 week)

## Assumptions & risks
- Assumptions (cost model, SLA, elasticities) are documented per artifact and changeable — never hardcoded silently.
- Risk: scope creep into "one more analysis." Guardrail: if it doesn't serve the policy decision or the TO-BE flow, it doesn't get built.
- Risk: synthetic-data skepticism in interviews. Mitigation: honesty framework (§16 + assumptions log + proxy stakeholder note in README).
