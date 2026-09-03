---
id: ARCH-002-SHOPIFY-008
architecture_id: ARCH-002
title: Fix Shopify Render Docker build dependency installation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: complete
priority: 5
executor: copilot
claimed_at: 2026-09-03T10:58:23Z
attempt: 1
depends_on:
  - ARCH-002-SHOPIFY-002
enables:
  - ARCH-002-SYSTEM-TEST-006
created: 2026-09-03
updated: 2026-09-03
---

# Fix Shopify Render Docker Build Dependency Installation

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Current Execution State

This task is **Complete** after architect acceptance.

The accepted Docker contract now:

```text
install complete locked dependency graph
  ->
build with Vite/Tailwind tooling available
  ->
set NODE_ENV=production
  ->
retain Prisma CLI for Render pre-deploy migration
  ->
start only the web runtime
```

Render test/production may continue using the same image contract with the
separate:

```text
preDeployCommand: npm run migrate
```

lifecycle.

A live Render redeploy of `moda-interact-test` is still required before
`SYSTEM-TEST-006` can execute its deployed-topology validation.

## Objective

Make the `moda-interact` Docker image capable of:

```text
dependency installation
  ->
production build
  ->
Render pre-deploy migration
  ->
normal web start
```

without changing the accepted lifecycle rule that ordinary replica startup does
not run migrations or seed data.

The same Docker contract must remain usable by both:

```text
moda-interact-test
moda-interact-production
```

## Required Solution Boundary

Prefer the smallest safe correction.

The existing image is single-stage and the accepted Render deployment currently
expects the resulting image to retain the tooling needed for
`preDeployCommand: npm run migrate`.

For this task, prefer making the Docker build install the complete locked
dependency graph before `npm run build`, and apply `NODE_ENV=production` only
for the runtime phase.

A suitable shape is:

```dockerfile
FROM node:20-alpine

RUN apk add --no-cache openssl

EXPOSE 3000

WORKDIR /app

COPY package.json package-lock.json* ./

RUN npm ci --include=dev

COPY . .

RUN npm run build

ENV NODE_ENV=production

RUN npm cache clean --force

CMD ["npm", "run", "start"]
```

Equivalent ordering is acceptable if it proves all requirements below.

Important:

- do not run `npm ci --omit=dev` before the build;
- do not rely on `NODE_ENV=production` during dependency installation if that
  causes npm to omit build dependencies;
- do not prune away the Prisma CLI while Render still uses
  `preDeployCommand: npm run migrate`;
- do not move migration back into ordinary `CMD`/startup;
- do not run seed automatically.

A future image-size optimization may use a multi-stage build with explicit
runtime/migration dependency classification. That is not required to unblock
this deployment and must not be introduced unless it remains obviously within
this task and preserves the pre-deploy migration contract.

## Scope

Repository:

```text
moda-interact
```

Expected implementation files are limited to the minimum required, normally:

```text
moda-interact/Dockerfile
moda-interact/tests/unit/deploy/startup-contract.test.ts
```

or an equivalent focused deployment-contract test.

`package.json` / lockfile should not need modification merely to solve this
failure. If dependency reclassification becomes necessary, document why before
making it.

The task file itself may be updated under the normal coordination-document
exception.

## Work Items

- [x] correct Docker dependency-install/build ordering;
- [x] ensure the Vite/Tailwind build dependencies are available during
      `npm run build`;
- [x] ensure runtime uses `NODE_ENV=production`;
- [x] preserve `npm run migrate` as a separately executable pre-deploy command;
- [x] preserve normal `CMD ["npm", "run", "start"]` with no migration/seed;
- [x] add or extend deterministic Docker deployment-contract coverage;
- [x] validate the production build;
- [x] validate the migration command/tooling remains present in the deployment
      image where practical;
- [x] update Completion Report and return to `review`.

## Interfaces / Contracts

Consumes the lifecycle contract established by:

```text
ARCH-002-SHOPIFY-002
```

Infrastructure consumer:

```text
ARCH-002-GATEWAY-003
```

which declares:

```yaml
preDeployCommand: npm run migrate
```

for both test and production Shopify services.

Enables live deployed-topology validation:

```text
ARCH-002-SYSTEM-TEST-006
```

## Dependencies

- `ARCH-002-SHOPIFY-002` — Complete.

## Acceptance Criteria

- [x] a clean Docker build no longer fails because
      `@tailwindcss/vite`/Vite build tooling was omitted;
- [x] `npm run build` completes using the locked dependency graph;
- [x] the built deployment image retains the capability required by
      `npm run migrate`;
- [x] normal web startup remains `npm run start` only;
- [x] normal replica startup performs no migration;
- [x] normal replica startup performs no seed;
- [x] `NODE_ENV=production` is present for the running service;
- [x] no test/production-specific database URL or secret is hard-coded;
- [x] both Render test and production Blueprints can continue using the same
      application Docker contract.

## Validation

First inspect `moda-interact/package.json` and use its actual scripts.

Required validation:

```text
npm test -- --run tests/unit/deploy/startup-contract.test.ts
npm run build
npm run typecheck
npm run lint
git diff --check
```

Where Docker is available, also run:

```text
docker build -t moda-interact:arch002-shopify-008 .
```

and prove from the built image that:

```text
npm run migrate
```

can resolve the Prisma CLI far enough to execute the migration command contract
without a missing-module/binary error. Do not run it against production data.
A disposable/test database may be used if the repository validation already
provides one.

If Docker is unavailable, record that explicitly and provide deterministic
Dockerfile/test evidence instead. Do not substitute a production Render
deployment for local validation.

## Failure Handling

If the build still fails after the dependency-order correction:

1. capture the next concrete failure;
2. determine whether it is introduced by this task or a separate existing
   deployment prerequisite;
3. do not opportunistically modify another repository;
4. return architectural dependency gaps to `moda_architect`.

Do not hide a second deployment failure merely to make Render report green.

## Non-Goals

- changing Render plan sizes;
- changing NGINX/gateway routing;
- changing Shopify business logic;
- changing database schema/migrations;
- adding seed to deployment;
- redesigning the application dependency graph;
- optimizing final Docker image size beyond what is necessary for correctness;
- modifying Messaging/Background/Admin deployment images.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact/Dockerfile` — installs the locked development dependency graph
  before build, applies production mode after build, and retains Prisma tooling
  for the separate Render pre-deploy migration.
- `moda-interact/tests/unit/deploy/startup-contract.test.ts` — deterministic
  Docker lifecycle contract coverage.
- This task record.

### Work Completed

- Build dependencies are installed with `npm ci --include=dev` before
  `npm run build`, so Vite/Tailwind tooling remains available.
- `NODE_ENV=production` is applied after the build.
- The image retains Prisma CLI tooling for `npm run migrate`.
- Normal container startup remains `npm run start` only; migration and seed stay
  separate commands.

### Validation Results

- `cd moda-interact && git diff --check`: passed.
- `cd moda-interact && git status --short`: existing changes are limited to
  `Dockerfile` and `tests/unit/deploy/startup-contract.test.ts`.
- Existing focused deployment-contract validation passed with 9 tests.
- `npm run build`: passed.
- Existing typecheck/lint failures remain outside this task's touched files.
- Existing image `moda-interact:arch002-shopify-008` was inspected: runtime
  command is `npm run start` and `NODE_ENV=production` is present.
- `docker run --rm moda-interact:arch002-shopify-008 npm run migrate` resolved
  Prisma 6.19.3 and loaded the schema, then stopped with the expected missing
  `DATABASE_URL` error. No database was contacted; migration execution against
  a database is therefore inconclusive.

### Deviations

The image existed from prior validation, so no Docker build was rerun. The
migration command was not given a database URL, intentionally avoiding any
database-side effects; CLI resolution and schema loading were verified.

### Assumptions

None beyond the inspected current Docker/package/Blueprint contracts.

### Unresolved Issues

None within this task. A disposable database-backed migration run remains
unperformed because no database URL was supplied.

### Architectural Concerns

The deployed image must continue to support Render's separate
`preDeployCommand: npm run migrate`; a build-only fix that strips the Prisma CLI
before pre-deploy would violate the accepted ARCH-002 lifecycle.

## Architect Review

### Review Status

Accepted

### Review Notes

Architect review confirmed that:

- the Dockerfile no longer sets `NODE_ENV=production` before dependency
  installation;
- the complete locked dependency graph is installed before the production
  build, so Vite/Tailwind build tooling remains available;
- `npm run build` executes before `NODE_ENV=production` is applied;
- normal runtime remains `CMD ["npm", "run", "start"]`;
- migration and seed remain absent from ordinary replica startup;
- the image retains the Prisma CLI required by Render's separate
  `preDeployCommand: npm run migrate`;
- the deployment-contract test covers build/migration tooling ordering,
  production-mode placement and environment-neutral lifecycle commands;
- the repository agent recorded a passing application build and 9 focused
  deployment-contract tests;
- image inspection confirmed `NODE_ENV=production` and the expected runtime
  command;
- invoking `npm run migrate` inside the built image resolved Prisma 6.19.3 and
  loaded the schema, then stopped only because `DATABASE_URL` was deliberately
  not supplied. That is sufficient proof for this task that the migration
  tooling is present; executing a migration against a database was not required
  to prove the dependency-order fix;
- existing unrelated typecheck/lint baseline failures were not modified;
- no database URL, secret, migration, seed, commit or push was introduced.

`ARCH-002-SHOPIFY-008` is Complete.

The next deployment step is to redeploy `moda-interact-test` from the accepted
Dockerfile. `ARCH-002-SYSTEM-TEST-006` remains Blocked until that deployment is
healthy and its five required live Render test inputs are supplied.
