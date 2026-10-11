---
id: ARCH-035-WOOCOMMERCE-007
architecture_id: ARCH-035
title: Capture supported Woo cart and checkout activity
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 63
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-035-API-008
enables:
  - ARCH-035-BACKGROUND-001
  - ARCH-035-SYSTEM-TEST-002
created: 2026-10-11
updated: 2026-10-11
---

# ARCH-035-WOOCOMMERCE-007: Capture supported Woo cart and checkout activity

## Architecture

- Architecture ID: `ARCH-035`
- Architecture document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`
- Coordinator: `moda_architect`
- Source baseline: uploaded `moda-interact-workspace(20261011-185536).zip`; task is a portable definition, not a claimed/materialised worktree.

## Objective

Publish accurate cart/checkout updates from Woo classic and Blocks/Store API flows to the authenticated Moda commerce ingress.

## Context

The previous Shopify/Woo merchant-screen parity assessment showed this specific gap. Reuse the already accepted
ARCH-026 WordPress connection, locale and Shop security foundations and ARCH-027 billing components; do not duplicate
provider-neutral Moda domain state. The current capability is not established by this task definition.

## Deterministic implementation specification — mandatory

**Architect contract.** The exact model/column names, paths, API shapes, authentication boundary, state machine and
negative cases below are the implementation target. This section supersedes less-specific high-level text elsewhere
in this task. Agents may split production code into smaller modules, but must not change a public contract, migration
field, ownership rule, or dependency without returning to the architect. If a named existing dependency is absent or
incompatible, **STOP** and report the precise finding; do not silently invent a substitute.

**Files:** new `includes/Activity/{CheckoutIdentity,CheckoutSnapshot,ActivityOutbox,ActivityPublisher}.php` and
PHPUnit tests; thin activation/bootstrap hooks in `includes/Plugin.php`/`includes/Runtime.php`; add checkout consent
UI adapter under `includes/Activity/CheckoutConsent.php` with WordPress gettext strings. Use WooCommerce Action
Scheduler (already a Woo dependency) for bounded async delivery; no homegrown WordPress database table, no direct JS
POST to hosted API and no main-thread remote HTTP on checkout.

**Capture contract:** for classic Woo cart/checkout use documented `woocommerce_cart_updated`,
`woocommerce_checkout_update_order_review`, `woocommerce_checkout_create_order` and equivalent server-side hooks
after checking Woo version; for Checkout Blocks use Store API hooks
`woocommerce_store_api_checkout_update_order_meta` and `woocommerce_store_api_checkout_order_processed` (or the
supported order hooks used by WOO-008) with tests proving Blocks firing. Generate one UUID `checkoutKey` per Woo
session stored as opaque Woo session attribute, stable across cart updates; persist this key on the order with Woo
CRUD `update_meta_data('_moda_checkout_key', key)` (HPOS-safe, never `postmeta` SQL). Maintain monotonic revision per
checkoutKey. No token fabrication from email/IP; cart without checkout URL sets URL null.

**Privacy/consent:** collect explicit WhatsApp recovery consent from a dedicated checkbox/Store API extension, record
time only if opted-in, and validate actual submitted E.164; never infer opt-in from terms-of-sale, marketing checkbox
or order creation. Snapshot matches Shared v1 **exactly**, max 20 typed line items, same-origin checkoutUrl, no
billing addresses/email/name/payment metadata. Save `eventId`, canonical bytes, `checkoutKey`, revision in an Action
Scheduler durable job once; retries preserve same ID/bytes. Publisher calls API-008 server-to-server via stored
credential, exponential capped retry (e.g. 30s, 2m, 10m, 30m, max 6), redacts logs, and doesn't block checkout or
customer order placement. Installation disconnect immediately halts sends. Test guest/auth, Classic/Blocks, empty
cart, updates, session expiry, 5xx/network/replay, HPOS and consent/no-number.

## High-level scope (non-authoritative summary)

- Use appropriate WooCommerce-supported hooks in PHP for guest and authenticated carts and checkout updates, including cookie/session/checkout identity stability.
- Send Shared v1-compliant minimal consent-authorised snapshots via server-side installation credential, bounded retries and deterministic idempotency.
- Respect privacy/redaction and never invent customer phone, email or checkout URL; do not send arbitrary browser-authored transactions straight to Moda.
- Keep hook/runtime extraction modular and ensure graceful failure does not block checkout completion.

## Out of Scope

- Unrelated Shopify or Woo Billing feature changes; changing another repository in this task.
- Other services' implementation code, `docs/decisions/**/_index.md`, and architecture index reconciliation.

## Implementation work items — mandatory

- [ ] Implement **exactly** the named files, routes/models and public DTO fields in the Deterministic implementation specification; do not widen cross-repository ownership.
- [ ] Enforce every declared shop/platform binding, validation boundary, state transition, CAS/idempotency invariant, denial path and privacy restriction.
- [ ] Implement the **specific negative and concurrency test matrix** named in the specification; record actual commands and real results.
- [ ] Prove that affected Shopify behaviour and current ARCH-026/027 Woo onboarding/billing contracts are preserved.
- [ ] Provide a bounded diff, changed-file list, applied migration/Shared package version where applicable, task Completion Report, and clean synchronised implementation/task worktree evidence.

## Cross-repository boundary (common requirements)

- Owning repository: `moda-interact-woocommerce`; consume only versioned, accepted cross-repository contracts.
- Hosted Woo identity is the authenticated Shop/installation; no client-controlled `shopId` or Shopify-session authentication. Where browser UI is in scope, transport runs through privileged WordPress REST/PHP with nonce and `manage_woocommerce` capability.
- For merchant display, all 20 supported WordPress UI locales use administrator language with site fallback; this must not change Shop or customer conversation language.
- New or changed externally visible API fields require strict bounded runtime schema validation and a matching OpenAPI/Shared contract owned by the producer.
- No additional external interface is authorised beyond the bounded scope above.

## Dependencies

- `ARCH-035-API-008` must be architect-accepted Complete before this task is claimed.

## Enables

- `ARCH-035-BACKGROUND-001`
- `ARCH-035-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Classic checkout, Checkout Blocks, guest/authenticated and empty/updated cart smoke matrix.
- [ ] Duplicate activity, throttling/timeout, consent and disconnect tests.
- [ ] WordPress activation/uninstall/HPOS compatibility and source/ZIP tests.
- [ ] Scope stays within `moda-interact-woocommerce` and preserves approved cross-provider and 20-locale contracts.
- [ ] Baseline, task launcher isolation, implementation commit, parent task report and regression evidence are recorded without false claims for unavailable provider services.
- [ ] `git diff --check` and repository-required build/test/lint commands pass or precise blockers are reported.

## Validation

- [ ] Run repository-declared focused test suites plus full typecheck/lint/build where applicable.
- [ ] Run real integration/black-box provider or disposable database evidence when this task's scope includes that dependency; do not substitute a mocked success.
- [ ] Check tenant isolation, disconnected/revoked credential handling, idempotency and requested negative cases.
- [ ] For Woo UI tasks, run `npm run test:i18n`, `npm run i18n:verify:20`, PHP/JS tests, admin-locale test, `npm run plugin-zip` and manual LocalWP workflow.
- [ ] Verify `git diff --check` and submit the canonical Completion Report; leave all `_index.md` files untouched until explicit reconciliation.

## Stop Condition

When requirements/acceptance and required validation are fulfilled, set the task to `review`, populate the Completion
Report and return to `moda_architect`. Do not begin dependent tasks or change other repositories on this task branch.

## Implementation Notes

Keep production responsibilities in small testable modules; prefer provider-neutral existing ownership to Shopify/Woo
service duplication. Return unexpected cross-repository schema or provider-contract gaps to the architect before
widening scope.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

Dependencies will be rechecked at task claim time; no generated task document itself creates a branch, provider credential, tested artifact or release.

### Unresolved Issues

None identified beyond documented dependencies/provider gating.

### Architectural Concerns

None reported at definition time.

## Architect Review

### Review Status

Pending implementation.

### Review Notes

No implementation reviewed.

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending.

### Follow-up

Return to architect on implementation submission.
