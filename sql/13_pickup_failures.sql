-- ============================================================
-- 13 — Pickup failures: which courier, where?
-- Requires: 00_cost_view.sql  (v_return_cost)
-- QUESTION: Where do pickups fail (attempts > 1), by courier x city tier?
-- (Feeds the courier-SLA recommendation: penalties need a number.)
-- ============================================================
SELECT v.courier, c.city_tier,
    COUNT(*) AS n_returns,
    ROUND(AVG(v.pickup_attempts), 2) AS avg_attempts,
    ROUND(AVG(CASE WHEN v.pickup_attempts > 1 THEN 1.0 ELSE 0 END) * 100, 1)
        AS pct_needing_reattempt,
    ROUND(AVG(CASE WHEN v.pickup_attempts > 2 THEN 1.0 ELSE 0 END) * 100, 1)
        AS pct_needing_3_attempts
FROM v_return_cost v
JOIN customers c ON c.customer_id = v.customer_id
GROUP BY v.courier, c.city_tier
ORDER BY pct_needing_reattempt DESC;
