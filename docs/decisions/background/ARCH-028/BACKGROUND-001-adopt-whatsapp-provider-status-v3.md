---
id: ARCH-028-BACKGROUND-001
architecture_id: ARCH-028
title: Adopt WhatsApp provider-status v3 and explicit status transitions
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
  - ARCH-028-DATABASE-001
  - ARCH-028-SHARED-002
enables:
  - ARCH-028-MESSAGING-001
created: 2026-10-03
updated: 2026-10-07
---

# Adopt WhatsApp provider-status v3 and explicit status transitions

## Architecture

Architecture ID: `ARCH-028`

Architecture document: `docs/architecture/ARCH-028-whatsapp-delivery-failure-convergence.md`

Coordinator: `moda_architect`

## Objective

Adopt the exact published dual-version WhatsApp provider-status contract, persist bounded provider failure evidence, and replace the unsafe numeric status rank with explicit delivery-state transitions while preserving delivered-usage and retry semantics.

## Context

Current `STATUS_RANK` orders `FAILED < SENT`, so a late SENT can resurrect a failed message. ARCH-028 requires a partial transition lattice instead.

This remains a consumer/evidence task. It does not classify provider codes or compensate/reachability/notify.

## Scope

Update the exact published Shared dependency, accepted database submodule, `whatsapp-provider-status.service.ts`, and focused tests.

Explicit transitions:

```text
PENDING -> SENT | DELIVERED | READ | FAILED
SENT -> DELIVERED | READ | FAILED
FAILED -> DELIVERED | READ
DELIVERED -> READ
READ -> no later state
```

A late SENT from FAILED/DELIVERED/READ is ignored. DELIVERED/READ may supersede FAILED as stronger positive evidence. Historical failure evidence is retained.

For v3 FAILED persist bounded `providerFailureCode` and `failedAt`; v2 FAILED may persist `failedAt` without inventing a code. Replayed v3 FAILED may enrich a null failure code on an already-FAILED message.

## Out of Scope

- Meta webhook parsing/production.
- Provider-code classification.
- RecoveryOutreachAttempt/follow-up mutation.
- Reachability/suppression.
- Compensation/hard-limit correction.
- Synchronous send rejection.
- Merchant notification.

## Requirements

- [ ] Consume exact SHARED-002 package and accepted DATABASE-001 fields.
- [ ] Accept v2 and v3 through canonical Shared parser.
- [ ] Replace numeric total rank with explicit allowed transitions.
- [ ] FAILED -> SENT is impossible.
- [ ] FAILED -> DELIVERED/READ is permitted.
- [ ] DELIVERED/READ never regress to FAILED/SENT.
- [ ] Persist bounded failure evidence and allow idempotent evidence enrichment.
- [ ] Preserve one idempotent `DELIVERED_WHATSAPP_MESSAGE` usage event and Serializable/CAS retry behaviour.

## Work Items

- [ ] Upgrade exact Shared package and database gitlink.
- [ ] Implement explicit status transition helper/lattice.
- [ ] Persist v3 failure evidence and v2 failedAt semantics.
- [ ] Add replay/enrichment and out-of-order tests, including FAILED then SENT.
- [ ] Preserve delivered usage/accounting tests.

## Interfaces / Contracts

Consumes `NormalizedWhatsAppStatus` v2/v3 from `@modainteract/moda-interact-shared/billing` and DATABASE-001 message fields.

## Dependencies

- `ARCH-028-DATABASE-001`
- `ARCH-028-SHARED-002`

## Enables

- `ARCH-028-MESSAGING-001`

## Acceptance Criteria

- [ ] FAILED cannot be resurrected by SENT.
- [ ] DELIVERED/READ may supersede FAILED and clear no historical failure fields.
- [ ] v2/v3 compatibility and failure enrichment are idempotent.
- [ ] Unknown/non-outbound/unowned handling remains bounded.
- [ ] Delivered usage identity/accounting is unchanged.
- [ ] No ARCH-028 recovery/reachability/compensation policy is introduced.

## Validation

Run repository-declared Prisma generation/validation, focused provider-status tests, unit/full tests, build and `git diff --check` as declared by the current repository.

## Stop Condition

Complete report -> `review` -> return to `moda_architect` -> STOP.

## Implementation Notes

Do not encode the lattice as another arbitrary numeric rank. Make allowed transitions explicit and test every contested edge.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

Not Started.

### Validation Results

Not Run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
