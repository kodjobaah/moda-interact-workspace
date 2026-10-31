---
id: ARCH-052-SYSTEM-TEST-001
architecture_id: ARCH-052
title: Certify Shopify initial outreach personalization and all offer modes
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
- ARCH-052-BACKGROUND-013
- ARCH-052-ADMIN-003
- ARCH-052-SHARED-012
- ARCH-052-BACKGROUND-008
- ARCH-052-SHOPIFY-001
- ARCH-052-BACKGROUND-009
- ARCH-052-ADMIN-001
- ARCH-052-ADMIN-002
- ARCH-052-SHARED-003
- ARCH-052-MCP-001
- ARCH-052-MCP-002
- ARCH-052-MCP-003
- ARCH-052-COMMERCE-006
- ARCH-052-COMMERCE-007
- ARCH-052-BACKGROUND-010
- ARCH-052-GATEWAY-001
- ARCH-052-SHARED-010
- ARCH-052-BACKGROUND-007
- ARCH-052-BACKGROUND-012
- ARCH-052-BACKGROUND-011
- ARCH-052-SHARED-014
enables: []
created: '2026-10-29'
updated: 2026-10-31
---

# ARCH-052-SYSTEM-TEST-001: Certify Shopify initial outreach personalization and all offer modes

## Architecture

Architecture ID: `ARCH-052`.

Architecture document: `docs/architecture/ARCH-052-checkout-personalised-initial-whatsapp-outreach.md`.

Coordinator: `moda_architect`. This is a **portable canonical definition — defined but not materialised**. No developer Git branch/worktree, commit or push is asserted.

## Objective

Independently certify Shopify initial recovery outreach, built-in MCP discount tools, code-published product tools, the standalone InitialOutreachOfferAgent and truthful alternative-product promotions.

## Context

Terminal cross-service validation after architect acceptance and developer manual inspection; do not implement upstream features inside system test.

Evidence and paths refer to the 29 October 2026 08:07 uploaded workspace snapshot; implementation must re-read current task/code before claiming.

## Scope

**Attempt 14 integrated certification:** exercise actual paged discount-options + on-demand details (including page 75 of 120, cursor tamper, provider `PARTIAL/UNKNOWN` and selected-vs-unselected offers), provider category/collection IDs and Woo simple products with null variant ID, LangGraph decisions, merchant `product_search` opt-in, approved target/locale/header variant selection, one- and two-CTA template transport, stored outbound message receipt and text-only send independent of IMAGE. Separately certify approved optional IMAGE enhancement after BG007, ADMIN002 and BG012. Validate the sample-free Admin frozen IMAGE registration, trusted `https://www.modainteract.com/assets/whatsup-sample.jpeg` Meta upload and provider-only handle insertion (with a stubbed Meta Graph upload in automated tests), immutable-hash preservation, failure before Graph create and actual Meta IMAGE approval evidence where a live sandbox is available. The sample is not the checkout/product image.

**ARCH-053 is external ownership:** no Woo link issuance/restore implementation, validation or dependency belongs in this system test. Use an already-populated Shopify `CheckoutRecovery.checkoutUrl` fixture as input and assert the existing approved checkout CTA binds that value without any ARCH-052 link-generation call. ARCH-053 has its own terminal tests for restoring the URL.


- Run end-to-end Shopify fixtures for NONE/FIXED/AI and two-stage promotion decisions: checkout coupon qualifies; checkout coupon fails but related alternative product qualifies; only an unrelated product has genuine current offer; none verified; partial catalogue and provider timeouts. Assert exact approved Meta wording distinguishes alternative product from abandoned basket and does not invent an offer.
- Verify `tools/list` exposes system discount tools only to an authenticated shop and authorised outreach purpose, while product search tools require active code-published Commerce descriptor, feature entitlement and exact revision; conversation tools remain isolated. Test invalid shop/purpose, revoked tool/grant, selected FIXED IDs only, AI includes unchecked discounts, truthful 50-offer `truncated` handling, model invalid/timeout fallback and stale MCP catalogue evidence.
- For Woo, test **MCP -> WooCommerce REST** direct product search/detail, encrypted grant rotation, DNS/SSRF protection, variant image/category/permalink, and no hosted Moda API proxy or checkout-link generation call. For Shopify, test **MCP -> Shopify GraphQL** product search and detail. Discount discovery is sourced from current shop-scoped PostgreSQL catalogue records with no separate proof endpoint.
- Verify checkout category translation, image optional fallback, per-template purpose+promotionTarget approval, cross-sell consent/category, final STOP/moderation, billing/Meta-confirmed persisted outbound template `recoveryPromise` and linked `outboundMessageId`, duplicate delivery and merchant Support notifications; preserve no-coupon scenario.
- Exercise provider test sandboxes/simulators and clearly record which externally approved Meta/Store integration checks remain manual; system tests are terminal after all prerequisite implementation tasks are Complete.

## Out of Scope

- No production source modifications or downstream implementation tasks.

No out-of-repository modifications, new competing generic logger, uncapped provider operations, or implementation of Enables tasks.

## Requirements

### Multi-discount certification — normative 30 October 2026

Certify Shopify current merchant multi-selection against a source-backed 1..3 checkout offer group, each code/offer identity, pairwise supported combinations, incompatible/unknown partner fallback, approved plural Meta template revision, a single initial send/credit and the persisted confirmed outbound offer set. No forced application or savings guarantee at send time. Verify attempts, duplicates, messages, STOP/consent, moderator/billing and tenant isolation. Shopify same-line Plus/reciprocal tags must fail closed when unknown; Woo `individualUse` and post-restore apply behavior are separately certified in ARCH-053-SYSTEM-TEST-003.


- Record real test evidence and provider/API limitations; a mocked fixture alone is not a claim of live WhatsApp approval.
- Use architecture-approved test isolation, no customer data or real unauthorized WhatsApp sends.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider cart, coupon and order mutation is prohibited in ARCH-052. Checkout-link creation and customer-click cart restoration are upstream/out of scope.

### Mandatory deterministic targeting + stacking matrix (Shopify)

Create source-like checkout fixtures with **stable line keys**, product and variant IDs, provider category/collection IDs, observed pre-discount merchandise subtotal/currency, and same-shop discount detail responses. Test these scenarios end-to-end through MCP/Background, not only a mocked final positive boolean:

1. Product targeting inclusion and exclusion override, variant mismatch, two distinct cart lines sharing product ID, exact category/collection IDs versus category label only, truncated provider targets, and missing sale-item status.
2. Source minimum-subtotal inclusive edge and one unit below, different or missing threshold currency, `totalMinor` including tax/shipping while merchandise subtotal is too low, minimum quantity with known/unknown scope, usage exhaustion, customer restriction, and known expired/unavailable offer.
3. Two disjoint PRODUCT discounts (mutual class permissions, no Plus required); same-line PRODUCT+PRODUCT with Plus and reciprocal **both-direction** tags; non-Plus, one-way tags, unknown tags, unknown/false class booleans, ORDER+PRODUCT and PRODUCT+SHIPPING pairs; all three pairs for a triple.
4. Model proposes A/B/C but only A/C pair is source-supported; verify exactly A/C is rendered in an independently approved plural template and the confirmed receipt; if only A is source-supported, verify approved singular fallback. Revocation/checkout generation changes between selection and send cannot produce stale plural copy or duplicate credits.
5. `PARTIAL` facts missing only combination fields allow eligible *singleton* when all other conditions are established, while incomplete targeting/customer/quantity excludes even singleton; catalogue pagination incomplete must not be reported as exhaustively checked.

Any `UNKNOWN`/unsupported condition affecting eligibility or pair support must lead to a proven subset or approved NO_OFFER/no-send. Provider checkout remains final authority; do not assert discounts are guaranteed applied. Record named scenario outcomes in the Completion Report.

## Work Items

### Provider-origin diagnostic certification — 31 October 2026 (mandatory)

- [ ] Provider-origin diagnostics: inject Shopify discount-sync GraphQL `errors` with HTTP 200, product-search GraphQL 403, distinct OpenRouter 400/429 messages, Meta upload/CREATE/send failures and an MCP non-2xx response. At the owning logger boundary, assert **actual returned** source messages/codes/request IDs, distinct internal reason codes, original SDK transport exceptions where no response exists, and no invented provider detail. Distinct stages must be traceable with shop/recovery/attempt or request correlation.
- [ ] Security/failure isolation: inject provider error strings containing bearer token, email, signed URL and prompt text; assert only explicitly redacted/truncated provider-origin fragments reach Shared logs, no such values reach MCP results, model context, WhatsApp or saved snapshots. Preserve retries, approved fallback and single-send/credit semantics; sink failures do not change business result.

- [ ] Assemble isolated fixture and full initial send flows.
- [ ] Run negative/race/fallback/provider-budget matrix.

- [ ] Run the five mandatory Shopify eligibility and pair/triple matrices above with checkout-line and source-currency assertions, verify live MCP facts versus the trusted checkout projection, and prove no model-supplied eligibility boolean is trusted.
- [ ] Return certification and outstanding external Meta/provider checks.

## Interfaces / Contracts

Built-in MCP `commerce_get_discount_options`, published `commerce_search_products`/`commerce_get_product`, the existing generic `CommerceToolResultSchema`, SHARED-006 outreach purpose and SHARED-008 product contract, and the existing Meta initial-send/no-extra-database contract. SHARED-005 is a completed historical task, not an active proof consumer or publication prerequisite.

## Dependencies

- ARCH-052-BACKGROUND-008
- ARCH-052-SHOPIFY-001
- ARCH-052-BACKGROUND-009
- ARCH-052-ADMIN-001
- ARCH-052-ADMIN-002
- ARCH-052-SHARED-003
- ARCH-052-MCP-001
- ARCH-052-MCP-002
- ARCH-052-MCP-003
- ARCH-052-COMMERCE-006
- ARCH-052-COMMERCE-007
- ARCH-052-BACKGROUND-010
- ARCH-052-GATEWAY-001


- ARCH-052-SHARED-014
## Enables

None.

## Acceptance Criteria

- [ ] An upstream provider/SDK error cannot be replaced in logs by a guessed explanation; internal `reasonCode` remains separate, source provenance is truthful and security/redaction tests pass.

- [ ] Alternative-product CTA URL derives from a successful same-shop MCP exact-product response matching the selected product/variant; hostile or model-authored product URLs fail closed to an approved NO_OFFER/no-send, never appear in outbound Meta parameters or the confirmed alternative-product promise. Existing `checkout.url` remains unchanged and receives no new ARCH-052 URL validation.

- [ ] No invented coupon/product/category link or checkout discount when conditions are unknown/incomplete; a related product promotion is worded separately.
- [ ] Both CTA bindings are carried only when Meta-approved and ordered by actual provider indices; absent approved media does not block text-only flow.
- [ ] No ARCH-052 checkout URL issuance, extra validation or ARCH-053 reverse dependency.


- [ ] Every Shopify offer advertised has contemporaneous checkout or alternative-product MCP catalogue evidence.
- [ ] Direct MCP product search needs no hosted Moda API call.
- [ ] Initial outreach keeps original safety, credit and idempotent send behavior across 3 modes.

- [ ] Run provider-error fixtures with captured Shared logging sink across source services and injected transport/model failures; compare logged message to literal injected upstream error after only deliberate redaction/truncation, then verify no sensitive content and no provider error invented for local failures.

## Validation

- [ ] Negative integration cases: cross-tenant product result, wrong product/variant, missing/null URL, untrusted storefront origin, malformed/non-HTTPS URL, userinfo/port, hostname lookalike, private/loopback host and AI-proposed external link; verify no unsafe product CTA and no unapproved fallback. Positive case: independently trusted current-shop product URL and approved two-button index mapping.

- [ ] System-test declared integration commands, PostgreSQL/Redis and Meta simulator checks.
- [ ] Test evidence with logs/traces and `git diff --check`.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation pass, complete the report, set task `status: review`, hand the implementation branch and parent task report to `moda_architect` and **STOP**. Do not begin a dependent task, merge, push main, or edit architecture indexes as a repository agent.

## Implementation Notes

**Expected owning repository locations (verify paths in the execution worktree; create proposed paths only if appropriate):**

- `moda-interact-system-test/ (new ARCH-052 Shopify scenarios/fixtures)`

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
