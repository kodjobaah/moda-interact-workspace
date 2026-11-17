---
id: ARCH-077-BACKGROUND-001
architecture_id: ARCH-077
title: Associate Shopify cart consent with checkout and manage temporary Redis lifecycle
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 55
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-077-SHOPIFY-001, ARCH-077-SHOPIFY-002]
enables: [ARCH-077-BACKGROUND-002, ARCH-077-SYSTEM-TEST-001]
created: 2026-11-17
updated: 2026-11-17
---

# Associate Shopify cart consent with checkout and manage temporary Redis lifecycle

## Architecture / status

[ARCH-077](../../../architecture/ARCH-077-shopify-owned-whatsapp-checkout-consent.md). **Pending. Implement only after the accepted S001 Redis identity contract and S002 temporary-consent contract are frozen.** Do not invent a separate consent source, checkout matching mechanism or cleanup scheduler.

## Objective and boundary

Associate the latest explicit, temporary consent selection made in the Shopify cart (S002/S003) with the corresponding checkout from an authenticated Shopify event. Retain that selection only while the cart/checkout may still enter recovery or until the eligible recovery's consent has been successfully materialised by B002 in PostgreSQL. Reuse existing Shopify Background lifecycle touchpoints for terminal cleanup.

- B001 handles **cart-to-checkout association and temporary Redis lifecycle only**. It does not decide whether a checkout is recoverable, grant or revoke durable customer consent, select a WhatsApp number, create recoveries, reserve credits or send messages.
- B002 evaluates recoverability, reads the latest effective selection, resolves the recipient and **applies any required GRANT/REVOKE to existing PostgreSQL customer records only during eligible recovery processing**. B001 must not write `Customer` or `CustomerPhone` consent fields.
- For an authenticated returning customer, S002 reads the existing consent from PostgreSQL for checkbox presentation. B001 must **never manufacture a new Redis grant** from that database state or maintain a permanent customer-preference key.
- For Shopify Plus, an authenticated checkout extension records its selection directly against the checkout in S002/S004. No cart-to-checkout transfer is required; B001 must preserve any later explicit checkout selection.

## Existing touchpoints (Background repository)

- `src/services/checkout-recovery/checkout-event-orchestrator.service.ts` — verified checkout-created/updated and cart-activity handling.
- `src/events/shopify-contract-adapter.ts` and `src/events/checkout-worker-dispatch.ts` — existing authenticated Shopify event consumers; preserve their published wire contracts.
- `src/services/pending-recovery-candidate.service.ts` and `src/services/pending-recovery-candidate/candidate-lifecycle.service.ts` — existing pending-candidate creation/cancellation/terminal outcomes.
- `src/services/pending-recovery-candidate/candidate-activity.service.ts` — cart/checkout updates and empty-cart cancellation.
- `src/services/pending-recovery-candidate/candidate-index.store.ts` and `src/domain/pending-recovery-candidate.ts` — existing job-ID indexes, TTLs and checkout/order lock keys.
- `src/services/pending-recovery-candidate/checkout-order-guard.service.ts` and `src/services/checkout-recovery/recovery-materialization.service.ts` — existing completed-order guard and recovery maturity outcome boundary. B002 owns consent materialisation; B001 may be invoked on its **confirmed** completion or terminal outcomes only.
- New B001-owned module: `src/services/shopify-checkout-consent/` (unless S001 freezes a different exact path), limited to separate consent-key read/association/cleanup operations.

## Association requirements

- [ ] Read authenticated `shopId`, `cartToken` and `checkoutToken` from the existing checkout-created event; require S001-verified cart-token equivalence. Scope every lookup and write to that shop. Do not infer identity from email, phone, items or creation time.
- [ ] Record the **association** between cart and checkout using the versioned, separate consent Redis namespace from S001. The checkout-created webhook itself never creates a GRANT or REVOKE; absent cart choice remains absent.
- [ ] Support choice-before-checkout-event and checkout-event-before-choice; also handle duplicate/replayed events, checkout-updated delivery, cart alias changes and missing/conflicting cart tokens. Do not assume the `carts/create` webhook preceded the S002 choice.
- [ ] Resolve the latest accepted, explicit choice at the time B002 reads the checkout. A checkout reference to cart consent is acceptable if S001 freezes that representation; do **not** introduce independently mutable, conflicting copies of permission.
- [ ] A newer explicit checkout selection from S004 must take precedence over an older cart selection under S001's accepted action-ordering contract. A delayed GRANT must not overwrite a later REVOKE. Reconciliation is idempotent and uses bounded, atomic Redis operations.
- [ ] One cart mapping to conflicting checkouts, a mismatched shop or an unverifiable link must not authorise either checkout by guessing. Report a typed denial/ambiguity for B002 to consume.
- [ ] Missing Redis records or transient Redis errors do not convert to consent. Preserve normal checkout and existing worker execution as far as possible; B002 fails closed on missing or unverified permission. Log the original safe Redis/provider error and reason code server-side.

## Temporary retention and lifecycle cleanup

- [ ] Keep temporary cart consent while its cart remains eligible to produce a checkout; an orphan cart with no checkout expires under the **bounded** S001-approved TTL. Do not retain a permanent customer preference or indefinite consent history in Redis.
- [ ] Keep checkout-associated selections while a pending candidate awaits maturity, during existing bounded Shopify abandoned-checkout verification retries, or while B002 has not yet completed a required PostgreSQL consent materialisation.
- [ ] After B002 confirms an eligible recovery's consent decision was successfully materialised in existing PostgreSQL records, remove temporary consent keys and association aliases **when no concurrent eligible consumer still requires them**. Do not remove consent on an attempted/failed materialisation.
- [ ] On completed orders, definitive cancellations, terminal non-recoverability or checkout expiry, remove temporary consent and association records after the applicable existing lifecycle outcome is confirmed. No PostgreSQL consent materialisation for normally completed or otherwise ineligible checkouts.
- [ ] An empty cart may retire that cart's temporary selection, but must **not** delete consent still required by an already-created eligible checkout. Handle cart/checkout ownership and alias cleanup with S001's frozen rules, including duplicate terminal events and late webhook replays.
- [ ] Clean up through existing Background lifecycle outcomes, not via a new BullMQ queue or cleanup scheduler. TTL is a bounded failsafe, not a replacement for terminal cleanup. The consent retention window must cover candidate maturity and bounded provider verification retries without silently inheriting the candidate-index TTL.
- [ ] Cleanup must be idempotent and compare the current owner/revision before deleting shared aliases, so delayed cleanup for an old checkout cannot erase a newer active cart or checkout selection.

## Worker/Redis isolation and deployment constraints

- [ ] Use **only** S001-approved Shopify consent keys for new writes. Do not store a consent Boolean, grant or revision in BullMQ job data or existing pending-candidate index values.
- [ ] Preserve exactly the meaning, ownership and TTLs of `pending-recovery:index:cart:*`, `pending-recovery:index:checkout:*`, `pending-recovery:index:shop:*`, `pending-recovery:lock:*` and `pending-recovery:order-completed:*`. Existing code may continue using them for its current purpose, but B001 consent logic must not mutate them.
- [ ] Do not change queue names, job IDs, delay or reschedule calculations, order-completion tombstones, lock ownership, cancellation policy, billing admission, checkout maturity or the ARCH-076 sender path.
- [ ] No global Redis `FLUSH*`, `KEYS` scan, eviction-policy/connection change, shared-namespace deletion or new persistent background process. Use bounded key lookups and atomic updates approved in S001.
- [ ] Version the new keys/contracts so the Shopify writer and Background reader can detect incompatible deployments and fail closed; do not reinterpret existing worker keys as consent data.
- [ ] No changes to database schema/migrations, `moda-interact-woocommerce`, `moda-interact-api` or Shopify-native WhatsApp consent. Do not edit `docs/decisions/**/_index.md`.

## Acceptance evidence

Run disposable Redis tests with the real candidate-index and BullMQ services. At minimum verify:

1. GRANT before checkout creation; checkout creation before GRANT; GRANT then REVOKE before/after association; S004 checkout-level REVOKE after cart GRANT.
2. Duplicate, late and out-of-order checkout/cart webhooks; missing cart token; cart-token change; conflicting cart-to-checkout mapping; cross-shop isolation.
3. Returning authenticated customer with a DB grant but no current cart action: B001 does not write a synthetic GRANT; B002 can evaluate the existing permission via its approved boundary.
4. Pending maturity and bounded provider-visibility retry retain temporary consent; successful B002 materialisation removes it only after confirmation; a failed DB write retains it for eligible retry.
5. Checkout completion, cancellation, terminal non-recoverability, empty cart, orphan cart TTL and checkout expiry remove only eligible temporary keys. A completed checkout never updates PostgreSQL consent.
6. Candidate index cleanup does not accidentally remove active consent; late consent cleanup does not delete a newly owned alias; repeated cleanup is safe.
7. Before/after snapshots prove identical job IDs, BullMQ payload/metadata, delays, index values/TTLs, checkout locks and completed-order tombstones under consent operations. WooCommerce worker outcomes remain identical.
8. Redis failures and restarted connections result in no inferred grant, no customer-facing checkout error and preserved existing worker scheduling/cancellation semantics.
9. Record exact worktree/commit, frozen S001 contract version, disposable Redis identifier, executed test commands/results and cleanup evidence; distinguish mocked from integrated worker tests.

## Stop conditions

Stop and refer back to the architect if the S001 cart-to-checkout association cannot be verified, the S002 consent contract is still ambiguous, B001 would need to alter existing worker key meaning/job data/TTL, consent would be removed before a necessary B002 materialisation, or a terminal cleanup could erase a newer consent selection. **Do not solve these gaps with inferred identity, extra queues, permanent Redis customer preferences or PostgreSQL schema changes.**
