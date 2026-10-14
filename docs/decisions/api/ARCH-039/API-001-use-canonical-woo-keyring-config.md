---
id: ARCH-039-API-001
architecture_id: ARCH-039
title: Replace Woo REST-read API-specific keyring configuration
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 20
executor: developer
claimed_at: 2026-10-14T21:37:59Z
attempt: 1
depends_on:
  - ARCH-039-SHARED-004
enables:
  - ARCH-039-API-002
created: 2026-10-14
updated: 2026-10-14
---


# Replace Woo REST-read API-specific keyring configuration

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_api` / `moda-interact-api`

## Objective

Replace Woo REST-read API-specific keyring configuration. This is one bounded, repository-owned outcome; do not move to another task on completion.

## Context

ARCH-039 makes one published credential security mechanism authoritative for hosted Node services. The developer has chosen a non-production data clear rather than historical encryption-key migration. This task is part of the agreed staged adoption plan; see the parent architecture for exact cross-service invariants.

## Scope

- Migrate `src/woocommerce/rest-read/config.ts`, relevant runtime configuration typing/startup/dev scripts and operator documentation to `COMMERCE_CONNECTION_KEYS_JSON` and `COMMERCE_CONNECTION_ACTIVE_KEY_ID`.
- Preserve `MODA_WOO_REST_READ_PUBLIC_ORIGIN` as a *non-keyring* Woo-specific configuration input.

## Out of Scope

No changes to WooCommerce merchant PHP/plugin secret storage.

## Requirements

- **Mandatory closed-set credential configuration:** for AES credential encryption/decryption, credential key selection and Commerce connection-command HMAC, the **only permitted environment variable names anywhere in ARCH-039 runtime configuration** are `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`. No other names, aliases, old Woo keyring variables, service-specific encryption/HMAC variables, dual-read, fallback, generated defaults or alternate sources may be used for these purposes. Other unrelated application environment settings are unaffected.
- API Woo credential operations may read **only** `COMMERCE_CONNECTION_KEYS_JSON` and `COMMERCE_CONNECTION_ACTIVE_KEY_ID` from the closed set; they **must not** read or receive `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`. `MODA_WOO_REST_READ_KEYRING` and `MODA_WOO_REST_READ_ACTIVE_KEY_ID` are forbidden even as fallback aliases.

- Remove `MODA_WOO_REST_READ_KEYRING` and `MODA_WOO_REST_READ_ACTIVE_KEY_ID` from the API runtime and documentation; no dual-read or base64url compatibility mode.
- Parse strict Shared keyring/active selector only; partial configuration fails closed.
- The endpoint remains explicitly disabled when Woo authorisation is intentionally not configured, but malformed/incomplete enabled config must fail.
- Preserve public-origin SSRF/security checks and API authorisation rules.

## Work Items

- [ ] Change API config parser/typing, tests and dev startup examples.
- [ ] Remove old env var references in API source/scripts/docs, excluding unavoidable historical task docs.
- [ ] Verify enable/disable/configuration negative test matrix.

## Interfaces / Contracts

- Published Shared keyring and active-key helpers; canonical key IDs and padded Base64.

## Dependencies

- ARCH-039-SHARED-004

## Enables

- ARCH-039-API-002

## Acceptance Criteria

- [ ] Woo API credential paths only use the two canonical encryption variables; legacy-only configuration cannot enable the encrypted capability and command HMAC is never consumed.

- [ ] API only reads the canonical keyring and active selector for Woo REST-read encryption.
- [ ] No Woo-specific duplicate keyring config remains in runtime.
- [ ] Public-origin validation and strict authorisation are unchanged.

## Validation

- [ ] Focused API config + authorisation tests
- [ ] API typecheck and build
- [ ] Changed-file lint and `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. For developer completion, an explicit developer approval is required after accepted review.

## Implementation Notes

API-002 separately migrates grant envelope crypto; do not change database schema.

Use the canonical parent/implementation task-worktree preparation protocol, preserve dedicated worktree and start-of-attempt synchronization evidence, and do not edit `docs/decisions/**/_index.md` before architecture-session confirmation. No direct changes to another agent's repository.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-14T21:37:59Z. Attempt 0 review history is preserved below.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None beyond the parent architecture.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Not yet reviewed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending review.

### Follow-up

None.
