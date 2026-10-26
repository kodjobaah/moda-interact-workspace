---
id: ARCH-050-BACKGROUND-003
architecture_id: ARCH-050
title: Wire WooCommerce confirmed initial outreach to the common Support notice
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
  - ARCH-050-BACKGROUND-001
  - ARCH-048-BACKGROUND-005
enables:
  - ARCH-050-SYSTEM-TEST-002
created: 2026-10-26
updated: 2026-10-26
---

# Wire WooCommerce confirmed initial outreach to the common Support notice

## Architecture

Architecture ID: `ARCH-050`. Architecture document: `docs/architecture/ARCH-050-merchant-recovery-initial-outreach-support-notifications.md`. Coordinator: `moda_architect`.

## Objective

Attach deduplicated merchant Support notifications to the existing guarded WooCommerce first-send finalisation without opening its production outbound gate or scheduling a follow-up.

## Context

`src/services/woocommerce-recovery/woo-recovery-outreach.adapters.ts` owns the `finalize.confirmed` adapter; `woo-recovery-outreach.service.ts` currently enables outbound exclusively under test mode. ARCH-048-BACKGROUND-005 owns its existing composition.

## Scope

**Modify only:** `moda-interact-background/src/services/woocommerce-recovery/woo-recovery-outreach.adapters.ts` and a focused test (e.g. `tests/unit/services/woocommerce-recovery/woo-initial-outreach-notice.test.ts`). Touch `tests/integration/woo-recovery-composed-services.integration.test.ts` and existing Woo first-send tests only when wiring assertions require it.

**Inspect without changing:** `src/services/woocommerce-recovery/woo-recovery-outreach.service.ts`, `src/services/woocommerce-recovery/contracts.ts`, `src/services/checkout-recovery/recovery-initial-outreach-support-notice.*`. No WordPress/plugin/API files belong to this task.

## Out of Scope

- Enabling live Woo outbound; changing ARCH-048 worker routing, order/checkout capture, ARCH-046 final SQL consent fence, human handover or merchant UI.

## Requirements

- Within `createWooRecoveryOutreachService(...).finalize.confirmed`, keep current guards requiring sequence 1, `followUpDueAt === null`, conversation ownership and the existing billing `commitSuccessfulInitiation` call.
- Replace the adapter's local `markWaitingAfterConfirmedSend(attempt.id,...)` and independent replay-validation branch with `recoveryInitialOutreachSupportNoticeService.finalizeConfirmedInitial({ shopId: recovery.shopId, checkoutRecoveryId: recovery.id, outreachAttemptId: attempt.id, outboundMessageId: message.id, sentAt: message.sentAt, followUpDueAt: null })`.
- Accept `created`, `disabled`, `replayed` outcomes and keep `checkoutRecovery.updateMany({id,shopId,status:"DETECTED" ...})` after successful finaliser completion.
- Never schedule Shopify's `ensureScheduledInitialFollowUp`, never add Woo sequence 2, and never invoke the notice primitive for `HUMAN` messages.
- Preserve `WooRecoveryOutreachService.enabled()` test-only outbound gate (`NODE_ENV==="test"` with injected `enableTestOutbound`), guarded provider sender and ARCH-046 final-send STOP/consent security. No setting is allowed to bypass these.
- Preserve existing error propagation/compensation boundary: a confirmed external send + Support persistence failure is retried using the existing durable provider admission, not resent/charged again.

## Work Items

- [ ] Import/consume BACKGROUND-001 finalisation interface and singleton inside Woo adapter's `finalize.confirmed` callback.
- [ ] Remove only the now-redundant adapter-local attempt transition and replay check; leave Woo guard, billing and recovery status update unchanged.
- [ ] Add tests for enabled/disabled, duplicate, exception after confirmed provider state, no Shopify follow-up, HUMAN exclusion and default test-only outbound gate.

## Interfaces / Contracts

- Same `ConfirmedInitialOutreachFinalizer.finalizeConfirmedInitial(ConfirmedInitialRecoveryOutreachInput)` port owned by BACKGROUND-001; Woo always passes `followUpDueAt: null`.
- The existing `WooOutreachDependencies["finalize"]["confirmed"]` signature and Woo checkout/coordinator inputs remain unchanged; adapter consumes port internally.
- No new API endpoint, BullMQ event, WordPress call or production sender enablement.

## Dependencies

- `ARCH-050-BACKGROUND-001` must be `complete` in canonical task metadata before claim.
- `ARCH-048-BACKGROUND-005` must be `complete` in canonical task metadata before claim.

## Enables

- `ARCH-050-SYSTEM-TEST-002` may become eligible only after architect acceptance and Complete state.

## Acceptance Criteria

- [ ] Same verified initial automated Woo send causes one Support notice iff merchant opted in, and initial recovery status updates exactly as before.
- [ ] Retries/duplicate confirmed provider results do not create duplicate alerts, extra credits or new outbound messages.
- [ ] Woo test-only gate and final-send consent/STOP protections remain enforced, follow-up scheduling stays absent.
- [ ] Integration can run with existing Woo test fixtures and injected guarded sender; no production Meta send required.

## Validation

- [ ] Focused Woo adapter unit test and `tests/integration/woo-recovery-composed-services.integration.test.ts`, plus existing `woo-initial-send-fence` integration tests via declared `scripts/test-integration.mjs` when relevant.
- [ ] `npm run build`, targeted ESLint, `git diff --check`; record test-only outbound configuration as evidence.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, update this task to `review`, provide the Completion Report, return control to `moda_architect`, and **STOP**. Do not start dependent work. A system-test task is terminal and cannot be used as a prerequisite for implementation.

## Implementation Notes

BACKGROUND-001 owns the transaction and code/version contract. BACKGROUND-003 only integrates the Woo `finalize.confirmed` path; this separation deliberately avoids merge conflicts with BACKGROUND-002. Existing `ARCH-048-BACKGROUND-005` must be `complete` in canonical task YAML before claim (it is complete in the inspected 2026-10-26 snapshot); do not reopen it merely for this notification.

## Completion Report

### Status

Not Started.

### Files Changed

None (definition only).

### Work Completed

None.

### Validation Results

Not executed; no implementation claimed.

### Deviations

None.

### Assumptions

The task is based on the 2026-10-26 uploaded snapshot and must recheck current canonical code during execution.

### Unresolved Issues

None recorded at definition time.

### Architectural Concerns

Return newly discovered cross-repository/schema/security/contract issues to `moda_architect`.

### Task Branch / Worktree Evidence

Not materialised. Launcher-resolved parent/implementation task worktree, synchronization and branch evidence are required at execution.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not yet reviewed.

### Follow-up

None.
