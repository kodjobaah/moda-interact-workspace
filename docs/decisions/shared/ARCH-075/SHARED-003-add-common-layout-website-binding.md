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

Ready for Review. Source committed and pushed at `3e1a06fa44733c1c6ade6e9d259a7805a8a7a5cf`, [Shared PR83](https://github.com/kodjobaah/moda-interact-shared/pull/83). Candidate5.13.9 is packed and validated, not published. No source/main merge or live mutation by this task.

### Files Changed

- `src/recovery-template-bindings.ts` and `src/commerce/outreach/template-contracts.ts`: canonical `shop.websiteUrl` on both existing semantic surfaces; optional nullable `variables.shopWebsiteUrl` host carrier on existing outreach input.
- `src/commerce/outreach/variables.ts`: resolve that separate saved website scalar through existing binding handling; no checkout/name inference.
- `src/shop-website-url.ts`: small internal lexical HTTPS-origin guard reused by outreach input/resolver and existing wrapper renderer, no content builder or authority lookup.
- `src/commerce/presentation/wrapper-contracts.ts`, `wrapper-projection.ts`, `wrapper-render.ts`: new existing-token key and validated value; legacy parser/renderer/digest conventions unchanged.
- `src/commerce/presentation/common-recovery-layout.ts` and public index: strict `CommonRecoveryLayoutReference` / `readCommonRecoveryLayoutReference(raw,sha256)` reusing existing immutable prepared-wrapper parser/hash.
- `src/shop-website-url.test.ts`, `src/commerce/presentation/common-recovery-layout.test.ts`, `src/recovery-template-bindings.test.ts`: focused positive, legacy, missing/unsafe, binding, exact-reference/hash and common-boundary coverage.
- `scripts/validate-recovery-multipart.mjs`, package script alias and README: extend exact installed artifact public Node/types/browser checks for website/common-reference behavior and document source authority/compatibility.
- `package.json`, `package-lock.json`: candidate5.13.9 metadata only; no dependency changes.

### Work Completed

The website remains a separate semantic value, never overloaded into `shop.name` or derived from checkout/model text. Host-provided values must be canonical single-line HTTPS origins, with optional root slash and no credentials/ports/non-root path/query/fragment. Missing optional carrier remains compatible with old inputs; requesting it without a value fails via existing unavailable binding/variable semantics. Both schema and resolver guard invalid values. Existing checkout conditional/button restrictions and unknown-key rejection remain intact.

The exact common reference contains schemaVersion1, bounded definitionId/localeId, lower-hex sourceHash/contentHash, canonical supported languageTag and PreparedWrapper. Its parser delegates contentHash verification to `readPreparedWrapper` using the injected existing digest convention. It requires one body response slot, no productImage, exactly one shop name and website header token, empty static footer and one checkout conditional ending with the trusted checkout variable on its own final line. The final-line guard preserves already accepted multipart footer compatibility without rendering, inferring variable content or inserting formatting. No frame/content builder, new renderer, setting/table or transport contract was introduced.

Admin's selected immutable SHARED projection remains sole common content authority. The reference parser deliberately does not prove current selection/tenant/source authority: hosts must re-read definition/locale/status/current identity and both hashes. Existing old wrapper projections/registration snapshots remain readable with original hash semantics; new consumer wiring and activation belong to Admin/Background tasks.

### Validation Results

All final checks ran against unchanged source `3e1a06fa44733c1c6ade6e9d259a7805a8a7a5cf`:

- Final focused semantic/wrapper/reference suite19/19 passed. Cases include a real frozen approved-template render using website as its own parameter while preserving shop.name, direct resolver missing/unsafe failures, optional carrier absence without added parsed fields, old output identity, strict keys/buttons, token positions/checkout restriction, canonical origins and immutable common-reference/hash/role boundaries.
- `npm test`:786 total,783 passed,3 existing declared skips,0 failures;77.91s. Existing legacy wrapper/outreach/media tests remain green.
- `npm run typecheck`:passed. `npm run build`:passed ESM and DTS (DTS35.10s).
- Exact accepted-candidate archive: `/tmp/moda-arch075-shared003-artifacts/modainteract-moda-interact-shared-5.13.9.tgz` (530089 bytes), generated from the validated exact-head build with `npm pack --ignore-scripts`.
- SHA256: `c8486e03372676760ccffed3c2e6e207d4e0e48acb07321ac5c3f9c671a28054`.
- SHA1: `f9e04f53f0d7ba96ecefcfab0101ca91dc39f2fa`.
- Integrity: `sha512-iT3WMndGmXHpnmVVX7VDia1DkfCqBTVR7F3mh9I9UgxAFpwOZ/vq7STX2Jbbp25+6VHUjXbPhp1BI9IRutbM3A==`.
- `npm run validate:common-recovery-layout -- <exact archive>`:passed installed Node ESM/public types/browser runtime+isolation for new bindings/reference and retained multipart exports. Actual installed metadata is5.13.9 and archive SHA256 matches. `npm run validate:commerce-presentation` and `npm run validate:commerce-outreach` passed existing public entrypoint/packed JS/declarations and frozen-render checks without provider I/O. Candidate receipt is `/tmp/moda-arch075-shared003-artifact-receipt.json`.
- Registry version5.13.9 availability checked before versioning (E404). No public publication attempted. Repository has no configured CI workflow; exact-head local full-suite/build/installed artifact proof is reported, not an invented CI result.
- Diff/whitespace/privacy checks pass; source tree clean. One initial readonly-array test-fixture type error was corrected by copying fixture arrays, without changing runtime or weakening assertions. No production access or cross-repository implementation edits occurred.

Prepared launcher isolation/synchronization proof from `/tmp/moda-arch075-shared003-prepare.json`:

- Canonical primary workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-SHARED-003`; implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-SHARED-003`; both branches `task/ARCH-075-SHARED-003`.
- Parent/implementation remote-task fast-forward not needed; origin/main already current for both. Implementation base `8fc7bb9981cdd1a410c4a0848b812cfb7b31533a`; pre-claim parent `0030c4eb55822d610a6ba1c53304e2d985c1b5d0`; durable claim `4f64847779d1a41e931c6c6daa997c01af641514`.
- Recursive submodule sync/update passed, no implementation submodules. Shared/default checkout was not switched/used; no prior task worktree reused or repeat claim/startup discovery. Canonical Node bootstrap used; no environment/permission workaround.
- Architect scope/coordination commits `a3da50e67` and `a899891f7` are preserved. Only this assigned parent task file is changed for review submission; Architect Review remains unchanged.

### Deviations

Necessary binding carrier/resolver and genuine shared common-reference parser were explicitly amended into this task by architect/root before source freeze. No content/frame builder or duplicate renderer was added. No CI workflow exists, so exact-head local and installed artifact proof is recorded accurately.

### Assumptions

Only a host-verified saved shop origin is supplied. Structural reference validity does not authorize a client snapshot or replace immutable active-definition/locale/status/hash re-read. SourceHash shape is checked here; actual source equality is host authority.

### Unresolved Issues

Publication belongs to SHARED-004 after architect acceptance, root source merge and explicit approval of this exact5.13.9 public artifact. Admin/Background consumers and coordinated Meta locale activation remain their tasks. No old approved template is rewritten by this additive source change.

### Architectural Concerns

Keep the selected Admin immutable SHARED projection as content authority; do not create a second formatting source or infer website/tenant authority from model/body/checkout data. Host implementation must preserve authored family body/offer/opt-out content and original current-source fences.

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
