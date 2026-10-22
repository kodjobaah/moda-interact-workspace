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
status: pending
priority: 22
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-045-DATABASE-002
  - ARCH-045-BACKGROUND-001
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

Record explicit WhatsApp customer STOP/unsubscribe requests **by canonical phone** before ordinary routing can ignore them: a STOP quoting a reliably resolved merchant outbound message blocks that phone at the identified merchant, while a **standalone STOP blocks that phone at every merchant where it is currently registered**. Where affected shops use Shopify, attempt to synchronise the unsubscribe back to Shopify without adding a new consent table or changing delivery reachability.

## Context

`whatsapp.worker.ts` may route/ignore a message before a consent opt-out is interpreted. The normalised inbound message is not guaranteed to carry `shopId`; the same phone can occur at multiple merchants. Current `CustomerPhone` provides durable customer no-contact state, while the existing `WhatsAppRecipientReachability` concerns provider delivery failures, not consent.

## Scope

- Detect deterministic STOP/UNSUBSCRIBE intent using the authenticated inbound message and existing moderation/abuse admission, **before** ignored/guidance/AI/human conversation routing discards the request. Do not substitute LLM classification for explicit commands.
- Read the authenticated inbound sender as a canonical WhatsApp number. If `contextMessageId` references a **reliably resolved original merchant outbound message**, identify that message's shop and block **all active CustomerPhone records for that canonical number within that shop**. If the inbound STOP has **no quoted outbound message**, do not infer a shop from the latest conversation: block **every active matching CustomerPhone across all currently registered merchants**, including both Shopify and WooCommerce. If a quoted reference exists but cannot be resolved reliably, use the same number-wide STOP rather than guessing one shop. Cross-merchant matching is permitted **only for this negative STOP operation**, never for positive consent.
- Idempotently record STOP/no-contact and provider inbound event identity on **each affected active CustomerPhone** in a short transaction. Duplicates must not redate/revise a previous STOP or leave partial merchant subsets. A newer verified affirmative consent can re-authorise only its own shop/phone; a stale native Shopify grant or Woo merchant re-enable must not silently clear STOP across shops.
- For each affected **Shopify** merchant with a verified Shopify customer/default phone association, call the typed BACKGROUND-001 `unsubscribeRecipient()` to set native WhatsApp marketing consent to `UNSUBSCRIBED`, using that merchant's authorised Shopify installation. Record local STOP **before** external calls and call Shopify **outside** the SQL transaction. On Shopify outage, missing `write_customers` permission or mutation userErrors, retain local STOP and use the **existing bounded inbound-job retry/failure mechanism** for idempotent resynchronisation; if it cannot durably resume incomplete per-merchant Shopify writes, report that concrete gap to the architect rather than claiming eventual consistency or inventing a queue in this task. Do not pretend remote success. A Woo merchant requires no Shopify call.
- If no active CustomerPhone exists for the canonical sender, report the unmatched STOP without falsely claiming durable future suppression. This v1 rule covers **registered numbers**, not unknown future merchants; do not invent a global suppression table. A nonexistent/invalid phone must not mutate unrelated records.
- Preserve existing ARCH-040 handover/moderation and normal customer-initiated service-window replies; only business-initiated proactive recovery is blocked by this consent override.

## Out of Scope

- No new customer/session/erasure table, recipient-reachability consent columns, consent-specific queue or global WhatsApp policy rewrite. No merchant opt-out UI/API (separately owned by Shopify app and Woo API/plugin).

## Requirements

- [ ] Quoted STOP applies to the identified merchant's phone records; **standalone or unresolvable-quote STOP** blocks every active matching phone across all registered merchants, before ordinary routing/ignored-message logic. Existing CustomerPhone no-contact state blocks proactive Marketing sends.
- [ ] Cross-merchant updates occur **only** for standalone/unresolved-quote STOP and are scoped by the canonical sender phone; no positive consent, Customer merge or unrelated number is changed. Missing matching phones are explicitly reported, not marked suppressed.
- [ ] Moderation, human handover and legitimate in-window service replies retain their distinct established rules.
- [ ] STOP-to-Shopify unsubscribe is attempted per affected Shopify merchant; failed API calls never undo local STOP, and each retry uses the stored STOP timestamp against current Shopify consent `updatedAt` to avoid overwriting a demonstrably newer affirmative opt-in. Uncertain chronology stays blocked pending explicit resolution; idempotent retry never duplicates local revisions.

## Work Items

- [ ] Implement a small deterministic opt-out detector at the existing authenticated inbound worker boundary, respecting moderation ordering.
- [ ] Implement explicit quoted-message-to-shop resolution and number-wide fallback; update the correct merchant-scoped or cross-merchant set of current CustomerPhone records atomically/idempotently before ignored/guidance routing.
- [ ] Call BACKGROUND-001 typed Shopify unsubscribe for each affected Shopify merchant outside SQL locks, with tested retry/failure/userErrors handling; no Woo external call. Add quoted, standalone, unresolved quote, multi-customer same-shop, multi-shop, duplicate, partial Shopify outage and concurrent re-consent tests.

## Interfaces / Contracts

Consumes `ARCH-045-DATABASE-002` CustomerPhone local no-contact fields, existing Meta-normalised inbound provider message/conversation mapping and the reusable consent policy read by ARCH-045-BACKGROUND-001/004 and ARCH-046-BACKGROUND-001/004. No new cross-service event schema or recipient-reachability consent table. A standalone STOP deliberately has **all registered merchants** as its target; no guessed recent-conversation shop. Quoted STOP uses validated outbound-message correlation. BACKGROUND-001 provides Shopify unsubscribe; no additional shared queue or global no-contact table.

## Dependencies

- `ARCH-045-DATABASE-002`
- `ARCH-045-BACKGROUND-001`

## Enables

- `ARCH-045-BACKGROUND-002`
- `ARCH-045-BACKGROUND-004`
- `ARCH-046-BACKGROUND-002`
- `ARCH-046-BACKGROUND-004`
- `ARCH-045-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`
- `ARCH-046-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] An authenticated STOP updates the **correct set of active canonical-phone records**, with one effective stop per targeted record despite duplicate delivery; per-shop Shopify unsubscribe failures leave all local blocks in effect.
- [ ] A standalone STOP for a shared number blocks all currently registered shops without disabling any different number. An explicitly referenced merchant STOP leaves other shops untouched. An unresolvable quote follows the number-wide rule and an unmatched sender yields no invented durable suppression.
- [ ] STOP is not lost to ignored/guidance route and does not suppress otherwise legitimate in-window customer-service replies.

## Validation

- [ ] Focused `whatsapp.worker` tests for quoted shop-specific STOP, standalone cross-merchant STOP, unresolvable quote fallback, duplicate provider IDs, multi-merchant and same-shop duplicate numbers, no registered phone, local STOP vs later Shopify consent/merchant re-enable; no PII in logs.
- [ ] ARCH-040 moderation/human-control regression tests, Background send policy denial after STOP and `git diff --check`.
- [ ] Realistic provider-fake STOP-to-Shopify UNSUBSCRIBED mutation tests (`write_customers` denial, userErrors, HTTP failure, retry, lost ACK and partial per-merchant success), including later provider SUBSCRIBED with `updatedAt` after STOP (no stale unsubscribe), older/equal/unknown timestamps (no unsafe local regrant), preserving other shops' no-contact restrictions.

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
