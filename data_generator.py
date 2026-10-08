"""
data_generator.py — Vastra "The Returns Fix" synthetic dataset
===============================================================
Project 2 of the resume top-4: cost + policy + process redesign of D2C
fashion returns. Fictional brand, fully synthetic data.

DATA-HONESTY (non-negotiable): every number in this file is generated.
Assumptions are documented below and in DATA_DICTIONARY.md. Nothing here
is real company data.

Time period: 2025-01-01 .. 2025-12-31 (12 months), customers acquired
from 2022-01-01 onward.

KEY ASSUMPTIONS
- Line-level return rate ~28% (310K returns / 1.1M lines), matching the spec.
- AOV ~ Rs 1,800.
- 4% of orders are "bracketing" orders (same SKU, 3 sizes, keep 1).
- Refund SLA: return initiated -> refund credited <= 10 days.
- WH-Mumbai records refund credit dates in BUSINESS days, WH-Delhi in
  CALENDAR days (seeded inconsistency the analyst must discover).
- QC runs as a Monday batch: qc_done timestamps cluster on Mondays.
- 30% of pickups are missing the courier handoff scan timestamp.
- Customer-selected reason codes are noisy: "other" = 18% of selections,
  "damaged" is over-selected ~2x (customers pick it to get free pickup).
- ~0.4% duplicate return requests from app retries (undiscovered dupes).

Usage:
    python data_generator.py --scale 1.0 --out ./data --seed 42
    --scale 0.02  -> quick smoke test (~2% of rows)
"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------
# Catalog / config
# ----------------------------------------------------------------------------
CATEGORIES = {
    # category: (size_system, price_lo, price_hi, return_rate_multiplier)
    "Kurtas":   ("apparel_top", 799, 2499, 1.25),
    "Dresses":  ("apparel_top", 999, 2999, 1.45),
    "Shirts":   ("apparel_top", 699, 1999, 1.00),
    "T-Shirts": ("apparel_top", 399, 999, 0.85),
    "Jeans":    ("apparel_bottom", 1199, 2799, 1.20),
    "Trousers": ("apparel_bottom", 999, 2299, 1.05),
    "Sarees":   ("free", 1499, 4999, 0.90),
    "Footwear": ("footwear", 899, 2999, 1.10),
    "Handbags": ("free", 1299, 3999, 0.70),
    "Jewellery":("free", 499, 2499, 0.55),
}
SIZE_SYSTEMS = {
    "apparel_top": ["XS", "S", "M", "L", "XL", "XXL"],
    "apparel_bottom": ["28", "30", "32", "34", "36"],
    "footwear": ["UK6", "UK7", "UK8", "UK9", "UK10", "UK11"],
    "free": ["Free"],
}
WAREHOUSES = ["WH-Mumbai", "WH-Delhi"]
COURIERS = {"Delhivery": 0.08, "XpressBees": 0.14, "EcomExpress": 0.11}  # pickup-fail rate
CITY_TIERS = ["Tier1", "2", "3"]
CHANNELS = ["app", "web", "instagram"]
ACQ_CHANNELS = ["paid_ads", "organic", "referral", "marketplace"]
REASONS_SELECTED = ["size_fit", "quality_issue", "damaged", "wrong_item",
                    "changed_mind", "other"]


def build_sku_catalog(rng, n_skus=2000):
    cats = list(CATEGORIES.keys())
    cat = rng.choice(cats, size=n_skus,
                     p=np.array([1.4, 1.2, 1.0, 1.1, 0.9, 0.8, 0.7, 0.8, 0.5, 0.6]) / 9.0)
    skus = []
    for i, c in enumerate(cat):
        _, lo, hi, _ = CATEGORIES[c]
        skus.append((f"SKU-{i:05d}", c, int(rng.integers(lo, hi + 1))))
    return pd.DataFrame(skus, columns=["sku", "category", "mrp"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--out", type=str, default="./data")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    rng = np.random.default_rng(a.seed)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    S = a.scale  # scale factor

    N_CUST, N_ORD = int(450_000 * S), int(800_000 * S)
    START, END = pd.Timestamp("2025-01-01"), pd.Timestamp("2025-12-31")
    days = (END - START).days

    # ---------------------------------------------------------------- 1. customers
    cust_ids = [f"CUST-{i:06d}" for i in range(N_CUST)]
    signup = pd.to_datetime(rng.integers(
        pd.Timestamp("2022-01-01").value // 10**9,
        END.value // 10**9, N_CUST), unit="s")
    customers = pd.DataFrame({
        "customer_id": cust_ids,
        "signup_date": signup.normalize(),
        "city_tier": rng.choice(CITY_TIERS, N_CUST, p=[0.45, 0.35, 0.20]),
        "acquisition_channel": rng.choice(ACQ_CHANNELS, N_CUST,
                                          p=[0.45, 0.30, 0.10, 0.15]),
        "trust_score": np.clip(rng.normal(62, 14, N_CUST), 5, 99).round(1),
    })

    # ---------------------------------------------------------------- 2. orders (+lines)
    # Festive spike Oct-Nov
    month_w = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1.45, 1.45, 1.2])
    month_w /= month_w.sum()
    order_month = rng.choice(12, N_ORD, p=month_w)
    order_day = rng.integers(0, 28, N_ORD)
    order_date = pd.to_datetime(
        {"year": 2025, "month": order_month + 1, "day": order_day + 1})
    basket = np.clip(rng.lognormal(np.log(1800), 0.55, N_ORD), 299, 15000).round(0)
    orders = pd.DataFrame({
        "order_id": [f"ORD-{i:07d}" for i in range(N_ORD)],
        "customer_id": rng.choice(cust_ids, N_ORD),
        "order_date": order_date,
        "basket_value": basket,
        "discount": (basket * rng.choice([0, 0.1, 0.15, 0.2], N_ORD,
                                        p=[0.4, 0.3, 0.2, 0.1])).round(0),
        "channel": rng.choice(CHANNELS, N_ORD, p=[0.55, 0.30, 0.15]),
        "warehouse_id": rng.choice(WAREHOUSES, N_ORD, p=[0.6, 0.4]),
        "courier": rng.choice(list(COURIERS.keys()), N_ORD, p=[0.4, 0.35, 0.25]),
    })

    sku_cat = build_sku_catalog(rng)
    n_lines = rng.choice([1, 2, 3], N_ORD, p=[0.55, 0.30, 0.15])
    line_order_idx = np.repeat(np.arange(N_ORD), n_lines)
    n_total_lines = len(line_order_idx)
    sku_idx = rng.integers(0, len(sku_cat), n_total_lines)
    lines = pd.DataFrame({
        "order_id": orders["order_id"].values[line_order_idx],
        "sku": sku_cat["sku"].values[sku_idx],
        "category": sku_cat["category"].values[sku_idx],
        "price": sku_cat["mrp"].values[sku_idx],
    })
    # sizes per category system
    def pick_size(c):
        return rng.choice(SIZE_SYSTEMS[CATEGORIES[c][0]])
    lines["size"] = [pick_size(c) for c in lines["category"].values]
    lines["line_id"] = [f"LN-{i:07d}" for i in range(n_total_lines)]

    # --- bracketing injection: orders with exactly 3 lines -> same SKU, 3 sizes, keep 1
    # (~2.2% of orders => ~10% of all returns; the policy-addressable segment)
    three_line_orders = np.where(n_lines == 3)[0]
    n_bracket = int(N_ORD * 0.022)
    bracket_ords = rng.choice(three_line_orders, min(n_bracket, len(three_line_orders)),
                              replace=False)
    bracket_line_idx = []
    for oi in bracket_ords:
        li = np.where(line_order_idx == oi)[0]
        base = li[0]
        c = lines["category"].iloc[base]
        sizes = SIZE_SYSTEMS[CATEGORIES[c][0]]
        if len(sizes) < 3:
            continue  # free-size categories can't bracket
        s3 = rng.choice(sizes, 3, replace=False)
        for j, idx in enumerate(li[:3]):
            lines.at[lines.index[idx], "sku"] = lines["sku"].iloc[base]
            lines.at[lines.index[idx], "size"] = s3[j]
        bracket_line_idx.extend(li[:3].tolist())
    is_bracket_line = np.zeros(n_total_lines, bool)
    is_bracket_line[bracket_line_idx] = True
    lines["is_bracketing_order"] = is_bracket_line

    # ---------------------------------------------------------------- 3. returns (calibrated to ~28% line rate)
    cat_mult = lines["category"].map({c: v[3] for c, v in CATEGORIES.items()}).values
    base_p = 0.245
    p_ret = np.clip(base_p * cat_mult, 0.02, 0.6)
    p_ret[is_bracket_line] = 0.67  # keep 1 of 3
    returned = rng.random(n_total_lines) < p_ret
    # calibrate total to target
    target = int(n_total_lines * 0.28)
    cur = returned.sum()
    if cur != target:
        # adjust by flipping lowest/highest-propensity non-bracket lines
        idx_nb = np.where(~is_bracket_line)[0]
        order = np.argsort(p_ret[idx_nb])
        diff = target - cur
        if diff > 0:
            flip = idx_nb[order[-(diff):]] if diff < len(order) else idx_nb
            returned[flip] = True
        else:
            flip = idx_nb[order[:(-diff)]]
            returned[flip] = False
    ret_lines = lines[returned].copy().reset_index(drop=True)
    n_ret = len(ret_lines)
    ret_lines["return_id"] = [f"RET-{i:07d}" for i in range(n_ret)]
    ret_lines["return_date"] = (
        pd.to_datetime(orders.set_index("order_id").loc[ret_lines["order_id"],
                                                        "order_date"].values)
        + pd.to_timedelta(rng.integers(1, 21, n_ret), unit="D")).normalize()

    # TRUE reason (hidden logic for triangulation) vs CUSTOMER-SELECTED (noisy)
    true_reason = np.where(
        ret_lines["is_bracketing_order"].values, "bracketing",
        rng.choice(["size_fit", "quality_issue", "damaged_transit", "wrong_item",
                    "remorse", "other"],
                   n_ret, p=[0.30, 0.18, 0.07, 0.05, 0.25, 0.15]))
    sel = []
    for t in true_reason:
        r = rng.random()
        if t == "bracketing":
            sel.append(rng.choice(["size_fit", "changed_mind", "other"],
                                  p=[0.5, 0.3, 0.2]))
        elif t == "size_fit":
            sel.append("damaged" if r < 0.18 else "size_fit")  # free-pickup gaming
        elif t == "remorse":
            sel.append("damaged" if r < 0.22 else ("other" if r < 0.40 else "changed_mind"))
        elif t == "quality_issue":
            sel.append("quality_issue" if r < 0.8 else "damaged")
        else:
            sel.append({"damaged_transit": "damaged", "wrong_item": "wrong_item",
                        "other": "other"}[t])
    # force "other" to ~18% overall
    sel = np.array(sel)
    other_mask = rng.random(n_ret) < 0.02
    sel[other_mask] = "other"
    ret_lines["true_reason"] = true_reason          # analyst must NOT use; for our validation
    ret_lines["reason_code"] = sel                  # what the customer clicked
    ret_lines["refund_amount"] = ret_lines["price"].values

    # duplicate app-retry returns (~0.4%, undiscovered)
    n_dup = int(n_ret * 0.004)
    dup_idx = rng.choice(n_ret, n_dup, replace=False)
    dups = ret_lines.iloc[dup_idx].copy()
    dups["return_id"] = [f"RET-D{i:06d}" for i in range(n_dup)]
    dups["is_duplicate"] = True
    ret_lines["is_duplicate"] = False
    returns = pd.concat([ret_lines, dups], ignore_index=True)
    n_ret_all = len(returns)

    # ---------------------------------------------------------------- 4. shipments
    orders["forward_cost"] = np.clip(rng.normal(72, 12, N_ORD), 40, 140).round(0)
    shipments = orders[["order_id", "forward_cost", "warehouse_id",
                        "courier"]].copy()
    # reverse cost only meaningful if order had a return; fill anyway
    shipments["reverse_cost"] = np.clip(rng.normal(88, 15, N_ORD), 45, 170).round(0)

    # ---------------------------------------------------------------- 5. return_journey (event stream)
    r = returns.reset_index(drop=True)
    nR = len(r)
    initiated = pd.to_datetime(r["return_date"].values)
    # pickup attempts (courier failure model)
    fail_p = r["order_id"].map(
        orders.set_index("order_id")["courier"]).map(COURIERS).values
    attempts = 1 + (rng.random(nR) < fail_p).astype(int) \
        + (rng.random(nR) < fail_p * 0.3).astype(int)
    attempts = np.clip(attempts, 1, 3)
    d_pick_sched = rng.uniform(0.5, 2.0, nR) + (attempts - 1) * rng.uniform(2, 4, nR)
    d_transit = rng.uniform(2, 6, nR)
    picked_up = initiated + pd.to_timedelta(d_pick_sched, unit="D")
    received = picked_up + pd.to_timedelta(d_transit, unit="D")
    # QC Monday batch: next Monday strictly after received
    dow = received.dayofweek.values
    to_monday = ((7 - dow) % 7)
    to_monday[to_monday == 0] = 7
    qc_done = (received + pd.to_timedelta(to_monday + rng.uniform(0, 0.3, nR), unit="D"))
    refund_issued = qc_done + pd.to_timedelta(rng.uniform(1, 3, nR), unit="D")

    stages = ["initiated", "pickup_scheduled", "picked_up", "received_at_wh",
              "qc_done", "refund_issued"]
    ts = [initiated, initiated + pd.to_timedelta(rng.uniform(0, 0.5, nR), unit="D"),
          picked_up, received, qc_done, refund_issued]
    # column_stack then ravel: row i gets (r_i, s_0..s_5) in order.
    # (A plain concatenate would misalign stages across returns.)
    stage_ts = np.column_stack([t.values for t in ts]).ravel()
    journey = pd.DataFrame({
        "return_id": np.repeat(r["return_id"].values, 6),
        "stage": np.tile(stages, nR),
        "stage_ts": stage_ts,
    })
    # 30% missing courier handoff scan
    miss = (journey["stage"] == "picked_up") & (rng.random(len(journey)) < 0.30)
    journey.loc[miss, "stage_ts"] = pd.NaT
    journey = journey.sort_values(["return_id", "stage_ts"]).reset_index(drop=True)
    returns["pickup_attempts"] = attempts

    # ---------------------------------------------------------------- 6. qc_outcomes
    qmap = {"bracketing": [0.92, 0.05, 0.03], "size_fit": [0.88, 0.07, 0.05],
            "quality_issue": [0.30, 0.20, 0.50], "damaged_transit": [0.10, 0.75, 0.15],
            "wrong_item": [0.85, 0.10, 0.05], "remorse": [0.90, 0.07, 0.03],
            "other": [0.80, 0.12, 0.08]}
    probs = np.array([qmap[t] for t in r["true_reason"].values])
    qc_res = np.array(["resellable", "damaged", "defective"])[
        (rng.random((nR, 1)) < probs.cumsum(1)).argmax(1)]
    qc_outcomes = pd.DataFrame({
        "return_id": r["return_id"].values,
        "qc_result": qc_res,
        "refurb_cost": np.where(qc_res == "resellable",
                                np.clip(rng.normal(45, 12, nR), 10, 120).round(0), 0),
        "qc_agent": rng.choice([f"QC-{i:02d}" for i in range(1, 25)], nR),
    })

    # ---------------------------------------------------------------- 7. refunds
    # skip refunds for duplicates + 1% "never issued" exceptions
    has_refund = ~(returns["is_duplicate"].values)
    has_refund[rng.random(n_ret_all) < 0.01] = False
    rf = returns[has_refund].reset_index(drop=True)
    nrf = len(rf)
    issued = pd.to_datetime(
        journey[journey["stage"] == "refund_issued"]
        .drop_duplicates("return_id").set_index("return_id")
        .loc[rf["return_id"], "stage_ts"].values)
    wh = rf["order_id"].map(orders.set_index("order_id")["warehouse_id"]).values
    n_days = rng.integers(2, 6, nrf)
    credited = issued + pd.to_timedelta(n_days, unit="D")
    biz = wh == "WH-Mumbai"          # business-day warehouse: push over weekends
    dow_i = issued.dayofweek.values
    extra = np.zeros(nrf)
    extra[biz] = 2 * ((dow_i[biz] + n_days[biz]) // 7)
    credited = credited + pd.to_timedelta(extra, unit="D")
    refunds = pd.DataFrame({
        "return_id": rf["return_id"].values,
        "refund_initiated_at": issued,
        "refund_credited_at": credited,
        "refund_mode": rng.choice(["source", "bank_transfer", "wallet"], nrf,
                                  p=[0.7, 0.2, 0.1]),
        "days_basis": np.where(biz, "business", "calendar"),  # seeded inconsistency
    })
    total_days = (refunds["refund_credited_at"] - pd.to_datetime(
        rf["return_date"].values)).dt.days
    refunds["sla_breach_flag"] = total_days > 14

    # ---------------------------------------------------------------- 8. cx_tickets (~90K)
    n_tix = int(90_000 * S)
    t_ret = rng.choice(rf["return_id"].values, n_tix)
    t_cust = rf.set_index("return_id").loc[t_ret, "order_id"].map(
        orders.set_index("order_id")["customer_id"]).values
    t_created = pd.to_datetime(rf.set_index("return_id").loc[t_ret, "return_date"].values) \
        + pd.to_timedelta(rng.integers(0, 20, n_tix), unit="D")
    breach = refunds.set_index("return_id").loc[t_ret, "sla_breach_flag"].values
    p_wismo = np.where(breach, 0.55, 0.18)
    u = rng.random(n_tix)
    t_cat = np.where(u < p_wismo, "WISMO",
                     np.where(u < p_wismo + 0.15, "pickup_issue", "quality"))
    cx_tickets = pd.DataFrame({
        "ticket_id": [f"TIX-{i:06d}" for i in range(n_tix)],
        "customer_id": t_cust,
        "return_id": t_ret,
        "created_at": t_created,
        "category": t_cat,
        "handle_mins": np.clip(rng.normal(11, 5, n_tix), 2, 45).round(0),
    })

    # ---------------------------------------------------------------- 9. trust score refresh
    ret_per_cust = returns["order_id"].map(
        orders.set_index("order_id")["customer_id"]).value_counts()
    ord_per_cust = orders["customer_id"].value_counts()
    rr = (ret_per_cust / ord_per_cust).fillna(0)
    customers = customers.set_index("customer_id")
    customers["trust_score"] = np.clip(
        customers["trust_score"]
        + (customers["signup_date"] < "2024-01-01").astype(int) * 8
        - (customers.index.map(rr).fillna(0) * 60), 5, 99).round(1)
    customers = customers.reset_index()

    # ---------------------------------------------------------------- write out
    tables = {
        "customers": customers[["customer_id", "signup_date", "city_tier",
                                "acquisition_channel", "trust_score"]],
        "orders": orders[["order_id", "customer_id", "order_date", "basket_value",
                          "discount", "channel"]],
        "order_lines": lines[["line_id", "order_id", "sku", "category", "size", "price"]],
        "shipments": shipments,
        "returns": returns[["return_id", "line_id", "order_id", "sku", "size",
                            "return_date", "reason_code", "refund_amount",
                            "pickup_attempts"]],
        "return_journey": journey,
        "qc_outcomes": qc_outcomes,
        "refunds": refunds,
        "cx_tickets": cx_tickets,
    }
    # NOTE: true_reason + is_duplicate + is_bracketing_order are GENERATOR-ONLY
    # columns. They are intentionally NOT written out — the analyst must derive
    # bracketing and triangulate reasons from the noisy data. (Kept in memory
    # for our own validation only.)
    for name, df in tables.items():
        df.to_csv(out / f"{name}.csv", index=False)

    # data dictionary
    dd = ["# DATA DICTIONARY — Vastra Returns Fix (synthetic)",
          "",
          "> Generated by `data_generator.py`. All data is synthetic. Key known",
          "> inconsistencies are listed under each table; the analyst is expected",
          "> to discover and handle them.",
          ""]
    notes = {
        "customers": "trust_score 0-100; higher = older, well-behaved customers.",
        "orders": "12 months of 2025; festive spike Oct-Nov baked in.",
        "order_lines": "1-3 lines/order; sizes follow category size systems.",
        "shipments": "forward_cost/reverse_cost in Rs; warehouse drives refund day-basis.",
        "returns": "line_id links each return to its exact order line (size included, "
                   "so bracketing lines stay distinguishable). reason_code is CUSTOMER-SELECTED "
                   "and noisy: 'other' ~18%, 'damaged' over-selected (~2x) as customers game "
                   "free pickup. Contains ~0.4% undiscovered duplicate app-retry rows — "
                   "true dupes share (order_id, line_id). "
                   "pickup_attempts: 1-3 (courier failure model).",
        "return_journey": "Event stream, 6 stages. 30% of pickup scans missing "
                         "(stage_ts null). qc_done clusters on Mondays (batch QC).",
        "qc_outcomes": "qc_result in {resellable, damaged, defective}.",
        "refunds": "days_basis: WH-Mumbai = business days, WH-Delhi = calendar "
                  "days (seeded inconsistency). sla_breach_flag = initiated->credited > 14 days. "
                  "~1% of returns never got a refund row (exception cases).",
        "cx_tickets": "WISMO = 'where is my refund'; breach returns generate ~3x tickets.",
    }
    for name, df in tables.items():
        dd.append(f"## {name} ({len(df):,} rows)")
        dd.append(notes[name])
        dd.append("")
        for c in df.columns:
            dd.append(f"- `{c}` ({df[c].dtype})")
        dd.append("")
    (out / "DATA_DICTIONARY.md").write_text("\n".join(dd))

    # verification summary
    rr_line = len(returns) / len(lines) * 100
    print(f"customers   : {len(customers):,}")
    print(f"orders      : {len(orders):,}")
    print(f"order_lines : {len(lines):,}")
    print(f"returns     : {len(returns):,}  (line-level return rate {rr_line:.1f}%)")
    print(f"journey evts: {len(journey):,}")
    print(f"refunds     : {len(refunds):,}  (breach rate {refunds['sla_breach_flag'].mean()*100:.1f}%)")
    print(f"cx_tickets  : {len(cx_tickets):,}")
    print(f"WISMO share : {(cx_tickets['category'] == 'WISMO').mean()*100:.1f}%")
    print(f"'other' reason share: {(returns['reason_code'] == 'other').mean()*100:.1f}%")
    print("OK - files written to", out.resolve())


if __name__ == "__main__":
    main()
