---
id: ARCH-025-SHOPIFY-009
architecture_id: ARCH-025
title: Extract subscription-ended notification workflow
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 90
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-025-SHOPIFY-008
enables:
  - ARCH-025-SHOPIFY-010
created: 2026-10-01
updated: 2026-10-02
---

# Extract subscription-ended notification workflow

## Architecture

Architecture ID: `ARCH-025`

Architecture document: `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`

Coordinator: `moda_architect`

## Objective

Extract subscription-ended support-message persistence, lifecycle identity derivation and translation scheduling into a dedicated service while preserving post-commit/best-effort isolation from billing state.

## Context

`syncSubscription()` currently invokes a substantial notification side effect for the no-active-subscription path. Moving that side effect before the final sync extraction reduces coordinator scope and establishes an explicit failure-isolation boundary.

## Scope

Authorised implementation surface:

```text
app/services/billing/billing.service.ts
app/services/billing/subscription-ended-notification.service.ts              # new
tests/unit/services/billing/subscription-ended-notification.service.test.ts  # new
```

Merchant-support service code is not modified.

## Out of Scope

- changing support message schema/codes/actions.
- changing translation infrastructure.
- changing when a subscription is classified ended.
- sync coordinator extraction itself.
- edits to frozen `billing.service.test.ts`.

## Requirements

### Common ARCH-025 invariants

- Preserve `BillingService` constructor compatibility: `new BillingService(provider, database, dispatchTranslation)`.
- Preserve every existing public `BillingService` method signature and the `billingService` singleton export.
- Preserve all current public exports from `app/services/billing/billing.service.ts`; moved symbols must be compatibility re-exported from that file.
- Do not change routes/callers as part of extraction.
- Extracted modules MUST NOT import `billing.service.ts`; dependency direction is façade/coordinator -> collaborator.
- Do not change billing rules, error codes/strings, transaction boundaries, lock order, provider call order, retry semantics, idempotency, CAS/fencing, entitlement arithmetic or durable lifecycle state.
- Do not add provider/API calls or database round trips to the equivalent path solely because code moved.
- Extracted collaborator constructors must be side-effect-free: store/wire dependencies only. Do not perform provider/database I/O, environment discovery or eager Prisma-model access during `new BillingService(...)`; the frozen suite constructs the façade with many partial test doubles.
- This is move-only refactoring: do not remove, coalesce, reorder or otherwise optimise away an existing provider/database read, write, lock or transaction as an incidental cleanup. Any intentional I/O change is outside this task.
- Do not introduce a new logger, DI container, command bus, plugin framework or generic billing framework.
- `tests/unit/services/billing.service.test.ts` is frozen: do not edit it. Its SHA-256 must remain `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`. The proven pre-task failure set is `ARCH025-TEST-001`; the task must introduce no additional failing identifier.
- Add focused tests in a new/explicitly authorised test file for the extracted owner; do not move existing assertions out of the frozen regression file in this task.
- Full `npm test` must introduce no new failure. An unrelated documented baseline failure may be referenced only if it is unchanged and the current task did not touch its affected area.

### R1 — move exact notification capability without moving sync classification

Move logic equivalent to:

```text
TranslationDispatch
SubscriptionLifecycle
SubscriptionIdentityFacts
deriveLifecycleIdentity
persistSubscriptionEndedNotification
renderSubscriptionEndedMessage
```

into the notification service/module. The sync transaction must continue deciding whether the **previous** Subscription was ACTIVE/TRIALING and constructing the immutable lifecycle facts; this task does not move no-contract classification or the billing Subscription update into the notification service.

### R2 — preserve public helper export

`renderSubscriptionEndedMessage` remains exportable from `billing.service.ts` for compatibility.

### R3 — preserve support-message identity/idempotency

Keep the same lifecycle identity derivation, source-key format/version, system message code, language selection, upsert/duplicate behaviour and translation request creation rules.

### R4 — preserve failure isolation and exact error propagation

Do not move notification/translation work into the transaction that commits billing Subscription state. Notification or translation dispatch failure must not roll back an already committed billing projection.

After the billing transaction commits, preserve the current error rule exactly: failure with message `Unable to derive a durable subscription lifecycle identity.` is rethrown; all other notification-persistence or translation-dispatch failures are best-effort and do not fail `syncSubscription()`. Keep the missing-identity constant as a repository-internal export if needed so the caller does not duplicate/change the string.

### R5 — preserve dispatch injection and timing

The existing `BillingService` third constructor dependency (`dispatchTranslation`) remains supported and is passed to the extracted notification owner. Move/define the repository-internal `TranslationDispatch = (translationId: string) => Promise<void>` type with this owner and import the type into the façade rather than making the notification module depend on `billing.service.ts`. The owner may persist then dispatch using that injected function, but dispatch must occur only after the notification persistence transaction has committed and only when a translation ID was newly returned, exactly as today.

## Work Items

- [x] Create `SubscriptionEndedNotificationService` and move lifecycle identity/render/persistence/translation logic while leaving ended-state classification in sync.
- [x] Preserve compatibility re-export of `renderSubscriptionEndedMessage`.
- [x] Wire façade/sync path to the collaborator without changing side-effect timing.
- [x] Add focused tests for provider-ID/cycle fallback lifecycle identity, missing-identity rethrow, source-key replay/idempotency, language/translation decisions, post-commit dispatch and best-effort non-identity failure isolation.
- [x] Prove frozen façade regression suite remains byte-identical and introduces no failing identifier outside `ARCH025-TEST-001`.

## Interfaces / Contracts

Consumes existing merchant-support functions and Shared merchant-communication constants. Repository-internal lifecycle identity derivation may be imported by the still-unextracted sync path. No new event/queue/shared contract.

## Dependencies

- `ARCH-025-SHOPIFY-008`

## Enables

- `ARCH-025-SHOPIFY-010`

## Acceptance Criteria

- [x] Subscription-ended support side effect has one owner.
- [x] Message identity/code/language and translation semantics are unchanged.
- [x] Already committed billing state remains isolated from notification/dispatch failure; missing durable lifecycle identity still propagates while all other notification/dispatch failures remain best-effort.
- [x] `renderSubscriptionEndedMessage` compatibility export remains.
- [x] Frozen façade suite remains byte-identical and introduces no failing identifier outside `ARCH025-TEST-001`.

## Validation

- [x] `npm run prisma:generate`
- [x] `node -e "const fs=require('node:fs'),crypto=require('node:crypto');const p='tests/unit/services/billing.service.test.ts';const h=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');if(h!=='bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4'){console.error(h);process.exit(1)};console.log(h)` prints `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`
- [x] `git diff -- tests/unit/services/billing.service.test.ts` is empty
- [x] `npm test -- tests/unit/services/billing.service.test.ts` introduces no failing identifier outside `ARCH025-TEST-001`
- [x] `npm test -- tests/unit/services/billing/subscription-ended-notification.service.test.ts` passes the new focused capability tests
- [x] `npm test` introduces no new failures
- [x] `npm run typecheck`
- [x] `npx eslint app/services/billing/billing.service.ts app/services/billing/subscription-ended-notification.service.ts tests/unit/services/billing/subscription-ended-notification.service.test.ts`
- [x] `npm run build`
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin the enabled task.

## Implementation Notes

The service may own its internal database transaction for support-message persistence exactly as today. Do not combine it with generic merchant-support ownership.


## Completion Report

### Status

Review

### Files Changed

- `moda-interact/app/services/billing/billing.service.ts`
- `moda-interact/app/services/billing/subscription-ended-notification.service.ts`
- `moda-interact/tests/unit/services/billing/subscription-ended-notification.service.test.ts`

### Work Completed

- Extracted lifecycle identity derivation, ended-message rendering, source-keyed support-message persistence, translation creation/dispatch, and best-effort failure policy into `SubscriptionEndedNotificationService`.
- Kept previous-subscription ended-state classification and immutable lifecycle fact construction in the existing `syncSubscription()` transaction; notification work remains after that transaction commits.
- Preserved `BillingService(provider, database, dispatchTranslation)` compatibility and the `renderSubscriptionEndedMessage` export. The new collaborator has no dependency on `billing.service.ts`.
- Added eight focused tests covering provider-ID and cycle-fallback identity, message compatibility, source-key replay, stored/configured language, translated-message persistence, dispatch-after-commit, persistence/dispatch failure isolation, and the missing-identity rethrow after billing commit.

Review correction (Attempt 2; report-only, A1-R1):
- All five Acceptance Criteria above are satisfied by the implementation and validation evidence recorded here.
- Reviewed and pushed implementation commit: `209a36138dd438815c3ee360298a97db6d2d6f85`.
- Architect-reviewed parent report commit: `723de58dad8e15775afe24d229b0d12bf8da1ad6`.
- Attempt 2 parent claim commit: `940016ff3b26feb655f64dc6280bfd20c68a100d`; synchronized-main merge in the parent worktree: `92755ae3`.
- Final implementation worktree is clean at `c7b14b5131fd00506da651e7bf0d10e8309c2f9b`, which is `origin/main` and contains the reviewed implementation; the remote task ref remains the reviewed implementation commit above. No implementation source or test changes were made for this report correction.
- Final parent report branch is `task/ARCH-025-SHOPIFY-009`; the report correction is committed and pushed, and the worktree is clean and aligned with `origin/task/ARCH-025-SHOPIFY-009`.

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-025-SHOPIFY-009`
  parent branch: `task/ARCH-025-SHOPIFY-009`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-025-SHOPIFY-009`
  implementation branch: `task/ARCH-025-SHOPIFY-009`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Recursive implementation submodules:
  git submodule sync --recursive: passed
  git submodule update --init --recursive: passed
  recorded submodule commits: `database` at `cfeeb12456b4e05067a96857a8c47837d7e33bbd`

### Validation Results

- `npm run prisma:generate`: passed.
- Frozen regression SHA-256: `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`; `git diff -- tests/unit/services/billing.service.test.ts` is empty.
- Focused notification suite: passed, 8 tests.
- Frozen façade suite: 195 passed, 18 failed; the failures match the documented `ARCH025-TEST-001` baseline.
- Full `npm test`: 82 files passed, 5 failed, 8 skipped; 1,009 tests passed, 24 failed, 33 skipped. The 24 failures match the established `ARCH025-TEST-001` baseline; no new failure identifier was observed.
- `npm run typecheck`: passed.
- Required targeted ESLint command: passed (toolchain emits its existing TypeScript-version support warning).
- `npm run build`: passed; existing Vite dependency annotation, external Prisma browser-entry, empty-chunk and chunk-size warnings remain non-fatal.
- `git diff --check`: passed.

### Deviations

None.

### Assumptions

None; the notification owner retains the existing support persistence transaction and is invoked only after billing projection commit.

### Unresolved Issues

The unchanged repository test baseline `ARCH025-TEST-001` remains: 18 frozen BillingService failures and 24 full-suite failures.

### Architectural Concerns

None identified.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 accepted.

Attempt 1 requested one report-only correction, A1-R1: the implementing agent had submitted the task to review with all five Acceptance Criteria unchecked and without durable implementation/report commit evidence. Attempt 2 closes that correction without changing production or test source and without rerunning validation, exactly as requested.

The implementation remains the architecture-conformant extraction reviewed in Attempt 1. `SubscriptionEndedNotificationService` owns lifecycle identity derivation, source-keyed support-message persistence and translation dispatch; previous ACTIVE/TRIALING ended-state classification remains in `syncSubscription()`; notification persistence starts only after the billing projection transaction commits; and only `Unable to derive a durable subscription lifecycle identity.` propagates while all other notification/dispatch failures remain best-effort. `renderSubscriptionEndedMessage` remains compatibility-exported from `billing.service.ts` and the third `BillingService` constructor dependency remains supported.

Reviewed implementation task ref: `209a36138dd438815c3ee360298a97db6d2d6f85`.
Attempt 2 parent report correction: `4429008d87766e4b40fbfdfc4c743dfdbe060794`.
Developer-integrated implementation main: `c7b14b5131fd00506da651e7bf0d10e8309c2f9b`; GitHub comparison from the reviewed task commit to that merge commit contains no file delta, and the remote task ref remains pinned to the reviewed implementation commit.

### Reviewed Files

- `moda-interact/app/services/billing/billing.service.ts`
- `moda-interact/app/services/billing/subscription-ended-notification.service.ts`
- `moda-interact/tests/unit/services/billing/subscription-ended-notification.service.test.ts`
- `docs/decisions/shopify/ARCH-025/SHOPIFY-009-extract-subscription-ended-notification-service.md`
- `docs/decisions/shopify/ARCH-025/_index.md`
- `docs/architecture/ARCH-025-shopify-billing-service-maintainability.md`
- `docs/development-baseline.md` (`ARCH025-TEST-001`)

### Validation Reviewed

- Attempt 2 is report-only; implementation and dependency state were unchanged, so validation was not rerun per the Attempt 1 correction contract.
- All five Acceptance Criteria are now checked by the implementing agent.
- Focused notification suite from the reviewed implementation: 8/8 passed.
- Frozen façade SHA-256 remains `bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4`; frozen test diff is empty.
- Frozen façade suite: 195 passed / 18 failed; every failure is within `ARCH025-TEST-001`.
- Full suite: 1,009 passed / 24 failed / 33 skipped; every failure is within `ARCH025-TEST-001`.
- Prisma generation, typecheck, targeted ESLint, production build and `git diff --check` were previously recorded as passing and remain the accepted implementation evidence.
- Parent report branch head `4429008d87766e4b40fbfdfc4c743dfdbe060794` is pushed; the implementation task ref remains `209a36138dd438815c3ee360298a97db6d2d6f85`.
- The implementation main merge `c7b14b5131fd00506da651e7bf0d10e8309c2f9b` contains the reviewed task commit with no additional file delta.

### Architecture Conformance

Conforms to ARCH-025 and SHOPIFY-009. Notification ownership, lifecycle identity/source-key semantics, language/translation behavior, post-commit failure isolation, exact missing-identity propagation and façade compatibility are preserved. Attempt 2 changes coordination evidence only and introduces no implementation delta.

### Follow-up

`ARCH-025-SHOPIFY-010` is promoted to `ready`. `ARCH-025-SHOPIFY-011` remains Pending until SHOPIFY-010 is architect-accepted Complete.
