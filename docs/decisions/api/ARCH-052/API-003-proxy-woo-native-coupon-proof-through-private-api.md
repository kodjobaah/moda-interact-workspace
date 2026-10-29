---
id: ARCH-052-API-003
architecture_id: ARCH-052
title: Expose authenticated private Woo discount-proof proxy with existing Woo provider grant
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
- ARCH-052-WOOCOMMERCE-001
enables:
- ARCH-052-BACKGROUND-003
- ARCH-052-GATEWAY-001
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-API-003: Expose authenticated private Woo discount-proof proxy with existing Woo provider grant

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Proxy bounded provider-native Woo coupon eligibility proof to Background without giving Background Woo credentials or letting untrusted callers trigger coupon changes.

## Context

WooCommerce-001 owns provider-local WC_Discounts rule evaluation. Background cannot use an unprotected plugin endpoint or provider credentials; hosted API owns Woo read grants and is the only service that can authenticate the merchant installation.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Add `src/woocommerce/rest-read/recovery-coupon-proof.operation.ts` with exactly one allowlisted provider method/route `GET /wp-json/wc/v3/moda/recovery/coupon-proof`; headers `X-Moda-Checkout-Key`, `X-Moda-Coupon-Id` and `X-Moda-Checkout-Fingerprint` (no query/body), read from trusted checkout+discount rows, never an arbitrary caller URL, coupon code or cart payload. Send only using the existing Woo read grant, pinned HTTPS origin and authenticated REST key; do not add a general proxy capability.
- Add private `POST /internal/v1/recovery/discount-proof` API HTTP route (same path as Commerce, distinct internal host), strict Shared-005 request body <=2048 bytes and Shared-004 HMAC with Redis replay lock. On every call confirm Shop.platform=WOOCOMMERCE, CheckoutRecovery.id/shopId/current fingerprint, candidate discount id/shopId maps to `woo:coupon:<positive integer>`, active installation, read grant freshness and checkoutKey ownership. Match proof result back to shop/checkout/fingerprint/provider code/currency; mismatches and unverified extension rules => `unavailable` or hard reject.
- Use existing Woo provider connection and credential-grant service for service-side authentication and provider transport; do not expose REST credentials, personal data or checkoutKey in response/logs. Reject 401/403 before any tenant data read, cross-shop and unrecognised coupon IDs with 404, grant revoked with 503 typed unavailable.
- Add API integration harness tests: Woo native proof eligible/ineligible/unavailable, cross-tenant, invalid proof HMAC/replay, missing Woo read grant, plugin 401/403, tampered result and zero provider-side mutations.

## Out of Scope

- No Woo coupon rule reimplementation in hosted API, no public reverse proxy, no persistence schema, no merchant coupon selection edits.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Woo provider must authenticate the narrowly scoped read-only custom route using the established installed Woo REST key read grant; this requires plugin-side WOOCOMMERCE-001 integration tests to prove a read-only key can make this GET request. If this cannot be verified, mark blocked and report to architect rather than silently elevate grant permissions.
- Woo REST read-only key uses a **GET** request with identity data in strictly validated HTTPS headers, not URI query params; `Cache-Control: no-store` on both request and response. Native provider route must never require write-scoped Woo API keys or mutate cart/coupon/order state on read.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Add exactly one Woo REST custom read operation.
- [ ] Implement authenticated tenant-scoped API-private proxy route and proof validation.
- [ ] Prove read-grant auth/permission and failure isolation with DB/Redis/plugin simulator.

## Interfaces / Contracts

- Private `POST /internal/v1/recovery/discount-proof` HMAC Shared-004; Shared-005 proof request/result; fixed Woo custom `/wp-json/wc/v3/moda/recovery/coupon-proof` via read-only provider grant.

## Dependencies

- `ARCH-052-SHARED-003` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-WOOCOMMERCE-001` — new ARCH-052 prerequisite (not yet materialised).

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-BACKGROUND-003`
- `ARCH-052-GATEWAY-001`

## Acceptance Criteria

- [ ] A signed Background request reaches verified native Woo proof without any public/custom generic proxy or exposed Woo credentials.
- [ ] Unknown/read-grant-incompatible Woo rule never returns a verified offer.

## Validation

- [ ] API read-grant, HMAC/Redis/Postgres and plugin proof integration tests.
- [ ] API declared build/typecheck and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-api/src/woocommerce/rest-read/recovery-coupon-proof.operation.ts (new)`
- `moda-interact-api/src/woocommerce/rest-read/`
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
