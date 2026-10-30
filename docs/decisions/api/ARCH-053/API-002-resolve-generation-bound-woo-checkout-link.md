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
status: complete
priority: 40
executor: null
claimed_at: null
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

Architecture ID: `ARCH-053`. Document: `docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md`. Coordinator: `moda_architect`. Materialised and accepted Complete at Attempt 2. No customer-facing deployment is authorized by this task.

## Objective

Resolve Woo recovery link with installation and generation authorization. One bounded outcome in `moda-interact-api` owned by `moda_api`.

## Context

The task was claimed for Attempt 2 after SHARED-002 and DATABASE-001 were accepted Complete. The original 2026-10-30 07:59 dependency snapshot is historical; the launcher re-gated both prerequisites before the attempt. ARCH-052 remains separately owned dynamic discount discovery and is not a checkout-URL implementation domain.

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
- [x] `npm run typecheck`; `git diff --check`
- [x] `npm run lint` was run; its only reported finding is the unrelated current-main `no-empty` at `src/merchant/support/routes.ts:75`. Focused ESLint over task-owned code and tests passes; see the Completion Report.

## Stop Condition

When Work Items, Acceptance Criteria and required Validation are complete, update ONLY this task's authorised execution metadata, checklists and Completion Report, set `status: review` and return to `moda_architect`; **STOP**. Do not begin Enables, merge task branches, push `main` or change Architect Review yourself.

## Implementation Notes

Keep API route order consistent with `composeApiRoutes` and avoid introducing a new generic logger, CORS surface, redirect or cached GET. Any gateway routing gap must be reported to architect, not fixed in API code.

## Completion Report

### Status

Accepted Complete at Attempt 2. Attempt 1's implementation commit `756130ebf579b43c0e8d32557698ff26ecff0bf8` and its report are retained below as historical evidence. Attempt 2 integrates the accepted DATABASE-001 schema tree in the API database submodule and reruns the resolver validations.

### Attempt 2 Rework

#### Architect Review Corrections

- **Database module integration — implemented.** API commit `7fc1e1035e6b0678c5a9364cdccde16bee76f59f` updates only the API repository's `database` submodule pointer to `af77c594ecbfc78c26d01c0021a090830884bbff`. The accepted DATABASE-001 commit is `33d2f6b6107ea57bd9dfe38e2e3d6e24df9556be`. The accepted commit and pinned submodule commit have the identical tree `f65f86e06b63410f8223ecc9b0f3baa5272d7273`; their package, Prisma schema, migrations and DATABASE-001 PostgreSQL test artifacts have no diff. `database/prisma/schema.prisma` contains `CheckoutRecovery.wooRestoreSnapshot Json?`. No Database-owned source was edited, and no parent-workspace submodule gitlink was staged.
- **Prisma client regeneration — implemented.** `npm run typecheck` ran `prisma generate --schema database/prisma/schema.prisma` against the integrated schema and then completed TypeScript checking successfully.
- **Resolver and required validation — blocked only on repository-wide lint.** The isolated PostgreSQL integration and all seven focused resolver authorization/service tests pass. `npm run typecheck`, focused ESLint over API-002 implementation/tests, and `git diff --check` pass. Required `npm run lint` was rerun but reports one unrelated `no-empty` error at `src/merchant/support/routes.ts:75`, introduced by current `origin/main` commit `13bbbd062c63844cacd5a943953e00731475c58e`; `git blame` confirms the line belongs to that mainline commit and the file is outside this task's change. No unrelated source edit was made.
- **Shared v1 contract — implemented.** The lockfile and installed dependency resolve to Shared `2.8.0`. Runtime imports from `@modainteract/moda-interact-shared/woocommerce` confirmed `WooRestoreResolveRequestV1Schema` and `WooRestoreResolveResponseV1Schema` are exported. The response remains strict v1 with `outreachOffer: {kind:"NONE",reason:"NO_CONFIRMED_OFFER"}` until API-003.

#### Attempt 2 Validation Results

- `npm run test:arch053-recovery-restore:postgres` — passed; isolated PostgreSQL verified the real resolver SQL, latest-generation and tenant gates, coupon data preserved only inside the snapshot, and an eligible response using a supported persisted snapshot.
- `npx tsx --test tests/unit/woocommerce/recovery-restore/service.test.ts tests/unit/woocommerce/recovery-restore/routes.test.ts` — 7 passed, 0 failed.
- `npm run typecheck` — passed; regenerated Prisma Client v6.19.3 from `database/prisma/schema.prisma` before TypeScript checking.
- `npx eslint src/woocommerce/recovery-restore src/composition/woocommerce.ts src/composition/routes.ts src/index.ts tests/unit/woocommerce/recovery-restore tests/integration/woocommerce/recovery-restore tests/unit/composition --max-warnings=0` — passed.
- `npm run lint` — failed on the unrelated current-main `no-empty` finding at `src/merchant/support/routes.ts:75`; task-owned files pass the focused ESLint command above.
- `git diff --check` — passed.
- Shared runtime export probe — both required resolver v1 schemas imported successfully from installed Shared `2.8.0`.

#### Attempt 2 Scope and Remaining Caveats

No resolver behavior or Database-owned files were changed in this rework; the required change is consumption of the accepted database schema through the API repository's `database` submodule. The resolver remains read-only, strict Shared single-v1, and returns `NONE/NO_CONFIRMED_OFFER` until API-003. The order-terminal limitation remains observed-only: Woo orders whose events were never delivered to Moda cannot be detected from the API's available persisted evidence. No production-readiness or integrated-feature claim is made. The repository-wide lint failure is recorded for architect disposition; it was not fixed outside API-002 scope.

### Attempt 1 Report (Retained)

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

## Architect Review — Attempt 2 (Accepted Complete)

### Review Status

Accepted Complete at Attempt 2.

### Review Notes

Reviewed the Attempt 2 API implementation and report. The API task branch now pins the accepted DATABASE-001 schema tree (`af77c594ecbfc78c26d01c0021a090830884bbff`), and Prisma Client generation/typecheck used that schema. The resolver performs a parameterized read scoped by the authenticated installation and shop, admits only the current recovery generation, validates the stored HTTPS URL and canonical site binding, checks the token digest in constant time, and returns only the published Shared v1 response for a supported snapshot. It remains read-only and does not publish queue jobs or call Woo. The initial `NONE/NO_CONFIRMED_OFFER` value is the required temporary v1 behavior until API-003. No blocking code or architecture issue was found.

Repository-wide lint was rerun and still reports one unrelated `no-empty` finding in `src/merchant/support/routes.ts:75`, from current `origin/main`; the report says the task-owned files pass focused ESLint. This does not indicate a defect in this task's changed files and is recorded as an outstanding repository baseline issue, not as a passing full-repository lint result. The documented order-event limitation remains: an order event never delivered to Moda cannot be inferred from the API's available durable evidence.

### Reviewed Files

- API-002 resolver service, request contract and route.
- Woo route composition and integration-runner registration changes.
- Focused route/service tests and isolated PostgreSQL resolver test.
- API database submodule pointer and the DATABASE-001 schema revision.
- This task's Attempt 2 Completion Report and validation evidence.

### Validation Reviewed

The report records the isolated PostgreSQL resolver integration, 7 focused authorization/service tests, Prisma generation and `npm run typecheck`, focused ESLint, Shared 2.8.0 runtime export checks, and `git diff --check` as passing. Full `npm run lint` was run and has the unrelated finding described above. The API implementation task branch is clean at `a86b339` and its `origin/task/ARCH-053-API-002` ref points to the same commit. Validation was reviewed from the durable report; it was not rerun during architect review.

### Architecture Conformance

Conforms to the API-002 scope and ARCH-053 authorization boundary. It does not expose a public bearer-link read, mutate recovery state, or claim that API-002 alone completes the customer-facing restore flow. No production deployment is authorized; API-003 and the compatible WooCommerce restoration path remain separate gates.

### Follow-up

`ARCH-053-WOOCOMMERCE-002` remains Pending because `ARCH-053-WOOCOMMERCE-001` is Ready, not Complete. `ARCH-053-API-003` remains Pending because `ARCH-053-BACKGROUND-004` is Pending. No downstream task is eligible for promotion, and no task branch was merged to `main`.
