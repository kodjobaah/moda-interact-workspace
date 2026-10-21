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

Consume the published Shopify WhatsApp consent-change signal and **only synchronise current `commerce.CustomerPhone`** from Shopify's present authority; never trigger checkout reconciliation or recovery.

## Context

`SHOPIFY-001` emits a minimal validated consent-sync event. `BACKGROUND-001` owns the current Shopify GraphQL reader and safe monotonic CustomerPhone update. This task only routes events through the existing Background queue/worker infrastructure.

## Scope

- Add a distinct validated `ShopifyWhatsAppConsentSyncJobV1Schema` dispatch branch to the existing worker/queue, separate from checkout-v2 parsing, using the published Shared package. No new BullMQ queue or event format.
- Resolve `shopId` and Shopify customer ID from trusted event identity through Shared numeric/GID conversion; invoke BACKGROUND-001 to read current Shopify phone/consent and update the existing CustomerPhone. Do not treat the webhook payload itself as an opt-in.
- If the shop-linked Customer is unavailable or ambiguous, record bounded non-PII diagnostics and do not invent a new Customer from a phone. Existing customer/phone lifecycle constraints remain in force; privacy erasure implementation is **not** added by this consent task.
- Handle replay, ordering, outdated provider observations, schema mismatch and provider failure using existing bounded job retry/failure handling. Never override newer CustomerPhone consent, customer STOP or merchant suppression with an older observation.
- Explicitly prohibit checkout lookup, pending-candidate scheduling, `RecoveryInitiationService`, merchant Support notices, credit or provider-send effects in this event consumer.

## Out of Scope

- No consent-driven checkout scan/sweeper, candidate retention, direct recovery resumption, additional evidence polling, 72-hour timeout, customer-erasure work or new durable consent table.

## Requirements

- [ ] All valid consent-change signals cause a **fresh provider-state check**, not acceptance of a stale event's asserted grant.
- [ ] This handler may update current CustomerPhone and bounded diagnostics only; it cannot create, reschedule or send a recovery.
- [ ] Wrong-shop, absent-customer and reordered events remain tenant-safe and fail closed without inventing a customer or opt-in.

## Work Items

- [ ] Wire published Shared sync-job validation and distinct dispatch into the existing Shopify Background worker.
- [ ] Invoke the BACKGROUND-001 injected native synchroniser and record bounded success/no-op/failure outcomes.
- [ ] Test duplicate/reordered events, numeric/GID identity, provider outage and assertion of **zero** recovery/candidate/notice/billing effects.

## Interfaces / Contracts

**Producer:** ARCH-045-SHOPIFY-001. **Contract:** published ARCH-045-SHARED-001/002 consent-sync event. **Consumer:** this handler invokes ARCH-045-BACKGROUND-001 and writes existing ARCH-045-DATABASE-002 CustomerPhone fields only. No consent-wakeup or Woo contract.

## Dependencies

- `ARCH-045-DATABASE-002`
- `ARCH-045-BACKGROUND-001`
- `ARCH-045-SHARED-002`
- `ARCH-045-SHOPIFY-001`

## Enables

- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] A real native grant/revoke change eventually updates the correct current CustomerPhone while a stale/duplicate signal cannot regress local state or local STOP.
- [ ] A consent-sync job alone produces **zero** checkout candidates, CheckoutRecovery rows, merchant notices, WhatsApp sends, usage charges or new recovery queue activity.
- [ ] Unresolvable customer/shop, GraphQL errors and unexpected schema versions are handled deterministically using existing bounded failure mechanisms.

## Validation

- [ ] Typed worker dispatch tests, native provider refresh and monotonic CustomerPhone update tests, duplicate/reordered job, wrong-tenant, missing customer, provider unavailable and no-side-effect assertions.
- [ ] Repository-declared checks and `git diff --check`.

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
