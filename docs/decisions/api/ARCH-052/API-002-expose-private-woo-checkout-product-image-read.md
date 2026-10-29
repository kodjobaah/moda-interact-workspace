---
id: ARCH-052-API-002
architecture_id: ARCH-052
title: Expose bounded authenticated Woo product/variation image read for Background
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 35
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-SHARED-003
enables:
- ARCH-052-BACKGROUND-007
- ARCH-052-SYSTEM-TEST-002
- ARCH-052-GATEWAY-001
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-API-002: Expose bounded authenticated Woo product/variation image read for Background

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Use the existing API-process-only WooCommerce read grant to return one public product/variation image to authenticated Background without exposing generic Woo credentials.

## Context

`src/woocommerce/rest-read/product-operation.ts` currently `products.retrieve` projects only id/name/sku/price/stock; Background has no callable Woo provider-image reader. Existing rest-read README prohibits direct external consumers without a separate authenticated service boundary.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Extend `src/woocommerce/rest-read/product-operation.ts` with exact `products.retrieve.image` (`productId:positive integer`) and `products.variation.retrieve.image` (`productId`, `variationId`:positive integers) operations; GET fixed Woo `/wp-json/wc/v3/products/{id}` and `/products/{id}/variations/{variationId}` paths with `_fields=id,images` or `_fields=id,image`, and `context=view`. Never accept URL/path/method from caller.
- Project strict `{productId:number,variantId:number|null,imageUrl:string|null}`; use variation image when present, else product images[0].src. Only absolute HTTPS URLs without credentials/fragment/control chars and <=2048 bytes are candidates; do not send arbitrary provider response or private credentials to Background.
- Add fixed private `POST /internal/v1/recovery/product-image` to existing API HTTP composition/routes. Require the published Shared Node-only HMAC verifier, Redis nonce replay store, request body <=2048 bytes, strict `{shopId,checkoutRecoveryId,productId,variantId}` with provider IDs as canonical positive integers and `checkoutRecovery.shopId` matching requested shop. Verify Shop.platform=WOOCOMMERCE, ACTIVE installation, matching read grant and credential version immediately before and after provider read.
- Return canonical Shared `RecoveryProductImageResultSchema` (`found`, `not_found`, `unavailable`); do not expose public merchant read route, Woo REST keys or other product fields. Provider credentials remain inside `createWooProductReadPort` with existing DNS pinned, HTTPS, redirect, timeouts and revocation checks.
- Authentication failures => 401/403, invalid identifiers or wrong-shop => 404, stale/revoked grant => `unavailable` 503; HTTP/provider exceptions log through Shared logger with bounded codes and propagate/mapped explicitly, never silently swallowed.
- Add API real database/Redis integration tests including wrong shop, replayed auth, missing key, expired nonce, expired grant, DNS private redirect, variation-image fallback, absent image and no provider writes.

## Out of Scope

- No public generic Woo product proxy, no merchant installation API change, no R2 media persistence, no new Prisma model, no unauthenticated service routing.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Only authenticated Background is permitted to call the route; Render private network alone is not authorisation.
- No feature implementation should accept a caller-supplied arbitrary image URL.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Extend exact product/variation media projection and provider allowlist.
- [ ] Add strictly authenticated private endpoint and tenant/read-grant checks.
- [ ] Run PostgreSQL, Redis, Woo read simulator negative cases.

## Interfaces / Contracts

- Private route `POST /internal/v1/recovery/product-image`, HMAC Shared-004, versioned Shared-002 result; internal request `{shopId,checkoutRecoveryId,productId,variantId}`.

## Dependencies

- `ARCH-052-SHARED-003` — new ARCH-052 prerequisite (not yet materialised).

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-BACKGROUND-007`
- `ARCH-052-SYSTEM-TEST-002`
- `ARCH-052-GATEWAY-001`

## Acceptance Criteria

- [ ] Background can obtain one verified shop-bound image candidate from Woo REST read permissions; absent/blocked candidate returns typed absence.
- [ ] Wrong shop, replay, expired grant or unsafe URL never leaks product information/credentials.

## Validation

- [ ] API REST read/unit and PostgreSQL + Redis HMAC integration tests.
- [ ] API build/typecheck/lint and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-api/src/woocommerce/rest-read/product-operation.ts`
- `moda-interact-api/src/woocommerce/rest-read/provider-connection.service.ts`
- `moda-interact-api/src/woocommerce/rest-read/recovery-product-image.routes.ts (new)`
- `moda-interact-api/src/composition/routes.ts`
- `moda-interact-api/tests/`

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
