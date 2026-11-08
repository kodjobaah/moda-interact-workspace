# ARCH-066 — Normative initial-outreach evaluation and preview contract

This is the implementation contract for SHARED-004/005, BACKGROUND-002, COMMERCE-002 and SYSTEM-TEST-002. It supersedes their earlier prose where inconsistent. Original conversational tasks and completed Shared5.6.0 release remain unchanged. This document defines new work, not deployed behavior.

## 1. Ownership and exports

Shared owns read-only evaluation, reconciliation and frozen-template rendering. Hosts own authentication, database reads, model credentials, authorized provider calls, clocks, cancellation, execution policy, storage and delivery. No import from a service repository is permitted in Shared. No Prisma, Redis, Meta SDK or media upload in the outreach export. This export is server-side: it need not inherit the browser-only constraints of `/commerce/presentation`.

Public subpath `@modainteract/moda-interact-shared/commerce/outreach`, built JS and declarations, exports:

- `InitialOutreachEvaluationInputSchema`, `InitialOutreachEvaluationResultSchema`, `InitialOutreachRenderInputSchema`, `InitialOutreachRenderResultSchema` (strict Zod, types inferred).
- `evaluateInitialOutreach(input, ports): Promise<InitialOutreachEvaluationResult>`; `evaluateInitialOutreachPreview` is an alias, not a separate implementation.
- `renderInitialOutreachPreview(input): InitialOutreachRenderResult`, deterministic synchronous rendering of a host-validated frozen template projection.
- `fingerprintInitialOutreachBasket(input): string`, SHA256 canonical JSON using the existing price-comparison algorithm; host recovery/attempt IDs are excluded from the reusable basket content hash. Hosts retain existing production fingerprint calculation/admission checks separately.
- Typed `InitialOutreachPorts`, `InitialOutreachToolCall` and all four inferred input/result types.

## 2. Exact input contract

Use existing CommerceEnvironmentSchema, CommerceProductSchema, CurrencySchema, HashSchema, CommerceModelInvoker and Commerce tool argument/output schemas. Do not invent a second money, provider product, model or offer schema. IDs use existing native provider validation; host IDs are trimmed1..191. Times are ISO UTC. All objects strict, arrays bounded. No z.custom that accepts unvalidated nested JSON.

Evaluation input:

```ts
{
  schemaVersion: 1,
  runId: string, shopId: string,
  platform: 'SHOPIFY' | 'WOOCOMMERCE', environment: CommerceEnvironment,
  checkout: {
    id: string, generation: number, // positive safe integer
    currency: string, // CurrencySchema
    url: string, // HTTPS, no credentials; host-approved checkout URL
    lines: Array<{
      lineKey: string, // unique trimmed1..128; original order retained
      productId: string, variantId: string | null,
      quantity: number, // positive safe integer
      checkoutUnitPrice: string | null // existing unsigned decimal money validator
    }> // 1..100
  },
  policy: {
    mode: 'NONE' | 'FIXED' | 'AI_BEST_APPLICABLE',
    authorisedDiscountIds: string[] // <=50 distinct; FIXED only, otherwise empty
  },
  instructions: {
    platformText: string, platformRevisionId: string,
    merchantText: string | null, merchantRevisionId: string | null,
    purposeText: string, purposeProfileRevisionId: string
  }, // text fields <=8000 each; nonempty platform/purpose; nullable pairs consistent
  limits: {deadlineMs: number, modelSteps: number, remoteCalls: number, outputTokens: number}
}
```

Limits are positive safe integers admitted by the host's current execution policy; no new UI defaults or hidden budget increase. Host freezes clock start before evaluation. Every port uses the same AbortSignal. Run expiry = start + deadlineMs. Remote-call budget counts every actual provider/model-tool call attempt under existing runner semantics; deduplicated reuse is zero additional calls. Cap input JSON at131072 UTF8 bytes before evaluation. Reject over-limit inputs before I/O. No phone, email, customer record, attempt ID or fake recovery attempt is necessary. A host records historical checkout total separately; reusable evaluation never calls a merchandise subtotal the payable checkout total.

## 3. Port signatures and source relocation

```ts
interface InitialOutreachPorts {
  signal: AbortSignal;
  now(): Date;
  callTool(call: InitialOutreachToolCall): Promise<unknown>;
  modelInvoker: CommerceModelInvoker;
  log(event: {
    stage: 'INPUT'|'PRODUCT_READ'|'RECONCILE'|'OFFER_SELECT'|'REVALIDATE'|'COMPLETE';
    runId: string; shopId: string; reasonCode: string | null;
    lineKey: string | null; toolName: string | null; durationMs: number;
  }): void;
}
```

`InitialOutreachToolCall` is a discriminated union of exactly `commerce_get_product`, `commerce_get_discount_options`, `commerce_get_discount_details`, each with existing canonical args plus runId, shopId, platform and the same signal. Host translates this to existing authenticated local/MCP adapters and adds trusted tool context; model cannot provide shop identity or grant. Shared validates outputs with canonical schemas after the port returns. Unknown fields/tool names rejected; no arbitrary tool escape hatch. No search tool is exposed in checkout outreach. Port rejects carry existing typed error code/retryability, not raw HTTP body. Cancellation/deadline wins over later completion.

Relocate reusable code from Background, maintaining service delegates in BACKGROUND-002:

| Source in Background | New Shared responsibility |
|---|---|
| `src/agents/initial-outreach-offer.types.ts` | Replace nested z.custom contracts with strict schemas; shared results omit production attempt metadata |
| `initial-outreach-offer.agent.ts`, `.graph.ts`, `.instructions.ts` | Bounded offer-selection graph/model handling through injected model/tool ports |
| `initial-outreach-offer.eligibility.ts`, `.combinations.ts`, `initial-outreach-offer-product-target.ts` | Current checkout eligibility/combination arithmetic and product membership checks |
| `src/services/recovery-pricing/price-comparison.ts` and pure arithmetic in `checkout-price-reconciliation.service.ts` | Decimal-safe price comparison and checkout-line reconciliation |
| `src/services/recovery-template-preparation/recovery-template-selection.ts` | Pure assignment selection from validated repository projections |
| `recovery-template-bindings.ts`, `initial-checkout-items-policy.ts`, `recovery-template-items-summary.ts` | Frozen binding validation, checkout-summary slot and template parameter composition |
| Pure label/value functions in `recovery-template-brand.ts` | Prepared variable resolution from passed brand/category/customer values |

Do not move `recovery-template-preparer.service.ts` wholesale: it resolves WABA, database catalogue and media and may prepare derivatives. Keep those side effects in Background. Do not introduce caller-defined arbitrary render callback as a substitute for shared rendering. Shared must own the same binding/selection/summary algorithms exercised by both hosts.

## 4. Deterministic evaluation sequence

1. Parse strict input; validate identity and currency, unique line keys and native parent/variant IDs. Fail before port I/O on invalid input.
2. Visit distinct productId+variantId pairs in first-line order, sequentially, calling exact get_product. Validate current-shop/provider/parent identity, canonical output and observation timestamp within this run. Always do this in NONE mode too. No title matching, category search or substitute product. A duplicate pair reuses the observation and retains both checkout lines/quantities.
3. Any failed/missing/foreign exact read refuses the preview, even if other lines succeeded. Do not silently remove a basket line. Product unavailable/purchasability false refuses with PRODUCT_UNAVAILABLE. No stale snapshot as current evidence.
4. Reconcile historical versus live unit price per line using existing decimal-safe price comparison. Keep both values. Sum current price times checkout quantity in minor units; currency mismatch, missing current price or unsafe arithmetic refuses. This is current merchandise subtotal, never proof Shopify/Woo checkout price itself changed; checkoutPriceChange remains UNVERIFIABLE unless the existing provider contract independently proves it.
5. NONE => no offer tool or model calls, NO_VERIFIED_OFFER decision. FIXED => read only authorized offer details and apply existing eligibility. AI_BEST_APPLICABLE => existing checkout-scoped option discovery/details/model selection with existing max3 compatible offers and discount arithmetic. No eligible offer is a successful NO_VERIFIED_OFFER, not a fabricated saving. Refuse malformed model choices; never grant eligibility from model prose.
6. Checkout-only amendment: existing ALTERNATIVE_PRODUCT_PROMOTION branch is not permitted in this path. Remove it from the new input-to-model choice schema/prompt; unexpected result refuses OUTSIDE_CHECKOUT. Background adapters must explicitly reject that branch for initial checkout outreach; do not remove unrelated conversational recommendations or historical receipt parsing. This is an intentional behavior change from current graph, not a claim of unchanged behavior.
7. Before ready result, re-read each distinct checkout product pair once, in the same order, and every selected offer's details. Revalidate price/availability/eligible membership. If product or selected-offer facts changed, refuse CURRENT_FACTS_CHANGED; no unbounded reselect/retry loop. NONE still rechecks product facts. Empty offer selection performs no offer recheck. All these calls consume limits and appear in activity. No automatic retries in this new evaluator; hosts must not wrap it in hidden provider retry loops.
8. Return typed result. Evaluation cannot issue a production admission token. Production performs its existing final send fence/revalidation after evaluation.

## 5. Result and reason contract

Discriminated result:

- `{kind:'ready',schemaVersion:1,runId,shopId,basketFingerprint,evaluatedAt,lines, currentMerchandiseSubtotal,offerDecision,toolActivity}`.
- `{kind:'refused',schemaVersion:1,runId,shopId,stage,reasonCode,lineKey:string|null,toolActivity}`. No rendered message on refusal.

`lines` (same order/count as input) contains `{lineKey,productId,variantId,quantity,checkoutUnitPrice,currentProduct:CommerceProduct,comparison:'EQUAL'|'DIFFERENT'|'INCOMPARABLE'}`. Output <=524288 UTF8 bytes; overflow refuses RESULT_TOO_LARGE. `currentMerchandiseSubtotal` is `{amountDecimal,currency}`. `offerDecision` is strict union `NO_VERIFIED_OFFER {reasonCode,discoveryIncomplete:boolean}` or `CHECKOUT_DISCOUNT {offerSet:InitialOutreachCheckoutOfferSet,members,group,discoveryIncomplete:boolean}`. Relocate existing member/eligibility/group schemas as strict Zod from the source types; preserve their data, no z.custom placeholders. Existing production result wrapper adds real shop/recovery/attempt/generation/fingerprint metadata after validation; preview never invents it.

Reasons are closed enum: INPUT_INVALID, OUTSIDE_CHECKOUT, PRODUCT_NOT_FOUND, PRODUCT_UNAVAILABLE, IDENTITY_MISMATCH, CURRENCY_MISMATCH, PRICE_UNAVAILABLE, ARITHMETIC_UNSAFE, PROVIDER_UNAVAILABLE, DENIED, CANCELLED, DEADLINE, BUDGET_EXHAUSTED, INVALID_RESULT, CURRENT_FACTS_CHANGED, RESULT_TOO_LARGE. Successful no-offer reasons preserve existing bounded codes, max96. Exceptions from ports are translated once, not leaked; unexpected exceptions => INVALID_RESULT with bounded diagnostics. `toolActivity` uses existing preview event shape toolName/modelStep/attempt/status/durationMs/errorCode, bounded by remoteCalls, never raw bodies or credentials.

## 6. Frozen initial-template rendering contract

Hosts perform existing tenant/WABA assignment, approved-registration/locale/hash/binding-fingerprint checks and resolve ready media **before** rendering. Extract the strict frozen registration/binding projection types from `recovery-template.types.ts` and existing bindings code, preserving existing field names/schema versions. No new authoring AST. Render input is `{schemaVersion:1,evaluation:<ready result>,preparedProjection:<validated selected registration and bindings>,variables:{shopName,customerFirstName,checkoutUrl,shopCategory},headerMedia:<ready existing R2 reference|null>}`. Variable nullability/limits follow existing binding validation; synthetic customer firstName is 'Test customer' and labelled. Same-shop checkout URL comes from authenticated checkout reader, never the browser. Parameter rendering uses live product titles/options for the checkout summary, original quantities; prices/discount terms from validated evaluation only. Checkout facts have inert text semantics.

Result ready: `{kind:'ready',purpose,templateProvenance:{variantId,registrationId,definitionId,providerTemplateId,providerTemplateName,providerLanguageCode,submittedContentHash,bindingFingerprint},parameters:<existing PreparedMetaComponent[]>,headerPreview:<existing ready media reference|null>,renderedText:string}`. Reuse existing template body/header/button binding and parameter caps verbatim. Preview body limit4096 UTF16 including substituted template body; over-limit refuses MESSAGE_TOO_LARGE, never cut parameters/URL/offer terms. Other render refusal reasons preserve existing TemplateUnavailableReason and add MESSAGE_TOO_LARGE. No active approved assignment => refusal, never substitute conversation wrapper/raw agent text. Output is text plus parameter projection, not provider approval or send authorization.

Header rule: reuse a READY existing authorized R2 derivative only. Studio must not invoke derivative generation/upload. If image assignment lacks ready media, use existing approved TEXT assignment selection fallback; if none exists, MEDIA_NOT_READY refusal. Production may prepare media in its host before calling the same renderer. No Meta calls from preview, including status refresh; current saved registration status is shown with checked timestamp.

## 7. Test gates

Shared unit goldens assert exact call order, duplicate reuse, two product reads per distinct pair on ready NONE, no model/offer calls for NONE, budget consumption and all refusal reasons. Fixed model ports make selection deterministic. Run both-platform/clothing/nail-varnish/tree/custom-label fixtures through one implementation. Assert merchant labels/units preserved; no merchandise enums. Compare existing checkout discount/summary/template goldens except intentionally prohibited alternative products and newly mandatory live reads. Missing facts never become invented attributes or payable totals.

Background/Studio integration tests compare parameters, provenance and full text for the same frozen inputs, not stochastic model wording. Verify no preview writes to recovery/attempt/customer/credit/outbox and no Meta/media mutation. Failure/expiry and configured-image TEXT fallback cases required. The reference-context DB table remains conversational only; outreach preview needs no schema migration.
