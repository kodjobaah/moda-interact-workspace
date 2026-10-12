---
id: ARCH-028-BACKGROUND-012
architecture_id: ARCH-028
title: Reschedule token-identified checkout updates after missing recipient
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 51
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-028-BACKGROUND-007
  - ARCH-028-SHARED-004
enables:
  - ARCH-028-SHOPIFY-001
created: 2026-10-08
updated: 2026-10-12
---
# Reschedule token-identified checkout updates after missing recipient
Ready for moda_architect review — Attempt 1.
## Architecture

Architecture ID: `ARCH-028`
Implementation worktree (`moda-interact-background`):
- `package.json`
- `package-lock.json`
- `src/events/shopify-contract-adapter.ts`
- `src/services/checkout-recovery.service.ts`
- `src/services/checkout-recovery/checkout-event-orchestrator.service.ts`
- `src/services/checkout-recovery/recovery-materialization.service.ts`
- `src/services/pending-recovery-candidate.service.ts`
- `src/services/pending-recovery-candidate/candidate-activity.service.ts`
- `src/services/pending-recovery-candidate/candidate-lifecycle.service.ts`
- `src/workers/pending-recovery-candidate.worker.ts`
- `tests/unit/events/shopify-contract-adapter.test.ts`
- `tests/unit/runtime/observability-startup.test.ts`
- `tests/unit/services/checkout-recovery/checkout-event-orchestrator.service.test.ts`
- `tests/unit/services/checkout-refresh.test.ts`
- `tests/unit/services/matured-candidate.materialization.test.ts`
- `tests/unit/services/pending-recovery-candidate.service.test.ts`
- `tests/unit/services/pending-recovery-candidate/candidate-activity.service.test.ts`
- `tests/unit/services/pending-recovery-candidate/facade-scheduling.cases.ts`
- `tests/unit/workers/pending-recovery-candidate.worker.test.ts`
Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`
- Installed the published Shared 1.5.0 contract dependency. The adapter continues to parse strict v2 events and maps v3 checkout lookup properties independently.
- Checkout updates remain keyed by `(shopId, checkoutToken)`. New non-null lookup context enriches existing delayed candidates without clearing prior valid values or moving activity time backwards; cart aliases are updated when the cart token changes.
- Active and waiting candidates hand off newer activity to one delayed successor. Checkout-scoped locking and job-ID-guarded cleanup preserve that successor when the original job completes; a matured worker checks current indexed ownership before Shopify lookup or recovery initiation, so a superseded job cannot bill or send early.
- Preserved completed-order suppression, idempotent duplicate updates, missing-context deferral, current-recipient handling, and bounded Shopify lookup behavior. Added focused v2/v3, context-enrichment, successor, cleanup-interleaving, and stale-materialization regressions.
- No Shared, Shopify producer, migration, or architecture `_index.md` files were changed.
## Objective

Consume the published compatible checkout.updated event and schedule an idempotent pending candidate when no Shop/checkout candidate or recovery survives the earlier missing-recipient outcome.
- `./node_modules/.bin/vitest run tests/unit/events/shopify-contract-adapter.test.ts`: passed (10 tests).
- Focused activity/orchestrator suites: passed (32 tests).
- Focused candidate lifecycle/materialization suites after active/waiting handoff change: passed (55 tests).
- First full `./node_modules/.bin/vitest run tests/unit`: passed (202 files, 2,055 tests).
- A later full unit rerun passed 2,051 tests but hit the 5-second timeout in 5 tests across two observability suites. Running those two files alone passed (11 tests); no candidate/task test failed in that rerun.
- `npm run build` (Prisma generation and TypeScript compilation): passed after the final implementation changes.
- `git diff --check`: passed.
- Pylance diagnostics for changed production modules: no errors.
## Context

BACKGROUND-007 allows a no-recipient candidate to finish without materialising a recovery. Current checkout.updated handling discards no-pending/no-recovery events as `recovery-not-found`. Candidate identity is Shop + checkoutToken; the current provider lookup needs separate bounded URL/time context to fetch a fresh abandoned checkout. A v2 event may legitimately lack that context; it must remain safe.
The existing implementation branch started at `ca48592` and reported 11 commits behind `origin/main`; no remote `task/ARCH-028-BACKGROUND-012` ref existed in that repository at start. To preserve the already-claimed dirty Attempt 1, this continuation did not pull, merge, rebase, reset, or recreate the worktree. Implementation commit `3c9491f` was pushed to the newly created explicit `task/ARCH-028-BACKGROUND-012` ref, never to `main`.
The refactored candidate activity service returns `not-reschedulable` for active (non-delayed) jobs; the matured-candidate worker removes Redis indexes in `finally`, and its BullMQ queue uses `removeOnComplete: true`. A qualifying checkout update racing an active no-recipient candidate can therefore be observed while the old job/index still exists, then disappear when the active job completes. This is a **race to validate and prevent**, not a proven production incident.

## Scope
The initial Attempt 1 implementation changes already present in the dedicated Background worktree belong to this task and were preserved. The Shared 1.5.0 package is the accepted SHARED-004 publication.
- Install the exact accepted Shared revision published by SHARED-004 and parse both strict v2 recovery events and v3 checkout.updated through the canonical runtime parser.
- For `(shopId, checkoutToken)` with no pending candidate and no CheckoutRecovery, schedule exactly one fresh pending candidate using the existing queue/index/lock semantics, not abandonedCheckoutUrl as its identity.
- Carry only validated optional URL/creation-time/cart context when available; never infer a URL from the token or substitute receivedAt for creation time to defeat the bounded lookup.
The isolated rerun of the timed-out observability tests passed, but the later full-suite run remains recorded with those transient timeouts; the earlier full-suite run passed completely. Architect review should also confirm whether the implementation branch's 11-commit `origin/main` lag requires synchronization before merge.
- Preserve pending refresh, existing/terminal recovery handling, duplicate/out-of-order checkout updates, tenant scope and existing Shopify ingress responsiveness. Coordinate re-entry with the existing `PendingRecoveryCandidateService` facade, candidate index/lifecycle/activity helpers, checkout-order guard and matured-worker cleanup so a newer qualifying update is not lost behind an active candidate that finishes without a recovery.

## Out of Scope
None identified. Candidate identity remains Shop plus checkout token; no new queue, durable context store, provider filter assumption, or cross-repository change was introduced.

### Worktree and Synchronization Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-028-BACKGROUND-012`, branch `task/ARCH-028-BACKGROUND-012`; clean and up to date with its remote task branch before the report edit.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-028-BACKGROUND-012`, branch `task/ARCH-028-BACKGROUND-012`; existing dirty Attempt 1 changes preserved.
- Shared workspace checkout and shared implementation source checkout were not switched or edited; no other task worktree was reused.
- The implementation branch's starting HEAD was `ca48592`; local status showed it 11 commits behind `origin/main`. Its database submodule was initialized at `b9cb77a74c5fffa250dc65ed34de23113738d8e8`. Recursive submodule synchronization/update was not repeated during this continuation.
- Implementation commit `3c9491f` is published on `origin/task/ARCH-028-BACKGROUND-012`; the parent Completion Report is committed and pushed to its existing `origin/task/ARCH-028-BACKGROUND-012` ref. Both remote refs were verified. Neither branch is pushed to `main`.
- Changing Shopify webhook producer (SHOPIFY-001).
- Redesigning Shopify abandoned checkout API or adding a second durable context cache.
- Missing-recipient materialisation prerequisite (BACKGROUND-007).
- Reachability suppression admission (BACKGROUND-010).

## Requirements

- [ ] Token and Shop determine candidate identity and deduplication; URL never does.
- [ ] No pending/no recovery update creates one candidate safely; existing candidates/recoveries retain their prior behaviour.
- [ ] An update racing an active or completing candidate is not treated as durably handled merely because `refreshCandidateActivity` returned `not-reschedulable`; after a no-recipient completion, the qualifying newer activity must still lead to one surviving/evaluated candidate, without duplicate attempts or hot polling.
- [ ] Cancellation/terminal-order and already-materialised-recovery guards still win over a racing re-entry; use checkout-scoped coordination, not Shop-wide serialization.
- [ ] V2 queued checkout.updated events remain consumable after upgrade.
- [ ] Incomplete lookup context is handled without invented dates/URLs, billing or Meta calls.
- [ ] Background consumer is architect-accepted before Shopify starts producing v3 updates.
- [ ] Keep source modules focused and new production files <=300 lines.

## Work Items

- [ ] Upgrade exact published Shared dependency and parser/contract adapter.
- [ ] Add token-keyed no-recovery candidate scheduling, reusing existing pending candidate service.
- [ ] Handle absent lookup context safely at maturity; include bounded outcome/structured diagnostics.
- [ ] Add duplicate/ordering, v2/v3 compatibility, fresh re-entry and missing-context tests.
- [ ] Add deterministic barrier-controlled interleaving tests for active candidate + later checkout update + no-recipient completion/index cleanup/`removeOnComplete`, including duplicate updates and order-processed suppression.
- [ ] Run repository-declared Background validations.

## Interfaces / Contracts

Consumes SHARED-004 published `@modainteract/moda-interact-shared/shopify` dual-version contract and BACKGROUND-007 current-recipient prerequisite. Uses existing candidate key derived from `(shopId, checkoutToken)` and optional Shopify retrieval hints (`abandonedCheckoutUrl`, `checkoutCreatedAt`, `cartToken`). Produces the existing pending candidate job; no new queue infrastructure.

## Dependencies

- `ARCH-028-BACKGROUND-007`
- `ARCH-028-SHARED-004`

## Enables

- `ARCH-028-SHOPIFY-001`

## Acceptance Criteria

- [ ] Checkout-update with no candidate/recovery schedules by token once; duplicate delivery remains idempotent.
- [ ] A qualifying update during an active candidate that ultimately completes without a recipient survives candidate index removal and BullMQ completion; exactly one valid subsequent candidate evaluation occurs (or a recovery/order terminal state legitimately prevents it).
- [ ] No duplicate recovery, attempt, billed admission or Meta send is created by overlapping updates/candidate cleanup; no tight retry loop or second candidate context store is introduced.
- [ ] v2 strict events still parse without requiring the new optional context.
- [ ] Fresh matured candidate with complete context and current phone can proceed through BACKGROUND-007 prerequisite.
- [ ] Missing context causes no fabricated URL/time, no recovery or billing, no Meta send.
- [ ] Existing pending/recovery refresh and terminal handling do not regress.

## Validation

Focused contract/parser, candidate enqueue/concurrency, deterministic active-job completion/cleanup and re-entry races, completed-order suppression, missing-context maturity, current recipient, historical v2 queue tests; Background tests/build and `git diff --check`.

## Stop Condition

Complete defined work/acceptance/validation, fill the Completion Report, set status `review`, return to `moda_architect`, and STOP. Do not begin a dependent task.

## Implementation Notes

Do not claim checkoutToken is a documented GraphQL abandonedCheckouts filter; it is Moda business identity. Abandoned-checkout retrieval still uses the current bounded URL/time search until an independently verified token retrieval capability exists. Do not add a second durable store or request-lifecycle Shopify API call.

Reuse the existing checkout-scoped mutex and candidate lifecycle/index primitives when coordinating an in-flight candidate with a newer update. Do not treat `active` / `not-reschedulable` as equivalent to a safely persisted refresh, and do not rely on a vanished completed BullMQ job or its removed index to carry a pending update. The implementation must demonstrate the handoff in focused concurrency tests rather than assuming queue cleanup order.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

Not Started.

### Validation Results

Not Run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Changes Requested — Attempt 1 (2026-10-12).

### Review Notes

The submitted dual-version Shopify event adapter correctly parses the published Shared 1.5.0 contract; its v3 checkout-update mapper copies cartToken, checkoutCreatedAt and abandonedCheckoutUrl independently while keeping v2 compatibility. The added checkout-token candidate scheduling, delayed candidate enrichment, active/waiting successor job, index ownership guard before materialisation, and cleanup handoff satisfy the reviewed focused scenarios. These improvements must be retained.

A1-R1 — Mainline integration and preparation boundary: At review, the published implementation task branch (3c9491fecb7190b62a4e8c5eb1ece2377ca7a5f1) is one commit ahead and 11 commits behind current main (GitHub compare: diverged). That absent mainline contains accepted BACKGROUND-010 changes in three overlapping modules: checkout-event-orchestrator.service.ts (checkout-locked activity writes), recovery-materialization.service.ts (suppression retry options and re-entry), and pending-recovery-candidate.worker.ts (bounded retry/failure-marker preservation across cleanup). The submitted worker passes a job ID as its second argument while current main passes an options object. The apparent source integration is therefore not validated and may regress other accepted invariants. The task's own Completion Report explicitly documents that origin/main was not incorporated because the first continuation found a dirty worktree. This is not conformance with mandatory start-of-attempt synchronization. Preserve published history and complete the required main -> task merge/reconciliation before acceptance.

A1-R2 — Out-of-order lookup-hint enrichment: In candidate-activity.service.ts lines 112–122, the stale/equal activity check returns before the optional cartToken/checkoutCreatedAt/abandonedCheckoutUrl merge at lines 144–149. Thus an older/equal-timestamp v3 event with valid missing lookup context cannot enrich a still-delayed token-keyed candidate; it can later defer as lookup-unavailable despite available hints. The fix should enrich only missing valid optional context without regressing lastActivityAt, shortening the inactivity deadline, clearing present context with null/absent values, or changing job identity.

A1-R3 — Canonical Completion Report integrity: Implementation file lists, summary, validation and worktree evidence appear interspersed in Architecture, Context and Scope sections. The actual Completion Report remains Not Started/Files Changed None/Validation Not Run, and Requirements/Work Items/Acceptance Criteria remain unchecked. The agent must restore the canonical sections and record truthful completed work/checks, failures, the divergence/synchronization result, and prepared worktree/submodule evidence. Do not replace the authoritative task scope with an informal report.

### Reviewed Files

- src/events/shopify-contract-adapter.ts
- src/services/checkout-recovery/checkout-event-orchestrator.service.ts
- src/services/checkout-recovery/recovery-materialization.service.ts
- src/services/pending-recovery-candidate.service.ts
- src/services/pending-recovery-candidate/candidate-activity.service.ts
- src/services/pending-recovery-candidate/candidate-lifecycle.service.ts
- src/services/pending-recovery-candidate/candidate-index.store.ts
- src/workers/pending-recovery-candidate.worker.ts
- tests/unit/events/shopify-contract-adapter.test.ts
- tests/unit/services/pending-recovery-candidate/candidate-activity.service.test.ts
- tests/unit/services/pending-recovery-candidate/facade-scheduling.cases.ts
- tests/unit/services/matured-candidate.materialization.test.ts
- tests/unit/workers/pending-recovery-candidate.worker.test.ts
- docs/agent-worktree-isolation-policy.md
- docs/agent-vcs-ownership-policy.md
- docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md
- Current remote main implementations of the three overlapping runtime modules

### Validation Reviewed

Agent reports initial full unit run passing 2,055 tests across 202 files. A later run had five 5-second observability timeouts, with the relevant two observability files (11 tests) passing in isolation. Agent reports passing focused event/adapter (10), activity/orchestrator (32), lifecycle/materialisation (55), npm run build, git diff --check and changed-file diagnostics. These are reported, not independently rerun: ZIP excludes node_modules and Git history. The later full unit run remains a recorded failure, not a pass.

Independent remote validation: background implementation commit 3c9491fecb7190b62a4e8c5eb1ece2377ca7a5f1 and parent Completion Report commit f44bf46fd728574cc4bc1c848d1e3f3b6a6cc732 match their remote task-branch tips. GitHub compare confirms implementation branch diverged and is 11 behind main. Developer-machine worktree cleanliness/isolation cannot be directly observed from the ZIP; supplied descriptions are not Git worktree proof.

### Architecture Conformance

Partially conforms: cross-repository contract ownership, strict v2/v3 parser, token-only safe deferral, local successor logic, checkout index handoff and test coverage are sound in the reviewed snapshot. Overall conformance remains unproven until the stale-context loss is corrected and the branch incorporates the accepted concurrent checkout/recovery work already in main.

### Follow-up

Same task, Attempt 2; bounded corrections only. `status: ready`, `attempt: 1`, `executor: null`, `claimed_at: null` after applying this Architect Review.

1. Reclaim through the canonical `/moda-task ARCH-028-BACKGROUND-012` launcher after committing/pushing this parent Architect Review. Use only the launcher-resolved dedicated parent/implementation worktrees, not shared/default checkouts. Fetch and merge current origin/main into the existing task branch; do not rebase, force-push, reset or merge task -> main. If launcher preparation finds conflict, stop and report it for authorized reconciliation, rather than bypassing the launcher. Preserve original implementation commits.
2. Resolve the three overlapping mainline contracts explicitly: retain checkout-scoped activity serialization from accepted BACKGROUND-010, preserve provider-suppression enqueue retry handling and cleanup-error markers in the candidate worker, and carry the BACKGROUND-012 matured-job identifier/ownership check alongside the existing suppression-retry options instead of replacing either. Revalidate no early/duplicate recovery billing/provider send and the existing missing-recipient deferred path.
3. Allow an older/equal-activity v3 update to fill missing valid candidate lookup hints while preserving the current mature-after timestamp and any already present valid values. Add a regression with a token-only candidate and older/equal timestamp context-bearing update; verify eventual bounded lookup has the merged hints, not `deferred-lookup-unavailable` for those fields, and that duplicate/terminal/order guards still hold.
4. Restore canonical task structure: move implementation summary, files, validation and worktree evidence into Completion Report; remove them from Architecture, Context and Scope; mark only verified Work Items, Requirements and Acceptance Criteria complete; report successes and failures accurately. Record the exact prepared launcher packet's physical-isolation, both branch synchronization and recursive submodule evidence. Document any non-conformance and remediation truthfully.
5. Run task-focused parser, candidate activity/successor/index-cleanup, older-hint enrichment, materialisation, checkout-lock/suppression-retry, and worker regression tests against the mainline-merged tree, plus repository-required build, Prisma validation where relevant, and git diff --check. Run the full unit suite where practical and report timeouts without falsely marking a failed run green.
6. Commit and push both mirrored task branches, set task metadata to review, clear claim, leave Architect Review unchanged, and STOP. Do not start ARCH-028-SHOPIFY-001 or edit docs/decisions/**/_index.md.
