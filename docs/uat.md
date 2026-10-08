# UAT Cases — Returns Module Rebuild (Vastra)

| ID | Scenario | Preconditions | Steps | Expected result | Pass criteria | Traces to |
|----|----------|---------------|-------|-----------------|---------------|-----------|
| UAT-01 | Happy path: exchange | Customer, 0 returns this quarter; item size M | 1. Initiate return (reason: size_fit) 2. Accept exchange (size L) 3. Confirm | Exchange confirmed instantly; replacement order created; no fee | Replacement ships in forward SLA; refund path not triggered | US-01, BR-05 |
| UAT-02 | Happy path: clean refund | High-trust customer (score 85), item ₹1,200 | 1. Initiate return 2. Courier pickup scan 3. QC resellable | Instant refund initiated on pickup scan (RULE-02); credited ≤ 5 days post-QC | Timestamps logged per stage; no manual touch | US-08, US-02, BR-01 |
| UAT-03 | Pickup failure ×3 | Customer in Tier-3 pincode | 1. Initiate return 2. Simulate 3 failed pickups | CX auto-notified; customer offered self-drop + ₹50 credit (RULE-04) | Escalation ticket created; offer visible in app | US-09, RULE-04 |
| UAT-04 | QC damage dispute | Customer claimed "damaged"; QC finds resellable | 1. Return flows to QC 2. QC marks resellable | Classified fake_damage_claim; fee rules apply normally; NO damage write-off booked | Triangulation logic matches UAT expectation; finance report shows no write-off | US-04, BR-04 |
| UAT-05 | 2nd-return fee trigger | Customer with 1 return this quarter | 1. Initiate 2nd return (reason: changed_mind) 2. Review summary | ₹49 fee shown with reason "2nd return this quarter" BEFORE confirm (FR-08) | Fee deducted from refund; rule ID logged (NFR-03) | US-03, US-10, RULE-01 |
| UAT-06 | Genuine damage exempt | Customer with 3 returns this quarter; item arrives damaged | 1. Initiate 4th return 2. QC marks damaged | Fee = ₹0 despite count (RULE-03); SKU flagged to sourcing review | No fee line; sourcing ticket created | US-04, RULE-03 |
| UAT-07 | SLA breach escalation | Return with projected credit > 14 days | 1. Nightly projection job runs | Proactive SMS sent before day 14; CX dashboard flags return (FR-04) | Customer receives notification; no WISMO ticket needed | US-06, BR-10 |
| UAT-08 | Duplicate app-retry | Customer double-taps submit | 1. Submit return twice within 60s | Single return_id processed; duplicate ignored; ONE refund | NFR-04: no double payment in payout log | NFR-04 |

## Entry / exit criteria
- **Entry:** BRD v1.0 signed; test data covers all 9 tables incl. seeded quality issues.
- **Exit:** all 8 cases pass; BR-01…BR-10 measurable in the UAT dashboard; zero critical defects open.
