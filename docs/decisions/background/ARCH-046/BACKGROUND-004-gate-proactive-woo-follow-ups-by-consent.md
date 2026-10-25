---
id: ARCH-046-BACKGROUND-004
architecture_id: ARCH-046
title: Enforce final Woo initial-recovery WhatsApp send consent and STOP fence
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 38
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-046-BACKGROUND-001
  - ARCH-046-BACKGROUND-002
  - ARCH-045-BACKGROUND-005
  - ARCH-048-BACKGROUND-004
enables:
  - ARCH-048-BACKGROUND-005
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-25
---

# Enforce final Woo initial-recovery WhatsApp send consent and STOP fence

## Architecture

Architecture ID: `ARCH-046`.

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`.

Coordinator: `moda_architect`.

**Execution frontier (25 October 2026): Ready, unclaimed, Attempt 0.** `ARCH-046-BACKGROUND-002` is explicitly Complete on its parent task branch at commit `64d20849`; the other declared dependencies are Complete. This task is promoted from `pending` to `ready` after all explicit dependencies became Complete. Its old external requirement for a Woo follow-up engine has been removed because this task is **narrowed to the initial-send/final-permit capability already required by ARCH-048**. No attempt is claimed or started by this promotion.

## Execution Ownership Amendment

On 25 October 2026, the developer explicitly took over this ready agent-owned task through `/moda_developer_create`. Execution and completion authority are now developer-controlled; `assigned_agent: moda_background`, task scope, dependencies and acceptance criteria are unchanged. Attempt 1 was claimed at `2026-10-25T16:39:00Z` after all explicit dependencies were verified Complete and both canonical task worktrees were prepared. This amendment records execution ownership only; no feature implementation has started.

## Objective

Implement a **Woo-specific, consent- and STOP-guarded final provider-admission sender** for the initial abandoned-checkout recovery template, including retries/reentries of the same initial attempt, by satisfying the existing `WooGuardedInitialSender` contract used by accepted `ARCH-048-BACKGROUND-004`. Preserve existing billing, attempt and provider idempotency semantics. Do not enable Woo scheduled or merchant post-window follow-ups.

## Context

`src/services/woocommerce-recovery/woo-recovery-outreach.service.ts` already defines `WooGuardedInitialSender.sendInitial()` and `findExistingAdmission()`. `woo-recovery-outreach.adapters.ts` explicitly requires a reviewed guarded sender and states that the generic `OutboundWhatsAppAdmissionService.sendTemplate` is **not** an acceptable Woo final sender without a Woo-specific final SQL consent fence. The business service already performs earlier recipient, observed-order, consent, Marketing-template and billing rechecks; these **do not replace** the last durable provider-permit guard.

The STOP writer/final permit must honour the existing Shop-first transaction lock order. A provider request must happen **only after** an admission transaction has successfully committed. Current Woo order observations are event-derived; they cannot prove a payment event that never reached Moda. This limitation remains explicit.

## Scope

- Implement **one** bounded Woo initial-send guard/adapter in `moda-interact-background` (for example `src/services/woocommerce-recovery/woo-guarded-initial-sender.service.ts`) matching the already published Background-local `WooGuardedInitialSender` TypeScript interface from BG004. This is an implementation task for the final-send boundary, **not** a second Woo outreach/orchestrator business service.
- Reuse existing outbound/provider-admission, `ConversationMessage` provider dispatch key, moderation, conversation and billing services. Add only the Woo-specific admission validation needed at the final durable permit, reusing shared STOP helpers and approved locked-row ordering. If the existing infrastructure cannot satisfy the contract without a new cross-repository interface/schema, stop and return that dependency gap to the architect; **do not** imitate atomicity with a preflight-only check.
- Validate current shop installation ACTIVE/not revoked, matching Woo Shop and `CheckoutRecovery`, exact current `CustomerPhone` and recipient, `whatsappConsentDecision = GRANTED` with applicable local STOP and merchant suppression clear, and appropriate latest successfully observed order/recovery terminal evidence. Do not infer opt-in from a collected number or let a delayed native grant clear a STOP. Confirm selected template is provider-verified **Marketing**, not merely Moda catalogue-approved.
- For the final **SQL transaction**, acquire relevant locks in the established order (Shop before recipient/attempt/message rows, consistent with STOP and recovery send paths); compare current recipient/consent and no-contact revision to the caller's expected snapshot and reject stale/mismatched state. Evaluate durable recovery/attempt and already-admitted provider idempotency in the same permit decision. Check event-derived order terminal status via accepted BG002 services at the checkout-locked orchestration boundary and enforce durable terminal suppression in the permit where persisted state is available. **No external provider/Redis/network I/O inside SQL locks.** Do not claim a Redis-only observation is transactionally locked in SQL.
- On known pre-permit denial: no provider call, no permanent initial-attempt consumption and release/refund a reversible credit reservation through the existing BG004/RecoveryBillingService flow. For DB/unavailable evidence/unknown provider outcome: throw or return an explicitly retryable/reconciliation state according to the existing sender contract; do not convert it into successful `suppressed` or send a second message.
- Enforce at-most-once durable provider admission with `findExistingAdmission(idempotencyKey)` and preserve the existing `PENDING`/`SENT`/`FAILED` reconciliation behaviour of BG004. Provider-confirmed sends retain earned charges even if a later terminal event arrives. No second initial message or second credit on replay.
- Reuse approved shared structured logging; unexpected DB, recipient, provider-permit and compensation failures must be awaited, logged safely and propagated. No sensitive customer contents or tokens in logs.

## Out of Scope

- **No** scheduled sequence-two Woo follow-up, merchant-authored proactive post-window recovery template, WhatsApp recipient consent queue, new follow-up scheduler or new billing scheme. Woo `followUpDueAt` remains null; no follow-up is enabled by this task. Those capabilities require separate approval/task definitions before any activation.
- No changes to the completed first-row admission policy or its shared merchant notification service; no duplicate STOP notification. `ARCH-046-BACKGROUND-002` owns initial row-denial Support notices.
- No reimplementation of existing general-service-message guard or weakening of its STOP requirement for human/AI in-window replies. No new WordPress REST checkout reader, session access, Shopify HTTP preflight or database schema by assumption.

## Requirements

### R1 — Existing Woo sender contract (do not redefine)

```ts
interface WooGuardedInitialSender {
  sendInitial(input: {
    recovery: WooOutreachRecovery;
    attemptId: string;
    conversationId: string;
    recipient: string;
    consent: WooRecoveryConsentSnapshot;
    template: WooMarketingTemplate;
    idempotencyKey: string;
    recoveryCreditSourceKey: string;
  }): Promise<{ kind: "admitted" } | { kind: "suppressed"; reason: string }>;
  findExistingAdmission(idempotencyKey: string): Promise<PersistedMessage | null>;
}
```

The canonical declaration and `PersistedMessage` type live in `woo-recovery-outreach.service.ts`. Implement against that declaration. The caller `WooRecoveryOutreachService.processInitial()` owns attempt creation, reservation, finalization and compensation; do not duplicate its business flow.

### R2 — Final decision matrix

| Current evidence at final permit | Required behaviour |
|---|---|
| Exact recipient GRANTED; no STOP/suppression; active installation; no known terminal state; verified Marketing template; no prior provider permit | Admit **once**, then use approved provider-delivery path after SQL commit |
| Customer STOP or merchant suppression; consent withdrawn/unknown/recipient changed; shop/installation inactive | Suppress before provider permit; no Meta call; reversible credit reservation released |
| Paid/cancelled/terminal order **already observed by Moda** or terminal recovery status | Suppress without Meta send even when candidate BullMQ job is absent |
| Missing/Utility/Authentication/unverified template category | Suppress without Meta call, no credit consumed |
| Database/guard dependency unavailable or unexpected failure | Fail closed and propagate; do not claim customer refusal or mark job completed |
| Existing `PENDING` provider admission with uncertain outcome | Reconcile; **never** blindly send twice or release a potentially earned charge |
| Existing provider-confirmed `SENT`/`DELIVERED`/`READ` | Return existing admission for BG004's idempotent finalization, no new Meta call |
| Existing confirmed `FAILED` admission | Follow existing compensation/reconciliation; no second first-send attempt |

An initial-send reentry is still sequence **1** and follows the same final fence. A different checkout or shop may not reuse this attempt's provider idempotency key.

### R3 — Race boundaries, logging and rollout

- A STOP committed **before** the final permit obtains its Shop lock blocks that permit; a STOP committed **after** a completed permit may be too late to stop an already admitted provider call. Document and test this ordering honestly.
- The event-only design cannot detect a Woo payment/update event never delivered to Moda. Do not claim live Woo verification. Preserve default-off Woo send gating until developer approval after integrated system testing.
- All technical exceptions propagate to the correct worker retry/reconciliation boundary using the existing shared structured logger. No new local generic logger, swallowed exceptions, PII-rich logs, unbounded retries or Redis/provider I/O within a DB transaction.

## Work Items

- [x] Inspect accepted BG004 service and adapters, BG002 observed-order/coordination services, exact-recipient consent reader, STOP lock writer, existing outbound SQL permit and provider idempotency/billing capabilities.
- [x] Implement and inject one concrete `WooGuardedInitialSender`, using existing admission/attempt/credit primitives without copying the entire outbound sender.
- [x] Enforce the R2 matrix with correct durable permit, Meta request outside SQL and explicit compensation/uncertain-outcome handling.
- [ ] Add focused injected service tests, PostgreSQL/Redis concurrency/fault-injection tests and STOP/terminal/Marketing-category regression cases; validate read-after-commit existing admissions.
- [x] Record evidence for lock ordering, credential/tenant scope, absence of DB transaction I/O and shared logger/exception propagation.

## Interfaces / Contracts

Consumes `WooGuardedInitialSender`, `WooRecoveryOutreachService` and `createWooRecoveryOutreachService()` from accepted ARCH-048-BG004; `WooRecoveryConsentReader` from ARCH-046-BG001; observed-order/checkout guard contracts from ARCH-048-BG002; CustomerPhone STOP/no-contact from ARCH-045-BG005; existing transactional outbound provider admission and billing contracts. The **final sender** is produced here for injection into ARCH-048-BG005's composition; no worker modifications in this task.

If a provider-admission schema/contract gap prevents atomic final consent/STOP checks, treat this task as blocked by a newly discovered dependency and return it to `moda_architect` rather than introducing a second unsafe sender.

## Dependencies

- `ARCH-046-BACKGROUND-001`
- `ARCH-046-BACKGROUND-002`
- `ARCH-045-BACKGROUND-005`
- `ARCH-048-BACKGROUND-004`

## Enables

- `ARCH-048-BACKGROUND-005`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [x] A concrete, testable Woo `WooGuardedInitialSender` exists; the existing BG004 outreach service consumes it without a bare generic sender bypass.
- [x] Final permit correctly enforces all R2 cases, STOP lock ordering, exact recipient consent, observed terminal outcomes and verified Marketing template. Meta and Redis calls are **outside** the permit transaction.
- [x] No duplicate first send or credit on concurrent workers, retries or uncertain provider states; denial releases reversible reservations without permanently consuming sequence 1.
- [ ] SHOPIFY/general in-window replies continue to use their existing guards; no Woo sequence-two follow-up is scheduled or authorised.
- [x] Shared structured logs are bounded, DB/Redis/provider faults propagate or reconcile and are never silently swallowed.
- [x] Default-off Woo send state is preserved until BG005 and terminal system-test acceptance; no assumption that an undelivered Woo event can be detected.

## Validation

- [x] Focused typecheck/unit + PostgreSQL permit/lock tests for current consent revisions, STOP/merchant suppression, installation/recipient change, template category and terminal recovery.
- [ ] Two-client concurrent initial-attempt/send, STOP-versus-permit, paid/cancelled-order-versus-send, provider-confirmed/uncertain/failed-retry, billing source attribution and compensation tests.
- [ ] Existing Shopify/outbound general guard and human/AI in-window STOP regressions; verify no new Woo follow-up path or Redis/HTTP under SQL lock.
- [ ] Repository-declared relevant build/lint/test scripts, `git diff --check` and Completion Report with actual worktree/branch isolation evidence.

## Stop Condition

After the scope, criteria and validation are complete, set `status: review`, fill the Completion Report, return to `moda_architect` and **STOP**. Do not wire new workers, activate Woo sends or begin BG005. Required launcher-resolved worktree/synchronization evidence must be recorded.

## Implementation Notes

The earlier BG004 definition required a Woo follow-up engine that ARCH-048 deliberately does not provide. This revision removes that *implementation prerequisite* and narrows the task to the real initial-send safety gap. It does **not** assert that the guard is already implemented. Do not alter the completed ARCH-048-BG004 service merely to make an unguarded `sendTemplate()` typecheck. If a safe adapter cannot be built using current provider-admission capabilities, return a concrete missing primitive to the architect rather than silently weakening the final fence. Do not update domain `_index.md` files.

## Completion Report

### Status

Ready for Review — developer-owned workflow **Attempt 1** (four incremental implementation patch revisions). Implementation committed and pushed; architect acceptance and explicit developer completion are not claimed.

### Files Changed

**Implementation repository:** `moda-interact-background`, branch `task/ARCH-046-BACKGROUND-004`, commit `0c92e12` (`feat(ARCH-046-BACKGROUND-004): enforce Woo final consent and STOP send fence`), pushed to `origin` on 25 October 2026. The commit contains **10 files, 1,131 insertions and 23 deletions**:

- `src/services/outbound-whatsapp-admission/outbound-message-delivery.service.ts`
- `src/services/outbound-whatsapp-admission/outbound-provider-failure.service.ts`
- `src/services/woocommerce-recovery/woo-guarded-initial-sender.service.ts` (new)
- `src/services/woocommerce-recovery/woo-initial-send-fence.service.ts` (new)
- `src/services/woocommerce-recovery/woo-recovery-outreach.service.ts`
- `tests/integration/woo-initial-send-fence.integration.test.ts` (new)
- `tests/unit/services/woocommerce-recovery/woo-guarded-initial-sender.service.test.ts` (new)
- `tests/unit/services/woocommerce-recovery/woo-initial-delivery.service.test.ts` (new)
- `tests/unit/services/woocommerce-recovery/woo-initial-send-fence.service.test.ts` (new)
- `tests/unit/services/woocommerce-recovery/woo-recovery-outreach.service.test.ts`

**Parent task branch:** This task definition alone is updated for review submission. No parent architecture, domain `_index.md`, unrelated task, implementation code or submodule gitlink is included in the review-report patch.

### Work Completed

- Implemented `WooGuardedInitialSenderService` against the existing `WooGuardedInitialSender` contract and `WooInitialSendFenceService` for final Woo sequence-one provider admission; existing outreach continues to own reservations, billing, compensation and attempt finalisation.
- Reused the established outbound moderation, persisted `ConversationMessage` admission and provider delivery machinery. Final SQL permit locks Shop first, checks recovery/conversation/attempt identity, exact registered recipient, consent revision, active Woo installation, local STOP/suppression and durable terminal order evidence, and commits the provider dispatch key before the external provider call.
- Preserved duplicate-admission protection, existing confirmed-send reconciliation and fail-closed behaviour for uncertain provider outcomes. Denied pre-permit sends release reversible credit reservations without permanently consuming sequence one.
- Reused `@modainteract/moda-interact-shared/logging` for structured, bounded error diagnostics. Technical failures are logged and rethrown; a compensation failure retains the original error rather than being swallowed.
- Added focused sender, permit, provider-delivery and outreach unit tests and real PostgreSQL tests for concurrent permit contenders, STOP ordering, terminal order evidence, consent/recipient/install changes and provider dispatch persistence.
- Preserved default-off Woo outbound gating and absence of Woo follow-up scheduling or BG005 worker composition.

### Validation Results

Evidence from the developer's terminal captures dated 25 October 2026:

| Validation | Result / evidence |
|---|---|
| Focused `npm test -- ...` (five unit test files, including the existing outbound delivery suite) | **PASS: 5/5 suites, 89/89 tests**; recorded in `typescript(20261025-170947)` |
| `npm run test:integration -- tests/integration/woo-initial-send-fence.integration.test.ts` | **PASS: 1/1 suite, 5/5 tests** against PostgreSQL after the fourth incremental patch revision; recorded in `typescript(20261025-172449)` |
| `npx tsc --noEmit && echo "TypeScript PASS"` | **PASS**, explicit success marker in `typescript(20261025-180507)` |
| `git diff --check` and `git diff --cached --check` | No errors shown in `typescript(20261025-180507)` |
| `git commit` / `git push origin task/ARCH-046-BACKGROUND-004` | **PASS**; implementation commit `0c92e12` and new remote task branch confirmed in `typescript(20261025-180507)` |

Earlier incremental patch revisions exposed invalid **test-fixture** records for the recipient format and funded `UsageReservation`. Those errors were corrected without relaxing production database constraints. The final five-test PostgreSQL run is green. These four patch deliveries belong to the **same claimed developer workflow Attempt 1**; they are not four separately claimed workflow attempts.

The supplied logs do **not** establish a completed `npm run lint`, `npm run build`, full test suite, live Redis fault/concurrency integration run, or separately targeted Shopify/human/AI in-window STOP regression suites. Focused outbound delivery regression tests are included in the 89 passing unit tests, but should not be described as full cross-flow regression coverage. Such unverified items remain unchecked above for review.

### Execution / Worktree Evidence

- Canonical parent worktree named by the archive and startup record: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-046-BACKGROUND-004`.
- Dedicated implementation worktree shown by the terminal archive helper: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-046-BACKGROUND-004`.
- Implementation branch `task/ARCH-046-BACKGROUND-004` and the successful pushed commit are evidenced by the terminal log.
- The task's existing developer claim states that both task worktrees were prepared/synchronised with `origin/main` and that the recursive database submodule was initialised at gitlink `3f1f50b91c9e93ff9647a3d1d7f6fd46b9b888b9`. The current terminal capture **does not independently include** the launcher-resolved preparation packet, parent branch's Git common-dir/isolation proof, or a fresh start-of-attempt synchronisation command. Those must be checked by the architect against available task preparation evidence.
- The terminal log shows an untracked local `typescript` recording in the implementation worktree. It was **not included** in commit `0c92e12`.

### Deviations

No new database migration, new shared API, Woo follow-up engine or BG005 worker wiring was introduced. The unit and PostgreSQL suites were run, but the broader validation originally requested by this task is not fully evidenced in the supplied logs; this is explicitly disclosed rather than reported as passed.

### Assumptions

- `ARCH-048-BACKGROUND-004` continues to own the checkout lease, earlier observed-order preflight, first-send credit reservation and compensation. BG005 will compose the guarded sender when separately authorised.
- Existing durable Woo order observations only reflect events received by Moda. A missing Woo event cannot be inferred by this sender, nor can a Redis-only observation be claimed to be SQL-locked.
- Woo outbound remains default-off until the separate composition, developer activation and integrated system-test gates are satisfied.

### Unresolved Issues

- **Validation evidence gaps for review:** no completed broad repository lint/build, Redis-backed concurrency/fault-injection run, independently targeted Shopify/human/AI STOP regression suite or full billing source-attribution integration test was supplied. The architect should determine whether these require execution before acceptance and, if necessary, return specific Changes Requested to this same task.
- The latest terminal capture proves the implementation commit/push but not the independent physical worktree preparation and synchronisation packet required by `docs/agent-worktree-isolation-policy.md`. Reconcile with the existing claim evidence before acceptance.
- No BG005 worker wiring, Woo outbound activation, or end-to-end production send is claimed as part of this task.

### Architectural Concerns

- STOP committed before the Shop-locked provider permit blocks admission; STOP committed after the permit cannot retroactively retract a provider request. Tests exercise both orderings.
- The permit uses durable PostgreSQL state for atomic decisions; the previously accepted Redis checkout/order observation remains an earlier guarded boundary, not a phantom SQL lock. Undelivered Woo events remain an explicit architectural limitation.
- Provider-uncertain admissions must be reconciled, not blindly retried with a new first send or automatically compensated as though no dispatch occurred.

## Architect Review

### Review Status

Pending.

### Review Notes

Task definition narrowed to initial send + sequence-one retries; no implementation acceptance claimed.

### Reviewed Files

ARCH-048-BG004 service/adapters, existing general SQL STOP fence, ARCH-046-BG001, BG002 task definitions.

### Validation Reviewed

Static code review only; no BG004 implementation tests run.

### Architecture Conformance

Consistent with ARCH-048's initial-outreach-only boundary and default-off rollout.

### Follow-up

Only after BG002 complete may the architect promote this BG004 task to Ready. Woo follow-ups require separately approved future implementation work.

## Developer Self-Review - Changes Requested

### Review Decision

Attempt 1 is not accepted for developer completion. The implementation branch is committed and pushed, but the current Completion Report marks required Work Items, Acceptance Criteria and Validation incomplete and explicitly records evidence gaps.

### Required Corrections

- Complete and report the task-owned concurrency and fault cases: two-client initial-send admission, STOP-versus-permit ordering, observed paid/cancelled order versus send, provider-confirmed/uncertain/failed retry behavior, billing source attribution and compensation. Include read-after-commit validation for existing admissions.
- Complete and report the Shopify/general outbound and human/AI in-window STOP regressions. Add evidence that no Woo follow-up path was introduced and no Redis or HTTP operation occurs while SQL locks are held.
- Run the repository-declared relevant lint/build checks and any remaining focused/full checks required by the task; record exact commands and results. Do not report the broad checks as passing without evidence.
- Record canonical launcher preparation/synchronization evidence for the parent and implementation worktrees, including physical isolation and recursive submodule state, or attach the existing durable preparation packet that proves it.
- Update the Completion Report and task checkboxes only to reflect verified work. Keep Woo outbound default-off; do not wire BG005 or broaden task scope.

### State Transition

Returned to `ready`, with `executor: null`, `claimed_at: null`, and Attempt 1 unchanged. No new attempt is claimed by this review; the next `/moda_developer_create` invocation may claim Attempt 2.
