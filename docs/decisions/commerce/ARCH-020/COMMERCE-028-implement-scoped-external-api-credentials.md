---
id: ARCH-020-COMMERCE-028
architecture_id: ARCH-020
title: Implement scoped external API credentials
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 150
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-020-COMMERCE-020
  - ARCH-020-DATABASE-003
  - ARCH-020-SHARED-002
enables:
  - ARCH-020-COMMERCE-032
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-024
  - ARCH-020-GATEWAY-003
created: 2026-09-21
updated: 2026-09-22
---

# Implement scoped external API credentials

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Own src/commerce/connections/credentials/** only. Implement credential encryption, CAS/replay, rotation and exact-shop resolution using020 command kernel. No connection metadata lifecycle, UI, HTTP or integration-factory edits.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Own src/commerce/connections/credentials/** only. Implement credential encryption, CAS/replay, rotation and exact-shop resolution using020 command kernel. No connection metadata lifecycle, UI, HTTP or integration-factory edits.

## Out of Scope

Writes, OAuth, unsandboxed code, customer-specific lookups, live credentials or
WhatsApp sends, pricing/merchant feature overrides, automatic API discovery,
external-result caching and other owners' implementation files. No live deployment.

## Requirements

Use C21 named interfaces and bounded examples. All dependencies must be accepted
Complete before claim. Readiness is not execution. Component tasks may prove their
ports with fixtures; only024 and SYSTEM-TEST-002 claim real assembled flow.
Protect every UI command against double clicks, preserve same-operation retries,
and never expose secrets or raw external response data in errors/logs.

## Work Items

- [x] Implement createCredentialService with getCredentialStatus/setCredential/removeCredential/resolveConnection/checkConnectionAvailability as C21 section9 defines.
- [x] Reuse020 locked command kernel for same-transaction credential and audit writes; do not clone replay/auth/digest logic or modify its files.
- [x] Implement AES-GCM/AAD/keyring handling, exact scope/no-fallback and current enabled checks. Keep secret result internal; status/availability expose no authentication value.
- [x] Deliver two-client credential race, stored-secret roundtrip and rotation fixtures; retain no real secrets in fixtures/logs.

## Interfaces / Contracts

C21 sections1–8 retain data/behavior requirements. [Section9](../../../architecture/ARCH-020-external-api-tools.md#9-tightened-implementation-boundaries-and-evidence) is authoritative for the narrowed ownership, factory signatures, scenario IDs and handoff rules. Consume accepted exports; no consumer may repair a missing producer by weakening the contract. Record actual dependency commits and published package versions.

## Dependencies

- ARCH-020-COMMERCE-020
- ARCH-020-DATABASE-003
- ARCH-020-SHARED-002

## Enables

- ARCH-020-COMMERCE-032
- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-024
- ARCH-020-GATEWAY-003

## Acceptance Criteria

- [x] CR01: PLATFORM and two PER_SHOP credentials roundtrip through real service; correct decrypted value reaches a recording internal consumer, never a public DTO.
- [ ] CR02: same-command duplicate yields one credential effect/audit; changed replay and stale credential version reject; NULL-platform uniqueness exercised on PostgreSQL. Developer PostgreSQL validation remains required.
- [x] CR03: wrong shop, absent credential, disabled connection, invalid key/AAD/tag and removed credential deny/unavailable exactly; old revision remains fixed while secret rotation affects future calls.

## Validation

Provide `test:arch020-external-credentials` and scenario IDs from C21 section9. Start with the named positive path through the actual owned implementation. Add the specified rejection/race cases. Each report maps criterion -> test file/test name -> command -> observable result, not just a suite count. No claimed success based only on safe rejection or missing-config tests. Preserve each review reproduction as a committed regression alongside adjacent allowed/denied cases.

Use focused checks while implementing, then existing typecheck/build/lint where defined. Record unrun developer-owned PostgreSQL/container checks accurately; executable scenarios must still exist. No repeated unrelated full suites or screenshot quotas. No live credentials/WhatsApp delivery.

## Stop Condition

Submit implementation and parent report through normal mirrored task branches,
then stop at Review for moda_architect. Never self-accept, launch downstream tasks,
merge main, publish service deployments or update workspace service gitlinks.
Shared's package publication is required only for SHARED-002 as explicitly scoped.
SYSTEM-TEST-002 requires explicit developer invocation even when Ready.

## Implementation Notes

Use /moda-task launcher-resolved dedicated worktrees and preparation packet.
Task authoring on main is the user's documentation exception, not permission for
implementation on main. Preserve unrelated work and existing task claims.

## Completion Report

### Status

Review-ready, Attempt 1 implementation submitted to `moda_architect`.

### Files Changed

- `moda-interact-commerce/src/commerce/connections/credentials/index.ts`
- `moda-interact-commerce/tests/external-credentials.test.ts`
- `moda-interact-commerce/package.json`

### Work Completed

Added `createCredentialService` under its assigned path only. It uses the
accepted COMMERCE-020 `ConnectionCommandKernel` for credential mutation replay,
authorization, locking and same-transaction audit behavior. The service performs
AES-256-GCM encryption with a random 12-byte nonce, 16-byte tag, key ID and
canonical `{connectionRevisionId, shopId, keyId}` AAD. It supports active-key
rotation while retaining old keyring entries for decryption.

`resolveConnection` is the only local sensitive result: decrypted header values
remain inside the Commerce service. Status and availability APIs expose only
configuration/version/timestamp or exclusion reason. Scope resolution is exact:
PER_SHOP never falls back to platform or another shop, disabled connections deny,
and decrypt/AAD/tag/key failures fail closed.

### Validation Results

Agent-executed validation:

| Criterion | Committed test | Command | Observable result |
| --- | --- | --- | --- |
| CR01 | `external credentials > CR01 encrypts an exact-shop secret and decrypts only for the internal resolver`; `CR01 isolates two shop credentials and supports a platform credential without exposing it in status` | `npm run test:arch020-external-credentials` | PLATFORM plus two exact PER_SHOP secrets roundtrip through `createCredentialService`; only `resolveConnection` receives header value; status has no secret. |
| CR02 (non-PostgreSQL portion) | `external credentials > CR02 applies CAS and replay without a second credential effect` | `npm run test:arch020-external-credentials` | Same command replay makes one effect; changed replay returns `CONFLICTING_REPLAY`; concurrent same-version clients produce exactly one success and one `STALE_CAS`. |
| CR03 | `external credentials > CR03 reports disabled, missing, invalid-key, and removed credentials without revealing a secret` | `npm run test:arch020-external-credentials` | Missing/wrong-shop/disabled/key/AAD-tag/removed paths deny or fail unavailable; retained old key decrypts before rotation and active key encrypts replacement. |

- `npm run test:arch020-external-credentials`: passed, 1 file and 4 tests.
- `npm run test:arch020-external-connection-lifecycle`: passed, 1 file and 9 tests.
- `npx eslint src/commerce/connections/credentials tests/external-credentials.test.ts`: passed.
- `git diff --check`: passed.
- `npm run lint`: non-zero only for existing `src/studio/connections/connections-ui.tsx:235` hook-rule diagnostic and unrelated warnings; no credential diagnostic.
- `npm run typecheck`: non-zero on 11 existing diagnostics in `src/commerce/connections/command-kernel.ts`, `src/commerce/connections/lifecycle/index.ts`, `src/commerce/integration/backend/executors.ts`, and `tests/code-response-processor.test.ts`; no credential diagnostic.
- `npm run build`: QuickJS packaging/smoke, Prisma generation and Next compilation passed; subsequent type checking stopped on the same 11 unrelated diagnostics.

Developer validation required:

```bash
npm run test:arch020-backend-integration:postgres
```

Expected success condition: run the disposable PostgreSQL credential scenario to
prove the database partial unique index permits one NULL-platform credential,
rejects duplicate NULL-platform rows, and preserves transaction/audit rollback.
This long PostgreSQL/container rehearsal was not agent-executed.

### Deviations

No scope deviation. The service is frontend/HTTP/factory independent and does not
modify COMMERCE-020 kernel, DATABASE schema, UI, transport or integration code.

### Assumptions

Shared package version `@modainteract/moda-interact-shared@0.14.2` supplies the
credential DTO/result contracts and `canonicalJson`. The launcher materialized
the database submodule at `7f920e8f2ad523e78e566f4dbdfbb1f68118b082`.

### Unresolved Issues

CR02 remains pending real PostgreSQL partial-unique-index evidence. The focused
fixture proves the service's replay/CAS behavior but is not a replacement for the
developer-owned container/database rehearsal.

### Architectural Concerns

No contract contradiction found. The repository baseline currently blocks full
typecheck/build after compilation in unrelated pre-existing files as recorded
above.

### Git / VCS

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-028`
  implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-028`
  mirrored branch: `task/ARCH-020-COMMERCE-028`
  implementation commit: `715da4d`, pushed to the implementation task branch.

The launcher claimed Attempt 1 as `3b610c19076630439b454a1c23175e39f62cda10` and
verified the recursive database submodule at the recorded commit. This parent
report update is the review handoff commit.

## Architect Review

### Review Status

Pending.

### Review Notes

Definition only; no implementation acceptance.

### Reviewed Files

Not applicable.

### Validation Reviewed

Not applicable.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile readiness/indexes after prerequisite acceptance; no automatic launch.
