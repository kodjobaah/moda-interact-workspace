---
id: ARCH-052-COMMERCE-002
architecture_id: ARCH-052
title: Read first checkout-product image from Shopify product facts
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
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
- ARCH-052-BACKGROUND-007
- ARCH-052-SYSTEM-TEST-001
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-COMMERCE-002: Read first checkout-product image from Shopify product facts

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Expose a bounded, shop-scoped image-source record for a product actually present in the abandoned Shopify checkout.

## Context

Commerce product search and variant-facts readers exist, but their selected GraphQL products currently omit image metadata. CheckoutRecovery.lineItems stores product/variant IDs without image URLs.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Extend the existing Shopify Commerce product/variant facts GraphQL documents and strict parsers only where needed to read one appropriate variant/product image with source identity, MIME/size metadata if provider exposes it, and current product availability.
- Use the exact variant/product IDs taken from authenticated CheckoutRecovery; do not free-text search for a visually similar item or another merchant’s product.
- Return a bounded source descriptor to the approved private consumer; do not insert arbitrary public image URLs into template headers or create a new image normalization framework.
- Preserve existing search/discount results, GraphQL scopes, request budget and checkout ID authorization.

## Out of Scope

- No R2 upload, media DB write, Woo image sourcing, template header change or storefront cart mutation.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- No image found is a normal `unavailable` result, not a fabricated/placeholder image.
- Only Shopify-controlled image source for the exact checkout product/variant, with safe URL handling and no automatic redirects.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Add pinned Shopify product media GraphQL selection and parser.
- [ ] Connect media source to trusted checkout product IDs.
- [ ] Add provider-schema, wrong-shop and no-image fixtures.

## Interfaces / Contracts

- Extend existing Commerce `productFacts.readVariants` with an optional source-image projection on an approved private read port; BG007 performs normalization.

## Dependencies

None.

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-BACKGROUND-007`
- `ARCH-052-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] No untrusted seller-entered URL can become an approved Meta media link without BG007 normalization.
- [ ] Existing Commerce product search/discount evaluation tests remain green.

## Validation

- [ ] Commerce GraphQL schema validation and product reader unit tests.
- [ ] Build/typecheck/lint and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-commerce/src/commerce/products/index.ts`
- `moda-interact-commerce/src/commerce/products/ (media reader helper)`
- `moda-interact-commerce/tests/`

Source ownership is restricted to the assigned repository plus this task file. `moda_architect` owns architectural/dependency/index reconciliation. The implementing agent should stop for an architectural connector/schema gap rather than inventing a cross-repository workaround.

## Completion Report

### Status

Not Started — portable definition, no task claim.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run.

### Deviations

None reported.

### Assumptions

Execution will verify its current workspace, source state, dependency versions and test harness.

### Unresolved Issues

None established by implementation.

### Architectural Concerns

Report discovered cross-repository/credential/provider-proof issues to `moda_architect`.


## Architect Review

### Review Status

Pending.

### Review Notes

Planning only; no source implementation accepted.

### Reviewed Files

The task definition was authored from the 29 October 2026 snapshot; a code implementation has not been reviewed.

### Validation Reviewed

None for implementation.

### Architecture Conformance

To be determined after implementation review.

### Follow-up

Materialise with the canonical task launcher after the planning patch is integrated and dependencies become Complete.
