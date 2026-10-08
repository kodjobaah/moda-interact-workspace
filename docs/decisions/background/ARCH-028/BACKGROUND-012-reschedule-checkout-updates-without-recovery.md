---
id: ARCH-028-BACKGROUND-012
architecture_id: ARCH-028
title: Reschedule token-identified checkout updates after missing recipient
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 51
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-028-BACKGROUND-007
  - ARCH-028-SHARED-004
enables:
  - ARCH-028-SHOPIFY-001
created: 2026-10-08
updated: 2026-10-08
---
# Reschedule token-identified checkout updates after missing recipient

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Consume the published compatible checkout.updated event and schedule an idempotent pending candidate when no Shop/checkout candidate or recovery survives the earlier missing-recipient outcome.

## Context

BACKGROUND-007 allows a no-recipient candidate to finish without materialising a recovery. Current checkout.updated handling discards no-pending/no-recovery events as `recovery-not-found`. Candidate identity is Shop + checkoutToken; the current provider lookup needs separate bounded URL/time context to fetch a fresh abandoned checkout. A v2 event may legitimately lack that context; it must remain safe.

## Scope

- Install the exact accepted Shared revision published by SHARED-004 and parse both strict v2 recovery events and v3 checkout.updated through the canonical runtime parser.
- For `(shopId, checkoutToken)` with no pending candidate and no CheckoutRecovery, schedule exactly one fresh pending candidate using the existing queue/index/lock semantics, not abandonedCheckoutUrl as its identity.
- Carry only validated optional URL/creation-time/cart context when available; never infer a URL from the token or substitute receivedAt for creation time to defeat the bounded lookup.
- If provider lookup context is incomplete at maturity, return a bounded non-billable lookup-unavailable/deferred result: no recovery/attempt/usage/Meta call and no hot polling. Distinguish this from absence of checkout identity.
- Preserve pending refresh, existing/terminal recovery handling, duplicate/out-of-order checkout updates, tenant scope and existing Shopify ingress responsiveness.

## Out of Scope

- Changing Shopify webhook producer (SHOPIFY-001).
- Redesigning Shopify abandoned checkout API or adding a second durable context cache.
- Missing-recipient materialisation prerequisite (BACKGROUND-007).
- Reachability suppression admission (BACKGROUND-010).

## Requirements

- [ ] Token and Shop determine candidate identity and deduplication; URL never does.
- [ ] No pending/no recovery update creates one candidate safely; existing candidates/recoveries retain their prior behaviour.
- [ ] V2 queued checkout.updated events remain consumable after upgrade.
- [ ] Incomplete lookup context is handled without invented dates/URLs, billing or Meta calls.
- [ ] Background consumer is architect-accepted before Shopify starts producing v3 updates.
- [ ] Keep source modules focused and new production files <=300 lines.

## Work Items

- [ ] Upgrade exact published Shared dependency and parser/contract adapter.
- [ ] Add token-keyed no-recovery candidate scheduling, reusing existing pending candidate service.
- [ ] Handle absent lookup context safely at maturity; include bounded outcome/structured diagnostics.
- [ ] Add duplicate/ordering, v2/v3 compatibility, fresh re-entry and missing-context tests.
- [ ] Run repository-declared Background validations.

## Interfaces / Contracts

Consumes SHARED-004 published `@modainteract/moda-interact-shared/shopify` dual-version contract and BACKGROUND-007 current-recipient prerequisite. Uses existing candidate key derived from `(shopId, checkoutToken)` and optional Shopify retrieval hints (`abandonedCheckoutUrl`, `checkoutCreatedAt`, `cartToken`). Produces the existing pending candidate job; no new queue infrastructure.

## Dependencies

- `ARCH-028-BACKGROUND-007`
- `ARCH-028-SHARED-004`

## Enables

- `ARCH-028-SHOPIFY-001`

## Acceptance Criteria

- [ ] Checkout-update with no candidate/recovery schedules by token once; duplicate delivery remains idempotent.
- [ ] v2 strict events still parse without requiring the new optional context.
- [ ] Fresh matured candidate with complete context and current phone can proceed through BACKGROUND-007 prerequisite.
- [ ] Missing context causes no fabricated URL/time, no recovery or billing, no Meta send.
- [ ] Existing pending/recovery refresh and terminal handling do not regress.

## Validation

Focused contract/parser, candidate enqueue/concurrency, missing-context maturity, current recipient, historical v2 queue tests; Background tests/build and `git diff --check`.

## Stop Condition

Complete defined work/acceptance/validation, fill the Completion Report, set status `review`, return to `moda_architect`, and STOP. Do not begin a dependent task.

## Implementation Notes

Do not claim checkoutToken is a documented GraphQL abandonedCheckouts filter; it is Moda business identity. Abandoned-checkout retrieval still uses the current bounded URL/time search until an independently verified token retrieval capability exists. Do not add a second durable store or request-lifecycle Shopify API call.

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
