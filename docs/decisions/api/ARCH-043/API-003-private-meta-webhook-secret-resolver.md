---
id: ARCH-043-API-003
architecture_id: ARCH-043
title: Provide purpose-scoped private Meta secret resolution without a Messaging integration
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
enables:
- ARCH-043-GATEWAY-001
- ARCH-043-SYSTEM-TEST-001
created: '2026-10-17'
updated: '2026-10-17'
---

# Provide purpose-scoped private Meta secret resolution without a Messaging integration

## Architecture

- Parent: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Sealed-secret schema/security contract: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Owner: `moda_api` / `moda-interact-api`. This is a portable definition, **defined but not materialised**.

## Objective

Provide purpose-scoped private Meta secret resolution without a Messaging integration.

## Context

ARCH-043 stores designated application secrets as encrypted JSON envelopes within `PlatformConfiguration`; the decrypt/unseal root is external and the audit remains redacted. Never convert an existing domain credential value to plaintext or alter pre-existing encrypted-credential AAD.

## Scope

- Read and decrypt only the messaging.meta secret purpose under trusted environment scope.
- Implement a narrowly scoped, authenticated private Meta-purpose resolver for explicitly authorised future service identities, never generic arbitrary-key access. Do not integrate any current Messaging caller.
- Verify approved service identity, secret purpose, replay/expiry where applicable; never return secrets to browser/public API clients.
- Coordinate private routing and identity with Gateway; fail closed when service authentication or DB unseal fails. No Messaging service credential is issued, and no Messaging call site is changed in this task.

## Out of Scope

- No public generic secret-fetch endpoint, Messaging runtime changes, direct Messaging Postgres access or secret exposure through logs/metrics.

## Requirements

- Unauthorized callers cannot resolve Meta secret; only a separately authorised private service identity may resolve the current secret for one request; absent such an identity, requests are denied.

## Work Items

- [ ] Read and decrypt only the messaging.meta secret purpose under trusted environment scope.
- [ ] Implement a narrowly scoped, authenticated private Meta-purpose resolver for explicitly authorised future service identities, never generic arbitrary-key access. Do not integrate any current Messaging caller.
- [ ] Verify approved service identity, secret purpose, replay/expiry where applicable; never return secrets to browser/public API clients.
- [ ] Coordinate private routing and identity with Gateway; fail closed when service authentication or DB unseal fails. No Messaging service credential is issued, and no Messaging call site is changed in this task.
- [ ] Record actual files, validation and launcher-resolved isolation/synchronisation evidence in Completion Report; stop at Review.

## Interfaces / Contracts

- Persistence `PlatformConfiguration`/`PlatformConfigurationAudit`: `ARCH-043-DATABASE-001`.
- Existing encryption/decryption: `@modainteract/moda-interact-shared/security/credentials/node` (ARCH-039). ARCH-043 sealed JSON and frozen canonical AAD bytes are specified in `docs/architecture/ARCH-043-configuration-schema-review.md`; Admin writes and authorised service readers independently implement/verify this documented format without new Shared publication.
- Owner retains environment and service authorisation, per-request fresh reads, failure semantics and logging. No cross-operation configuration/secret cache is introduced. Never place unseal/root keys in PostgreSQL.

## Dependencies

- `ARCH-043-DATABASE-001`

## Enables

- `ARCH-043-GATEWAY-001`
- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Unauthorized callers cannot resolve Meta secret; only a separately authorised private service identity may resolve the current secret for one request; absent such an identity, requests are denied.

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
