---
id: ARCH-039-SHARED-002
architecture_id: ARCH-039
title: Provide shared authenticated AES-256-GCM credential primitives
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


# Provide shared authenticated AES-256-GCM credential primitives

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_shared` / `moda-interact-shared`

## Objective

Provide shared authenticated AES-256-GCM credential primitives. This is one bounded, repository-owned outcome; do not move to another task on completion.

## Context

ARCH-039 makes one published credential security mechanism authoritative for hosted Node services. The developer has chosen a non-production data clear rather than historical encryption-key migration. This task is part of the agreed staged adoption plan; see the parent architecture for exact cross-service invariants.

## Scope

- Implement a generic sealed credential envelope contract, bounded AES-256-GCM seal/open using explicit keyring + AAD and a Node-only crypto module under the Shared entrypoint.
- Support `Uint8Array`/Buffer data for JSON-structured Woo credentials as well as UTF-8 provider secrets; domains retain plaintext parsing and safety semantics.

## Out of Scope

No backfill/migration, provider token-format validation or HMAC command hashing.

## Requirements

- Always generate a fresh 12-byte nonce; authentication tag exactly 16 bytes; ciphertext bounded nonempty and <=8192 bytes.
- Explicit key ID on output; enforce validated keyring and key identity; reject altered AAD, unknown key ID, malformed nonce/tag, tampering, malformed input and invalid UTF-8 only where string output is requested.
- No DB, environment access, provider API, sensitive logging or fallback plaintext; expose safe error categories without raw crypto exceptions.

## Work Items

- [ ] Implement seal/open/envelope validation with authenticated data supplied by caller.
- [ ] Add round-trip, nonce uniqueness, wrong-key/wrong-AAD, tamper, length and invalid-input tests.
- [ ] Build/test the subpath and type declarations.

## Interfaces / Contracts

- `sealCredential`, `openCredential`, `isValidCredentialEnvelope` in `@modainteract/moda-interact-shared/security/credentials/node`; accepts explicit domain-bound AAD.

## Dependencies

- ARCH-039-SHARED-001

## Enables

- ARCH-039-SHARED-004

## Acceptance Criteria

- [ ] All in-scope AES-256-GCM code can use one bounded authenticated primitive.
- [ ] Wrong-key, AAD or corrupted envelope always fails closed with secret-free result.
- [ ] Crypto module remains Node-only.

## Validation

- [ ] Focused Shared AEAD/unit and tamper tests
- [ ] Shared typecheck and build
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. For developer completion, an explicit developer approval is required after accepted review.

## Implementation Notes

Exact persisted row shape and domain-specific error mapping remain caller-owned; no database schema change.

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
