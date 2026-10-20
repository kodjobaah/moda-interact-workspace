---
id: ARCH-046-DATABASE-001
architecture_id: ARCH-046
title: Store Woo WhatsApp consent on CustomerPhone and source on installation
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-046-API-003
  - ARCH-046-API-001
  - ARCH-046-BACKGROUND-001
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-20
---

# Store Woo WhatsApp consent on CustomerPhone and source on installation

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

## Objective

Persist Woo current WhatsApp recovery consent **on the existing shop-owned `CustomerPhone`**, with merchant source settings on `WooCommerceInstallation` and only one minimal immutable change/evidence record for audit and idempotent wakeups.

## Context

The snapshot already has `commerce.Customer`, `commerce.CustomerPhone` and `woocommerce.WooCommerceInstallation`. The earlier proposal for three new source/current/evidence models duplicated these structures. Guest checkout identity needs a safe verified customer linkage, **not** a merge by phone alone. ARCH-045-DATABASE-001 is superseded.

## Scope

- Extend existing `WooCommerceInstallation` with hosted `consentSourceMode=NOT_CONFIGURED|MODA_CHECKBOX|SUPPORTED_EXTERNAL`, optional approved external provider and monotonic `consentSourceEpoch`/revision; absence/default fails closed. Source switch changes eligibility of old grants without deleting historical proof. **No new source-config table.**
- Extend existing `Customer` with **only necessary** shop-unique verified Woo account or server-bound guest checkout identity linkage (e.g. scoped Woo customer ID and guest checkout/session digest). No phone/email-only identity merge; never overload `shopifyCustomerId` with Woo IDs. Add safe indexes/uniqueness validated against actual source data.
- Extend existing `CustomerPhone` with purpose-specific **current** WhatsApp checkout-recovery consent `GRANTED|REVOKED` (null/unknown is not granted), canonical exact phone, source/provider/epoch, disclosure version, monotonic revision, last evidence event identity and effective grant/revoke timestamps. Ensure only the **correct active phone row** can authorise sends; new phone starts unknown until positively consented. No new current-consent table.
- Add **at most one** minimal append-only consent evidence/change model, linked to shop/customer/phone, with unique `(shopId,eventId)`, optional verified checkout collection context, decision, source/epoch, disclosure proof and bounded processing/ack metadata. New evidence is marked **non-actionable for recovery wakeup while the Woo recovery engine is disabled**, not indefinitely queued. This record is **not** a checkout-scoped current projection or pending CheckoutRecovery.
- Make current phone update and new immutable receipt atomic, support revision ordering, duplicate replay, source-switch invalidation and concurrent grant/revoke; migrate fresh and existing PostgreSQL with safe retention/export/erasure consideration.

## Out of Scope

- No separate `WooWhatsAppRecoveryConsent` current projection or `WooWhatsAppConsentSourceConfiguration` table.
- No `WHATSAPP_CONSENT_MISSING` enum; no initial `CheckoutRecovery` on missing consent; no Shopify consent persistence or WordPress-owned DB table.

## Requirements

- [ ] Customer identity must be verified and shop-scoped; phone number alone cannot claim an unrelated customer's grant.
- [ ] Grants apply only to the exact customer/phone/consent-purpose and active merchant source/provider/epoch, **not one checkout or a 72-hour period**.
- [ ] Revocation and changed number fail closed; old delayed grant cannot overwrite a newer revoke/source epoch.
- [ ] Evidence receipt processing has a bounded terminal cleanup even while Woo recovery engine is not enabled; consent itself remains independent of receipt retention.

## Work Items

- [ ] Author necessary additive Prisma fields/indexes on existing Customer/CustomerPhone/WooCommerceInstallation and one minimal evidence/change model.
- [ ] Rehearse fresh + upgrade PostgreSQL, customer/phone uniqueness, guest identity, late revision, source switching, duplicate event, outbox processing and privacy deletion.

## Interfaces / Contracts

`commerce.Customer`, `commerce.CustomerPhone`, `woocommerce.WooCommerceInstallation`; one `WooWhatsAppConsentEvidence`-equivalent immutable record owned by Database. API-003 updates installation config, API-001 updates customer phone/evidence, Background-001 reads current phone and config; Background-003 consumes bounded evidence wakeups. No Shared queue schema invented.

## Dependencies

None

## Enables

- `ARCH-046-API-003`
- `ARCH-046-API-001`
- `ARCH-046-BACKGROUND-001`
- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Source choice is stored on existing installation; current consent on existing CustomerPhone; **only one new evidence/change table at most**, no recovery enum.
- [ ] Unique correct customer/phone+tenant resolution, revocation ordering, idempotent duplicate, source invalidation and no guest phone-only merge proven in disposable PostgreSQL.
- [ ] No update fabricates permission from previous checkout/order/CRM data.

## Validation

- [ ] Repository-declared Prisma generate/validate/migrate and focused disposable PostgreSQL fresh/upgrade/idempotence/replay tests; `git diff --check`.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

Keep evidence minimal and queryable. Do not attach consent truth to a Woo order alone: checkout can be abandoned before the order is placed.

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
