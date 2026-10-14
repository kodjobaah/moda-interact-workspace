---
id: ARCH-039-SYSTEM-TEST-001
architecture_id: ARCH-039
title: Certify unified credential encryption and least-privilege configuration end-to-end
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 80
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-039-SHARED-004
  - ARCH-039-ADMIN-001
  - ARCH-039-ADMIN-002
  - ARCH-039-BACKGROUND-001
  - ARCH-039-BACKGROUND-002
  - ARCH-039-COMMERCE-001
  - ARCH-039-COMMERCE-002
  - ARCH-039-MCP-001
  - ARCH-039-API-001
  - ARCH-039-API-002
  - ARCH-039-GATEWAY-001
enables: []
created: 2026-10-14
updated: 2026-10-14
---


# Certify unified credential encryption and least-privilege configuration end-to-end

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_system_test` / `moda-interact-system-test`

## Objective

Certify unified credential encryption and least-privilege configuration end-to-end. This is one bounded, repository-owned outcome; do not move to another task on completion.

## Context

ARCH-039 makes one published credential security mechanism authoritative for hosted Node services. The developer has chosen a non-production data clear rather than historical encryption-key migration. This task is part of the agreed staged adoption plan; see the parent architecture for exact cross-service invariants.

## Scope

- Extend black-box system tests to certify Admin writer/Commerce-Background-MCP readers where applicable and API writer/Background Woo reader.
- Validate malformed config, auth-tag/AAD tampering, tenant isolation and canonical Gateway secret distribution.

## Out of Scope

No production secrets, destructive deployment/database operation or feature refactor.

## Requirements

- **Mandatory closed-set credential configuration:** for AES credential encryption/decryption, credential key selection and Commerce connection-command HMAC, the **only permitted environment variable names anywhere in ARCH-039 runtime configuration** are `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`. No other names, aliases, old Woo keyring variables, service-specific encryption/HMAC variables, dual-read, fallback, generated defaults or alternate sources may be used for these purposes. Other unrelated application environment settings are unaffected.
- Black-box fixtures and service startup may configure **only** `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` (writers only) and `COMMERCE_CONNECTION_COMMAND_HMAC_KEY` (Commerce only) for these ARCH-039 secrets. Exercise canonical absent/invalid, legacy-only, and forbidden-recipient cases; never hide a missing key via an alternate variable. Other unrelated test/runtime configuration is unaffected.

- Use black-box executors, fixtures, assertions, orchestration and evidence with the established system-test module separation.
- Use disposable non-production Postgres/Redis fixtures if needed; never clear a persistent database or use real credentials.
- Confirm developer-controlled non-production clear/cutover checkpoint before asserting breaking-only behaviour.
- No system-test task gates unfinished implementation; it runs after all required tasks are accepted Complete.

## Work Items

- [ ] Test an environment with only obsolete Woo encryption variables (canonical names missing) and reject it; separately test forbidden active-key and command-HMAC recipients without exposing secret values.

- [ ] Add black-box interop scenarios with the same canonical 32-byte Base64 key/IDs and independent HMAC key: Admin/Commerce/API credential writers use published `encryptCredential` while authorised Commerce/Background/MCP readers use published `decryptCredential`; exercise the actual service boundaries, not duplicate test-only cryptography.
- [ ] Add wrong-key, wrong-environment/purpose, wrong-tenant, tag tamper, missing-secret, API keyring format rejection and least-privilege scenarios.
- [ ] Record evidence locations and failures without plaintext or key leakage.

## Interfaces / Contracts

- All accepted consumer implementations, published Shared version exposing exactly `encryptCredential`/`decryptCredential` for credential cryptography, and validated Gateway Blueprints. Service adapters may map persisted envelope fields but must not call deprecated `sealCredential`, `openCredential` or `openCredentialText`.

## Dependencies

- ARCH-039-SHARED-004
- ARCH-039-ADMIN-001
- ARCH-039-ADMIN-002
- ARCH-039-BACKGROUND-001
- ARCH-039-BACKGROUND-002
- ARCH-039-COMMERCE-001
- ARCH-039-COMMERCE-002
- ARCH-039-MCP-001
- ARCH-039-API-001
- ARCH-039-API-002
- ARCH-039-GATEWAY-001

## Enables

None.

## Acceptance Criteria

- [ ] Black-box negative evidence proves that legacy-only/alias configuration cannot activate encryption, missing/invalid canonical settings fail closed, and active-key/HMAC secrets do not reach unauthorised services.

- [ ] Cross-service text-credential interoperability holds for correct authorised writer `encryptCredential`, reader `decryptCredential` and exact AAD (including Woo JSON-string grants); no separate local crypto path or deprecated Shared API remains.
- [ ] Tamper, mismatched domain/tenant, malformed configuration and missing keys fail closed.
- [ ] Gateway attachments expose only keyring to readers and active selector to writers, Commerce-only HMAC.
- [ ] System-test report includes independently reproducible black-box evidence.

## Validation

- [ ] Focused cross-service black-box acceptance suite
- [ ] Disposable fixture cleanup and evidence checks
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. Do not self-accept or begin dependent work.

## Implementation Notes

System testing may inspect but must not modify business implementation repositories. Leave task review for moda_architect acceptance.

Use the canonical parent/implementation task-worktree preparation protocol, preserve dedicated worktree and start-of-attempt synchronization evidence, and do not edit `docs/decisions/**/_index.md` before architecture-session confirmation. No direct changes to another agent's repository.

## Completion Report

### Status

Not Started

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
