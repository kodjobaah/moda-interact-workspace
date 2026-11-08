---
id: ARCH-066-SHARED-011
architecture_id: ARCH-066
title: Correct frozen outreach brand binding compatibility
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: complete
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on: ["ARCH-066-SHARED-010"]
enables: ["ARCH-066-SHARED-012"]
created: 2026-11-08
updated: 2026-11-08
---
# Correct frozen outreach brand binding compatibility

## Architecture
ARCH-066; docs/architecture/ARCH-066-conversation-product-context-and-whatsapp-preview-parity.md and ARCH-066-initial-outreach-contract.md. Coordinator moda_architect.

## Objective
Preserve the existing supported frozen initial-template brand binding semantics through the published Shared outreach renderer.
## Context
BACKGROUND002 adoption exposed a required compatibility gap in immutable5.8.0: SemanticKeySchema allows shopBrand.logoAltText/logoWidth/logoHeight/squareLogoAltText, but PreparedVariableResolver.resolve has no corresponding cases and always refuses valid values. Background's existing RecoveryVariableResolver supports saved text/dimensions, mandatory-brand refusal, and authorized ready media URLs in body parameters. Generic shop.name fallback must not silently satisfy mandatory shopBrand.brandName.
## Scope
Shared outreach strict render input/data projection, resolver/bindings and focused compatibility fixtures only. Inspect actual5.8.0 exports/source and Background read-only evidence; do not import Background. Add the smallest bounded explicit data inputs for saved brand text/dimensions and ready same-shop media by role needed to preserve existing semantics. Shared retains deterministic semantic-key/cap validation/rendering, hosts retain database/media resolution and tenant authorization. Do not accept arbitrary callbacks, raw customer records, unvalidated dictionaries or original image URLs.
## Out of Scope
Standalone production identity,007/008/MCP002 resurrection, provider calls/media generation, producer/consumer edits, package publication, deployment, main integration and unrelated evaluator redesign.
## Requirements
Preserve all existing supported semantic keys and exact caps, required-vs-fallback distinction, positive safe bounded dimensions, prepared body/header/button fields and binding fingerprints. Missing/wrong-type/unsafe mandatory brand values fail closed; same-shop READY R2 media only, no original URL fallback. Valid body media bindings must work without an IMAGE header. Legacy ordinary shop.name/category inputs and no-brand templates retain behavior; no merchandise-specific keys. Preserve evaluator contracts, public009 product-details correction and all existing exports. Inspect invalid-URL validation throwing observed during Background fixtures; if directly reproduced in public renderer/schema, return typed INVALID_REQUEST instead of throwing for malformed input, with focused regression; do not widen trust.
## Work Items
- [x] Reproduce valid alt/dimension/body-media incompatibility and mandatory-brand distinction using exact published5.8.0 entrypoint.
- [x] Define minimal strict optional prepared brand/media data with explicit host/Shared boundaries and preserve prior no-brand input compatibility.
- [x] Implement deterministic supported bindings and fail-closed validation; no service-local imports or side effects.
- [x] Add positive/negative compatibility goldens and exact full text/parameter/provenance checks.
## Interfaces / Contracts
@modainteract/moda-interact-shared/commerce/outreach; InitialOutreachRenderInputSchema, renderInitialOutreachPreview, existing frozen SemanticKeySchema and strict ready-media contract. Extend documented data contract explicitly; do not pretend existing5.8 supports new inputs.
## Dependencies
ARCH-066-SHARED-010 Complete, immutable5.8.0 source/exports. No dependency on blocked Background or terminal system tests.
## Enables
ARCH-066-SHARED-012; consumer correction remains on original BACKGROUND002 after corrected publication.
## Acceptance Criteria
- [x] Valid saved logoAltText, squareLogoAltText, logoWidth/logoHeight bindings render exact expected parameters in INITIAL without copying Background algorithms.
- [x] Mandatory saved brandName cannot be satisfied by generic shop.name fallback; missing/invalid values refuse.
- [x] Authorized READY same-shop logo/square/cover URL body bindings preserve valid behavior; missing/wrong-shop/wrong-role/raw-original media refuses.
- [x] Existing nonbrand inputs, image/TEXT fallback, approved registration/binding integrity, provider parameter encoding and full-body bounds remain compatible.
- [x] Public runtime and declaration imports include corrected strict inputs; malformed input never weakens validation or leaks secrets.
## Validation
- [x] Focused outreach renderer/schema compatibility tests, including positive existing Background binding cases and negative tenant/type/value cases.
- [x] Existing outreach evaluator/render regressions, typecheck and production build per repository scripts.
- [x] Package public JS/declaration import smoke; record exact commands/results. No live calls.
## Stop Condition
After defined work/acceptance/required validation is complete, publish Completion Report at review and return control to moda_architect. Stop; no enabled task, release or consumer execution implicit.
## Implementation Notes
Exact initial evidence: Shared src/commerce/outreach/variables.ts switch afterbrandName/3URLs falls through; template-contracts.ts includes the4unimplemented fields. Background src/services/recovery-template-preparation/recovery-template-brand.ts supports saved type/cap semantics. Reuse approved Shared logger only if logging changes. If more contract work is required, return precise gap rather than expand scope. Use canonical launcher dedicated worktrees when execution is explicitly invoked; definition only now.
## Completion Report
### Status
Ready for Review — exact prepared brand/media correction implemented, validated and published on task branches.
### Files Changed
src/commerce/outreach/template-contracts.ts; variables.ts; render.ts; contracts.ts; index.ts; render.test.ts; contracts.test.ts; test-fixtures.ts; README.md; scripts/validate-commerce-outreach.mjs.
### Work Completed
Implemented exact normative schemas PreparedOutreachBrandSchema, PreparedOutreachBrandMediaSchema and PreparedOutreachBrandMediaItemSchema with inferred public types. Optional top-level preparedBrand/preparedBrandMedia preserve schemaVersion1 and no-brand input compatibility. Nested keys required, strict objects, nullable unavailable fields, 200 UTF16 text cap and integer dimensions1..10000 unchanged from normative contract.

Resolver now reads saved brandName/alt/square-alt and numeric width/height only from preparedBrand; every emitted text follows existing boundedText checks. Mandatory brandName never uses variables.shopName; ordinary shop.name remains unchanged. Fixed BODY URL slots use preparedBrandMedia independently of headerMedia, preserving exact validated parsed URL. Existing IMAGE CHECKOUT_PRODUCT/header/textFallback/frozen assignment rules remain unchanged; no header or raw original URL fallback is synthesized.

Complete structural validation runs first. Supplied preparedBrand tenant mismatch refuses IDENTITY_MISMATCH; all nonnull brand-media entries are validated for matching tenant/key-role and no fragment/dotted hostname before assignment/fallback, even when unused. Shape/type/status/kind/URL failures refuse INVALID_REQUEST; missing bound brand text/dimensions refuse BINDING_VALUE_UNAVAILABLE; missing role media refuses MEDIA_NOT_READY. Existing HTTPS refinement made total with URL.canParse; malformed renderer input returns typed refusal, not thrown URL error. No network/provider/database operation, arbitrary callback, service import or alternative renderer.

Exact frozen goldens preserve mandatory INITIAL shop.name/one checkout.itemsSummary per architect fixture reconciliation, then requested five saved-brand or three media subsequences; full7/5ordered parameters, complete body/provenance/button bytes asserted. Existing no-brand/body4096/4097/IMAGE-TEXT fallback/registration/hash/locale/all INITIAL offer-purpose regressions retained.
### Validation Results
- Published5.8.0 isolated public ESM reproduction (installed exact registry package): valid required INITIAL templates produced BINDING_VALUE_UNAVAILABLE for logoAltText/squareLogoAltText/logoWidth/logoHeight, incorrectly rendered generic Merchant for mandatory shopBrand.brandName, BODY logoUrl refused MEDIA_NOT_READY without header, malformed checkoutURL THREW. Receipt: /private/tmp/arch066-shared011-reproduction.log. First fixture attempt was rejected DEFINITION_UNAVAILABLE due missing mandatory bindings; corrected reproduction preserves them and is the authoritative evidence.
- `npx tsx --test src/commerce/outreach/*.test.ts`: PASS 79/79, zero skips/failures. Prior required run78/79; all normative reconciled brand/media/evaluator/render cases passed, sole extra whitespaceURL assertion expected raw rather than existing parsed normalized URL. Test-only assertion corrected; production source unchanged.
- `npm run typecheck`: PASS.
- `npm run build`: PASS ESM and declarations for final production source.
- `npm run validate:commerce-outreach`: PASS local pack installed in disposable consumer; all package export targets, public runtime and declaration imports for new schemas/types, positive saved-brand render/ordered parameters/fingerprint, evaluator/product APIs and malformedURL typed refusal verified. No source/internal-dist consumer imports. Temporary smoke project removed by existing script.
- `git diff --check`: PASS.
- Fixtures cover saved five fields, three BODY media with no header and CHECKOUT_PRODUCT header, mandatory-vs-generic distinction, missing/null values, unused wrongtenant/role, malformed/HTTP/credential/oversized URLs, raw/original/unknown/missingkeys, fragments including empty fragment, undotted hostnames, text200/201 UTF16 including astral characters/unpaired surrogate/controls/braces, dimensionbounds/types, legacy no-brand, fallback/hash/locale and4096/4097limits.
### Deviations
Only architect-approved fixture reconciliation ff55693ad: original brand/media-only fixtures conflicted with preserved INITIAL shop.name/itemsSummary requirements. Required bindings retained; requested vectors remain exact contiguous subsequences with complete arrays/body/provenance assertions. No selection/runtime policy weakening. Existing Zod https parsing normalizes surrounding URL whitespace; resolver emits exact validated parsed URL without further rewriting, and regression compares against parsed value while preserving existing schema semantics. No field layout/enum/version/export-map/lockfile/buildtool changes.
### Consumer Handoff
BACKGROUND-002/COMMERCE-002 populate preparedBrand from existing same-shop saved columns: brandName, logoAltText, logoWidth, logoHeight, squareLogoAltText; unavailable columns null. Never substitute generic shopName for mandatory saved brandName. Authorized ready R2 derivatives populate logo/squareLogo/coverImage slots with matching LOGO/SQUARE_LOGO/COVER_IMAGE roles and trusted shopId. Existing independent IMAGE header remains headerMedia, including CHECKOUT_PRODUCT. Hosts retain database/media ownership/authorization and resolve configured derivatives; Shared validates deterministic supplied shape/identity/roles/caps and frozen rendering only. Consumers adopt exact accepted immutable SHARED-012 artifact after separate publication. Background remaining72 failures still require original same-task investigation/revalidation; these goldens do not waive them.
### Assumptions
Trusted hosts authorize saved same-shop brand data and READY R2 derivatives; URL hostname is never proof of ownership. No original URL fallback or callback.
### Unresolved Issues
None scoped. Consumer adoption/publication/deployment remain separate.
### Architectural Concerns
No standalone resurrection, checkout/offer-policy redesign, new table, credit/consent/send/admission change, live call, publication or main integration.
### Git / VCS
Task branch: task/ARCH-066-SHARED-011.

Prepared physical isolation:
- canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
- parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-066-SHARED-011
- parent branch: task/ARCH-066-SHARED-011
- implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-066-SHARED-011
- implementation branch: task/ARCH-066-SHARED-011
- shared/default checkout switched/mutated for task implementation: no
- another task worktree reused: no

Prepared synchronization:
- parent remote task branch fast-forwarded: not-needed
- parent origin/main incorporated: already-current
- implementation remote task branch fast-forwarded: not-needed
- implementation origin/main incorporated: already-current
- recursive submodule sync/update: passed; noentries; ready
- Attempt1 claim e15f6947209feb0b1256fb6ca199b8e9cc74b9d3 pushed; no duplicate claim

Implementation 6c8bbe194337c7c2afb141047d24aeeeb23c48ca pushed to origin/task/ARCH-066-SHARED-011; implementation tree clean. Parent report committed/pushed on matching task branch after this edit; exact report commit available in Git history. Registry immutable5.8.0 remains unchanged; no package publication in011. Submodule gitlink staged: no. Main branches merged/pushed: no. Package version changed/published: no. Consumers modified: no. Enabled task started: no.

## Architect Review
### Review Status
Pending
### Review Notes
Definition authored after actual local/remote/canonical ID scan;011/012 unused, existing007–010 identities/claims preserved.
### Reviewed Files
Shared outreach variables/template contracts and Background brand/preparer tests read-only.
### Validation Reviewed
Repository implementation validation pending.
### Architecture Conformance
Bounded Shared-owned compatibility correction, separate publication and consumer adoption.
### Follow-up
Stop after review submission. Do not publish or implement consumers.

## Normative implementation amendment — exact contract (2026-11-08)

This section overrides discretionary wording above (“minimal”, “inspect”, “as needed”). Implement this contract without selecting a different field layout, fallback rule or limit. Preserve frontmatter, claims and historical reports. Definition amendment only; no source implementation/publication is asserted.

### Owned touch points

All paths below are relative to moda-interact-shared:

| Path | Required change |
|---|---|
| `src/commerce/outreach/template-contracts.ts` | Add the three exported schemas and inferred types below; add optional `preparedBrand` and `preparedBrandMedia` to InitialOutreachRenderInputSchema. Keep schemaVersion 1 and existing fields/result shape. |
| `src/commerce/outreach/variables.ts` | Resolve saved text/dimensions from preparedBrand; resolve brand URL semantics independently of headerMedia by fixed role mapping below. Preserve boundedText checks for every resolved text. |
| `src/commerce/outreach/render.ts` | Ensure malformed input returns INVALID_REQUEST without throwing; validate prepared tenant/role before assignment/render; retain current IMAGE/TEXT fallback and frozen rendering. |
| `src/commerce/outreach/contracts.ts` | Make existing `https` refinement total: use URL.canParse before new URL; invalid URLs fail schema validation rather than throwing. Preserve existing HTTPS/no credentials/2048 bound; do not change unrelated URL semantics. |
| `src/commerce/outreach/index.ts` | Export PreparedOutreachBrandSchema, PreparedOutreachBrandMediaSchema, PreparedOutreachBrandMediaItemSchema and corresponding inferred types from the public outreach entrypoint. Preserve every existing export. |
| `src/commerce/outreach/render.test.ts` | Add exact positive/negative goldens below using existing frozen registration rehash helper. |
| `src/commerce/outreach/contracts.test.ts` | Add strictness, bounds, legacy input and malformed URL safeParse regressions. |
| `src/commerce/outreach/test-fixtures.ts` | Add reusable same-shop saved brand/media fixture helpers; preserve existing no-brand fixture and expected bytes. |
| `src/commerce/outreach/README.md` | Document exact fields, limits, host authority, missing-data refusal, old-input compatibility and body/header distinction. |
| `scripts/validate-commerce-outreach.mjs` | Extend existing built public JS/declaration smoke to corrected fields/types/renderer; retain previous checks. |

No package version/lockfile/export-map/build-tool change is required: existing outreach entrypoint already exists. No database, Background, Commerce or MCP edits in this task. Background's `recovery-template-brand.ts` and four positive preparer fixtures are read-only compatibility evidence. If an owned symbol has moved, record its actual path before editing; no parallel renderer.

### Exact additive Zod declarations

Use existing `z`, `hostId` and `https`. Types are `z.infer<typeof ...>` with names matching schemas without `Schema`.

```typescript
export const PreparedOutreachBrandSchema = z.strictObject({
  shopId: hostId,
  brandName: z.string().max(200).nullable(),
  logoAltText: z.string().max(200).nullable(),
  logoWidth: z.number().int().min(1).max(10000).nullable(),
  logoHeight: z.number().int().min(1).max(10000).nullable(),
  squareLogoAltText: z.string().max(200).nullable(),
});
export const PreparedOutreachBrandMediaItemSchema = ReadyMediaSchema;
export const PreparedOutreachBrandMediaSchema = z.strictObject({
  logo: PreparedOutreachBrandMediaItemSchema.nullable(),
  squareLogo: PreparedOutreachBrandMediaItemSchema.nullable(),
  coverImage: PreparedOutreachBrandMediaItemSchema.nullable(),
});
// Add to existing strict InitialOutreachRenderInputSchema:
// preparedBrand: PreparedOutreachBrandSchema.nullable().optional(),
// preparedBrandMedia: PreparedOutreachBrandMediaSchema.nullable().optional(),
```

Every property within a supplied object is required; null denotes unavailable. Omitted/null top-level projections mean no prepared brand data. No default/coercion, dynamic record, catchall, extra brand URL field, implicit dimension conversion, schemaVersion bump or new result/reason enum. Dimensions are finite integers 1..10000 inclusive; text bounds use JavaScript string.length (UTF16 units), measured before trimming. All objects reject unknown keys. Existing hostId trimming/bounds remain unchanged.

ReadyMediaSchema remains the existing strict `{shopId, role, status:'READY', kind:'R2_DERIVATIVE', httpsUrl}` with HTTPS URL <=2048 and no username/password. For new brand-media entries also refuse URL fragments and URLs without a dotted hostname as MEDIA_NOT_READY after parsing. Do not impose a fixed R2 host/domain or infer R2 ownership from URL text: the trusted host resolves approved ready derivatives using its configured media owner. Shared makes no network/database calls. New projection never accepts raw/original ShopBrand URLs or media status/kind alternatives.

### Validation and resolution order

1. safeParse complete input first. Structural/type/bound failures return `{kind:'refused',reasonCode:'INVALID_REQUEST'}`; malformed URL input must never throw. Do not include raw data in errors/logs.
2. Before assignment/fallback, supplied preparedBrand.shopId must equal evaluation.shopId; mismatch returns IDENTITY_MISMATCH. Every nonnull supplied media item must have matching shopId and exact key/role: logo→LOGO, squareLogo→SQUARE_LOGO, coverImage→COVER_IMAGE. Wrong tenant/role or extra fragment/hostname restriction above returns MEDIA_NOT_READY. Validate supplied entries even if the selected template does not reference them; do not silently ignore a conflicting projection.
3. Existing approved-assignment, WABA, locale/hash/binding checks and IMAGE fallback keep their existing ordering after these new checks. headerMedia remains exclusively the existing IMAGE-header source (including CHECKOUT_PRODUCT); do not synthesize it from preparedBrandMedia and do not use it as a brand BODY binding fallback. Missing headerMedia can use only the existing approved textFallback projection.
4. For semantic `shopBrand.brandName`, `shopBrand.logoAltText`, `shopBrand.squareLogoAltText`, read only the matching preparedBrand field and pass through existing boundedText(value,200). Null/absent/blank/control text, unpaired surrogate or `{{`/`}}` refuses BINDING_VALUE_UNAVAILABLE when bound. Do not fall back to variables.shopName, category, domain, original URL or model prose. Preserve existing boundedText forbidden-control expression; no new text sanitization that silently changes content. Valid text emits trimmed text.
5. For shopBrand.logoWidth/logoHeight read only preparedBrand numeric field. Null/absent bound value refuses BINDING_VALUE_UNAVAILABLE; valid integer emits String(value), no units, rounding or locale formatting. Invalid nonnull values were rejected in step1.
6. Map shopBrand.logoUrl→preparedBrandMedia.logo.httpsUrl, squareLogoUrl→squareLogo.httpsUrl, coverImageUrl→coverImage.httpsUrl. Missing/null requested item returns MEDIA_NOT_READY. Emit exact validated URL, no rewriting/encoding for text parameters. All three may coexist in one BODY with no IMAGE header. They may coexist with a different authorised headerMedia role. CHECKOUT_PRODUCT is never a brand-media role.
7. Ordinary shop.name continues using variables.shopName; shop.categoryName/customer/checkout/offer semantics remain unchanged. Old valid inputs/templates with no shopBrand bindings render byte-identically. Old brand-binding inputs without the new projections now explicitly refuse instead of substituting generic shopName or borrowing header media. This deliberate safety correction must be documented; consumers adapt in their own tasks after SHARED-012 publication.
8. Preserve output parameter order, frozen fingerprint/provenance, encoded checkout button semantics, exact 4096 substituted BODY limit and existing full renderedText/result bounds. No arbitrary callback, raw passthrough or fallback from invalid brand evidence. Result parsing remains mandatory.

### Exact acceptance fixtures

Use approved same-shop frozen registration with recomputed matching content/binding hashes and ready evaluation. Fixed brand fixture: shopId=`shop-1`, brandName=`Saved brand`, logoAltText=`Saved logo alt`, logoWidth=100, logoHeight=200, squareLogoAltText=`Saved square alt`. variables.shopName=`Generic merchant` intentionally differs. Assert all five brand fields resolve to saved values; four existing Background compatibility cases are preserved, not replaced by refusals.

- One BODY binds brandName/alt/width/height/square-alt and yields exact ordered text parameters `[Saved brand, Saved logo alt, 100, 200, Saved square alt]`; assert exact full renderedText and all unchanged provenance values.
- TEXT-only BODY binds all three media roles using distinct `https://assets.example/logo.webp`, `/square.webp`, `/cover.webp`; assert exact ordered URLs and headerPreview null. Repeat with IMAGE CHECKOUT_PRODUCT header using fourth ready URL: correct header plus all three BODY URLs, no collision.
- Bound absent/null brand text/dimension → BINDING_VALUE_UNAVAILABLE; bound absent/null role media → MEDIA_NOT_READY. Generic shopName and headerMedia must not satisfy those bindings. Missing optional unused data does not refuse.
- Text 200 units valid; 201 invalid request; empty/whitespace/control/brace/unpaired-surrogate within schema bound refuses BINDING_VALUE_UNAVAILABLE when referenced. Dimensions 1 and10000 render;0,-1,10001,1.5,NaN,Infinity,string fail schema; null remains structurally valid. No coercion.
- Wrong prepared brand tenant → IDENTITY_MISMATCH; wrong media tenant/key-role → MEDIA_NOT_READY even unused. Wrong status/kind, unknown fields, missing required nested keys, invalid URL/HTTP/credentials/>2048 → INVALID_REQUEST. Valid parsed URL with fragment or undotted hostname → MEDIA_NOT_READY for preparedBrandMedia. Add safeParse malformed URL regression and render malformed URL returns typed refusal, never throws.
- Existing no-brand golden exact bytes unchanged; IMAGE unavailable uses valid approved TEXT fallback; no fallback refuses MEDIA_NOT_READY. Invalid registration/hash/locale still refuses. BODY4096 succeeds and4097 refuses MESSAGE_TOO_LARGE using otherwise valid frozen fixture/substitutions. All three INITIAL offer purposes retain existing behavior; unrelated-product promotion remains refused.

### Required validation and consumer handoff

Run `npx tsx --test src/commerce/outreach/*.test.ts`, `npm run typecheck`, `npm run build`, and `npm run validate:commerce-outreach`. Extend built public runtime/declaration smoke using the existing script's mechanism to import new schemas/types and render a positive brand fixture; no source/internal-dist consumer imports. Record exact results and accepted source commit. No publication in011.

Completion report must supply an explicit mapping for BACKGROUND-002/COMMERCE-002: existing same-shop saved brand columns populate preparedBrand (missing columns null); authorised ready derivatives populate fixed media slots with matching roles; existing IMAGE header remains headerMedia; no saved-brand fallback to generic name. Hosts retain trusted shop/database/media resolution, while Shared checks supplied identity/shape and renders. Consumers adopt only the exact accepted immutable SHARED-012 artifact; publish/adopt/deploy are separate steps. Background's remaining72 failures require same-task investigation and revalidation and are not waived by these goldens. No production admission/credit/consent/send changes, new table or standalone identity follows from this correction.

## Pre-existing amendment reconciliation — 2026-11-08
Launcher stopped on the pre-existing task-only uncommitted normative append above. Architect inspected it against the frozen-binding correction/checkout-led scope: compatible, no competing execution claim or source edits. Under developer explicit implementation/sync/task-publication authorization, preserve and publish the exact append as governing scope; no discard, claim or attempt increment occurs in this checkpoint. Canonical launcher performs the next claim. Completion remains developer; no release/consumer/main/live action authorized.

## Architect fixture reconciliation — 2026-11-08
The exact fixture vectors above conflict with preserved existing approved INITIAL selection: BODY must contain shop.name and exactly one checkout.itemsSummary. Four new brand/media-only fixtures were correctly refused DEFINITION_UNAVAILABLE before variable resolution; runtime policy must not be weakened. Architect resolves only this fixture contradiction under authorized task governance. Use valid rehashed frozen templates retaining these two mandatory BODY bindings, followed by the exact ordered five saved-brand or three media bindings requested above. Assert full complete parameter array, full renderedText/body bytes and provenance, with the requested brand/media vectors as exact ordered contiguous subsequences. One-field boundary/missing-value fixtures likewise retain mandatory bindings. CHECKOUT_PRODUCT header remains independent. Repeat published5.8 reproduction with these valid templates so a definition refusal is not misreported as missing resolver behavior. Exact schema layout/limits/refusal order, all other goldens, existing selection/hash rules and task scope remain unchanged. This reconciliation is not a new claim or implementation acceptance; Attempt1/history retained.

## Architect Review — Attempt1 (2026-11-08)
### Review Status
Accepted. Status remains review, unchanged Attempt1, executor/claimed_at cleared. Explicit developer completion pending via `/moda_developer_update ARCH-066-SHARED-011 complete`.
### Review Notes
Independently reviewed implementation6c8bbe194337c7c2afb141047d24aeeeb23c48ca and report134379e614b89613dc71f1bd8935dcc0e3902d87, both published/clean on mirrored canonical branches. Exact three strict exported schemas/types and optional preparedBrand/preparedBrandMedia match normative layout/limits. Mandatory savedbrand fields cannot borrow generic name; four missing bindings now render correctly. Fixed-role BODY media stays independent of IMAGE/CHECKOUT_PRODUCT header, validates supplied tenant/role even unused before assignment/fallback and rejects fragments/undotted hosts. Existing HTTPS refinement is total; malformed input refuses without throwing. Shared remains pure, host authorization/media resolution remain outside. No generic dictionary, callback, service import or parallel renderer.
### Reviewed Files
Outreach template-contracts/variables/render/contracts/index, tests and fixture helpers, README, installed public validation script. Reviewed exact saved-field/body-media full parameter arrays/body/provenance/button goldens, missing/null/type/UTF16/dimension and tenant-role/URL negative fixtures. Existing INITIAL approved selection, hashes, one checkout.itemsSummary/shop.name requirements and offer purposes preserved.
### Validation Reviewed
Required outreach suite79/79, zero skips/failures; declared typecheck; ESM/declaration production build; installed local-pack public JS and declaration smoke all pass. New three runtime schemas/types resolve through public outreach export, positive full7brand parameters/hash and legacy evaluator/product imports verified. Valid published5.8 reproduction proves four missing bindings, wrong generic-name fallback, unavailable BODY media and malformedURL throw. Initial invalid5brand-only fixtures were reconciled by explicit architectff55693, preserving mandatory bindings/full7or5arrays; no runtime policy weakening. Existing Zod normalization precedes exact validated URL-byte emission. diffcheck passes; no package/version/lockfile/export-map/buildtool change.
### Architecture Conformance
Conforms to exact preserved pre-existing normative amendment81d2842ef and fixture reconciliation. Prepared packet establishes primary root, exact sibling parent/implementation matching task branches, remote/main sync and recursive submodules ready/noentries; pushed Attempt1 claime15f6947. Source/report independently remote verified; parent gitlink unchanged. Registry5.8.0 remains immutable/unfixed; accepted source is not a published correction. No standalone007/008/MCP002 resurrection, release, consumer change, main/live/follow-on execution.
### Follow-up
SHARED012 remains Pending until explicit011completion, then separate immutable corrected publication. Background002 stays Blocked on012 and its unresolved same-task72failures; this Shared acceptance does not waive or certify consumer/admission/credit/send/Studio integration. Consumers populate exact saved columns/nulls and authorized ready fixed-role derivatives, keep headerMedia independent, then adopt only exact accepted012artifact. Terminal system/manual gates remain. No dependency promotion from Accepted review alone.

## Developer Completion Decision — 2026-11-08
Developer explicitly invoked `/moda_developer_update ARCH-066-SHARED-011 complete`. Accepted review750d5119ad4c1158b7048cc367ff2b7760f06b54 and implementation6c8bbe194337c7c2afb141047d24aeeeb23c48ca verified clean and remote-published. Complete at unchanged Attempt1; executor/claimed_at remain null. Existing79tests/typecheck/build/installed-public-smoke passing evidence retained without rerun. SHARED012 newly Ready, Attempt0/unclaimed; Background002 remains Blocked on corrected publication and unresolved72failures. No npm/main/live/consumer/follow-on execution.
