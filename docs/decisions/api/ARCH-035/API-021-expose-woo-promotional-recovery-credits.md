---
id: ARCH-035-API-021
architecture_id: ARCH-035
title: Expose real WooCommerce promotional recovery-credit offers, selection and history
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 35
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables:
  - ARCH-035-WOOCOMMERCE-017
created: 2026-10-22
updated: 2026-10-22
---
# ARCH-035-API-021: Expose real WooCommerce promotional recovery-credit offers, selection and history

## Architecture

- Parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`.
- This task resumes **functional Promotions parity** without reactivating historical superseded `ARCH-035-API-006`.
- Existing Shopify reference: `moda-interact/app/services/promotions/promotion.service.ts` and `app/routes/app/promotions/route.tsx`.

## Objective

Provide authenticated Woo merchants with real promotional recovery-credit offers, active selection and history, and a safe promotion-selection command using existing Moda billing records.

## Context

`ARCH-035-WOOCOMMERCE-005` is Complete as a UI-only screen. `src/promotions/promotions-screen.js` defaults to `UNAVAILABLE` because no Woo merchant Promotions API exists. The earlier `API-006` contract was superseded when ARCH-035 became UI-only and remains historical; do not reopen it or mark it implemented.

## Scope

- Add API-owned merchant Promotions contract, GET and PUT routes, business service(s), route registration, OpenAPI specification and focused tests in `moda-interact-api`.
- Reuse `PromotionCampaign`, `PromotionCampaignTranslation`, `PromotionalCreditGrant`, `MerchantPromotionSelection`, `Shop` and `Subscription` from the existing database; **no schema migration** is authorized.
- Reuse the documented Shopify promotion eligibility, grant, lock and history semantics without importing the Shopify application authentication/runtime.
- Use existing Woo installation authentication and resolved tenant Shop, and the shared structured logger.

## Out of Scope

- WooCommerce coupon codes, discount selection, new promotions/campaign creation, billing-provider charges, Shopify API changes, credit allocation by the plugin, WordPress UI integration, additional tables, `_index.md` files.

## Requirements

1. Hosted endpoints: `GET /v1/merchant/promotions?offerPage=1&historyPage=1&locale=<supported-locale>` and `PUT /v1/merchant/promotions/selection`. Both require the **active authenticated Woo installation**, not a Shopify session or browser-supplied Shop ID. `offerPage` and `historyPage` are integers 1–1000; offer/history page size is 6. `locale` is an optional validated merchant **display** locale; missing/unsupported translations fall back safely without changing shop/customer language.
2. GET returns a validated, versioned, no-store JSON response:
   ```json
   {"schemaVersion":1,"revision":"opaque","offers":[],"offersPagination":{"page":1,"pageSize":6,"totalEntries":0,"totalPages":1},"selection":null,"history":{"entries":[],"page":1,"pageSize":6,"totalEntries":0,"totalPages":1}}
   ```
   Each `offers[]` item has `id`, `merchantTitle`, `merchantDescription`, `quantity`, `expiresAt`, `exhausted`, `previouslyClaimed`, `currentlySelected` and any explicit eligibility/denial state needed by the existing UI. `selection` when present has `campaignId`, `merchantTitle`, `remainingQuantity`, `expiresAt`, `locked`, plus authoritative reserved/committed state if displayed. Each `history.entries[]` item has `campaignId`, `campaignTitle`, `status`, `quantityGranted`, `committedQuantity`, `remainingQuantity`, `lastSelectedAt`, `expiresAt`. History status must follow established lifecycle values; it must not be reduced to invented labels by the API.
3. PUT accepts **only** `{ "campaignId": "opaque-id", "expectedRevision": "opaque" }` with bounded IDs/revision. It returns an authoritative `{schemaVersion:1,revision,selection}` on success. A stale revision or competing differing selection yields `409` with a stable error code; invalid input `400`; invalid/revoked installation `401`; ineligible, expired, closed, exhausted, mismatched plan/shop or locked different selection yields bounded denied/conflict responses. Do not leak other-shop records.
4. Implement concurrency-safe single-selection semantics using existing `MerchantPromotionSelection` uniqueness/version and grant keys. Repeated identical selection must **not** issue a second credit grant, reset quantity or bypass consumption/reservations. Only server-side eligible campaigns can be selected. The revision is derived from authoritative shop selection state and checked atomically; no client-generated credit state.
5. Effective quantity is `quantity - reservedQuantity - committedQuantity`; eligibility respects `GLOBAL`/`PLAN`/`SHOP` scope, Shop state, active plan, campaign active window and previously claimed/exhausted semantics, consistent with the existing Shopify service. Historical grants remain visible according to tenant ownership after expiry, even when they are not selectable.
6. Response validation and OpenAPI are owned by this API. Return dates in ISO-8601, numeric non-negative counts, stable `(createdAt DESC,id DESC)` history ordering, bounded Prisma selects, `Cache-Control: private, no-store` and logs through `@modainteract/moda-interact-shared/logging` without secrets/customer PII. Preserve existing Shopify promotion behaviours.

## Work Items

- [x] Inspect Shopify `promotion.service.ts` and existing database model/constraint semantics; record any discovered incompatibility before implementation.
- [x] Implement read endpoint with offers, locked selection, history and locale fallback.
- [x] Implement concurrency-safe selected-campaign write, error mapping and idempotent retry.
- [x] Add schema validators, OpenAPI and merchant route composition.
- [x] Add comprehensive focused and integration tests; record exact evidence.

## Interfaces / Contracts

- API owner: `moda-interact-api`; canonical published interface is the new API OpenAPI file plus runtime request/response schemas. Woo plugin consumes this through server-side `ModaApiClient`, never browser-to-hosted requests.
- Existing schemas: `billing.PromotionCampaign`, `PromotionalCreditGrant`, `MerchantPromotionSelection`; no new cross-service queue contract.
- Consumer task: `ARCH-035-WOOCOMMERCE-017`; avoid a second Woo-specific credit accounting implementation.

## Dependencies

None. Existing ARCH-026/027 Woo installation/billing foundations are already recorded Complete; reverify schema/package pins when claiming.

## Enables

- `ARCH-035-WOOCOMMERCE-017`.

## Acceptance Criteria

- [x] A connected merchant sees only eligible current offers and its own current/history grants; localization falls back correctly (route and PostgreSQL service tests; not a live merchant end-to-end test).
- [x] Two concurrent selection attempts, repeated identical requests and stale revision produce at most one valid grant/selection and no credit reset.
- [x] Shop/plan mismatch, inactive shop/subscription, expired/closed/exhausted campaigns, no selection, bad input, unauthenticated/revoked installation and cross-shop requests have verified bounded outcomes (focused tests and service checks).
- [x] Grant reserved/committed counts and historical status remain intact; existing Shopify Promotions tests stay passing. API-side balance/history tests passed, and targeted Shopify promotion service/route regression tests passed (43/43).
- [x] Versioned contract, OpenAPI, shared structured logging, no-store response and no secrets/customer PII are verified by API contract/route tests and source inspection.

## Validation

- [x] Focused service/route and disposable PostgreSQL concurrency/tenant tests using repository-provided commands.
- [x] Repository-declared typecheck/lint/build and relevant Shopify regression evidence where available. Typecheck, lint, build, 555/555 API unit tests, focused Promotions PostgreSQL integration, and targeted Shopify promotion tests passed.
- [x] `git diff --check` plus launcher-resolved canonical parent/implementation task worktree and Completion Report evidence. The canonical launcher resolved both worktrees; implementation and parent branches are clean and synchronized at review publication.

## Stop Condition

Set `status: review`, complete the report, return to `moda_architect` and STOP. Do not start the Woo consumer task.

## Implementation Notes

Prefer small route/contract/read/command modules and injected persistence/test seams. Do not copy Shopify app auth or reimplement promotional-credit accounting in the Woo plugin. If a contract field is inconsistent with the actual billing service, document it and return it to the architect; do not invent state.

## Completion Report

### Status

Complete — developer-owned Attempt 1 passed review and was explicitly completed on 2026-10-22. API implementation, API validation, Shopify regression evidence, and canonical worktree publication evidence are complete.

### Files Changed

Implementation repository `moda-interact-api/` (relative to its repository root):

- `openapi/merchant-promotions-v1.yaml`
- `package.json`
- `scripts/test-arch035-promotions-postgres.mjs`
- `src/composition/merchant.ts`
- `src/merchant/promotions/context.ts`
- `src/merchant/promotions/contract.ts`
- `src/merchant/promotions/projection.ts`
- `src/merchant/promotions/read.ts`
- `src/merchant/promotions/request.ts`
- `src/merchant/promotions/routes.ts`
- `src/merchant/promotions/service.ts`
- `tests/integration/merchant/promotions/service.postgres.test.ts`
- `tests/unit/composition/real-route-registration.test.ts`
- `tests/unit/http/integration-runner-registration.test.ts`
- `tests/unit/merchant/promotions/contract.test.ts`
- `tests/unit/merchant/promotions/fixtures.ts`
- `tests/unit/merchant/promotions/openapi-contract.test.ts`
- `tests/unit/merchant/promotions/routes.test.ts`
- `tests/unit/merchant/promotions/service.test.ts`

Parent workspace task/report file (this review-preparation update):

- `docs/decisions/api/ARCH-035/API-021-expose-woo-promotional-recovery-credits.md`

### Work Completed

- Inspected the existing Shopify Promotions reference and existing billing/installation model semantics. Reused `PromotionCampaign`, its translations, `PromotionalCreditGrant`, `MerchantPromotionSelection`, `Shop` and `Subscription` without schema changes.
- Added hosted authenticated Woo merchant read/selection endpoints: `GET /v1/merchant/promotions` and `PUT /v1/merchant/promotions/selection`. Authenticated shop identity comes from the Woo installation principal; no browser-supplied tenant ID or Shopify session is accepted.
- Implemented current scoped offers (`GLOBAL`/`PLAN`/`SHOP`), fixed six-item pagination, locale fallback, selected grant state and tenant-scoped history with deterministic `(createdAt DESC, id DESC)` ordering.
- Implemented server-derived selection revision, transactional guarded selection with Serializable retry, stable 409/422 denial mapping, same-campaign idempotent replay, and preservation of existing reserved/committed credit quantities. The API does not perform credit consumption or create a second accounting path.
- Added runtime payload validation, OpenAPI 3.1 specification, merchant route composition, private no-store response headers and structured logging through the Shared logging interface, omitting secrets/customer content.
- Added focused request/route/contract/service tests and disposable PostgreSQL coverage for campaign scopes, expiry/closure/exhaustion, authorization and revoked installation, stale revisions, concurrent selections, idempotency, existing grants/history and tenant isolation.
- Corrected test fixtures and runner registration during patch revisions: Attempt 2 resolved TypeScript/test-runner failures and a zero-quantity fixture; Attempt 3 fixed an expiry date violating `PromotionCampaign_expiry_after_start`. The production Promotions service was not changed by those fixture corrections.

### Validation Results

Evidence supplied in the developer's 22 October 2026 terminal logs:

| Command | Outcome | Evidence |
| --- | --- | --- |
| `npm run typecheck` | **PASS** | Prisma Client generated and TypeScript exited without diagnostics. |
| `npm run lint` | **PASS** | `eslint . --max-warnings=0`; no errors or warnings reported. |
| `npm run build` | **PASS** | Prisma Client generated; `tsc -p tsconfig.build.json` completed. |
| `npm test` | **PASS** | 555 passed, 0 failed, 0 skipped. |
| `npm run test:arch035-promotions:postgres` | **PASS (Attempt 3)** | 58 Prisma migrations applied to a disposable PostgreSQL database; 1/1 integration tests passed, including concurrency, history, revocation and tenant isolation. |

Earlier validation failures were corrected in later patches: Attempt 1 TypeScript errors and invalid campaign quantity; Attempt 2 expiry fixture violated `PromotionCampaign_expiry_after_start` (`23514`); Attempt 3 completed without a PostgreSQL integration failure.

**Canonical-review evidence verified:** the launcher resolved the canonical parent and implementation worktrees; implementation commit `bde0019` and parent report commit `41c95a36` are published on `task/ARCH-035-API-021`, both branches are clean and synchronized, and targeted Shopify Promotions regression tests passed.

### Git / VCS

Evidence supplied by the developer on 22 October 2026 (shell output and task worktree archive):

- Task branch: `task/ARCH-035-API-021` in both repositories (implementation **verified**; parent worktree branch **not yet independently reported**).
- Parent physical task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-API-021` (developer `pwd` and attached snapshot).
- Implementation physical worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-API-021` (developer `pwd -P`).
- Implementation branch: `task/ARCH-035-API-021` (**verified** via `git branch --show-current`).
- Implementation HEAD: `bde00199207056c701c8b71c7b162552cebedeff` (**verified** via `git rev-parse HEAD`).
- Remote implementation branch: `origin/task/ARCH-035-API-021` at the identical SHA (**verified** via `git ls-remote --heads origin task/ARCH-035-API-021`; publication confirmed).
- Implementation `git status --short`: empty (**clean** at the time of the supplied output).
- Canonical launcher route: verified for the primary workspace and both task worktrees.
- Parent task branch: `task/ARCH-035-API-021`, clean at `41c95a36`, synchronized with its remote (`0 0`).
- Implementation branch: `task/ARCH-035-API-021`, clean at `bde0019`, synchronized with its remote (`0 0`).
- Launcher-resolved worktree ownership/isolation and shared/default checkout non-mutation: verified by the route and dedicated paths.
- `git diff --check` in both task worktrees: PASS.

### Deviations

- No production schema changes, Shopify source changes, Woo plugin code changes or `_index.md` edits.
- Attempt 2 also updated existing unit/integration runner registration expectations, including an existing Support integration suite; no Support business logic was modified.
- No additional production API behaviour was introduced by Attempt 3 (test-fixture change only).

### Assumptions

- The prior numbered patch files are **patch revisions** and do not by themselves establish the canonical YAML `attempt` or task claim. Preserve the current launcher-owned attempt number, `executor` and `claimed_at` from the real parent task worktree.
- The current attached parent task snapshot contains the already claimed Attempt 1 and API source, and the developer supplied matching local/remote implementation commit evidence. The snapshot itself does not contain authoritative launcher preparation evidence or parent Git metadata.
- Merchant display localization does not change tenant/customer conversation language; credit spend/consumption remains owned by existing billing logic.

### Unresolved Issues

- No remaining API test failure is shown in the supplied latest logs.
- No remaining API or Shopify Promotions regression failure is shown. Explicit developer completion has now been recorded below.

### Architectural Concerns

- No new database contract or cross-repository queue contract was introduced. The Woo consumer task `ARCH-035-WOOCOMMERCE-017` remains dependent on architect acceptance of this API task.
- The architect should independently inspect the actual implementation against the parent architecture and reconcile any runtime-contract difference. This report is not an architect acceptance.

## Architect Review

### Review Status

Passed/Accepted — developer Attempt 1 reviewed, reconciled, and explicitly completed.

### Review Notes

- Implementation branch is clean at `bde0019` and synchronized with its remote; the parent task branch is clean at `41c95a36` and synchronized with its remote.
- API typecheck, lint, build, 555 unit tests, focused Promotions PostgreSQL integration, and targeted Shopify Promotions regression tests (`43/43`) pass.
- No schema migration, Shopify production-source change, Woo plugin change, or `main` merge was performed.

### Reviewed Files

- `openapi/merchant-promotions-v1.yaml`
- `src/merchant/promotions/`
- `src/composition/merchant.ts`
- `scripts/test-arch035-promotions-postgres.mjs`
- `tests/unit/merchant/promotions/`
- `tests/integration/merchant/promotions/service.postgres.test.ts`

### Validation Reviewed

- `npm run typecheck` — PASS
- `npm run lint` — PASS
- `npm run build` — PASS
- `npm test` — PASS, 555/555
- `npm run test:arch035-promotions:postgres` — PASS
- Shopify promotion service/route tests — PASS, 43/43
- `git diff --check` — PASS

### Architecture Conformance

Accepted for the API-owned Woo Promotions contract: authenticated installation-scoped GET/PUT routes, existing billing records only, tenant-safe eligibility/history, concurrency-safe selection, bounded versioned responses, no-store headers, structured logging, and no duplicate credit-accounting path.

### Follow-up

No implementation follow-up remains. The direct downstream task `ARCH-035-WOOCOMMERCE-017` was inspected through the canonical launcher and remains `pending`; it was not claimed, started, or otherwise mutated by this completion.

## Developer Completion Decision — 2026-10-22

Explicit completion was authorized for Attempt 1 after the durable `Passed/Accepted` review. All required Work Items and Acceptance Criteria are checked, the implementation branch and parent report branch are clean and published, and no merge to `main` is required for task completion. The task transitions to `status: complete` with `executor: null`, `claimed_at: null`, and `attempt: 1`.

Dependency frontier reconciliation: `ARCH-035-WOOCOMMERCE-017` was resolved as `pending` by the canonical launcher. Its task report was not present in the resolved parent worktree for an authorized status update, so no downstream task record was changed and no task was started.

## Developer Takeover Amendment — 2026-10-22

The developer explicitly invoked `/moda_developer_create ARCH-035-API-021` for this ready agent-owned task. Execution and completion ownership are transferred to the developer (`execution_mode: developer`, `completion_mode: developer`); logical ownership remains `assigned_agent: moda_api`, and task scope, dependencies, acceptance criteria, and validation requirements are unchanged. The canonical launcher will record the developer claim after worktree preparation and dependency verification.
