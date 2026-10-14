---
id: ARCH-039-BACKGROUND-001
architecture_id: ARCH-039
title: Migrate Background runtime credential readers to Shared
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
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
enables:
  - ARCH-039-GATEWAY-001
  - ARCH-039-SYSTEM-TEST-001
created: 2026-10-14
updated: 2026-10-14
---


# Migrate Background runtime credential readers to Shared

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_background` / `moda-interact-background`

## Objective

Migrate Background runtime credential readers to Shared. This is one bounded, repository-owned outcome; do not move to another task on completion.

## Context

ARCH-039 makes one published credential security mechanism authoritative for hosted Node services. The developer has chosen a non-production data clear rather than historical encryption-key migration. This task is part of the agreed staged adoption plan; see the parent architecture for exact cross-service invariants.

## Scope

- Replace `src/commerce/credential-keyring.ts` parser and generic `src/security/aes-gcm-credential.ts` crypto usage for in-scope OpenRouter and translation/embedding provider credential consumers.
- Retain existing worker domain error taxonomy and model/provider retry behaviour.

## Out of Scope

Woo grant read is BACKGROUND-002; do not modify API sources.

## Requirements

- Reader-only Background services consume canonical `COMMERCE_CONNECTION_KEYS_JSON`, never active-key selector or HMAC.
- Use Shared model AAD and AEAD; malformed/missing keyring is unavailable, not a plaintext/config fallback.
- No change to queue admission, billing, provider calls, stored versions or provider outcome behaviour.

## Work Items

- [ ] Migrate parser and production credential readers to Shared.
- [ ] Run focused Background credential tests including malformed env and tamper/missing key ID.
- [ ] Leave Woo-specific grant mapping for BACKGROUND-002.

## Interfaces / Contracts

- Published Shared Node keyring and AEAD; existing Shared OpenRouter/translation AAD contracts.

## Dependencies

- ARCH-039-SHARED-004

## Enables

- ARCH-039-GATEWAY-001
- ARCH-039-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Background generic credential handling uses only Shared parser and crypto.
- [ ] Read-only worker paths do not depend on active selector.
- [ ] Worker business/queue behaviour unchanged.

## Validation

- [ ] Focused Background credential/runtime tests
- [ ] Background typecheck and build (where provided)
- [ ] Changed-file lint and `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. For developer completion, an explicit developer approval is required after accepted review.

## Implementation Notes

Any local adapter remaining must be only a service-specific error mapping. Retain the local generic AES helper temporarily where Woo still imports it; delete it in BACKGROUND-002 after Woo migration.

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
