---
id: ARCH-058-COMMERCE-002
architecture_id: ARCH-058
title: Remove cryptographic cursor validation from commerce pagination
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables: []
created: 2026-11-05
updated: 2026-11-05
---

# ARCH-058-COMMERCE-002: Remove cryptographic cursor validation

## Architecture

ARCH-058; docs/architecture/ARCH-058-commerce-agent-product-discovery.md. Coordinator: moda_architect. This explicitly overrides earlier signed-cursor requirements in ARCH-058-MCP-002 and historic product pagination definitions.

## Objective

Make Commerce preview adapters paginate without cryptographic cursor validation or a cursor secret.

## Context

Developer explicitly requested removal after absent COMMERCE_CURSOR_SECRET hid commerce_search_products. This is removal, not improved error handling. Existing tenant authorization remains the security boundary.

## Scope

Commerce local preview product pagination and adapter availability. Inspect src/commerce/products/index.ts and src/commerce/preview/local-policy-providers.ts plus owning tests/docs/environment examples. Remove the secret gate that currently returns only merchantKnowledge adapters. Cover every paginated local product adapter and any other Moda cursor crypto found in the repo. Preserve native discount-provider pagination and server-side policy authorization; do not reintroduce production execution into Studio or change standalone MCP client transport.

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

Keep published Shared tool input/output schemas, cursor null/string fields and maximum lengths unchanged. Upstream cursors stay provider-owned opaque data. No cross-service credential changes or new published contract required. MCP task ARCH-058-MCP-004 owns the production private runtime.

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

Architect-accepted and Complete — Attempt 1, 5 November 2026. Implementation committed and pushed as `bb56329b514302ec71189662b52dbe558b9530c3` on `task/ARCH-058-COMMERCE-002`. Architect acceptance is recorded below; no deployment or follow-on execution is asserted.

### Prepared Execution / Context

- Uses the same explicitly confirmed internal pre-production/restart context as the preceding MCP cursor work in this session: the developer confirmed “Yes—pre-production; restarts are fine.” This task removes the corresponding local Studio preview format, without a production compatibility bridge or deployment.
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-058-COMMERCE-002`; implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-058-COMMERCE-002`. Both branches `task/ARCH-058-COMMERCE-002`. Parent reused, implementation newly created by launcher; no shared/default checkout or another task worktree switched or edited.
- Launcher dependency gate passed (no explicit dependencies). Both remote task fast-forwards not needed; both origin/main integrations already current. Parent start `1c391146aa94e9254f64255b183f027d1036e8c2`; implementation start `32a02d874ac20275dc6f6f2b31e537ff9ae17316`.
- Durable claim `e00c0780553e0302ad11981d8d87110db800d221`, Attempt1, executor codex, `2026-11-05T14:48:57Z`. Implementation end `bb56329b514302ec71189662b52dbe558b9530c3`. Parent end is the publication commit containing this report, rather than an invented self-referential SHA.
- Launcher recursive submodule sync/update passed; nested Database recorded/working pin `bd2d09066a8eb178a56f48fbbf88df637c411059`, unchanged.
- `npm ci` passed from the lockfile; actual installed Shared5.0.0, Prisma client6.19.3, Next16.3.5, Vitest5.0.1, Zod4.6.5. Prescribed workspace bootstrap Node24.19.0/npm11.17.0. No dependency/schema changes.

### Files Changed

Six task-owned implementation files:

- `src/commerce/products/index.ts`: unsigned version3 position encoding/strict bounded parsing; removed HMAC, cursor expiry/bindings and secret DI.
- `src/commerce/preview/local-policy-providers.ts`: removed environment/length gate and secret plumbing; all existing local registrations available independently of a cursor secret.
- New `tests/product-pagination.test.ts` (108 lines); existing `tests/arch036-commerce-local-discounts.test.ts` no longer sets a retired prerequisite.
- `README.md`, `.env.example`: documented secret-free positions, current-call authority, breaking restart/rollback and preserved native protocols. The environment example did not previously contain a cursor-secret field; added a descriptive no-secret note.

### Work Completed / Owned Pagination Inventory

| Operation | Pagination handling | Preserved authority / limits |
| --- | --- | --- |
| Local `shopify.searchProducts` | Unsigned base64url UTF-8 JSON `{version:3,progress:{kind:'variants',after:<native edge>}}` | Authorize current active Shop ID/domain before every call; resolve current offline session/provider; apply current query/price/availability/currency/market filters |
| Local qualifying/similar recommendations | Reuse the same product search adapter and its positions | Existing discount evaluation, basket/product facts, provider budget and recommendation policy retained |
| Product-facts collection traversal | Native internal GraphQL `after` positions, unchanged | Fixed documents, authenticated context, request limit12, collection bound1000 and deadlines retained |
| Native Shopify discount traversal | Native provider opaque cursors, unchanged | Current tenant/session/scopes/NONE/FIXED/AI policy and native provider protocol retained |
| Native Woo discount traversal | Existing tenant-scoped Prisma composite cursor, unchanged | Current effective policy/override, catalogue eligibility, selected discounts and parameterized tenant predicates retained |

- Removed the only Moda-owned pagination cryptography found in Commerce: product HMAC signing/verification, TTL, shop/query/filter/currency/market comparisons and secret constructor input. No alternate key, store, verifier, hidden binding or compatibility path.
- Removed the early preview factory return that previously exposed only merchant knowledge without a sufficiently long secret. Basket, search, recommendations and discount registrations now remain available; execution still enforces their actual prerequisites.
- Positions contain no tenant, host, query, policy, credentials or customer data. Native edges pass unchanged as fixed GraphQL variables to the current provider. Strict version/shape, canonical base64url, UTF-8/JSON and nonblank1024-character native position parsing; Shared2048-character bound retained. Invalid/legacy tokens return INVALID_INPUT with bounded `Restart with cursor: null.` instruction; wire-oversized input retains the existing Shared INVALID_INPUT boundary. Oversized output continuation returns UNAVAILABLE instead of dropping progress.
- Current authorization runs before cursor parsing/provider IO. Copied positions use only the current tenant's provider/session and cannot override the current Shop/discount policy. Changing query/filter is no longer a cursor mismatch; rows still pass current filters. Positions are not snapshots and can skip/repeat after catalogue/filter changes.
- Kept query documents, public tool names/Shared schemas, native discount protocols, credential encryption, standalone MCP transport and production execution boundary unchanged. No deployment/cutover or other repository edits.

### Validation Results

All required local checks passed:

1. `npm test -- tests/product-pagination.test.ts tests/arch036-commerce-local-discounts.test.ts tests/arch036-commerce-discount-reader.test.ts tests/policy-operation-registry.test.ts tests/policy-operation-result-template.test.ts tests/preview-integration.test.ts tests/preview-service.test.ts tests/preview-routes.test.ts tests/arch038-preview-policy-service.test.ts tests/arch038-preview-policy-contracts.test.ts` — **90 tests passed in10 files**. Covers native multiple-page positions, position-only contents, query/filter changes and no expiry, two-tenant copied positions, current authorization denial, malformed/legacy/oversized/non-UTF-8 input, output-bound failure, provider cancellation/throttling, all seven local registrations/callability with absent/short/former secrets, NONE policy without provider IO and existing native Woo/Shopify discount/preview/registry regressions.
2. `npm run typecheck` — passed on final files. Generates the pinned Shopify schema and Next route types, then checks all included source/test TypeScript.
3. `npm run build` — passed through schema synchronization, manual packaging/smoke, code-runtime packaging/smoke, pinned Prisma generation and Next production build. Existing non-failing Nunjucks dynamic-loader warning remains; no generated output is committed.
4. `npm run lint` — exit0, zero errors and11 existing warnings outside changed files. Task-owned source/tests checked separately with `./node_modules/.bin/eslint src/commerce/products/index.ts src/commerce/preview/local-policy-providers.ts tests/product-pagination.test.ts tests/arch036-commerce-local-discounts.test.ts --max-warnings=0` — passed with zero warnings/errors.
5. `git diff --check` — passed.
6. Final runtime/config/docs scan for `COMMERCE_CURSOR_SECRET`, `cursorSecret`, `CURSOR_TTL_MS`: **zero matches**. Cursor crypto is absent from the product module; remaining source HMAC/encryption uses were inspected and classified below. The retired environment name remains only in new tests proving its value is ignored.

Schema synchronization uses installed `@shopify/dev-mcp@1.15.4`, Admin2026-07, SHA-256 `2b507dc1f74c6157e0eb98500db0f3c3e238d69eaf0d98fd7657ac7ed3f6900b`; no API operation or schema/version changed. Focused tests use synthetic provider/Prisma ports, restore environment/global state, and perform no live merchant/model/provider operation. No Docker/database/infrastructure or live validation was launched or claimed; no task-owned external resources require cleanup. No full repository test-suite result is claimed.

Logs: `/tmp/arch058-commerce002-{install,prisma,focused,typecheck,build,lint,focused-lint}.log`. Durable format/ownership/restart guidance is in README. No cursor/credential/customer payload logging was added.

### Deviations

None. Existing native discount-provider pagination is preserved as required; no unnecessary wrapper or migration was introduced. No new published Shared contract was needed.

### Assumptions

Confirmed pre-production pagination restarts are acceptable. Pagination positions supply progress only and are not a snapshot, tenant grant or correctness authority. Standard provider errors under a changed native position remain provider errors.

### Unresolved Issues

No task-owned implementation or required-validation blocker. Architect review accepted Attempt 1. The unrelated full-lint warnings do not occur in task-owned files; no unrelated cleanup was performed.

### Architectural Concerns

Unrelated security cryptography is retained: Woo OAuth authoring signatures (`woocommerce/authoring-transport.ts`), signed authoring-live-test proof/expiry (`woocommerce/authoring-live-test.ts`), connection command HMAC (`connections/command-kernel.ts`), model credential decryption (`integration/preview/openrouter-credential.ts`), embedding credential decryption and basket fingerprints. These are not pagination cursors. No authentication/credential/tenant control, main branch, gitlink/index, another task or another implementation repository was changed. Architect Review remains unchanged.

## Architect Review

### Review Status

Accepted on 2026-11-05. Attempt 1 Complete; executor/claimed_at cleared, attempt unchanged. No actionable findings.

### Review Notes

Reviewed implementation `bb56329b514302ec71189662b52dbe558b9530c3`, matching its pushed task branch. The scoped removal uses bounded unsigned versioned pagination positions, removes secret gating and cryptographic/query/tenant bindings, and preserves current-call authorization, provider/session resolution, fixed query variables, page/scan limits and cancellation. Invalid/legacy positions request restart; current tenant/policy remains authoritative. No credential encryption or authentication control was removed. The report records the explicitly confirmed pre-production restart boundary; this acceptance does not certify deployment or compatibility with old tokens.

### Reviewed Files

All six implementation files: product cursor encoding/parsing, local registration factory, focused pagination and discount tests, README and environment example. Also inspected the task requirements, source/provenance report and recorded validation evidence.

### Validation Reviewed

- Independently ran the exact ten-file focused pagination/executor/preview command listed in the Completion Report: **90 tests passed across 10 files**. Local evidence `/tmp/commerce002-review.log`.
- Independently checked the implementation correction whitespace and source/remote identity; `git diff --check` passed. Worktrees were clean before this documentation update.
- Independently scanned the owned runtime/config/docs for residual cursor-secret/TTL/crypto gates: no matches.
- Reviewed submitted typecheck/build and focused lint evidence, including completed Next build output; these checks were not independently rerun. No live provider, Docker, deployment or full-repository-suite validation is claimed.

### Architecture Conformance

Conforms to the explicitly authorized unsigned-cursor override. Public Shared cursor schemas and native provider protocols remain unchanged. No dependency/schema/gitlink change or compatibility bridge was introduced. Breaking pagination restart and rollback limits are documented.

### Follow-up

No explicit downstream dependencies or enabled tasks exist for this task; none are promoted. Existing terminal architecture validation and deployment gates remain separately owned. No implementation edit, main merge, package publication, deployment or follow-on execution is performed by this acceptance.
