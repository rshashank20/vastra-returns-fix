-- ============================================================
-- 05 — Cost concentration: which customers drive the bleed?
-- Requires: 00_cost_view.sql  (v_return_cost)
-- QUESTION: What % of customers drive what % of return cost?
-- (Expectation: a small minority drives the majority — the core
-- argument against a blanket fee and for a segmented policy.)
-- ============================================================
WITH cust AS (
    SELECT customer_id,
           COUNT(*) AS n_returns,
           SUM(total_cost) AS tc
    FROM v_return_cost
    GROUP BY customer_id
),
dec AS (
    SELECT *, NTILE(10) OVER (ORDER BY tc DESC) AS decile
    FROM cust
)
SELECT
    decile,
    COUNT(*) AS n_customers,
    SUM(n_returns) AS returns_in_decile,
    ROUND(SUM(tc) / 100000, 1) AS cost_lakh,
    ROUND(SUM(tc) * 100.0 / SUM(SUM(tc)) OVER (), 1) AS pct_of_total_cost,
    ROUND(SUM(SUM(tc)) OVER (ORDER BY decile
                             ROWS BETWEEN UNBOUNDED PRECEDING
                                      AND CURRENT ROW)
          * 100.0 / SUM(SUM(tc)) OVER (), 1) AS cumulative_pct
FROM dec
GROUP BY decile
ORDER BY decile;
