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
status: in_progress
priority: 40
executor: codex
claimed_at: 2026-10-30T17:49:22Z
attempt: 2
depends_on:
- ARCH-052-BACKGROUND-009
- ARCH-052-SHARED-010
enables:
- ARCH-052-MCP-002
created: '2026-10-30'
updated: 2026-10-30
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

Ready for architect review. The existing Shopify discount catalogue path now stores bounded provider-observed condition facts in `ShopifyDiscount.providerSnapshot`.

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
