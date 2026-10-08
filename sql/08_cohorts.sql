-- ============================================================
-- 08 — Cohort analysis: do acquired customers return more?
-- Requires: 00_cost_view.sql  (v_return_cost)
-- QUESTION: Does return rate vary by acquisition channel / cohort?
-- (If paid-ads customers return far more, CAC math is overstated and
-- marketing is buying the returns problem.)
-- ============================================================
WITH cust_ord AS (
    SELECT c.customer_id, c.acquisition_channel,
           STRFTIME('%Y', c.signup_date) || '-Q'
               || (CAST(STRFTIME('%m', c.signup_date) AS INTEGER) / 4 + 1)
               AS cohort,
           COUNT(DISTINCT o.order_id) AS n_orders
    FROM customers c
    LEFT JOIN orders o ON o.customer_id = c.customer_id
    GROUP BY c.customer_id, c.acquisition_channel, cohort
),
cust_ret AS (
    SELECT customer_id, COUNT(*) AS n_returns
    FROM v_return_cost
    GROUP BY customer_id
)
SELECT
    co.acquisition_channel,
    co.cohort,
    COUNT(*) AS n_customers,
    SUM(co.n_orders) AS total_orders,
    COALESCE(SUM(cr.n_returns), 0) AS total_returns,
    ROUND(COALESCE(SUM(cr.n_returns), 0) * 100.0
          / NULLIF(SUM(co.n_orders), 0), 1) AS returns_per_100_orders
FROM cust_ord co
LEFT JOIN cust_ret cr ON cr.customer_id = co.customer_id
GROUP BY co.acquisition_channel, co.cohort
ORDER BY co.cohort, returns_per_100_orders DESC;
