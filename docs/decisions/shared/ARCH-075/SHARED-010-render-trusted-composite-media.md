---
id: ARCH-075-SHARED-010
architecture_id: ARCH-075
title: Render and prepare trusted composite recovery media
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-075-SHARED-009
enables: 
  - ARCH-075-SHARED-011
created: 2026-11-13
updated: 2026-11-13
---

# Render and prepare trusted composite recovery media

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; moda_architect.

## Objective

Produce a deterministic verified composite derivative from separately trusted logo/header and optional verified product through existing bounded media I/O.

## Context

User approved one bubble, original assets separate: small contained logo beside readable full shopname/website, divider then optional product; answer/checkout remain real caption, absent from bitmap. Node mechanics already owned in Shared. Native unchanged. Contract009 must be accepted/integrated.

## Scope

Existing Shared Node media primitives plus bounded composite renderer/preparer, licensed deterministic font assets/package inclusion, actual offline output/Alpine validation and direct tests.

## Out of Scope

Host database/tenant policy/config reads, live/provider sends, native template changes, public publication, consumer implementation, arbitrary URL/model markup, new generic network/R2 library or pre-render cache service.

## Requirements

- Implement accepted009 distinct composite contract. Reuse safe pinned HTTPS fetcher, guarded immutable R2 writer/probe/hash verification and abort/transport-close mechanics. Only explicit trusted source descriptors/actual validated sourcebytes; no arbitrary model URL. Original assets untouched.
- Version/fix geometry, colors, encoder settings and font identity. Contain-not-crop logo/banner in modest header, full readable canonical shoplabels/name/website wrap, divider, optional product below preserving ratio. Optional product produces header-only composite, never empty/duplicated answer. No unauthorized translations or injected branding prose.
- Bundle explicit licensed font assets and shaping settings; do not assume Alpine fonts. Escape markup, bound text/pixels/input/output/dimensions and detect unsupported glyph/overflow rather than tofu/clipped text. Missing font/unsupportedheader/transform failure returns safe omission so host sends complete TEXT. No truncation. Record supported coverage and actual multilingual boundary tests.
- Exact encoded output contentSHA/MIME/length/dimensions verified; separate composite key binds tenant/render identity/outputSHA, exact publicorigin/key URL, both sourcehashes/commonheader/layout/font hashes. Timestamps/answer/customer/checkout tokens absent from bitmap/cache key. Existing immutable HEAD deduplicates writes after render; don't claim pre-render caching unless actually implemented/tested.
- Whole preparation bounded under existing5s optional media budget and original remaining turn deadline minus safety margin, no additional fresh5s for every stage. Abort propagation and bounded source/R2/probe, cleanup/cancel safe. No provider side effects.
- Preserve old1125x600 verification defaults; new composite dimensions explicit, not forged through old verifier. No old output/regression changes.
- Return actual deterministic output artifact for root visual review using private supplied Eugene logo/product inputs; do not commit those shopassets, customer information or privateURLs. Actual node22-alpine/nohostfont test must prove rendered pixels/text/header/product and readable geometry (not constants-only).

### V1 geometry and offline review inputs

Architect accepted proposed V1 geometry: width1125, branded header height300, contained logo maximum180×180 at48,60, canonical text beside at264,24 within813×252, reserved lower spacing before the product. Render the FULL authored canonical header literally once, including its divider text; do NOT draw a second decorative divider or infer/strip a divider by regex. No new structured partition is needed. Product optional: preserved1125×600 contain area below y300 gives1125×900; no-product gives1125×300. No crop or distortion of approved temporary banner/product. Final measured artifact is reviewed by root before acceptance, not inferred from constants.

Private operator QA inputs exist under primary local-backups/arch075-live-20261113/composite-qa/{logo.jpg,product.jpg}; original hashes supplied securely by root. Use offline only, never commit those assets or URLs. Canonical full header includes authored translated labels; do not repeat header/divider in caption or invent translations. Unsupported glyph/fit returns safe omission.

### Read-only runtime/font preflight

Actual isolated node22-alpine (Node22.23.5, Sharp0.35.4, libvips8.18.6, Pango1.58.2) has no installed fonts but supports explicit fontfile. Small official candidate: Google/fonts commit7dc16b7de42db624b902f2292b68ed9e489e5053/ofl/poppins/Poppins-Regular.ttf,160316 bytes, SHA2567e65201e9b79159e2300267cc885e16c8dcef2424cdfa09a29bfb0980a94a7ba; OFL.txt4385 bytes, SHA2566be04893d770899a015649c7aa3b582f871b272f8747a92b78b17c3e5c8b2573, copyright2020PoppinsProjectAuthors/SIL OFL1.1. Retain license/provenance.

Use explicit generated glyph coverage from pinned font (candidate471scalars), bounded supported repertoire and no normalization. Missing/unsupported glyphs can silently produce PNG, so PNG success is not coverage evidence. English Eugene/Latin accents/common punctuation supported; the actual canonical U+2500 divider MUST be covered by the chosen font too (Poppins coverage was checked and U+2500 is ABSENT; Poppins is rejected for this canonical header. Select a pinned licensed alternative covering U+2500, without replacing or stripping authored divider). unsupported CJK/Arabic/emoji/decomposed marks require fullTEXT fallback. Fixed fontfile/family/size/DPI, escaped Pango markup, measured height with no autofit/shrink. Current packagefiles omit fontassets and tsupclean erasesdist: package font/license/coverage explicitly and verify actual packed Node path after bundling. No new font manager/dependency needed for this bounded supported set. Renderer must still prove actual readable pixels and root visual artifact; preflight only establishes runtime availability.

### Selected deterministic font (preflight complete)

Select official DejaVuSans2.37, not Poppins: archive https://github.com/dejavu-fonts/dejavu-fonts/releases/download/version_2_37/dejavu-sans-ttf-2.37.zip SHA2565c6e497a2f36552cb5ffb112c413a6af39c0f3c47653662b90b4fa6499822fd7; TTF757076 bytes SHA2567da195a74c55bef988d0d48f9508bd5d849425c1770dba5d7bfc6ce9ed848954. Retain complete8816-byte LICENSE SHA2567a083b136e64d064794c3419751e5c7dd10d2f64c108fe5ba161eae5e5958a93 (BitstreamVera, DejaVu changes public-domain, imported Arev terms; NOT OFL). Derive explicit coverage from pinned font (5918scalars), reject unsupported instead of substitution.

Actual private canonical English header119UTF8bytes SHA2567e2d7c8d8ab536a6addcb2aa8061bf4ba8ddd72a391fb0f8a72e288d05798aeb has every scalar supported includingU2500. In real fontless Node22Alpine Sharp0.35.4, font DejaVu Sans28/dpi72/rgba:true/width813/no-trim escapedtext produced537×153 pixels (fits180 height);32pt620×176 fits tightly;36pt exceeds180. Root subsequently required larger mobile-readable text: measure40/44/48 in813×252 (textTop24, logoTop60), choose largest fit without shrinking. The earlier28 result is availability evidence, not final font size. This is preflight text-only, not full compositor acceptance; full bitmap/private root review still mandatory. Local operator copies are in temporary moda-font-preflight directory; renderer owner may copy only verified font/license into its own task source, not the private header/shop assets.

## Work Items

- [ ] Implement safe deterministic compositor/preparation with font/license provenance.
- [ ] Verify bound/cache/output/optionalproduct/fallback and actual Alpine rendering.
- [ ] Return private actualQA image and measured receipt to root; run required checks and publish exact source/report.

## Interfaces / Contracts

Accepted SHARED009 browser contract; existing commerce/presentation/node safe fetch/R2/probe/deadline primitives. Node-only renderer imports must never leak browser exports.

## Dependencies

ARCH-075-SHARED-009 Complete/Accepted and integrated before preparation.

## Enables

ARCH-075-SHARED-011 release gate; Background consumer only after accepted package contract and proper publication gate.

## Acceptance Criteria

- [ ] Actual bitmap matches approved order and retains full canonical header; no customer/checkout/answer pixels.
- [ ] Optional product, original inputs, font/markup/glyph/overflow and bounded missing/network/timeout cases safe.
- [ ] Trusted dual provenance/output hashes/public object verification and old defaults preserved.
- [ ] Real Alpine output and root visual review evidence, declared checks and clean mirrored source/report.

## Validation

- [ ] Deterministic pixels/outputhash/sourcechange/textchange/fonthash/cache identity tests; malformed/foreign/unsafe input, timeouts/probe/conflict/overflow/glyph cases.
- [ ] Actual no-hostfont node22-alpine renderer and offline private Eugene output for root review; no live send.
- [ ] Declared relevant/fulltests/type/build/available scopedlint, packed asset/license/browser separation/privacy checks.

## Stop Condition

Publish exact mirrored source/report, set review and return architect. No main merge, live mutation, enabled consumer or npm publication without release-specific authorization.

## Implementation Notes

Normal launcher dedicated sibling worktrees. You are not alone; preserve others and primary. Original approved mock is schematic only: small contained logo alongside shop details, divider, product beneath. Root owns operational/visual review and integration; no live sends.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

### Deviations

None

### Assumptions

Root owns final integration and live authorization.

### Unresolved Issues

Publication and consumer/live proof remain gated.

### Architectural Concerns

Return gaps before widening.

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

No architectural/live completion claim.
