---
id: ARCH-046-API-003
architecture_id: ARCH-046
title: Read and change authoritative Woo WhatsApp consent collection source
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
updated: 2026-10-20
---

# Read and change authoritative Woo WhatsApp consent collection source

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from the 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status represents definition eligibility only.

## Objective

Provide one authenticated, durable, shop-scoped consent-source configuration API whose epoch invalidates prior checkout grants whenever the merchant switches collection sources.

## Context

WordPress checkout display settings alone cannot protect Background sending after a source switch; the hosted system must know which collector is authoritative. DATABASE-001 stores the source configuration. The merchant's existing WordPress admin UI will consume this API through a privileged server-side proxy under WOOCOMMERCE-005.

## Scope

- Define narrow versioned read/update routes for the authenticated Woo installation's `shopId`; do not accept arbitrary shop identifiers from callers. Use existing Woo installation authentication and strict input validation.
- Support `NOT_CONFIGURED` (initial default), `MODA_CHECKBOX`, and `SUPPORTED_EXTERNAL` with a required exact allowlisted provider ID. Never allow external mode without an architect-approved, versioned, enabled adapter certification in the deployed plugin; no provider is presently certified. Treat external mode as unavailable until that prerequisite exists.
- Transactionally update source configuration and monotonically increment configuration epoch for every actual mode/provider change; unchanged idempotent update must not rotate epoch. Require optimistic revision/check to prevent racing admin updates.
- Return the committed source mode/provider/epoch and safe display capabilities; reject unauthorised, stale, unapproved-provider and malformed writes with clear codes. API failure does not acknowledge a source switch or grant.

## Out of Scope

- No checkout opt-in ingestion; API-001 owns consent events. No third-party vendor adapter, automatic checkbox recognition, cookie-consent integration, recovery send or direct browser-to-Moda secret exposure.
- No standalone Woo recovery settings UI; WOOCOMMERCE-005 owns the WordPress admin presentation and capability/nonce check.

## Requirements

- `NOT_CONFIGURED` means no authorised outbound recovery, even if historical GRANTED records remain; previously stored grants must not automatically become valid if the merchant switches back to a former source.
- Configuration epoch is current hosted truth; new consent events must be stamped against it by API-001 and checked by BACKGROUND-001. Every source change invalidates grants from a former epoch without global checkout scans.
- The WordPress plugin may cache **only acknowledged** settings for checkout UI; on API errors it cannot claim successful merchant configuration.

## Work Items

- [ ] Define strict authenticated read/update DTO, supported-source registry check and documented error semantics.
- [ ] Implement source configuration transactions with optimistic concurrency, no-op idempotency and epoch bump on changes.
- [ ] Test disabled/default, approved Moda, denied unknown provider, stale update, concurrency, revoked installation and cross-tenant access.

## Interfaces / Contracts

API-owned versioned Woo consent-source configuration read/update contract consumed by WOOCOMMERCE-005 and used as current-authority input by API-001. Canonical Prisma model is DATABASE-001; no new Shared package needed for the existing PHP-to-HTTPS API boundary. Exact route names are owned by this task rather than presumed deployed.

## Dependencies

- `ARCH-046-DATABASE-001`

## Enables

- `ARCH-046-API-001`
- `ARCH-046-WOOCOMMERCE-005`
- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

## Acceptance Criteria

- [ ] Only a connected authorised Woo installation can read/change its own source, never another tenant's.
- [ ] Initial missing configuration is NOT_CONFIGURED; changing source/provider increments epoch atomically, while identical idempotent update does not.
- [ ] Unsupported/unapproved external provider cannot become active, even if another plugin advertises a checkbox.
- [ ] Repeated source switches cannot reactivate historical grants from a previous epoch; API failure cannot report source-change success.

## Validation

- [ ] Focused API auth/contract and disposable PostgreSQL config epoch/idempotency/concurrency tests.
- [ ] Repository-declared typecheck/lint/build for changed surface and `git diff --check`.

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
