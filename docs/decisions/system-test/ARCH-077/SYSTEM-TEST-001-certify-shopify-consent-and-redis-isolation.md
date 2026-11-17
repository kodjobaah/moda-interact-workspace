---
id: ARCH-077-SYSTEM-TEST-001
architecture_id: ARCH-077
title: Certify Shopify checkout consent and Redis worker isolation
task_kind: verification
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 70
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-077-SHOPIFY-003, ARCH-077-SHOPIFY-004, ARCH-077-SHOPIFY-005, ARCH-077-BACKGROUND-001, ARCH-077-BACKGROUND-002, ARCH-077-SHOPIFY-006]
enables: []
created: 2026-11-17
updated: 2026-11-17
---

# Certify Shopify checkout consent and Redis worker isolation

## Architecture / status

[ARCH-077](../../../architecture/ARCH-077-shopify-owned-whatsapp-checkout-consent.md). **Pending; this definition is not evidence that any test has run.** Execute against the finally reconciled ARCH-077 contracts **after** obsolete Shopify-native marketing-consent ingress and processing have been removed by S006. Do not reinstate legacy job compatibility for preproduction.

## Objective and invariant

Certify the Shopify application and Background worker implementation using the approved **deferred consent materialisation** lifecycle. The application records explicit checkbox changes temporarily in **checkout/cart-scoped Redis**; it reads a returning authenticated customer's existing consent from **PostgreSQL**. Background applies a pending grant or withdrawal to existing `Customer`/`CustomerPhone` records **only when that checkout becomes recoverable**. Completed or otherwise ineligible checkouts produce no consent database update. Once materialised, PostgreSQL is authoritative for initial outreach, follow-ups and final proactive send admission; Redis is not a permanent customer preference store or a mandatory per-message read.

For this Shopify-only flow, the existing PostgreSQL `SHOPIFY_NATIVE` source value denotes **Moda's Shopify checkout-checkbox evidence**, not Shopify Messaging or Shopify's marketing-consent GraphQL API. There is no new enum, table or migration. Keep the WooCommerce application and `moda-interact-api` unchanged.

## Execution environment and ownership

- Use disposable, isolated Redis and PostgreSQL 17/pgvector for queue, consent, recovery and outbound tests. Never mutate production Redis, customer records or send live unsolicited WhatsApp messages.
- Run the installed Shopify application and Background integration paths with their actual compatible package pins and Redis key contracts. Use a Meta provider emulator/fixtures for sends. Include real Shopify development-store/browser evidence for the supported cart App Block and (separately) a Shopify Plus checkout environment. Mark Plus **uncertified** if no eligible Plus test store is available; do not substitute a mocked extension result for real storefront certification.
- Capture repository/worktree paths, exact SHAs, submodule pins, deployed/test Shopify app configuration and selected storefront/checkout extension targets, disposable infrastructure identifiers and cleanup outcomes.
- Preserve existing ARCH-076 sender-pool tests, BullMQ worker tests, WooCommerce/API regressions and the checkout/consent version contracts. Do not create new queues, schema migrations or legacy compatibility code as part of testing.

## Mandatory acceptance scenarios

### A. Shopify identity, UI and read precedence

- [ ] Cart-page `/cart.js` cart identity correlates with a verified Shopify checkout webhook `cart_token` under S001; capture an actual token example in redacted form. Check cart-created webhook before/after explicit selection, checkout-created before/after selection, duplicate or delayed webhooks, changed/null token, cart reused for conflicting checkouts and a cart that never reaches checkout. Never infer association by phone, email, products or timestamps.
- [ ] Shopify Plus checkout extension uses its verified checkout identity/session token, writes directly to checkout-scoped Redis without a cart alias, and handles guest identity, missing token, reload and accelerated-checkout unsupported paths.
- [ ] New customer: no verified existing consent and no pending choice => checkbox unchecked. Authenticated returning customer on a **new cart**: S002 reads the matching merchant/customer's existing `CustomerPhone` decision from PostgreSQL; `GRANTED` displays checked, `REVOKED`/`UNKNOWN` displays unchecked. No checkbox-render/status-read side effect creates a new grant or a Redis choice.
- [ ] Same cart or checkout with an accepted, pending Redis choice displays that choice ahead of an older database value. Distinct anonymous carts never inherit a previous guest's consent; never expose cross-merchant or cross-customer state.
- [ ] Both S003 and S004 enabled on a Plus store: latest accepted explicit cart/checkout action determines checkout display; a read or prechecked display does not generate a new action.

### B. Consent writes and deferred database materialisation

- [ ] Deliberate checkbox GRANT or REVOKE only writes the **temporary** cart/checkout Redis selection. Verify `Customer`, `CustomerPhone` and consent revision fields in PostgreSQL remain unchanged immediately after each action, whether the user is new or returning.
- [ ] Grant, withdraw, regrant and duplicate/reordered actions from multiple tabs use the S001/S002 accepted action and revision contract; the latest accepted **explicit decision** wins. An old grant must not overwrite a newer withdrawal; a subsequent new explicit grant can restore permission. STOP suppression remains authoritative independently of checkbox state.
- [ ] An abandoned checkout passes existing Shopify recoverability, merchant delay, bounded verification and ownership checks. Background reads the latest applicable pending selection; GRANT materialises `GRANTED`, REVOKE materialises `REVOKED`, and the resulting PostgreSQL state governs recovery admission. Verify the latest accepted action **within one checkout** is selected; **across checkouts**, only distinct successfully materialised eligible selections update SQL and a replay of an older successful materialisation must not undo a later one.
- [ ] No new Redis selection + previously verified PostgreSQL `GRANTED` => eligible recovery can reuse existing consent without fabricating a new checkbox action. No selection + PostgreSQL `UNKNOWN`/`REVOKED` => no permission or proactive outreach. A missing Redis record is not an explicit withdrawal.
- [ ] Checkout paid/completed or definitively ineligible before becoming recoverable => **no PostgreSQL consent materialisation**, including if the customer explicitly unchecked a pre-existing grant; temporary Redis cleanup follows the agreed lifecycle. A subsequent new cart reads whatever PostgreSQL decision remains. Do not impose an additional immediate-SQL withdrawal workflow contrary to S002.
- [ ] Consent action itself must never enqueue recovery, reserve billing credits or send WhatsApp messages. Recovery creation and first outreach happen only after verified eligibility and final permissions.

### B2. Mandatory A-then-B deferred decisions, outreach and conversation continuation

- [ ] **A checkbox GRANT** while A is active: assert only temporary Redis writes, no `CustomerPhone` changes, no outreach. **A independently recoverable:** one SQL GRANTED materialisation followed by one permitted initial outbound. The SQL final-send path remains authoritative.
- [ ] **B checkbox REVOKE** while A previously GRANTED/sent: assert only B-scoped Redis REVOKE, no SQL change, no new immediate suppression, and A's not-yet-sent proactive follow-up remains governed by current GRANTED/STOP until B recoverability. **B completes payment:** assert B choice discarded and SQL still GRANTED; no B outreach/consent write. No test may substitute immediate SQL opt-out or Redis send suppression for the chosen rule.
- [ ] **B independently recoverable** with verified customer/recipient: assert SQL REVOKED commits **before** message-admission denial, with zero initial outreach for B even if no `CheckoutRecovery` is created, and A's not-yet-provider-accepted follow-up or proactive retry is blocked by the existing SQL fence. A's delivered initial message and conversation history are preserved; no retroactive recall/credit invention.
- [ ] **Customer replies to Cart A** after B REVOKE: existing AI and human replies can proceed if admitted by normal WhatsApp 24-hour service window, moderation, STOP and routing. An unsolicited scheduled follow-up cannot piggyback on the 24-hour window. Revoke never closes A's conversation or turns a customer-originated response into a new initial outreach.
- [ ] **C future recoverable, no explicit selection** uses current REVOKED and sends nothing; **C explicit GRANT materialises at independent recoverability** and permits outreach only if all other guards pass. Active STOP blocks everything it already blocks, regardless of any checkbox GRANT or REVOKE.
- [ ] Duplicate webhook/recovery materialisation for A after B, forced crash after A SQL commit before Redis acknowledgement, two concurrent materialisation transactions for same `CustomerPhone`, and retry of B REVOKE must show **no replay regrant or double revision**. On inability to guarantee one-time durable ordering using existing schema, fail certification with `MATERIALISATION_IDEMPOTENCY_BLOCKER`; do not guess or add an unapproved migration.
- [ ] Provider-accepted message before B REVOKE is not recalled. Proactive message requiring a final SQL gate **after** B REVOKE must not be initiated. Verify no credit double-commit/refund and existing ARCH-076 sender routing unchanged.


### C. Recipient resolution and database enforcement

- [ ] Retrieve current contact details from the authoritative Shopify abandoned checkout. Test customer phone -> billing phone -> shipping phone precedence, null/invalid higher-priority values, differing valid values, all absent, customer identity mismatch, and the production regression `customer.phone=null` with matching billing/shipping numbers. A phone in an address alone does not create consent; a shipping recipient demonstrably unrelated to the consenting customer must not be authorised.
- [ ] Persist only shop-scoped, validated customer/phone relationships; preserve an active STOP record through a formatting-only phone change. Assert database `SHOPIFY_NATIVE` source is used **for Moda Shopify checkbox consent** without any Shopify `defaultPhoneNumber.whatsAppMarketingConsent` reads. Keep existing PostgreSQL decision/revision/no-contact guards and explicit customer identity links.
- [ ] After materialisation, verify initial send, re-entry, follow-up, retry, multipart and proactive SQL final-dispatch checks use current **PostgreSQL** consent and STOP; no new Redis network call is required on every outbound send. Materialised REVOKE, invalid/moved recipient, changed revision or STOP suppresses subsequent proactive sends. Human/customer-initiated conversation paths retain their separate existing eligibility rules.
- [ ] Existing outbound billing reservation/compensation, checkout cancellation, no-response follow-up cap and ARCH-076 sender assignment are unchanged; a blocked outreach must not leak credits or duplicate sender allocation.

### D. Redis lifecycle and worker isolation

- [ ] Temporary consent keys use only the approved, separate versioned namespace. Snapshot values and TTLs for existing `pending-recovery:index:cart:*`, `pending-recovery:index:checkout:*`, `pending-recovery:index:shop:*`, checkout/order locks, order-completion tombstones and BullMQ-managed queue metadata before/after consent actions and cleanup. Assert job IDs, due times, retry/verification state, indexes, memberships and existing TTL semantics remain unchanged.
- [ ] Cart-to-checkout association is idempotent and never writes consent into pending-candidate BullMQ payloads or replaces a job ID in a worker-owned index. Test webhook/checkbox ordering and conflicting associations without global Redis `KEYS` scans or unbounded operations.
- [ ] Temporary selection survives existing checkout maturity and bounded Shopify visibility retries until it can be applied. On database write failure, do not acknowledge materialisation or delete the pending consent prematurely; use the existing bounded retry mechanism if still eligible.
- [ ] After successful recoverable materialisation, clean up no-longer-needed temporary consent. On paid/completed, cancelled or definitively ineligible checkout, remove temporary records without updating PostgreSQL. An abandoned cart with no checkout receives bounded expiry. Candidate-index removal alone must never delete consent before materialisation succeeds.
- [ ] Redis read/write timeout, restart, missing key, malformed record, TTL expiry and eviction do not manufacture a new grant or corrupt other worker state. When Redis is unavailable at recovery maturity, do not reinterpret an unread pending choice as absent; fail closed/defer under the approved lifecycle. Verify Redis memory isolation and no global configuration change affecting worker queues.

### E. Silent failure and retirement

- [ ] S003/S004 initial consent read failure hides only Moda's checkbox; failed GRANT/REVOKE does not appear saved. Test network timeout, invalid response, unreachable Moda backend, Redis unavailable and PostgreSQL status-read failure. No customer-facing error, retry banner, blocked cart, delayed payment or merchant-site technical exception. Preserve original provider/Redis diagnostic message server-side **with sensitive-data redaction**.
- [ ] Exact English checkbox text is `Send me WhatsApp shopping updates, reminders and offers.`; all 20 Shopify locales preserve its meaning. Verify disclosure text/version/locale accompany each accepted temporary action; no WooCommerce catalogue changes.
- [ ] After S006, no Shopify native marketing-consent webhook subscription, publisher, synchroniser, provider read or handler remains. No test requires draining/compatibly processing obsolete preproduction jobs. Confirm the **shared checkout-events queue** still processes all cart, checkout and order work normally, and that Shopify privacy webhooks remain functional.
- [ ] Merchant activation guidance/verified status works for cart-page App Blocks and Plus checkout extensions; unsupported themes and unavailable extension state are not falsely reported as enabled.

### F. Required guest versus authenticated cart-binding proof (newly frozen)

- [ ] Signed App Proxy shop authentication alone is not asserted as guest identity. A guest checkbox action creates only a temporary choice. For a verified marker + matching authenticated checkout `cart_token` digest + attributable customer/recipient, recovery-time materialisation follows the explicit choice; no earlier SQL/proactive effect occurs.
- [ ] For a guest with a valid but copied marker where the authenticated checkout `cart_token` differs (or is missing), B002 returns `DEFER_IDENTITY_OR_RECIPIENT`, writes no consent and sends nothing. Do not treat the marker as a bearer authorisation or fall back to basket/email/time matching.
- [ ] For a logged-in customer, capture the Shopify customer ID **only** from verified signed App Proxy context at the accepted action. The checkout may have a different/missing cart token only if the authoritative checkout customer ID exactly matches the saved verified action customer ID. Mismatch, absent ID, cross-shop and client-injected ID fail closed.
- [ ] Demonstrate the no-SQL-at-click rule and A-GRANT/B-REVOKE deferred lifecycle in both permitted binding paths; also assert out-of-order CREATE/UPDATE, Redis outage and post-commit retry invariants. Test server-issued 256-bit markers separately; the 17 November browser marker was a feasibility experiment, not a production implementation test.

## Reporting and release acceptance

Provide a scenario-by-scenario matrix with **actual command, observed result, test type (unit/integration/real Shopify), evidence reference, and pass/fail**. Report repository trees/SHAs, Shared/Prisma pins, Redis namespace/configuration and memory observations, disposable PostgreSQL/Redis identities, exact setup/teardown commands, and proof all test containers and keys were removed. Do not claim measured worker performance or a Plus browser pass from static inspection or mocks.

**Acceptance:** Consent is captured temporarily, materialised only for a recoverable checkout, then enforced in existing PostgreSQL outbound guards; checkout completion causes neither consent DB update nor recovery. Redis consent lifecycle does not interfere with existing Background worker indexes/jobs, STOP always wins, and Shopify/WooCommerce/ARCH-076 regressions pass. Final certification is performed on the **post-S006** implementation.

**Stop conditions:** Any unverified customer/checkout association authorising a message, incorrect consent decision ordering at materialisation, failed STOP or PostgreSQL final-send protection, temporary Redis consent removed before a required retry, consent operation mutating worker-owned Redis structures, unsolicited live send, or missing real-browser certification for a claimed supported extension blocks the relevant production activation. Record the precise evidence and return to the architect instead of changing these rules in the test task.
