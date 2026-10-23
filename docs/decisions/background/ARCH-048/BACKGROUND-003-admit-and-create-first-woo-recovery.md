---
id: ARCH-048-BACKGROUND-003
architecture_id: ARCH-048
title: Implement Woo maturity and first-recovery admission service
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-048-BACKGROUND-001
- ARCH-048-BACKGROUND-002
- ARCH-048-WOOCOMMERCE-002
- ARCH-048-WOOCOMMERCE-003
- ARCH-046-BACKGROUND-001
enables:
- ARCH-046-BACKGROUND-002
- ARCH-048-BACKGROUND-004
- ARCH-048-BACKGROUND-005
created: '2026-10-23'
updated: '2026-10-23'
---

# ARCH-048-BACKGROUND-003 — Implement Woo maturity and first-recovery admission service

## Architecture

Architecture ID: `ARCH-048`

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`

Coordinator: `moda_architect`

Portable **architect proposal**, Attempt 3, based on the 23 October 2026 snapshot and Attempt 2 task definitions. Defined but not materialised: no remote branch, worktree, implementation commit, review acceptance or release is claimed. Before execution re-read canonical dependencies and latest Architect Review in the developer workspace. The developer confirms `ARCH-046-BACKGROUND-004` complete after the snapshot; do not reopen it.

## Objective

Implement `WooRecoveryAdmissionService` that evaluates a mature Woo candidate against successfully received checkout/order evidence, the existing durable recovery record and current exact-recipient consent, and **creates only the first `CheckoutRecovery` row**, never an attempt, charge or message.

## Context

Shopify's present `RecoveryMaterializationService` invokes a Shopify provider checkout lookup and its downstream initiating path can send immediately. Woo must use a provider-specific admission adapter over reusable shop/DB/consent primitives, not trick Shopify's provider resolver with Woo event data. This task provides the pre-INSERT consent decision seam consumed by pending ARCH-046-BACKGROUND-002; BG005 wires the actual maturity worker later.

## Scope

- Own `src/services/woocommerce-recovery/woo-recovery-admission.service.ts` and focused tests; add a narrow reusable row-only insert helper only if a genuinely platform-neutral existing helper is insufficient. Do not modify Shopify-only lookup paths to pretend Woo live state is verified.
- Expose `evaluateMatured(candidate: WooPendingCandidate, context): Promise<WooAdmissionOutcome>` returning discriminated outcomes including `created { recoveryId }`, `already-exists`, `superseded`, `denied { reason }`, and `deferred { reason }`. Only `created` may be passed to outbound orchestration.
- Require an explicit Woo-source candidate from BG001, authenticate shop/platform and installation, check merchant delay from last **successfully received** activity and current bounded snapshot (real nonempty items, amount/currency, exact Customer/CustomerPhone matching); reject incomplete/stale/ambiguous evidence.
- Under shared checkout-scoped lease, compare latest event watermark and BG002 terminal order policy, read existing `CheckoutRecovery` with/without candidate job, and recheck before row INSERT. A `MESSAGE_SENT`/`ENGAGED`/terminal existing row cannot lead to a second initial recovery, including EXPIRED/re-entry without separately approved generation policy.
- Call existing ARCH-046-BACKGROUND-001 current exact-recipient marketing permission/STOP/suppression **before INSERT**; invalid/unavailable/revoked/ambiguous identity or consent yields typed denial/defer and zero row. Prepare an injected denied-admission result hook consumed by ARCH-046-BACKGROUND-002 for one idempotent merchant Support notice without implementing the notice here.
- Create existing `CheckoutRecovery` and applicable `CheckoutRecoveryStatusHistory` transactionally and idempotently under the existing unique `(shopId,checkoutToken,generation)` contract; preserve correct customer, basket and value snapshot. Return only the created recovery ID, never dispatch inline.
- Reconcile crash/retry between candidate maturity and insert; prevent concurrent duplicate generation, idempotent `already-exists`, and do not call Background→Moda API or WooCommerce.

## Out of Scope

- No worker modification, Action Scheduler, billing, initial `RecoveryOutreachAttempt`, WhatsApp, Support notice implementation, Woo guest session read or new Moda database schema.
- No Shopify customer resolver, Shopify abandoned checkout lookup or direct invocation of existing send-and-bill initialisation.

## Requirements

- **Service boundary:** computes admission decision and row-only creation; all sending/billing is BG004 and all wiring BG005.
- Absent/expired BullMQ job is never proof that no recovery exists; check PostgreSQL under transaction/concurrency discipline.
- One initial generation per Woo checkout lineage. If existing status suggests re-entry, fail closed pending separately approved policy rather than auto-increment generation.
- Current consent for exact canonical customer phone and local STOP supersede stale positive evidence. Never create a consent-wait recovery row.
- No claim of live checkout verification: latest *received* event is all that can be known under outbound-only design.
- An accepted `created` result is not a guarantee of send; BG004 performs independent irreversible dispatch guards.

## Work Items

- [ ] Implement injected service with typed admission result; isolate all provider-specific snapshot/recipient resolution from Shopify-specific functions.
- [ ] Exercise default current-consent gating and add stable denial result hook for ARCH-046-BACKGROUND-002 without writing its Support-message logic.
- [ ] Test two workers, duplicate delayed job, missing job + existing row, missing items/customer, wrong shop, terminal order, STOP/revocation and consent reader unavailable.
- [ ] Prove created service result alone does not enqueue/send/charge; preserve Shopify materialisation tests.

## Interfaces / Contracts

**Service port:**

```ts
interface WooRecoveryAdmissionPort {
  evaluateMatured(candidate: WooPendingCandidate, context: { jobId?: string }): Promise<WooAdmissionOutcome>;
}
type WooAdmissionOutcome =
  | { kind: "created"; recoveryId: string }
  | { kind: "already-exists"; recoveryId: string; status: string }
  | { kind: "superseded" | "denied" | "deferred"; reason: string };
```

**Inputs:** only typed Woo-source candidate from BG001 (last accepted evidence + watermark), BG002 order guard, active tenant/installation, shop recovery policy, exact customer/phone and ARCH-046 current marketing consent reader.

**Output contract to ARCH-046-BACKGROUND-002:** stable denial reasons and an injectible before-INSERT consent-policy/admission-result hook; ARCH-046 owns deduplicated merchant Support notice implementation. BG004 sees only a committed recoveryId. No public cross-service API is added.

**File boundary:** own Woo admission service/adapter, optional reusable *row-only* DB helper, own tests. Do not edit checkout/order workers, pending candidate worker, existing Shopify-only lookup service, initial-send services or `src/entrypoints/*`.

## Dependencies

- `ARCH-048-BACKGROUND-001`
- `ARCH-048-BACKGROUND-002`
- `ARCH-048-WOOCOMMERCE-002`
- `ARCH-048-WOOCOMMERCE-003`
- `ARCH-046-BACKGROUND-001`

## Enables

- `ARCH-046-BACKGROUND-002`
- `ARCH-048-BACKGROUND-004`
- `ARCH-048-BACKGROUND-005`

## Acceptance Criteria

- [ ] First-insert occurs exactly once for eligible shop + Woo checkout lineage; no side effects if an existing first recovery or attempt is found even after job deletion.
- [ ] No INSERT/attempt/bill/send for missing/ambiguous recipient, empty/oversized basket evidence, placed/paid/cancelled order, immature candidate, STOP or non-GRANTED current marketing consent.
- [ ] Explicit row-only result port enables ARCH-046 missing-consent notices and BG004 outbound service; no premature worker wiring.
- [ ] Concurrency and production historical Shopify behaviours pass regressions.

## Validation

- [ ] Focused unit tests with injected current consent and order state/clock; rejection matrix and no network sends.
- [ ] Postgres/Redis idempotency tests for materialise/cancel/update races and existing-sent/no-candidate path.
- [ ] Shopify recovery admission regressions, repository-declared typecheck/lint and `git diff --check`.

## Stop Condition

After completing only the task's scoped service, tests, Acceptance Criteria and Validation, populate the Completion Report, set status to `review`, return control to `moda_architect`, and **STOP**. Do not wire a worker or start a dependent task. Record launcher-prepared parent and implementation dedicated worktree paths, physical isolation, synchronisation, submodule state and both task branch revisions in the Completion Report.

## Implementation Notes

ARCH-046-BACKGROUND-002 may integrate its notice/consent decision implementation directly against this service seam after this task is architect-accepted. That task is distinct from worker composition (BG005).

- Use `/moda-task` launcher preparation and the actual task worktrees on the developer's machine; a portable ZIP is not an execution claim or Git baseline.
- Respect service/file ownership and cross-repository boundaries in this task and the parent architecture. Do not modify `docs/decisions/**/_index.md` before explicit architect session closure.
- Reuse approved shared logging and existing domain infrastructure; inspect actual repository `package.json` and perform only relevant declared checks. Record exact evidence and any impossible test rather than inventing a pass.
- All checkout/session/phone/order logging must exclude raw PII, secrets, session tokens and full basket data; record bounded reason codes and structured correlation IDs only.

## Completion Report

### Status

Not Started — portable task definition only.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run by repository implementer; no developer repository worktree or remote is accessible from this review package.

### Deviations

None.

### Assumptions

Latest uploaded ZIP and proposed task files may lag active developer branches. Latest dependency state must be checked before materialisation. The developer reports `ARCH-046-BACKGROUND-004` complete; reuse accepted implementation without editing its task definition.

### Unresolved Issues

Confirm actual approved cross-task dependency versions before implementation; raise missing canonical shared contracts or unimplementable business guarantees to the architect rather than inventing substitutes.

### Architectural Concerns

The outbound-only event design cannot identify Woo updates/payments whose events never arrive; this limitation must remain explicit and Woo outbound disabled until reviewed.

## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
