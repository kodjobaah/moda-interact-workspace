---
id: ARCH-043-SHARED-003
architecture_id: ARCH-043
title: Define sealed platform-secret envelope and Node-only codec
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
- ARCH-043-SHARED-002
created: '2026-10-17'
updated: '2026-10-17'
---

# Define sealed platform-secret envelope and Node-only codec

## Architecture

- Parent: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Sealed-secret schema/security contract: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Owner: `moda_shared` / `moda-interact-shared`. This is a portable definition, **defined but not materialised**.

## Objective

Define sealed platform-secret envelope and Node-only codec.

## Context

ARCH-043 stores designated application secrets as encrypted JSON envelopes within `PlatformConfiguration`; the decrypt/unseal root is external and the audit remains redacted. Never convert an existing domain credential value to plaintext or alter pre-existing encrypted-credential AAD.

## Scope

- Inspect existing ARCH-039 crypto/AAD primitives and reuse them where format-compatible; otherwise create a narrowly scoped, tested sealed-config envelope adapter.
- Define strict envelope and purpose-specific decrypted payload schemas for commerce.connectionKeys, auth.admin, auth.commerce, shopify.oauth, messaging.meta.
- Bind authenticated data to environment/key/revision/schema, reject tampering, unsupported algorithm, unknown wrapping key and plaintext JSON.
- Ensure no browser-safe export or Node secret import leak; support root-key rotation compatibility vectors.

## Out of Scope

- No DB migrations, admin UI, app consumers, release/publish or different provider credential scheme.

## Requirements

- Cross-service persisted format is versioned and integrity-protected.
- Deterministic compatibility/tamper/key-rotation tests pass across supported runtimes; no real secret bytes in fixtures.

## Work Items

- [ ] Inspect existing ARCH-039 crypto/AAD primitives and reuse them where format-compatible; otherwise create a narrowly scoped, tested sealed-config envelope adapter.
- [ ] Define strict envelope and purpose-specific decrypted payload schemas for commerce.connectionKeys, auth.admin, auth.commerce, shopify.oauth, messaging.meta.
- [ ] Bind authenticated data to environment/key/revision/schema, reject tampering, unsupported algorithm, unknown wrapping key and plaintext JSON.
- [ ] Ensure no browser-safe export or Node secret import leak; support root-key rotation compatibility vectors.
- [ ] Record actual files, validation and launcher-resolved isolation/synchronisation evidence in Completion Report; stop at Review.

## Interfaces / Contracts

- Persistence `PlatformConfiguration`/`PlatformConfigurationAudit`: `ARCH-043-DATABASE-001`.
- Node-only sealed envelope format/validation: `ARCH-043-SHARED-003`, published under `ARCH-043-SHARED-002`.
- Owner retains environment and service authorisation, caching, failure semantics and logging. Never place unseal/root keys in PostgreSQL.

## Dependencies

None

## Enables

- `ARCH-043-SHARED-002`

## Acceptance Criteria

- [ ] Cross-service persisted format is versioned and integrity-protected.
- [ ] Deterministic compatibility/tamper/key-rotation tests pass across supported runtimes; no real secret bytes in fixtures.

## Validation

- [ ] Unit tests and typecheck/lint/build
- [ ] Package export-surface and ciphertext compatibility vectors
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
