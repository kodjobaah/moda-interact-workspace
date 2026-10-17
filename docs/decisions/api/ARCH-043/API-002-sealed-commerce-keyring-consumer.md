---
id: ARCH-043-API-002
architecture_id: ARCH-043
title: Consume sealed Commerce connection keys in hosted API
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-043-DATABASE-001
enables:
- ARCH-043-GATEWAY-001
- ARCH-043-SYSTEM-TEST-001
created: '2026-10-17'
updated: '2026-10-17'
---

# Consume sealed Commerce connection keys in hosted API

## Architecture

- Parent: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Sealed-secret schema/security contract: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Owner: `moda_api` / `moda-interact-api`. This is a portable definition, **defined but not materialised**.

## Objective

Consume sealed Commerce connection keys in hosted API.

## Context

ARCH-043 stores designated application secrets as encrypted JSON envelopes within `PlatformConfiguration`; the decrypt/unseal root is external and the audit remains redacted. Never convert an existing domain credential value to plaintext or alter pre-existing encrypted-credential AAD.

## Scope

- Replace hosted API Commerce keyring/active-key environment reads for the Woo REST-read authorisation path.
- Use approved server-only unwrap material, preserve ARCH-039 keyring validation, AAD and fail-closed partial config.
- Read/decrypt the current secret directly for each relevant operation, with trusted environment scope, without cross-operation caches or stale fallbacks.

## Out of Scope

- No tenant signing secrets in browser, no private Meta read endpoint, no Merchant Knowledge policy changes.

## Requirements

- Woo read-authorisation retains correct credential decryption/rotation and fails closed on invalid DB secret.

## Work Items

- [ ] Replace hosted API Commerce keyring/active-key environment reads for the Woo REST-read authorisation path.
- [ ] Use approved server-only unwrap material, preserve ARCH-039 keyring validation, AAD and fail-closed partial config.
- [ ] Read/decrypt the current secret directly for each relevant operation, with trusted environment scope, without cross-operation caches or stale fallbacks.
- [ ] Record actual files, validation and launcher-resolved isolation/synchronisation evidence in Completion Report; stop at Review.

## Interfaces / Contracts

- Persistence `PlatformConfiguration`/`PlatformConfigurationAudit`: `ARCH-043-DATABASE-001`.
- Existing encryption/decryption: `@modainteract/moda-interact-shared/security/credentials/node` (ARCH-039). ARCH-043 sealed JSON and frozen canonical AAD bytes are specified in `docs/architecture/ARCH-043-configuration-schema-review.md`; Admin writes and authorised service readers independently implement/verify this documented format without new Shared publication.
- Owner retains environment and service authorisation, fresh per-operation retrieval, failure semantics and logging; no secret cache. Never place unseal/root keys in PostgreSQL.

## Dependencies

- `ARCH-043-DATABASE-001`

## Enables

- `ARCH-043-GATEWAY-001`
- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Woo read-authorisation retains correct credential decryption/rotation and fails closed on invalid DB secret.

## Validation

- [ ] REST-read and credential compatibility tests
- [ ] Typecheck/build
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
