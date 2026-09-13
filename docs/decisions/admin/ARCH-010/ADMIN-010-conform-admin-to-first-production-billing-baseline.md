---
id: ARCH-010-ADMIN-010
architecture_id: ARCH-010
title: Conform Admin billing controls to the clean first-production baseline
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 8
executor: null
claimed_at: null
attempt: 2
depends_on:
- ARCH-010-DATABASE-013
- ARCH-010-SHARED-008
- ARCH-010-ADMIN-001
enables:
- ARCH-010-ADMIN-002
- ARCH-010-ADMIN-004
- ARCH-010-ADMIN-008
created: 2026-09-12
updated: '2026-09-13'
---

# ARCH-010-ADMIN-010: Conform Admin billing controls to the clean first-production baseline

## Architecture

Read first:

```text
docs/architecture/ARCH-010-first-production-baseline.md
docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md
docs/architecture/ARCH-010-promotional-campaigns.md
```

ARCH-010 is the first-production baseline. `ARCH-010-ADMIN-001` remains immutable accepted history; this task removes compatibility behaviour that ADMIN-001 intentionally retained while the schema was still incremental.

## Objective

Make `moda-interact-admin` compile and behave exclusively against the clean ARCH-010 database/shared baseline, with no runtime dependency on removed development-era billing fields, enums, cancellation state, or direct promotional grants.

## Context

ADMIN-001 correctly moved lifetime-Free configuration to `PlatformBillingPolicy.lifetimeFreeRecoveryAllowance`, but it deliberately retained legacy audit/read compatibility for `BillingPlan.freeLifetimeConversationAllowance` because the old schema still existed at that point.

DATABASE-013 removes that legacy schema. SHARED-008 publishes the clean cross-service contract. The Admin repository must therefore stop reading, serialising, validating, presenting, or testing removed compatibility state.

## Scope

Inspect the current Admin repository before editing, especially:

```text
src/app/(protected)/billing/**
src/app/actions/billing-*.ts
src/components/admin/billing-*.tsx
src/lib/admin/billing*.ts
src/lib/admin/*promotion*.ts
src/lib/admin/*refund*.ts
src/lib/admin/types.ts
tests/security/*billing*.test.mjs
tests/security/*promotion*.test.mjs
```

Also search the repository for every removed baseline symbol named in Requirements below. Modify only files required to remove those dependencies and preserve accepted ARCH-010 Admin behaviour.

## Out of Scope

Do not:

- redesign the Admin billing UI;
- implement ADMIN-002/003 refund workflow;
- implement ADMIN-004/005/006 promotion workflow;
- implement ADMIN-007/008/009 upgrade-economics workflow;
- mutate database schema;
- reintroduce compatibility aliases;
- add merchant-facing routes;
- reopen or edit the accepted ADMIN-001 task history.

## Requirements

### 1. Lifetime-Free Admin state uses only the platform policy and shop counter

The current authority is:

```text
PlatformBillingPolicy.lifetimeFreeRecoveryAllowance
ShopEntitlementCounter(LIFETIME_FREE_RECOVERY_CREDITS)
```

Remove all Admin runtime/type/test dependencies on:

```text
BillingPlan.freeLifetimeConversationAllowance
BillingAllowanceAdjustment
FREE_RECOVERY_LIFETIME
FREE_ALLOWANCE_ADJUSTED
```

Do not preserve those fields in audit snapshot serializers merely because old development rows once contained them. There is no first-production compatibility requirement.

The accepted platform-policy control and its `PLATFORM_POLICY_CHANGED` audit behaviour remain.

### 2. Remove local subscription-cancellation compatibility

Search for and remove Admin code/contracts/UI/tests whose only purpose is the removed local cancellation state machine:

```text
SubscriptionCancellationRequest
SubscriptionCancellationMode
SubscriptionCancellationStatus
BILLING_CANCELLATION_REQUEST_RECEIVED
BILLING_CANCELLATION_COMPLETED
BILLING_CANCELLATION_REJECTED
```

Do not replace them with another local approval/request workflow. Provider subscription lifecycle/reconciliation remains the authority.

If no such Admin code exists, record the negative search evidence and make no speculative changes.

### 3. Promotions are campaign-linked only

Remove any Admin path that can create or present a campaign-less/direct `PromotionalCreditGrant` as a first-release action.

Admin promotion implementation after this task must assume:

```text
PromotionalCreditGrant.campaignId is required
exact grant lot is promotional capacity authority
no ShopEntitlementCounter(PROMOTIONAL_RECOVERY_CREDITS)
no direct-grant compatibility provenance
```

Do not implement the still-pending campaign-management tasks in this correction task.

### 4. Refund Admin types match the human provider-settlement baseline

Remove any compile/runtime/test dependency on:

```text
RecoveryCreditPurchaseStatus.REFUNDED
RecoveryCreditRefundSettlementMode
CURRENT_CYCLE_APP_EVENT_CORRECTION
negative App Event correction UsageEvent fields
```

The pending refund Admin tasks will build on DATABASE-013's human `REFUND | CREDIT` settlement model. Do not implement their workflow here.

### 5. Upgrade-economics schema availability

DATABASE-013 incorporates the valid schema requirements that were previously assigned to superseded DATABASE-012. This task does not implement upgrade-economics UI, but Admin Prisma/types must compile cleanly against that final baseline so ADMIN-008 can proceed later without a second compatibility layer.

### 6. No substitute compatibility layer

Do not create:

- local duplicate enums for removed Prisma values;
- optional `any`/fallback properties for removed fields;
- raw SQL using removed enum literals;
- migration-era adapters;
- fake campaign identities for old direct grants.

If accepted Admin business behaviour genuinely cannot be represented by DATABASE-013/SHARED-008, STOP and report the exact contract gap to `moda_architect`.

## Work Items

- [x] Verify DATABASE-013 and SHARED-008 are Complete and installed/resolved by the task worktree.
- [x] Search for every removed baseline symbol listed in this task.
- [x] Remove lifetime-Free legacy plan/adjustment compatibility.
- [x] Remove local cancellation compatibility if present.
- [x] Remove direct/campaign-less promotion compatibility if present.
- [x] Remove old refund/negative-App-Event compatibility if present.
- [x] Preserve accepted platform-policy controls and authorization/audit boundaries.
- [x] Add/update focused regression coverage.
- [x] Run repository-declared validation.

## Interfaces / Contracts

Consumes:

```text
DATABASE-013 final Prisma baseline
@modainteract/moda-interact-shared version published by SHARED-008
```

Canonical lifetime-Free names:

```text
PlatformBillingPolicy.lifetimeFreeRecoveryAllowance
EntitlementCounter.LIFETIME_FREE_RECOVERY_CREDITS
```

This task creates no new cross-service contract.

## Dependencies

- `ARCH-010-DATABASE-013`
- `ARCH-010-SHARED-008`
- `ARCH-010-ADMIN-001`

## Enables

- `ARCH-010-ADMIN-002`
- `ARCH-010-ADMIN-004`
- `ARCH-010-ADMIN-008`

## Acceptance Criteria

1. Admin builds/types against DATABASE-013 with no reference to `BillingPlan.freeLifetimeConversationAllowance` or `BillingAllowanceAdjustment`.
2. No Admin source/test uses `FREE_RECOVERY_LIFETIME`; canonical lifetime state uses `LIFETIME_FREE_RECOVERY_CREDITS`.
3. No Admin source/test depends on the removed local cancellation models/contracts.
4. No Admin first-release action creates a campaign-less/direct promotional grant or depends on the aggregate promotional entitlement counter.
5. No Admin source/test depends on `RecoveryCreditPurchaseStatus.REFUNDED`, negative-App-Event refund settlement mode, or refund correction UsageEvents.
6. Accepted lifetime-Free platform-policy control, authorization and audit behaviour still pass focused tests.
7. No merchant authentication/route boundary changes are introduced.
8. Repository-wide search evidence proves removed baseline symbols are absent except where they appear in intentional historical documentation outside implementation ownership.
9. Required repository validation passes or only documented unchanged baseline failures remain.

## Validation

Use the actual scripts declared by `package.json`. At minimum:

```text
focused Admin billing/security tests covering touched behaviour
repository typecheck when declared
repository lint when declared
repository build when declared
git diff --check
```

Also run exact source/test searches for:

```text
freeLifetimeConversationAllowance
BillingAllowanceAdjustment
FREE_RECOVERY_LIFETIME
SubscriptionCancellationRequest
RecoveryCreditPurchaseStatus.REFUNDED
CURRENT_CYCLE_APP_EVENT_CORRECTION
PROMOTIONAL_RECOVERY_CREDITS
```

Any remaining implementation reference must be explained and must not recreate compatibility state.

## Implementation Notes

This task is deliberately a correction/conformance task. Do not opportunistically implement downstream Admin features merely because their final schema is now available.

## Completion Report

### Status

Ready for Review.

### Files Changed

- `src/app/actions/billing-controls.ts`
- `src/components/admin/billing-controls.tsx`
- `src/components/admin/tenant-billing.tsx`
- `src/i18n/locales/en.json`
- `src/i18n/required-keys.ts`
- `src/lib/admin/billing-control-validation.ts`
- `src/lib/admin/billing-controls.ts`
- `src/lib/admin/billing-plan-audit.ts`
- `src/lib/admin/billing.ts`
- `src/lib/admin/types.ts`
- `tests/security/admin-billing-controls.test.mjs`
- `tests/security/admin-billing-plan.test.mjs`
- `tests/security/admin-billing-visibility.test.mjs`

### Work Completed

- Removed the obsolete `BillingAllowanceAdjustment` action, parser, reads, audit action, and UI form.
- Migrated Admin lifetime recovery reads to `EntitlementCounter.LIFETIME_FREE_RECOVERY_CREDITS` and counter-only allowance values.
- Removed legacy `BillingPlan.freeLifetimeConversationAllowance` audit serialization and fixtures.
- Preserved SUPER_ADMIN platform-policy authorization, `PLATFORM_POLICY_CHANGED`, before/after audit values, and policy revalidation paths.
- Updated focused security coverage and removed obsolete adjustment translation keys.
- No Admin cancellation, promotion-counter, refund-status, or App Event correction compatibility code was present; no speculative replacements were added.
- Attempt 2 removed the obsolete `billing.adjustments` catalogue and required-key entries.
- Attempt 2 added the exact first-production tenant billing regression asserting the compatibility key is absent.
- Attempt 2 revalidated the existing production conformance implementation without changing billing actions, readers, schema, Shared contracts, or downstream Admin workflows.

### Validation Results

- Focused billing security tests: 30 passed, 0 failed.
- Full Admin tests: 148 passed, 0 failed.
- Admin unit tests: 42 passed, 0 failed.
- `prisma:validate`: passed.
- `prisma:generate`: passed.
- `npm run lint`: passed with two pre-existing `react-hooks/exhaustive-deps` warnings in `src/components/admin/queue-monitor.tsx`.
- Production build: passed; existing BullMQ optional-dependency warnings remain.
- Focused Prettier checks for all three Attempt 2 files: passed.
- `git diff --check`: passed.
- Repository-wide `npm run format:check` reports 78 pre-existing unformatted files; none are the three files changed by Attempt 2.
- Removed-symbol search has no runtime/production matches; remaining matches are intentional negative assertions in `admin-billing-controls.test.mjs` and `admin-billing-plan.test.mjs`.
- Stale-i18n search has only the new negative assertion in `admin-billing-visibility.test.mjs`.

Physical worktree isolation:
  canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
  parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-ADMIN-010
  parent branch: task/ARCH-010-ADMIN-010
  implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-ADMIN-010
  implementation branch: task/ARCH-010-ADMIN-010
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

### Deviations

Repository-wide formatting is not green because of pre-existing formatting drift outside this task. The changed-file formatting check is green.

### Assumptions

- The implementation worktree uses its recorded database gitlink `014408e0402221f08a3961880b34e828a8bdc736`; that submodule was initialized in the canonical implementation worktree for validation.
- Dependencies were installed with `npm ci` in the canonical implementation worktree only. No shared/default checkout was linked, switched, or mutated.

### Unresolved Issues

None blocking review.

### Architectural Concerns

None. The accepted platform-policy mutation and audit boundary remain unchanged.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 is functionally close to the ARCH-010 first-production baseline and does **not** require a redesign. The core implementation inspected by `moda_architect` is correct in the following respects:

- `src/app/actions/billing-controls.ts` no longer creates `BillingAllowanceAdjustment` rows or emits `FREE_ALLOWANCE_ADJUSTED` audit events;
- `src/lib/admin/billing-controls.ts` and `src/lib/admin/billing.ts` read shop-lifetime Free capacity only from `EntitlementCounter.LIFETIME_FREE_RECOVERY_CREDITS`;
- `src/lib/admin/billing-plan-audit.ts` no longer serialises `BillingPlan.freeLifetimeConversationAllowance`;
- the existing SUPER_ADMIN platform-policy mutation, `PLATFORM_POLICY_CHANGED` audit event, before/after audit values and internal Admin route boundary remain intact;
- searches of `src/**` and `tests/**` found no runtime cancellation compatibility, no aggregate promotional counter compatibility, and no removed refund/negative-App-Event compatibility;
- no downstream ADMIN-002/003/004/005/006/007/008/009 workflow was implemented opportunistically.

Attempt 1 is **not accepted** because the correction task and its durable execution evidence are incomplete. Reclaim this same task as Attempt 2 and perform **only** the corrections below. Do not redesign the Admin billing UI or change accepted billing-policy behaviour.

#### Correction 1 — remove the final obsolete allowance-adjustment i18n key

The tenant billing UI no longer renders an allowance-adjustment value, but the obsolete key remains in the first-production catalogue/required-key list.

Make exactly these source changes:

1. In `src/i18n/locales/en.json`, delete the complete entry:

   ```text
   "billing.adjustments": "Allowance adjustments",
   ```

2. In `src/i18n/required-keys.ts`, delete the complete required-key entry:

   ```text
   "billing.adjustments",
   ```

3. In `tests/security/admin-billing-visibility.test.mjs`, add one focused regression test named exactly:

   ```text
   first-production tenant billing exposes no allowance-adjustment compatibility key
   ```

   That test must:

   - load `src/i18n/locales/en.json`;
   - load `src/i18n/required-keys.ts` as text;
   - assert that `catalogue["billing.adjustments"]` is `undefined`;
   - assert that `src/i18n/required-keys.ts` does not contain the literal string `"billing.adjustments"`.

Do **not** rename the obsolete key, add an alias, or replace it with another adjustment concept. `billing.remaining`, `billing.committed`, `billing.reserved`, and the canonical lifetime-Free entitlement display remain unchanged.

#### Correction 2 — complete the task-owned Work Item state

The task reached `status: review` while every checkbox under `## Work Items` remained unchecked. The repository-agent execution protocol requires the implementing agent to update those task-owned checkboxes.

During Attempt 2:

1. Re-evaluate each existing Work Item against the final Attempt 2 implementation and validation.
2. Change a Work Item from `[ ]` to `[x]` only when it is actually satisfied.
3. Before returning the task to `review`, all nine Work Items in this task must be `[x]`.
4. Do not delete, rename, merge, or rewrite the Work Items merely to make them appear complete.

#### Correction 3 — record mandatory physical-worktree and synchronization evidence

The Attempt 1 Completion Report does not contain the evidence required by `docs/agent-worktree-isolation-policy.md`.

For Attempt 2, use the launcher-resolved canonical parent and implementation worktrees for `ARCH-010-ADMIN-010`. Do not invent paths from this review note and do not copy example paths from documentation.

At the start of Attempt 2, perform the policy-required synchronization for **both** task worktrees and record the actual outcomes. Do not use a shared/default checkout or another task's worktree for task implementation or validation.

For Attempt 2 validation, do **not** symlink `moda-interact-admin/database` or `moda-interact-admin/node_modules` from the shared/default Admin checkout. The validation must execute from the canonical `ARCH-010-ADMIN-010` implementation worktree using the database submodule revision recorded by that worktree and dependencies available to that worktree. If the canonical task worktree cannot be validated without mutating a shared/default checkout, STOP and report the exact isolation/environment problem instead of claiming conformance.

Add the following block verbatim in structure under `## Completion Report`, filling every value with the **actual Attempt 2 evidence**:

```text
Physical worktree isolation:
  canonical workspace root: <actual launcher-resolved path>
  parent worktree: <actual launcher-resolved path>
  parent branch: task/ARCH-010-ADMIN-010
  implementation worktree: <actual launcher-resolved path>
  implementation branch: task/ARCH-010-ADMIN-010
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current
```

Use only one of the allowed values shown for each synchronization result. If reality does not support one of the required `no` statements, STOP and report the non-conformance; do not falsify the Completion Report.

#### Correction 4 — run the validation contract literally

`moda-interact-admin/package.json` declares repository-wide lint. Attempt 1 reported focused ESLint only, so the minimum Validation section was not fully satisfied.

From the canonical Attempt 2 implementation worktree, run all of the following after Correction 1:

```bash
npm run prisma:validate
npm run prisma:generate
node --test \
  tests/security/admin-billing-controls.test.mjs \
  tests/security/admin-billing-plan.test.mjs \
  tests/security/admin-billing-visibility.test.mjs
npm test
npm run test:unit
npm run lint
npm run build
npm run format:check
git diff --check
```

Also run this exact removed-symbol search over implementation/tests:

```bash
rg -n \
  'freeLifetimeConversationAllowance|BillingAllowanceAdjustment|FREE_RECOVERY_LIFETIME|SubscriptionCancellationRequest|SubscriptionCancellationMode|SubscriptionCancellationStatus|BILLING_CANCELLATION_REQUEST_RECEIVED|BILLING_CANCELLATION_COMPLETED|BILLING_CANCELLATION_REJECTED|RecoveryCreditPurchaseStatus\.REFUNDED|RecoveryCreditRefundSettlementMode|CURRENT_CYCLE_APP_EVENT_CORRECTION|PROMOTIONAL_RECOVERY_CREDITS|FREE_ALLOWANCE_ADJUSTED' \
  src tests
```

Expected search result: no implementation/runtime matches. Intentional **negative assertions in tests** that literally name a removed symbol are allowed and must be identified as such in the Completion Report.

Run this exact stale-i18n search:

```bash
rg -n 'billing\.adjustments' src tests
```

Expected result after Correction 1: the only permitted match is the new negative regression assertion in `tests/security/admin-billing-visibility.test.mjs`. There must be no catalogue, required-key, component, action, helper, or type match.

For repository-wide validation:

- `npm run lint` must be executed; do not substitute a changed-file-only lint command.
- `npm run format:check` may continue to report pre-existing unrelated formatting drift only if the Completion Report records the exact result and confirms that **none of the files changed by ADMIN-010** are among the failing files.
- Do not edit unrelated files merely to make repository-wide formatting green.
- Any lint/build/test/type/Prisma failure in a file changed by ADMIN-010 is blocking and must be corrected in this same task before returning to review.

#### Attempt 2 scope boundary and stop conditions

Allowed implementation changes for Attempt 2 are limited to:

```text
src/i18n/locales/en.json
src/i18n/required-keys.ts
tests/security/admin-billing-visibility.test.mjs
```

plus task-owned updates to:

```text
docs/decisions/admin/ARCH-010/ADMIN-010-conform-admin-to-first-production-billing-baseline.md
```

Do not modify the already-correct billing actions, readers, audit serializer, Prisma schema, Shared package, another repository, another ARCH-010 task, or architecture documents.

If fulfilling these instructions appears to require any additional production source change, schema change, cross-service contract change, or another repository modification, STOP and return the exact gap to `moda_architect` instead of improvising.

After all four corrections are complete and all required evidence is recorded:

1. update `Completion Report` with Attempt 2 files changed, validation results, deviations, assumptions, unresolved issues, architectural concerns, and the mandatory worktree/synchronization block;
2. ensure all nine Work Items are `[x]`;
3. set Completion Report status to `Ready for Review`;
4. set task status to `review`;
5. commit and push the implementation task branch;
6. commit and push the parent task branch containing the updated task file;
7. STOP and return control to `moda_architect`.

Do not start `ARCH-010-ADMIN-002`, `ARCH-010-ADMIN-004`, `ARCH-010-ADMIN-008`, or any other dependent/adjacent task.

### Reviewed Files

- `src/app/actions/billing-controls.ts`
- `src/components/admin/billing-controls.tsx`
- `src/components/admin/tenant-billing.tsx`
- `src/i18n/locales/en.json`
- `src/i18n/required-keys.ts`
- `src/lib/admin/billing-control-validation.ts`
- `src/lib/admin/billing-controls.ts`
- `src/lib/admin/billing-plan-audit.ts`
- `src/lib/admin/billing.ts`
- `src/lib/admin/types.ts`
- `tests/security/admin-billing-controls.test.mjs`
- `tests/security/admin-billing-plan.test.mjs`
- `tests/security/admin-billing-visibility.test.mjs`
- `docs/architecture/ARCH-010-first-production-baseline.md`
- `docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md`
- `docs/architecture/ARCH-010-promotional-campaigns.md`
- `docs/agent-worktree-isolation-policy.md`
- this task's Completion Report

### Validation Reviewed

- Compared the returned implementation files against the pre-ADMIN-010 ARCH-010 snapshot.
- Independently searched `src/**` and `tests/**` for all removed symbols required by this task; only intentional negative-test assertions remained for the named removed symbols.
- Independently ran `admin-billing-controls.test.mjs` and `admin-billing-visibility.test.mjs` successfully from the review archive.
- `admin-billing-plan.test.mjs` could not be independently executed from the compressed review archive because the archive intentionally contains no installed `@modainteract/moda-interact-shared` dependency. This review-environment limitation does not contradict the agent's reported validation, but Attempt 2 must rerun the complete validation set from the canonical implementation worktree.
- Identified one stale, now-unused first-production catalogue/required-key pair: `billing.adjustments`.
- Identified missing mandatory worktree/start-of-attempt evidence and incomplete Work Item checkboxes in the durable Completion Report/task state.
- Identified that the declared repository-wide `npm run lint` validation was not reported as executed in Attempt 1.

### Architecture Conformance

The production logic inspected in Attempt 1 conforms to the intended ARCH-010 Admin baseline: lifetime-Free authority is the platform policy plus `LIFETIME_FREE_RECOVERY_CREDITS`, legacy adjustment mutation is removed, and the authorization/audit boundary remains intact. Acceptance is withheld only for the bounded cleanup, validation, and execution-evidence corrections specified above.

### Follow-up

Reclaim this same task as Attempt 2. No new architecture task is required. Dependants remain gated until `ARCH-010-ADMIN-010` is architect-accepted `complete`.

### Attempt 2 — Accepted

#### Review Status

Accepted.

Attempt 2 satisfied the bounded Changes Requested contract without reopening the accepted Admin billing design.

The architect verified the published implementation commit `8eb55556bfd64124543fa7dd9915934467b0cc27`. It changes exactly the three files permitted for Attempt 2:

```text
src/i18n/locales/en.json
src/i18n/required-keys.ts
tests/security/admin-billing-visibility.test.mjs
```

The obsolete `billing.adjustments` entry is absent from both the locale catalogue and required-key list. The required regression test exists with the exact name:

```text
first-production tenant billing exposes no allowance-adjustment compatibility key
```

and proves both catalogue absence and required-key absence.

Repository-wide removed-symbol inspection of the returned source found no runtime/production compatibility references. The remaining legacy-name matches are intentional negative assertions in tests, exactly as permitted by the Attempt 2 review contract.

The architect independently executed:

```text
node --test tests/security/admin-billing-visibility.test.mjs
```

and confirmed:

```text
12 tests
12 passed
0 failed
```

The Completion Report records the required canonical parent/implementation worktrees, no shared-checkout mutation, no reuse of another task worktree, and all four start-of-attempt synchronization outcomes. All nine task-owned Work Items are complete.

The reported repository validation is accepted:

```text
focused billing/security: 30 passed
full Admin tests: 148 passed
unit tests: 42 passed
Prisma validate/generate: passed
repository-wide lint: passed with two pre-existing warnings
production build: passed
git diff --check: passed
```

Repository-wide `npm run format:check` continues to report 78 pre-existing files, but none of the three Attempt 2 files are among them; focused formatting for all three Attempt 2 files passed. This is an unchanged baseline deviation and is not an ADMIN-010 acceptance blocker.

Published evidence:

```text
implementation commit: 8eb55556bfd64124543fa7dd9915934467b0cc27
parent Completion Report commit: 39db0530f9a760d816967635b4366d9aadcf32eb
```

Both remote task branches were verified at those published heads.

#### Architect Decision

**Accepted — Attempt 2.**

Because `completion_mode: automatic`, the task is now:

```text
status: complete
attempt: 2
executor: null
claimed_at: null
```

#### Dependency reconciliation

Acceptance of ADMIN-010 does not by itself promote its listed dependants in the returned snapshot because each still has additional incomplete dependencies. Do not start ADMIN-002, ADMIN-004, or ADMIN-008 solely because ADMIN-010 is now Complete; readiness must be recalculated from each authoritative individual task file against the latest workspace state.

