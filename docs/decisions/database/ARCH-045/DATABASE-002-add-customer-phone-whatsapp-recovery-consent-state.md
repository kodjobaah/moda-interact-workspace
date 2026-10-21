---
id: ARCH-045-DATABASE-002
architecture_id: ARCH-045
title: Add shared current WhatsApp recovery consent to CustomerPhone
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
  - ARCH-045-BACKGROUND-001
  - ARCH-045-BACKGROUND-003
  - ARCH-046-DATABASE-001
created: 2026-10-21
updated: 2026-10-21
---
# Add shared current WhatsApp recovery consent to CustomerPhone

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** portable definition, **not** materialised in a developer task worktree or committed/pushed; no execution claim exists.

## Objective

Add one additive, cross-platform **current WhatsApp checkout-recovery consent state** to existing `commerce.CustomerPhone`, for Shopify and WooCommerce, without creating a `CheckoutRecovery` or separate consent-current table.

## Context

The inspected `CustomerPhone` has shop-owned customer linkage and active phone intervals but no WhatsApp consent state. Shopify webhook sync and Woo opt-in API must write the **same canonical fields**. The obsolete ARCH-045-DATABASE-001 consent-block recovery enum remains Superseded; this is a separate new task under the same initiative, not a re-use of the withdrawn task ID.

## Scope

- Define minimum current-state fields/enum on `CustomerPhone` for `WHATSAPP_CHECKOUT_RECOVERY`: unknown/not-granted-by-default state, authoritative platform/source, source-observed/updated timestamp, verification time, Woo provider/installation source epoch where applicable, and enough monotonic decision version to reject older observations. Preserve exact phone and Customer/Shop ownership.
- Design active-phone matching/uniqueness and indexes based on actual stored data; prevent ambiguous active same-customer phone grants, cross-tenant identity collisions, phone-change inheritance and default grants. Do not use phone alone as an identity key.
- Provide one additive Prisma migration, fresh/upgrade PostgreSQL tests and tenant/customer/exact-recipient, default-deny, revoke, source-epoch, out-of-order and rolling consumer compatibility checks.
- Implement **only** the shared current-state schema here. ARCH-046-DATABASE-001 separately owns Woo installation configuration and one immutable Woo evidence record; no Shopify consent audit table, recoveries, queue tables or event polling flags.

## Out of Scope

- No `RecoveryAdmissionBlockReason.WHATSAPP_CONSENT_MISSING` or `CheckoutRecovery` creation for missing consent.
- No Shopify webhook handler, Woo API write, provider read, audit history table, evidence wakeup/processing worklist or recovery scheduler.
- No separate platform-specific `CustomerPhone` consent schema; one current record supports both platforms without sharing their authority rules.

## Requirements

- Default/new/migrated CustomerPhone consent is UNKNOWN/NOT_GRANTED, never implicitly GRANTED.
- Exact customer and active phone scope; a phone change or customer merge must not inherit another number/customer grant.
- Persist enough Shopify provider ordering and Woo source epoch/revision to prevent older changes or stale source selection resurrecting consent.
- Shopify local state is a validated projection of Shopify-native consent, not a substitute for a fresh provider check where required. Woo hosted CustomerPhone is current consent authority under the active installation collector.

## Work Items

- [ ] Inspect existing CustomerPhone identity/history invariants, implement minimally sufficient additive Prisma fields and migration.
- [ ] Add focused PostgreSQL fresh/upgrade, null/default-deny, scope, exact-phone, stale-version and source-epoch tests.
- [ ] Record schema field names and ownership for both ARCH-045/046 consumer tasks.

## Interfaces / Contracts

**Owner:** `moda_database`. **Schema:** `commerce.CustomerPhone` current WhatsApp recovery permission, purpose/source/provider timestamp and Woo epoch binding. **Writers:** ARCH-045-BACKGROUND-001/003 for verified Shopify state; ARCH-046-API-001 for verified Woo grant/revoke. **Readers:** ARCH-045-BACKGROUND-001/002/004 and ARCH-046-BACKGROUND-001/002/004. **Separate evidence:** ARCH-046-DATABASE-001 only. No new Shared Redis queue or consent-driven recovery worklist.

## Dependencies

None

## Enables

- `ARCH-045-BACKGROUND-001`
- `ARCH-045-BACKGROUND-003`
- `ARCH-046-DATABASE-001`

## Acceptance Criteria

- [ ] One current decision lives on CustomerPhone with safe unknown default and exact customer/phone scope.
- [ ] Both platforms can consume the schema without duplicating current consent tables; Shopify source not overwritten by Woo events.
- [ ] Out-of-order/old source epochs cannot convert a revoked or unknown current decision into an eligible grant.
- [ ] Disposable PostgreSQL migration/schema tests pass; no new CheckoutRecovery/notice/evidence-worklist table or consent expiry.

## Validation

- [ ] Repository-declared Prisma validate/generate, disposable PostgreSQL migration fresh/upgrade tests, schema-focused tests and `git diff --check`.

## Stop Condition

When all scoped work and validation are complete, populate the Completion Report, set `status: review` and return to `moda_architect`. STOP; do not implement consumer tasks or publication.

## Implementation Notes

Read current database schema and actual repo validation commands before implementation. Define one compatible current-state storage contract while keeping Shopify native consent authority and Woo installed-source epoch policy distinct. Do not create additional current-state projection or event-wakeup tables. Preserve `docs/decisions/**/_index.md` until this documentation session is explicitly closed. Use canonical task launcher/worktree and completion evidence.

## Completion Report

### Status
Not Started — portable definition, not materialised.

### Files Changed
None.

### Work Completed
None.

### Validation Results
Not run; this is a task definition.

### Deviations
None.

### Assumptions
Current supplied schema is a point-in-time reference; verify real implementation branch.

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
