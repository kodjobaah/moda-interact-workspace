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
status: in_progress
priority: 56
executor: developer
claimed_at: 2026-10-20T11:39:27Z
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

- [x] Implement checkout hook adapter and small bounded event publisher, reusing the existing PHP Moda API client. Present in the implementation worktree; changes are not yet committed or published.
- [x] Persist the checkoutKey in appropriate Woo checkout/session/order metadata without a new custom WordPress table. Session and order-object metadata handling are present; changes are not yet committed or published.
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

In Progress — Attempt 1 claimed by developer at 2026-10-20T11:39:27Z. Implementation review found checkout capture and checkout-key persistence code in the implementation worktree, but completion gates remain open. No passing/Accepted review is recorded.

### Files Changed

Implementation worktree changes observed (uncommitted): `composer.json`, `includes/Api/ModaApiClient.php`, `includes/Runtime.php`, `includes/Checkout/CheckoutActivityPublisher.php`, `includes/Checkout/CheckoutCapture.php`, `includes/Checkout/CheckoutKey.php`, `includes/Checkout/CheckoutSnapshot.php`, and `tests/CheckoutCaptureTest.php`. An unrelated untracked `typescript` text file is present and was left untouched.

### Work Completed

Checkout hooks, bounded checkout snapshot/event publishing through the existing API client, Action Scheduler retry handling, and session/order-object checkout-key persistence are implemented in the worktree. A focused test file covers simulated Classic/Blocks hook registration, event identity, retries, and selected failure cases. The required live WooCommerce Classic/Blocks/HPOS integration evidence and plugin regression test run are not available, so the test work item remains incomplete.

### Validation Results

`composer lint` passed, including PHP syntax checks for the new checkout files. `npm run build` passed; webpack reported the existing entrypoint-size/performance warnings. Focused PHPUnit could not run because `vendor/bin/phpunit` is absent. WordPress integration, plugin regression tests, package/ZIP smoke test, and full diff review remain outstanding.

### Deviations

None.

### Assumptions

The task claim is durable on the canonical parent task branch. The implementation changes observed are not yet durable: the implementation worktree has uncommitted changes, its task-named local branch is based on `origin/main`, and no matching implementation `origin/task/ARCH-035-WOOCOMMERCE-007` branch exists.

### Unresolved Issues

Focused PHPUnit and required WordPress integration/regression validation have not passed or been run. Implementation changes must be committed and pushed on the implementation task branch before completion. The untracked `typescript` artifact is unexplained and remains untouched. No accepted review exists.

### Architectural Concerns

Capture-only is not permanent event archiving. Completed BullMQ jobs can expire; future recovery enablement must consider that captured past events may be unavailable.

## Architect Review

### Review Status

Not Accepted — implementation publication, required validation, and a durable passing review are missing.

### Review Notes

Scope reopened from Superseded only for the 20 October 2026 WooCommerce checkout/order capture exception. Historical supersession remains in Git. No architectural acceptance of implementation is implied.

### Reviewed Files

Reviewed the checkout capture/publisher/key/snapshot implementation, API client/runtime wiring, focused test file, and published API activity schema in the routed implementation/source worktrees. Full diff review is still outstanding because the implementation changes are uncommitted.

### Validation Reviewed

PHP lint passed; production build passed with bundle-size warnings. Focused PHPUnit was unavailable (`vendor/bin/phpunit` missing). Required WordPress integration and plugin regression validation not run.

### Architecture Conformance

Not accepted. The observed design uses the existing API client and Action Scheduler and avoids checkout-path HTTP, but required integration evidence and durable implementation publication are outstanding.

### Follow-up

None.
