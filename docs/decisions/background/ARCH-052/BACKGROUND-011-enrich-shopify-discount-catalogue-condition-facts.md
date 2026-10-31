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
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 3
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

Changes requested after Attempt 3 architect review; ready for Attempt 4. The existing Shopify discount catalogue path now stores bounded provider-observed condition facts and projects the Shopify Basic discount-combination policy through the Shared condition-facts contract in `ShopifyDiscount.providerSnapshot`.

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
