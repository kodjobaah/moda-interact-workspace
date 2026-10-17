---
id: ARCH-043-SHOPIFY-002
architecture_id: ARCH-043
title: Consume sealed Shopify OAuth bootstrap credentials
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
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

# Consume sealed Shopify OAuth bootstrap credentials

## Architecture

- Parent: `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Sealed-secret schema/security contract: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Owner: `moda_app` / `moda-interact`. This is a portable definition, **defined but not materialised**.

## Objective

Consume sealed Shopify OAuth bootstrap credentials.

## Context

ARCH-043 stores designated application secrets as encrypted JSON envelopes within `PlatformConfiguration`; the decrypt/unseal root is external and the audit remains redacted. Never convert an existing domain credential value to plaintext or alter pre-existing encrypted-credential AAD.

## Scope

- Load sealed shopify.oauth credentials before constructing the current synchronous shopifyApp client in app/shopify.server.js.
- Preserve Shopify token refresh and webhook HMAC verification, session storage and scopes.
- Prove bootstrapping, readiness and authenticated failure mode for unavailable DB/KMS without bypass or arbitrary fallback.
- Document and test safe OAuth secret rotation; keep no credentials in browser/Shopify admin responses.

## Out of Scope

- No existing Shopify webhook business filtering changes, Merchant Knowledge policy changes or service identity redesign.

## Requirements

- Protected Shopify ingress does not start with blank, stale-unbounded or unverified OAuth credentials.

## Work Items

- [ ] Load sealed shopify.oauth credentials before constructing the current synchronous shopifyApp client in app/shopify.server.js.
- [ ] Preserve Shopify token refresh and webhook HMAC verification, session storage and scopes.
- [ ] Prove bootstrapping, readiness and authenticated failure mode for unavailable DB/KMS without bypass or arbitrary fallback.
- [ ] Document and test safe OAuth secret rotation; keep no credentials in browser/Shopify admin responses.
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

- [ ] Protected Shopify ingress does not start with blank, stale-unbounded or unverified OAuth credentials.

## Validation

- [ ] OAuth/app start integration tests
- [ ] Webhook signature tests, typecheck/build
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
