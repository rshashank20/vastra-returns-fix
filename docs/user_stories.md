# User Stories — Returns Module Rebuild (Vastra)

These stories are based on the requirements identified during the returns cost and process analysis. Each story links back to the relevant BRD requirement so that the reason for the change is clear.

---

## US-01 — Instant exchange for size issues
**As a** customer returning an item because of a size or fit issue, **I want** the exchange option to be shown first and confirmed immediately, **so that** I can get the right size without placing a new order while waiting for a refund.

**Traces:** BR-05, FR-03

```gherkin
Given I start a return for a size_fit reason
When the return options are shown
Then exchange-in-my-size is selected by default
And the exchange is confirmed immediately
And the replacement follows the standard forward shipping SLA
```

---

## US-02 — Automatic refund for low-risk returns
**As a** finance controller, **I want** low-risk refunds to be approved automatically using defined rules, **so that** manual review is reserved for exceptions.

**Traces:** BR-01, FR-01

```gherkin
Given a return has a trust_score of 80 or above
And the item value is ₹2000 or less
And the customer has no fee history
When QC marks the item as resellable
Then the refund is credited within 24 hours without manual review
And the rule ID used for approval is stored for audit
```

---

## US-03 — Fee for repeated non-damage returns
**As a** finance controller, **I want** the ₹49 fee to be applied automatically from the customer's second return in a quarter, **so that** repeated return behaviour can be addressed without manual intervention.

**Traces:** BR-03, FR-02, RULE-01

```gherkin
Given the customer has already made 1 return in the current quarter
When the customer starts a 2nd return
And QC does not confirm damage
Then a ₹49 fee is shown before the return is confirmed
And the reason is shown as "2nd return this quarter"
And the fee is deducted from the refund amount
```

---

## US-04 — Exemption for genuine damage
**As a** customer who received a damaged or defective item, **I want** the return fee to be waived, **so that** I am not charged for a product-quality problem.

**Traces:** BR-04, RULE-03

```gherkin
Given QC marks the item as damaged or defective
When the refund amount is calculated
Then the return fee is ₹0 regardless of the customer's return count
And the SKU is added to the sourcing-quality review list
```

---

## US-05 — Prioritised QC queue
**As a** QC supervisor, **I want** the QC queue to prioritise items based on breach risk and item value, **so that** returns that are close to an SLA breach are handled before routine items.

**Traces:** BR-08, FR-05

```gherkin
Given 300 returned items are waiting for QC
When the supervisor opens the QC queue
Then the items are ordered by (days waiting × item value) in descending order
And any item projected to breach the SLA is highlighted
```

---

## US-06 — Proactive refund-delay notification
**As a** customer, **I want** to know about a likely refund delay before the SLA is missed, **so that** I do not have to contact support just to ask for an update.

**Traces:** BR-10, FR-04

```gherkin
Given the projected credit date for my return is beyond the SLA
When the nightly projection job runs
Then I receive an SMS/WhatsApp notification with the updated expected date before day 14
And the return is marked as proactively communicated
```

---

## US-07 — Courier pickup SLA tracking
**As a** warehouse operations manager, **I want** courier pickup failure rates tracked every week, **so that** SLA issues can be raised and penalty claims can be supported by the data.

**Traces:** BR-09, FR-06

```gherkin
Given the week's pickup attempts are available for each courier
When a courier's pickup failure rate exceeds 10%
Then a penalty claim draft is generated using ₹50 × excess failures
And the courier scorecard is updated
```

---

## US-08 — Instant refund for high-trust customers
**As a** high-trust customer, **I want** my refund to be initiated when I hand over the item, **so that** the return experience does not depend on waiting for the full QC cycle.

**Traces:** BR-06, RULE-02

```gherkin
Given trust_score is 80 or above
And the customer has no prior fee
When the courier scan confirms pickup
Then the refund is initiated immediately before QC
And abuse-monitoring rules flag unusual return velocity for review
```

---

## US-09 — Escalation after repeated pickup failure
**As a** customer, **I want** another way to complete my return when pickup fails repeatedly, **so that** the return does not remain stuck in the pickup stage.

**Traces:** RULE-04

```gherkin
Given 3 pickup attempts have failed
When the 3rd failure is recorded
Then CX is notified automatically
And I am offered a self-drop option with a ₹50 credit
```

---

## US-10 — Clear fee disclosure before confirmation
**As a** customer, **I want** to see any return fee and the rule behind it before I confirm the return, **so that** there are no unexpected deductions when the refund is processed.

**Traces:** FR-08; backlash mitigation

```gherkin
Given a return fee applies
When I review the return summary before confirmation
Then the fee amount is displayed
And the rule that triggered the fee is displayed
And I can cancel the return from the same screen
```

---

## Notes on traceability

The stories are intentionally kept close to the BRD requirements. The main areas covered are:

- **Customer experience:** exchanges, refund speed, notifications, pickup alternatives and fee transparency.
- **Operations:** QC prioritisation and courier SLA tracking.
- **Finance and controls:** rule-based refunds, repeat-return fees and damage exemptions.
- **System behaviour:** audit logging, rule execution and automated notifications.

The acceptance criteria describe the expected system behaviour that can later be used to create UAT cases.
