---
id: ARCH-046-BACKGROUND-001
architecture_id: ARCH-046
title: Read current Woo customer-phone consent for exact recipient
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 27
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-045-DATABASE-002
  - ARCH-045-SHARED-002
enables:
  - ARCH-046-BACKGROUND-002
  - ARCH-046-BACKGROUND-004
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-22
---

# Read current Woo customer-phone consent for exact recipient

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

## Objective

Provide a small injectable WooCommerce consent reader for **normal checkout reconciliation and existing authorised recovery sending**, using an unambiguous merchant-scoped active `CustomerPhone`, the existing Woo installation status and current no-contact restrictions.

## Context

`ARCH-045-DATABASE-002` stores current consent on CustomerPhone and immutable Woo grant/withdrawal evidence for audit. Consent evidence is **not** a current-state lookup, polling worklist or recovery trigger. The reader can be implemented and tested before the separate Woo recovery engine exists.

## Scope

- Resolve the shop from the authenticated Woo installation/approved job context and canonicalise the exact checkout recipient using published Shared phone rules; use `Customer.shopId` plus active `CustomerPhone` to select exactly one unambiguous shop-scoped match. Zero, ambiguous or changed-phone matches fail closed; never merge customers because their phone numbers match.
- Require current `GRANTED` WhatsApp checkout-recovery permission from a verified Moda checkbox, no customer STOP and no merchant recovery suppression, and an active installation. A merchant's customer enable toggle cannot create a grant; optional merchant disable is a separate negative restriction.
- Treat recovery as **business-initiated WhatsApp Marketing**, not a utility/transactional notification. The current CustomerPhone permission must cover that marketing purpose; merely capturing the checkout phone, or selecting a customer in merchant admin, is not consent.
- Return typed allowed/not-authorised/unavailable/ambiguous results and an exact-recipient snapshot with current consent/no-contact revision for use by future pre-create and final outbound fences. DB read failures deny; Woo requires **no Shopify HTTP preflight**.
- Reuse an injectable Background policy shape compatible with Shopify first-send/follow-up consumers without duplicating consent decision rules. Test one/no/multiple matches, cross-shop duplicate numbers, canonical-country ambiguity, activation/disconnect, revoke, STOP, merchant enable/disable and DB failure.

## Out of Scope

- No Woo recovery materialisation engine (BACKGROUND-002), evidence scan/polling (BACKGROUND-003 superseded), checkout UI/API capture, external plugin adapter, new identity table or installation consent configuration.

## Requirements

- [ ] Only one exact active CustomerPhone linked to the authenticated shop, a current valid GRANTED permission, no stronger local no-contact and active Woo installation can authorise proactive recovery.
- [ ] A phone match or merchant checkbox/toggle alone never grants permission; stale or withdrawn source decisions cannot be inherited by changed phone or another customer.
- [ ] This reader never schedules checkout work; it remains testable while ARCH-035 is capture-only.
- [ ] A standalone WhatsApp STOP propagated by ARCH-045-BACKGROUND-005 to all registered matching CustomerPhones also blocks the Woo merchant; a quoted STOP for another shop must not modify Woo permission.

## Work Items

- [ ] Implement injected current Woo CustomerPhone/installation consent reader with canonical shop-scoped recipient lookup and typed decision/snapshot.
- [ ] Test missing/ambiguous/cross-shop/changed phone, grant/revoke, STOP, merchant suppression and installation lifecycle without a live Woo recovery engine.

## Interfaces / Contracts

Consumes `ARCH-045-DATABASE-002` CustomerPhone and existing WooCommerceInstallation (no added consent columns), published `ARCH-045-SHARED-001/002` phone canonicalisation. The API is the writer; future `ARCH-046-BACKGROUND-002/004` inject this reader. No Shared Woo consent queue schema.

## Dependencies

- `ARCH-045-DATABASE-002`
- `ARCH-045-SHARED-002`

## Enables

- `ARCH-046-BACKGROUND-002`
- `ARCH-046-BACKGROUND-004`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Same-shop unique exact phone and current granted consent plus active installation are required; cross-shop duplicates never leak permission, same-shop duplicates deny.
- [ ] Customer STOP and merchant suppression override a grant; merchant re-enable never manufactures consent or clears STOP.
- [ ] Reader does not consume evidence history, trigger recovery, require a Woo checkout identity table or use Shopify provider calls.

## Validation

- [ ] Focused DB-backed exact-recipient canonical-phone, cross-tenant, zero/one/multiple matches, installation revoke/reconnect, grant/revoke/STOP and failure tests.
- [ ] Injectability/typed decision and revision-snapshot tests plus `git diff --check`.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

This task is safe to implement before a Woo recovery engine exists; do not include admission integration here.

Before any implementation, use `/moda-task` deterministic preparation against the **developer's actual** primary workspace, read the latest task/Architect Review, the parent architecture, relevant agent instructions, and the repository's real `package.json` scripts. Do not invent environment variables or claim a completed checkout/recovery source from the snapshot. Do not modify another repository, architecture-wide docs or `docs/decisions/**/_index.md` in a repository task. Use `@modainteract/moda-interact-shared/logging` for Node server diagnostics; PHP uses WordPress-specific safe diagnostics. Preserve official user/merchant i18n and tenant boundaries.

## Completion Report

### Status

Not Started — portable, not materialised.

### Files Changed

None — no runtime implementation in this documentation patch.

### Work Completed

None.

### Validation Results

Not run by a repository agent; no developer worktree/remote access is available from this snapshot.

### Deviations

None.

### Assumptions

Source is the supplied 2026-10-20 snapshot, not necessarily latest developer worktree. Versioned APIs/schema and future Woo recovery capability must be verified when eligible. Consent has no Moda-imposed waiting/expiry period. Recheck the current customer-phone permission and independently applicable checkout validity; do not invent a retention deadline.

### Unresolved Issues

None recorded at definition time; raise actual missing cross-repository contract/rollout dependencies to moda_architect before scope drift.

### Architectural Concerns

None recorded beyond explicit context and gates.

## Architect Review

### Review Status

Pending — no implementation reviewed or accepted.

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
