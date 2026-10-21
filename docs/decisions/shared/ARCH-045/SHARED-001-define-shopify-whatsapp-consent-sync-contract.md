---
id: ARCH-045-SHARED-001
architecture_id: ARCH-045
title: Define Shopify WhatsApp consent-state sync event on existing queue
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
updated: 2026-10-21
---
# Define Shopify WhatsApp consent-state sync event on existing queue

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** portable definition, **not** materialised in a developer task worktree or committed/pushed; no execution claim exists.

## Objective

Define one minimal published v1 **Shopify consent-state synchronisation** signal so an authenticated Shopify webhook can ask Background to refresh `CustomerPhone`. The event must never request a checkout re-evaluation or recovery wakeup.

## Context

The inspected Shopify webhook queue types accept checkout/cart/order/discount events, not the WhatsApp consent topic. A bounded cross-repository sync contract is required for asynchronous processing, but **reuse the existing Shopify BullMQ infrastructure**; do not introduce a dedicated recovery queue or consent-triggered scheduler.

## Scope

- Define `ShopifyWhatsAppConsentSyncJobV1Schema` (name can follow repository conventions), typed payload `{schemaVersion:1,shopId,shopifyCustomerId,deliveryId,triggeredAt}` and stable deterministic job identity. No customer phone, consent Boolean or checkout identity in the payload.
- Define a **distinct job name** routed through an existing approved Shopify webhook queue. Keep this sync job outside the checkout v2 event parser and explicit checkout-recovery event type; consumers validate their correct schema.
- Export stable runtime validator, job constants and identity helper through published Shared entrypoint(s); test malformed payload, duplicate delivery, cross-shop isolation and absence of checkout wakeup fields.

## Out of Scope

- No new BullMQ queue, separate queue schema for Woo, HTTP handler, provider lookup, CustomerPhone write, recovery candidate, recovery retry job or source publication in this implementation task.

## Requirements

- [ ] Exactly one canonical sync event; it cannot masquerade as checkout-created/updated or carry authority to send.
- [ ] All producers/consumers import published Shared schema, not local duplicates.
- [ ] Only existing queue plumbing is extended; no new infrastructure or recovery wakeup.

- Shopify `customer_id` webhook numeric form and GraphQL GID must converge using the *single* published `ARCH-045-SHARED-003` conversion; never accept arbitrary strings as a verified customer principal or use an unscoped customer numeric ID without the authenticated shop.

## Work Items

- [ ] Add the small versioned sync-event schema and existing-queue job name plus deterministic ID helper.
- [ ] Add strict validator/export/replay and queue compatibility tests.

- [ ] Include numeric/GID equality and malformed/other-resource customer IDs in producer/consumer contract fixtures.

## Interfaces / Contracts

**Owner:** moda_shared. **Published package:** `@modainteract/moda-interact-shared/shopify` (Node-only hashing subpath when required). **Producer:** `ARCH-045-SHOPIFY-001`. **Consumer:** `ARCH-045-BACKGROUND-003`. **Version:** 1. **Business effect:** update current `CustomerPhone` after provider verification; never locate/retry checkouts. No new queue.

## Dependencies

None

## Enables

- `ARCH-045-SHARED-002`

## Acceptance Criteria

- [ ] Versioned schema rejects PII/extra fields and malformed identity; deterministic ID deduplicates retries.
- [ ] Existing checkout event type remains valid/unchanged and sync is routed by its own job name.
- [ ] No new queue, recovery trigger or provider consent policy in Shared.

- [ ] Validated Shopify numeric ID and equivalent Customer GID bind to the same shop-scoped identity; invalid payload cannot be published as a trusted principal.

## Validation

- [ ] Focused shared schema/job identity tests, package entrypoint/export validation and `git diff --check`.

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
