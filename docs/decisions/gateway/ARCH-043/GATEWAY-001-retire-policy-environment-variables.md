---
id: ARCH-043-GATEWAY-001
architecture_id: ARCH-043
title: Remove retired application-policy environment variables
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-043-ADMIN-001
- ARCH-043-ADMIN-002
- ARCH-043-ADMIN-002
- ARCH-043-BACKGROUND-001
- ARCH-043-BACKGROUND-002
- ARCH-043-API-001
- ARCH-043-API-002
- ARCH-043-API-003
- ARCH-043-COMMERCE-001
- ARCH-043-COMMERCE-002
- ARCH-043-SHOPIFY-001
- ARCH-043-SHOPIFY-002
- ARCH-043-MCP-001
- ARCH-043-ADMIN-004
- ARCH-043-API-004
- ARCH-043-BACKGROUND-008
- ARCH-043-BACKGROUND-009
- ARCH-043-SHOPIFY-003
enables:
- ARCH-043-SYSTEM-TEST-001
created: '2026-10-17'
updated: '2026-10-17'
---

# Remove retired application-policy environment variables

## Architecture

- Architecture: `ARCH-043` — `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Proposed schema/key contract: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Repository owner: `moda-interact-gateway` / `moda_gateway`.
- Portable definition only: **defined but not materialised**; task worktrees, claims and Git commits must be established by normal task launcher.

## Objective

Remove proven-unused environment declarations for policy and approved application secrets **only after** authenticated database-backed consumers and their secret import/rotation gates are accepted.

## Context

Gateway owns the Render Blueprints and deployment topology, not repository consumer source.

## Scope

- Review the Render Blueprint and environment-specific configuration for both policy and secret variables.
- Remove Commerce keyring/active ID and supported AUTH_SECRET/Google/Shopify OAuth declarations only when each participating consumer demonstrates secure DB-only startup, rotation and recovery. **Do not remove META_APP_SECRET or WHATSAPP_VERIFY_TOKEN from Messaging**: that integration is excluded from ARCH-043.
- Keep `DATABASE_URL`, Redis, deploy identity/URLs, `OTEL_*` and the externally managed `MODA_CONFIG_UNSEAL_KEY` or KMS identity; never commit the root value.
- Verify that the optional private API-003 endpoint is not publicly reachable, enforces service identity, and cannot be called without an approved identity. Do not establish API-to-Messaging connectivity. Record environment-specific rollback matrix.

## Out of Scope

- No deletion of DB state, secrets, consumers, unrelated config and no promotion of system-test dependencies into this task.

## Requirements
### 17 October 2026 reconciliation guardrails

Do not remove `AUTH_SECRET`, `AUTH_GOOGLE_ID`, or `AUTH_GOOGLE_SECRET` for Admin/Commerce: they are deliberate fallback bundles on **absent** DB auth records and are resolved only on authentication requests. Keep `AUTH_URL`, `WOO_BILLING_ENVIRONMENT`, `MODA_WOO_REST_READ_PUBLIC_ORIGIN`, cryptographic unwrap roots, and Meta webhook verification (`META_APP_SECRET`/`WHATSAPP_VERIFY_TOKEN`) external. Retire only per-service credential names actually made obsolete by the eight additional accepted consumer tasks, with a rollback matrix; never assume that an Admin UI setting automatically migrates all consumers.


- Maintain test/production separation and no secret values in Blueprint.
- Render topology remains deployable with all independent service startups.

## Work Items

- [ ] Audit `render.test.yaml`, `render.production.yaml` and canonical `render.yaml` where applicable for policy variables replaced by ARCH-043.
- [ ] Remove obsolete settings only after the owning consumer explicitly proves database-only behaviour and safe rollback.
- [ ] Keep required bootstrap variables, Messaging Meta verification credentials, other public-ingress credentials not migrated by an accepted consumer, DB/Redis, OTEL and Woo-plugin local connection environment variables.
- [ ] Record environment-specific deploy sequencing and a rollback table.
- [ ] Record actual files changed, validation results, worktree isolation and Completion Report; stop at Review.

## Interfaces / Contracts

- `PlatformConfiguration` and `PlatformConfigurationAudit` are owned by `ARCH-043-DATABASE-001`; schema supports typed non-secret objects and sealed envelopes; environment-scoped and redacted in audit.
- Closed policy shapes are specified in `docs/architecture/ARCH-043-configuration-schema-review.md`. Admin validates before writes; each service independently validates the configuration it consumes. No ARCH-043 Shared publication is required.
- Existing billing, tenant, provider credential and bootstrap contracts retain their established owners.

## Dependencies

- `ARCH-043-ADMIN-001`
- `ARCH-043-ADMIN-002`
- `ARCH-043-BACKGROUND-001`
- `ARCH-043-BACKGROUND-002`
- `ARCH-043-API-001`
- `ARCH-043-API-002`
- `ARCH-043-API-003`
- `ARCH-043-COMMERCE-001`
- `ARCH-043-COMMERCE-002`
- `ARCH-043-SHOPIFY-001`
- `ARCH-043-SHOPIFY-002`
- `ARCH-043-MCP-001`

## Enables

- `ARCH-043-SYSTEM-TEST-001`

### Fresh pre-production configuration ownership

No `MODA_ARCH043_DISABLE_LEGACY_POLICY_EDITORS` flag exists and Gateway must not create or enable one. ADMIN-002 removes duplicate R2 and support translation editor keys directly. Consumers move to canonical `merchant.knowledge.r2` and the existing Commerce translation provider/model authority, respectively. Gateway should only retire provider environment variables actually superseded by independently accepted reader tasks; keep infrastructure/authentication fallback variables under the approved boundary.

## Acceptance Criteria

- [ ] Maintain test/production separation and no secret values in Blueprint.
- [ ] Render topology remains deployable with all independent service startups.
- [ ] The bounded task implementation passes the specified validation without regressions to existing domain configuration.

## Validation

- [ ] Blueprint parser/validation and diff review
- [ ] Deployment environment matrix/roll-back check

## Stop Condition

Complete the defined scope and required validation, update the task and Completion Report to Review, return to `moda_architect`, and STOP. No execution of enabled tasks and no `_index.md` edits.

## Implementation Notes

- Preserve service ownership boundaries and existing published ARCH-039 credential functions. Use the ARCH-043 documented policy shapes and AAD byte convention; do not invent a new crypto codec or require new Shared publication.
- Changes to shared generic logging, if needed, must use `@modainteract/moda-interact-shared/logging`.
- Use launcher-resolved dedicated task worktrees and start-of-attempt synchronisation evidence.

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

Awaiting implementation, validation evidence and architect decision.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Not yet assessed.

### Follow-up

None

## 17 October 2026 ARCH-043 extension (architect-owned amendment)

Do not remove Admin/Commerce Auth.js env credentials until ADMIN-002 and COMMERCE-002 demonstrate DB bootstrap/rotation; remove R2/env upload fields only after all API/Shopify/Background consumers use the single sealed record. Do not remove merchant-specific WooCommerce REST credentials; global `woocommerce.auth` has no approved runtime consumer.
