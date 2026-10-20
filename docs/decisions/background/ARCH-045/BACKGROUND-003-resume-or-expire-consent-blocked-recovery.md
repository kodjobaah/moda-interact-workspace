---
id: ARCH-045-BACKGROUND-003
architecture_id: ARCH-045
title: Resume or expire consent-blocked recovery on Shopify consent change
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-045-DATABASE-001
  - ARCH-045-SHARED-002
  - ARCH-045-SHOPIFY-001
  - ARCH-045-BACKGROUND-002
enables:
  - ARCH-045-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-20
---
# Resume or expire consent-blocked recovery on Shopify consent change

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** portable definition, **not** materialised in a developer task worktree or committed/pushed; no execution claim exists.

## Objective

Consume Shopify WhatsApp consent changes to safely resume the same consent-blocked recovery, while deterministically expiring it after 72 hours even without a later event.

## Context

Shopify can deliver duplicate/out-of-order consent-change webhooks. Existing capacity resume supports checkout locks and fresh checkout lookup but only knows capacity/suppression admission reasons; this task extends it with consent-targeted wakeups, not a parallel recovery engine.

## Scope

- Register a consumer for published Shared v1 consent-change queue in the existing Background recovery worker deployment, with strict runtime validation, bounded retries, shared structured logging and queue lifecycle cleanup.
- Resolve exact `(shopId,shopifyCustomerId)` to Moda Customer and scan only indexed `DETECTED`, `WHATSAPP_CONSENT_MISSING`, non-expired recoveries via bounded pages; do not correlate by phone alone.
- Schedule idempotent **targeted** resume through existing recovery-capacity-resume service (separate consent trigger identity), not generic all-shop capacity recovery; extend targeted admission/re-entry and terminalisation to the new block reason without unblocking other reasons.
- On re-entry, use fresh Shopify consent, current canonical recipient, real abandoned-checkout/paid-order checks, original maturity delay, shop entitlement/ownership/reachability suppression, 72-hour deadline and existing unique sequence-one attempt/billing/provider idempotency.
- At deadline set still-blocked `DETECTED` recovery to `EXPIRED` with status history; use deterministic delayed deadline wakeup **and** bounded past-deadline repair in existing periodic recovery repair cycle to survive a missed wakeup. Do not poll all unexpired blocked recoveries.
- Handle absent/unlinked Shopify ID, revoked/late webhook, duplicate, queue race, completed order, changed phone, retryable Shopify API outage and credit release correctly.

## Out of Scope

- No merchant Support notification implementation (BACKGROUND-002); no new queue infrastructure service, new dashboard or consent cache.
- No customer-phone-only search to infer consent; no reactivation of `EXPIRED`, `COMPLETED`, `CANCELLED`.
- No general-purpose recovery follow-up redesign (BACKGROUND-004).

## Requirements

- [ ] Only event-matched blocked recoveries for the exact tenant and verified Shopify customer are candidates; current consent **always** read live near send.
- [ ] 72-hour window from original `detectedAt`, no extension from webhook/update/repair/retry; expiry at timestamp boundary is terminal.
- [ ] Webhook absence cannot keep an eligible blocked recovery open forever; no busy polling.
- [ ] Queue event never carries the raw customer phone, and duplicate/out-of-order deliveries cannot double-message or double-bill.

## Work Items

- [ ] Add Shared-event consumer and bounded customer-matching selection.
- [ ] Wire consent-only targeted resume with fresh Shopify+checkout recheck and existing locks/attempts.
- [ ] Add deterministic expiry wakeup and bounded past-deadline repair.
- [ ] Add failure, identity isolation, concurrency, expiration and idempotency tests.

## Interfaces / Contracts

Consumes published `ShopifyWhatsAppConsentChangedJobV1Schema` (SHARED-001/002), `WHATSAPP_CONSENT_MISSING` (DATABASE-001), BACKGROUND-001 consent reader and existing Background recovery-capacity-resume queue/worker. No new cross-service format invented locally.

## Dependencies

- `ARCH-045-DATABASE-001`
- `ARCH-045-SHARED-002`
- `ARCH-045-SHOPIFY-001`
- `ARCH-045-BACKGROUND-002`

## Enables

- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Consent added within 72h, same customer/phone/abandoned checkout -> the *same* generation resumes once and follows normal billable admission only after verified permission.
- [ ] Consent revoked, stale update, missing identity, completed checkout, terminal status, mismatch or expired wait -> **zero** provider sends and charges.
- [ ] Duplicate/reordered webhooks and concurrent workers do not create duplicate sequence-one attempt, message or credit.
- [ ] Deadline expiry succeeds even when no consent webhook arrives and after simulated delayed-job loss; repair is bounded and uses existing timer/worker.
- [ ] No unexpected consent/scoped event impact on existing capacity/suppression resumes.

## Validation

- [ ] Focused Background event-consumer/resume/expiry tests with stub Shopify and disposable PostgreSQL/Redis where required.
- [ ] Inject retryable Shopify API and queue-add failures; run repository-declared build/check and `git diff --check`.

## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. For publication task, do not rerun implementation validation.

## Implementation Notes

Do not treat `ShopifyWhatsAppConsentChangedJobV1` as proof of subscription. The clean return when identity is not linkable is to leave DETECTED blocked (and later expire), not guess from phone. Use separate small event-consumer, resume/expiry policy and integration wiring instead of a monolithic file.

Before claiming, use the deterministic `/moda-task` launcher and its **actual** prepared packet, read the task's complete current Architect Review, and verify task/dependency status in the developer's canonical workspace. Preserve `docs/decisions/**/_index.md` untouched until the developer explicitly closes the architecture documentation session. New runtime structured logging uses `@modainteract/moda-interact-shared/logging` where applicable. No source outside this task's owner repository may be changed unless explicitly authorised by the architecture.

## Completion Report

### Status

Not Started — external portable definition, not materialised.

### Files Changed

None — not implemented.

### Work Completed

None.

### Validation Results

Not run; the supplied snapshot is not the developer's task worktree.

### Deviations

None.

### Assumptions

Use the 2026-10-20 snapshot for orientation; revalidate active code/configuration when the task is materially claimed. ARCH-045's provisional 72-hour consent-wait deadline is the exact v1 task contract unless the developer and architect amend it before implementation.

### Unresolved Issues

None recorded at definition time; report any discovered cross-repository dependency rather than implementing outside ownership.

### Architectural Concerns

None recorded at definition time.

## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

None.

### Reviewed Files

None — portable definition only.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
