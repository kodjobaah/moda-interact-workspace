---
id: ARCH-045-BACKGROUND-002
architecture_id: ARCH-045
title: Skip unconsented Shopify recovery creation and notify merchant
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-045-BACKGROUND-001
  - ARCH-045-BACKGROUND-005
enables:
  - ARCH-045-BACKGROUND-004
  - ARCH-045-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-22
---
# Skip unconsented Shopify recovery creation and notify merchant

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** portable definition, **not** materialised in a developer task worktree or committed/pushed; no execution claim exists.

## Objective

During **ordinary Shopify checkout reconciliation**, reject unconsented first recoveries **before the first `CheckoutRecovery` INSERT** and publish one truthful checkout-keyed merchant Support notice without sending WhatsApp or charging a recovery credit.

## Context

`BACKGROUND-001` supplies Shopify-native current consent and an injectable policy. `recovery-initiation.service.ts` currently creates a recovery before some later admission checks; the policy must move to a pre-create seam. `BACKGROUND-004` will own the last pre-provider sending fence shared by all proactive paths.

## Scope

- Integrate `ShopifyWhatsAppConsentService.evaluateRecipient()` at mature pending-candidate/**each distinct new Shopify checkout** reconciliation before creating a first `CheckoutRecovery`, reserving credits or sending. Obtain a fresh Shopify `readCurrent()` observation for that checkout, project its native decision to CustomerPhone, and retain existing paid/abandoned checkout, exact recipient, entitlement and idempotency gates. Duplicate deliveries of the same checkout must not produce redundant recovery or billing work.
- On confirmed no opt-in, unknown/revoked consent, ambiguous recipient or local customer STOP/merchant suppression: no first recovery row, attempt, charge or provider send. Keep Shopify temporary provider/API verification outages as a **distinct fail-closed technical outcome** under the existing bounded retry rules.
- Reuse existing `MerchantSupportMessage(kind=SYSTEM)` and a bounded deterministic `sourceKey` derived from shop, **hashed** checkout identity and reason. Show one checkout/reason notice without leaking phone/checkout tokens; never claim the customer refused consent when Shopify was unavailable or identity could not be resolved. No separate Support table.
- Apply the same initial-admission policy to first-send re-entry through existing `DETECTED` recoveries, capacity resume, recipient suppression and initial-send retries. Historical pre-existing recoveries may retain their rows, but no new send/credit is permitted after withdrawal or no-contact. `BACKGROUND-004` supplies the shared **final** dispatch guard.
- A later consent grant updates CustomerPhone only. Reconsideration requires an independently occurring **normal** checkout event/reconciliation; the pending-candidate index is not retained merely to wait for consent.
- An approved **Marketing-category** abandoned-basket template is required for first proactive recovery outreach; neither a generic utility/transactional template nor phone collection alone can authorise the send. BACKGROUND-004 owns common template-category and final-dispatch checks; the initial recovery cannot bypass that path.

## Out of Scope

- No consent-blocked recovery status/enum, 72-hour consent clock, consent-specific queue/sweeper, Shopify merchant consent-collector configuration, customer opt-in WhatsApp request, privacy-erasure fence or recipient-reachability schema change.
- Do not implement the final scheduled/post-window send fence owned by BACKGROUND-004 or webhook-consent synchronisation owned by BACKGROUND-003.

## Requirements

- [ ] The first recovery must **not** exist when current exact customer/phone consent is unverified or denied; use no `DETECTED` consent-wait row.
- [ ] All initial admission and first-send retry/reentry paths use the same injected consent/no-contact policy and preserve existing billing/reservation/compensation rules.
- [ ] Merchant notices distinguish confirmed no opt-in from identity ambiguity and transient Shopify verification failure, without falsely asserting customer refusal.
- [ ] Missing consent is not a reason to retain or periodically poll an abandoned checkout; only ordinary future reconciliation may attempt again.
- [ ] Each new Shopify checkout's initial recovery decision freshly verifies native WhatsApp marketing consent and persists the result to CustomerPhone. Later sends from an already-created recovery read stored permission and do not make another Shopify consent API call.

## Work Items

- [ ] Move the first consent check before `RecoveryInitiationService` persists its first recovery; wire the existing candidate and direct initiation paths.
- [ ] Reuse that policy for capacity/suppression and legacy `DETECTED` first-send reentries, delegating final pre-provider fencing to BACKGROUND-004.
- [ ] Implement idempotent checkout-keyed Support notices with distinct bounded denial/failure reasons.
- [ ] Test duplicate candidates, no new recovery/charge on denial, technical failure retry, real later checkout event and no-event inactivity.

## Interfaces / Contracts

Consumes BACKGROUND-001 current CustomerPhone + Shopify authority and existing normal checkout candidate/initiation, Support and billing contracts. Depends on BACKGROUND-005's durable customer STOP semantics; **no second permanent no-contact representation** is created in `WhatsAppRecipientReachability`.

## Dependencies

- `ARCH-045-BACKGROUND-001`
- `ARCH-045-BACKGROUND-005`

## Enables

- `ARCH-045-BACKGROUND-004`
- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Initial negative/unknown/unavailable permission creates no new CheckoutRecovery, outbound message, recovery attempt or billable charge; duplicates produce at most one notice per checkout/reason.
- [ ] Direct initiation, pending candidate maturation, capacity resume, suppression retry and old `DETECTED` first sends cannot bypass latest phone consent/STOP. Existing rows are not rewritten merely to model missing consent.
- [ ] The first recovery Marketing template cannot be sent using a Utility classification or an unverified template category; no provider send or credit on a category/consent denial.
- [ ] A grant alone causes no recovery/candidate job; a later legitimate reconciliation may create the first recovery only if the checkout still qualifies.
- [ ] API outage, missing identity and confirmed absent opt-in produce appropriately distinct operational/merchant outcomes.

## Validation

- [ ] Focused candidate/materialisation, direct initiation, capacity/suppression reentry, Support deduplication, billing/Meta zero-send and unavailable-provider tests; assert no new recovery on initial denial.
- [ ] Real next checkout event versus no event, paid-order race, changed recipient, duplicate jobs, customer STOP/merchant suppression and `git diff --check`.
- [ ] Marketing-template availability/classification tests, one provider consent verification per new checkout (not per follow-up), missing-consent merchant notice and Shopify read outage distinction.

## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. For publication task, do not rerun implementation validation.

## Implementation Notes

Prefer a small consent admission/merchant notice service injected into the existing initiation method. Use Shared logging; do not expand a large orchestration module with generic logging/transport logic. Existing Support inbox copy is delivered by the app, not via Meta WhatsApp.

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

Use the 2026-10-20 snapshot only as a baseline; verify current active code on task claim. Consent has no fixed 72-hour wait or expiry; checkout eligibility follows the authoritative lifecycle.

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
