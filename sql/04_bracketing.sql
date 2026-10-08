-- ============================================================
-- 04 — Bracketing deep-dive: who are the serial bracketeers?
-- Requires: 00_cost_view.sql  (v_return_cost, v_bracketing_orders)
-- QUESTION: What % of customers bracket, and what share of cost do
--           they drive? (This is the segment a fee policy must target.)
-- ============================================================

-- 4a. Customer-level bracketing profile
WITH brack AS (
    SELECT v.customer_id,
           COUNT(DISTINCT b.order_id) AS n_bracketing_orders,
           COUNT(v.return_id)         AS n_bracketing_returns,
           SUM(v.total_cost)          AS bracketing_cost
    FROM v_return_cost v
    JOIN v_bracketing_orders b
      ON b.order_id = v.order_id AND b.sku = v.sku
    GROUP BY v.customer_id
),
tot AS (
    SELECT SUM(total_cost) AS grand_cost, COUNT(*) AS grand_n
    FROM v_return_cost
)
SELECT
    COUNT(*) AS n_bracketeers,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(DISTINCT customer_id)
                              FROM v_return_cost), 2) AS pct_of_returning_customers,
    SUM(n_bracketing_returns) AS bracketing_returns,
    ROUND(SUM(n_bracketing_returns) * 100.0
          / (SELECT grand_n FROM tot), 1) AS pct_of_all_returns,
    ROUND(SUM(bracketing_cost) / 100000, 1) AS bracketing_cost_lakh,
    ROUND(SUM(bracketing_cost) * 100.0
          / (SELECT grand_cost FROM tot), 1) AS pct_of_total_cost
FROM brack;

-- 4b. How concentrated are bracketeers? (returns per bracketeer)
SELECT
    n_bracketing_orders,
    COUNT(*) AS n_customers,
    ROUND(AVG(n_bracketing_returns), 1) AS avg_returns_each
FROM (
    SELECT v.customer_id,
           COUNT(DISTINCT b.order_id) AS n_bracketing_orders,
           COUNT(v.return_id) AS n_bracketing_returns
    FROM v_return_cost v
    JOIN v_bracketing_orders b
      ON b.order_id = v.order_id AND b.sku = v.sku
    GROUP BY v.customer_id
)
GROUP BY n_bracketing_orders
ORDER BY n_bracketing_orders;
