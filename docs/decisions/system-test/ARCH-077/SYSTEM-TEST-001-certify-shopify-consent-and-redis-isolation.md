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
depends_on: [ARCH-077-SHOPIFY-003, ARCH-077-SHOPIFY-004, ARCH-077-SHOPIFY-005, ARCH-077-BACKGROUND-001, ARCH-077-BACKGROUND-002]
enables: []
created: 2026-11-17
updated: 2026-11-17
---

# Certify Shopify checkout consent and Redis worker isolation

## Architecture / status

[ARCH-077](../../../architecture/ARCH-077-shopify-owned-whatsapp-checkout-consent.md). **Pending; no system-test execution is claimed by creating this definition.**

## Objective

Test actual Shopify and Background workflows, especially consent-vs-Redis worker isolation and final proactive dispatch, with no live customer messages or production Redis mutation.

## Execution environment

- Disposable Redis and PostgreSQL 17/pgvector for queue, consent and recovery tests; isolate BullMQ prefixes, jobs, keys and database names.
- Real Shopify development store/browser for supported Theme App Extension/Plus targets, recording actual supported plan and token provenance.
- Meta WhatsApp emulator/provider fixtures for outbound; no unsolicited live marketing sends.
- Existing ARCH-076 sender-pool and WooCommerce regression suites remain unmodified.

## Mandatory cases

- [ ] Cart token from `/cart.js` matches/normalises to verified checkout `cart_token` only under proven correlation; cart event before/after choice; checkout event before/after choice; null/missing/changed cart token; duplicate/late webhooks; multiple checkouts from cart; cart deletion/completion.
- [ ] Plus direct checkout GRANT/REVOKE, correct signed checkout token, no cart alias, missing context and accelerated checkout limitations.
- [ ] Verified same cart/checkout reload; **returning authenticated customer on a new cart** reads current preference and can withdraw; guests on new cart do not inherit it. No cross-shop/cross-customer leakage.
- [ ] Stale and reordered action replay; two browser tabs; regrant after withdrawal; concurrent customer withdrawal and existing checkout opt-in; STOP remains terminal.
- [ ] Matching, absent and conflicting billing/shipping phone; `customer.phone=null` positive case with verified recipient evidence; no grant from phone alone; no identity inference by email/product/time.
- [ ] Maturity/abandoned lookup, recovery delay, bounded Shopify retries, order paid/cancelled, no unsolicited recovery on consent checkbox action, correct ARCH-076 sender allocation and credit compensation.
- [ ] Initial, follow-up, retry, human reply and multipart checks; withdrawal acknowledged before provider dispatch blocks send; provider send already accepted before withdrawal documented; Redis error/timeout/missing key fail closed.
- [ ] Snapshot preexisting `pending-recovery:index:{shop,cart,checkout}*`, locks, order-completed tombstones and BullMQ queue metadata. Consent actions must not alter their values, TTL, job IDs, due times, retries, cleanup or index membership. Candidate cleanup must not delete valid consent evidence.
- [ ] Redis restart, persistence, eviction and memory-pressure exercise; no global `KEYS`/blocking scans; consent TTL independent of pending candidate TTL, no accidental cross-environment namespace collision.
- [ ] Shopify's 20 locale catalogues and immutable recorded disclosure; no Shopify Messaging native consent calls; WooCommerce/API behaviour unchanged.

## Evidence and acceptance

Report workspace tree, SHA/pins, exact commands, Docker/Redis/Postgres identifiers, cleanup evidence, actual browser execution vs simulation, observed concurrency ordering and pass/fail. **Acceptance:** all high-stakes race, identity, Redis isolation, STOP and worker regression cases actually pass; no undeclared schema or Woo/API changes.

**Stop:** any accepted withdrawal followed by a newly initiated proactive send, or any consent operation mutating existing worker-owned Redis key semantics, blocks production activation.
