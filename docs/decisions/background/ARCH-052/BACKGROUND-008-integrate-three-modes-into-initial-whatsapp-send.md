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
status: pending
priority: 65
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-SHARED-012
- ARCH-052-ADMIN-003
- ARCH-052-BACKGROUND-010
- ARCH-052-BACKGROUND-005
- ARCH-052-ADMIN-001
enables:
- ARCH-052-SYSTEM-TEST-001
- ARCH-052-SYSTEM-TEST-002
created: '2026-10-29'
updated: '2026-10-30'
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

## Work Items

- [ ] Extend existing WhatsApp template send/automated-message persistence for 0/1/2 approved dynamic URL buttons, preserving exact approved index-to-variable mapping and existing consent/moderation/idempotency/credit guards.
- [ ] Bind `promotion.productUrl` only from BACKGROUND-010's authenticated current-shop `commerce_get_product` evidence; reject missing, mismatched, model-authored or unsafe product URLs with typed no-offer/no-send, and do not alter checkout URL handling.
- [ ] Select target/header/locale-specific approved TEXT registration before ambiguity resolution; use only the stored `CheckoutRecovery.checkoutUrl` for checkout CTA, no extra validation or link generation. Preserve unrelated URL handling.
- [ ] Extend the persisted `recoveryPromise` with the alternative product/offer identity in existing `ConversationMessage.content`; follow-up reads provider-confirmed sent message, not current catalogue state.


- [ ] Bind the three trusted offer outcomes into the existing approved template/send flow without a new messaging pipeline.
- [ ] Bind the exact already-stored `CheckoutRecovery.checkoutUrl` for both platforms to the existing approved checkout CTA without added URL validation or URL-specific fallback; prove no link-generation or restore API call occurs.
- [ ] Extend existing `RecoveryOfferPromise` and persisted `ConversationMessage.content` only as necessary for alternative products, and make follow-up consume the confirmed initial outbound message; never duplicate the same offer into offerSnapshot.
- [ ] Run two-provider end-to-end initial-send, current-policy-change, unchanged checkoutUrl binding, duplicate/idempotency and follow-up integration suites.

## Interfaces / Contracts

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

## Dependencies

- `ARCH-052-BACKGROUND-010` — accepted LangGraph agent and supported decision.
- `ARCH-052-BACKGROUND-005` — basket/shop presentation.
- `ARCH-052-ADMIN-001` — approved deterministic initial TEXT template target variants.

Product images (`BACKGROUND-007`/`ADMIN-002`) and Gateway deployed topology are **not** implementation prerequisites for the text-only send; those remain dependencies of final system-test certification. Do not add an ARCH-053 task dependency; ARCH-053 consumes confirmed ARCH-052 outbound receipts, never the reverse.

## Enables

- `ARCH-052-SYSTEM-TEST-001`
- `ARCH-052-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Core text outreach sends without ARCH-049 media prerequisites or IMAGE template registration; independently approved two-button alternative template emits correct two provider CTA indexes and message receipt.
- [ ] The initial WhatsApp sender does not request any URL from API/ARCH-053; `checkout.url` reads the stored value, and no new checkout-URL validator is introduced.


- [ ] Correct approved text distinguishes discount on abandoned checkout from a separate product offer.
- [ ] No alternative promotion is prepared or sent unless its product CTA is sourced from a successful current-shop MCP exact-product result, matches the selected product/variant and passes product URL/approved storefront-host safety; a failure takes an approved NO_OFFER or no-send path and does not alter the checkout CTA.
- [ ] All added promotions have current MCP catalogue evidence, required marketing permissions and valid approved template.
- [ ] No duplicate send/billing, no added checkout URL verification or provider lookup, no checkout URL generation/proxy, no duplicate URL persistence and no change to final outbound consent/moderation/admission gates.

## Validation

- [ ] Background simulated Meta send tests for purpose/locale/target/header collision, one-button checkout, two-button alternative, unapproved second CTA, persisted receipt and follow-up, text-only when image work absent, and no ARCH-053 issuance calls.
- [ ] Inject successful/failed MCP exact-product results and test same-shop correct product, Shopify custom storefront host accepted when independently authenticated, Woo origin accepted, cross-shop/wrong-variant provenance rejected, missing/null product URL, model-supplied URL ignored, wrong approved CTA index, and unsafe `http:`, `javascript:`, `data:`, credential-bearing, port-bearing, hostname-prefix lookalike, loopback/IP-literal, whitespace/control or overlength URLs. Assert typed NO_OFFER/no-send, zero unsafe outbound Meta parameters, zero alternative-product promise recorded for rejected sends, bounded logging without raw URLs, and unchanged `checkout.url` behavior.


- [ ] Background initial-send unit and PostgreSQL tests (Shopify + Woo, duplicate/retry/provider race, merchant-setting changes, initial/follow-up persisted promise, unchanged binding of the stored checkoutUrl for both platforms). Assert no checkout URL validation branch, no restore-link API call and no checkout-link provider lookup.
- [ ] Existing ARCH-047/048/050 admission, moderation, STOP, credit and notification suites.
- [ ] Background build/lint and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

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

Not Started — portable definition, no task claim.

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run.

### Deviations

None reported.

### Assumptions

Execution will verify its current workspace, source state, dependency versions and test harness.

### Unresolved Issues

None established by implementation.

### Architectural Concerns

Report discovered cross-repository/credential/MCP-catalogue issues to `moda_architect`.


## Architect Review

### Review Status

Pending.

### Review Notes

Planning only; no source implementation accepted.

### Reviewed Files

The task definition was authored from the 29 October 2026 snapshot; a code implementation has not been reviewed.

### Validation Reviewed

None for implementation.

### Architecture Conformance

To be determined after implementation review.

### Follow-up

Materialise with the canonical task launcher after the planning patch is integrated and dependencies become Complete.
