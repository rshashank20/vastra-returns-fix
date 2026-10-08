-- ============================================================
-- 06 — SKU return-toxicity: which products should be fixed/delisted?
-- Requires: 00_cost_view.sql  (v_return_cost)
-- QUESTION: Which SKUs combine high return rate x high cost x volume?
-- toxicity = return_rate x avg_cost_per_return x n_returns
-- (A SKU can be toxic via rate, via cost, or via sheer volume.)
-- ============================================================
WITH sold AS (
    SELECT sku, category, COUNT(*) AS n_sold, AVG(price) AS avg_price
    FROM order_lines
    GROUP BY sku, category
),
ret AS (
    SELECT sku, COUNT(*) AS n_ret, AVG(total_cost) AS avg_cost
    FROM v_return_cost
    GROUP BY sku
)
SELECT
    s.sku,
    s.category,
    s.n_sold,
    r.n_ret AS n_returns,
    ROUND(r.n_ret * 100.0 / s.n_sold, 1) AS return_rate_pct,
    ROUND(r.avg_cost, 0) AS avg_cost_per_return,
    ROUND(r.n_ret * 100.0 / s.n_sold * r.avg_cost * r.n_ret / 100000, 1)
        AS toxicity_index,
    ROUND(r.n_ret * r.avg_cost / 100000, 1) AS total_cost_lakh
FROM sold s
JOIN ret r ON r.sku = s.sku
WHERE s.n_sold >= 50
ORDER BY toxicity_index DESC
LIMIT 30;
