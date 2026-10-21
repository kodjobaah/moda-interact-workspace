---
id: ARCH-035-API-020
architecture_id: ARCH-035
title: Expose Woo two-way merchant Support API
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 31
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables:
  - ARCH-035-WOOCOMMERCE-016
created: 2026-10-21
updated: 2026-10-22
---

# ARCH-035-API-020: Expose Woo two-way merchant Support API

## Architecture

Architecture ID: `ARCH-035`. Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`. Coordinator: `moda_architect`.

**Lifecycle:** Portable definition from the developer-supplied 2026-10-21 workspace ZIP, now materialised in the canonical parent task worktree. No implementation claim existed before this developer preparation.

## Objective

Expose the existing Shopify-equivalent merchant Support thread/history, compose, and read-state commands to authenticated WooCommerce installations through the hosted API.

## Context

The existing `ARCH-035-API-001` was superseded without implementation during the former UI-only phase. `ARCH-035-WOOCOMMERCE-001` has since delivered the Support UI but its real client still has `read:false`, `send:false`, `markRead:false`. Shopify reference: `moda-interact/app/services/merchant-support/merchant-support.service.ts` and `app/routes/app/merchant-support/route.jsx`. ARCH-046 consent notices use the same existing Support SYSTEM messages; a separate read-only notice endpoint would duplicate this thread.

## Scope

- Add bounded installation-authenticated Support read, send and mark-read routes and register in the current modular API composition.
- Reuse existing support.MerchantSupportThread and support.MerchantSupportMessage, their translation pipeline and Shared merchant-communications validators.
- Ship strict API DTO validation/OpenAPI contract and focused service/route/database tests; keep read and write code in independently testable modules.

## Out of Scope

- No new Support schema/migration, separate notice feed/inbox, customer WhatsApp send, admin queue redesign or Woo/PHP code.
- No merchant Shopify sessions or Shopify-only refund, purchase cancellation or privileged admin actions.

## Requirements

- Provide `GET /v1/merchant/support/messages?page=1&pageSize=25`, `POST /v1/merchant/support/messages` with `{body,actionId}` and `POST /v1/merchant/support/messages/{messageId}/read` with empty body; own exact response DTOs and publish them in OpenAPI. A schemaVersion field is required.
- Read returns page/pageSize/total/totalPages/unread/items, ordered exactly as Shopify merchant Support; include `MERCHANT`, available `ADMINISTRATIVE` and available `SYSTEM`, translated/original display and safe `systemCode`/`systemVersion`. Bounded pageSize 10/25/50; reject invalid/unexpected inputs.
- Authenticate only via existing active Woo installation credentials and derive Shop server-side. Never accept browser-supplied `shopId`, `shopifyUserId`, platform-admin identifier or tenant owner. Preserve Shopify-like ability to read Support in supported restricted lifecycle states; do not relax a revoked/uninstalled installation.
- Validate 500 Unicode graphemes using the published `AuthoredSupportBodySchema` and `countUnicodeGraphemes` contract. Save MERCHANT message with null `shopifyUserId`; preserve default-language/translation rules and `needsAdminResponse`/merchant-version semantics.
- Use per-shop actionId idempotency with unique `sourceKey` (`woo-support:<shopId>:<actionId>` or a deterministically bounded equivalent); same action + body returns the same result, same action + changed body returns conflict. Concurrent duplicates must not produce multiple Support messages or translations.
- Mark-read is monotonic and restricted to the authenticated Shop-owned ADMINISTRATIVE or SYSTEM message; another shop/unknown message must never leak existence. Read is not a send and must not consume usage credits.
- Translation pending-state persistence precedes best-effort queue dispatch; dispatch outage must not discard a committed merchant message. Use Shared structured logging without credentials, message bodies or sensitive PII; protect provider and database failures.
- Compatibility: existing Shopify Support flows, internal admin reply handling, and ARCH-046 SYSTEM notices must remain functional.

## Work Items

- [x] Reuse existing Woo installation authentication, API route/error infrastructure, Support persistence and Shared merchant-communications contracts.
- [x] Implement tenant-scoped Support history with translated/original display, pagination, unread totals and SYSTEM notices.
- [x] Implement transactional, action-ID-idempotent merchant composition and durable translation-pending state before best-effort dispatch.
- [x] Implement shop-scoped monotonic mark-read for ADMINISTRATIVE/SYSTEM messages.
- [x] Register strict Woo-authenticated routes, runtime DTO validation, OpenAPI and focused unit/integration coverage.

## Interfaces / Contracts

- Owner of HTTP DTOs: `moda-interact-api`. Consumers: WooCommerce privileged WordPress REST proxy in `ARCH-035-WOOCOMMERCE-016`; no browser direct hosted credentials.
- Reuse published `@modainteract/moda-interact-shared/merchant-communications` (`AuthoredSupportBodySchema`, translation queue contracts, language/length rules) and existing Prisma Support schema.
- All three hosted routes run only under Woo installation authentication, never Shopify session authentication.

## Dependencies

None

## Enables

- `ARCH-035-WOOCOMMERCE-016`

## Acceptance Criteria

- [x] Shop A cannot list, send as, or mark-read for Shop B; tests cover revoked/uninstalled/rotated installation credentials.
- [x] Read projection includes SYSTEM notices, ADMINISTRATIVE replies and MERCHANT messages, with safe display/translation metadata.
- [x] Repeated/concurrent action IDs replay a single message; changed-body reuse returns conflict without duplicate translation records.
- [x] 500 Unicode graphemes are accepted and 501 rejected; translation and processing-state handling are covered.
- [x] No new tables, support pipelines, billing charges or Shopify regressions. The committed API change introduces no migration or billing path; existing Shopify Support service and route regression suites pass.
- [x] OpenAPI and validated runtime DTOs agree; authorization, invalid-request, unavailable and conflict responses are covered by focused tests.

## Validation

- [x] Focused route/service unit tests and disposable PostgreSQL tests passed; separate Shopify Support regression execution also passed.
- [x] API `typecheck`, zero-warning `lint`, `build` and `git diff --check` passed in the developer worktree.

## Stop Condition

After all required Work Items, Acceptance Criteria and task-specific Validation are satisfied, update the task Completion Report and `status: review`, return to `moda_architect` and STOP. Do not perform dependent tasks, create new task implementation worktrees, merge or push main, or change `docs/decisions/**/_index.md`.

## Implementation Notes

Reuse business rules from Shopify as the behaviour reference, but do not import the Shopify app runtime into the hosted API. Avoid copying reusable published validators. Do not reinterpret the earlier superseded `API-001` as completed or reactivate its history. Keep implementation bounded to the hosted API service.

Start with `scripts/start-agent-task.py --prepare` through the normal `/moda-task` path. The prepared packet proves canonical parent/implementation worktree identity, synchronization and submodule state; record that packet in the Completion Report. Re-read the latest task and architect review before claiming. Use actual repository scripts. The architect in this externally supplied ZIP session has not created any Git branches or worktrees.

## Completion Report

### Status

Complete — Attempt 1 passed developer self-review and the developer recorded the explicit completion decision on 2026-10-22. The implementation and parent report are committed and pushed; required focused validation, including Shopify Support regression tests, passed. No merge to `main` was performed.

### Files Changed

The published implementation commit changes only these 18 files in `moda-interact-api`:

- `openapi/merchant-support-v1.yaml`
- `package.json`
- `scripts/test-arch035-woo-support-postgres.mjs`
- `src/auth/woo-installation/authenticator.ts`
- `src/composition/merchant.ts`
- `src/index.ts`
- `src/merchant/support/commands.service.ts`
- `src/merchant/support/contract.ts`
- `src/merchant/support/installation.ts`
- `src/merchant/support/read.service.ts`
- `src/merchant/support/request.ts`
- `src/merchant/support/routes.ts`
- `src/merchant/support/translation-queue.ts`
- `tests/integration/merchant/support/service.postgres.test.ts`
- `tests/unit/auth/woo-installation/authenticator.test.ts`
- `tests/unit/merchant/support/contract.test.ts`
- `tests/unit/merchant/support/openapi.test.ts`
- `tests/unit/merchant/support/routes.test.ts`

### Work Completed

- Added Woo installation-authenticated `GET /v1/merchant/support/messages`, `POST /v1/merchant/support/messages`, and `POST /v1/merchant/support/messages/{messageId}/read`. Shop identity is derived from the installation on the server, not request-supplied tenant or Shopify identities.
- Reused the existing Support thread/message tables and Shared validators. Added paginated, chronological history with unread totals, translated/original display and SYSTEM notice visibility; permitted supported restricted-installation reads while rejecting revoked credentials.
- Implemented 500-grapheme body validation, shop-scoped action-ID idempotency, safe changed-body conflict responses and transactional writes; persisted pending translation state before best-effort queue dispatch.
- Implemented monotonic, tenant-scoped ADMINISTRATIVE/SYSTEM mark-read without outbound messaging or billing effects.
- Added strict versioned HTTP DTOs, safe error handling, API composition, OpenAPI, route/contract/authentication unit tests and a disposable PostgreSQL concurrency/tenant-isolation integration test.
- Corrected the PostgreSQL test runner's ESLint `no-undef` failure by explicitly importing `process` from `node:process`; no production behavior changed in this follow-up correction.

### Validation Results

Developer execution evidence supplied on 2026-10-21:

- `npm run test:arch035-woo-support:unit`: **PASS, 12/12 tests**, including Woo authentication, restricted/revoked installations, bounds and Unicode graphemes, versioned DTO/OpenAPI, route validation and safe error mapping (`typescript(20261021-223534)`).
- `npm run test:arch035-woo-support:postgres`: **PASS, 1/1 disposable PostgreSQL integration test**, covering concurrent duplicate actions, tenant isolation, SYSTEM/Support visibility, queued-translation outage and monotonic read state. All 58 existing migrations applied to the disposable database; no new migration was added (`typescript(20261021-223534)`).
- Shopify merchant Support regressions: **PASS, 20/20 tests** across `tests/unit/merchant-support-service.test.ts` and `tests/unit/merchant-support-route.test.ts` in the existing Shopify app (`npm test -- tests/unit/merchant-support-service.test.ts tests/unit/merchant-support-route.test.ts`, 2026-10-22).
- `npm run typecheck`: **PASS**; Prisma Client v6.19.3 generated and TypeScript typechecked without errors (`typescript(20261021-225420)`).
- `npm run lint`: **PASS**, `eslint . --max-warnings=0` with no errors or warnings after the runner-only `node:process` correction (`typescript(20261021-225420)`). The initial run reported five `process`-related `no-undef` errors; these were corrected before publication.
- `npm run build`: **PASS**, Prisma generation and `tsc -p tsconfig.build.json` completed successfully (`typescript(20261021-225420)`).
- `git diff --check`: no whitespace errors reported in the supplied command output. The final local `git status` after the commit/push reports `working tree clean` and `up to date with origin/task/ARCH-035-API-020`.
- Published commit and remote reference: **verified** at `dff135fe4f195f63d49d0cde66fd6556802ea8e1`; its 18 changed files match the user's commit output and the repository revision.
- Canonical task worktrees were verified: parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-API-020` on `task/ARCH-035-API-020`, implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-API-020` on the same task branch. Both are clean; parent and implementation task branches are synchronized with their origin task refs. The implementation is based on current `origin/main`.

### Deviations

No production feature deviation or database-schema change identified. The only post-test correction was the explicit Node `process` import in the disposable PostgreSQL test runner; the full lint/typecheck/build checks were rerun successfully afterward.

### Assumptions

- The developer's reported clean and synchronized implementation worktree is the same `task/ARCH-035-API-020` branch containing published commit `dff135fe4f195f63d49d0cde66fd6556802ea8e1`.
- Existing Support persistence, translation queue contract and Shopify implementation remain owned by their original modules. The new routes are Woo installation-authenticated and do not establish a Shopify session.

### Unresolved Issues

No known required work item or acceptance criterion remains incomplete. The disposable PostgreSQL integration passed in the supplied developer evidence; focused API and Shopify regression suites were also executed during this review and passed. No implementation or parent-report changes remain uncommitted.

### Architectural Concerns

No new Support table, separate merchant inbox, billing path, WhatsApp pipeline, WooCommerce/PHP change or Shared package contract was introduced. This implementation provides hosted routes for dependent `ARCH-035-WOOCOMMERCE-016`; consumer/UI integration remains a separate task. Retain the existing `ARCH-035-API-001` supersession history.

## Developer Self-Review - Passed/Accepted

Attempt 1 passed developer self-review. All Work Items and Acceptance Criteria are complete; the API implementation is committed and pushed at `dff135fe4f195f63d49d0cde66fd6556802ea8e1`; the focused Woo Support suite passed 12/12, the disposable PostgreSQL integration passed 1/1, and existing Shopify Support service/route regressions passed 20/20. Typecheck, lint, build and diff hygiene passed in the supplied validation evidence. The accepted self-review remains historical and unchanged.

## Developer Completion Decision

On 2026-10-22, the developer explicitly completed `ARCH-035-API-020` with `/moda_developer_update ARCH-035-API-020 complete`. The durable Attempt 1 Passed/Accepted self-review is unchanged; all required Work Items, Acceptance Criteria and validations are recorded as passing. Status is `complete`; executor and claimed_at are null; attempt remains 1. The implementation and parent task branches are published. No merge to `main` was performed.

## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

Definition approved for handoff; no implementation has been accepted.

## Developer Takeover and Materialisation Amendment — 2026-10-21

The developer explicitly invoked `/moda_developer_create ARCH-035-API-020` for this ready agent-owned portable task. The definition was materialised on the canonical parent task branch from the supplied task content. Execution ownership is transferred to the developer and completion requires an explicit developer decision after architect review. The logical repository owner remains `moda_api`; task scope, dependencies, acceptance criteria and validation requirements are unchanged.
