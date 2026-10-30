---
id: ARCH-053-BACKGROUND-001
architecture_id: ARCH-053
title: Carry validated restoration evidence through Woo candidates
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
attempt: 1
depends_on:
- ARCH-053-SHARED-002
enables:
- ARCH-053-BACKGROUND-002
- ARCH-053-WOOCOMMERCE-001
created: 2026-10-29
updated: 2026-10-30
---

# ARCH-053-BACKGROUND-001 — Carry validated restoration evidence through Woo candidates

## Architecture

Architecture ID: `ARCH-053`. Document: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Coordinator: `moda_architect`. Materialised and accepted Complete at Attempt 1. Parent and implementation task branches are published; no producer deployment is claimed.

## Objective

Carry validated restoration evidence through Woo candidates. One bounded outcome in `moda-interact-background` owned by `moda_background`.

## Context

The inspected snapshot is dated 2026-10-30 07:59. ARCH-052 owns dynamic discount discovery and is not a checkout-URL implementation domain. ARCH-048-BACKGROUND-007..011 task files are present, but none has been accepted Complete in this snapshot (007 Ready, 008–011 Pending). This task is **Pending** from the snapshot/dependency inventory, subject to fresh launcher re-gating.

## Scope

- Change `src/events/woo-checkout-capture.ts` to accept the **additive optional** `checkout.restoration` in the existing `woo.activity.v1` BullMQ job using published `WooCartRestoreSnapshotV1Schema` (all other strict fields, job name, ID and canonical JSON digest behaviour unchanged).
- Change `src/services/woocommerce-recovery/contracts.ts`, `woo-checkout-activity.service.ts`, `woo-checkout-activity.adapters.ts` and the candidate queue/index adapter only as necessary to retain the entire verified `restoration` field on newest nonempty candidate, replacing it alongside basket items and timestamp when newer snapshot arrives.
- Update the test suite for validation, dedupe, stale events, same-second ambiguity, empty baskets and candidate overwrite; no new queue.

## Out of Scope

No PostgreSQL insert, no Woo plugin PHP or API route, no candidate maturity admission or URL issuance, no ARCH-048 generation-state reimplementation.

No execution of Enabled tasks, unrelated cross-repository implementation, extra database objects or new generic logger.

## Requirements

- No reconstruction from `lineItems` or from SKU/title; no fabricated restoration on old/absent events. `checkout.restoration` absent => unknown; unsupported => persist explicit unsupported evidence. Fingerprint with coupon change produces a distinct validated event only when API supplied it.
- A stale delivery may never overwrite a newer candidate's coupons, variation attributes or snapshot readiness. Preserve identity `(shopId,checkoutToken)` until generation support from ARCH-048. Maintain established upper bounds and reject digest mismatches.
- Do not create recovery records, issue URLs or alter billing/outreach in this task.

### Mandatory workflow/security invariants

- Inspect `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/developer-task-workflow.md`, `docs/task-definition-materialization.md` and the launcher preparation evidence. Use the **dedicated, synchronized parent and implementation task worktrees**; do not operate from a shared checkout or claim a branch was pushed without evidence. Implement only the owning repository and assigned task metadata. No unrelated refactors, migrations, agent handoffs or remote pushes to `main`.
- Read the ARCH-053 parent architecture and all dependency tasks before claiming Ready. Any missing contract or incorrect owner is a blocking architect question; do not invent a local parallel schema or silently change another agent's task. System-test tasks must remain terminal.
- Never swallow unexpected errors: Node uses `@modainteract/moda-interact-shared/logging`; PHP uses the existing safe plugin diagnostics (not a competing generic Node logger). Report bounded event codes, ids and outcomes, propagate retryable failures to their owning boundary, omit tokens, full URLs, coupon codes and customer personal data from logs.
- The plugin cannot access PostgreSQL/Redis. The API cannot mutate merchant WordPress cart sessions. Background cannot directly call an unverified merchant endpoint to mint URLs. Do not enable Woo production WhatsApp sending, relax final consent/STOP/order gates, or add cross-generation outreach caps/cooldowns.

## Work Items

- [x] Use published Shared validator for nested restore field; preserve existing event envelope digest and job IDs.
- [x] Carry restoration through candidate create/update/cancel/replay and deterministic stale checks.
- [x] Add tests for no field, unsupported, coupons-only change, quantity change, delayed replay and invalid nested schema.

## Interfaces / Contracts

Queue remains `woo-checkout-capture-v1` / `checkout-updated` with **canonical `woo.activity.v1`** event wrapper + optional Shared-validated `checkout.restoration` (same value from API v1 after verified phone projection); no new version, Redis queue key or event type. Consumers of `WooPendingCandidate` obtain `candidate.basket.checkout.restoration`; missing remains unknown/unrestorable and unsupported remains unsupported. HTTP-only `canonicalPhone` and `verifiedCountryCode` must never reach the queue.

## Dependencies

- `ARCH-053-SHARED-002` (must be architect-accepted Complete)

## Enables

- `ARCH-053-BACKGROUND-002`
- `ARCH-053-WOOCOMMERCE-001`

## Acceptance Criteria

- [x] Use published Shared validator for nested restore field; preserve existing event envelope digest and job IDs.
- [x] Carry restoration through candidate create/update/cancel/replay and deterministic stale checks.
- [x] Add tests for no field, unsupported, coupons-only change, quantity change, delayed replay and invalid nested schema.
- [x] No regression in tenant isolation, historical generation preservation, valid shopper cart or consent/STOP/terminal order guards.
- [x] Tests demonstrate invalid/stale/replayed and unexpected errors do not produce silent success or malformed URLs.
- [x] No change outside assigned domain repository code plus owned task Completion Report; no ARCH-052 work.

## Validation

- [x] Background focused Woo capture parser and candidate unit tests
- [x] Background declared typecheck/lint and queue replay tests (changed-file lint passed; full lint has one unrelated existing failure documented below)
- [x] `git diff --check`

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are complete, update ONLY this task's authorised execution metadata, checklists and Completion Report, set `status: review` and return to `moda_architect`; **STOP**. Do not begin Enables, merge task branches, push `main` or change Architect Review yourself.

## Implementation Notes

The queue consumer task must be architect-accepted before the coordinated pre-production rollout of the updated API v1 validator and WooCommerce v1 producer; there is no HTTP v3 contract or second queue version. Use the shared logger, not another generic logger, for bounded validation failures.

## Completion Report

### Status

Accepted Complete at Attempt 1 by the architect.

### Files Changed

- `package.json`
- `package-lock.json`
- `src/events/woo-checkout-capture.ts`
- `tests/unit/events/woo-checkout-capture.test.ts`
- `tests/unit/services/woocommerce-recovery/woo-checkout-activity.service.test.ts`
- `tests/unit/services/woocommerce-recovery/woo-candidate-queue.service.test.ts`

### Work Completed

Pinned the Background consumer to published Shared `2.7.2` and validated the optional queue-boundary `checkout.restoration` with `WooCartRestoreSnapshotV1Schema`. The existing event wrapper, job name/ID and canonical JSON digest inputs remain unchanged.

Carried the validated snapshot as part of the complete checkout payload in the existing Woo candidate job. Newer supported/unsupported snapshots replace the prior value along with basket items and activity time; absent restoration remains absent. Added coverage for absent and invalid nested values, supported/unsupported evidence, coupon-only changes, quantity changes, queue replacement, and a delayed resumption replay that cannot overwrite a later successor snapshot. No new queue, database write, recovery record, URL issuance, or ARCH-052 behavior was introduced.

### Validation Results

- `npm ci --ignore-scripts --no-audit --no-fund`: passed using the updated lockfile; generated Prisma Client with `npm run prisma:generate`.
- `npm run build`: passed, including TypeScript compilation.
- Focused Woo parser, activity/candidate, queue adapter and capture worker tests: 4 files passed, 41 tests passed.
- `./node_modules/.bin/eslint src/events/woo-checkout-capture.ts tests/unit/events/woo-checkout-capture.test.ts tests/unit/services/woocommerce-recovery/woo-checkout-activity.service.test.ts tests/unit/services/woocommerce-recovery/woo-candidate-queue.service.test.ts`: passed.
- `npm run lint`: one existing unrelated error at `src/services/translation-reconciliation.service.ts:218` (`preserve-caught-error`). That file is unchanged from `origin/main`; changed-file lint passed.
- `git diff --check`: passed.

### Deviations

Background was still pinned to Shared `2.5.1`, which does not expose the published WooCommerce restoration schema. Updated the exact dependency and lock entry to published `2.7.2` as required to consume SHARED-002. Full-repository lint remains blocked by the unrelated existing finding recorded above; it is outside this task's files and ownership.

### Assumptions

Shared-002's completion report records `2.7.2` as registry-published with the required `@modainteract/moda-interact-shared/woocommerce` export. `npm ci` resolved that exact package and validation used its published schema.

### Unresolved Issues

None.

### Architectural Concerns

None. Candidate payload remains in the existing queue; no cross-service producer/API implementation was changed.

### Git / VCS

- Task branch: `task/ARCH-053-BACKGROUND-001`.
- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-053-BACKGROUND-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-053-BACKGROUND-001`.
- Parent and implementation worktrees were created for this task; neither shared checkout was switched or used for implementation.
- Launcher synchronization: parent remote task branch fast-forwarded `not-needed`; parent `origin/main` was already current. Implementation remote task branch fast-forwarded `not-needed`; implementation `origin/main` was already current.
- Recursive submodule sync and update-init passed. The initialized `database` submodule is at `af77c594ecbfc78c26d01c0021a090830884bbff`.
- Claim commit: `bc590be93af223a556ba8e6701c65ffdcf458b77` (launcher committed and pushed it).
- Implementation commit: `41699ba` (`feat(ARCH-053-BACKGROUND-001): retain Woo restore evidence`); pushed to `origin/task/ARCH-053-BACKGROUND-001`.
- Parent task/report branch: completion report committed and pushed to `origin/task/ARCH-053-BACKGROUND-001`. No implementation submodule gitlink is staged.
- Neither task branch was merged into `main`; no `main` branch was changed.

## Architect Review — Attempt 1 (Accepted)

### Review Status

Accepted. The implementation satisfies the bounded candidate-pipeline contract. Mark the task Complete at Attempt 1; no implementation merge or producer deployment is implied.

### Review Notes

The queue boundary uses the published strict Shared restoration schema as an optional checkout field. The existing event envelope, job identity, size limit and canonical digest calculation are preserved; restoration data participates in the digest when present. `basketFrom` carries the entire validated checkout object into the existing nonempty candidate, so newer snapshots replace prior restoration evidence, while absent restoration remains absent. The existing generation-aware watermark and queue replacement paths prevent stale events and delayed resumption replays from overwriting newer evidence. No database writes, URL issuance, new queue or ARCH-052 behavior were added.

The out-of-scope URL-safety acceptance wording is satisfied by the explicit boundary: this task does not create or format URLs. Existing invalid, stale, replay and unexpected-error behavior remains covered by the reported suite.

### Reviewed Files

Reviewed the implementation diff in `src/events/woo-checkout-capture.ts`, the queue/candidate serialization tests and the checkout-activity tests, along with the Completion Report and task scope. Candidate transport is generic and required no source changes in the queue/index adapter.

### Validation Reviewed

The Completion Report records build, 41 focused tests across four files, changed-file lint, Prisma generation and `git diff --check` passing. Full-repository lint reports one existing unrelated `preserve-caught-error` finding in unchanged `src/services/translation-reconciliation.service.ts:218`; the limitation is disclosed and changed-file lint passed. Validation was reviewed from the published report; tests were not rerun during architect review.

### Architecture Conformance

The change preserves the existing queue and candidate identity, uses only published Shared validation, and does not cross Background ownership into persistence, URL issuance or WooCommerce producer work. The task's dependency on SHARED-002 is Complete.

### Follow-up

Promote BACKGROUND-002 to Ready because its explicit dependencies BACKGROUND-001 and DATABASE-001 are Complete. WOOCOMMERCE-001 remains Pending because API-001 is still Ready, not Complete. No consumer deployment or production activation is authorized by this acceptance.
