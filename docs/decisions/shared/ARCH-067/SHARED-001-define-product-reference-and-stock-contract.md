---
id: ARCH-067-SHARED-001
architecture_id: ARCH-067
title: Define shared references, stock facts and WhatsApp composition
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
depends_on: []
enables: ["ARCH-067-SHARED-002"]
created: 2026-11-09
updated: 2026-11-09
---
# Define shared references, stock facts and WhatsApp composition

## Objective and binding specification
Implement the owned portion of [ARCH-067](../../../architecture/ARCH-067-product-reference-and-current-stock-parity.md). Every schema, mapping, persistence, rendering, diagnostic and compatibility rule there is normative. No merchandise-specific behavior. Dependencies must be complete before execution.

## Exact work and touch points
Owned touch points: src/commerce/schemas.ts; product-context.ts and tests; instructions.ts; runner/graph/nodes/invoke-model.ts; runner/index.ts; runner/preflight.ts; model/openrouter-model-client.internal.ts serialization tests; presentation/facts.ts, fact-messages.ts, schemas.ts, compose.ts, render.ts, index.ts; commerce public index.ts and public import validation scripts. Implement every Shared contract in the architecture document; extend exported types and generated tool output JSON schemas through existing generation. Do not create parallel inventory facts/renderers in hosts. Test built public runtime and declarations, not only source imports. Tests: legacy context/product fixtures; selected options arbitrary names (height, finish, volume as well as color); presentation ordered [20,3] survives recency sorting [3,20]; ambiguous labels require clarification; all stock states and0; invalid/negative/unsafe count normalization semantics; context size/TTL/ownership; no stale count authority; exact WhatsApp body and locale/length boundaries. Run npm run typecheck, npm run build and targeted product-context/presentation/runner/model tests using repository scripts. Record accepted source/build archive provenance for publication.

## Exact Zod additions and public API (binding)
Use the existing `zod` dependency and `z.infer`; no second validation library, hand-written duplicate host interfaces or new database schema. This section specifies the implementation, not an already implemented API.

### 1. `src/commerce/schemas.ts`
Add before CommerceProductSchema:
```ts
export const CommerceProductStockSchema = z.discriminatedUnion('status', [
  z.strictObject({
    status: z.literal('KNOWN'),
    quantity: z.number().int().min(0).max(Number.MAX_SAFE_INTEGER),
    scope: z.enum(['PRODUCT', 'VARIANT']),
  }),
  z.strictObject({ status: z.literal('NOT_TRACKED') }),
  z.strictObject({ status: z.literal('UNAVAILABLE') }),
]);
export type CommerceProductStock = z.infer<typeof CommerceProductStockSchema>;
export function normalizeCommerceStockQuantity(value: unknown): number | null {
  return typeof value === 'number' && Number.isSafeInteger(value)
    ? Math.max(0, value) : null;
}
```
Add exactly this property to existing CommerceProductSchema; retain all existing properties:
```ts
stock: CommerceProductStockSchema.optional(),
```
Do not coerce numeric strings, null, booleans or decimals. No quantity/default on NOT_TRACKED/UNAVAILABLE: strict schemas reject such fields. Numeric negative provider quantities normalize to0 before schema parsing, but a negative wire quantity fails validation. `available` retains its independent current behavior. Public CommerceToolOutputs search/get already reference CommerceProductSchema: retain that relationship; update their generated descriptor projections rather than introducing separate schemas.

### 2. `src/commerce/product-context.ts`
Replace the inline reference object with these exported schemas, using existing `id` (string1..128) and `date` (UTC z.iso.datetime({offset:false})):
```ts
export const CommerceProductReferencePairSchema = z.strictObject({
  productId: id,
  variantId: id.nullable(),
});
export type CommerceProductReferencePair =
  z.infer<typeof CommerceProductReferencePairSchema>;
export const CommerceConversationProductReferenceSchema =
  CommerceProductReferencePairSchema.extend({
    title: z.string().min(1).max(512),
    observedAt: date,
    selectedOptions: CommerceProductSelectedOptionsSchema.optional(),
  });
export const CommerceProductPresentationSchema = z.strictObject({
  references: z.array(CommerceProductReferencePairSchema).max(3).refine(
    rows => new Set(rows.map(r => JSON.stringify([r.productId,r.variantId]))).size === rows.length,
    'Duplicate presented product',
  ),
  presentedAt: date,
});
export type CommerceProductPresentation =
  z.infer<typeof CommerceProductPresentationSchema>;
```
Import CommerceProductSelectedOptionsSchema from schemas.ts. It is the existing canonical normalizer: at most16 selected name/value pairs; reuse its optionLabel constraints and normalization exactly, without introducing color/size enums. Each existing optionLabel replaces CR/LF/tab sequences with one space, trims, requires1..128 characters and rejects remaining C0/C1 control characters; selectedOptions normalizes non-arrays to[], examines first16 entries, drops invalid labels and deduplicates exact name/value pairs. Keep reference title/observedAt unchanged; native identity validation still runs in the outer context.

The complete context object shape before superRefine is exactly:
```ts
z.strictObject({
  schemaVersion: z.literal(1),
  shopId: id,
  conversationId: id,
  platform: z.enum(['SHOPIFY','WOOCOMMERCE']),
  references: z.array(CommerceConversationProductReferenceSchema).max(20),
  updatedAt: date,
  presentation: CommerceProductPresentationSchema.optional(),
})
```
Retain the existing platform-specific native-ID and32768-byte checks. Extend superRefine to reject any presentation pair absent from references and any duplicate pair in references. A zero-length presentation is valid and explicitly clears the last displayed list; absence means legacy/no recorded list. No stock/price/description fields are admitted in context. Freshness remains a merge/read concern, using the existing24-hour window and identity.now (not Date.now inside pure helpers).

Expose this exact signature:
```ts
export function recordCommerceProductPresentation(
  context: CommerceConversationProductContext,
  pairs: readonly CommerceProductReferencePair[],
  identity: CommerceProductContextIdentity,
): CommerceConversationProductContext;
```
Algorithm: first merge(context,[],identity) to enforce ownership/freshness; safeParse a copied pairs array against presentation references schema; reject duplicate/missing/expired pairs with Error('PRODUCT_PRESENTATION_INVALID'); preserve supplied order; attach presentedAt=new Date(identity.now).toISOString(); leave general references/updatedAt unchanged; parse the complete result. Do not silently truncate supplied pairs. Final size failure also raises PRODUCT_PRESENTATION_INVALID. All successful replies record the actual rendered ordered pairs (empty when no product is displayed), so 'first' never refers to an older list hidden by a later reply.

In mergeConversationProductContext, copy normalized selectedOptions from each canonical observation when supplied; retain previous optional value when a newer observation omits it, replace when newer observation supplies it (including []). Preserve previous presentation only while presentedAt and every referenced pair remain fresh and retained; otherwise remove it entirely. Merge must not create/reorder presentation from search results. When trimming for byte budget, remove presentation first, then existing oldest-reference trimming. Validate final object. Existing exact-ID/title resolver signature and MISSING/AMBIGUOUS behavior remain; no fuzzy automatic selection introduced.

### 3. `src/commerce/presentation/facts.ts`
Extend the existing CommerceProductFactSchema with exactly:
```ts
stock: CommerceProductStockSchema,
observedAt: DateSchema,
```
Import both existing schemas from their canonical modules; retain current IDs,title,description,attributes,options,selectedOptions unchanged. `verifyCommerceProductFacts` retains its current signature/result union and exact-pair checks. In each verified fact set:
```ts
stock: product.data.stock ?? {status:'UNAVAILABLE'},
observedAt: product.data.observedAt,
```
No freshness claim is made merely by parsing observedAt: the host must supply the fresh authorized read stipulated in the contract. The model's answer schema stays unchanged: productDetailSelections is at most3 unique productId/variantId pairs, never stock quantities. Reuse PRODUCT_DETAILS rather than adding an INVENTORY answer kind.

In fact-messages.ts add a typed per-supported-locale stock message record (all existing supported locales required; no English fallback). English source strings are exactly: PRODUCT known `Available quantity: {quantity}.`; VARIANT known `Available quantity for this option: {quantity}.`; NOT_TRACKED `Exact stock quantities are not tracked.`; UNAVAILABLE `Exact stock quantity is currently unavailable.` Render after existing description/attribute/option lines. Localize quantity with Intl.NumberFormat(locale,{useGrouping:false,maximumFractionDigits:0}); replace only the quantity placeholder, with no interpolation of model prose. Keep existing partial-description notices. Stock unknown must not force referral when product identity/details are otherwise verified.

### 4. Exports, JSON and compatibility tests
Export all new schemas/types/functions from commerce public index.ts; presentation index.ts retains/export updated fact schemas. Generated declarations must resolve through published `@modainteract/moda-interact-shared/commerce`. No root/private-path import required. Do not change response disposition enum, presentation selection schema, existing optional fields or database schemaVersion.

Add exact parser boundary tests: quantities0 and Number.MAX_SAFE_INTEGER pass; -1,0.5,MAX_SAFE_INTEGER+1,'2',null fail KNOWN wire parsing; NOT_TRACKED with quantity fails; stock omission on legacy product passes but verified fact yields UNAVAILABLE; legacy context lacking both additions passes; reference21/presentation4/duplicate/missing pair fails; ordered presentation preserves input independent of lexical IDs; selectedOptions uses existing normalization; serialized32768/32769 boundary; future/expired observations and foreign shop/conversation fail existing read/merge fences. Built OpenRouter request JSON must include ordered presentation plus selectedOptions, without stock as persisted reference authority. Test successful composition then failed next turn retains state, and successful no-product reply clears presentation. Preserve all existing wrapper/body limits and public schema export checks.

## Acceptance criteria
All owned requirements above and architecture contract are implemented and verified. List every actual changed path and test result. Shared behavior must be imported through published public exports; no copied cross-repository source. Unknown inventory remains distinct from zero. Existing authorization, checkout ownership, WhatsApp composition and replay rules pass regression checks. No unresolved design choices may be silently substituted; report a concrete contract conflict before implementing an alternative.

## Non-goals
No inventory mutation, new database table, token-refresh redesign, new template approval/WABA validation, category sequencing redesign or budget increase.

## Completion Report
Status: Ready for Review. Implementation `467cc1abf5afc467f73861f9830430524022bacd` committed/pushed/remotely matched on task/ARCH-067-SHARED-001; clean implementation tree. No registry publication. Final validation chain exit0.

Final build provenance: exact source above, final ESM+DTS build after near-cap and oneOf/const corrections; retained canonical dist and scripts-disabled local archive `/private/tmp/arch067-shared001-validated-5.10.0.tgz`, SHA256`44a81c0468a0a6dd62c0df75a12fa5877038028435f897057874c0478eb138a8`, integrity`sha512-XURWUjRFmBG6K5hGTltTBqcBQXfm3/h6giI5PLa8LbglWWSaDSXWXW0GdBkzMAcRoNOPwYmXSFdlE6wxj/MGrA==`, 453336bytes/145files. Pack receipt `/private/tmp/arch067-shared001-pack.json`. Package/lock metadata unchanged at5.10.0; archive is validation candidate only, not registry5.10.0 or a version selection for002. Later publication must verify source/dist byte parity and select its own unused version under its task; no build/test reruns authorized merely for release validation.

Acceptance matrix:
- Stock contract: schemas.ts exports exact optional product stock union/type and pure safe-integer normalizer (negative→0; malformed/decimal/unsafe→null); legacy products parse unchanged. Product outputs derive canonical JSON through existing Zod generation, no duplicate provider mapping or bootstrap script.
- Reference contract: product-context.ts adds optional selectedOptions and ordered presentation under unchanged version1,32768bytes/20refs/24h/native-ID/ownership checks. Pair uniqueness/membership checked; record helper records exact supplied order/time, throws invalid pairs, applies existing deterministic tail eviction after insertion and invalidates whole presentation if any pair evicted. No prices/stock authority persisted. Context tests include20,3presentation vs3,20recency, arbitrary Height/Finish/Volume, ambiguity, TTL/eviction, and exact32760-byte insertion edge.
- Model context: runner/instructions.ts explains ordinal latest successful presentation and stale option labels; invoke-model.ts includes presentation and selectedOptions. Real runner projection and OpenRouter serialization tests retain exact order/labels. Host owns recording only after successful composition and atomic reply persistence; Shared does not invent host state.
- Verified facts/composition: presentation/facts.ts projects current provider stock and observedAt (existing DateSchema), omitted legacy stock→UNAVAILABLE, exact selection max3 unchanged. Existing deterministic WhatsApp composition/wrapper/body limits retained. All20supported locales distinguish known0/product vs selected variant/not tracked/unknown; attributes/descriptions/options still rendered. Tests assert exact known0body, locale catalogues, safe fallback and prior authorization/replay/checkout regressions.
- Canonical output usability: amendment implemented in purpose-output.ts with bounded typed scalar const and exactly-one oneOf semantics, same depth8/nodes256/properties128/schema+result32KiB/string4096/array128/2..4branches. Mixedunion/constenum/unknownkeys/malformedscalar/nonfinite/unsafeconst rejected; no new regex/eval or lossy projection. Tests compile real generated get/search outputs and validate complete stock states/counts/legacy omissions plus hostile/overlapping branches. Historical purpose-output.fixtures.json untouched; new purpose-output.accepted015.fixtures.json generated from exact accepted015source a19519e4 serves baseline equality with sole optional stock delta. Baseline proof `/private/tmp/arch067-shared001-purpose-baseline.log`: accepted get/search true atdepth7/8, stock initially false dueoneOf/const, exact stripped-stock equality; bounded correction closes introduced gap.
- Public contract: existing commerce/presentation wildcard exports expose additive types/functions; installed public runtime/declaration smoke imports stock/context/fact APIs, exercises record helper and generated-stock canonical compiler with0; built clean-process runner/Commerce and browser-safe presentation checks retained. No service source imports.

Changed paths: src/commerce/schemas.ts; product-context.ts/.test.ts; runner/instructions.ts; runner/graph/nodes/invoke-model.ts; runner/runner.test.ts; model/openrouter-model-client.test.ts; presentation/facts.ts/.test.ts; presentation/fact-messages.ts; purpose-output.ts/.test.ts; purpose-output.accepted015.fixtures.json; scripts/validate-commerce-outreach.mjs. Existing public wildcard indices, composition wrappers, preflight context merge and OpenRouter request.context serializer already delegate correctly, so no duplicate bodies added.

Validation: final affected product-context, presentation, runner, model, purpose-output/profile suite168/168 PASS; `npm run typecheck` PASS. Final `npm run build` ESM+DTS, `npm run validate:commerce-entrypoints`, `npm run validate:commerce-presentation`, and `npm run validate:commerce-outreach` installed public runtime/declarations all PASS, final command chain exited0. Logs `/private/tmp/arch067-shared001-final-tests.log`, `...-typecheck.log`, `...-build.log`, `...-entrypoints.log`, `...-presentation-public.log`, `...-installed-public.log`. Earlier test harness missing AbortSignal fixed; stock canonical compatibility gap escalated and resolved by exact architect amendment; initial157required tests were not used to waive it. No test failures waived.

Compatibility/deviations: stock wire optional; new verified fact stock+observedAt canonical, no model quantity accepted. Context remains v1 and legacy JSON valid without rewrite. Actual instructions path runner/instructions.ts (task shorthand corrected). Shared has no owned generated bootstrap artifact script: existing canonical output generation directly includes stock, verified in built public smoke; hosts own persisted release/bootstrap fingerprints and diagnostics. Pure Shared helpers introduce no competing logger; provider-read/final-verification diagnostics, fresh deduplicated reads and rolling writer gate are consumer tasks. Readers must deploy before literaltrue COMMERCE_PRODUCT_REFERENCE_V2_WRITE_ENABLED writers; this task does not activate it or change host files. No deployment/stock mutation/database cleanup/reset/seed, consumer, release/version, main or follow-on work.

Launcher evidence: canonical root /Users/kwadwoadomafriyie/project/moda-interact-workspace; parent /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-067-SHARED-001; implementation /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-067-SHARED-001; bothtask/ARCH-067-SHARED-001. Both created, remoteFFnot-needed/mainalready-current; parentbaselineb2ba305d8e6c75faa1a29446be6db87953fac57c, implementationbaseline5d253a339aec3104ec9c18adb79f93d58fad7b2b. Recursive sync/updatepassed, noentriesready; no dependencies gatepassed. Launcher claimAttempt1codex2026-11-09T05:02:52Z33488a38639cdbd0be133406a2a40d6a525d407e pushed; startup/claim not repeated. Not-reviewed preexisting review read in full, no ChangesRequested items. Shared/default/another-task checkout not mutated/reused. ArchitectReview untouched; developercompletion retained.


## Architect Review
Status: Not reviewed.


## Canonical stock output subset compatibility amendment — 2026-11-09
Actual accepted5.10baseline generatedget_product/searchproducts descriptors compile with depth7/8; currentdescriptors differ ONLY by optionalstock and fail because exact normative Zoddiscriminatedunion emits oneOf/stringconst. This is task-introduced usability gap, not excusedbaseline. Bounded same-owner touchpoints additionally include src/commerce/purpose-output.ts, purpose-output.test.ts and an exactgeneratedacceptedbaseline testfixture ifneeded. Preserve canonical generatedrepresentation; do not lossyconvertoneOf toanyOf or change exactStockSchema.
Support scalarconst (string,boolean,null,finite typednumber/safeinteger only; no object/arrayconst) and oneOf exactly-one-matchingbranch semantics. Preserve existinganyOf and reject mixedunionkeywords/unsupportedfields; preventconst/enum combinations bypassingconstraints. Keep ALL resource/securitylimits unchanged: depth8,256nodes,128properties,32KiBschema/result,4096implicitstring,128array,2..4unionbranches, code-ownedfixedpatterns/no callerregex/code. This is keywordcompatibility, not budgetincrease.
Requiredproof: realgeneratedget/search descriptorscompile and validatefullproducts withKNOWNzero/positive/safe-max PRODUCT/VARIANT, NOT_TRACKED/UNAVAILABLE and legacyomittedstock; malformedstock/extra fields reject. OverlappingoneOf matchesreject; malformed/mixedconst/unions and hostiledepth/node/property/byte/patternlimitsreject. Comparecurrentdescriptor to actualaccepted5.10generatedbaseline plus EXACToptionalstockdelta; retain historicalauditedfixture unchanged aslegacyvalidatorvectors, do not erase unrelateddelta or fabricatebaseline. Record exact baselineproofreceipt /private/tmp/arch067-shared001-purpose-baseline.log. Rerun affectedpurpose/stock/context/runner/model tests, typecheck/finalbuild/publicJS+declarations, and retain acceptedfinalartifact provenance; no release/consumer/source-main changes.


## Architect Review
### Review Status
Accepted
### Review Notes
Reviewed actual source467cc1abf5afc467f73861f9830430524022bacd/report4dd608776ab1a3ecb6fa4a1101dc40088c66d805. Independently verified canonicalsourceclean/remotehashmatched. Prepared parent/implementationisolation, Attempt1claim33488a386, sync/submodule/nodeps packet conforms; no sourceworkbyarchitect. Earlier Notreviewedplaceholder historical.
### Reviewed Files
schemas.ts; product-context.ts/tests; runner/instructions and invoke-model; modelserialization/runner tests; presentationfacts/messages/tests; purpose-output compiler/tests/exactacceptedbaselinefixture; installedpublicvalidationscript.
### Validation Reviewed
Finalexpanded168/168PASS; typecheck; finalESM+DTSbuild; cleanprocesspublicentrypoints, browserpresentation, installedpublicruntime/declarations includinggeneratedget/searchstockcompiler. Orderedpresentation[20,3] retainedagainstrecency[3,20], selectedOptionsarbitrarynames, ambiguity/identity/TTL/eviction, near-cap32768tail-eviction/wholepresentationinvalidation, nostockpersistence, modelrequestserialization; stockKNOWNzero/safemax/scopes/NOT_TRACKED/UNAVAILABLE/legacyomission, malformedcountnormalizer andlocalizedstockcomposition/lengthregressions. Actualacceptedbaseline get/searchcompiled(depth7/8); onlyoptionalstock introducedoneOf/constfailure. Narrowapprovedcorrection supports exact-one unions/scalarconst withallprior caps/fixedpatterns unchanged; oldhostilevectors/overlap/malformedkeywords andhistoricalfixtures retained. Realgeneratedschema/runtimepubliccompile verified, no source-onlyproof.
### Architecture Conformance
Exactoptionalstock schema andpurepublicquantitynormalizer; mandatoryverifiedstock+DateSchemaobservedAt, no modelquantityauthority. V1contextcaps20refs/3presented/24h/32768bytes/ownership retained, no category-specific/Englishordinalparser. ExistingSharedcomposition/WhatsAppwrapper used; purehelpersno competinglogger, providerdiagnostics/atomicreplycontextwritegate remainconsumer-owned. Publicwildcardexports/runtime/declarations validated; existingproductoutputs dynamicallygenerateadditivestock. No budgetincrease, migration/provider/inventorywrite, version/publication/consumer/main/live work.
### Follow-up
Accepted atReview unchangedAttempt1; claimcleared; explicitdevelopercompletionpending via /moda_developer_update ARCH-067-SHARED-001 complete. SHARED002remainsPendinguntilactual001Complete; no consumersunblocked. Retain finalvalidatedarchive /private/tmp/arch067-shared001-validated-5.10.0.tgz SHA25644a81c0468a0a6dd62c0df75a12fa5877038028435f897057874c0478eb138a8 and canonicaldist/sourceprovenance for separaterelease, notpublishedfeatureavailability. Reader-firststockdeployment and referencewritegatefalseuntilbothreaders required; terminalsystemreceipt ownsoperationalgate.


## Explicit developer completion decision — 2026-11-09
Developer invoked /moda_developer_update ARCH-067-SHARED-001 complete. DurableAcceptedAttempt1review77917fb2d69a3efbd47cf99b26db4991f766bf35/source467cc1abf5afc467f73861f9830430524022bacd independentlyverifiedclean/remotelypublished. Complete unchangedAttempt1/claimnull. Required168/typecheck/build/publicchecks evidence retained without reruns. SHARED002soleprerequisite satisfied, ReadyAttempt0/unclaimed; allconsumers remainPendingpublication. No tests/release/main/live/consumer/follow-onexecution. Reader-firststockdeployment and referencewritegatefalseuntilbothreaders mandatory.
