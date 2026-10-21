---
id: ARCH-046-BACKGROUND-003
architecture_id: ARCH-046
title: "Superseded: Woo consent-evidence recovery wakeups"
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 36
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-10-20
updated: 2026-10-21
---

# Superseded: Woo consent-evidence recovery wakeups

## Architecture

Architecture ID: `ARCH-046`

Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`

Coordinator: `moda_architect`

**Lifecycle:** portable definition from 2026-10-20 snapshot; not materialised, claimed, committed, implemented or architect-accepted. Status means definition eligibility only.

**Execution gate:** This task is intentionally `blocked` pending a separately approved Woo recovery lifecycle/live checkout-state contract, and must **not** be claimed merely because its enumerated task dependencies become Complete.

## Objective

**SUPERSEDED — DO NOT IMPLEMENT.** A Woo consent change updates `CustomerPhone` and immutable evidence, but does not schedule checkout lookup, recovery creation or any consent-specific background worklist.

## Context

The approved 2026-10-21 correction removes bounded evidence wakeups, lease/ack processing and later-consent direct recovery materialisation. A future **normal Woo checkout reconciliation**, if any, reads the current CustomerPhone through BACKGROUND-001 and applies the pre-creation gate in BACKGROUND-002. The separately approved Woo recovery engine remains unavailable in this snapshot.

## Scope

- No implementation; preserve task record as trace of withdrawn evidence-wakeup proposal.
- Remove this task from enabled/dependent recovery/system-test prerequisites.
- Do not introduce evidence processing metadata or a polling worker under any other task.

## Out of Scope

- Evidence poll/claim/ack/retry, old checkout scan, consent-driven candidate schedule, new Redis event/schema, first recovery materialisation and consent-only expiry.

## Requirements

- Consent ingestion stops after current phone + immutable audit commit.
- Only a legitimate subsequent **normal** checkout reconciliation can reconsider a checkout.

## Work Items

- [ ] Not applicable — superseded before execution. Do not claim.

## Interfaces / Contracts

None. Historical ARCH-046-DATABASE-001 immutable evidence is an audit fact only; API-001 is writer and BG001/002 read current CustomerPhone.

## Dependencies

None

## Enables

None

## Acceptance Criteria

- [ ] Not applicable — superseded task; no runtime code.

## Validation

- [ ] Verify no active task depends on this ID and no evidence-processing worklist is accidentally reintroduced.

## Stop Condition

Superseded. **Do not claim, execute, move to review or implement this task.** Preserve as historical definition.

## Implementation Notes

No code change. This portable task file records the architect decision to use ordinary recovery reconciliation only. Preserve `docs/decisions/**/_index.md` untouched until the documentation session closes.

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

Source is the supplied 2026-10-20 snapshot, not necessarily latest developer worktree. Versioned APIs/schema and future Woo recovery capability must be verified when eligible. Consent has no Moda-imposed waiting/expiry period. Recheck the current customer-phone permission and independently applicable checkout validity; do not invent a retention deadline.

### Unresolved Issues

External approved Woo recovery lifecycle/live checkout-state reader and independently accepted send/billing admission are currently missing; task remains Blocked.

### Architectural Concerns

None recorded beyond explicit context and gates.

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
