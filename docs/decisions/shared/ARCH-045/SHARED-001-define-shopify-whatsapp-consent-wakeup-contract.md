---
id: ARCH-045-SHARED-001
architecture_id: ARCH-045
title: Define Shopify WhatsApp consent-update event contract
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-045-SHARED-002
created: 2026-10-20
updated: 2026-10-20
---
# Define Shopify WhatsApp consent-update event contract

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** portable definition, **not** materialised in a developer task worktree or committed/pushed; no execution claim exists.

## Objective

Publish one canonical **source-defined** v1 queue payload and deterministic identity for Shopify WhatsApp-consent change wakeups consumed by Background.

## Context

Shopify ingress and Background use published `@modainteract/moda-interact-shared/shopify` event contracts. No cross-service consent-change contract currently exists.

## Scope

- Add `ShopifyWhatsAppConsentChangedJobV1Schema`, inferred TypeScript type, queue/job constants and deterministic job ID helper to the appropriate browser-safe and Node-only Shared subpaths.
- Payload is exactly `{schemaVersion: 1, shopId, shopifyCustomerId, deliveryId, triggeredAt}`; customer identifier is a numeric string, `triggeredAt` is an ISO timestamp or null; fields validated and bounded.
- Add strict schema tests and deterministic id tests, including cross-shop delivery collisions and unknown payload keys.

## Out of Scope

- No Shopify ingress, Background worker, DB schema or provider consent policy.
- No raw phone number, email, webhook body, consent Boolean or presumed `SUBSCRIBED` state in the queue.
- No publication in this implementation task.

## Requirements

- [ ] One canonical queue/job name dedicated to customer WhatsApp consent wakeups; do not put an incompatible job into the existing checkout-event worker queue.
- [ ] No provider state is trusted in the event; consumer must query Shopify current state.
- [ ] Node hashing, if needed, stays out of browser-safe Shared entrypoints; no local duplicate helpers in producer/consumer.

## Work Items

- [ ] Implement canonical Zod schema, constants and identity helper.
- [ ] Export typed symbols through approved Shared entrypoints.
- [ ] Add invalid/duplicate/collision contract tests.

## Interfaces / Contracts

**Owner:** moda_shared. **Package:** `@modainteract/moda-interact-shared/shopify` and Node-only helper as needed. **Producer:** moda-interact. **Consumer:** moda-interact-background. **Runtime schema:** `ShopifyWhatsAppConsentChangedJobV1Schema`. **Version:** `1`.

## Dependencies

None

## Enables

- `ARCH-045-SHARED-002`

## Acceptance Criteria

- [ ] Valid v1 payload passes; malformed ID, oversized data, wrong version or extra PII fields fail.
- [ ] Duplicate delivery has the same job ID; different shops/IDs cannot collide.
- [ ] No application repo or Shopify/DB credential code is introduced.

## Validation

- [ ] Repository-declared Shared focused schema/helper tests, build/exports checks and `git diff --check`.

## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. For publication task, do not rerun implementation validation.

## Implementation Notes

Use existing Shopify Shared naming/style. Preserve published export compatibility. Stop at review: publication is a separate task.

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

Use the 2026-10-20 snapshot for orientation; revalidate active code/configuration when the task is materially claimed. ARCH-045 does not impose a consent-expiry window; current Shopify consent and actual checkout eligibility are separate.

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
