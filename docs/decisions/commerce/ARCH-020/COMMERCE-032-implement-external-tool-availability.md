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
status: in_progress
priority: 150
executor: copilot
claimed_at: 2026-09-22T11:15:09Z
attempt: 2
depends_on:
  - ARCH-020-COMMERCE-013
  - ARCH-020-COMMERCE-028
  - ARCH-020-COMMERCE-037
  - ARCH-020-SHARED-002
  - ARCH-020-COMMERCE-037
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
- ARCH-020-COMMERCE-037
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

Blocked — Attempt 1.

### Review Notes

Reviewed by `moda_architect` against the exact submitted source snapshot associated by
the developer with implementation `10639c7` and parent handoff `b2aab231`.

The COMMERCE-032 resolver itself is directionally conformant with C21 section 9.5:

- it consumes already base-eligible candidate descriptors;
- live execution filters the original grant by exact tool ID + exact tool revision;
- candidate capability provenance must overlap the originally granted capability
  provenance;
- a newer tool revision cannot expand an old grant;
- current connection exclusions preserve actual tool/revision/capability/
  connectionRevision identities;
- connection lookup `unavailable` is returned as typed unavailable rather than
  converted into an eligibility exclusion;
- availability status is reused by exact connection revision only within one resolver
  call;
- the trusted merchant shop ID is passed consistently to the availability dependency;
- no provider call, secret, grant write or cross-call cache is introduced.

Attempt 1 is **Blocked rather than Changes Requested** because review exposed a
cross-task producer/consumer contract mismatch that COMMERCE-032 cannot correctly fix
inside `external-availability/**`.

The accepted COMMERCE-028 producer currently implements:

```ts
checkConnectionAvailability(input: {
  connectionRevisionId: string;
  shopId: string | null;
})
```

with scope-key semantics:

```text
PLATFORM:
  shopId must be null

PER_SHOP:
  shopId must be the exact merchant shop ID
```

Its current guard is equivalent to:

```text
PLATFORM + non-null shopId
  -> CREDENTIAL_MISSING
```

COMMERCE-032, however, correctly follows the C21 section 9.5 consumer shape:

```ts
resolve({
  shopId: "<trusted merchant shop ID>",
  candidates,
  grant,
})
```

and passes that merchant shop ID to `checkConnectionAvailability` for every candidate.

Therefore the real assembled PLATFORM path is currently:

```text
032 resolve(shopId = "shop-A")
  -> accepted 028 checkConnectionAvailability(
       connectionRevisionId = platform revision,
       shopId = "shop-A"
     )
  -> 028 sees PLATFORM + non-null shopId
  -> CREDENTIAL_MISSING
```

even when the PLATFORM connection is enabled and its credential exists at
`shopId IS NULL`.

The current AV01 focused test does not expose this because it uses a permissive mock
`checkConnectionAvailability` and never composes the accepted COMMERCE-028 producer.
This is an upstream port-semantics defect, not a reason for 032 to invent connection
scope metadata, retry null/non-null probes or weaken exact-shop isolation.

The correct architecture is now explicit:

```text
checkConnectionAvailability input shopId
  = trusted merchant identity
  = always non-null

inside COMMERCE-028 availability projection:
  PLATFORM -> credential lookup shopId = null
  PER_SHOP -> credential lookup shopId = trusted merchant shopId
```

`getCredentialStatus`, `setCredential`, `removeCredential` and `resolveConnection`
retain their existing scope-key semantics and nullable shop ID contracts. Only the
read-only availability projection receives normalized merchant identity semantics.

This producer correction is materialized as `ARCH-020-COMMERCE-037`. COMMERCE-032
must not implement the missing producer behavior locally.

The uploaded task record is also not reconciled with the developer handoff: YAML still
contained an active `copilot` claim and the Completion Report remained `Not Started`.
This Architect overlay clears the claim and records the blocked disposition; after
COMMERCE-037 is accepted, the next validation-only COMMERCE-032 attempt must update
its Work Items, Acceptance Criteria, Validation and Completion Report truthfully.

### Reviewed Files

- `src/commerce/external-availability/index.ts`
- `tests/external-availability.test.ts`
- accepted `src/commerce/connections/credentials/index.ts`
- `package.json`
- C21 sections 8 and 9.1–9.6
- this task file and current domain index

### Validation Reviewed

Submitted developer evidence:

```text
npm run test:arch020-external-availability
  PASS — focused AV01–AV03 suite

npx eslint \
  src/commerce/external-availability/index.ts \
  tests/external-availability.test.ts
  PASS

git diff --check
  PASS

npm run typecheck
  NON-ZERO — reported unrelated integration/backend baseline

npm run lint
  NON-ZERO — reported unrelated Connections hook baseline
```

These repository baseline failures are not the blocker.

The blocking reproduction is source-level compatibility with the accepted COMMERCE-028
producer: a PLATFORM revision receives the non-null merchant shop ID from 032 and is
therefore excluded as `CREDENTIAL_MISSING`.

### Architecture Conformance

COMMERCE-032 source is provisionally conformant with the intended C21 availability
consumer boundary, but cannot be accepted until the accepted availability producer
matches that boundary.

No COMMERCE-032 source change is presently required.

### Follow-up

Keep this task:

```yaml
status: blocked
attempt: 1
executor: null
claimed_at: null
```

and add dependency:

```yaml
- ARCH-020-COMMERCE-037
```

After COMMERCE-037 is architect-accepted Complete:

```text
moda_architect:
  blocked -> ready
  attempt remains 1
  claim remains clear
```

The next normal:

```text
/moda-task ARCH-020-COMMERCE-032
```

must claim **Attempt 2 exactly once**.

Attempt 2 is validation/reconciliation only unless the producer correction exposes a
new 032-owned defect:

1. rerun `npm run test:arch020-external-availability`;
2. add/retain one regression proving a PLATFORM candidate is available when the
   corrected producer receives merchant `shopId = "shop-A"` and resolves its stored
   PLATFORM credential at null scope;
3. retain exact PER_SHOP shop isolation and old-grant pinning;
4. update Work Items / AV01–AV03 / Validation / Completion Report;
5. return to review and STOP.

Do not start COMMERCE-024 or COMMERCE-012.
Reconcile readiness/indexes after prerequisite acceptance; no automatic launch.

## Architect Dependency Reconciliation — COMMERCE-037 acceptance — 2026-09-22

`ARCH-020-COMMERCE-037` is now an explicit prerequisite because it defines the
merchant-identity semantics of the `checkConnectionAvailability(...)` port consumed
by this task.

COMMERCE-032 remains **Ready** because COMMERCE-037 is Complete in the same
reconciliation. No implementation claim is created by this documentation update.
