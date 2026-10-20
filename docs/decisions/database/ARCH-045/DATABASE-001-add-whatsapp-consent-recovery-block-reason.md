---
id: ARCH-045-DATABASE-001
architecture_id: ARCH-045
title: Add WhatsApp consent-specific recovery block reason
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-045-BACKGROUND-002
  - ARCH-045-BACKGROUND-003
  - ARCH-045-SYSTEM-TEST-001
created: 2026-10-20
updated: 2026-10-20
---
# Add WhatsApp consent-specific recovery block reason

## Architecture

Architecture ID: `ARCH-045`
Architecture document: `docs/architecture/ARCH-045-shopify-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** portable definition, **not** materialised in a developer task worktree or committed/pushed; no execution claim exists.

## Objective

Extend the existing `RecoveryAdmissionBlockReason` enum so a consent-blocked `DETECTED` recovery is durable and distinguishable from capacity exhaustion and recipient reachability suppression.

## Context

The snapshot already has `CheckoutRecovery.admissionBlockedAt`, `admissionBlockReason`, `detectedAt` and customer/recovery indexes. There is no consent-specific reason. Add only the enum value and a safe corresponding Prisma migration; avoid speculative consent tables.

## Scope

- Add `WHATSAPP_CONSENT_MISSING` to `RecoveryAdmissionBlockReason` in `prisma/schema.prisma`.
- Generate the normal Database-owned migration, validate fresh database creation and the existing enum values, and prove the field round-trips through generated Prisma Client.
- Review existing `(shopId, admissionBlockReason, status, detectedAt)` and `(shopId,customerId,detectedAt,id)` indexes for exact queries; do not create another index unless measured need.

## Out of Scope

- No new `CheckoutRecoveryStatus`, stored marketing-consent Boolean, merchant notice rows, webhook handling or Background logic.
- No historical data backfill or guessed Shopify consent evidence.

## Requirements

- [ ] Existing values `RECOVERY_CAPACITY_EXHAUSTED` and `WHATSAPP_RECIPIENT_SUPPRESSED` remain unchanged.
- [ ] `DETECTED` recovery can be conditionally updated to the new reason with `admissionBlockedAt`; terminal recovery must not be reactivated.
- [ ] No schema for CRM/phone-based customer consent or new expiry column; initial expiry uses existing `detectedAt`.

## Work Items

- [ ] Implement enum + migration.
- [ ] Run Prisma validation, generated-client type proof and disposable PostgreSQL migration test.
- [ ] Document migration compatibility if production data/queues exist.

## Interfaces / Contracts

Prisma `RecoveryAdmissionBlockReason.WHATSAPP_CONSENT_MISSING` is consumed by BACKGROUND-002/003; no queue or provider contract is owned here.

## Dependencies

None

## Enables

- `ARCH-045-BACKGROUND-002`
- `ARCH-045-BACKGROUND-003`
- `ARCH-045-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Prisma Client recognises new reason and writes/reads it on a DETECTED recovery.
- [ ] No existing enum value or index was removed; migration passes fresh PostgreSQL rehearsal.
- [ ] No customer or recovery data is rewritten to assert consent.

## Validation

- [ ] Run repository-declared Prisma schema validation and migration checks.
- [ ] Run focused PostgreSQL integration round-trip and `git diff --check`.

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

Use the 2026-10-20 snapshot for orientation; revalidate active code/configuration when the task is materially claimed. ARCH-045's provisional 72-hour consent-wait deadline is the exact v1 task contract unless the developer and architect amend it before implementation.

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
