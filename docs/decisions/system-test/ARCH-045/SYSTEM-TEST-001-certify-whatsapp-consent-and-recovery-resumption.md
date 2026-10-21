---
id: ARCH-045-SYSTEM-TEST-001
architecture_id: ARCH-045
title: Certify Shopify phone-consent sync and normal reconciliation gating
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
  - ARCH-045-DATABASE-002
  - ARCH-045-SHARED-002
  - ARCH-045-SHOPIFY-001
  - ARCH-045-SHOPIFY-002
  - ARCH-045-BACKGROUND-001
  - ARCH-045-BACKGROUND-002
  - ARCH-045-BACKGROUND-003
  - ARCH-045-BACKGROUND-004
  - ARCH-045-SHARED-003
  - ARCH-045-DATABASE-003
  - ARCH-045-SHOPIFY-003
  - ARCH-045-SHOPIFY-004
  - ARCH-045-SHOPIFY-005
  - ARCH-045-BACKGROUND-005
enables: []
created: 2026-10-20
updated: 2026-10-21
---
# Certify Shopify phone-consent sync and normal reconciliation gating

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** portable definition, **not** materialised in a developer task worktree or committed/pushed; no execution claim exists.

## Objective

Black-box certify Shopify native consent changes update **current CustomerPhone** but do **not** trigger recovery, and that **the next ordinary checkout reconciliation** reads the latest consent before first recovery creation.

## Context

Terminal validation after all implementation, migration and Shared publication tasks are architect-accepted. Old `DETECTED+WHATSAPP_CONSENT_MISSING`, 72-hour consent wait and immediate-consent-webhook recovery scenarios are superseded.

## Scope

- Exercise authenticated Shopify consent-change webhook to published Shared existing-queue sync job, Background current Shopify GraphQL read, correct `commerce.CustomerPhone` update and absence of any checkout candidate/CheckoutRecovery/charge/notice side effect **from consent event alone**.
- Exercise normal abandoned-checkout event with missing/unknown consent: zero recovery, sequence-one attempt, provider sends or credit, one shop+checkout-keyed merchant Support notice.
- Later native SUBSCRIBED change with **no further checkout event**: assert phone state updates but no new recovery. Then emit a real normal checkout update/reconciliation for the same still-abandoned/unpaid checkout: assert one first recovery, correct billing and no duplicate send.
- Exercise no subsequent checkout event, removed/matured candidate, completed checkout, changed exact phone or customer, duplicate/out-of-order sync, sync outage, local stale grant revoked remotely, follow-up final pre-send check and redacted diagnostics.
- No 72-hour consent expiry. Source authority and checkout business eligibility remain independent.

- **Release-blocking C1-C6:** Include phone-only legacy merge, two customers sharing the number, UK local vs `+44`, ambiguous country, changed phone, missing Shopify guest/customer identity, provider 200-with-errors, numeric webhook vs GID, redaction tombstone and old-sync replay, recipient STOP and merchant-processed opt-out.
- Trace every first send entry: matured candidate, direct initiation, suppression/capacity unblocking, existing DETECTED history, scheduled sequence-two, merchant post-window human template; assert current consent and short SQL fence under concurrent revocation.
- Exercise real `customers/data_request` export and `customers/redact` erasure including historical CustomerPhone rows, and confirm no rehydration; do not treat a 200 webhook acknowledgement with no actual privacy handling as compliance.
- Observe bounded Support notices and retry behaviour, consent change without subsequent checkout event (no recovery), and later legitimate normal checkout update (first recovery if still eligible).

## Out of Scope

- No actual production messaging, source-code implementation or fabricated integration PASS when live Shopify fixture unavailable.

## Requirements

- [ ] Black-box production-like boundaries, durable DB credit/candidate evidence, tenant isolation and redacted logs.
- [ ] Missing Docker/test-shop capability recorded as incomplete, not PASS.

## Work Items

- [ ] Build consolidated black-box fixtures for local CustomerPhone plus Shopify provider authority, webhook and checkout/event queue.
- [ ] Run no-grant, webhook-only no-recovery, later genuine checkout reconciliation, duplicate/stale and outbound revoked tests.
- [ ] Record DB/customer-phone/provider/merchant Support and credits evidence with explicit missing-live-Shopify gaps.

## Interfaces / Contracts

ARCH-045-DATABASE-002, published SHARED-001/002 **sync** event, SHOPIFY-001/002, BACKGROUND-001/002/003/004. No consent-driven recovery wakeup or superseded DATABASE-001.

## Dependencies

- `ARCH-045-DATABASE-002`
- `ARCH-045-SHARED-002`
- `ARCH-045-SHOPIFY-001`
- `ARCH-045-SHOPIFY-002`
- `ARCH-045-BACKGROUND-001`
- `ARCH-045-BACKGROUND-002`
- `ARCH-045-BACKGROUND-003`
- `ARCH-045-BACKGROUND-004`
- `ARCH-045-SHARED-003`
- `ARCH-045-DATABASE-003`
- `ARCH-045-SHOPIFY-003`
- `ARCH-045-SHOPIFY-004`
- `ARCH-045-SHOPIFY-005`
- `ARCH-045-BACKGROUND-005`

## Enables

None

## Acceptance Criteria

- [ ] Consent change updates exact CustomerPhone and **alone causes no recovery, candidate or send**.
- [ ] Without consent, ordinary reconciliation creates zero recovery/credit with correctly scoped Support notice.
- [ ] A **subsequent actual** reconciliation on eligible checkout can create exactly one first recovery after grant; without event there is no guaranteed re-evaluation.
- [ ] Late revocation blocks send/follow-up even if local mirror stale; no arbitrary 72-hour clock.

- [ ] Verified no recovery before consent; no initial or proactive send after STOP/erasure/source switch; no customer identity leakage or Meta charge on denial.
- [ ] Shopify export/erase paths produce verifiable outcomes and old events do not resurrect erased phone/consent state.

## Validation

- [ ] Consolidated PostgreSQL/BullMQ and Shopify provider evidence, billing/Support assertions, trusted vs stubbed provider boundaries, `git diff --check`.

- [ ] Realistic queued event/DB and provider/mock tests cover all review cases rather than only isolated task mocks.

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
