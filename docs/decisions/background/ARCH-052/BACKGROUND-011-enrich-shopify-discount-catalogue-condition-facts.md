---
id: ARCH-052-BACKGROUND-011
architecture_id: ARCH-052
title: Enrich Shopify discount catalogue with source-backed targeting facts
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 40
executor: null
claimed_at: null
attempt: 6
depends_on:
- ARCH-052-BACKGROUND-009
- ARCH-052-SHARED-010
enables:
- ARCH-052-MCP-002
created: '2026-10-30'
updated: 2026-10-31
---

# ARCH-052-BACKGROUND-011: Enrich existing Shopify discount catalogue with targeting facts

## Architecture

ARCH-052. Parent `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`. New repository-owned implementation task, not materialised.

## Objective

Extend the **existing** Shopify discount sync projection so `ShopifyDiscount.providerSnapshot` contains genuine discount kind/value, product/variant/collection targets, purchase thresholds and known restrictions needed by MCP-002. Do not create a separate provider-proof API or business eligibility engine.

## Context

`src/providers/shopify-discount.provider.ts` currently queries only discount title, summary, status, dates and codes. `ShopifyDiscountCatalogueService.reconcile()` already upserts `providerSnapshot`; BACKGROUND-009 separates provider status from merchant selection and must be accepted before this task changes the same path. WooCommerce's `woo-coupon-normalization.ts` already captures coupon restriction fields and does not require a new sync implementation in this task.

## Scope

- Extend `src/providers/shopify-discount.provider.ts` GraphQL selection and `normalizeDiscount()` to retain **bounded, typed, safe** provider discount facts for supported Shopify Basic code/automatic discounts, including discount percentage/amount and currency, customerGets product/variant/collection selections, exclusions when available, minimum subtotal/quantity and customer scope when available. Use Shopify's actual typed GraphQL fragments; do not invent unsupported fields or call the checkout provider.
- Store the fetched facts inside the **existing** `ShopifyDiscount.providerSnapshot` in the existing catalogue upsert. Keep `providerStatus`, `startsAt`, `endsAt`, `lastSyncedAt`, `unavailableAt` and merchant-owned `isAvailable` behaviour unchanged. No Prisma migrations.
- Project **completeness** and `unrepresentedConditions` evidence: app discounts, BxGy, unsupported targeting, incomplete nested pagination and unknown values remain `PARTIAL` or `UNKNOWN`, never falsely `COMPLETE`. Deep provider target enumeration must have bounded pagination/request size; incomplete target enumeration is not represented as an empty unrestricted set.
- Preserve the existing Shopify discount GraphQL page iteration, sync generation transaction and failure handling. Reuse Shared structured logging; no secrets, full raw payloads or customer data in diagnostics.

## Out of Scope

Woo coupon sync, MCP tool implementation, product API search, Commerce private proof routes, AI/LLM ranking, merchant selection UI, schema/migrations, provider cart mutation, ARCH-053 checkout URLs.

## Requirements

- Provider native targets are captured in raw Shopify IDs; `productType` labels are not equivalent to collection IDs. Do not infer conditions from discount title or `summary` text.
- A response whose provider targeting has more nodes than the bounded fetch is marked incomplete. Never mark unsupported/custom provider apps as fully representable.
- Do not make `isAvailable` track Shopify status; BACKGROUND-009 owns that separation.

## Work Items

- [x] Extend the Shopify discount GraphQL fragments and provider normalisation for observed conditions, with explicit supported/partial/unknown outcomes.
- [x] Persist condition facts in the existing `providerSnapshot`, not another table or service.
- [x] Test Basic automatic/code product targets, collection targets, percentage/fixed amounts, purchase minimum, BxGy/app incomplete, nested target truncation, sync retries and preserved merchant selection.
- [x] Run targeted Background test/typecheck/build scripts, record worktree and validation evidence.

## Interfaces / Contracts

Producer: `ShopifyDiscountProvider.listDiscounts` -> `ShopifyDiscountRecord.providerSnapshot` -> existing catalogue upsert. Consumer: MCP-002 reads `providerSnapshot` and maps to `CommerceDiscountConditionFactsSchema` from published SHARED-010. **No new external wire contract**: the snapshot remains database-internal JSON; its provider-observed values map to the exact Shared-009 fields. Missing or incomplete provider targeting must be represented through `completeness`/`unrepresentedConditions` in MCP output.

## Dependencies

- ARCH-052-BACKGROUND-009
- ARCH-052-SHARED-010

## Enables

- ARCH-052-MCP-002

## Acceptance Criteria

- [x] Targeting/value facts are truly source-backed for supported Shopify types and remain bounded.
- [x] Provider pagination/truncation cannot be confused with unrestricted discounts.
- [x] Original catalogue sync and merchant `isAvailable` invariants pass regression tests.

## Validation

- [x] Background Shopify provider and catalogue sync tests with real-world shaped GraphQL fixtures.
- [x] Declared Background typecheck/build and `git diff --check`; record command outcomes.

## Stop Condition

Set `status:review`, return Completion Report to architect and STOP. Do not start MCP-002.

## Implementation Notes

Source files: `moda-interact-background/src/providers/shopify-discount.provider.ts`, `src/services/shopify-discount-catalogue.service.ts` (only if necessary to retain provider facts), corresponding tests. Existing Woo source unchanged. This task deliberately does not make live provider reads during outreach; only the pre-existing catalogue synchroniser reads Shopify.

## Completion Report

### Status

Accepted after Attempt 6. Malformed job payloads and invalid timestamps receive explicit per-job Shared error logs with bounded, redacted exception fields, while original errors still propagate to BullMQ.

### Files Changed

Implementation commit `00941fdef05611569b73f2e106e442c6781ae6d1` is pushed to `origin/task/ARCH-052-BACKGROUND-011`:

- `moda-interact-background/src/providers/shopify-discount.provider.ts`
- `moda-interact-background/tests/unit/providers/shopify-discount.provider.test.ts`
- `moda-interact-background/tests/unit/services/shopify-discount-catalogue.service.test.ts`

The catalogue service already persists `providerSnapshot` through its existing upsert; no service or schema change was needed. The implementation branch contains no dependency-file or submodule-gitlink changes.

### Work Completed

The existing 2026-07 Shopify GraphQL query now selects typed native Basic discount values, customerGets targets, minimum requirements, customer context and available usage facts. It handles automatic and code Basic discounts while retaining the existing app, BxGy and free-shipping catalogue selection. Provider snapshots include the Shared-010 condition-facts fields, and a regression asserts the shape parses through `CommerceDiscountConditionFactsSchema`.

Target enumeration is capped at 20 products, variants or collections per nested connection, with 10 discount nodes per request and an overall 1,000-page bound. Truncated targets and unsupported/app/BxGy types are marked `PARTIAL` with bounded `unrepresentedConditions`; they are never treated as unrestricted. The outer cursor must advance or the provider throws, allowing the existing sync failure/retry path to handle it. No titles or summaries are used to infer conditions, and no customer identifiers are fetched for customer scope.

The catalogue retry regression verifies a failed provider read does not persist a partial snapshot and a subsequent retry stores the enriched facts. The existing PostgreSQL selection integration verifies merchant `isAvailable` remains selected after a later sync. Provider status, sync timestamps, row unavailability, and merchant selection handling remain owned by the existing catalogue service.

### Validation Results

- Focused command `npm exec vitest run tests/unit/providers/shopify-discount.provider.test.ts tests/unit/services/shopify-discount-catalogue.service.test.ts` — 2 files, 11 tests passed.
- Existing PostgreSQL selection integration `npm run test:arch052-shopify-discount-selection:postgres` — 1 file, 2 tests passed.
- `npm run build` — passed, including Prisma Client generation and TypeScript compilation.
- Changed-file ESLint on the provider and both test files — passed.
- `git diff --check` — passed.

The implementation worktree initially had no `node_modules`; `npm ci` installed the lockfile dependencies. npm reported 23 dependency advisories (10 moderate and 13 high); no package manifest or lockfile was changed.

### Launcher and Synchronization Evidence

Preparation packet claim: Attempt 1, `codex`, pushed parent claim commit `fc950dff27247e160dcabf12dc73b15e803cc054`; dependency gate passed with `ARCH-052-BACKGROUND-009` and `ARCH-052-SHARED-010` both Complete.

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-BACKGROUND-011`, branch `task/ARCH-052-BACKGROUND-011`; created for this task. Start sync: remote task branch fast-forward `not-needed`; `origin/main` incorporated `already-current`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-BACKGROUND-011`, branch `task/ARCH-052-BACKGROUND-011`; created for this task. Start sync: remote task branch fast-forward `not-needed`; `origin/main` incorporated `already-current`.
- Recursive submodule sync and update passed. `database` is initialized at `af77c594ecbfc78c26d01c0021a090830884bbff`.
- The shared workspace and source checkout were not switched or mutated for task implementation; no other task worktree was reused. `main` was not changed.

### Deviations, Assumptions and Unresolved Issues

No scope deviations or unresolved architecture questions. Native Shopify Basic discounts expose included item targets but no separate excluded-product selection; excluded target arrays therefore remain empty for those supported types. Unsupported types and unrepresented market restrictions remain partial. The Architect Review and parent architecture/index were not modified. ARCH-052-MCP-002 was not started.

### Attempt 2 — Architect Review Correction

The requested correction is implemented in commit `b2824e2` on the same task branch and pushed to `origin/task/ARCH-052-BACKGROUND-011`. Both `DiscountAutomaticBasic` and `DiscountCodeBasic` now query `combinesWith.orderDiscounts`, `productDiscounts`, `shippingDiscounts`, and `productDiscountsWithTagsOnSameCartLine`. The normalized `combinesWith` object is retained in the existing provider snapshot; its tag list is capped at 24 entries and each tag at 128 characters. Truncation or malformed policy data is explicitly reported as `COMBINATION_TAGS_TRUNCATED` or `COMBINATION_POLICY_UNAVAILABLE`.

The Shared-010 condition-facts contract has no fields for discount-class combinations or same-cart-line tags. Therefore Basic discount facts now include `COMBINATION_POLICY_NOT_REPRESENTED_IN_SHARED_FACTS` and remain `PARTIAL`, even when their other observed fields are complete. The regression asserts both GraphQL fragments select the policy, the normalized policy survives in the provider snapshot, and the Shared schema accepts the resulting partial facts. Shopify's versioned API reference documents these fields on `DiscountCombinesWith` and both Basic discount types: [DiscountCombinesWith](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/DiscountCombinesWith), [DiscountAutomaticBasic](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/DiscountAutomaticBasic), and [DiscountCodeBasic](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/DiscountCodeBasic).

#### Architect Review item disposition

- **Combination policy omitted while facts could be COMPLETE — implemented.** Added the selection for both Basic types, retained the bounded normalized policy in `providerSnapshot.combinesWith`, and forced `conditionFacts.completeness` to `PARTIAL` with an explicit Shared-contract unrepresented reason. Focused assertion: `tests/unit/providers/shopify-discount.provider.test.ts` checks both selections, the policy values, partial completeness, and Shared schema parsing.

#### Attempt 2 validation

- `npm exec vitest run tests/unit/providers/shopify-discount.provider.test.ts tests/unit/services/shopify-discount-catalogue.service.test.ts` — 2 files, 11 tests passed.
- `npm exec eslint -- src/providers/shopify-discount.provider.ts tests/unit/providers/shopify-discount.provider.test.ts` — passed.
- `npm run build` — passed (Prisma Client generation and TypeScript compilation).
- `git diff --check` — passed in both the implementation and parent task worktrees.

#### Attempt 2 launcher and branch evidence

- The prepared launcher claimed Attempt 2 as `codex`; authoritative task metadata records `claimed_at: 2026-10-30T17:49:22Z`. Parent claim commit: `c87784cd9dd62b744c76a73c78925029f7928dba`, pushed to `origin/task/ARCH-052-BACKGROUND-011`.
- The dedicated implementation worktree remained on `task/ARCH-052-BACKGROUND-011`, starting from `00941fdef05611569b73f2e106e442c6781ae6d1`; at inspection, local `HEAD` and `origin/task/ARCH-052-BACKGROUND-011` matched. The report-only parent worktree remained on the same task branch.
- The launcher invocation returned no preparation packet text after the task entered `in_progress`, so detailed fast-forward/`origin/main` merge summaries and recursive-submodule output for Attempt 2 are unavailable in this report. The launcher's authoritative claim metadata and commit are retained above; Attempt 1 synchronization evidence remains recorded in the preceding section.

ARCH-052-MCP-002 was not started.

### Attempt 3 — Shared Combination-Facts Projection

Implementation commit `f92458d` is pushed to `origin/task/ARCH-052-BACKGROUND-011`.

The prepared launcher claimed Attempt 3 as `codex` at `2026-10-31T01:36:31Z` and pushed parent claim commit `3ffe08d824f1f6a2a662135e63834415a3e14af5`. Its dependency gate passed for `ARCH-052-BACKGROUND-009` and `ARCH-052-SHARED-010`.

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-BACKGROUND-011`, branch `task/ARCH-052-BACKGROUND-011`, starting at `1963a82ed20fce52b5af88bba1aad1b28adfae4a`; remote task-branch fast-forward was `not-needed`, and `origin/main` was already current.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-BACKGROUND-011`, branch `task/ARCH-052-BACKGROUND-011`, starting at `b2824e28a7b53347e2f64c0622d462a8bc2db7cb`; remote task-branch fast-forward was `not-needed`, and `origin/main` was already current.
- Recursive database submodule initialization and synchronization passed at `af77c594ecbfc78c26d01c0021a090830884bbff`.

The configured public npm registry was checked for `@modainteract/moda-interact-shared@2.8.2` and returned `E404` (“No match found for version 2.8.2”). The available published `2.8.1` contract provides `CommerceDiscountCombinationFactsSchema` with `discountClasses`, `shopifyPlus`, `combinesWith`, `discountTags`, and `allowedSameLineProductTags`; the provider test parses projected facts through the published `CommerceDiscountConditionFactsSchema`. The implementation therefore pins Shared `2.8.1`, the available contract version that supports the requested projection, rather than claiming to consume unavailable `2.8.2`.

The existing Shopify query now selects `shop.plan.shopifyPlus`, both Basic types' `discountClasses` and `tags`, and their order/product/shipping plus same-cart-line combination policy. The provider projects those fields into the Shared combination facts, bounds tags to the contract's 64-entry/128-character limits, retains a bounded normalized policy in the existing provider snapshot, and marks facts `PARTIAL` with explicit reasons when policy fields or plan context are missing or truncated. Complete source-backed fixtures now prove the projected facts parse through Shared and may be `COMPLETE`; a missing-plan regression proves policy uncertainty remains `PARTIAL`. No catalogue service, persistence path, database schema, or other repository changed.

#### Attempt 3 Architect Review disposition

- **Verify Shared 2.8.2 and project combination facts when supported — implemented.** Registry verification found 2.8.2 unavailable, while the available Shared 2.8.1 published schema includes all required combination fields. Pinned 2.8.1 and projected the fields in `src/providers/shopify-discount.provider.ts`. Regression coverage in `tests/unit/providers/shopify-discount.provider.test.ts` asserts the GraphQL selection, all five projected fields, Shared schema parsing, and conservative PARTIAL behavior when plan context is absent.
- **Preserve PARTIAL while known combination policy is unrepresented — implemented.** Combination completeness now depends on the fetched flags, classes, discount tags, same-line tags, and plan context; missing or truncated values produce named unrepresented conditions. The previous unconditional Shared-unrepresented reason is removed because the selected contract now represents these facts.
- **Do not start MCP-002 — satisfied.** No MCP-002 work was started.

#### Attempt 3 validation

- `npm exec vitest run tests/unit/providers/shopify-discount.provider.test.ts tests/unit/services/shopify-discount-catalogue.service.test.ts` — 2 files, 12 tests passed.
- `npm exec eslint -- src/providers/shopify-discount.provider.ts tests/unit/providers/shopify-discount.provider.test.ts` — passed.
- `npm run build` — passed, including Prisma Client generation and TypeScript compilation.
- `git diff --check` — passed.
- `npm view @modainteract/moda-interact-shared@2.8.2 version` — returned `E404`; `2.8.2` is not available from the configured public registry. The available published contract was validated through the focused Shared-schema parsing regression.
- The Attempt 2 PostgreSQL selection integration result remains recorded above (2 tests passed). It was not rerun in Attempt 3 because the changes are confined to the provider query/normalization, dependency pin and provider unit coverage; no database behavior or schema changed.
- Installing Shared 2.8.1 reported 40 npm audit advisories (27 moderate, 13 high). The package install also emitted lifecycle-script allow-list notices. These are dependency-install observations; no remediation outside this bounded task was performed.

ARCH-052-MCP-002 was not started.

### Attempt 4 — Recurring Cycle Limit Correction

Implementation commit `871670b` is pushed to `origin/task/ARCH-052-BACKGROUND-011`.

The prepared launcher claimed Attempt 4 as `codex` at `2026-10-31T02:06:34Z` and pushed parent claim commit `4d370b5c05ab656fd2fc1c3469fda5e0f0f9b1ee`. Its dependency gate passed for `ARCH-052-BACKGROUND-009` and `ARCH-052-SHARED-010`.

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-BACKGROUND-011`, branch `task/ARCH-052-BACKGROUND-011`, starting at `e6d77848d54e723b020d22d3f4b0ba0541ee6e34`; remote task-branch fast-forward was `not-needed`, and `origin/main` was incorporated (`yes`).
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-BACKGROUND-011`, branch `task/ARCH-052-BACKGROUND-011`, starting at `f92458d6188515e49ec2eaa1ba8615c6852fd73a`; remote task-branch fast-forward was `not-needed`, and `origin/main` was already current.
- Recursive database submodule sync and initialization passed at `af77c594ecbfc78c26d01c0021a090830884bbff`.

Both `DiscountAutomaticBasic` and `DiscountCodeBasic` GraphQL fragments now select `recurringCycleLimit`. The existing provider snapshot retains its normalized integer value (or `null` when unavailable). Shared 2.8.1 has no condition-facts field for this restriction, so a positive limit adds `RECURRING_CYCLE_LIMIT_NOT_REPRESENTED_IN_SHARED_FACTS` and keeps facts PARTIAL. A null, missing, or invalid value adds `RECURRING_CYCLE_LIMIT_UNAVAILABLE` and also keeps facts PARTIAL; zero means no cycle cap and does not by itself reduce completeness. Shopify documents the automatic field as non-null, the code field as nullable, and zero as indefinite: [DiscountAutomaticBasic](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/DiscountAutomaticBasic), [DiscountCodeBasic](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/DiscountCodeBasic). No Shared contract change was needed; the value remains available in the existing provider snapshot and incompleteness is explicit in the Shared facts.

#### Attempt 4 Architect Review disposition

- **Select and retain recurringCycleLimit for both Basic types — implemented.** Updated `src/providers/shopify-discount.provider.ts` query fragments and bounded normalization to retain the value under the existing provider snapshot.
- **Prevent COMPLETE when a cycle limit may affect subscription eligibility — implemented.** Positive, null, missing and invalid values make facts PARTIAL with explicit bounded reasons because Shared 2.8.1 cannot represent the restriction. Zero is retained as the source-backed unlimited value.
- **Add both-type regressions and Shared schema parsing — implemented.** `tests/unit/providers/shopify-discount.provider.test.ts` checks both Basic fragments, positive limits on both types, null code-limit behavior, explicit PARTIAL reasons and Shared schema parsing.
- **Do not start MCP-002 — satisfied.** No MCP-002 work was started.

#### Attempt 4 validation

- `npm exec vitest run tests/unit/providers/shopify-discount.provider.test.ts tests/unit/services/shopify-discount-catalogue.service.test.ts` — 2 files, 15 tests passed.
- `npm exec eslint -- src/providers/shopify-discount.provider.ts tests/unit/providers/shopify-discount.provider.test.ts` — passed.
- `npm run build` — passed, including Prisma Client generation and TypeScript compilation.
- `git diff --check` — passed.
- PostgreSQL selection integration was not rerun: this correction changes only Shopify provider fields/normalization and provider unit coverage; no persistence or database behavior changed. The earlier Attempt 2 integration result remains recorded above.

ARCH-052-MCP-002 was not started.

### Attempt 5 — Shared Logger Diagnostic Correction

The prepared launcher claimed Attempt 5 as `codex` at `2026-10-31T03:24:48Z` and pushed parent claim commit `19805fa2adb1a2965f9d1b96db23499f5010ce65`. Its dependency gate passed for `ARCH-052-BACKGROUND-009` and `ARCH-052-SHARED-010`.

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-BACKGROUND-011`, branch `task/ARCH-052-BACKGROUND-011`, starting at `1527b061a12be0bd8a2feb3d309d0887626ea3f5`; task-branch fast-forward was `not-needed`, and `origin/main` was already current.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-BACKGROUND-011`, branch `task/ARCH-052-BACKGROUND-011`, starting at `871670b47bd9a3ccb9831eac42ffd1d5d1d1cd7a`; task-branch fast-forward was `not-needed`, and `origin/main` was already current.
- Recursive submodule synchronization and initialization passed; the database submodule is at `af77c594ecbfc78c26d01c0021a090830884bbff`.

The provider now represents Shopify GraphQL errors with bounded provider response diagnostics. It preserves source `errors[].message`, `extensions.code`, HTTP status, and an available request ID. Provider message, code, request ID, exception message, stack, and up to three cause entries are redacted and bounded before becoming explicit fields passed to the Shared logger. Internally generated pagination/response failures have `origin: internal`; external GraphQL failures have `origin: provider_response`; transport exceptions retain `origin: sdk_exception`. Missing provider errors do not create a fabricated `providerErrors` field. The response body and successful GraphQL payload are never logged. Non-JSON HTTP error responses retain only HTTP status and a `providerResponseFormat: non_json` marker because their body cannot be safely filtered as structured source diagnostics.

The catalogue service logs a stable `reasonCode` and persists `lastErrorCode: SHOPIFY_DISCOUNT_PROVIDER_FAILED`, independent of provider diagnostic text. The worker logs explicit exception stack/cause fields for internal and SDK failures and avoids a second log for provider failures already logged at the catalogue boundary. Failures continue to propagate for the existing retry behavior. Regression tests assert safe GraphQL message/code retention, diagnostics reaching the service/worker Shared logger fields, redaction of test credentials and PII, stable persisted failure classification, and single-boundary provider logging.

#### Attempt 5 Architect Review disposition

- **Preserve bounded, redacted actual diagnostics — implemented.** Added explicit exception name, message, stack, and bounded cause fields at the logging boundary; the Shared logger still owns output serialization and sink isolation.
- **Preserve actionable Shopify GraphQL failures safely — implemented.** Retain sanitized provider message, code, status and request ID only; raw response bodies and customer/provider payloads are not logged.
- **Keep catalogue state stable and add regressions — implemented.** Failure persistence uses a stable Moda reason code, and provider/service/worker tests verify safe diagnostic fields and no duplicate boundary log.
- **Keep MCP-002 pending — satisfied.** No MCP-002 implementation was started.

#### Attempt 5 validation

- Focused command `npm test -- tests/unit/providers/shopify-discount.provider.test.ts tests/unit/services/shopify-discount-catalogue.service.test.ts tests/unit/workers/shopify-discount-sync.worker.test.ts` — 3 files, 24 tests passed.
- Changed-file ESLint across the provider, service, worker, and three corresponding unit test files — passed.
- `npm run build` — passed, including Prisma Client generation and TypeScript compilation.
- `git diff --check` — passed in the implementation and parent task worktrees.
- PostgreSQL selection integration was not rerun; the correction changes diagnostics and stable error classification only, and does not alter database queries or selection behavior. The earlier Attempt 2 integration evidence remains recorded above.

The implementation changes are in `src/providers/shopify-discount.provider.ts`, `src/services/shopify-discount-catalogue.service.ts`, `src/workers/shopify-discount-sync.worker.ts`, and their three corresponding unit tests. No package, lockfile, submodule gitlink, database schema, or MCP implementation changes were made.

Implementation commits `5106838d6d582eb9ef08484d9de71232a6bf33ef` and `cffbbd819850c1d33d0c6840f7ff13da26210edd` are pushed to `origin/task/ARCH-052-BACKGROUND-011`.

ARCH-052-MCP-002 was not started.

### Attempt 6 — Log Invalid Shopify Discount Sync Jobs

The prepared launcher claimed Attempt 6 as `codex` at `2026-10-31T04:13:34Z` and pushed parent claim commit `f24073c0da5f42a343faf0ea65b0c8239833355e`. Its dependency gate passed for `ARCH-052-BACKGROUND-009` and `ARCH-052-SHARED-010`.

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-BACKGROUND-011`, branch `task/ARCH-052-BACKGROUND-011`, starting at `e118ac0556d67bb40225685f572149fafe427b59`; task-branch fast-forward was `not-needed`, and `origin/main` was already current.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-BACKGROUND-011`, branch `task/ARCH-052-BACKGROUND-011`, starting at `cffbbd819850c1d33d0c6840f7ff13da26210edd`; task-branch fast-forward was `not-needed`, and `origin/main` was already current.
- Recursive submodule synchronization and initialization passed; the database submodule is at `af77c594ecbfc78c26d01c0021a090830884bbff`.

The worker now performs shared job parsing, `requestedAt` validation, validated-field construction, and processing inside one per-job `try/catch`. Invalid payloads and timestamps emit `shopify.discount_sync.failed` with stable `reasonCode: SHOPIFY_DISCOUNT_SYNC_JOB_INVALID` and bounded, redacted `errorName`, `errorMessage`, `errorStack`, and cause fields. The invalid-input log omits job identifiers and payload-derived fields entirely. After successful validation, processing failures retain their existing stable sync reason and safe validated context. The worker rethrows the original exception in every failure case so BullMQ retry/rejection behavior is unchanged.

#### Attempt 6 Architect Review disposition

- **Log malformed job payloads through the Shared logger — implemented.** Added the parse operation to the existing processor failure boundary and a regression showing its actual redacted message, stack and cause reach the Shared logger.
- **Log invalid `requestedAt` and preserve retry propagation — implemented.** Invalid timestamps receive the same stable invalid-job classification and reject to BullMQ; the regression asserts no reconciliation call occurs.
- **Exclude raw payload and untrusted fields — implemented.** Tests assert malformed and invalid-timestamp log records omit the job ID, shop context and injected private payload values.
- **Keep MCP-002 pending — satisfied.** No MCP-002 implementation was started.

#### Attempt 6 validation

- Focused command `npm test -- tests/unit/providers/shopify-discount.provider.test.ts tests/unit/services/shopify-discount-catalogue.service.test.ts tests/unit/workers/shopify-discount-sync.worker.test.ts` — 3 files, 26 tests passed.
- Changed-file ESLint across the provider, service, worker and three corresponding unit test files — passed.
- `npm run build` — passed after aligning the safe worker context types with nullable `shopId` and `webhookTopic` in the Shared payload schema; includes Prisma Client generation and TypeScript compilation.
- `git diff --check` — passed in the implementation and parent task worktrees.
- PostgreSQL selection integration was not rerun; this correction is limited to worker job validation and error logging, without database behavior changes. The earlier Attempt 2 integration result remains recorded above.

The Attempt 6 implementation changes only `src/workers/shopify-discount-sync.worker.ts` and `tests/unit/workers/shopify-discount-sync.worker.test.ts`. No package, lockfile, submodule gitlink, database schema or MCP implementation changes were made.

Implementation commit `ab0feab2649ca2a175997d65ec57ff9fd7261971` is pushed to `origin/task/ARCH-052-BACKGROUND-011`.

ARCH-052-MCP-002 was not started.

## Architect Review

### Review Status

Changes Requested — Attempt 1.

### Review Notes

The Shopify Basic discount query omits the source-available `combinesWith` policy for both automatic and code discounts. Shopify exposes order, product, and shipping combination rules (plus same-cart-line product-discount tags) on these types. `normalizeConditionFacts()` can nevertheless mark a Basic discount `COMPLETE`, leaving a known restriction absent from the snapshot and making completeness overstate the observed facts.

For the next attempt, query and retain the combination policy in the existing provider snapshot and make it available to the eventual condition projection. If the agreed condition-facts contract cannot represent a policy, explicitly mark that policy unrepresented and keep completeness `PARTIAL`; do not report `COMPLETE` while the known policy is omitted. Keep the fix within this task's existing catalogue path and do not start MCP-002.

### Reviewed Files

- `moda-interact-background/src/providers/shopify-discount.provider.ts`
- `moda-interact-background/tests/unit/providers/shopify-discount.provider.test.ts`
- `moda-interact-background/tests/unit/services/shopify-discount-catalogue.service.test.ts`
- This task's Completion Report and VCS evidence.

### Validation Reviewed

Reviewed the submitted evidence: 11 focused unit tests, 2 PostgreSQL selection integration tests, build/typecheck, changed-file lint, and `git diff --check` are reported as passing. These checks were not rerun during this architect review.

### Architecture Conformance

Changes Requested. Source-backed targeting, bounded pagination, retry behavior, merchant selection preservation, scope boundaries, and the reported task worktree evidence otherwise conform. The unqueried combination policy prevents acceptance because the implementation can label an incomplete restriction set `COMPLETE`.

### Follow-up

Return the same task to `ready` for Attempt 2. Preserve Attempt 1 history and do not promote ARCH-052-MCP-002 until this task is accepted and its other dependencies are complete.


## Architect Review — Attempt 2

### Review Status

Changes Requested — Attempt 2.

### Review Notes

Attempt 2 now retrieves and retains Shopify Basic discount combination policy and conservatively marks the condition facts PARTIAL because the Shared-010 contract does not represent that policy. This addresses the completeness risk identified in Attempt 1. Before changing the projection, Attempt 3 must verify whether the currently published Shared 2.8.2 contract supports these combination fields. If supported, project the source-backed fields through the contract with regression coverage; if unsupported, retain PARTIAL and document the exact contract limitation. Do not report COMPLETE while a known policy is not represented, and do not start MCP-002.

### Reviewed Files

- Attempt 2 implementation summary, changed files, and validation evidence in this task report.
- `docs/decisions/background/ARCH-052/_index.md` (reconciled with `origin/main`).

### Validation Reviewed

Reviewed the reported Attempt 2 focused tests, PostgreSQL selection integration, build, changed-file lint, and `git diff --check`; these were not rerun during this architect review.

### Architecture Conformance

The bounded Shopify provider snapshot and conservative PARTIAL completeness behavior remain within task scope. Acceptance is deferred until Attempt 3 establishes whether Shared 2.8.2 can represent the retrieved combination policy and the implementation projects it when supported.

### Follow-up

Return the task to `ready` for Attempt 3. Preserve the Attempt 1 and Attempt 2 history. Keep ARCH-052-MCP-002 unpromoted until this task is accepted and its other dependencies are complete.


## Architect Review — Attempt 3

### Review Status

Changes Requested — Attempt 3.

### Review Notes

The Attempt 3 combination-policy projection is supported by the published Shared 2.8.1 schema; the registry lookup for 2.8.2 and the reported contract tests are consistent with that conclusion. One source-backed Basic discount restriction remains omitted: Shopify exposes `recurringCycleLimit` on both `DiscountAutomaticBasic` and `DiscountCodeBasic`, but the GraphQL query does not select it. The current Shared 2.8.1 `CommerceDiscountConditionFactsSchema` has no field for this limit, and the provider can still label otherwise complete Basic facts `COMPLETE` without recording or flagging it.

For Attempt 4, select and retain `recurringCycleLimit` in the existing provider snapshot. If the Shared contract cannot represent it, add a bounded `unrepresentedConditions` reason and keep the condition facts `PARTIAL` whenever the value may affect subscription eligibility. Add regression coverage for both Basic discount types and schema parsing. Do not start MCP-002.

### Reviewed Files

- `src/providers/shopify-discount.provider.ts`
- `tests/unit/providers/shopify-discount.provider.test.ts`
- Attempt 3 Completion Report and Shared 2.8.1 contract evidence.

### Validation Reviewed

Reviewed the Attempt 3 reported focused tests, changed-file lint, build, `git diff --check`, and Shared registry/schema verification. These checks were not rerun during this architect review.

### Architecture Conformance

The combination policy is now source-backed and projected through the available Shared contract. Acceptance is deferred because `recurringCycleLimit` is another source-backed restriction omitted from the projection while completeness can be reported as `COMPLETE`.

### Follow-up

Return the task to `ready` for Attempt 4. Preserve prior attempt history and keep ARCH-052-MCP-002 unpromoted until this task is accepted and its other dependencies are complete.


## Architect Review — Attempt 4

### Review Status

Accepted — Complete.

### Review Notes

Attempt 4 resolves the remaining completeness finding. Both Shopify Basic GraphQL fragments select `recurringCycleLimit`, and the existing provider snapshot retains the normalized value. A positive value is preserved and marks Shared facts PARTIAL because Shared 2.8.1 cannot represent the cycle cap; null, missing, or invalid values also mark facts PARTIAL with an explicit unavailable reason. Zero is retained as the source-backed unlimited value and does not reduce completeness. This matches Shopify's 2026-07 Admin API documentation for [DiscountAutomaticBasic](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/DiscountAutomaticBasic) and [DiscountCodeBasic](https://shopify.dev/docs/api/admin-graphql/2026-07/objects/DiscountCodeBasic).

The Attempt 3 Shared combination-facts projection remains valid. No Shared contract change is needed for this task; the unrepresentable positive cycle limit is explicitly surfaced as incomplete.

### Reviewed Files

- `src/providers/shopify-discount.provider.ts`
- `tests/unit/providers/shopify-discount.provider.test.ts`
- Attempt 4 Completion Report and VCS evidence.

### Validation Reviewed

Reviewed the reported 15 focused provider/service tests, changed-file ESLint, build, and `git diff --check`; these checks were not rerun during architect review. The implementation reports no database changes and appropriately did not rerun PostgreSQL selection integration.

### Architecture Conformance

Accepted. The bounded provider snapshot preserves source-backed combination and cycle-limit facts, marks unsupported or unavailable conditions PARTIAL, and keeps existing catalogue persistence and merchant selection behavior unchanged.

### Follow-up

Mark ARCH-052-BACKGROUND-011 Complete. The separate, unmaterialized ARCH-052-BACKGROUND-013 task is superseded because its tags, discount classes, and Plus entitlement requirements are delivered by this accepted implementation. Remove that redundant dependency from MCP-002 and SYSTEM-TEST-001. MCP-002 is dependency-ready; do not start it as part of this review.


## Architect Review — Post-Acceptance Logging Finding

### Review Status

Changes Requested — reopen for Attempt 5.

### Review Notes

The catalogue service and worker do call the Shared structured logger with the thrown `Error`, and the log includes its message. However, Shared logging sanitizes `Error` objects to only `name` and `message`, so the stack and cause chain are omitted. In addition, the provider currently replaces Shopify GraphQL `errors` with a generic `Shopify discount GraphQL returned an invalid response` exception. Those paths lose the diagnostics needed to identify the underlying provider failure.

For the next attempt, retain bounded, redacted details from the actual error (including stack and cause where available) as explicit structured fields, and preserve actionable Shopify GraphQL error messages/codes without logging raw response bodies, credentials, or customer data. Keep stable catalogue error state separate from diagnostic text. Add regression coverage proving the actual diagnostic fields reach the Shared logger and GraphQL failure details are retained safely.

### Reviewed Files

- `src/providers/shopify-discount.provider.ts`
- `src/services/shopify-discount-catalogue.service.ts`
- `src/workers/shopify-discount-sync.worker.ts`
- Shared `@modainteract/moda-interact-shared/logging` Error sanitization behavior.

### Architecture Conformance

Changes Requested. Provider failures are not silently swallowed, but current logging does not retain enough error detail to understand their underlying cause. Preserve the bounded and redacted diagnostics described above while keeping provider response payloads and secrets out of logs.

### Follow-up

Return the task to `ready` for Attempt 5. Preserve Attempts 1–4 and the prior acceptance record as history. Keep `ARCH-052-MCP-002` pending until this logging gap is corrected and the task is accepted again.


## Architect Review — Attempt 5

### Review Status

Changes Requested — Attempt 5.

### Review Notes

The Attempt 5 provider and reconciliation errors now reach the Shared logger with bounded, redacted exception diagnostics, and Shopify GraphQL messages/codes are retained without logging raw bodies. The non-JSON response handling correctly records only HTTP status and a `non_json` marker.

One worker failure path remains outside the logging boundary: `parseShopifyDiscountSyncJob(job.data)` and the `requestedAt` date validation run before the `try` block. If either throws, the job processor rejects to BullMQ without an explicit Shared error log containing the actual exception. The worker-level `error` event handler is not a substitute for per-job processor failure logging.

Move payload parsing and timestamp validation inside the worker's failure logging boundary. Log a stable reason code and bounded, redacted exception name/message/stack/cause fields while preserving retry propagation. Do not include the raw job payload or untrusted fields in the log. Add regressions proving malformed job data and invalid timestamps are logged through the Shared logger and still reject for BullMQ handling.

### Reviewed Files

- `src/workers/shopify-discount-sync.worker.ts`
- `tests/unit/workers/shopify-discount-sync.worker.test.ts`
- Attempt 5 Completion Report and validation evidence.

### Validation Reviewed

Reviewed the reported 24 focused tests, changed-file ESLint, build/typecheck and `git diff --check`; these checks were not rerun during this architect review.

### Architecture Conformance

Changes Requested. Attempt 5 resolves the provider diagnostic and sensitive non-JSON response concerns, but malformed job input and invalid timestamps still lack explicit per-job Shared error logs.

### Follow-up

Return the task to `ready` for Attempt 6. Preserve Attempts 1–5 and the Attempt 5 implementation/report history. Keep `ARCH-052-MCP-002` pending until this task is accepted and its other dependencies are complete.


## Architect Review — Attempt 6

### Review Status

Accepted — Complete.

### Review Notes

The remaining per-job logging gap is closed. Shared job parsing and `requestedAt` validation now execute inside the worker processor's failure boundary. Invalid payloads use the stable `SHOPIFY_DISCOUNT_SYNC_JOB_INVALID` reason code and the Shared diagnostic helper records bounded, redacted exception name, message, stack and causes. Invalid input is logged without job identifiers or payload-derived context. The worker rethrows the original exception, preserving BullMQ retry/rejection handling.

The regressions cover malformed parser input and invalid timestamps, assert the diagnostic fields reach the Shared logger, verify sensitive payload values are absent, and confirm processor rejection. Provider response bodies remain excluded from logs. No remaining ARCH-052-BACKGROUND-011 acceptance gap was found.

### Reviewed Files

- `src/workers/shopify-discount-sync.worker.ts`
- `tests/unit/workers/shopify-discount-sync.worker.test.ts`
- Attempt 6 Completion Report and validation evidence.

### Validation Reviewed

Reviewed the reported 26 focused tests, changed-file ESLint, build/typecheck and `git diff --check`; these checks were not rerun during architect review.

### Architecture Conformance

Accepted. The implementation closes the requested malformed-job and invalid-timestamp logging gap, retains bounded/redacted diagnostics, excludes raw job payloads and preserves failure propagation. MCP-002 remains Pending because its other dependencies are incomplete. BACKGROUND-013 is now Ready because BACKGROUND-011 was its sole dependency.
