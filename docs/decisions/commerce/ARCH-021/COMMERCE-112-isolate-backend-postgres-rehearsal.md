---
id: ARCH-021-COMMERCE-112
architecture_id: ARCH-021
title: Isolate backend PostgreSQL rehearsal from persistent databases
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 78
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-09-30
updated: 2026-09-30
---

# Isolate backend PostgreSQL rehearsal from persistent databases

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Make `tests/backend-postgres-rehearsal.test.ts` impossible to run against a long-lived development/staging/production database and make the normal rehearsal command provision and destroy its own invocation-owned PostgreSQL target.

The rehearsal may continue to create records such as:

```text
Updated rehearsal
Race A
Race B
Narrow rehearsal
```

but those records must exist only inside the invocation-owned disposable database, which is destroyed after the run.

## Context

The current command:

```text
npm run test:arch020-backend-integration:postgres
```

delegates to:

```text
scripts/rehearse-commerce-backend-postgres.sh
```

which currently accepts an arbitrary caller-supplied:

```text
DATABASE_URL
```

and runs:

```text
tests/backend-postgres-rehearsal.test.ts
```

against that target.

The test creates/updates durable Tool, ToolRevision, Audit and Release/Pointer state and intentionally does not remove those rows. When the supplied target is a normal development database, the Global tool library accumulates records such as `Updated rehearsal`, `Race A`, `Race B` and `Narrow rehearsal`.

The repository already contains the correct isolation precedent in:

```text
scripts/run-external-wiring-disposable.mjs
scripts/rehearse-publication-postgres.sh
```

where task-owned Docker resources use loopback/random ports, tmpfs storage, ownership labels and guaranteed cleanup.

This task applies the same isolation principle to `backend-postgres-rehearsal.test.ts`.

## Scope

Primary changes:

```text
tests/backend-postgres-rehearsal.test.ts
scripts/rehearse-commerce-backend-postgres.sh
scripts/run-backend-postgres-rehearsal-disposable.mjs
```

`package.json` should remain unchanged because its existing:

```text
test:arch020-backend-integration:postgres
```

script already invokes `scripts/rehearse-commerce-backend-postgres.sh`.

Do not change production persistence code.

## Out of Scope

- Deleting already-existing rehearsal records from the developer's current database.
- Modifying Tool library presentation; COMMERCE-111 owns that concern.
- Changing production Tool/Release/Audit semantics.
- Weakening or deleting existing rehearsal assertions.
- Replacing PostgreSQL integration coverage with mocks.
- Using a shared development/staging database with post-test cleanup as the primary safety mechanism.
- Requiring Redis for this PostgreSQL-only rehearsal.
- Changing Prisma schema/migrations.
- Updating `docs/decisions/commerce/ARCH-021/_index.md` during implementation. Architect review will reconcile the index after acceptance.

## Requirements

### R1 — direct test invocation fails closed before Prisma connects

Before constructing:

```ts
new PrismaClient()
```

validate all of:

```text
COMMERCE_BACKEND_REHEARSAL_DISPOSABLE=1
DEPLOYMENT_ENVIRONMENT_NAME=test
DATABASE_URL present
database name matches:
  ^arch021_backend_rehearsal_[a-z0-9_]+$
```

Parse the database name from the `DATABASE_URL` pathname.

Use stable errors:

```text
BACKEND_REHEARSAL_UNSAFE_ENVIRONMENT
BACKEND_REHEARSAL_UNSAFE_DATABASE_TARGET
```

If any check fails, throw before a Prisma client can connect or any write can occur.

Do not add an override that bypasses this guard.

### R2 — the normal runner owns its PostgreSQL target

Add:

```text
scripts/run-backend-postgres-rehearsal-disposable.mjs
```

using the repository's existing disposable-Docker patterns.

It MUST:

```text
require ARCH020_REHEARSAL_ALLOW_DISPOSABLE_DOCKER=1
require a local Unix-socket Docker context
use postgres:16.4-alpine
create a unique runId and container name
label ownership:
  moda.commerce.backend-rehearsal-run=<runId>
create database:
  arch021_backend_rehearsal_<safeRunSuffix>
generate a random password
publish PostgreSQL only to 127.0.0.1 on a Docker-assigned random port
use tmpfs for /var/lib/postgresql/data
create no persistent Docker volume
wait for pg_isready
```

Do not use a caller-supplied `DATABASE_URL` as the target.

The child test receives only the runner-generated URL.

### R3 — prepare Prisma only inside the task checkout/disposable target

Before the Vitest rehearsal:

```text
generate Prisma Client from database/prisma/schema.prisma
prepare the disposable database from database/prisma/schema.prisma
```

Use the repository-local Prisma CLI.

Database preparation may use:

```text
prisma db push --schema database/prisma/schema.prisma --skip-generate
```

because this task validates backend adapter behaviour, not migration sequencing.

### R4 — make the rehearsal fixture self-contained

`backend-postgres-rehearsal.test.ts` must no longer depend on arbitrary pre-existing rows such as:

```text
an active PlatformAdmin
an existing Feature Capability
an existing published Tool revision
```

Create the minimum prerequisite graph inside the disposable database before behavioural assertions.

Use a run-unique suffix and seed:

```text
one active SUPER_ADMIN PlatformAdmin
one active billing Feature
one baseline Tool
one DRAFT Tool revision
publish that revision through the real Commerce lifecycle
one direct Feature Capability bound to that Tool
```

Use existing production lifecycle/Feature-authoring services for Tool publication and Capability creation rather than bypassing the code path with a fake published state.

### R5 — stop scanning ambient database state

Replace the current prerequisite discovery:

```ts
releaseState.capabilities.find(...)
```

with the exact Capability identity created by the rehearsal fixture.

Release creation must use that test-owned Capability explicitly.

The test must not depend on rows left by another developer/test.

### R6 — preserve all existing behavioural proof

Keep coverage for:

```text
snapshot/transaction parity
durable replay
conflicting replay rejection
stale CAS rejection
same-row CAS race across independent clients
release creation
release activation
rollback on injected failure
narrow initial Tool creation replay
same-name race
rollback of injected narrow failure
audit result identity
independence from the legacy global publication lock
```

Do not weaken assertions to simplify disposable setup.

### R7 — the public rehearsal shell no longer accepts a persistent target

Change:

```text
scripts/rehearse-commerce-backend-postgres.sh
```

to perform only:

```text
set -euo pipefail
cd repository root
node scripts/run-backend-postgres-rehearsal-disposable.mjs
bash scripts/rehearse-publication-postgres.sh
```

Remove the current caller-`DATABASE_URL` contract.

The first phase owns its disposable PostgreSQL container. The existing publication rehearsal continues to own/clean its separate disposable container.

### R8 — cleanup is mandatory

The new runner must clean its invocation-owned PostgreSQL container from a `finally`/termination-safe path.

Cleanup MUST:

```text
verify ownership label before deletion
remove the container
verify no container with the current ownership label remains
```

If cleanup fails, return non-zero and print the retained resource identity.

Handle normal completion plus SIGINT/SIGTERM without silently leaking the container.

### R9 — no hidden external target path

Do not support:

```text
DATABASE_URL override
COMMERCE_TEST_DATABASE_URL override
pre-existing PostgreSQL host/port
shared named database
Docker volume reuse
```

for this rehearsal.

If Docker is unavailable, fail/block. Never fall back to the developer database.

### R10 — historical pollution cleanup remains separate

C112 prevents new pollution.

Do not add a migration or broad delete query that removes historical `rehearsal_*`, `narrow_*`, `race_*` rows from an arbitrary database. Existing rows may now be referenced and need explicit operator review.

## Work Items

- [ ] Add the fail-closed disposable-target guard before PrismaClient construction.
- [ ] Seed the test's own active admin, Feature, published Tool and direct Capability prerequisite.
- [ ] Replace ambient Capability discovery with the exact fixture Capability ID.
- [ ] Add the invocation-owned disposable PostgreSQL runner.
- [ ] Bind PostgreSQL only to loopback/random port and use tmpfs/no volume.
- [ ] Prepare Prisma client/schema only against the disposable target.
- [ ] Preserve the existing backend rehearsal behavioural breadth.
- [ ] Guarantee ownership-checked cleanup on pass/fail/signals.
- [ ] Make `rehearse-commerce-backend-postgres.sh` call the disposable runner, then the existing publication rehearsal.
- [ ] Prove the unsafe-target guard fails before connection.
- [ ] Prove the normal rehearsal leaves zero task-owned Docker resources.
- [ ] Run targeted ESLint, typecheck and `git diff --check`.
- [ ] Complete the Completion Report and STOP.

## Interfaces / Contracts

No production interface changes.

New test-only execution contract:

```text
COMMERCE_BACKEND_REHEARSAL_DISPOSABLE=1
DEPLOYMENT_ENVIRONMENT_NAME=test
DATABASE_URL=<runner-owned arch021_backend_rehearsal_* database>
```

The normal npm command creates that environment.

## Dependencies

None.

This task is independent of COMMERCE-111.

## Enables

None.

## Acceptance Criteria

- [ ] Direct test execution rejects an ordinary development database name before Prisma connection/write.
- [ ] Direct execution rejects a missing disposable-authorization flag.
- [ ] Direct execution rejects a non-test deployment environment.
- [ ] The normal npm rehearsal creates its own PostgreSQL container/database.
- [ ] The runner never uses a caller-supplied DATABASE_URL as the target.
- [ ] The target database name matches `arch021_backend_rehearsal_*`.
- [ ] PostgreSQL is bound only to loopback on a random host port.
- [ ] Database storage is tmpfs and no persistent Docker volume is created.
- [ ] The rehearsal creates its own prerequisite admin/Feature/published Tool/Capability graph.
- [ ] Release creation uses the exact test-owned Capability rather than scanning ambient state.
- [ ] All existing replay/CAS/race/rollback/narrow-lock assertions still pass.
- [ ] Updated rehearsal / Race A / Race B / Narrow rehearsal exist only inside the disposable database for that run.
- [ ] The invocation-owned container is removed after success.
- [ ] The invocation-owned container is removed after failure.
- [ ] Cleanup failure is surfaced as command failure.
- [ ] The existing publication PostgreSQL rehearsal still runs after the backend rehearsal.
- [ ] No Prisma schema/migration or production persistence code is changed.
- [ ] Project typecheck and targeted lint pass.

## Validation

### Unsafe-target guard

Prove a non-disposable database is rejected **before connection** using a URL whose host need not exist:

```text
COMMERCE_BACKEND_REHEARSAL_DISPOSABLE=1
DEPLOYMENT_ENVIRONMENT_NAME=test
DATABASE_URL=postgresql://invalid:invalid@127.0.0.1:1/moda_development
```

Run only the backend rehearsal test and assert failure contains:

```text
BACKEND_REHEARSAL_UNSAFE_DATABASE_TARGET
```

It must fail because of the database-name guard, not because port `1` is unreachable.

Also prove absence of:

```text
COMMERCE_BACKEND_REHEARSAL_DISPOSABLE=1
```

fails with:

```text
BACKEND_REHEARSAL_UNSAFE_ENVIRONMENT
```

### Full disposable proof

With local Docker available:

```text
ARCH020_REHEARSAL_ALLOW_DISPOSABLE_DOCKER=1 \
npm run test:arch020-backend-integration:postgres
```

Required evidence:

```text
backend-postgres-rehearsal.test.ts passes
existing publication PostgreSQL rehearsal passes
runner prints invocation-owned container identity
runner prints cleanup success
zero containers remain for the run ownership label
```

### Static/project validation

Run:

```text
npm exec -- eslint \
  tests/backend-postgres-rehearsal.test.ts \
  scripts/run-backend-postgres-rehearsal-disposable.mjs

npm run typecheck
git diff --check
```

Inspect:

```text
git diff -- \
  tests/backend-postgres-rehearsal.test.ts \
  scripts/rehearse-commerce-backend-postgres.sh \
  scripts/run-backend-postgres-rehearsal-disposable.mjs
```

and confirm no unrelated source/dependency churn.

If Docker is unavailable in the prepared task environment, record the exact environment blocker and return the task `blocked`; do not validate against a long-lived database instead.

## Stop Condition

After disposable isolation and the full Docker proof pass:

1. set C112 to `review`;
2. complete the Completion Report with exact launcher/worktree/synchronization/submodule evidence, Docker ownership/cleanup evidence and validation results;
3. STOP.

Do **not** update:

```text
docs/decisions/commerce/ARCH-021/_index.md
```

during implementation. The Architect review/acceptance step owns the index reconciliation.

Do not begin COMMERCE-111 or another follow-on task.

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
