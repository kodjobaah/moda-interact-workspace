---
id: ARCH-078-SYSTEM-TEST-001
architecture_id: ARCH-078
title: Certify Shopify billing plan and usage-event mapping lifecycle
task_kind: verification
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 80
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-078-DATABASE-001, ARCH-078-BACKGROUND-001, ARCH-078-SHOPIFY-001, ARCH-078-ADMIN-001]
enables: []
created: 2026-11-22
updated: 2026-11-22
---

# ARCH-078-SYSTEM-TEST-001 — Certify Shopify billing plan and usage-event mapping lifecycle

## Architecture and dependencies

Follow [ARCH-078](../../../architecture/ARCH-078-shopify-provider-authoritative-billing-plan-and-usage-event-mapping.md).

Run only after architect acceptance of:
- `ARCH-078-DATABASE-001`
- `ARCH-078-BACKGROUND-001`
- `ARCH-078-SHOPIFY-001`
- `ARCH-078-ADMIN-001`

## Objective

Verify the end-to-end Shopify billing plan and usage-event mapping contract using the existing modular system-test framework, disposable PostgreSQL and provider fixtures. This task is verification only; it must not introduce application behaviour or a new test framework.

The supplied source snapshots do not include an initialized `moda-interact-system-test` submodule. On claim, inspect the canonical system-test repository and use its existing executor/fixture/assertion/helper structure. If no existing billing integration harness is available, stop and report the exact gap rather than inventing a new framework or placing a large test in one file.

## Required scenarios

### A. Unknown local plan handle

- Provider fixture returns exactly one valid `FlatRatePrice` handle `starter`.
- Neither `BillingPlan` nor `MerchantPricingPlan` contains `starter`.
- Reconciliation records `observedShopifyPlanHandle = starter`, sets status `UNMAPPED`, keeps `lastSyncErrorCode` and `lastSyncErrorAt` null, and records all provider-returned usage-event handles in `unmappedShopifyUsageEventHandles`.
- Admin Unmapped Subscriptions shows the exact handle and the Register Plan action.
- No repeated retry is scheduled solely for this configuration condition.
- An administrator registers the exact `starter` catalogue plan. Existing operational plan repair/materialisation is then requested through the existing workflow.

### B. Plan exists but usage-event catalogue is incomplete

- Provider fixture returns `starter` and usage handles `bronze-top-up`, `silver-top-up`, `gold-top-up`.
- `MerchantPricingPlan(starter)` has only `bronze-top-up` and `silver-top-up`.
- The plan materialises/resolves normally.
- Subscription remains provider-derived ACTIVE or TRIALING.
- `unmappedShopifyUsageEventHandles` contains exactly `gold-top-up`.
- `lastSyncErrorCode` and `lastSyncErrorAt` remain null.
- Admin shows the active subscription and exact missing handle, with a link to the existing plan editor.
- Mapped Bronze/Silver purchase options remain available; Gold is unavailable until configured.

### C. Administrator resolves a usage-event mapping

- Add the exact `gold-top-up` `MerchantPricingUsageEvent` to the `starter` catalogue plan through the existing Admin plan editor/action.
- Run the next normal Background reconciliation using the same provider response.
- Verify `unmappedShopifyUsageEventHandles` becomes `[]`.
- Verify Subscription status remains ACTIVE/TRIALING and no sync error is created.
- Verify the usage-event-only Admin attention row disappears.

### D. Provider/catalogue directionality

- Provider returns only `bronze-top-up`; catalogue contains Bronze, Silver and Gold. No missing-provider error or diagnostic is produced for Silver/Gold.
- Provider returns a handle absent from the catalogue. Only that provider-returned handle is recorded as unmapped.
- No catalogue event absent from Shopify is materialised, offered for purchase or reported as missing.
- Duplicate provider handles produce one deterministic array entry.

### E. Recovery reporting handle independence

- Test paid plans with `shopifyRecoveryUsageEventHandle` set to an arbitrary customer-defined value, set to a value not in provider `usageEventHandles`, and null.
- In all cases, a valid plan with a valid included allowance/billing cycle materialises and activates.
- Verify no `MISSING_USAGE_METER` is produced from this reporting handle.
- Verify the existing included-recovery App Events publisher still uses the configured reporting value where configured; do not submit a billable TieredPrice event or create a charge in this test.

### F. Actual failures remain failures

- A real Shopify Partner API error still follows existing provider-failure handling and preserves the original provider error message/details.
- A real database transaction or billing-period integrity failure retains existing SYNC_ERROR handling.
- A malformed provider response with no valid flat-rate plan handle remains a provider-contract failure; Admin must not guess a handle.
- A genuine legacy single-pack meter validation, if exercised by an existing legacy fixture, remains separate from MerchantPricingUsageEvent mapping and is not confused with the new array.

## Test isolation and evidence

- Use disposable PostgreSQL and the existing provider fixture/stub mechanism. Do not use a production or developer database.
- No real subscription charge, usage charge, top-up purchase or refund is created.
- No real Shopify mutation is needed. If the test harness requires a live Shopify development store or a paid approval to prove a provider read, stop and request explicit approval before performing it.
- Keep test executors, fixtures, assertions and helpers modular. Do not create a single oversized test file.
- Prove that the database container and any Redis/container resources are cleaned up.
- Report actual test commands, database/container image, test fixtures, repository commit SHAs and submodule pins. Distinguish mocked provider evidence from any live Shopify evidence.

## Acceptance criteria

- [ ] All scenarios A-F pass.
- [ ] No `MISSING_USAGE_METER` caused by `shopifyRecoveryUsageEventHandle`.
- [ ] No sync error for provider-returned but unmapped `MerchantPricingUsageEvent` handles.
- [ ] Unknown local plan mapping is `UNMAPPED`, with null sync-error fields.
- [ ] ACTIVE/TRIALING status is preserved when only usage-event mappings are incomplete.
- [ ] Admin can see exact handles and resolve them through existing catalogue UI.
- [ ] Existing purchase/reporting/refund/credit-accounting behavior remains unchanged.
- [ ] Disposable services are cleaned up and evidence is reproducible.

## Stop condition

Submit the system-test report and stop for architect review. Do not deploy, migrate a hosted database, approve a live paid subscription or create a real Shopify usage charge.
