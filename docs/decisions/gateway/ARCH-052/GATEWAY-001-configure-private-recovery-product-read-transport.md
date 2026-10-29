---
id: ARCH-052-GATEWAY-001
architecture_id: ARCH-052
title: Route private product-image reads and declare independent HMAC secrets
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-COMMERCE-003
- ARCH-052-API-002
- ARCH-052-API-003
- ARCH-052-API-004
- ARCH-052-SHARED-003
enables:
- ARCH-052-BACKGROUND-006
- ARCH-052-BACKGROUND-007
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-GATEWAY-001: Route private product-image reads and declare independent HMAC secrets

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Declare two existing private service origins and their shared signed read credentials for the recovery worker across both deployed Render environments.

## Context

**Snapshot fact:** Gateway has `render.test.yaml` and `render.production.yaml`; no `render.yaml` is present in this snapshot. Both already declare private Commerce/API services and the `moda-recovery-worker` worker. Modify the files that actually exist, not an invented blueprint.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Modify actual `moda-interact-gateway/render.test.yaml` and `moda-interact-gateway/render.production.yaml` (snapshot has **no** root render.yaml). In each create an independent env var group `moda-recovery-private-read-<environment>` declaring `MODA_RECOVERY_PRIVATE_READ_HMAC_KEYS` `sync:false`; attach only to the existing private Commerce/API services and the `moda-recovery-worker`. Separate key material per environment; never commit values.
- On the environment recovery worker add `MODA_RECOVERY_PRIVATE_READ_ACTIVE_KID` `sync:false`, `MODA_RECOVERY_PRIVATE_READ_COMMERCE_HOSTPORT` and `MODA_RECOVERY_PRIVATE_READ_API_HOSTPORT` derived by `fromService` hostport of the existing private services, with trusted internal URL scheme builder. Existing Gateway `MODA_COMMERCE_UPSTREAM`/`MODA_API_UPSTREAM` patterns identify exact service names, not a customer URL.
- Block public gateway Nginx/HAProxy routing of `/internal/v1/recovery/discount-proof`, `/internal/v1/recovery/product-image`, `/internal/v1/recovery/restore-link` to both service targets; test browser/public denial. Private worker calls must still be verified via Shared-004 HMAC and 120sec Redis nonce on each owning service.
- Document out-of-band secure provisioning and rotation of a randomly generated 32-byte base64url HMAC key per environment, active caller KID switch before removing old key and fail-closed text/no-offer fallback. Do not alter other public routes or expose secret values in Git.

## Out of Scope

- No API route handler logic, image fetching, new database, app service-level auth bypass, or production-secret values in Git.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- No secret key committed in the Blueprint.
- Failure to provision route/key makes image optional unavailable; no bypass and no blocking no-discount text outreach.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider mutation is prohibited except the customer-initiated Woo cart restoration explicitly owned by WOOCOMMERCE-002.

## Work Items

- [ ] Declare exact Render Blueprint variables and private origin.
- [ ] Verify public denial and authenticated internal route with test topology.
- [ ] Document key rotation and operational disable/fallback.

## Interfaces / Contracts

- Existing `render.test.yaml` and `render.production.yaml` private Commerce/API services and recovery worker, Shared-004 HMAC + private origins.

## Dependencies

- `ARCH-052-COMMERCE-003` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-API-002` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-API-003` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-API-004` — new ARCH-052 prerequisite (not yet materialised).
- `ARCH-052-SHARED-003` — new ARCH-052 prerequisite (not yet materialised).

All dependencies must be `status: complete` in the authoritative individual task YAML immediately before launcher preparation; architect acceptance or Ready alone is insufficient. No non-system-test task depends on a system-test task.

## Enables

- `ARCH-052-BACKGROUND-006`
- `ARCH-052-BACKGROUND-007`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Both Render environment Blueprints validate and select exact private service addresses; no new public `/internal/v1` ingress.
- [ ] HMAC secrets independently provisioned for test/production with no secrets in Git; absent credentials fail closed.

## Validation

- [ ] Render Blueprint lint/validation and private/public route smoke fixtures.
- [ ] Secrets scan and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-gateway/render.test.yaml`
- `moda-interact-gateway/render.production.yaml`
- `moda-interact-gateway/nginx/`
- `moda-interact-gateway/haproxy/`
- `moda-interact-gateway/docs/`

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
