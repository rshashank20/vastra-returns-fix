-- ============================================================
-- 02 — Cost by reason x category: WHERE does the Rs 18.2 cr go?
-- Requires: 00_cost_view.sql  (v_return_cost)
-- QUESTION: Which reason x category cells bleed the most?
--
-- CAVEAT: reason_code is CUSTOMER-SELECTED and noisy ('damaged' ~2x
-- over-selected, 'other' ~21%). This shows *claimed* reasons; 03
-- triangulates the *true* reasons. Don't present this as root cause.
-- ============================================================
SELECT
    reason_code,
    category,
    COUNT(*) AS n_returns,
    ROUND(AVG(total_cost), 0) AS avg_cost_per_return,
    ROUND(SUM(total_cost) / 100000, 1) AS total_cost_lakh,
    ROUND(SUM(total_cost) * 100.0 / SUM(SUM(total_cost)) OVER (), 1)
        AS pct_of_total_cost
FROM v_return_cost
GROUP BY reason_code, category
ORDER BY SUM(total_cost) DESC;
