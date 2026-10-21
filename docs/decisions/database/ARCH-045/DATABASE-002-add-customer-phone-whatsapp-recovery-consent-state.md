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
  - ARCH-045-DATABASE-003
  - ARCH-045-SHOPIFY-004
  - ARCH-045-BACKGROUND-005
  - ARCH-045-SHOPIFY-005
  - ARCH-046-API-005
  - ARCH-046-BACKGROUND-001
  - ARCH-046-API-001
  - ARCH-045-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
  - ARCH-046-SYSTEM-TEST-001
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

- **C1/C2:** Do not promote or merge `commerce.Customer` identity merely on phone equality. Store the exact canonical recipient with a verified shop-owned customer binding; ambiguous or unparseable numbers remain non-granted, never copied between people, shops, previous phone intervals or Woo/Shopify authority domains.
- Use the published Shared canonical phone identity contract (`ARCH-045-SHARED-003` and release `SHARED-002`) for Node writers/readers; country context must be explicit and verified, not inferred from an arbitrary shop locale. Store/compare the E.164-equivalent full number; the provider-specific digits-only address is a separate outbound adapter.
- Define and index one *active* canonical recipient per customer/purpose as required by actual data, with conditional writes and concurrency-safe phone rotation. If another verified customer has the same number, do not inherit their consent or use ambiguous phone lookup as proof of ownership.
- **C6/H4/H5:** Persist a shop/customer/phone-specific durable no-contact override and monotonic decision revision (source, actor/reason, observed timestamp/evidence reference, non-sensitive audit metadata). STOP/merchant opt-out denies all proactive sends even if the current Shopify projection says `SUBSCRIBED`; only a verified affirmative opt-in newer than the local opt-out and for that exact customer/phone/purpose may clear the override. Source switches, phone rotations and stale webhook retries cannot clear it.
- Support fast short-transaction checks on active recipient, source epoch, current decision and no-contact revision; design a database predicate/index needed by the final outbound fence without introducing network I/O or a second current-consent table.

- **Unbound STOP:** When authenticated Meta ingress proves shop and canonical recipient but cannot safely identify one CustomerPhone, extend existing `whatsapp.WhatsAppRecipientReachability` (or a demonstrably equivalent *existing* shop-recipient record) with a **non-expiring no-contact flag/revision**, separate from its temporary `suppressUntil` semantics. This is a negative shop/recipient safety fence only, not a second consent authority or new table. It is cleared only by verified newer affirmative permission for that recipient/shop; telephone reassignment remains fail-closed.

## Work Items

- [ ] Inspect existing CustomerPhone identity/history invariants, implement minimally sufficient additive Prisma fields and migration.
- [ ] Add focused PostgreSQL fresh/upgrade, null/default-deny, scope, exact-phone, stale-version and source-epoch tests.
- [ ] Record schema field names and ownership for both ARCH-045/046 consumer tasks.

- [ ] Implement/test canonical active-phone uniqueness and safe migration of legacy rows (no automatic grant or identity merge from historical phone-only data).
- [ ] Add the current no-contact override and monotonic revision/fence fields to the same CustomerPhone model, including safe regrant semantics; test concurrent source rotation/revocation and exact-recipient SQL predicate.

- [ ] Cover permanent shop-recipient opt-out and short SQL fence queries even where no verified CustomerPhone exists; do not overload time-based reachability suppression as an infinite timestamp.

## Interfaces / Contracts

**Owner:** `moda_database`. **Schema:** `commerce.CustomerPhone` current WhatsApp recovery permission, purpose/source/provider timestamp and Woo epoch binding. **Writers:** ARCH-045-BACKGROUND-001/003 for verified Shopify state; ARCH-046-API-001 for verified Woo grant/revoke. **Readers:** ARCH-045-BACKGROUND-001/002/004 and ARCH-046-BACKGROUND-001/002/004. **Separate evidence:** ARCH-046-DATABASE-001 only. No new Shared Redis queue or consent-driven recovery worklist.

- `ARCH-045-SHARED-003` owns the reusable Node phone/Shopify ID canonicalisation contract, published via `ARCH-045-SHARED-002`; PHP must pass matching golden vectors. `ARCH-045-BACKGROUND-005`, Shopify merchant opt-out and Woo authenticated merchant opt-out write the same local no-contact fields; no extra projection table.

## Dependencies

None

## Enables

- `ARCH-045-BACKGROUND-001`
- `ARCH-045-BACKGROUND-003`
- `ARCH-046-DATABASE-001`
- `ARCH-045-DATABASE-003`
- `ARCH-045-SHOPIFY-004`
- `ARCH-045-BACKGROUND-005`
- `ARCH-045-SHOPIFY-005`
- `ARCH-046-API-005`
- `ARCH-046-BACKGROUND-001`
- `ARCH-046-API-001`
- `ARCH-045-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`
- `ARCH-046-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] One current decision lives on CustomerPhone with safe unknown default and exact customer/phone scope.
- [ ] Both platforms can consume the schema without duplicating current consent tables; Shopify source not overwritten by Woo events.
- [ ] Out-of-order/old source epochs cannot convert a revoked or unknown current decision into an eligible grant.
- [ ] Disposable PostgreSQL migration/schema tests pass; no new CheckoutRecovery/notice/evidence-worklist table or consent expiry.

- [ ] Two customers sharing a phone cannot inherit each other's grant; UK national/international equivalents normalise only with justified country context; malformed/ambiguous/rotated phones deny outreach.
- [ ] A newer STOP or merchant no-contact override wins over a stale Shopify SUBSCRIBED sync, Woo grant replay, and all proactive sends; an independently verified newer explicit grant is needed to restore eligibility.
- [ ] Current-state/revision fence is viable under a short database transaction without provider or queue access.

- [ ] A STOP for a shop-recipient with no safely matched Customer still denies all proactive outreach to that shop-recipient until new verified permission; another shop is unaffected.

## Validation

- [ ] Repository-declared Prisma validate/generate, disposable PostgreSQL migration fresh/upgrade tests, schema-focused tests and `git diff --check`.

- [ ] Disposable PostgreSQL concurrency and migration fixtures: local/`+44` conversion, ambiguity, shared phone across customer IDs, double-active race, rotation, STOP precedence, source-epoch ABA and send-fence read.

- [ ] Same recipient in two shops, unresolved guest/no Customer, recent STOP then older SUBSCRIBED, and later verifiable opt-in test.

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
