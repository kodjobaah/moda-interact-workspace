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
status: review
priority: 10
executor: codex
claimed_at: 2026-11-13T02:01:15Z
attempt: 2
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

- [x] Complete assigned bounded capability only.
- [x] Prove compatibility and meaningful negative/failure behavior.
- [x] Submit mirrored branch/report and stop.

## Interfaces / Contracts

Common content authority: selected immutable Admin SHARED wrapper revision and locale projection. Shared owns canonical semantic key/wrapper validation; Admin owns authoring/compiler/reference/activation; Background owns tenant-derived values, frozen rendering, sending and current fences. Existing template registration hashes remain authority for provider components.

## Dependencies

ARCH-075-SHARED-002

## Enables

Only explicitly promoted dependent tasks after acceptance.

## Acceptance Criteria

- [x] One common content source is used without duplicated formatting or unauthorized semantic widening.
- [x] Old stored projections/registrations remain readable and immutable; new fields do not grant tenant/provider authority.
- [x] Assigned validation and isolated mirrored synchronization evidence are complete.

## Validation

- [x] Focused semantic key/wrapper projection positive/unknown-key/legacy/digest tests.
- [x] Full declared package tests, typecheck, ESM/DTS build and exact packed installed JS/types/browser exports.
- [x] Immutable artifact hashes and privacy/diff checks.

## Stop Condition

After required work and validation, submit review and STOP. No enabled-task execution, merge, live mutation or unapproved public release.

## Implementation Notes

You are not alone; preserve other changes. Canonical prepared packet is startup/isolation authority. Report actual cross-owner gaps rather than inventing a setting/schema or weakening strict validation.

## Completion Report

### Status

Ready for Review, corrected attempt2. Source committed and pushed at `b576c5ef33df88da1e010f9ceeb76999a3285bee`, [Shared PR83](https://github.com/kodjobaah/moda-interact-shared/pull/83). Candidate5.13.9 is rebuilt/packed and fully validated after Changes Requested, not published. Previous source3e1a06fa and artifact SHA256c8486e03372676760ccffed3c2e6e207d4e0e48acb07321ac5c3f9c671a28054 are superseded and are not release candidates.

### Files Changed

- Canonical template surfaces `src/recovery-template-bindings.ts`, `src/commerce/outreach/template-contracts.ts`: add `shop.websiteUrl` and optional nullable outreach `variables.shopWebsiteUrl` carrier; no existing button authority widened.
- `src/commerce/outreach/variables.ts`, `src/shop-website-url.ts`, wrapper contracts/projection/render: resolve the separate host-saved lexical HTTPS origin through existing renderer/token semantics, preserving old values/inputs/digests and missing-value refusal.
- `src/commerce/presentation/common-recovery-layout.ts` and public index: exact typed snapshot parser reusing existing prepared-wrapper/hash conventions. Attempt2 adds explicit common-only header and conditional token allowlists.
- Website/bindings/common-layout tests: positive/unknown/unsafe/missing/legacy/immutable-hash checks; attempt2 adds valid-hash prohibited-token injections and generic wrapper compatibility assertions.
- `scripts/validate-recovery-multipart.mjs`, package alias and README: exact installed artifact Node/public-types/browser proof and content-authority documentation. Attempt2 adds installed Node/browser injection rejection checks.
- `package.json` and lock: candidate5.13.9 only, no dependency changes. No frame builder, new renderer, table/setting, provider/state transport or consumer implementation.

### Work Completed

The canonical website remains separate from shop.name and is not inferred from checkout/model text. Both existing semantic surfaces and wrapper tokens support it. Optional carrier absence leaves legacy parsing unchanged; selected unavailable values fail normally. Existing origin guard rejects credentials, explicit ports, non-root paths/query/fragments and multi-line/noncanonical data. Website values are host-supplied tenant-verified origins; Shared performs no database/environment/source authorization.

The exact reference remains schemaVersion1, bounded definitionId/localeId, sourceHash/contentHash, supported canonical languageTag and PreparedWrapper. It delegates contentHash integrity to existing `readPreparedWrapper`/injected SHA256(stableJson(prepared)). Common body is exactly one response.body slot, productImage absent, static footer empty. HEADER now permits only literal text and shop.name/shop.websiteUrl once each; the sole checkout conditional permits only literal text and checkout.url once as its own final line. No content/formatting is generated. Generic wrappers retain their prior broader variables.

Admin's selected immutable SHARED revision remains content authority; hosts must re-read exact current definition/locale/status/hash identity. Parsed client snapshots never grant tenant/source/provider authority. Old projections/registrations remain immutable/readable; downstream consumers and coordinated activation remain their owning tasks.

#### Changes Requested disposition

1. **Implemented** — explicit token allowlists in `common-recovery-layout.ts`; no change to generic `readPreparedWrapper` or its broader variable set.
2. **Implemented** — valid-hash customer.firstName, brand name, logo/square/cover URL/alt/dimension header and conditional injection negatives in `common-recovery-layout.test.ts`, plus non-common name/site conditional negatives. Every existing other-variable fixture is still accepted by the generic wrapper parser, proving scoped tightening. Existing custom literal text/common positive cases remain green.
3. **Implemented** — corrected exact-head full package/types/ESM/DTS/installed artifact/browser checks below. Installed smoke rejects independently rehashed customer/logo injections while preserving generic parsing. No publication or follow-on task executed.

### Validation Results

- Meaningful original-code regression on source3e1a06fa:5 passed,1 failed; injected customer.firstName with valid contentHash incorrectly returned common-reference ok. Correction changed runtime as requested, not merely test expectations.
- Corrected focused common-reference + website suite14/14 passed; full exact-head `npm test`:787 total,784 passed,3 existing declared skips,0 failures,73.37s. All legacy wrapper/outreach/media tests remain green.
- `npm run typecheck`:passed. `npm run build`:ESM and DTS passed (DTS50.14s). All final checks ran with source `b576c5ef33df88da1e010f9ceeb76999a3285bee` unchanged and clean.
- Fresh same-version candidate path: `/tmp/moda-arch075-shared003-attempt2-artifacts/modainteract-moda-interact-shared-5.13.9.tgz`; separate from the preserved superseded archive. Packed from corrected exact-head validated build with `npm pack --ignore-scripts`.
- SHA256: `79731a5e54a1a9f5d1a0fdeb84cc4db1d2968c416cfa9543de52a813088e4043`.
- SHA1: `27a8a49cc80992e109f33d55ea0cfba5aa8ee8b3`.
- Integrity: `sha512-bLXw6dofV8bq/TJzE8STzk9/jT0WSHM5R01x4d1Ki+xVQ+VAfVg63+hzewXas5KYjUMtBOMxBX60gtB4U/uVfg==`.
- `npm run validate:common-recovery-layout -- <exact corrected archive>`:passed installed Node ESM/public TypeScript/browser isolation and runtime, including valid-hash prohibited-token rejection and retained multipart/website APIs. Installed metadata is5.13.9 and byte hash matches. `npm run validate:commerce-presentation` and `npm run validate:commerce-outreach` passed existing public JS/declaration/frozen-render checks without provider I/O.
- Current receipt: `/tmp/moda-arch075-shared003-attempt2-artifact-receipt.json`. The old receipt explicitly records superseded/publication-ineligible state; original archive bytes were preserved, not overwritten.
- Candidate5.13.9 was unallocated (registryE404) before initial versioning. No publication attempted in either source attempt; release task must recheck availability and approval for the actual accepted artifact. No CI workflow is configured in this repository; no absent CI is claimed green.
- Diff/whitespace/privacy and clean-tree checks pass. No source schema/type or assertion weakening, production access, cross-owner edit, source/main merge or provider I/O.

Canonical attempt2 preparation proof from `/tmp/moda-arch075-shared003-attempt2-prepare.json`:

- Primary workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; dedicated parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-SHARED-003`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-SHARED-003`; both `task/ARCH-075-SHARED-003`.
- Same correct task worktrees reused; no other task/shared/default checkout used or switched. Parent and implementation remote-task fast-forward not needed; parent origin/main incorporated yes, implementation already current. Parent synchronized pre-claim head `f71460da0cf11379eeacc6826ed8bb2e89da43fb`; implementation pre-attempt head3e1a06fa; durable attempt2 claim `a64d594f226c410a031f74040c1935e50228a9df`.
- Recursive implementation submodule sync/update passed; no implementation submodules. No repeat claim/startup preparation or environment/permission workaround. Canonical Node bootstrap retained.
- Changes Requested47eec76e2 and architect coordination/main merge are preserved; only this assigned task record changed for report submission. Latest Architect Review is unchanged by repository owner.

### Deviations

None for correction. Initial source work's approved carrier/resolver/reference scope remains intact. Attempt2 implements every requested correction within the same mirrored branches and candidate version; no unauthorized new builder or consumer work.

### Assumptions

Hosts enforce selected immutable SHARED definition/locale/status/source/content equality and supply tenant-verified website/checkout values. The snapshot parser validates structure/integrity, not current authority.

### Unresolved Issues

None for assigned source correction. Formal architect acceptance, root source merge and explicit public artifact release gate precede SHARED-004; Admin/Background consumption and Meta activation remain downstream. Superseded initial archive must not be published.

### Architectural Concerns

Common-reference variables must remain intentionally narrower than generic wrappers so Meta projection never invents mappings. Keep the single Admin-owned content source and original current-source/tenant fences; do not substitute parsed snapshots or hardcoded framing.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Actual source3e1a06fa review found one missing common-reference invariant: required name/site presence does not exclude other valid wrapper variables. Header/conditional can therefore contain values outside the approved common Meta-projectable frame. Correct within this same source task, preserving generic legacy wrapper behavior.

### Reviewed Files

common-recovery-layout.ts and existing wrapper parser; website binding/resolver source and focused tests; immutable artifact/report evidence.

### Validation Reviewed

Initial exact head783 passed/3 skips, types/build/installed proof recorded but not accepted as final because the following correction changes runtime. Existing work/isolation evidence remains valid; next claim increments preserved attempt once.

### Architecture Conformance

Correction required: common reference HEADER permits only text and shop.name/shop.websiteUrl, each exactly once; checkout conditional permits only text and checkout.url exactly once on its own final line. Body exactly response slot, static footer empty, no productImage and hash checks remain unchanged. Generic prepared wrappers may still support their existing broader variable set.

### Follow-up

1. Add explicit token allowlists to the new common-reference parser.
2. Add valid-hash negative fixtures inserting customer.firstName and logo/other variables in header/conditional; existing common custom-text positives and generic wrapper compatibility remain green.
3. Run required corrected exact-head source checks/build/installed artifact, submit revised report and immutable5.13.9 hashes. No publication or follow-on work. Reclaim via canonical launcher, no alternate checkout.
