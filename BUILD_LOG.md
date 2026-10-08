# Build log

How this project was actually built. Including the bugs, because a project
with no bugs is a project nobody ran.

## Oct 7 — picking the project

I had four project specs locked and a planned build order starting with
Dark Store Triage. I started with the Returns Fix instead. Reason: it
merges analytics and BA process work in one repo, which makes it the
strongest single proof-of-work piece.

## Oct 8, ~1am — the ₹657 bug

First full run of the cost model said ₹657 per return. That felt wrong,
so I checked the journey timestamps instead of trusting the output.
Return events were misaligned across returns (timestamps from one
return's journey leaking into another's duration math). Fixed the
generator, re-ran: ₹511. Lesson I won't forget: never quote the first
number.

## Oct 8 — the meaningless "other" bucket

First version of the true-reason triangulation dumped 32% of cost into
an `other` bucket. A bucket that big means the classification logic is
giving up. Rewrote the CASE so every damaged/defective QC outcome lands
in a named bucket (genuine damage, quality failure, fake claim, etc.).
The "other" bucket is now 3.9%. If your catch-all is bigger than your
insights, your logic is wrong.

## Oct 8 — bracketing was too thin to matter

First bracketing injection only produced 2.2% of returns. Real enough
to detect, too thin to build a policy around. Re-injected at ~8% of
returns. The generator immediately crashed: my bracketing code tried to
pick 3 sizes for free-size categories (sarees have one size). Added a
guard to skip free-size categories. Synthetic data still needs edge-case
handling.

## Oct 8 — the SLA call

Started with a 10-day SLA because it sounded standard. Then I noticed
the refund timestamps mix business days and calendar days in the data,
which made 10 days an arbitrary line. Moved it to 14 calendar days and
documented why. Breach rate: 56.8%. The threshold is a judgment call and
it's labeled as one.

## Oct 8 — blank quarters

Cohort analysis came back with NULL quarters. I'd used `%q` in
`STRFTIME`, which SQLite doesn't support. Replaced it with explicit
month math. Small bug, but it would have shipped a broken chart.

## Oct 8 — the exchange proxy

There is no exchange event in the data, so I proxied it with "same
customer buys again within 14 days." Only 6.3% do. That's a weak proxy
and it's labeled as directional, not a finding. The exchange lever in
the recommendation is a process change to be modeled, not something the
data proves. Knowing what your data can't tell you is part of the job.

## Oct 8, ~2am — the handoff

I was tired and told my AI assistant to "build the whole project." It
did: Excel models, BRD, user stories, UAT, memo. Everything with
business judgment in it (elasticities, deterred shares, requirement
wording) is flagged in `docs/assumptions.md` for me to review, because
I have to defend it in interviews. A portfolio I can't explain is a
liability.

## Oct 8 — the "looks AI-generated" pass

First version of this repo read like a consulting template. Uniform
voice, em-dashes everywhere, no rough edges. Rewrote the README and
memo in plain language and added this log. The BRD and user stories
stayed formal because those documents are supposed to be formal.
