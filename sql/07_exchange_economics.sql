-- ============================================================
-- 07 — Exchange-vs-refund economics: does the sale survive?
-- Requires: 00_cost_view.sql  (v_return_cost)
-- QUESTION: When a customer returns, do they buy again quickly
--           (exchange-like behaviour, sale retained) or disappear
--           (refund, sale lost)? What is each path worth?
--
-- PROXY (documented): no explicit exchange events exist in the data, so
-- a return followed by a new order from the same customer within 14 days
-- is treated as the "retained sale" path. This is an assumption, not a
-- measured exchange — label it as such in the memo.
-- ============================================================
WITH nxt AS (
    SELECT v.return_id, v.customer_id, v.return_date, v.refund_amount,
           MIN(o.order_date) AS next_order_date,
           MIN(o.basket_value) AS next_basket
    FROM v_return_cost v
    LEFT JOIN orders o
           ON o.customer_id = v.customer_id
          AND o.order_date > v.return_date
          AND o.order_date <= DATE(v.return_date, '+14 days')
    GROUP BY v.return_id, v.customer_id, v.return_date, v.refund_amount
)
SELECT
    CASE WHEN next_order_date IS NOT NULL
         THEN 'reordered_within_14d (retained-sale path)'
         ELSE 'no_reorder (lost-sale path)' END AS path,
    COUNT(*) AS n_returns,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct,
    ROUND(AVG(refund_amount), 0) AS avg_refund_given,
    ROUND(AVG(next_basket), 0)  AS avg_next_basket
FROM nxt
GROUP BY path;
