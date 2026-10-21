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
  - ARCH-045-DATABASE-002
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

- Implement installation-authenticated read/update of `consentSourceMode`, approved provider ID and monotonic `consentSourceEpoch` on the existing WooCommerceInstallation row; derive shop from credentials, never caller-selected shop ID.
- Support `NOT_CONFIGURED` (default), `MODA_CHECKBOX`, and `SUPPORTED_EXTERNAL` only when a specific adapter is architect-approved and enabled. No external provider certified by this snapshot.
- On a real source/provider switch increment epoch atomically; BACKGROUND-001/current consent admission must reject previous-epoch grants until a verified decision is recorded using the active source. Preserve historical Woo evidence.
- Only update merchant source configuration; do **not** publish a consent-change recovery job, scan customer/checkouts or silently grant consent.

## Out of Scope

- No new config table, Woo storefront checkbox, consent grant, automatic third-party plugin detection, cookie tracking or recovery send.

## Requirements

- [ ] Installation tenant-scoped merchant source/epoch is authoritative, independent from each customer phone permission.
- [ ] A settings change is never WhatsApp consent and never triggers recovery; stale grants are ineligible through epoch check.

- **H4:** Source-epoch changes must be strictly monotonic under a single DB row lock/conditional update. A switch `MODA -> EXTERNAL -> MODA` is not epoch-equivalent to the initial Moda configuration; stale in-flight grants and evidence cannot become current eligibility.
- Reject disabled source and unapproved third-party provider even if a Woo plugin still displays an earlier checkbox; preserve local STOP override and consent evidence on source switch.

## Work Items

- [ ] Extend existing installation-authenticated API read/update path with mode and epoch fencing.
- [ ] Test stale/concurrent update, no-op, provider unavailable, auth/tenant denial and DB outage.

## Interfaces / Contracts

Reads/writes ARCH-045-DATABASE-002 WooInstallation source/provider/epoch; Woo settings client WOOCOMMERCE-005. ARCH-046-API-001 checks source before writing current CustomerPhone and audit evidence; Background-001 checks on each normal reconciliation. No Shared queue or recovery wakeup.

## Dependencies

- `ARCH-045-DATABASE-002`

## Enables

- `ARCH-046-API-001`
- `ARCH-046-WOOCOMMERCE-005`
- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Mode/provider/epoch idempotently persist for correct installation, source switch blocks old grants without deleting evidence.
- [ ] No third-party integration selectable without certified adapter; no queue/recovery side effects from updating setting.

- [ ] Parallel admin source changes, consent submissions, credential rotation and ABA source sequence never revive old grants; no change queues checkout work.

## Validation

- [ ] Focused authenticated route, Prisma transaction and concurrent update tests; OpenAPI/typecheck/build commands actually defined by repo; `git diff --check`.

- [ ] PostgreSQL concurrency fixtures for source changes vs in-flight consent API writes and forged/stale provider selection.

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
