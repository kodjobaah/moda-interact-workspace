---
id: ARCH-026-BACKGROUND-001
architecture_id: ARCH-026
title: Adopt the shared Shop onboarding milestone in Background billing workflows
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 3
depends_on:
  - ARCH-026-DATABASE-001
  - ARCH-025-BACKGROUND-007
enables:
  - ARCH-026-ADMIN-001
  - ARCH-026-BACKGROUND-002
created: 2026-10-02
updated: 2026-10-03
---

# Adopt the shared Shop onboarding milestone in Background billing workflows

## Architecture

Architecture ID:

`ARCH-026`

Architecture document:

`docs/architecture/ARCH-026-woocommerce-application-foundation.md`

Coordinator:

`moda_architect`

## Objective

Migrate Background billing/subscription reconciliation and Shopify discount-catalogue eligibility from the legacy Shopify-specific `ShopSettings.onboardingCompleted` source to provider-neutral `commerce.Shop.onboardingCompleted`, while continuing to mirror successful onboarding completion to `shopify.ShopSettings.onboardingCompleted` for transitional compatibility.

Preserve all existing reconciliation classification, locking, retry, billing-period, pending-plan, reinstall and discount-sync semantics.

## Context

DATABASE-001 adds and backfills:

```text
commerce.Shop.onboardingCompleted
```

while retaining:

```text
shopify.ShopSettings.onboardingCompleted
```

ARCH-025 has completed the billing-subscription reconciliation maintainability refactor. The previous 1,900-line implementation is now a thin coordinator plus extracted collaborators. The current inspected production references to the legacy onboarding milestone are owned by:

```text
src/services/billing-subscription-reconciliation/reconciliation-context.ts
src/services/billing-subscription-reconciliation/classification.ts
src/services/billing-subscription-reconciliation/reconciliation-queue.service.ts
src/services/billing-subscription-reconciliation.service.ts
src/services/billing-subscription-reconciliation/initial-activation-reconciliation.service.ts
src/services/billing-subscription-reconciliation/reinstall-reconciliation.service.ts
src/services/shopify-discount-catalogue.service.ts
```

`ReconciliationContextService` owns the durable Shop/subscription snapshot, `classification.ts` owns lifecycle classification, `ReconciliationQueueService` owns startup reconstruction eligibility, and the coordinator owns only dispatch/logging. Successful initial activation and reinstall completion writes now live in their dedicated lifecycle services.

ARCH-025 also deliberately preserved the pre-existing `lockShop(...)` SQL text in `billing-subscription-reconciliation/locking.ts`. That helper currently targets `"shopify"."Shop"`, while the canonical Shop table is `"commerce"."Shop"`. ARCH-025 was move-only and explicitly did not correct that target. Because this ARCH-026 task makes the shared Shop row authoritative and writes it in onboarding-completion transactions, correcting that lock target and establishing a safe lock order for those dual-write completion transactions is now directly in scope.

The discount catalogue uses the legacy flag as one eligibility condition.

WooCommerce must not depend on a Shopify settings table. The shared Shop field becomes the provider-neutral lifecycle source, but the legacy field remains a compatibility mirror until a later cleanup architecture explicitly removes it.

## Scope

Modify only `moda-interact-background` production/test files required to migrate these onboarding reads/writes.

### Authoritative reads

After this task, Background lifecycle/reconciliation decisions that mean "has this Moda merchant completed the one-time onboarding milestone?" MUST read:

```text
Shop.onboardingCompleted
```

rather than the nested Shopify settings flag.

This includes reconciliation classification branches such as initial-versus-established activation, cycle discovery/rollover/frozen/plan-change decisions, startup reconstruction eligibility and Shopify discount catalogue eligibility where onboarding completion is a condition.

The extracted reconciliation boundary MUST make the shared field explicit rather than carrying the legacy relation forward:

- `ReconciliationContextService` selects top-level `Shop.onboardingCompleted`;
- `ReconciliationClassificationRow` carries `onboardingCompleted: boolean` rather than `settings.onboardingCompleted`;
- classification, skip telemetry and coordinator accepted-job logging consume that top-level value;
- `ReconciliationQueueService.reconstruct()` filters on top-level `Shop.onboardingCompleted`;
- no lifecycle handler should need `ShopSettings` merely to determine whether onboarding completed.

Do not change provider-specific conditions that are genuinely Shopify-owned.

### Completion writes

Every Background transaction that currently establishes onboarding completion by writing:

```text
ShopSettings.onboardingCompleted = true
```

must set both:

```text
Shop.onboardingCompleted = true
ShopSettings.onboardingCompleted = true
```

inside the same existing transaction/provider-I/O boundary.

Because the shared Shop row is now part of the completion write, this task explicitly authorises the minimum lock correction required for those completion transactions:

- correct `lockShop(...)` to lock `"commerce"."Shop"`;
- where onboarding completion writes Shop + ShopSettings + Subscription state, acquire the three lifecycle row locks in `Shop -> ShopSettings -> Subscription` order before the authoritative writes;
- where a delegated helper acquires the Subscription lock (for example same-plan rollover), acquire Shop and ShopSettings before invoking that helper;
- do not change lock order for retry/failure/cycle/plan-change transactions that do not establish onboarding completion.

Do not move provider/network calls into the database transaction. Do not introduce a second lock abstraction.

The shared field is monotonic in normal runtime behavior. No Background path may reset it to false.

### Reinstall semantics

Reinstall/reconciliation must preserve the existing invariant that a merchant who completed onboarding previously does not become a first-time onboarding merchant again.

Do not use plugin/install connection state as the onboarding source.

## Out of Scope

- Removing `ShopSettings.onboardingCompleted`.
- Shopify app migration; owned by ARCH-026-SHOPIFY-001.
- Admin migration; owned by ARCH-026-ADMIN-001.
- Further restructuring of the ARCH-025 reconciliation collaborators or coordinator beyond changes directly required for this source/dual-write migration.
- Subscription status/state redesign.
- Billing-provider abstraction.
- Woo billing implementation.
- Queue/event contract changes.
- Gateway/API/WordPress changes.
- System-test terminal validation.

## Requirements

### R1 — Shared field is authoritative for Background lifecycle reads

Background must use `Shop.onboardingCompleted` when determining the one-time Moda onboarding milestone.

### R2 — Transaction/provider boundaries are preserved and completion locking is safe

Provider/network placement and transaction boundaries remain unchanged. The only authorised lock change is the shared-Shop correction/canonical completion ordering defined in Scope.

### R3 — Successful completion is mirrored

Every Background-owned transition that establishes onboarding completion sets both shared and legacy flags to true in the same transaction.

### R4 — No reset to onboarding

Established merchant reconciliation, reinstall, cancellation, plan change, rollover or billing attention must not reset the shared milestone.

### R5 — No lifecycle redesign

Do not add a new durable activation/account status; preserve existing Subscription projection and pending-plan semantics.

### R6 — Discount behavior is unchanged except source

Shopify discount catalogue eligibility retains the same behavioral conditions while replacing only the onboarding source.

## Work Items

- [x] Update the Background repository's nested database gitlink to accepted DATABASE-001 and regenerate Prisma.
- [x] Update `reconciliation-context.ts` to select top-level `Shop.onboardingCompleted` and stop selecting ShopSettings solely for lifecycle classification.
- [x] Update `classification.ts`, coordinator logging and `reconciliation-queue.service.ts` to consume the shared top-level milestone.
- [x] Correct `lockShop(...)` to target `"commerce"."Shop"` and update focused lock tests.
- [x] Change `initial-activation-reconciliation.service.ts` completion transactions to set shared + legacy flags atomically using the authorised completion lock order.
- [x] Change every `reinstall-reconciliation.service.ts` path that currently establishes onboarding completion to set shared + legacy flags atomically; preserve provider/retry/rollover semantics.
- [x] Change Shopify discount catalogue onboarding eligibility to read the shared Shop field.
- [x] Update focused extracted reconciliation/discount tests without weakening existing lifecycle assertions.
- [x] Add static audit coverage documenting any remaining legacy field references as compatibility writes only.

## Interfaces / Contracts

### Database contract owner

`ARCH-026-DATABASE-001`

### Authoritative lifecycle field

```text
commerce.Shop.onboardingCompleted
```

### Retained compatibility mirror

```text
shopify.ShopSettings.onboardingCompleted
```

No queue/shared-package contract changes are introduced.

## Dependencies

- `ARCH-026-DATABASE-001`
- `ARCH-025-BACKGROUND-007`

DATABASE-001 must be architect-accepted Complete and the Background nested database gitlink must point to the accepted main commit before implementation. ARCH-025-BACKGROUND-007 is Complete and establishes the extracted reconciliation ownership boundaries this task must modify rather than recreating the former monolith.

## Enables

- `ARCH-026-ADMIN-001`
- `ARCH-026-BACKGROUND-002`

ADMIN-001 additionally depends on SHOPIFY-001 so Admin switches its cross-platform presentation only after both current onboarding completion writers maintain the shared field. BACKGROUND-002 serializes the later shared international-context source migration in the same repository.

## Acceptance Criteria

- [x] Background reconciliation classification reads shared `Shop.onboardingCompleted` rather than legacy ShopSettings state.
- [x] Every Background initial-activation completion path sets shared and legacy onboarding flags to true in the same existing transaction.
- [x] No Background production path resets shared onboarding completion to false.
- [x] Established reinstall/rollover/plan-change/frozen paths retain their existing classification semantics.
- [x] Shopify discount catalogue behavior is unchanged except that onboarding eligibility reads the shared field.
- [x] Transaction boundaries, provider-call placement, retry scheduling and log semantics remain unchanged; onboarding-completion transactions use the explicitly authorised `Shop -> ShopSettings -> Subscription` lock order and no other lifecycle lock ordering changes.
- [x] No queue contract or billing state vocabulary changes.
- [x] Legacy ShopSettings field remains present and is used only as a compatibility mirror in changed Background code.
- [x] `lockShop(...)` targets the canonical `"commerce"."Shop"` table; no production lock SQL references `"shopify"."Shop"`.

## Validation

Required categories:

- [x] `npm run prisma:generate` from the accepted DATABASE-001 gitlink and `npm run prisma:validate`;
- [x] focused `vitest` suites for `reconciliation-context`, `classification`, `reconciliation-queue`, coordinator dispatch/logging, initial activation, reinstall and locking;
- [x] focused regression proving every successful Background-owned onboarding completion writes shared + legacy milestones in one transaction and uses the authorised lock order;
- [x] focused Shopify discount-catalogue eligibility test proving the shared Shop milestone is authoritative; add a direct service test if the current worker tests do not exercise `getEligibility(...)`;
- [x] existing `billing-subscription-reconciliation.service.test.ts` regression suite remains active; update fixtures/assertions to the shared top-level milestone without weakening lifecycle coverage;
- [x] static search/audit of production `src/` legacy onboarding references with compatibility writes documented;
- [x] `npm run test:unit` (executed; residual unrelated suite blockers are recorded below);
- [x] `npm test` (executed; residual unrelated and database-environment failures are recorded below);
- [x] `npm run build` (the repository build runs TypeScript compilation);
- [x] `git diff --check`;
- [x] clean implementation task-worktree evidence; parent task-report worktree is committed and pushed separately.

The repository currently declares no standalone `lint` or `typecheck` npm script. Do not invent one for this task; use the repository-declared build plus focused/full tests above.

## Stop Condition

After Work Items, Acceptance Criteria and Validation complete, set the task to `review`, finish the Completion Report, return to `moda_architect`, and STOP.

## Implementation Notes

ARCH-025 already completed the maintainability refactor. Do not collapse or bypass its extracted owners. Make the source migration in the canonical collaborator that now owns each behavior, and keep `billing-subscription-reconciliation.service.ts` as the coordinator.

The `lockShop(...)` schema-target correction and onboarding-completion lock ordering are authorised only because the shared Shop row becomes part of the durable completion boundary in this task; do not broaden this into general lock cleanup.

The legacy field remains because other consumers are being migrated incrementally. This is pre-production transitional compatibility, not a new permanent dual-source design.

## Completion Report

### Status

Ready for Architect Review

### Files Changed

Production:

- `src/services/billing-subscription-reconciliation.service.ts`
- `src/services/billing-subscription-reconciliation/classification.ts`
- `src/services/billing-subscription-reconciliation/initial-activation-reconciliation.service.ts`
- `src/services/billing-subscription-reconciliation/locking.ts`
- `src/services/billing-subscription-reconciliation/reconciliation-context.ts`
- `src/services/billing-subscription-reconciliation/reconciliation-queue.service.ts`
- `src/services/billing-subscription-reconciliation/reinstall-reconciliation.service.ts`
- `src/services/shopify-discount-catalogue.service.ts`

Tests:

- `tests/unit/services/billing-reconciliation.service.test.ts`
- `tests/unit/services/billing-subscription-reconciliation.service.test.ts`
- `tests/unit/services/billing-subscription-reconciliation/classification.test.ts`
- `tests/unit/services/billing-subscription-reconciliation/coordinator.test.ts`
- `tests/unit/services/billing-subscription-reconciliation/initial-activation-reconciliation.service.test.ts`
- `tests/unit/services/billing-subscription-reconciliation/locking.test.ts`
- `tests/unit/services/billing-subscription-reconciliation/reconciliation-context.test.ts`
- `tests/unit/services/billing-subscription-reconciliation/reconciliation-queue.service.test.ts`
- `tests/unit/services/billing-subscription-reconciliation/reinstall-reconciliation.service.test.ts`
- `tests/unit/services/shopify-discount-catalogue.service.test.ts`
- `tests/unit/shared-onboarding-authority.test.ts`

### Work Completed

- Migrated reconciliation projection, classification, queue reconstruction, coordinator telemetry and discount eligibility to the provider-neutral Shop milestone.
- Dual-wrote shared Shop and legacy ShopSettings completion flags inside initial Free/Paid and reinstall completion transactions; corrected the Shop lock table and applied `Shop -> ShopSettings -> Subscription` only to completion paths.
- Added completion atomicity/lock-order assertions, direct discount eligibility tests with opposing shared/mirror values, and a production-source guard against legacy onboarding reads. Compatibility writes remain intentionally in the initial activation and reinstall collaborators.
- The Background repository consumes `database/` at `16dba1a7c88f432f2f7d2cf718ae8297977cdcc3`, the accepted DATABASE-002 descendant containing DATABASE-001. Its parent is merged DATABASE-001 main `201e0a7044e7ab20d21538487816163ade2233b0`. BACKGROUND-001 did not change this gitlink: the same `16dba1a7...` pointer was already present at pre-task Background parent `ffb4fbc28561070561edae06485bb2ed6e168b41`.
- Implementation commit `3918ee03df507631387a7a73dbe157ece47eb3a1` is pushed to `origin/task/ARCH-026-BACKGROUND-001`.
- Attempt 3 is evidence/report-only; no Background implementation source, tests, package files, or database dependency changed. The durable launcher claim is commit `e7c8b497ba2f675f7afef6822e695df8ff1320bf` (Attempt 3, Copilot, claimed `2026-10-03T18:09:32Z`). Attempt 2's launcher claim commit is `1b2b72df39511a68bc5cde524401630005c0fe31`.
- Deterministic launcher/worktree evidence:
  - canonical primary workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`;
  - parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-026-BACKGROUND-001` / `task/ARCH-026-BACKGROUND-001`;
  - implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-026-BACKGROUND-001` / `task/ARCH-026-BACKGROUND-001`;
  - shared/default workspace checkout switched or mutated for task work: no; shared Background implementation checkout switched or mutated: no; another task worktree reused: no. Both dedicated task worktrees were reused.
  - parent task-branch fast-forward: `not-needed`; parent `origin/main` incorporation: `already-current`;
  - Background implementation task-branch fast-forward: `not-needed`; implementation `origin/main` incorporation: `already-current`;
  - recursive implementation submodules: `git submodule sync --recursive` passed; `git submodule update --init --recursive` passed; prepared `database/` commit `16dba1a7c88f432f2f7d2cf718ae8297977cdcc3`.
- Final branch evidence after the Attempt 3 claim: implementation local/remote head `3918ee03df507631387a7a73dbe157ece47eb3a1` (unchanged); parent local/remote head `e7c8b497ba2f675f7afef6822e695df8ff1320bf`; both worktrees were clean. This report-only update is committed and pushed on the same parent task branch.

### Validation Results

- PASS: `npm run prisma:generate`, `npm run prisma:validate`, `npm run build`, and `git diff --check`.
- PASS: focused onboarding/reconciliation/discount/static-audit regression: 13 files, 240 tests passed; the dedicated coordinator suite passed 146 tests.
- PASS: direct discount-catalogue authority test passed both cases; activation and reinstall completion tests assert shared/mirror writes and lock ordering.
- PASS: production `src/` audit found no reads from nested ShopSettings onboarding state and no lock SQL targeting `"shopify"."Shop"`; the remaining `shopSettings.update` calls are completion compatibility mirrors.
- KNOWN BASELINE (`ARCH025-BACKGROUND-TEST-001`): the recorded `npm run test:unit` result was 1,546/1,550 passing, with the same three rotating provider-cycle assertions and one matured-candidate language assertion; `tests/unit/commerce/evidence.test.ts` has the known absent ARCH-020 sibling-worktree fixture condition.
- KNOWN BASELINE (`ARCH025-BACKGROUND-TEST-001`): `npm test` had those same unit/fixture conditions plus four PostgreSQL integration tests unable to connect to `localhost:5432`. Architect differential review confirms the submitted outcome introduced no new failing test or suite identity; failures that disappeared are improvements and must not be recreated.
- The changed onboarding paths are covered by the passing focused suites. No standalone lint/typecheck command was added because the repository declares neither. Attempt 3 changed only task-report evidence and the implementation/dependency tree is unchanged, so validation was not rerun as authorized by the review instructions.

### Deviations

No implementation deviation. The remaining full-suite conditions are established repository baseline `ARCH025-BACKGROUND-TEST-001`, not unresolved BACKGROUND-001 blockers. Attempt 3 was report-only, as directed by Architect Review.

### Assumptions

- DATABASE-001 adds/backfills the shared Shop milestone and keeps the legacy field.

### Unresolved Issues

None specific to BACKGROUND-001. The known repository-wide test conditions are documented under `ARCH025-BACKGROUND-TEST-001` above and were independently confirmed by differential review to introduce no new failure identity.

### Architectural Concerns

None identified in the changed onboarding paths. Architect Review remains pending.

## Developer Override - Reopened (2026-10-03)

- Previous accepted attempt: none. Attempt 1 was claimed and remained in progress; no implementation changes or acceptance record exist.
- Reopen reason: the developer explicitly requested `/moda_developer_update ARCH-026-BACKGROUND-001 reopen` after the task launcher declined to prepare the existing active claim. Reopening clears that claim so the task can return to normal preparation without losing Attempt 1 history.
- Transition: `in_progress` -> `ready`; `executor` and `claimed_at` cleared; `attempt` remains `1`.
- This reopen is not a claim. `execution_mode: agent` and `completion_mode: automatic` remain unchanged. The implementation task worktree contains no task changes and remains at `origin/main`.

## Architect Review

### Review Status

Accepted — Attempt 3.

### Review Notes

Attempt 3 satisfies the sole evidence/report correction from Attempt 2.
`ARCH-026-BACKGROUND-001` is accepted Complete.

No Background implementation source changed after the architect accepted implementation
`3918ee03df507631387a7a73dbe157ece47eb3a1` in substance. The corrected Completion
Report at pushed parent head
`aef533de54d3a36d77222085e4c2baea2abdca76` now makes the required preparation and
baseline evidence durable.

The uploaded Attempt-3 snapshot matches the pushed report exactly: the local task-file
Git blob is `abf48a5bfeefe81879b53b4f6660e8dfa3a06896`, which is the same blob GitHub
reports for that file at `aef533de...`. GitHub also confirms the implementation task
branch remains exactly:

```text
3918ee03df507631387a7a73dbe157ece47eb3a1
```

with no Attempt-3 source commit.

The Attempt-3 report closes A2-R1 by recording:

```text
canonical primary workspace
  /Users/kwadwoadomafriyie/project/moda-interact-workspace

parent task worktree
  /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-026-BACKGROUND-001
  task/ARCH-026-BACKGROUND-001

implementation task worktree
  /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-026-BACKGROUND-001
  task/ARCH-026-BACKGROUND-001

shared/default workspace mutated for task work
  no

shared Background checkout mutated
  no

another task worktree reused
  no

parent task fast-forward
  not-needed

parent origin/main incorporation
  already-current

implementation task fast-forward
  not-needed

implementation origin/main incorporation
  already-current

git submodule sync --recursive
  passed

git submodule update --init --recursive
  passed

prepared database/
  16dba1a7c88f432f2f7d2cf718ae8297977cdcc3
```

The database ancestry wording is now exact. `16dba1a7...` is the accepted DATABASE-002
descendant containing DATABASE-001; its parent is merged DATABASE-001 main
`201e0a7044e7ab20d21538487816163ade2233b0`. The report also correctly records that
BACKGROUND-001 did **not** change this gitlink because the same pointer was already
present at pre-task Background parent
`ffb4fbc28561070561edae06485bb2ed6e168b41`.

The repository-wide non-green checks are now correctly classified as the durable
`ARCH025-BACKGROUND-TEST-001` baseline rather than unresolved BACKGROUND-001 blockers:

- the same three rotating billing-reconciliation assertions;
- the same matured-candidate language assertion;
- the same absent ARCH-020 sibling-worktree fixture condition;
- the same four PostgreSQL `localhost:5432` connection failures.

The differential review introduced no new failing test or suite identity. Attempt 3 was
therefore correctly report-only and did not rerun validation or manufacture a source
commit.

The previously reviewed implementation remains architecture-conformant:

- shared `commerce.Shop.onboardingCompleted` is authoritative for Background
  reconciliation/classification/queue and discount-eligibility reads;
- no production code reads the legacy ShopSettings milestone as authority;
- successful initial activation and reinstall completion atomically write shared Shop
  + retained ShopSettings compatibility state;
- no production path resets the shared milestone to false;
- `lockShop(...)` targets canonical `"commerce"."Shop"`;
- completion paths preserve the authorised
  `Shop -> ShopSettings -> Subscription` ordering;
- provider/network placement, billing-period ownership, retry semantics, queue
  contracts and lifecycle vocabulary remain unchanged.

Focused validation remains the accepted Attempt-2 evidence:

```text
focused onboarding/reconciliation/discount/static audit
  13 files / 240 tests passed

coordinator suite
  146 / 146 passed

Prisma generation / validation
  passed

production build
  passed

git diff --check
  passed
```

The prior Attempt-2 Changes Requested review is retained below as historical review
context.

#### Prior Attempt 2 review history

The BACKGROUND-001 implementation is accepted in substance. No production or test
source correction is requested.

Architect inspection of implementation
`3918ee03df507631387a7a73dbe157ece47eb3a1` confirms that the shared
`commerce.Shop.onboardingCompleted` field is now authoritative throughout the
Background-owned one-time onboarding lifecycle:

- `ReconciliationContextService` selects top-level `Shop.onboardingCompleted`;
- `ReconciliationClassificationRow` carries the top-level boolean rather than the
  legacy `settings.onboardingCompleted` relation;
- classification predicates, skip telemetry and coordinator accepted-job logging
  consume the shared field;
- `ReconciliationQueueService.reconstruct()` filters on top-level
  `Shop.onboardingCompleted`;
- Shopify discount-catalogue eligibility uses `Shop.onboardingCompleted` and does not
  consult the legacy mirror.

A production-source audit of the submitted snapshot independently finds:

```text
legacy ShopSettings onboarding reads
  0

shared onboarding writes to false
  0

lock SQL targeting "shopify"."Shop"
  0

canonical lock SQL targeting "commerce"."Shop"
  present
```

The only remaining production uses of `ShopSettings.onboardingCompleted` in the changed
lifecycle owners are compatibility writes to `true`.

The completion transactions are architecture-conformant:

- initial Free activation locks `Shop -> ShopSettings -> Subscription`, then writes
  shared + legacy onboarding completion in the existing transaction;
- initial Paid activation uses the same lock order and dual-write;
- Free reinstall completion uses the same lock order and dual-write;
- Paid reinstall activation uses the same lock order and dual-write;
- post-rollover activation locks `Shop -> ShopSettings -> Subscription` before the
  authoritative completion writes;
- the same-plan rollover path locks `Shop -> ShopSettings` before invoking the delegated
  rollover helper that owns the Subscription lock, preserving the explicitly authorised
  ordering without introducing a second locking abstraction.

Provider/network calls remain outside the database completion transactions. Retry,
classification, billing-period, pending-plan, discount-sync and queue-publish ownership
remain in their accepted ARCH-025 collaborators.

`lockShop(...)` now correctly targets:

```text
"commerce"."Shop"
```

and no unrelated retry/failure/cycle/plan-change lock ordering was redesigned.

The reported repository-wide failures do not block this task. The workspace already
contains durable `ARCH025-BACKGROUND-TEST-001`, established by same-environment
pre-task/submitted-tree differential testing. That baseline explicitly covers:

- the same three rotating billing-reconciliation assertion identities;
- the same matured-candidate language-context assertion;
- the same `tests/unit/commerce/evidence.test.ts` absent ARCH-020 task-worktree fixture;
- the same four PostgreSQL integration failures caused by unavailable
  `localhost:5432`.

The submitted full-suite outcome introduces no new failing test/suite identity. Baseline
failures that have disappeared are improvements and must not be recreated. The focused
onboarding/reconciliation/discount validation remains 13 files / 240 tests passed, with
the complete coordinator suite at 146/146.

The nested database gitlink also needs a documentation correction, not a code change.
GitHub independently confirms both the implementation parent
`ffb4fbc28561070561edae06485bb2ed6e168b41` and submitted implementation already
point at:

```text
database/
  16dba1a7c88f432f2f7d2cf718ae8297977cdcc3
```

Therefore BACKGROUND-001 did not change the database gitlink. `16dba1a7...` is the
accepted DATABASE-002 descendant whose parent is merged DATABASE-001 main
`201e0a7044e7ab20d21538487816163ade2233b0`; it contains the required DATABASE-001
`Shop.onboardingCompleted` contract plus the later accepted international-context
columns. This is an acceptable schema base, but the Completion Report must not call
`16dba1a7...` “the accepted DATABASE-001 commit” or claim this task updated the gitlink.

Acceptance is withheld only because the Completion Report does not yet durably record
the deterministic launcher preparation packet required by the task-review protocol.

#### A2-R1 — record the full launcher/worktree/synchronization packet

Attempt 3 is evidence/report-only. Record the launcher-resolved evidence for the
Attempt-2 implementation:

- canonical primary workspace path;
- dedicated parent task worktree path and `task/ARCH-026-BACKGROUND-001` branch;
- dedicated Background implementation worktree path and matching task branch;
- explicit statements that the shared/default workspace and shared Background checkout
  were not switched/mutated for task work and that no other task worktree was reused;
- parent task-branch fast-forward result and `origin/main` incorporation state at
  preparation;
- Background implementation task-branch fast-forward result and `origin/main`
  incorporation state at preparation;
- recursive `git submodule sync --recursive` and
  `git submodule update --init --recursive` results;
- prepared/final nested `database/` gitlink, identifying
  `16dba1a7c88f432f2f7d2cf718ae8297977cdcc3` accurately as the accepted
  DATABASE-002 descendant containing DATABASE-001, and noting that the gitlink was
  already present at pre-task Background parent `ffb4fbc...`;
- Attempt-2 claim evidence if the launcher recorded a claim commit;
- final implementation/report heads and clean local/remote alignment.

Correct the Completion Report statements that currently describe the residual full-suite
outcomes as unresolved task blockers. Reference `ARCH025-BACKGROUND-TEST-001` and state
that no new failure identity was introduced.

Do not change Background production/test source merely to create another implementation
commit. No rerun of the already-complete focused/full validation is required when the
implementation/dependency tree is unchanged. If launcher synchronization introduces
relevant Background source, package/lockfile or database-submodule drift, rerun only the
validation materially affected by that drift and record it.

The architect reconciliation accompanying this review also removes the committed
ARCH-026 conflict markers and duplicate Background frontier prose from architect-owned
coordination files; those are not assigned to the Background implementation agent.

#### Attempt 2 reviewed files (historical)

- `src/services/billing-subscription-reconciliation.service.ts`
- `src/services/billing-subscription-reconciliation/reconciliation-context.ts`
- `src/services/billing-subscription-reconciliation/classification.ts`
- `src/services/billing-subscription-reconciliation/reconciliation-queue.service.ts`
- `src/services/billing-subscription-reconciliation/locking.ts`
- `src/services/billing-subscription-reconciliation/initial-activation-reconciliation.service.ts`
- `src/services/billing-subscription-reconciliation/reinstall-reconciliation.service.ts`
- `src/services/shopify-discount-catalogue.service.ts`
- all changed focused reconciliation/discount/static-audit tests
- durable `ARCH025-BACKGROUND-TEST-001` evidence in the ARCH-025 architecture/task
  history
- accepted DATABASE-001 / DATABASE-002 git ancestry and Background submodule state
- this task Completion Report
- ARCH-026 Background index and parent architecture coordination state

#### Attempt 2 validation reviewed (historical)

- GitHub implementation commit
  `3918ee03df507631387a7a73dbe157ece47eb3a1`.
- GitHub parent report branch
  `000e0cb6d8891efefaebf952868a004dc6894b80`.
- Focused onboarding/reconciliation/discount/static audit: submitted 13 files /
  240 tests passed.
- Complete coordinator regression: submitted 146/146 passed.
- Submitted Prisma generation/validation, production build and `git diff --check`:
  passed.
- `npm run test:unit`: submitted 1,546/1,550 passed plus the known ARCH-020 fixture
  collection condition; all residual identities are covered by
  `ARCH025-BACKGROUND-TEST-001`.
- `npm test`: the same baseline identities plus four baseline PostgreSQL
  `localhost:5432` connection failures; no task-owned failure category.
- Independent static source audit: no legacy onboarding read, no shared milestone reset
  to false and no obsolete Shopify Shop lock target.
- GitHub submodule inspection: pre-task parent and submitted implementation both pin
  `database/` to `16dba1a7c88f432f2f7d2cf718ae8297977cdcc3`.

#### Attempt 2 architecture conformance (historical)

Conformant in implementation. BACKGROUND-001 correctly migrates Background onboarding
authority to shared Shop state, preserves the legacy compatibility mirror, establishes
the authorised canonical completion lock ordering and does not redesign provider,
billing, queue or reconciliation ownership.

Acceptance is pending only durable launcher/VCS/submodule preparation evidence and
Completion Report wording corrections.

#### Attempt 2 follow-up (historical)

Return this same task to Ready with Attempt 2 retained and claim clear. Reclaim through
`/moda-task ARCH-026-BACKGROUND-001`; the next claim must create Attempt 3 exactly once.

Attempt 3 is evidence/report-only unless preparation exposes relevant drift. Do not
begin `ARCH-026-BACKGROUND-002` or `ARCH-026-ADMIN-001` until BACKGROUND-001 is
architect-accepted Complete.

### Architecture Conformance

Accepted. BACKGROUND-001 completes the provider-neutral onboarding authority migration
for Background without changing billing/reconciliation ownership. The shared Shop
milestone is authoritative; the legacy Shopify setting is a compatibility mirror only;
completion writes are atomic; and the canonical completion lock ordering is explicit.

### Follow-up

`ARCH-026-BACKGROUND-001` is Complete / Accepted at Attempt 3.

All dependencies are now satisfied for:

- `ARCH-026-BACKGROUND-002` -> Ready, Attempt 0, claim clear.
- `ARCH-026-ADMIN-001` -> Ready, Attempt 0, claim clear.

`ARCH-026-ADMIN-002` remains Pending on ADMIN-001. Do not start either newly Ready task
implicitly; each must be claimed through its own `/moda-task` workflow.
