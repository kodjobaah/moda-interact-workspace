---
id: ARCH-015-SYSTEM-TEST-001
architecture_id: ARCH-015
title: End-to-end acceptance for recovery-credit purchase, carry-forward and refunds
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: manual
status: ready
priority: 90
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-015-SHARED-001
- ARCH-015-DATABASE-001
- ARCH-015-DATABASE-002
- ARCH-015-SHOPIFY-001
- ARCH-015-SHOPIFY-002
- ARCH-015-BACKGROUND-001
- ARCH-015-BACKGROUND-002
- ARCH-015-SHOPIFY-003
- ARCH-015-BACKGROUND-003
- ARCH-015-ADMIN-001
enables: []
created: 2026-09-15
updated: 2026-09-16
---

# ARCH-015-SYSTEM-TEST-001

## Objective

Prove the accepted ARCH-015 contracts against deployed/integrated services. Do not compensate for failed implementation by adding test-only behavior.

## Acceptance scenarios

At minimum automate/document deterministic scenarios for:

1. current Shopify plan correlates to exact ARCH-014 `shopifyPlanHandle`;
2. only matching ARCH-014 usage-event/provider-meter intersections become top-up offers;
3. same event handle under another plan never leaks into current plan;
4. Shopify live price is displayed/used as provider truth;
5. `price.active=false` returned live item is not discarded;
6. zero matched offers still renders top-up section with "No top ups are currently available for this subscription.";
7. provider verification outage shows verification-unavailable state and no Buy action;
8. null legacySubscriptionId native App Pricing purchase succeeds with deterministic context;
9. first same-handle purchase snapshots baseline B, publishes +1, and becomes ACTIVE only after provider B+1 proof;
10. second same-handle purchase uses fresh post-first baseline;
11. same shop/same handle concurrent purchase single-flight;
12. same shop/different handles can proceed independently;
13. retries reuse idempotency and do not duplicate charge/lot;
14. zero-cost top-up can activate with exact provider quantity proof and zero monetary delta;
15. fractional provider baseline after refund supports a subsequent +1 purchase;
16. Starter purchased lots survive upgrade to Growth;
17. historical lots are consumed before current-context refundable lots;
18. spending purchased credits does not publish top-up App Events;
19. historical lot stays spendable but normal refund is unavailable;
20. current positive-value lot can enter refund hold;
21. refund web request does not synchronously invoke/await Background;
22. existing billing scheduler discovers REQUESTED refund;
23. safe full refund submits -1 correction;
24. safe partial refund submits fractional correction;
25. 202 does not complete refund;
26. later exact provider quantity/cost proof completes refund automatically without Admin;
27. transient provider delay does not duplicate correction;
28. unsafe correction routes PROVIDER_ACTION_REQUIRED before any automatic event;
29. Admin exact REFUND/CREDIT evidence completes manual fallback;
30. Admin cannot issue manual monetary action when `automaticCorrectionUsageEventId` exists;
31. automatic correction baseline/expected-after evidence is stored as typed RecoveryCreditRefund columns and remains immutable across scheduler retries;
32. no UsageEvent metadata JSON is required for settlement proof;
33. mismatched provider evidence becomes NEEDS_ATTENTION;
34. no historical purchased lot is rewritten during plan/cycle transition;
35. no runtime top-up decision falls back to singular BillingPlan pack fields.

36. Admin REQUESTED refund is read-only and exposes no lock/reject/manual-settlement controls;
37. REQUESTED withdrawn zero-reservation refund is presented as READY_FOR_REFUND_PROCESSING, never READY_FOR_PROVIDER_ACTION;
38. NEEDS_ATTENTION never exposes or accepts the normal manual REFUND/CREDIT evidence path;
39. automatic correction blocks manual monetary action even when its UsageEvent is NEEDS_ATTENTION;
40. automatic correction refund links to the existing Billing App Event drawer using `view=events&eventId=<id>`;
41. completed refund presentation distinguishes automatic App Event correction from manual REFUND/CREDIT settlement;
42. refund-specific English Admin copy matches the architect localization matrix exactly;
43. if additional accepted Admin locale catalogues exist at implementation time, implemented refund-specific values match the architect matrix exactly for each locale;
44. no ADMIN-002 implementation task or temporary Admin compatibility path is required.

## Evidence

Capture:

```text
provider activeSubscription snapshots
ARCH-014 plan/event records used
purchase/refund rows before/after
RecoveryCreditRefund automaticCorrectionUsageEventId and typed correction evidence
UsageEvent ids, quantities and idempotency keys
provider quantity/cost before/after
entitlement aggregate before/after
relevant UI state
worker logs for scheduled refund discovery/reconciliation
```

Redact credentials/tokens.

## Stop conditions

STOP and return evidence rather than weakening assertions if any accepted task contract cannot be demonstrated in the deployed test environment.

## Completion protocol

Publish terminal acceptance report, set task `status: review`, return to `moda_architect`, STOP.
