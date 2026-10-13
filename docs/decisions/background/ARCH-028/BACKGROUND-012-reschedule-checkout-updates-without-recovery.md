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
status: complete
priority: 51
executor: null
claimed_at: null
attempt: 3
depends_on:
  - ARCH-028-BACKGROUND-007
  - ARCH-028-SHARED-004
enables:
  - ARCH-028-SHOPIFY-001
created: 2026-10-08
updated: 2026-10-12
---
# Reschedule token-identified checkout updates after missing recipient
Architect-accepted — Attempt 3.
## Architecture

Architecture ID: `ARCH-028`
Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`
## Objective

Consume the published compatible checkout.updated event and schedule an idempotent pending candidate when no Shop/checkout candidate or recovery survives the earlier missing-recipient outcome.
## Context

BACKGROUND-007 allows a no-recipient candidate to finish without materialising a recovery. Current checkout.updated handling discards no-pending/no-recovery events as `recovery-not-found`. Candidate identity is Shop + checkoutToken; the current provider lookup needs separate bounded URL/time context to fetch a fresh abandoned checkout. A v2 event may legitimately lack that context; it must remain safe.
The refactored candidate activity service returns `not-reschedulable` for active (non-delayed) jobs; the matured-candidate worker removes Redis indexes in `finally`, and its BullMQ queue uses `removeOnComplete: true`. A qualifying checkout update racing an active no-recipient candidate can therefore be observed while the old job/index still exists, then disappear when the active job completes. This is a **race to validate and prevent**, not a proven production incident.

## Scope
The Shared 1.5.0 package is the accepted SHARED-004 publication.
- Install the exact accepted Shared revision published by SHARED-004 and parse both strict v2 recovery events and v3 checkout.updated through the canonical runtime parser.
- For `(shopId, checkoutToken)` with no pending candidate and no CheckoutRecovery, schedule exactly one fresh pending candidate using the existing queue/index/lock semantics, not abandonedCheckoutUrl as its identity.
- Carry only validated optional URL/creation-time/cart context when available; never infer a URL from the token or substitute receivedAt for creation time to defeat the bounded lookup.
- Preserve pending refresh, existing/terminal recovery handling, duplicate/out-of-order checkout updates, tenant scope and existing Shopify ingress responsiveness. Coordinate re-entry with the existing `PendingRecoveryCandidateService` facade, candidate index/lifecycle/activity helpers, checkout-order guard and matured-worker cleanup so a newer qualifying update is not lost behind an active candidate that finishes without a recovery.

## Out of Scope
None identified. Candidate identity remains Shop plus checkout token; no new queue, durable context store, provider filter assumption, or cross-repository change was introduced.

## Requirements

- [x] Token and Shop determine candidate identity and deduplication; URL never does.
- [x] No pending/no recovery update creates one candidate safely; existing candidates/recoveries retain their prior behaviour.
- [x] An update racing an active or completing candidate is not treated as durably handled merely because `refreshCandidateActivity` returned `not-reschedulable`; after a no-recipient completion, the qualifying newer activity must still lead to one surviving/evaluated candidate, without duplicate attempts or hot polling.
- [x] Cancellation/terminal-order and already-materialised-recovery guards still win over a racing re-entry; use checkout-scoped coordination, not Shop-wide serialization.
- [x] V2 queued checkout.updated events remain consumable after upgrade.
- [x] Incomplete lookup context is handled without invented dates/URLs, billing or Meta calls.
- [x] Background consumer is architect-accepted before Shopify starts producing v3 updates.
- [x] Keep source modules focused and new production files <=300 lines.

## Work Items

- [x] Upgrade exact published Shared dependency and parser/contract adapter.
- [x] Add token-keyed no-recovery candidate scheduling, reusing existing pending candidate service.
- [x] Handle absent lookup context safely at maturity; include bounded outcome/structured diagnostics.
- [x] Add duplicate/ordering, v2/v3 compatibility, fresh re-entry and missing-context tests.
- [x] Add deterministic barrier-controlled interleaving tests for active candidate + later checkout update + no-recipient completion/index cleanup/`removeOnComplete`, including duplicate updates and order-processed suppression.
- [x] Run repository-declared Background validations.

## Interfaces / Contracts

Consumes SHARED-004 published `@modainteract/moda-interact-shared/shopify` dual-version contract and BACKGROUND-007 current-recipient prerequisite. Uses existing candidate key derived from `(shopId, checkoutToken)` and optional Shopify retrieval hints (`abandonedCheckoutUrl`, `checkoutCreatedAt`, `cartToken`). Produces the existing pending candidate job; no new queue infrastructure.

## Dependencies

- `ARCH-028-BACKGROUND-007`
- `ARCH-028-SHARED-004`

## Enables

- `ARCH-028-SHOPIFY-001`

## Acceptance Criteria

- [x] Checkout-update with no candidate/recovery schedules by token once; duplicate delivery remains idempotent.
- [x] A qualifying update during an active candidate that ultimately completes without a recipient survives candidate index removal and BullMQ completion; exactly one valid subsequent candidate evaluation occurs (or a recovery/order terminal state legitimately prevents it).
- [x] No duplicate recovery, attempt, billed admission or Meta send is created by overlapping updates/candidate cleanup; no tight retry loop or second candidate context store is introduced.
- [x] v2 strict events still parse without requiring the new optional context.
- [x] Fresh matured candidate with complete context and current phone can proceed through BACKGROUND-007 prerequisite.
- [x] Missing context causes no fabricated URL/time, no recovery or billing, no Meta send.
- [x] Existing pending/recovery refresh and terminal handling do not regress.

## Validation

Focused contract/parser, candidate enqueue/concurrency, deterministic active-job completion/cleanup and re-entry races, completed-order suppression, missing-context maturity, current recipient, historical v2 queue tests; Background tests/build and `git diff --check`.

## Stop Condition

Complete defined work/acceptance/validation, fill the Completion Report, set status `review`, return to `moda_architect`, and STOP. Do not begin a dependent task.

## Implementation Notes

Do not claim checkoutToken is a documented GraphQL abandonedCheckouts filter; it is Moda business identity. Abandoned-checkout retrieval still uses the current bounded URL/time search until an independently verified token retrieval capability exists. Do not add a second durable store or request-lifecycle Shopify API call.

Reuse the existing checkout-scoped mutex and candidate lifecycle/index primitives when coordinating an in-flight candidate with a newer update. Do not treat `active` / `not-reschedulable` as equivalent to a safely persisted refresh, and do not rely on a vanished completed BullMQ job or its removed index to carry a pending update. The implementation must demonstrate the handoff in focused concurrency tests rather than assuming queue cleanup order.

## Completion Report

### Status

Ready for architect review — Attempt 3.

### Files Changed

Task-owned files include `package.json`, `package-lock.json`, `src/events/shopify-contract-adapter.ts`, `src/services/checkout-recovery.service.ts`, `src/services/checkout-recovery/checkout-event-orchestrator.service.ts`, `src/services/checkout-recovery/recovery-materialization.service.ts`, `src/services/pending-recovery-candidate.service.ts`, `src/services/pending-recovery-candidate/candidate-activity.service.ts`, `src/services/pending-recovery-candidate/candidate-index.store.ts`, `src/services/pending-recovery-candidate/candidate-lifecycle.service.ts`, and `src/workers/pending-recovery-candidate.worker.ts`. Tests cover the adapter, orchestrator, checkout refresh, matured materialization, candidate scheduling/activity/lifecycle, and candidate worker. The mainline merge also retains accepted BACKGROUND-010 changes in checkout activity serialization, suppression retry/re-entry, and cleanup-marker handling.

Attempt 3 implementation changes were limited to `src/services/pending-recovery-candidate/candidate-activity.service.ts` and `tests/unit/services/pending-recovery-candidate/candidate-activity.service.test.ts`.

### Work Completed

- Merged current `origin/main` into the existing task branch without rewriting published history. Resolved the four overlapping files by retaining checkout-scoped activity locking, suppression retry options and cleanup error markers, while carrying the BACKGROUND-012 matured job ID through the same options object.
- Attempt 3 A2-R1 correction: stale/equal activity now keeps each already-populated cart token, checkout creation time and abandoned-checkout URL, and fills only missing hints. Conflicting-only updates do not call `job.updateData`, alter delay/indexes, change activity time, or change job identity. A mixed missing-URL/populated-time regression proves that the missing URL is enriched without replacing the existing time or cart token. The newer-activity refresh policy is unchanged.
- Added regressions for older and equal timestamps, stale hint enrichment followed through bounded Shopify lookup, worker retry options and checkout-lock behavior.
- Attempt 2 launcher evidence: dedicated parent and implementation worktrees were used; both branches were synchronized with current main; recursive implementation submodule synchronization/update and recorded-commit verification passed. Shared/default checkouts and other task worktrees were not reused or switched for implementation.
- Attempt 3 prepared execution used canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`, parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-028-BACKGROUND-012`, and implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-028-BACKGROUND-012`, both on `task/ARCH-028-BACKGROUND-012`. The parent worktree was at the pushed claim commit `54098192ebb70a74d1364a112d292ada4ccd9d2d`; the implementation worktree started at `b5795539e19c62a5b9ed7b6ccc433ee895043cc9` with current main already incorporated. The launcher verified recursive submodules; `database` remained at `b9cb77a74c5fffa250dc65ed34de23113738d8e8`. No shared/default checkout, other task worktree, or submodule gitlink was changed.
- The launcher ran `git submodule sync --recursive` and `git submodule update --init --recursive` in the implementation worktree and verified recorded submodule commits. `database` is at `b9cb77a74c5fffa250dc65ed34de23113738d8e8`.
- Attempt 2 implementation commit `b5795539e19c62a5b9ed7b6ccc433ee895043cc9` remains in history. Attempt 3 implementation commit `2be5beb8462813d76e9f9ee904a11c914b59cbac` is pushed to `origin/task/ARCH-028-BACKGROUND-012`; the local branch matches that remote ref and the implementation worktree is clean. The parent task claim commit was pushed at `54098192ebb70a74d1364a112d292ada4ccd9d2d`; this Attempt 3 report and review status are submitted on the same parent task branch. Neither branch is pushed to `main`.

### Validation Results

- Attempt 3 focused activity suite: passed (17 tests), including the conflicting older/equal values, mixed enrichment, and existing null-field enrichment cases. The first focused run caught a null-preservation issue in the initial edit; the fallback was corrected and the same suite passed on rerun.
- Mandated focused activity/stale context, checkout refresh, candidate lifecycle/successor, recovery materialization/job ownership, suppression admission, checkout orchestration, and pending-candidate worker suites: passed (8 files, 129 tests).
- Repository-declared `npm run test:unit`: passed (204 files, 2,109 tests).
- `npm run build` (Prisma client generation and TypeScript compilation): passed.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.
- PostgreSQL integration was not run for Attempt 3 and remains unverified; it is not reported as passing.
- Final implementation verification: clean worktree, task branch matches pushed commit `2be5beb8462813d76e9f9ee904a11c914b59cbac`, and database submodule remains at `b9cb77a74c5fffa250dc65ed34de23113738d8e8`.

### Deviations

The first canonical preparation attempt stopped on the authorized mainline merge conflicts. After the user authorized reconciliation, the conflicts were resolved in the existing dedicated implementation worktree, then the canonical launcher was rerun successfully and durably claimed Attempt 2. An opt-in PostgreSQL integration test could not run because the configured local database was unavailable.

### Assumptions

Checkout token remains Moda business identity rather than an asserted Shopify GraphQL filter. Retrieval continues to use the bounded URL/time lookup contract.

### Unresolved Issues

Awaiting architect review. Optional PostgreSQL integration validation remains unverified because no local PostgreSQL endpoint was available.

### Architectural Concerns

None identified beyond the explicit review gate: Shopify producer work must remain blocked until the Background consumer is architect-accepted.

## Architect Review

### Review Status

Accepted — Attempt 3 (2026-10-12).

### Review Notes

**Attempt 3 — Accepted (2026-10-12):**

A2-R1 **resolved**. `PendingRecoveryCandidateActivityService.enrichMissingLookupContext()` now prefers existing non-null `cartToken`, `checkoutCreatedAt`, and `abandonedCheckoutUrl` over conflicting stale/equal-update hints, enriching only genuinely absent lookup context. The new regressions cover both older and equal-timestamp conflicting updates and mixed missing/populated hints. Conflicting-only activity does not call `job.updateData`, `changeDelay`, or candidate index mutations; missing-only enrichment updates the existing delayed BullMQ job without moving the activity timestamp, maturity deadline, checkout identity, or job identity.

Previously resolved A1-R1 mainline integration and BACKGROUND-010 interoperability, A1-R3 task/launcher evidence, strict v2/v3 shared-contract handling, matured-job ownership and suppression-retry coexistence remain intact. No further task-owned corrections are required.

**Historical Attempt 2 review (preserved):**

A1-R1 **resolved**. The implementation task branch includes the accepted mainline BACKGROUND-010 checkout-scoped activity locking, suppression-admission retries, and cleanup-error marker handling. The matured-job ID is carried alongside `retrySuppressionAdmission` in the materialization options instead of replacing the accepted contract. Independent remote comparison confirms the task branch contains current `main` and is not behind it. The Task Attempt 2 execution packet and Completion Report record launcher-resolved sibling worktrees, branch synchronization, and recursive submodule preparation. The implementation commit `b5795539e19c62a5b9ed7b6ccc433ee895043cc9` and parent report commit `36501e5099d7e810b9fd54977a5aa910af6a5a4b` match the published task refs.

A1-R3 **resolved**. The Completion Report is in the canonical section; actual source changes and validation are recorded, and relevant Requirement, Work Item, and Acceptance Criteria checkboxes are updated. The producer-acceptance gate remains unchecked until this task receives an Accepted review.

A1-R2 **partially resolved**. Stale/equal-timestamp events now enrich null candidate lookup hints without altering `lastActivityAt`, `changeDelay`, or candidate job ID. However, `PendingRecoveryCandidateActivityService.enrichMissingLookupContext()` at `src/services/pending-recovery-candidate/candidate-activity.service.ts` lines 211–213 uses `input.checkoutCreatedAt ?? existing.checkoutCreatedAt` and `input.abandonedCheckoutUrl ?? existing.abandonedCheckoutUrl`. A stale/equal event containing *non-null* conflicting fields replaces already populated valid current hints. This violates the explicit Attempt 1 requirement to fill **only missing** context. The new tests exercise initially-null context but not conflicting non-null values. Stale checkout events may therefore regress bounded lookup to an older URL or different creation-time window. This is a bounded task-owned correctness defect, not a redesign request.

**Historical Attempt 1 review notes (retained below):**

The submitted dual-version Shopify event adapter correctly parses the published Shared 1.5.0 contract; its v3 checkout-update mapper copies cartToken, checkoutCreatedAt and abandonedCheckoutUrl independently while keeping v2 compatibility. The added checkout-token candidate scheduling, delayed candidate enrichment, active/waiting successor job, index ownership guard before materialisation, and cleanup handoff satisfy the reviewed focused scenarios. These improvements must be retained.

A1-R1 — Mainline integration and preparation boundary: At review, the published implementation task branch (3c9491fecb7190b62a4e8c5eb1ece2377ca7a5f1) is one commit ahead and 11 commits behind current main (GitHub compare: diverged). That absent mainline contains accepted BACKGROUND-010 changes in three overlapping modules: checkout-event-orchestrator.service.ts (checkout-locked activity writes), recovery-materialization.service.ts (suppression retry options and re-entry), and pending-recovery-candidate.worker.ts (bounded retry/failure-marker preservation across cleanup). The submitted worker passes a job ID as its second argument while current main passes an options object. The apparent source integration is therefore not validated and may regress other accepted invariants. The task's own Completion Report explicitly documents that origin/main was not incorporated because the first continuation found a dirty worktree. This is not conformance with mandatory start-of-attempt synchronization. Preserve published history and complete the required main -> task merge/reconciliation before acceptance.

A1-R2 — Out-of-order lookup-hint enrichment: In candidate-activity.service.ts lines 112–122, the stale/equal activity check returns before the optional cartToken/checkoutCreatedAt/abandonedCheckoutUrl merge at lines 144–149. Thus an older/equal-timestamp v3 event with valid missing lookup context cannot enrich a still-delayed token-keyed candidate; it can later defer as lookup-unavailable despite available hints. The fix should enrich only missing valid optional context without regressing lastActivityAt, shortening the inactivity deadline, clearing present context with null/absent values, or changing job identity.

A1-R3 — Canonical Completion Report integrity: Implementation file lists, summary, validation and worktree evidence appear interspersed in Architecture, Context and Scope sections. The actual Completion Report remains Not Started/Files Changed None/Validation Not Run, and Requirements/Work Items/Acceptance Criteria remain unchecked. The agent must restore the canonical sections and record truthful completed work/checks, failures, the divergence/synchronization result, and prepared worktree/submodule evidence. Do not replace the authoritative task scope with an informal report.

### Reviewed Files

Attempt 3 additionally inspected:
- `src/services/pending-recovery-candidate/candidate-activity.service.ts` — stale/equal-context fallbacks and no-op handling
- `tests/unit/services/pending-recovery-candidate/candidate-activity.service.test.ts` — older/equal conflicting populated hints and mixed-context enrichment
- Attempt 3 Completion Report, ARCH-028 task dependencies, checkout-scoped coordination and review history

Attempt 2 additionally inspected:
- `src/services/pending-recovery-candidate/candidate-activity.service.ts` (lines 109–149 and 207–228, blocking A2-R1)
- `tests/unit/services/pending-recovery-candidate/candidate-activity.service.test.ts` (stale/equal context test coverage)
- `src/services/pending-recovery-candidate/candidate-lifecycle.service.ts` (active/waiting successors)
- `src/services/checkout-recovery/recovery-materialization.service.ts` (job ownership / suppression-retry option coexistence)
- `src/workers/pending-recovery-candidate.worker.ts` (cleanup errors and retry flags)
- `src/services/checkout-recovery/checkout-event-orchestrator.service.ts` (checkout activity lock)
- Attempt 2 Completion Report and branch reconciliation evidence

Historical Attempt 1 reviewed files (retained below):

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

Attempt 3 agent-reported: focused tests PASS (8 files, 129 tests); full unit suite PASS (204 files, 2,109 tests); `npm run build` PASS; `npm run prisma:validate` PASS; `git diff --check` PASS. PostgreSQL integration remains UNVERIFIED, not passed; this optional environment-dependent validation was already assessed as non-blocking for A2-R1. I inspected the actual source and test assertions but did not independently execute the Node/Prisma suite or database integration.

Independently verified the implementation commit `2be5beb8462813d76e9f9ee904a11c914b59cbac` and parent report commit `6c99dc827c24df4b0746c3f7fbfec853f84a7c52` against their exact remote `task/ARCH-028-BACKGROUND-012` branch tips. Both changed implementation/test Git blob IDs and the parent task Git blob ID match the submitted ZIP. GitHub compare shows Background task branch ahead of current `main` by 4 commits and 0 behind. Launcher-resolved dedicated worktree, synchronization and recursive submodule evidence is recorded in the Completion Report; physical developer-machine cleanliness was not independently observed.

Attempt 2 agent-reported validation: full unit suite PASS (204 files, 2,106 tests); focused regressions PASS; `npm run build` PASS; `npx prisma validate --schema database/prisma/schema.prisma` PASS; changed-file diagnostics and `git diff --check` PASS. The earlier observability timeout run and subsequent isolated/passing full run are honestly distinguished. Optional PostgreSQL integration remained UNVERIFIED due to no `localhost:5432`; this is not independently a blocker for the specific A2-R1 correction, but must not be represented as a pass. I inspected source/test assertions and did not rerun unit/build/Prisma validation in the snapshot, which has no installed dependencies.

Independent GitHub check: both reported task branch tips match the exact remote commit SHAs; task branch currently contains `main` and is three task commits ahead / zero behind at review. Parent task and sampled implementation file Git blobs match uploaded snapshot. Task worktree isolation/cleanliness is supported by the launcher packet in the report, not direct observation of developer-machine worktrees.

Historical Attempt 1 validation (retained below):

Agent reports initial full unit run passing 2,055 tests across 202 files. A later run had five 5-second observability timeouts, with the relevant two observability files (11 tests) passing in isolation. Agent reports passing focused event/adapter (10), activity/orchestrator (32), lifecycle/materialisation (55), npm run build, git diff --check and changed-file diagnostics. These are reported, not independently rerun: ZIP excludes node_modules and Git history. The later full unit run remains a recorded failure, not a pass.

Independent remote validation: background implementation commit 3c9491fecb7190b62a4e8c5eb1ece2377ca7a5f1 and parent Completion Report commit f44bf46fd728574cc4bc1c848d1e3f3b6a6cc732 match their remote task-branch tips. GitHub compare confirms implementation branch diverged and is 11 behind main. Developer-machine worktree cleanliness/isolation cannot be directly observed from the ZIP; supplied descriptions are not Git worktree proof.

### Architecture Conformance

Attempt 3: **Conforms — Accepted**. Bounded token/Shop-scoped candidate re-entry, v2/v3 canonical published contract use, late lookup-hint enrichment, ordered candidate maturity, completed-order/terminal prevention, current recipient admission and mainline BACKGROUND-010 protections meet this task's defined requirements. No runtime contract, database migration, additional queue, Shopify producer work, or unrelated refactor was introduced in Attempt 3. All previously blocking review findings are resolved.

Attempt 2: conforms on mainline reconciliation, shared-contract versioning, checkout-level coordination, successor preservation, materialization job-ID and retry-option coexistence, and honest validation reporting. A2-R1 prevents full acceptance because stale/equal events can still replace non-null current lookup hints. No database, Shopify, Shared, queue, or unrelated service changes are justified by this correction.

Historical Attempt 1 assessment (retained below):

Partially conforms: cross-repository contract ownership, strict v2/v3 parser, token-only safe deferral, local successor logic, checkout index handoff and test coverage are sound in the reviewed snapshot. Overall conformance remains unproven until the stale-context loss is corrected and the branch incorporates the accepted concurrent checkout/recovery work already in main.

### Follow-up

None required for `ARCH-028-BACKGROUND-012`. The developer performs final integration (implementation branch first, then parent gitlink/task branch). `ARCH-028-SHOPIFY-001` becomes eligible for Architect readiness promotion once its accepted dependencies and merged consumer implementation are available; this patch neither starts Shopify work nor changes its task state or any `_index.md`.

**Historical Attempt 2 A2-R1 correction contract (satisfied by Attempt 3):**

1. Reclaim **the same task** through `/moda-task ARCH-028-BACKGROUND-012` only after this parent review patch has been committed and pushed. This review returns the task to `status: ready`, `attempt: 2`, `executor: null`, `claimed_at: null`. The launcher owns canonical physical worktree preparation and synchronization.
2. In `src/services/pending-recovery-candidate/candidate-activity.service.ts`, for stale/equal activity, prefer every already-present valid hint (`cartToken`, `checkoutCreatedAt`, `abandonedCheckoutUrl`) over incoming values. Enrich only fields that are genuinely missing. Continue accepting independently optional context, and do not regress `lastActivityAt`, adjust maturity deadline, create another job, erase populated context, or change tenant/checkout identity. Do not alter newer-activity refresh policy unnecessarily.
3. Add a focused test with a delayed candidate that already has a valid checkout-created timestamp and abandoned URL, followed by an older/equal update bearing different non-null values. Assert the stored/job candidate retains the originals, `job.updateData` is not called merely for conflicting hints, `changeDelay` is not called, and existing null-field enrichment tests continue to pass. Test a mixed case where one hint is missing and another populated, proving enrichment does not overwrite the populated one.
4. Rerun the task-focused stale/equal context, candidate activity, checkout-refresh, successor/ownership, materialization, suppression retry and worker suites against the synchronized task branch, plus repository-required build, Prisma validation and `git diff --check`. Report genuinely executed checks. PostgreSQL integration is optional here and must remain explicitly unverified unless actually run successfully.
5. Update the Attempt 3 Completion Report, leave the Architect Review unchanged, commit/push both mirrored task branches, submit `status: review` with the claim cleared, and STOP. Do not start `ARCH-028-SHOPIFY-001`, create another queue or modify `docs/decisions/**/_index.md`.

**Historical Attempt 1 follow-up (retained below; superseded by the Attempt 2 contract above):**

Same task, Attempt 2; bounded corrections only. `status: ready`, `attempt: 1`, `executor: null`, `claimed_at: null` after applying this Architect Review.

1. Reclaim through the canonical `/moda-task ARCH-028-BACKGROUND-012` launcher after committing/pushing this parent Architect Review. Use only the launcher-resolved dedicated parent/implementation worktrees, not shared/default checkouts. Fetch and merge current origin/main into the existing task branch; do not rebase, force-push, reset or merge task -> main. If launcher preparation finds conflict, stop and report it for authorized reconciliation, rather than bypassing the launcher. Preserve original implementation commits.
2. Resolve the three overlapping mainline contracts explicitly: retain checkout-scoped activity serialization from accepted BACKGROUND-010, preserve provider-suppression enqueue retry handling and cleanup-error markers in the candidate worker, and carry the BACKGROUND-012 matured-job identifier/ownership check alongside the existing suppression-retry options instead of replacing either. Revalidate no early/duplicate recovery billing/provider send and the existing missing-recipient deferred path.
3. Allow an older/equal-activity v3 update to fill missing valid candidate lookup hints while preserving the current mature-after timestamp and any already present valid values. Add a regression with a token-only candidate and older/equal timestamp context-bearing update; verify eventual bounded lookup has the merged hints, not `deferred-lookup-unavailable` for those fields, and that duplicate/terminal/order guards still hold.
4. Restore canonical task structure: move implementation summary, files, validation and worktree evidence into Completion Report; remove them from Architecture, Context and Scope; mark only verified Work Items, Requirements and Acceptance Criteria complete; report successes and failures accurately. Record the exact prepared launcher packet's physical-isolation, both branch synchronization and recursive submodule evidence. Document any non-conformance and remediation truthfully.
5. Run task-focused parser, candidate activity/successor/index-cleanup, older-hint enrichment, materialisation, checkout-lock/suppression-retry, and worker regression tests against the mainline-merged tree, plus repository-required build, Prisma validation where relevant, and git diff --check. Run the full unit suite where practical and report timeouts without falsely marking a failed run green.
6. Commit and push both mirrored task branches, set task metadata to review, clear claim, leave Architect Review unchanged, and STOP. Do not start ARCH-028-SHOPIFY-001 or edit docs/decisions/**/_index.md.
