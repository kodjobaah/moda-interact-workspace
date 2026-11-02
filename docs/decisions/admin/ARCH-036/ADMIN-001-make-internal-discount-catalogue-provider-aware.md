---
id: ARCH-036-ADMIN-001
architecture_id: ARCH-036
title: "Show provider status and merchant selection separately in Admin"
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 60
executor: developer
claimed_at: 2026-11-02T14:30:35Z
attempt: 1
depends_on: ["ARCH-036-BACKGROUND-001"]
enables: ["ARCH-036-SYSTEM-TEST-001"]
created: 2026-10-12
updated: 2026-11-02
---

# ARCH-036-ADMIN-001 — Show provider-aware discount provenance in Moda Admin

## Architecture

- Architecture ID: `ARCH-036`.
- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Coordinator: `moda_architect`.
- Canonical parent task definition is published on `task/ARCH-036-ADMIN-001`. Implementation remains unclaimed; prepare it through `/moda_developer_create` before editing application code.

## Objective

Make Admin discount catalogue and recovery policy presentation provider-aware without conflating provider status with merchant selection.

## Context


The existing Admin console reads discount rows and ShopSettings/override FK. BACKGROUND-001 adds **Woo rows only** into the same table. For Woo, `providerStatus` is provider lifecycle and `isAvailable` is merchant selection; for Shopify, accepted ARCH-052-BACKGROUND-009 also makes `isAvailable` merchant selection; provider availability is represented separately. Background owns Woo provider synchronisation; API-002 owns Woo merchant checkbox changes. Admin must keep merchant selection and provider validity distinct on both platforms.

## Scope

Update internal list/filter/badges and recovery override presentation for **Woo**. Display provider, provider status, Woo selected-for-recovery flag and catalogue freshness independently. Preserve existing override actor/reason/audit/expiry behaviour and Shopify single-FK controls without changing Shopify selection/sync.

## Out of Scope

- No new PostgreSQL discount/coupon catalogue, selection, sync staging or join **tables**; reuse existing physical `ShopifyDiscountCatalogue`, `ShopifyDiscount`, policy and attempt records.
- No other repository's implementation, incidental feature work, migration-history rewrite, or `_index.md` modification.
- No new unsupported coupon promises, billing changes or checkout mutation.
- No implementation of tasks listed under Enables; return to the architect at the defined stop point.

## Requirements

- For Woo, never interpret `isAvailable=false` as deleted/provider unavailable; show unselected ACTIVE coupons as provider-valid. For Shopify, preserve the accepted ARCH-052-BACKGROUND-009 meaning: `isAvailable` is merchant selection; use provider status/current-catalogue/liveness fields for provider validity.
- Only ACTIVE/current/in-date/fixedSelectable rows can appear as assignable Admin choices. These predicates establish catalogue/code usability, not checkout eligibility or guaranteed redemption. Display expired, removed, unselectable and revoked/stale rows distinctly; missing optional provider facts must not be invented or labelled checkout-valid.
- Admin override FIXED retains one **real same-Shop discount FK** and is independent of Woo merchant checkbox selections; use valid provider/catalogue predicates rather than requiring a Woo checkbox to be checked. Preserve Shopify override behaviour, audit and authorization without inventing multi-coupon override storage or placing Woo namespace in an FK.
- No SQL/schema changes, historical row deletions, security/role expansion or cross-tenant catalogue leakage.

## Work Items

- [ ] Update `src/lib/admin/data.ts` catalogue queries and `src/components/admin/tenant-recovery-settings.tsx` presentation so Woo catalogue validity, assignability and merchant selection are separate; preserve existing Shopify behavior.
- [ ] Preserve Admin single-FK override and audit semantics.
- [ ] Add provider-aware Shop, empty/error and inactive coupon fixtures.
- [ ] Test merchant/Admin isolation and Shopify regression.

## Interfaces / Contracts


Existing Prisma discount/policy rows and shop/role authorisation. No API-001 read proxy or new Shared contract; no new schema.

## Dependencies

- `ARCH-036-BACKGROUND-001`

## Enables

- `ARCH-036-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Admin shows ACTIVE unselected coupons distinctly from removed/expired coupons.
- [ ] Both list reads and override writes enforce the target Shop/provider; stale, removed, expired, unselectable and foreign-Shop IDs are rejected on the server, including rows invalidated after the list was loaded.
- [ ] Existing Shopify Admin override and audit work **without changing Shopify behaviour**; Woo FIXED override can choose a valid same-Shop coupon independently of the merchant checkbox flags.
- [ ] No database change.

## Validation

- [ ] Focused Admin read/write tests for ACTIVE checked and unchecked Woo rows, stale catalogue, expiry, removed/unselectable rows, foreign-Shop IDs and a stale-choice write; prove unchecked valid Woo coupons remain assignable by Admin while existing Shopify predicates remain unchanged.
- [ ] Verify desktop/narrow layouts, provider/selection labels and existing override actor/reason/audit/expiry behavior; no merchant checkbox-write endpoint or new permissions.
- [ ] Role/tenant constraints, lint, typecheck/build and `git diff --check`.

## Stop Condition

After the bounded work, Acceptance Criteria and required Validation are complete, update the Completion Report, set the task to `review`, return to `moda_architect`, and STOP. Do not start dependent tasks or write `_index.md`.

## Implementation Notes

Do not change Shopify app, Shopify sync, CommerceAgent, recovery workers, or Woo plugin from Admin. Admin may expose only Woo catalogue status/selection and the existing single-FK override.

For developer execution, use the canonical `/moda_developer_create ARCH-036-ADMIN-001` preparation/worktree process once the task is materialised and Ready. For agent execution use `/moda-task ARCH-036-ADMIN-001`. Do not implement from a shared checkout merely because the patch can be applied there. Validate using the repository's **actual** `package.json`/tooling and record launcher-resolved physical parent and implementation worktrees, start-of-attempt sync/submodules, branch/commit and test evidence. Never accept an unverified claim of test success.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-11-02T14:30:35Z. Attempt 0 review history is preserved below.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run; task not claimed.

### Deviations

None.

### Assumptions

The implementation executor will verify local checkout, dependencies and available toolchain at claim time.

### Unresolved Issues

None recorded by an implementation executor.

### Architectural Concerns

Report schema, cross-service or provider-proof deviations to `moda_architect` instead of silently expanding scope.

## Architect Review

### Review Status

Pending.

### Review Notes

Portable definition only, not implementation acceptance.

### Reviewed Files

Current 12 October 2026 source snapshot used to define ownership; implementation not yet reviewed.

### Validation Reviewed

None from this task.

### Architecture Conformance

To be determined after implementation inspection.

### Follow-up

Await canonical materialisation, execution and review.

## Definition reconciliation — 2026-11-02

Admin main 420b86a still filters running/selectable discounts using isAvailable:true in src/lib/admin/data.ts (around lines 342–370), and tenant-recovery-settings.tsx presents Shopify-specific catalogue/override labels. Provider-aware Woo display and checkbox-independent Woo override choices remain unimplemented. Apply the corrected Shopify selection semantics above and run the required tenant/override/regression tests.

## Implementation readiness — 2026-11-02

Ready, Attempt 0, unclaimed. The accepted Background prerequisite is complete. Implement only Admin queries, UI and server-side override validation; neither Commerce work nor new provider fetching is a prerequisite. Keep developer-controlled completion: submit for architect acceptance, then await the explicit developer completion decision.


## Architect local implementation review — Attempt 1, 2 November 2026

### Decision and lifecycle

**Changes requested on the local working-tree implementation; no architect acceptance.** The developer requested review before formal submission. Preserve `status: in_progress`, `executor: developer`, the original claim timestamp, Attempt 1 and developer-controlled completion. Do not mark this task Complete, clear its active claim, or promote ARCH-036-SYSTEM-TEST-001. The earlier Completion Report placeholders still await developer reconciliation through `/moda_developer_update ARCH-036-ADMIN-001`.

Reviewed the eight changed/untracked files in the canonical implementation worktree, based on implementation HEAD `420b86aa90ca9dbb13f4c1af796ee7b60d38d05f`. These implementation changes are uncommitted and unpublished; this review does not publish them. The parent review note is separately published on the task branch.

### Findings

1. **P2 — enforce provider identity on the Shopify path too.** `src/lib/admin/discount-eligibility.ts:44` returns `discount.isAvailable` for Shopify after shared catalogue checks, before validating provider identity. A same-Shop ACTIVE/current row with `shopifyDiscountNodeId: "woo:coupon:27"`, `providerType: "WooCoupon:percent"`, `isAvailable: true` and `fixedSelectable: true` returns assignable for a SHOPIFY Shop. The database schema does not enforce provider identity against the Shop platform. Both the list and override writer use this helper, so such a wrong-provider row can be displayed/assigned despite the task's explicit target-provider requirement. Validate the existing Shopify identity/type shape without changing the existing merchant-selection predicate; add wrong-provider tests in both directions. The observed input does not demonstrate cross-tenant access: same-Shop filtering is already present.
2. **P2 — execute the required read/write security cases.** The five focused checks in `tests/security/admin-tenant-recovery-policy.test.mjs` and `admin-shopify-discount-sync.test.mjs` use source-string assertions. The four added unit tests execute only the eligibility helper. No changed test actually runs the catalogue read or `upsertTenantRecoveryPolicyOverrideAction` against a controlled transaction to prove unchecked Woo assignment, foreign-Shop/wrong-provider rejection, invalidation between listing and submit, role denial, and atomic audit/override rollback. Add behavioral coverage at the real action/service boundary (with a suitable isolated database fixture for transaction behavior) and verify the existing Shopify path. A regex matching `Serializable` or an audit call is not evidence that those behaviors hold.

### Validation and positive findings

- Independently ran `node --conditions=import --import tsx --test tests/unit/arch036-admin-discount-eligibility.test.ts tests/security/admin-tenant-recovery-policy.test.mjs tests/security/admin-shopify-discount-sync.test.mjs`: **9/9 passed** (4 helper tests and 5 source-inspection tests), Node 24.19.0.
- Independently imported the actual eligibility helper with the Shopify/Woo identity-mismatch fixture described above: returned `{ "wrongProviderAssignable": true }`. No source changes were needed for reproduction.
- `git diff --check` passed.
- Inspected same-Shop queries, current-generation/unavailable/expiry predicates, Woo checkbox-independent assignment, SUPER_ADMIN checks, existing reason/actor/expiry fields, audit and override in one serializable transaction, and provider-separated display. These are the appropriate implementation direction. No schema changes found.
- Executor-reported TypeScript, changed-file ESLint and production build passes are recorded as supplied evidence, not independently rerun. Existing BullMQ build warnings and repository-wide lint failure in `use-shop-brand-media-role.ts` remain reported baseline limitations.
- Required desktop/narrow-screen verification was not supplied or performed in this review; record it with the final developer submission.

### Follow-up

Fix the provider guard and add behavioral read/write coverage. Correct the new Shopify label/test wording that calls `isAvailable` provider availability: accepted ARCH-052 makes it merchant selection, although this task preserves Shopify's existing filter behavior. Complete the required desktop/narrow UI checks. Reconcile the Completion Report and publish the implementation through the developer workflow before requesting final acceptance; an explicit developer completion decision remains required after acceptance. No implementation edits or commits were made by the architect.

Reviewed working-tree fingerprint (SHA-256 of the ordered eight relative paths and file bytes, NUL-separated): `edaad7bfef545031d882bd0a4e9f256dd6734dcfae97a5f7421be3de761f6932`.


## Architect local correction review — Attempt 1, 2 November 2026

### Decision

**Changes requested: remaining validation gaps; no final architect acceptance.** The earlier Shopify/Woo identity regression is fixed. Keep the developer-owned `in_progress` claim and Attempt 1 unchanged. Implementation remains uncommitted; no downstream promotion or implementation publication is performed by this review.

### Verified correction

Shopify now rejects Woo IDs/types and no longer treats merchant selection as provider validity. Woo selection remains independent of assignment. Both list and write paths share eligibility checks. The server action calls the extracted override service and retains its SUPER_ADMIN guard, actor/reason/expiry handling and serializable transaction. The table presents merchant selection separately on both platforms. No schema changes were found.

### Remaining findings

1. **P2 — complete the requested behavioral security/transaction evidence.** The new service tests are useful and execute real service logic, but `tests/unit/arch036-admin-recovery-policy-override.test.ts:60–120` implements rollback itself by cloning state and committing only after the callback resolves. It cannot demonstrate PostgreSQL audit/override atomicity. Every service invocation supplies `authorize: async () => "admin-1"` (line 140), so actual role rejection remains covered only by source-string assertions. No new behavioral test invokes the catalogue read, and the successful Shopify case remains a helper test rather than an override service/action regression. Complete the prior review's isolated database transaction check, exercise real authorization denial with no writes, and add behavioral catalogue/read and successful Shopify override coverage. Record test-double evidence separately from database evidence; do not claim the former certifies database rollback.
2. **P2 — required visual validation remains outstanding.** The task explicitly requires desktop/narrow layout and label verification. Missing local AUTH_URL/database configuration explains the absent check but does not satisfy it. Use an isolated configured test app or a representative rendered fixture exercising the actual component and styles, with active selected/unselected, inactive/stale, empty/error and override states. Record screenshots/results for desktop and narrow widths before acceptance. Do not use persistent merchant data.

### Independent validation and limits

Ran under Node 24.19.0:
`node --conditions=import --import tsx --test tests/unit/arch036-admin-discount-eligibility.test.ts tests/unit/arch036-admin-recovery-policy-override.test.ts tests/security/admin-tenant-recovery-policy.test.mjs tests/security/admin-shopify-discount-sync.test.mjs`.

**14/14 passed:** 4 eligibility helper cases, 5 override service cases using transaction doubles, and 5 source-inspection security/UI cases. `git diff --check` passed. Executor-reported TypeScript, changed-file ESLint and production build passes were not independently rerun; optional BullMQ warnings remain reported. No visual verification was performed in this review.

The ten reviewed implementation files remain local and unchanged by the reviewer. Reconcile the stale Completion Report placeholders and publish through the developer workflow after required validation is complete. ARCH-036-SYSTEM-TEST-001 remains unpromoted. Historical findings and evidence are preserved above.

Reviewed working-tree fingerprint (SHA-256 of the ordered ten paths listed in this review's inspection and file bytes, NUL-separated): `b4579a46f0c8b4a5d3eff3cd7b9b8f4fe24e6835f5ff14c3829f73ccb87e0cb2`.
