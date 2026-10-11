---
id: ARCH-028-SHARED-003
architecture_id: ARCH-028
title: Define compatible checkout-update lookup-context contract
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 28
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-028-SHARED-002
enables:
  - ARCH-028-SHARED-004
created: 2026-10-08
updated: 2026-10-11
---
# Define compatible checkout-update lookup-context contract

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Define a strict new-version Shopify checkout.updated event contract with `(shopId, checkoutToken)` identity and optional bounded provider lookup context, while continuing to parse unchanged queued v2 events.

## Context

Current `CheckoutUpdatedPayloadV2Schema` is `.strict()` and contains only `checkoutToken`. It must not be extended in place: older consumers would reject new v2 fields. The existing Background `AbandonedCheckoutLookupService` currently needs a URL and creation-time search window to retrieve an abandoned checkout, which is different from the checkout business identity. Define this contract only after the WhatsApp Shared release gate to avoid competing publication branches.

## Scope

- Preserve the existing v2 checkout.updated schema and all other v2 recovery-event types without changes.
- Introduce a separately versioned strict v3 checkout.updated shape with required non-empty `checkoutToken` and optional nullable bounded `cartToken`, `checkoutCreatedAt` (ISO datetime) and `abandonedCheckoutUrl` (URL using existing bound). Do not require URL/timestamp to identify or deduplicate a checkout.
- Expose the canonical versioned parser/type accepting existing v2 recovery events and v3 checkout.updated, with a clearly named v3 event/version export; retain the old v2 parser for existing clients.
- Keep queue name, deterministic checkout ordering key, tenant/receipt/authentication fields, versioning rules and payload bounds consistent with the existing Shopify Shared event contract.
- Add focused strictness/version/no-context tests, including rejection of a v3-shaped event labelled v2 and malformed optional lookup context.

## Out of Scope

- Shopify webhook normalization/producer (SHOPIFY-001).
- Background candidate re-entry/lookup (BACKGROUND-012).
- Modifying WhatsApp provider-status v2/v3 contract or its SHARED-002 release.
- Publishing the package (SHARED-004).
- Adding a required `abandonedCheckoutUrl` identity or new Redis/database context cache.

## Requirements

- [x] `shopId + checkoutToken` remains canonical application business identity; URL is optional Shopify lookup context only.
- [x] V2 strict schema is unchanged; v2 queue events still parse with canonical new parser.
- [x] V3 checkout.updated has distinct version and bounded optional context, while other v2 event variants remain valid.
- [x] Other existing Shopify event schemas, queue names and deterministic IDs are unchanged.
- [x] Cross-repository consumers use the published Shared exports rather than local copies.

## Work Items

- [x] Define/export strict v3 checkout.updated payload/event and version metadata.
- [x] Add canonical parser/type for v2 recovery events plus v3 checkout.updated.
- [x] Add tests for v2/v3, absent context, bad URL/datetime, unknown fields and existing event regressions.
- [x] Validate public `@modainteract/moda-interact-shared/shopify` export declarations and package build.

## Interfaces / Contracts

Owner `moda-interact-shared`; package export `@modainteract/moda-interact-shared/shopify`; producers `moda-interact`; consumers `moda-interact-background`. Runtime validation via canonical v2/v3 event parser. Existing v2 checkout.updated stays strict and unchanged. New v3 payload: `{checkoutToken, cartToken?, checkoutCreatedAt?, abandonedCheckoutUrl?}` with optional fields nullable and bounded; `tenant.shopId` scopes checkout identity.

## Dependencies

- `ARCH-028-SHARED-002`

## Enables

- `ARCH-028-SHARED-004`

## Acceptance Criteria

- [x] Existing v2 events parse without mutation or rewritten queue history.
- [x] Canonical parser accepts new strict version only with correct version metadata.
- [x] No URL or timestamp is required to identify or correlate an update.
- [x] Malformed context fails schema validation; producer/consumer cannot diverge on versions.
- [x] Repository-declared Shared tests/typecheck/build/export checks pass.

## Validation

Focused Shopify event schema and public subpath export tests, repository-declared Shared validation/build, `git diff --check`. Do not publish during this implementation task.

## Stop Condition

Complete defined work/acceptance/validation, fill the Completion Report, set status `review`, return to `moda_architect`, and STOP. Do not begin a dependent task.

## Implementation Notes

This is a cross-repository runtime contract, so implement once in Shared. Version the event instead of mutating strict v2. Do not invent a token-filtered Shopify API; the existing provider retrieval still uses bounded URL/time lookup context when available.

## Completion Report

### Status

Ready for Architect Review.

### Files Changed
`src/shopify/constants.ts`, `src/shopify/index.ts`, `src/shopify/v3/checkout-updated.schema.ts`, `src/shopify/v3/recovery-event.schema.ts`, `src/shopify/recovery-event.schema.ts`, and `src/shopify/recovery-event.schema.test.ts`.

### Work Completed
Added a separately versioned strict checkout.updated v3 contract. The v3 payload requires a non-empty checkout token and permits optional nullable cart token (bounded to 100 characters), ISO checkout creation time, and abandoned-checkout URL (bounded by the existing URL limit). The strict v3 event envelope carries schema version 3 and existing Shopify event metadata. Existing v2 schemas and `parseShopifyRecoveryEventV2` remain unchanged.

Added the canonical `ShopifyRecoveryEventSchema`, `ShopifyRecoveryEvent`, and parse/safe-parse functions accepting existing v2 recovery events plus v3 checkout.updated. Exported v3 constants, payload/event schemas and types, and the canonical parser from `@modainteract/moda-interact-shared/shopify`. No producer/consumer, queue, ordering-key, package-version, or publication changes were made; no local consumer contract copies were added.

### Validation Results
- Focused command `node_modules/.bin/tsx --test src/shopify/recovery-event.schema.test.ts src/shopify/v2/recovery-event.test.ts`: 25 passed, 0 failed.
- `npm run typecheck`: passed.
- `npm run build`: passed; generated `dist/shopify/index.d.ts` contains the v3 version/type/schema and canonical parser exports.
- `npm test`: 253 tests, 252 passed, 0 failed, 1 skipped. The skipped existing BullMQ telemetry test requires `TEST_REDIS_URL`.
- Runtime import from `@modainteract/moda-interact-shared/shopify` successfully parsed a v3 checkout.updated event.
- `git diff --check`: passed.
- No package publication was performed.

### Deviations
The new implementation worktree did not contain `node_modules`; validation temporarily linked the existing canonical Shared dependency tree into the implementation worktree. The temporary symlink was removed after validation; no dependency manifests or lockfiles were changed.

### Assumptions

None.

### Unresolved Issues
One existing Redis-dependent test was skipped because `TEST_REDIS_URL` was not configured. All event-contract tests and remaining Shared tests passed.

### Architectural Concerns
No architecture deviation. The strict v2 schemas/parser, Shopify queue contract and ordering helpers remain unchanged; only Shared exports were added. Producers, consumers, package version and publication state remain unchanged as required by scope.

### Attempt 1 Worktree and Launcher Evidence

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; launcher confirmed it was not derived from a previous task worktree.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-028-SHARED-003`, branch `task/ARCH-028-SHARED-003`; created for this task, not reused.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-028-SHARED-003`, branch `task/ARCH-028-SHARED-003`; created for this task, not reused.
- Parent sync: remote task branch fast-forward `not-needed`; `origin/main` incorporation `already-current`; prepared head `f2d12696c3575cc4320b8ed76c4a262bf2f3588e`.
- Implementation sync: remote task branch fast-forward `not-needed`; `origin/main` incorporation `already-current`; prepared head `a70ebf20b93f6e1250d768e57a9c08a0d92950b7`.
- Recursive implementation submodule sync and update both passed; status `ready`; no submodule entries were present.
- Attempt 1 claim commit `54e044ff0e24c4f409b1b373df2203867c36e985` was committed and pushed. Implementation changes were confined to the dedicated implementation worktree; the task report is confined to the dedicated parent worktree. No shared/default checkout or foreign task worktree was modified.

## Architect Review

### Review Status

Accepted — Attempt 1 (2026-10-11).

### Review Notes

The contract implementation conforms to the agreed strict, separately versioned Shopify checkout-update design. The existing strict v2 schema and `parseShopifyRecoveryEventV2` remain unchanged. New strict v3 `checkout.updated` payload and envelope schemas accept `checkoutToken` identity with optional nullable bounded lookup hints, and the canonical parser accepts v2 recovery events and v3 checkout updates without altering queue contracts or ordering helpers.

Verified pushed implementation commit `fbd05b232e708e551dd275e6f09bbce7d5200edd` on `kodjobaah/moda-interact-shared`, and pushed report commit `ce6592a88d6d954ca8533f8243dbb7fd3a6400ad` on `kodjobaah/moda-interact-workspace`. Each named `task/ARCH-028-SHARED-003` branch points to its reported SHA; the implementation commit changes only the six files listed in the Completion Report. The submitted worktree packet records canonical dedicated parent and implementation paths, synchronization and recursive submodule checks; physical worktrees and local cleanliness cannot be independently re-observed from the exported ZIP.

### Reviewed Files

- `src/shopify/constants.ts`
- `src/shopify/index.ts`
- `src/shopify/v3/checkout-updated.schema.ts`
- `src/shopify/v3/recovery-event.schema.ts`
- `src/shopify/recovery-event.schema.ts`
- `src/shopify/recovery-event.schema.test.ts`
- Existing v2 `checkout-updated.schema.ts` and `recovery-event.schema.ts` for compatibility
- `package.json` Shopify subpath export and the canonical SHARED-003 task report

### Validation Reviewed

The Completion Report records 25 focused passing Shopify-event tests, passing typecheck and build, clean public-subpath runtime import, and 252 passing full-suite tests (0 failures, 1 existing Redis-dependent skip with `TEST_REDIS_URL` unset). Test sources and the exported public entrypoint were inspected; these commands were not rerun in this review container because the exported ZIP excludes installed dependencies/build artefacts. `git diff --check` passed in the implementation report. GitHub commit identity, touched-file list and exact task-branch tips were independently verified.

### Architecture Conformance

Accepted. `(shopId, checkoutToken)` is the canonical identity; URL and creation time are optional lookup context. Separate v3 metadata protects strict v2 consumers; consumers must adopt the published canonical parser before the Shopify v3 producer is enabled. No package publication or producer/consumer changes occurred in SHARED-003.

### Follow-up

Promote `ARCH-028-SHARED-004` to Ready. SHARED-004 is a publication-only task: publish one approved compatible package revision and verify its clean installed Shopify exports before `ARCH-028-BACKGROUND-012` adopts the consumer-first contract. Do not begin consumer or producer integration as part of this review.
