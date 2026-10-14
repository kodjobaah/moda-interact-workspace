---
id: ARCH-038-ADMIN-003
architecture_id: ARCH-038
title: Manage Merchant LIVE CommerceAgent overrides
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 22
executor: null
claimed_at: null
attempt: 3
depends_on:
  - ARCH-038-DATABASE-001
  - ARCH-038-ADMIN-001
enables:
  - ARCH-038-SYSTEM-TEST-001
created: 2026-10-13
updated: 2026-10-14
---
# Manage Merchant LIVE CommerceAgent overrides

## Architecture

- Architecture ID: `ARCH-038`
- Architecture document: `docs/architecture/ARCH-038-commerce-agent-execution-budget-policies.md`
- Coordinator: `moda_architect`
- Assigned agent: `moda_admin`
- Repository: `moda-interact-admin`

## Objective

Allow authorised Moda administrators to set or clear per-Shop LIVE budget overrides from Tenant Directory merchant details.

## Context

Merchant override is the highest-priority LIVE setting but must never be editable by merchants themselves.

## Scope

- Add a separate **CommerceAgent Policy** section to the internal Tenant Directory merchant detail/admin view, reusing the schema-driven Admin editor from ADMIN-001 with independent **Override / Inherit** controls.
- Expose Shop overrides and a read-only **Platform / current Price Plan / Merchant / Effective** per-field comparison, with accurate source labels. Show the current subscribed plan and link to its existing editor when verified.
- Add authorised CAS mutations, required audit reason, clear-to-inherit, disabled repeat submission, inline validation, conflict/reload recovery and a scoped paginated **Policy History** using CommerceAuditEvent.
- Include unknown/no-current-plan and mismatched-plan provenance without inventing a plan selection or implying an effective plan override.

## Out of Scope

- No Shopify/WooCommerce/merchant-facing settings page or write endpoint.
- Do not modify existing ShopBillingPolicyOverride or Preview policy.

## Requirements

- Target Shop comes from trusted internal merchant ID, not a spoofable request scope.
- Clearing either Shop `budget` key deletes that explicit key, then falls back to Price Plan and Platform without copying inherited values; reject JSON null, empty override and unsupported versions/keys. Use the ADMIN-001 allowlisted field descriptors.
- Reject cross-shop operations and expired/invalid Admin access.

## Work Items

- [x] Build internal merchant budget settings read and mutation flow using shared Admin policy editor; display independent controls and current verified plan link (when available).
- [x] Render effective-policy comparison with per-field Platform/Plan/Merchant/Effective source labels; provide explicit unknown/current-plan-unresolved state.
- [x] Present scoped, paginated audit history with before/after changes, reason and actor.
- [x] Add authorisation/tenant/CAS/audit, duplicate-submit/conflict-reload, missing-plan, history isolation, independent-field fallback, stale-form replay across clear, and explicit empty Policy History regressions.

## Interfaces / Contracts

Consumes DATABASE-001 `CommerceModelPolicy` (`context=LIVE`, `scope=SHOP`, sparse JSONB `budget`), ADMIN-001 reusable Admin editor/field descriptors, and existing BillingPlan/MerchantPricingPlan resolution for display. No Background-owned runtime code.

## Dependencies

- `ARCH-038-DATABASE-001`
- `ARCH-038-ADMIN-001`

## Enables

- `ARCH-038-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Only platform admins can change Shop overrides.
- [x] Per-field inheritance and source display match the agreed hierarchy.
- [x] Preview policies and other Shop records remain untouched.
- [x] UI displays verified plan (with link), per-field inheritance, effective value and source even when plan resolution is unavailable.
- [x] Policy History is scoped to the trusted Shop/environment/context and shows actor, time, reason and changed fields; stale submissions offer recovery. The server-issued Shop/admin scope is verified before mutation, and the durable audit revision prevents stale forms from becoming valid after clear.

## Validation

- [x] Focused Tenant Directory component/server-action tests (27 passed across six focused files; Node emitted existing `MODULE_TYPELESS_PACKAGE_JSON` warnings).
- [x] Attempt 3 focused ADMIN-003 suite: **38 passed, 0 failed** across seven focused files, including create-clear-version-0 replay rejection without a policy/audit write and explicit empty-history rendering. Node emitted existing `MODULE_TYPELESS_PACKAGE_JSON` warnings for TypeScript test files.
- [x] Attempt 3 `tsc --noEmit`: passed.
- [x] Attempt 3 changed production-file ESLint: passed with zero errors.
- [x] Attempt 3 `npm run build`: passed, including Prisma generation and Next.js TypeScript/build phases. Existing BullMQ dynamic-dependency and optional `@valkey/valkey-glide` warnings remain non-fatal.
- [x] Attempt 3 `git diff --check origin/main...HEAD`: passed.

## Stop Condition

Once all defined work items, acceptance criteria and required validation are satisfied, submit the Completion Report and return for authorised review. Do **not** start enabled or neighbouring tasks. Required evidence unavailable in this environment must be recorded as unverified, not claimed passed.

## Implementation Notes

Use the launcher-resolved dedicated parent and implementation worktrees with matching `task/ARCH-038-ADMIN-003` branches and record physical isolation, synchronization and submodule evidence in the Completion Report. This definition is portable and **not yet materialised** in the developer's Git workspace. Follow the actual repository scripts rather than assuming uniform package commands. No `docs/decisions/**/_index.md` changes until the developer explicitly ends this architecture session. Preserve unrelated ARCH-037 and other in-progress changes; reconcile newer checkouts before implementation.

## Completion Report

### Status

Submitted for authorised review — Attempt 3 developer self-review passed. Completion remains pending the authorised reviewer. Attempt 1 and Attempt 2 review history is preserved below.

### Files Changed

- `database` (submodule pointer to DATABASE-001 commit `40674aea91527d5645aa922c9627af673b487223`)
- `src/app/(protected)/page.tsx`
- `src/app/actions/commerce-model-shop-policy.ts`
- `src/components/admin/commerce-model-policy/live-shop-policy.tsx`
- `src/components/admin/tenant-detail-panel.tsx`
- `src/components/admin/tenant-table.tsx`
- `src/lib/admin/commerce-model-shop-policy-fields.ts`
- `src/lib/admin/commerce-model-shop-policy-scope.ts`
- `src/lib/admin/commerce-model-shop-policy.ts`
- `tests/unit/commerce-model-shop-policy-action.test.mjs`
- `tests/unit/commerce-model-shop-policy-component.test.mjs`
- `tests/unit/commerce-model-shop-policy-fields.test.ts`
- `tests/unit/commerce-model-shop-policy-scope.test.mjs`
- `tests/unit/commerce-model-shop-policy-page.test.mjs`
- `tests/unit/commerce-model-shop-policy-tenant-panel.test.mjs`
- `tests/unit/commerce-model-shop-policy.test.ts`

### Work Completed

- Added SUPER_ADMIN-only LIVE Shop dashboard reads, sparse Shop override mutations with CAS and transactional audit, and Tenant Directory CommerceAgent controls.
- Added an HMAC-signed, expiring scope bound to the server-resolved Shop and authenticated Admin; mutation validates that scope before opening a transaction and rejects a different posted Shop ID.
- Added Platform/Price Plan/Merchant/Effective provenance, current-plan resolution/link, scoped paginated history, and explicit unresolved-plan display.
- Preserved a monotonic Shop/environment CAS revision using the durable audit stream across policy-row deletion and recreation; legacy clear events cannot reset the revision.
- Updated the implementation database submodule to the completed DATABASE-001 schema commit and regenerated Prisma Client.
- Added focused service/parser/scope/action/component/page/tenant-panel tests for role gates, signed-scope tampering, sparse inheritance, audit/CAS behavior, stale-form replay after clear, empty history, UI errors, concurrent submission, history pagination, and plan resolution.

### Validation Results

- Focused seven-file suite (Attempt 3): **PASS**, 38 tests, 0 failures; existing Node module-type warnings emitted for `.ts` tests.
- Changed production-file ESLint: **PASS**, zero errors.
- `./node_modules/.bin/tsc --noEmit` (Attempt 3): **PASS** with the accepted DATABASE-001 schema generated into Prisma Client.
- `npm run build` (Attempt 3): **PASS**. Prisma generation, Next compilation, TypeScript, page data and production trace stages completed. Existing BullMQ dynamic-dependency and optional `@valkey/valkey-glide` warnings are non-fatal.
- `git diff --check origin/main...HEAD`: **PASS**.

### Deviations

- Attempt 3 implementation changes are committed and published at `3f8c5b645c688c8446504666a3c4dd44920ce678` on `origin/task/ARCH-038-ADMIN-003`; the database submodule remains at `40674aea91527d5645aa922c9627af673b487223`. Both canonical task worktrees were clean before this report update.
- The implementation branch is synchronized with its remote; the parent report branch was synchronized before this reconciliation.
- The implementation worktree's database submodule is initialized at `40674aea91527d5645aa922c9627af673b487223`; recursive synchronization passed during Attempt 2 preparation.

### Assumptions

None

### Unresolved Issues

None identified in the developer review. Authorised review and completion decision remain pending.

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending implementation

### Follow-up

None

## Developer Self-Review - Changes Requested

### Review Result

Changes Requested — Attempt 1. Transition to `ready` with `executor: null` and `claimed_at: null`; preserve `attempt: 1`. Do not create Attempt 2 in this review.

### Required Corrections

1. Replace the browser-controlled `shopId` mutation target with a server-bound or otherwise verifiable selected-tenant scope. Add an action-level cross-Shop tampering test proving a different valid Shop ID cannot be written or audited.
2. Reconcile the implementation worktree's `database` submodule with the completed DATABASE-001 task commit `40674aea91527d5645aa922c9627af673b487223`, regenerate Prisma Client, fix the `commerce-model-shop-policy-fields.test.ts` type error and any remaining task-local diagnostics, then rerun `tsc --noEmit` and `npm run build`.
4. Commit and push task-owned implementation changes on `task/ARCH-038-ADMIN-003` after resolving the unexplained untracked `typescript` file's ownership; do not stage that file without confirming it belongs to this task.

### Evidence Reviewed

- Server page mints scope from its server-resolved selected Tenant and authenticated Admin. The mutation verifies the HMAC scope, compares it with the posted `shopId`, and rejects cross-Shop mismatch before the transaction.
- Focused suite: **34 passed, 0 failed** across the seven ADMIN-003 unit test files, including different-Shop ID tampering and invalid/expired/other-admin scope cases.
- `tsc --noEmit`, changed production-file ESLint, `npm run build`, and implementation `git diff --check origin/main...HEAD`: **PASS**.
- Scope revision review: create from no row uses version 0 and creates a row at schema default version 1; clearing deletes the row and audit metadata resets next version to 0. The dashboard reports 0 when no row exists. Therefore the original unexpired version-0 form can pass the CAS check again after clear.
- Component renders `No policy changes recorded.` for empty history, but no component test asserts that state.
- Implementation branch `task/ARCH-038-ADMIN-003` is published at `d8da968f5fa12f7a1cb1b08e429c6958c511115e`; the database submodule is at accepted dependency commit `40674aea91527d5645aa922c9627af673b487223`. Parent branch before this report update is published at `5dd2bf8a8f16c03a09c601cebce504f6b4222f78`.

### Remaining Issues

- Monotonic CAS revision across Shop-policy deletion and the explicit empty Policy History test remain outstanding.

### Follow-up

Preserve Attempt 1 and its current implementation worktree. A new developer claim increments once to Attempt 2 after the worktree is clean and the claim workflow succeeds.

## Developer Self-Review - Changes Requested - Attempt 2

### Review Result

Changes Requested — Attempt 2. The selected Shop/admin scope is now server-signed and validated, the required DATABASE-001 schema is pinned, and all executed focused/build validations pass. Return the task to `ready`, clear `executor`/`claimed_at`, and preserve `attempt: 2`.

### Required Corrections

1. Prevent stale version-0 forms from being replayed after a Shop override is cleared. Keep a monotonic per-Shop/environment revision across row deletion and compare every mutation against that retained revision; do not reset audit `nextEditVersion` or the dashboard CAS version to zero after clear. Add a regression that loads a no-row version-0 form, creates an override, clears it, then replays that original form and proves the action rejects it without recreating policy or appending an audit event.
2. Add a component test asserting the empty Policy History state is rendered when the history list is empty.
3. Preserve the current server-issued HMAC Shop/admin scope checks and corrected database submodule commit. Rerun the seven-file focused suite, `tsc --noEmit`, changed-file ESLint, `npm run build`, and `git diff --check`.

### Evidence Reviewed

- Attempt 2 implementation is committed/pushed at `d8da968f5fa12f7a1cb1b08e429c6958c511115e`; `database` points at `40674aea91527d5645aa922c9627af673b487223`.
- Focused ADMIN-003 tests: **34 passed, 0 failed**. Typecheck, changed-file ESLint, production build, and implementation diff check pass. Build emits existing non-fatal BullMQ/Valkey warnings.
- HMAC scope is issued from the server-resolved selected Tenant and authenticated Admin, expires, verifies Admin identity, and is checked before a transaction. A posted different existing Shop ID and tampered/expired/other-admin scopes are rejected in tests.
- CAS replay defect: after create, policy row version is 1; clear deletes that row and writes audit `nextEditVersion: 0`; dashboard then exposes version 0. The original unexpired form from before create carries expected version 0 and can pass again after clear.
- UI contains the empty-history message, but current component tests omit an assertion for it.
- Canonical parent and implementation task worktrees are clean and synchronized; parent task report is the only pending file change from this reconciliation.

### Remaining Issues

- Monotonic revision must survive clearing the sparse Shop policy row.
- Explicit empty Policy History component assertion is missing.

### Follow-up

After these corrections are committed/pushed on the same implementation task branch and focused checks pass, use `/moda_developer_update ARCH-038-ADMIN-003` to reconcile Attempt 2 again. Do not create Attempt 3 in this review.

## Developer Self-Review - Passed - Attempt 3

### Review Result

Passed — Attempt 3. The task is submitted for authorised review with `status: review`; `executor` and `claimed_at` are cleared. Because `completion_mode: developer`, this is not a completion decision.

### Evidence Reviewed

- Attempt 3 implementation commit `3f8c5b645c688c8446504666a3c4dd44920ce678` is published and matches `origin/task/ARCH-038-ADMIN-003`; both implementation and parent worktrees were clean before this report update.
- `shopPolicyRevision` uses the stable Shop/environment audit identity and latest transition to retain a logical CAS revision across deletion/recreation. Clear advances the audit revision; legacy clear records with `nextEditVersion: 0` are guarded by their previous version.
- Regression coverage exercises create, clear, dashboard revision, rejected replay of the original version-0 form without policy/audit writes, and subsequent authorised recreation at the next monotonic version. The component test explicitly asserts `No policy changes recorded.` for empty history.
- Focused seven-file suite: **38 passed, 0 failed**. `tsc --noEmit`, changed production-file ESLint, `npm run build`, and `git diff --check origin/main...HEAD`: **PASS**. Build warnings for existing BullMQ dynamic dependency and optional Valkey package are non-fatal.

### Remaining Issues

None identified. Await authorised review; do not start the enabled system-test task from this developer review.

### Follow-up

Authorised reviewer to review Attempt 3 and decide completion. Do not merge the task branch to main as part of this report update.
