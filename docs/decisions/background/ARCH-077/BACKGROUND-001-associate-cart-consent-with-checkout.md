---
id: ARCH-077-BACKGROUND-001
architecture_id: ARCH-077
title: Read Shopify abandoned checkout attributes through existing recovery verification
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 55
executor: copilot
claimed_at: 2026-11-17T20:27:28Z
attempt: 1
depends_on: [ARCH-077-SHOPIFY-001, ARCH-077-SHARED-001, ARCH-077-SHOPIFY-002]
enables: [ARCH-077-BACKGROUND-002, ARCH-077-SYSTEM-TEST-001]
created: 2026-11-17
updated: 2026-11-17
---

# Integrate authoritative Shopify checkout attributes into recovery candidates

**Pending; after accepted S002 and completed historical Shared/S001 dependencies.** The [signed-attribute receipt v1 contract](../../../architecture/ARCH-077/checkout-attribute-consent-v1.md) supersedes the former B001 Redis marker-to-checkout association and Redis consent cleanup task. No new marker map, consent TTL extension, Redis choice reader or consent-specific BullMQ job is required.

## Existing Background touchpoints (inspect actual repo before editing)

- Existing checkout-created/updated V2/V3 consumer, checkout candidate identity, mature-at calculation, verification/retry and order-completion paths. Preserve current queue names, job IDs, dueAt, pending indexes, locks and `pending-recovery:order-completed:*` tombstones.
- Existing authoritative `AbandonedCheckout` GraphQL query/service: ensure **only this already needed query** selects `customAttributes {key value}` on the matching checkout. Do not call Shopify again solely for consent; do not put receipt into the existing queue message or save it in Redis.
- Preserve original authenticated webhook checkout token and (where available) the cart token along the existing candidate identity. If existing candidate transport cannot prove they belong to the same abandoned checkout, stop: do not guess from basket items, timestamp, email, customer name, or reuse the optional old SHARED-001 marker fields.
- Provide typed `authoritativeCheckoutAttributes` and trusted webhook checkout/cart token input to B002's verifier **within the existing maturity handoff**, no new queue/evidence store. Do not decide or materialise GRANT/REVOKE in B001; B002 owns signed receipt verification, SQL consent revision and final proactive admission.

## Lifecycle and failure outcomes

- No B001 consent cleanup on cart empty, order completion, abandoned checkout materialisation or Redis TTL. Shopify's checkout owns its attribute lifecycle; B001 retains only *existing* worker indexes and retries. A completed/paid/terminal checkout does not create SQL consent or outreach.
- A missing attribute is `NO_EXPLICIT_CHOICE`; duplicate named attributes, malformed provider shape, missing authenticated event token, unavailable provider data or mismatched checkout identity are typed denial/defer, not a default GRANT. The actual HMAC decision is verified by B002; do not treat an unverified string as consent.
- Existing unrelated Redis cache, BullMQ and checkout queues continue as before. No new DB schema, Redis namespace, timed cleanup job or Shopify API call. Existing privacy logs and provider error redaction stay intact.

## Tests/acceptance

- The prior live non-Plus probe was present in GraphQL `customAttributes`. New tests must prove **signed consent receipt** survives from S003 cart into the same authoritative query; Plus S004 is tested separately.
- Mocked and disposable Redis worker tests: created/updated before/after maturity, duplicate/out-of-order events, missing/duplicate attribute, delayed provider visibility, completion and cancellation, no change to existing BullMQ job identities, indexes/TTL, billing, STOP or sender routing. Validate no extra GraphQL query solely for consent.
- If candidate lacks authenticated checkout/cart token needed by the receipt binding rules, return the exact blocker to architect; do not add back a marker correlation service or alter Shared schema unilaterally.
