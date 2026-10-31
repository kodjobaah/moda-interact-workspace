---
id: ARCH-052-SYSTEM-TEST-002
architecture_id: ARCH-052
title: Certify Woo initial outreach, MCP commerce facts and existing checkout CTA
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 95
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-052-ADMIN-003
- ARCH-052-BACKGROUND-014
- ARCH-052-SHARED-012
- ARCH-052-BACKGROUND-008
- ARCH-052-BACKGROUND-015
- ARCH-052-GATEWAY-001
- ARCH-052-ADMIN-001
- ARCH-052-ADMIN-002
- ARCH-052-SHARED-003
- ARCH-052-MCP-001
- ARCH-052-MCP-002
- ARCH-052-MCP-003
- ARCH-052-MCP-006
- ARCH-052-COMMERCE-006
- ARCH-052-COMMERCE-007
- ARCH-052-BACKGROUND-010
- ARCH-052-SHARED-010
- ARCH-052-BACKGROUND-007
- ARCH-052-BACKGROUND-012
- ARCH-052-SHARED-014
enables: []
created: '2026-10-29'
updated: 2026-10-31
---

# ARCH-052-SYSTEM-TEST-002: Certify Woo initial outreach, MCP commerce facts and existing checkout CTA

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Independently certify WooCommerce initial recovery outreach, built-in MCP discount tools, code-published product tools, the standalone InitialOutreachOfferAgent and truthful alternative-product promotions.

## Context

Woo native coupon-proof endpoints are superseded for ARCH-052; promotional matching uses the MCP catalogue and product data. An already-populated `CheckoutRecovery.checkoutUrl` is assumed to be supplied by the upstream checkout recovery workflow; link generation and customer-click cart restoration are explicitly out of scope.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

**Attempt 14 integrated certification:** exercise actual paged discount-options + on-demand details (including page 75 of 120, cursor tamper, provider `PARTIAL/UNKNOWN` and selected-vs-unselected offers), provider category/collection IDs and Woo simple products with null variant ID, LangGraph decisions, merchant `product_search` opt-in, approved target/locale/header variant selection, one- and two-CTA template transport, stored outbound message receipt and text-only send independent of IMAGE. Separately certify approved optional IMAGE enhancement after BG007, ADMIN002 and BG012. Validate the sample-free Admin frozen IMAGE registration, trusted `https://www.modainteract.com/assets/whatsup-sample.jpeg` Meta upload and provider-only handle insertion (with a stubbed Meta Graph upload in automated tests), immutable-hash preservation, failure before Graph create and actual Meta IMAGE approval evidence where a live sandbox is available. The sample is not the checkout/product image.

**ARCH-053 is external ownership:** no Woo link issuance/restore implementation, validation or dependency belongs in this system test. Use an already-populated `CheckoutRecovery.checkoutUrl` fixture (including a Woo fixture) as input and assert the existing approved checkout CTA binds that value without any ARCH-052 link-generation call. ARCH-053 has its own terminal tests for restoring the URL.


- Run end-to-end WooCommerce fixtures for NONE/FIXED/AI and two-stage promotion decisions: checkout coupon qualifies; checkout coupon fails but related alternative product qualifies; only an unrelated product has genuine current offer; none verified; partial catalogue and provider timeouts. Assert exact approved Meta wording distinguishes alternative product from abandoned basket and does not invent an offer.
- Verify `tools/list` exposes system discount tools only to an authenticated shop and authorised outreach purpose, while product search tools require active code-published Commerce descriptor, feature entitlement and exact revision; conversation tools remain isolated. Test invalid shop/purpose, revoked tool/grant, selected FIXED IDs only, AI includes unchecked discounts, truthful 50-offer `truncated` handling, model invalid/timeout fallback and stale MCP catalogue evidence.
- For Woo, test **MCP -> WooCommerce REST** direct product search/detail, encrypted grant rotation, DNS/SSRF protection, variant image/category/permalink, and no hosted Moda API proxy or checkout-link generation call. For Shopify, test **MCP -> Shopify GraphQL** product search and detail. Discount discovery is sourced from current shop-scoped PostgreSQL catalogue records with no separate proof endpoint.
- Verify that the already-populated `CheckoutRecovery.checkoutUrl` is bound **unchanged** to the existing approved Resume checkout button for WooCommerce. ARCH-052 adds no checkout URL validation and no URL-specific fallback test; availability and correctness of the stored value belong to the upstream recovery workflow. A separate alternative-product `promotion.productUrl` must never replace the checkout URL. Verify checkout category translation, optional image fallback, per-template purpose+promotionTarget approval, cross-sell consent/category, final STOP/moderation, billing/Meta-confirmed persisted outbound template `recoveryPromise` and linked `outboundMessageId`, duplicate delivery and merchant Support notifications; preserve the no-coupon scenario.
- Exercise provider test sandboxes/simulators and clearly record which externally approved Meta/Store integration checks remain manual; system tests are terminal after all prerequisite implementation tasks are Complete.

## Out of Scope

- No provider implementation work, deployment configuration invention or early system-test gating of other tasks.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

### Multi-discount certification — normative 30 October 2026

Certify WooCommerce current merchant multi-selection against a source-backed 1..3 checkout offer group, each code/offer identity, pairwise supported combinations, incompatible/unknown partner fallback, approved plural Meta template revision, a single initial send/credit and the persisted confirmed outbound offer set. No forced application or savings guarantee at send time. Verify attempts, duplicates, messages, STOP/consent, moderator/billing and tenant isolation. Shopify same-line Plus/reciprocal tags must fail closed when unknown; Woo `individualUse` and post-restore apply behavior are separately certified in ARCH-053-SYSTEM-TEST-003.


- Never claim live end-to-end approval based only on mocked Meta or development-local Woo HTTPS; list manual provider verification separately.
- No customer data leakage in fixture logs or screenshots.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider cart, coupon and order mutation is prohibited in ARCH-052. Checkout-link creation and customer-click cart restoration are upstream/out of scope.

### Mandatory deterministic targeting + stacking matrix (WooCommerce)

Create source-like Woo checkout/coupon fixtures with stable line keys, exact product/variation/category IDs, observed pre-discount subtotal + authenticated currency, Woo coupon restriction snapshots and current merchant FIXED/AI policy:

1. Product/category include+exclude, variation versus parent-product ID, excluded sale item with observed/unknown sale status, and unavailable category IDs; unknown source fields never silently imply ALL.
2. `minimumAmount`/`maximumAmount` with inclusive boundary and wrong/missing store currency, **Woo zero/empty no-threshold values and zero global/per-user quotas correctly unrestricted versus positive exhausted quotas**, expired vs `expiryUnverified`, global/per-user usage restrictions, Woo email/metadata presence flags true/false/null and `limit_usage_to_x_items`; unsupported restrictions yield UNVERIFIABLE rather than a coupon claim.
3. Two distinct eligible coupons both `individualUse:false` versus one true and one null; triple with one incompatible member; incomplete Woo customer/extension constraints block a claimed compatible group, without asserting Woo native acceptance in advance.
4. FIXED selected versus unselected IDs and AI catalogue mode; offer revoked or basket generation changed after selection; one approved Meta plural message and the actual confirmed ordered `recoveryPromise` (not guessed restored savings); fallback to approved singleton or no-send without extra credit.
5. Confirm ARCH-052 does **not** generate/validate the stored `checkoutUrl`, mutate Woo cart or apply coupons. Native coupon redemption/conflicts on resume are covered by **ARCH-053-SYSTEM-TEST-003**, not these tests.

Each scenario must assert the eligibility verdict, line keys where relevant, subset/pair verdict, Meta binding, preserved confirmed receipt and tenant identity. Report mocked vs live provider evidence separately.

### Merchant identification and quoted Reply guidance — WooCommerce

- The provider-approved initial template for every covered offer mode visibly contains the **authenticated current-shop name** and tells the customer to use WhatsApp Reply on that exact message before sending text or voice (up to two minutes). Validate the frozen approval identity, TEXT/IMAGE where available, target-specific copy, correct 20-locale token preservation and no unapproved template fallback.
- The confirmed outbound `providerMessageId` and existing attempt/message/conversation association must be queryable by the runtime route. An incoming quote to that outbound ID resolves the intended shop and recovery; the same customer/WhatsApp sender sharing another shop must never change the destination. STOP precedence, moderation, single-credit and no duplicate message remain unchanged.
- Cross-platform same-number ambiguity and spoof/voice edge cases are covered by `ARCH-052-SYSTEM-TEST-003`; this task still certifies its **own** platform's end-to-end outreach and quoted Reply path.

### Optional R2 product-media acceptance matrix — 31 October 2026

- `ARCH-052-BACKGROUND-007` is terminal IMAGE-certification input; successful
  IMAGE sending requires an exact same-shop `commerce_get_product` variant/
  featured-image source, product-specific 1125x600 white-padded JPEG, verified
  public R2 GET/hash and independently Meta-approved IMAGE variant. The public
  header URL must begin at the configured R2 origin, **not** the merchant's raw
  image URL; TEXT fallback must remain independent of image infrastructure.
- For Shopify `Shop.domain`, verify `https://myshop.com` -> `myshop.com` and
  `myshop.com` -> `myshop.com`. For Woo canonical installation URL verify
  `https://myshop.com/myshop` -> `myshop.com-myshop` and nested path, `www`,
  case-preserving Woo paths and distinct `/a-b` versus `/a/b` keys. Public URL
  path must include exact platform, UTC preparation day and persisted outreach
  attempt ID. Product and variant tokens must match source identity digests.
- Exercise two registered shops, different platforms, two attempts on the
  same day, next-day retry of one attempt, follow-up as a new attempt, domain
  reassignment, untrusted image URL, wrong variant, revoked image, R2 HEAD
  mismatch, public GET failure and missing R2 configuration. None may allow
  cross-tenant object reuse or fallback to the original merchant image URL.
- Verify transparent/portrait/tiny/high-resolution test sources produce
  non-cropped, centred, white-padded **1125x600 JPEG**, with up/downscaling,
  metadata stripped and final bytes <5 MiB. Preserve ARCH-049 ShopBrand
  object layout and golden output test fixtures.
- Simulate image ready Oct 31, Meta send Nov 1 and upload with failed Meta
  send. R2 path indicates **preparation** date only; only the confirmed
  `ConversationMessage` and its `sentAt` establish actual customer outreach.
  No second send, Meta bypass, extra credit or media table.

## Work Items

### Provider-origin diagnostic certification — 31 October 2026 (mandatory)

- [ ] Provider-origin diagnostics: inject Woo REST 400 (`{"code":"woocommerce_rest_invalid_product_id","message":"Invalid product ID."}`), 401, 503 and a request-timeout SDK error in the accepted direct reader (MCP-006), plus MCP non-2xx and OpenRouter/Meta errors. Assert actual Woo/SDK/MCP/Meta messages, statuses/codes and request IDs appear in the owning server-side Shared log with separate internal reason codes, without inventing upstream errors when none were returned.
- [ ] Redaction and outcome preservation: inject credentials, customer emails/phone and signed URLs in error strings; assert redaction/truncation markers, no leakage to model/MCP/WhatsApp, no duplicate checkout recovery or credit, and unchanged authorized/denied/retry/fallback semantics.

- [ ] Add Woo initial-outreach integrated scenarios.

- [ ] Execute the five Woo eligibility/compatibility matrices above against validated MCP detail data and trusted cart lines, asserting explicit failure reasons and accurate approved fallback.
- [ ] Exercise unchanged stored checkoutUrl CTA binding, coupon-rule failures and credit/STOP matrix; assert no checkout URL validation, restore-token issuance, private restore-link proxy or customer-click cart-restoration test is required by ARCH-052.
- [ ] Record reproducible certification and residual external verification.

- [ ] Add WooCommerce initial-template fixture for NO_OFFER, CODE, AUTOMATIC and ALTERNATIVE_PRODUCT where supported, testing actual approved wording, same-shop `shop.name`, dynamic URL button indexes, provider-confirmed outbound message ownership, quoted text and voice routing.

## Interfaces / Contracts

Built-in MCP `commerce_get_discount_options`, published `commerce_search_products`/`commerce_get_product`, the existing generic `CommerceToolResultSchema`, SHARED-006 outreach purpose and SHARED-008 product contract, and the existing Meta initial-send/no-extra-database contract. SHARED-005 is a completed historical task, not an active proof consumer or publication prerequisite.

## Dependencies

- `ARCH-052-MCP-006` — accepted Woo source-origin error preservation.

- ARCH-052-BACKGROUND-008
- ARCH-052-GATEWAY-001
- ARCH-052-ADMIN-001
- ARCH-052-ADMIN-002
- ARCH-052-SHARED-003
- ARCH-052-MCP-001
- ARCH-052-MCP-002
- ARCH-052-MCP-003
- ARCH-052-COMMERCE-006
- ARCH-052-COMMERCE-007
- ARCH-052-BACKGROUND-010


- ARCH-052-SHARED-014
## Enables

None.

## Acceptance Criteria

- [ ] An upstream provider/SDK error cannot be replaced in logs by a guessed explanation; internal `reasonCode` remains separate, source provenance is truthful and security/redaction tests pass.

- [ ] Alternative-product CTA URL derives from a successful same-shop MCP exact-product response matching the selected product/variant; hostile or model-authored product URLs fail closed to an approved NO_OFFER/no-send, never appear in outbound Meta parameters or the confirmed alternative-product promise. Existing `checkout.url` remains unchanged and receives no new ARCH-052 URL validation.

- [ ] No invented coupon/product/category link or checkout discount when conditions are unknown/incomplete; a related product promotion is worded separately.
- [ ] Both CTA bindings are carried only when Meta-approved and ordered by actual provider indices; absent approved media does not block text-only flow.
- [ ] No ARCH-052 checkout URL issuance, extra validation or ARCH-053 reverse dependency.


- [ ] Every WooCommerce offer advertised has contemporaneous checkout or alternative-product MCP catalogue evidence.
- [ ] Direct MCP product search needs no hosted Moda API call.
- [ ] Initial outreach passes the existing recovery checkout URL unchanged into the approved template, keeps original consent, credit and idempotent send behavior across 3 modes, and adds no checkout URL validation, link generation or API proxy.

- [ ] Run provider-error fixtures with captured Shared logging sink across source services and injected transport/model failures; compare logged message to literal injected upstream error after only deliberate redaction/truncation, then verify no sensitive content and no provider error invented for local failures.

- [ ] A WooCommerce customer using WhatsApp Reply to a confirmed outbound initial message reaches its original recovery conversation for both text and audio, never another merchant's conversation; a missing/unapproved compliant template prevents the misleading invitation from being sent.

## Validation

- [ ] Negative integration cases: cross-tenant product result, wrong product/variant, missing/null URL, untrusted storefront origin, malformed/non-HTTPS URL, userinfo/port, hostname lookalike, private/loopback host and AI-proposed external link; verify no unsafe product CTA and no unapproved fallback. Positive case: independently trusted current-shop product URL and approved two-button index mapping.

- [ ] System-test harness with WordPress/WooCommerce, Postgres/Redis and Meta simulator.
- [ ] Woo Classic/Blocks recovery fixtures with pre-populated checkout URL, exact CTA binding and `git diff --check`; no customer-click restoration implementation/certification in ARCH-052.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

- [ ] Validate contextual quotation with the existing normalized `contextMessageId` (for both `content.type=text` and `content.type=audio`), source-specific shop and recipient checks, actual Meta `providerMessageId`, two-minute audio limit and deduplicated inbound persistence. No order confirmation routing is implied.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-system-test/ (new ARCH-052 Woo scenarios/fixtures)`

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
