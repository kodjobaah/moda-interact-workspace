---
id: ARCH-039-BACKGROUND-002
architecture_id: ARCH-039
title: Migrate Background Woo REST-read grant decryption to Shared
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
  - ARCH-039-BACKGROUND-001
enables:
  - ARCH-039-GATEWAY-001
  - ARCH-039-SYSTEM-TEST-001
created: 2026-10-14
updated: 2026-10-14
---


# Migrate Background Woo REST-read grant decryption to Shared

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_background` / `moda-interact-background`

## Objective

Migrate Background Woo REST-read grant decryption to Shared. This is one bounded, repository-owned outcome; do not move to another task on completion.

## Context

ARCH-039 makes one published credential security mechanism authoritative for hosted Node services. The developer has chosen a non-production data clear rather than historical encryption-key migration. This task is part of the agreed staged adoption plan; see the parent architecture for exact cross-service invariants.

## Scope

- Update `src/services/woo-coupon-grant.service.ts` to use Shared keyring, AAD and authenticated opening of API-created Woo read grants.
- Keep per-call pre/post installation eligibility and grant version verification.

## Out of Scope

Unrelated Woo billing, coupon provider semantics and API authorisation are out of scope.

## Requirements

- Consume `COMMERCE_CONNECTION_KEYS_JSON` only, without separate Woo keyring or active key selector.
- Validate decrypted Woo key/secret JSON array in Background domain code after Shared AEAD open.
- Do not weaken tenant, installation, revocation, rotation, credential-version, site URL or read-scope validation.

## Work Items

- [ ] Replace inline Woo AAD and generic crypto calls with published Shared functions; delete the now-unreferenced Background generic AES helper.
- [ ] Update Woo coupon grant tests for API-produced ciphertext, wrong tenant, stale version, revocation/tamper.
- [ ] Document canonical shared keyring without dual-encoding workaround.

## Interfaces / Contracts

- Published `createWooRestReadGrantAad`, Shared AEAD/keyring; coordinate compatibility with API-002.

## Dependencies

- ARCH-039-SHARED-004
- ARCH-039-BACKGROUND-001

## Enables

- ARCH-039-GATEWAY-001
- ARCH-039-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Woo grants produced by API-002 decrypt only for authorised current installation.
- [ ] No dual keyrings or base64url config workaround remains.
- [ ] Grant changes during paginated reads remain fenced.

## Validation

- [ ] Focused Woo grant/transport tests
- [ ] Background typecheck and build (where provided)
- [ ] Changed-file lint and `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. For developer completion, an explicit developer approval is required after accepted review.

## Implementation Notes

No new encryption keys at worker startup; no database migration.

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
