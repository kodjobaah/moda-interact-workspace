---
id: ARCH-052-COMMERCE-003
architecture_id: ARCH-052
title: Expose authenticated private Shopify discount-proof and product-image reads
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-COMMERCE-001
- ARCH-052-COMMERCE-002
- ARCH-052-SHARED-003
enables:
- ARCH-052-BACKGROUND-003
- ARCH-052-BACKGROUND-007
- ARCH-052-GATEWAY-001
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-COMMERCE-003: Expose authenticated private Shopify discount-proof and product-image reads

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Expose existing Commerce-owned current Shopify discount proof and product/variant-image readers to Background through two HMAC-protected private service routes.

## Context

Commerce-001/002 own Shopify provider reads, but there is currently no Background-callable service endpoint for those results. A private Next.js route layer is necessary; never ask Background to import unpublished Commerce source or access Commerce private Shopify credentials.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Add two Next.js Node-runtime route handlers at `app/internal/v1/recovery/discount-proof/route.ts` and `app/internal/v1/recovery/product-image/route.ts` (HTTP paths `/internal/v1/recovery/discount-proof`, `/internal/v1/recovery/product-image`). Both POST-only JSON <=2048 bytes, no cache, Node-only and invoke the published Shared-004 HMAC verifier + existing Redis connection for 120s replay locks. Block unauthenticated, stale, replayed or wrong-path requests before DB/provider reads.
- Discount route parses exactly Shared-005 `RecoveryDiscountProofRequestSchema`, loads Shop by shopId and CheckoutRecovery by `{id,shopId}`, verifies SHOPIFY and present checkoutFingerprint matches the freshly recomputed stored checkout facts; loads candidate `{id,shopId}` from database, and invokes the exact Commerce-001 supported read-only evaluator. Return only Shared-005 proof result; unsupported/stale/denied must never be `eligible`.
- Image route parses `{shopId,checkoutRecoveryId,productId,variantId}` (strict, product/variant Shopify GID strings, no arbitrary URL); reloads selected checkout lineItems for identity and Shop.platform=SHOPIFY; invokes Commerce-002 product media reader; returns only Shared-002 image result. Exact provider IDs must match a persisted checkout line.
- Use Commerce-owned credential/session resolution and existing bounded provider transport; do not read credentials from merchant browser. No mutation of Shopify checkout, discounts, cart, coupons or products. Retry/timeout <=2sec per read.
- Add Node/Next route integration tests for valid HMAC, replay, wrong shop, revoked Shopify access, stale checkout, wrong candidate/line, safe not-found, no-coupon promise and no provider write. Log bounded non-sensitive status via shared logger; preserve errors.

## Out of Scope

- No public gateway rewrite, Node HMAC duplication, provider eligibility rule engine rewrite, extra image table or secret in Git.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Private Render networking is defense in depth, not replacement for signature, replay and exact tenant/line checks.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Add two route handlers with shared auth guard.
- [ ] Connect exact existing Commerce readers and fresh shop-scoped persisted checkout validation.
- [ ] Add authenticated route/Redis/provider integration tests.

## Interfaces / Contracts

- `POST /internal/v1/recovery/discount-proof` -> Shared-005 result and `POST /internal/v1/recovery/product-image` -> Shared-002 result, both Shared-004 signed, Next Node runtime.

## Dependencies

- `ARCH-052-COMMERCE-001` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-COMMERCE-002` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-SHARED-003` — new ARCH-052 prerequisite (not yet materialised).

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-BACKGROUND-003`
- `ARCH-052-BACKGROUND-007`
- `ARCH-052-GATEWAY-001`

## Acceptance Criteria

- [ ] Background receives correct current eligibility/photo candidate without Commerce secret or public bypass.
- [ ] Tampered/replayed/cross-tenant reads denied before provider access.

## Validation

- [ ] Commerce Next route unit and Redis/Postgres integration tests; build/typecheck/lint.
- [ ] `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-commerce/app/internal/v1/recovery/discount-proof/route.ts (new)`
- `moda-interact-commerce/app/internal/v1/recovery/product-image/route.ts (new)`
- `moda-interact-commerce/src/commerce/discounts/`
- `moda-interact-commerce/src/commerce/products/index.ts`
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
