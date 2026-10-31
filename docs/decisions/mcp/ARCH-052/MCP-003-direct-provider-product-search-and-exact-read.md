---
id: ARCH-052-MCP-003
architecture_id: ARCH-052
title: Execute Shopify and WooCommerce product search directly inside MCP
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 40
executor: null
claimed_at: null
attempt: 3
depends_on:
- ARCH-052-SHARED-010
- ARCH-052-COMMERCE-006
- ARCH-052-MCP-005
enables:
- ARCH-052-BACKGROUND-007
- ARCH-052-COMMERCE-007
- ARCH-052-GATEWAY-001
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: 2026-10-31
---

# ARCH-052-MCP-003: Execute Shopify and WooCommerce product search directly inside MCP

## Architecture

Architecture ID: `ARCH-052`. Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. Coordinator: `moda_architect`. Materialised and prepared on the canonical task branches for Attempt 1.

## Objective

Integrate **generic published** `commerce_search_products` and `commerce_get_product` execution into MCP across Shopify and WooCommerce. Consume the accepted direct Woo reader from **MCP-005**, with the bounded product-field, variation-read and permalink-validation extensions defined below; do not implement a duplicate transport or call the hosted API.

## Context

`src/connections/ports.ts` already declares `products.list`/`products.retrieve`; `runtime/ports.ts` only registers Woo when an injected `ApprovedWooProductReader` exists. `WooProductReadService` in the hosted API is the security/behaviour reference, NOT a service proxy. Shopify MCP already executes bounded GraphQL product search and has an offline session reader.

## Scope

- Implement the published policy-operation dispatcher for `products.search` and `products.get` as defined by COMMERCE-006; use the published SHARED-010 product input/output schemas and the existing generic MCP response wrapper.
- Shopify: reuse existing `src/execution/policy/shopify-core.ts` GraphQL product search and exact product lookup, extending projection to include genuine `categoryIds`/`collectionIds` if provider-returned and `variantId` from the actual variant; do not substitute product type/name for an ID.
- WooCommerce: consume the accepted MCP-005 `ApprovedWooProductReader` and existing connection/provider path. This task may extend that path only with the bounded read fields, variation operation and safe permalink projection in the Architect Scope Amendment below. Map provider IDs to strings, simple products to `variantId:null`, and variation products to source variation IDs; never infer identity or fields. No API proxy or new credential/keyring implementation.
- Preserve existing page cursors, request budgets, shop/feature permissions, bounded results, and shared logger. A missing provider category/collection ID remains absent; a simple Woo product is valid with `variantId:null`. Validate Woo permalinks inside the direct adapter against the independently authenticated installation origin; use `url:null` when host ownership cannot be proved.
- Keep result metadata compatible with product-search drafts published by COMMERCE-007; tool registration and publication are distinct tasks.
- For the returned `CommerceProduct.url`, use only the direct authenticated provider response for the **same current shop**. Validate canonical storefront-host ownership at the provider adapter/projection boundary against an independently authenticated shop origin: WooCommerce's verified installation site origin or Shopify's authenticated storefront/primary-domain metadata (including legitimate custom storefront domains). Do **not** derive an allowed-host list from the candidate URL, discount description, AI output or untrusted query. If host ownership cannot be established, return `url:null` as permitted by the existing product schema; do not provide a customer-facing URL to BACKGROUND-010. No new Shared schema or hosted API route is required for this internal validation.

## Out of Scope

No additional database table/column/migration, migration backfill, alternate provider proxy, customer-facing product database/cache, secret-bearing logs, unrelated architecture or other repository implementation.

## Requirements

- The MCP host uses published Shared-010 package schemas; `CommerceProductSchema.variantId` is nullable and `categoryIds`/`collectionIds` contain only provider IDs, not inferred labels.
- Shop identity, connection grant and `product_search` feature permission are mandatory. No MCP-to-API product requests or new product database.
- Secure direct Woo credential/transport and grant enforcement remain owned by the accepted MCP-005 adapter. MCP-003 may make the bounded response/variation extensions specified by the Architect Scope Amendment, but must preserve and regression-test MCP-005 encryption, origin, DNS, TLS, redirect, response-bound and grant-recheck protections; it must not reproduce those protections in a second transport.
- Preserve source product identity and missing fields; no fabricated prices, sale evidence, variant IDs, categories, or links.

### Provider-origin read diagnostics (31 October 2026)

For the Shopify GraphQL search/exact-product operations owned here
(`src/execution/policy/shopify-core.ts` and existing Shopify connection
port), preserve the actual returned Shopify `errors[].message` and
`extensions.code`, HTTP status/request ID and any safely bounded error
details. Handle GraphQL 200 plus `errors` as a real source failure, not
an empty result. If no provider response exists, record the original SDK/
transport `Error.name`, `Error.message` and cause without inventing a
provider error. Record Moda reason/status separately. Use the Shared logger,
with explicit sensitive-span redaction and bounds, and do not expose real
provider error payloads in `commerce_get_product`/`commerce_search_products`
results or the LLM's MCP projection. Maintain tenant and URL-origin checks.

The already accepted Woo REST reader (`src/connections/woocommerce/
direct-product-reader.ts`) is **not** modified under MCP-003: the dedicated
`ARCH-052-MCP-006` task owns the diagnostic-only correction to that accepted
reader. MCP-003 may proceed independently; integrated Woo system validation
waits for MCP-006. No new shared logging utility, transport proxy, HTTP
request or application-owned model contract is required.

## Work Items

- [ ] Wire published `commerce_search_products` and `commerce_get_product` handlers to existing shop connections and the MCP-005 Woo reader, including only the response/variation extensions authorized below.
- [ ] Extend Shopify and Woo product output mapping for `variantId:null`, provider category/collection IDs, optional image and sale evidence using the exact Shared contract. Extend the existing Woo reader request/response path to retrieve bounded variation records with real IDs and the required product fields.
- [ ] Test entitlement, shop scope, partial/missing product fields, Woo simple/variation products, Shopify variant collections and direct provider access.
- [ ] Test that product URLs are direct current-shop provider results with independently authenticated storefront-host ownership; valid Shopify custom domains and verified Woo origins remain usable, while spoofed/external hosts, cross-shop records and unknown-origin URLs return `url:null` without granting an arbitrary host. Woo permalink filtering must use the origin already authenticated inside the direct adapter and must not expose it to callers.
- [ ] Validate generic result schema, tool descriptor names, cancellation, structured errors and declared MCP scripts.
- [ ] Preserve and log original Shopify GraphQL/HTTP/SDK error strings and extension codes at the direct provider boundary; test 200+GraphQL `errors` and safe redaction without modifying the accepted Woo reader.

## Interfaces / Contracts

Consumer of `@modainteract/moda-interact-shared/commerce` published by SHARED-010: `CommerceToolInputs.commerce_search_products`, `.commerce_get_product`, their `CommerceToolOutputs` and `CommerceProductSchema` with nullable `variantId`, optional `categoryIds`/`collectionIds`. Internal Woo port: retain `ApprovedWooProductReader.read` and extend the existing `WooCommerceProductReadRequest` union only for bounded variation reads. MCP-005 provides the accepted secure transport/grant baseline; MCP-003 owns the narrowly scoped product-field, variation and permalink extensions required by the projection. COMMERCE-006 owns code-defined `products.search`/`products.get` draft registrations; COMMERCE-007 publishes after MCP-003 is accepted.

## Dependencies

- `ARCH-052-SHARED-010` — published full product identity contract.
- `ARCH-052-COMMERCE-006` — canonical product-tool descriptors/operation registry.
- `ARCH-052-MCP-005` — secure direct Woo read adapter accepted in MCP.

## Enables

- ARCH-052-BACKGROUND-007
- ARCH-052-COMMERCE-007
- ARCH-052-GATEWAY-001
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] Search and exact-product tools work for both store types with published result schemas and no internal API proxy.
- [ ] Woo simple products return `variantId:null`; genuine variants retain their source variation ID and are obtained through bounded provider reads.
- [ ] Provider categories/collections are source IDs, not inferred category-label aliases; missing fields remain unknown/absent.
- [ ] Shop/entitlement/credential access remains enforced and errors logged safely.
- [ ] The tool never yields a customer-facing product URL whose storefront-host ownership cannot be established for its authenticated shop; absence is represented as `url:null` under the existing contract, not a fabricated product or a permissive new host allowlist.

- [ ] Shopify GraphQL error-response and transport-exception tests assert original error message/extension code, correct provenance and request ID; no raw API payload leaks and no misleading empty success.

## Validation

- [ ] MCP published-tool invocation tests, direct Shopify GraphQL and mocked Woo reader integration; tenant isolation, revoked tool/grant, schema validation, cursor behaviour, variation pagination/bounds and URL origin filtering.
- [ ] Rerun the focused MCP-005 direct-reader security regression tests affected by the reader/port extension; verify grant, credential, origin, DNS, TLS, redirect, deadline and response-size behavior remains unchanged.
- [ ] Declared MCP typecheck/build and `git diff --check`.

## Stop Condition

Once Work Items, acceptance criteria and validation are met, set task status to `review`, complete its report, return to `moda_architect` and **STOP**. Do not mark it Complete, publish another task, merge branches or push `main`.

## Implementation Notes

Expected MCP owning code: `src/execution/policy/`, `src/connections/resolver.ts`, `src/runtime/ports.ts` composition, the existing Woo request/reader path for the exact bounded extension authorized above, and tests. Do not change credential decryption, grant resolution, authenticated origin resolution, pinned network transport or other MCP-005 security behavior. No hosted API product route, no extra Prisma tables, no Shared edits. Publisher runs only in COMMERCE-007.

## Completion Report

### Status

Attempt 3 implementation complete; submitted for Architect Review. The prior Attempt 2 review corrections are addressed, and no acceptance decision has been made by this agent.

### Files Changed

- `moda-interact-mcp/src/connections/shopify/provider.ts` — preserve bounded, redacted Shopify provider diagnostics at the source boundary, with an injectable Shared logger for semantic tests.
- `moda-interact-mcp/tests/unit/connections/shopify/provider.test.ts` — cover GraphQL and HTTP source messages, codes, status/request-ID provenance, transport errors and causes, explicit redaction, and bounds.
- `moda-interact-mcp/tests/unit/execution/policy/shopify-core.test.ts` — prove provider messages and payloads do not reach the published tool result.
- `moda-interact-mcp/src/connections/woocommerce/direct-product-reader.ts` — remove the diagnostic-only MCP-003 change; retain the authorized product, variation, and permalink implementation from the earlier task commit. Woo diagnostics remain MCP-006-owned.

### Work Completed

- Shopify GraphQL HTTP 200 `errors[]` failures now log the source `message`, `extensions.code`, safe path/location/extension details, HTTP status and provider request ID. Errors remain failures; they are not converted into empty successes.
- Shopify HTTP errors log their source error message/code/details when structured. Non-JSON bodies are read with a 4 KiB cap and redacted before logging.
- Shopify fetch/SDK failures with no provider response log the original exception name, message and up to two causes. The internal `McpRequestError` retains the original exception as its cause; no provider error object is invented when no provider response exists.
- Each event identifies `origin` (`provider_response`, `sdk_exception`, or `internal`) and records the Moda `reasonCode` separately. Provider message text is capped at 768 characters; provider details at 1 KiB. Redaction and truncation are flagged.
- Explicit source-text and structured-detail redaction covers credentials/tokens, email, phone, addresses, payment-card-like numbers, and sensitive detail keys. Provider responses, request arguments, and credentials are not returned in published tool results.
- Removed Attempt 2’s Woo diagnostic event and field collection. The approved Woo product field, bounded variation-read, and permalink checks remain, and the existing MCP-005 security paths are unchanged.

### Validation Results

- Focused command: `/Users/kwadwoadomafriyie/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node --import tsx --test tests/unit/connections/shopify/provider.test.ts tests/unit/execution/policy/shopify-core.test.ts tests/unit/connections/woocommerce/direct-product-reader.test.ts tests/unit/connections/woocommerce/provider.test.ts tests/unit/connections/resolver.test.ts tests/unit/runtime/service-ports.test.ts` — **51 passed, 0 failed**.
- Typecheck: `/Users/kwadwoadomafriyie/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node node_modules/typescript/bin/tsc --noEmit -p tsconfig.json` — passed.
- Production TypeScript compile: `/Users/kwadwoadomafriyie/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node node_modules/typescript/bin/tsc -p tsconfig.build.json` — passed.
- `git diff --check` — passed.

### Deviations

None. Attempt 3 implemented the Architect’s required Shopify diagnostics/tests and removed MCP-003-owned Woo diagnostic changes without editing MCP-006 or MCP-005 task records.

### Unresolved Issues

None known. Architect review remains pending.

### Git / VCS

- Task branch: `task/ARCH-052-MCP-003` in both repositories.
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-MCP-003`; implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-MCP-003`.
- Launcher preparation: parent started at architect review commit `8e51cc5818103e43c196c148dd593533ce8e4494`; implementation started at `04530c8233db9e4dc42a1c82959597152f09f047`. Parent and implementation `origin/main` were already incorporated; neither task branch needed a remote task fast-forward. Recursive submodule synchronization and initialization passed; database submodule was `139765042baad3901682cfe9c54a3d6bba73e75c`.
- Launcher claim commit: `26eb7bd001946077cdbb7446b2c93b5e09a5b867`, pushed to the parent task branch.
- Implementation commit `d3805c2` is pushed to `origin/task/ARCH-052-MCP-003`; no main branch was merged or modified.
- Parent submodule gitlink staged: no. Shared/default checkout switched or used for implementation: no. Another task worktree reused: no.

## Attempt 2 Completion Report (Historical)

### Status

Attempt 2 was returned for architect changes on 2026-10-31. Core product execution is implemented and pushed, but provider-origin diagnostics do not yet meet the task contract. Attempt 1 remains historical; this reviewed Attempt 2 remains unchanged and the next launcher claim creates Attempt 3.

### Files Changed

- `moda-interact-mcp/package.json`, `package-lock.json` — pin published Shared 2.8.1 product contracts.
- `moda-interact-mcp/src/connections/ports.ts`, `resolver.ts`, and `woocommerce/provider.ts` — admit only bounded product variation list/retrieve reads.
- `moda-interact-mcp/src/connections/woocommerce/direct-product-reader.ts` — request the approved product and variation fields, return bounded variation pages, null unsafe permalinks against the authenticated installation origin, and log safe structured failure diagnostics.
- `moda-interact-mcp/src/connections/shopify/provider.ts` — log safe structured provider failure diagnostics for Shopify product reads.
- `moda-interact-mcp/src/execution/policy/shopify-core.ts`, `shopify-core-executor.ts`, `moda-interact-mcp/src/runtime/service-ports.ts` — implement published `products.search`/`products.get` execution for both store platforms, Shopify exact reads and custom storefront validation, Woo projection/pagination, and safe structured failure logging.
- Focused tests for the direct Woo reader, provider allowlist, product adapters, and published executor.

### Work Completed

- Wired published product search and exact lookup through the existing tenant-scoped store resolver; no hosted API proxy or new transport was added.
- Implemented Shopify exact product/variant reads and mapped only provider-returned category and collection IDs. A verified GraphQL primary domain is accepted for storefront permalinks; unverified URLs remain `null` without dropping the product.
- Added Woo product fields and actual variation reads to the existing MCP-005 path. Pagination is bounded by three product pages and twelve provider reads per invocation, the shared result limit and deadline; signed cursors retain continuation state.
- Exact Woo variation reads verify both requested variation ID and parent ID. Simple products retain `variantId: null`; no identity, price or category IDs are inferred.
- Preserved MCP-005 credential, grant, DNS, TLS, redirect, response-size, timeout and post-read grant checks. The adapter validates Woo permalinks against its already verified installation origin without exposing that origin.
- Provider failures returned as policy errors are logged through the shared logger with an occurrence ID, operation, platform, shop ID, error code and retryability. Provider payloads, arguments and credentials are excluded. Thrown failures continue through the existing MCP error logger.
- Follow-up diagnostic refinement logs the internal reason code, failure stage, duration, and available upstream status and provider request ID at both adapter boundaries; Woo also records response media type, size, and a validated provider error code, while Shopify records bounded GraphQL error codes, paths, and locations. These diagnostics are recorded before public error-code mapping loses detail. Raw response bodies, URLs, arguments, credentials and arbitrary exception messages remain excluded.

### Validation Results

- Focused reader, provider, resolver, published executor and service-port checks: **41 passed, 0 failed** before the final diagnostic refinement. This includes the MCP-005 grant/credential/DNS/redirect/deadline/response regressions, unsafe Woo and Shopify URL handling, Shopify custom domains, Woo variation pagination, exact parent identity and safe failure logging.
- `npm run build`: passed.
- `tsc --noEmit -p tsconfig.json`: passed after the diagnostic refinement.
- No tests were run after the diagnostic refinement.
- `git diff --check`: passed.

### Deviations

None. Implementation stayed within the Attempt 2 scope amendment; MCP-005’s task record and completion report were not changed.

### Assumptions

- WooCommerce does not provide standard product currency/vendor fields through the approved REST projection; these remain unknown where no trusted source value exists.
- Product-search cursors remain tenant/query/filters bound and use the existing HMAC cursor secret configuration.

### Unresolved Issues

None known. Architect review remains pending; no acceptance decision has been made by this agent.

### Architectural Concerns

No new architecture concern identified. MCP-005 security codepaths are preserved and covered by focused regression tests.

### Git / VCS

- Task branch: `task/ARCH-052-MCP-003` in both repositories.
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-MCP-003`; implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-MCP-003`.
- Dedicated worktrees were used; shared workspace/default implementation checkouts were not switched or edited for task implementation. No other task worktree was reused.
- Start synchronization: parent `origin/main` was already current and the existing task branch was synchronized; implementation `origin/main` was already current and no remote implementation task branch existed at preparation. Recursive submodule initialization passed; database submodule was `139765042baad3901682cfe9c54a3d6bba73e75c`.
- Implementation repository commits: `150beadc7506cbf4155857cb1109855516db8ea8` (product reads) and `04530c8` (safe provider diagnostics); both pushed to `origin/task/ARCH-052-MCP-003`.
- Parent task-file claim commit: `ab54c2b8a63e98a3f05cbb19fc7b44246fac8fa3`; the completion report is included in the current parent task branch update.
- Parent submodule gitlink staged: no. Implementation `main` merged: no. Workspace `main` merged: no.

## Attempt 1 Completion Report (Historical)

### Status

Returned for Architect direction. Attempt 1 was claimed, but implementation is blocked by a contract gap in the accepted Woo reader. No source changes were made; the task is in `review` with executor and claim cleared.

### Files Changed

No implementation files changed. The prepared implementation worktree remains clean at its starting commit.

### Work Completed

Prepared Attempt 1 through the canonical launcher. The dependency gate passed for ARCH-052-SHARED-010, ARCH-052-COMMERCE-006 and ARCH-052-MCP-005. Inspected the MCP-005 read port, direct Woo REST reader and connection resolver against this task's required product projection.

### Validation Results

Implementation validation was not run because the current approved Woo contract cannot provide required product/variation evidence, and this task explicitly forbids implementing the MCP-005-owned direct reader. This is a contract audit, not a passing implementation validation.

### Deviations

No implementation deviation. Returned the task before source changes rather than expanding the MCP-005-owned reader or fabricating product identity/fields.

### Assumptions

The released Shared contract required by this task is available as `@modainteract/moda-interact-shared@2.8.1`; the MCP manifest is currently pinned to `2.7.1` and must be updated when implementation resumes.

### Unresolved Issues

The accepted MCP-005 port cannot support the WooCommerce acceptance criteria:

- `WooCommerceProductReadRequest` only supports list/search and product retrieve by product ID; there is no variation read operation or variant identifier in the request.
- The MCP-005 direct REST reader explicitly requests `_fields=id,name,sku,price,stock_status,stock_quantity,categories` for both operations. It therefore cannot return product type/variation IDs, permalink, images, regular/sale price or the other evidence needed for the required Woo product projection.
- The product connection exposes only platform, shop ID and `readProducts`; the resolver does not expose the independently verified installation origin needed to validate Woo permalinks.

This task explicitly prohibits implementing `src/connections/woocommerce/direct-product-reader.ts` and requires consumption of the already accepted MCP-005 reader. `moda_architect` must amend/sequence the owning MCP-005 contract and provide the verified-origin interface before this task can safely satisfy its Woo acceptance criteria. No candidate URL or product field may be inferred to work around the gap.

### Architectural Concerns

Attempt 1 returned for Architect direction before implementation. The launcher prepared the dedicated worktrees and pushed the parent claim. The accepted MCP-005 interface does not expose the Woo variant/product fields required here and the current resolver does not expose its independently verified origin. No source changes or tests were made. Work Items and Acceptance Criteria remain incomplete; no acceptance decision is requested from this agent.

### Synchronization and Version Control

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-MCP-003`, branch `task/ARCH-052-MCP-003`; parent `origin/main` was incorporated. The launcher claim commit is `04d27dcc6ffc88fbeae9455df1bbec75a96b51cd`, pushed to the task branch.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-MCP-003`, branch `task/ARCH-052-MCP-003`; implementation `origin/main` was already current. Recursive submodule sync and initialization passed; database submodule is `139765042baad3901682cfe9c54a3d6bba73e75c`.
- The implementation worktree is clean at `f1d2a10a29c6930cfc316dfc6119d795100bd1a3`; no implementation commit or implementation-branch push was made because no source changes were safe within this task's boundary.
- No shared/default checkout or other task worktree was used for implementation; no main branch was changed.

## Architect Review

### Attempt 2 Architect Review — Changes Requested

#### Review Status

Changes requested — 2026-10-31. Attempt 2 remains the reviewed attempt; the next launcher claim will create Attempt 3.

#### Review Notes

The product execution, bounded Woo variation reads, tenant/parent identity checks, and URL filtering are materially implemented. Attempt 2 is not accepted because the added Shopify provider diagnostics omit source messages required by the task, required diagnostic tests are absent, and diagnostic-only changes were added to the accepted Woo reader even though ARCH-052-MCP-006 owns that correction.

#### Required Changes

- At the Shopify provider boundary, retain the actual bounded `errors[].message` and `extensions.code` for GraphQL failures, plus original SDK/transport `Error.name`, `Error.message`, and available cause when no provider response exists. Apply explicit sensitive-span redaction and bounds before logging; keep source diagnostics distinct from Moda reason/status. Do not expose them in tool results or model-visible MCP errors.
- Add focused Shopify provider tests for HTTP and GraphQL 200-with-errors paths, transport exceptions, source message/code/request-ID provenance, redaction, and absence of raw provider payloads from public tool results.
- Remove the diagnostic-only changes to `src/connections/woocommerce/direct-product-reader.ts` from MCP-003. Leave the approved product-field/variation/permalink extensions in place as authorized; ARCH-052-MCP-006 owns Woo source-error diagnostics. Do not edit MCP-006 or MCP-005 task records.
- Run the focused tests after the final diagnostic edits. The reported 41 tests predate the final refinement; typecheck alone does not validate its logging behavior. Update the Completion Report with the final test evidence and exact implementation/parent branch synchronization.

#### Reviewed Files

- Attempt 2 Completion Report and task criteria.
- Implementation branch `task/ARCH-052-MCP-003` at `04530c8233db9e4dc42a1c82959597152f09f047`, pushed and clean.
- `src/connections/shopify/provider.ts`, `src/execution/policy/shopify-core.ts`, Woo direct reader and focused product tests.

#### Validation Reviewed

The report records 41 focused checks passing before the final diagnostics refinement, build passing, and typecheck passing after refinement. No tests were run after that refinement. These results were not rerun during architect review.

#### Architecture Conformance

The core product execution follows the task’s Shopify/Woo ownership and data-source constraints. Attempt 2 does not meet the newly added provider-origin diagnostic criteria and must remove the Woo diagnostic portion reserved for MCP-006. The task is returned to Ready; no implementation is accepted yet.

#### Follow-up

Claim Attempt 3 through the canonical launcher after completing the required corrections.

### Attempt 1 Architect Review — Changes Requested

#### Review Status

Changes requested — 2026-10-31. Attempt 1 remains the reviewed attempt; the next launcher claim will create Attempt 2.

#### Review Notes

Attempt 1 correctly identified a real mismatch between the task’s required Woo product projection and the accepted MCP-005 reader. MCP-005 is Complete and remains accepted. MCP-003 is amended to own a narrow extension of that reader for source product fields, bounded variation reads, and permalink validation inside the reader using its already verified installation origin. The amendment does not authorize changes to credential/grant security or network transport.

#### Required Changes

- Extend the existing Woo read request/reader path to return the source fields required by the published Shared product schema, including product type, permalink, image, regular/sale price, sale state, and variation identities.
- Add a bounded, paginated read for actual variation records. Preserve source variation and parent IDs; do not synthesize IDs or mark variable parent products as actual variants. Respect the existing MCP deadline, request budget and result limit.
- Validate each candidate Woo permalink inside the authenticated direct adapter against the independently verified `canonicalSiteUrl` host already loaded from the active installation. Return `url:null` on mismatch, malformed URL or unknown origin; do not expose the origin or create a caller-controlled allowlist.
- Preserve MCP-005 grant, credential, DNS pinning, TLS, redirect, response-size, timeout and post-read grant-recheck behavior. Add focused regression coverage for those existing protections along with MCP-003 projection tests.
- Leave MCP-005’s task record and accepted completion unchanged. No API proxy, Shared schema, database, or package publication changes are authorized.

#### Reviewed Files

- MCP-003 task definition and Attempt 1 Completion Report.
- MCP-005 accepted task definition and Completion Report.
- MCP-005 implementation report at `72ca88dd35967607e6749a5aed9b42cc49339d0b`; the direct adapter keeps the verified installation origin internal.

#### Validation Reviewed

No MCP-003 implementation validation was run or claimed.

#### Architecture Conformance

The task is returned to Ready with the bounded scope amendment. Existing dependency MCP-005 remains Complete; no dependency regression or MCP-005 reopen is required.

#### Follow-up

Claim Attempt 2 through the canonical launcher after reading the amended requirements.
