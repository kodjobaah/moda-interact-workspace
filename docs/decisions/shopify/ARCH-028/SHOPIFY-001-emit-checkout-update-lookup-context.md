---
id: ARCH-028-SHOPIFY-001
architecture_id: ARCH-028
title: Emit compatible checkout.updated lookup context from Shopify
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 55
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-028-SHARED-004
  - ARCH-028-BACKGROUND-012
enables:
  - ARCH-028-SYSTEM-TEST-001
created: 2026-10-08
updated: 2026-10-08
---
# Emit compatible checkout.updated lookup context from Shopify

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Produce validated versioned checkout.updated events containing the canonical checkoutToken and only optional, trustworthy Shopify lookup context, after the Background consumer can accept the new version.

## Context

The current Shopify `normalizeCheckoutUpdatedPayload` returns only `{checkoutToken}` even if the verified Shopify webhook contains `cart_token`, `created_at` or `abandoned_checkout_url`. The current strict v2 event must remain unchanged for queued/older consumers. SHOPIFY-001 is a producer-only implementation after SHARED-004 and consumer-first BACKGROUND-012 acceptance.

## Scope

- Use the exact published Shared Shopify event contract from SHARED-004 and emit v3 only for `checkout.updated`; retain v2 for all other existing Shopify recovery-event variants.
- Preserve checkoutToken from the verified Shopify webhook as the sole checkout identity alongside tenant Shop ID; normalize only actually present optional `cart_token`, `created_at`, `abandoned_checkout_url` using existing validators/bounds.
- Keep webhook authentication, receipt/delivery IDs, tenant-scoped ordering key, queue acceptance/acknowledgement latency and deterministic deduplication unchanged.
- If context is absent in a legitimate update, emit a valid token-only v3 event and do not invent a URL/date or drop an authenticated business event solely on that basis.
- Use fixtures proving normalisation and at-least-once delivery, including missing and malformed optional context handling consistent with the published schema.

## Out of Scope

- Changing Background candidate scheduling or abandoned checkout lookup (BACKGROUND-012).
- Changing Shared event schemas or publishing Shared package.
- Using abandonedCheckoutUrl for deduplication, identity or primary ordering.
- New synchronous Shopify Admin API calls within webhook ingress.

## Requirements

- [ ] Shopify events remain keyed by `(shopId, checkoutToken)` and keep deterministic ordering keys.
- [ ] Producer begins emitting v3 only after consumer-first BACKGROUND-012 is Complete/architect-accepted.
- [ ] Optional lookup hints are validated and never fabricated.
- [ ] Other webhook topics and existing v2 contracts remain unchanged.
- [ ] Authenticated webhook durable-acceptance and fast-acknowledgement semantics do not regress.

## Work Items

- [ ] Install exact published Shared revision.
- [ ] Extend checkout-update normalizer and event builder for versioned optional lookup hints.
- [ ] Add regression tests covering absent/bad context, checkout identity, ordering and existing v2 events.
- [ ] Run task-relevant Shopify package tests/typecheck/build.

## Interfaces / Contracts

Producer `moda-interact`; consumer `moda-interact-background`; owner `moda-interact-shared`; runtime validator from exact SHARED-004 `@modainteract/moda-interact-shared/shopify` publication. v3 checkout.updated preserves required `checkoutToken` and adds optional nullable `cartToken`, `checkoutCreatedAt`, `abandonedCheckoutUrl` as Shopify lookup hints.

## Dependencies

- `ARCH-028-SHARED-004`
- `ARCH-028-BACKGROUND-012`

## Enables

- `ARCH-028-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Valid SHOP-scoped checkout.updated v3 always carries non-empty checkoutToken; URL is never used as identity.
- [ ] v2 producer paths for other Shopify topics continue to pass.
- [ ] Missing context does not cause fabricated values, webhook rejection or premature business filtering.
- [ ] Exact Shared publication revision is installed and upgraded Background consumer is accepted.
- [ ] Focused ingress contract/authentication/queue regression tests pass.

## Validation

Focused checkout normalization + webhook ingress/queue tests, repository-declared Shopify typecheck/build as relevant, `git diff --check`.

## Stop Condition

Complete defined work/acceptance/validation, fill the Completion Report, set status `review`, return to `moda_architect`, and STOP. Do not begin a dependent task.

## Implementation Notes

Preserve the existing minimal ingress boundary: receive/authenticate/normalize/durably enqueue/acknowledge. The URL, when present, is a retrieval hint and customer recovery link, not a business identifier. Do not synchronously query abandonedCheckouts in the webhook handler.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

Not Started.

### Validation Results

Not Run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
