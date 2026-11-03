---
id: ARCH-053-BACKGROUND-002
architecture_id: ARCH-053
title: Persist immutable restore snapshot at Woo recovery admission
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 35
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-053-BACKGROUND-001
- ARCH-053-DATABASE-001
enables:
- ARCH-053-BACKGROUND-003
created: 2026-10-29
updated: 2026-10-30
---

# ARCH-053-BACKGROUND-002 — Persist immutable restore snapshot at Woo recovery admission

## Architecture

Architecture ID: `ARCH-053`. Document: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Coordinator: `moda_architect`. **Portable canonical task: defined but not materialised**; no Git branch, worktree, commit, push, review or producer deployment claimed.

## Objective

Persist immutable restore snapshot at Woo recovery admission. One bounded outcome in `moda-interact-background` owned by `moda_background`.

## Context

The inspected snapshot is dated 2026-10-30 07:59. ARCH-052 owns dynamic discount discovery and is not a checkout-URL implementation domain. ARCH-048-BACKGROUND-007..011 task files are present, but none has been accepted Complete in this snapshot (007 Ready, 008–011 Pending). This task is **Pending** from the snapshot/dependency inventory, subject to fresh launcher re-gating.

## Scope

- Modify `src/services/woocommerce-recovery/woo-recovery-admission.service.ts` and `woo-recovery-admission-evidence.ts` and targeted repository tests, *not* checkout-candidate scheduling or worker composition.
- In the existing transaction that creates `CheckoutRecovery`, write the validated latest candidate `checkout.restoration` to `wooRestoreSnapshot` as Prisma JSON, or `null` when absent; preserve `lineItems` display projection, original total and customer identity exactly as before.
- Reuse ARCH-048's existing generation selection once available: evidence is immutable per `(shopId,checkoutToken,generation)` and never copied onto another generation when a duplicate or stale candidate matures.

## Out of Scope

No link token creation, `checkoutUrl` mutation, Woo PHP/API routing, new status values, generation policy or outreach changes.

No execution of Enabled tasks, unrelated cross-repository implementation, extra database objects or new generic logger.

## Requirements

- No snapshot guessed from productId-only lineItems and no partial coupon truncation. Supported snapshot is complete; unsupported snapshot remains explicit JSON but cannot produce a link. No update to previously admitted row's historical items/coupons.
- Ensure unique-generation conflict/retry returns the original recovery without replacing its snapshot. New-generation admission must read **new** candidate evidence, not old generation's lineItems.
- Preserve existing consent/STOP/customer matching, order evidence, transaction lock and no Redis/network operations within database transaction.

### Mandatory workflow/security invariants

- Inspect `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/developer-task-workflow.md`, `docs/task-definition-materialization.md` and the launcher preparation evidence. Use the **dedicated, synchronized parent and implementation task worktrees**; do not operate from a shared checkout or claim a branch was pushed without evidence. Implement only the owning repository and assigned task metadata. No unrelated refactors, migrations, agent handoffs or remote pushes to `main`.
- Read the ARCH-053 parent architecture and all dependency tasks before claiming Ready. Any missing contract or incorrect owner is a blocking architect question; do not invent a local parallel schema or silently change another agent's task. System-test tasks must remain terminal.
- Never swallow unexpected errors: Node uses `@modainteract/moda-interact-shared/logging`; PHP uses the existing safe plugin diagnostics (not a competing generic Node logger). Report bounded event codes, ids and outcomes, propagate retryable failures to their owning boundary, omit tokens, full URLs, coupon codes and customer personal data from logs.
- The plugin cannot access PostgreSQL/Redis. The API cannot mutate merchant WordPress cart sessions. Background cannot directly call an unverified merchant endpoint to mint URLs. Do not enable Woo production WhatsApp sending, relax final consent/STOP/order gates, or add cross-generation outreach caps/cooldowns.

## Work Items

- [x] Write `wooRestoreSnapshot` transactionally at admission without changing display `lineItems`.
- [x] Test supported, unsupported, absent, stale and simultaneous admissions, plus subsequent generation snapshot separation.
- [x] Record exact Prisma dependency version and required submodule update in Completion Report.

## Interfaces / Contracts

Source `WooPendingCandidate.basket.checkout.restoration` from BACKGROUND-001; column from DATABASE-001; parser from published Shared. No change to public API or queue. `null` means unknown; unsupported JSON means known-unrestorable.

## Dependencies

- `ARCH-053-BACKGROUND-001` (must be architect-accepted Complete)
- `ARCH-053-DATABASE-001` (must be architect-accepted Complete)

## Enables

- `ARCH-053-BACKGROUND-003`

## Acceptance Criteria

- [x] Write `wooRestoreSnapshot` transactionally at admission without changing display `lineItems`.
- [x] Test supported, unsupported, absent, stale and simultaneous admissions, plus subsequent generation snapshot separation.
- [x] Record exact Prisma dependency version and required submodule update in Completion Report.
- [x] No regression in tenant isolation, historical generation preservation, valid shopper cart or consent/STOP/terminal order guards.
- [x] Tests demonstrate invalid/stale/replayed and unexpected errors do not produce silent success or malformed URLs; this task leaves `checkoutUrl` null and does not create links.
- [x] No change outside assigned domain repository code plus owned task Completion Report; no ARCH-052 work.

## Validation

- [x] Focused Background admission test suite with mocked and Postgres-backed transaction where available
- [x] Package-defined build/typecheck; `git diff --check`
- [x] Adversarial stale/duplicate candidate case and no external network within transaction

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are complete, update ONLY this task's authorised execution metadata, checklists and Completion Report, set `status: review` and return to `moda_architect`; **STOP**. Do not begin Enables, merge task branches, push `main` or change Architect Review yourself.

## Implementation Notes

After ARCH-048-BACKGROUND-011 becomes accepted, generation-aware admission must be reconciled in ARCH-053-BACKGROUND-003 without overwriting this task's snapshot decisions. If generational admission code is absent, test against current baseline then mark downstream integration blocked.

## Completion Report

### Status

Ready for Review

### Files Changed

Implementation branch `task/ARCH-053-BACKGROUND-002`, commit `4430635`:

- `moda-interact-background/src/services/woocommerce-recovery/woo-recovery-admission.service.ts`
- `moda-interact-background/tests/unit/services/woocommerce-recovery/woo-recovery-admission.service.test.ts`
- `moda-interact-background/tests/integration/woo-recovery-admission.integration.test.ts`
- This task's checklists and Completion Report only.

### Work Completed

The validated candidate's complete `checkout.restoration` value is now written to `CheckoutRecovery.wooRestoreSnapshot` in the same PostgreSQL transaction as the recovery and its admission history. Missing evidence is persisted as `Prisma.DbNull`; supported and unsupported evidence remain explicit JSON. The existing display `lineItems`, currency, total, customer, consent fences, candidate/watermark checks, and checkout URL behavior are unchanged.

Unit coverage verifies supported, unsupported and absent snapshots, unchanged display projection, stale evidence rejection, concurrent maturity and separate generation-2 evidence. The disposable PostgreSQL/Redis integration test verifies the supported snapshot is durably persisted in the admission transaction.

Dependency and schema evidence:

- `@prisma/client`: package range `^6.19.3`, lockfile exact version `6.19.3` (installed/generated Prisma Client `6.19.3`).
- `prisma` CLI: package range `^6.19.3`, lockfile exact version `6.19.3`.
- Required database submodule: initialized at `af77c594ecbfc78c26d01c0021a090830884bbff`, which contains the `wooRestoreSnapshot Json?` column; no submodule pointer change was staged.

Physical worktree and preparation evidence:

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-053-BACKGROUND-002`, `task/ARCH-053-BACKGROUND-002`.
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-053-BACKGROUND-002`, `task/ARCH-053-BACKGROUND-002`.
- Shared workspace and source implementation checkouts were not switched or mutated; no other task worktree was reused.
- Parent remote task branch fast-forwarded: `not-needed`; parent `origin/main` incorporated: `already-current`.
- Implementation remote task branch fast-forwarded: `not-needed`; implementation `origin/main` incorporated: `already-current`.
- `git submodule sync --recursive`: passed; `git submodule update --init --recursive`: passed.

Implementation commit `4430635` was pushed to `origin/task/ARCH-053-BACKGROUND-002`.

### Validation Results

- `npm exec vitest -- run tests/unit/services/woocommerce-recovery/woo-recovery-admission.service.test.ts`: passed, 1 file / 38 tests.
- `npm run test:integration -- tests/integration/woo-recovery-admission.integration.test.ts`: passed, 1 file / 3 tests using the repository disposable PostgreSQL and Redis infrastructure.
- `npm run build` (runs Prisma generation and TypeScript compilation): passed; Prisma Client 6.19.3 generated.
- `git diff --check`: passed.
- The transaction writes only to PostgreSQL; Redis candidate and watermark reads occur before transaction entry. The existing test suite covers stale candidates, duplicate/concurrent admission, invalid evidence and propagated unexpected errors.

### Deviations

The launcher marked this prepared execution as `rework.required: true` with `previous_attempt: 0`, while the complete task's `## Architect Review` is still `Pending` and contains no requested corrections. No Changes Requested correction checklist was present to apply; implementation followed the task scope and acceptance criteria. This discrepancy is reported for architect reconciliation and the Architect Review section was not edited.

### Assumptions

The launcher's dependency gate passed for BACKGROUND-001 and DATABASE-001. Candidate restoration is already Shared-validated upstream, so admission stores that complete value without reparsing or synthesizing it from display line items.

### Unresolved Issues

No implementation or validation issues remain. The launcher/task Architect Review state discrepancy above awaits moda_architect reconciliation.

### Architectural Concerns

None. This task does not create a URL or perform external network operations.

## Architect Review

### Review Status

Accepted Complete at Attempt 1.

### Review Notes

Reviewed implementation commit `443063572b2a1d44f797286e114c1b1394009724` and the submitted Completion Report. The admitted candidate's validated restoration value is persisted with the recovery row inside the existing PostgreSQL transaction. Missing evidence maps to SQL `NULL`, explicit unsupported evidence remains JSON, and the historical `lineItems` projection is unchanged. Existing recovery rows are classified before creation, so duplicate/stale admissions do not replace a prior generation's evidence. No blocking implementation or architecture issue was found.

### Reviewed Files

- `moda-interact-background/src/services/woocommerce-recovery/woo-recovery-admission.service.ts`
- `moda-interact-background/tests/unit/services/woocommerce-recovery/woo-recovery-admission.service.test.ts`
- `moda-interact-background/tests/integration/woo-recovery-admission.integration.test.ts`
- This task's Completion Report and acceptance checklist.

### Validation Reviewed

Reviewed the submitted evidence: 38 focused unit tests, 3 PostgreSQL/Redis integration tests, `npm run build`, and `git diff --check` passed. The implementation task branch is clean at `4430635` and `origin/task/ARCH-053-BACKGROUND-002` points to that commit. Validation was reviewed from the durable report; it was not rerun during architect review.

### Architecture Conformance

Conforms to ARCH-053: the snapshot is immutable per admitted recovery generation, no URL is created, no external network or Redis operation runs inside the database transaction, and checkout identity, consent, order, and display-projection behavior remain in their existing boundaries.

### Follow-up

Promoted `ARCH-053-BACKGROUND-003` to `ready`: its dependencies `ARCH-053-BACKGROUND-002` and `ARCH-048-BACKGROUND-011` are Complete. No task branch was merged to `main`.
