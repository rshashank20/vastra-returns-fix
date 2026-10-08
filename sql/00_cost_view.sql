-- ============================================================
-- 00 — Shared cost model (RUN THIS FIRST)
-- Vastra "Returns Fix" · Project 2
--
-- Creates v_return_cost: one row per return with the FULLY-LOADED cost
-- broken into components. Every later analysis builds on this view, so
-- the assumptions live in exactly one place.
--
-- COST MODEL (documented assumptions):
--   A1  reverse shipping       = shipments.reverse_cost (actual, Rs)
--   A2  forward shipping waste = shipments.forward_cost  (actual)
--   A3  QC labour              = Rs 35 per inspection    (assumption: ~10 min @ Rs 210/hr)
--   A4  refurb                 = qc_outcomes.refurb_cost (actual; 0 if not resellable)
--   A5  CX handle cost         = handle_mins x Rs 4/min  (assumption: Rs 240/hr agent cost)
--   A6  dead-inventory holding = journey_days x price x 12% / 365
--                                (assumption: 12% annual holding rate)
--   A7  write-off              = price x 55% when qc_result in ('damaged','defective')
--                                (assumption: COGS ~55% of selling price)
--
-- DEDUP: ~0.4% app-retry duplicates share (order_id, line_id); keep first.
-- ============================================================

DROP VIEW IF EXISTS v_return_cost;
CREATE VIEW v_return_cost AS
WITH dedup AS (
    SELECT r.*,
           ROW_NUMBER() OVER (PARTITION BY r.order_id, r.line_id
                              ORDER BY r.return_id) AS rn
    FROM returns r
),
ret AS (
    SELECT * FROM dedup WHERE rn = 1
),
line_info AS (
    SELECT line_id, category, size, price FROM order_lines
),
journey_days AS (
    SELECT return_id,
           JULIANDAY(MAX(stage_ts)) - JULIANDAY(MIN(stage_ts)) AS jdays
    FROM return_journey
    WHERE stage_ts IS NOT NULL
    GROUP BY return_id
),
cx AS (
    SELECT return_id, COALESCE(SUM(handle_mins), 0) AS mins
    FROM cx_tickets
    GROUP BY return_id
)
SELECT
    ret.return_id, ret.line_id, ret.order_id, ret.sku,
    ret.return_date, ret.reason_code, ret.refund_amount, ret.pickup_attempts,
    o.customer_id,
    li.category, li.size, li.price,
    s.warehouse_id, s.courier, s.reverse_cost, s.forward_cost,
    q.qc_result, q.refurb_cost,
    COALESCE(j.jdays, 0)                                          AS journey_days,
    COALESCE(s.reverse_cost, 0)                                   AS c_reverse,
    COALESCE(s.forward_cost, 0)                                   AS c_forward_waste,
    35.0                                                          AS c_qc_labour,
    COALESCE(q.refurb_cost, 0)                                    AS c_refurb,
    COALESCE(cx.mins, 0) * 4.0                                    AS c_cx,
    COALESCE(j.jdays, 0) * li.price * 0.12 / 365.0                 AS c_holding,
    CASE WHEN q.qc_result IN ('damaged', 'defective')
         THEN li.price * 0.55 ELSE 0.0 END                         AS c_writeoff,
    (COALESCE(s.reverse_cost, 0) + COALESCE(s.forward_cost, 0) + 35.0
     + COALESCE(q.refurb_cost, 0) + COALESCE(cx.mins, 0) * 4.0
     + COALESCE(j.jdays, 0) * li.price * 0.12 / 365.0
     + CASE WHEN q.qc_result IN ('damaged', 'defective')
            THEN li.price * 0.55 ELSE 0.0 END)                     AS total_cost
FROM ret
JOIN orders o        ON o.order_id  = ret.order_id
LEFT JOIN line_info li   ON li.line_id  = ret.line_id
LEFT JOIN shipments s    ON s.order_id  = ret.order_id
LEFT JOIN qc_outcomes q  ON q.return_id = ret.return_id
LEFT JOIN cx             ON cx.return_id = ret.return_id
LEFT JOIN journey_days j ON j.return_id = ret.return_id;

-- Bracketing orders: same customer + same SKU + 3+ distinct sizes in one order
DROP VIEW IF EXISTS v_bracketing_orders;
CREATE VIEW v_bracketing_orders AS
SELECT o.customer_id, ol.order_id, ol.sku
FROM order_lines ol
JOIN orders o ON o.order_id = ol.order_id
GROUP BY o.customer_id, ol.order_id, ol.sku
HAVING COUNT(DISTINCT ol.size) >= 3;
