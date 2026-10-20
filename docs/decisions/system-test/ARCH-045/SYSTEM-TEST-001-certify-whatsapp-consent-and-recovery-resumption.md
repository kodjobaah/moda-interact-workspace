---
id: ARCH-045-SYSTEM-TEST-001
architecture_id: ARCH-045
title: Certify consent-blocked recovery merchant notice and resumption
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
  - ARCH-045-DATABASE-001
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
# Certify consent-blocked recovery merchant notice and resumption

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** portable definition, **not** materialised in a developer task worktree or committed/pushed; no execution claim exists.

## Objective

Certify the real Shopify merchant/customer checkout-recovery lifecycle when WhatsApp consent is missing, later granted, withdrawn, or expires, including merchant notice and credit-accounting invariants.

## Context

Cross-service behaviour crosses Shopify authenticated webhooks, Shared contract, Background worker, PostgreSQL, Redis/BullMQ, Shopify Admin consent read and Support inbox. This terminal validation executes **only after all implementation and Shared publication tasks are architect-accepted Complete**, with developer manual validation allowed first.

## Scope

- Exercise real authenticated Shopify checkout and consent-change ingress, real Shared job transport and Background worker processing with deterministic Shopify/Meta provider fixtures or test-shop verification where possible.
- Verify merchant Support inbox system message once and no provider send/credit reservation/commit when consent is absent.
- Verify later verified Shopify SUBSCRIBED matches same customer/number, checkout remains abandoned and within 72h -> existing recovery resumes and sends once.
- Verify duplicate/out-of-order events, shop/customer/recipient mismatch, missing Shopify ID, unsubscribed/revoked, completed order, expiry, dropped expiry wakeup repair, provider/API failures, and sequence-two scheduled/merchant templates.
- Record precise billing/entitlement and outbound provider evidence, correlation paths and terminal state.

## Out of Scope

- Do not implement production features, change database schema, repair provider defects in test task or use production customer records.
- No model language-quality tests or unauthorised real WhatsApp sends.
- No new system-test dependency for non-system-test tasks.

## Requirements

- [ ] Black-box tests use normal app->queue->worker->database->provider boundaries, not private service method mocks as sole evidence.
- [ ] Missing Docker/Shopify test store/permissions is an explicit incomplete gate, not an invented PASS.
- [ ] Proof of no credit consumption includes actual durable entitlement/counter/admission rows, not only mocked send count.
- [ ] No plaintext sensitive customer payload or token in evidence logs.

## Work Items

- [ ] Create isolated reusable fixtures, executors and assertions in the consolidated `moda-interact-system-test` repository.
- [ ] Run success, waiting, later consent, revoked, expired and duplicate concurrency scenarios.
- [ ] Publish evidence paths, observable statuses and billing/send checks in the completion report.

## Interfaces / Contracts

Uses actual published Shared v1 consent event and actual task APIs implemented by ARCH-045-DATABASE-001, SHARED-001/002, SHOPIFY-001/002 and BACKGROUND-001/002/003/004.

## Dependencies

- `ARCH-045-DATABASE-001`
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

- [ ] Absent consent: DETECTED+reason, one inbox message, zero send, zero credit reserved/consumed.
- [ ] Later eligible opt-in: re-entry into same recovery generation and exactly one verified message/credit result.
- [ ] Revocation/late event/mismatch/completed checkout/expired recovery: zero new provider sends/credits.
- [ ] Expiry is eventual even without consent webhook, and duplicate/out-of-order delivery cannot double-send/charge.
- [ ] Scheduled and human post-window templates respect consent; approved in-window human replies unaffected.

## Validation

- [ ] Consolidated system-test targeted Shopify lifecycle and billing suite; docker/PostgreSQL/Redis orchestration, evidence logs and `git diff --check`.
- [ ] If a real Shopify test-store opt-in cannot be exercised, explicitly separate provider-contract simulation evidence from live Shopify verification; do not claim full live certification.

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
