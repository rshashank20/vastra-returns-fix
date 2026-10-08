# User Stories — Returns Module Rebuild (Vastra)

Format: story + Gherkin acceptance criteria. Each story traces to a BRD requirement.

---

## US-01 — Instant exchange (customer)
**As a** customer returning for a size issue, **I want** exchange shown as the
default option with instant confirmation, **so that** I don't rebuy elsewhere
while waiting 14 days. *(Traces: BR-05, FR-03)*

```gherkin
Given I initiate a return for a size_fit reason
When the return options load
Then exchange-in-my-size is preselected and confirmation is instant
And the replacement ships within the standard forward SLA
```

## US-02 — Auto-refund rules (system)
**As a** finance controller, **I want** low-risk refunds auto-approved by rules,
**so that** manual effort focuses on exceptions. *(Traces: BR-01, FR-01)*

```gherkin
Given a return with trust_score >= 80, item value <= ₹2000, no fee history
When QC marks it resellable
Then the refund is credited without manual review within 24h
And the rule ID is logged against the return for audit
```

## US-03 — Bracketeer fee trigger (customer + finance)
**As a** finance controller, **I want** the ₹49 fee auto-applied from the 2nd
return in a quarter, **so that** bracketing behaviour is priced without manual
policing. *(Traces: BR-03, FR-02, RULE-01)*

```gherkin
Given a customer with 1 return already this quarter
When they initiate a 2nd return and QC does not confirm damage
Then a ₹49 fee line is shown BEFORE confirmation with the reason "2nd return this quarter"
And the fee is deducted from the refund
```

## US-04 — Fee exemption on genuine damage (customer)
**As a** customer with a genuinely damaged item, **I want** no fee charged,
**so that** I'm not punished for Vastra's quality failure. *(Traces: BR-04, RULE-03)*

```gherkin
Given QC marks the item damaged or defective
When the refund is computed
Then fee = ₹0 regardless of return count
And the SKU is flagged to the sourcing-quality review list
```

## US-05 — QC prioritization queue (warehouse)
**As a** QC supervisor, **I want** the day's QC queue ordered by breach-risk ×
item value, **so that** SLA-critical items never wait behind routine ones.
*(Traces: BR-08, FR-05)*

```gherkin
Given 300 items awaiting QC
When the supervisor opens the queue
Then items are ordered by (days waiting × item value) descending
And any item projected to breach SLA is highlighted red
```

## US-06 — Proactive WISMO deflection (customer + CX)
**As a** customer, **I want** a delay notification before I have to ask,
**so that** I don't open a ticket. *(Traces: BR-10, FR-04)*

```gherkin
Given my return's projected credit date exceeds the SLA
When the projection is computed (nightly job)
Then I receive an SMS/WhatsApp with the new expected date BEFORE day 14
And no WISMO ticket is needed for this return
```

## US-07 — Courier SLA tracking (ops)
**As a** warehouse ops manager, **I want** weekly courier fail-rate tracking,
**so that** penalty claims are automatic, not argued. *(Traces: BR-09, FR-06)*

```gherkin
Given the week's pickup attempts per courier
When fail-rate exceeds 10%
Then a penalty claim draft (₹50 × excess failures) is generated
And the courier scorecard updates
```

## US-08 — High-trust instant refund (customer)
**As a** loyal customer, **I want** my refund the day I hand over the item,
**so that** returning feels safe. *(Traces: BR-06, RULE-02)*

```gherkin
Given trust_score >= 80 and no prior fee
When the courier scan confirms pickup
Then the refund is initiated immediately (before QC)
And abuse monitoring flags velocity anomalies for review
```

## US-09 — Pickup failure escalation (customer + CX)
**As a** customer, **I want** an alternative when pickup fails repeatedly,
**so that** my return isn't stuck. *(Traces: RULE-04)*

```gherkin
Given 3 failed pickup attempts
When the 3rd failure is logged
Then CX is auto-notified and I am offered a self-drop option with a ₹50 credit
```

## US-10 — Fee transparency (customer)
**As a** customer, **I want** to see any fee and its reason before confirming,
**so that** there are no refund-day surprises. *(Traces: FR-08; backlash mitigation)*

```gherkin
Given a fee applies to my return
When I review the return summary
Then the fee amount AND the rule that triggered it are displayed
And I can cancel the return from that screen
```
