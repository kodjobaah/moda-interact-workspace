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
enables:
  - ARCH-045-BACKGROUND-003
  - ARCH-045-BACKGROUND-004
  - ARCH-045-SHOPIFY-002
  - ARCH-045-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-20
---
# Skip unconsented Shopify recovery creation and notify merchant

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** portable definition, **not** materialised in a developer task worktree or committed/pushed; no execution claim exists.

## Objective

Before creating the initial Shopify `CheckoutRecovery`, verify WhatsApp consent for the exact customer/phone and notify the merchant once for an unconsented checkout, with **no recovery row, attempt or credit**.

## Context

`recovery-materialization.service.ts` currently calls `initiate(seed,generation,recipient)` after resolving a mature, still-abandoned checkout and phone. `recovery-initiation.service.ts` may persist the recovery immediately, so consent must be gated **before that call**, not by updating `DETECTED` afterwards. Merchant Support already supports unique `sourceKey` notices.

## Scope

- Inject BACKGROUND-001 read-only Shopify consent policy at the mature checkout/recipient boundary **before** `initiate/upsertRecovery`; refuse creation for absent, revoked, unlinked, mismatched or otherwise unverified opt-in. Distinguish API unavailable from explicit negative state; retry unavailable reads boundedly without inventing consent.
- Create at most one existing `MerchantSupportMessage(kind=SYSTEM)` with deterministic bounded `sourceKey` derived from `shopId + checkoutToken + reason` (hash if needed), **never `recoveryId`**. Inform merchant no message/credit and that later opt-in only permits reconsideration while the checkout remains eligible/identifiable. Do not imply customer explicitly refused if collection is merely unknown or API unavailable.
- Preserve checkout candidate context for legitimate later re-evaluation **only through an existing, bounded and eligible checkout-state/candidate mechanism**; inspect real candidate removal on maturation. Do not create a `CheckoutRecovery`, new waiting table, indefinite Redis polling or 72-hour consent deadline for a denied candidate. Report unresolved reference-retention gap to architect, rather than promise lossless future wakeup without evidence.
- For an **authorised** recovery, preserve existing first creation/attempt/billing/suppression workflow and arrange a final fresh consent fence near irreversible provider dispatch, with existing pre-provider release/compensation for withdrawal.

## Out of Scope

- No `RecoveryAdmissionBlockReason` migration, `DETECTED` waiting record, new Support table, custom consent-expiry job or customer WhatsApp message seeking opt-in.
- No consent webhook consumer (BACKGROUND-003) or follow-up changes (BACKGROUND-004).

## Requirements

- [ ] Explicit negative/unknown/unlinked consent yields **zero** CheckoutRecovery rows for this attempted initial materialisation, attempts, credit reserves/commits and provider sends.
- [ ] Provider verification errors remain fail-closed and retryable; do not mislabel a temporary outage as customer refusal.
- [ ] Merchant notification deduplicates by `(shop, checkout, reason)` across duplicate events/workers; failed notices can be repaired independently of sending.
- [ ] Existing capacity/suppression and no-phone logic are unaffected after positive consent admission.

## Work Items

- [ ] Add injected pre-creation consent seam, preserve checkout lock/order recheck, and final pre-provider gate for authorised path.
- [ ] Add idempotent checkout-keyed Support SYSTEM message and failure-safe retry.
- [ ] Audit candidate retention/discovery after no-consent maturation; record limits and narrow tested behaviour.
- [ ] Test duplicates, concurrency, provider unavailable, zero recovery rows/credits/sends and legitimate subscribed path.

## Interfaces / Contracts

Consumes ARCH-045-BACKGROUND-001 reader and existing Shopify `PendingRecoveryCandidate`/checkout lookup. Produces existing Support `MerchantSupportMessage` identified by shop/checkout/reason. No new database or queue contract.

## Dependencies

- `ARCH-045-BACKGROUND-001`

## Enables

- `ARCH-045-BACKGROUND-003`
- `ARCH-045-BACKGROUND-004`
- `ARCH-045-SHOPIFY-002`
- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Negative or unknown consent creates **no recovery** and no charge/provider send, with one correctly worded merchant notice for the checkout.
- [ ] Positive consent can create one recovery under original business gates; subsequent withdrawal before sending stops and compensates admission.
- [ ] Verified behavior for absent/consumed candidate is documented; no unfounded promise of unconditional later recovery.
- [ ] No consent-specific expiry clock, admission reason or new persistence table.

## Validation

- [ ] Focused Background candidate/materialisation, notice-idempotency and billing/provider tests; disposable PostgreSQL where needed; repository-declared build and `git diff --check`.

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
