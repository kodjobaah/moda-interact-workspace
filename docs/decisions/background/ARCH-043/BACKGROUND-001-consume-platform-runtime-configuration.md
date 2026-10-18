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

Replace scoped Woo coupon and speech transcription environment policies with validated `PlatformConfiguration` reads, while resolving **support-message translation model selection** from existing enabled `CommerceTranslationModelConfiguration` automatic default, not a second `support.translation` row. Commerce keyring and Shopify OAuth belong to BACKGROUND-002.

## Context

Existing BackgroundRuntimeConfig remains untouched and continues governing its current domains.

## Scope

- Add a trusted-environment PostgreSQL configuration reader with service-owned strict validation; fetch once per relevant job/work cycle with no cross-operation cache or stale fallback.
- Replace Woo coupon sync environment tuning reads for nine settings plus worker concurrency with the supported `woo.couponSync` key.
- Read `speech.transcription` for speech only. For new support-message translation jobs, select the existing enabled `CommerceTranslationModelConfiguration` automatic default in the correct Commerce environment, not `support.translation`; retain the existing job's selected model for queued/claimed work and preserve unrelated pricing/category workflows.
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
- [ ] Read `speech.transcription` for speech. Resolve enabled automatic `CommerceTranslationModelConfiguration` model for new support-message translations only; preserve existing queued-job models and other translation flows.
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

### 18 October support translation selection review gate

- Inspect where new `MerchantMessageTranslation` work and its batch model are first selected. Require a valid enabled automatic default from `CommerceTranslationModelConfiguration` before creating new support translation work; do **not** overwrite existing queued/claimed model IDs or `BackgroundRuntimeConfig` cadence.
- Reconcile any existing `support.translation` stored model against the automatic default and record explicit operator approval if outcomes change. The legacy row becomes migration-only, not a fallback or competing source.
- Validate deployment-to-`CommerceEnvironment` mapping and no-default/disabled/missing-model error. Coordinate with BACKGROUND-009 existing OpenAI credential resolver; do not add a new Admin translation credential or secret-purpose write.


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
