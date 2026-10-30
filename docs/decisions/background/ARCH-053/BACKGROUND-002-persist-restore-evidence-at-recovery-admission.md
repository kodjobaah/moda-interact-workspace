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
status: in_progress
priority: 35
executor: codex
claimed_at: 2026-10-30T15:25:53Z
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

- [ ] Write `wooRestoreSnapshot` transactionally at admission without changing display `lineItems`.
- [ ] Test supported, unsupported, absent, stale and simultaneous admissions, plus subsequent generation snapshot separation.
- [ ] Record exact new Prisma dependency version and required submodule update in Completion Report.

## Interfaces / Contracts

Source `WooPendingCandidate.basket.checkout.restoration` from BACKGROUND-001; column from DATABASE-001; parser from published Shared. No change to public API or queue. `null` means unknown; unsupported JSON means known-unrestorable.

## Dependencies

- `ARCH-053-BACKGROUND-001` (must be architect-accepted Complete)
- `ARCH-053-DATABASE-001` (must be architect-accepted Complete)

## Enables

- `ARCH-053-BACKGROUND-003`

## Acceptance Criteria

- [ ] Write `wooRestoreSnapshot` transactionally at admission without changing display `lineItems`.
- [ ] Test supported, unsupported, absent, stale and simultaneous admissions, plus subsequent generation snapshot separation.
- [ ] Record exact new Prisma dependency version and required submodule update in Completion Report.
- [ ] No regression in tenant isolation, historical generation preservation, valid shopper cart or consent/STOP/terminal order guards.
- [ ] Tests demonstrate invalid/stale/replayed and unexpected errors do not produce silent success or malformed URLs.
- [ ] No change outside assigned domain repository code plus owned task Completion Report; no ARCH-052 work.

## Validation

- [ ] Focused Background admission test suite with mocked and Postgres-backed transaction where available
- [ ] `npm run typecheck` / package-defined validation; `git diff --check`
- [ ] Adversarial stale/duplicate candidate case and no external network within transaction

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are complete, update ONLY this task's authorised execution metadata, checklists and Completion Report, set `status: review` and return to `moda_architect`; **STOP**. Do not begin Enables, merge task branches, push `main` or change Architect Review yourself.

## Implementation Notes

After ARCH-048-BACKGROUND-011 becomes accepted, generation-aware admission must be reconciled in ARCH-053-BACKGROUND-003 without overwriting this task's snapshot decisions. If generational admission code is absent, test against current baseline then mark downstream integration blocked.

## Completion Report

### Status

Not Started

### Files Changed

None — portable task definition only.

### Work Completed

Not Started.

### Validation Results

Not Run — no implementation claimed.

### Deviations

None.

### Assumptions

Design reconciled against uploaded 2026-10-30 07:59 source snapshot; re-check source and prior task acceptance before implementation.

### Unresolved Issues

None asserted as executed; dependencies must be materialised/accepted.

### Architectural Concerns

Return any cross-service schema/provider/transaction concern to `moda_architect` before improvising.

## Architect Review

### Review Status

Pending

### Review Notes

Not Reviewed — task not executed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

To be assessed after implementation.

### Follow-up

None.
