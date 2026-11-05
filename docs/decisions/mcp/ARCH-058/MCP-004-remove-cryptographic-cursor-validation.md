---
id: ARCH-058-MCP-004
architecture_id: ARCH-058
title: Remove cryptographic cursor validation from mcp pagination
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 30
executor: codex
claimed_at: 2026-11-05T14:05:48Z
attempt: 1
depends_on: []
enables: []
created: 2026-11-05
updated: 2026-11-05
---

# ARCH-058-MCP-004: Remove cryptographic cursor validation

## Architecture

ARCH-058; docs/architecture/ARCH-058-commerce-agent-product-discovery.md. Coordinator: moda_architect. This explicitly overrides earlier signed-cursor requirements in ARCH-058-MCP-002 and historic product pagination definitions.

## Objective

Make MCP commerce tools paginate without cryptographic cursor validation or a cursor secret.

## Context

Developer explicitly requested removal after absent COMMERCE_CURSOR_SECRET hid commerce_search_products. This is removal, not improved error handling. Existing tenant authorization remains the security boundary.

## Scope

MCP product search and discount catalogue pagination, runtime capability advertisement and ports/config/docs. Inspect src/execution/policy/product-search-cursor.ts, shopify-core.ts, shopify-core-executor.ts, src/execution/discount-catalogue.ts, src/runtime/{ports,prisma,service-ports}.ts, README.md and .env.example. Search every remaining cursor-secret consumer in this repository. Cover Shopify product edges, Woo product offsets, taxonomy/category search progress and discount catalogue afterId. Product search must be advertised and callable without COMMERCE_CURSOR_SECRET when all actual authorization/provider prerequisites are satisfied; other independent failures remain enforced.

## Out of Scope

Other repository implementation; credential encryption; authentication; tenant isolation; new Shared wire contracts; deployment/cutover; unrelated cleanup.

## Requirements

Remove Moda cursor signing, encryption/authentication, expiry enforcement and query/shop/connection/mode/policy fingerprint binding checks. Remove COMMERCE_CURSOR_SECRET configuration, minimum-length gates and dependency injection from the owning runtime. A continuation is untrusted pagination position only; it never supplies shop identity, provider host, credentials, authorization, policy, SQL fragments or entitlement. Resolve those from the authenticated current call every time. Retain bounded string/JSON parsing, known version/shape, finite safe nonnegative offsets and bounded IDs/provider tokens, existing Shared 2048-character wire bound, page/scan/output limits, parameterized database queries and provider cancellation/deadlines. Do not add another secret, database cursor store, compatibility signature verifier or alternate generic crypto implementation.

New continuations are unsigned versioned position envelopes (base64url JSON where multiple progress fields are needed); fields contain only progress, not auth/query bindings. They are not encrypted: never serialize secrets, customer payloads or tenant context. Forward native upstream opaque cursors unchanged inside the position envelope to the current authenticated provider; never decode/rewrite provider-owned cursors or accept provider URLs/SQL. Remove cursor-based filter/mode/fingerprint mismatch rejection; apply the current call's normal filters and policy to every returned row. Changing filters may restart/skip/duplicate positions; pagination is not a snapshot or correctness authority. Current NONE/disabled policy still denies data even with a supplied cursor.

Compatibility: make a coordinated breaking deployment of these internal pre-production continuations. Old Moda HMAC product v2, encrypted catalogue and Commerce signed tokens are not migrated or verified: return the established bounded INVALID_INPUT restart instruction, allowing the caller to retry from cursor null. Do not infer legacy tokens as arbitrary valid provider cursors. No public tool names, Shared cursor field types or provider cursor protocols change. Rollback restarts pagination; no durable business data migration. Confirm actual deployment context before execution; if production compatibility is now required, return that conflict to the architect rather than inventing a bridge.


## Work Items

- [x] Inventory all owned paginated operations and remove cursor cryptography/binding/secret gates.
- [x] Preserve bounded parsing, current-call authorization and provider/database safety.
- [x] Update focused tests, environment examples and runtime documentation.

## Interfaces / Contracts

Keep published Shared tool input/output schemas, cursor null/string fields and maximum lengths unchanged. Upstream cursors stay provider-owned opaque data. No cross-service credential changes or new published contract required. Commerce task ARCH-058-COMMERCE-002 owns preview parity.

## Dependencies

None. The existing implemented pagination surfaces are available; these repository-owned removals can be reviewed independently.

## Enables

None. Execution does not authorize follow-on tasks or system-test runs.

## Acceptance Criteria

- [x] All owned paginated operations work with absent, short or formerly configured cursor secret, with no cursor cryptographic or binding check.
- [x] Valid unsigned pagination progresses; malformed/oversized/unsafe progress is bounded and rejected.
- [x] Old Moda signed/encrypted cursors request restart without secret or verification.
- [x] Changed query/filter does not trigger old cursor binding checks.
- [x] Cross-tenant copied/manipulated positions cannot access another shop or bypass current policy.
- [x] Provider opaque cursors pass through unchanged; no host/query injection or unbounded scan.
- [x] Docs/config no longer require COMMERCE_CURSOR_SECRET for owned runtime.
- [x] No credential encryption/authentication control was removed.

## Validation

- [x] Inspect package.json and run declared focused pagination/executor/advertisement tests.
- [x] Cover no-secret listing/call, multiple pages, changed filters, legacy cursor restart, malformed progress, current-policy NONE/denial and two-tenant isolation.
- [x] Run repository-declared typecheck/build required by local instructions; record exact commands/results.
- [x] Search owned runtime/config for residual cursor secret/crypto gates; explain unrelated cryptography retained.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation, finish Completion Report, set review, return to moda_architect and STOP. No deployment or follow-on execution.

## Implementation Notes

Use current code as baseline, not an old ARCH-058 patch. Retain semantic operational logging without customer/cursor payload exposure. Standard provider validation errors remain provider errors; removing Moda cursor binding does not remove authorization.

## Completion Report

### Status

Ready for Review — Attempt 1, codex, 5 November 2026. Implementation committed/pushed as `2f5bf96504063cc93f170da53baf37d177aaf2a7` on `task/ARCH-058-MCP-004`. No architect acceptance, deployment or follow-on execution is asserted.

### Prepared Execution / Deployment Context

- The developer explicitly confirmed in this session: **“Yes—pre-production; restarts are fine.”** This satisfies the task's deployment-context gate before implementation. Old pagination sessions may restart; no production compatibility bridge is required.
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-058-MCP-004`; implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-058-MCP-004`. Both branches `task/ARCH-058-MCP-004`. Parent reused, implementation newly created by launcher; no shared/default checkout or other task worktree was switched or edited.
- Launcher dependency gate passed (no explicit prerequisites); both remote task fast-forwards not needed, both origin/main integrations already current. Parent start `d9a3b59c75fdbf50618cb092c4ff07c542b44eef`; implementation start `bd3357d9e2642c11029e03f2151187d6988120dd`.
- Durable claim `210252232a6be56a358ae716529dfd7bbd93ce24`, Attempt1, executor codex, `2026-11-05T14:05:48Z`. Parent end is this report's publication commit, rather than an invented self-referential SHA. Implementation end `2f5bf96504063cc93f170da53baf37d177aaf2a7`.
- Launcher recursive submodule sync/update passed; nested Database recorded/working commit `bd2d09066a8eb178a56f48fbbf88df637c411059`, unchanged.
- `npm ci` and Prisma generation passed. Actual installed Shared5.0.0, Prisma client6.19.3, MCP SDK1.30.0, Zod4.6.5; prescribed workspace bootstrap Node24.19.0/npm11.17.0. No dependency/schema/wire contract changes.

### Files Changed

16 declared-scope implementation files:

- `src/execution/policy/product-search-cursor.ts`, `shopify-core.ts`, `shopify-core-executor.ts`.
- `src/execution/discount-catalogue.ts`.
- `src/runtime/ports.ts`, `prisma.ts`, `service-ports.ts`.
- `README.md`, `.env.example`.
- Existing focused cursor/core/composition/discount/service-port unit tests; existing Prisma and product-discovery integration fixtures/expectations updated for removed options and current-policy cursor semantics.

### Work Completed / Pagination Inventory

| Owned operation | Current unsigned position | Preserved current-call authority / bounds |
| --- | --- | --- |
| Shopify product text/browse (`products.search`, legacy published `shopify.searchProducts`) | version3 `variants.after` | Fixed provider document/current filters; opaque provider token forwarded unchanged as variable; current authenticated connection and shop |
| Shopify taxonomy/category product search | version3 `category.productAfter`, `variantAfter` | Current taxonomy membership and category/publication checks; native product/variant provider edges |
| Woo product/category/variation search | version3 `woo.productPage`, `productIndex`, `variationPage`, `variationIndex` | Parent identity obtained from current connection's returned row; current category/publication/visibility/purchasability filters; no cursor-provided parent/host/tenant |
| Shopify/Woo discount catalogue options | version2 `afterId` | Current tenant, NONE/FIXED/AI policy and active override; parameterized tenant/afterId query and per-row ownership checks |

- Removed HMAC/AES cursor cryptography, secret configuration/DI, minimum-length advertisement/execution gates, expiry, query/shop/connection/mode/policy bindings, catalogue generation fingerprint checks and Woo page-content hashes. No alternate secret, cursor database, legacy verifier or generic crypto substitute.
- Envelopes contain only progress. Strict known-version/shape parsing, canonical base64url and valid UTF-8/JSON checks, Shared2048-character cursor bound,1024-character provider token and128-character discount ID bounds remain. Woo pages1–1000/indexes0–20 require finite safe integers. Provider call/page limits (Shopify3 pages, Woo12 calls and existing page cap), discount250-row batches/5000 scanned-row cap/50-result bound, output limits/deadlines/cancellation retained.
- Different search modes restart progress; changed filters/catalogue can skip or repeat positions instead of pretending to be a bound snapshot. Current query and policy apply to every returned row. Valid positions never bypass NONE, tenant, connection, release, grant, revocation or provider validation.
- Old Moda/Commerce signed tokens, old product envelopes and encrypted catalogue tokens return bounded INVALID_INPUT with `Invalid pagination cursor. Restart with cursor: null.` via the existing optional renderedText field. The published product executor preserves this instruction through rendering. No public tool name or Shared field/type change.
- README documents the confirmed coordinated breaking pre-production deployment, rollback restart, exact position ownership, parsing/bounds and removal of the cursor-secret requirement. Credential setup remains documented.

### Validation Results

All task-required checks passed:

1. Focused declared runner: `./node_modules/.bin/tsx --test tests/unit/execution/policy/product-search-cursor.test.ts tests/unit/execution/policy/shopify-core.test.ts tests/unit/execution/policy/product-search-composition.test.ts tests/unit/execution/discount-catalogue.test.ts tests/unit/runtime/service-ports.test.ts tests/unit/runtime/ports.test.ts tests/unit/runtime/prisma.test.ts` — **62 passed,0 failed/skipped** before the final added discount-secret variant case; all focused cases are also included in the final full run below.
2. `npm run test:unit` — **326 passed,0 failed,0 skipped** on final source/tests. Covers actual registry advertisement and callable search without secret; absent/short/former secret variants for search and discount pagination; static120-offer catalogue traversal;45-variant category and Woo traversal; changed filters/modes/pages; legacy/malformed/oversized/unsafe/non-UTF-8 progress and bounded restart instructions; unchanged native opaque edges; copied cursor through a different authenticated tenant/provider; policy NONE/FIXED and existing authorization/credential/lifecycle/provider regressions.
3. `npm run typecheck` — passed on final source/tests.
4. `npm run build` — passed, including pinned Prisma generation and production TypeScript compilation.
5. `npm run typecheck:integration` — passed; updated integration fixture configuration/expectations compile. Docker integration suites were **not run** and are not claimed as persistence or deployment proof; the task requires focused pagination/executor/advertisement tests, not a database rehearsal.
6. `npm run lint` — passed, zero warnings/errors. `git diff --check` — passed.
7. Final owned runtime/config/docs search across70 files: **zero matches** for `COMMERCE_CURSOR_SECRET`, `cursorSecret`, `createHmac`, `createCipheriv`, `createDecipheriv`, `timingSafeEqual`, old cursor TTL/binding/page-hash symbols. Test-only references remain solely to prove the old environment value is ignored. Non-cursor policy override expiry remains enforced.

Initial baseline:57/58 focused tests passed; one required the ignored pinned Shopify schema artifact. Provisioned it using the repository's documented `npm run schema:install:shopify -- /Users/kwadwoadomafriyie/project/moda-interact-workspace/moda-interact-commerce/lib/discovery/artifacts/admin-2026-07.json`. Installer verified exact SHA-256 `2b507dc1f74c6157e0eb98500db0f3c3e238d69eaf0d98fd7657ac7ed3f6900b`. No replacement schema was fetched/guessed and no Commerce file was edited. Final tests include the real pinned document validation. Installed artifact/build output remain Git-ignored local prerequisites.

Local logs: `/tmp/arch058-mcp004-{install,prisma,schema,baseline,focused,unit,typecheck,build,integration-types,lint}.log`. No new persisted fixture databases, Docker containers, live providers or deployment resources were created. Environment variants restore the prior value in finally; no cursor/credential/customer payload was added to operational logging.

### Deviations

None. Existing integration test seams were updated to remove retired DI and old binding expectations, without running expensive integration orchestration. Schema artifact provisioning followed the existing hash-checked local installer.

### Assumptions

Confirmed internal pre-production breaking deployment permits restarting pagination. Pagination positions are not authoritative snapshots: changes may skip/duplicate rows and upstream providers may reject an opaque token under a changed query. Such provider errors remain provider errors, not Moda signature/binding checks.

### Unresolved Issues

No task-owned implementation or required-validation blocker. Architect review pending. Commerce preview parity remains owned by ARCH-058-COMMERCE-002; no other repository is modified or follow-on task started.

### Architectural Concerns

Unrelated cryptography is retained: Shared credential decryption/AAD/keyring consumers for merchant knowledge/reference embeddings/Woo grants; existing basket fingerprints, manifest/reference-source hashes and occurrence UUIDs. Authentication, tenant isolation, release/grant authorization, approved provider connection resolution, parameterized database queries, budgets and transport controls are unchanged. No schema/Shared wire change, main merge, gitlink/index update or cutover. Architect Review below is unchanged.

## Architect Review

### Review Status
Pending

### Review Notes
Task definition only; no implementation claim or acceptance.

### Reviewed Files
None

### Validation Reviewed
None

### Architecture Conformance
Pending implementation.

### Follow-up
None
