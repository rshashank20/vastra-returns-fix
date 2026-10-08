#!/usr/bin/env python3
"""Build the Returns Fix web dashboard (single self-contained index.html)."""
#!/usr/bin/env python3
"""Build the Returns Fix web dashboard (single self-contained index.html).

Usage:  python3 build_dashboard.py      # run from anywhere
Reads:  ../vastra.db  (build it first:  python3 ../data_generator.py --scale 1.0)
Writes: index.html next to this script. No other dependencies.
"""
import json
import sqlite3
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB = BASE.parent / "vastra.db"
OUT = BASE / "index.html"

con = sqlite3.connect(DB)
d = {}
d["true_reason"] = [dict(zip(["bucket", "n"], r)) for r in con.execute("""
WITH flagged AS (
    SELECT v.*,
           CASE WHEN b.order_id IS NOT NULL THEN 1 ELSE 0 END AS is_bracketing
    FROM v_return_cost v
    LEFT JOIN (SELECT DISTINCT order_id FROM (
        SELECT o.order_id FROM order_lines o
        GROUP BY o.order_id, o.sku HAVING COUNT(DISTINCT o.size) >= 3)) b
      ON b.order_id = v.order_id),
classified AS (
    SELECT CASE
        WHEN is_bracketing = 1 THEN 'bracketing'
        WHEN reason_code = 'quality_issue' AND qc_result = 'defective' THEN 'quality_failure'
        WHEN reason_code = 'damaged' AND qc_result = 'damaged' THEN 'genuine_damage'
        WHEN qc_result = 'damaged' THEN 'damaged_item_other_claim'
        WHEN qc_result = 'defective' THEN 'defective_item_other_claim'
        WHEN reason_code = 'damaged' AND qc_result = 'resellable' THEN 'fake_damage_claim'
        WHEN reason_code IN ('size_fit','changed_mind','other') AND qc_result = 'resellable'
             AND is_bracketing = 0 THEN 'fit_or_remorse'
        WHEN reason_code = 'wrong_item' AND qc_result = 'resellable' THEN 'wrong_item'
        WHEN qc_result IS NULL THEN 'unknown_qc'
        ELSE 'other_true' END AS bucket
    FROM flagged)
SELECT bucket, COUNT(*) FROM classified GROUP BY bucket ORDER BY COUNT(*) DESC""").fetchall()]
d["monthly"] = [dict(zip(["month", "n_returns", "cost_lakh"], r)) for r in con.execute("""
SELECT SUBSTR(return_date,1,7) AS m, COUNT(*), ROUND(SUM(total_cost)/100000,1)
FROM v_return_cost GROUP BY m ORDER BY m""").fetchall()]
d["stage_avg"] = dict(zip(["sched", "pickup", "transit", "qc", "refund"], con.execute("""
SELECT ROUND(AVG(d_sched),2), ROUND(AVG(d_pickup),2), ROUND(AVG(d_transit),2),
       ROUND(AVG(d_qc),2), ROUND(AVG(d_refund),2)
FROM (SELECT JULIANDAY(t1)-JULIANDAY(t0) AS d_sched, JULIANDAY(t2)-JULIANDAY(t1) AS d_pickup,
             JULIANDAY(t3)-JULIANDAY(t2) AS d_transit, JULIANDAY(t4)-JULIANDAY(t3) AS d_qc,
             JULIANDAY(t5)-JULIANDAY(t4) AS d_refund
      FROM (SELECT return_id,
                MAX(CASE WHEN stage='initiated' THEN stage_ts END) AS t0,
                MAX(CASE WHEN stage='pickup_scheduled' THEN stage_ts END) AS t1,
                MAX(CASE WHEN stage='picked_up' THEN stage_ts END) AS t2,
                MAX(CASE WHEN stage='received_at_wh' THEN stage_ts END) AS t3,
                MAX(CASE WHEN stage='qc_done' THEN stage_ts END) AS t4,
                MAX(CASE WHEN stage='refund_issued' THEN stage_ts END) AS t5
            FROM return_journey WHERE stage_ts IS NOT NULL GROUP BY return_id))""").fetchone()))
d["breach_anatomy"] = [dict(zip(["grp", "sched", "pickup", "transit", "qc", "refund"], r)) for r in con.execute("""
WITH piv AS (
    SELECT return_id,
        MAX(CASE WHEN stage='initiated' THEN stage_ts END) AS t0,
        MAX(CASE WHEN stage='pickup_scheduled' THEN stage_ts END) AS t1,
        MAX(CASE WHEN stage='picked_up' THEN stage_ts END) AS t2,
        MAX(CASE WHEN stage='received_at_wh' THEN stage_ts END) AS t3,
        MAX(CASE WHEN stage='qc_done' THEN stage_ts END) AS t4,
        MAX(CASE WHEN stage='refund_issued' THEN stage_ts END) AS t5
    FROM return_journey WHERE stage_ts IS NOT NULL GROUP BY return_id)
SELECT COALESCE(r.sla_breach_flag,0),
    ROUND(AVG(JULIANDAY(t1)-JULIANDAY(t0)),2), ROUND(AVG(JULIANDAY(t2)-JULIANDAY(t1)),2),
    ROUND(AVG(JULIANDAY(t3)-JULIANDAY(t2)),2), ROUND(AVG(JULIANDAY(t4)-JULIANDAY(t3)),2),
    ROUND(AVG(JULIANDAY(t5)-JULIANDAY(t4)),2)
FROM piv p JOIN v_return_cost v ON v.return_id = p.return_id
LEFT JOIN refunds r ON r.return_id = v.return_id GROUP BY 1""").fetchall()]
d["backlog"] = [dict(zip(["month", "wh", "avg_backlog"], r)) for r in con.execute("""
WITH ev AS (
    SELECT DATE(j.stage_ts) AS d, v.warehouse_id AS w,
        SUM(CASE WHEN j.stage='received_at_wh' THEN 1 ELSE 0 END) AS a,
        SUM(CASE WHEN j.stage='qc_done' THEN 1 ELSE 0 END) AS c
    FROM return_journey j JOIN v_return_cost v ON v.return_id = j.return_id
    WHERE j.stage IN ('received_at_wh','qc_done') AND j.stage_ts IS NOT NULL
    GROUP BY d, w),
bl AS (
    SELECT d, w, SUM(a-c) OVER (
        PARTITION BY w ORDER BY d ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS b
    FROM ev)
SELECT SUBSTR(d,1,7), w, ROUND(AVG(b)) FROM bl GROUP BY 1, 2 ORDER BY 1, 2""").fetchall()]
d["courier"] = [dict(zip(["courier", "reattempt_pct"], r)) for r in con.execute("""
SELECT courier, ROUND(AVG(CASE WHEN pickup_attempts > 1 THEN 1.0 ELSE 0 END)*100,1)
FROM v_return_cost GROUP BY courier ORDER BY 2 DESC""").fetchall()]
d["deciles"] = [dict(zip(["decile", "pct_cost", "cum_pct"], r)) for r in con.execute("""
WITH ranked AS (
    SELECT customer_id, SUM(total_cost) AS c,
           NTILE(10) OVER (ORDER BY SUM(total_cost) DESC) AS d
    FROM v_return_cost GROUP BY customer_id)
SELECT d,
    ROUND(SUM(c)*100.0/(SELECT SUM(c) FROM ranked),1),
    ROUND(SUM(SUM(c)) OVER (ORDER BY d)*100.0/(SELECT SUM(c) FROM ranked),1)
FROM ranked GROUP BY d ORDER BY d""").fetchall()]
d["toxic"] = [dict(zip(["sku", "category", "n_sold", "n_returns", "ret_rate", "avg_cost"], r)) for r in con.execute("""
WITH sold AS (
    SELECT sku, category, COUNT(*) AS n_sold FROM order_lines GROUP BY sku, category),
ret AS (
    SELECT sku, COUNT(*) AS n_returns, ROUND(AVG(total_cost)) AS avg_cost
    FROM v_return_cost GROUP BY sku)
SELECT s.sku, s.category, s.n_sold, COALESCE(r.n_returns,0),
       ROUND(COALESCE(r.n_returns,0)*100.0/s.n_sold,1), COALESCE(r.avg_cost,0)
FROM sold s LEFT JOIN ret r ON r.sku = s.sku
WHERE s.n_sold >= 500 ORDER BY 5 DESC LIMIT 15""").fetchall()]
con.close()

PRETTY = {
    "bracketing": "Bracketing", "fit_or_remorse": "Fit / remorse",
    "fake_damage_claim": "Fake damage claim", "quality_failure": "Quality failure",
    "genuine_damage": "Genuine damage", "damaged_item_other_claim": "Damaged (other claim)",
    "defective_item_other_claim": "Defective (other claim)", "wrong_item": "Wrong item",
    "other_true": "Other",
}
d["pretty"] = PRETTY
DATA = json.dumps(d)

html_head = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Returns Fix — Vastra</title>
<script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#0e1319;color:#e8edf3;font-family:-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;line-height:1.5}
.wrap{max-width:1180px;margin:0 auto;padding:32px 20px 64px}
header.hero{padding:28px 0 8px;border-bottom:1px solid #232d3a;margin-bottom:28px}
header.hero .kicker{color:#f0b429;font-size:12px;letter-spacing:3px;text-transform:uppercase;margin-bottom:8px}
header.hero h1{font-size:34px;font-weight:700;letter-spacing:-.5px}
header.hero p{color:#9aa4b2;max-width:720px;margin-top:8px;font-size:15px}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:24px 0 8px}
.kpi{background:#161e28;border:1px solid #232d3a;border-radius:12px;padding:18px}
.kpi .v{font-size:30px;font-weight:700;color:#fff}
.kpi .v small{font-size:15px;color:#9aa4b2;font-weight:400}
.kpi .l{color:#9aa4b2;font-size:12.5px;margin-top:4px}
.kpi.hl{border-color:#f0b429}
.kpi.hl .v{color:#f0b429}
section{margin-top:44px}
section h2{font-size:21px;margin-bottom:4px}
section .sub{color:#9aa4b2;font-size:13.5px;margin-bottom:18px;max-width:760px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.card{background:#161e28;border:1px solid #232d3a;border-radius:12px;padding:18px;min-height:120px}
.card h3{font-size:14px;font-weight:600;margin-bottom:2px}
.card .note{color:#9aa4b2;font-size:12px;margin-bottom:10px}
.callout{background:#1a1407;border:1px solid #f0b429;border-radius:12px;padding:20px;margin-top:14px}
.callout b{color:#f0b429}
table{width:100%;border-collapse:collapse;font-size:13px}
th{text-align:left;color:#9aa4b2;font-weight:500;padding:8px;border-bottom:1px solid #232d3a}
td{padding:8px;border-bottom:1px solid #1c2530}
tr:hover td{background:#1a2230}
footer{margin-top:56px;padding-top:20px;border-top:1px solid #232d3a;color:#9aa4b2;font-size:12.5px}
footer a{color:#f0b429}
@media(max-width:860px){.kpis{grid-template-columns:repeat(2,1fr)}.grid2{grid-template-columns:1fr}}
</style></head>
<body><div class="wrap">
<header class="hero">
<div class="kicker">Vastra &middot; D2C fashion &middot; returns analytics</div>
<h1>The Returns Fix</h1>
<p>Leadership thought a return cost &#8377;88. Customers thought refunds took forever.
Both were right about the feeling and wrong about the scale. This dashboard is the
full picture: what a return really costs, why customers really return, where refunds
get stuck, and the policy that fixes it.</p>
</header>
<div class="kpis">
<div class="kpi"><div class="v">&#8377;18.16 <small>cr / yr</small></div><div class="l">Fully-loaded return cost</div></div>
<div class="kpi"><div class="v">&#8377;511 <small>/ return</small></div><div class="l">vs &#8377;88 perceived (6&times; the assumed cost)</div></div>
<div class="kpi"><div class="v">56.8<small>%</small></div><div class="l">Refunds breaching the 14-day SLA</div></div>
<div class="kpi hl"><div class="v">+&#8377;3.48 <small>cr / yr</small></div><div class="l">Segmented policy upside (modelled)</div></div>
</div>
<section><h2>1 &middot; The bleed</h2>
<div class="sub">A return is not the &#8377;88 reverse-shipping fee. It is seven cost layers, and the biggest one &mdash; write-offs &mdash; is invisible in the shipping ledger.</div>
<div class="grid2">
<div class="card"><h3>How &#8377;88 becomes &#8377;511</h3><div class="note">Fully-loaded cost per return, by component</div><div id="wf"></div></div>
<div class="card"><h3>What returns really are</h3><div class="note">Triangulated true reason: claimed reason &times; QC outcome &times; ordering pattern</div><div id="donut"></div></div>
</div>
<div class="card" style="margin-top:14px"><h3>Returns and cost through 2025</h3><div class="note">Monthly volume vs cost &mdash; the bleed never stops</div><div id="monthly"></div></div>
</section>
<section><h2>2 &middot; The journey</h2>
<div class="sub">Refunds take ~12 days and breach SLA 56.8% of the time. The delay is not everywhere &mdash; it is in two specific stages.</div>
<div class="grid2">
<div class="card"><h3>Where the days go</h3><div class="note">Average days per stage, initiation &rarr; refund</div><div id="stages"></div></div>
<div class="card"><h3>The smoking gun: QC</h3><div class="note">Breached vs clean refunds &mdash; QC is the only stage that doubles</div><div id="anatomy"></div></div>
</div>
<div class="grid2" style="margin-top:14px">
<div class="card"><h3>Standing QC backlog</h3><div class="note">Monthly average backlog, units &mdash; scheduling problem, not headcount</div><div id="backlog"></div></div>
<div class="card"><h3>Pickup failures by courier</h3><div class="note">% of pickups needing a reattempt &mdash; a vendor problem, not geography</div><div id="courier"></div></div>
</div>
</section>
<section><h2>3 &middot; Who &amp; why</h2>
<div class="sub">A small slice of customers drives most of the cost, and a handful of SKUs drive most of the quality failures.</div>
<div class="grid2">
<div class="card"><h3>Cost concentration</h3><div class="note">Top 20% of customers &rarr; ~50% of return cost</div><div id="deciles"></div></div>
<div class="card"><h3>Toxic SKUs</h3><div class="note">Highest return rates (min. 500 units sold) &mdash; overwhelmingly Dresses</div><div id="toxictbl"></div></div>
</div>
</section>
<section><h2>4 &middot; The decision</h2>
<div class="sub">Four problems, one blanket fee cannot fix them. The segmented policy targets the 6% who game the system instead of punishing everyone.</div>
<div class="card"><h3>Policy options, net margin impact (&#8377; cr / yr, modelled)</h3><div class="note">From excel/policy_scenarios.xlsx &mdash; assumptions documented, sensitivity-tested</div><div id="policy"></div></div>
<div class="callout"><b>Recommendation: SEGMENTED.</b> Exchange-first as the default path &middot; &#8377;49 fee from the 2nd return per quarter (genuine damage always free) &middot; instant refunds for high-trust customers &middot; QC to daily flow &middot; 24-hr courier pickup SLA. Rebuild cost &#8377;6.5L, payback under one month (modelled).</div>
</section>
<footer>All data is <b>synthetic</b>, generated for this case study &mdash; no real company data.
Figures labelled <b>modelled</b> are scenario outputs under documented assumptions, not measured results.
Full method, SQL, Excel models and BA package: <a href="https://github.com/rshashank20/vastra-returns-fix">github.com/rshashank20/vastra-returns-fix</a></footer>
</div>
<script>
const D = %%DATA%%;
const FG = '#e8edf3', MUT = '#9aa4b2';
function base(h){return {paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)',font:{color:FG,size:12},margin:{l:120,r:20,t:10,b:40},height:h||300,xaxis:{gridcolor:'#232d3a',zerolinecolor:'#232d3a'},yaxis:{gridcolor:'#232d3a',zerolinecolor:'#232d3a'}}}

// ---- waterfall: cost buildup ----
(function(){
  const comp=[['Reverse shipping',88],['Wasted fwd shipping',72],['QC labour',35],['Refurbishment',33],['CX handling',11],['Holding cost',7],['Write-offs',265]];
  Plotly.newPlot('wf',[{type:'waterfall',orientation:'v',
    x:comp.map(c=>c[0]).concat(['Fully-loaded']),
    y:comp.map(c=>c[1]).concat([0]),
    measure:comp.map(()=>'relative').concat(['total']),
    connector:{line:{color:'#3a4657'}},
    increasing:{marker:{color:'#3fb6b2'}},totals:{marker:{color:'#f0b429'}}}],
    Object.assign(base(300),{margin:{l:40,r:20,t:10,b:90},xaxis:{tickangle:-20}}));
})();
// ---- donut: true reason ----
(function(){
  const order=['fit_or_remorse','bracketing','fake_damage_claim','quality_failure','genuine_damage','damaged_item_other_claim','defective_item_other_claim','wrong_item','other_true'];
  const cols={'fit_or_remorse':'#3fb6b2','bracketing':'#f0b429','fake_damage_claim':'#e5484d','quality_failure':'#e5484d','genuine_damage':'#e5484d','damaged_item_other_claim':'#c98a2e','defective_item_other_claim':'#c98a2e','wrong_item':'#6e7b8f','other_true':'#6e7b8f'};
  const rows=order.map(b=>D.true_reason.find(r=>r.bucket===b)).filter(Boolean);
  Plotly.newPlot('donut',[{type:'pie',hole:.52,labels:rows.map(r=>D.pretty[r.bucket]),values:rows.map(r=>r.n),
    marker:{colors:rows.map(r=>cols[r.bucket]),line:{color:'#161e28',width:2}},
    textinfo:'percent',textposition:'inside',hovertemplate:'%{label}<br>%{value:,} returns<extra></extra>'}],
    Object.assign(base(300),{showlegend:true,legend:{orientation:'h',y:-.15},margin:{l:20,r:20,t:10,b:60}}));
})();
// ---- monthly trend ----
(function(){
  const m=D.monthly;
  Plotly.newPlot('monthly',[
    {type:'bar',x:m.map(r=>r.month),y:m.map(r=>r.n_returns),name:'Returns',marker:{color:'#3fb6b2'},yaxis:'y'},
    {type:'scatter',mode:'lines+markers',x:m.map(r=>r.month),y:m.map(r=>r.cost_lakh),name:'Cost (₹ lakh)',marker:{color:'#f0b429'},yaxis:'y2'}],
    Object.assign(base(280),{margin:{l:60,r:60,t:10,b:40},yaxis:{title:'Returns'},yaxis2:{title:'₹ lakh',overlaying:'y',side:'right'},showlegend:true,legend:{orientation:'h',y:1.08}}));
})();
// ---- stages funnel (hbar) ----
(function(){
  const s=D.stage_avg, rows=[['Scheduling',s.sched],['Pickup',s.pickup],['Transit',s.transit],['QC',s.qc],['Refund',s.refund]];
  Plotly.newPlot('stages',[{type:'bar',orientation:'h',x:rows.map(r=>r[1]),y:rows.map(r=>r[0]),
    marker:{color:rows.map(r=>r[0]>=4?'#e5484d':'#3fb6b2')},
    text:rows.map(r=>r[1].toFixed(1)+' days'),textposition:'outside'}],
    Object.assign(base(280),{margin:{l:90,r:60,t:10,b:40},xaxis:{title:'Avg days'}}));
})();
// ---- breach anatomy ----
(function(){
  const g=D.breach_anatomy, stages=['sched','pickup','transit','qc','refund'], names={sched:'Scheduling',pickup:'Pickup',transit:'Transit',qc:'QC',refund:'Refund'};
  const mk=(grp,color,name)=>({type:'bar',orientation:'h',name:name,
    x:stages.map(s=>g.find(r=>r.grp===grp)[s]), y:stages.map(s=>names[s]), marker:{color:color}});
  Plotly.newPlot('anatomy',[mk(0,'#3fb6b2','Clean'),mk(1,'#e5484d','Breached')],
    Object.assign(base(280),{barmode:'group',margin:{l:90,r:20,t:10,b:40},xaxis:{title:'Avg days'},showlegend:true,legend:{orientation:'h',y:1.08}}));
})();
// ---- backlog ----
(function(){
  const wh=[...new Set(D.backlog.map(r=>r.wh))], cols={'WH-Delhi':'#3fb6b2','WH-Mumbai':'#f0b429'};
  const traces=wh.map(w=>{const rows=D.backlog.filter(r=>r.wh===w);
    return {type:'scatter',mode:'lines',x:rows.map(r=>r.month),y:rows.map(r=>r.avg_backlog),name:w,
      line:{color:cols[w]||'#9aa4b2'},fill:'tozeroy',fillcolor:(cols[w]||'#9aa4b2')+'22'}});
  Plotly.newPlot('backlog',traces,Object.assign(base(280),{margin:{l:60,r:20,t:10,b:40},yaxis:{title:'Units'},showlegend:true,legend:{orientation:'h',y:1.08}}));
})();
// ---- courier ----
(function(){
  const c=D.courier;
  Plotly.newPlot('courier',[{type:'bar',orientation:'h',x:c.map(r=>r.reattempt_pct),y:c.map(r=>r.courier),
    marker:{color:c.map(r=>r.reattempt_pct>15?'#e5484d':'#3fb6b2')},
    text:c.map(r=>r.reattempt_pct+'%'),textposition:'outside'}],
    Object.assign(base(220),{margin:{l:110,r:60,t:10,b:40},xaxis:{title:'% pickups needing reattempt'}}));
})();
// ---- deciles ----
(function(){
  const dz=D.deciles;
  Plotly.newPlot('deciles',[
    {type:'bar',x:dz.map(r=>'D'+r.decile),y:dz.map(r=>r.pct_cost),name:'% of cost',marker:{color:'#3fb6b2'},yaxis:'y'},
    {type:'scatter',mode:'lines+markers',x:dz.map(r=>'D'+r.decile),y:dz.map(r=>r.cum_pct),name:'Cumulative %',marker:{color:'#f0b429'},yaxis:'y2'}],
    Object.assign(base(280),{margin:{l:50,r:50,t:10,b:40},yaxis:{title:'% of cost'},yaxis2:{title:'Cumulative %',overlaying:'y',side:'right',range:[0,105]},showlegend:true,legend:{orientation:'h',y:1.08}}));
})();
// ---- toxic table ----
(function(){
  const t=D.toxic;
  document.getElementById('toxictbl').innerHTML='<table><tr><th>SKU</th><th>Category</th><th>Sold</th><th>Returned</th><th>Rate</th><th>Avg cost</th></tr>'+
    t.map(r=>`<tr><td>${r.sku}</td><td>${r.category}</td><td>${r.n_sold}</td><td>${r.n_returns}</td><td>${r.ret_rate}%</td><td>&#8377;${Math.round(r.avg_cost)}</td></tr>`).join('')+'</table>';
})();
// ---- policy options ----
(function(){
  const rows=[['Status quo',0,'#6e7b8f'],['Flat ₹49 fee',2.19,'#6e7b8f'],['Flat ₹99 fee',3.17,'#6e7b8f'],['Exchange-first only',2.36,'#6e7b8f'],['★ Segmented (recommended)',3.48,'#f0b429']];
  Plotly.newPlot('policy',[{type:'bar',orientation:'h',x:rows.map(r=>r[1]),y:rows.map(r=>r[0]),
    marker:{color:rows.map(r=>r[2])},text:rows.map(r=>r[1]?'₹'+r[1]+' cr':''),textposition:'outside'}],
    Object.assign(base(260),{margin:{l:220,r:80,t:10,b:40},xaxis:{title:'Net margin impact, ₹ cr/yr (modelled)'}}));
})();
</script></body></html>
"""
out = html_head.replace("%%DATA%%", DATA)
open(OUT, "w").write(out)
print("written", OUT, len(out) // 1024, "KB")
