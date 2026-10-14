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
status: ready
priority: 22
executor: null
claimed_at: null
attempt: 1
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
- [ ] Add authorisation/tenant/CAS/audit, duplicate-submit/conflict-reload, missing-plan, history isolation and independent-field fallback regressions. Existing focused tests cover most cases, but browser-posted Shop ID tampering is not rejected/tested, and the new parser test has a TypeScript diagnostic.

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
- [ ] Policy History is scoped to the trusted Shop/environment/context and shows actor, time, reason and changed fields; stale submissions offer recovery. Mutation target scope is currently taken directly from a browser-submitted `shopId` and is not bound to the server-selected tenant.

## Validation

- [x] Focused Tenant Directory component/server-action tests (27 passed across six focused files; Node emitted existing `MODULE_TYPELESS_PACKAGE_JSON` warnings).
- [ ] Relevant typecheck/lint/build scripts. Changed production-file ESLint passed with zero errors. `tsc --noEmit` and `npm run build` failed because the implementation worktree's database submodule is at `5f6c7d473771ca7beac8dd64729f228438d95bc4`, which lacks ARCH-038 `CommerceModelPolicy` types/actions; the required DATABASE-001 schema is available at task commit `40674aea91527d5645aa922c9627af673b487223`. Typecheck also reported a type error in `tests/unit/commerce-model-shop-policy-fields.test.ts`.
- [x] `git diff --check` for the implementation worktree.

## Stop Condition

Once all defined work items, acceptance criteria and required validation are satisfied, submit the Completion Report and return for authorised review. Do **not** start enabled or neighbouring tasks. Required evidence unavailable in this environment must be recorded as unverified, not claimed passed.

## Implementation Notes

Use the launcher-resolved dedicated parent and implementation worktrees with matching `task/ARCH-038-ADMIN-003` branches and record physical isolation, synchronization and submodule evidence in the Completion Report. This definition is portable and **not yet materialised** in the developer's Git workspace. Follow the actual repository scripts rather than assuming uniform package commands. No `docs/decisions/**/_index.md` changes until the developer explicitly ends this architecture session. Preserve unrelated ARCH-037 and other in-progress changes; reconcile newer checkouts before implementation.

## Completion Report

### Status

Changes Requested — Attempt 1. The focused behavior suite passes, but trusted Shop mutation scope and a valid dependency schema/typecheck/build remain unresolved. Attempt 1 is returned to `ready`; attempt remains 1. Implementation edits remain uncommitted in the canonical implementation worktree and are preserved for correction.

### Files Changed

- `src/app/(protected)/page.tsx`
- `src/app/actions/commerce-model-shop-policy.ts`
- `src/components/admin/commerce-model-policy/live-shop-policy.tsx`
- `src/components/admin/tenant-detail-panel.tsx`
- `src/components/admin/tenant-table.tsx`
- `src/lib/admin/commerce-model-shop-policy-fields.ts`
- `src/lib/admin/commerce-model-shop-policy.ts`
- `tests/unit/commerce-model-shop-policy-action.test.mjs`
- `tests/unit/commerce-model-shop-policy-component.test.mjs`
- `tests/unit/commerce-model-shop-policy-fields.test.ts`
- `tests/unit/commerce-model-shop-policy-page.test.mjs`
- `tests/unit/commerce-model-shop-policy-tenant-panel.test.mjs`
- `tests/unit/commerce-model-shop-policy.test.ts`

### Work Completed

- Added SUPER_ADMIN-only LIVE Shop dashboard reads, sparse Shop override mutations with CAS and transactional audit, and Tenant Directory CommerceAgent controls.
- Added Platform/Price Plan/Merchant/Effective provenance, current-plan resolution/link, scoped paginated history, and explicit unresolved-plan display.
- Added focused service/parser/action/component/page/tenant-panel tests for role gates, sparse inheritance, audit/CAS behavior, UI errors, concurrent submission, history pagination, and plan resolution.

### Validation Results

- Focused suite: **PASS**, 27 tests across six files; existing Node module-type warnings emitted for `.ts` tests.
- Changed production-file ESLint: **PASS**, zero errors.
- `git diff --check`: **PASS**.
- `./node_modules/.bin/tsc --noEmit`: **FAIL**. Prisma-generated types do not include `CommerceModelPolicy` or the ARCH-038 audit action because the implementation worktree's database submodule is pinned at `5f6c7d473771ca7beac8dd64729f228438d95bc4`. The new `tests/unit/commerce-model-shop-policy-fields.test.ts` also reports an incompatible inferred `FormData` fixture type.
- `npm run build`: **FAIL** at Next.js typecheck after successful production compilation. The same stale generated Prisma schema produces errors in the ADMIN-003 service/action and the existing ADMIN-001/002 policy modules. Existing BullMQ optional/dynamic dependency warnings also appear but are not the failure cause.

### Deviations

- The implementation branch has no published `origin/task/ARCH-038-ADMIN-003` ref. The parent task branch was synchronized by merging current `origin/main` into the existing claim branch and published at `b65b308e517b3ba91eba4a1dfc8736559614d1a3`.
- The canonical implementation worktree contains the task changes as uncommitted edits plus an unexplained untracked `typescript` file. That file was not opened, staged, changed, or included in the task file list.

### Assumptions

None

### Unresolved Issues

- `saveLiveShopBudgetAction` trusts `shopId` read directly from submitted `FormData`; only existence and SUPER_ADMIN role are checked. Bind the target to a server-verified selected-tenant scope and reject tampering; add a regression that changes the submitted ID to another valid Shop and verifies no mutation/audit occurs.
- The implementation submodule is at `5f6c7d473771ca7beac8dd64729f228438d95bc4`; the required ARCH-038 DATABASE-001 schema commit `40674aea91527d5645aa922c9627af673b487223` is available on database `origin/task/ARCH-038-DATABASE-001`. Point the implementation worktree at the completed dependency commit, regenerate Prisma Client, fix any remaining task-local type errors, and rerun typecheck/build.
- Implementation edits are uncommitted and not published on an implementation task remote branch. Preserve the unexplained untracked `typescript` file unless its owner confirms it belongs to this task.

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

- `saveLiveShopBudgetAction` parses `shopId` from submitted `FormData`; `mutateLiveShopPolicy` only verifies that the Shop exists and then scopes database mutations to that supplied ID. No action test changes the submitted ID to another existing Shop.
- Focused suite: **27 passed, 0 failed** across `commerce-model-shop-policy.test.ts`, `commerce-model-shop-policy-fields.test.ts`, and four action/component/page/tenant-panel `.mjs` files.
- Changed production-file ESLint and implementation `git diff --check`: **PASS**.
- Typecheck/build fail because Prisma generation used database submodule commit `5f6c7d473771ca7beac8dd64729f228438d95bc4`, which lacks the ARCH-038 policy schema; the task-local fields test also has a TypeScript fixture typing error. Required schema commit `40674aea91527d5645aa922c9627af673b487223` is available in database `origin/task/ARCH-038-DATABASE-001`.
- Parent task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-038-ADMIN-003` is clean and published at `b65b308e517b3ba91eba4a1dfc8736559614d1a3`. Implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-038-ADMIN-003` is on `task/ARCH-038-ADMIN-003` with uncommitted task files and untracked `typescript`; no remote implementation task ref exists. Recursive `database` submodule is initialized at `5f6c7d473771ca7beac8dd64729f228438d95bc4`.

### Remaining Issues

- Trusted Shop target binding, schema/toolchain alignment, and all task-owned implementation publication remain outstanding.

### Follow-up

Preserve Attempt 1 and its current implementation worktree. A new developer claim increments once to Attempt 2 after the worktree is clean and the claim workflow succeeds.
