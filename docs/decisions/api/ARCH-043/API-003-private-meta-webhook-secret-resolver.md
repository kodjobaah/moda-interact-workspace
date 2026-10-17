---
id: ARCH-043-API-003
architecture_id: ARCH-043
title: Expose authenticated private Meta webhook secret snapshot
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
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
- ARCH-043-MESSAGING-001
- ARCH-043-SYSTEM-TEST-001
created: '2026-10-17'
updated: '2026-10-17'
---

# Expose authenticated private Meta webhook secret snapshot

## Architecture

- Parent: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Sealed-secret schema/security contract: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Owner: `moda_api` / `moda-interact-api`. This is a portable definition, **defined but not materialised**.

## Objective

Expose authenticated private Meta webhook secret snapshot.

## Context

ARCH-043 stores designated application secrets as encrypted JSON envelopes within `PlatformConfiguration`; the decrypt/unseal root is external and the audit remains redacted. Never convert an existing domain credential value to plaintext or alter pre-existing encrypted-credential AAD.

## Scope

- Read and decrypt only the messaging.meta secret purpose under trusted environment scope.
- Expose a narrowly scoped, authenticated private service-to-service resolver for Messaging, never generic arbitrary-key access.
- Verify approved service identity, secret purpose, replay/expiry where applicable; never return secrets to browser/public API clients.
- Coordinate private routing and identity with Gateway; fail closed when service authentication or DB unseal fails.

## Out of Scope

- No public generic secret-fetch endpoint, direct Messaging Postgres access or secret exposure through logs/metrics.

## Requirements

- Unauthorized callers cannot resolve Meta secret; legitimate private Messaging identity can fetch an expiring scoped snapshot.

## Work Items

- [ ] Read and decrypt only the messaging.meta secret purpose under trusted environment scope.
- [ ] Expose a narrowly scoped, authenticated private service-to-service resolver for Messaging, never generic arbitrary-key access.
- [ ] Verify approved service identity, secret purpose, replay/expiry where applicable; never return secrets to browser/public API clients.
- [ ] Coordinate private routing and identity with Gateway; fail closed when service authentication or DB unseal fails.
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
- `ARCH-043-MESSAGING-001`
- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Unauthorized callers cannot resolve Meta secret; legitimate private Messaging identity can fetch an expiring scoped snapshot.

## Validation

- [ ] Private endpoint auth/isolation/replay tests
- [ ] Typecheck/build and negative tests
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
