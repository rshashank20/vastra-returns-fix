# Power BI Build Guide — The Returns Fix (Vastra)

> **Explicit scope:** this is a BUILD GUIDE, not a `.pbix` file. It specifies
> the data model, DAX, and exact visuals so the dashboard can be built in
> ~1 day from the CSVs in `data/`. Every visual traces to a Phase 1/2 query —
> no orphan charts.

## 1. Data model

**Import:** the 9 CSVs from `data/` via Power Query. No reshaping needed except:
- Parse all `*_at` / `*_date` / `stage_ts` columns as DateTime.
- `refunds.days_basis` is text (business/calendar) — keep as-is; it documents
  the seeded inconsistency.

**Relationships** (single direction, many-to-one unless noted):
| From | To | On | Notes |
|---|---|---|---|
| order_lines[order_id] | orders[order_id] | inner | — |
| orders[customer_id] | customers[customer_id] | — | — |
| shipments[order_id] | orders[order_id] | — | one row per order |
| returns[line_id] | order_lines[line_id] | — | exact line grain (NOT order_id+sku: bracketing!) |
| return_journey[return_id] | returns[return_id] | — | one-to-many event stream |
| qc_outcomes[return_id] | returns[return_id] | — | one-to-one |
| refunds[return_id] | returns[return_id] | — | one-to-one; ~1% missing = exception cases |
| cx_tickets[return_id] | returns[return_id] | — | one-to-many; tickets may lack return_id → keep blanks visible |

**One calculated column** (on `returns`) — the triangulated true reason,
mirroring `sql/03_true_reason.sql` logic (bracketing flag via a merged
`bracketing_orders` table built in Power Query from order_lines with
`COUNT DISTINCT size >= 3` per order_id+sku):
```dax
true_reason =
VAR is_brack = NOT ISBLANK(RELATED(bracketing_orders[order_id]))
RETURN SWITCH(TRUE(),
  is_brack, "bracketing",
  returns[reason_code]="damaged" && RELATED(qc_outcomes[qc_result])="damaged", "genuine_damage",
  RELATED(qc_outcomes[qc_result])="damaged", "damaged_item_other_claim",
  RELATED(qc_outcomes[qc_result])="defective", "defective_item_other_claim",
  returns[reason_code]="damaged", "fake_damage_claim",
  returns[reason_code] IN {"size_fit","changed_mind","other"}, "fit_or_remorse",
  "other_true")
```

## 2. DAX measures
```dax
Avg cost per return   = 511            // precomputed in sql/01; stored as measure for cards
Total return cost cr  = 18.16
Breach rate %         = DIVIDE(COUNTROWS(FILTER(refunds, refunds[sla_breach_flag]=1)), COUNTROWS(refunds))
WISMO per 100         = DIVIDE(COUNTROWS(FILTER(cx_tickets, cx_tickets[category]="WISMO")), COUNTROWS(returns)) * 100
Avg refund days       = 10.2           // sql/09 initiated→refund_issued
Bracketeer share %    = 6.14           // sql/04
```
*(Cost-component breakdowns come from the precomputed per-return cost table
exported from `v_return_cost` — see §4 note. Do NOT rebuild the cost model in
DAX; the SQL view is the single source of truth.)*

**Recommended:** export `v_return_cost` from SQLite to `returns_costed.csv`
(`sqlite3 vastra.db ".headers on" ".mode csv" "SELECT * FROM v_return_cost;" > data/returns_costed.csv`)
and import it as the fact table for all cost visuals. One source of truth.

## 3. Pages & exact visuals

**Page 1 — The bleed** (answers: how bad is it?)
- KPI cards: ₹18.16 cr total cost · ₹511 avg/return (vs ₹88 perceived) · 56.8% breach rate
- Stacked bar: cost components per return (reverse 88 / forward waste 72 / QC 35 / refurb 33 / CX 11 / holding 7 / write-off 265)
- Line: returns + cost per month (2025)
- Slicers: category, warehouse

**Page 2 — The journey** (answers: where does it stall?)
- Funnel: avg days per stage — sched 0.3 → pickup 1.4 → transit 4.0 → QC 4.1 → refund 2.0 (bottleneck highlighted)
- Bar: breached vs clean stage durations (QC 5.1 vs 2.9 — the smoking gun)
- Area: QC backlog over time by warehouse (standing 1.5–2.3K units)
- Line: SLA breach % by month × warehouse
- Alert visual: courier fail-rate table (XpressBees 17.8% vs Delhivery 10.3%)

**Page 3 — Who & why** (answers: who bleeds us, and why do they return?)
- Line: cumulative % of cost by customer decile (top 20% → 49.9%)
- Donut: true_reason split (fit_or_remorse 47.6%, bracketing 8.0%, fake_damage 10.2%, quality_failure 6.5%, …)
- KPI cards: 13,535 bracketeers (6.1%) · 36,402 fake damage claims
- Table: top-30 toxic SKUs (return rate × avg cost) — Dresses 40–47%

**Page 4 — Policy & process lab** (answers: what do we do?)
- Bar: policy options net impact (status quo 0 / flat49 ₹2.19cr / flat99 ₹3.17cr / exchange-first ₹2.36cr / ★ segmented ₹3.48cr) — values pasted from `excel/policy_scenarios.xlsx` Model sheet, refreshed manually per scenario review
- Card: recommendation — SEGMENTED (fee from 2nd return/qtr + exchange-first + instant refunds high-trust)
- Guardrail KPIs: exchange uptake %, repeat-purchase post-return, % good customers affected (6%)
- Text box: TO-BE flow summary (5 SLA gates) — condensed from `docs/flows_to_be.mmd`

## 4. Build notes
- **Do not rebuild the cost model in DAX.** `returns_costed.csv` (from `v_return_cost`) is the fact table; DAX only aggregates.
- The `days_basis` inconsistency (business vs calendar) is a feature to *show*, not clean: add a footnote on Page 2.
- Keep the 30% missing pickup scans visible: Page 2 funnel labels the pickup stage "n=70% (scan gap)".
- Refresh: full CSV reload; no incremental logic needed for a 12-month static build.
