---
id: ARCH-035-BACKGROUND-001
architecture_id: ARCH-035
title: Consume Woo checkout capture jobs safely
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 62
executor: null
claimed_at: null
attempt: 3
depends_on: [ARCH-035-API-008, ARCH-035-WOOCOMMERCE-007]
enables: [ARCH-035-SYSTEM-TEST-002]
created: 2026-10-11
updated: 2026-10-21
---

# ARCH-035-BACKGROUND-001: Consume Woo checkout capture jobs safely

## Architecture

- Architecture: `ARCH-035`; document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`.
- Coordinator: `moda_architect`; baseline: `moda-interact-workspace(20261018-121025).zip`, revised 2026-10-20.
- Former task was superseded under the UI-only revision; this definition reopens only the explicitly approved **capture-only** scope. The supplied 2026-10-21 task-worktree snapshot records developer execution at Attempt 1; live Git branch publication and launcher worktree synchronization are not independently established by this snapshot.

## Objective

Introduce a Woo-specific checkout job consumer that validates enqueued checkout snapshots without triggering recovery workflows.

## Context

The current checkout.worker.ts consumes only published Shopify contracts and immediately invokes CheckoutRecoveryService. Adding Woo events to Shopify queues would be unsafe. This task is a capture-only queue consumer, not recovery materialisation.

## Scope

- Add a narrow Woo checkout worker/handler using existing Redis/BullMQ connections and worker lifecycle.
- Consume only API-008 Woo checkout queue and schemaVersion/kind; validate shop identity and bounded snapshots at the consumer boundary.
- Emit structured, non-sensitive accepted/ignored/failed processing outcomes and existing instrumentation, and permit normal retry of transient faults.
- Wire the worker to existing Background bootstrap without changing Shopify checkout worker behaviour.

## Out of Scope

- Customer WhatsApp opt-in/consent forms, permission evidence or allowlist management.
- Recovery materialisation, scheduling, outreach, WhatsApp, AI, charging or offer selection.
- New Woo activity receipts/lineage tables, new Shared contracts or Shopify-event impersonation.
- Changes to another repository or any `docs/decisions/**/_index.md` file.
- CheckoutRecoveryService calls, pending recovery candidates, GraphQL checkout lookup, recovery materialisation, billing, WhatsApp, or permanent event history.

## Requirements

- Job validation must be independent from Shopify parser and reject malformed/unknown schema versions.
- No DB writes merely to acknowledge capture; after successful consumption the job is not a future replay source.
- Do not import Shopify checkout adapters or call recovery pipeline as a side effect.
- A retryable infrastructure failure must fail the job rather than be swallowed; operator failure visibility through existing BullMQ facilities.

## Work Items

- [x] Implement small Woo checkout job consumer + bootstrap wiring.
- [x] Add tests proving valid checkout event is processed once per retained job and invalid event fails safely.
- [x] Regression-test existing Shopify queues and worker start-up (Shopify contract adapter and entrypoint isolation tests; real Redis integration checks Shopify queue isolation).

## Interfaces / Contracts

**API-owned `woo.activity.v1` contract** (published as strict OpenAPI + integration fixtures, not a new Shared package in this bounded scope):

```json
{
  "schemaVersion": "woo.activity.v1",
  "eventId": "stable-opaque-event-id",
  "eventType": "CHECKOUT_UPDATED",
  "checkoutKey": "stable-shop-scoped-key",
  "occurredAt": "2026-10-20T12:00:00.000Z",
  "checkout": { "currency": "GBP", "total": "29.99", "items": [] }
}
```

`eventType` is one of `CHECKOUT_UPDATED`, `ORDER_PLACED`, `ORDER_PAID`, `ORDER_CANCELLED`. For orders, use an `order` object with `orderId`, status and same `checkoutKey`; `checkout` is absent. A Woo producer sends no shop ID: API resolves Shop from installation credentials. Bounded customer/contact fields and line-item fields must be explicitly defined in the authoritative API schema; omit unavailable fields rather than fabricating them. Correlation key is `(authenticated shopId, checkoutKey)`. Stable `eventId` is retained on retries of the **same emitted event**; later genuine updates use a new `eventId`.

The hosted API owns `POST /v1/woocommerce/activity`. Checkouts are implemented by API-008; order event types are enabled by API-019 on the same route. Queue payloads retain `schemaVersion`, authenticated `shopId`, event identity, kind, checkout key and bounded validated snapshot. Background must validate the queued payload again and must **not** call the Shopify event parser. These contracts are specific to this API/Background integration; if a published cross-service primitive becomes necessary, stop and return the new ownership requirement to the architect rather than implement a competing Shared module.

## Dependencies

- `ARCH-035-API-008` — must be Complete and accepted before claiming.
- `ARCH-035-WOOCOMMERCE-007` — must be Complete and accepted before claiming.

## Enables

- `ARCH-035-SYSTEM-TEST-002`

## Acceptance Criteria

- [x] Woo checkout jobs are routed only to Woo consumer.
- [x] No CheckoutRecovery row, pending candidate, credit usage or messaging side effects in the inspected capture-only worker path.
- [x] Invalid payload fails visibly; safe structured logs include bounded identifiers but not customer payloads.
- [x] Shopify checkout worker unaffected (distinct queue/worker, focused regression tests and Redis queue isolation).

## Validation

- [x] Focused unit/regression tests **27/27 PASS** and real Redis/BullMQ worker integration **1/1 PASS** in the fresh post-gitlink-correction run on 2026-10-21. Earlier test-only correction evidence remains recorded below.
- [x] Background `npm run lint` and `npm run build` (Prisma client generation and TypeScript compilation) passed in the post-correction run. Focused Shopify contract-adapter and entrypoint regressions passed; the full unrelated Shopify inventory was not rerun.
- [x] `git diff --check` and `git diff --cached --check` passed; final worktree is clean and the branch-level `database` gitlink diff is empty. No database migration was introduced.

## Stop Condition

After work items, acceptance criteria and required validation are satisfied, finish the Completion Report, transition the task to `review`, return it to `moda_architect`, and STOP. Do not proceed to enabled tasks.

## Implementation Notes

Do not register a second competing Worker on the same queue as the order worker: use the two Woo-specific queue boundaries published by API-008 and API-019. Only record an operation-level observation; future Woo recovery will need separate scoped tasks for current checkout state and existing candidate integration.

## Completion Report

### Status

**Attempt 3 developer self-review passed; awaiting explicit developer completion and architect review (2026-10-21).** Attempt 1 and Attempt 2 Changes Requested remain preserved below. The developer removed the unrelated database gitlink advance in implementation commit `40250184c1cfe1777d4541d49d7135036c9b8192`, reran all required validation, and independently verified the implementation diff, clean/synchronized branch and dependencies during this review. The task is in `review`; no architect acceptance or task completion is implied.

Attempt 3 remains the active reviewed attempt (`attempt: 3`); its executor and claim timestamp are cleared as required for review. The focused unit/regression suite passed 27/27, the real Redis/BullMQ integration passed 1/1, lint/build and whitespace checks passed, and both required dependencies resolve `complete`. The task remains developer-completion-owned and requires explicit completion before any downstream task proceeds.

### Files Changed

Implementation repository: `moda-interact-background/`. Files supplied in the implementation patch plus the worker-test correction:

- `src/entrypoints/shopify-event.ts`
- `src/events/woo-checkout-capture.ts`
- `src/index.ts`
- `src/observability/queue-performance.ts`
- `src/observability/worker-metrics.ts`
- `src/workers/woo-checkout-capture.worker.ts`
- `tests/integration/woo-checkout-capture.integration.test.ts`
- `tests/unit/events/woo-checkout-capture.test.ts`
- `tests/unit/runtime/entrypoint-isolation.test.ts`
- `tests/unit/workers/woo-checkout-capture.worker.test.ts`

No schema migration, Shared contract or `docs/decisions/**/_index.md` change was included in these patches. Subsequent corrective commit `4025018` restores only the Background repository's `database` submodule gitlink to its baseline; it makes **no net database gitlink change** relative to `origin/main` and does not modify database repository history.

### Work Completed

- Added a Woo-specific validator for API-008 `woo.activity.v1` / `checkout-updated` jobs in the `woo-checkout-capture-v1` queue. It validates the authenticated `shopId`-bound job ID, SHA-256 content digest, schema version and bounded checkout/customer fields without using the Shopify parser.
- Added a dedicated BullMQ worker that observes and acknowledges valid checkout capture events. Invalid or tampered jobs fail visibly through BullMQ, with bounded structured logging and no recovery, candidate, billing, WhatsApp or database-write execution path.
- Registered the worker with existing Background entrypoint and worker-metrics/queue-performance instrumentation; the Shopify checkout worker remains independent.
- Added parser, worker, entrypoint isolation and disposable real Redis/BullMQ integration tests covering acceptance, duplicate job identity, invalid digest retries and isolation from the Shopify checkout queue.
- Corrected one worker unit-test assertion after it incorrectly matched the word `billing` in a comment. The correction excludes comments when checking executable source and does **not** change production runtime code.
- Resolved the sole outstanding Attempt 2 scope issue: restored the Background task branch's `database` gitlink from `807af3393f992c8a19bc9ef278d7e7e05f41799d` to `caee3df61dbb38c8319ebcd3cfaf68522743245e` and published `40250184c1cfe1777d4541d49d7135036c9b8192`. This did not change the Woo capture worker or rewrite/delete the database submodule history.

### Validation Results

Evidence is recorded chronologically. The Attempt 1 checks passed, and Attempt 2 added no fresh test results. **After the gitlink correction on 2026-10-21**, the developer reran the focused tests, real Redis/BullMQ integration, lint, build and whitespace checks. The correction was committed and pushed as `40250184c1cfe1777d4541d49d7135036c9b8192`; the subsequently supplied read-only Git output verifies the worktree and remote are synchronized. The earlier failed scope review remains historical evidence, not a current blocker.

| Command / check | Observed result |
| --- | --- |
| Attempt 1 focused Vitest command (same four files as below) | **PASS 27/27** on the then-current implementation worktree; see Attempt 1 review history. |
| `npm run test:integration -- tests/integration/woo-checkout-capture.integration.test.ts` | **PASS 1/1** real Redis/BullMQ integration. Valid event completed; invalid digest failed on both configured attempts; Shopify checkout queue unaffected. |
| `npm run lint` | **PASS**, ESLint reported no errors. |
| `npm run build` (`npm run prisma:generate && tsc`) | **PASS**, Prisma Client v6.19.3 generated and TypeScript compilation completed without errors. |
| Attempt 1 `git diff --check` | **PASS** for the then-current implementation worktree. |
| Canonical task branch/publication check (Attempt 1) | **BLOCKED at that review**: local task branch pointed to `origin/main`; source changes were uncommitted. This finding was corrected before Attempt 2. |
| Canonical task branch/publication check (Attempt 2) | **PASS for isolation/publication**: implementation worktree is clean at `eab139058ab851da9ad0b2932ee2c8134f199687`, matching `origin/task/ARCH-035-BACKGROUND-001` and containing `origin/main`. The task diff still contains the out-of-scope database gitlink advance, so scope correction is not complete. |
| Attempt 2 focused tests, integration, lint, build, whitespace | **NOT RUN during Attempt 2**: this is a historical review fact. Fresh tests were subsequently rerun after the pointer correction. |
| Post-correction `npx vitest run tests/unit/events/woo-checkout-capture.test.ts tests/unit/workers/woo-checkout-capture.worker.test.ts tests/unit/runtime/entrypoint-isolation.test.ts tests/unit/events/shopify-contract-adapter.test.ts` | **PASS 27/27** across four files: parser 3/3; worker 4/4; entrypoint isolation 10/10; Shopify adapter 10/10. |
| Post-correction `npm run test:integration -- tests/integration/woo-checkout-capture.integration.test.ts` | **PASS 1/1**, real Redis/BullMQ. Valid API-shaped checkout was accepted; malformed content digest failed on two attempts as intended. No recovery, billing, or messaging side effects. |
| Post-correction `npm run lint` | **PASS**, ESLint completed without reported errors. |
| Post-correction `npm run build` | **PASS**, `prisma generate` (v6.19.3) then `tsc` completed. |
| Post-correction `git diff --check` and `git diff --cached --check` | **PASS** after the gitlink pointer correction was staged. |
| Final implementation Git confirmation | **PASS**: HEAD and `origin/task/ARCH-035-BACKGROUND-001` both `40250184c1cfe1777d4541d49d7135036c9b8192`; `git status --porcelain` empty; `git diff origin/main...HEAD -- database` empty. |
| Database gitlink baseline | `caee3df61dbb38c8319ebcd3cfaf68522743245e`; unrelated `807af33...` pointer removed from the net task diff without altering database repository history. |
| Migration / Shared contract | None introduced by this implementation. |

### Deviations

- The initial worker test erroneously matched a prohibited word in an explanatory comment. A test-only correction was applied, and the affected worker suite passed 4/4 on rerun.
- Focused Shopify checkout adapter and entrypoint regressions were run; there is no claim that every unrelated Shopify test suite was rerun.

### Assumptions

- API-008 remains the authoritative producer of the authenticated `woo.activity.v1` checkout capture job; Background validates the queued job independently.
- Both the earlier task branch-topology problem and the unrelated gitlink change have been resolved. The canonical implementation branch is clean and tracks its matching remote at `40250184c1cfe1777d4541d49d7135036c9b8192`; the earlier untracked terminal recording is no longer present.
- Capture consumption is observation-only rather than durable archival; later recovery functionality remains separately owned.

### Unresolved Issues

- **No outstanding implementation or test correction is identified by the supplied post-correction evidence.** The Attempt 2 gitlink issue is resolved by commit `4025018`, the required fresh validation passed, and the implementation worktree is clean and synchronized.
- **Workflow gate:** Attempt 3 claim and passing developer self-review are recorded. Explicit developer completion and architect acceptance remain pending; this self-review does not mark the task complete or authorize an enabled task.
- The historical source task noted the absence of a newer workspace containing `ARCH-040-DATABASE-006`. No change to that schema or ARCH-040 code is required by this capture-only task.

### Architectural Concerns

Capture-only is not permanent event archiving. Completed BullMQ jobs can expire; future recovery enablement must consider that captured past events may be unavailable.

## Execution Ownership Amendment

Developer execution was explicitly requested for this task. The task remains
assigned to `moda_background`; execution ownership is changed from the
automatic agent path to the developer path for this attempt.

- Previous execution mode: `agent`
- Previous completion mode: `automatic`
- New execution mode: `developer`
- New completion mode: `developer`
- Amendment date: 2026-10-21

## Architect Review

### Review Status

Pending architect review. Developer Self-Review — Changes Requested (Attempt 1) is recorded below; no architect acceptance is implied.

### Review Notes

Scope reopened from Superseded only for the 20 October 2026 WooCommerce checkout/order capture exception. Historical supersession remains in Git. No architectural acceptance of implementation is implied.

### Reviewed Files

None.

### Validation Reviewed

Not reviewed by the architect. Focused developer self-review validation results and publication limitations are recorded above.

### Architecture Conformance

Not evaluated by the architect. The developer self-review found the implementation scope capture-only, but cannot accept it while the implementation is unpublished, the task worktree tracks `origin/main`, and unrelated/unexplained dirty paths prevent safe publication.

### Follow-up

Resolve the out-of-scope database gitlink delta and rerun focused validation before the next developer self-review. Attempt 1 branch/upstream and untracked-path issues are resolved.

## Developer Self-Review - Changes Requested

**Reviewed 2026-10-21T14:17:54Z, Attempt 1.** The task's focused behavior checks pass on the current implementation worktree: unit/regression suite 27/27, real Redis/BullMQ integration 1/1, ESLint, TypeScript build, and `git diff --check`. The task's three Work Items and four Acceptance Criteria are implemented in the current source tree. However, the implementation is not durably attributable to the task branch: the canonical worktree's `task/ARCH-035-BACKGROUND-001` is configured to track `origin/main`, has the same commit as `origin/main` (`c5e6da4`), and there is no `origin/task/ARCH-035-BACKGROUND-001`; the implementation and test files remain uncommitted. The worktree also contains a database gitlink change (`caee3df` to `807af33`) whose submodule includes unrelated ARCH-040 diagnostics changes, plus an unexplained untracked root `typescript` file. These were not modified or discarded.

Required, testable corrections before resubmitting:

1. Restore valid isolation/publication for the canonical implementation worktree: ensure `task/ARCH-035-BACKGROUND-001` is based on the appropriate task/mainline history and tracks `origin/task/ARCH-035-BACKGROUND-001`; preserve the current task changes while doing so. Do not switch/reset a shared checkout or force-push.
2. Identify and preserve the owner/source of the changed `database` gitlink and untracked `typescript` file. Exclude both from BACKGROUND-001 unless an architect-approved scope change establishes they belong here; do not delete or revert them as part of the correction.
3. Commit and push only the intended BACKGROUND-001 implementation and test files on the correct implementation task branch, then verify both canonical worktrees are clean and synchronized and update the report with the resulting commit evidence.
4. After branch/scope correction, rerun the focused unit/regression and real Redis integration tests, lint, build, and whitespace check against the committed task branch.

Transition: `status: ready`, `executor: null`, `claimed_at: null`, `attempt: 1` (unchanged). The next developer claim may begin Attempt 2; no claim is created by this review.

## Developer Claim — Attempt 2

**Claimed — 2026-10-21T14:45:20Z.** The developer invoked `/moda_developer_create ARCH-035-BACKGROUND-001` after Attempt 1 Changes Requested. The task transitioned from `ready`, Attempt 1, null executor to `in_progress`, Attempt 2, `executor: developer`. `execution_mode: developer`, `completion_mode: developer`, and `assigned_agent: moda_background` remain unchanged.

- Dependency gate: `ARCH-035-API-008` and `ARCH-035-WOOCOMMERCE-007` both resolve `complete` through the canonical launcher.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-BACKGROUND-001`, branch `task/ARCH-035-BACKGROUND-001`, clean before claim; contains current `origin/main` via merge `35c339c8c`. Before this claim/report commit, the branch was 27 commits ahead of its remote.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-BACKGROUND-001`, branch `task/ARCH-035-BACKGROUND-001`, clean before claim at `eab139058ab851da9ad0b2932ee2c8134f199687`, matching `origin/task/ARCH-035-BACKGROUND-001` and containing current `origin/main`.
- Correction focus: resolve the unrelated database gitlink advance `caee3df` -> `807af33` without modifying or discarding database submodule history, then rerun focused tests, integration, lint, build and whitespace checks on the corrected task branch. No feature implementation changes were made as part of this claim.

## Developer Self-Review - Changes Requested

**Reviewed 2026-10-21, Attempt 2.** The parent and implementation task worktrees are clean and synchronized with their matching task remotes. Both required dependencies resolve `complete`. The implementation branch remains at `eab139058ab851da9ad0b2932ee2c8134f199687`; no implementation commit or fresh validation evidence was added during Attempt 2. Inspection of the branch diff against `origin/main` confirms that the database gitlink still advances from `caee3df61dbb38c8319ebcd3cfaf68522743245e` to `807af3393f992c8a19bc9ef278d7e7e05f41799d`, an unrelated ARCH-040 change outside this task. Review is **Changes Requested**.

Required, testable corrections before resubmitting:

1. Remove the unrelated database gitlink change from the BACKGROUND-001 task diff by restoring the task branch pointer to the appropriate baseline. Do not delete, reset, or rewrite the database submodule's own work/history; verify `git diff origin/main...HEAD -- database` is empty afterward.
2. Rerun the focused unit/regression command, real Redis/BullMQ integration test, `npm run lint`, `npm run build`, and `git diff --check` from the canonical implementation worktree after the correction; record actual results and commit evidence.
3. Confirm the canonical implementation task branch is clean and matches its remote, then update the Completion Report to describe the corrected task diff and current validation evidence.

Transition after Attempt 2 review: `status: ready`, `executor: null`, `claimed_at: null`, `attempt: 2` (unchanged). The following developer claim begins Attempt 3.

## Developer Claim — Attempt 3

**Claimed — 2026-10-21T15:24:33Z.** The developer invoked `/moda_developer_create ARCH-035-BACKGROUND-001` from the canonical `ready` state after the Attempt 2 Changes Requested corrections were completed and documented. The task transitioned to `in_progress`, Attempt 3, `executor: developer`; `execution_mode: developer`, `completion_mode: developer`, and `assigned_agent: moda_background` remain unchanged.

- Dependency gate: `ARCH-035-API-008` and `ARCH-035-WOOCOMMERCE-007` both resolve `complete` through the canonical launcher.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-BACKGROUND-001`, branch `task/ARCH-035-BACKGROUND-001`, clean after merge of current `origin/main` at `87b25134e`; claim/report commit will publish this synchronization.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-BACKGROUND-001`, branch `task/ARCH-035-BACKGROUND-001`, clean and matching its remote at `40250184c1cfe1777d4541d49d7135036c9b8192`, containing current `origin/main`.
- Correction evidence: `4025018` restores the database gitlink from `807af33` to baseline `caee3df`; `git diff origin/main...HEAD -- database` is empty. The task diff contains only the ten intended Background source/test files; the unexplained root `typescript` path is absent.
- Post-correction validation has already been run and recorded above: focused unit/regression 27/27, Redis/BullMQ integration 1/1, lint, build, `git diff --check`, and `git diff --cached --check` passed. This create step performs no implementation edits.

## Developer Self-Review - Passed

**Reviewed 2026-10-21, Attempt 3.** Reviewed the capture parser, worker, and focused parser/worker/Redis integration tests. The consumer validates the API-owned `woo.activity.v1` checkout job at the queue boundary, verifies shop-bound deterministic job identity and payload digest, and rejects malformed or unexpected fields. The worker is capture-only, uses bounded structured logs and existing telemetry, and propagates invalid jobs to BullMQ; no recovery, database, billing, or WhatsApp execution path was found. The Shopify queue remains isolated.

Fresh validation from the canonical implementation worktree:

| Command / check | Observed result |
| --- | --- |
| Focused Vitest run for Woo parser/worker, entrypoint isolation and Shopify contract adapter | **PASS 27/27** across four files. |
| `npm run test:integration -- tests/integration/woo-checkout-capture.integration.test.ts` | **PASS 1/1**, real Redis/BullMQ integration; valid job completed, duplicate job identity was stable, invalid digest failed after two attempts, and the Shopify queue remained empty. |
| `npm run lint` | **PASS**. |
| `npm run build` | **PASS**, Prisma client generation and TypeScript compilation. |
| `git diff --check` and `git diff --cached --check` | **PASS**. |
| Implementation branch and scope | **PASS**: `HEAD` and `origin/task/ARCH-035-BACKGROUND-001` both `40250184c1cfe1777d4541d49d7135036c9b8192`; worktree clean; ten intended source/test paths only; no database gitlink diff; no root `typescript` path. |
| Parent task branch | **PASS** before this report update: clean and synchronized at `a63b8ae2a50fcd3030299198341b12445dbb77c6`, with current `origin/main` included. |
| Dependencies | **PASS**: `ARCH-035-API-008` and `ARCH-035-WOOCOMMERCE-007` both resolve `complete`. |

Review outcome: **Passed**. The task transitions to `status: review`, with `executor: null`, `claimed_at: null`, and `attempt: 3` unchanged. Completion mode remains `developer`; explicit developer completion and architect review are still required. No implementation changes, merge to main, or downstream task execution were performed as part of this self-review.
