---
id: ARCH-045-BACKGROUND-005
architecture_id: ARCH-045
title: Record inbound WhatsApp opt-outs and enforce no-contact precedence
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 22
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-045-DATABASE-002
enables:
  - ARCH-045-BACKGROUND-002
  - ARCH-045-BACKGROUND-004
  - ARCH-046-BACKGROUND-002
  - ARCH-046-BACKGROUND-004
  - ARCH-045-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
  - ARCH-046-SYSTEM-TEST-001
created: '2026-10-21'
updated: 2026-10-22
---
# Record inbound WhatsApp opt-outs and enforce no-contact precedence

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** Portable architecture correction; not materialised, executed or architect-accepted.

## Objective

Record explicit WhatsApp customer STOP/unsubscribe requests **by canonical phone** before ordinary routing can ignore them: a STOP quoting a reliably resolved merchant outbound message blocks that phone at the identified merchant, while a **standalone STOP blocks that phone at every merchant where it is currently registered**. Record the STOP **only in Moda** and notify each affected merchant through the existing Support SYSTEM messages. No Shopify unsubscribe mutation, Shopify `write_customers` scope or new consent table/reachability changes.

## Context

`whatsapp.worker.ts` may route/ignore a message before a consent opt-out is interpreted. The normalised inbound message is not guaranteed to carry `shopId`; the same phone can occur at multiple merchants. Current `CustomerPhone` provides durable customer no-contact state, while the existing `WhatsAppRecipientReachability` concerns provider delivery failures, not consent.

## Scope

- After authenticated inbound admission, detect explicit deterministic STOP/UNSUBSCRIBE **before** moderation rejection, ignored/guidance/AI/human routing or any other normal message disposition can discard it. Preserve moderation logging where applicable, but it must not prevent a valid opt-out from taking effect. Do not substitute LLM classification for explicit commands.
- Read the authenticated inbound sender as a canonical WhatsApp number. If `contextMessageId` references a **reliably resolved original merchant outbound message**, identify that message's shop and block **all active CustomerPhone records for that canonical number within that shop**. If the inbound STOP has **no quoted outbound message**, do not infer a shop from the latest conversation: block **every active matching CustomerPhone across all currently registered merchants**, including both Shopify and WooCommerce. If a quoted reference exists but cannot be resolved reliably, use the same number-wide STOP rather than guessing one shop. Cross-merchant matching is permitted **only for this negative STOP operation**, never for positive consent.
- Use the existing authenticated inbound event identity for idempotency and persist STOP/no-contact on **each affected active CustomerPhone** in a short database transaction. Do not add event-ID columns to CustomerPhone. Duplicates must not redate/revise a previous STOP or leave partial merchant subsets. Once set, the `CUSTOMER_STOP` reason and no-contact state are never cleared by a Shopify read/webhook (even a newer `SUBSCRIBED`), Woo checkout consent grant or merchant re-enable. Only a future separately authorised, verified **customer-requested Moda STOP removal** could change this; no such automatic flow is added here.
- After local STOP is committed, publish one **idempotent `MerchantSupportMessage(kind=SYSTEM)` per affected merchant**, correlated to shop and an opaque canonical-phone STOP identity without exposing raw phone numbers in logs or source keys. Distinguish an explicit quoted shop-specific STOP from a standalone number-wide STOP. Prefer committing per-merchant Support notices with the STOP state in the same PostgreSQL transaction when the existing Support writer supports this; otherwise use its existing idempotent `sourceKey` and bounded inbound retry/reconciliation for partial notice failures. Report a concrete delivery guarantee gap instead of inventing another queue or table. A duplicate inbound webhook must not redate STOP or create another merchant notice. No calls to Shopify or WooCommerce provider APIs are made for STOP.
- If no active CustomerPhone exists for the canonical sender, report the unmatched STOP without falsely claiming durable future suppression. This v1 rule covers **registered numbers**, not unknown future merchants; do not invent a global suppression table. A nonexistent/invalid phone must not mutate unrelated records.
- Preserve existing ARCH-040 handover/moderation and distinct service-window classification, but the local STOP **blocks every subsequent outbound WhatsApp message** to the targeted shop/phone, including in-window human/AI replies, queued sends and retries; no outbound STOP acknowledgement is sent to the customer.

## Out of Scope

- No new customer/session/erasure table, recipient-reachability consent columns, consent-specific queue or global WhatsApp policy rewrite. No new Shopify merchant opt-out UI (SHOPIFY-005 is superseded), Woo merchant preference UI/API or customer STOP-removal interface.

## Requirements

- [ ] Quoted STOP applies to the identified merchant's phone records; **standalone or unresolvable-quote STOP** blocks every active matching phone across all registered merchants, before ordinary routing/ignored-message logic. Existing CustomerPhone no-contact state blocks **all** outbound sends to affected shops/phones, including service-window replies.
- [ ] Cross-merchant updates occur **only** for standalone/unresolved-quote STOP and are scoped by the canonical sender phone; no positive consent, Customer merge or unrelated number is changed. Missing matching phones are explicitly reported, not marked suppressed.
- [ ] Moderation and human handover retain their distinct rules, but no in-window reply or human message bypasses an active STOP.
- [ ] An active STOP is an independent local prohibition that cannot be overridden by Shopify consent reads/webhooks, new checkouts, Woo checkbox grants or a merchant preference toggle. No Shopify mutation or remote retry is executed.
- [ ] Each affected merchant receives one idempotent Moda Support SYSTEM notice; a partial Support-notice failure is retried without clearing STOP or notifying a different merchant.

## Work Items

- [ ] Implement a small deterministic opt-out detector at the existing authenticated inbound worker boundary, ahead of any moderation or routing disposition that could drop STOP; test even an otherwise rejected inbound message still opts out.
- [ ] Implement explicit quoted-message-to-shop resolution and number-wide fallback; update the correct merchant-scoped or cross-merchant set of current CustomerPhone records atomically/idempotently before ignored/guidance routing.
- [ ] Create idempotent per-merchant Support SYSTEM notices after the STOP update, with partial-delivery retry and no raw phone PII in logs/source keys. Add quoted, standalone, unresolved quote, multi-customer same-shop, multi-shop, duplicate, Shopify `SUBSCRIBED` after STOP, Woo grant/merchant re-enable and concurrent send-fence tests. No Shopify or Woo outbound consent mutation.

## Interfaces / Contracts

Consumes `ARCH-045-DATABASE-002` CustomerPhone local no-contact fields, existing Meta-normalised inbound provider message/conversation mapping and the reusable consent policy read by ARCH-045-BACKGROUND-001/004 and ARCH-046-BACKGROUND-001/004. No new cross-service event schema or recipient-reachability consent table. A standalone STOP deliberately has **all registered merchants** as its target; no guessed recent-conversation shop. Quoted STOP uses validated outbound-message correlation. BACKGROUND-001 only reads Shopify consent; no Shopify write, new Shared queue or global no-contact table.

## Dependencies

- `ARCH-045-DATABASE-002`

## Enables

- `ARCH-045-BACKGROUND-002`
- `ARCH-045-BACKGROUND-004`
- `ARCH-046-BACKGROUND-002`
- `ARCH-046-BACKGROUND-004`
- `ARCH-045-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`
- `ARCH-046-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] An authenticated STOP updates the **correct set of active canonical-phone records**, with one effective stop per targeted record despite duplicate delivery; each affected merchant receives a deduplicated Support notice and no later Shopify consent response removes the local blocks.
- [ ] A standalone STOP for a shared number blocks all currently registered shops without disabling any different number. An explicitly referenced merchant STOP leaves other shops untouched. An unresolvable quote follows the number-wide rule and an unmatched sender yields no invented durable suppression.
- [ ] STOP is not lost to ignored/guidance routing and suppresses **all** outbound WhatsApp messages to the affected phone/shop, including in-window customer-service replies.

## Validation

- [ ] Focused `whatsapp.worker` tests for quoted shop-specific STOP, standalone cross-merchant STOP, unresolvable quote fallback, duplicate provider IDs, multi-merchant and same-shop duplicate numbers, no registered phone, local STOP vs later Shopify consent/merchant re-enable; no PII in logs.
- [ ] ARCH-040 moderation/human-control regression tests, Background send policy denial after STOP and `git diff --check`.
- [ ] Realistic integration tests prove `SUBSCRIBED` before/after STOP and consent-sync webhook replay cannot clear STOP; merchant Support notices are exactly once per affected merchant; partial notice failures resume; no Shopify unsubscribe mutation or `write_customers` dependency exists.

## Stop Condition

After defined Work Items, Acceptance Criteria and required Validation, record dedicated parent/implementation task worktree and start-of-attempt synchronisation evidence, set `status: review`, submit Completion Report to `moda_architect`, and STOP. No dependent task may start before architect acceptance.

## Implementation Notes

Use the architect-approved consent model: no initial CheckoutRecovery without verified current permission, no arbitrary consent timeout, and consent changes do not trigger checkout reconciliation. Follow the current `/moda-task` launcher and exact published Shared/Database contracts. Preserve `docs/decisions/**/_index.md` until architecture session completion is confirmed. Use Shared structured logging on Node; bounded WordPress-safe diagnostics in PHP. Any missing cross-repository capability returns to architect rather than being implemented outside repository ownership.

## Completion Report

### Status
Not Started — definition only.

### Files Changed
None.

### Work Completed
None.

### Validation Results
Not run; no implementation branch.

### Deviations
None.

### Assumptions
Use latest developer implementation branch at claim; supplied snapshot is a reference.

### Unresolved Issues
None recorded.

### Architectural Concerns
None recorded.

## Architect Review

### Review Status
Pending — no implementation reviewed.

### Review Notes
None.

### Reviewed Files
None.

### Validation Reviewed
None.

### Architecture Conformance
Not assessed.

### Follow-up
None.

**2026-10-22 architect coordination:** Promoted `pending -> ready` because all declared dependencies in the supplied snapshot are `complete`. Task remains unclaimed (`executor: null`, `claimed_at: null`, `attempt: 0`). This eligibility change does not materialise a branch/worktree or start implementation.
