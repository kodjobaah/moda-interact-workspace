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
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
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

Architecture ID: `ARCH-053`. Document: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Coordinator: `moda_architect`. **Portable canonical task: defined but not materialised**; no Git branch, worktree, commit, push, review or producer deployment claimed.

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

- [ ] Use published Shared validator for nested restore field; preserve existing event envelope digest and job IDs.
- [ ] Carry restoration through candidate create/update/cancel/replay and deterministic stale checks.
- [ ] Add tests for no field, unsupported, coupons-only change, quantity change, delayed replay and invalid nested schema.

## Interfaces / Contracts

Queue remains `woo-checkout-capture-v1` / `checkout-updated` with canonical `woo.activity.v1` event wrapper + additive optional `checkout.restoration`; TypeScript schema from published Shared package. No new Redis queue key or event type. Consumers of `WooPendingCandidate` must be able to obtain `candidate.basket.checkout.restoration`.

## Dependencies

- `ARCH-053-SHARED-002` (must be architect-accepted Complete)

## Enables

- `ARCH-053-BACKGROUND-002`
- `ARCH-053-WOOCOMMERCE-001`

## Acceptance Criteria

- [ ] Use published Shared validator for nested restore field; preserve existing event envelope digest and job IDs.
- [ ] Carry restoration through candidate create/update/cancel/replay and deterministic stale checks.
- [ ] Add tests for no field, unsupported, coupons-only change, quantity change, delayed replay and invalid nested schema.
- [ ] No regression in tenant isolation, historical generation preservation, valid shopper cart or consent/STOP/terminal order guards.
- [ ] Tests demonstrate invalid/stale/replayed and unexpected errors do not produce silent success or malformed URLs.
- [ ] No change outside assigned domain repository code plus owned task Completion Report; no ARCH-052 work.

## Validation

- [ ] Background focused Woo capture parser and candidate unit tests
- [ ] Background declared typecheck/lint and queue replay tests
- [ ] `git diff --check`

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are complete, update ONLY this task's authorised execution metadata, checklists and Completion Report, set `status: review` and return to `moda_architect`; **STOP**. Do not begin Enables, merge task branches, push `main` or change Architect Review yourself.

## Implementation Notes

The queue consumer task must be accepted/deployed before an API v3 producer forwards new fields. Use the shared logger, not another generic logger, for bounded validation failures.

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
