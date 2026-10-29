---
id: ARCH-052-COMMERCE-003
architecture_id: ARCH-052
title: Serve authenticated private Shopify checkout and alternative-product discount proof
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
- ARCH-052-COMMERCE-008
- ARCH-052-SHARED-003
enables:
- ARCH-052-GATEWAY-001
- ARCH-052-MCP-002
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-COMMERCE-003: Serve authenticated private Shopify checkout and alternative-product discount proof

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Expose one private-network-only, strictly tenant-scoped Shopify discount-proof POST route for BOTH original checkout and verified alternative-product target, with no private product-image route.

## Context

Commerce-001 and Commerce-008 own Shopify provider-specific discount proof. MCP-003 obtains product images directly using its Shopify GraphQL connection. Background never calls Commerce image endpoint.

## Scope

- Implement only `app/internal/v1/recovery/discount-proof/route.ts` as POST-only, Node runtime, <=2048B JSON, `Cache-Control:no-store`, deny public Gateway ingress; require a trusted private caller and authoritative same-shop recovery/attempt/discount checks; no Shared-004 signatures or Redis replay nonce. No `/internal/v1/recovery/product-image` route.
- Validate Shared-005 request target CHECKOUT vs ALTERNATIVE_PRODUCT, reload exact `{shopId,checkoutRecoveryId,outreachAttemptId}` state and verified `ShopifyDiscount` candidate, match shop, current fingerprint, product/variant if alternate, and invoke COMMERCE-001 or COMMERCE-008 read-only evaluator. Return strict Shared-005 proof with no raw provider response or secret.
- Integration tests for attempted public access, wrong-shop proof, unsupported product rules, expired provider data, both targets, closed/disabled tenant and zero cart mutation.

## Out of Scope

- No public gateway rewrite, Node HMAC implementation, provider eligibility rule engine rewrite, extra image table or secret in Git.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Private Render networking is defense in depth, not replacement for signature, replay and exact tenant/line checks.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Add precisely one `POST /internal/v1/recovery/discount-proof` route under `app/internal/v1/recovery/discount-proof/route.ts` with private-network-only access, strict request-size limits and fresh tenant/recovery authorisation.
- [ ] Dispatch Shared-005 `CHECKOUT` proof to COMMERCE-001 and `ALTERNATIVE_PRODUCT` proof to COMMERCE-008, after current exact shop/recovery/attempt/product validation.
- [ ] Add private route/public-access-denial/Shopify provider integration tests for both targets, including expiry, wrong tenant and no provider mutation.
- [ ] Run Commerce's declared checks, `git diff --check`; verify no product-image route was created.

## Interfaces / Contracts

`POST /internal/v1/recovery/discount-proof` Shared-005 proof through private-only transport and strict same-shop authorisation. No product-image route and no WooCommerce API proxy.

## Dependencies

- `ARCH-052-COMMERCE-001` — must be Complete and architect-accepted before this task starts.
- `ARCH-052-COMMERCE-008` — must be Complete and architect-accepted before this task starts.
- `ARCH-052-SHARED-003` — must be Complete and architect-accepted before this task starts.

Dependencies are authoritative in YAML; system tests are terminal validation and must never block implementation.

## Enables

- `ARCH-052-GATEWAY-001`
- `ARCH-052-MCP-002`

## Acceptance Criteria

- [ ] MCP obtains current Shopify coupon eligibility for both checkout and alternate-product targets through the single private Commerce proof route.
- [ ] Invalid/replayed/cross-tenant requests fail before provider access, and no provider mutation occurs.
- [ ] Product image and search are obtained directly by MCP GraphQL; this task creates **no private product-image route**.

## Validation

- [ ] Commerce Next route unit and Redis/Postgres integration tests; build/typecheck/lint.
- [ ] `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

Owning repository paths:
- `moda-interact-commerce/app/internal/v1/recovery/discount-proof/route.ts` (new)
- `moda-interact-commerce/src/commerce/discounts/` (existing evaluators from COMMERCE-001/008)
- `moda-interact-commerce/tests/` (new route/provider integration tests)

Do not add `app/internal/v1/recovery/product-image/route.ts`. The MCP service owns product read/search directly. Scope is Commerce repository plus this task report only.

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
