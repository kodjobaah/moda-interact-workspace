---
id: ARCH-052-COMMERCE-008
architecture_id: ARCH-052
title: Verify Shopify discounts for a specific recommended product without checkout mutation
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 25
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-COMMERCE-001
- ARCH-052-SHARED-003
enables:
- ARCH-052-COMMERCE-003
- ARCH-052-MCP-004
- ARCH-052-SYSTEM-TEST-001
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-COMMERCE-008: Verify Shopify discounts for a specific recommended product without checkout mutation

## Architecture

Architecture ID: `ARCH-052`. Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`. **Defined but not materialised**; no Git branch or worktree created.

## Objective

Add an exact, read-only alternative-product target to the existing Shopify discount-proof evaluator.

## Context

COMMERCE-001 proves discounts against the original checkout. If none applies, the InitialOutreachOfferAgent may promote another product, but only when a provider-backed rule proves the offer applies to that alternative purchase; matching a category name is not proof.

## Scope

- In the existing `src/commerce/discounts/` reader, add Shared-005 target `{kind:"ALTERNATIVE_PRODUCT",productId,variantId,quantity:1}`. Verify product/variant belongs to the authenticated Shopify shop and remains published/available, then evaluate the candidate discount rules including product/collection/category inclusion/exclusion, customer eligibility, starts/expiry, minimum spend, combination/usage and exact present pricing for this hypothetical single-product purchase. Reuse COMMERCE-001’s rule/proof primitives and existing Shopify Admin GraphQL access; no new independent Shopify discount engine.
- A rule requiring unverifiable checkout, customer or basket facts must return typed `unsupported`/`unavailable`, not eligibility. Never mutate a cart, create a discount code, reserve inventory or change checkout lines.
- Return Shared-005 result with target identity, current proof fingerprint and truthfully bounded promotional value. The proof must describe a *different* product, not a discount on abandoned lineItems.
- Tests cover product not sold, unknown collection, excluded variant, customer restriction, total-minimum not met, no usage data, provider timeout and positive exact rule proof; no writes.

## Out of Scope

No additional database table/column/migration, migration backfill, alternate provider proxy, customer-facing product database/cache, secret-bearing logs, unrelated architecture or other repository implementation.

## Requirements

- Only assigned repository code and this task report may be changed. Do not implement Enabled tasks.
- Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, the exact launcher packet and dedicated mirrored parent/implementation worktrees. Re-read the authoritative task before claiming.
- Use `@modainteract/moda-interact-shared/logging` for new Node structured logs; record unexpected exceptions with bounded reason codes and propagate to the owning error/retry boundary. Never log credentials, complete URLs, coupon codes, raw provider payloads or customer personal data.
- Authenticate every shop/grant/call with its trusted identity, enforce provider deadlines, bounded pagination, strict response projection, customer/tenant separation and read-only provider behavior.
- This is a **pre-production breaking design**. Do not add legacy adapters/backfills or change conversation CommerceAgent lifecycle.

## Work Items

- [ ] Implement exactly the scoped files and runtime behavior.
- [ ] Add deterministic unit and negative/security tests.
- [ ] Run the required validation; record all commands and evidence in Completion Report.

## Interfaces / Contracts

Shared-005 `RecoveryDiscountProofRequestSchema.target.kind=ALTERNATIVE_PRODUCT`; existing COMMERCE-001 evaluator and COMMERCE-003 private proof endpoint. `MCP-004` is consumer; no Commerce Studio authoring.

## Dependencies

- `ARCH-052-COMMERCE-001` — must be Complete and architect-accepted before this task starts.
- `ARCH-052-SHARED-003` — must be Complete and architect-accepted before this task starts.

Dependencies are authoritative in YAML; system tests are terminal validation and must never block implementation.

## Enables

- `ARCH-052-COMMERCE-003`
- `ARCH-052-MCP-004`
- `ARCH-052-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Provider-backed eligible only with provable candidate/product/customer rules and positive value.
- [ ] No cart mutation or unverified storefront claim.
- [ ] Existing checkout proof continues to work.

## Validation

- [ ] Shopify discount policy unit tests and private provider integration tests.
- [ ] Commerce repository typecheck/lint/build as declared; `git diff --check`.

Use the scripts actually declared by the repository's package/tooling. Record unrun checks as unverified; include `git diff --check`.

## Stop Condition

Once Work Items, acceptance criteria and validation are met, set task status to `review`, complete its report, return to `moda_architect` and **STOP**. Do not mark it Complete, publish another task, merge branches or push `main`.

## Implementation Notes

Expected workspace-relative owned source paths (confirm paths exist in checked-out worktree before editing):

- `moda-interact-commerce/src/commerce/discounts/`
- `moda-interact-commerce/src/commerce/products/index.ts` (read existing functions only unless required to expose eligibility facts)
- `moda-interact-commerce/tests/`

## Completion Report

### Status

Not Started — portable definition; no task claim.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run.

### Deviations

None reported.

### Assumptions

Confirm execution baseline in dedicated task worktree.

### Unresolved Issues

None established.

### Architectural Concerns

Return material contract/security/proof gaps to `moda_architect` without inventing a workaround.

## Architect Review

### Review Status

Pending.

### Review Notes

Definition only; no implementation accepted.

### Reviewed Files

Task definition and uploaded 29 October 2026 snapshot only.

### Validation Reviewed

No implementation tests yet.

### Architecture Conformance

Pending implementation review.

### Follow-up

Materialise through canonical task launcher only after dependencies are Complete.
