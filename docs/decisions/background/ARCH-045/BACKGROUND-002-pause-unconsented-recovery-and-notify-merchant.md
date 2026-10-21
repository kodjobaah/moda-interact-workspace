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
  - ARCH-045-BACKGROUND-005
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

- **C3:** The consent and local no-contact check must occur **before the first CheckoutRecovery INSERT**, not merely before a later optional admission gate. Existing `recovery-initiation.service.ts` currently creates the row first; move/restructure the admission seam while retaining idempotent creation and original checkout eligibility checks.
- Apply the same injectable Background-owned consent policy to **all business-initiated first-send entries**: matured pending candidate, capacity-unblocked `DETECTED` recovery (`recovery-capacity-resume-processor.service.ts`), suppression re-entry, any initial send retries and legacy pre-existing DETECTED rows. Deny first-send on stale/changed/opted-out identity without consuming billing reservation or attempting Meta.
- Merchant notice sourceKey is shop + hashed stable checkout reference (never a raw customer phone or checkout token). Distinguish customer not opted in, identity ambiguous, merchant collector not configured, and temporary provider/verification outage; dedupe and bound notices per shop without inventing a new table.
- Require an up-to-date E.164-equivalent recipient and a *current* non-redacted customer identity; after phone change or privacy erasure, the previous pending candidate is not eligible to materialise.

- First recovery materialisation and every business-initiated first-send retry must check both exact CustomerPhone consent/no-contact **and** the durable existing shop/recipient STOP safety fence, even if Customer lookup is ambiguous.

## Work Items

- [ ] Gate existing matured-candidate pre-materialisation path using BACKGROUND-001 current phone plus provider refresh.
- [ ] Add checkout-keyed merchant system notice with idempotent deduplication.
- [ ] Test absent consent, subsequent real checkout-event re-evaluation, no-event no-op, API outage, duplicate job, paid checkout and no send/charge.

- [ ] Trace and instrument all first-send/creation entry points, including capacity/suppression/legacy re-entries; implement one common pre-create plus first-send policy gate.
- [ ] Add idempotent checkout-keyed merchant Support notices with separate copy for non-consent versus verification outage, volume cap and no PII.

## Interfaces / Contracts

Consumes `ARCH-045-DATABASE-002` via BACKGROUND-001 current phone consent/Shopify native authority; existing checkout reconciliation and Support source-key APIs. No consent-wakeup listener, no `WHATSAPP_CONSENT_MISSING` enum.

## Dependencies

- `ARCH-045-BACKGROUND-001`
- `ARCH-045-BACKGROUND-005`

## Enables

- `ARCH-045-BACKGROUND-004`
- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Without verified grant, missing/revoked/unknown => zero CheckoutRecovery/Meta send/recovery credit, and one appropriate checkout-keyed merchant notice.
- [ ] After later opt-in, only an actual **normal** checkout reconciliation can create first recovery if live checkout/order and all gates still qualify.
- [ ] No candidate-retention promise, consent-specific deadline, new queue or provider-outage bypass.

- [ ] No initial recovery row for a first-ever unconsented checkout; an older DETECTED row can remain for history but cannot send after grant withdrawal.
- [ ] Candidate creation/retry/resumption never claims initial send or a credit on no-contact, unavailable consent, reused phone, redaction or changed recipient.

## Validation

- [ ] Focused Background candidate/materialisation and merchant Support tests, no event vs next real checkout update, billing/notification/timeout assertions, `git diff --check`.

- [ ] Run direct initiation, candidate maturation, capacity resume, suppression re-entry, repeated webhook/candidate, recipient rotation, STOP and billing compensation tests; assert zero Meta sends and first-charge attempts on denial.

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
