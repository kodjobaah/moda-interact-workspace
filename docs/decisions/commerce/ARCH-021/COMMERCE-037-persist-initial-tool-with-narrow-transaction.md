---
id: ARCH-021-COMMERCE-037
architecture_id: ARCH-021
title: Persist initial Tool creation with a narrow PostgreSQL transaction
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 46
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-036
enables:
  - ARCH-021-COMMERCE-038
created: 2026-09-25
updated: 2026-09-26
---

# Persist initial Tool creation with a narrow PostgreSQL transaction

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Route the COMMERCE-036 initial Tool + draft command through a narrow PostgreSQL transaction that touches only the operation/audit record, the new `CommerceTool` and the new `CommerceToolRevision`, eliminating whole-publication materialisation and global publication serialization from this creation path while preserving idempotency and atomicity.

## Context

The current Prisma publication adapter implements every publication mutation as:

```text
Prisma interactive transaction
  -> global pg_advisory_xact_lock('moda-commerce-publication')
  -> readState()
       CommerceTool.findMany()
       CommerceToolRevision.findMany()
       CommerceCapability.findMany()
       CommerceCapabilityRevision.findMany()
       CommerceRelease.findMany(...)
       CommerceReleasePointer.findMany()
       CommerceAuditEvent.findMany()
  -> mutate one in-memory PublicationState
  -> writeState()
       reread broad publication tables
       diff state
       write differences
  -> commit
```

`PrismaPublicationStorage.transaction()` currently has:

```text
maxWait: 1000 ms
timeout: 10000 ms
```

Manual creation exposed an expired interactive transaction after the 10-second lifetime. Increasing that timeout would mask the storage mismatch rather than correct it.

COMMERCE-036 establishes the atomic business command. This task changes only its PostgreSQL persistence path. Other publication commands continue to use the existing generic state transaction until separately justified.

## Scope

Primary files:

```text
src/commerce/publication/ports.ts
src/commerce/publication/lifecycle.ts
src/commerce/integration/backend/publication-storage.ts
src/commerce/integration/backend/index.ts             # only if dependency wiring requires it

tests/commerce-lifecycle.test.ts
tests/backend-integration.test.ts
tests/fixtures/publication-store.ts
```

Add one focused PostgreSQL persistence/rehearsal test file or extend an existing Commerce backend PostgreSQL rehearsal only where needed to prove real concurrent database semantics.

Primary schema consumed without migration:

```text
database/prisma/schema.prisma
  CommerceTool
  CommerceToolRevision
  CommerceAuditEvent
  PlatformAdmin
```

## Out of Scope

- Rewriting generic `PublicationStoragePort.transaction()` for capabilities/releases/other Tool mutations.
- Changing the 10-second timeout as the fix.
- Removing the existing global-lock state transaction for unrelated publication operations.
- Database schema or Prisma migration changes.
- Studio Server Actions/services; COMMERCE-038 owns those.
- Browser authoring; COMMERCE-039 owns that.
- Phase 2 tab gating.
- Publication/live-test rules.
- New permanent custom telemetry solely for this correction.

## Requirements

### R1 — dedicated narrow persistence boundary

Provide a dedicated persistence path for the COMMERCE-036 initial-create operation. The exact interface name may follow repository conventions, but it MUST accept the already validated/normalized initial-create input plus actor/operation identity and return the COMMERCE-036 result.

Do not implement the new command by calling:

```text
readState()
writeState()
snapshot()
```

inside or immediately around its persistence transaction.

The generic publication state abstraction remains for other commands.

### R2 — bounded database work

The successful PostgreSQL path may touch only data required for this operation:

```text
CommerceAuditEvent        operation replay/audit identity
CommerceTool              one insert
CommerceToolRevision      one insert
PlatformAdmin             only as required by existing FK/auth principal guarantees
```

It MUST NOT load or diff:

```text
all CommerceTool rows
all CommerceToolRevision rows
CommerceCapability
CommerceCapabilityRevision
CommerceRelease
CommerceReleaseCapability
CommerceReleasePointer
all CommerceAuditEvent rows
```

The transaction must not acquire the existing global:

```sql
pg_advisory_xact_lock(hashtext('moda-commerce-publication'))
```

for this command.

### R3 — operation-scoped concurrency/idempotency

Preserve the accepted one-operation replay semantics under multiple Commerce instances.

A narrow operation-scoped synchronization mechanism keyed by `operationId` is permitted/expected where required, for example an operation-keyed PostgreSQL advisory transaction lock. It must not serialize unrelated Tool creation operations behind one global publication lock.

Within the synchronized operation:

1. read the exact audit/operation record for `operationId` only;
2. if present, verify actor/action/payload hash and return its recorded result;
3. if the same id was used with different input, return `OPERATION_REUSE_CONFLICT`;
4. otherwise create the Tool, revision and audit in the same transaction.

Preserve the existing durable replay convention used by the publication layer: the operation/audit row remains directly addressable by the operation identity. Do not introduce a new idempotency table in this task.

### R4 — direct Tool insert

Create exactly one `CommerceTool` from the validated input.

The database `CommerceTool.name @unique` constraint is the correctness boundary for competing different operations that attempt the same immutable Tool name.

Translate the relevant unique-name failure into existing lifecycle `CONFLICT` semantics; do not perform a whole-table name scan for concurrency correctness.

### R5 — direct initial revision insert

Create exactly one `CommerceToolRevision` in the same transaction with:

```text
toolId             created Tool id
revisionNumber     1
status             DRAFT
contractVersion    commerce.v1
editVersion        1
definitionVersion  validated proposedDefinition.definitionVersion
definition         canonical persisted Tool definition
createdByAdminId   authorized actor id
```

Do not publish it and do not set published metadata.

The existing database uniqueness constraints remain authoritative:

```text
(toolId, revisionNumber)
(toolId, definitionVersion)
```

### R6 — one audit/replay record

Create one `CommerceAuditEvent` for `CREATE_TOOL` in the same transaction.

Its metadata must preserve the existing operation replay payload hash and result, with result containing both:

```text
toolId
toolRevisionId
```

The audit must reference both `toolId` and `toolRevisionId` where the existing schema supports them.

No second `CREATE_TOOL_DRAFT` audit is created for this composite initial operation.

### R7 — real atomicity

If any of these fail:

```text
Tool insert
ToolRevision insert
audit insert
configured post-write failure hook where applicable
```

the database transaction rolls back all new rows.

A failed command must not leave:

```text
CommerceTool without initial revision
CommerceToolRevision without Tool
business rows without the operation audit
```

### R8 — real concurrent behaviour

Provide executable PostgreSQL evidence for at least:

1. two independent clients/process-equivalent service instances using the same operationId and identical input -> one Tool, one revision, one audit, both callers resolve to the same durable result;
2. same operationId with changed payload/actor -> deterministic replay conflict;
3. different operationIds racing on the same Tool name -> one success and one Tool-name `CONFLICT`;
4. unrelated operationIds creating different Tool names are not serialized by the global publication advisory lock.

Use existing disposable/rehearsal infrastructure where practical. Do not require a developer's manually configured persistent database when the repository already provides an isolated PostgreSQL test path.

### R9 — no timeout inflation workaround

Do not increase:

```text
PrismaPublicationStorage.transaction timeout
```

as the means of passing this task.

If the generic transaction timeout is changed for an independently justified reason, document it as a deviation; the initial-create command must still use the narrow path defined here.

## Work Items

- [ ] Define the narrow initial Tool persistence port/method.
- [ ] Route only the COMMERCE-036 initial-create lifecycle command through it.
- [ ] Implement operation-scoped replay synchronization without the global publication lock.
- [ ] Insert Tool, revision 1 and audit directly in one Prisma transaction.
- [ ] Map Tool-name uniqueness to bounded `CONFLICT` semantics.
- [ ] Preserve identical replay and conflicting-reuse semantics.
- [ ] Add rollback regressions.
- [ ] Add real PostgreSQL concurrency/replay coverage.
- [ ] Prove the new path does not invoke whole-state read/write helpers.

## Interfaces / Contracts

Consumes the COMMERCE-036 lifecycle input/result contract.

Database contract consumed as-is:

```text
CommerceTool.name UNIQUE
CommerceToolRevision @@unique([toolId, revisionNumber])
CommerceToolRevision @@unique([toolId, definitionVersion])
CommerceAuditEvent primary operation/audit identity convention
```

No Shared-package or cross-repository contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-036

## Enables

- ARCH-021-COMMERCE-038

## Acceptance Criteria

- [ ] Initial Tool creation performs no `readState()`, `writeState()` or whole-publication `snapshot()` operation.
- [ ] Initial Tool creation does not acquire the global `moda-commerce-publication` advisory lock.
- [ ] One transaction creates exactly one Tool, revision 1 DRAFT and audit record.
- [ ] The transaction returns both created identifiers without a broad reread.
- [ ] Tool-name uniqueness is database-enforced and mapped to `CONFLICT`.
- [ ] Identical concurrent operation replay returns one durable result and creates one set of business rows.
- [ ] Conflicting operation reuse remains rejected.
- [ ] Failure of any write rolls back Tool, revision and audit together.
- [ ] Different operationIds are not globally serialized solely by publication locking.
- [ ] No Prisma schema/migration change is required.
- [ ] The existing generic storage path for unrelated publication commands remains behaviourally unchanged.

## Validation

- [ ] `npm run test:arch021-tool-authoring-common`
- [ ] `npm run test:arch020-backend-integration`
- [ ] focused initial-create PostgreSQL concurrency/replay/rollback test
- [ ] `npm run prisma:generate` when generated Prisma client state is required by the repository checkout
- [ ] targeted lint/typecheck with zero new task-owned diagnostics
- [ ] source audit proving the initial-create path does not call `readState`, `writeState`, `snapshot` or the global publication advisory lock
- [ ] `git diff --check`

## Stop Condition

After the narrow database path and real concurrency/rollback evidence are complete, set this task to `review`, complete the Completion Report and STOP. Do not expose the command through Studio Server Actions and do not modify the React authoring flow.

## Implementation Notes

Keep business validation/authorization in the Commerce lifecycle/service ownership boundary. The Prisma adapter owns durable atomicity, uniqueness and concurrency mechanics; it must not independently invent different Tool-definition rules.

An operation-keyed PostgreSQL advisory transaction lock is acceptable because it serializes only competing uses of the same operation identity. Do not reuse the current one-lock-for-all-publication-mutations design.

## Completion Report

### Status
Not Started

### Files Changed
None

### Work Completed
None

### Validation Results
None

### Deviations
None

### Assumptions
None

### Unresolved Issues
None

### Architectural Concerns
None

## Architect Review

### Review Status
Pending

### Review Notes
None

### Reviewed Files
None

### Validation Reviewed
None

### Architecture Conformance
Pending

### Follow-up
None
