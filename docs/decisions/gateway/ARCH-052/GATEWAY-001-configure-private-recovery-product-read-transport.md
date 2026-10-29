---
id: ARCH-052-GATEWAY-001
architecture_id: ARCH-052
title: Configure private Shopify proof and direct MCP WooCommerce REST access
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
- ARCH-052-MCP-003
- ARCH-052-SHARED-003
enables:
- ARCH-052-BACKGROUND-008
- ARCH-052-MCP-002
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: '2026-10-29'
---

# ARCH-052-GATEWAY-001: Configure private Shopify proof and direct MCP WooCommerce REST access

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Provision private Shopify discount-proof transport and independent direct MCP Woo REST credential configuration, with no product-search or checkout-link MCP-to-API proxy.

## Context

**Snapshot fact:** Gateway has `render.test.yaml` and `render.production.yaml`; no `render.yaml` is present in this snapshot. Both already declare private Commerce/API services and the `moda-recovery-worker` worker. Modify the files that actually exist, not an invented blueprint.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

- Modify exactly `moda-interact-gateway/render.test.yaml` and `render.production.yaml` (snapshot files). Keep the Commerce Shopify discount-proof route reachable only over internal private service links; do not provision or route any new Woo checkout-restoration API operation. Do not introduce Shared-004 signature/nonce keys or Redis replay configuration. Do not expose any `/internal/v1/recovery/*` route through public Gateway.
- For existing private `moda-interact-mcp-<env>` Render service, declare `COMMERCE_CONNECTION_KEYS_JSON` and `COMMERCE_CONNECTION_ACTIVE_KEY_ID` as `sync:false`, provision securely per environment, and set explicit Woo connection mode (public HTTPS in deployed environments). MCP reads encrypted Woo grants via existing database connectivity and performs outbound **direct Woo REST** over bounded authenticated HTTPS; no `MODA_RECOVERY_PRIVATE_READ_API_HOSTPORT` for MCP, no product-image route.
- Keep `MODA_RECOVERY_PRIVATE_READ_COMMERCE_HOSTPORT` for MCP-to-Commerce Shopify discount proof. Do **not** add `MODA_RECOVERY_PRIVATE_READ_API_HOSTPORT` for initial outreach: Background already has `CheckoutRecovery.checkoutUrl`, and MCP communicates directly with provider APIs. Do not provision Woo consumer keys directly in Render YAML; read the encrypted stored grants and Shared keyring.
- Document key rotation before removing old IDs, fail-closed startup for missing/malformed MCP keyring, same-environment grant isolation and network egress requirements for public Woo hosts. Test environment and public route denial, denied credentials, SSRF protections, and successful direct MCP Woo read with no call to Moda API.

## Out of Scope

- No API route handler logic, image fetching, new database, app service-level auth bypass, or production-secret values in Git.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

- Commerce Shopify proof uses internal private connectivity with strict application tenant/recovery checks; product search/GET and Woo coupon proof use direct provider connections in MCP. No checkout-restoration route or host/port environment wiring belongs to ARCH-052. Do not expose `/internal/v1/recovery/*` via any public Gateway route.
- Missing, malformed or unprovisioned MCP credential keyring must **fail closed for Woo read**, without exposing a credential or weakening tenant isolation. Optional product images may fall back to approved text templates; no provider proof => no unverified discount.
- Read `docs/agent-vcs-ownership-policy.md` and `docs/agent-worktree-isolation-policy.md`. Require launcher-resolved task worktree and start-of-attempt synchronisation evidence.
- Use Shared logger for any new Node runtime logs and record unexpected exceptions using bounded reasons without raw provider URLs or secrets.
- No cart, coupon, order or Shopify provider mutation. Checkout URL issuance and customer-click cart restoration are upstream/out of scope for ARCH-052.

## Work Items

- [ ] Update exactly `moda-interact-gateway/render.test.yaml` and `render.production.yaml` for private Commerce Shopify discount proof; do not provision a Woo checkout-restoration route, any product/image proxy to hosted API or a Background-to-API restore host/port.
- [ ] Provision secure environment-specific `COMMERCE_CONNECTION_KEYS_JSON` and `COMMERCE_CONNECTION_ACTIVE_KEY_ID` placeholders only for MCP, and the existing private Commerce proof host/port wiring; do not add Background-to-API restore host/port or new HMAC key variables. No plaintext secrets committed.
- [ ] Verify MCP direct read-only outbound Woo HTTPS egress with grant/credential revalidation, and test public route denial; assert zero MCP-to-Moda-API product/coupon-proof calls.
- [ ] Validate exact Blueprint files, secret scan, release isolation, fail-closed credential/route state and `git diff --check`.

## Interfaces / Contracts

Existing Render environment files and private-only Commerce proof route; MCP direct Woo REST uses Shared credential keyring encryption/identity and MCP-003 secure transport. Existing checkout URL is stored in `CheckoutRecovery` and requires no Gateway route.

## Dependencies

- `ARCH-052-COMMERCE-003` — must be Complete and architect-accepted before this task starts.
- `ARCH-052-MCP-003` — must be Complete and architect-accepted before this task starts.
- `ARCH-052-SHARED-003` — must be Complete and architect-accepted before this task starts.

Dependencies are authoritative in YAML; system tests are terminal validation and must never block implementation.

## Enables

- `ARCH-052-BACKGROUND-008`
- `ARCH-052-MCP-002`
- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Blueprint config has no MCP-to-API product/proof proxy route; MCP direct Woo REST has secure per-environment keyring.
- [ ] Commerce Shopify discount-proof remains private-only and denies public ingress; no new Woo restore-link API endpoint, proxy or environment variable is introduced by ARCH-052.
- [ ] No secrets committed and no public private-read ingress.

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
