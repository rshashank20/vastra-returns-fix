-- ============================================================
-- 01 — Fully-loaded cost per return (HEADLINE)
-- Requires: 00_cost_view.sql  (v_return_cost)
-- QUESTION: What does one return REALLY cost Vastra?
-- ============================================================
SELECT 'HEADLINE' AS view,
       COUNT(*) AS n_returns,
       ROUND(AVG(total_cost), 0)             AS avg_cost_per_return_rs,
       ROUND(SUM(total_cost) / 10000000, 2)  AS total_cost_cr,
       ROUND(AVG(c_reverse), 0)             AS avg_reverse_ship,
       ROUND(AVG(c_forward_waste), 0)       AS avg_forward_waste,
       ROUND(AVG(c_qc_labour), 0)           AS avg_qc_labour,
       ROUND(AVG(c_refurb), 0)              AS avg_refurb,
       ROUND(AVG(c_cx), 0)                  AS avg_cx_cost,
       ROUND(AVG(c_holding), 0)             AS avg_holding,
       ROUND(AVG(c_writeoff), 0)            AS avg_writeoff
FROM v_return_cost;
