---
id: ARCH-026-DATABASE-003
architecture_id: ARCH-026
title: Persist tenant-scoped WooCommerce read authorisation state
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-026-DATABASE-001
enables:
  - ARCH-026-API-007
created: 2026-10-10
updated: 2026-10-10
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

- [ ] Add Prisma grant and pending-attempt models plus constrained relations to Woo installation state.
- [ ] Add migration, FK/unique/index/length/expiry/consumption invariants, documenting retention/cascade decisions.
- [ ] Validate migration on a fresh PostgreSQL database and a database with existing Woo installations.
- [ ] Add tests for cross-installation ownership, duplicate grant/attempt races, invalid envelope, consumption and cascade cases.

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

- [ ] Exactly one currently selected REST read grant can be associated with a Woo installation without affecting the inbound Moda installation credential.
- [ ] A pending grant is bound to its installation/version and can be consumed at most once; late/stale attempts cannot overwrite an approved newer grant.
- [ ] No plaintext Woo consumer key or secret column exists; AEAD metadata and key ID are preserved correctly.
- [ ] FK, uniqueness, check and deletion semantics are enforced by PostgreSQL, not only by Prisma.
- [ ] Fresh installation and upgrade rehearsals preserve existing Shops, Woo installations, Free billing/entitlements and migration history.

## Validation

- [ ] `npm run prisma:validate` (or the repository-declared equivalent).
- [ ] `npm run status` against the rehearsal database after applying migrations.
- [ ] Fresh and upgrade migration/integrity tests using disposable PostgreSQL, including concurrency cases.
- [ ] `git diff --check`, with only database ownership and this task's Completion Report changed.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation pass, set this task to `review`, record the Completion Report and return to `moda_architect`. STOP; do not implement the hosted callback or plugin UI.

## Implementation Notes

Do not introduce a reversible cleartext staging field. The API owns key material and AEAD operations. Grant states and attempts must remain independent of the automatic Free-plan installation transaction. This capability is new; existing Woo merchant data must not be reset to introduce it.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

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
