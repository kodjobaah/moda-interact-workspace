---
id: ARCH-039-API-002
architecture_id: ARCH-039
title: Migrate Woo REST-read grant AES-GCM implementation to Shared
task_kind: implementation
domain: api
repository: moda-interact-api
assigned_agent: moda_api
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
  - ARCH-039-API-001
enables:
  - ARCH-039-GATEWAY-001
  - ARCH-039-SYSTEM-TEST-001
created: 2026-10-14
updated: 2026-10-14
---


# Migrate Woo REST-read grant AES-GCM implementation to Shared

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_api` / `moda-interact-api`

## Objective

Migrate Woo REST-read grant AES-GCM implementation to Shared. This is one bounded, repository-owned outcome; do not move to another task on completion.

## Context

ARCH-039 makes one published credential security mechanism authoritative for hosted Node services. The developer has chosen a non-production data clear rather than historical encryption-key migration. This task is part of the agreed staged adoption plan; see the parent architecture for exact cross-service invariants.

## Scope

- Replace crypto and duplicated Woo grant AAD in `src/woocommerce/rest-read/envelope.ts` with published Shared seal/open and Woo AAD builder.
- Keep the existing Woo grant database fields and API business validation.

## Out of Scope

No database schema migration or provider API redesign.

## Requirements

- AES key/ID comes only from API-001 canonical configuration.
- Shared AEAD seals canonical Woo consumer key/secret JSON payload; API remains responsible for value validation, cleanup, tenant/installation binding and error mapping.
- No backwards reader or re-encryption migration: pre-production encrypted grants are developer-cleared before cutover.

## Work Items

- [ ] Migrate envelope functions and related tests to Shared.
- [ ] Prove API encrypt -> Background-compatible AAD/vector (through contract tests); tampering and tenant mismatch fail.
- [ ] Confirm no `createCipheriv`/`createDecipheriv` duplicate remains for this grant path.

## Interfaces / Contracts

- Published Shared Node crypto + `createWooRestReadGrantAad`; stable existing Woo grant fields.

## Dependencies

- ARCH-039-SHARED-004
- ARCH-039-API-001

## Enables

- ARCH-039-GATEWAY-001
- ARCH-039-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] API-produced grants use shared encryption and the exact shared Woo AAD.
- [ ] No competing Woo AES implementation or local AAD clone remains.
- [ ] Grant authorisation, revocation and secret handling remain strict.

## Validation

- [ ] Focused API Woo read-grant and authorisation tests
- [ ] API integration tests using disposable Postgres where required/available
- [ ] API typecheck/build and `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. For developer completion, an explicit developer approval is required after accepted review.

## Implementation Notes

The independent Background consumer task remains responsible for its own tenant/runtime checks.

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
