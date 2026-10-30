---
id: ARCH-053-API-002
architecture_id: ARCH-053
title: Resolve Woo recovery link with installation and generation authorization
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-053-SHARED-002
- ARCH-053-DATABASE-001
enables:
- ARCH-053-WOOCOMMERCE-002
- ARCH-053-API-003
- ARCH-053-API-003
created: 2026-10-29
updated: 2026-10-30
---

# ARCH-053-API-002 — Resolve Woo recovery link with installation and generation authorization

## Architecture

Architecture ID: `ARCH-053`. Document: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Coordinator: `moda_architect`. **Portable canonical task: defined but not materialised**; no Git branch, worktree, commit, push, review or producer deployment claimed.

## Objective

Resolve Woo recovery link with installation and generation authorization. One bounded outcome in `moda-interact-api` owned by `moda_api`.

## Context

The uploaded workspace snapshot is dated 2026-10-29. ARCH-052 owns dynamic discount discovery and must not be used for these checkout-URL changes. An ARCH-048 next-generation dependency exists only as a separate *portable* proposal until accepted/materialised. This task is **Pending** from the snapshot/dependency inventory, subject to fresh launcher re-gating.

## Scope

- Create `src/woocommerce/recovery-restore/{contract.ts,service.ts,routes.ts}` and focused tests; wire route in `src/composition/woocommerce.ts`, `src/composition/routes.ts` and respective composition tests. Route `POST /v1/woocommerce/recovery-restore/resolve` only, installation bearer authentication through existing `WooInstallationAuthenticator`.
- Strict request body `{schemaVersion:'woo.restore.resolve.v1',recoveryId,token}`, max 4096 bytes, `Cache-Control: no-store`; no shopId, customerId, coupon code, product IDs or restore URL accepted from caller. Resolve recovery by `id` AND authenticated `shopId`; look up latest generation for the same shop+checkoutToken; status allowed `DETECTED|MESSAGE_SENT|ENGAGED`; reject terminal flags, >7-day checkout freshness, cancelled or later generation, deleted/disabled installation/shop, absent/unsupported snapshot, invalid canonical-site URL and mismatch between stored URL and recovery identity.
- Parse URL's expected `moda_interact_resume=1`, `r` and `t`; compare submitted token with stored 43-character token using SHA-256 digests in `timingSafeEqual`; do not concatenate a caller-supplied hostname. Validate the stored HTTPS URL is on the installation's canonical site (including allowed home path) and consistent with Shop.domain. Return only Shared positive response `{schemaVersion,status:'eligible',recoveryId,checkoutKey,snapshot}`; denials indistinguishable `404 {error:'restore_unavailable'}`, bad shape 400, dependency outage 503.
- Read-only: no update to CheckoutRecovery, no new recovery record, Redis job, consent, message or Woo cart. Check existing durable order-terminal evidence if accessible, and document uncertainty for never-delivered Woo order events.

## Out of Scope

No public token minting, no Woo cart mutation, no Background admission, no merchant REST coupon proof, no change to dynamic discounts.

No execution of Enabled tasks, unrelated cross-repository implementation, extra database objects or new generic logger.

## Requirements

- Enforce tenant boundary with authenticated installation, not embedded URL shop identifier. A guessed recovery ID, wrong shop, stale generation, tampered token, old coupon or expired status never produces basket or contact data.
- On load/transient DB failures, return bounded 503 and log error safely; never respond with a nominal valid snapshot. Logs must never contain token, raw stored URL, customer details or coupon codes.
- If there is no corresponding published Shared contract, do not write local clone. The route is server-to-server only; never expose as a publicly unprotected bearer-link read.

### Mandatory workflow/security invariants

- Inspect `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/developer-task-workflow.md`, `docs/task-definition-materialization.md` and the launcher preparation evidence. Use the **dedicated, synchronized parent and implementation task worktrees**; do not operate from a shared checkout or claim a branch was pushed without evidence. Implement only the owning repository and assigned task metadata. No unrelated refactors, migrations, agent handoffs or remote pushes to `main`.
- Read the ARCH-053 parent architecture and all dependency tasks before claiming Ready. Any missing contract or incorrect owner is a blocking architect question; do not invent a local parallel schema or silently change another agent's task. System-test tasks must remain terminal.
- Never swallow unexpected errors: Node uses `@modainteract/moda-interact-shared/logging`; PHP uses the existing safe plugin diagnostics (not a competing generic Node logger). Report bounded event codes, ids and outcomes, propagate retryable failures to their owning boundary, omit tokens, full URLs, coupon codes and customer personal data from logs.
- The plugin cannot access PostgreSQL/Redis. The API cannot mutate merchant WordPress cart sessions. Background cannot directly call an unverified merchant endpoint to mint URLs. Do not enable Woo production WhatsApp sending, relax final consent/STOP/order gates, or add cross-generation outreach caps/cooldowns.

## Work Items

- [ ] Implement strict resolver route, service and composition wiring.
- [ ] Add eligible/expired/superseded/invalid-token/wrong-tenant/status/order tests and uniform-denial response.
- [ ] Verify no DB writes/Redis operations or token leakage and verify complete URL host/path binding.

## Interfaces / Contracts

Plugin caller via `ModaApiClient` server-side installation auth; Shared `WooRestoreResolveRequestV1Schema` and response, version `woo.restore.resolve.v1`. Validity is checked at resolve time (customer POST), not GET landing.

## Dependencies

- `ARCH-053-SHARED-002` (must be architect-accepted Complete)
- `ARCH-053-DATABASE-001` (must be architect-accepted Complete)

## Enables

- `ARCH-053-WOOCOMMERCE-002`
- `ARCH-053-API-003` — additive opt-in v2 response on the same authenticated route; **v1 remains unchanged**.
- `ARCH-053-API-003` — additive opt-in v2 response on the same authenticated route; **v1 remains unchanged**.

## Acceptance Criteria

- [ ] Implement strict resolver route, service and composition wiring.
- [ ] Add eligible/expired/superseded/invalid-token/wrong-tenant/status/order tests and uniform-denial response.
- [ ] Verify no DB writes/Redis operations or token leakage and verify complete URL host/path binding.
- [ ] No regression in tenant isolation, historical generation preservation, valid shopper cart or consent/STOP/terminal order guards.
- [ ] Tests demonstrate invalid/stale/replayed and unexpected errors do not produce silent success or malformed URLs.
- [ ] No change outside assigned domain repository code plus owned task Completion Report; no ARCH-052 work.

## Validation

- [ ] API unit route/auth/schema tests, malicious token and second shop fixtures
- [ ] Isolated Postgres integration with multiple generations and unsupported/expired coupon **codes preserved only as data**
- [ ] `npm run typecheck`, `npm run lint`; `git diff --check`

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are complete, update ONLY this task's authorised execution metadata, checklists and Completion Report, set `status: review` and return to `moda_architect`; **STOP**. Do not begin Enables, merge task branches, push `main` or change Architect Review yourself.

## Implementation Notes

Keep API route order consistent with `composeApiRoutes` and avoid introducing a new generic logger, CORS surface, redirect or cached GET. Any gateway routing gap must be reported to architect, not fixed in API code.

## Completion Report

### Status

Not Started

### Files Changed

None — portable task definition only.

### Work Completed

Not Started.

### Validation Results

Not Run — no implementation claimed.

### Deviations

None.

### Assumptions

Design based on uploaded 2026-10-29 source snapshot; re-check source and prior task acceptance before implementation.

### Unresolved Issues

None asserted as executed; dependencies must be materialised/accepted.

### Architectural Concerns

Return any cross-service schema/provider/transaction concern to `moda_architect` before improvising.

## Architect Review

### Review Status

Pending

### Review Notes

Not Reviewed — task not executed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

To be assessed after implementation.

### Follow-up

None.
