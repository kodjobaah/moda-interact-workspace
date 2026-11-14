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
status: complete
priority: 10
executor: codex
claimed_at: 2026-11-13T23:31:11Z
attempt: 1
depends_on:
  - ARCH-075-SHARED-009
enables: 
  - ARCH-075-SHARED-011
created: 2026-11-13
updated: 2026-11-14
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

### Final typography choice

Root approved DejaVuSans44/dpi72 after actual no-autofit/no-trim fontless Alpine probe: exact canonical header716×241 fits813×252;40pt766×222,48pt779×264 exceeds height. Render at fixed44 with measured width/height/glyph guards, no shrinking. Logo180×180 at48,60; text at264,24; header300. Full compositor image and responsive root visual review still required; text-only preflight does not prove whole image.

### Required opt-in one-root carrier completion (architect amendment)

Read-only Background engine audit confirms accepted009 media union alone cannot pass the existing recovery multipart carrier. Add a NEW opt-in composite-aware recovery carrier/parser/digest in this same010 source before combined release. Minimal new wire shape reuses schemaVersion1/kindRECOVERY_MULTIPART/parts and exactly one HEADER with COMPOSITE_IMAGE; alternatively pass exact legacy carrier unchanged. No new roles/fields, composite+extra-parts or relaxation of old validators.

Trusted parse/build must call accepted009 composite parser with independently supplied canonical boundaries/provenance/output receipt; structural union/digest alone is not authorization. New carrier digest must preserve byte-identical old plan digests; current5.13.10 must reject new shape while new opt-in reader accepts exact old vectors. Export browser-safe pure helpers/types separately from Node renderer. Add focused negative/mixed-role/count/trusted-context and packed/browser/type vectors. Share exact stable API with Background owner before publication; no service-local duplicated validator or second release. This is a directly required contract completion discovered before any publication, not runtime/ownership expansion.

## Work Items

- [x] Implement safe deterministic compositor/preparation with font/license provenance.
- [x] Verify bound/cache/output/optionalproduct/fallback and actual Alpine rendering.
- [x] Return private actualQA image and measured receipt to root; run required checks and publish exact source/report.

## Interfaces / Contracts

Accepted SHARED009 browser contract; existing commerce/presentation/node safe fetch/R2/probe/deadline primitives. Node-only renderer imports must never leak browser exports.

## Dependencies

ARCH-075-SHARED-009 Complete/Accepted and integrated: Shared mainbc98bf13d8d2596490d9497783637e8eac6f96c6 and parentmaine8483ed0f6fb078fb694d946f67ff2cf6ec064a9. Normal preparation may claim this Ready task.

## Enables

ARCH-075-SHARED-011 release gate; Background consumer only after accepted package contract and proper publication gate.

## Acceptance Criteria

- [x] Actual bitmap matches approved order and retains full canonical header; no customer/checkout/answer pixels.
- [x] Optional product, original inputs, font/markup/glyph/overflow and bounded missing/network/timeout cases safe.
- [x] Trusted dual provenance/output hashes/public object verification and old defaults preserved.
- [x] Real Alpine output and root visual review evidence, declared checks and clean mirrored source/report.

## Validation

- [x] Deterministic pixels/outputhash/sourcechange/textchange/fonthash/cache identity tests; malformed/foreign/unsafe input, timeouts/probe/conflict/overflow/glyph cases.
- [x] Actual no-hostfont node22-alpine renderer and offline private Eugene output for root review; no live send.
- [x] Declared relevant/fulltests/type/build/available scopedlint, packed asset/license/browser separation/privacy checks.

## Stop Condition

Publish exact mirrored source/report, set review and return architect. No main merge, live mutation, enabled consumer or npm publication without release-specific authorization.

## Implementation Notes

Normal launcher dedicated sibling worktrees. You are not alone; preserve others and primary. Original approved mock is schematic only: small contained logo alongside shop details, divider, product beneath. Root owns operational/visual review and integration; no live sends.

## Completion Report

### Status

Ready for Review. Root approved actual host and actual fontless Alpine mobile product/no-product visual outputs. All final required checks passed.

### Files Changed

- `node/composite-renderer.ts`: fixed contained bitmap compositor, escaped literal full header, pinned font/coverage/overflow guards, exact output verification and runtime-bound shaping receipt.
- `node/composite-image.ts`: trusted dual/optional derivative source validation and whole-attempt bounded fetch/render/immutable-write/public-probe preparer; failed selected product never becomes header-only success.
- `node/metadata-verifier.ts`: explicit bounded dimensions with the unchanged 1125×600 default.
- `node/r2-writer.ts`: pre-I/O abort guards preventing delayed HEAD/factory work from issuing late PUT.
- `composite-recovery.ts` and presentation/Node barrels: opt-in single composite HEADER carrier/parser/digest and Node exports, with every old validator unchanged.
- `node/composite-image.test.ts`: deterministic pixels, input/hash/tenant/glyph/font/overflow/markup/optional-product/deadline/collision/probe/late-HEAD and carrier trust regression vectors.
- `assets/recovery-composite/{DejaVuSans.ttf,LICENSE.txt,coverage.json,manifest.json}`: exact official licensed font, complete original license, generated 5,918-scalar coverage, pinned source/config hashes.
- `package.json`, packed Node/browser validators and README: explicit asset packaging, actual installed Node resolution, browser/old-reader compatibility and consumer/replay responsibilities. No dependency/version/lock change.

Paths above are under `src/commerce/presentation/` unless stated otherwise. Sixteen implementation files changed; no private QA image/header or runtime consumer included.

### Work Completed

Implemented the accepted fixed V1 geometry and full literal canonical header exactly once, with no extra divider, text normalization, crop, shrink or injected copy. Logo/product originals remain unchanged. JPEG output is independently re-decoded and hashed; trusted key/origin, tenant/render/output identity and explicit product-dependent 1125×900/300 dimensions are enforced. Rendering failure safely omits optional media; host retains complete TEXT fallback.

Reused existing pinned HTTPS, guarded immutable R2 and exact public GET probe. One budget is min(5000ms, original remaining turn minus1000ms) across both sources and all later stages. Abort/timeout/cleanup and selected-product failures are bounded safe omissions. HEAD reuse deduplicates writes after rendering; no pre-render cache service or host database/configuration/policy lookup implemented.

Static font asset manifest SHA `9213e2b12cdc77c7de70ed5b738e1894efeae4b54657a31373236d2642065b02`; official TTF SHA `7da195a74c55bef988d0d48f9508bd5d849425c1770dba5d7bfc6ce9ed848954`; full license SHA `7a083b136e64d064794c3419751e5c7dd10d2f64c108fe5ba161eae5e5958a93`; coverage SHA `4f7b61ab9a530ba988efa8b6e87cfed72b7e06a08d0f3422eed89094c7a3e8ed`. Assets resolve correctly outside tsup-cleaned dist after actual package installation. License is Bitstream Vera/DejaVu/Arev, not OFL.

`RECOVERY_COMPOSITE_RENDER_PROFILE` binds the whole actual sharp.versions, platform/arch/Node and fixed typography/encoding. Runtime-bound font manifest is `8ed59c795a11ee6218fe71e0e2bd3cea21397d21be86eb88501edd7f5e9998e1` on tested Darwin and `f583b8435957dd99ab54be10a106a12617361725eb3290dcb8c589111616b058` on tested Alpine. Determinism is within the same pinned runtime; no cross-platform byte-identity claim. Original frozen runtime/font/output receipts remain authoritative on replay, with current source/control attestation separate.

Architect-required carrier completion implemented: `RecoveryCompositeMultipartDeliveryPlanSchema`, `parseRecoveryCompositeMultipartDeliveryPlan(raw,{checkoutUrl,composite},sha256)`, builder and digest admit exactly one HEADER with COMPOSITE_IMAGE or exact legacy multipart. New parser invokes independently trusted composite parsing and requires matching checkout contexts. No new wire field/role/version, extra part or relaxed old validator. Stable API was returned to coordinator for Background owner.

### Actual Offline Visual Evidence

Root final visual gate PASS for both product/no-product 375px host and actual fontless Alpine samples; coordinator independently viewed 320px. Actual canonical shop header and separate supplied logo/product only; no answer/customer/checkout pixels, live sends or committed private asset. Root saved private durable approved copies/receipts.

Private local outputs: `/tmp/ARCH-075-SHARED-010/{actual,alpine-actual}-{product,no-product}{,-320,-375}.jpg`; actual Alpine receipt `alpine-receipt.json` in that directory. Source QA ran real Node22.23.5/linux-x64/Sharp0.35.4/libvips8.18.6/Pango1.58.2 without system fonts via TAR-stdin/tmpfs Docker (host bind mounts are not visible to this daemon).

Actual Alpine canonical text measures716×241 within813×252; product output1125×900/87449bytes SHA `21c0588f599d219382fc0afe37dfc2db289c97ac260faab9f2b161ea55a997cf`; no-product1125×300/30406bytes SHA `9064f98ecf7c36dd0c7f465814748f4c234f6573cada43214cefe8ce817b69e1`. QA artifact cycles793ms/182ms include preview writing/resizing. Host canonical text measures734×213; product SHA `a47376156e6a4230423a0e8e0701877d9812813d14fe34cbf73db1ca0d27a929`; no-product SHA `af32d6c88043928c256e89c410e9010a31cf743141c5b7b23917dc1f52dc4374`. Layout differences are represented by different runtime and content hashes.

### Validation Results

- Final settled focused:43 passed,0 failed, including generic late-HEAD/no-late-PUT regression and old media golden bytes.
- `npm run typecheck`: passed.
- `npm test`:811 tests,808 passed,0 failed,3 declared skips.
- `npm run build`: ESM and DTS passed.
- Local `npm pack --ignore-scripts` and `validate:recovery-composite-node`: installed real package font/license/coverage/path resolution, deterministic repeated output, actual text/logo/product pixel checks and original verifier defaults passed.
- `validate:recovery-composite`: installed ESM/types/browser isolation, trusted new carrier, actual published5.13.10 rejection of new carrier and byte-identical old media/all five legacy multipart-order digests passed.
- Exact same packed artifact installed in actual fontless Node22 Alpine: real Node exports/font/license/pixels/repeated output and explicit dimensions passed. Packed fixture pure-render timings: Darwin531ms product/59ms no-product; Alpine441ms product/219ms no-product. These establish rendering cost, not a production network-latency guarantee; the whole preparation still enforces the original deadline.
- Exact unpublished tested archive `/tmp/ARCH-075-SHARED-010/modainteract-moda-interact-shared-5.13.10.tgz`,161 files, SHA `d3928d3c8f9b4a5bc7415005eab891360c38d5c9b69935f1c8b9d1eda62a19ac`. Version remains5.13.10; this is validation packaging only, not publication. Only four licensed static font assets were added to the package; no private QA files.
- No lint script/config declared. Source/privacy/diff checks passed except the exact upstream LICENSE line77 trailing space, intentionally retained byte-identically per required license hash. Diff check excluding that unchanged third-party text is clean.

### Deviations

No scope deviation. Required carrier amendment and shared writer abort defense are implemented. Superseded in-flight validation was terminated after the abort correction; one final serial settled-source focused/type/full/build/pack/browser/installed-Alpine pipeline passed. Initial Docker bind-mount attempt was replaced with the already proven TAR-stdin/tmpfs method; no environment restart or new font manager.

### Assumptions

Background supplies current trusted source/common/control authorization and immutable original delivery receipts, retains complete logical text and handles omission as full TEXT. Shared performs no host policy lookup, provider send or runtime migration. Future replay must not replace frozen receipt identity with the current runtime font hash.

### Unresolved Issues

None within010. Combined accepted009+010 publication011, Background adoption/integration and live proof remain separately gated. No contract-only release, registry publication, main merge, live send or consumer work performed.

### Architectural Concerns

Root visual gate is satisfied offline; this does not establish live delivery. Old readers reject new composite carrier; compatible reader rollout/drain remains required before emissions.

### Git / VCS

Both mirrored branches `task/ARCH-075-SHARED-010`. Implementation commit `483f7a27c654a3a49d6ec4896c616cd0475a938c` pushed, source PR https://github.com/kodjobaah/moda-interact-shared/pull/87 . Parent review report committed/pushed by its containing commit. Durable launcher claim `d91386c7353738f9cd6e4460aae8494ddeffe7e7` pushed. No agent main merges or parent gitlink staging.

Launcher isolation/synchronization evidence:
- Canonical root `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-SHARED-010`, reused on task/ARCH-075-SHARED-010; initial head2c700adb4f5d52967ba2d2cb8f392157aafe322e.
- Implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-SHARED-010`, created on task/ARCH-075-SHARED-010; initial headbc98bf13d8d2596490d9497783637e8eac6f96c6.
- Shared workspace/implementation checkouts switched/mutated:no; another task worktree reused:no.
- Both remote task fast-forwards:not-needed; both origin/main incorporated:already-current.
- Recursive submodule sync/update-init passed; statusready; entriesnone. Dependency gate passed SHARED009Complete.

## Architect Review

### Review Status

Accepted

### Review Notes

Independently reviewed exact source483f7a27c654a3a49d6ec4896c616cd0475a938c and mirrored report808520a3668d43de5eb576d8adfe5034c6c02099. No findings. Node renderer pins licensed font/coverage, escapes canonical literal header without normalization or added divider, checks measured fit and both actual input hashes, contains original images and verifies explicit output dimensions/hash. Runtime-bound shaping identity includes all Sharp versions/platform/architecture/Node/fixed settings; no unsupported cross-platform byte identity or pre-render cache claim.

Preparation reuses existing safe pinned fetch/immutable R2/public probe, exact current origin/key/input identity and one bounded controller; unsupported/missing/font/fit/network/timeout paths omit safely. Existing verifier1125x600 default retained. Minimal reused-writer pre-I/O abort checks prevent late PUT after delayed HEAD, without schema/API expansion.

New opt-in carrier is legacy or exactly one HEADER COMPOSITE_IMAGE, trusted parser delegates009 independent boundaries/provenance/output validation and checks outer checkout identity; old public schemas and digests unchanged. Pure browser exports remain Node-free.

### Reviewed Files

composite-recovery.ts; Node composite-renderer.ts/composite-image.ts and tests; Node metadata-verifier/r2-writer changes; browser/Node exports, package assets/license/coverage/manifest, validation scripts and README. Actual private host and Alpine product output/receipts inspected; no private assets committed.

### Validation Reviewed

43focusedPASS;811full/808PASS/3declaredskips;typecheck/ESM+DTS;installed packed Node asset/license/path/pixel/determinism and browser/types/actual5.13.10 compatibility; exact packed fontlessNode22Alpine allPASS. Root approved product/no-product375 visuals, canonical readable singledivider and uncropped sources. Actual Alpine1125x900/300 with716x241 header measured, root evidence durable privately. Archive161files SHA d3928d3c8f9b4a5bc7415005eab891360c38d5c9b69935f1c8b9d1eda62a19ac is unpublished validation5.13.10, not release. Upstream LICENSE trailing space retained to preserve exact license hash; other diff/privacy checks clean. Launcher isolation/synchronization and clean mirrored publication reviewed. No additional broad reruns.

### Architecture Conformance

Conforms to Shared reusable Node mechanics/browser contract separation, immutable original source/provenance and one-bubble approved design. No host policy/database/provider send or live activation. Frozen receipts retain original runtime identity; consumers must not replace it with current hash.

### Follow-up

Root merges source/parent actual pin. Then promote011 release preparation (no publish before explicit exact-archive approval) and014 defaultOFF preparatory source/local-packed tests. Actual published dependency final lock/npmci and genuine live delivery remain gated. ARCH-075 stays In Progress.

## Developer Integration

Root merged Shared PR87 at reviewed source483f7a27c654a3a49d6ec4896c616cd0475a938c after architect acceptance de7b86b65. Actual source main merge de3f9ee5d1aa24c4ac6c51b3f82b12269fddd300 is recorded by this gitlink.43 focused tests,808 full passes/3 configured skips, build/types, installed packaged assets/browser/old-reader compatibility and exact packed fontless Alpine checks passed. Root independently inspected and approved actual Alpine product/no-product mobile outputs, preserving the original assets and canonical header. No hosted checks are configured for this PR. This integrates source only; no public release, enabled sender or live WhatsApp send.
