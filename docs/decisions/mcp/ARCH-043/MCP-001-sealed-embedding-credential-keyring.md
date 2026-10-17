---
id: ARCH-043-MCP-001
architecture_id: ARCH-043
title: Consume sealed Commerce keyring for MCP embedding credentials
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
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
- ARCH-043-SHARED-002
enables:
- ARCH-043-GATEWAY-001
- ARCH-043-SYSTEM-TEST-001
created: '2026-10-17'
updated: '2026-10-17'
---

# Consume sealed Commerce keyring for MCP embedding credentials

## Architecture

- Parent: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Sealed-secret schema/security contract: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Owner: `moda_mcp` / `moda-interact-mcp`. This is a portable definition, **defined but not materialised**.

## Objective

Consume sealed Commerce keyring for MCP embedding credentials.

## Context

ARCH-043 stores designated application secrets as encrypted JSON envelopes within `PlatformConfiguration`; the decrypt/unseal root is external and the audit remains redacted. Never convert an existing domain credential value to plaintext or alter pre-existing encrypted-credential AAD.

## Scope

- Replace env-backed Commerce keyring reads in MCP embedding-runtime with sealed commerce.connectionKeys.
- Preserve published Shared decryption AAD and embedding-provider credentials compatibility.
- Test missing/wrong-environment/unsealable secret fails closed and never logs secret bytes.

## Out of Scope

- No embedding model/provider policy changes or new credential models.

## Requirements

- Existing encrypted MCP embedding credentials decrypt unchanged; missing/invalid secret denies operation.

## Work Items

- [ ] Replace env-backed Commerce keyring reads in MCP embedding-runtime with sealed commerce.connectionKeys.
- [ ] Preserve published Shared decryption AAD and embedding-provider credentials compatibility.
- [ ] Test missing/wrong-environment/unsealable secret fails closed and never logs secret bytes.
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

- [ ] Existing encrypted MCP embedding credentials decrypt unchanged; missing/invalid secret denies operation.

## Validation

- [ ] MCP credential and embedding tests
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
