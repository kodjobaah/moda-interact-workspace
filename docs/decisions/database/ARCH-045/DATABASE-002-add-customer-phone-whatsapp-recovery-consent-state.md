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
status: review
priority: 20
executor: null
claimed_at: null
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
updated: 2026-10-22
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

- [x] Reconcile the existing unmerged Attempt 1 Prisma schema and migration to the **one-new-table/one-existing-table-extension** contract, removing all rejected models/columns/enums/triggers.
- [x] Define shared CustomerPhone default-UNKNOWN consent, canonical recipient, source/time/revision and customer/merchant opt-out precedence; add focused indexes/constraints.
- [x] Add `commerce.WhatsAppConsentEvidence` with tenant-safe foreign keys, immutable GRANT/REVOKE facts, consent wording, unique event ID and conflict detection.
- [x] Cover one/no/ambiguous merchant-scoped canonical-phone matches, no cross-shop reuse, no grant inferred from lookup, changed phone, STOP and concurrent consent transitions in PostgreSQL tests.
- [x] Verify no DB changes to Customer, WooCommerceInstallation or WhatsAppRecipientReachability and no Woo checkout-identity/privacy-erasure table remains in the unmerged schema.
- [x] Validate fresh/upgrade migration and schema/test scripts declared by `moda-interact-database`, plus `git diff --check`; report actual commands/results and reconciled changed files in the existing Attempt 1 Completion Report.

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

- [x] The unmerged migration creates exactly **one** new table (`commerce.WhatsAppConsentEvidence`) and extends exactly **one** existing persisted model (`commerce.CustomerPhone`) for consent; Customer, WooCommerceInstallation and WhatsAppRecipientReachability have no new persisted consent columns.
- [x] Default unknown; active canonical recipient lookup is shop-scoped through existing Customer and never automatically grants consent. One safe phone match can be reused; ambiguous duplicate matches deny permission rather than merging customers.
- [x] Only authenticated legitimate Shopify-native or Woo Moda-checkbox GRANT can authorise a customer/phone; revoke, merchant restriction and customer STOP are reflected monotonically and cannot be bypassed by stale decisions.
- [x] Each accepted Woo grant/revoke creates one immutable matching `WhatsAppConsentEvidence` fact atomically with current CustomerPhone, and identical `(shopId,eventId)` replays are idempotent while conflicting replays fail.
- [x] No `WooCheckoutCustomerIdentity`, `CustomerPrivacyErasureFence`, installation consent mode/provider fields, additional reachability columns, external consent sources or erasure-specific mutations remain in the revised Prisma schema/migration.
- [x] Fresh and upgrade PostgreSQL checks, race/idempotency tests, model/migration validation and `git diff --check` pass with actual evidence.
- [x] No grant/withdraw event creates CheckoutRecovery, triggers extra reconciliation or consumes usage credits.

## Validation

- [x] Run the database package's real Prisma validation/generation and schema contract commands, inspecting available scripts first.
- [x] Run disposable PostgreSQL fresh+upgrade migration and test the exact table/schema name plus absence of removed structures.
- [x] Exercise shop-scoped phone lookup (one/none/ambiguous), UK-number canonical variants, default deny, authenticated grant/revoke/regrant, changed number, STOP/merchant suppression, duplicate ID/conflicting digest and concurrent ordering.
- [x] Verify no modifications to unrelated models, no Redis/provider network calls in SQL transactions, and `git diff --check`.
- [x] Record validation evidence in the already-claimed Attempt 1 Completion Report; return for review, not unilateral completion.

## Stop Condition

After all revised Work Items, Acceptance Criteria and validation pass, update the **existing Attempt 1** Completion Report, set the task to `review`, return it for the authorised review/developer completion decision, and STOP. No separate rework task, no opportunistic Woo or API implementation and no domain `_index.md` edits.

## Implementation Notes

The developer is permitted to amend the in-progress task because its implementation is unmerged. The current snapshot's task report still says `Files Changed: None` despite unmerged schema/migration/test files being present; reconcile the actual branch diff and report accurately before review. Do not infer a Git commit/push, task acceptance or test pass from this snapshot. Keep the existing developer claim/attempt and any durable prior review intact. The change removes speculative persistent Woo identity, source selection and erasure structures while preserving tenant-scoped phone matching, explicit opt-in, evidence history and durable customer-phone opt-outs. The ARCH-045 Shared publication remains separate; this task does not implement Shared helpers or API endpoints.

## Completion Report

### Status

Ready for Review — developer-owned Attempt 1 passed review. The simplified consent implementation and disposable PostgreSQL suites passed. The final database implementation was committed and pushed at `e0ab833` (`feat(database)`), with a clean implementation worktree. Explicit developer completion remains pending.

### Files Changed

The final database implementation on `task/ARCH-045-DATABASE-002` is committed as `e0ab833` (`feat(database)`) and matches `origin/task/ARCH-045-DATABASE-002`. It covers these six files:

- `package.json` — ARCH-045 consent validation scripts.
- `prisma/schema.prisma` — `CustomerPhone` current consent and one `commerce.WhatsAppConsentEvidence` model.
- `prisma/migrations/20261021170000_arch045_shared_woo_consent_privacy/migration.sql` — revised, still-unmerged migration and database guards.
- `docs/ARCH-045-046-consent-database-contract.md` — tenant and consumer boundary, canonical phone and evidence contract.
- `scripts/test-arch045-consent-postgres.mjs` — disposable fresh/upgrade database fixtures and negative/race tests.
- `scripts/validate-arch045-consent-schema.mjs` — static schema-contract validation.

This handoff patch changes only the current task `.md` file in the parent workspace. No `docs/decisions/**/_index.md`, parent architecture or other task definition is modified.

### Work Completed

- Reduced the in-flight schema to current permission on existing `commerce.CustomerPhone` and **one new table**: append-only `commerce.WhatsAppConsentEvidence`. Removed the earlier consent-source configuration, Woo checkout-identity, privacy-erasure and reachability modifications from the unmerged schema/migration.
- Implemented `UNKNOWN` default, canonical digits-only international recipient, Shopify-native/Woo-checkbox provenance, consent revision/sequence, source/decision times and strong `CUSTOMER_STOP` versus merchant suppression ordering.
- Added tenant-safe relationships and indexes. Existing `Customer` and installation tables receive no new persisted consent/provider/privacy columns; phone lookup remains shop-scoped and cannot mint a grant.
- Enforced matching Woo evidence with the current phone decision in the same transaction, immutable history, `(shopId,eventId)` uniqueness, payload conflict rejection, revision ordering and active-installation checks.
- Kept checkout reconciliation, WhatsApp dispatch, billing and usage outside the database consent write path, with no new recovery/scheduler/credit state.
- Updated the SQL fixture from `commerce.UsageEvent` to the actual `billing.UsageEvent` table after the first simplified-schema run; this was a test-only correction.

### Validation Results

**Developer terminal evidence, 2026-10-22** (the latest upload validates the revised schema after the test-fixture correction):

- `npm run validate` — **PASS** (`prisma validate --schema prisma/schema.prisma`), in earlier 22 October log, after simplification.
- `npm run prisma:generate` — **PASS** (`prisma generate --schema prisma/schema.prisma`), earlier 22 October log.
- `npm run test:arch045-consent-schema` — **PASS**, earlier 22 October log; one evidence table, default deny and excluded structures verified.
- `npm run test:arch045-consent:postgres:fresh` — **PASS**; 59 migrations, all focused fixture assertions.
- `npm run test:arch045-consent:postgres:upgrade` — **PASS**; 59 migrations, all focused fixture assertions.
- `npm run lint` — **PASS** (`eslint . --max-warnings=0`) in the latest log.
- Fresh and upgrade test sections each report passing one-table/default-deny/canonical-number checks; shop isolation and ambiguous phone lookup; atomic Woo GRANT/REVOKE/regrant, immutable evidence and replay; STOP precedence and installation lifecycle; concurrent revision ordering; changed phone and no recovery/credit side effects.
- Logged SQL `ERROR:` lines precede passing assertions and represent intentional rejected writes, not test failures. PostgreSQL identifier-truncation notices originate from pre-existing migrations; both test runs finish `PASS`.
- **Final implementation Git evidence (2026-10-22):** `git diff --check` produced no errors, `git status --short` was empty, and `git log -1 --oneline` reported `e0ab833 (HEAD -> task/ARCH-045-DATABASE-002, origin/task/ARCH-045-DATABASE-002) feat(database)`. `git branch --show-current` reported `task/ARCH-045-DATABASE-002`. The developer's `pwd` identified `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-045-DATABASE-002`, consistent with the dedicated implementation worktree listed previously.
- **Review evidence verified:** the canonical launcher resolved the parent and implementation worktrees; the implementation branch is clean and synchronized, and the parent branch is clean and synchronized at review publication.

### Deviations

None in the final database scope. The pre-merge migration was revised in place, as explicitly instructed by the 21 October simplification. A test-only UsageEvent schema-reference fix was needed for full integration-suite completion.

### Assumptions

The migration remains **unmerged** and the revised version is not applied to persistent production state; developer Docker test containers are disposable. If a persistent database has already recorded the earlier migration checksum, resolve that deployment history explicitly rather than applying the revised file over an existing persistent installation.

### Unresolved Issues

No outstanding database test failure or uncommitted implementation amendment is shown. The accepted review record is being committed and pushed in the parent `task/ARCH-045-DATABASE-002` branch. Explicit developer completion remains the only lifecycle follow-up.

### Architectural Concerns

The database enforces source/platform consistency, an active Woo installation, matching auditable evidence and STOP precedence. It **cannot authenticate an HTTP checkout submission or Shopify API observation by itself**; verified source/session identity and country-aware phone normalisation remain with the owning API/Shopify/Woo/Shared consumers per the task's `Interfaces / Contracts`. These are not additional database tables or a reason to restore the withdrawn identity/erasure design.

## Architect Review

### Review Status
Passed/Accepted — developer Attempt 1 reviewed and reconciled. Explicit developer completion remains pending because `completion_mode: developer`.

### Review Notes
- The implementation branch is clean at `e0ab833` and synchronized with `origin/task/ARCH-045-DATABASE-002` (`0 0` parity); `git diff --check` passes.
- `npm run validate`, `npm run test:arch045-consent-schema`, and `npm run lint` pass.
- Disposable PostgreSQL fresh and upgrade suites pass. Their logged SQL `ERROR:` lines are expected negative assertions; the suites report passing checks for schema boundaries, default deny, tenant isolation, atomic grant/revoke/regrant, immutable evidence, replay conflict detection, STOP precedence, installation lifecycle, concurrent revision ordering, and recipient rotation.
- The canonical launcher resolves the required parent and implementation worktrees, and the parent task branch is synchronized. No merge to `main` is required or performed.

### Reviewed Files
- `package.json`
- `prisma/schema.prisma`
- `prisma/migrations/20261021170000_arch045_shared_woo_consent_privacy/migration.sql`
- `scripts/test-arch045-consent-postgres.mjs`
- `scripts/validate-arch045-consent-schema.mjs`
- `docs/ARCH-045-046-consent-database-contract.md`

### Validation Reviewed
- `npm run validate` — PASS
- `npm run test:arch045-consent-schema` — PASS
- `npm run test:arch045-consent:postgres:fresh` — PASS
- `npm run test:arch045-consent:postgres:upgrade` — PASS
- `npm run lint` — PASS
- `git diff --check` — PASS

### Architecture Conformance
Accepted for the stated ARCH-045 consent foundation: one new `commerce.WhatsAppConsentEvidence` table, consent fields only on existing `commerce.CustomerPhone`, default-deny and tenant-safe ordering enforced, and excluded identity/privacy/reachability structures absent.

### Follow-up
Developer must explicitly invoke `/moda_developer_update ARCH-045-DATABASE-002 complete` to authorize completion. Downstream dependency-frontier reconciliation follows that explicit completion.

## Developer Execution Ownership Amendment — 2026-10-21

The developer explicitly invoked `/moda_developer_create ARCH-045-DATABASE-002` for this agent-owned task. Execution and completion authority are transferred to the developer; `assigned_agent: moda_database`, repository ownership, scope, dependencies and acceptance criteria are unchanged. Canonical launcher preparation will record the developer attempt after worktree synchronization and dependency verification.
