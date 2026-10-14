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
status: review
priority: 10
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-039-SHARED-001
  - ARCH-039-SHARED-002
  - ARCH-039-SHARED-003
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

- **Mandatory closed-set credential configuration:** for AES credential encryption/decryption, credential key selection and Commerce connection-command HMAC, the **only permitted environment variable names anywhere in ARCH-039 runtime configuration** are `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and `COMMERCE_CONNECTION_COMMAND_HMAC_KEY`. No other names, aliases, old Woo keyring variables, service-specific encryption/HMAC variables, dual-read, fallback, generated defaults or alternate sources may be used for these purposes. Other unrelated application environment settings are unaffected.
- Shared is a **pure Node library** for ARCH-039 secrets: never read `process.env`, introduce or document another credential-security environment name, infer an environment variable by convention, or generate replacement keys. Callers inject parsed values sourced exclusively from the canonical `COMMERCE_CONNECTION_KEYS_JSON`, `COMMERCE_CONNECTION_ACTIVE_KEY_ID` and (for Commerce commands only) `COMMERCE_CONNECTION_COMMAND_HMAC_KEY` via their authorised server adapters. Publication must not introduce alternate configuration.

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

- [x] Confirm Accepted + Complete SHARED-001, SHARED-002, SHARED-003 and SHARED-005.
- [x] Record approved package version; update only version/release metadata and lockfile if required.
- [x] Verify the existing publication resolves from the registry at **that exact version**; it was already published, so no duplicate publish was attempted.
- [x] Inspect package metadata/contents for Node ESM and `.d.ts` export and the listed symbol names; confirm `sealCredential`, `openCredential`, `openCredentialText` and `isValidCredentialEnvelope` are not exported; record release evidence.
- [x] Prove release-only diff and no unrelated implementation changes.

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

- [x] Shared code, published exports, fixtures and documentation introduce no service-local secret environment name, environment reads or fallback configuration for ARCH-039 credential security.

- [x] All four Shared implementation tasks accepted and explicitly developer-completed.
- [x] Registry contains the chosen package version with the exact Node subpath, expected exports and type declarations.
- [x] Publication source diff limited to approved version/release metadata; no code/test changes and no consumer integration.

## Validation

- [x] Accepted prerequisite states independently checked
- [x] Registry resolution and clean install confirm the exact version and subpath package map; release was already published when reviewed.
- [x] Release-only diff and `git diff --check`

## Stop Condition

After all Work Items, Acceptance Criteria and required Validation are complete, update only this task's allowed metadata and Completion Report, set `status: review`, return to `moda_architect`, and STOP. Developer completion requires an explicit developer decision after accepted review. Do not begin dependent tasks.

## Implementation Notes

`task_kind: publication` is a **release-only gate** under the architect policy. Do not rerun build, typecheck, lint, unit or integration tests merely to validate implementation again. If missing exports are found, STOP and return a correction to the proper Shared implementation task.

Use the canonical dedicated parent/implementation task-worktree launcher and preserve initial synchronization evidence. Do not create/update `docs/decisions/**/_index.md` until the architecture session is explicitly confirmed complete. No implementation edits outside `moda-interact-shared`.

## Completion Report

### Status

Ready for explicit developer completion decision — Attempt 1 passed developer self-review. Attempt remains 1; explicit completion is pending.

### Files Changed

- `moda-interact-shared/package.json`
- `moda-interact-shared/package-lock.json`
- This task record.

### Work Completed

- Independently confirmed SHARED-001, SHARED-002, SHARED-003 and SHARED-005 are `complete`, have durable passing/accepted developer self-reviews, and record explicit developer completion decisions.
- The Shared task branch contains only version metadata changes relative to synchronized `origin/main`: `2.4.0` to `2.4.1` in `package.json` and the root lockfile metadata. The release commit is `943a4e6260cae3eab5cbb68f9c3d4d131072737e`; it is tagged locally as `v2.4.1` and pushed on `origin/task/ARCH-039-SHARED-004`.
- Confirmed the public registry resolves `@modainteract/moda-interact-shared@2.4.1`; exact tarball: `https://registry.npmjs.org/@modainteract/moda-interact-shared/-/moda-interact-shared-2.4.1.tgz`; shasum: `57d8b792e3a47de95d8d1afebbe6adaefee28039`; integrity: `sha512-iPe5clTjPewWkQiOMNo/epYsxwazyuAf6TBmdUd8W1kcVEgP3e3FIR/chFaorm00tqakDfYciUxuF76KlZrzeg==`.
- Verified the published `exports` map routes `./security/credentials/node` to `./dist/security/credentials/node.js` and `./dist/security/credentials/node.d.ts`, with `./commerce/model` retained. No credential-security root/browser export was added.

### Validation Results

- Clean temporary npm install of exact version `2.4.1` succeeded; importing `@modainteract/moda-interact-shared/security/credentials/node` succeeded.
- Runtime exports include `parseCredentialKeyring`, `resolveActiveCredentialKey`, `CredentialSecurityError`, `encryptCredential`, `decryptCredential`, `createCommerceEmbeddingCredentialAad`, `createWooRestReadGrantAad` and `parseCommerceConnectionCommandHmacKey`. Type declarations include `CredentialKeyring` and `CredentialEnvelope`.
- Runtime export scan confirmed `sealCredential`, `openCredential`, `openCredentialText` and `isValidCredentialEnvelope` are absent; the declaration file contains no matching retired names.
- `git diff --name-only origin/main...HEAD` contains only `package.json` and `package-lock.json`; `git diff --check` passed. No implementation source, tests or consumer repository changed.
- Implementation task branch push succeeded. The parent task claim was already pushed; this review/report update will be committed and pushed separately.

### Deviations

- The exact release was already present in the public registry when reconciliation began. No second publication attempt was made; registry metadata, the exact-version install and subpath import provide release evidence.

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

## Developer Self-Review Passed/Accepted

- Attempt: 1.
- Result: Passed. The four implementation prerequisites are explicitly developer-completed; the published artifact resolves the required Node-only ESM/declaration subpath and expected symbols; the source diff is release-only.
- Evidence: exact npm registry metadata and integrity recorded above; clean install and import of `@modainteract/moda-interact-shared@2.4.1`; required/retired export inspection; `git diff --check` passed; implementation branch is committed and pushed.
- Lifecycle: this task uses `completion_mode: developer`. The task is now `review`; explicit developer completion is pending. Attempt remains 1.
