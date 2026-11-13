---
id: ARCH-075-SHARED-003
architecture_id: ARCH-075
title: Add canonical website binding for common recovery layout
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-11-13T01:33:50Z
attempt: 1
depends_on:
  - ARCH-075-SHARED-002
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Add canonical website binding for common recovery layout

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Add canonical website binding for common recovery layout.

## Context

The user explicitly requires all Meta templates, AI replies and HUMAN messages to share one shop header and checkout footer, with product images separate. Existing Admin-owned SHARED wrapper definition/slot is the common immutable content authority; family-specific body/offer/opt-out content stays intact. No duplicate hardcoded frame builders.

## Scope

Add shop.websiteUrl to BOTH existing canonical recovery-template semantic key surfaces (recovery-template-bindings and commerce/outreach template contracts), wrapper variables/parser, and additive optional outreach variables.shopWebsiteUrl/resolver plumbing; public exports/types, compatibility tests and candidate5.13.9 exact artifact. Reuse existing prepared wrapper token contracts/rendering, no new frame/content builder.

## Out of Scope

Other repositories, new database tables/settings, provider permissions, live registrations/activation, source merges, unapproved publication, changing billing/cap semantics, arbitrary source refactors, automatic mutation of approved templates. Background engine001 remains on published5.13.8 and producer-disabled.

## Requirements

Optional outreach carrier is a host-supplied verified single-line HTTPS origin: no credentials, explicit port, query, fragment or non-root path. Absent carrier remains compatible; a requested unavailable website fails through existing resolution semantics. Do not accept the key without making its existing resolver surface functional. The website is a separate semantic value, never overload shop.name or insert multi-line arbitrary text into one Meta parameter. Host supplies verified saved shop origin; Shared does not read environment/database or derive authorization. Existing old projections, unknown-key rejection and checkout conditional restrictions stay intact. New website token may appear wherever the corresponding shop.name text token is valid, subject to existing family-specific Admin rules. No new template-part transport contract. Build exact immutable5.13.9 only if available; no publication in this task.

### Frozen common reference contract

Also own the actual Admin→Background reference contract in this same candidate: exact `{schemaVersion:1,definitionId,sourceHash,localeId,languageTag,contentHash,prepared:PreparedWrapper}`. Export its type and strict browser-safe parser. Reuse existing `readPreparedWrapper` with injected `PresentationDigest`; contentHash remains SHA256(stableJson(prepared)), never a new convention or Node dependency. Bound IDs, validate lower-hex SHA256 hashes and supported canonical language, reject unknown fields/tampering.

Common prepared projection: MODA_CONVERSATION_WRAPPER, body exactly the response.body slot, no productImage, common header identifies shop.name and shop.websiteUrl once, static footer empty, one checkout.available conditional carrying trusted checkout.url once at the end. No new content/frame builder. Return actual existing parser incompatibility instead of weakening legacy rules. Host re-reads exact immutable SHARED definition+locale/status/hash and verifies selected/current identity; client-supplied reference alone is not authority. Admin embeds it in new immutable Meta authoring JSON; Background consumes the same reference. Preserve existing old wrapper/Meta contracts without this optional new reference.

## Work Items

- [ ] Complete assigned bounded capability only.
- [ ] Prove compatibility and meaningful negative/failure behavior.
- [ ] Submit mirrored branch/report and stop.

## Interfaces / Contracts

Common content authority: selected immutable Admin SHARED wrapper revision and locale projection. Shared owns canonical semantic key/wrapper validation; Admin owns authoring/compiler/reference/activation; Background owns tenant-derived values, frozen rendering, sending and current fences. Existing template registration hashes remain authority for provider components.

## Dependencies

ARCH-075-SHARED-002

## Enables

Only explicitly promoted dependent tasks after acceptance.

## Acceptance Criteria

- [ ] One common content source is used without duplicated formatting or unauthorized semantic widening.
- [ ] Old stored projections/registrations remain readable and immutable; new fields do not grant tenant/provider authority.
- [ ] Assigned validation and isolated mirrored synchronization evidence are complete.

## Validation

- [ ] Focused semantic key/wrapper projection positive/unknown-key/legacy/digest tests.
- [ ] Full declared package tests, typecheck, ESM/DTS build and exact packed installed JS/types/browser exports.
- [ ] Immutable artifact hashes and privacy/diff checks.

## Stop Condition

After required work and validation, submit review and STOP. No enabled-task execution, merge, live mutation or unapproved public release.

## Implementation Notes

You are not alone; preserve other changes. Canonical prepared packet is startup/isolation authority. Report actual cross-owner gaps rather than inventing a setting/schema or weakening strict validation.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Pending

### Deviations

None

### Assumptions

None beyond approved contracts.

### Unresolved Issues

None currently; return concrete gaps.

### Architectural Concerns

Preserve one common content authority and immutable prior registrations.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual source review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
