-- ============================================================
-- 11 — WISMO cost of slowness: what does delay cost in CX tickets?
-- Requires: 00_cost_view.sql  (v_return_cost)
-- QUESTION: How many "where is my refund" tickets does each breach
--           bucket generate? (Puts a rupee-adjacent number on slowness.)
-- ============================================================
WITH b AS (
    SELECT v.return_id,
           COALESCE(r.sla_breach_flag, 0) AS breached
    FROM v_return_cost v
    LEFT JOIN refunds r ON r.return_id = v.return_id
),
t AS (
    SELECT return_id, COUNT(*) AS n_wismo,
           SUM(handle_mins) AS wismo_mins
    FROM cx_tickets
    WHERE category = 'WISMO'
    GROUP BY return_id
)
SELECT CASE WHEN b.breached = 1 THEN 'breached' ELSE 'clean' END AS grp,
    COUNT(*) AS n_returns,
    COALESCE(SUM(t.n_wismo), 0) AS wismo_tickets,
    ROUND(COALESCE(SUM(t.n_wismo), 0) * 100.0 / COUNT(*), 1)
        AS wismo_per_100_returns,
    ROUND(COALESCE(SUM(t.wismo_mins), 0) / 60.0, 0) AS wismo_agent_hours,
    ROUND(COALESCE(SUM(t.wismo_mins), 0) * 4.0 / 100000, 2)
        AS wismo_cost_lakh
FROM b
LEFT JOIN t ON t.return_id = b.return_id
GROUP BY b.breached;
