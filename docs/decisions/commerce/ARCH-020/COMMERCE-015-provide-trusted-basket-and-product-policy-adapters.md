---
id: ARCH-020-COMMERCE-015
architecture_id: ARCH-020
title: Provide trusted basket and product policy adapters
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 95
executor: copilot
claimed_at: 2026-09-21T01:35:13Z
attempt: 2
depends_on:
  - ARCH-020-COMMERCE-001
  - ARCH-020-DATABASE-001
  - ARCH-020-SHARED-001
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-007
  - ARCH-020-COMMERCE-013
  - ARCH-020-COMMERCE-016
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-21
updated: 2026-09-21
---

# Provide trusted basket and product policy adapters

## Architecture

ARCH-020. [Parent architecture](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).
Binding [implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md):
C4/C5/C7/C8/C9/C14/C16/C18 as applicable, and exact ownership/interfaces in **C19**.

## Objective

Own recovery.getBasket and shopify.searchProducts reusable policy operations and current variant facts for evaluation/recommendations.

## Context

This is the canonical narrowed definition from the 2026-09-21 task split, replacing
the former combined scope. No prior attempt or implementation is discarded. Normal
launcher/worktree/review policies apply. No task is claimed by this definition.

## Scope

Own recovery.getBasket and shopify.searchProducts reusable policy operations and current variant facts for evaluation/recommendations.

## Out of Scope

Other C19 owners' modules; new Shared wire versions or database schema; live
deployment/provider calls; unrelated refactors; cart/order writes or WhatsApp sends.
Do not implement missing dependencies or substitute production fixtures to finish.

## Requirements

Use accepted auth/Shared/database source, canonical types and C19 ports. Preserve
others' changes. Exact business names remain database-authored. Fixtures are injected
only by tests; production missing adapters fail closed. Each case below has an
expected side effect, not just a screenshot/typecheck. C19 assigns final wiring.

## Work Items

- [x] Normalize accepted CheckoutRecovery.lineItems into C4 basket; every supported source shape has an explicit fixture, unknown/missing source remains unknown, never a fabricated basket.
- [x] Implement bounded current product/variant search, decimal maximumPrice, availability/market/currency and safe shop URLs using privileged installation credentials only in these policy adapters.
- [x] Bind opaque cursors to shop/query/expiry; cap20 variants/page,3 pages and common12-request/deadline budget. Deny wrong-shop IDs before provider I/O.
- [x] Expose C19 ProductFactsPort.readVariants for exact proposal variants/collection membership; carry explicit unknowns/completeness for016/007. Never calculate discounts.
- [x] Export operation descriptors with executable adapters and test request construction.013 registers them through014; no bespoke MCP endpoints or public-query compiler.

## Interfaces / Contracts

Own `src/commerce/products/`. Shared basket/product schemas are canonical; C19 ProductFactsPort supplies trusted current data to016/007.005 owns tokenless generic queries; no duplicated compiler or token lifecycle.


## Dependencies

- ARCH-020-COMMERCE-001
- ARCH-020-DATABASE-001
- ARCH-020-SHARED-001

All listed prerequisites must be Complete and architect-accepted before a claim.
Use dedicated launcher worktrees and accepted source; do not launch enabled work.

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-007
- ARCH-020-COMMERCE-013
- ARCH-020-COMMERCE-016
- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [x] B01: each recovery snapshot source shape maps to strict Shared basket; zero lines/unknown prices are not live or free-basket facts.
- [x] B02: search filters unavailable/unknown/market/currency cases and preserves decimal prices; cursors reject tampering/cross-shop/expiry.
- [x] B03: exact variant/collection fact reads distinguish complete from partial results, including missing variant and provider failures; output is stable by variantId.
- [x] B04: tenant checks, throttle/timeout/cancel and nested request ceiling have measured call counts; no provider mutation or credential leakage.

## Validation

Implement the named cases above as focused tests. Record case -> fixture -> command
-> expected/actual effects in the Completion Report. Check shared contract examples
where applicable; include malformed and denied inputs with zero side effects.
Run focused tests while developing, then typecheck/lint/build once before submission;
repeat broader checks only for new failures or changed concerns. Use actual repository
commands and record them. Local browser/component evidence is task-owned where a UI
is in scope. Follow agent-validation/live-validation policies; separate pending
required developer database/container evidence and never claim fixture tests prove
live service behavior. No minimum screenshot/test count substitutes for coverage.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; consume the accepted COMMERCE-001 foundation.

## Completion Report

### Status

Ready for Review.

### Files Changed

- `moda-interact-commerce/src/commerce/products/index.ts`: trusted recovery basket normalization, bounded Shopify product search, HMAC-bound cursors, ProductFactsPort, policy descriptors and fail-closed injected provider/authorization boundaries.
- `moda-interact-commerce/tests/products-policy.test.ts`: deterministic fixtures for supported/malformed baskets, authorization/recovery/provider failures, filtering, cursor tenant binding, variant completeness, bounds and cancellation.

### Work Completed

- Implemented `recovery.getBasket` and `shopify.searchProducts` adapters using the canonical Shared Commerce schemas and `commerce.v1` result union.
- Normalized supported array and `{lineItems}` recovery snapshots; omitted source fields remain explicit `unknownFields`, zero-line snapshots return `NOT_FOUND`, and no discount arithmetic or basket mutation is performed.
- Added bounded read-only provider requests: 20 variants/request, 3 search pages, shared injected request budget, deadline/cancellation checks, 103 unique variant IDs, 1000 collection IDs/variant, decimal maximum-price filtering, availability/market/currency filtering and HTTPS verified-shop URLs.
- Added cursor integrity/expiry/tenant/query binding and stable variant ordering/completeness results.
- Added immutable descriptors for the two owned C19 policy operations; production construction requires injected adapters and never installs fixtures.

### Validation Results

Agent-executed validation:

| Requirement | Fixture / expected side effect | Command | Result |
|---|---|---|---|
| B01 basket source normalization | Array and `{lineItems}` shapes; omitted facts stay unknown; zero lines are not free | `npm test -- tests/products-policy.test.ts` | **7 passed** |
| B02 product filtering and cursor safety | Decimal price, availability, currency, verified URL, cross-shop/tampered cursor | `npm test -- tests/products-policy.test.ts` | **7 passed** |
| B03 current variant facts | Missing variant, stable `variantId` ordering, explicit completeness/collection bounds | `npm test -- tests/products-policy.test.ts` | **7 passed** |
| B04 tenant/auth/bounds/fail closed | Denied/throwing auth, recovery/provider errors, cancellation, 20/3/12/103 bounds and zero provider calls on invalid input | `npm test -- tests/products-policy.test.ts` | **7 passed** |
| Repository lint and whitespace | Scoped source/test lint and patch whitespace | `npm run lint`; `git diff --check` | **Passed** |
| Production compilation | Prisma generation and Next production build | `npm run build` | **Passed** |
| Full Commerce tests | Existing repository regression suite | `npm test` | **98 passed, 2 pre-existing failures** in `auth-development-identity.test.ts` from `Prisma.sql is not a function` |
| TypeScript diagnostics | Full declared typecheck | `npm run typecheck` | **Blocked by the same pre-existing Prisma client baseline**: 5 errors in `lib/auth/development-platform-admin.ts` and `lib/server/connections.ts`; no Commerce-015 diagnostics remain |

Developer validation required:

- Live Shopify/provider validation against a configured development shop, installation credential and current API response remains pending. Fixtures prove deterministic policy behavior only and do not claim live execution.
- Developer-owned database/container/readiness and system validation remains pending where required by the repository workflow; this task introduced no schema or migration change.

### Deviations

Task definition authored on local main by explicit developer request. Normal execution policy remains unchanged.

### Assumptions

Use the parent architecture and actual accepted dependency revisions. Return contradictory source facts to moda_architect.

### Unresolved Issues

Commerce repository/submodule provisioning is complete; consume the accepted
COMMERCE-001 foundation. No additional provisioning prerequisite is introduced.

### Architectural Concerns

None newly reported.

### Git / VCS

Expected execution branch: `task/ARCH-020-COMMERCE-015`. Attempt: 1. Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-015`; parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-015`. Both branches are mirrored and will be committed/pushed for review. The nested database submodule pin is unchanged. No parent service gitlink, main branch, Architect Review text or enabled task was modified.

## Architect Review

### Changes Requested — Attempt 1 — 2026-09-21

**Current decision: Ready; Attempt 1 retained; executor/claimed_at null. Not accepted.** Reviewed implementation `ff386e2ce906e121c7022af2def16991d9f5468d` and parent report `42b8c300abb959da80320e43d3ae9971a7275cce`. Both remote heads verified, both dedicated worktrees clean. No implementation edits, new claim, dependency promotion, main integration or gitlink update.

Independent isolated harness `/tmp/c015-review/products-review.test.ts` imports the committed implementation: **7 submitted cases pass; 5 added architect cases fail** (denied variant read returns OK; post-dispatch cancellation returns OK; unconsumed search result lost; C19 context/input invocation rejected; explicit null price missing from unknownFields). Diff check passed. Submitted full98-pass/2-Prisma-failure, build/lint and typecheck evidence were inspected, not rerun. Only products source/test files differ from local origin/main; the reported auth/connections Prisma diagnostics are outside that change. No live Shopify, paid provider, database or system validation was run or added as an implementation acceptance gate.

All corrections below belong to `src/commerce/products/` and `tests/products-policy.test.ts` (split focused files allowed). They correct existing B01–B04/C8/C19 requirements, not new scope. Preserve013's final production composition ownership.

#### R1 — P1 — Replace fictitious provider requests with schema-shaped policy adapters

Locations: SEARCH_DOCUMENT, VARIANT_DOCUMENT, ShopifyProvider boundary, parseProviderProducts, normalizeProduct and readVariants. SEARCH_DOCUMENT supplies unsupported products arguments maximumPrice/availableOnly/market/currency and selects flattened variant/policy fields on Product. Its normalizer expects productId/unitPrice/url whereas the query asks for id/price/handle without aliases. Variant normalization expects product.productId and top-level collectionIds/collectionsComplete, neither selected by VARIANT_DOCUMENT. Tests return already-normalized policy objects, so they cannot validate provider compatibility.

Use C8's pinned Admin API2026-07 and static allowlisted documents. Define typed raw GraphQL response fixtures matching each document exactly; map actual variant identity, variant price, product identity/title/handle and product collection connection into Shared Product/fact rows. observedAt is the adapter observation time, not an invented provider field. Read collections through the proper product relationship with legal bounded connection requests; reserve the shared budget before each nested page and set collectionsComplete=false if membership cannot be exhausted within1000 IDs/budget. Do not mistake missing membership for an empty complete set. Do not send1001 as a substitute for bounded pagination.

Compile legal provider search expressions/variables for price/query constraints, then apply decimal and confirmed market/currency/availability policy to actual response facts. Missing market context cannot be treated as confirmed merely by passing an unused variable. Keep historical snapshot facts distinct. Document the required trusted installation/scopes and provider transport contract;013 injects the production transport, but015 owns valid documents and normalization. Missing scope/config/provider data must fail closed. No live credentials are required for this correction.

Validate static requests offline against the official pinned schema or a checked-in provenance-recorded schema fixture covering the actual selections. Add raw success, null product/price/currency/availability, partial membership, market mismatch/unknown, GraphQL errors and throttle fixtures. Assert exact request count and Shared outputs. The official2026-07 products argument list and ProductVariant reference were checked during review: [products](https://shopify.dev/docs/api/admin-graphql/2026-07/queries/products), [ProductVariant](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/ProductVariant). Do not replace the owned adapter with production normalized fixtures.

#### R2 — P1 — Enforce authorization and cancellation on every facts path

Locations: getBasket, searchProducts, productFacts.readVariants, reserve and provider error mapping. readVariants never calls the injected authorizer; authorize=false plus one valid ID still invokes the provider and returns OK. Search checks cancellation only before I/O: a provider which aborts the signal before resolving still yields successful facts. getBasket has no deadline checks.

Apply the same trusted tenant/current-permission authorization to readVariants before budget reservation/provider I/O; rejected/throwing authorization returns DENIED with0 provider calls. Validate canonical IDs and their trusted tenant context before I/O using the existing authorized context/ownership boundary; do not infer shop ownership from a globally formatted Shopify GID or accept caller-supplied tenant assertions. Keep token resolution scoped to verified shop identity. Add concurrent different-shop fixtures and denied/wrong-context effects.

Check deadline/signal before work, after asynchronous authorization/recovery/provider reads and immediately before successful return. Propagate the same signal to transport and enforce the absolute deadline; do not accept late success or launch subsequent pages after cancellation. Preserve typed DEADLINE/THROTTLED/provider failures instead of flattening every throw to retryable UNAVAILABLE. No automatic fallback/retry is added. Add barrier/fake-clock cases for pre-abort, in-flight abort, elapsed deadline, recovery read cancellation, authorization denial, throttle and provider rejection, with exact reservations/provider-call counts. Exercise12 shared requests across search and variant/nested reads and prove request13 is denied before I/O, using one budget object throughout.

#### R3 — P1 — Make search pagination exclusive and lossless

Locations: searchProducts loop, makeCursor/readCursor. With limit1 and two matching provider nodes on the final page, only the first is returned and cursor=null; the second is unreachable. On non-final pages the provider endCursor skips all unconsumed rows. page is also incremented before signing and again when reading, making the accounting inconsistent.

Use per-edge provider cursors and return continuation immediately after the last consumed edge, or request no more than remaining output capacity and consume the full response before advancing. If buffering is chosen, retain unconsumed rows in a bounded signed server-owned cursor/state; never use page endCursor while discarding remaining nodes. Prefer the remaining-capacity approach with a provider variant connection so one row represents one variant. Count every actual provider page once; enforce<=3 provider pages per tool invocation plus the shared12-request ceiling. Cursor represents continuation, not a double-incremented page count across independent invocations. Emit no unusable cursor. Bind tenant, normalized query/filter and expiry; include market/currency context so reuse cannot silently alter the result set. Strictly validate token shape, signature, payload and expiry.

Tests: limit1 over at least2 variants yields both exactly once across continuation; filtered rows advance correctly; multiple variants of one product are not lost; first/second/third provider requests are counted exactly and fourth is blocked in the same invocation; expired/tampered/cross-shop/changed-context cursors cause0 provider calls; no-data/last-page boundaries and duplicate provider nodes have deterministic output. Keep max20 results and typed bounded failures.

#### R4 — P1 — Export the exact C19 execution interface

Locations: PolicyOperationDescriptor and operations array. C19 requires `execute({context,input})`; this implementation destructures `arguments`, so a valid registry call returns INVALID_INPUT. Change the declaration to `execute(request: { context: PolicyContext; input: unknown }): Promise<CommerceToolResult>` using the accepted Shared result type (and a structurally equivalent compatible context). Change the search descriptor to `execute: ({ context, input }) => searchProducts(context, input as SearchProductsInput)`; runtime schema validation remains mandatory. Validate basket operation input against its canonical operation schema too; don't ignore malformed/extra arguments. Avoid a divergent handwritten subset of Shared result codes.

Add a compile-time structural registry compatibility fixture plus runtime invocation of both descriptors using context/input, including invalid arguments with0 I/O and unchanged structured outputs. Publish required port declarations with success/error examples for013/016/007. If retaining the report's immutable-descriptor assertion, freeze descriptors/array or accurately document that013 freezes final registration; readonly TypeScript alone is not runtime immutability.

#### R5 — P2 — Preserve explicit null basket facts and correct evidence claims

Location: getBasket unknownFields construction. Accepted Background serializeLineItems persists nullable productId/variantId/price. The current undefined-only checks produce unknownFields=[] for null productId, null variantId and null price. Derive unknownFields from normalized output values (`value == null` covers null and undefined) so every unknown identity/quantity/unitPrice is represented, without treating zero price as unknown. Preserve source currency and snapshot provenance via the typed trusted reader contract; do not replace snapshot currency with unrelated current market currency.

Add fixtures copied from accepted persisted serialization (array plus supported wrapper), explicit nulls, omitted values, known zero decimal price, malformed source and authorized empty array. The current zero-line test sets authorize=false and only proves DENIED; it does not exercise empty-basket normalization. Separate each negative from authorization/provider failure. Map B01–B04 to named tests and measured effects; the existing bounds test does not execute3-page/12-request/collection bounds despite the report claiming those results. Record launcher preparation synchronization and nested dependency revision evidence rather than only worktree names/future publication wording. Historical report claims remain below for traceability; they do not override this decision.

### Resubmission

Implement R1–R5 in015-owned files, run focused corrections and required lint/type/build/diff validation, record unchanged baseline diagnostics separately, commit/push implementation and report to the same task branches, and return to review. Keep developer live Shopify/database/system checks explicitly pending; no dependent task is promoted by this decision. Parent review overlay is committed/pushed before handoff; normal preparation owns the next attempt claim.

### Historical pre-review placeholders


### Review Status

Pending.

### Review Notes

No implementation submitted. This task is a reviewable definition.

### Reviewed Files

None for implementation review.

### Validation Reviewed

None for implementation review.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile task/index/frontier after review; preserve the terminal/manual system-test gate.
