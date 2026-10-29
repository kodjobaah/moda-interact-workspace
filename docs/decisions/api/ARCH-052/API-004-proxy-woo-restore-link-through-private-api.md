---
id: ARCH-052-API-004
architecture_id: ARCH-052
title: Issue Woo checkout-restoration links through private hosted API read grant
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
- ARCH-052-WOOCOMMERCE-002
enables:
- ARCH-052-BACKGROUND-006
- ARCH-052-GATEWAY-001
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-API-004: Issue Woo checkout-restoration links through private hosted API read grant

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Expose the Woo plugin signed checkout-restoration link to Background through one authenticated tenant-checked API operation.

## Context

Existing Woo read credentials and active installation grant are API-only. Background-006 must not invent a direct outbound WordPress connection, and a customer return-to-checkout URL is not an image or coupon proof.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Add fixed private `POST /internal/v1/recovery/restore-link` to the existing API HTTP composition, secured by the published Shared-004 Node HMAC signer/verifier (exact third allowlisted path), <=2048-byte strict body `{shopId,checkoutRecoveryId,checkoutFingerprint}`, Redis 120-second nonce replay protection.
- Within authenticated API process re-read Shop.platform=WOOCOMMERCE, current CheckoutRecovery.id/shopId, checkoutKey/fingerprint, ACTIVE installation and unrevoked Woo REST read grant; reject mismatched client fingerprint before any provider call.
- Add only allowlisted Woo REST read operation `GET /wp-json/wc/v3/moda/recovery/restore-link` with server-derived checkoutKey and checkoutFingerprint in `X-Moda-Checkout-Key` and `X-Moda-Checkout-Fingerprint` request headers (no query-string or GET body) through existing pinned HTTPS Woo connection/credentials. Never permit caller-chosen provider URL, coupon cart mutation or generic proxy.
- Validate plugin response strict `{url:string,expiresAt:string}`: absolute canonical Woo HTTPS origin matching installation, path `/moda-recovery/restore/<opaque-token>`, no userinfo/fragment, expiry >now and <=30min, no embedded raw checkoutKey. Return the same bounded typed response to Background, with no URL persisted or logged.
- Add API read grant/HMAC/Redis/tenant/expired-link tests, plugin 401/403, unsafe redirect URL, expired/revoked installation, failed REST auth and no Woo cart write.

## Out of Scope

- No new schema, no browser-facing API, no direct Woo credentials in Background, no plugin restore implementation or shared generic proxy.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- The plugin read-key must have explicit permission to issue a link; this is not authority to mutate the merchant cart.
- Woo REST read-only key uses a **GET** request with identity data in strictly validated HTTPS headers, not URI query params; `Cache-Control: no-store` on both request and response. Native provider route must never require write-scoped Woo API keys or mutate cart/coupon/order state on read.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Implement one fixed private route + one allowlisted plugin operation.
- [ ] Enforce exact checkout/shop/grant and canonical URL validator.
- [ ] Run real API+plugin integration negative tests.

## Interfaces / Contracts

- Private signed `POST /internal/v1/recovery/restore-link`; `{shopId,checkoutRecoveryId,checkoutFingerprint}` -> `{url,expiresAt}`.

## Dependencies

- `ARCH-052-SHARED-003` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-WOOCOMMERCE-002` — new ARCH-052 prerequisite (not yet materialised).

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-BACKGROUND-006`
- `ARCH-052-GATEWAY-001`

## Acceptance Criteria

- [ ] Signed restore link is returned only for the owning, active Woo checkout without leaking Woo REST credentials or raw checkoutKey.
- [ ] Unapproved/stale/unsafe destination never reaches Meta template preparation.

## Validation

- [ ] API HMAC/Redis/DB + Woo read port integration tests.
- [ ] API declared build/typecheck/lint and git diff --check.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-api/src/woocommerce/rest-read/recovery-restore-link.operation.ts (new)`
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
