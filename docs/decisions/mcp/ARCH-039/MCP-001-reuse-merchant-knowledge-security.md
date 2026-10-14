---
id: ARCH-039-MCP-001
architecture_id: ARCH-039
title: Migrate MCP Merchant Knowledge keyring and embedding decryption to Shared
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
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
enables:
  - ARCH-039-GATEWAY-001
  - ARCH-039-SYSTEM-TEST-001
created: 2026-10-14
updated: 2026-10-14
---


# Migrate MCP Merchant Knowledge keyring and embedding decryption to Shared

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_mcp` / `moda-interact-mcp`

## Objective

Migrate MCP Merchant Knowledge keyring and embedding decryption to Shared. This is one bounded, repository-owned outcome; do not move to another task on completion.

## Context

ARCH-039 makes one published credential security mechanism authoritative for hosted Node services. The developer has chosen a non-production data clear rather than historical encryption-key migration. This task is part of the agreed staged adoption plan; see the parent architecture for exact cross-service invariants.

## Scope

- Replace `src/execution/merchant-knowledge/credential-keyring.ts` clone and `embedding-runtime.ts` local AES-GCM/AAD with published Shared code.

## Out of Scope

No general MCP server refactor or tenant policy changes.

## Requirements

- **Mandatory closed-set credential configuration:** for AES credential encryption/decryption, credential key selection and Commerce connection-command HMAC, the **only permitted environment variable names anywhere in ARCH-039 runtime configuration** are `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`. No other names, aliases, old Woo keyring variables, service-specific encryption/HMAC variables, dual-read, fallback, generated defaults or alternate sources may be used for these purposes. Other unrelated application environment settings are unaffected.
- This MCP credential-reader task may read **only** `COMMERCE_CONNECTION_KEYS_JSON` from the closed set; it **must not** read or receive the active-key selector or command-HMAC secret. Decryption selects the stored envelope key ID.

- MCP receives only `COMMERCE_CONNECTION_KEYS_JSON`; it is a reader, never an encryption-key writer or command HMAC owner.
- Keep MCP private execution, tool/resource boundaries, tenant separation and embedding provider gating unchanged.
- Build `CredentialEnvelope` from stored embedding credential columns and call published `decryptCredential({ keyring, envelope, aad }): string` with `createCommerceEmbeddingCredentialAad`; never require the active writer key ID. Failures (including invalid UTF-8) must be bounded unavailable, never secret exposure or fallback plaintext.

## Work Items

- [ ] Migrate imports and remove local parser/AEAD/AAD.
- [ ] Update unit/integration embedding tests and negative config paths.
- [ ] Confirm no credential API is exposed through MCP tools.

## Interfaces / Contracts

- `decryptCredential`, `CredentialEnvelope` and keyring helpers from `@modainteract/moda-interact-shared/security/credentials/node`, plus `createCommerceEmbeddingCredentialAad`. Do not preserve local AEAD or reimplement the former binary open helper.

## Dependencies

- ARCH-039-SHARED-004

## Enables

- ARCH-039-GATEWAY-001
- ARCH-039-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] MCP uses only `COMMERCE_CONNECTION_KEYS_JSON` for this capability, not an alternate keyring, active selector or command HMAC; missing/legacy-only canonical configuration fails closed.

- [ ] MCP `decryptCredential` reads Admin `encryptCredential` embedding envelopes using identical Shared AAD, with credential text returned only inside the private authorised runtime.
- [ ] No competing parser or crypto module remains for Merchant Knowledge.
- [ ] MCP tools cannot expose key bytes.

## Validation

- [ ] Focused MCP keyring/embedding unit and integration tests where supported
- [ ] MCP typecheck/build
- [ ] Changed-file lint and `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. For developer completion, an explicit developer approval is required after accepted review.

## Implementation Notes

Preserve private host registration and existing MCP `capabilities.tools` behaviour.

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
