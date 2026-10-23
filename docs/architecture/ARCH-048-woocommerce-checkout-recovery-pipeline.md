---
id: ARCH-048
title: WooCommerce event-driven checkout recovery pipeline
status: proposed
coordinator: moda_architect
created: 2026-10-23
updated: 2026-10-23
---

# ARCH-048: WooCommerce event-driven checkout recovery pipeline

## Status

**Proposed for developer review — not implemented or materialised.** The source basis is the uploaded `moda-interact-workspace(20261023-170312).zip` (23 October 2026); the user's later confirmation that `ARCH-046-BACKGROUND-004` is complete supersedes that snapshot's older task status. Recheck canonical task branches before claiming work. Do not edit `docs/decisions/**/_index.md` until the developer confirms architecture reconciliation.

## Problem

ARCH-035's authenticated Woo plugin -> hosted API -> two BullMQ capture-worker paths exist, but the workers deliberately acknowledge events without scheduling checkout maturity, reconciling orders with recovery candidates, creating `CheckoutRecovery` rows or initiating outreach. The plugin's `CheckoutKey` is a stable shop-scoped correlation token kept in the Woo session and copied to HPOS-compatible order metadata (`_moda_checkout_key`), **not** a Woo session/cart retrieval token. `CheckoutSnapshot::fromCart()` returns `null` for an empty cart, so emptying a basket currently emits no checkout-clearing event. The hosted REST-read service supports product operations, not an authoritative guest checkout and order lookup.

## Goals

- Match Shopify's event-driven shape: Woo checkout/order hooks -> authenticated API admission -> separate capture queues -> Background correlation/scheduling -> maturity check -> first recovery/initial outreach.
- On each genuine checkout update, replace the prior candidate/timer; on an empty basket or terminal order outcome, cancel/suppress the matching checkout generation.
- Verify the current Woo session/cart **and associated order outcome**, under the authenticated installation, at maturity and again at final initial-send dispatch; distinguish `paid`, `cancelled`, `empty`, `not-found`, `unavailable` and `ambiguous` rather than turning lookup failures into permission to send.
- Use existing Customer, CustomerPhone, ShopSettings, CheckoutRecovery, RecoveryOutreachAttempt, MerchantSupportMessage, usage/reservation and conversation tables and existing billing/STOP/consent services.
- Fail closed on unknown identity, permission, terminal/invalid provider state or unavailable credentials; avoid duplicate rows, sends and charges under concurrent/duplicate/out-of-order events.

## Non-Goals

- No new Moda PostgreSQL tables/migrations, separate candidate event ledger or Woo-specific billing schema; no changes to Shopify recovery behaviour.
- No new merchant/staff accounts, consent wakeup poller, permission-by-phone-collection, global checkout history scan or generic arbitrary-URL provider proxy.
- No reopening of accepted ARCH-035 capture-only tasks or completed `ARCH-046-BACKGROUND-004`; no rewriting domain `_index.md` files in this review package.
- No automatic campaign to historical carts when a consent grant arrives; only subsequent normal checkout activity can start a new evaluation.

## Current Architecture (inspected source)

- `moda-interact-woocommerce/includes/Checkout/CheckoutCapture.php`, `CheckoutSnapshot.php`, `CheckoutKey.php`, `OrderLifecycleCapture.php`: Classic/Blocks capture, keyed order correlation and Action Scheduler publication; empty carts currently produce no snapshot.
- `moda-interact-api/src/woocommerce/activity/contract.ts`: `woo.activity.v1` `CHECKOUT_UPDATED`, `ORDER_PLACED`, `ORDER_PAID`, `ORDER_CANCELLED`; bounded `checkout.items: []` is supported. Hosted activity route resolves shop from authenticated installation and places Woo events on separate queues.
- `moda-interact-background/src/workers/woo-checkout-capture.worker.ts` and `woo-order-capture.worker.ts`: capture-only; neither creates or schedules a recovery.
- `moda-interact-background/src/domain/pending-recovery-candidate.ts` and `services/pending-recovery-candidate/*`: existing Shopify transient candidate/index/order-lock mechanics to reuse conceptually without treating a Woo key as a Shopify token.
- `moda-interact-api/src/woocommerce/rest-read/provider-connection.service.ts`: existing shop-scoped, credential-verified, DNS-pinned product-only Woo read; extend safely rather than adding a raw HTTP fetch helper.
- `moda-interact-database/prisma/schema.prisma`: existing `CheckoutRecovery` uniqueness `(shopId, checkoutToken, generation)` and existing customer/consent, outreach, billing and installation data.

## Proposed Architecture

```text
Woo Classic / Checkout Blocks checkout activity + order hooks
      |
      v
Woo publisher / Action Scheduler (stable eventId per occurrence)
      |
      v
Hosted authenticated POST /v1/woocommerce/activity
      |
      +-- checkout capture queue --> Woo checkout Background consumer
      |                             --> checkout-keyed delayed candidate
      |                                 (update/reschedule/empty = cancel)
      |
      `-- order capture queue -----> Woo order Background consumer
                                    --> shop+checkout-key order fence
                                    --> cancel/suppress if paid/cancelled

Matured Woo candidate
      --> current-state query via hosted API's trusted Woo read port
      --> provider-backed Woo plugin cart/order projection
      --> verified live unpaid/nonempty/nonterminal + maturity
      --> exact shop/customer/phone + current permission/STOP + entitlement
      --> unique first CheckoutRecovery + initial outreach attempt
      --> existing credit reservation/charge/compensation
      --> second current-state and consent/STOP/Marketing-template fence
      --> WhatsApp delivery
```

### State and temporal guarantees

1. Correlation: `(authenticated shopId, checkoutKey)`; match `order.checkoutKey` and Woo order metadata exactly. Never infer from phone/email or cross-shop identifiers.
2. A new checkout activity event advances a bounded last-activity watermark and replaces the delayed candidate; stale/out-of-order events cannot reverse a newer terminal decision. Deduplicate retries by stable `eventId`.
3. `ORDER_PLACED` **is not proof of payment**. A pending/on-hold order is handled under explicit provider-state eligibility, not automatically paid and not automatically abandoned. `ORDER_PAID` and `ORDER_CANCELLED` fence the exact checkout generation; a genuinely new checkout key may start a new evaluation.
4. Pre-creation candidates are transient BullMQ/Redis state, not `CheckoutRecovery`. A lost candidate can miss an outreach opportunity but must never cause an unjustified message. DB recovery/lifecycle is durable only after admission. Make job/index/tombstone TTL and replay behaviour explicit and bounded.
5. The Woo checkout key alone does not permit guest-session lookup. Woo plugin must prove a secure bounded checkoutKey-to-current-session binding or return `unavailable/expired/ambiguous`; order lookup must be HPOS-compatible. Provider-read failure is **not** treated as `not-found` or `unpaid`.
6. Repeat provider/consent checks immediately before the initial provider send; use a checkout-scoped lock/fence for running workers. A completed asynchronous check is not a durable permission to dispatch later.
7. No first `CheckoutRecovery`, outreach attempt or charge before positive exact-recipient marketing consent; `ARCH-046-BACKGROUND-002` will later add deduplicated missing-consent merchant Support notices at the approved admission seam. The completed `ARCH-046-BACKGROUND-004` final-send safeguard must be reused (user-confirmed complete after snapshot).

## Repository Responsibilities

| Repository | Owner | ARCH-048 tasks |
|---|---|---|
| `moda-interact-woocommerce` | `moda_woocommerce` | `WOOCOMMERCE-001` guest-session/order state projection; `WOOCOMMERCE-002` explicit empty-basket activity |
| `moda-interact-api` | `moda_api` | `API-001` trusted provider read; `API-002` authenticated Background state-query boundary |
| `moda-interact-background` | `moda_background` | `BACKGROUND-001` checkout timers; `BACKGROUND-002` order correlation; `BACKGROUND-003` maturity/first row; `BACKGROUND-004` billing/initial dispatch |
| `moda-interact-system-test` | `moda_system_test` | `SYSTEM-TEST-001` integrated lifecycle verification |

## Data Model

No new Moda schema. Use `Shop`, `WooCommerceInstallation` / read grant, `ShopSettings`, `Customer`, `CustomerPhone`, `CheckoutRecovery`, `CheckoutRecoveryStatusHistory`, `RecoveryOutreachAttempt`, `Conversation`, `MerchantSupportMessage`, usage/reservation and existing billing records. `(shopId, checkoutToken, generation)` is already unique. Transient candidate, job index, order fence and retry markers must have explicit bounded retention and must not masquerade as permanent history. Woo plugin-local session correlation may use its existing Woo/WordPress storage only when bounded, privacy-safe and demonstrably compatible with active guest sessions; it does **not** justify a new Moda table.

## Interfaces / Contracts

- Ingest: existing `woo.activity.v1` authenticated API route, validated event identities and original checkout/order queues; do not mislabel Woo events as Shopify.
- Provider state query: `ARCH-048-WOOCOMMERCE-001` defines a narrow versioned checkout-key/order-ID projection (no arbitrary URL or bulk session enumeration); `ARCH-048-API-001` validates/authenticates it. Explicit current observation time, matched checkout identity, optional verified associated order ID, basket total/line data and unambiguous terminal/payment status; errors remain structured and distinct.
- Background query: `ARCH-048-API-002` owns the authenticated state-query transport/response; reuse an existing canonical shared runtime contract if present. Before crossing a new API/Background contract boundary, verify the applicable `@modainteract/moda-interact-shared` exports. If no approved cross-service runtime contract mechanism exists, stop and request a bounded Shared owning task/publication gate rather than maintain divergent local schemas.
- Consent: existing `ARCH-046-BACKGROUND-001` exact-recipient policy; `ARCH-046-BACKGROUND-002` missing-consent Support seam; developer-confirmed complete `ARCH-046-BACKGROUND-004` outbound fence and `ARCH-045-BACKGROUND-005` authoritative STOP.
- Billing: existing provider-neutral recovery admission, usage, reservation, credit-source attribution and failure compensation. No new Woo-only charge types.

## Consistency, Ordering and Failure Handling

Use narrow checkout-scoped locks plus generation/job identity; tolerate at-least-once and out-of-order queue delivery, same-ID/different-body conflicts, order-first events, missing Woo events, interrupted scheduling, checkout expiration, authentication failure, retries, worker restarts and payment during send admission. Never perform external HTTP or Redis calls inside a Prisma transaction. Terminal fences must also stop active workers and existing recovery sends; deleting a delayed job alone is insufficient. Bounded retries for transient read failure preserve fail-closed behaviour and never duplicate charges.

## Scalability and Observability

The hot path is bounded event validation and checkout-keyed schedule/index updates, not a provider lookup for every hook; provider reads occur at maturity and final initial-send validation. Use existing BullMQ per-worker observability and the published Shared structured logger for service diagnostics. Include shop ID, safe checkout fingerprint, event/job/retry ID and classified outcomes; exclude raw customer phone, personal cart payloads, keys, tokens and credentials. Reuse standard tracing/metrics rather than invent generic duplicates. No infrastructure change is presently justified; if the internal API read requires new deployment routing or secrets, identify an explicit Gateway task before enabling the producer/consumer.

## Security

Only the installed trusted Woo provider edge may expose session/order state, with strict installation binding; only trusted Background callers may access the hosted state query. Server-side customer resolution remains shop-scoped. Verify state-reader auth against existing granted credentials or an explicitly approved plugin-specific mechanism; do not expose guest session IDs/cart tokens to merchants or arbitrary API callers. Validate pre- and post-provider-I/O installation/grant state, DNS pinning, redirects, response bounds and cancellation. Marketing templates, current consent and STOP are independent outbound blockers.

## Rollout and Validation

Assume **production-compatible rollout until actual environment state is verified** (no evidence yet establishes a safe breaking pre-production reset). Existing ARCH-035 event capture remains safe with old workers while new consumers/readers deploy. Deploy compatible plugin read/empty-cart support first, then API trusted read and Background query, then scheduling/reconciliation, then admission/consent notices and billing/dispatch behind a disabled Woo recovery feature gate. Verify `ARCH-046-BACKGROUND-004` completion in canonical Git (user reported a post-snapshot completion). Enable actual first sends only after `ARCH-046-BACKGROUND-002` and final-send/Marketing-template enforcement are accepted. Run the terminal ARCH-048 system test after all implementation dependencies and developer manual validation. No new Prisma migration, package publication or infrastructure work is proposed by default.

## Decisions / Tasks

| Task | Owner | Definition status | Dependencies (task IDs; see task files for full list) |
|---|---|---|---|
| `ARCH-048-WOOCOMMERCE-001` | Woo | ready | ARCH-035-WOOCOMMERCE-007/008 |
| `ARCH-048-WOOCOMMERCE-002` | Woo | ready | ARCH-035-WOOCOMMERCE-007, ARCH-035-API-008 |
| `ARCH-048-API-001` | API | pending | ARCH-048-WOOCOMMERCE-001 |
| `ARCH-048-API-002` | API | pending | ARCH-048-API-001 |
| `ARCH-048-BACKGROUND-001` | Background | ready | ARCH-035-BACKGROUND-001, ARCH-035-API-008 |
| `ARCH-048-BACKGROUND-002` | Background | ready | ARCH-035-BACKGROUND-002, ARCH-035-API-019 |
| `ARCH-048-BACKGROUND-003` | Background | pending | API-002, BACKGROUND-001/002, WOOCOMMERCE-002, ARCH-046-BACKGROUND-001 |
| `ARCH-048-BACKGROUND-004` | Background | pending | BACKGROUND-003, ARCH-046-BACKGROUND-002/004 |
| `ARCH-048-SYSTEM-TEST-001` | System Test | pending | all ARCH-048 implementations + consent/STOP integration |

Existing `ARCH-046-BACKGROUND-002` remains blocked pending the approved first-recovery insertion seam, and should later add `ARCH-048-BACKGROUND-003` to its dependency list. Its older billing-completion prerequisite wording must be narrowed at reconciliation: `ARCH-048-BACKGROUND-004` waits for this consent-notice task, so making that notice task wait for completed billing would create a cycle. Existing `ARCH-046-SYSTEM-TEST-002` should later be amended to depend on the integrated engine/send prerequisites. **Do not modify completed `ARCH-046-BACKGROUND-004`** or create a circular dependency with it. These cross-architecture amendments are a separate reconciliation action, not applied in this review-only patch.

## Open Questions / Review Gates

1. Verify that the plugin can safely bind guest checkoutKey to the current Woo session for the required lifetime; if not, the team must revise the provider-lookup approach, not silently assume correctness.
2. Confirm whether the existing API-to-Background service authentication, Shared contract and infrastructure need an explicit narrow addition before `API-002` can run.
3. Confirm the exact unpaid/pending-order recovery business policy; placed does not mean paid, and eligibility cannot be inferred from the event name alone.
4. Reconcile post-snapshot completion evidence for `ARCH-046-BACKGROUND-004` in canonical task/implementation branches before enabling dispatch.
5. Obtain developer approval of this architecture, materialise portable task definitions in the real workspace, and **only then** start eligible implementation tasks.

## Change History

- 2026-10-23: First review proposal based on the uploaded workspace and architectural discussion; nine bounded tasks, existing Moda tables, Shopify-parity event flow, live Woo state lookup, empty-cart event, existing consent/STOP/billing integration. No task was claimed or implemented.
