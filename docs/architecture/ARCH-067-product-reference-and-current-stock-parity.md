---
id: ARCH-067
title: Remember product identity and verify current stock
status: in_progress
coordinator: moda_architect
created: 2026-11-09
updated: 2026-11-09
---
# ARCH-067 — Remember product identity and verify current stock

## Binding decisions
This corrects ARCH-066 product follow-ups for arbitrary merchandise on Shopify and WooCommerce. Studio local execution and Background → MCP must expose identical canonical facts and use the same Shared selection verification and WhatsApp composition. No new table, capability, inventory-write operation, template registration or WABA validation. Preserve existing checkout-led production ownership and initial-outreach behavior. Never infer inventory from price, availability, attributes or an earlier reply.

## Shared stock contract (normative)
Add and publicly export CommerceProductStockSchema in src/commerce/schemas.ts; add `stock: CommerceProductStockSchema.optional()` to CommerceProductSchema for legacy outputs. New adapters always emit it. Exact schema:
```ts
export const CommerceProductStockSchema = z.discriminatedUnion('status', [
 z.strictObject({status:z.literal('KNOWN'), quantity:z.number().int().min(0).max(Number.MAX_SAFE_INTEGER), scope:z.enum(['PRODUCT','VARIANT'])}),
 z.strictObject({status:z.literal('NOT_TRACKED')}),
 z.strictObject({status:z.literal('UNAVAILABLE')}),
]);
```
Quantity means provider-reported aggregate sellable inventory for this exact selected native identity, not a reservation or promise to fulfill. Known zero remains distinct from unavailable. Negative provider inventory normalizes to zero; availability remains independently mapped, including backorders. Decimal, unsafe or malformed quantities become UNAVAILABLE, never rounded. Omitted legacy stock becomes UNAVAILABLE during fact verification. Product facts carry stock plus observedAt using the existing DateSchema; no model-supplied quantity is accepted as evidence.

Shopify: add inventoryQuantity and inventoryItem { tracked } to every variant projection (search, category search, product get, variant get), response parsers and mapping. tracked false => NOT_TRACKED; tracked true + safe integer inventoryQuantity => KNOWN/VARIANT; missing tracking/count => UNAVAILABLE. A product-only read with multiple variants must not report the first variant as product-wide stock: quantity is UNAVAILABLE until an exact variant is selected. Keep exact variant-parent membership checks. Woo: add manage_stock to existing product/variation field allowlists alongside stock_quantity. Explicit boolean true + safe integer => KNOWN with PRODUCT for a simple product or VARIANT for a variation. Explicit false => NOT_TRACKED. Variation manage_stock='parent' => UNAVAILABLE (no invented variant count); variable parent => UNAVAILABLE. Missing/null/invalid data => UNAVAILABLE. No sum of variants, no location total invented, no stock mutation.

## Persisted reference contract (normative)
Keep context schemaVersion 1 and existing storage. Add optional selectedOptions using existing CommerceProductSelectedOptionsSchema to each reference. Add optional top-level `presentation: z.strictObject({references:z.array(z.strictObject({productId:id,variantId:id.nullable()})).max(3),presentedAt:date})`. Existing v1 JSON remains valid. The same 32768-byte context, 20-reference, 24-hour freshness and shop/conversation/platform fences remain. Validate presentation pairs are unique and present in context references. Expired/evicted pairs remove the presentation as a whole. Never persist stock/prices as reference authority.

Export `recordCommerceProductPresentation(context, pairs, identity)`; accepts at most three unique existing pairs, preserves supplied order, records identity.now, throws PRODUCT_PRESENTATION_INVALID for missing/duplicate/foreign pairs. Call only after successful verified composition and persist atomically with the actual composed assistant reply. General search result order must not become presentation order. Failed turns leave previous context/presentation unchanged. Product details/options and recommendation renderers supply exact ordered pairs actually rendered; no text parsing. Preserve current recency sorting for general references.

Extend ModelRequest context.productReferences with selectedOptions and presentation. Existing OpenRouter serialization already includes request.context: retain it. Explain in Shared instructions that ordinal references address the latest successfully presented list (not general references); labels/options identify candidates, never current stock. Multiple candidates => ask clarification. No arbitrary English-only color/ordinal parser or clothing-specific fields. The model supplies native pairs to existing get_product; provider membership validation remains authoritative. Exact IDs are not fabricated from a title or URL.

## Verified answer and WhatsApp contract (normative)
Reuse PRODUCT_DETAILS/productDetailSelections (maximum three) and verifyCommerceProductFacts; extend CommerceProductFactSchema with stock and observedAt. Fetch exact selected pairs fresh in the current turn's presentation verification phase, deduplicated within that phase. Reject foreign/unobserved selections using existing rules. renderCommerceProductFacts adds localized stock lines for KNOWN/NOT_TRACKED/UNAVAILABLE using existing supported-language catalogues, including explicit scope for variant counts. It must render 0, distinguish unknown from zero, and never claim a product total for variant stock. Existing description/attribute/option rendering retained. Use existing composeCommerceResponse and configured WhatsApp wrapper; enforce its existing BODY limits and safe fallback behavior, no new free-text bypass. Studio displays that same composed body; Background sends that body through existing moderation/outbox fences. Do not depend on model prose to preserve counts.

## Diagnostics
At authorized product read/final verification log native productId, variantId, stock status/scope, reason enum (KNOWN, NOT_TRACKED, MISSING_PROVIDER_FIELD, INVALID_PROVIDER_QUANTITY, PARENT_MANAGED, VARIANT_REQUIRED), context reference count, presentation count and correlation IDs. Do not log tokens/raw provider bodies/customer text. Quantity need not be logged. Reuse existing logger/event families; diagnostic additions must not replace error codes or change retry policy.

## Rollout and compatibility
Additive wire fields require Shared correction publication before consumers. Both consumers pin the exact published artifact/integrity recorded by SHARED-002; never guess next npm version. Deploy readers supporting new JSON before writers emit presentation/selectedOptions; consumer tasks retain emission disabled until both Studio and Background readers are deployed, with an operational gate documented in the system-test receipt. Exact host gate: server-only `COMMERCE_PRODUCT_REFERENCE_V2_WRITE_ENABLED`, enabled only by the literal string `true`, defaults false, in Commerce and Background. False strips the two additive reference fields before persistence (retain existing IDs/titles/timestamps), but readers always accept them; true persists them. This is a rolling-deployment switch, not a merchant setting or schema-version change. Add it to both repositories’ .env.example and deployment documentation. Never strip identity checks or stock verification when false. No database migration: existing Background JSONB stores the complete context object and schemaVersion stays1; Studio stores it in existing Redis conversation record. Old JSON loads without rewriting. Do not run cleanup/reset/seed against test or production as part of this work.

## Test determinism and public dependencies
Contract tests use scripted model replies with exact native pair selections, fixed clock and provider fixtures; do not assert success from nondeterministic live model phrasing. Add model request serialization assertions for the latest presentation order and selectedOptions. Optional manual model smoke is additional evidence only. Stock/reference normalization must live in Shared exported pure helpers `normalizeCommerceStockQuantity(value)` (safe integer -> max(0,value), otherwise null), with host provider-specific tracking/scope mapping only; do not duplicate generic count validation. Existing product result output contracts and persisted tool/release schemas must include the additive stock field; update generated bootstrap artifacts and verification fingerprints through their existing scripts, never directly patch database releases. No sync/apply command runs automatically. For schema equality tests compare the built public Shared schema used by both adapters.


## Ownership and implementation clarification — 2026-11-09
SHARED001 owns the pure public stock/count/reference/fact/composition APIs and Shared runner/modelrequest propagation. Actual instructions file is src/commerce/runner/instructions.ts, superseding the task shorthand instructions.ts. Generated producttool JSONschemas derive from CommerceProductSchema via existing generation; prove the built public output schema includes stock, do not invent a Sharedbootstrapgenerator. Provider-specific tracking/scope/diagnostic reason mapping belongs Commerce/MCP; Background/Commerce own finalverification lifecycle logging and atomic reply/context persistence. Shared purehelpers do not instantiate a competinglogger or persist stockauthority; hosts retain existing Sharedstructuredlogger/eventfamilies and correlation. No new telemetrysignal or infrastructuretopology is required: bounded fields extend existing domain diagnostics; no transport/gateway task. The explicitserverwritegate and deployment-order checklist remain consumer/system-test responsibilities, not enabled in Shared001.

## Decisions / Tasks
| Task | Owner | Status | Depends On |
|---|---|---|---|
| ARCH-067-SHARED-001 | moda_shared | Complete / Accepted Attempt1 | None |
| ARCH-067-SHARED-002 | moda_shared | Complete / Accepted Attempt1 | ARCH-067-SHARED-001 |
| ARCH-067-COMMERCE-001 | moda_commerce | Complete / Accepted Attempt1 | ARCH-067-SHARED-002 |
| ARCH-067-MCP-001 | moda_mcp | Complete / Accepted Attempt1 | ARCH-067-SHARED-002 |
| ARCH-067-BACKGROUND-001 | moda_background | Complete / Accepted Attempt2 | ARCH-067-SHARED-002, ARCH-067-MCP-001 |
| ARCH-067-SYSTEM-TEST-001 | moda_system_test | Ready / dependency-ready; manual-gated; Attempt0 unclaimed | ARCH-067-COMMERCE-001, ARCH-067-BACKGROUND-001, ARCH-067-MCP-001 |

Terminal systemvalidation remains developer-manual-gated after all actual prerequisitesComplete; no automaticconsumer/system execution or architectureImplemented claim. Existing publishedwire/contracts and persistedv1JSON require compatible reader-first rollout, no schema migration.


## Canonical stock output subset compatibility amendment — 2026-11-09
Actual accepted5.10baseline generatedget_product/searchproducts descriptors compile with depth7/8; currentdescriptors differ ONLY by optionalstock and fail because exact normative Zoddiscriminatedunion emits oneOf/stringconst. This is task-introduced usability gap, not excusedbaseline. Bounded same-owner touchpoints additionally include src/commerce/purpose-output.ts, purpose-output.test.ts and an exactgeneratedacceptedbaseline testfixture ifneeded. Preserve canonical generatedrepresentation; do not lossyconvertoneOf toanyOf or change exactStockSchema.
Support scalarconst (string,boolean,null,finite typednumber/safeinteger only; no object/arrayconst) and oneOf exactly-one-matchingbranch semantics. Preserve existinganyOf and reject mixedunionkeywords/unsupportedfields; preventconst/enum combinations bypassingconstraints. Keep ALL resource/securitylimits unchanged: depth8,256nodes,128properties,32KiBschema/result,4096implicitstring,128array,2..4unionbranches, code-ownedfixedpatterns/no callerregex/code. This is keywordcompatibility, not budgetincrease.
Requiredproof: realgeneratedget/search descriptorscompile and validatefullproducts withKNOWNzero/positive/safe-max PRODUCT/VARIANT, NOT_TRACKED/UNAVAILABLE and legacyomittedstock; malformedstock/extra fields reject. OverlappingoneOf matchesreject; malformed/mixedconst/unions and hostiledepth/node/property/byte/patternlimitsreject. Comparecurrentdescriptor to actualaccepted5.10generatedbaseline plus EXACToptionalstockdelta; retain historicalauditedfixture unchanged aslegacyvalidatorvectors, do not erase unrelateddelta or fabricatebaseline. Record exact baselineproofreceipt /private/tmp/arch067-shared001-purpose-baseline.log. Rerun affectedpurpose/stock/context/runner/model tests, typecheck/finalbuild/publicJS+declarations, and retain acceptedfinalartifact provenance; no release/consumer/source-main changes.


## Shared contract implementation review — 2026-11-09
SHARED001AcceptedReviewAttempt1; explicitdevelopercompletionpending. Source467cc1abf5afc467f73861f9830430524022bacd clean/published.168targetedtests/typecheck/finalESM+DTS/cleanpublicentrypoints/browserpresentation/installedruntime+declarations pass. Canonicalpurposecompiler nowaccepts exactgeneratedstockoneOf/const with all previoussecurity/resourcecaps unchanged; historicalauditedfixtures retained, acceptedbaseline optionalstockdelta proven. Contextv1selectedoptions/presentation preservesorder/ownership/TTL/32768cap; near-cap deterministic tail eviction invalidateswholepresentation ifpairremoved. No release/consumers enabled; SHARED002Pendinguntil001Complete.

### Explicit strict-reader rollout sequencing
Optionalstock permits NEW readers to consume legacyoutputs; it does not make OLDstrict readers accept stock. Deploy Background/Studio readers using acceptedpublishedcontract before enabling/deploying MCPstockwriter; localStudio stockreader/writer upgrade together. Keep COMMERCE_PRODUCT_REFERENCE_V2_WRITE_ENABLED false untilbothreference readersdeployed, thenenableonlyliteraltrue afteroperationalgate recordedinsystemreceipt. No separate stockflag or newinfrastructureintroduced; this clarifies existingreader-first compatible deployment sequence. No rollout or gateenablement occursinShared001.


2026-11-09 explicitcompletionfrontier: SHARED001CompleteAcceptedAttempt1 source467cc1a/review77917fb2cleanpublished; SHARED002ReadyAttempt0/unclaimed release-only, no execution. Allconsumers/systemtasksPending, referencegatefalseandreader-before-stockwriter sequencepreserved; architectureInProgress.


## Immutable stock/reference publication review — 2026-11-09
SHARED002AcceptedReviewAttempt1, explicitdevelopercompletionpending; public5.11.0 exactrelease-source1ad0d7c47c0a9e1d3d12072b62e238aec1cc92fe versionmetadataonly. Accepted001source/dist reused140filesbyte-identical, no implementationreruns. Downloaded453336byte/145file archiveSHA25628db9055f58355fb9779b190beb0eccda356e20fd9a52cf0b753cd1564789309 andintegrity sha512-VwVUszfUz0Bgs0alcnjJYK0m5bY7Jt9Nb/LuPRPgrWqk/JCFYqrWbzf7rnsXP2Z8EWlf4yfojbibnOQ4/9YyOg== matchregistry/localreviewedbytes; installedpublicruntime/declaration imports verify stock/reference/canonicalcompiler andallpriorpublicexports. ConsumerstatusesremainPendinguntil002actuallyComplete. Publishedavailability isnot deploymentapproval: readersbeforeMCPstockwriter, referencewritegatefalseuntilbothreaders, no source/main/live/consumerexecution.


2026-11-09 explicitreleasecompletionfrontier: SHARED002CompleteAcceptedAttempt1, exact5.11.0receiptverified. Commerce001/MCP001ReadyAttempt0/unclaimed; Background001PendingMCP001; SystemTest001Pendingconsumerclosures/manualgate. No consumerexecution/deployment/gateenablement/tests/npm/main/live. Reader-firststock and defaultfalse referencegateuntilbothreadersremainmandatory.

## Reconciled consumer frontier — 2026-11-09
MCP001 Complete1ecd2038e; COMMERCE001 Complete72ef2d55f; Shared002 Complete5.11.0. BACKGROUND001 Ready at Attempt0/unclaimed. SYSTEM-TEST001 remains Pending on Background001/manual-gated. No implementation/deployment/gate enablement or architectureImplemented claim.

2026-11-09 Background explicit completion frontier: BACKGROUND001 Complete / Accepted Attempt2, sourceee342a14b3e5311fc34b2898b8ec65226aa30647, passingreviewb9507041b. Commerce001/MCP001 independently Complete. SYSTEM-TEST001 Ready/dependency-ready at unchanged Attempt0, no executor/claim; developer manual gate retained. Architecture remains in_progress until terminal evidence. Reader-first deployment and default-false context emission gate remain mandatory. No system execution, deployment, main integration or operational gate enabled.
