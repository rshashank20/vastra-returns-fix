-- ============================================================
-- 03 — True-reason triangulation: customers lie, QC + patterns don't
-- Requires: 00_cost_view.sql  (v_return_cost, v_bracketing_orders)
-- QUESTION: What share of returns is genuinely quality/damage vs
--           bracketing vs fit/remorse, once we correct the lies?
--
-- METHOD (documented judgment):
--   1. Flag bracketing returns: return belongs to an order where the
--      same customer bought the same SKU in 3+ sizes (v_bracketing_orders).
--   2. Cross claimed reason x QC outcome.
--   3. CASE reclassification into true_reason buckets (rules below).
--
-- NOTE: 'genuine_damage' requires the customer to have claimed damage AND
-- QC to confirm it. Claimed damage + resellable QC = gaming the free pickup.
-- Buckets are QC-led for the expensive outcomes so no large 'other' bucket
-- survives: every damaged/defective item lands in a named bucket.
-- ============================================================

-- 3a. The cross-tab: claimed reason x QC outcome (spot the lies)
SELECT
    v.reason_code  AS claimed,
    v.qc_result    AS qc_found,
    COUNT(*)       AS n,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct
FROM v_return_cost v
GROUP BY v.reason_code, v.qc_result
ORDER BY n DESC;

-- 3b. The triangulation: CASE rules -> true_reason
WITH flagged AS (
    SELECT v.*,
           CASE WHEN b.order_id IS NOT NULL THEN 1 ELSE 0 END AS is_bracketing
    FROM v_return_cost v
    LEFT JOIN v_bracketing_orders b
           ON b.order_id = v.order_id AND b.sku = v.sku
),
classified AS (
    SELECT *,
        CASE
            WHEN is_bracketing = 1 THEN 'bracketing'
            WHEN reason_code = 'quality_issue' AND qc_result = 'defective'
                THEN 'quality_failure'
            WHEN reason_code = 'damaged' AND qc_result = 'damaged'
                THEN 'genuine_damage'
            WHEN qc_result = 'damaged' THEN 'damaged_item_other_claim'
            WHEN qc_result = 'defective' THEN 'defective_item_other_claim'
            WHEN reason_code = 'damaged' AND qc_result = 'resellable'
                THEN 'fake_damage_claim'
            WHEN reason_code IN ('size_fit', 'changed_mind', 'other')
                 AND qc_result = 'resellable' AND is_bracketing = 0
                THEN 'fit_or_remorse'
            WHEN reason_code = 'wrong_item' AND qc_result = 'resellable'
                THEN 'wrong_item'
            WHEN qc_result IS NULL THEN 'unknown_qc'
            ELSE 'other_true'
        END AS true_reason
    FROM flagged
)
SELECT
    true_reason,
    COUNT(*) AS n_returns,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) AS pct_of_returns,
    ROUND(AVG(total_cost), 0)  AS avg_cost_per_return,
    ROUND(SUM(total_cost) / 100000, 1) AS total_cost_lakh,
    ROUND(SUM(total_cost) * 100.0 / SUM(SUM(total_cost)) OVER (), 1)
        AS pct_of_total_cost
FROM classified
GROUP BY true_reason
ORDER BY SUM(total_cost) DESC;
