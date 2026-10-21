---
id: ARCH-045-BACKGROUND-003
architecture_id: ARCH-045
title: Synchronise Shopify consent webhook into CustomerPhone
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
  - ARCH-045-DATABASE-002
  - ARCH-045-BACKGROUND-001
  - ARCH-045-SHARED-002
  - ARCH-045-SHOPIFY-001
enables:
  - ARCH-045-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-21
---
# Synchronise Shopify consent webhook into CustomerPhone

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** portable definition, **not** materialised in a developer task worktree or committed/pushed; no execution claim exists.

## Objective

Consume a Shopify consent-state sync signal and **update the existing current `CustomerPhone` consent** using Shopify authority. Do not touch checkout candidates, recovery materialisation, merchant notice or billing.

## Context

ARCH-045-SHOPIFY-001 emits the published minimal Shared sync event. Background-001 owns the safe Shopify GraphQL source-of-truth reader and CustomerPhone update. The user-approved behaviour is **sync now; normal checkout reconciliation later**, not immediate retry of old abandoned checkouts.

## Scope

- Route the validated published `ShopifyWhatsAppConsentSyncJobV1Schema` job in the existing Shopify Background worker/queue infrastructure **separately from checkout v2 event parsing**; no new BullMQ queue.
- Derive shop and Shopify customer from trusted event identity, use BACKGROUND-001 to fetch Shopify **current** phone/marketing-consent, and update the right existing `commerce.CustomerPhone` with monotonic source timestamp/version protection.
- If no safely linked shop-owned Customer exists, record a bounded non-PII no-op; if that Customer exists but its active verified Shopify phone does not, create the exact customer-owned phone safely; a later ordinary checkout reconciliation can initialise permission from Shopify. Never join customers by phone or create a checkout from this signal.
- Handle duplicates, reordered webhooks, transient Shopify API errors and schema/version mismatch with existing bounded queue retry semantics; no consent age timeout.
- **Explicitly prohibit** calling `RecoveryInitiationService`, pending-candidate schedule/refresh, checkout lookup, merchant Support notice or credit/provider code from this handler.

## Out of Scope

- No customer-to-checkout scan, checkout index retention, direct/indirect recovery wakeup, consent-driven queue or periodic sweep.
- No new consent table; CustomerPhone schema owned by DATABASE-002.

## Requirements

- [ ] Consent webhook changes only current phone permission and bounded sync diagnostics.
- [ ] A later grant does not itself create recovery or schedule reconciliation.
- [ ] Out-of-order/double deliveries cannot overwrite more recent consent decisions or cause send/charge.

- Use one Shared numeric-ID -> Customer GID conversion and authenticated shop mapping; never match by phone alone, invent a customer identity or update another tenant. A privacy-erased identity is rejected even when an older consent webhook is retried.
- Never allow an old Shopify provider observation to overwrite a newer local STOP/no-contact override. Ignore duplicate/out-of-order sync jobs and classify GraphQL permission-denied as unavailable, not an affirmative grant.

## Work Items

- [ ] Add distinct existing-queue job dispatch and validation for published Shared sync event.
- [ ] Invoke BACKGROUND-001 native-current consent sync with correct identity and ordering.
- [ ] Test grant/revocation, absent customer, duplicate/reordering, provider timeout and assertion of **zero** recovery/candidate/notice side effects.

- [ ] Add numeric/GID, erased customer, local STOP vs Shopify SUBSCRIBED, stale sync and wrong-shop integration tests.

## Interfaces / Contracts

**Consumer:** published `ARCH-045-SHARED-001/002` Shopify consent-sync event. **Writes:** only `ARCH-045-DATABASE-002` current CustomerPhone fields via BACKGROUND-001. **Producer:** ARCH-045-SHOPIFY-001. No checkout/recovery contract.

## Dependencies

- `ARCH-045-DATABASE-002`
- `ARCH-045-BACKGROUND-001`
- `ARCH-045-SHARED-002`
- `ARCH-045-SHOPIFY-001`

## Enables

- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Accepted consent webhook leads to correct current CustomerPhone update from Shopify provider authority.
- [ ] No new CheckoutRecovery, candidate job, merchant notice, usage charge or message arises solely from consent event.
- [ ] Duplicate/out-of-order and missing-link events remain tenant safe and do not override current consent.

- [ ] Delayed grant cannot rehydrate an erased Customer/CustomerPhone nor clear a newer locally recorded no-contact override.

## Validation

- [ ] Focused existing Shopify worker typed dispatch, provider adapter, database update, error/replay and no-side-effect tests; repository-declared checks and `git diff --check`.

- [ ] Stale/duplicate webhook sync test; consent-sync handler never creates a CheckoutRecovery or recovery queue item.

## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. For publication task, do not rerun implementation validation.

## Implementation Notes

Do not treat `ShopifyWhatsAppConsentSyncJobV1` as proof of subscription. Verify provider state and the exact shop-owned customer/phone; update only the current CustomerPhone projection. Never query a checkout or call recovery materialisation in the sync handler. Keep typed event dispatch and consent projection modular instead of introducing a monolithic file.

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
