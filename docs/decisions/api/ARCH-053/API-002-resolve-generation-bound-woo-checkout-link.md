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
status: in_progress
priority: 40
executor: copilot
claimed_at: 2026-10-30T16:18:52Z
attempt: 2
depends_on:
- ARCH-053-SHARED-002
- ARCH-053-DATABASE-001
enables:
- ARCH-053-WOOCOMMERCE-002
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

The inspected snapshot is dated 2026-10-30 07:59. ARCH-052 owns dynamic discount discovery and is not a checkout-URL implementation domain. ARCH-048-BACKGROUND-007..011 task files are present, but none has been accepted Complete in this snapshot (007 Ready, 008–011 Pending). This task is **Pending** from the snapshot/dependency inventory, subject to fresh launcher re-gating.

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

**Single-version handoff:** SHARED-001 makes `outreachOffer` mandatory in the first `woo.restore.resolve.v1` response. This task must return the complete strict v1 response, initially `{kind:"NONE",reason:"NO_CONFIRMED_OFFER"}` (without loading outbound messages). API-003, a later independently reviewable API task, substitutes a verified confirmed-offer projection on that **same** v1 response. Do not introduce v2 routing, conditional version branches or a dual-version adapter. No part of this staged implementation may be deployed as complete feature delivery until API-003 and WooCommerce-007/008 are accepted.

**Mandatory initial v1 response example before API-003 enriches confirmed sent-message evidence:**

```json
{
  "schemaVersion": "woo.restore.resolve.v1",
  "status": "eligible",
  "recoveryId": "recovery_456",
  "checkoutKey": "woo-example-checkout",
  "snapshot": {
    "schemaVersion": "woo.cart-restore.v1",
    "kind": "supported",
    "appliedCouponCodes": ["SAVE10"],
    "lines": [{"productId": "101", "quantity": 2}]
  },
  "outreachOffer": {"kind": "NONE", "reason": "NO_CONFIRMED_OFFER"}
}
```

This value is a **temporary execution-stage outcome**, not a different wire version or permission to deploy a customer-facing flow that ignores sent recommendations. API-003 must replace the NONE branch with trusted confirmed-message evidence before ARCH-053 is considered integrated. Both tasks must use the same `WooRestoreResolveResponseV1Schema` from the published Shared package.

## Work Items

- [x] Implement strict resolver route, service and composition wiring.
- [x] Add eligible/expired/superseded/invalid-token/wrong-tenant/status tests and uniform-denial response.
- [x] Verify no DB writes/Redis operations or token leakage and verify complete URL host/path binding.

## Interfaces / Contracts

Plugin caller via `ModaApiClient` server-side installation auth; Shared `WooRestoreResolveRequestV1Schema` and response, version `woo.restore.resolve.v1`. Validity is checked at resolve time (customer POST), not GET landing.

## Dependencies

- `ARCH-053-SHARED-002` (must be architect-accepted Complete)
- `ARCH-053-DATABASE-001` (must be architect-accepted Complete)

## Enables

- `ARCH-053-WOOCOMMERCE-002`
- `ARCH-053-API-003` — enrich the existing single v1 response from the confirmed initial sent-message receipt; no second version or route.

## Acceptance Criteria

- [x] Implement strict resolver route, service and composition wiring.
- [x] Add eligible/expired/superseded/invalid-token/wrong-tenant/status/order tests and uniform-denial response.
- [x] Verify no DB writes/Redis operations or token leakage and verify complete URL host/path binding.
- [x] No regression in tenant isolation, historical generation preservation, valid shopper cart or consent/STOP/terminal order guards.
- [x] Tests demonstrate invalid/stale/replayed and unexpected errors do not produce silent success or malformed URLs.
- [x] No change outside assigned domain repository code plus owned task Completion Report; no ARCH-052 work.

## Validation

- [x] API unit route/auth/schema tests, malicious token and second shop fixtures
- [x] Isolated Postgres integration with multiple generations and unsupported/expired coupon **codes preserved only as data**
- [x] `npm run typecheck`, `npm run lint`; `git diff --check`

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are complete, update ONLY this task's authorised execution metadata, checklists and Completion Report, set `status: review` and return to `moda_architect`; **STOP**. Do not begin Enables, merge task branches, push `main` or change Architect Review yourself.

## Implementation Notes

Keep API route order consistent with `composeApiRoutes` and avoid introducing a new generic logger, CORS surface, redirect or cached GET. Any gateway routing gap must be reported to architect, not fixed in API code.

## Completion Report

### Status

Changes Requested — Attempt 1. Implementation commit `756130ebf579b43c0e8d32557698ff26ecff0bf8` is reported pushed to `origin/task/ARCH-053-API-002`; database-module integration and resolver revalidation remain required before acceptance.

### Files Changed

- `moda-interact-api/package.json`, `package-lock.json` — pin the published Shared contract package from `2.5.0` to `2.7.2`; add and register the isolated PostgreSQL resolver test command.
- `moda-interact-api/src/woocommerce/recovery-restore/contract.ts` — strict Shared request parsing, 4096-byte bound and request identity validation.
- `moda-interact-api/src/woocommerce/recovery-restore/service.ts` — parameterized read-only recovery/shop/installation query, latest-generation and seven-day eligibility, stored canonical HTTPS URL/path/query checks, constant-time SHA-256 token digest comparison, snapshot validation and complete offer-aware v1 response validation.
- `moda-interact-api/src/woocommerce/recovery-restore/routes.ts` — installation-authenticated POST, no-store 200, uniform recovery 404, malformed 400, unauthenticated 401, and safely logged dependency 503.
- `moda-interact-api/src/composition/woocommerce.ts`, `src/composition/routes.ts`, `src/index.ts` — wire resolver into production Woo route composition.
- `moda-interact-api/tests/unit/woocommerce/recovery-restore/service.test.ts`, `routes.test.ts` — focused authorization, contract, malformed input, token/URL tampering, uniform denial, no-write and log-redaction tests.
- `moda-interact-api/tests/integration/woocommerce/recovery-restore/service.postgres.test.ts`, `scripts/test-arch053-recovery-restore-postgres.mjs` — disposable PostgreSQL test for latest generation, second-shop isolation, unsupported snapshots, freshness and coupon-data preservation.
- `moda-interact-api/tests/unit/composition/routes.test.ts`, `tests/unit/composition/real-route-registration.test.ts`, `tests/unit/http/integration-runner-registration.test.ts` — route registration coverage and default disposable integration-runner registration. The runner guard now also lists the already-chained ARCH-049 runner it had omitted.
- This task file — execution checklists and Completion Report only. Architect Review remains unchanged.

### Work Completed

Implemented `POST /v1/woocommerce/recovery-restore/resolve` using `WooInstallationAuthenticator` and the published `@modainteract/moda-interact-shared/woocommerce` v1 request, snapshot and response schemas. The authenticated principal supplies tenant identity; caller fields cannot select a shop. A single parameterized `SELECT` scopes the recovery by ID and shop, joins the current Shop and installation, and requires the maximum generation for the same shop/checkout token. Eligibility requires an allowed status, unset completion/expiry flags, last external activity within seven days and not in the future, active Woo Shop and installation, current credential version, matching canonical site and Shop.domain, and an exact restore URL identity.

The stored URL is bounded and parsed, must be HTTPS on the canonical origin and expected root/home-subpath pathname, contain exactly the expected three unique query fields, bind `r` to the recovery, and carry a canonical 43-character base64url token. Submitted and stored token SHA-256 digests are compared with `timingSafeEqual`. Only a Shared-schema-validated supported snapshot is returned, with the required initial `outreachOffer: {kind:"NONE",reason:"NO_CONFIRMED_OFFER"}`. The service exposes only `$queryRaw`; it performs no Prisma writes, Redis access, queue publication, consent/message/cart operation or outbound-message lookup. Logs include bounded shop/recovery identifiers and outcomes, never tokens, stored URLs, coupons, customer data or exception contents.

### Validation Results

- `npm run test:arch053-recovery-restore:postgres` — passed against a uniquely named disposable PostgreSQL container; checks the actual parameterized resolver query with multiple generations, a second shop/installation, terminal generation, unsupported snapshot, stale recovery and an expired coupon preserved only as original snapshot data. Container cleanup is in `finally`; no hosted database was contacted.
- Focused `npx tsx --test tests/unit/woocommerce/recovery-restore/service.test.ts tests/unit/woocommerce/recovery-restore/routes.test.ts` — 7 passed.
- Focused `npx tsx --test tests/unit/composition/routes.test.ts tests/unit/composition/real-route-registration.test.ts` — 6 passed.
- Focused integration-runner registration guard — 1 passed.
- `npm test -- --test-reporter=dot` — 633 passed, 0 failed.
- `npm run typecheck` — passed; Prisma Client generated from the prepared API database submodule schema.
- `npm run lint` — passed with `--max-warnings=0`.
- `git diff --check` — passed.
- Published Shared 2.7.2 runtime probe — required Woo resolver request, response and offer schemas imported successfully.
- Initial `runTests` adapter invocation did not discover this repository's `node:test` files. Direct repository `tsx --test` commands were used. The first full suite run then identified the integration inventory's omission; its owner test manifest was corrected and the final full suite passed.

### Deviations

The API database submodule is pinned to commit `728734b7f1c05a9175ada032e113babeb8066cda`, whose Prisma schema does not yet include `CheckoutRecovery.wooRestoreSnapshot`. Per API ownership and the explicit no-gitlink rule, no database schema or submodule pointer was changed. The service uses a parameterized SQL projection for the field owned by DATABASE-001; until the accepted database revision is integrated into the API's database submodule, that query will fail closed as 503. No deployment/readiness claim is made.

### Assumptions

The `Shop.domain` created by the Woo installation flow is the canonical site URL, including its home subpath, as confirmed in the owning API code. Shared 2.7.2 is the accepted published contract version. The v1 response intentionally remains `NONE/NO_CONFIRMED_OFFER` until API-003.

### Unresolved Issues

The API schema has no persisted Woo order-event/terminal-order evidence model, so this task can suppress only recovery terminal state (`COMPLETED`, `EXPIRED`, `CANCELLED` and corresponding timestamps). An order event not delivered to Moda cannot be detected or treated as proof; the existing architecture records this as an observed-only limitation. No live merchant call or new cross-service order lookup was added.

### Architectural Concerns

The accepted DATABASE-001 submodule revision must be integrated before the new SQL projection is operational; the current branch deliberately does not stage or update the database submodule gitlink. Architect review should also confirm the intended residual risk for Woo order events that were never delivered to Moda. API-003 must enrich this same v1 response before integrated feature delivery; this API-002 implementation is not production feature certification.

### Prepared Worktree Evidence

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-053-API-002`, branch `task/ARCH-053-API-002`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-053-API-002`, branch `task/ARCH-053-API-002`.
- Launcher claim commit: `9b1ffd07b31f9ca510ddcf0ecfc0e682d35d5cdb`; dependency gate passed for SHARED-002 and DATABASE-001.
- Implementation commit: `756130ebf579b43c0e8d32557698ff26ecff0bf8`; remote task ref verified at that commit. The prepared implementation worktree's upstream was configured as `origin/main`; it was not synchronized or rebased during this attempt, and the task commit was explicitly pushed to `origin/task/ARCH-053-API-002`. `origin/main` remains at `13bbbd062c63844cacd5a943953e00731475c58e`.
- No API database submodule gitlink or other workspace-owned file was staged.

## Architect Review

### Review Status

Changes Requested — Attempt 1

### Review Notes

The implementation report confirms that the API database submodule was pinned to `728734b7f1c05a9175ada032e113babeb8066cda`, whose Prisma schema lacks `CheckoutRecovery.wooRestoreSnapshot`. The resolver therefore cannot execute its eligibility query against the task's prepared database module and fails closed with 503. The later local-only gitlink observation is not published integration evidence and does not satisfy this review gate.

Required for Attempt 2:
- Integrate the architect-accepted ARCH-053-DATABASE-001 revision into the API repository's `database` submodule on the API task branch; do not modify Database-owned schema or migration files and do not update the parent workspace gitlink.
- Regenerate the API Prisma client from that integrated schema and verify the SQL/Prisma projection selects `wooRestoreSnapshot` from the actual schema.
- Rerun the isolated PostgreSQL resolver test and demonstrate an eligible response using a supported persisted snapshot, alongside the focused authorization tests, typecheck, lint, and `git diff --check`.
- Update the Completion Report with the exact database submodule commit and fresh validation results. Keep the documented limitation concerning Woo order events never delivered to Moda unless new authoritative evidence resolves it.

The existing API-002 implementation and reported tests are otherwise retained for rework; this correction is limited to consuming the accepted Database module and proving the resolver's positive path against it. No production-readiness or integrated-feature acceptance is implied.

### Reviewed Files

Reviewed the API-002 implementation report, its recorded validation, and the prepared task/submodule evidence.

### Validation Reviewed

The reported unit, integration, typecheck, lint and diff checks do not establish that the resolver works with the accepted database schema: the report explicitly records the missing `wooRestoreSnapshot` field in the prepared API database submodule. Attempt 2 must rerun the resolver integration against the integrated module.

### Architecture Conformance

The route/service ownership and read-only design remain within API scope. Acceptance is blocked because the API task branch did not consume the accepted ARCH-053-DATABASE-001 schema revision; no database-module integration or executable eligible resolution is currently established.

### Follow-up

Return the task to `ready`, clear executor/claim metadata, and preserve Attempt 1 history. The launcher may prepare Attempt 2 after this review update is published on the parent task branch.
