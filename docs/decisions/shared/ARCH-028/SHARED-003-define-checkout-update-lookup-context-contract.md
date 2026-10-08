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
status: ready
priority: 28
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-028-SHARED-002
enables:
  - ARCH-028-SHARED-004
created: 2026-10-08
updated: 2026-10-08
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

- [ ] `shopId + checkoutToken` remains canonical application business identity; URL is optional Shopify lookup context only.
- [ ] V2 strict schema is unchanged; v2 queue events still parse with canonical new parser.
- [ ] V3 checkout.updated has distinct version and bounded optional context, while other v2 event variants remain valid.
- [ ] Other existing Shopify event schemas, queue names and deterministic IDs are unchanged.
- [ ] Cross-repository consumers use the published Shared exports rather than local copies.

## Work Items

- [ ] Define/export strict v3 checkout.updated payload/event and version metadata.
- [ ] Add canonical parser/type for v2 recovery events plus v3 checkout.updated.
- [ ] Add tests for v2/v3, absent context, bad URL/datetime, unknown fields and existing event regressions.
- [ ] Validate public `@modainteract/moda-interact-shared/shopify` export declarations and package build.

## Interfaces / Contracts

Owner `moda-interact-shared`; package export `@modainteract/moda-interact-shared/shopify`; producers `moda-interact`; consumers `moda-interact-background`. Runtime validation via canonical v2/v3 event parser. Existing v2 checkout.updated stays strict and unchanged. New v3 payload: `{checkoutToken, cartToken?, checkoutCreatedAt?, abandonedCheckoutUrl?}` with optional fields nullable and bounded; `tenant.shopId` scopes checkout identity.

## Dependencies

- `ARCH-028-SHARED-002`

## Enables

- `ARCH-028-SHARED-004`

## Acceptance Criteria

- [ ] Existing v2 events parse without mutation or rewritten queue history.
- [ ] Canonical parser accepts new strict version only with correct version metadata.
- [ ] No URL or timestamp is required to identify or correlate an update.
- [ ] Malformed context fails schema validation; producer/consumer cannot diverge on versions.
- [ ] Repository-declared Shared tests/typecheck/build/export checks pass.

## Validation

Focused Shopify event schema and public subpath export tests, repository-declared Shared validation/build, `git diff --check`. Do not publish during this implementation task.

## Stop Condition

Complete defined work/acceptance/validation, fill the Completion Report, set status `review`, return to `moda_architect`, and STOP. Do not begin a dependent task.

## Implementation Notes

This is a cross-repository runtime contract, so implement once in Shared. Version the event instead of mutating strict v2. Do not invent a token-filtered Shopify API; the existing provider retrieval still uses bounded URL/time lookup context when available.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

Not Started.

### Validation Results

Not Run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
