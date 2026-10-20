---
id: ARCH-045-BACKGROUND-002
architecture_id: ARCH-045
title: Block unconsented recovery and notify merchant once
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
  - ARCH-045-DATABASE-001
  - ARCH-045-BACKGROUND-001
enables:
  - ARCH-045-BACKGROUND-003
  - ARCH-045-BACKGROUND-004
  - ARCH-045-SHOPIFY-002
  - ARCH-045-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-20
---
# Block unconsented recovery and notify merchant once

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** portable definition, **not** materialised in a developer task worktree or committed/pushed; no execution claim exists.

## Objective

Pause initial checkout recovery when Shopify WhatsApp consent cannot be verified and create one deduplicated merchant Support inbox notice without provider send or recovery credit.

## Context

`recovery-initiation.service.ts` currently applies recipient suppression then creates the initial outreach attempt and billing admission. `MerchantSupportMessage.sourceKey` already supports exactly-once merchant system notices.

## Scope

- Integrate BACKGROUND-001 consent reader after resolving a real Shopify customer and canonical recipient, **before** sequence-one outreach creation/billing; handle identity-unknown as not authorised for proactive sending.
- For absent/unsubscribed/mismatched/unknown customer, conditionally persist `DETECTED` + `WHATSAPP_CONSENT_MISSING` with `admissionBlockedAt`; 72-hour wait is from `detectedAt`. Distinguish retryable consent verification unavailability and never continue to a send on an error.
- Create or reuse one merchant Support SYSTEM message per recovery generation with deterministic `sourceKey=arch045:consent-missing:<recoveryId>` and safe text: consent not verified, no customer message and no recovery credit, eligible later opt-in may resume before expiry.
- Use existing shop-unique support thread and source-key uniqueness, handle repeated checkout events / retry / partial failure and expose bounded domain logging.
- Preserve other admission blocks, recipient suppression and capacity handling; never overwrite an unrelated block silently.

## Out of Scope

- No Shopify consent-update webhook ingestion/resumption (BACKGROUND-003).
- No new alert transport, merchant WhatsApp notification, new merchant Support schema or separate consent DB.
- No changes to no-recipient pre-materialisation behaviour or follow-up paths (BACKGROUND-004).

## Requirements

- [ ] Blocked initial recovery generates **zero** sequence-one billable attempts, credit reservations/commits and outbound provider sends.
- [ ] One (not N) Support SYSTEM notice, even after duplicate materialisation/retries; Support notification failures are retryable/repairable without allowing send.
- [ ] Only a still-DETECTED recovery in its own shop/generation is updated; never reactivate terminal recovery or erase other block reasons.
- [ ] Merchant-facing text is accurate and does not promise resumption after expiry, or confuse tracking consent with WhatsApp marketing consent.

## Work Items

- [ ] Inject consent gate into initial admission.
- [ ] Persist specific block and idempotent merchant notification.
- [ ] Test duplicates, races, failure of merchant-support DB write, no-charge invariant and snapshot identity uncertainty.

## Interfaces / Contracts

Consumes `RecoveryAdmissionBlockReason.WHATSAPP_CONSENT_MISSING` (DATABASE-001) and BACKGROUND-001 reader; produces existing `MerchantSupportMessage` SYSTEM with deterministic `sourceKey`. No new cross-service schema.

## Dependencies

- `ARCH-045-DATABASE-001`
- `ARCH-045-BACKGROUND-001`

## Enables

- `ARCH-045-BACKGROUND-003`
- `ARCH-045-BACKGROUND-004`
- `ARCH-045-SHOPIFY-002`
- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] No consent -> DETECTED+specific reason+one merchant Support notice, zero charge/provider/sequence-one attempt.
- [ ] Repeated events, two concurrent workers and transient Support write failures converge without duplicate notices or accidental admission.
- [ ] Subscribed matching customer follows unchanged normal recovery admission, with an additional near-provider fresh consent verification/release if state changed after any provisional reservation.
- [ ] Provider failure is fail-closed and handled retryably without mislabelling it as explicit subscribed consent.

## Validation

- [ ] Focused Background initial-recovery/billing mock tests and disposable PostgreSQL duplicate/atomicity evidence.
- [ ] Provider-send spy proves blocked path sends zero; `git diff --check` and repository-declared build.

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

Use the 2026-10-20 snapshot for orientation; revalidate active code/configuration when the task is materially claimed. ARCH-045's provisional 72-hour consent-wait deadline is the exact v1 task contract unless the developer and architect amend it before implementation.

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
