---
id: ARCH-052-BACKGROUND-008
architecture_id: ARCH-052
title: Send approved checkout or alternative-product promotion via existing initial outreach
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 65
executor: null
claimed_at: null
attempt: 3
depends_on:
- ARCH-052-SHARED-012
- ARCH-052-ADMIN-003
- ARCH-052-BACKGROUND-010
- ARCH-052-BACKGROUND-005
- ARCH-052-ADMIN-001
- ARCH-052-BACKGROUND-015
- ARCH-052-BACKGROUND-016
enables:
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
- ARCH-052-SYSTEM-TEST-003
created: '2026-10-29'
updated: 2026-11-01
---

# ARCH-052-BACKGROUND-008: Send approved checkout or alternative-product promotion via existing initial outreach

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Compose the existing initial outreach with a source-supported checkout discount, separately source-supported alternative-product promotion or approved no-offer fallback, without replacing existing Meta/consent/billing send gates.

## Context

ARCH-047 BG006 already integrates `AutomatedRecoveryTemplateService` with initial send and final Meta/credit admission; ARCH-048 Woo outreach and ARCH-050 Support notices are complete. This task extends those, not creates a new send pipeline.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

**Attempt 14 text-first delivery (normative):** implement **approved TEXT** variants first. Do not wait on BG007 or ADMIN002 for text-only initial outreach. Choose the initial approved registration using `(purpose, language, promotionTarget=CHECKOUT|ALTERNATIVE_PRODUCT, headerKind=TEXT, WABA/shop and immutable revision)` **before** the existing language/assignment ambiguity check. Preserve same-purpose legacy follow-up behaviour. If the chosen target is absent or unapproved, use an independently approved NO_OFFER or typed no-send; never silently render an alternative-product offer through checkout-only copy.

**Dynamic CTA transport:** the existing `templateSendFields()` currently keeps one `dynamicUrlButton` and `WhatsAppTemplateSend` carries one; for an approved alternative-product template with two buttons, extend the **existing** transport to support ordered `dynamicUrlButtons[]` with unique provider indexes, retaining the existing single-button path for unaffected templates. Amend `src/integration/whatsapp/types.ts`, `src/services/whatsapp.service.ts`, `src/services/recovery-template-integration/prepared-template-send.ts`, and `src/services/conversation-moderation/automated-template-input.ts` together; persist the actual populated approved button parameters in the existing `ConversationMessage.content`. Keep checkout and promotional URLs assigned to their **own** approved button indices. Do not send a second button unless the actual approved Meta registration contains it.

**ARCH-053 ownership:** Woo URL capture/issuance and restoration are handled exclusively by ARCH-053, which already has a downstream dependency on ARCH-052-BACKGROUND-008 for offer-aware restoration. No reverse dependency or HTTP issuance call is permitted. ARCH-052 consumes only upstream `CheckoutRecovery.checkoutUrl`. The existing `RecoveryVariableResolver.checkout()` has a five-minute observation and URL/host check; align the ARCH-052 **trusted persisted-recovery URL binding path** with our agreed upstream contract (no additional URL validation in ARCH-052). Do not change unrelated generic URL checks or add new validation/fallback rules. Passing the stored value as `checkout.url` is distinct from the existing Meta-approved dynamic URL **parameter encoding** required by template transport; encoding does not generate or revalidate a recovery URL.


- Initial sequence one reads **current** merchant discount settings from Background and consumes the Background-010 trusted `CHECKOUT_DISCOUNT` / `ALTERNATIVE_PRODUCT_PROMOTION` / `NO_VERIFIED_OFFER` decision. NONE never calls discount MCP/AI. Stage-2 alternative promo is permitted only for merchant-authorised discount mode and MCP-catalogueed product+discount pairing; a product merely sharing a taxonomy category is insufficient.
- Use existing six Meta **purposes** (`INITIAL_NO_OFFER`, `INITIAL_CODE_OFFER`, `INITIAL_AUTOMATIC_OFFER` and follow-ups) without a DB enum change. For checkout discount use approved `promotionTarget:CHECKOUT` CODE/AUTOMATIC variant; for other product use independently Meta-approved `promotionTarget:ALTERNATIVE_PRODUCT` CODE/AUTOMATIC variant. Never render alternative offer using an approved checkout-only copy. Bind distinct `promotion.productName`, `promotion.productUrl`, `promotion.offerDescription` and source-backed code when provided; keep abandoned-cart checkout return button separately. No claim alternate discount applies to existing cart.
- For alternate promotion, use only MCP-returned canonical storefront product URL and independently approved CTA/link text; do not change approved button URL prefix after Meta approval. Require marketing consent/category/merchant permission for cross-sell content; if required permission or approved variant absent, use approved NO_OFFER or typed no-send. No unapproved on-the-fly message body.
- Optional BG007 image may show checkout item or promoted product only with matching approved IMAGE variant, otherwise approved text-only. For **both Shopify and WooCommerce**, the Resume checkout CTA uses the existing `CheckoutRecovery.checkoutUrl` as supplied by the recovery workflow; ARCH-052 does not generate, refresh, reconstruct or validate checkout URLs.
- **Checkout URL binding (no new validation or provider/API call):** read `CheckoutRecovery.checkoutUrl` from the recovery already loaded by Background. The field is assumed to be populated upstream for **both platforms**. Pass its exact stored value unchanged to the existing `checkout.url` semantic binding and approved Resume checkout button through the current template-preparation path. **Do not implement a new checkout URL check** of format, `https:` scheme, host/origin, userinfo, fragment, length, Meta URL prefix, expiry or reachability, and do not implement URL-specific invalid/missing fallback branches or tests in ARCH-052. Existing general template approval and delivery behaviour is unchanged; do not add a parallel validator or override the established delivery system. Never synthesize a generic `/checkout` URL, create a Woo restore-link client/service, invoke API-004 or a WordPress restoration endpoint, or construct a link from checkout IDs. No short-lived token, new expiry rule or fresh-link contract is introduced. Do not log the raw URL or copy it into a new policy/offer table or JSON snapshot; existing `ConversationMessage.content` retains its populated button parameter as in the established send path. For `ALTERNATIVE_PRODUCT_PROMOTION`, the separately provider-backed `promotion.productUrl` belongs **only** to its separately approved promotional CTA; never replace the checkout CTA with a product URL. Preserve the checkout CTA independently where both approved buttons exist.
- The actual prepared template parameters and existing `recoveryPromise` must remain the **single durable source of customer-facing claims** in the confirmed outbound `ConversationMessage.content`, linked through `RecoveryOutreachAttempt.outboundMessageId`. Extend the existing `RecoveryOfferPromise` only to distinguish `ALTERNATIVE_PRODUCT_PROMOTION` and its exact source-backed discount/product/variant identifiers, title and URL reference as necessary. Do not write or read a second `offerSnapshot.sentOffer` or duplicate policy/offer history. On follow-up, read the confirmed initial outbound message and its persisted parameters/promise; do not infer a promise from merchant settings or merely prepared/unconfirmed messages. Preserve ARCH-046 consent/STOP, moderation, credit/idempotency, human handover and ARCH-050 merchant Support notification.
- Integration tests for all three merchant modes × two platforms × checkout/alternative/no-offer, changed product/coupon, missing image/category, correct unchanged stored checkoutUrl binding, approved/non-approved promotion target, marketing refusal, Meta timeout, duplicate queues and credit confirmation.

## Out of Scope

- No new Meta template creation on send path, no independent billing/consent engine, no cart mutations, no reopening ARCH-050 notices or paid follow-up business changes.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

### Multi-discount send and immutable receipt — normative 30 October 2026

- Accept BACKGROUND-010's validated checkout offer set of 1..3. Before send, recheck CURRENT merchant policy, all selected identities, source-backed codes, provider status and complete evidence for **every** included offer. On any failed member, reselect/trim only to a separately verified compatible subset; no stale or fabricated co-discount claim.
- Bind multi-CODE checkout choices only to an independently **Meta-approved** checkout-target template revision exposing `offer.codes` and accurate plural wording from ADMIN-003. Preserve `offer.code` for the original approved single-code path. Automatic-only combinations use separately approved **plural** automatic copy from ADMIN-003 and must not claim a code. Mixed automatic+code offers require accurate approved copy for each claimed benefit, else safe singleton fallback. Never splice extra code text into a frozen unapproved variant.
- Construct the source-grounded `InitialOutreachCheckoutOfferSet` (published Shared), preserving exact ordered code/provider IDs; attach it to the existing `recoveryPromise` in the **single** prepared/confirmed `ConversationMessage.content` linked by `outboundMessageId`. One initial WhatsApp message/credit only; no new attempt snapshot/table or second promotional message. Preserve customer-facing parameters exactly as submitted to Meta.
- In Shopify, outreach describes potential discounts and codes; it must NOT claim codes are preapplied to checkout. In Woo, ARCH-053 independently reads the confirmed immutable receipt and applies codes through Woo's native cart API only after customer confirmation. ARCH-052 neither issues nor validates restore links, mutates carts nor introduces Woo HTTP coupon calls.
- New unit and integration cases: Shopify PRODUCT+SHIPPING, ORDER+PRODUCT, same-line Plus/two-way tags, incompatible partner/unknown policy, Woo `individualUse`, triple combinations with one invalid member, Meta missing approval, retry/policy revocation, historic receipt/follow-up, and fallback single/no-send without duplicate message/billing.


**Attempt 4 architect blocker resolution — product CTA provenance and safety (normative, BG-owned):** `promotion.productUrl` is an **alternative-product promotional value**, not the existing `checkout.url` value. It must come verbatim from a `CommerceProduct.url` returned by a **successful, schema-validated** `commerce_get_product` MCP tool result for the **authenticated current shop**, carried via BACKGROUND-010's trusted result/evidence object. It must not be accepted from the model's output, its prose, merchant instructions, template samples, a checkout item, a request body, an arbitrary link, or a product-search string that has not been confirmed by exact-product lookup. The agent may select an offer/product ID; it does **not** generate the destination URL.

The Background resolver must enforce these explicit steps before populating any alternative-product body or CTA binding:

1. Require a validated `ALTERNATIVE_PRODUCT_PROMOTION` decision with a matching source-bound exact-product record assembled by BACKGROUND-010 from an authenticated MCP `commerce_get_product` result. Shop identity comes from the trusted Background caller and MCP outer request context, never model-supplied `shopId`. Reject a result lacking provenance, from another shop, without a successful MCP response or without a non-null product.
2. Compare the returned `CommerceProduct.productId` and nullable `variantId` exactly with the chosen product/variant identity. Preserve the original `CommerceProduct.url`; do not generate or substitute a merchant, model, catalogue-title or checkout URL. Missing or ambiguous identity is unusable.
3. Validate **only the promotional product URL**: require a nonempty absolute HTTPS URL, no username/password, non-default or explicit port, fragment, control/whitespace characters, IP-literal/localhost destination or excessive length (max 2048). Require the URL's canonical hostname to have been authorised for this authenticated shop by MCP-003's provider/connection-origin check, not by an allowlist inferred from the URL itself. Inability to establish trusted storefront-host ownership is a rejection, not a permission to broaden the allowlist. The approved Meta URL-button prefix and binding index remain immutable; encode the sourced URL only into the Meta-approved `promotion.productUrl` slot. Do not fetch, follow redirects or issue a checkout-link API call to validate a promotional URL.
4. If provenance, shop/ID match, URL or matching approved variant fails, return a typed `PROMOTION_PRODUCT_URL_UNAVAILABLE`/no-offer outcome at the existing preparation boundary. Use an independently approved NO_OFFER text template **only if the current policy and all existing send gates permit that fallback**; otherwise no-send. Never send the alternative promotion with an unsafe/missing product link, insert it into the wrong button, or silently replace `checkout.url`.
5. These product-only checks **must not be applied to `CheckoutRecovery.checkoutUrl`**. ARCH-052 reads that upstream-populated field unchanged as agreed; ARCH-053 owns its issuance/restoration. Preserve existing consent/STOP, moderation, Meta approval, credits, idempotency and durable `ConversationMessage.content` semantics.

The product URL evidence/validation helpers are Background-local (no new Shared contract, Prisma table, or Admin source change). Structured logging must include only bounded reason codes and source/tool identity, **never raw URLs or credentials**. Unexpected MCP/URL handling exceptions are logged through the Shared logger and propagated to the existing retry/failure boundary; expected invalid URLs return the typed unavailable result.


- No new offerSnapshot policy or sent-offer contract, no backfill or legacy adapters. The existing message receipt remains authoritative; preserve the existing one-send/idempotency rules.
- Before final send, re-read current merchant mode and selected IDs for FIXED; if the chosen offer is no longer authorised or the checkout is no longer recoverable, replace with approved NO_OFFER or skip send, never advertise revoked offer. When FIXED or AI has no verifiable offer, use NO_OFFER only if its own approved variant exists, otherwise typed no-send. If a verification budget was exhausted or the catalogue was incomplete, do not claim that no merchant discount exists. If the model fails and an MCP source-supported offer exists, use BACKGROUND-010's deterministic verified fallback.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider cart, coupon and order mutation is prohibited in ARCH-052. Checkout-link creation and customer-click cart restoration are upstream/out of scope.

### Final validation/admission contract — 31 October 2026 (mandatory)

- Consume only a `CHECKOUT_DISCOUNT` 1..3 **validated** `InitialOutreachCheckoutOfferSet`, with the Background-local per-member eligibility/line-match and per-pair compatibility evidence from BACKGROUND-010. **Do not** call an LLM to prove eligibility, inspect product names to match coupons, call a new MCP proof endpoint or re-evaluate arbitrary untrusted model output in the sender.
- Immediately before initial template preparation, **re-read** the current recovery `shopId`, generation and basket fingerprint, the current FIXED/AI/NONE merchant settings, current provider offer rows/IDs/codes/status/dates and a fresh, Background-local current-source fence (catalogue `syncGeneration` plus a digest of the selected same-shop rows) **instead of** an MCP revision field or an identity comparison to the snapshot seen by BG010. Treat the BG010 result as candidates only. Re-read each candidate through authenticated `commerce_get_discount_details`, re-run the same pure BACKGROUND-010 eligibility/combination helpers on trusted current facts and reject stale or unsupported members; do not reuse an old positive verdict. No **direct Shopify/Woo/hosted-API provider** call is allowed in Background's final guard; the separate BG016 price preflight may use the existing **private MCP exact-product** interface outside a database transaction. If exact current facts cannot be established, return approved NO_OFFER or typed no-send. Do not invent a five-minute TTL or mutate a checkout.
- For a changed/invalid member, recompute the **maximal separately validated subset of the already proposed members** (no new offer from a different shop/candidate). Every remaining member must still pass every individual condition and all remaining pairs. A 3->2 or 2->1 reduction requires selecting the *actual* approved matching plural/singular Meta revision before variable binding; unapproved plural/mixed copy => independently approved singleton or NO_OFFER/no-send. Re-check source status and authorisation at actual dispatch/admission. Record a single message for the **actual** sent set, never the pre-trim original.
- Bind `offer.codes` only from the ordered deliverable CODE members in the final verified set; automatic-only set has no code slot; mixed CODE/AUTOMATIC requires explicitly approved truthful mixed copy. Keep existing approved `offer.code` for single CODE. No aggregation of percentage savings, offer totals or claim that coupons were applied. The message receipt must preserve the exact ordered `InitialOutreachCheckoutOfferSet` in the original *confirmed* `ConversationMessage.content.recoveryPromise` and never in a second mutable claim. `RecoveryOutreachAttempt.outboundMessageId` must point to that confirmed message; retries/duplicate delivery must not create divergent receipts or extra credits.
- If the current checkout's original coupons conflict with newly recommended coupons, do not promise they will stack; original Woo applied codes and native restore/apply behaviour are handled **only in ARCH-053**. ARCH-052 must not create a checkout URL, verify it, or call Woo/Shopify redemption APIs.

### Accepted current-source revalidation contract — ARCH-052 architect unblock (31 October 2026)

**Supersedes only the prior requirement to identify/compare the source revision used by BG010.** Do not add `sourceRevision`, `snapshotId` or any new property to `CommerceToolResultSchema`, `CommerceDiscountDetailsSchema` or MCP results. Do not modify accepted Shared/MCP tasks, add an MCP tool, call Shopify/Woo directly or invent an independent source-of-truth for discount conditions. `InitialOutreachAgentResult` is a **candidate proposal**, not a valid send-time eligibility certificate. The `CommerceDiscountConditionFacts.observedAt` timestamp is evidence of observation, **not** a catalogue revision and not a five-minute proof.

**A. Exact files, types and ownership** (Background repository only):

- Create `src/services/recovery-offers/current-discount-source-fence.ts`: `readCurrentDiscountSourceFence(input): Promise<DiscountSourceFenceResult>`. Inject the existing Prisma client/transaction factory, clock and cancellation, not module-global mutable state. Use `canonicalJson` from the published `@modainteract/moda-interact-shared/commerce` and Node `createHash('sha256')`, not a new serializer or Shared schema. Export a readonly `DiscountSourceFence` containing `{shopId, platform, syncGeneration, selectedOfferIds, snapshotDigest}`; `snapshotDigest` is a lowercase 64-character SHA-256 hex digest. A `UNAVAILABLE` result includes one stable internal reason code; never export/log raw discount codes or `providerSnapshot`.
- Create `src/services/recovery-offers/current-outreach-offer-revalidation.service.ts`: `revalidateCurrentOutreachOffer(input): Promise<CurrentOutreachOfferDecision>`. Inject current context/price-report builder, `RecoveryOutreachMcpSelectorService`, source-fence reader and clock. `input` is `{shopId, checkoutRecoveryId, outreachAttemptId, proposed: InitialOutreachAgentResult, signal: AbortSignal}`. The discriminated output is `CHECKOUT_DISCOUNT` with **fresh** `InitialOutreachCheckoutOfferSet`, `members`, eligible-line decisions and pairwise group; `ALTERNATIVE_PRODUCT_PROMOTION` with exact refreshed source-bound offer/product; `NO_VERIFIED_OFFER`; or typed `FAILURE` (no unchecked offer may survive). All types remain Background-local; reuse imported BG010/BG016 and published commerce types. Use actual repository-relative imports; no duplicated cross-service type or eligibility algorithm.
- Integrate into the existing `initial-outreach-offer-selection.service.ts` and `recovery-template-integration/automated-recovery-template.service.ts` (plus both owning initial-send paths: `src/services/checkout-recovery/recovery-initiation.service.ts`, `src/services/woocommerce-recovery/woo-recovery-outreach.service.ts` and its `woo-recovery-outreach.adapters.ts` template/sender ports). The revalidator must run **after** BG010 and the refreshed BG016 context and **before** choosing/formatting the approved template. Existing `selectCompatibleCheckoutOffers` and `evaluateCheckoutDiscount` remain the only checkout eligibility/stacking algorithms. Extract the current pure `productTargetMatches` predicate from `agents/initial-outreach-offer.graph.ts` into a shared **Background-local** helper and call it from both BG010 and the final alternate-product guard; do not create a second targeting implementation.

**B. Deterministic source fence, both platforms:**

1. Validate 1..3 unique original `offerId` values for CHECKOUT or exactly 1 for ALTERNATIVE_PRODUCT. Never introduce a fourth/new ID or a different-shop offer. Query the existing `ShopifyDiscountCatalogue` (used by *both* Shopify and Woo sync) by authenticated `shopId`; query only those exact `ShopifyDiscount.id` rows with `shopId` in the same **short** `RepeatableRead` read-only transaction. Network/MCP/Meta operations MUST NOT execute in that transaction. Validate the `Shop.platform` against the recovery and each source row. Use `select` fields; no unbounded catalogue scan.
2. Require catalogue `status='CURRENT'`, finite positive `syncGeneration`, `activeSyncToken=null`, `unavailableAt=null`, and non-null `lastSuccessfulSyncAt`; every selected discount must exist exactly once with matching `shopId`, `lastSeenSyncGeneration=syncGeneration` and `unavailableAt=null`. This rejects a sync in progress, a failed/unavailable catalogue, or a Woo coupon retained after missing the most recent successful scan. Fail closed when unavailable. Do **not** treat a stale-but-previously-successful synchronisation as proof of current provider truth.
3. Create the digest over `canonicalJson({shopId,platform,catalogue,discounts})` encoded as UTF-8 with prefix `ARCH052_DISCOUNT_SOURCE_FENCE_V1\0`. The `catalogue` projection uses keys `status`, `syncGeneration`, `activeSyncToken`, `lastSuccessfulSyncAt`, `unavailableAt`. The `discounts` array is sorted ascending by internal `id`; each object uses exactly `id`, `shopId`, `shopifyDiscountNodeId`, `method`, `providerStatus`, `startsAt`, `endsAt`, `singleRedeemCode`, `codeCount`, `fixedSelectable`, `isAvailable`, `unavailableAt`, `lastSeenSyncGeneration`, `lastSyncedAt`, `updatedAt`, `providerSnapshot`. Convert Dates to UTC `.toISOString()` and preserve JSON `null`; the JSON snapshot remains internal to digest computation. The chosen published `canonicalJson` handles canonical key ordering; limit every fence database transaction to 2,000 ms `maxWait` and 10,000 ms `timeout` and reject expiration; reject missing/invalid fields, any individual `providerSnapshot` larger than 1,048,576 canonical UTF-8 bytes or a complete serialized digest input larger than 4,194,304 UTF-8 bytes; do not add a local generic JSON serializer. Hash **actual** persisted values, not a guessed revision or model text.
4. Take fence `F1`; open one new authenticated purpose-scoped MCP session and `tools/list`; call `commerce_get_discount_details({offerId})` **once for each original ID** (maximum three), plus exact `commerce_get_product` for the selected alternative product when needed. Apply the published `CommerceToolOutputs` validators in the existing selector. Bound this final discount/product read to **15,000 ms total**, with propagated cancellation, maximum three details and one exact product read. Treat `ERROR`, `details:null`, missing/invalid identity, unsupported/partial required conditions and exhausted budget as unavailable for that member; capture originating provider/MCP errors through the existing Shared logger. Close the MCP client in `finally` without losing the original error.
5. Take fence `F2` immediately after MCP reads and **require exact equality** of `shopId`, `platform`, `syncGeneration`, ordered IDs and `snapshotDigest` with `F1`. If unequal, fail the *entire* proposed discount group closed (approved NO_OFFER or typed no-send), not a mixed-generation offer. Recheck trusted merchant mode/selection and checkout/attempt generation, status and BG016 fingerprint before member evaluation. **Do not** attempt to prove F1 equals BG010's earlier observation; old BG010 evidence is discarded for eligibility.
6. For each fresh `details`, require exact `details.offer.offerId`, non-null `providerDiscountId`, matching provider and original `providerDiscountId`/method/code. Use **the just-returned** `details.offer` as `offerFromOptions` for `evaluateCheckoutDiscount({context: refreshedContext, offerFromOptions: details.offer, details, priceReconciliation: refreshedPriceReport, evaluatedAt: clock()})`; it is not a fabricated catalogue option. This is allowed only because the authenticated `commerce_get_discount_details` response already includes a validated `CommerceOfferSchema` and MCP reauthorises the offer **on every detail call**. Do not claim an offer appears in all pages of `commerce_get_discount_options`; no options scan or cursor is necessary. `SUPPORTED` only passes individually; `UNVERIFIABLE` and `NOT_APPLICABLE` are excluded.
7. Recompute `selectCompatibleCheckoutOffers({candidates: freshSupportedCandidates, proposedOfferIds: originalOrder})`; use only its supported 1..3 subset. Never reuse old `members`, `eligibility`, `group`, code, description or persisted sent promise from the model choice. When a member disappears or loses eligibility, reselect an independently Meta-approved matching single/plural/code/automatic template; mixed copy that is not approved must reduce to another **separately validated** subset or approved NO_OFFER/no-send. If `mode=NONE`, skip all discount calls; if FIXED changed or a policy override revoked an ID, no stale offer may pass. No second AI invocation or newly discovered offer is allowed.
8. For `ALTERNATIVE_PRODUCT_PROMOTION`, perform the same discount/merchant/source fencing, then require a *fresh* successful `commerce_get_product` for the original exact product/variant and use the BG010 pure product-target matcher with current facts. Preserve MCP-authenticated shop identity and current safe storefront URL as defined by the existing promotion URL policy. If the product/discount changed, is unverified or cannot be re-proven, use approved NO_OFFER or typed no-send—never claim a coupon applies to the abandoned cart and never invent an alternative.
9. At **actual provider-send admission**, take fence `F3` and re-read the attempt/recovery generation, BG016 basket fingerprint and current merchant mode/selected IDs. Require they still match the validated offer/`F2`. If changed, suppress the prepared promotion before Meta dispatch; do not reuse/restart old positive proof. Re-run BG016 at the final price-sensitive preparation boundary as already required and fail closed on new unknown monetary conditions. Perform all these reads outside the Meta call and without holding a database transaction across MCP/network operations. Pass the *in-memory* F2 token only on the `prepared` branch of the existing `AutomatedTemplateResult` and through the existing Woo `WooMarketingTemplate`/template-selector port; never serialize it into `ConversationMessage.content`, a Meta payload or a new persistence model. In Shopify `RecoveryInitiationService.handleCheckoutCreated`, validate F3 **after** `billingService.revalidateBeforeProvider` and **before** `outboundWhatsAppAdmissionService.sendTemplate`. In Woo `WooRecoveryOutreachService`, validate F3 **after** the second consent/order/template/credit checks and **before** `sender.sendInitial`, using the accepted token from the originally prepared template; the second Woo template comparison must not trigger a second AI invocation. For either platform, on pre-provider denial release the credit via the existing `releaseBeforeProvider` path and do not mark an unknown provider failure or send an older prepared template. Existing STOP/moderation/credit/idempotency gates remain authoritative. There is an unavoidable provider-side race after final admission; a sent WhatsApp message cannot be recalled.

**C. Exact failure and evidence semantics:** `F1/F2/F3` are in-memory, attempt-local *consistency checks*, not a stored five-minute certificate, independent durable ledger or proof of live Shopify/Woo redemption. A change to synchronised source or permission is never treated as an unchanged offer. On incomplete source, missing catalogue, mismatch, grant revocation, incomplete targeting, unknown price context, source churn or timeout: retain only a newly demonstrated eligible and pair-compatible subset when the two-sided fence is stable; otherwise select an independently approved compliant NO_OFFER or typed no-send. Never silently treat stale/missing as no discounts available; never introduce checkout-URL validation or direct provider HTTP calls. Audit the final actually sent offer set only through the existing confirmed `ConversationMessage.content`/`recoveryPromise` and `RecoveryOutreachAttempt.outboundMessageId`; log bounded shop/recovery/attempt, digest prefix, reason and original errors, not raw URLs/codes/provider snapshots.

### Actual provider failures at final send (mandatory 31 October 2026)

In the existing WhatsApp/Meta send integration (`src/services/whatsapp.service.ts`
and the established send/admission failure path), log the **actual Meta Graph
error** on non-success response: its original structured `error.message`,
`error.code`, `error_subcode`, `error_data` (only safe bounded fields),
HTTP status and Meta request/trace ID when supplied. Preserve the originating
exception/cause chain and the existing typed retry/send outcome. A Meta error
must never be logged merely as an inferred `META_SEND_FAILED`, a template
approval hypothesis or a fabricated provider message. `reasonCode` remains
separate. When Meta supplies no response, log the actual SDK/transport
exception as `origin:sdk_exception` and do not invent `providerError`.

Use the Shared logger and the provider-origin redaction contract in
`docs/observability/shared-logging.md`; do not log tokens, raw HTTP headers,
checkout/promotional URLs, actual customer template variables, provider success
bodies or unredacted error payloads. The real Meta failure must be observable
even where a permitted fallback/no-send/retry follows, without a second send
or credit charge. Preserve existing moderation, consent, idempotency and CAS.

### Shared WhatsApp sender / merchant-specific Reply binding — mandatory

- Before attempting Meta send, select the **provider-approved immutable revision** whose actual frozen BODY includes the `shop.name` merchant identification and context-Reply instruction specified by `ARCH-052-ADMIN-003`. This applies to CHECKOUT, ALTERNATIVE_PRODUCT, NO_OFFER and all single/multi-offer outcomes (TEXT and optional IMAGE). Do not append unapproved text outside the template, manufacture a template parameter, or select an older approval with missing instructions. If no qualifying revision exists for shop/WABA/purpose/locale/target/header, use typed no-send; do **not** fall back to a non-compliant NO_OFFER revision.
- Resolve `shop.name` from the authenticated `CheckoutRecovery.shop` and bind it to the frozen semantic position; the model, an MCP result, a separate merchant's catalog and a WhatsApp profile display name do not supply this identity. For one merchant's checkout, never bind another merchant's name even if the customer phone and sending WABA are shared.
- After provider confirmation, retain the real `providerMessageId`, `direction=OUTBOUND`, durable sent timestamp, `Conversation.id`, `CheckoutRecovery.id/shopId/customer`, and the existing `RecoveryOutreachAttempt.outboundMessageId` link through **the same existing** `ConversationMessage`/attempt receipt. This provider-message identity is the key used by `recovery-routing.service.ts` when a customer quotes the template with text or audio. Do not create a second message mapping, conversation, or outbound receipt.
- The send gate MUST be enabled only when `ARCH-052-BACKGROUND-015` has validated the existing quoted-message route for text and audio. A send may not claim that Reply reaches the correct merchant if there is no durable mapping to the actual Meta-confirmed outbound message. Preserve duplicate-send/credit, moderation, consent, STOP and follow-up invariants.
- Do not implement inbound transcription, standalone order-confirmation replies, a generic merchant inbox, or an order-to-conversation mapping in BACKGROUND-008; `BACKGROUND-015` owns the recovery reply route. Failed or uncertain Meta sends are not considered a valid quoted outbound until an existing confirmation/receipt is present.

### Final price-sensitive admission and optional IMAGE boundary — mandatory

This task owns the **final sender check**, not the BG016 comparison algorithm and not BG007's post-text image implementation. Immediately before selecting/binding the approved initial template and consuming the existing send-admission transaction, re-read the trusted recovery generation, basket fingerprint computed by BG016 `fingerprintRecoveryPricingBasket()`, and merchant settings and invoke BG016 price reconciliation **again for the current attempt**. Do not reuse the pre-LangGraph price observation on a later retry, claim a five-minute proof, fetch product prices from Shopify/Woo directly, or mutate the checkout. A newer checkout generation, changed line identity/quantity or unresolved current price context invalidates price-sensitive claims in the selected offer set. Recheck supported remaining offers and pairwise stacking with current source facts, choose only a source-supported approved price-neutral/singular/plural template, or return typed no-send. Do not run a second AI loop merely because prices changed.

- An observed catalogue difference is not a confirmed customer payable-price change. Suppress stale totals, `offer.savings`, current/new line prices and any claimed price rise/fall when checkout context is unverified. Effective monetary thresholds require a fresh, fully verified `currentMerchandiseSubtotal` from BG016. If unavailable, the affected offer is UNVERIFIABLE, not eligible by historical value; a separately supported non-monetary offer or approved NO_OFFER template may still send.
- Keep BG008's core **TEXT-first** functionality independent of BG007/ARCH-049 optional media. The optional IMAGE phase in BG007 must consume **only** the latter task's `OutreachProductMediaResult.kind:READY` with same shop/recovery/attempt/product/variant and verified R2 `publicImageUrl`; never bind raw MCP `product.imageUrl`, ShopBrand assets, R2 keys or unverified URLs to Meta. No BG008 -> BG007 dependency; BG007 depends on the accepted text sender and adds approved IMAGE after it. If optional media fails, use an independently approved TEXT variant without bypassing price/consent/discount send gates.
- Preserve exactly one provider-confirmed outbound receipt and credit as already defined. A prepared image object is not evidence that outreach was sent. Keep Meta approved text/promotion words unchanged unless an independently approved revision exists. Log original provider/MCP failures via the Shared logger with bounded redaction and internal reason codes separately.

## Work Items

- [ ] Invoke the accepted BG016 reconciliation at **final** initial send preparation and each retry; reject changed generation/fingerprint and stale price-sensitive claims, without directly calling Shopify/Woo providers.
- [ ] Re-evaluate thresholds and 1..3 compatible offers against current verified facts; choose correct approved price-neutral/singular/plural fallback or no-send without a second LLM pass or extra Meta attempt.
- [ ] Keep the approved TEXT path independent of BG007, but enforce that optional IMAGE enhancement can bind only a same-attempt BG007 READY R2 public derivative, never source product URL.

- [ ] Extend existing WhatsApp template send/automated-message persistence for 0/1/2 approved dynamic URL buttons, preserving exact approved index-to-variable mapping and existing consent/moderation/idempotency/credit guards.
- [ ] Bind `promotion.productUrl` only from BACKGROUND-010's authenticated current-shop `commerce_get_product` evidence; reject missing, mismatched, model-authored or unsafe product URLs with typed no-offer/no-send, and do not alter checkout URL handling.
- [ ] Select target/header/locale-specific approved TEXT registration before ambiguity resolution; use only the stored `CheckoutRecovery.checkoutUrl` for checkout CTA, no extra validation or link generation. Preserve unrelated URL handling.
- [ ] Extend the persisted `recoveryPromise` with the alternative product/offer identity in existing `ConversationMessage.content`; follow-up reads provider-confirmed sent message, not current catalogue state.


- [ ] Bind the three trusted offer outcomes into the existing approved template/send flow without a new messaging pipeline.

- [ ] Implement the final current-policy/recovery-generation/snapshot/source-fact recheck for all 1..3 members and every pair; on revocation/snapshot change, trim only to a proven subset and bind an independently approved matching Meta template or no-send.
- [ ] Persist the **actual sent** ordered group in the existing provider-confirmed `recoveryPromise` linked from `outboundMessageId`, never the rejected pre-send group; make retry/idempotency use that same confirmed message.
- [ ] Bind the exact already-stored `CheckoutRecovery.checkoutUrl` for both platforms to the existing approved checkout CTA without added URL validation or URL-specific fallback; prove no link-generation or restore API call occurs.
- [ ] Extend existing `RecoveryOfferPromise` and persisted `ConversationMessage.content` only as necessary for alternative products, and make follow-up consume the confirmed initial outbound message; never duplicate the same offer into offerSnapshot.
- [ ] Run two-provider end-to-end initial-send, current-policy-change, unchanged checkoutUrl binding, duplicate/idempotency and follow-up integration suites.

- [ ] Bind the current-shop `shop.name` and exact approved Reply guidance without modifying approved template bodies or sharing the merchant name from a different recovery.
- [ ] Extend/verify the existing provider-confirmed `ConversationMessage` receipt (`providerMessageId`, `sentAt`, `conversationId`, existing attempt link) so quoted text and voice events can resolve the same recovery; do not add another mapping table or another delivery attempt.
- [ ] Enforce no-send when a compliant approved revision or confirmed quoted-message receipt capability is missing; test retry, duplicate provider callbacks and historical recovery generation.

- [ ] Implement BG008-local current-discount source fence and final discount/product revalidator with a fresh MCP session and existing BG010/BG016 helpers. Verify F1/F2 equality and F3 provider-admission fencing; tests must distinguish current persisted evidence from live provider redemption. No Shared/MCP contract changes.

## Interfaces / Contracts

**Price admission input:** `CheckoutPriceReconciliationService.reconcile(input: PriceReconciliationInput): Promise<CheckoutPriceReconciliation>` from BG016, called after current recovery/generation/fingerprint is established and before final offer/template binding. `catalogueComparison` never authorizes price-change/savings copy; only `currentMerchandiseSubtotal` backed by equivalent checkout-context evidence can support current monetary thresholds. **Optional IMAGE input (implemented after text send in BG007):** its existing Background-local `OutreachProductMediaResult`; send only a matching `READY.publicImageUrl` with an approved IMAGE header. Do not add a Shared schema or an R2 image record.

**Product promotion evidence (Background-local type; do not put in Shared or MCP result envelope):**

```typescript
import type { CommerceProduct } from "@modainteract/moda-interact-shared/commerce";

export type SourceBoundOutreachProduct = Readonly<{
  sourceTool: "commerce_get_product";
  authenticatedShopId: string; // assigned by trusted MCP client context, not AI
  product: CommerceProduct;    // parsed successful MCP exact-product result
}>;
```

BACKGROUND-010 constructs this only after the MCP response validates; the model chooses identifiers, never `authenticatedShopId`, `sourceTool`, `product.url` or the product payload. The selected agent result carries the source-bound record to BACKGROUND-008 without model reconstruction. The trusted MCP/shop scope and product ID/variant ID must match before `product.url` may become `promotion.productUrl`. MCP-003 owns the independently authenticated storefront-host check on the provider projection. Background additionally rejects unusable URL syntax and preserves the approved Meta component binding index. These are application business/safety checks, not new Zod refinements. `checkout.url` remains upstream supplied, unmodified and outside this promotional URL check.


Shared-002 template `promotionTarget`, `checkout.url`/`promotion.productUrl` binding and URL-button contracts; existing `CheckoutRecovery.checkoutUrl` for both platforms; Background-local `InitialOutreachAgentResult`; existing persisted `recoveryPromise`/`ConversationMessage.content` receipt and `RecoveryOutreachAttempt.outboundMessageId`; existing Meta approval, consent, credit and send pipeline unchanged. No API restore-link response or new URL schema.

**Final source-state equivalence (architect-approved):** use published `CommerceToolInputs/Outputs.commerce_get_discount_details` and `commerce_get_product`, current shop/attempt/price context, existing `ShopifyDiscountCatalogue.syncGeneration` and exact same-shop `ShopifyDiscount` fields to build `DiscountSourceFence`. No new MCP wire fields or same-BG010-snapshot identity requirement. F1/F2 must agree before accepting fresh eligibility; F3 must still agree at actual dispatch admission. The source fence never substitutes for `CommerceDiscountConditionFacts`, BG016 or final native checkout validation.

## Dependencies

- `ARCH-052-BACKGROUND-016` — current, attempt-scoped, deterministic price-reconciliation operation. This is a prerequisite for truthful final TEXT outreach; `BACKGROUND-007` remains the **downstream optional** IMAGE enhancement.

- `ARCH-052-BACKGROUND-010` — accepted LangGraph agent and supported decision.
- `ARCH-052-BACKGROUND-005` — basket/shop presentation.
- `ARCH-052-ADMIN-001` — approved deterministic initial TEXT template target variants.

Product images (`BACKGROUND-007`/`ADMIN-002`) and Gateway deployed topology are **not** implementation prerequisites for the text-only send; those remain dependencies of final system-test certification. Do not add an ARCH-053 task dependency; ARCH-053 consumes confirmed ARCH-052 outbound receipts, never the reverse.

- `ARCH-052-BACKGROUND-015` — accepted recovery contextual-routing and guidance guarantees before the customer-facing instruction can be enabled.

## Enables

- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`
- `ARCH-052-SYSTEM-TEST-003` — shared sender contextual reply certification.

## Acceptance Criteria

- [ ] Final-send preflight detects fresh source price differences and unknown market/currency context; no stale checkout total, savings, unit-price change or threshold-qualified discount reaches Meta unless comparable current checkout evidence exists. Unchanged catalogue value alone never certifies checkout price.
- [ ] Price-sensitive offer invalidation reselects only a currently supported compatible subset and an independently approved correct template, or typed no-send; unchanged no-price claim may still use the existing TEXT send with consent/STOP/credit guards intact.
- [ ] TEXT send passes without BG007/R2; optional IMAGE send uses only BG007 READY `publicImageUrl` for exact shop/recovery/attempt/item and provider-approved header; image source URLs never appear in Meta header, recorded promise or provider-safe diagnostics.

- [ ] Inject Meta Graph 400/429 and a transport exception; verify emitted records retain the original Meta message/code/subcode and request ID (when supplied), separate internal reason codes, bounded redaction and unchanged send-admission/retry/credit semantics.

- [ ] Core text outreach sends without ARCH-049 media prerequisites or IMAGE template registration; independently approved two-button alternative template emits correct two provider CTA indexes and message receipt.
- [ ] The initial WhatsApp sender does not request any URL from API/ARCH-053; `checkout.url` reads the stored value, and no new checkout-URL validator is introduced.


- [ ] Correct approved text distinguishes discount on abandoned checkout from a separate product offer.
- [ ] No alternative promotion is prepared or sent unless its product CTA is sourced from a successful current-shop MCP exact-product result, matches the selected product/variant and passes product URL/approved storefront-host safety; a failure takes an approved NO_OFFER or no-send path and does not alter the checkout CTA.
- [ ] All added promotions have current MCP catalogue evidence, required marketing permissions and valid approved template.

- [ ] A multi-offer send requires one exact source-backed eligible matching-line decision per member (when line-specific), pairwise source-backed compatibility for every pair, current merchant selection/mode, unchanged checkout generation/fingerprint and an approved correct plural/mixed Meta revision; a revocation or changed fact never leaks a stale original set into rendered message or promise.
- [ ] No duplicate send/billing, no added checkout URL verification or provider lookup, no checkout URL generation/proxy, no duplicate URL persistence and no change to final outbound consent/moderation/admission gates.

- [ ] Final-send provider-error logging tests including a real distinct Meta error string, missing provider body and redacted customer/credential echo; verify emitted payloads and billing/idempotency remain unchanged.

- [ ] Every ARCH-052 initial message from a shared Meta phone identifies the correct tenant merchant and instructs the customer to quote **this** message using WhatsApp Reply and to send text or a voice note (two-minute limit). This remains true for no offer, one-to-three compatible discounts, alternative product, and approved TEXT/IMAGE variants.
- [ ] The real Meta-confirmed outgoing provider message ID maps back to exactly one existing conversation and recovery/attempt and is not reused across merchants, retries or WABA identities. No customer guidance is advertised when the provider registration is unapproved or the binding is absent; no additional credit is consumed.

- [ ] F1 and F2 bracket same-shop MCP detail reads with a CURRENT shared Shopify/Woo catalogue generation and selected-row canonical digest; F3 prevents a stale Meta send after current source/policy mutation. Missing, ongoing/failed sync, wrong shop, mismatched generation or changed row/snapshot always fail closed. No MCP revision field or direct provider API was added.
- [ ] Each original checkout offer is refreshed through `commerce_get_discount_details`, independently re-evaluated by BG010's existing pure helper and pair checker; all source-bound output bindings and provider-confirmed receipts use only the surviving current subset. Alternative promotions require independently refreshed product-and-offer targeting, with no duplicate targeting engine.

## Validation

- [ ] Add final-preparation fake BG016 tests covering before/after AI price change, price rise/decrease, unchanged catalogue but unknown checkout context, stale attempt/generation, minimum subtotal boundary crossing, Meta-only R2 derivative, IMAGE unavailable -> approved TEXT, send/no-send/idempotent receipt. Assert zero new checkout URL/provider API code and no duplicated credit.

- [ ] Background simulated Meta send tests for purpose/locale/target/header collision, one-button checkout, two-button alternative, unapproved second CTA, persisted receipt and follow-up, text-only when image work absent, and no ARCH-053 issuance calls.
- [ ] Inject successful/failed MCP exact-product results and test same-shop correct product, Shopify custom storefront host accepted when independently authenticated, Woo origin accepted, cross-shop/wrong-variant provenance rejected, missing/null product URL, model-supplied URL ignored, wrong approved CTA index, and unsafe `http:`, `javascript:`, `data:`, credential-bearing, port-bearing, hostname-prefix lookalike, loopback/IP-literal, whitespace/control or overlength URLs. Assert typed NO_OFFER/no-send, zero unsafe outbound Meta parameters, zero alternative-product promise recorded for rejected sends, bounded logging without raw URLs, and unchanged `checkout.url` behavior.


- [ ] Background initial-send unit and PostgreSQL tests (Shopify + Woo, duplicate/retry/provider race, merchant-setting changes, initial/follow-up persisted promise, unchanged binding of the stored checkoutUrl for both platforms). Assert no checkout URL validation branch, no restore-link API call and no checkout-link provider lookup.

- [ ] Add current-source revalidation tests: 3->2/2->1 approved-template re-selection, changed checkout fingerprint/generation, changed providerStatus/code/expiry, FIXED selection revoked after model choice, insufficient currency/targeting/partial rules, mixed automatic+code unapproved copy, provider-confirmed receipt containing only actual sent group, retry exactly-one-send/one-credit, and no external provider/checkout URL call.
- [ ] Existing ARCH-047/048/050 admission, moderation, STOP, credit and notification suites.
- [ ] Background build/lint and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

- [ ] Inject two shops sharing one Meta sender and one customer phone, source-backed `shop.name` values and distinct Meta message IDs; verify exact tenant-specific template parameter binding, correct durable receipt/attempt link, no cross-merchant context leakage, approved-only revisions, duplicate/retry semantics and typed no-send before approval.

- [ ] Add `tests/unit/services/recovery-offers/current-discount-source-fence.test.ts` and `current-outreach-offer-revalidation.service.test.ts`: two shops (same phone), both Shopify/Woo catalogue, Shopify and Woo F3 placement immediately before their existing `sendTemplate`/`sendInitial` provider admission, frozen in-memory token never persisted, duplicate Woo template selection not rerunning the agent, `syncGeneration` changes during reads, same-generation mutable row/code/status/`providerSnapshot` changes, changing FIXED selection/override, missing/old Woo coupon, no catalogue, missing/failed/partial detail, 3-to-2 and 2-to-1 re-evaluation, stale pair tags, missing alternative product, retry and F3 dispatch race. Assert F1/F2/F3 failure always blocks stale promotional claims, no raw provider data in logs, and no DB transaction spans MCP/Meta.
- [ ] Exercise the existing final-send/Meta/credit regression suites after integrating this guard; run focused lint, typecheck, full Background tests and the PostgreSQL/two-platform integration validation required by this task (report any genuinely unavailable harness instead of claiming it passed).

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-background/src/services/recovery-template-integration/automated-recovery-template.service.ts`
- `moda-interact-background/src/services/recovery-template-preparation/`
- `moda-interact-background/src/services/checkout-recovery/recovery-initiation.service.ts`
- `moda-interact-background/src/services/recovery-template-integration/prepared-template-send.ts`
- `moda-interact-background/src/services/conversation-moderation/automated-template-input.ts`
- `moda-interact-background/tests/integration/`

Source ownership is restricted to the assigned repository plus this task file. `moda_architect` owns architectural/dependency/index reconciliation. The implementing agent should stop for an architectural connector/schema gap rather than inventing a cross-repository workaround.

## Completion Report

### Status

Ready for Review — Attempt 2 implementation and validation evidence are recorded below. Attempt 1 details below are retained as historical evidence and are superseded where noted by the Attempt 2 completion update.

### Files Changed

Implementation work is in the dedicated Background task worktree. This task file records the current implementation and validation state.

### Work Completed

Implemented or extended the existing initial outreach path with attempt-scoped BG010/BG016 composition, post-agent trusted context refresh, target/header/shop-name-aware approved TEXT selection, singular/plural checkout CODE binding selection, maximal homogeneous offer-set fallback, alternative-product source provenance checks, separate checkout/product CTA binding, ordered multi-button persistence/transport, Woo attempt-ID forwarding, and singleton confirmed checkout-offer receipt parsing for follow-up.

Added the architect-approved Background-local current-discount source fence and final offer revalidator. F1/F2 use bounded same-shop RepeatableRead reads, catalogue `syncGeneration`, selected-row generation checks, and a canonical SHA-256 digest; a fresh authenticated MCP session rereads each proposed discount and exact alternative product outside database transactions. Fresh checkout decisions reuse BG010's eligibility and pair-selection helpers; alternative product targeting reuses its extracted pure matcher. F3 rechecks current recovery/attempt/price/policy and the source digest before Shopify and Woo provider admission. The token exists only in memory, and Woo no longer repeats template/agent selection at its second pre-provider check.

Added focused coverage for source-fence isolation/digest changes, F1/F2 churn, exact-product refresh and mismatch, F3 admission denial on both platforms, duplicate Woo selection avoidance, promotional URL rejection, and the previously implemented template/transport/receipt behavior.

Extended the existing Woo disposable outreach fixtures with the saved basket, published trusted prompt configuration, and approved CHECKOUT/shop-name template bindings now required by the initial sender. Added the same required basket fields to the generation-two recovery fixture; these are fixture-only changes and do not weaken the production trust checks.

Fixed the Shopify discount facts producer to include the schema-required subtotal currency while preserving the published decimal-string subtotal representation. Removed untrusted exception text from model-bridge, credential-revocation, conversation-wrapper, and generic recovery-offer logs; retained the original exception propagation. Corrected the initial-outreach finalization log to avoid duplicating a raw error message and aligned brittle runtime/billing assertions with current shared logging and package-version contracts.

### Validation Results

Passed: `pnpm exec tsc --noEmit`.

Passed: `pnpm lint`.

Passed focused Vitest run: 10 files, 131 tests, covering source fencing/revalidation, Shopify materialization, Woo admission, worker loading, legacy template-media behavior, and Support-notice finalization. All 12 files that failed in the preceding full-suite run also passed in a focused rerun after local fixes.

Passed: `git diff --check`.

Passed PostgreSQL source-fence integration through the disposable harness: 1 file, 2 tests. Both Shopify and WooCommerce persisted rows were exercised; a same-generation row update changed the digest, and a stale-generation row failed closed.

Passed existing ARCH-052 discount-selection PostgreSQL integration: 1 file, 2 tests.

Passed WhatsApp Cloud API emulator integration: 1 file, 1 test covering generated no-offer, checkout-code, and alternative-product payloads, including approved template identity/language and ordered URL button parameters.

Full Background unit suite (`pnpm test:unit`): an earlier run passed 326 files / 3,470 tests. This was superseded on 1 November by a fresh full run: **326 files / 3,488 tests passed**.

Additional Background safety unit selection: **passed** — 17 files and 206 tests covering Woo admission/send fence and notice finalization, Shopify consent, moderation, outbound admission, and credit/send admission.

Broader PostgreSQL integration attempt across 12 consent, STOP, moderation, credit, notification, and outreach files: **not passed** — 50 passed / 10 failed. Failures included the incomplete Woo trusted-context fixtures (currency/basket and prompt/template contract, addressed in the fixture updates above), an existing Woo permit-race log assertion that expected a sanitized synthetic error instead of the injected original error, an Aimock route construction assertion, and timeout/disposable-PostgreSQL readiness failures. This run is evidence of gaps, not a passing broad regression gate.

Focused Woo PostgreSQL/Redis initial-outreach integration: **passed in isolation** — 1 file, 17 tests. This run used the corrected trusted-context/template fixtures and a fresh disposable PostgreSQL/Redis environment. It resolves the previously inconclusive result for this focused suite, but does not establish a clean combined broad integration gate.

Focused Woo final-send-permit race integration: **passed in isolation** — 1 file, 5 tests. The permit logs a bounded `PERSISTENCE_FAILURE` plus safe error name/code, rethrows the original database exception, and preserves race behavior. Its focused unit selection passed with the current-source revalidation tests — 2 files, 30 tests.

Focused unit safety validation after those integration attempts: **passed** — 206/206 as above. Targeted ESLint on the three edited Woo fixture/test files and `git diff --check` completed without diagnostics.

Focused repeat of the eight selected consent/STOP/moderation/notification/recipient/template-admission PostgreSQL integration files: **passed after timeout isolation** — 38 tests total. The initial combined run had 35/36 pass because one general STOP-ordering case exceeded Vitest's default five-second timeout; rerunning that file with `--testTimeout 30000` passed all 3 tests. This focused result does not include the separate failing Woo initial-outreach or provider-race files.

Continued Attempt 1 validation: the current-source revalidation unit file passed — 23/23, including 3-to-2 and 2-to-1 proposed subsets, FIXED revocation, inactive/expired offers, exact-product refresh, and unsafe promotional URL rejection. A Background-local syntax guard now rejects non-HTTPS, credentials, explicit ports, fragments, whitespace/control characters, localhost/IP-literal hosts, and overlength promotional URLs before binding. It applies only to `promotion.productUrl`; stored `CheckoutRecovery.checkoutUrl` remains unchanged. This does not prove selection of the matching approved singular/plural Meta revision or end-to-end receipt for a reduced set.

The focused Woo permit unit and current-source revalidation suites passed together — 2 files, 41 tests. The automated template coordinator suite passed — 20/20, including 3-to-2 plural and 2-to-1 singular approved-revision selection, receipt payload containing only the surviving offers, one resolver invocation, and fail-closed behavior when the plural revision is unavailable. These coordinator tests use the real template preparer/receipt builder but do not simulate Meta confirmation or a database commit. Changed-file ESLint and `pnpm exec tsc --noEmit` passed after the URL guard and coordinator cases were added.

The focused template-preparer unit suite passed — 19/19. The ARCH-047 PostgreSQL template-preparation integration passed — 1/1 after its fixture was updated with the required promotion target, authenticated shop-name binding, and Reply instructions. `WhatsAppService` unit validation passed — 24/24, including source-faithful Meta error logging, redaction of injected phone/token/URL data, transport cause-chain preservation, and ordered dynamic buttons. Targeted ESLint on the modified implementation/test files and `pnpm exec tsc --noEmit` completed without diagnostics; `git diff --check` passed.

The ARCH-047 Meta provider-failure integration was rerun in isolation and remains **failed — 2/2**: the separate template-registration error path logs a plain non-JSON provider response body as `providerErrorMessage`/`providerErrorBody`. This is not the final WhatsApp send adapter owned by the send-logging acceptance item, so it was not changed in this attempt; it remains an adjacent logging finding for architect disposition.

Latest validation on 1 November: `pnpm test:unit` passed — 326 files / 3,488 tests; `pnpm lint` passed; `pnpm exec tsc --noEmit` passed. The updated Aimock integration now uses direct HTTP requests to a loopback-validated LLMock endpoint and a typed `CommerceModelInvoker`, following the working local HTTP pattern rather than the constructor mock seam. It passed with the focused disposable integration batch: 6 files / 24 tests across Aimock, both-platform source-fence persistence, Shopify discount selection, Woo initial outreach, template preparation and the WhatsApp template emulator. A second focused disposable batch passed: 6 files / 28 tests across Woo send-fence/admission races, Shopify final-template permit/status admission and initial outreach Support notification. These focused results do not replace the previously failed combined broad PostgreSQL run or downstream system certification.

Downstream system-test listing was attempted in `moda-interact-system-test` with the three ARCH-052 task IDs; the runner returned `Unknown scenario ARCH-052-SYSTEM-TEST-001`. No downstream system tests were executed or claimed.

At the end of Attempt 1, complete two-platform end-to-end/system coverage, a clean combined broad PostgreSQL regression gate, and several acceptance items remained uncertified. Attempt 2 validation and remaining gaps are recorded below.

### Deviations

The implemented F1/F2 fence brackets fresh MCP reads and detects changes to synchronized source rows, but it does not prove live Shopify/Woo redemption state. F3 has a provider-side race after the final admission check, as acknowledged by the accepted contract. Several listed adversarial, multi-member trimming, Postgres, and system-test cases remain unimplemented/unrun. The available broad integration run also surfaced the separately recorded failures above; do not treat it as regression certification.

### Assumptions

The accepted 31 October architect unblock is followed: no MCP revision/snapshot property or Shared/MCP contract change was introduced. The local catalogue generation and selected-row digest are used only as attempt-local consistency checks, not as a live provider eligibility certificate.

### Unresolved Issues

At the end of Attempt 1, remaining acceptance gaps included adversarial permission/source revocation coverage, full PostgreSQL/two-platform/system tests, and a clean combined broad regression gate. The downstream system-test runner did not recognize the ARCH-052 task IDs as executable scenarios. Attempt 2 disposition follows.

### Architectural Concerns

Report discovered cross-repository/credential/MCP-catalogue issues to `moda_architect`.

### Attempt 2 Completion Update

#### Changes and Evidence

- Preserved and continued the existing implementation from checkpoint commit `d2d51f4`; no user changes were discarded or rewritten.
- Added the bounded promotional product URL safety check and current-source revalidation/template-selection coverage in the checkpoint. Checkout URL handling remains unchanged.
- Pushed the implementation task branch `task/ARCH-052-BACKGROUND-008`. The branch contains the earlier implementation commit `895bfb3`, synchronization merge `178d236`, and preserved checkpoint `d2d51f4`.
- Updated only this task's status and Completion Report. The `## Architect Review` section remains untouched.

#### Attempt 2 Validation

- Passed full Background unit suite: 326 files, 3,488 tests.
- Passed Background lint and TypeScript no-emit typecheck.
- Passed focused source-fence, offer-revalidation, approved-template selection, and Woo send-admission tests: 4 files, 65 tests.
- Passed WhatsApp send adapter and provider-failure unit tests: 2 files, 35 tests.
- Passed persisted source-fence PostgreSQL integration: 1 file, 2 tests; passed Shopify discount-selection PostgreSQL integration: 1 file, 2 tests; passed WhatsApp template emulator: 1 file, 1 test.
- Passed initial-send/Aimock/Woo F3/template-preparation integrations: 4 files, 13 tests; passed final-template permit/status and Support-notice integrations: 3 files, 12 tests.
- Passed `git diff --check` for the implementation branch.

#### Remaining Gaps and Disposition

- The earlier broad PostgreSQL integration batch remains non-passing (50 passed, 10 failed) as documented above; focused relevant suites pass, but this is not a clean combined regression gate.
- Full downstream system certification remains unavailable: the system-test runner reported `Unknown scenario ARCH-052-SYSTEM-TEST-001`. This attempt did not claim system tests passed.
- The task's complete matrix of adversarial merchant permission/source revocation, every platform/mode/outcome combination, and all historical receipt/follow-up scenarios is not fully certified by the focused tests run here. The remaining matrix is returned for Architect review; no broader acceptance is claimed.
- The known registration-error integration finding for a plain non-JSON provider response remains outside this task's final-send adapter slice; final send adapter error/redaction tests passed.
- No schema, Shared/MCP contract, checkout URL validation/issuance, provider cart mutation, or cross-repository changes were made.

#### Branches

- Implementation branch: `task/ARCH-052-BACKGROUND-008`, pushed through `d2d51f4d56417cb07be6bf9918e79ad80e4e0398`.
- Parent task branch: `task/ARCH-052-BACKGROUND-008`; this report/status update is to be committed and pushed separately.

Completion Report status: Ready for Review. No Architect acceptance decision has been made by this agent.

### Attempt 3 Completion Update

#### Prepared Execution and Git Evidence

- Executed the matching prepared Attempt 3 packet; the launcher had already claimed the task and pushed parent claim commit `7958fa8e07db073bc01291db8b01bce18b15d61b`. No claim was repeated.
- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-052-BACKGROUND-008`; implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-052-BACKGROUND-008`.
- Both task branches are `task/ARCH-052-BACKGROUND-008`. Prepared parent pre-claim head was `4b2361dd48b26fb36a08e87876c249dbce43c5a1`; prepared implementation head was `d2d51f4d56417cb07be6bf9918e79ad80e4e0398`.
- Packet recorded both worktrees reused, clean before claim, task-branch fast-forward `not-needed`, and `origin/main` `already-current`. At verification, parent HEAD and `origin/task/ARCH-052-BACKGROUND-008` were both `7958fa8e07db073bc01291db8b01bce18b15d61b`; implementation HEAD and its matching origin task ref were both `d2d51f4d56417cb07be6bf9918e79ad80e4e0398`.
- Recursive implementation submodule sync/update passed; the database submodule was at `7c377282aa5819b3008b7d7f3018f44f4161523e`. Dependency gate passed. No worktree was recreated or reset.

#### Attempt 3 Changes and Validation

- Added `tests/unit/services/recovery-routing.service.test.ts`: `routes shared-sender quotes from the same phone to each exact merchant recovery` verifies two quoted provider message IDs for one customer phone and shared WABA resolve to distinct conversation, recovery and shop identities.
- Added `tests/unit/services/recovery-template-preparation/recovery-template-preparer.test.ts`: `binds each shared-WABA template to its own authenticated merchant name` verifies separate shop-scoped prepared `shop.name` values and catalogue lookups under the same WABA.
- Added `tests/unit/services/recovery-template-integration/automated-recovery-template.service.test.ts`: `passes the exact persisted SHOPIFY checkout URL to template preparation` and the corresponding `WOOCOMMERCE` case assert that the stored URL, including its original query encoding, is forwarded unchanged for both platform contexts.
- Full Background unit suite passed: `pnpm test:unit`, 326 files and 3,492 tests. Focused task unit selection passed: 5 files and 151 tests, covering template preparation, confirmed-message follow-up/history, shared-sender routing and both platform F3 admission paths. Background `pnpm lint` and `pnpm exec tsc --noEmit` passed. `git diff --check` passed.
- Isolated disposable PostgreSQL/integration results: `arch048-woo-initial-outreach.integration.test.ts` 17/17; `woo-initial-send-fence-races.integration.test.ts` 5/5; `arch052-discount-source-fence.integration.test.ts` 2/2; `initial-outreach-offer-aimock.integration.test.ts` 1/1; `arch052-shopify-discount-selection.integration.test.ts` 2/2; `arch052-initial-template-emulator.integration.test.ts` 1/1; `arch047-recovery-template-preparation.integration.test.ts` 1/1. The Woo initial-outreach suite covers concurrent dispatch/replay with one confirmed send and one credit; the current-source tests exercise persisted source mutation and the F3 unit cases deny dispatch after admission validation changes.
- Follow-up evidence includes the coordinator tests `reads a confirmed singleton checkout offer-set receipt for follow-up verification` and `denies a follow-up when initial proof is missing or unsafe`, plus the quoted text/audio recovery-routing cases. This is unit/routing evidence; no new two-merchant Meta-confirmed end-to-end receipt test was added.

#### Failure Classification and Remaining Scope

- The earlier broad disposable PostgreSQL run remains recorded as 50 passed / 10 failed. The retained Attempt 2 report describes the failure categories (Woo trusted-context fixture mismatch, stale Woo race-log expectation, Aimock route assertion, and disposable PostgreSQL readiness/timeouts), but does not preserve the original ten individual test names. Those historical names could not be recovered, so they are not fabricated here.
- The relevant current task suites for Woo initial outreach, Woo final-admission races, Aimock, and source fencing were rerun separately above and pass. Disposable PostgreSQL readiness/timeouts did not recur in these isolated runs. The combined broad batch was not rerun; these results do not certify it or establish that unrelated harness failures were resolved.
- The added tests establish separate preparation and quoted-message routing boundaries, not a full two-shop Meta send with distinct committed `ConversationMessage`/attempt receipts. Nor do the new platform URL tests execute a full provider send. The task's complete all-mode/all-platform end-to-end matrix, every listed policy/source mutation, and downstream system certification remain unverified; corresponding checklist items remain unchecked.
- The downstream system-test runner's `Unknown scenario ARCH-052-SYSTEM-TEST-001` remains a non-blocking downstream limitation. No runner changes or system-test certification are claimed. The separate template-registration logging path remains out of scope and unchanged.
- No schema, Shared/MCP contract, checkout URL validation/issuance, provider cart mutation, or cross-repository changes were made.

Completion Report status: Ready for Review. No Architect acceptance decision has been made by this agent.


## Architect Review

### Review Status

Changes Requested — Attempt 3. The same task is ready for Attempt 4 after this review is published.

### Review Notes

The Attempt 3 unit, lint, typecheck, and isolated integration results are useful, and the prepared-worktree evidence is complete. The attempt-3 branch adds the requested separate shared-sender routing, merchant-name preparation, stored checkout URL binding, and follow-up/history unit coverage. Review remains Changes Requested because the historical PostgreSQL failure evidence can now be recovered, one task-relevant failed integration case has no reported rerun, and the required confirmed-send tenant-isolation assertion remains unverified.

1. Reconcile the original 50-passed/10-failed run using the retained output artifact `copilot-terminal-output-497a3257-de64-4f30-af89-6c7203abf711.txt`; do not rerun the entire 12-file batch solely to recreate its aggregate. The exact failed cases and original outcomes are:
  - `tests/integration/arch048-woo-initial-outreach.integration.test.ts`: `persists exactly one confirmed send, Free credit charge and usage event under concurrent dispatch/replay`; `cancels a resumed generation, releases its reserved free credit once, and permits generation two independently`; `releases a resumed attempt from its exact paid-included reservation owner and replays idempotently`; `releases the reserved credit when placed arrives after the last preflight but before provider permit`; the corresponding `paid` and `cancelled` cases; and `rechecks authoritative local STOP after reservation and refunds without sending`. The first, second, placed/paid/cancelled, and STOP cases failed with `BASKET_CURRENCY_INVALID`; the paid-included case timed out at the default five seconds. Attempt 3 reports this isolated file passing 17/17 after fixture corrections. In the next Completion Report, map each exact selector to that run/result; do not report the original combined batch as passing.
  - `tests/integration/woo-initial-send-fence-races.integration.test.ts`: `rolls back the provider permit on a post-write database fault, logs and allows a safe retry` failed because the old assertion expected a synthetic `PERSISTENCE_FAILURE` instead of the injected originating error. Attempt 3 reports this isolated file passing 5/5; record that exact selector/result.
  - `tests/integration/initial-outreach-offer-aimock.integration.test.ts`: `routes real model/tool/model turns through loopback and returns the source-validated offer` failed because the expected local model route construction was absent. Attempt 3 reports the revised isolated Aimock test passing 1/1; record that exact selector/result.
  - `tests/integration/initial-outreach-agent-context.integration.test.ts`: `binds current shop policy, sequence-one attempt, published instructions and same-fingerprint price evidence` timed out at five seconds. No Attempt 3 rerun is recorded. Run this exact case alone against a fresh disposable PostgreSQL environment with a suitable test timeout (for example 30 seconds), then record its exact result and classify any remaining timeout using the readiness evidence. Fix it only if the failure is attributable to this task.

  No names are to be invented. The current exact log plus the Attempt 3 isolated suite totals are evidence for the nine rerun cases; only the trusted-context case needs a new execution unless a reviewable run artifact contradicts those totals. Do not expand this task into the separate template-registration logging path or claim the combined 50/10 run passed.

2. Add one bounded Background integration assertion for the remaining shared-sender acceptance gap. Using two shop recoveries for the same customer phone and shared WABA with a mocked/emulated Meta confirmation, assert each send binds its own trusted `shop.name`, receives a distinct provider message ID, persists the existing confirmed `ConversationMessage` and `RecoveryOutreachAttempt.outboundMessageId` relationship to the correct shop/recovery/conversation, and routes a quote of each ID back to that same recovery. Replay/duplicate delivery must not create another confirmed message or credit charge. The existing preparer and router unit tests are useful but do not jointly prove this durable confirmed-send path, as the Attempt 3 report acknowledges. Keep this in Background ownership; do not make downstream system certification a prerequisite.

3. Keep the report's other explicitly unverified all-mode/all-platform cases unchecked unless the current evidence proves them. Record the Attempt 3 focused pass totals as submitted, and do not claim the `Unknown scenario ARCH-052-SYSTEM-TEST-001` attempt as a Background failure; system tests remain terminal downstream work.

### Reviewed Files

- Attempt 3 implementation commit `904dedcce53354416b2ebcf04075bb12119911c6` and its three changed unit-test files.
- Completion Report Attempt 3 and retained broad PostgreSQL failure output `copilot-terminal-output-497a3257-de64-4f30-af89-6c7203abf711.txt`.
- The Attempt 2 review and corrections preserved in parent task-branch history.

### Validation Reviewed

Reviewed, but did not independently rerun, the submitted `pnpm test:unit` (326 files / 3,492 tests), focused unit selection (5 files / 151 tests), lint, typecheck, and isolated integration results. The historical output confirms 4 failed files / 10 failed tests in the original broad batch and provides the exact selectors above. Attempt 3 reports isolated passes of 17/17 Woo initial-outreach tests, 5/5 Woo send-fence race tests, and 1/1 Aimock test; no isolated rerun of the trusted-context test is reported. Implementation worktree is clean on `task/ARCH-052-BACKGROUND-008` at `904dedcce53354416b2ebcf04075bb12119911c6`, equal to `origin/task/ARCH-052-BACKGROUND-008`. Parent task worktree is clean on the same-named branch at `a8bc79107d13768619ebee3570134deb3d23ffde`, equal to its origin task ref. The prepared packet records clean reused canonical worktrees, `origin/main` already current, recursive submodule update passing, database submodule `7c377282aa5819b3008b7d7f3018f44f4161523e`, and dependency gate passing.

### Architecture Conformance

The inspected ownership and attempt-isolation requirements conform. Acceptance is withheld for the two bounded test/evidence gaps above. The original broad batch remains recorded as non-passing; isolated suite reruns are not represented as a clean combined regression gate.

### Follow-up

Return this same task to `ready`; preserve `attempt: 3`, clear `executor` and `claimed_at`, and preserve both task branches and all implementation commits. `moda_background` owns the bounded corrections above. All declared dependencies are Complete. After this parent review update is committed and pushed, the deterministic launcher may prepare and claim Attempt 4 in the same canonical task worktrees; normal synchronization and dependency checks still apply. The domain index and architecture task table already show `Ready` and remain consistent.
