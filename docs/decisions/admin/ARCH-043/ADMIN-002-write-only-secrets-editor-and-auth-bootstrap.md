---
id: ARCH-043-ADMIN-002
architecture_id: ARCH-043
title: Write-only secrets editor and Admin authentication bootstrap
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-043-DATABASE-001
- ARCH-043-SHARED-002
enables:
- ARCH-043-GATEWAY-001
- ARCH-043-SYSTEM-TEST-001
created: '2026-10-17'
updated: '2026-10-17'
---

# Write-only secrets editor and Admin authentication bootstrap

## Architecture

- Parent: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Sealed-secret schema/security contract: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Owner: `moda_admin` / `moda-interact-admin`. This is a portable definition, **defined but not materialised**.

## Objective

Write-only secrets editor and Admin authentication bootstrap.

## Context

ARCH-043 stores designated application secrets as encrypted JSON envelopes within `PlatformConfiguration`; the decrypt/unseal root is external and the audit remains redacted. Never convert an existing domain credential value to plaintext or alter pre-existing encrypted-credential AAD.

## Scope

- Add restricted write-only Admin actions for the five approved secret purposes, with actor auth, independent secret-rotation permission and confirmation.
- Encrypt server-side before CAS write; store only redacted audit metadata, never replayable secret bytes, and show configured/revision status without revealing ciphertext.
- Provide one-time authenticated CLI import to seed auth.admin before changing Admin login bootstrap (CLI must work without an existing Admin web session).
- Load auth.admin early enough for Auth.js; prove fail-closed cold start, session compatibility/rotation and strict environment scoping.

## Out of Scope

- No unauthorised generic secret browser endpoint, raw secret logs, plaintext table values, external KMS setup or direct Messaging DB access.

## Requirements

- Admin can securely import/rotate secrets and remains inaccessible when required secrets cannot be resolved.
- No plaintext, ciphertext or root material returned to browser, audit or logs.

## Work Items

- [ ] Add restricted write-only Admin actions for the five approved secret purposes, with actor auth, independent secret-rotation permission and confirmation.
- [ ] Encrypt server-side before CAS write; store only redacted audit metadata, never replayable secret bytes, and show configured/revision status without revealing ciphertext.
- [ ] Provide one-time authenticated CLI import to seed auth.admin before changing Admin login bootstrap (CLI must work without an existing Admin web session).
- [ ] Load auth.admin early enough for Auth.js; prove fail-closed cold start, session compatibility/rotation and strict environment scoping.
- [ ] Record actual files, validation and launcher-resolved isolation/synchronisation evidence in Completion Report; stop at Review.

## Interfaces / Contracts

- Persistence `PlatformConfiguration`/`PlatformConfigurationAudit`: `ARCH-043-DATABASE-001`.
- Node-only sealed envelope format/validation: `ARCH-043-SHARED-003`, published under `ARCH-043-SHARED-002`.
- Owner retains environment and service authorisation, caching, failure semantics and logging. Never place unseal/root keys in PostgreSQL.

## Dependencies

- `ARCH-043-DATABASE-001`
- `ARCH-043-SHARED-002`

## Enables

- `ARCH-043-GATEWAY-001`
- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Admin can securely import/rotate secrets and remains inaccessible when required secrets cannot be resolved.
- [ ] No plaintext, ciphertext or root material returned to browser, audit or logs.

## Validation

- [ ] Focused Admin authorisation and redaction tests
- [ ] Cold-start/Auth.js tests, build, lint, typecheck
- [ ] `git diff --check`

## Stop Condition

Finish scoped implementation and required validation, update Completion Report, mark task Review, and return to moda_architect. STOP; do not execute follow-on tasks or update `_index.md`.

## Implementation Notes

Reuse Shared/ARCH-039 approved primitives and shared logging; preserve domain auth/tenant boundaries. Physical isolation/synchronisation evidence from task launcher required for acceptance.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

Awaiting implementation and validation.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Not assessed.

### Follow-up

None
