---
id: ARCH-045-DATABASE-002
architecture_id: ARCH-045
title: Implement shared WhatsApp consent, Woo evidence and privacy schema
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
  - ARCH-045-SHOPIFY-003
  - ARCH-045-SHOPIFY-004
  - ARCH-045-SHOPIFY-005
  - ARCH-046-API-001
  - ARCH-046-API-003
  - ARCH-046-API-004
  - ARCH-046-API-005
  - ARCH-046-BACKGROUND-001
  - ARCH-045-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-21
updated: 2026-10-21
---
# Implement shared WhatsApp consent, Woo evidence and privacy schema

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** At developer-create start, the task definition was present on `origin/main`, but no task-specific branch/worktree or execution claim existed. This invocation is preparing developer execution on the canonical task branch; no external definition is being materialised.

## Objective

Implement **one reviewed Database-owned schema change set** for ARCH-045 and ARCH-046: current WhatsApp recovery permission and permanent local no-contact on existing `commerce.CustomerPhone`, Woo consent-source settings on existing `woocommerce.WooCommerceInstallation`, a single immutable Woo consent-evidence history model, minimally necessary verified Woo identity/checkout linkage, and durable privacy erasure protection. This task absorbs all requirements previously defined in `ARCH-045-DATABASE-003` and `ARCH-046-DATABASE-001`. It never creates a consent-only `CheckoutRecovery` or an evidence-driven recovery worklist.

## Context

The inspected database has `commerce.Customer`, `commerce.CustomerPhone`, `woocommerce.WooCommerceInstallation` and shop-recipient reachability, but it lacks current WhatsApp recovery permission, the Woo source epoch and audit facts, a verified Woo guest-to-checkout/customer binding, and a reliable privacy-erasure fence. These were previously separated into three database tasks with explicit interfaces and are now consolidated under this task for one `moda_database` implementation/review. `ARCH-045-DATABASE-001` (obsolete admission-block enum), `ARCH-045-DATABASE-003` (standalone erasure schema) and `ARCH-046-DATABASE-001` (standalone Woo schema) remain **Superseded** and must not be materialised. The consolidated scope remains solely Prisma/schema/migrations and database validation; API, Shopify, Woo plugin, Background and privacy application logic stay with their owning repositories.

## Scope

**A. Shared exact-recipient current consent and negative-only safety fences**
- Extend `commerce.CustomerPhone` for `WHATSAPP_CHECKOUT_RECOVERY`: fail-closed current decision (`UNKNOWN`/not granted default), verified shop/customer/active canonical phone, authority/source and provider timestamp, verification time, monotonic revision and Woo provider/source epoch where applicable. Never inherit a grant across tenant, customer, changed/reassigned number or source epoch.
- Define active-phone uniqueness, indexes, rotation, conditional writes, and a short SQL read/fence for the current revision/recipient/source/no-contact. Phone matching is not verified customer identity; do not auto-merge two customers sharing a number.
- Persist shop/customer/recipient-specific STOP and merchant opt-out overrides and ordering so stale provider `SUBSCRIBED` events or old Woo retries cannot clear them. For an unbound authenticated shop/recipient STOP, reuse `whatsapp.WhatsAppRecipientReachability` (or demonstrably equivalent *existing* negative-only model) with permanent no-contact and revision distinct from temporary `suppressUntil`; no second positive-consent authority.

**B. Woo installation configuration, consent evidence and verified identity**
- Extend the existing `woocommerce.WooCommerceInstallation` with `NOT_CONFIGURED` default collection mode, optional explicitly approved external provider ID and monotonic source epoch/revision, without adding a settings table.
- Add **exactly one** immutable `WooWhatsAppConsentEvidence`-equivalent history model for verified `GRANT`/`REVOKE` decisions: shop/customer/active canonical phone/purpose, source/provider/epoch, disclosure wording/version/locale, unique `(shopId,eventId)`, canonical payload digest for same-ID/different-body rejection, revision, recorded timestamp and only verified checkout collection context. No claim, lease, ready, ack, retry, outbox or poller fields.
- Define the smallest verified Woo account-or-cryptographically-bound guest session → checkout → existing `commerce.Customer` link required for consent and future normal checkout reconciliation. Account/session/checkout must be installation/shop-scoped and indexed, with session rotation, login/logout and bounded retention. A separate non-consent identity-link entity is permitted **only** if existing models cannot safely represent the join; justify it; never join customer identity merely on phone/email or raw checkout key.

**C. Privacy erasure and race-proof protection for both platforms**
- Define the smallest persistent shop/platform-principal redaction/tombstone fence, with privacy-minimised lookup identity and monotonic cutoff, readable atomically by Shopify sync and Woo API writers. Reuse existing schema when sufficient; add a tombstone table only if necessary to prevent stale rehydration, not a new consent-state table.
- Support erasure of both current and historical `CustomerPhone.phone` and consent/contact PII; define which Woo immutable evidence fields are exported, deleted or pseudonymised under a verified erasure request and what minimal non-identifying integrity fields may legally remain. Privacy erasure overrides ordinary evidence immutability.
- Specify safe identity rebinding after erasure only for a genuinely new verified customer lifecycle, old-event retries, concurrency with consent sync and Woo grant/revoke, shop deletion and tenant isolation.

**D. Database delivery and testing**
- Produce a coherent additive Prisma schema/migration set (one or more ordered migrations if technically needed), disposable PostgreSQL fresh/upgrade, privacy/concurrency and rollback-compatibility tests. Keep provider/business workflows outside this Database-owned task. No Shopify-specific consent history table or consent-triggered recovery queue.

## Out of Scope

- No initial `CheckoutRecovery` for a missing grant, no consent-specific recovery-block enum, automatic checkout rescan, consent-triggered recovery job, evidence worklist or arbitrary consent expiry.
- No Shopify webhook/GraphQL caller, Woo API/controller, Woo checkout UI, Meta processor, commerce reconciliation service, merchant notice handler, privacy HTTP handler or external plugin adapter.
- No new current-consent table or merchant configuration table; Woo evidence history is **not** a current-consent source. Never add a second positive consent source for unbound STOP.
- No generalised customer identity replacement/refactor outside the specific durable schema/constraints needed here.

## Requirements

- New and migrated customer-phone consent defaults to UNKNOWN/not granted. Only the exact verified shop/customer/active canonical phone and selected provider/source may receive a current grant; reused/rotated numbers, ambiguous principals and old source epochs fail closed.
- The schema supports validated published Shared phone/Shopify ID compatibility vectors (`ARCH-045-SHARED-001` published by `ARCH-045-SHARED-002`) without imposing a country guess from an arbitrary locale. Node callers use the Shared implementation; Woo PHP tests consume identical golden vectors.
- The same short database transaction can fence shop, recipient, phone/current decision revision, source epoch, local permanent no-contact and privacy erasure. No provider/Redis network call occurs inside that transaction.
- A durable unbound shop/recipient STOP is negative-only, survives restarts and supersedes positive consent until a newer verified opt-in is authorised for that shop/recipient; other shops are unaffected.
- Woo consent source choice lives solely on existing `WooCommerceInstallation` with `NOT_CONFIGURED` default. `CustomerPhone` is the only current Woo permission record; exactly one append-only evidence table carries immutable ordinary decisions, replay digest and disclosure proof, not a background poller.
- The Woo account/guest identity link must be independently verifiable from the plugin/hosted API and reusable by later normal checkout reconciliation; no phone-only or email-only promotion to Customer identity.
- A privacy erasure removes active and ended phone/consent PII and prevents delayed Shopify sync, Woo retries and racing API writes from rehydrating the erased principal. Woo evidence erasure/pseudonymisation is permitted under the verified privacy contract while preserving lawful minimum integrity.
- Migration and indexes must preserve tenant isolation, old-schema compatibility (unless an explicitly approved pre-production breaking rollout is demonstrated), concurrent source switches/grant/revoke ordering, canonical recipient scope and no default grants.

## Work Items

- [ ] Inspect actual `commerce.Customer`, `commerce.CustomerPhone`, `woocommerce.WooCommerceInstallation` and `whatsapp.WhatsAppRecipientReachability` models plus migrations before choosing the minimal schema and index set.
- [ ] Add shared current WhatsApp recovery consent/source/revision and permanent contact restrictions to existing CustomerPhone; implement active-recipient constraints and safe phone rotation/migration defaults.
- [ ] Add permanent negative-only shop/recipient opt-out when no single CustomerPhone can be safely resolved; verify it is distinct from temporary reachability suppression.
- [ ] Add WooInstallation consent mode/provider ID/source epoch with default `NOT_CONFIGURED` and source-switch ABA protection.
- [ ] Add exactly one immutable Woo consent-evidence history model, `(shopId,eventId)` uniqueness, payload-digest replay contract, disclosure/source metadata, safe privacy redaction and no queue/worklist fields.
- [ ] Define the verified Woo account/guest session/checkout to Customer identity association, using existing schema where possible; justify any minimal non-consent link entity and retain no raw bearer/session token.
- [ ] Add/reuse a shop/platform-principal privacy erasure marker/fence plus historical CustomerPhone erasure semantics, with concurrency-safe lookup and lawful Woo evidence anonymisation rules.
- [ ] Produce additive ordered Prisma migration(s), document exact consumer field contracts and indexes for Shopify, Background, Woo API and plugin.
- [ ] Run disposable PostgreSQL fresh/upgrade/concurrency tests: UK local/`+44` equivalence with verified country context; ambiguous/malformed recipient; active-phone uniqueness and rotation; same phone different customers/shops; STOP and stale provider events; short SQL send fence; Woo source switch/epoch ABA and replay mismatch; guest session takeover/rotation and cross-shop checkoutKey reuse; privacy erase versus late sync/regrant and evidence anonymisation.
- [ ] Record precise validation results and any genuinely missing cross-repository contract rather than implementing API or worker logic here.

## Interfaces / Contracts

**Owner:** `moda_database`, repository `moda-interact-database`, serving ARCH-045 **and** ARCH-046.

- **Current authority/projection:** `commerce.CustomerPhone` — shared exact-recipient consent and no-contact revision (Shopify native provider is authoritative externally; Woo's current permission is owned locally under an active installation source).
- **Merchant selection:** existing `woocommerce.WooCommerceInstallation` — mode, approved provider and monotonic source epoch, used by `ARCH-046-API-003` and Woo Background readers.
- **Woo evidence:** one `WooWhatsAppConsentEvidence`-equivalent immutable ordinary fact model — written transactionally with current-state changes by `ARCH-046-API-001`, read for audit/privacy, **never polled to schedule a recovery**.
- **Woo identity:** verified shop/install-bound account/guest/checkout linkage to `commerce.Customer`; the API/plugin provide trusted authentication/session proof, not this database task.
- **Privacy:** shop/platform principal fence protects Shopify sync and Woo writes, historical phone erasure and Woo evidence privacy operations; Shopify and Woo privacy controllers remain service-owned.
- **Consumers:** ARCH-045-BACKGROUND-001/002/003/004/005; ARCH-045-SHOPIFY-003/004/005; ARCH-046-API-001/003/004/005; ARCH-046-BACKGROUND-001/002/004 and corresponding terminal system tests.
- **Published identity contract:** `ARCH-045-SHARED-001` (including the merged phone/Shopify principal helpers), released as `ARCH-045-SHARED-002`. No Shared Woo queue or consent-only recovery scheduler.

## Dependencies

None. This is the single foundational schema task for both architectures; its implementation must not wait for another ARCH-045/046 Database task.

## Enables

- `ARCH-045-BACKGROUND-001`
- `ARCH-045-BACKGROUND-003`
- `ARCH-045-BACKGROUND-005`
- `ARCH-045-SHOPIFY-003`
- `ARCH-045-SHOPIFY-004`
- `ARCH-045-SHOPIFY-005`
- `ARCH-046-API-001`
- `ARCH-046-API-003`
- `ARCH-046-API-004`
- `ARCH-046-API-005`
- `ARCH-046-BACKGROUND-001`
- `ARCH-045-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`


## Acceptance Criteria

- [ ] One current default-deny WhatsApp recovery consent representation on `commerce.CustomerPhone` shared by Shopify and Woo, with exact verified shop/customer/phone, source, epoch, revision and permanent no-contact precedence; no new positive current-consent table.
- [ ] E.164-equivalent canonicalisation with verified context and storage/index policy cannot cross-customer/tenant grant or fail open for invalid numbers, rotated recipient, reused number or ambiguous guest.
- [ ] Existing shop/recipient reachability can block permanent unbound STOP without becoming a separate consent authority or conflating temporary suppression.
- [ ] `WooCommerceInstallation` carries the only merchant consent-source setting, defaults to `NOT_CONFIGURED`, and source changes/ABA cannot preserve a stale grant as eligible.
- [ ] Exactly one immutable Woo consent-evidence table captures accepted grant/revoke, canonical event digest, source epoch, exact recipient and disclosure proof; same ID/different body is rejected; privacy erasure is explicitly handled; **no** claim/ack/worklist/polling fields.
- [ ] Woo account/guest principal and checkout association is shop/install/session scoped, safely rotated and readable by future approved normal checkout reconciliation without phone-based customer merging. Any extra identity-link entity is justified and minimised.
- [ ] Verified privacy erasure covers historical as well as current CustomerPhone contact/consent PII, prevents late provider/API rehydration and defines Woo evidence anonymisation/retention boundaries.
- [ ] Conditional/revision transactions resist stale Shopify sync, Woo grants after revoke, local STOP override, concurrent source switch and privacy erasure without provider or queue calls inside SQL transactions.
- [ ] Disposable PostgreSQL fresh/upgrade schema/migration, identity, replay, source, privacy and concurrency tests pass; migration/rollback and external consumer contract are documented.
- [ ] No missing-consent `CheckoutRecovery`, new consent wake-up queue, arbitrary consent timeout or separate current-consent projection is introduced.

## Validation

- [ ] Run repository-declared Prisma schema validate/generate and relevant database lint/checks (inspect actual scripts; do not invent commands).
- [ ] Run disposable PostgreSQL **fresh and upgrade** migration tests, including existing rows/default-deny and indexes/uniqueness.
- [ ] Run targeted database concurrency tests for exact recipient/identity, source epoch/decision ordering, Woo event replay/digest, unbound STOP, short SQL dispatch fence and erasure/replay races.
- [ ] Run Woo guest-session and shop-installation identity fixtures, privacy export/erase and immutable-evidence sanitisation checks.
- [ ] `git diff --check` (workspace/implementation worktree as applicable).

## Stop Condition

After the scoped shared/Shopify/Woo schema and migration Work Items, Acceptance Criteria and Validation are complete, populate Completion Report with launcher-resolved dedicated parent/implementation worktree and synchronization evidence, set `status: review`, return to `moda_architect`, and **STOP**. Do not implement API, Shopify, Woo or Background consumers within this task.

## Implementation Notes

This **single Database implementation task** deliberately absorbs the previous `ARCH-045-DATABASE-003` and `ARCH-046-DATABASE-001` scopes. Supersede those old definitions, **do not execute them**, and make consumers depend only on `ARCH-045-DATABASE-002`. Migrations may be appropriately split for safe deploy order but remain one reviewed Database outcome. Preserve identical current-state field ownership and one immutable Woo history table. `CommerceAuditEvent` is not assumed a valid customer-consent audit substitute. Privacy erasure must prevent later stale rehydration. Do not add recovery wakeup worklist/claims or consent-specific CheckoutRecovery state. Follow canonical `/moda-task` launcher and real repository validation scripts, preserve `docs/decisions/**/_index.md` until the developer closes the architecture documentation session.

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
