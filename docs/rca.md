# Root-Cause Analysis — The Returns Fix (Vastra)

I approached the problem in two parts: first, I looked at **why returns were expensive**; then I looked at **why refunds were taking so long**. The two analyses point to different operational problems, but they also connect to each other.

All findings below come from the Phase 1 and Phase 2 SQL analyses. Where a result is directional or based on a proxy, I have called that out instead of treating it as a measured fact.

---

## 1. Cost thread — there is no single returns problem

### What I first looked at

The number leadership was using was roughly **₹88 per return**, mainly based on reverse shipping. I wanted to check the fully-loaded cost instead of assuming that figure represented the actual economic impact.

The analysis gave an average cost of about **₹511 per return**, or roughly **₹18.16 crore per year** (`sql/01`). The largest component was write-offs, followed by reverse shipping and wasted forward shipping.

### What the data showed

I then compared the customer's claimed return reason with the QC result and ordering behaviour (`sql/03`). That changed the way I looked at the problem:

- About **26% of returns** were classified as genuine quality failures or real damage. They were expensive at about **₹1,195 each**, so they accounted for roughly **62% of total return cost**.
- **47.6%** were fit/remorse returns at about **₹258 each**. They were high-volume, but much cheaper per return.
- **10.2%** were classified as fake damage claims: the customer selected damaged, but QC found the item resellable.
- **8.0%** of returns were linked to bracketing behaviour; the bracketing analysis identified **13,535 customers** buying three sizes of the same SKU (`sql/04`).

That made a blanket return fee look less attractive. The expensive quality problem, fit/remorse behaviour, and bracketing behaviour do not have the same root cause, so they should not be handled in exactly the same way.

### Where the cost is concentrated

The top **20% of customers account for 49.9% of return cost** (`sql/05`). I also checked acquisition cohorts and channels, and return rates were broadly flat across them (`sql/08`). Because of that, I did not treat marketing acquisition as the main cause of the returns problem.

The SKU analysis showed another pattern: several Dress SKUs had return rates in the **40–47% range** (`sql/06`). That points to a product or sourcing issue rather than something a customer-facing fee can solve.

### Cost-thread root cause

The main finding here is that **"returns" is too broad a category to fix with one policy**.

I see four different problems in the data:

1. **Quality failures / genuine damage** → product and sourcing problem.
2. **Bracketing** → customer-behaviour and policy problem.
3. **Fake damage claims** → process and policy-control problem.
4. **Fit / remorse** → product-information and customer-experience problem.

The policy therefore needs to be segmented rather than applying the same treatment to every customer and every return reason.

---

## 2. Process thread — the refund delay is mainly a flow problem

### What I first looked at

The headline process issue was simple: refunds were taking around **10.2 days from initiation to credit**, and **56.8%** of refunds breached the 14-day SLA.

Instead of assuming the warehouse needed more people, I broke the journey into stages and compared breached returns with clean returns (`sql/09`, `sql/10`).

### What the data showed

The biggest difference was at the QC stage:

- QC took about **5.1 days on breached refunds**.
- QC took about **2.9 days on clean refunds**.

That made QC the clearest stage-level difference associated with the breach. The overall average alone would only tell me that QC is slow; comparing the two groups helped identify where the delay mattered most.

I then checked the backlog rather than jumping straight to a headcount recommendation. The backlog analysis showed a standing QC backlog of roughly **1,500–2,300 units**, with arrivals and completions reasonably close on average (`sql/12`). The timestamp pattern also showed QC completions clustering on Mondays.

That combination suggested a **batching/scheduling problem** rather than a simple lack of capacity. The issue is not just how many people are doing QC; it is when the work is being processed.

### Courier performance

Pickup performance was another source of delay. XpressBees had a **17.8% reattempt rate**, compared with **10.3% for Delhivery** (`sql/13`). The gap appeared across city tiers, so I treated courier execution as a vendor-performance issue worth addressing through service-level terms rather than as a geography-specific problem.

### Customer-support cost of the delay

The process delay also shows up in CX data. Breached returns generated about **14.0 WISMO tickets per 100 returns**, versus **4.4** for clean returns — about **3.2× higher** (`sql/11`). The analysis attributes about **5,180 agent-hours**, or **₹12.43 lakh**, to WISMO handling for breached returns.

That matters because the refund delay is not only a customer-experience issue. It creates an additional operating cost.

### Process-thread root cause

The strongest process explanation from the data is:

**QC batching + weak courier handoff controls → longer return journey → more SLA breaches → more "where is my refund" contacts.**

The evidence does not support jumping straight to a blanket headcount increase. The first intervention should be better scheduling/cadence and clearer courier SLAs.

---

## 3. How the two threads connect

The two analyses cannot be treated as completely separate.

### Slow refunds can weaken an exchange-first strategy

Only **6.3%** of returns were followed by a reorder within 14 days (`sql/07`). This is a **directional proxy**, not a measured exchange rate, because the dataset does not contain explicit exchange events.

My interpretation is that an exchange-first policy is much harder to make work if the underlying return flow still takes around ten days. The process has to become faster for the exchange path to be credible.

### Policy rules also need system support

A targeted fee or trust-based refund rule only works if the returns system can actually apply the rule consistently. That is why the policy recommendation is tied to the BRD and the rebuilt returns flow rather than being treated as a standalone pricing change.

### Process improvements need a business case

The process changes also need to be justified in financial terms. The capacity model estimates the cost of moving to a daily QC flow and compares it with the potential savings from lower holding and CX costs. Those numbers are **modelled**, not measured outcomes.

---

## 4. Final diagnosis

The project started with a broad question — **"How do we reduce returns?"** — but the analysis made that question more specific.

The cost problem is not simply a high return rate. It is a mix of **quality failures, fit/remorse, bracketing, and policy/process leakage** with very different economics.

The process problem is not simply that refunds are slow. The clearest operational signals are **QC batching and weak courier pickup controls**, and the delay has a measurable CX-support cost.

So the recommendation is a single program with two linked workstreams:

- **Policy:** exchange-first as the default path, a targeted fee from the second return in a calendar quarter, and controlled instant refunds for high-trust customers.
- **Process:** move QC toward a daily flow, strengthen courier pickup SLAs, automate eligible refund decisions, and proactively communicate delays.

The policy and financial outcomes are based on the assumptions documented in `docs/assumptions.md` and the Excel scenario models. They should be treated as **pilot hypotheses until validated with live data**.
