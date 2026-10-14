---
id: ARCH-039-SHARED-001
architecture_id: ARCH-039
title: Provide strict canonical credential keyring and active-key validation
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-039-SHARED-002
  - ARCH-039-SHARED-003
  - ARCH-039-SHARED-004
created: 2026-10-14
updated: 2026-10-14
---


# Provide strict canonical credential keyring and active-key validation

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_shared` / `moda-interact-shared`

## Objective

Provide strict canonical credential keyring and active-key validation. This is one bounded, repository-owned outcome; do not move to another task on completion.

## Context

ARCH-039 makes one published credential security mechanism authoritative for hosted Node services. The developer has chosen a non-production data clear rather than historical encryption-key migration. This task is part of the agreed staged adoption plan; see the parent architecture for exact cross-service invariants.

## Scope

- Create the Node-only Shared credential-security entrypoint and public types; implement strict JSON/base64 parsing and active-key resolution.
- Export via package `exports`, build/types; no environment access in the library.

## Out of Scope

Provider-specific tokens and provider business validation are out of scope.

## Requirements

- `COMMERCE_CONNECTION_KEYS_JSON` is a JSON object containing 1–16 keys with IDs matching `[A-Za-z0-9_-]{1,64}` and exactly 32 bytes encoded as canonical padded standard Base64.
- Reject missing, empty, malformed, noncanonical, oversized, prototype-shaped unsafe identifiers, duplicate logical IDs and missing active selector for writers. Reader helpers must work without an active selector.
- Do not return an empty keyring on missing input; do not accept base64url as a separate format. Errors never include key material.

## Work Items

- [ ] Implement parsing/key selection and immutable public type surface.
- [ ] Test valid, missing, empty, malformed, noncanonical, prototype-key, max keyring size, active-key selection and reader-only use.
- [ ] Verify Node-only module never enters browser entrypoints.

## Interfaces / Contracts

- Exports from `@modainteract/moda-interact-shared/security/credentials/node`: `parseCredentialKeyring`, `resolveActiveCredentialKey`, and associated types.

## Dependencies

None.

## Enables

- ARCH-039-SHARED-002
- ARCH-039-SHARED-003
- ARCH-039-SHARED-004

## Acceptance Criteria

- [ ] Canonical 32-byte standard-base64 parsing with uniform key-ID rules; no alternate parser or encoding mode.
- [ ] Malformed/missing config fails closed and errors reveal no secrets.
- [ ] Reader path does not need active writer key; package export is Node-only.

## Validation

- [ ] Focused unit tests for valid and invalid input matrix
- [ ] Shared typecheck and build
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. For developer completion, an explicit developer approval is required after accepted review.

## Implementation Notes

No crypto envelope, domain-specific AAD or consumer changes here.

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
