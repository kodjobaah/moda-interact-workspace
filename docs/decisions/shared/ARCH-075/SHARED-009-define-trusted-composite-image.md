---
id: ARCH-075-SHARED-009
architecture_id: ARCH-075
title: Define trusted composite recovery image contract
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
claimed_at: 2026-11-13T23:07:13Z
attempt: 1
depends_on:
  - ARCH-075-SHARED-006
enables: 
  - ARCH-075-SHARED-010
created: 2026-11-13
updated: 2026-11-13
---

# Define trusted composite recovery image contract

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; moda_architect.

## Objective

Define one additive trusted composite image carrier that binds rendered shop branding and optional verified product to the real answer/footer caption.

## Context

User approved single bubble: original logo and product remain separate assets; a deterministic derived bitmap shows logo beside shop details, divider then optional product, while answer and one canonical checkout footer stay real caption text. Supersedes unexecuted two-bubble SHARED007/008/BG013. Native template changes remain excluded.

## Scope

Browser-safe composite provenance/prepared-image/plan schema and digest exports plus direct contract tests. Existing runtime primitives are reused; no image renderer implementation in this task.

## Out of Scope

Renderer/fonts/network/R2 execution, package version/publication, service consumer, native template AST/registration, schema/database or new generic framework.

## Requirements

- Add distinct COMPOSITE_IMAGE kind to the appropriate media carrier; do not pretend output is logo BRAND_IMAGE or product IMAGE. Keep existing TEXT/IMAGE/BRAND_IMAGE/frozen multipart bytes/digests and validators unchanged.
- Provenance binds exact trusted LOGO/SQUARE_LOGO source origin/generation/fingerprint plus actual input byte hash, optional verified product shop/platform/product/variant+actual byte hash, same tenant, canonical rendered header text/common reference hash, layout/renderer/font asset identity, strict output dimensions/MIME/size/SHA and trusted publicOrigin/objectKey/publicUrl identity. Product absence is explicit, supporting no-product AI/HUMAN.
- Caption is complete answer+canonical footer, <=1024 Unicode codepoints; no truncation/global URL count. Full logical header+answer+footer remains separately authoritative for moderation/history/receipt. Host must cryptographically bind exact caption/bitmap header to original canonical boundaries before send, not infer equivalence from text inclusion.
- New composite key namespace binds tenant hash/render identity/output hash; output URL equals exact trusted origin/key and key suffix matches content SHA. No model URLs or secret/customer/checkout/answer content in reusable bitmap/cache identity. Define fixed bounded geometry/layout version in coordination with Node renderer; existing1125x600 output assumptions must not silently validate taller composite bytes.
- Browser export contains no Node/Sharp/Prisma/config reads. Runtime authorization remains Background-owned, current source provenance reattested before send. No fields/roles/version changes elsewhere unless concrete compatibility need is returned.
- Demonstrate current5.13.10 rejects new kind; new reader accepts exact old plans. No writer activation/publication. Malformed/mixed-tenant/forged origin/hash/key/caption/control/oversize cases fail closed.

## Work Items

- [x] Define minimal distinct provenance and plan schema/digest.
- [x] Prove optional-product, same-tenant and exact source/output identities.
- [x] Preserve legacy contract/digest and browser safety; publish source/report.

## Interfaces / Contracts

Published commerce/presentation media plan exports and existing brand/product provenance schemas. New composite is additive schemaVersion1 carrier; no new multipart role needed unless proven.

## Dependencies

ARCH-075-SHARED-006 Complete and published5.13.10. Root released resource hold after BG012 final checks; this Ready task may prepare normally. No implementation worktree was created at definition time.

## Enables

ARCH-075-SHARED-010 only after source acceptance/integration.

## Acceptance Criteria

- [x] Distinct composite with trusted same-tenant dual/optional-product provenance and exact public output identity.
- [x] Caption/logical-body separation explicit; no unsafe URL/string inference or source relabel.
- [x] Legacy vectors/digests unchanged; browser-safe packed exports and negative guards pass.

## Validation

- [x] Focused schema/digest RED/GREEN optional-product, forgery/control/Unicode/caption/tenant/output cases.
- [x] Declared relevant/full tests/type/build/available scoped lint and packed/browser safety checks.
- [x] Diff/privacy, exact isolated source/report and compatibility evidence.

## Stop Condition

Publish exact mirrored source/report, set review and return architect. No main merge, live mutation, enabled consumer or npm publication without release-specific authorization.

## Implementation Notes

Normal launcher dedicated sibling worktrees. You are not alone; preserve others and primary. Original approved mock is schematic only: small contained logo alongside shop details, divider, product beneath. Root owns operational/visual review and integration; no live sends.

## Completion Report

### Status

Ready for Review; independent architect review required.

### Files Changed

- `src/commerce/presentation/composite-image.ts`: distinct pure provenance/prepared image/plan/reader schemas, trusted canonical boundary builder/parser, tenant/render/boundary/plan SHA bindings and fixed geometry.
- `src/commerce/presentation/index.ts`: additive browser-safe exports only.
- `src/commerce/presentation/composite-image.test.ts`: optional product, tenant/input/output forgery, Unicode/control/bounds, exact canonical whitespace and footer line, distinct-kind and digest compatibility vectors.
- `scripts/validate-recovery-composite.mjs`, `package.json`: packed installed ESM/types/browser validator, including actual published 5.13.10 old-reader rejection and exact old media/multipart digest comparisons.
- `README.md`: unreleased contract/geometry/trust responsibilities and rollout limits.

### Work Completed

Added opt-in `COMPOSITE_IMAGE` schemaVersion1 without changing any old TEXT/IMAGE/BRAND_IMAGE/multipart schema, role or digest. Product is explicit null or a verified shop/platform/product/variant identity and input byte hash. Logo uses the existing strict trusted brand origin/generation/fingerprint (LOGO/SQUARE_LOGO only) plus actual input byte hash; all inputs share one tenant. Provenance also binds exact canonical header/common-reference hash and immutable layout/renderer/font manifest identities.

Output is JPEG below 5 MiB, 1125×900 with product or1125×300 without, using the new tenant/render/output content-hash namespace and exact trusted origin/key URL. Contextual parser recomputes tenant/render identity, compares independent current provenance/public origin, and requires an independently verified output SHA/size receipt. Schemas and digests alone do not attest bytes or confer authorization.

Canonical caption is answerText+footerText and original logical body is headerText+answerText+footerText, with no inserted separators, trim or normalization. Parser compares exact independently supplied canonical boundaries and original logical body; boundary digest binds every component, and plan digest binds image/provenance/output and both text forms. Actual caption final trusted URL line is validated through the existing checkout parser. Caption1024codepoints and original 4096 UTF-16-unit text limits remain distinct; no global URL count or truncation.

Geometry coordinated with architect before freeze: modest contained 180×180 logo at (48,60) alongside full header 813×252 at (264,24) in a 300px header; optional contained 1125×600 product below at (0,300). Initial extra graphic-divider proposal was removed following inspection of actual canonical boundaries: render full authored header (including its divider) literally exactly once; no heuristic partition/stripping and no added ornament. Renderer must fall back if exact header/font glyphs cannot fit, without modifying canonical text. No renderer/font/network/R2 implementation, service consumer, native template/database change, version bump or publication.

### Validation Results

- RED: focused new-contract test failed before barrel export with missing `ConversationCompositeMediaDeliveryPlanSchema`; no false claim of old reader support.
- Final production geometry: 23/23 focused composite/multipart tests passed, including exact owned whitespace, caption final-line checks and readable header geometry. Architect-requested same-checkout-URL authored-answer test-only addition: 11/11 affected composite tests passed; exact answer plus canonical footer and trusted parse remain valid, without any global URL-count heuristic.
- `npm test`: 800 tests, 797 passed, 0 failed, 3 declared skips before the subsequent coordinate-only readability adjustment. Final affected focused/type/build/packed checks passed after that adjustment; no unrelated broad repeat was added for the final test-only request.
- Final `npm run typecheck` and `npm run build`: passed (ESM and DTS).
- `npm pack --ignore-scripts --json --pack-destination /tmp/ARCH-075-SHARED-009`, then `npm run validate:recovery-composite -- /tmp/ARCH-075-SHARED-009/modainteract-moda-interact-shared-5.13.10.tgz`: passed installed ESM, installed exported declarations, isolated browser execution, actual published 5.13.10 rejection of composite, and exact existing TEXT/BRAND_IMAGE/IMAGE plus all five valid multipart-order bytes/digest vectors.
- Final unpublished candidate archive SHA-256 `a026569f6f1e676a29417e14cf87455cca9dbf3cdeb1199c2724b4069f264aad`; package version remains 5.13.10. This is validation packaging only, not publication.
- No lint script/config is declared; no substitute lint contract invented.
- Diff/privacy: synthetic-only tests; private shop assets were not read, copied or committed; no Node/Sharp/Prisma/config import added to browser entrypoint.

### Deviations

No scope deviation. Exact authored concatenation and literal single authored divider clarified against actual Background boundaries before freezing. Renderer 010 remains separate; no font choice frozen here. Root readability correction implemented in fixed geometry and explicit vectors; architect same-checkout-URL coverage request implemented in the focused test, with 11 affected tests passing. Production bytes did not change for that test-only addition.

### Assumptions

Background is the intended production producer/consumer. Node renderer010 will consume the same exports directly. Host independently verifies common reference/provenance/current authorization and renderer/public-probe bytes; never derive trusted context from the stored plan/model. `commonReferenceHash` hashes stableJson of the complete verified common reference; `fontAssetSha256` hashes a canonical ordered font manifest including shaping settings. Old workers must drain after compatible reader deployment before new kind emits.

### Unresolved Issues

Renderer 010, combined publication 011, Background consumer and live/visual acceptance remain separate gated work. No release 009 alone.

### Architectural Concerns

No new cross-repository dependency beyond the explicitly sequenced renderer/release/consumer. The pure contract preserves old frozen plans; old 5.13.10 readers reject new composite kind by design.

### Git / VCS

Mirrored branch `task/ARCH-075-SHARED-009`. Durable parent claim `db1d0fca1518d98be73a950bb664a416a2652cb4` pushed. Implementation source `09a195c92f7500597944e26707c5c0a3954b00aa` pushed to origin/task/ARCH-075-SHARED-009, source PR https://github.com/kodjobaah/moda-interact-shared/pull/86 . Parent review report is committed/pushed by its containing commit on the same mirrored task branch (no self-referential hash claim). No agent main merges or parent implementation gitlink staged.

Launcher physical isolation/synchronization evidence:
- Canonical workspace `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-075-SHARED-009` reused on task/ARCH-075-SHARED-009, initial head 8a241ca99dc2f308a6e4e416271f28a1ec353310.
- Implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-075-SHARED-009` created on task/ARCH-075-SHARED-009, initial head 232bcb3a3e5a8385aa76fc50f1c59da34f323fb1.
- Shared workspace/implementation checkouts switched/mutated for task work: no; another task worktree reused: no.
- Both remote task fast-forwards: not-needed; both origin/main incorporated: already-current.
- Recursive submodule sync/update-init passed; status ready; entries none. Dependency gate passed SHARED006 Complete.

## Architect Review

### Review Status

Accepted

### Review Notes

Independently reviewed exact source09a195c92f7500597944e26707c5c0a3954b00aa and report4ab6143bf5c5d9efb7037bf63982a57964e240d0. No findings. Distinct opt-in composite carrier binds current independently supplied logo/optional-product provenance, tenant/render/output identity, exact canonical header/answer/footer boundaries and caption/logical-body digest without disguising output as an existing image kind. Structural parse/digest is explicitly not authorization; host reattestation and trusted renderer/probe receipt remain required.

Initial newline insertion mismatch was corrected before acceptance: canonical boundaries concatenate verbatim. Authored same checkout URL is retained separately from appended footer; no global occurrence heuristic. Full header including authored divider is rendered once; no separate ornament. Final geometry has independent813×252 text area and centered modest logo, retaining300/900 canvas. No renderer/font/publication/consumer work was smuggled into contract task.

### Reviewed Files

composite-image.ts and tests, presentation index, packed validator script, package script and README. Existing commonLayoutBody boundary semantics and media/multipart schemas inspected.

### Validation Reviewed

Full800/797PASS/3declaredskips before coordinate-only correction; final23focused/typecheck/ESM+DTS/packed installed ESM/types/browser and published5.13.10 compatibility passed after correction. Final test-only sameURL vector11/11 passed. Existing all media/five multipart-order bytes/digests preserved. Candidate validation archivea026569f6f1e676a29417e14cf87455cca9dbf3cdeb1199c2724b4069f264aad is unpublished5.13.10 packaging, not a release. No declared lint contract. Privacy and dedicated launcher synchronization/isolation evidence reviewed. No unnecessary repeat tests.

### Architecture Conformance

Conforms to Shared browser-safe contract ownership and additive production compatibility. No old validators/digests changed, no Node/Sharp/runtime secrets leaked. Source acceptance does not activate new writer or constitute publication.

### Follow-up

Root merges exact source/parent pin; then promote renderer010. Combined009+010 release011 requires exact tested archive/public approval, not contract-only publication. BG014 remains defaultOFF preparatory/final-release gated. ARCH-075 remains In Progress.
