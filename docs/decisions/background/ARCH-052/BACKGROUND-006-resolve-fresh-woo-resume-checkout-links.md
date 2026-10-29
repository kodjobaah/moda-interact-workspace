---
id: ARCH-052-BACKGROUND-006
architecture_id: ARCH-052
title: Resolve fresh authenticated Woo restore links at initial send preparation
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-API-004
- ARCH-052-GATEWAY-001
enables:
- ARCH-052-BACKGROUND-008
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-BACKGROUND-006: Resolve fresh authenticated Woo restore links at initial send preparation

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Supply a currently valid, trusted Woo checkout URL to the existing Meta dynamic checkout button without storing long-lived bearer URLs on CheckoutRecovery.

## Context

`automated-recovery-template.service.ts` currently depends on CheckoutRecovery.checkoutUrl and a five-minute observedAt limit, while Woo admission records `checkoutUrl:null`.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Implement `src/services/woocommerce-recovery/woo-recovery-checkout-url.service.ts`, caller of **only** API-004 private `POST /internal/v1/recovery/restore-link` with Shared-004 HMAC, from fixed Gateway-001 `MODA_RECOVERY_PRIVATE_READ_API_HOSTPORT`; never call the WordPress host directly or handle Woo REST credentials.
- Sign exact `{shopId,checkoutRecoveryId,checkoutFingerprint}` read from persisted CheckoutRecovery, validate API response expiry <=30min, canonical merchant HTTPS bound site and exact `/moda-recovery/restore/<opaque-token>` path; no userinfo/fragment, private host or untrusted redirect. Do not persist/log bearer URL.
- Set current `TrustedCheckout` from verified URL, observedAt now and explicit expiry during INITIAL template preparation, not from stale checkoutUrl. Invalid/missing route or expiry => approved no-button template or typed no-send, never generic empty Woo checkout.
- Preserve Shopify verified checkoutUrl logic and existing consent/billing send admission. Add integration tests for stale key, malicious URL, wrong installation, expired token, missing private key, returning Woo item cart and no provider side effect on issuance.

## Out of Scope

- No Woo plugin implementation, no hosted API activity schema change, no discount eligibility, new checkout state store, or general network/proxy framework.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Never perform plugin network I/O inside SQL final permit or billing transaction.
- Revoked grants, private-origin/SSRF, wrong-shop, expired tokens or unavailable Woo site return a typed unavailable result.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Implement signed API-only Woo link client.
- [ ] Validate exact installation host, expiry and trusted checkout.
- [ ] Test Meta CTA includes only current safe URL, no persistence/logging.

## Interfaces / Contracts

- API-004 signed private `/internal/v1/recovery/restore-link`, Shared-004 request authentication, `TrustedCheckout` output.

## Dependencies

- `ARCH-052-API-004` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-GATEWAY-001` — new ARCH-052 prerequisite (not yet materialised).

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-BACKGROUND-008`

## Acceptance Criteria

- [ ] Woo CTA restores the targeted checkout only on customer click; no generic cart URL.
- [ ] Missing provider read never exposes credentials or leads to false CTA.

## Validation

- [ ] Background Woo transport fixtures, request/response validation and recovery template preparation integration.
- [ ] Build/lint and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-background/src/services/recovery-template-integration/automated-recovery-template.service.ts`
- `moda-interact-background/src/services/woocommerce-recovery/ (trusted checkout-link adapter)`
- `moda-interact-background/src/services/woo-coupon-grant.service.ts`

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
