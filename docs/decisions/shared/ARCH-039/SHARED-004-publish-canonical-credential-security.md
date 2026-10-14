---
id: ARCH-039-SHARED-004
architecture_id: ARCH-039
title: Publish the accepted Node credential-security API
task_kind: publication
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-039-SHARED-001
  - ARCH-039-SHARED-002
  - ARCH-039-SHARED-003
  - ARCH-039-SHARED-005
enables:
  - ARCH-039-ADMIN-001
  - ARCH-039-ADMIN-002
  - ARCH-039-BACKGROUND-001
  - ARCH-039-BACKGROUND-002
  - ARCH-039-COMMERCE-001
  - ARCH-039-MCP-001
  - ARCH-039-API-001
created: 2026-10-14
updated: 2026-10-14
---

# Publish the accepted Node credential-security API

## Architecture

Architecture ID: `ARCH-039`
Architecture document: `docs/architecture/ARCH-039-canonical-credential-security.md`
Coordinator: `moda_architect`
Owner: `moda_shared` / `moda-interact-shared`

## Objective

Publish the accepted Shared release that contains the complete, verified keyring, AEAD, AAD and independent command-HMAC parsing API.

## Context

ARCH-039 standardises hosted credential security before consumer refactoring. The developer will clear non-production credential and command-audit state: this is a breaking pre-production cutover without historical compatibility. Interfaces established here are the binding contracts for downstream Shared and service tasks.

## Scope

- Choose the approved next package version, apply version/release metadata only, and publish through the existing Shared npm release workflow.
- Verify that consumers can resolve exactly `@modainteract/moda-interact-shared/security/credentials/node` with its ESM and `.d.ts` declarations from the published package.

## Out of Scope

- No changes to cryptography, keyring parser, AAD, HMAC decoder, unit tests or other runtime source.
- Do not rerun implementation tests/build/typecheck/lint already accepted under SHARED-001/002/003/005.
- No consumer dependency updates or service configuration in a Shared publication task.

## Requirements

Publication begins only after **all four** implementation tasks have `status: complete` and Accepted Architect Review (developer completion authority satisfied).

The registry package must expose, under ONE Node-only subpath:

```text
parseCredentialKeyring, resolveActiveCredentialKey,
CredentialSecurityError, CredentialKeyring,
CredentialEnvelope, encryptCredential, decryptCredential,
createCommerceEmbeddingCredentialAad,
createWooRestReadGrantAad,
parseCommerceConnectionCommandHmacKey
```

Verify complete package `exports` map for Node entrypoint and declaration path, no requirement for root/browser re-exports; existing `commerce/model` OpenRouter/translation exports remain intact. The published version, git commit and successful registry resolution are recorded in the Completion Report. Publication does not change implementation code, introduce new crypto fallback or repeat accepted tests.

## Work Items

- [ ] Confirm Accepted + Complete SHARED-001, SHARED-002, SHARED-003 and SHARED-005.
- [ ] Record approved package version; update only version/release metadata and lockfile if required.
- [ ] Execute existing approved publication command and verify registry resolves **that exact version**.
- [ ] Inspect package metadata/contents for Node ESM and `.d.ts` export and the listed symbol names; confirm `sealCredential`, `openCredential`, `openCredentialText` and `isValidCredentialEnvelope` are not exported; record release evidence.
- [ ] Prove release-only diff and no unrelated implementation changes.

## Interfaces / Contracts

Published `@modainteract/moda-interact-shared/security/credentials/node` using all interfaces established in SHARED-001/002/003/005, plus unchanged previous `@modainteract/moda-interact-shared/commerce/model` OpenRouter/translation AAD exports.

## Dependencies

- ARCH-039-SHARED-001
- ARCH-039-SHARED-002
- ARCH-039-SHARED-003
- ARCH-039-SHARED-005

## Enables

- ARCH-039-ADMIN-001
- ARCH-039-ADMIN-002
- ARCH-039-BACKGROUND-001
- ARCH-039-BACKGROUND-002
- ARCH-039-COMMERCE-001
- ARCH-039-MCP-001
- ARCH-039-API-001

## Acceptance Criteria

- [ ] All four Shared implementation tasks accepted and explicitly developer-completed.
- [ ] Registry contains the chosen package version with the exact Node subpath, expected exports and type declarations.
- [ ] Publication source diff limited to approved version/release metadata; no code/test changes and no consumer integration.

## Validation

- [ ] Accepted prerequisite states independently checked
- [ ] Publish command succeeded; registry install/metadata confirms exact version and subpath package map
- [ ] Release-only diff and `git diff --check`

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. Developer completion requires an explicit developer decision after accepted review. Do not begin dependent tasks.

## Implementation Notes

`task_kind: publication` is a **release-only gate** under the architect policy. Do not rerun build, typecheck, lint, unit or integration tests merely to validate implementation again. If missing exports are found, STOP and return a correction to the proper Shared implementation task.

Use the canonical dedicated parent/implementation task-worktree launcher and preserve initial synchronization evidence. Do not create/update `docs/decisions/**/_index.md` until the architecture session is explicitly confirmed complete. No implementation edits outside `moda-interact-shared`.

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

None beyond parent architecture.

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
