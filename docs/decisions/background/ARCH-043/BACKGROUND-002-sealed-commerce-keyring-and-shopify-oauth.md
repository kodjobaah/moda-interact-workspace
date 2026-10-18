---
id: ARCH-043-BACKGROUND-002
architecture_id: ARCH-043
title: Consume sealed Commerce keyring and Shopify OAuth
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
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
- ARCH-043-ADMIN-002
enables:
- ARCH-043-GATEWAY-001
- ARCH-043-SYSTEM-TEST-001
created: '2026-10-17'
updated: '2026-10-17'
---

# Consume sealed Commerce keyring and Shopify OAuth

## Architecture

- Parent: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Sealed-secret schema/security contract: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Owner: `moda_background` / `moda-interact-background`. This is a portable definition, **defined but not materialised**.

## Objective

Consume sealed Commerce keyring and Shopify OAuth.

## Context

ARCH-043 stores designated application secrets as encrypted JSON envelopes within `PlatformConfiguration`; the decrypt/unseal root is external and the audit remains redacted. Never convert an existing domain credential value to plaintext or alter pre-existing encrypted-credential AAD.

## Scope

- Use the sealed commerce.connectionKeys keyring where Background currently calls Shared keyring parsing.
- Use sealed shopify.oauth for Shopify session-refresh client ID/secret.
- Preserve job processing ordering, AAD bytes, prior credential decrypt and tenant isolation.
- Read and decrypt required configuration fresh for each relevant operation; no cache or stale last-known-good secret fallback; fail closed when required keys are unavailable after cutover.

## Out of Scope

- No Woo coupon tuning changes or other non-secret runtime policies.

## Requirements

- Existing credential decrypt and token-refresh workflows pass against encrypted DB-stored secret configuration.

## Work Items

- [ ] Use the sealed commerce.connectionKeys keyring where Background currently calls Shared keyring parsing.
- [ ] Use sealed shopify.oauth for Shopify session-refresh client ID/secret.
- [ ] Preserve job processing ordering, AAD bytes, prior credential decrypt and tenant isolation.
- [ ] Read and decrypt required configuration fresh for each relevant operation; no cache or stale last-known-good secret fallback; fail closed when required keys are unavailable after cutover.
- [ ] Record actual files, validation and launcher-resolved isolation/synchronisation evidence in Completion Report; stop at Review.

## Interfaces / Contracts

- Persistence `PlatformConfiguration`/`PlatformConfigurationAudit`: `ARCH-043-DATABASE-001`.
- Existing encryption/decryption: `@modainteract/moda-interact-shared/security/credentials/node` (ARCH-039). ARCH-043 sealed JSON and frozen canonical AAD bytes are specified in `docs/architecture/ARCH-043-configuration-schema-review.md`; Admin writes and authorised service readers independently implement/verify this documented format without new Shared publication.
- Owner retains environment and service authorisation, fresh per-operation reads, failure semantics and logging. Never place unseal/root keys in PostgreSQL.

## Dependencies

- `ARCH-043-DATABASE-001`

## Enables

- `ARCH-043-GATEWAY-001`
- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Existing credential decrypt and token-refresh workflows pass against encrypted DB-stored secret configuration.

## Validation

- [ ] Focused Background credential tests
- [ ] Typecheck/build and compatibility/rotation vectors
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

## 17 October 2026 ARCH-043 extension (architect-owned amendment)

Background Merchant Knowledge R2 acquirer also consumes all six fields from sealed `merchant.knowledge.r2`, with its own existing hard limits. Coordinate with BACKGROUND-001 so R2 is not sourced from competing policy/env providers. Require ADMIN-002 and verification of the developer forward migration for this new consumer.
