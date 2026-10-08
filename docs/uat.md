# UAT Cases — Returns Module Rebuild (Vastra)

These cases are meant to check the main customer and operations paths in the proposed returns flow. I focused on the cases that connect directly to the business rules and user stories, rather than trying to cover every possible edge case.

| ID | Scenario | Preconditions | Steps | Expected result | Pass criteria | Traces to |
|----|----------|---------------|-------|-----------------|---------------|-----------|
| UAT-01 | Happy path: exchange | Customer has 0 returns this quarter; item size M | 1. Initiate a return with reason `size_fit` 2. Select exchange for size L 3. Confirm | Exchange is confirmed immediately; replacement order is created; no return fee is charged | Replacement enters the forward-shipping flow within SLA; refund flow is not triggered | US-01, BR-05 |
| UAT-02 | Happy path: clean refund | High-trust customer (score 85); item value ₹1,200 | 1. Initiate return 2. Record courier pickup scan 3. QC marks item as resellable | Instant refund is initiated from the pickup scan as defined by RULE-02; refund is credited within 5 days after QC | Stage timestamps are recorded and the case does not require manual intervention | US-08, US-02, BR-01 |
| UAT-03 | Pickup failure ×3 | Customer is in a Tier-3 pincode | 1. Initiate return 2. Simulate first failed pickup 3. Simulate second failed pickup 4. Simulate third failed pickup | CX is notified automatically; customer is offered self-drop plus ₹50 credit as defined by RULE-04 | An escalation ticket is created and the offer is visible to the customer | US-09, RULE-04 |
| UAT-04 | QC damage dispute | Customer selected `damaged`; QC finds the item resellable | 1. Move the return through to QC 2. Record QC result as resellable | The case is classified as `fake_damage_claim`; normal fee rules apply and no damage write-off is created | Triangulation produces the expected classification and the finance report contains no damage write-off for the case | US-04, BR-04 |
| UAT-05 | 2nd-return fee trigger | Customer has already made 1 return this quarter | 1. Initiate a second return with reason `changed_mind` 2. Review the return summary before confirming | A ₹49 fee is shown before confirmation with the explanation "2nd return this quarter" as defined by FR-08 | Fee is deducted from the refund and the applicable rule ID is recorded under NFR-03 | US-03, US-10, RULE-01 |
| UAT-06 | Genuine damage exempt | Customer has 3 returns this quarter; returned item is genuinely damaged | 1. Initiate the fourth return 2. QC records the item as damaged | Fee remains ₹0 despite the return count, as defined by RULE-03; SKU is sent for sourcing review | No fee is shown and a sourcing-review ticket is created | US-04, RULE-03 |
| UAT-07 | SLA breach escalation | Return is projected to have a credit date beyond 14 days | 1. Run the nightly projection job | A proactive SMS is sent before day 14 and the return is flagged in the CX dashboard as defined by FR-04 | Customer receives the notification and the case does not need to rely on a WISMO ticket to surface the delay | US-06, BR-10 |
| UAT-08 | Duplicate app-retry | Customer submits the same return twice within 60 seconds | 1. Submit the return 2. Submit the same request again | Only one `return_id` is processed; the duplicate request is ignored and only one refund can be created | Payout log contains no double payment and NFR-04 is satisfied | NFR-04 |

## Entry / exit criteria

- **Entry:** BRD v1.0 is signed off and the test data covers all 9 tables, including the seeded data-quality issues.
- **Exit:** all 8 cases pass; BR-01 through BR-10 can be measured in the UAT dashboard; no critical defects remain open.
