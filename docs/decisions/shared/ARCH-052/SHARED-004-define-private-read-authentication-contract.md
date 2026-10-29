---
id: ARCH-052-SHARED-004
architecture_id: ARCH-052
title: Define signed private recovery product-read request authentication
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
- ARCH-052-SHARED-003
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-SHARED-004: Define signed private recovery product-read request authentication

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Publish one bounded Node-only request signing/verifying contract for Background -> API/Commerce private read calls, without browser-visible secrets.

## Context

Woo `createWooProductReadPort` is deliberately API-process-only; its existing contract forbids exposing a generic unauthenticated HTTP proxy. A new service-to-service read requires an explicit authentication and replay contract.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Create `src/node/recovery-private-read-auth.ts` and publish `/node/recovery-private-read-auth`; no service-local HMAC reimplementation.
- Only allowlist POST fixed paths `/internal/v1/recovery/product-image`, `/internal/v1/recovery/discount-proof`, `/internal/v1/recovery/restore-link`; canonical HMAC bytes are UTF-8 `v1\nPOST\n<exact-path>\n<unix-timestamp>\n<base64url-nonce>\n<hex-sha256(raw-JSON-body)>` with no final newline. Reject query strings, any other method/path and bodies over 2048 bytes.
- Headers exactly `X-Moda-Read-Key-Id`, `X-Moda-Read-Timestamp` Unix seconds, `X-Moda-Read-Nonce` base64url of 16 random bytes, `X-Moda-Read-Signature` base64url HMAC-SHA256. Canonicalise over raw body bytes before parse; reject changed JSON byte representation after signing.
- Keyring `MODA_RECOVERY_PRIVATE_READ_HMAC_KEYS` strict JSON object up to three `kid:base64url-32-byte-secret`; caller active kid from `MODA_RECOVERY_PRIVATE_READ_ACTIVE_KID`. Require 32 cryptographically random bytes, kid ASCII `[A-Za-z0-9_-]{1,32}`, no default/blank fallback.
- Verify clock skew <=60secs, constant-time signature comparison and nonce re-use via caller-injected Redis `SET NX EX 120` keyed by caller/key/nonce, fail closed on Redis outage; no logging of HMAC, checkout body or keys.
- Node-only export, no browser-safe transitive imports; deterministic signing/verification fixtures for all three paths, wrong key/method/path, old timestamp, nonce replay, tampered bytes and absent config.

## Out of Scope

- No service credentials in shared package; no API route, no gateway ingress, no exposure to browser-safe entrypoints, no merchant/provider data.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Use dedicated HMAC keys, not `commerce.commandHmacKey`, ShopBrand R2 keys, encryption AAD keys or Woo installation secrets.
- Never log key material, signatures, full request body or customer identifiers.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Create Node-only signing and verifying primitives.
- [ ] Add strict keyring parser and deterministic replay/tamper vectors.
- [ ] Test browser-safe export isolation.

## Interfaces / Contracts

- `@modainteract/moda-interact-shared/node/recovery-private-read-auth`: parser, signer, verifier; caller injects nonce replay port and secret config.
- Strict request authenticates service identity only; API checks target shop/platform/grant independently.

## Dependencies

None.

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-SHARED-003`

## Acceptance Criteria

- [ ] Unknown key/wrong signature/replayed request/clock skew/missing Redis fails closed.
- [ ] No crypto duplicated by service consumers and no secrets exposed through browser bundles.

## Validation

- [ ] Shared Node-only tests and package export resolution, build/typecheck.
- [ ] `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-shared/src/node/recovery-private-read-auth.ts`
- `moda-interact-shared/src/node/recovery-private-read-auth.test.ts`
- `moda-interact-shared/package.json`

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
