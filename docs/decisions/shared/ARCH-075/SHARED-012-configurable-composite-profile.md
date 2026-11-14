---
id: ARCH-075-SHARED-012
architecture_id: ARCH-075
title: Render trusted composite images from bounded runtime profiles
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
claimed_at: 2026-11-14T01:23:21Z
attempt: 1
depends_on:
  - ARCH-075-SHARED-011
enables:
  - ARCH-075-SHARED-013
  - ARCH-075-ADMIN-009
created: 2026-11-14
updated: 2026-11-14
---

# Render trusted composite images from bounded runtime profiles

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; moda_architect.

## Objective

Accept a trusted immutable bounded layout profile so supported visual-value changes require configuration revisions rather than Shared publication.

## Context

User explicitly requests the architecture correction before merge/deployment. Published5.13.11 remains immutable. Existing approved visual order is logo/shop details/literal divider, optional product, actual answer+one checkout footer caption. The existing fixed-V1 implementation is preserved for replay, not silently rewritten.

## Scope

Additive browser-safe profile/provenance/output/plan schemas and hash helpers; Node configurable renderer/preparer; opt-in carrier reader delegating all legacy V1 branches exactly. Existing reusable rendering/safe fetch/R2/probe mechanics and bounded image proof remain owned here. No publication in this task.

## Out of Scope

Admin UI/database/environment selection, arbitrary CSS/drawlists/scripts/font URLs, native Meta template changes, live sends/configuration, consumer implementation or publication.

## Requirements

- Shared receives explicit trusted profile snapshot; it never chooses active policy, reads DB/env or owns visual defaults. Admin owns runtime values/revision; Background owns selection/freeze/final authority.
- Profile schemaVersion1 with fixed supported fontId DEJAVU_SANS_2_37 and named fields: canvasWidth,headerOnlyHeight,withProductHeight; logoLeft,logoTop,logoWidth,logoHeight; textLeft,textTop,textWidth,textHeight,fontSize,textLineSpacingPt; productLeft,productTop,productWidth,productHeight. No arbitrary objects of operations.
- Technical bounds: canvasWidth640..1600, headerOnlyHeight160..640, withProductHeight400..1840, logo width/height32..320, textWidth128..1600,textHeight32..640, productWidth128..1600,productHeight128..1200,fontSize24..96. Integers only. Coordinates nonnegative and <=1840; logo/text rectangles fit header; textLineSpacingPt0 or fontSize..2*fontSize; productTop>=headerOnlyHeight and product rectangle fits product canvas; withProductHeight>headerOnlyHeight; both outputs<=2000000pixels. Do NOT require logo-left-of-text or any visual placement order; supported bounded profiles may put logo above/centered with text below. Nonoverlap/readability belongs to owning Admin policy where appropriate. These are safety bounds, not visual defaults. Output dimensions derive from supplied profile and optional product, never fixed1125/300/900 literals in the new contract.
- Preserve literal header incl authored divider exactly once, contained uncropped original logo/product, fixed escaped text/fixedDPI72/white/JPEG/leftalignment/no-autofit semantics. Unsupported glyph/overflow/deadline returns existing typed fallback outcome; no silent truncation/replacement.
- Add explicit opt-in V2 provenance/plan/prepared output with full validated profile snapshot+canonical digest and source/runtime/font/output/caption/logical-body proofs. Separate content-addressed v2 namespace. Old V1 schemas/parsers/digests/render outputs remain unchanged; new reader delegates old branches byte-for-byte; old .11 rejects V2 safely.
- Reuse existing immutable upload/probe/AbortSignal/one original media deadline. No duplicate generic crypto/fetch/R2 mechanism. Runtime/font identity binds profile and actual library environment, no cross-platform byte-identity claim. Preserve old manifest/V1 hash computation; V2 resource identity covers the same bundled font/license/cmap without embedded size/geometry, separately bound to the full profile digest.
- Default-looking profile fixture is consumer-owned test input reproducing accepted visual geometry. Prove two materially different valid profiles (left logo, then top/centered logo with text below plus different font size/spacing/product gap) render correctly through the SAME installed package WITHOUT changing package code, and immutable profile tamper cannot pass trusted validation.
- No secrets/shop assets/customer URLs in public fixtures/package. Root alone merges/publishes/live tests.

### User-authoritative validation boundary — 2026-11-14

User explicitly prohibits Shared Zod business validation. New V2 Zod schemas parse structural wire data only: types, required/exact keys and supported contract versions. Do NOT put operational min/max policy, defaults, active/current revision, eligibility or layout preferences in Zod refinements. Published .11 V1 remains unchanged for compatibility.

Implement finite/integer/resource allocation limits, pixel budget and rectangle containment as explicit named pure rendering-safety functions, invoked before any decode/allocation/network work and reusable by owners. Safety is bounded execution/memory and valid image geometry, not a disguised business range or placement preference. Admin owns operational authoring ranges/defaults/nonoverlap/readability; Background owns persisted selection/eligibility/current revision. Separate these classifications explicitly in report/tests. Independent source/provenance/caption/output integrity checks remain explicit trusted parser functions; wire shape does not grant authorization. Return exact helper API and classification to architect before acceptance. Prior numeric intervals in this definition are intended Admin operational field ranges, not Shared schema rules; Shared retains only justified technical ceilings/positive geometry/finite checks.

### User-authoritative saved-template ownership correction

The saved common SHARED template is the sole layout authority. Independent PlatformConfiguration layout policy is superseded and MUST NOT be introduced. Add the smallest optional profile-bearing prepared/common-reference extension needed by Admin009 and BG014: `compositeProfile` plus canonical `compositeProfileSha256` in immutable prepared common layout; Admin source AST owns the profile and deterministic compilation copies/hash-binds it. Existing source/prepared hashes and selected definition/locale/common reference bind these exact bytes. Absent fields preserve legacy prepared bytes/hashes/read results; old frozen receipts remain untouched. New readers validate optional fields structurally plus explicit safety/digest binding, never infer profile from a second active policy/default. Expose one agreed typed prepared/reference API through existing presentation exports, no parallel layout registry/table. Translations must preserve profile metadata unchanged; hosts enforce source/locale/current-reference authority. Existing profile-generic renderer remains; no environment/DB policy logic in Shared. Reader-first rollout must account old readers rejecting new optional fields.

### V2 caption policy boundary

Root explicitly confirms: mandatory checkout URL/checkout-footer-last is application policy, not new Shared V2 validation. Shared V2 verifies exact host-supplied caption/logical parts and cryptographic identity plus actual Meta technical caption limits; it must not impose checkout placement/preferences on otherwise safely bound parts. Background owns canonical footer decomposition/required trusted checkout behavior. Add a safe alternate supplied-parts acceptance vector in Shared and application rejection vector in BG. Published .11 V1 semantics remain exact. This supersedes inherited V1 placement requirements for V2 only.

### User-authoritative current-only composite cleanup

User explicitly removes obsolete template compatibility as an objective. Root's read-only production inventory2026-11-14T02:12:15Z found zero RECOVERY_COMPOSITE outbound presentations and six delivery parts all READ/no future deadline; fixed .11 composite writer was never merged/deployed/enabled. Remove obsolete fixed composite V1 schemas/renderers/exports/carrier decoder branches and V1-preservation tests from NEW source. Public already published .11 artifact remains immutable. Preserve established non-composite TEXT/BRAND_IMAGE/IMAGE and generic multipart/status/repair functionality; do not broaden cleanup to unrelated historical message systems. Current executable composite format is only saved-template-bound profile format. Old template rows/audit/history are retained as non-executing records; applications require current-profile templates and root coordinates replacement before deployment/activation. No record deletion/live migration in this task. This explicitly supersedes previous V1-composite compatibility requirements; preserve source checkpoints/backups rather than adapters. Tests prove old fixed-composite input is rejected, current profile integrity/safety/two-layout behavior and established non-composite behavior remain valid.

## Work Items

- [x] Add current profile/provenance/parser/carrier APIs, reject obsolete fixed composites and preserve established non-composite behavior.
- [x] Add parameter-driven Node renderer/preparer using existing mechanics.
- [x] Validate two profile revisions, actual packed runtime/fontless Alpine output and safety failures.
- [x] Push mirrored implementation/report and stop for review.

## Interfaces / Contracts

New additive V2 APIs under existing commerce/presentation and Node subpaths. Profile snapshot/hash must be independently supplied by host authority, not self-attested by stored plan. Existing .11 APIs remain unchanged. Document exact exports for Admin009 and BG014 correction before consumers execute.

## Dependencies

ARCH-075-SHARED-011 Complete and integrated before launcher execution.

## Enables

Shared013 release-only preparation/publication; Admin009 bounded existing-policy editor; BG014 next-attempt adoption after accepted contract. Public release requires separate explicit exact-archive approval.

## Acceptance Criteria

- [x] Runtime profile changes within technical safety alter rendering without Shared code/version changes.
- [x] Obsolete fixed composite format is rejected; current trusted source/profile/output/caption binding fails closed; established non-composite behavior remains intact (user-authoritative cleanup supersedes fixed replay compatibility).
- [x] Actual renderer respects approved semantic order, no answer/checkout pixels and typed omission for complete host text fallback.
- [x] Required checks and canonical isolation evidence recorded; no publication/live mutation.

## Validation

- [x] Focused explicit safety/dimensions/hash/tamper/current-only/non-composite/transport vectors including left and top/centered arrangements.
- [x] Actual two-profile rendering including bundled font/overflow/timeout/R2/probe; packed fontless Alpine and browser-safe imports.
- [x] Declared full tests/type/build and package asset/secret/diff checks appropriate to changed code; no invented lint script.

## Stop Condition

After required scope/checks, push both task branches, set review, return Completion Report and STOP. No enabled-task work/publication/main merge.

## Implementation Notes

Normal launcher dedicated sibling worktrees. You are not alone; preserve all others. Keep reusable mechanics in Shared and product/active-policy authority in owners. Return missing contract gaps before widening.

## Completion Report

### Status

Ready for Review. Required source/package/runtime checks and root actual-image visual review passed. No publication or live changes.

### Files Changed

Implementation checkpoint `59068290eb69506fd7a5d248c5ed359cfb98163d`, source PR https://github.com/kodjobaah/moda-interact-shared/pull/89 (source review).

- Pure `composite-profile.ts`, `composite-image-v2.ts`, `composite-recovery-v2.ts`: structural profile/current wire types, explicit safety/identity/output/host-byte binding and current-only carrier.
- `wrapper-contracts.ts`/`wrapper-projection.ts`: optional prepared `compositeProfile` + `compositeProfileSha256`, explicit pair/digest validation; existing whole prepared/common-reference hashes bind both.
- Node current renderer/preparer and reusable font/raster/preparation/source modules, geometry-free pinned asset manifest; current entrypoint exports.
- Removed unused fixed composite contracts, renderer/preparer, carrier branches, exports, fixed tests/scripts; retained established non-composite media/multipart behavior. Added current tests, installed-package validation script and README documentation.

### Work Completed

- Shared owns structural contracts and explicit technical safety only. `RecoveryCompositeProfileSchema` has no operational ranges/refinements/defaults. `assertRecoveryCompositeProfileSafety(profile):void` checks positive safe integer allocation dimensions/font, nonnegative coordinates/spacing, output pixel budget and rectangle containment. `assertRecoveryCompositeTextAllocationV2` separately bounds raw text/Pango work. Admin owns presentation ranges, defaults, nonoverlap/readability/product order; Background owns current selected-template authority.
- Explicit trusted helpers `assertRecoveryCompositeProvenanceIdentityV2`, `assertRecoveryCompositeOutputIdentityV2`, `assertRecoveryCompositeImageBindingV2` retain independent tenant/source/profile/runtime/output/hash proof. Mandatory host-only `trusted.body` and `trusted.logicalBody` bind exact independently supplied bytes; answer/footer/header metadata is also digest-bound. Shared chooses no concatenation, trim/nonblank/checkout placement/count policy.
- Exact current APIs: `getRecoveryCompositeRuntimeIdentityV2({profile,profileSha256})` synchronous; `createRecoveryCompositeImageRendererV2({profile,profileSha256})`; `prepareRecoveryCompositeImageV2(input:RecoveryCompositePreparationInputV2,deps?)`. Current carrier parser context is `{checkoutUrl,compositeV2}`; no fixed composite context/decoder.
- No independent PlatformConfiguration registry or Shared defaults. Saved source/prepared/common reference is the sole application layout authority. Optional absent historical prepared reads remain structural/audit-only; hosts require current profile for executable sending.
- Profile changes drive both left-logo and centered/top-logo arrangements through the same exact installed artifact. All four optional-product dimensions and pixel separation/containment were verified. Unsupported glyph/overflow/identity/deadline fails closed; selected missing product never becomes header-only success. One original budget covers source/render/immutable storage/probe, including late noncooperative HEAD prevention of later PUT.
- Root-authorized zero-record cutover removes obsolete fixed composite APIs from new source. Public .11 archive remains immutable; unrelated TEXT/IMAGE/BRAND_IMAGE and established multipart are preserved. Removed public APIs are breaking; architect/root will select a separate major release and exact-public-archive approval. No implementation version change.

### Validation Results

- `npm run typecheck`: PASS, including final current-only tests.
- Focused current profile/Node + established media/multipart: PASS31/31. Added exact caption/logical independence, fixed-format rejection and current source/output/deadline/late-HEAD/storage/probe regressions: PASS13/13 current-focused total.
- `npm test`: PASS797, 3 configured skips (800 total); this full run preceded four additional current-only regression cases, all covered by the subsequent focused13 run. No production-byte edits after full run/build.
- `npm run build`: ESM and DTS PASS. No declared lint script; none invented.
- Exact unpublished candidate `/tmp/ARCH-075-SHARED-012/shared012-current-029bdf8c2016.tgz`: SHA256 `029bdf8c2016ffe926d54e3c79ab759d51ad51df234297712a9f1af43a2a0929`, 965707 bytes /161 files, integrity `sha512-CUeAf6EmUBMt5gGsa8lQpjbPsFOZmBhLJkdeIydloc1OLsBGdFX9Fav7ui8hgg2tdoqKxeQTmX4jbO2AdHDQpA==`. Metadata version remains5.13.11 only for unpublished consumer testing; supersedes prior provisional artifacts.
- `node scripts/validate-recovery-composite-v2.mjs <exact candidate>`: PASS installed Node ESM/types/browser isolation, same-artifact two-profile product/no-product raster/pixel/determinism, saved prepared/common reference binding and mismatch rejection. Public synthetic fixtures only.
- Packed candidate scan:161 files, zero private QA inputs/assets and zero obsolete fixed layout constants in JS/declarations. `git diff --check`: PASS. PR currently has no configured check statuses.
- Actual private same-package host proof protected at `/tmp/ARCH-075-SHARED-012/private-actual-final-host/`; fontless Alpine proof at `/tmp/ARCH-075-SHARED-012/private-actual-saveable-alpine/`. Each contains four full images,375px previews and input/runtime/profile/output receipt; no private data is committed. Root independently viewed all four final Alpine previews and relayed PASS through architect. Admin independently evaluated the final top profile with real `compositeProfileError===null` and matching digest `7c8f95941e47a7501da6b3dcad328e67c89769399cd93364498c7a89a13cedfd`.
- Actual left geometry1125x900/300, text734x213 host versus716x241 Alpine; centered/top1125x1280/640, text669x386 host versus766x414 Alpine. Final consumer-owned top QA profile uses textTop200/textHeight440 within header640, font40/spacing48, contained logo180x160 at472,20 and product1077x576 at24,680. Earlier360/400 text boxes safely returned HEADER_OVERFLOW; no truncation, fallback profile, Shared code/default/range change or false success. Admin’s unchanged authoring helper accepts final profile.
- Actual host times1034/107/322/140ms; Alpine1052/274/1204/392ms (left product/no-product then top product/no-product; includes375px preview work). Exact tarball unpacked under canonical installed package location, real native Sharp0.35.4 and required external dependencies, Node22.23.5/linuxx64, no installed system-font directories. Complete runtime receipts include all native library versions; same source/profile input hashes and distinct host/Alpine runtime/output hashes explicitly verified. No cross-platform byte identity claimed.
- Private input SHA256: logo `bc39de76a5c4f5bb3947dea5e308825b0a192324bc2003931a422b7b353b9d9b`, product `dac12cf07aaf872951675788df3c3a2f4ad9aafda8f47ae70d804975ecc7ae9c`, canonical header `7e2d7c8d8ab536a6addcb2aa8061bf4ba8ddd72a391fb0f8a72e288d05798aeb`. No answer/checkout text supplied to bitmap renderer.
- Launcher canonical isolation: primary workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent `moda-interact-workspace-task-ARCH-075-SHARED-012`; implementation `moda-interact-workspace.worktrees/ARCH-075-SHARED-012`; mirrored `task/ARCH-075-SHARED-012`. Parent reused/implementation created; both origin-main synchronization checks already-current, task remote fast-forward not-needed; recursive submodule ready/no entries. Durable claim `e21752fe25eedfca9dc5cd46e2eb5769ef1c483a`, executor codex/attempt1. No gitlinks/other task files staged.

### Deviations

Later explicit user amendments supersede initial compatibility/independent-configuration objectives: fixed composite removed; saved template owns profile; Shared validation is structural plus explicit technical/provenance safety. No old fixed-render byte-preservation adapter remains. Existing non-composite behavior retains its own established contracts.

### Assumptions

Root owns source/parent integration, actual visual approval, separate release/version selection/publication authorization and application rollout.

### Unresolved Issues

None for this Shared source scope. Exact artifact was handed to Admin/Background under root’s provisional testing authorization; their lifecycle acceptance remains separately owned. Admin same-pack renderer/profile proof passed; Background same-pack build/type/focused325 passed and its service integration validation remains separately owned.

### Architectural Concerns

Deleting previously public fixed-composite exports is a breaking public API change. A subsequent release must use architect/root-approved version (root guidance6.0.0) and a new exact archive/publication approval; never republish/unpublish public5.13.11. Runtime identity hashes complete sharp.versions/platform/arch/Node/fixed settings/profile; deterministic bytes are promised only within the same pinned runtime. No cross-runtime byte identity or migration mechanism claimed.

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

No architecture/live completion claim.
