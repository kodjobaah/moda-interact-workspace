---
id: ARCH-045-DATABASE-001
architecture_id: ARCH-045
title: "Superseded: WhatsApp consent recovery admission enum"
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-20
updated: 2026-10-20
---
# Superseded: WhatsApp consent recovery admission enum

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** portable definition, **not** materialised in a developer task worktree or committed/pushed; no execution claim exists.

## Objective

**SUPERSEDED — DO NOT IMPLEMENT.** Initial missing WhatsApp consent does not create a `CheckoutRecovery`, so no `RecoveryAdmissionBlockReason.WHATSAPP_CONSENT_MISSING` migration is required.

## Context

The 2026-10-20 design correction moves the consent check before the existing `RecoveryInitiationService` persists a recovery. Existing enum values for *already created* capacity/recipient-suppressed recoveries remain unchanged. Shopify stores its own WhatsApp consent.

## Scope

- No implementation. Retain this canonical task record for traceability of the withdrawn enum proposal.
- If a developer already materialised or applied this task on the **actual** branch, refer existing migration/commits to `moda_architect` for reconciliation; do not silently delete a deployed migration.

## Out of Scope

- No Prisma enum change, recovery table change, consent table, data backfill or runtime implementation.

## Requirements

- No `CheckoutRecovery` may be created merely because consent is missing.
- The authoritative current Shopify consent is read from Shopify, not duplicated in Moda.

## Work Items

- [ ] None — superseded; must not be claimed or executed.

## Interfaces / Contracts

None. Existing `RecoveryAdmissionBlockReason` and Shopify recovery schema are unchanged.

## Dependencies

None

## Enables

None — all prior downstream dependencies on this task are removed.

## Acceptance Criteria

- [ ] Not applicable — task superseded before execution in supplied portable baseline.

## Validation

- [ ] No source validation required for a superseded unexecuted proposal; verify no active task depends on this ID.

## Stop Condition

After completing only the defined Work Items, Acceptance Criteria and required Validation, record the canonical task worktree/branch and start-of-attempt synchronization evidence, populate the Completion Report, set `status: review`, return control to `moda_architect` and **STOP**. Do not launch enabled or unrelated tasks. For publication task, do not rerun implementation validation.

## Implementation Notes

Use the normal migrations directory; do not edit copies of database schema in dependent service submodules as separate owners.

Before claiming, use the deterministic `/moda-task` launcher and its **actual** prepared packet, read the task's complete current Architect Review, and verify task/dependency status in the developer's canonical workspace. Preserve `docs/decisions/**/_index.md` untouched until the developer explicitly closes the architecture documentation session. New runtime structured logging uses `@modainteract/moda-interact-shared/logging` where applicable. No source outside this task's owner repository may be changed unless explicitly authorised by the architecture.

## Completion Report

### Status

Not Started — external portable definition, not materialised.

### Files Changed

None — not implemented.

### Work Completed

None.

### Validation Results

Not run; the supplied snapshot is not the developer's task worktree.

### Deviations

None.

### Assumptions

Use the 2026-10-20 snapshot only as a baseline; verify current active code on task claim. Consent has no fixed 72-hour wait or expiry; checkout eligibility follows the authoritative lifecycle.

### Unresolved Issues

None recorded at definition time; report any discovered cross-repository dependency rather than implementing outside ownership.

### Architectural Concerns

None recorded at definition time.

## Architect Review

### Review Status

Pending — no implementation reviewed.

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
