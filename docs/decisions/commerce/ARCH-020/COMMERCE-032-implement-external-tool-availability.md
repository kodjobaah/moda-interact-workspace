---
id: ARCH-020-COMMERCE-032
architecture_id: ARCH-020
title: Implement external tool availability
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 150
executor: copilot
claimed_at: 2026-09-22T10:26:49Z
attempt: 1
depends_on:
  - ARCH-020-COMMERCE-013
  - ARCH-020-COMMERCE-028
  - ARCH-020-SHARED-002
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-024
created: 2026-09-21
updated: 2026-09-22
---

# Implement external tool availability

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Own src/commerce/external-availability/** only. Implement shared read-only external-tool availability projection for merchant inspection and live authorization; no page, network, secret disclosure or grant creation.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Own src/commerce/external-availability/** only. Implement shared read-only external-tool availability projection for merchant inspection and live authorization; no page, network, secret disclosure or grant creation.

## Out of Scope

Review.
WhatsApp sends, pricing/merchant feature overrides, automatic API discovery,
external-result caching and other owners' implementation files. No live deployment.

- `moda-interact-commerce/src/commerce/external-availability/index.ts`
- `moda-interact-commerce/tests/external-availability.test.ts`
- `moda-interact-commerce/package.json`

Use C21 named interfaces and bounded examples. All dependencies must be accepted
Complete before claim. Readiness is not execution. Component tasks may prove their
- Implemented `createExternalAvailabilityResolver({checkConnectionAvailability})`.
- Inspection resolves all base-eligible candidates; live execution filters by the original grant's exact tool and revision identity before checking current connection status.
- New credentials or releases cannot expand an old grant; candidate capability provenance must still overlap the original grant.
- Current disabled, missing-revision, missing-credential and unavailable-key states retain the actual tool, tool revision, capability keys and connection revision identity. Lookup outages return typed unavailable instead of an eligibility exclusion.
- Availability checks are shop-scoped and reused by connection revision only within one resolver call; no provider calls, secrets, grant writes or cross-call caching are introduced.
Protect every UI command against double clicks, preserve same-operation retries,
and never expose secrets or raw external response data in errors/logs.

- AV01 -> `tests/external-availability.test.ts` / `returns eligible descriptors and real missing-credential exclusions` -> `npm run test:arch020-external-availability` -> passed.
- AV02 -> `tests/external-availability.test.ts` / `uses the same current status projection for inspection and live authorization` -> `npm run test:arch020-external-availability` -> passed; concurrent shop-scoped calls retained separate shop IDs and disabled/missing-credential reasons.
- AV03 -> `tests/external-availability.test.ts` / `keeps old grants pinned and returns lookup outages as unavailable` -> `npm run test:arch020-external-availability` -> passed; new revision excluded, same pinned revision remained selected after rotation, revocation excluded it, and outage returned typed unavailable.
- Changed-file diagnostics: `get_errors` -> no errors; `npx eslint src/commerce/external-availability/index.ts tests/external-availability.test.ts` -> passed.
- `git diff --check` -> passed.
- `npm run typecheck` -> blocked by existing unrelated errors in `src/commerce/integration/backend.ts` and `src/commerce/integration/backend/publication-storage.ts`; no errors were reported in the changed files.
- `npm run lint` -> blocked by existing unrelated `react-hooks/set-state-in-effect` error in `src/studio/connections/connections-ui.tsx`; changed-file ESLint passed.
- PostgreSQL/container and live-provider checks were not run; they are not required for this pure resolver and no live credentials were used.

- [ ] Export section9 createExternalAvailabilityResolver over current connection status/credential availability and the accepted base eligibility result.
- [ ] Keep original granted tool/revision set as the upper bound; new credentials/releases cannot expand old grants. Recheck exact scope/enabled/revision and key availability consistently.
The first focused test invocation required `npm ci` because the prepared implementation worktree had no installed dependencies. The locked dependency install completed with existing peer/engine/audit warnings; no package lock changes were made.
- [ ] Prove two merchants, pinned old/new revisions, changed credential configuration, disabled connection and missing-key paths with same resolver used by both consumers.

## Interfaces / Contracts
C21 section9 supplies already accepted base-eligible external candidates and the connection availability port. Candidate descriptors are preserved unchanged, and the trusted caller supplies the shop identity.
C21 sections1–8 retain data/behavior requirements. [Section9](../../../architecture/ARCH-020-external-api-tools.md#9-tightened-implementation-boundaries-and-evidence) is authoritative for the narrowed ownership, factory signatures, scenario IDs and handoff rules. Consume accepted exports; no consumer may repair a missing producer by weakening the contract. Record actual dependency commits and published package versions.

## Dependencies
Repository-wide typecheck and lint remain blocked by pre-existing unrelated failures listed above. Architect review should confirm the exact success/unavailable result shape expected by the eventual COMMERCE-024 composition consumer.
- ARCH-020-COMMERCE-013
- ARCH-020-COMMERCE-028
- ARCH-020-SHARED-002
No cross-repository or contract conflict found. The implementation does not modify Shared, Background, connection services, HTTP execution or grant creation.
## Enables

- ARCH-020-COMMERCE-012
Expected mirrored branch: `task/ARCH-020-COMMERCE-032`. Attempt1 claimed by `copilot` through the launcher. Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-032`; parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-032`.

Physical worktree isolation:
  canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
  parent branch: `task/ARCH-020-COMMERCE-032`
  implementation branch: `task/ARCH-020-COMMERCE-032`
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: not-needed
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: not-needed
  implementation origin/main incorporated: already-current

Recursive implementation submodules:
  `git submodule sync --recursive`: passed
  `git submodule update --init --recursive`: passed
  recorded `database` submodule commit: `7f920e8f2ad523e78e566f4dbdfbb1f68118b082`

Implementation commit: `10639c7` (`feat(commerce): add external availability resolver`), pushed to `origin/task/ARCH-020-COMMERCE-032`. Parent report commit and push follow; no main merge or service gitlink update is performed.
## Acceptance Criteria

- [ ] AV01: eligible PLATFORM and exact PER_SHOP cases return expected descriptors; missing credential excluded with real identities/reason, not a fabricated feature ID.
- [ ] AV02: inspection and runtime availability agree for same facts; no provider calls, credential data or grant writes; expired/disabled contexts remain denied by base authorization.
- [ ] AV03: credential addition never grants an unpinned tool to old conversation; rotation uses same pinned revision; revocation removes permission.

## Validation

Provide `test:arch020-external-availability` and scenario IDs from C21 section9. Start with the named positive path through the actual owned implementation. Add the specified rejection/race cases. Each report maps criterion -> test file/test name -> command -> observable result, not just a suite count. No claimed success based only on safe rejection or missing-config tests. Preserve each review reproduction as a committed regression alongside adjacent allowed/denied cases.

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

Not Started.

### Files Changed

None; task definition only.

### Work Completed

None.

### Validation Results

No implementation validation performed.

### Deviations

Definition authored on main under the user's existing instruction.

### Assumptions

C21 read-only scope; visual rules and generic JavaScript only inside the specified sandbox.

### Unresolved Issues

No implementation reported. Explicit dependencies gate execution.

### Architectural Concerns

Return contradictory accepted source facts to moda_architect before weakening contracts.

### Git / VCS

Expected mirrored branch: task/ARCH-020-COMMERCE-032. Attempt0; no implementation worktree or
commit claimed. At submission record physical isolation, dependency versions,
recursive database submodule evidence where applicable, commits and pushes.

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
