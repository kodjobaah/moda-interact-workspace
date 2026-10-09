---
id: ARCH-028-BACKGROUND-007
architecture_id: ARCH-028
title: Require current WhatsApp recipient before recovery materialisation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 25
executor: null
claimed_at: null
attempt: 2
depends_on: []
enables:
  - ARCH-028-BACKGROUND-005
  - ARCH-028-BACKGROUND-012
created: 2026-10-07
updated: 2026-10-09
---

# Require current WhatsApp recipient before recovery materialisation

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Require a canonical, Shop-scoped current `CustomerPhone` before materialising a `CheckoutRecovery`; when the number is missing, finish the candidate with no recovery, billing or Meta work. Ensure the resolved recipient passed to the initial send is the same one that passed this prerequisite. Checkout-update re-entry is a separate task (BACKGROUND-012).

## Context

The current recovery initiator creates `CheckoutRecovery` before recipient resolution and then throws when no customer phone/test recipient exists. `PendingRecoveryCandidate` already represents a checkout that may later become recoverable, so a missing phone should stop materialisation before a durable recovery exists. No DATABASE-003 required-recipient field, provider status or compensation contract is needed for this prerequisite.

The fresh abandoned-checkout lookup may contain a phone that Customer resolution persists through `CustomerPhoneService`; otherwise an already-current Shop-scoped `CustomerPhone` may still exist. Only the absence of an active usable `CustomerPhone` after that resolution is a true missing-recipient outcome. `Customer.phone` is not authoritative.

## Scope

- At matured-candidate materialisation, use the fresh abandoned-checkout snapshot to resolve/update the Shop-scoped Customer and `CustomerPhone` history before deciding recipient availability.
- If no active usable current `CustomerPhone` exists, return a bounded `no-recipient`/deferred outcome **without creating `CheckoutRecovery`**, `RecoveryOutreachAttempt`, UsageReservation/UsageEvent, outbound message or provider call.
- Preserve the normal matured-candidate cleanup; do not keep a fake blocked recovery solely as a waiting record.
- Pass the same canonical digits-only `CustomerPhone` recipient into the initial recovery-send path; it must not silently fall back to stale `Customer.phone`, checkout customer fields or a non-test WhatsApp recipient override.
- If a current `CustomerPhone` exists even when `Customer.phone` is null/stale, treat the recipient as present and continue with the existing admission path. BACKGROUND-005 will separately enforce durable per-attempt recipient snapshots once DATABASE-003 is integrated.
- Do not add aggressive polling solely for missing phone.

## Out of Scope

- Later `CHECKOUTS_UPDATE` re-entry, its Shared/Shopify producer/Background consumer contracts (BACKGROUND-012, SHARED-003/004, SHOPIFY-001).
- Recipient suppression TTL and mandatory attempt-recipient schema adoption.
- Provider error classification.
- Synchronous failure.
- Merchant notification.

## Requirements

- [x] Missing recipient is zero billing and zero provider work.
- [x] It is not persisted as a permanent Customer property.
- [x] A later usable phone is eligible when another valid candidate is evaluated; this task does not manufacture a retry event.
- [x] Test-only recipient behaviour remains explicitly development/test scoped and must not become production identity state.
- [x] New ARCH-028 production source files SHOULD target <=200 physical lines and MUST NOT exceed 300 physical lines.
- [x] Existing production source files already above 300 physical lines may receive only minimal integration/composition edits; substantive new ARCH-028 policy, orchestration, persistence/accounting or provider-specific behaviour MUST be extracted into focused modules.
- [x] Keep independently testable orchestration, policy/classification, persistence/accounting and provider-adapter responsibilities separated; do not introduce a new catch-all service merely because they belong to the same architecture task.

## Work Items

- [x] Move the missing-recipient decision to the pending-candidate materialisation boundary before `CheckoutRecovery` creation.
- [x] Resolve/update Customer + current `CustomerPhone` from the fresh checkout snapshot and use current `CustomerPhone` as the authoritative source.
- [x] Return a bounded deferred/no-recipient result without recovery/attempt/billing/provider state.
- [x] Ensure initial provider send receives exactly the canonical recipient validated at materialisation, not a stale original webhook/customer field.
- [x] Ensure a null/stale `Customer.phone` does not block when an active `CustomerPhone` exists.
- [x] Add focused tests.
- [x] Review touched production-file sizes/responsibilities and extract focused modules before any new or expanded production source crosses the 300-line ceiling.

## Interfaces / Contracts

Consumes existing Customer/CustomerPhone resolution and pending-candidate materialisation services. Provides a bounded canonical recipient prerequisite for BACKGROUND-005 and BACKGROUND-012. No new database enum/state or required attempt-recipient field is introduced here.

## Dependencies

None.

## Enables

- `ARCH-028-BACKGROUND-005`
- `ARCH-028-BACKGROUND-012`

## Acceptance Criteria

- [x] Missing recipient produces no `CheckoutRecovery`, outreach attempt, billing reservation, outbound UsageEvent/message or Meta call.
- [x] Existing current `CustomerPhone` is honored even when `Customer.phone` is null/stale.
- [x] The exact validated current `CustomerPhone` recipient is supplied to the initial Meta send; production cannot silently substitute `TEST_WHATSAPP_RECIPIENT` or a stale snapshot.
- [x] Duplicate candidate execution remains idempotent and current non-missing recipients retain existing recovery behaviour.
- [x] No polling loop or durable no-recipient recovery block is introduced.
- [x] No new ARCH-028 production source file exceeds 300 physical lines; new files target <=200 lines where the responsibility remains coherent.
- [x] Existing >300-line production files contain only thin ARCH-028 wiring/composition changes, with substantive new behaviour implemented in focused modules.
- [x] No touched production module combines independently testable orchestration, policy/classification, persistence/accounting and provider-specific mechanics into one catch-all implementation.

## Validation

Focused recovery-initiation tests, full Background unit tests/build and `git diff --check`. When PostgreSQL integration is required, run it through the repository-owned `npm run test:integration` disposable PostgreSQL/Redis harness; do not depend on a pre-existing `localhost:5432` instance or run integration cases against a durable database. Record separately any verified, unrelated pre-task suite failures.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

Do not conflate missing recipient with `WHATSAPP_RECIPIENT_SUPPRESSED`. Suppression is a durable policy block on a known recipient and may remain on a materialised recovery; missing recipient means there is no executable recovery yet.

Prefer a bounded candidate-materialisation recipient prerequisite and reuse existing Customer/CustomerPhone services. Keep `recovery-initiation.service.ts` thin; the separate BACKGROUND-012 task handles checkout-update re-entry after the Shared contract and producer/consumer rollout are defined.

Maintainability is part of acceptance, not a post-task cleanup. Prefer a thin task-facing/orchestrator service that delegates to focused domain modules. Tests may remain larger when a cohesive behavioural matrix is clearer; the production-source line ceiling does not require microscopic file splitting.

## Completion Report

### Status

Ready for Review

### Files Changed

Implementation repository:

- `src/services/checkout-recovery/recovery-recipient-resolver.service.ts`
- `src/services/checkout-recovery/recovery-materialization.service.ts`
- `src/services/checkout-recovery/recovery-initiation.service.ts`
- `src/services/checkout-recovery.service.ts`
- `tests/unit/services/matured-candidate.materialization.test.ts`
- `tests/unit/services/checkout-recovery/recovery-materialization.service.test.ts`
- `tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts`
- `vitest.config.ts`
- `scripts/test-integration.mjs`
- `tests/integration/translation-enum-bindings.integration.test.ts`

Parent task record: this task file only.

### Work Completed

- Added a focused `RecoveryRecipientResolverService` that resolves/updates the Customer from the fresh abandoned-checkout seed, reads that Customer's active Shop-scoped `CustomerPhone`, and returns its digits-only number or `null`.
- The matured-candidate materialisation path now resolves the recipient before initiation. Missing/empty current phone returns `deferred-no-recipient` before creating a CheckoutRecovery, outreach attempt, billing admission/reservation, outbound message or provider call.
- Passed the exact resolved recipient through recovery initiation to the outbound send. A checkout snapshot's phone and `Customer.phone` are not fallback identities for this path.
- Restricted the legacy `TEST_WHATSAPP_RECIPIENT` override to explicit `development` or `test` `NODE_ENV` values; production cannot use it.
- Candidate index cleanup remains in the worker's existing `finally` path for the new deferred result. No polling or durable no-recipient recovery state was added.
- Added focused regressions for no-recipient side-effect absence, current CustomerPhone precedence when snapshot/Customer phone is absent or stale, digits-only send recipient, bounded materialisation outcome, and production rejection of the test override.
- Production source sizes: new resolver 17 lines; recovery materialisation 134; recovery initiation 253; checkout recovery composition 206. No new production module exceeds 300 lines; the new resolver is below the 200-line target.
- Default Vitest collection now excludes `tests/integration/**` unless `MODA_DISPOSABLE_INTEGRATION=1`; the translation-enum DB suite independently requires that marker. The existing disposable integration harness now includes that suite by default without adding a new provisioning path.

### Attempt 2 Launcher Evidence

- Canonical primary workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-028-BACKGROUND-007`, `task/ARCH-028-BACKGROUND-007`.
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-028-BACKGROUND-007`, `task/ARCH-028-BACKGROUND-007`.
- Shared workspace checkout switched or mutated for task work: no. Shared implementation checkout switched or mutated: no. Another task worktree reused: no.
- Start-of-attempt synchronization: parent and implementation remote task branches fast-forwarded `not-needed`; `origin/main` was `already-current` in both worktrees.
- Recursive implementation submodules: `git submodule sync --recursive` passed; `git submodule update --init --recursive` passed; database submodule at `ef51500b2728bc0c894e627dfa1c9e6c9d4d9a13`.
- Attempt 2 claim: executor `copilot`, claimed `2026-10-09T09:47:15Z`, parent claim commit `326d95b646c85c36967e4b1e2155d6dacd97246d`, committed and pushed. Implementation worktree began at `fcd7dfe63471458ca14734e3de4083b38f0b7754`.

### Validation Results

- `npm ci`: passed; installed 496 packages. npm reported 9 audit findings (3 moderate, 6 high) and install-script approval notices; package manifests/lockfiles were not changed.
- Focused materialisation and initiation suites: 55 tests passed across `matured-candidate.materialization.test.ts`, `recovery-materialization.service.test.ts` and `recovery-initiation.service.test.ts`.
- `npm test` with `TEST_DATABASE_URL=postgresql://postgres@127.0.0.1:5432/should_not_connect?schema=public`: 174 test files and 1,877 tests passed. No integration files were collected and no connection to the deliberately unreachable local endpoint was attempted.
- Focused recipient/materialisation/initiation tests: 3 files, 55 tests passed.
- `npm run test:integration -- tests/integration/translation-enum-bindings.integration.test.ts`, with the same stale ambient URL: 1 file, all 4 translation-enum tests passed through the disposable harness. The helper used `pgvector/pgvector:pg17`, unique generated database credentials and Docker-assigned ports; it overrides both test database and Redis URLs and removes both containers/volumes in `finally`.
- Default `npm run test:integration`: 4 of 5 files passed; 12 tests passed and the unchanged `tests/integration/conversation-turn-scheduling.integration.test.ts` case `coalesces three persisted fragments and claims only the settled current version` timed out at 5 seconds. A targeted harness run of that file plus `tests/integration/commerce/voice-workflow.test.ts` reproduced the same scheduling timeout and 3 voice-workflow failures (`job.opts` is undefined in the test-created BullMQ job at `src/workers/whatsapp.worker.ts:84`); 4 of the 8 selected tests passed.
- `npm run test:unit`: 173 files passed, 1 file failed; 1,876 tests passed and 1 failed. The failure was one 5-second timeout in unchanged `tests/unit/runtime/observability-startup.test.ts`. Running that file alone produced 6 passes and 4 timeouts; the previous attempt had passed it alone, confirming this remains an unstable unrelated validation surface. The earlier attempt's four translation-enum `localhost:5432` failures are now prevented in the default path and the cases pass in the disposable harness.
- `npm run build`: passed, including Prisma generation and TypeScript compilation. `npm run prisma:validate`: passed. `git diff --check`: passed. Editor diagnostics reported no errors in changed production modules/tests.
- The translation-enum localhost failure identities are also recorded in development baseline `ARCH025-BACKGROUND-TEST-001`; that baseline does not excuse unsafe default routing. No package manifest/lockfile changes were made; the earlier `npm ci` reported 9 audit findings (3 moderate, 6 high).

### Deviations

The task's default `npm test` path and disposable translation-enum suite now pass. Remaining failures are outside changed files: the `ARCH-007-BACKGROUND-010` conversation-turn scheduling integration timeout, the unchanged voice-workflow fixture's missing `job.opts`, and variable observability startup timeouts. These are recorded for `moda_background` follow-up; no unrelated worker behavior, fixture, or observability code was changed. The ARCH-025 translation-enum baseline is retained as historical evidence, while the unsafe default collection behavior has been corrected here.

### Assumptions

- `CustomerService.resolveCustomer` remains the authoritative Shop-scoped identity resolver for a fresh abandoned-checkout snapshot; `CustomerPhoneService.getCurrentPhone` returns only the active phone for that resolved Customer.
- Stripping all non-digits from the active `CustomerPhone.phone` is the required canonical outbound recipient representation.

### Unresolved Issues

The unrelated conversation-turn scheduling, voice-workflow fixture, and observability startup failures remain as detailed in Attempt 2 Validation Results. The current task's focused suites, default suite with stale `TEST_DATABASE_URL`, disposable translation-enum suite, build, Prisma validation and diff check pass.

### Architectural Concerns

None within this task's bounded missing-recipient prerequisite. Durable per-attempt recipient snapshots and checkout-update re-entry remain with their separately assigned ARCH-028 tasks.

## Architect Review

### Review Status

Changes Requested — Attempt 1 (2026-10-09).

### Review Notes

Reviewed the uploaded ARCH-028-BACKGROUND-007 workspace snapshot, task definition, parent ARCH-028 architecture, implemented recipient flow and focused regressions. Verified implementation commit `fcd7dfe63471458ca14734e3de4083b38f0b7754` and parent task report commit `c563f3fab5986041db07cbc032e4e84e69281b46` on their corresponding task branches. The missing-recipient functionality is architecturally conforming: fresh checkout -> Shop-scoped Customer/current `CustomerPhone` -> digits-only initial destination; `deferred-no-recipient` is returned before `CheckoutRecovery`, attempt, billing or provider work. Current candidate cleanup, idempotency and production test-recipient restrictions are retained. No source correction is requested for the recipient workflow itself.

**A1-R1 — Ensure PostgreSQL tests use the existing disposable harness (test-infrastructure correction and validation required).**

`moda-interact-background/package.json` currently runs `npm test` as bare `vitest run`; `vitest.config.ts` includes `tests/integration/**`. `tests/integration/translation-enum-bindings.integration.test.ts` is enabled whenever ambient `TEST_DATABASE_URL` is present, without requiring `MODA_DISPOSABLE_INTEGRATION=1`; four cases consequently attempted `localhost:5432` and failed. In contrast, `scripts/test-integration.mjs` already provisions disposable `pgvector/pgvector:pg17` through `@modainteract/moda-interact-shared/testing/node` and passes the disposable marker to the Vitest child, but its default selected suites omit translation-enum bindings.

Make the repository's default test path safe: no PostgreSQL integration should execute against an ambient persistent/local/remote `TEST_DATABASE_URL` unless the explicit disposable integration harness has established its managed database. Prefer a central Vitest collection boundary between normal/default tests and explicitly launched disposable integration (preserving the existing broad default unit/source test coverage); also gate the translation-enum tests on the approved disposable marker. Include that suite in the existing disposable harness's default list, without adding another PostgreSQL provisioning framework or weakening the actual DB assertions. Demonstrate `npm test` with a stale/unreachable `TEST_DATABASE_URL` cannot attempt `localhost:5432` and that `npm run test:integration` executes the four translation-enum cases on a newly provisioned disposable PostgreSQL 17 database, with cleanup afterward. The harness must retain safe temporary credentials/ports and must not target the configured Render/remote database.

**A1-R2 — Completion Report lacks required launcher-resolved worktree evidence (report/evidence correction required).**

The report provides pushed commits and says task worktrees are clean, but omits the canonical primary workspace root, launcher-resolved *both* physical task-worktree paths, parent/implementation task branches, preparation/synchronization with remote task branches and `origin/main`, recursive submodule synchronization status and attempt claim evidence. Restore those facts from the actual prepared launcher packet and record them in the Completion Report. A clean checkout or pushed commit is not sufficient proof of physical isolation. If execution used the shared checkout or another task's worktree, restore the canonical task worktrees, check out the already-pushed task branch there, rerun required validation and correct the report; do not create code churn only to manufacture a new commit.

**A1-R3 — Disposition of unrelated full-suite failures (verification/report correction, not feature refactor).**

The submitted `npm test` reported 1,922 passes / 40 skips / 9 failures: four PostgreSQL connection failures covered by A1-R1, three voice-workflow `job.opts` fixture failures, and two observability load-time timeouts. `npm run test:unit` also reported four observability timeouts; the observability file passed ten tests alone. After isolating integration tests, rerun the required task tests and provide precise before/after or known-baseline evidence to distinguish any remaining failures from task regressions. Do not modify unrelated voice/observability runtime behavior or mask their failures solely to obtain a green report. If a new regression is found, return it to the owning task/review path; if proven pre-existing, retain its specific unresolved evidence and identify the relevant baseline or follow-up owner. Nine npm audit findings are disclosed, not silently treated as resolved.

### Reviewed Files

- `src/services/checkout-recovery/recovery-recipient-resolver.service.ts`
- `src/services/checkout-recovery/recovery-materialization.service.ts`
- `src/services/checkout-recovery/recovery-initiation.service.ts`
- `src/services/checkout-recovery.service.ts`
- `src/workers/pending-recovery-candidate.worker.ts`
- `src/services/customer.service.ts`, `src/services/customer.phone.service.ts`
- `tests/unit/services/matured-candidate.materialization.test.ts`
- `tests/unit/services/checkout-recovery/recovery-materialization.service.test.ts`
- `tests/unit/services/checkout-recovery/recovery-initiation.service.test.ts`
- `tests/integration/translation-enum-bindings.integration.test.ts`
- `scripts/test-integration.mjs`, `vitest.config.ts`, `package.json`
- parent architecture, task definition, Completion Report and applicable worktree policy.

### Validation Reviewed

The implementing agent reports focused recipient/materialization/initiation tests 55 passed; build, Prisma generation, `git diff --check` passed; repository tests failed as recorded above. Source, test assertions and script configuration were independently inspected. The reviewer did not rerun the npm suites or disposable database tests in this environment (Node v22 without installed repository packages or Docker). The test routing correction must be validated by `moda_background` using the repository's declared Node toolchain and disposable services.

### Architecture Conformance

Recipient flow is conforming within BACKGROUND-007's bounded business scope. The current PostgreSQL test collection and missing mandatory worktree evidence prevent formal acceptance. Existing ARCH-025 baseline documentation records the same translation-enum localhost failure identities on historical commits, but that precedent does not justify continuing to run tests against a non-disposable endpoint. BACKGROUND-005 and BACKGROUND-012 remain gated until this task is accepted Complete.

### Follow-up

Return the **same** `ARCH-028-BACKGROUND-007` task to `ready`, clear its execution claim, retain `attempt: 1` and have `moda_background` perform the bounded test-routing/evidence correction on Attempt 2. Run focused recipient tests, both normal and disposable integration validation as applicable, build, Prisma validation and diff check; publish the mirrored task branches and resubmit. Do not start BACKGROUND-005 or BACKGROUND-012, modify other service business code, or create/update any `docs/decisions/**/_index.md` file before user-requested final reconciliation.
