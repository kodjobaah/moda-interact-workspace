---
id: ARCH-045-BACKGROUND-003
architecture_id: ARCH-045
title: Re-evaluate Shopify checkout on later WhatsApp consent
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
  - ARCH-045-SHARED-002
  - ARCH-045-SHOPIFY-001
  - ARCH-045-BACKGROUND-002
enables:
  - ARCH-045-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-20
---
# Re-evaluate Shopify checkout on later WhatsApp consent

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** portable definition, **not** materialised in a developer task worktree or committed/pushed; no execution claim exists.

## Objective

Use Shopify WhatsApp consent-change events to re-evaluate **still-addressable abandoned checkouts** and create a first recovery only after fresh verified consent and normal checkout eligibility.

## Context

The new webhook wakes by `(shopId,shopifyCustomerId)`, not by checkout/recovery ID. Under the corrected model no recovery exists while consent is absent. The snapshot's transient `PendingRecoveryCandidate` indexes may be removed after maturation, so durable re-discovery cannot be assumed. Existing checkout locks and materialisation are preferable to a new recovery engine.

## Scope

- Consume published Shared consent-change event in Background with strict validation, bounded retry and shared structured logging. Treat event as a **hint to re-read current Shopify consent**; do not trust event timing as current permission.
- Find only checkout candidates **actually linked to** `(shopId,shopifyCustomerId)` via safe existing candidate identity or authoritative, bounded Shopify checkout lookup. Verify the reference survived the earlier no-consent path; never join by phone or by a Support notice alone, and never scan every shop/customer.
- Re-run current abandoned/unpaid/order eligibility, age/maturity according to existing rules, phone/recipient match, shop entitlements/suppression and live Shopify consent under existing checkout-scoped lock **before first recovery creation**. Only then enter ordinary recovery materialisation/sequence-one idempotency.
- If candidate/reference was removed, checkout cannot be read safely, or is completed/expired, no-op and record bounded reason; a subsequent legitimate checkout event may provide another opportunity. No invented 72-hour consent hold, `DETECTED` consent recovery or new consent-expiry/repair job. If reliable wakeup requires an additional durable checkout reference not already approved, **stop and return the dependency gap to architect** instead of adding a table speculatively.
- Cover duplicate/out-of-order webhook deliveries, multi-candidate customer, competing checkout updates, changed phone/customer identity and consent revocation before provider dispatch.

## Out of Scope

- No new recovery waiting status, consent-specific enum/table, expiry cron, phone-only guest match, or blanket Shopify checkout scan.
- No merchant notice writer (BACKGROUND-002), new recovery algorithm or follow-up send policy (BACKGROUND-004).

## Requirements

- [ ] An event never directly authorises a send; current Shopify `SUBSCRIBED` for exact verified recipient is required.
- [ ] A first recovery is created only on verified actionable checkout; no recovery pre-exists solely due to lack of consent.
- [ ] Checkout lifecycle/eligibility, **not consent age or 72 hours**, determines whether later recovery is possible.
- [ ] Absent identity or lost candidate is a safe no-op with honest limitation, not a phone-number search or forced recovery.

## Work Items

- [ ] Wire Shared-event consumer and bounded customer->candidate/checkout re-evaluation path.
- [ ] Verify candidate retention/re-discovery after BACKGROUND-002 skip and implement only approved bounded reuse.
- [ ] Test duplicate/reordered webhook, multiple checkouts/customer, missing reference, completed checkout, current consent mismatch, race and exactly-one materialisation/charge.

## Interfaces / Contracts

Consumes published `ShopifyWhatsAppConsentChangedJobV1Schema` from ARCH-045-SHARED-001/002, ARCH-045-BACKGROUND-001 consent reader and BACKGROUND-002 pre-creation gate. No `WHATSAPP_CONSENT_MISSING` enum.

## Dependencies

- `ARCH-045-SHARED-002`
- `ARCH-045-SHOPIFY-001`
- `ARCH-045-BACKGROUND-002`

## Enables

- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] An identifiable abandoned checkout with later valid Shopify consent becomes exactly **one first recovery**, not a resumed prior `DETECTED` record; ordinary credit/provider semantics follow.
- [ ] Revoked, wrong recipient/customer/shop, no live checkout, paid checkout and duplicate event yield no new send/charge.
- [ ] No artificial 72-hour wait, arbitrary checkout revival or polling of unbounded candidates.
- [ ] If safe customer->checkout correlation cannot be demonstrated, architect is notified and task is not falsely accepted as unconditional automatic resumption.

## Validation

- [ ] Focused consent event/checkout recheck tests, fake Shopify data and disposable PostgreSQL/Redis where relevant; repository-declared build and `git diff --check`.

## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. For publication task, do not rerun implementation validation.

## Implementation Notes

Do not treat `ShopifyWhatsAppConsentChangedJobV1` as proof of subscription. When the customer-to-checkout identity cannot be verified or the original checkout cannot be re-discovered, perform no recovery creation, provider send or credit reservation; report a bounded no-op rather than guessing from a phone number. Keep event consumption, checkout re-evaluation and initial-materialisation integration modular instead of introducing a monolithic file.

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
