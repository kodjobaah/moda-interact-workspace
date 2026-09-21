---
id: ARCH-020-DATABASE-003
architecture_id: ARCH-020
title: Persist external API connections and encrypted credentials
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
executor: null
claimed_at: null
priority: 145
attempt: 1
depends_on:
  - ARCH-020-DATABASE-001
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-020
  - ARCH-020-COMMERCE-028
created: 2026-09-21
updated: 2026-09-21
---

# Persist external API connections and encrypted credentials

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Own Prisma schema, SQL migrations, generated-client guidance and ERD only. Implement exactly the four models, enums, partial indexes and immutable triggers in C21 section3. Do not implement encryption, HTTP, Studio or application seed data.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Own Prisma schema, SQL migrations, generated-client guidance and ERD only. Implement exactly the four models, enums, partial indexes and immutable triggers in C21 section3. Do not implement encryption, HTTP, Studio or application seed data.

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

- [ ] Map every section3 field to Prisma/SQL, retaining existing tables and grants. Add Shop/PlatformAdmin backrelations and RESTRICT relations.
- [ ] Provide migrations for credential scope uniqueness (including NULL platform rows), version/bounds checks and immutable revisions/audit. Encryption bytes are stored opaquely; no plaintext field.
- [ ] Document migration/client-generation consumption for Commerce nested database submodule and rollback limitations; do not copy schema into consumers.

## Interfaces / Contracts

C21 is the shared contract between these tasks. Own only the paths identified
above. Record exact accepted dependency SHA/package version and source exports
in the Completion Report. No catch-all shared integration barrel. Return genuine
contract contradictions with a source reproduction; do not weaken validation.

## Dependencies

- ARCH-020-DATABASE-001

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-020
- ARCH-020-COMMERCE-028

## Acceptance Criteria

- [ ] X02: fresh and existing disposable database migrations succeed without changing existing tool/grant rows.
- [ ] Duplicate platform/shop credential rows, invalid byte lengths, stale immutable updates/deletes and foreign keys fail with expected constraints; transaction rollback leaves zero partial rows.

## Validation

Provide `test:arch020-external-connections:database` in the owning repository and document its exact scope.
Run focused changed-boundary tests, then existing repository typecheck/build
and lint where defined. Inspect package scripts first; do not invent a claim that
an absent script passed. Use C21 controlled transports and isolated stores.
Follow current developer-owned live/container validation policy; clearly separate
actual agent results from required unrun developer checks. No arbitrary screenshot
quota or repeated full-suite runs without new changes/failures.

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

Implementation submitted for architect review.

### Files Changed

- `prisma/schema.prisma`
- `prisma/migrations/20260921160000_arch020_external_connections/migration.sql`
- `scripts/validate-arch020-external-connections.mjs`
- `scripts/generate-erd.mjs`
- `docs/generated/prisma-erd.puml`
- `docs/generated/erd.png`
- `README.md`
- `package.json`

### Work Completed

Implemented the C21 section 3 database boundary in the dedicated database
worktree: four commerce models, three enums, Shop/PlatformAdmin backrelations,
RESTRICT foreign keys, version/length/digest/object checks, platform and
per-shop credential partial unique indexes, and immutable revision/audit
triggers. Credentials are stored only as opaque byte columns; no plaintext
secret field or application encryption was added. The ERD generator now removes
trailing whitespace emitted by the PlantUML generator so generated output passes
repository whitespace checks. The validator covers fresh/upgrade migration
rehearsals, existing-row preservation, duplicate platform/shop credentials,
credential byte bounds, foreign keys, immutable rows, and transaction rollback.

### Validation Results

Passed in the dedicated implementation worktree:

- `node --check scripts/validate-arch020-external-connections.mjs`
- `npm run prisma:validate`
- `npm run prisma:generate`
- `npm run format -- --check`
- `npm run erd:puml`
- `git diff --check`

Not run: fresh and upgrade disposable PostgreSQL validator modes. The local
PostgreSQL database was unavailable (`arch020_connections_test_fresh` did not
exist), and database provisioning was cancelled. No database pass is claimed.

### Deviations

The PostgreSQL acceptance rehearsal remains for architect/developer execution
when isolated local databases are available. No schema or application fallback
was added to compensate.

### Assumptions

C21 read-only scope; visual rules and generic JavaScript only inside the specified sandbox.

### Unresolved Issues

Database-backed X02 evidence is pending because the isolated PostgreSQL test
databases were unavailable in this execution environment.

### Architectural Concerns

Return contradictory accepted source facts to moda_architect before weakening contracts.

### Git / VCS

Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-DATABASE-003`.
Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-DATABASE-003`.
Attempt 1. Implementation commit `a96dfd7` pushed to
`origin/task/ARCH-020-DATABASE-003`. Repository baseline was `5abfd87f`; Prisma
client version was `6.19.3`. No submodules were present in the implementation
packet. Parent claim commit was `b1f07a21`.

## Architect Review

### Attempt 1 — Changes Requested (2026-09-21)

Reviewer: moda_architect. Reviewed implementation `a96dfd7f78a8d8c6b2d9dc1fbfd3a92df0623a7b` and parent report `cee2910850e0e3e7d9ed53452feaa6cde9a52cc5`; dedicated worktrees clean and both submitted remote heads verified. **Changes Requested; Ready, Attempt 1 retained; executor/claimed_at null.**

The additive SQL contains the four C21 tables, required enums, partial platform/shop uniqueness, RESTRICT relations, opaque credential bytes, bounded checks and immutable revision/audit triggers. No application encryption or provider implementation was added. Preserve that scope. Three concrete corrections remain before the required X02 rehearsal can provide trustworthy evidence.

#### A1-R1 — Align Prisma timestamps with the C21 migration

File: `prisma/schema.prisma`, all four CommerceExternal models.

C21 section3 and the migration require timestamptz(3), but all six new timestamp fields use plain DateTime without @db.Timestamptz(3). Prisma's schema SQL therefore describes TIMESTAMP(3), different from the checked-in migration's TIMESTAMPTZ(3). This is a schema/migration inconsistency that can produce drift and later timezone-changing alterations; Prisma syntax validation alone does not detect it.

Add @db.Timestamptz(3) to createdAt/updatedAt on CommerceExternalConnection and CommerceExternalCredential, and createdAt on CommerceExternalConnectionRevision and CommerceExternalConnectionAudit. Preserve @default(now()) and @updatedAt semantics; reconcile any SQL/Prisma default differences deliberately. Regenerate the client/ERD as required and compare the new tables' generated SQL against the migration. Do not alter existing unrelated timestamp columns.

#### A1-R2 — Make fresh/upgrade fixture setup executable

File: `scripts/validate-arch020-external-connections.mjs`, Shop and PlatformAdmin inserts in both modes.

Both branches issue raw INSERTs containing only Shop(id,domain) and PlatformAdmin(id,email). Their accepted baseline migration defines updatedAt as NOT NULL with no SQL default. Prisma @updatedAt is applied by Prisma model operations, not by $executeRawUnsafe. Thus either mode will fail in setup before exercising the new tables, even after the missing database is provisioned.

Supply deterministic updatedAt values in all four raw fixture INSERTs, or use valid Prisma model creation that supplies the required fields. Retain explicit disposable-target/empty-database guards; do not add production defaults or disable constraints to make the rehearsal pass. Document the exact two mode commands and their prerequisites. This is a script defect independent of current infrastructure availability.

#### A1-R3 — Ensure X02 assertions measure their claimed constraints and preserved data

File: the same validator, mustReject helper, rejection fixtures and upgrade preservation.

mustReject currently treats every exception as success. A missing table, wrong fixture, connection failure or an unrelated constraint can therefore masquerade as the intended protection. In particular, deleting the referenced revision could fail through credential FKs even without its immutable trigger. Several credential-bound checks reuse the already occupied platform revision, so a unique-index failure could mask a missing byte-bound check. Upgrade preservation compares only Shop/Admin row counts, not contents or the existing tool/grant records explicitly named in X02.

Use the database error's SQLSTATE and available constraint identity to distinguish the expected unique/check/FK/immutable failure from infrastructure or unrelated errors. Where Prisma does not expose the constraint name, isolate the violating condition using an otherwise valid unoccupied fixture and assert the specific SQLSTATE. Verify immutable DELETE on an unreferenced revision so an FK cannot satisfy the assertion. Retain a successful adjacent insert before each boundary group. For rollback, assert the intended failure occurred after the first successful write and that its inserted row is absent afterward.

For upgrade, seed a minimal valid existing tool/revision/grant graph under the predecessor schema (reuse the existing accepted fixture helpers where suitable), record relevant row contents/hashes before applying this additive migration and compare after, alongside Shop/Admin. Counts alone cannot establish unchanged values. This is the required X02 migration preservation evidence, not a request to test the whole legacy database or add an exhaustive constraint matrix.

#### Verification and disposition

Reran Node syntax validation and `npm run prisma:validate`: passed. Rendered schema SQL with `prisma migrate diff --from-empty --to-schema-datamodel prisma/schema.prisma --script` without a database: all six new timestamps are TIMESTAMP(3), confirming A1-R1 against the migration's TIMESTAMPTZ(3). Static review traced the fixture inserts to the accepted baseline SQL and reviewed migration constraints, triggers, schema, validator and documentation. No PostgreSQL provisioning, migration or container operation was performed. The report correctly leaves real fresh/upgrade evidence unrun; no database-backed pass is inferred from static checks.

Unlike the migration checks discussed for COMMERCE-013, fresh/upgrade and constraint validation directly belong to DATABASE-003 because this task creates the migration. After fixing the script/schema issues, the two isolated modes still require real execution and recorded results before X02 is established. Keep unrun evidence explicit and use developer-provided/authorized disposable infrastructure; do not silently mark it passed or change shared databases.

Ready for corrections, Attempt 1 retained, claims cleared. No acceptance, implementation edits, main merge, gitlink update or downstream promotion. COMMERCE-020/028 remain gated on their actual dependencies; no automatic launch. Historical submission review notes are retained below and superseded by this decision.


### Review Status

Pending.

### Review Notes

Implementation is bounded to the C21 section 3 database ownership. Review the
migration SQL and run the documented fresh/upgrade PostgreSQL validator before
acceptance; this report intentionally leaves that evidence open.

### Reviewed Files

Implementation commit `a96dfd7` and the files listed in the Completion Report.

### Validation Reviewed

Repository-side Prisma, generator, formatting, syntax, and whitespace checks
passed. PostgreSQL migration/constraint rehearsal remains unrun.

### Architecture Conformance

Conforms to the C21 section 3 ownership and does not implement encryption,
HTTP, Studio, or application seed data.

### Follow-up

Run both documented disposable PostgreSQL validator modes, then accept or return
for rework. No downstream task was launched.
