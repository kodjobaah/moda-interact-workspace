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
- ARCH-052-SHARED-010
- ARCH-052-BACKGROUND-007
enables: []
created: '2026-10-29'
updated: '2026-10-30'
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

**Attempt 14 integrated certification:** exercise actual paged discount-options + on-demand details (including page 75 of 120, cursor tamper, provider `PARTIAL/UNKNOWN` and selected-vs-unselected offers), provider category/collection IDs and Woo simple products with null variant ID, LangGraph decisions, merchant `product_search` opt-in, approved target/locale/header variant selection, one- and two-CTA template transport, stored outbound message receipt and text-only send independent of IMAGE. Separately certify approved optional IMAGE enhancement after BG007/ADMIN002.

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

- Never claim live end-to-end approval based only on mocked Meta or development-local Woo HTTPS; list manual provider verification separately.
- No customer data leakage in fixture logs or screenshots.
- Review `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, and task preparation packet. Use dedicated mirrored task worktrees, correct start-of-attempt synchronization, and record both histories.
- Use `@modainteract/moda-interact-shared/logging` for new Node runtime logs. Unexpected exceptions must be logged with bounded, non-sensitive context and propagated to the owning retry/failure boundary; avoid silent catch. Plugin PHP must reuse its existing bounded operational logger.
- Do not send raw checkout URLs, bearer tokens, customer personal data or untrusted media source URLs to logs/telemetry.
- Provider cart, coupon and order mutation is prohibited in ARCH-052. Checkout-link creation and customer-click cart restoration are upstream/out of scope.

## Work Items

- [ ] Add Woo initial-outreach integrated scenarios.
- [ ] Exercise unchanged stored checkoutUrl CTA binding, coupon-rule failures and credit/STOP matrix; assert no checkout URL validation, restore-token issuance, private restore-link proxy or customer-click cart-restoration test is required by ARCH-052.
- [ ] Record reproducible certification and residual external verification.

## Interfaces / Contracts

Built-in MCP `commerce_get_discount_options`, published `commerce_search_products`/`commerce_get_product`, the existing generic `CommerceToolResultSchema`, SHARED-006 outreach purpose and SHARED-008 product contract, and the existing Meta initial-send/no-extra-database contract. SHARED-005 is a completed historical task, not an active proof consumer or publication prerequisite.

## Dependencies

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

## Enables

None.

## Acceptance Criteria

- [ ] Alternative-product CTA URL derives from a successful same-shop MCP exact-product response matching the selected product/variant; hostile or model-authored product URLs fail closed to an approved NO_OFFER/no-send, never appear in outbound Meta parameters or the confirmed alternative-product promise. Existing `checkout.url` remains unchanged and receives no new ARCH-052 URL validation.

- [ ] No invented coupon/product/category link or checkout discount when conditions are unknown/incomplete; a related product promotion is worded separately.
- [ ] Both CTA bindings are carried only when Meta-approved and ordered by actual provider indices; absent approved media does not block text-only flow.
- [ ] No ARCH-052 checkout URL issuance, extra validation or ARCH-053 reverse dependency.


- [ ] Every WooCommerce offer advertised has contemporaneous checkout or alternative-product MCP catalogue evidence.
- [ ] Direct MCP product search needs no hosted Moda API call.
- [ ] Initial outreach passes the existing recovery checkout URL unchanged into the approved template, keeps original consent, credit and idempotent send behavior across 3 modes, and adds no checkout URL validation, link generation or API proxy.

## Validation

- [ ] Negative integration cases: cross-tenant product result, wrong product/variant, missing/null URL, untrusted storefront origin, malformed/non-HTTPS URL, userinfo/port, hostname lookalike, private/loopback host and AI-proposed external link; verify no unsafe product CTA and no unapproved fallback. Positive case: independently trusted current-shop product URL and approved two-button index mapping.

- [ ] System-test harness with WordPress/WooCommerce, Postgres/Redis and Meta simulator.
- [ ] Woo Classic/Blocks recovery fixtures with pre-populated checkout URL, exact CTA binding and `git diff --check`; no customer-click restoration implementation/certification in ARCH-052.

Use actual repository scripts rather than assuming uniform `npm` commands; record required integration harness/environment gaps without claiming unrun tests passed.

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
