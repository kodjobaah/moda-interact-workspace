---
id: ARCH-045-DATABASE-002
architecture_id: ARCH-045
title: Add shared customer-phone consent and WhatsApp consent evidence
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 20
executor: developer
claimed_at: 2026-10-21T18:04:20Z
attempt: 1
depends_on: []
enables:
  - ARCH-045-BACKGROUND-001
  - ARCH-045-BACKGROUND-003
  - ARCH-045-BACKGROUND-005
  - ARCH-045-SHOPIFY-005
  - ARCH-046-API-001
  - ARCH-046-API-005
  - ARCH-046-BACKGROUND-001
  - ARCH-045-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-21
updated: 2026-10-21
---
# Add shared customer-phone consent and WhatsApp consent evidence

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`

**In-flight architectural correction, 2026-10-21:** Attempt 1 is developer-claimed and its Prisma migration/tests remain **unmerged**. Amend the **same task and existing unmerged migration** before review; retain `status: in_progress`, `execution_mode: developer`, `completion_mode: developer`, `executor`, `claimed_at`, `attempt: 1` and all history. The agreed scope is **one new `commerce.WhatsAppConsentEvidence` model/table plus consent-related fields on existing `commerce.CustomerPhone`**. No other tables or existing-model data columns are authorised by this consent initiative. This amendment neither implements nor accepts the task.

## Objective

Implement the smallest shared WhatsApp checkout-recovery consent schema for Shopify and WooCommerce: **current permission on existing `commerce.CustomerPhone`**, plus **one new append-only `commerce.WhatsAppConsentEvidence` audit table** for grants/withdrawals collected by Moda's WooCommerce checkout. The existing `commerce.Customer` and its `shopId` supply merchant ownership; resolve Woo customers by **merchant-scoped canonical phone** where safe. Consent is never granted merely because a number matches.

## Context

This task consolidates the consent portions of superseded `ARCH-046-DATABASE-001`. The earlier Attempt 1 schema/migration introduced separate `WooCheckoutCustomerIdentity`, `CustomerPrivacyErasureFence`, external-provider/installation settings, new `Customer` principal fields, and changes to `WhatsAppRecipientReachability`. Those are **not** part of the agreed consent scope. Erasure and broader privacy export/redaction belong to a separate future architecture; they are not requirements of this task. Existing WhatsApp reachability remains a delivery concern with its existing schema. Shopify continues to check Shopify's native WhatsApp marketing consent; Woo uses only Moda's optional checkout checkbox and documented, authorised manual merchant *suppression* (not merchant-created consent).

## Scope

**A. Extend existing `commerce.CustomerPhone`**

- Store one current checkout-recovery WhatsApp consent decision, default `UNKNOWN` (not granted); source `SHOPIFY_NATIVE` or `WOO_MODA_CHECKBOX`; current canonical phone; timestamps needed to distinguish a current provider observation/accepted Woo decision; and monotonic revision/ordering needed to reject stale grant/revoke writes.
- Store local no-contact/opt-out state on the **same** CustomerPhone, distinguishing a customer STOP from a merchant's recovery suppression. A merchant may remove only its own suppression, subject to an already valid grant and any stronger customer STOP; merchant selection cannot create a grant.
- Use a canonical international phone representation with explicit country context when required. Match by `Customer.shopId` and the currently active `CustomerPhone` canonical phone; use **the existing `Customer`**, not a new identity table or principal digest. If one safe active merchant-scoped phone match exists, reuse it; if none exists, create the existing Customer/CustomerPhone records through the owning API/Background workflow; if several matches are ambiguous, fail closed. Do not merge two existing Customer rows merely because their phone matches.
- A phone lookup may locate a customer but **must not change `UNKNOWN`/`REVOKED` to `GRANTED`**. Only a verified Shopify-native decision or a deliberate authenticated Moda-checkbox action can grant consent. A changed number must not automatically reuse the former number's consent; one merchant's record must never match another merchant's number.
- Add only justified enum values, indexes and constraints supporting exact matching, safe concurrent updates and default-deny. `CustomerPhone` is the only current permission representation; no pending-consent checkout state, recovery block enum or consent-triggered worklist.

**B. Add exactly one `commerce.WhatsAppConsentEvidence` table**

- Use the canonical Prisma model and PostgreSQL table name **`WhatsAppConsentEvidence`** in schema `commerce`, not `WooWhatsAppConsentEvidence` in schema `woocommerce`.
- Record immutable Woo Moda-checkbox GRANT/REVOKE decisions with `shopId`, existing `customerId`/`customerPhoneId`, authenticated installation reference where useful, unique `(shopId,eventId)`, conflict-detecting payload digest, accepted consent decision/revision, purpose, disclosure version/text/locale as appropriate and recorded timestamp. Keep enough evidence to demonstrate the actual opt-in/withdrawal and idempotent retries without storing raw session bearer tokens.
- No current-consent duplication in the evidence table, no evidence-driven polling, claim/ack/retry state, provider modes, source-epoch/provider IDs or consent expiry. Consumer workflows read `CustomerPhone`, not evidence history, to determine present permission.
- Model tenant-safe relationships using existing `Shop`, `Customer`, `CustomerPhone` and `WooCommerceInstallation` keys. Prisma relation fields needed solely for a new evidence foreign key are acceptable; **do not add new persisted columns** to those existing tables other than CustomerPhone consent fields.

**C. Explicit exclusions from the unmerged implementation**

- **No** `WooCheckoutCustomerIdentity` table, `WooCheckoutPrincipalKind`, `CustomerPrivacyErasureFence` table or privacy-fence principal digest/revision columns on Customer. No `verifiedPrincipalDigest`, `verifiedPrincipalPlatform`, `privacyErasedAt` or `privacyRevision` additions from this task.
- **No** new consent fields on `WooCommerceInstallation`; no `WooWhatsAppConsentCollectionMode`, external-provider ID, source epoch/revision or source-selection configuration.
- **No** new columns or changes to `whatsapp.WhatsAppRecipientReachability`. Its existing delivery suppression is separate from consent; the positive current permission and identifiable STOP live on CustomerPhone.
- **No** erasure-specific nullable conversion of existing `CustomerPhone.phone`, erasure table, erasure triggers, permanent recollection ban or privacy export/erase tests in this task.
- **No** additional customer/session identity table. The Woo hosted API and plugin authenticate the installation and origin of a deliberate checkout checkbox decision at their **runtime boundary**, then resolve/create `Customer` by `(shopId, canonicalPhone)` with explicit ambiguity handling.

**D. Correct the unmerged migration and tests**

- Revise the existing Attempt 1 `prisma/schema.prisma`, `prisma/migrations/20261021170000_arch045_shared_woo_consent_privacy/migration.sql` and `scripts/test-arch045-consent-postgres.mjs` **in place**. Do not introduce a compensating migration just to remove unmerged code. If a persistent database has applied the unmerged migration, record the actual migration-repair/reset strategy rather than silently editing applied history.
- Remove obsolete models/enums/columns/triggers and test fixtures; confirm the single evidence model/table uses the intended `commerce` schema and name. Validate fresh and upgrade migration paths, race safety, cross-shop isolation, duplicate event-ID conflict, grant→withdraw→regrant ordering, unknown-by-default, and no side effects on CheckoutRecovery, queue, credit or messaging.

## Out of Scope

- Shopify/WooCommerce HTTP endpoints, consent collection UI, recovery orchestration, WhatsApp send logic, third-party plugin/CMP adapters, merchant contact-management UI, or Shared package publication.
- General customer privacy export, erasure, redaction, anti-recollection fence, customer identity infrastructure, delivery reachability redesign or installation consent-provider configuration.
- A new recovery when consent is missing, a consent-driven checkout wake-up, a synthetic 72-hour consent expiry or billing changes.

## Requirements

- Default deny: a newly created or migrated CustomerPhone never starts `GRANTED` based on existing phone information.
- Match only within the authenticated merchant (`Customer.shopId`) and an exact, currently active canonical phone. Reuse **one** unambiguous existing customer; otherwise create a new ordinary customer/phone if none exists or reject ambiguous duplicates safely. No cross-tenant lookup or mass customer merge.
- Identity lookup and permission verification are separate: a matched customer is **not proof** that this shopper checked the checkbox. Only verified Shopify-native state or a deliberate authenticated Woo checkout GRANT may update permission positively. Stale decisions and local customer STOP must not be overridden.
- The Woo evidence table is immutable audit history and idempotency protection, not current authority or a recovery scheduler. Its name is `commerce.WhatsAppConsentEvidence` for cross-platform vocabulary even though v1 evidence writers are WooCommerce-specific.
- No schema/logic for external providers, new Woo identity tables, privacy erasure fences, modified reachability, or merchant installation settings is introduced.
- All changes are tenant-scoped, safe under concurrent writes and compatible with the existing `Customer`/`CustomerPhone` relations. No provider or Redis network calls occur inside SQL transactions.

## Work Items

- [ ] Reconcile the existing unmerged Attempt 1 Prisma schema and migration to the **one-new-table/one-existing-table-extension** contract, removing all rejected models/columns/enums/triggers.
- [ ] Define shared CustomerPhone default-UNKNOWN consent, canonical recipient, source/time/revision and customer/merchant opt-out precedence; add focused indexes/constraints.
- [ ] Add `commerce.WhatsAppConsentEvidence` with tenant-safe foreign keys, immutable GRANT/REVOKE facts, consent wording, unique event ID and conflict detection.
- [ ] Cover one/no/ambiguous merchant-scoped canonical-phone matches, no cross-shop reuse, no grant inferred from lookup, changed phone, STOP and concurrent consent transitions in PostgreSQL tests.
- [ ] Verify no DB changes to Customer, WooCommerceInstallation or WhatsAppRecipientReachability and no Woo checkout-identity/privacy-erasure table remains in the unmerged schema.
- [ ] Validate fresh/upgrade migration and schema/test scripts declared by `moda-interact-database`, plus `git diff --check`; report actual commands/results and reconciled changed files in the existing Attempt 1 Completion Report.

## Interfaces / Contracts

- **Owner:** `moda_database`, `ARCH-045-DATABASE-002`, sole Database implementation foundation shared by ARCH-045 and ARCH-046.
- **Current state:** `commerce.CustomerPhone`, joined to existing `commerce.Customer.shopId`, canonical number, default-deny permission, source, timestamps/revision and local no-contact.
- **Evidence:** single new `commerce.WhatsAppConsentEvidence` historical Woo opt-in/withdrawal record; no worklist/scheduler.
- **Woo installation:** unchanged existing `woocommerce.WooCommerceInstallation` identity/authentication lifecycle; no source mode or consent configuration.
- **Consumer-owned runtime identity:** `ARCH-046-API-001` resolves existing Customer/CustomerPhone by authenticated merchant + canonical phone and requires a deliberate verified consent action before positive write. `ARCH-046-WOOCOMMERCE-002` transmits that action securely. Neither requires a persisted Woo identity-link table.
- **Shopify:** Shopify remains the native consent authority; `ARCH-045-BACKGROUND-001/003` update/read current CustomerPhone via the published `ARCH-045-SHARED-001/002` contracts.

## Dependencies

None. This remains the already claimed Attempt 1 shared Database task.

## Enables

- `ARCH-045-BACKGROUND-001`
- `ARCH-045-BACKGROUND-003`
- `ARCH-045-BACKGROUND-005`
- `ARCH-045-SHOPIFY-005`
- `ARCH-046-API-001`
- `ARCH-046-API-005`
- `ARCH-046-BACKGROUND-001`
- `ARCH-045-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] The unmerged migration creates exactly **one** new table (`commerce.WhatsAppConsentEvidence`) and extends exactly **one** existing persisted model (`commerce.CustomerPhone`) for consent; Customer, WooCommerceInstallation and WhatsAppRecipientReachability have no new persisted consent columns.
- [ ] Default unknown; active canonical recipient lookup is shop-scoped through existing Customer and never automatically grants consent. One safe phone match can be reused; ambiguous duplicate matches deny permission rather than merging customers.
- [ ] Only authenticated legitimate Shopify-native or Woo Moda-checkbox GRANT can authorise a customer/phone; revoke, merchant restriction and customer STOP are reflected monotonically and cannot be bypassed by stale decisions.
- [ ] Each accepted Woo grant/revoke creates one immutable matching `WhatsAppConsentEvidence` fact atomically with current CustomerPhone, and identical `(shopId,eventId)` replays are idempotent while conflicting replays fail.
- [ ] No `WooCheckoutCustomerIdentity`, `CustomerPrivacyErasureFence`, installation consent mode/provider fields, additional reachability columns, external consent sources or erasure-specific mutations remain in the revised Prisma schema/migration.
- [ ] Fresh and upgrade PostgreSQL checks, race/idempotency tests, model/migration validation and `git diff --check` pass with actual evidence.
- [ ] No grant/withdraw event creates CheckoutRecovery, triggers extra reconciliation or consumes usage credits.

## Validation

- [ ] Run the database package's real Prisma validation/generation and schema contract commands, inspecting available scripts first.
- [ ] Run disposable PostgreSQL fresh+upgrade migration and test the exact table/schema name plus absence of removed structures.
- [ ] Exercise shop-scoped phone lookup (one/none/ambiguous), UK-number canonical variants, default deny, authenticated grant/revoke/regrant, changed number, STOP/merchant suppression, duplicate ID/conflicting digest and concurrent ordering.
- [ ] Verify no modifications to unrelated models, no Redis/provider network calls in SQL transactions, and `git diff --check`.
- [ ] Record validation evidence in the already-claimed Attempt 1 Completion Report; return for review, not unilateral completion.

## Stop Condition

After all revised Work Items, Acceptance Criteria and validation pass, update the **existing Attempt 1** Completion Report, set the task to `review`, return it for the authorised review/developer completion decision, and STOP. No separate rework task, no opportunistic Woo or API implementation and no domain `_index.md` edits.

## Implementation Notes

The developer is permitted to amend the in-progress task because its implementation is unmerged. The current snapshot's task report still says `Files Changed: None` despite unmerged schema/migration/test files being present; reconcile the actual branch diff and report accurately before review. Do not infer a Git commit/push, task acceptance or test pass from this snapshot. Keep the existing developer claim/attempt and any durable prior review intact. The change removes speculative persistent Woo identity, source selection and erasure structures while preserving tenant-scoped phone matching, explicit opt-in, evidence history and durable customer-phone opt-outs. The ARCH-045 Shared publication remains separate; this task does not implement Shared helpers or API endpoints.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-21T18:04:20Z. Attempt 0 review history is preserved below.

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

## Developer Execution Ownership Amendment — 2026-10-21

The developer explicitly invoked `/moda_developer_create ARCH-045-DATABASE-002` for this agent-owned task. Execution and completion authority are transferred to the developer; `assigned_agent: moda_database`, repository ownership, scope, dependencies and acceptance criteria are unchanged. Canonical launcher preparation will record the developer attempt after worktree synchronization and dependency verification.
