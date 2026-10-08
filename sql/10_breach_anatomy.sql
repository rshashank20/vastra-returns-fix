-- ============================================================
-- 10 — SLA breach anatomy: which stage delay predicts breach?
-- Requires: 00_cost_view.sql  (v_return_cost)
-- QUESTION: When refunds breach the 14-day SLA, which stage is to blame?
-- (Compare average stage durations for breached vs clean refunds —
--  the stage with the biggest gap is the driver.)
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
    SELECT v.return_id,
        COALESCE(r.sla_breach_flag, 0) AS breached,
        JULIANDAY(p.t_sched)    - JULIANDAY(p.t_initiated) AS d_sched,
        JULIANDAY(p.t_picked)   - JULIANDAY(p.t_sched)     AS d_pickup,
        JULIANDAY(p.t_received) - JULIANDAY(p.t_picked)    AS d_transit,
        JULIANDAY(p.t_qc)       - JULIANDAY(p.t_received)  AS d_qc,
        JULIANDAY(p.t_issued)   - JULIANDAY(p.t_qc)         AS d_refund
    FROM piv p
    JOIN v_return_cost v ON v.return_id = p.return_id
    LEFT JOIN refunds r  ON r.return_id = v.return_id
)
SELECT CASE WHEN breached = 1 THEN 'BREACHED (>14d)' ELSE 'clean' END AS grp,
    COUNT(*) AS n,
    ROUND(AVG(d_sched), 1)   AS avg_sched,
    ROUND(AVG(d_pickup), 1)  AS avg_pickup,
    ROUND(AVG(d_transit), 1) AS avg_transit,
    ROUND(AVG(d_qc), 1)      AS avg_qc,
    ROUND(AVG(d_refund), 1)  AS avg_refund
FROM durs
GROUP BY breached;
