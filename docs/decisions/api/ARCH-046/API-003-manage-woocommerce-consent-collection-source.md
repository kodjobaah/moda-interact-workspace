---
id: ARCH-046-API-003
architecture_id: ARCH-046
title: Manage consent source on existing WooCommerceInstallation
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 23
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-046-DATABASE-001
enables:
  - ARCH-046-API-001
  - ARCH-046-WOOCOMMERCE-005
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
created: 2026-10-20
updated: 2026-10-21
---

# Manage consent source on existing WooCommerceInstallation

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from the 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status represents definition eligibility only.

## Objective

Expose authenticated, durable Woo merchant consent collector selection, persisted on **existing `WooCommerceInstallation`** with epoch fencing for customer-phone grants.

## Context

A WordPress-local checkbox setting is not a reliable Background authority. DATABASE-001 extends the installation record instead of creating a source-configuration table. Merchant UI consumes this through a privileged server-side proxy.

## Scope

- Implement narrow versioned authenticated read/update for connected Woo installation's own `shopId`; never accept caller-chosen tenant. Read/write installation `consentSourceMode`, provider ID and `consentSourceEpoch` with concurrency-safe optimistic revision.
- Support default `NOT_CONFIGURED`, `MODA_CHECKBOX`, and `SUPPORTED_EXTERNAL` **only** with a specifically approved and enabled provider adapter. No external adapter is certified by this snapshot, so the external choice is unavailable until separately reviewed.
- Increment epoch on actual mode/provider switch only; do not rotate on idempotent no-op. Existing customer-phone grant and append-only decision evidence remain historically intact, but **epoch mismatch** makes the old grant ineligible for future sends. A merchant configuration switch must **not** manufacture a customer grant/withdrawal event. API outage must not claim a successful switch.
- Return safe current source, provider availability and epoch to privileged WordPress UI; validate and report auth/stale/provider errors without exposing secrets.

## Out of Scope

- No new config table, Woo storefront checkbox, consent grant, automatic third-party plugin detection, cookie tracking or recovery send.

## Requirements

- [ ] Hosted installation mode/epoch is authoritative and tenant-scoped.
- [ ] Switching source invalidates **grant eligibility**, not the existence of a historical consent event, and cannot itself authorise a customer send.

## Work Items

- [ ] Extend existing installation-authenticated API read/update path with mode and epoch fencing.
- [ ] Test stale/concurrent update, no-op, provider unavailable, auth/tenant denial and DB outage.

## Interfaces / Contracts

Consumes DATABASE-001 `WooCommerceInstallation` fields; returns versioned source mode, provider and epoch. Used by WOOCOMMERCE-005 and API-001. No new cross-repository Shared contract.

## Dependencies

- `ARCH-046-DATABASE-001`

## Enables

- `ARCH-046-API-001`
- `ARCH-046-WOOCOMMERCE-005`
- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] No standalone source-config record; mode/epoch stored only on Woo installation.
- [ ] Old epoch grant ineligible after source switch and no insecure API fallback or cross-tenant updates.

## Validation

- [ ] Focused authenticated route, Prisma transaction and concurrent update tests; OpenAPI/typecheck/build commands actually defined by repo; `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, record launcher-resolved dedicated parent/implementation worktrees, physical isolation and start-of-attempt synchronization evidence in the Completion Report. Set status `review`, return to `moda_architect`, and **STOP**. Do not execute a dependent task.

## Implementation Notes

This is the host authority, not a second cookie CMP. Do not introduce a generic provider integration plugin ecosystem merely to implement the setting. Use `@modainteract/moda-interact-shared/logging` for bounded Node diagnostics, never log personal consent payloads, tokens or raw recipient phones. Inspect the actual repository scripts and agent VCS/isolation policies before executing.

## Completion Report

### Status

Not Started — portable, not materialised.

### Files Changed

None — no runtime implementation in this documentation patch.

### Work Completed

None.

### Validation Results

Not run by a repository agent; no developer worktree/remote access is available from this snapshot.

### Deviations

None.

### Assumptions

Source is the supplied 2026-10-20 snapshot; no external provider is presently certified.

### Unresolved Issues

None recorded at definition time. External vendor adapter implementation must be separately approved when a real vendor is nominated.

### Architectural Concerns

None recorded beyond explicit source and recovery gates.

## Architect Review

### Review Status

Pending — no implementation reviewed or accepted.

### Review Notes

None.

### Reviewed Files

None — portable definition only.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.
