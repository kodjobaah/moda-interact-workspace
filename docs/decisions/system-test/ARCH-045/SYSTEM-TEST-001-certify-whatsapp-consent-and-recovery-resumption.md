---
id: ARCH-045-SYSTEM-TEST-001
architecture_id: ARCH-045
title: Certify no Shopify recovery without consent and later first creation
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-045-SHARED-002
  - ARCH-045-SHOPIFY-001
  - ARCH-045-SHOPIFY-002
  - ARCH-045-BACKGROUND-001
  - ARCH-045-BACKGROUND-002
  - ARCH-045-BACKGROUND-003
  - ARCH-045-BACKGROUND-004
enables: []
created: 2026-10-20
updated: 2026-10-20
---
# Certify no Shopify recovery without consent and later first creation

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** portable definition, **not** materialised in a developer task worktree or committed/pushed; no execution claim exists.

## Objective

Black-box certify that Shopify never creates an initial `CheckoutRecovery` before current WhatsApp permission, and that later valid consent can trigger **first recovery creation** for a still-eligible checkout.

## Context

This is terminal validation after all implementation and Shared publication tasks are architect-accepted Complete, with developer manual testing allowed first. Previous `DETECTED+WHATSAPP_CONSENT_MISSING` and 72-hour expiry scenarios are superseded.

## Scope

- Exercise authenticated Shopify checkout and WhatsApp-consent webhook ingress, published Shared payload, Background workers, actual PostgreSQL/Redis state and a stub/controlled Shopify+Meta provider.
- Abandoned checkout lacking valid consent: assert **zero CheckoutRecovery rows**, zero sequence-one attempt, credit reservation/consumption and provider sends; **one checkout-keyed Support SYSTEM notice**.
- Later Shopify `SUBSCRIBED`: with safely linked still-identifiable checkout, same shop/customer/recipient, confirmed abandon/unpaid state and ordinary maturity/eligibility, assert **one first recovery** then correct billing/provider result. If checkout/candidate is genuinely gone, confirm safe no-op; do not invent missing checkout state.
- Test customer/phone mismatch, no ID, API outage, duplicate/out-of-order webhook, abandoned checkout completed meanwhile, current revoked consent, follow-ups and failed merchant notice repair.
- Verify no arbitrary 72-hour consent expiration; checkout eligibility may independently expire. Verify collection/reader not used to permit unrelated tracking consent.

## Out of Scope

- No actual production messaging, source-code implementation or fabricated integration PASS when live Shopify fixture unavailable.

## Requirements

- [ ] Black-box production-like boundaries, durable DB credit/candidate evidence, tenant isolation and redacted logs.
- [ ] Missing Docker/test-shop capability recorded as incomplete, not PASS.

## Work Items

- [ ] Add normal reusable fixtures/assertions into consolidated system-test repository.
- [ ] Execute no-consent/no-row, later-consent/new-row, unavailable checkout and revocation/follow-up scenarios.
- [ ] Record evidence paths, provider outcomes, Support source keys and billing invariant results.

## Interfaces / Contracts

Published Shared v1 wakeup; ARCH-045-SHARED-001/002, SHOPIFY-001/002, BACKGROUND-001/002/003/004. **No ARCH-045-DATABASE-001 dependency**.

## Dependencies

- `ARCH-045-SHARED-002`
- `ARCH-045-SHOPIFY-001`
- `ARCH-045-SHOPIFY-002`
- `ARCH-045-BACKGROUND-001`
- `ARCH-045-BACKGROUND-002`
- `ARCH-045-BACKGROUND-003`
- `ARCH-045-BACKGROUND-004`

## Enables

None

## Acceptance Criteria

- [ ] Missing/unknown consent => **zero CheckoutRecovery**, zero send/credit and one merchant checkout notice.
- [ ] Later valid consent + retrievable eligible checkout => exactly one first recovery, no double send/charge.
- [ ] Lost/expired/completed checkout, revoked or wrong recipient, duplicate event => no recovery/send; no 72-hour consent timer.
- [ ] Proactive existing-recovery follow-ups remain consent-gated; appropriate in-window replies unaffected.

## Validation

- [ ] Consolidated system-test checkout/recovery/credit assertions, PostgreSQL and BullMQ evidence, provider-contract fixture vs live Shopify tests clearly distinguished; `git diff --check`.

## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. For publication task, do not rerun implementation validation.

## Implementation Notes

This is terminal validation. Do not mark ARCH-045 Implemented until the architect reviews complete cross-service evidence.

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
