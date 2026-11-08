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
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
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
- [ ] Reproduce valid alt/dimension/body-media incompatibility and mandatory-brand distinction using exact published5.8.0 entrypoint.
- [ ] Define minimal strict optional prepared brand/media data with explicit host/Shared boundaries and preserve prior no-brand input compatibility.
- [ ] Implement deterministic supported bindings and fail-closed validation; no service-local imports or side effects.
- [ ] Add positive/negative compatibility goldens and exact full text/parameter/provenance checks.
## Interfaces / Contracts
@modainteract/moda-interact-shared/commerce/outreach; InitialOutreachRenderInputSchema, renderInitialOutreachPreview, existing frozen SemanticKeySchema and strict ready-media contract. Extend documented data contract explicitly; do not pretend existing5.8 supports new inputs.
## Dependencies
ARCH-066-SHARED-010 Complete, immutable5.8.0 source/exports. No dependency on blocked Background or terminal system tests.
## Enables
ARCH-066-SHARED-012; consumer correction remains on original BACKGROUND002 after corrected publication.
## Acceptance Criteria
- [ ] Valid saved logoAltText, squareLogoAltText, logoWidth/logoHeight bindings render exact expected parameters in INITIAL without copying Background algorithms.
- [ ] Mandatory saved brandName cannot be satisfied by generic shop.name fallback; missing/invalid values refuse.
- [ ] Authorized READY same-shop logo/square/cover URL body bindings preserve valid behavior; missing/wrong-shop/wrong-role/raw-original media refuses.
- [ ] Existing nonbrand inputs, image/TEXT fallback, approved registration/binding integrity, provider parameter encoding and full-body bounds remain compatible.
- [ ] Public runtime and declaration imports include corrected strict inputs; malformed input never weakens validation or leaks secrets.
## Validation
- [ ] Focused outreach renderer/schema compatibility tests, including positive existing Background binding cases and negative tenant/type/value cases.
- [ ] Existing outreach evaluator/render regressions, typecheck and production build per repository scripts.
- [ ] Package public JS/declaration import smoke; record exact commands/results. No live calls.
## Stop Condition
After defined work/acceptance/required validation is complete, publish Completion Report at review and return control to moda_architect. Stop; no enabled task, release or consumer execution implicit.
## Implementation Notes
Exact initial evidence: Shared src/commerce/outreach/variables.ts switch afterbrandName/3URLs falls through; template-contracts.ts includes the4unimplemented fields. Background src/services/recovery-template-preparation/recovery-template-brand.ts supports saved type/cap semantics. Reuse approved Shared logger only if logging changes. If more contract work is required, return precise gap rather than expand scope. Use canonical launcher dedicated worktrees when execution is explicitly invoked; definition only now.
## Completion Report
### Status
Not Started
### Files Changed
None
### Work Completed
None
### Validation Results
Not run; definition only.
### Deviations
None
### Assumptions
Hosts supply authorized saved data; Shared verifies deterministic structure/caps and tenant/media binding.
### Unresolved Issues
Published5.8.0 cannot preserve named valid bindings; BACKGROUND002 cannot be Accepted until corrected artifact is available and its same-task checks pass.
### Architectural Concerns
No standalone scope or live send authorization follows from rendering.
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
