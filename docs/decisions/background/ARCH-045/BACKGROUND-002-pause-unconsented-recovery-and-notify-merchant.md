---
id: ARCH-045-BACKGROUND-002
architecture_id: ARCH-045
title: Skip unconsented Shopify recovery creation and notify merchant
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
  - ARCH-045-BACKGROUND-001
enables:
  - ARCH-045-BACKGROUND-004
  - ARCH-045-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-21
---
# Skip unconsented Shopify recovery creation and notify merchant

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** portable definition, **not** materialised in a developer task worktree or committed/pushed; no execution claim exists.

## Objective

On **ordinary** Shopify pending-checkout maturation/reconciliation, read verified current `CustomerPhone` consent and create **no CheckoutRecovery** without valid matching permission; notify the merchant via a checkout-keyed Support SYSTEM notice.

## Context

ARCH-045-BACKGROUND-001 owns local-current consent and provider refresh. The existing matured candidate checks checkout/order and recipient before `RecoveryInitiationService` creates a recovery; insert the admission gate there, not as a `DETECTED` recovery block. A consent webhook itself does not schedule candidates.

## Scope

- At normal checkout candidate maturity, resolve the shop/customer/active exact phone, read current CustomerPhone consent, and use BACKGROUND-001 authoritative refresh on unknown/unverified state before allowing the first `RecoveryInitiationService` creation. Recheck provider state as near outbound as required by Background-001.
- Without valid consent create **zero CheckoutRecovery**, provider send, recovery credit reservation/charge or outreach attempt. A fresh provider outage is distinct from lack of consent, fails closed and follows bounded existing retry/error policy.
- Use existing `MerchantSupportMessage(kind=SYSTEM)` with deterministic bounded `sourceKey(shopId,checkoutToken,reason)`, no recovery ID and no PII. Distinguish missing customer consent, unavailable verification, and other recovery ineligibility.
- Do **not** retain candidates indefinitely or create a consent-wait record. If a subsequent ordinary checkout event schedules a new candidate, apply the same current-consent test. If no future reconciliation runs, no delayed recovery is promised.
- Preserve original checkout/order/entitlement/recipient-suppression and credit idempotency, compensation and normal candidate cleanup.

## Out of Scope

- No `RecoveryAdmissionBlockReason` migration, `DETECTED` waiting record, new Support table, custom consent-expiry job or customer WhatsApp message seeking opt-in.
- No consent webhook consumer (BACKGROUND-003) or follow-up changes (BACKGROUND-004).

## Requirements

- [ ] Never create a recovery, attempt or committed credit without valid shop/customer/exact-phone current permission.
- [ ] One idempotent merchant Support notice per checkout/reason; transient API verification outage is not misrepresented as customer refusal.
- [ ] The consent event handler does not call this service to trigger recovery; only normal checkout reconciliation enters this path.

## Work Items

- [ ] Gate existing matured-candidate pre-materialisation path using BACKGROUND-001 current phone plus provider refresh.
- [ ] Add checkout-keyed merchant system notice with idempotent deduplication.
- [ ] Test absent consent, subsequent real checkout-event re-evaluation, no-event no-op, API outage, duplicate job, paid checkout and no send/charge.

## Interfaces / Contracts

Consumes `ARCH-045-DATABASE-002` via BACKGROUND-001 current phone consent/Shopify native authority; existing checkout reconciliation and Support source-key APIs. No consent-wakeup listener, no `WHATSAPP_CONSENT_MISSING` enum.

## Dependencies

- `ARCH-045-BACKGROUND-001`

## Enables

- `ARCH-045-BACKGROUND-004`
- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Without verified grant, missing/revoked/unknown => zero CheckoutRecovery/Meta send/recovery credit, and one appropriate checkout-keyed merchant notice.
- [ ] After later opt-in, only an actual **normal** checkout reconciliation can create first recovery if live checkout/order and all gates still qualify.
- [ ] No candidate-retention promise, consent-specific deadline, new queue or provider-outage bypass.

## Validation

- [ ] Focused Background candidate/materialisation and merchant Support tests, no event vs next real checkout update, billing/notification/timeout assertions, `git diff --check`.

## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. For publication task, do not rerun implementation validation.

## Implementation Notes

Prefer a small consent admission/merchant notice service injected into the existing initiation method. Use Shared logging; do not expand a large orchestration module with generic logging/transport logic. Existing Support inbox copy is delivered by the app, not via Meta WhatsApp.

Before claiming, use the deterministic `/moda-task` launcher and its **actual** prepared packet, read the task's complete current Architect Review, and verify task/dependency status in the developer's canonical workspace. Preserve `docs/decisions/**/_index.md` untouched until the developer explicitly closes the architecture documentation session. New runtime structured logging uses `@modainteract/moda-interact-shared/logging` where applicable. No source outside this task's owner repository may be changed unless explicitly authorised by the architecture.

## Completion Report

### Status

Not Started — external portable definition, not materialised.

### Files Changed

None — not implemented.

### Work Completed

None.

### Validation Results

Not run; the supplied snapshot is not the developer's task worktree.

### Deviations

None.

### Assumptions

Use the 2026-10-20 snapshot only as a baseline; verify current active code on task claim. Consent has no fixed 72-hour wait or expiry; checkout eligibility follows the authoritative lifecycle.

### Unresolved Issues

None recorded at definition time; report any discovered cross-repository dependency rather than implementing outside ownership.

### Architectural Concerns

None recorded at definition time.

## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

None.

### Reviewed Files

None — portable definition only.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
