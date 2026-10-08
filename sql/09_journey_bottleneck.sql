-- ============================================================
-- 09 — Journey bottleneck: where do refunds get stuck?
-- Requires: 00_cost_view.sql  (v_return_cost)
-- QUESTION: Which stage (pickup scheduling, courier transit, QC backlog,
--           refund processing) adds the most days, by warehouse x courier?
--
-- NOTE: ~30% of pickup scans are missing (stage_ts null) — those rows are
-- excluded from the pickup-stage average, which slightly understates it.
-- ============================================================
WITH piv AS (
    SELECT return_id,
        MAX(CASE WHEN stage = 'initiated'         THEN stage_ts END) AS t_initiated,
        MAX(CASE WHEN stage = 'pickup_scheduled'  THEN stage_ts END) AS t_sched,
        MAX(CASE WHEN stage = 'picked_up'         THEN stage_ts END) AS t_picked,
        MAX(CASE WHEN stage = 'received_at_wh'    THEN stage_ts END) AS t_received,
        MAX(CASE WHEN stage = 'qc_done'           THEN stage_ts END) AS t_qc,
        MAX(CASE WHEN stage = 'refund_issued'     THEN stage_ts END) AS t_issued
    FROM return_journey
    WHERE stage_ts IS NOT NULL
    GROUP BY return_id
),
durs AS (
    SELECT v.warehouse_id, v.courier,
        JULIANDAY(p.t_sched)    - JULIANDAY(p.t_initiated) AS d_sched,
        JULIANDAY(p.t_picked)   - JULIANDAY(p.t_sched)     AS d_pickup,
        JULIANDAY(p.t_received) - JULIANDAY(p.t_picked)    AS d_transit,
        JULIANDAY(p.t_qc)       - JULIANDAY(p.t_received)  AS d_qc,
        JULIANDAY(p.t_issued)   - JULIANDAY(p.t_qc)         AS d_refund
    FROM piv p
    JOIN v_return_cost v ON v.return_id = p.return_id
)
SELECT warehouse_id, courier, COUNT(*) AS n_returns,
    ROUND(AVG(d_sched), 1)   AS avg_sched_days,
    ROUND(AVG(d_pickup), 1)  AS avg_pickup_days,
    ROUND(AVG(d_transit), 1) AS avg_transit_days,
    ROUND(AVG(d_qc), 1)      AS avg_qc_days,
    ROUND(AVG(d_refund), 1)  AS avg_refund_days,
    ROUND(AVG(COALESCE(d_sched,0) + COALESCE(d_pickup,0)
             + COALESCE(d_transit,0) + COALESCE(d_qc,0)
             + COALESCE(d_refund,0)), 1) AS avg_total_days
FROM durs
GROUP BY warehouse_id, courier
ORDER BY avg_total_days DESC;
