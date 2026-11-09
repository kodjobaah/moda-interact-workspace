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
status: review
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
