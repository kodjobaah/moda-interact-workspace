---
id: ARCH-039-SHARED-003
architecture_id: ARCH-039
title: Define cross-service AAD builders and independent command-HMAC key validation
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-039-SHARED-001
enables:
  - ARCH-039-SHARED-004
created: 2026-10-14
updated: 2026-10-14
---


# Define cross-service AAD builders and independent command-HMAC key validation

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_shared` / `moda-interact-shared`

## Objective

Define cross-service AAD builders and independent command-HMAC key validation. This is one bounded, repository-owned outcome; do not move to another task on completion.

## Context

ARCH-039 makes one published credential security mechanism authoritative for hosted Node services. The developer has chosen a non-production data clear rather than historical encryption-key migration. This task is part of the agreed staged adoption plan; see the parent architecture for exact cross-service invariants.

## Scope

- Add canonical AAD builder for Commerce embedding credential shared by Admin, Commerce and MCP.
- Add canonical AAD builder for Woo REST-read grants shared by API and Background.
- Add strict decoder for the independent `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`.

## Out of Scope

No command-kernel refactor, live HMAC rotation or ciphertext migration.

## Requirements

- Embedding AAD preserves the existing canonical JSON object semantics (credentialType, environment, purpose, provider, keyId).
- Woo AAD binds shopId, installationId, authorizationAttemptId and credentialVersionSnapshot; exact agreed shape produced by one helper.
- Keep existing OpenRouter and translation provider Shared AAD helpers, with no duplicate local copies.
- HMAC secret must be canonical padded standard Base64 for exactly 32 independent bytes; this decoder does not sign or verify commands and must not treat it as an AES key.

## Work Items

- [ ] Implement AAD builders, decoding and public exports.
- [ ] Add byte-for-byte AAD vectors and tamper/change-of-identity tests for both read/write sides.
- [ ] Add invalid HMAC configuration tests without printing any secret values.

## Interfaces / Contracts

- Exports for `createCommerceEmbeddingCredentialAad`, `createWooRestReadGrantAad`, `parseCommerceConnectionCommandHmacKey` under the Node credentials module or the existing Shared commerce namespace as consistent with existing exports.

## Dependencies

- ARCH-039-SHARED-001

## Enables

- ARCH-039-SHARED-004

## Acceptance Criteria

- [ ] Cross-service AAD is canonical and tenant/identity-bound.
- [ ] HMAC decoder rejects missing/noncanonical/wrong-size material independently of AES keyring.
- [ ] Existing OpenRouter/translation AAD remains unchanged.

## Validation

- [ ] Focused Shared deterministic AAD vector + HMAC-key tests
- [ ] Shared typecheck and build
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. For developer completion, an explicit developer approval is required after accepted review.

## Implementation Notes

The actual Commerce command-HMAC digest and database replay semantics remain in Commerce.

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
