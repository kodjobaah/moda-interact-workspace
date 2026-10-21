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
updated: 2026-10-21
---

# Store Woo WhatsApp consent on CustomerPhone and source on installation

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

## Objective

Persist the latest Woo WhatsApp recovery decision **on existing shop-owned `CustomerPhone`**, the merchant's chosen collector **on existing `WooCommerceInstallation`**, and individual grant/withdrawal proof in **one** append-only Woo-specific evidence record; no other consent or wakeup tables.

## Context

The inspected Prisma schema already has `commerce.Customer`, `commerce.CustomerPhone` and `woocommerce.WooCommerceInstallation`; source and current-consent tables would duplicate them. However, the mutable phone row does **not** provide immutable evidence of each original affirmative choice/withdrawal, replay uniqueness or reliable change wakeups. Existing Commerce Studio and administrative audit tables are purpose-specific and **not an equivalent customer-consent log**. Therefore this baseline justifies **exactly one** additional evidence table. If the developer's later canonical schema already contains a compatible evidence mechanism, stop and return that finding to the architect rather than implement a duplicate. Guest identity requires verified shop/session binding, not a merge by phone. ARCH-045-DATABASE-001 is superseded.

## Scope

- Extend existing `WooCommerceInstallation` with hosted `consentSourceMode=NOT_CONFIGURED|MODA_CHECKBOX|SUPPORTED_EXTERNAL`, optional approved external provider and monotonic `consentSourceEpoch`/revision; absence/default fails closed. Source switch changes eligibility of old grants without deleting historical proof. **No new source-config table.**
- Extend existing `Customer` with **only necessary** shop-unique verified Woo account or server-bound guest checkout identity linkage (e.g. scoped Woo customer ID and guest checkout/session digest). No phone/email-only identity merge; never overload `shopifyCustomerId` with Woo IDs. Add safe indexes/uniqueness validated against actual source data.
- Extend existing `CustomerPhone` with purpose-specific **current** Woo WhatsApp checkout-recovery consent `GRANTED|REVOKED` (null/unknown is not granted), canonical exact phone binding, source/provider/epoch, disclosure version, monotonic revision, last accepted evidence event identity and effective grant/revoke timestamps. Query a correctly resolved **active** phone row; a new/changed phone starts unknown until separately granted. Preserve Shopify-native consent authority; Woo fields may never grant Shopify permission. No new current-consent table.
- Add **one** `WooWhatsAppConsentEvidence`-equivalent append-only model, with shop/customer/CustomerPhone linkage, unique `(shopId,eventId)`, fixed consent purpose, `GRANT|REVOKE`, canonical recipient binding, source/provider/epoch, monotonic decision revision, server-accepted timestamp, disclosure proof (immutable wording reference/hash/version and locale, with the exact wording retrievable for audit) and optional **verified** checkout collection context. This model records the decision event; it is **not** a current-consent projection, a pending CheckoutRecovery, or a second configuration table.
- On **that same evidence row**, permit narrowly scoped mutable *processing-only* columns (actionability status, lease/claim, attempt count, next attempt, terminal ack). Evidence fact columns must remain immutable by app contract/DB guarantees; receipt state may transition. Pre-recovery events are `NOT_ACTIONABLE` at initial commit; later only new eligible grant receipts can be claimed by an approved engine. Add bounded indexed worklist/cleanup of processing state without deleting audit proof. Do not add a separate wakeup/outbox table or cross-repository queue schema.
- Make current phone transition and immutable evidence insert **one transaction**: same shop/event/facts is an idempotent replay, conflicting facts or stale revision are rejected, and source switch revokes *eligibility* by epoch mismatch without falsifying historical evidence. Prove safe concurrent grant/revoke, phone rollover, one-active-phone resolution, verified guest/account identity and installation fencing in fresh and upgrade PostgreSQL migrations. Retention and erasure apply to evidence separately from wakeup ack and consent state.

## Out of Scope

- No separate `WooWhatsAppRecoveryConsent` current projection, `WooWhatsAppConsentSourceConfiguration`, generic audit event repository, new wakeup/outbox table or dedicated Redis/Shared queue schema.
- No `WHATSAPP_CONSENT_MISSING` enum; no initial `CheckoutRecovery` on missing consent; no Shopify consent persistence or WordPress-owned DB table.

## Requirements

- [ ] Customer identity must be verified and shop-scoped; phone number alone cannot claim an unrelated customer's grant.
- [ ] Grants apply only to the exact customer/phone/consent-purpose and active merchant source/provider/epoch, **not one checkout or a 72-hour period**.
- [ ] Revocation and changed number fail closed; old delayed grant cannot overwrite a newer revoke/source epoch.
- [ ] Pre-recovery evidence is persisted for audit but **non-actionable** for wakeup at commit; later bounded claim/retry/terminal ack mutates only delivery metadata. Deleting a processed receipt must never be the default way to acknowledge work; consent validity is independent of evidence retention.

## Work Items

- [ ] Author only the necessary additive Prisma fields/indexes on existing Customer/CustomerPhone/WooCommerceInstallation and exactly one minimal Woo evidence/change model (subject to the newer-schema reuse check). Define current-state vs immutable-evidence vs mutable-worklist-field ownership and indexes explicitly.
- [ ] Rehearse fresh + upgrade PostgreSQL, tenant/customer/active-phone uniqueness, guest identity, stale/out-of-order revision, source-epoch switch, exact retry vs conflicting duplicate, immutable audit columns, non-actionable pre-recovery receipts, indexed claim/ack and privacy export/erasure.

## Interfaces / Contracts

**Schema contract:** `commerce.Customer` holds shop-scoped verified identity; `commerce.CustomerPhone` holds latest exact-number Woo permission; `woocommerce.WooCommerceInstallation` holds merchant source/provider/epoch; a single `woocommerce.WooWhatsAppConsentEvidence`-equivalent table holds append-only grant/withdrawal facts plus separately mutable wakeup processing columns. **Writers:** API-003 updates only installation source; API-001 atomically changes current phone consent and writes evidence. **Readers:** Background-001 checks only current phone + installation authority; Background-003 treats indexed actionable evidence as a *hint* and re-reads current state before any checkout evaluation. No new Shared queue schema, consent-wait CheckoutRecovery or per-checkout consent state.

## Dependencies

None

## Enables

- `ARCH-046-API-003`
- `ARCH-046-API-001`
- `ARCH-046-BACKGROUND-001`
- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Source mode is stored on existing installation; latest Woo consent is stored on existing CustomerPhone; **exactly one justified append-only evidence/change table** on the inspected schema, with immutable decision facts vs mutable bounded processing metadata. No new recovery enum, source/current table or event queue.
- [ ] Correct tenant/customer/active-phone resolution, revocation ordering, idempotent exact event retry vs conflicting duplicate, merchant source invalidation and no guest phone-only merge proven in disposable PostgreSQL. Pre-recovery receipts never backlog as actionable wakeups; processing cannot rewrite historical proof.
- [ ] No update fabricates permission from previous checkout/order/CRM data.

## Validation

- [ ] Repository-declared Prisma generate/validate/migrate and focused disposable PostgreSQL fresh/upgrade/idempotence/replay tests; `git diff --check`.

## Stop Condition

After completing **only** the defined Work Items, Acceptance Criteria and required Validation, record launcher-resolved dedicated parent/implementation worktrees, their physical isolation and start-of-attempt synchronization evidence in the Completion Report. Change task to `review`, return control to `moda_architect`, and **STOP**. Do not start enabled tasks. A `blocked` task must remain blocked until the architect verifies and records the external missing recovery dependency and explicitly makes it Ready.

## Implementation Notes

Keep evidence minimal, immutable and privacy-aware. `CommerceAuditEvent` is not a generic substitute for customer consent. Make the event ID, server decision timestamp, exact disclosure proof and verified recipient binding durable; mutable claim/ack columns are delivery bookkeeping, not consent facts. Do not attach permission to a Woo order alone: checkout can be abandoned before order placement.

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
