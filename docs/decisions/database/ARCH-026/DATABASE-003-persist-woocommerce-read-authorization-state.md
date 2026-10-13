---
id: ARCH-026-DATABASE-003
architecture_id: ARCH-026
title: Persist tenant-scoped WooCommerce read authorisation state
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-026-DATABASE-001
enables:
  - ARCH-026-API-007
created: 2026-10-10
updated: 2026-10-13
---

# Persist tenant-scoped WooCommerce read authorisation state

## Architecture

Architecture ID: `ARCH-026`.

Architecture document: `docs/architecture/ARCH-026-woocommerce-application-foundation.md`.

Coordinator: `moda_architect`.

## Objective

Introduce durable, shop-bound state for one active WooCommerce **read-only REST API grant** and its short-lived authorisation attempts, without changing Moda installation authentication.

## Context

The canonical `woocommerce.WooCommerceInstallation` currently stores a digest of the credential presented **from the plugin to Moda**. That digest is not usable for Moda-to-WooCommerce REST reads. WooCommerce's native `/wc-auth/v1/authorize` flow delivers a separate consumer key and secret through a callback; those need an encrypted-at-rest lifecycle tied to the verified installation. Existing `commerce.CommerceExternalCredential` rows belong to a platform-admin-managed connection/revision/audit workflow (`updatedByAdminId` is required), so they must not be silently repurposed for merchant-granted Woo credentials.

## Scope

`moda-interact-database` only:

- Add a provider-owned grant/credential model in PostgreSQL schema `woocommerce`, bound to `WooCommerceInstallation` and its authoritative `Shop` through immutable foreign keys.
- Add a provider-owned short-lived authorisation-attempt model with a one-way digest of the opaque callback token, expiry, single-consumption lifecycle and installation credential version/generation snapshot.
- Add the necessary Prisma relations, uniqueness, lifecycle constraints and bounded indexes, and a migration with fresh and existing-schema rehearsals.

## Out of Scope

- Raw credential issuance, callback HTTP handling, encryption implementation or application key management.
- Writing credentials to WordPress options, browser state, Commerce's admin-managed external credential table, Redis or logs.
- Shopify token or access-scope changes, billing, recovery or Commerce tool execution.
- Deleting or replacing existing Woo installation credentials.

## Requirements

1. **Separation:** Retain `WooCommerceInstallation.credentialDigest` and the existing `Shop -> WooCommerceInstallation` relationship unchanged. The new credential record is specifically for outbound `wc/v3` REST reads. One installation has at most one currently selected grant; expired/revoked grant metadata may be retained as bounded history only if required for idempotency and audit.
2. **Ownership:** Bind credentials and attempts to a canonical Woo installation. Use database FKs and uniqueness so a grant cannot be transferred to another tenant or mistaken for a Shopify Shop. Define deliberate cascade/retention behaviour on installation deletion.
3. **Encrypted envelope:** Persist ciphertext and the authenticated-encryption envelope metadata (nonce/IV, authentication tag, encryption-key identifier), Woo key identifier and the declared `read` permission. Neither consumer key nor consumer secret is stored as plaintext, even temporarily in a staging table. Encryption-key *values* remain external to schema and migrations.
4. **Attempt integrity:** Persist only a digest of the opaque unpredictable callback bearer, short expiry, consumption/outcome times, the expected installation/version and a stable attempt identity. Constrain duplicate consumption and stale-generation replacement; an expired or consumed attempt cannot authorise another grant. Do not use WordPress's `user_id` as a Moda tenant key.
5. **Lifecycle:** Represent at least active, revoked/invalid and absence distinctly without conflating them with `WooCommerceInstallationStatus` or `Shop.onboardingCompleted`. Store bounded provider identifiers, timestamps and rotation/version metadata. Do not introduce a WordPress locale or REST permission enum that implies broader access than `read`.
6. **Migration:** This is an additive migration. Existing Shopify/Woo Shop records and existing installation credential digests remain untouched. No automatic key grants, onboarding changes or data backfill are possible.

## Work Items

- [x] Add Prisma grant and pending-attempt models plus constrained relations to Woo installation state.
- [x] Add migration, FK/unique/index/length/expiry/consumption invariants, documenting retention/cascade decisions.
- [x] Validate migration on a fresh PostgreSQL database and a database with existing Woo installations.
- [x] Add tests for cross-installation ownership, duplicate grant/attempt races, invalid envelope, consumption and cascade cases.

## Interfaces / Contracts

- **Owned database schema:** `woocommerce` in `moda-interact-database/prisma/schema.prisma`.
- **Consumer:** `ARCH-026-API-007` will generate attempt tokens, encrypt and persist credentials, and transition their lifecycle. DATABASE-003 defines persistence only.
- **Existing invariant:** `ARCH-026-DATABASE-001` remains authoritative for `WooCommerceInstallation` and `commerce.Shop` identity.
- No network-level JSON or queue contract is introduced.

## Dependencies

- `ARCH-026-DATABASE-001` — Complete; Woo installation identity and immutable Shop ownership.

## Enables

- `ARCH-026-API-007`.

## Acceptance Criteria

- [x] Exactly one currently selected REST read grant can be associated with a Woo installation without affecting the inbound Moda installation credential.
- [x] A pending grant is bound to its installation/version and can be consumed at most once; late/stale attempts cannot overwrite an approved newer grant.
- [x] No plaintext Woo consumer key or secret column exists; AEAD metadata and key ID are preserved correctly.
- [x] FK, uniqueness, check and deletion semantics are enforced by PostgreSQL, not only by Prisma.
- [x] Fresh installation and upgrade rehearsals preserve existing Shops, Woo installations, Free billing/entitlements and migration history.

## Validation

- [x] `npm run prisma:validate` and `npm run prisma:generate`.
- [x] `npm run status` after applying all migrations through Prisma to an isolated fresh PostgreSQL rehearsal database; status reported all 47 migrations applied and schema up to date.
- [x] Fresh and upgrade migration/integrity tests using disposable PostgreSQL, including concurrency cases.
- [x] `git diff --check`; implementation changes are limited to database-owned schema, migration, documentation and focused tests.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation pass, set this task to `review`, record the Completion Report and return to `moda_architect`. STOP; do not implement the hosted callback or plugin UI.

## Implementation Notes

Do not introduce a reversible cleartext staging field. The API owns key material and AEAD operations. Grant states and attempts must remain independent of the automatic Free-plan installation transaction. This capability is new; existing Woo merchant data must not be reset to introduce it.

## Completion Report

### Status

In Review; passing developer self-review recorded, explicit developer completion pending.

### Files Changed

- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20261010120000_arch026_woocommerce_rest_read_grant/migration.sql`
- `moda-interact-database/docs/ARCH-026-woocommerce-rest-read-grant.md`
- `moda-interact-database/package.json`
- `moda-interact-database/scripts/validate-arch026-woocommerce-rest-read-grant.mjs`
- `moda-interact-database/scripts/test-arch026-woocommerce-rest-read-grant-postgres.mjs`
- This task Completion Report.

### Work Completed

- Added `WooCommerceRestReadAttempt` and `WooCommerceRestReadGrant` persistence with composite installation/Shop ownership, one selected grant per installation, digest-only callback tokens, encrypted envelope metadata, bounded expiry, lifecycle state and version snapshots.
- Added additive PostgreSQL constraints, indexes, guards and deferred transaction checks for active Woo installation ownership, read-only scope, one-time attempt consumption, same-transaction grant activation, monotonic grant rotation, stale version rejection, replay protection and cascade behavior. Existing inbound `credentialDigest` remains intact.
- Added database contract documentation and focused static and PostgreSQL fresh/upgrade harnesses covering tenant isolation, invalid envelope values, expiry, replay, grant activation/revocation/rotation, stale attempts, concurrent rotations, cascades, and preservation of Shop/install/Free-credit data.
- The schema, migration, documentation and original test harness were already present on `origin/main` when the canonical implementation worktree was prepared. During this review, corrected both test scripts so they require the target migration to remain in ordered history rather than incorrectly requiring it to remain the newest repository migration. That focused correction is committed and pushed as implementation commit `97d3ad6`.
- No API, WooCommerce plugin, billing or other out-of-scope implementation was changed. No material assigned-agent assistance occurred.

### Validation Results

Passed: `npm run prisma:validate` and `npm run prisma:generate`.

Passed: `npm run test:arch026-woocommerce-rest-read-grant` after correcting its stale newest-migration assertion.

Passed: `npm run test:arch026-woocommerce-rest-read-grant:postgres:fresh` and `npm run test:arch026-woocommerce-rest-read-grant:postgres:upgrade` against separate disposable PostgreSQL 17 fixtures. The suites applied the ordered SQL migrations and passed checks for existing Shop/install and Free-credit preservation, cross-installation and Shopify tenant rejection, bounded expiry and token digest, invalid AEAD envelope rejection, atomic one-time consumption, replay prevention, permission enforcement, grant rotation and revocation, stale generation rejection, concurrent rotation ordering, and deletion cascades. Both fixtures were removed.

Passed: `npm run migrate:deploy` followed by `npm run status` against a separate empty disposable PostgreSQL 17 fixture. Prisma applied all 47 migrations and reported the database schema up to date. The fixture was removed. The repository-configured database `npm run status` also reported 47 migrations and an up-to-date schema.

Passed: `git diff --check`. Prisma generation left no tracked artifacts. The implementation task branch is clean and pushed; task-specific test correction commit `97d3ad6` is on `origin/task/ARCH-026-DATABASE-003`.

### Deviations

The existing static and PostgreSQL harnesses asserted this migration had to be the newest migration, which became false as later migrations were added. Updated both checks to assert that the target migration remains in ordered migration history. PostgreSQL integrity rehearsals ran against invocation-owned local containers, not the configured shared database.

### Assumptions

The schema and migration implementation already present in the shared database baseline is part of this task's delivered implementation; no separate source diff was needed when its task worktree was created.

### Unresolved Issues

None known.

### Architectural Concerns

The focused validator correction is test-only and retains checks that the target migration exists and runs in order. Direct-SQL fresh/upgrade harnesses intentionally do not fabricate Prisma migration history; a separate Prisma `migrate deploy`/`status` rehearsal verified migration history end to end.

## Architect Review

### Review Status

Pending.

### Review Notes

Pending implementation review.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Await repository implementation and Completion Report.

## Execution Ownership Amendment

The developer explicitly invoked `/moda_developer_create ARCH-026-DATABASE-003` to take over implementation from the task's prior agent execution mode. `assigned_agent: moda_database` is unchanged; `execution_mode` and `completion_mode` are now `developer`. The task has been claimed as developer attempt 1 after confirming `ARCH-026-DATABASE-001` is complete and both canonical task worktrees are clean and synchronized. No implementation changes have been made in this preparation step.

## Developer Self-Review

### Review Result

Passed. Explicit developer completion is pending.

### Attempt

1

### Reviewed Scope

The `WooCommerceRestReadAttempt` and `WooCommerceRestReadGrant` Prisma models, additive migration, database contract documentation, static validator, PostgreSQL fresh/upgrade harness, and its migration-order correction.

### Validation Evidence

Prisma validation and generation, focused static validation, PostgreSQL fresh and upgrade integrity/concurrency rehearsals, Prisma `migrate deploy` and `status` on a disposable fresh database, configured database status, and `git diff --check` passed. Canonical implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-026-DATABASE-003` is clean on `task/ARCH-026-DATABASE-003`, synchronized to and tracking its published upstream. Canonical parent task worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-026-DATABASE-003` contains this report on the matching branch.

### Decision

Transition attempt 1 to `review` under `completion_mode: developer`; do not mark Complete. Explicit developer completion remains pending.
