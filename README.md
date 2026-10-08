# Vastra Returns Fix

**A business analysis case study on returns cost and refund delays for a fictional D2C fashion brand.**

> **Important:** This project uses synthetic data. The numbers below are calculated from that dataset or labelled as modelled assumptions. No real Vastra/company data is being presented.

## What was the problem?

Vastra has a **28% return rate**. Leadership was mainly looking at reverse shipping and treating **₹88** as the cost of a return.

I wanted to answer two practical questions:

1. **What does a return actually cost the business?**
2. **Why are refunds taking 10+ days?**

The first pass showed that the problem was bigger than shipping cost. Once reverse shipping, wasted forward shipping, QC, refurbishing, support and write-offs were included, the average return cost came to **₹511**, or about **₹18.2 crore a year** in this scenario.

At the same time, refunds took about **10.2 days** on average and **56.8%** of returns breached the 14-day SLA.

That meant this was not just a returns-policy problem. There was also a process problem behind it.

## What I found

### 1. Not all returns should be treated the same

The customer-selected return reason was not reliable enough on its own, so I compared it with QC results and ordering behaviour.

Some of the clearest patterns were:

- **~26%** were genuine quality/damage-related returns, but they were expensive — roughly **62% of total return cost**.
- **47.6%** were fit/remorse returns. They were much cheaper per return and looked more like a product-information problem than a fee problem.
- **10.2%** were cases where a customer claimed damage but QC found the item resellable.
- **8.0%** of returns matched the bracketing pattern I defined: customers buying multiple sizes and keeping one.

I also found that the **top 20% of customers accounted for 49.9% of return cost**. Return rates were broadly flat across acquisition channels, so this did not look like a problem caused by one marketing channel.

### 2. A few products were responsible for a lot of the quality problem

Return toxicity was not evenly distributed across the catalogue. Dresses were especially noticeable, with several SKUs showing return rates around **40–47%**.

That points to a product, sizing or sourcing issue for those SKUs rather than something that can be solved with a blanket customer fee.

### 3. Refund delays were mostly a process problem

The biggest bottleneck was **QC**.

QC took about **5.1 days on breached refunds**, compared with **2.9 days on clean refunds**. The timestamps also showed a Monday-heavy QC pattern, which is consistent with batch processing rather than a continuous daily flow.

The backlog analysis showed a fairly permanent queue of roughly **1,500–2,300 units**, which made scheduling look like the bigger problem than simply adding headcount.

There was a second issue on pickups: **XpressBees had a 17.8% reattempt rate vs 10.3% for Delhivery** in this dataset.

And the CX impact was visible. Breached returns generated about **14.0 WISMO tickets per 100 returns**, compared with **4.4** for clean returns — around **3.2× higher**.

## What I recommended

I did not recommend a blanket return fee.

The analysis pointed towards a more targeted policy combined with a process fix:

**Policy**

- Make **exchange-first** the default for eligible returns.
- Charge a **₹49 fee from the 2nd return in a calendar quarter** for non-genuine cases, while keeping confirmed quality/damage returns free.
- Allow **instant refunds for high-trust customers** subject to item-value and velocity rules.
- Review or fix the highest-return SKUs instead of pushing the problem onto customers.

**Process**

- Move QC from batch processing to a **daily flow**.
- Add measurable **courier pickup SLAs** and escalation rules.
- Auto-route eligible refunds instead of sending every case through the same manual path.
- Send proactive notifications when a return is likely to miss its SLA.

The policy model gives a **modelled net margin improvement of ₹3.48 crore/year** under the assumptions in `excel/policy_scenarios.xlsx`. This is a scenario result, not a measured business outcome. The recommendation memo also proposes a pilot before a full rollout.

## How I worked on it

I used the project as a full business-analysis exercise rather than starting with a dashboard.

### Data

`data_generator.py` creates the synthetic dataset and includes a few realistic data-quality problems such as noisy return reasons, missing pickup timestamps, duplicate app retries and inconsistent day-basis logic for refunds.

### SQL

The analysis is in `sql/` and covers:

- fully-loaded return cost
- return reason analysis
- reason triangulation
- bracketing detection
- customer cost concentration
- SKU return toxicity
- exchange vs refund economics
- cohort analysis
- return-journey bottlenecks
- SLA breach analysis
- WISMO analysis
- QC backlog
- courier pickup failures

### Excel

The three workbooks in `excel/` were used for the decision rather than just reporting numbers:

- `policy_scenarios.xlsx` — compare policy options and sensitivity to assumptions
- `capacity_model.xlsx` — look at QC/pickup capacity and backlog behaviour
- `business_case.xlsx` — compare rebuild cost with the modelled financial benefit

### BA deliverables

The `docs/` folder contains the parts I would normally hand to different stakeholders:

- stakeholder map + RACI
- BRD
- AS-IS and TO-BE flows
- user stories + acceptance criteria
- UAT cases
- assumptions and open validation points
- RCA

`recommendation_memo.md` brings the analysis together into the final business decision.

## Repo structure

```text
vastra-returns-fix/
├── dashboard/              # index.html: interactive web dashboard + build_dashboard.py
├── data_generator.py
├── DATA_DICTIONARY.md
├── BUILD_LOG.md
├── PLAN.md
├── sql/
├── excel/
├── docs/
├── recommendation_memo.md
└── powerbi_build_guide.md
```

The full dataset and SQLite database are generated locally and are not committed to the repository.

## Running the project

```bash
pip install -r requirements.txt
python3 data_generator.py --scale 0.02   # small sample for a quick run
python3 data_generator.py --scale 1.0    # full synthetic dataset
```

The generated data can then be loaded into SQLite and the SQL analyses in `sql/00–13` can be run.

## A few things I would validate in a real company

This is a case study, so several parts of the final recommendation are assumptions that would need real-world validation before implementation.

The biggest ones are:

- how much a ₹49 fee would actually change return behaviour
- how many fit/remorse returns would convert to exchanges
- the abuse rate for instant refunds
- actual QC throughput and staffing constraints
- the expected reduction in SLA breaches after moving to daily QC

These assumptions are documented in `docs/assumptions.md` instead of being presented as facts.

## Why I built this

I wanted one project that showed more than SQL and dashboards.

The goal was to take a messy business problem, work from raw operational data, figure out what was actually driving the problem, test possible actions, and then turn the recommendation into something a product/engineering team could build.

That is the part of the project I would be most comfortable discussing in an interview.
