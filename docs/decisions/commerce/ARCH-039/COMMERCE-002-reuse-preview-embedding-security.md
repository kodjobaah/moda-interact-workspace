---
id: ARCH-039-COMMERCE-002
architecture_id: ARCH-039
title: Migrate Commerce Preview and embedding credential readers to Shared
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-039-SHARED-004
  - ARCH-039-COMMERCE-001
enables:
  - ARCH-039-GATEWAY-001
  - ARCH-039-SYSTEM-TEST-001
created: 2026-10-14
updated: 2026-10-15
---


# Migrate Commerce Preview and embedding credential readers to Shared

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_commerce` / `moda-interact-commerce`

## Objective

Migrate Commerce Preview and embedding credential readers to Shared. This is one bounded, repository-owned outcome; do not move to another task on completion.

## Context

ARCH-039 makes one published credential security mechanism authoritative for hosted Node services. The developer has chosen a non-production data clear rather than historical encryption-key migration. This task is part of the agreed staged adoption plan; see the parent architecture for exact cross-service invariants.

## Scope

- Replace Preview OpenRouter and Merchant Knowledge embedding AES-GCM implementations with published `decryptCredential` and the appropriate Shared AAD builders. Map existing stored fields to `CredentialEnvelope` at each service boundary.
- Fix `lib/preview/runtime.ts` malformed keyring handling so optional Preview disablement cannot mask invalid enabled configuration.

## Out of Scope

No Studio UX redesign or external connection command changes.

## Requirements

- **Mandatory closed-set credential configuration:** for AES credential encryption/decryption, credential key selection and Commerce connection-command HMAC, the **only permitted environment variable names anywhere in ARCH-039 runtime configuration** are `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`. No other names, aliases, old Woo keyring variables, service-specific encryption/HMAC variables, dual-read, fallback, generated defaults or alternate sources may be used for these purposes. Other unrelated application environment settings are unaffected.
- Commerce may read `COMMERCE_CONNECTION_KEYS_JSON` and `COMMERCE_CONNECTION_ACTIVE_KEY_ID` for credential writes; **only Commerce command-signing code** may additionally read `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`, through the published independent HMAC parser. Preview/embedding readers consume the keyring, not a command-HMAC key. No other credential-security setting name is permitted.

- Consume the canonical keyring from the Commerce server adapter established by COMMERCE-001. Both credential readers call `decryptCredential({ keyring, envelope, aad }): string`, which selects the envelope key ID (not the active key). Preserve existing domain validation of returned provider credential text.
- Wrong environment/provider/purpose/key ID/authentication and corrupted envelope fail closed.
- Preserve preview abort semantics, retriable versus non-retriable outcomes, logging redaction and embedding provider/model validation.

## Work Items

- [ ] Migrate Preview resolver and Merchant Knowledge embedding runtime to published Shared APIs.
- [ ] Remove duplicate local AAD/envelope/plaintext validation and unsafe empty-config fallback.
- [ ] Test failure reasons and cross-service vectors.

## Interfaces / Contracts

- `decryptCredential`, `CredentialEnvelope` and keyring helpers from `@modainteract/moda-interact-shared/security/credentials/node`, with existing Shared OpenRouter AAD and published `createCommerceEmbeddingCredentialAad`. No alternate `openCredential` or local AES implementation.

## Dependencies

- ARCH-039-SHARED-004
- ARCH-039-COMMERCE-001

## Enables

- ARCH-039-GATEWAY-001
- ARCH-039-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Commerce uses only the three named canonical credential-security variables according to function; no service-local alternate, legacy alias, or fallback can enable credential or command signing.

- [ ] Preview/OpenRouter and embedding readers use the published `decryptCredential` text API with their correct Shared AAD, never a local decryptor.
- [ ] Invalid configured keyring does not become a silent empty ring.
- [ ] Preview/test conversation cancellation and provider selection semantics remain intact.

## Validation

- [ ] Focused Commerce Preview and embedding runtime tests
- [ ] Commerce typecheck and build
- [ ] Changed-file lint and `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. For developer completion, an explicit developer approval is required after accepted review.

## Implementation Notes

Domain-specific safe error categorisation can remain as an adapter around Shared exceptions.

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
