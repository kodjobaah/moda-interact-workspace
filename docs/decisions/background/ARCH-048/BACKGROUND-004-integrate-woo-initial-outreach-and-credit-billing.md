---
id: ARCH-048-BACKGROUND-004
architecture_id: ARCH-048
title: Implement Woo initial-outreach and credit-billing service
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 48
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-048-BACKGROUND-006
- ARCH-046-BACKGROUND-004
- ARCH-045-BACKGROUND-005
enables:
- ARCH-048-BACKGROUND-005
created: '2026-10-23'
updated: '2026-10-23'
---

# ARCH-048-BACKGROUND-004 — Implement Woo initial-outreach and credit-billing service

## Architecture

Architecture ID: `ARCH-048`

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`

Coordinator: `moda_architect`

Portable **architect proposal**, Attempt 5, based on the 23 October 2026 snapshot and Attempt 2 task definitions. Defined but not materialised: no remote branch, worktree, implementation commit, review acceptance or release is claimed. Before execution re-read canonical dependencies and latest Architect Review in the developer workspace. The developer confirms `ARCH-046-BACKGROUND-004` complete after the snapshot; do not reopen it.

## Objective

Implement `WooRecoveryOutreachService` as a separately testable first-recovery outreach capability that reserves credits, creates/uses the single initial attempt, applies the completed final consent/STOP/template and order guards and delegates delivery/compensation to existing platform infrastructure; **no workers are wired here**.

## Context

BG003 creates only an existing DB recovery. The completed ARCH-046-BACKGROUND-004 is the provider-dispatch consent fence and must be reused, not reopened. Billing, attempt lifecycle and compensation already exist and remain the source of truth; this Woo service is an adapter, not a second finance engine.

## Scope

- Own `src/services/woocommerce-recovery/woo-recovery-outreach.service.ts`, focused tests, and small Woo-specific adapters over current recovery reservation/attempt/dispatch services. Implement the BG006 outreach interface using an injected existing-recovery repository and a seeded test `recoveryId`; neither BG003 nor the ARCH-046 missing-consent notice implementation needs to exist to test this service. Avoid changing platform-neutral billing semantics.
- Expose `enqueueInitial(recoveryId)` for asynchronous/retryable initiation and `processInitial(recoveryId or attemptId)` for existing outbound-worker lifecycle integration, or an equivalently split interface where the irreversibility boundary is explicit. Neither method may create a new `CheckoutRecovery`.
- Under checkout-scoped final guard, load same shop + exact current recipient + committed recovery/attempt, check latest **received** order terminal evidence and merchant settings. Never start another initial attempt if one is sent or in flight; idempotent retry recovers pending same attempt.
- Reuse ARCH-046-BACKGROUND-004 final pre-provider consent/STOP/merchant suppression and Meta-approved Marketing template category at the actual send permit. Do not reconstruct a second independent consent checker or infer consent from contact details.
- Reuse existing entitlement, subscription/lifetime/purchased credit-source attribution, reservation, provider status and compensation. A delivered initial charge remains valid even if a paid order arrives later; a failed/rejected unused reservation must be correctly released.
- Implement explicit **default-disabled** Woo outbound gate with test-only controlled opt-in; gate evaluation occurs before credit reservation/send and does not affect normal Shopify sends.
- Block all Woo automatic follow-up, sequence-2, re-entry or recovery-resume sending until an independently approved order/consent/billing policy exists; use existing guarded hook/feature gating rather than opening a new route.
- Provide BG006-defined typed enqueue/dispatch outcomes `queued`, `already-initialized`, `sent`, `deferred`, `suppressed` and `failed-retryable` for orchestrator consumption and observability.

## Out of Scope

- No edits to Woo capture/maturity workers, orchestrator registration, new WhatsApp transport, credit accounting schema, completed ARCH-046-BACKGROUND-004 task or merchant WordPress read endpoint.
- No new follow-up messaging feature or live Woo provider lookup.

## Requirements

- **Business boundary:** outbound initiation/attempt/finalization and usage only; BG003 owns first row, BG005 owns wiring. A valid committed recovery fixture is sufficient for independent implementation; live service integration is not a prerequisite.
- The final irreversible-send gate must recheck both existing durable recovery/attempt state and latest observed order terminal/STOP/consent/template. Do not rely solely on a maturity-time permit.
- No duplicate initial message or credit even if BullMQ job is deleted/replayed, concurrent workers race or a retry follows uncertain provider outcome; existing provider idempotency policy must be preserved.
- All Woo follow-ups remain disabled by default even if the merchant configured a follow-up in another platform.
- No claim of detecting order events never delivered to Moda; sending requires explicit developer rollout approval after system validation.

## Work Items

- [ ] Implement isolated Woo outreach service with injected reservation, attempt, final guard, provider and refund/compensation interfaces.
- [ ] Add explicit default-off send gate and follow-up disablement; leave all ingress/worker wiring for BG005.
- [ ] Test duplicate enqueue/process, already-sent recovery after old queue job removed, payment concurrent with send, STOP/consent template gate, successful charge by bucket and rejection compensation.
- [ ] Prove Shopify messaging/billing regression suites remain green; record failure boundary between durable DB operation and queue enqueue.

## Interfaces / Contracts

**Owned capability interface (canonical definition in BG006):**

```ts
interface WooRecoveryOutreachDispatcher {
  enqueueInitial(recoveryId: string): Promise<WooOutreachEnqueueOutcome>;
  processInitial(recoveryId: string): Promise<WooOutreachDispatchOutcome>;
}
```

`processInitial` may delegate to an existing canonical attempt processor rather than create a second sender; preserve the durable attempt ID and existing provider transaction semantics. If no new queue step is necessary, describe the exact existing processor/trigger in Completion Report.

**Inputs:** an existing, committed `CheckoutRecovery.id` supplied as an opaque string and BG006 `WooObservedOrderStateReader` injected with a test fake until BG005 composition; current exact recipient, completed ARCH-046 final consent/STOP guard, existing `RecoveryOutreachAttempt`, current entitlements/usage reservations. BG004 does not call BG003 or ARCH-046-BACKGROUND-002.

**Outputs:** outcome only; no worker registration. BG005 is the only task that attaches enqueue/dispatch to running workers.

**File boundary:** Woo outreach service and adapters/tests only. Do not edit `src/workers/*`, `src/entrypoints/*`, BG001–003 services, or the accepted ARCH-046-BACKGROUND-004 task file.

## Dependencies

- `ARCH-048-BACKGROUND-006`
- `ARCH-046-BACKGROUND-004`
- `ARCH-045-BACKGROUND-005`

## Enables

- `ARCH-048-BACKGROUND-005`

## Acceptance Criteria

- [ ] One successful initial provider message and at most one charge per eligible recovery despite duplicates/retries, with correct source attribution and failure compensation.
- [ ] Known paid/cancelled/placed order, revoked consent, local STOP or invalid Marketing template prevents irreversible send and inappropriate credit consumption.
- [ ] Woo follow-up, sequence-2 and re-entry are gated off; release remains default-off.
- [ ] Task can be unit/integration reviewed before worker integration; BG005 is the sole runtime-wiring owner.

## Validation

- [ ] Focused injected-service unit tests for every exact sender/credit bucket, provider failure and idempotency state.
- [ ] Postgres/Redis integration for concurrent reservations/attempts and terminal event racing final send.
- [ ] Existing billing compensation, consent final-send, Shopify recovery regression and declared code checks plus `git diff --check`.

## Stop Condition

After completing only the task's scoped service, tests, Acceptance Criteria and Validation, populate the Completion Report, set status to `review`, return control to `moda_architect`, and **STOP**. Do not wire a worker or start a dependent task. Record launcher-prepared parent and implementation dedicated worktree paths, physical isolation, synchronisation, submodule state and both task branch revisions in the Completion Report.

## Implementation Notes

Investigate the actual pre-send fence exposed by accepted ARCH-046-BACKGROUND-004 in the developer branch. If the exposed interface is incompatible, return the dependency gap to the architect; do not edit accepted task scope or clone the guard.

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
