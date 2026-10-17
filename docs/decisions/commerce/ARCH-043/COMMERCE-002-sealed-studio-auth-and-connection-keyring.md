---
id: ARCH-043-COMMERCE-002
architecture_id: ARCH-043
title: Consume sealed Commerce authentication and connection keys
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
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

# Consume sealed Commerce authentication and connection keys

## Architecture

- Parent: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Sealed-secret schema/security contract: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Owner: `moda_commerce` / `moda-interact-commerce`. This is a portable definition, **defined but not materialised**.

## Objective

Consume sealed Commerce authentication and connection keys.

## Context

ARCH-043 stores designated application secrets as encrypted JSON envelopes within `PlatformConfiguration`; the decrypt/unseal root is external and the audit remains redacted. Never convert an existing domain credential value to plaintext or alter pre-existing encrypted-credential AAD.

## Scope

- Load auth.commerce and commerce.connectionKeys from encrypted DB on trusted server startup/read.
- Preserve existing credential decrypt AAD and ciphertext; decrypt keyring using external approved unwrap identity only.
- Update Studio auth/preview/tool/connection consumers to same stable source; keep keyring/Google secrets server-only.
- Fail closed for missing/wrong-env/unsealable configuration; test safe key rotation and session compatibility.

## Out of Scope

- No browser keys, provider ciphertext rewrite, unaudited fallback or change to preview policy implementation.

## Requirements

- Existing encrypted credentials remain readable with identical AAD; Studio does not start accepting protected requests without secrets.

## Work Items

- [ ] Load auth.commerce and commerce.connectionKeys from encrypted DB on trusted server startup/read.
- [ ] Preserve existing credential decrypt AAD and ciphertext; decrypt keyring using external approved unwrap identity only.
- [ ] Update Studio auth/preview/tool/connection consumers to same stable source; keep keyring/Google secrets server-only.
- [ ] Fail closed for missing/wrong-env/unsealable configuration; test safe key rotation and session compatibility.
- [ ] Record actual files, validation and launcher-resolved isolation/synchronisation evidence in Completion Report; stop at Review.

## Interfaces / Contracts

- Persistence `PlatformConfiguration`/`PlatformConfigurationAudit`: `ARCH-043-DATABASE-001`.
- Existing encryption/decryption: `@modainteract/moda-interact-shared/security/credentials/node` (ARCH-039). ARCH-043 sealed JSON and frozen canonical AAD bytes are specified in `docs/architecture/ARCH-043-configuration-schema-review.md`; Admin writes and authorised service readers independently implement/verify this documented format without new Shared publication.
- Owner retains environment and service authorisation, fresh per-operation reads where framework-supported, authentication bootstrap constraints, failure semantics and logging; no new configuration cache. Never place unseal/root keys in PostgreSQL.

## Dependencies

- `ARCH-043-DATABASE-001`

## Enables

- `ARCH-043-GATEWAY-001`
- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Existing encrypted credentials remain readable with identical AAD; Studio does not start accepting protected requests without secrets.

## Validation

- [ ] Focused credential and Studio auth tests
- [ ] Typecheck, lint and build, key rotation compatibility
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
