---
id: ARCH-039-COMMERCE-001
architecture_id: ARCH-039
title: Migrate Commerce external-connection credentials and command key to Shared
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
enables:
  - ARCH-039-COMMERCE-002
  - ARCH-039-GATEWAY-001
created: 2026-10-14
updated: 2026-10-14
---


# Migrate Commerce external-connection credentials and command key to Shared

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_commerce` / `moda-interact-commerce`

## Objective

Migrate Commerce external-connection credentials and command key to Shared. This is one bounded, repository-owned outcome; do not move to another task on completion.

## Context

ARCH-039 makes one published credential security mechanism authoritative for hosted Node services. The developer has chosen a non-production data clear rather than historical encryption-key migration. This task is part of the agreed staged adoption plan; see the parent architecture for exact cross-service invariants.

## Scope

- Replace `lib/server/credential-keyring.ts` duplicate parser and `src/commerce/connections/credentials/index.ts` local AES-GCM with published Shared keyring and AEAD.
- Import the SHARED-005 `parseCommerceConnectionCommandHmacKey(raw, aesKeyring)` decoder; pass its returned 32 bytes (not the encoded configuration text) to `createHmac` in the existing command digest implementation.

## Out of Scope

Preview/OpenRouter/embedding reader migration belongs to COMMERCE-002.

## Requirements

- Use canonical keyring + active selector for external connection credential writes; stored key ID for reads.
- Preserve `canonicalJson` external-connection AAD, scoped revision/shop identity, super-admin permission and audit/transaction behaviour.
- Command-HMAC key must be independent from AES keyring; new byte-key digest is deterministic and tested with an independent HMAC-SHA256 golden vector after the planned non-production audit wipe. Require rejection of an HMAC key equal to any configured AES key.
- Malformed keyring/HMAC causes explicit unavailable response, not partial enablement or empty-keyring fallback.

## Work Items

- [ ] Implement Shared parser/AEAD imports and typed adapters; remove duplicate crypto.
- [ ] Update external-connection command idempotency and credential tests for decoded HMAC bytes, tamper, missing keys, wrong shop AAD.
- [ ] Ensure `src/commerce/integration/backend.ts` respects all-or-nothing credential/HMAC config and safe errors.

## Interfaces / Contracts

- Published Shared Node keyring/AEAD and SHARED-005 HMAC decoder with `parseCommerceConnectionCommandHmacKey(raw, aesKeyring): Uint8Array`; Commerce owns external AAD and command digest semantics.
- The Commerce command-kernel dependency should accept HMAC **bytes**, not an encoded `string`; its canonical input serializer and replay/conflict rules remain unchanged.

## Dependencies

- ARCH-039-SHARED-004

## Enables

- ARCH-039-COMMERCE-002
- ARCH-039-GATEWAY-001

## Acceptance Criteria

- [ ] Commerce external connection credentials use published Shared crypto/keyring.
- [ ] HMAC key is decoded independently and deterministic replay checks work under new key.
- [ ] Service does not silently substitute empty keyring on invalid config.

## Validation

- [ ] Focused Commerce external credential/command kernel tests
- [ ] Commerce typecheck and build
- [ ] Changed-file lint and `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. For developer completion, an explicit developer approval is required after accepted review.

## Implementation Notes

Keep payment-independent connection operations and existing admin audit transaction boundaries untouched.

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
