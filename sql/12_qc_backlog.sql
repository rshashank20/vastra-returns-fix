-- ============================================================
-- 12 — QC backlog dynamics: arrivals vs completions
-- Requires: 00_cost_view.sql  (v_return_cost)
-- QUESTION: Does QC keep up with arrivals, or does a backlog build?
-- (backlog = running total of arrivals minus completions per warehouse)
-- ============================================================
WITH ev AS (
    SELECT DATE(j.stage_ts) AS d, v.warehouse_id,
        SUM(CASE WHEN j.stage = 'received_at_wh' THEN 1 ELSE 0 END) AS arrivals,
        SUM(CASE WHEN j.stage = 'qc_done'        THEN 1 ELSE 0 END) AS completions
    FROM return_journey j
    JOIN v_return_cost v ON v.return_id = j.return_id
    WHERE j.stage IN ('received_at_wh', 'qc_done') AND j.stage_ts IS NOT NULL
    GROUP BY d, v.warehouse_id
),
bl AS (
    SELECT d, warehouse_id, arrivals, completions,
        SUM(arrivals - completions) OVER (
            PARTITION BY warehouse_id ORDER BY d
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS backlog
    FROM ev
)
SELECT warehouse_id,
    ROUND(AVG(arrivals), 1) AS avg_daily_arrivals,
    ROUND(AVG(completions), 1) AS avg_daily_completions,
    MAX(backlog) AS peak_backlog_units,
    ROUND(AVG(backlog), 0) AS avg_backlog_units,
    SUM(CASE WHEN backlog > 200 THEN 1 ELSE 0 END) AS days_over_200_backlog
FROM bl
GROUP BY warehouse_id;

-- monthly trend (for the chart)
SELECT SUBSTR(d, 1, 7) AS month, warehouse_id,
       ROUND(AVG(backlog), 0) AS avg_backlog
FROM (SELECT d, warehouse_id, arrivals, completions,
             SUM(arrivals - completions) OVER (
                 PARTITION BY warehouse_id ORDER BY d
                 ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS backlog
      FROM (SELECT DATE(j.stage_ts) AS d, v.warehouse_id,
                   SUM(CASE WHEN j.stage = 'received_at_wh' THEN 1 ELSE 0 END) AS arrivals,
                   SUM(CASE WHEN j.stage = 'qc_done' THEN 1 ELSE 0 END) AS completions
            FROM return_journey j
            JOIN v_return_cost v ON v.return_id = j.return_id
            WHERE j.stage IN ('received_at_wh', 'qc_done') AND j.stage_ts IS NOT NULL
            GROUP BY d, v.warehouse_id))
GROUP BY month, warehouse_id
ORDER BY month, warehouse_id;
