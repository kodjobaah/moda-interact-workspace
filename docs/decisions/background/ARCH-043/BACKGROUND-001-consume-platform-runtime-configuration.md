---
id: ARCH-043-BACKGROUND-001
architecture_id: ARCH-043
title: Load operational policies from platform configuration
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
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

# Load operational policies from platform configuration

## Architecture

- Architecture: `ARCH-043` — `docs/architecture/ARCH-043-database-managed-platform-configuration.md`.
- Proposed schema/key contract: `docs/architecture/ARCH-043-configuration-schema-review.md`.
- Repository owner: `moda-interact-background` / `moda_background`.
- Portable definition only: **defined but not materialised**; task worktrees, claims and Git commits must be established by normal task launcher.

## Objective

Replace the scoped non-secret Woo coupon, speech transcription and support-message translation environment readers with fresh validated `PlatformConfiguration` reads per relevant job/work cycle. Commerce keyring and Shopify OAuth secret readers belong to BACKGROUND-002.

## Context

Existing BackgroundRuntimeConfig remains untouched and continues governing its current domains.

## Scope

- Add a trusted-environment PostgreSQL configuration reader with service-owned strict validation; fetch once per relevant job/work cycle with no cross-operation cache or stale fallback.
- Replace Woo coupon sync environment tuning reads for nine settings plus worker concurrency with the supported `woo.couponSync` key.
- Read `speech.transcription` and `support.translation` only for their owning flows, without changing provider secrets or Commerce product/pricing translation.
- Document which worker controls can update live and which require restart; safely handle invalid/unavailable database configuration.

## Out of Scope

- No credential/keyring/Shopify OAuth secret cutover; owned separately by BACKGROUND-002.

## Requirements

- Read PostgreSQL once at the beginning of each relevant business operation/job/work cycle. Do not query on every unrelated Shopify event or WhatsApp turn, and do not reuse a snapshot in a later operation.
- Preserve hard service caps and existing credential environment sources.
- No fallback to deprecated policy env once the migration is explicitly cut over; maintain safe no-row defaults where approved.
- If worker concurrency cannot change safely at runtime, require explicit restart/rollout without duplicate consumers.

## Work Items

- [ ] Add a trusted-environment PostgreSQL configuration reader with service-owned strict validation; fetch once per relevant job/work cycle with no cross-operation cache or stale fallback.
- [ ] Replace Woo coupon sync environment tuning reads for nine settings plus worker concurrency with the supported `woo.couponSync` key.
- [ ] Read `speech.transcription` and `support.translation` only for their owning flows, without changing provider secrets or Commerce product/pricing translation.
- [ ] Document which worker controls can update live and which require restart; safely handle invalid/unavailable database configuration.
- [ ] Record actual files changed, validation results, worktree isolation and Completion Report; stop at Review.

## Interfaces / Contracts

- `PlatformConfiguration` and `PlatformConfigurationAudit` are owned by `ARCH-043-DATABASE-001`; schema supports typed non-secret objects and sealed envelopes; environment-scoped and redacted in audit.
- Closed policy shapes are specified in `docs/architecture/ARCH-043-configuration-schema-review.md`. Admin validates before writes; each service independently validates the configuration it consumes. No ARCH-043 Shared publication is required.
- Existing billing, tenant, provider credential and bootstrap contracts retain their established owners.

## Dependencies

- `ARCH-043-DATABASE-001`

## Enables

- `ARCH-043-GATEWAY-001`
- `ARCH-043-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Read PostgreSQL once at the beginning of each relevant business operation/job/work cycle. Do not query on every unrelated Shopify event or WhatsApp turn, and do not reuse a snapshot in a later operation.
- [ ] Preserve hard service caps and existing credential environment sources.
- [ ] No fallback to deprecated policy env once the migration is explicitly cut over; maintain safe no-row defaults where approved.
- [ ] If worker concurrency cannot change safely at runtime, require explicit restart/rollout without duplicate consumers.
- [ ] The bounded task implementation passes the specified validation without regressions to existing domain configuration.

## Validation

- [ ] Woo sync and speech/provider policy unit coverage
- [ ] Fresh-read-after-revision-change and DB outage tests
- [ ] Worker restart/ownership and bounded per-relevant-operation DB query regression
- [ ] Typecheck/lint/build

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
