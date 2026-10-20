---
id: ARCH-035-WOOCOMMERCE-007
architecture_id: ARCH-035
title: Capture Woo checkout snapshots
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 56
executor: null
claimed_at: null
attempt: 1
depends_on: [ARCH-035-API-008]
enables: [ARCH-035-WOOCOMMERCE-008, ARCH-035-BACKGROUND-001]
created: 2026-10-11
updated: 2026-10-20
---

# ARCH-035-WOOCOMMERCE-007: Capture Woo checkout snapshots

## Developer Takeover

On 2026-10-20, the developer explicitly took ownership of Attempt 1 for implementation. The logical repository owner remains `moda_woocommerce`; this amendment changes only execution and completion authority to developer mode. The task scope, dependencies, acceptance criteria and architectural ownership are unchanged.

## Architecture

- Architecture: `ARCH-035`; document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`.
- Coordinator: `moda_architect`; baseline: `moda-interact-workspace(20261018-121025).zip`, revised 2026-10-20.
- Former task was superseded under the UI-only revision; this definition reopens only the explicitly approved **capture-only** scope. Task is defined but not materialised in the developer workspace.

## Objective

Capture WooCommerce checkout updates and submit bounded events through the installed plugin server-to-server to the accepted API route.

## Context

The plugin owns merchant-controlled Woo hooks and connected installation credentials. Capture must be non-blocking for shoppers and cover Classic and Checkout Blocks with minimal implementation.

## Scope

- Observe Woo checkout events through supported Classic and Checkout Blocks extension points and capture guest/customer checkouts.
- Keep one stable checkoutKey through repeated updates, and attach it to subsequently created orders using HPOS-compatible Woo metadata.
- Form bounded checkout snapshots with eventId, occurredAt, amounts, currency, items, optional contact and recovery URL only when actually available.
- Use an existing Woo background delivery facility; if no suitable durable retry exists, use the WooCommerce-bundled Action Scheduler rather than new queues/tables.
- Deliver through the existing connected-installation PHP API client and published API-008 contract.

## Out of Scope

- Customer WhatsApp opt-in/consent forms, permission evidence or allowlist management.
- Recovery materialisation, scheduling, outreach, WhatsApp, AI, charging or offer selection.
- New Woo activity receipts/lineage tables, new Shared contracts or Shopify-event impersonation.
- Changes to another repository or any `docs/decisions/**/_index.md` file.
- WordPress browser-exposed installation credential or synchronous mandatory HTTP delivery from the checkout request.

## Requirements

- Same eventId/payload must be preserved for retries; a new genuine checkout change gets a new eventId.
- Protect the customer checkout path: a failed Moda request may log/schedule retry but must not fail checkout.
- No invented consent or phone number. No client-provided Shop ID.
- Bound retries and payload size using existing Woo facilities; identify exhausted retries without exposing personal data.
- Classic, Blocks and HPOS pathways must use supported WooCommerce APIs/hooks; do not assume they share the same hook.

## Work Items

- [x] Implement checkout hook adapter and small bounded event publisher, reusing the existing PHP Moda API client. Published on implementation task branch at `5c4df4c`.
- [x] Persist the checkoutKey in appropriate Woo checkout/session/order metadata without a new custom WordPress table. Session and order-object metadata handling are published on the implementation task branch at `5c4df4c`.
- [ ] Add Classic and Blocks integration tests, retry/deduplication cases and plugin regression tests.

## Interfaces / Contracts

**API-owned `woo.activity.v1` contract** (published as strict OpenAPI + integration fixtures, not a new Shared package in this bounded scope):

```json
{
  "schemaVersion": "woo.activity.v1",
  "eventId": "stable-opaque-event-id",
  "eventType": "CHECKOUT_UPDATED",
  "checkoutKey": "stable-shop-scoped-key",
  "occurredAt": "2026-10-20T12:00:00.000Z",
  "checkout": { "currency": "GBP", "total": "29.99", "items": [] }
}
```

`eventType` is one of `CHECKOUT_UPDATED`, `ORDER_PLACED`, `ORDER_PAID`, `ORDER_CANCELLED`. For orders, use an `order` object with `orderId`, status and same `checkoutKey`; `checkout` is absent. A Woo producer sends no shop ID: API resolves Shop from installation credentials. Bounded customer/contact fields and line-item fields must be explicitly defined in the authoritative API schema; omit unavailable fields rather than fabricating them. Correlation key is `(authenticated shopId, checkoutKey)`. Stable `eventId` is retained on retries of the **same emitted event**; later genuine updates use a new `eventId`.

The hosted API owns `POST /v1/woocommerce/activity`. Checkouts are implemented by API-008; order event types are enabled by API-019 on the same route. Queue payloads retain `schemaVersion`, authenticated `shopId`, event identity, kind, checkout key and bounded validated snapshot. Background must validate the queued payload again and must **not** call the Shopify event parser. These contracts are specific to this API/Background integration; if a published cross-service primitive becomes necessary, stop and return the new ownership requirement to the architect rather than implement a competing Shared module.

## Dependencies

- `ARCH-035-API-008` — must be Complete and accepted before claiming.

## Enables

- `ARCH-035-WOOCOMMERCE-008`
- `ARCH-035-BACKGROUND-001`

## Acceptance Criteria

- [ ] Classic and Blocks flows each emit correct checkout events for guests and logged-in users.
- [ ] Updates share checkoutKey but have distinct eventIds; retries preserve both identity and content.
- [ ] Shopper checkout proceeds during an API outage.
- [ ] No consent UI, recovery scheduler or WhatsApp workflow is introduced.

## Validation

- [ ] PHPUnit and plugin JS tests where relevant, PHP lint and production build.
- [ ] WordPress integration: Classic + Blocks + HPOS correlation metadata, API failure/retry, checkout non-blocking proof.
- [ ] ZIP/plugin smoke test and diff check.

## Stop Condition

After work items, acceptance criteria and required validation are satisfied, finish the Completion Report, transition the task to `review`, return it to `moda_architect`, and STOP. Do not proceed to enabled tasks.

## Implementation Notes

Avoid normalising a Woo contact to a Shopify customer ID. Inspect current WooCommerce plugin hooks before selecting implementation points; if Blocks do not expose the assumed lifecycle, use supported Woo Blocks hooks, not undocumented hacks.

## Completion Report

### Status

Changes Requested — Attempt 1 was reviewed on 2026-10-20. The implementation branch is committed and pushed, but required runtime evidence is incomplete. Attempt remains 1; the task is ready for the next claim.

### Files Changed

Implementation task branch commit `5c4df4c` contains `composer.json`, `includes/Api/ModaApiClient.php`, `includes/Runtime.php`, `includes/Checkout/CheckoutActivityPublisher.php`, `includes/Checkout/CheckoutCapture.php`, `includes/Checkout/CheckoutKey.php`, `includes/Checkout/CheckoutSnapshot.php`, and `tests/CheckoutCaptureTest.php`. The implementation worktree is clean and the commit is published. An unrelated untracked `typescript` text file was observed before publication and left untouched; it is not part of the task commit.

### Work Completed

Checkout hooks, bounded checkout snapshot/event publishing through the existing API client, Action Scheduler retry handling, and session/order-object checkout-key persistence are implemented and published. A focused test file covers simulated Classic/Blocks hook registration, event identity, retries, and selected failure cases. PHPUnit regression validation passes; live WooCommerce Classic/Blocks/HPOS integration evidence is not available, so the integration-test work item remains incomplete.

### Validation Results

`composer lint` passed, including PHP syntax checks for the new checkout files. `npm run build` passed with webpack entrypoint-size/performance warnings. Focused checkout PHPUnit passed (5 tests, 44 assertions); full `composer test` passed (125 tests, 878 assertions). Focused tests use WordPress/Woo stubs, not a live runtime. Plugin JS tests, WordPress Classic/Blocks/HPOS integration, checkout-outage proof, and ZIP/plugin smoke test remain outstanding.

### Deviations

None.

### Assumptions

The implementation commit `5c4df4c` is durable on `origin/task/ARCH-035-WOOCOMMERCE-007`, and the implementation worktree is clean. Parent task record changes are committed and pushed separately on the matching parent task branch.

### Unresolved Issues

WordPress Classic/Blocks/HPOS integration, checkout-outage proof, plugin JS tests, and ZIP/plugin smoke test have not been run. No prior durable passing/Accepted review exists. The untracked `typescript` artifact was not included in the implementation task commit.

### Architectural Concerns

Capture-only is not permanent event archiving. Completed BullMQ jobs can expire; future recovery enablement must consider that captured past events may be unavailable.

## Architect Review

### Review Status

Changes Requested — this explicit completion request cannot pass because live integration/checkout-outage evidence and the remaining plugin validations are outstanding; no prior accepted review exists. The task was returned to `ready` with executor/claimed_at cleared and attempt unchanged at 1.

### Review Notes

Scope reopened from Superseded only for the 20 October 2026 WooCommerce checkout/order capture exception. Historical supersession remains in Git. No architectural acceptance of implementation is implied.

### Reviewed Files

Reviewed the published checkout capture/publisher/key/snapshot implementation, API client/runtime wiring, focused test file, and published API activity schema. Implementation task commit: `5c4df4c`.

### Validation Reviewed

PHP lint passed; production build passed with bundle-size warnings; focused PHPUnit passed (5 tests, 44 assertions); full PHP suite passed (125 tests, 878 assertions). Plugin JS, live WordPress integration, and package smoke validation remain outstanding.

### Architecture Conformance

Not accepted. The implementation uses the existing API client and Action Scheduler and avoids checkout-path HTTP. PHPUnit and production build pass, and implementation publication is verified; required live integration, outage proof, JS, and package validation remain outstanding.

### Developer Self-Review - Changes Requested

1. Add and run a WordPress/WooCommerce integration check proving Classic and Checkout Blocks guest and logged-in checkout updates emit valid `woo.activity.v1` events, preserve checkoutKey through HPOS order metadata, and continue checkout during API failure while retrying the identical event.
2. Run the plugin JS test suite and the ZIP/plugin smoke test; record exact commands and results.
3. Update the Work Items, Acceptance Criteria, and Validation checkboxes only after the corresponding evidence passes. Then submit the task for review again. Do not increment attempt in this review; the next claim performs the single increment.

The explicit completion request was not accepted. Task state is `ready`; executor and claimed_at are null; attempt remains 1. No downstream dependency-frontier reconciliation was performed because the task did not complete.

### Follow-up

None.
