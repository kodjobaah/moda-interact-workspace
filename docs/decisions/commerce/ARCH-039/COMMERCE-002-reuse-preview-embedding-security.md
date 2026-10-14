---
id: ARCH-039-COMMERCE-002
architecture_id: ARCH-039
title: Migrate Commerce Preview and embedding credential readers to Shared
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-039-SHARED-004
  - ARCH-039-COMMERCE-001
enables:
  - ARCH-039-GATEWAY-001
  - ARCH-039-SYSTEM-TEST-001
created: 2026-10-14
updated: 2026-10-14
---


# Migrate Commerce Preview and embedding credential readers to Shared

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_commerce` / `moda-interact-commerce`

## Objective

Migrate Commerce Preview and embedding credential readers to Shared. This is one bounded, repository-owned outcome; do not move to another task on completion.

## Context

ARCH-039 makes one published credential security mechanism authoritative for hosted Node services. The developer has chosen a non-production data clear rather than historical encryption-key migration. This task is part of the agreed staged adoption plan; see the parent architecture for exact cross-service invariants.

## Scope

- Replace Preview OpenRouter and Merchant Knowledge embedding AES-GCM implementations with published Shared open and AAD builders.
- Fix `lib/preview/runtime.ts` malformed keyring handling so optional Preview disablement cannot mask invalid enabled configuration.

## Out of Scope

No Studio UX redesign or external connection command changes.

## Requirements

- Consume the canonical keyring from the Commerce server adapter established by COMMERCE-001.
- Wrong environment/provider/purpose/key ID/authentication and corrupted envelope fail closed.
- Preserve preview abort semantics, retriable versus non-retriable outcomes, logging redaction and embedding provider/model validation.

## Work Items

- [ ] Migrate Preview resolver and Merchant Knowledge embedding runtime to published Shared APIs.
- [ ] Remove duplicate local AAD/envelope/plaintext validation and unsafe empty-config fallback.
- [ ] Test failure reasons and cross-service vectors.

## Interfaces / Contracts

- Published Shared AEAD/keyring; existing Shared OpenRouter AAD and new embedding AAD builder.

## Dependencies

- ARCH-039-SHARED-004
- ARCH-039-COMMERCE-001

## Enables

- ARCH-039-GATEWAY-001
- ARCH-039-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Preview/OpenRouter and embedding readers use shared security implementation.
- [ ] Invalid configured keyring does not become a silent empty ring.
- [ ] Preview/test conversation cancellation and provider selection semantics remain intact.

## Validation

- [ ] Focused Commerce Preview and embedding runtime tests
- [ ] Commerce typecheck and build
- [ ] Changed-file lint and `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. For developer completion, an explicit developer approval is required after accepted review.

## Implementation Notes

Domain-specific safe error categorisation can remain as an adapter around Shared exceptions.

Use the canonical parent/implementation task-worktree preparation protocol, preserve dedicated worktree and start-of-attempt synchronization evidence, and do not edit `docs/decisions/**/_index.md` before architecture-session confirmation. No direct changes to another agent's repository.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None beyond the parent architecture.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Not yet reviewed.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending review.

### Follow-up

None.
