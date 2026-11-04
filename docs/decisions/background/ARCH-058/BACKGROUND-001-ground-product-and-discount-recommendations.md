---
id: ARCH-058-BACKGROUND-001
architecture_id: ARCH-058
title: Ground inbound recommendations, shipping answers and store redirects
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-058-MCP-002
- ARCH-058-MCP-003
- ARCH-058-COMMERCE-001
enables:
- ARCH-058-SYSTEM-TEST-001
created: '2026-11-04'
updated: '2026-11-04'
---

# ARCH-058-BACKGROUND-001: Ground inbound recommendations, shipping answers and store redirects

## Architecture and execution boundary

Parent: `docs/architecture/ARCH-058-commerce-agent-product-discovery.md`. Binding contracts: `docs/architecture/ARCH-058/contracts.md`. Read first: `docs/architecture/ARCH-058/implementation-handoff.md` and its `execution-baseline.json`. Definition revision: **3**. This revision replaces the previous implementation directions; it does not claim execution or change lifecycle metadata.

Use the launcher-prepared parent and Background implementation worktrees and its dependency/synchronization packet. Follow `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/task-definition-materialization.md`, `docs/agent-validation-execution-policy.md` and `docs/observability/shared-logging.md`. Do not rerun launcher discovery, reopen completed tasks or derive paths from another task worktree. MCP-002, MCP-003 and COMMERCE-001 must be accepted and Complete before claim. The user has identified MCP-001 as already under development; this task does not modify its definition or implementation.

## Objective

Make inbound Commerce answers use the published instructions and verified current-shop product, discount and shipping observations. The model selects identifiers and an answer disposition; Background validates them and composes the entire controlled customer message. Preserve the existing runner, final-response envelope and single wrapper/moderation/admission/send path.

## Fixed baseline and reuse decisions

| Observed source | Required change; no rediscovery or alternative design |
|---|---|
| Background `package.json`/lockfile pin Shared `3.0.0`; SHARED-002 has accepted and published `4.0.0` | Pin exactly `4.0.0`, using the receipt in the common handoff. The runner is `1.1.0`. Do not rerun the publication task, choose `latest` or retain the old conditional-4.0.0 wording. |
| `src/commerce/host.ts::execute` already reads the owned Conversation and CheckoutRecovery, then invokes `runCommerceTurn` | Reuse that read, grant path, client and finalization point. Extend its Shop projection with `platform`; do not load a second initial recovery or invoke the outreach agent. |
| `src/services/recovery-offers/initial-outreach-agent-context.service.ts` already validates published prompt rows | Reuse its exact configuration/revision query semantics in the new conversation context module. Its attempt-specific service is read-only and must not be called with fabricated IDs. |
| `src/services/recovery-policy.service.ts::RecoveryPolicyService.resolve` already resolves merchant policy and active override | Call the real service with the full Prisma instance. Do not implement a second policy reader or treat a failed read/missing test delegate as `NONE`. |
| `initial-outreach-offer.eligibility.ts` and `.combinations.ts` contain the conservative pure rules | Extract the neutral pure rules as specified below; keep outreach report/attempt validation in its existing adapter. Do not build a second discount engine. |
| Host descriptors and authorization compare only published `toolId`/`toolRevisionId` today | Deliberately discriminate Shared's published/built-in union at all named callsites below. |
| Host `assertCurrent` checks version/lease; processor separately checks HUMAN takeover | Extend the same host state query with control fields. Keep all processor checks and their order. |
| `vitest.config.ts` excludes `tests/integration/**` outside the disposable mode | Add the exact isolated host-suite config below. A direct default-config invocation of `host.test.ts` is not valid evidence. |

Database schema/forward migration, taxonomy source/import and Commerce publication are prerequisites, not new work here. Use an accepted Database revision containing `ded8f14a60182f6b1443640f012caf0089b8a44c` and any later accepted migrations required by the current Background baseline. Update the `database` gitlink only when that prerequisite is missing; never reset a newer accepted descendant backwards or edit schema/migration bytes. If a declared accepted prerequisite's actual source/export is absent, use the handoff's integration stop condition rather than rebuilding that prerequisite in Background.

## Authorized files and functions

All paths in this section are relative to `moda-interact-background`. Preserve unrelated edits and existing task histories. New runtime names must describe commerce behavior, not contain architecture IDs.

| MODIFY | Exact responsibility |
|---|---|
| `package.json`, `package-lock.json` | Exact Shared `4.0.0` dependency and the two test scripts below. No other dependency upgrade. |
| `database` | Accepted gitlink only; normal Prisma generation. |
| `src/commerce/host.ts` | Context loading, mixed descriptors, observation recording, one budget ledger, finalization and result projection at the existing `execute` callsites. |
| `src/commerce/grants.ts` | Keep `wireGrant`, `readGrant`, `validateRelease`, `persistGrant` and Shared `manifestMatchesGrant`; update type narrowing only where required. Preserve create/P2002-winner behavior. |
| `src/commerce/mcp-client.ts::encodeCommerceContext` | Append the validated conversation-purpose `toolContext` to the existing assertion after validation; preserve separate outreach encoding and transport. |
| `src/commerce/host-diagnostics.ts`, `src/commerce/mcp-client.ts` | Preserve existing original safe source-failure/cause data through the host boundary and emit it via the existing Shared logger, as specified below. |
| `src/commerce/recovery-instructions.ts::RECOVERY_INSTRUCTIONS` | The trusted routing, selection, budget and historical-basket instructions below. No new agent or classifier. |
| `src/agents/types.ts::CommerceAgentResult` | Intersection with the private optional candidate property only. |
| `src/agents/initial-outreach-offer.eligibility.ts`, `.combinations.ts`, `.types.ts` | Exact pure-rule extraction/aliases below; preserve public outreach inputs/results. |
| `src/agents/initial-outreach-offer.graph.ts` | Explicitly reject the new optional-unavailable union branch at its four discount-output parses. No outreach decisions change. |
| `src/services/recovery-offers/current-outreach-offer-revalidation.service.ts` | Explicit unavailable-branch discrimination before accessing parsed discount details. It remains failure/incomplete evidence, never a newly allowed neutral success. |
| `src/services/conversation-turn-processor.service.ts` | Add the private candidate field to `getResult`'s return type and pass it at the existing `composeAiOutbound` call. No other processor change. |
| `src/services/conversation-wrappers/{compose-ai-outbound,contracts,service}.ts` | AI-only candidate propagation/validation and length-only candidate selection at the existing composition stage. |
| `tests/integration/commerce/{host.test,host.fixture}.ts` and existing `host-suites/{authority,grants,evidence,budgets,language}.ts` | Extend the existing loopback MCP/model fixture and register the focused new suites; keep existing assertions. |
| `tests/unit/commerce/{host-diagnostics,mcp-client}.test.ts`, existing outreach eligibility/combination/graph and current-offer-revalidation tests | Contract-union, actual logging sink and extraction compatibility regressions. |
| `tests/unit/services/conversation-wrappers/{compose-ai-outbound,service}.test.ts`, `tests/unit/services/conversation-turn-processor/ai-wrapper.cases.ts` | Candidate pass-through, exact replay, one read, refusal and unchanged single-send ordering. |

Create the following focused production modules under `src/commerce/recommendations/`. These exports are private Background APIs, not Shared/MCP contracts:

| Module | Required exports/responsibility |
|---|---|
| `context.ts` | `loadRecommendationContext`, `refreshRecommendationContext`, `RecommendationContext`; prompt/policy/basket projection and source identity. |
| `observations.ts` | `TurnRecommendationObservations`; validated turn-local product, option, detail and shipping records, latest-by-arguments lookup and a monotonic controlled-composition flag. |
| `disposition.ts` | `readRecommendationSelection`; pick/parse only the four owned detail fields and apply their cross-field/business rules. |
| `fallback-selection.ts` | `selectFallbackRecommendation`; pure selection of at most one already observed/proposed product for a soft disposition. It does not perform I/O. |
| `eligibility.ts` | `DiscountEvaluationPurchase`, `DiscountEligibilityDecision`, `ObservedDiscount`, `evaluatePurchaseDiscount`; the extracted neutral evaluator described below. |
| `combinations.ts` | `DiscountCombinationDecision`, `selectCompatibleOffers`; the existing reciprocal/pair/subset algorithm with neutral types. |
| `money.ts` | `decimalToMinorUnits`, `sumPurchaseSubtotal`, `formatObservedMoney`; exact decimal comparisons and bounded presentation, not a checkout price engine. |
| `revalidation.ts` | `finalizeRecommendation`; stable refresh planning, one budget counter, current-context checks and immutable validated render facts. |
| `shipping.ts` | `selectShippingPresentation`; fixed requiresShipping facts and verified policy references only. |
| `render.ts` | `renderRecommendationReply`; one complete localized message using only the finalized render facts. |
| `candidates.ts` | `buildReplyCandidates`; full, one-product and minimal complete bodies from the same facts. |
| `messages.ts` | `recommendationMessages`, `recommendationMessageKeys`; complete typed fixed-message catalogue for the 20 Shared locales. |

Create unit tests with matching module basenames under `tests/unit/commerce/recommendations/`; focused host suites `instruction-composition.ts`, `recommendations.ts`, `recommendation-revalidation.ts`, `recommendation-failures.ts`, `fallback-responses.ts`, `shipping-responses.ts`; `tests/integration/commerce/recommendation-context.integration.test.ts`; and the three synthetic fixture files `tests/fixtures/commerce/{product-recommendations,shipping-information,fallback-responses}.v1.json`. Create the test-only `vitest.commerce-host.config.ts` specified below. No other production module is needed.

Read-only: `src/commerce/evidence.ts`, `referral.ts`, `live-budget.ts`, `src/services/conversation-language.service.ts`, `conversation.service.ts`, `recovery-policy.service.ts`, the outreach context/price-reconciliation services, wrapper `{repository,selection,projection,render}.ts`, `src/agents/commerce.agent.ts`, `src/workers/whatsapp.worker.ts` and `scripts/test-integration.mjs`. The worker's existing `getResult: result => result` already preserves the new internal field; no worker edit is required.

## Implementation contract

### 1. Context: exact reads, bounds and instruction order

1. In the existing initial `conversation.findUnique` include, extend only `checkoutRecovery.shop.select` to `{id:true, domain:true, platform:true}`. Retain the current Conversation/recovery/customer ownership checks. Reject a non-AI initial control mode; capture its `controlRevision` together with the current inbound version and processing lease. Reuse the returned recovery `id`, `shopId`, `generation`, `currency`, `lineItems` and historical fields; do not requery them at initial load.
2. Invoke `loadRecommendationContext` after the existing retained grant/manifest validation and the definition of `assertCurrent`, before the first `available()` call and `runCommerceTurn` (the existing LIVE AbortSignal is already in scope). The mixed descriptor array may be built first; define `available`/its policy checks after context initialization. It receives the already read trusted row, resolved grant identity, actual Prisma instance, environment and signal. In parallel read the prompt configurations below and `new RecoveryPolicyService(db).resolve(shopId, now)`, with `assertCurrent` before and after. This is one prompt read plus the existing policy service's reads, not a per-tool prompt lookup.
3. Prompt query: `commerceAgentConfiguration.findMany({where:{environment,OR:[{scope:"PLATFORM",shopId:null},{scope:"SHOP",shopId}]},select:{scope:true,shopId:true,activePromptRevisionId:true,activePromptRevision:{select:{id:true,status:true,promptText:true,prompt:{select:{scope:true,shopId:true}}}}}})`. Require exactly one Platform row and at most one Shop row. Platform must have an active matching `PUBLISHED` revision, scope PLATFORM, null owner, nonblank text of at most 8000 characters. Shop absence or null active revision means no additive Shop instruction; a present active revision must match id/PUBLISHED/SHOP/current shop and the same text bound. Malformed/duplicate/missing Platform configuration throws a nonretryable `CommerceHostError("INCOMPATIBLE_VERSION")` with its specific context reason. A database exception propagates with cause; it is not an empty prompt.
4. Pass `hostInstructions: [...RECOVERY_INSTRUCTIONS, platformText, ...(shopText ? [shopText] : [])]`. Shared already places its kernel before this array, and the pinned response contract and release-frozen feature behavior after it. Do not add prompt text to untrusted `context`, append tool/knowledge text to these instructions or duplicate feature instructions. Platform/Shop text is loaded once per turn; prompt activation affects the next turn, not an in-flight runner.
5. Policy projection is exactly `{mode: policy.recoveryOfferMode, authorisedDiscountIds: mode === "FIXED" && policy.fixedShopifyDiscountId ? [policy.fixedShopifyDiscountId] : []}` plus `policy.source` for diagnostics. IDs are the existing canonical catalogue row IDs used by ARCH-052, not `providerDiscountId` or a coupon code. Require the real policy delegates in fixtures; the service's test-oriented missing-delegate fallback must not be used. A missing settings row follows the existing resolver's normal NONE semantics; an exception does not. FIXED without a selected ID authorizes no offer. `offerSnapshot` text is not current eligibility evidence.
6. Project a basket only from the owned recovery's actual `lineItems` array, at most 100 entries. Line keys are the existing `line-0001`, `line-0002`, ... order. Retain valid bounded product/variant IDs, positive safe-integer quantity, bounded title, and nullable category/collection IDs; absent/malformed optional facts stay null. Never synthesize a variant, default an unknown basket quantity to1 or use stored line prices/sale flags as current observations. Use the existing `fingerprintRecoveryPricingBasket` with actual shop/recovery/generation/currency/lineItems for the source fingerprint. A missing/oversized/unprojectable basket becomes `basket:null` with a bounded internal reason; it does not disable independent PRODUCT_ONLY recommendations. Catch only the projector's documented validation failure, not arbitrary database/programming errors. ADD/REPLACE requires a usable complete basket identity.
7. `RecommendationContext` contains trusted shop/provider/turn/grant identity, policy, prompt revision IDs, nullable basket `{generation,fingerprint,currency,lines}` and verified store reference. Expose only the bounded policy/basket projection and relevant existing recovery context to the model; never include token, credential, configuration row or raw source JSON. The existing 131072-byte context/history bound remains enforced by Shared. Build the store reference from the trusted Shop.domain: accept its existing HTTPS form or prefix a bare domain with `https://`, preserve a legitimate path, reject credentials/port/query/fragment/control characters/IP/localhost using the existing safe-product-URL validator. No model/tool URL becomes the store root. An invalid trusted store reference is `INVALID_INPUT`, not a guessed link.
8. `refreshRecommendationContext` is finalization-only: select the same recovery by `{id,shopId}` with `generation,currency,lineItems`, and rerun the same policy service. Only do the recovery read when a retained proposal uses the owned basket. Compare the original generation/fingerprint; a changed basket removes its dependent ADD/REPLACE or basket-suggestion proposals. Policy mode/authorized-ID change is a guarded DENIED outcome, not optional unavailability. Do not reload prompts, wrapper configuration or initial-outreach state.

### 2. Mixed grants, authorization and source observations

1. In `encodeCommerceContext`, retain the outreach branch unchanged. For a conversation, first validate the existing `CommerceAssertionSchema` object as today. Separately parse `CommerceConversationToolContextSchema` with `{purpose:"CONVERSATION",conversationId:turn.conversationId,inboundVersion:turn.inboundVersion,grantId:grant?.id ?? null}`, then encode `{...assertion.data,toolContext}` under the existing header. Do not add toolContext before the strict assertion parse. Grant null is initial resolution only; the retained client uses the persisted grant ID.
2. Build runner descriptors from the existing deduplicated published capability descriptors followed by `manifest.builtInTools`. `CommerceManifestSchema`, `CommerceConversationGrantSchema`, Shared `manifestMatchesGrant`, `isBuiltInTool`, `isTrustedCommerceBuiltInDescriptor` and `isTrustedCommerceBuiltInGrant` are available in 4.0.0 and must be used. Do not reconstruct canonical built-in hashes or assert a locally invented name-only permission.
3. Update both `available` and `RunnerTool.isAuthorized`: published branch matches toolId/revision/name/version and sorted capability keys as today; built-in branch matches exact kind/name/version/hash plus Shared's trusted-descriptor/grant check. Both require current `tools/list` presence and exact `{name,description,inputSchema}` equality. The retained descriptor set is not rewritten when policy changes: locally return false from built-in `isAuthorized` when the current context mode is NONE or FIXED has no authorized ID, so the model cannot cause a discount RPC in those states. Before a FIXED details call, reject an offerId outside that exact authorized list. MCP remains responsible for the fresh execution-time policy check; do not add another per-tool Background policy query. Reject duplicate names, published/built-in collisions, extra tools and changed hashes. Keep release validation and existing retained-grant immutability. A legacy runner1.0.0 grant remains incompatible; no automatic reset, widening or database deletion.
4. Instantiate one `TurnRecommendationObservations` after grant resolution. Every authorized runner `execute` records through it only after outer-envelope and exact canonical `CommerceToolOutputs[name]` validation. Recognized sources are precisely product get/search, discount options/details and shipping information under their accepted identities. Key by shop/provider/conversation/inboundVersion/grant/release, descriptor identity, canonical parsed arguments and result identity. Keep an immutable copy and sequence number; latest successful result for identical arguments wins. Do not parse arbitrary same-shaped results from another tool into these registries.
5. Product observations map `(productId,variantId)` to their actual get/search call. Options map offerId to the current mode and canonical offer; details map the requested offerId to its result, requiring `details.offer.offerId` equality and a matching options observation before a promotion. Shipping maps exact parsed `{productId,variantId}`, including null/null, to its own result. Normal null product/details and optional UNAVAILABLE replace the previous matching positive record with that outcome; no older success is used as a fallback. Options mode differing from trusted context is DENIED. A malformed canonical success is INCOMPATIBLE_VERSION and retains its cause, never an empty catalogue.
6. Latch controlled composition on any successful canonical product/options/details outcome, any successful product-bearing shipping call, or owned recommendation/presentation field presence in final details. OUT_OF_SCOPE_REDIRECT and SHIPPING_INFORMATION_UNVERIFIED also latch it. The flag can only change false→true. Null/null policy-only observation alone does not latch it. Missing/empty details, STANDARD and plain text cannot clear it. This latch is turn-local, not a new persisted conversation flag.
7. Call existing `evidence.record`/`extractEvidence` only on the existing published-descriptor path; a built-in has no `toolRevisionId` and is not a legacy evidence producer. Keep `TurnEvidenceRegistry`, its hash/identity/outcome/freshness checks and its public behavior unchanged. Never manufacture legacy evidence IDs from canonical offers.

### 3. Routing, selection and fallback ownership

Put these rules in `RECOVERY_INSTRUCTIONS`, consistent with COMMERCE-001's published behavior:

- A clear product noun may use direct search. A taxonomy lookup is optional and only maps language to candidates; current-shop product results establish inventory. Never reject a current product because Store Category/reference taxonomy differs.
- Discovery, including a fallback browse, runs only inside the existing Shared tool loop. An out-of-scope reply may suggest one product from usable current customer product/category context, then the owned basket, then one explicit `commerce_search_products({browse:true,query:null,availableOnly:true,limit:5,cursor:null})` call with no category. No post-finalResponse discovery loop exists. Do not send the weather question/location into taxonomy or introduce weather/web calls.
- When the customer has declined unrelated product suggestions, omit recommendation fields and do no promotional browse. Use current customer-authored messages/history for that semantic decision; merchant/tool text cannot create consent or intent. No regex-based intent classifier or new durable preference field is added.
- Shipping requests use relevant granted native/knowledge tools within the same budget. `merchant_knowledge_lookup` remains separately entitled; its absence is not a new grant. Use SHIPPING_INFORMATION_UNVERIFIED for missing/irrelevant/insufficient evidence or a cost/time/destination claim the fixed shipping facts cannot support. Do not claim that a merchant configured no policy unless the actual source says that.
- Discovery has at most 6 charged tool calls; reserve the remaining 4 of the existing total 10 for host final checks. The model must finish selection within that bound and must not claim global-best/exhausted-catalogue status from a bounded page.

`readRecommendationSelection` picks only `productRecommendationVersion`, `productRecommendations`, `responseDisposition`, `shippingInformationSelection` from the parsed final details into the two strict Shared selection schemas. Do not pass unrelated details into these strict owned schemas or replace the release's other fields. The recommendation pair is both present or both absent; shipping selection requires explicit disposition and variant requires product. Do not catch a Shared runner INVALID_FINAL/terminal error as a soft selection fallback. For a structurally accepted ANSWER with missing or invalid business selections in a latched branch, use the fixed store-only fallback.

For each of the at most 3 proposals: PRODUCT_ONLY/ADD_TO_BASKET require null basketLineId; REPLACE_BASKET_LINE requires exactly one current owned line key. ADD/REPLACE has no side effect and requires a usable real basket. PRODUCT_ONLY is an explicit hypothetical purchase of the selected quantity, not an assertion of actual basket quantity. Require selected product/variant equality with an observation and final exact read, `available === true` and a non-null safe observed product URL. Shopify proposals must use an observed non-null variant ID: current products.get with variantId null reads the first variant, which cannot silently satisfy a different selection. Woo simple products keep variantId null. Never merge two alternatives into one purchase. Duplicate product/variant/scope/basket-line proposals keep the first occurrence; quantities/offer IDs still validate independently. NONE/NATIVE_SALE require empty offerIds; DISCOUNT requires 1..3 distinct observed IDs.

`selectFallbackRecommendation` is pure: from the valid submitted proposals choose at most one, preferring an observed non-browse current-context result, then an exact owned-basket identity, then a browse result; preserve proposal order within a class. It never invents a selection from an unselected result or invokes another tool. Missing selection, unavailable/unsafe/unconfirmed product, or no permitted candidate means store-only. Browse establishes a store suggestion, not similarity or popularity. Model routing/relevance is a language-model responsibility tested with scripted scenarios; deterministic host source/permission checks are the guarantee of this task.

### 4. One pure discount evaluator, explicit supported calculations

Move the common status, identity, targeting, restriction and threshold comparisons out of `evaluateCheckoutDiscount` into `evaluatePurchaseDiscount`, leaving its outreach-specific `reportMatchesContext` helper in the original file. The common evaluator takes this neutral input rather than an `InitialOutreachAgentContext`:

```typescript
type DiscountEvaluationPurchase = Readonly<{
  provider: "SHOPIFY" | "WOOCOMMERCE";
  mode: "NONE" | "FIXED" | "AI_BEST_APPLICABLE";
  authorisedDiscountIds: readonly string[];
  currency: string | null;
  lines: readonly Readonly<{
    lineKey: string;
    productId: string | null;
    variantId: string | null;
    categoryIds: readonly string[] | null;
    collectionIds: readonly string[] | null;
    isSaleItem: boolean | null;
    quantity: number | null;
  }>[];
  currentMerchandiseSubtotal: null | Readonly<{
    amountDecimal: string;
    currency: string;
  }>;
}>;
```

`evaluatePurchaseDiscount({purchase,offerFromOptions,details,evaluatedAt})` returns `DiscountEligibilityDecision`, exactly the existing readonly structural decision `{offerId,verdict,eligibleLineKeys,reasonCodes}` with verdict SUPPORTED/NOT_APPLICABLE/UNVERIFIABLE. `ObservedDiscount` is exactly `{offer: z.infer<typeof CommerceOfferSchema>, details: CommerceDiscountDetails, eligibility: DiscountEligibilityDecision}`; Shared does not export a separate `CommerceOffer` type, so do not invent that import. `DiscountCombinationDecision` is the existing readonly `{verdict: "SUPPORTED" | "UNVERIFIABLE" | "INCOMPATIBLE", offerIds: readonly string[], reasonCodes: readonly string[]}`. Keep every existing status/date/identity/completeness/targeting/exclusion/usage/customer/sale/minimum-quantity check and reason code. Exclusions win. Empty known category/collection sets differ from unknown null. No minimum-quantity scope, buy-X-get-Y, customer-history or allocation engine is added.

The existing `evaluateCheckoutDiscount` keeps `reportMatchesContext` and its actual report/attempt/generation/fingerprint checks, then adapts its genuine context/report to the neutral input. Only a matching COMPLETE report supplies the subtotal. In `.types.ts`, replace only the bodies of `CheckoutEligibilityDecision`, `ObservedCheckoutOffer` and `CheckoutOfferGroupDecision` with aliases to `DiscountEligibilityDecision`, `ObservedDiscount` and `DiscountCombinationDecision`; old callers and result shapes remain unchanged. Move the existing combination algorithm verbatim into `selectCompatibleOffers`; the old `selectCompatibleCheckoutOffers` export delegates with the same inputs, proposal order, max 3, reciprocal Shopify permissions/same-line rules, Woo individual-use restrictions and stable subset tie-break. Preserve existing tests as compatibility evidence; do not loosen a prior UNVERIFIABLE result.

For conversations, construct each purchase independently: PRODUCT_ONLY contains its selected product/quantity; ADD contains the actual basket plus that line; REPLACE substitutes only its owned line. Product identity/category/collection/sale facts come from current canonical observations. Historical source line identities and quantities can identify the proposal; historical prices and sale flags cannot qualify it. A subtotal is available only when every required line has a freshly confirmed exact product, valid quantity, known unitPrice and the same known currency in that provider catalogue context. All required reads must fit the same finalization plan. Otherwise subtotal is null and a threshold-dependent offer stays UNVERIFIABLE. This is a proposed catalogue purchase, not verified customer-market checkout pricing; never describe it as a confirmed checkout total.

Freeze the conversation-only targeting/sale projection conservatively. Absent categoryIds/collectionIds remain null, not empty sets. Shopify current get/search reads `collections(first:20)` and the public product has no completeness field: an observed collectionIds array with fewer than 20 entries may supply that complete observed set; an array of 20 or more becomes null for eligibility, so a truncated list cannot clear an unobserved collection exclusion. Do not add collection pagination, change the get/search schema or alter the legacy outreach projection. Shared 4.0.0 has no product isSaleItem field: project true only when the refreshed product has a known currency and valid native saleEvidence with current unitPrice equal to salePrice and regularPrice greater than salePrice in that same product currency. Otherwise project null; missing/partial sale evidence never proves false. Before invoking the neutral evaluator for a conversation proposal, apply this exact additional source-completeness precondition: category facts are required when targeting.kind is CATEGORIES/MIXED with nonempty includedCategoryIds, or excludedCategoryIds is nonempty; collection facts are required when targeting.kind is COLLECTIONS/MIXED with nonempty includedCollectionIds, or excludedCollectionIds is nonempty. Required lines are every line of that one proposed purchase: the selected line for PRODUCT_ONLY, the complete resulting basket for ADD_TO_BASKET or REPLACE_BASKET_LINE. If any required line has null/incomplete IDs for a required dimension, return UNVERIFIABLE with the existing TARGET_LINE_IDENTITY_UNKNOWN reason and no eligible line keys before calling the neutral evaluator. Do not filter those lines by an inferred match. This guard also applies to ORDER/SHIPPING-only classes; their existing zero-matching-line shortcut cannot certify an unknown exclusion. Leave the extracted algorithm and legacy outreach behavior unchanged. The existing sale-exclusion rule treats projected null sale status as unknown, never false. These are explicit conservative limits of the existing wire data, not reasons to manufacture source facts or loosen outreach rules.

Move the existing `currencyExponent` and `minorUnits` helper bodies and their strict nonnegative `DECIMAL` grammar from `initial-outreach-offer.eligibility.ts` into `recommendations/money.ts`; keep the same Intl validity checks and exponent 0..4 behavior. `decimalToMinorUnits(value, currency)` composes those moved helpers and returns bigint/null, rejecting excess precision exactly as before. The neutral evaluator imports this one implementation; the outreach adapter delegates through it rather than retaining a second copy. The separate existing price-reconciliation parser remains read-only: do not make a third parser or broaden this extraction into that unrelated service. Use bigint multiplication/addition for quantity/subtotal and threshold comparisons; retain known matching `subtotalRequirementCurrency`. Woo unknown currency remains unknown. `formatObservedMoney` may convert to Number only after a safe-integer minor-unit check and exact decimal round-trip; otherwise omit the displayed amount. Use Shared internationalization formatters; never guess currency from locale.

Promotions are rendered only after SUPPORTED eligibility and supported stable combination selection. Render source-supported terms, not a computed coupon saving, combined percentage, discounted total, tax/shipping total or redemption guarantee. For PERCENTAGE require a positive represented value at most 100; FIXED_AMOUNT requires a positive value and known discount currency; FREE_SHIPPING is a supported offer term only, not delivery coverage or a live shipping quote. A missing/unsupported display term omits that promotion. Native sale requires permitting mode, exact same-currency observed regular/sale prices, salePrice equal to current unitPrice and regularPrice>salePrice; render current and regular prices only. NONE performs no discount reads and makes no sale/promotion claim. A failed/partial optional discovery means no verified offer for this suggestion, never “this shop has no discounts.”

Add an explicit `"outcome" in output` guard after each options/details parse in `initial-outreach-offer.graph.ts` (both `projectToolResult` branches and both execution-switch branches); throw `new Error("CONVERSATION_LOOKUP_OUTCOME_IN_OUTREACH")` and add that exact reason to its existing `INVALID_RESULT_REASONS` set. In `current-outreach-offer-revalidation.service.ts`, a successfully parsed unavailable branch returns `{kind:"FAILURE",reasonCode:"CONVERSATION_LOOKUP_OUTCOME_IN_OUTREACH",retryable:false}` before `.details` access (the existing finally still closes the selector). Do not convert it into a newly successful NO_VERIFIED_OFFER/neutral send.

### 5. One finalization budget and fixed refresh order

1. Keep the existing resolved LIVE deadline/output-token policy, AbortSignal, model-step budget and processing lease. Pass `budgets.remoteCalls:6` to `runCommerceTurn`; do not create another runner/model invocation. Count charged tool executions using the runner's existing convention: every `tools/call` attempt including its runner retry counts; initialize/manifest/tools-list control-plane calls retain their existing convention and deadline bounds. Preserve Shared 4.0.0's existing final admission rule: `discoveryAttempts + selectedLegacyEvidenceCount <= 6`. Its `EVIDENCE_RESERVATION_EXCEEDED` guard reserves legacy evidence inside the runner budget; six is not six usable discovery slots plus arbitrary legacy evidence. Put this exact restriction in the trusted instructions so an evidence-bearing turn can finish earlier. The host reserve does not override a runner rejection, and no Shared change is authorized.
2. On successful runner return, initialize one private `usedCalls = result.usage.remoteCalls` and a total ceiling 10. Existing legacy `evidence.refresh` runs first when required, with `remoteCalls:usedCalls,maxRemoteCalls:10`. Its replay callback increments the same counter once before each actual call. A resulting hard referral ends recommendation finalization. Never reset the counter for canonical observations or shipping.
3. Before finalization and before/after every awaited refresh, reuse `assertCurrent`. Its existing Conversation select gains `controlMode`, `controlRevision`, `languageTag` and `languageSource`; compare AI mode and the captured revision, and throw CANCELLED on takeover/change. Return the final successful state snapshot so its language values can be reused without a second language read. Preserve version/lease checks, cancellation and deadline propagation. No new state query is added beside these existing fences; finalization may reuse the same fence instead of an identical adjacent lookup.
4. `finalizeRecommendation` first validates owned selections and prepares a unique refresh set: each retained recommended product via `commerce_get_product`, additional exact basket products needed for its eligibility, each retained selected offer via `commerce_get_discount_details`, and the exact selected shipping call only when its facts/reference will be used. All must have authorized current-turn observations before planning. No search, options pagination, taxonomy, knowledge re-search or new offer selection occurs after finalResponse.
5. Plan the whole set before calling. If it exceeds `10-usedCalls`, remove the last alternative until one remains; then remove offer IDs from the end of that proposal, recomputing required basket/offer reads and compatibility; then remove shipping-dependent facts/reference and use the unverified disposition/store reference; finally remove the last product if necessary. Keep original order, deduplicate identical name/parsed-arguments calls, never execute a partial basket qualification plan. A proposal with no surviving supported offer becomes product-only without changing its purchase scope. This reduces claims, never increases the ceiling.
6. Execute sequentially in this order: retained recommended products in proposal order; remaining required basket products in line-key order; retained detail IDs in first-occurrence order; selected shipping. Each replay uses the same retained client/descriptor identity, checks the existing current `available()` authorization, increments usedCalls immediately before `client.call`, validates the exact canonical output, and replaces the observation. No uncounted retries. Policy is reread before and after the replay set using the same resolver; if no remote refresh is needed, do one final policy read for a controlled answer.
7. Exact ID mismatch/malformed success is a hard contract failure; auth/tenant/changed permission, STALE_TURN, cancellation and unexpected exceptions keep their guarded paths. An outer ERROR preserves the existing hard referral/host-failure behavior, never an optional fallback. Only canonical discount UNAVAILABLE inside OK degrades to no promotion. Normal null product/details, unavailable product, changed price/currency, incomplete eligibility or insufficient shipping evidence discard the old assessment and are recomputed/removed from fresh facts. No stale amount/code/link survives. Do not retry the model to regain a removed claim.
8. Legacy evidence remains independently required wherever evidenceIds were supplied; canonical SUPPORTED cannot replace it. This finalization is an observation-time fence, not provider-atomic redemption or a new processor/worker send hook.

### 6. Shipping, full text and exact locale behavior

`selectShippingPresentation` uses only the latest successful observation matching the parsed shipping selection and its authorized refresh. Both null IDs select policy-only. STANDARD with matching product status AVAILABLE and a known requiresShipping boolean renders exactly that positive/negative native fact independently of policy availability. An absent, UNSUPPORTED or SCOPE_NOT_GRANTED policy removes only its unavailable policy reference; it does not invalidate the known product fact. A verified AVAILABLE policy URL may be linked even when bodyStatus is EMPTY or TOO_LARGE. Use the unverified limitation for the requested unsupported cost/time/destination interpretation or a required product fact left unknown by VARIANT_REQUIRED/null requirement. Missing/insufficient policy or separately entitled knowledge justifies that limitation for the unsupported requested detail, not a claim that all shipping facts are unknown. Do not render weight/dimensions with unknown units, HTML, raw model policy summaries, source-embedded discount codes, rate/ETA or inferred destination coverage. Policy-only answers outside a controlled branch retain the existing ordinary grounded path.

At host finalization, use the SAME language input as `ConversationService.applyDetectedLanguage`: `context.conversation.messages.filter(m=>m.role==="user").map(m=>m.content).join("\n")`, tag/source from that final successful host state snapshot mapped as in that service, the final detection fields, and **`recoveryConversation:true`**. This flag is material: the existing recovery flow does not apply legacy CUSTOMER_EXPLICIT precedence. Reuse `conversationLanguageService.evaluateDetectedLanguage` (including >0.8 confidence, stable-input and same-base/regional preservation), then `resolveModaConfigurationLocale` for the fixed catalogue. Do not independently guess locale, change detected fields to force it or write language in the host. The processor remains its only writer.

`recommendationMessages` must be a typed complete Record over `MODA_SUPPORTED_LANGUAGE_TAGS`, exactly: `zh-Hans`, `zh-Hant`, `cs`, `da`, `nl`, `en`, `fi`, `fr`, `de`, `it`, `ja`, `ko`, `nb`, `pl`, `pt-BR`, `pt-PT`, `es`, `sv`, `th`, `tr`. Use the published Shared `createInternationalizationRuntime` and `validateIcuCatalogue(catalogue, recommendationMessageKeys, {locale})` exports. The English keys/text and required placeholders are frozen below; every locale must translate the complete meaning and preserve the same placeholders. Do not fill other locales with English text or use runtime translation.

| Key | English source text |
|---|---|
| `scopeLimit` | `I can help with this store's products, but I can't answer that question.` |
| `shippingUnverified` | `I can't confirm the shipping details for your request. Please check with the store.` |
| `shippingRequired` | `This item requires shipping.` |
| `shippingNotRequired` | `This item does not require shipping.` |
| `policyLink` | `Shipping policy: {url}` |
| `storeLink` | `Store: {url}` |
| `productOption` | `{title}` |
| `proposedQuantity` | `For a proposed purchase of {quantity}:` |
| `addProposal` | `If you add {quantity} of this item to your basket:` |
| `replaceProposal` | `If you replace the selected basket item with {quantity} of this item:` |
| `currentPrice` | `Current listed price: {price}` |
| `regularPrice` | `Regular listed price: {price}` |
| `percentTerms` | `Offer terms: a {percentage} discount, subject to its verified conditions.` |
| `amountTerms` | `Offer terms: a {amount} discount, subject to its verified conditions.` |
| `freeShippingTerms` | `Offer terms: free shipping, subject to checkout validation.` |
| `code` | `Code: {code}` |
| `automatic` | `Automatic offer; checkout confirms the final application.` |
| `checkoutQualification` | `Eligibility and the final price are confirmed at checkout.` |
| `productLink` | `View product: {url}` |
| `noVerifiedOffer` | `I couldn't verify an applicable offer for this suggestion.` |

Use ICU-safe apostrophe escaping where required; the rendered English sentences above remain exact. No runtime import-name discovery or additional Shared export is needed.

A controlled body contains, in order: its fixed scope/shipping sentence if applicable; verified policy reference when used; each selected purchase-scope/quantity, source title, known current price, supported terms/code/qualification and product URL; store reference for a minimal fallback. `noVerifiedOffer` is used only after an actual permitted discount attempt that yielded no supported claim, not when mode is NONE. Source offer titles/descriptions and model replyText are never promotion templates. Product titles are bounded plain data; reject control-bearing titles rather than introduce multiline commands. All URLs are exact verified observations and are never truncated. Do not render an internal reason, grant, opaque database ID or tool name to the customer.

The entire raw model replyText is discarded in a latched controlled branch. Hard REFER_TO_STORE still uses `renderStoreReferral` with empty details/evidence and never gains a promotion/candidate list. Ordinary unlatched greetings/clarifications and the allowed policy-only path retain normal guarded text. A malformed runner final response is not silently reclassified as a soft answer.

### 7. Private candidates and one wrapper stage

`CommerceAgentResult` becomes `Omit<CommerceFinalResponse,"details"> & {hostComposedReplyCandidates?: readonly string[]}`. Only `buildReplyCandidates` populates the field after successful host finalization: full body, first-product body, then minimal disposition plus verified store reference, in that order. Each candidate is complete, nonblank and at most 4096 UTF-16 code units (the existing wrapper limit); omit duplicates and individually oversized candidates. Set replyText to the first retained candidate. The minimal body is mandatory for a controlled answer with a valid store reference. No Shared/MCP/model schema is widened and a model-supplied lookalike field is ignored.

Add the same optional property to the processor's `getResult` return type and pass it conditionally, without reconstructing or sorting it, to the existing `composeAiOutbound` call after current language/control checks. Extend `composeAiOutbound`'s input and `RenderConversationResponseInput` with the optional property. In `ConversationWrapperService.renderConversationResponse`, validate count 1..3, each nonblank/max 4096, first===responseBody and `source === "AI"` when the property is present. Invalid arrays/HUMAN usage return INVALID_INPUT before any read. With no property, preserve the one-body behavior.

For a new render, keep one loadContext, one loadSlots, the existing slot/definition/locale/projection validation and the unchanged `renderPreparedWrapper`. Try complete candidates in order at that same point; advance only after OUTPUT_TOO_LONG. Any other refusal terminates unchanged. No configured slot plus existing passthrough policy returns the exact first responseBody. If every candidate exceeds the composed limit, preserve OUTPUT_TOO_LONG and the existing refusal handling; never bypass the wrapper, slice text or create another send.

For replay, use the existing branch before reads: prior responseDigest must equal digest of exactly one current candidate (or the ordinary one body); perform the existing message/source/applicationKey/body-digest checks against that matched body, including its presence in prior.body. Otherwise REPLAY_MISMATCH. The selected candidate supplies responseDigest/applicationKey for new rendered results. HUMAN input and ordinary one-body callers keep their original behavior. No new replay store, host wrapper read, provider recheck or send-stage hook is permitted.

### 8. Actual source diagnostics, not only a reason code

`CommerceMcpClient` already retains a bounded `sourceFailure`; host wrapping currently drops some of it. Extend `logCommerceHostFailure` with an optional original-failure parameter and pass the actual failure from `executeCommerceHost`. When wrapping a retained runnerHostFailure, retain both its cause and sourceFailure. Preserve safe original MCP status/request ID/code/message/details already projected at the source boundary. For local Prisma/SDK exceptions, retain their actual name/message/code and bounded cause chain (max 5, cycle-safe), with source marked accurately; never fabricate providerError for a local exception.

Reuse the existing MCP domain-safe text projection: move that small existing `safeDiagnosticText` function to `host-diagnostics.ts` as `safeCommerceDiagnosticText`, import it back into mcp-client, and use it when projecting the cause chain. Keep its existing bounds/redaction semantics and visible redactionApplied/truncated flags; unsafe entire payload text is `[REDACTED]`, not a guessed explanation. Continue to emit through `@modainteract/moda-interact-shared/logging`; no second logger, sink, generic redactor or telemetry framework. Do not log prompts, customer message/history, credentials, full headers/provider payloads or successful product/policy bodies. Original provider errors intentionally absent from public MCP results are logged by MCP, not reconstructed by Background. Sink failure cannot change propagation or fallback.

## Validation and acceptance evidence

### Exact test commands and discovery

Update only the Shared dependency first, using the immutable accepted version (no registry release discovery):

```sh
npm install --package-lock-only --save-exact @modainteract/moda-interact-shared@4.0.0
npm ci
npm ls @modainteract/moda-interact-shared --depth=0
```

Add these exact package scripts:

```json
{
  "test:commerce-recommendations": "vitest run tests/unit/commerce/recommendations tests/unit/commerce/host-diagnostics.test.ts tests/unit/commerce/mcp-client.test.ts tests/unit/commerce/evidence.test.ts tests/unit/agents/initial-outreach-offer.eligibility.test.ts tests/unit/agents/initial-outreach-offer.combinations.test.ts tests/unit/agents/initial-outreach-offer.graph.test.ts tests/unit/services/recovery-offers/current-outreach-offer-revalidation.service.test.ts",
  "test:commerce-host": "vitest run --config vitest.commerce-host.config.ts"
}
```

`vitest.commerce-host.config.ts` is test-only and contains exactly this configuration (normal formatting is immaterial):

```typescript
import { configDefaults, defineConfig } from "vitest/config";
export default defineConfig({
  test: {
    environment: "node",
    env: { DEPLOYMENT_ENVIRONMENT_NAME: "test" },
    include: ["tests/integration/commerce/host.test.ts"],
    exclude: configDefaults.exclude,
    fileParallelism: false,
    server: { deps: { inline: ["@modainteract/moda-interact-shared"] } },
  },
});
```

This suite uses its existing mocked Prisma and loopback MCP/AI Mock endpoints; it does not run Docker or contact live providers. Retain the fixture's assertion that the SDK baseURL is loopback. Extend its actual configuration/policy/owned-row mocks; do not bypass `loadRecommendationContext` or grant checks. Run from the prepared Background implementation worktree, after the workspace Node bootstrap contract if Node is absent:

```sh
npm run build
npm run lint
npm run test:commerce-recommendations
npm run test:commerce-host
npm exec vitest run tests/unit/services/conversation-turn-processor.service.test.ts tests/unit/services/conversation-wrappers/compose-ai-outbound.test.ts tests/unit/services/conversation-wrappers/service.test.ts tests/unit/services/conversation-wrappers/projection-and-render.test.ts
git diff --check
```

Build already runs prisma:generate. Do not add a second generation/build cycle without a relevant change. Verify the host output reports its registered tests; “no tests”, an excluded path or a skipped suite is not a pass.

The required real PostgreSQL boundary uses the existing disposable pg17/pgvector+Redis harness, not the developer's normal database. Under workspace-wide `docs/agent-validation-execution-policy.md` (Developer-Executed Validation and Explicit Override), prepare this exact handoff command and record it as **not run** until executed by the developer or an already-claimed task has the required explicit authorization:

```sh
node scripts/test-integration.mjs tests/integration/commerce/recommendation-context.integration.test.ts
```

Record the actual worktree/commit/database gitlink, command exit code, tested file/assertion count and container cleanup. This task cannot be accepted as fully validated from mocked tests alone. Do not use a local DATABASE_URL, automatically relax policy, skip the required boundary or call a blocked command successful.

### Required assertions, assigned to focused suites

| Suite | Required result |
|---|---|
| `instruction-composition` / context unit+PostgreSQL | Exact kernel/host/Platform/Shop/response/feature order; missing/duplicate/wrong-owner/non-PUBLISHED/oversized prompt rejects; one prompt lookup per turn; existing override/expiry semantics and FIXED IDs; no fabricated attempt; initial recovery reused. |
| `authority` / `grants` / observation unit | Null-grant resolution then retained grant header; published and built-in equality; altered hash/schema/name, cross-shop/version, revoked permission and duplicate/collision reject; real mixed grant insertion passes the accepted DB guard; no old-grant widening. |
| `recommendations` / pure eligibility+combination | All three independent scopes; Shopify explicit observed variant and Woo simple null; exact/category/collection targeting and exclusions; no fake current basket price; Shopify collection arrays of 19 versus 20 entries and an excluded collection outside the first20; conversation ORDER/SHIPPING-only exclusion with unknown IDs returns UNVERIFIABLE/TARGET_LINE_IDENTITY_UNKNOWN before the legacy non-line shortcut; absent/partial saleEvidence stays isSaleItem null while a valid native sale yields true; sale exclusions never accept unknown as false; subtotal currency/precision; original outreach decision/reason-code parity; supported terms only and stable subset behavior. |
| `recommendation-revalidation` / budget unit | Count the runner budget of six and shared total 10 including legacy replay; actual Shared admission permits five discovery attempts plus one selected legacy evidence and rejects six plus one with EVIDENCE_RESERVATION_EXCEEDED before host replay; exact stable plan pruning; each remaining selected read refreshed once; no post-final search; changed product/code/currency/basket/policy invalidates stale wording; no unrefreshed promotion. |
| `recommendation-failures` / evidence | Forged same-shaped other-tool data, model code/savings/prose, missing selection, plain text or STANDARD cannot escape the latch; optional UNAVAILABLE removes only promotion; outer error then success remains hard referral; cancelled/stale/HUMAN takeover during blocked await never sends. Use deterministic barriers, not sleeps. |
| `fallback-responses` | Scripted weather question→browse shirt+supported offer; NONE→product link; absent result/selection→store link; known basket precedes browse; declined suggestions→store-only with zero browse/discount calls; no weather/category/destination invention and no global-catalogue claims. |
| `shipping-responses` | Exact null/null and product/variant selection; product-bearing read latches even without selection; unlatched policy-only remains ordinary; VARIANT_REQUIRED, unknown requirement/units, absent/empty/oversized/scope-missing/unsupported policy; known positive/negative requiresShipping survives missing policy independently, and EMPTY/TOO_LARGE retains its verified URL; changed shipping fact/reference refresh; raw HTML/code never enters a composed offer; zero direct provider/cart calls. |
| language / messages / render | All 20 locale key sets and ICU placeholders; exact full English fixture bodies; complete translated bodies for a representative positive/negative shipping+promotion case in each locale; accepted same-turn language change, >0.8 boundary, stable-input filter, recovery legacy preference behavior and regional preservation match processor evaluation. |
| candidates / wrapper / processor | Full→one→minimal; one context/slot load; first-body passthrough; selected-candidate digest replay and mismatch; invalid/HUMAN/over-count arrays reject before reads; only length refusal advances; minimal-too-long stays refused; no second model/provider/wrapper call or extra send; unchanged language/control/moderation ordering. |
| actual diagnostic sink | Original harmless MCP/SDK/Prisma message and safe actual code/status/cause survive; secrets/PII/payload sentinels removed with flags; no invented provider fields; sink failure preserves original outcome. |

Synthetic fixtures must contain two shops/providers reusing local IDs, one source-backed available simple product, one explicit Shopify variant, distinct before/after facts, NONE/FIXED/AI/override modes, partial catalogue pages, optional unavailable and terminal error. Assert complete returned customer bodies as well as IDs/call counts. Scripted model tests establish integration/grounding behavior; they are not evidence of general semantic routing quality on all natural-language questions.

## Stop conditions and scope limits

Stop with the exact owner/path/export discrepancy when a prerequisite implementation is absent, its accepted contract differs, or an active writer owns a conflicting edit. Do not repair upstream source, republish Shared, alter the DB schema or reset grants. Preserve accepted ARCH-056/052 processor/outreach changes; only the explicitly named adapters/seams above may change. New source errors are not excused by an unrelated baseline condition; reference a documented baseline ID only when its actual condition is observed.

No new agent, queue, worker, transaction retry framework, product mirror, Admin/Redis implementation, taxonomy source download/import, quote/rate service, cart mutation, discount creation, API/provider HTTP from Background, deployment or `_index.md` change is authorized. A necessary additional writer/interface is an architect handoff before mutation.

## Completion Report

Not started. On execution record prepared isolation/synchronization evidence, parent/implementation branches and SHAs, the accepted dependency receipt/gitlink and installed 4.0.0 evidence, exact changed files, context/observation/refresh interfaces, source-rule extraction compatibility, complete-text/locale/length cases, actual command/test counts, original safe/redacted diagnostic examples, developer-run disposable evidence or its outstanding status, and overlap resolutions. Record actual implementation/parent task-report publication or its precise failure; do not claim merges/deployment.

## Architect Review

Pending. Acceptance requires the implemented source mapping, preserved initial-outreach/legacy evidence behavior, deterministic authorized-call accounting, complete controlled-body composition, unchanged downstream ownership and actual mandatory validation evidence. A task definition or proposed command is not proof of execution.
