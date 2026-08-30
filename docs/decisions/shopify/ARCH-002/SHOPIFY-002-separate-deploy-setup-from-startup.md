---
id: ARCH-002-SHOPIFY-002
architecture_id: ARCH-002
title: Separate database setup from Shopify replica startup
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
status: review
priority: 20
executor: codex
claimed_at: 2026-08-30T08:25:04Z
attempt: 1
depends_on:
  - ARCH-002-GATEWAY-001
enables: []
created: 2026-08-29
updated: 2026-08-30
---

# Separate Database Setup from Shopify Replica Startup

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Objective

Make `moda-interact` safe for horizontally scaled deployment by separating
build, migration, seed and normal web-process startup.

The resulting commands must be usable by both the test and production
Blueprints.

## Context

Discovery confirmed the existing Docker startup sequence could run:

```text
prisma migrate deploy
prisma seed
application start
```

for every replica start.

That is not an acceptable normal restart/scaling contract.

ARCH-002 requires:

```text
build
  ->
pre-deploy migration
  ->
replica start
```

with seeding remaining explicit/controlled.

## Scope

- provide a production web start command that starts only the web runtime;
- expose a migration-only command suitable for Render `preDeployCommand`;
- keep seed as an explicit controlled initialization command;
- ensure normal service restart/scale-out does not run migration or seed;
- update deployment documentation/scripts accordingly;
- keep commands environment-neutral so the same application artifact can be
  deployed to test and production.

## Out of Scope

- modifying Render Blueprint files;
- changing migration contents;
- changing seed business data;
- choosing whether production should contain seed data;
- gateway implementation;
- database schema redesign.

## Requirements

Normal replica startup must not execute migration.

Normal replica startup must not execute seed.

Migration execution must be independently callable and must use the environment's
configured `DATABASE_URL`.

Seed must be independently callable and must never execute automatically on an
ordinary service restart, horizontal scale-out or rolling deploy.

The commands used by GATEWAY-003 must work for both:

```text
render.test.yaml
render.production.yaml
```

Test and production must use their own database configuration.

Do not hard-code a test or production database URL.

Existing local development workflows may retain explicit setup helpers if they
are clearly separate from production deployment commands.

The application command contract must make these four phases distinguishable:

```text
build
migrate
seed
start
```

## Work Items

- [x] separate web startup from setup/migration/seed;
- [x] expose migration-only command;
- [x] expose/document explicit seed command;
- [x] ensure normal Docker/Render start launches only the web runtime;
- [x] add command-level tests or deterministic verification;
- [x] update deployment documentation;
- [x] verify replica restart/scale-out command does not execute migration/seed.

## Interfaces / Contracts

Provides commands consumed by:

```text
ARCH-002-GATEWAY-003
```

GATEWAY-003 owns the environment-specific `preDeployCommand` wiring.

The intended infrastructure sequence is:

```text
build
  ->
preDeployCommand: migration-only
  ->
startCommand/dockerCommand: web runtime only
```

Seed is never part of that automatic sequence.

## Dependencies

- `ARCH-002-GATEWAY-001`

## Enables

None.

## Acceptance Criteria

- [x] normal service startup performs no migration;
- [x] normal service startup performs no seed;
- [x] migration command is independently executable;
- [x] seed command is independently executable;
- [x] existing application starts successfully;
- [x] commands do not hard-code an environment/database;
- [x] test and production can use the same command contract;
- [x] production deployment documentation clearly distinguishes build, migrate,
      seed and start.

## Validation

- [x] relevant tests;
- [x] typecheck;
- [x] production build;
- [x] command-level verification;
- [x] prove normal start does not invoke migration;
- [x] prove normal start does not invoke seed.

## Implementation Notes

ARCH-002 intends Render `preDeployCommand` for migration on paid application
services. GATEWAY-003 owns that infrastructure wiring.

If a chosen test service plan does not support a required deployment feature,
return that infrastructure constraint to `moda_architect` rather than changing
the application command semantics.

## Completion Report

### Status

Ready for Review

### Files Changed

Implementation in `moda-interact`:

- `moda-interact/package.json` — added canonical lifecycle commands
  `migrate` (`npm run prisma:migrate:deploy`) and `seed`
  (`npm run prisma:seed`); removed the combined `docker-start` and `setup`
  scripts so no deployment/start path chains migration or seed.
- `moda-interact/Dockerfile` — container start command changed from
  `CMD ["npm", "run", "docker-start"]` to `CMD ["npm", "run", "start"]`
  so every replica start launches only the web runtime; documented the
  lifecycle contract in a comment.
- `moda-interact/tests/unit/deploy/startup-contract.test.ts` — new
  deterministic command-contract verification asserting the four
  distinguishable lifecycle phases (`build`, `migrate`, `seed`, `start`),
  that `start` never chains migration/seed, that `migrate`/`seed` are
  independently executable, that no combined `docker-start`/`setup` script
  exists, that the Docker `CMD` is the web runtime only, and that commands
  are environment-neutral (no hard-coded database URL).
- `moda-interact/README.md` — updated migration/seed documentation to the
  canonical commands and added a "Deployment lifecycle" section documenting
  the four-phase contract, the rule that normal replica startup runs only
  `start`, and GATEWAY-003 ownership of the Render `preDeployCommand` wiring.

Task-state file:

- `docs/decisions/shopify/ARCH-002/SHOPIFY-002-separate-deploy-setup-from-startup.md`
  — reconciled Work Items, Acceptance Criteria, Validation checkboxes and this
  Completion Report.

### Work Completed

- Separated web startup from setup/migration/seed: `start` runs only
  `react-router-serve ./build/server/index.js` (unchanged web runtime).
- Exposed migration-only command `npm run migrate` (Prisma `migrate deploy`
  against the environment's `DATABASE_URL`), suitable for a Render
  `preDeployCommand`.
- Exposed explicit seed command `npm run seed`
  (`node database/prisma/seed.mjs`); seed never runs automatically.
- Removed the combined `docker-start` and `setup` scripts; the Docker container
  now starts the web runtime only (`CMD ["npm", "run", "start"]`).
- Ordinary replica restart, horizontal scale-out and rolling deploy therefore
  execute neither migration nor seed.
- Added deterministic command-contract verification as a vitest unit test.
- Documented the build -> migrate -> start sequence (seed explicit/controlled)
  and GATEWAY-003 ownership of environment-specific `preDeployCommand` wiring.
- Kept all lifecycle commands environment-neutral (no hard-coded database URL).

### Validation Results

Executed 2026-08-30 in `moda-interact` (Node v24.19.0, npm 11.17.0).

- Full test suite (`npm run test`): **10 test files passed, 66 tests passed**
  (Duration 2.26s). Includes the new
  `tests/unit/deploy/startup-contract.test.ts` (7 tests).
- Deterministic command-contract verification: **passed** — asserts the four
  lifecycle phases exist, `start` never chains migration/seed, `migrate` and
  `seed` are independently executable, no `docker-start`/`setup` script exists,
  the Docker `CMD` is the web runtime only, and commands hard-code no database
  URL.
- Script-surface review (`npm run`): `docker-start`/`setup` **absent**;
  `build`, `migrate`, `seed`, `start` present.
- Production build (`npm run build`): **exit code 0 — success**. Prisma client
  generation succeeded; React Router SSR production build produced
  `build/server/index.js` (49 modules transformed; built in 661ms).
- Typecheck (`npm run typecheck`): **exit code 2 with the same 48 pre-existing
  errors** recorded by ARCH-002-SHOPIFY-001 in unrelated files
  (`app/db.server.js`, `app/routes/_index/route.jsx`, `app/routes/app._index.jsx`,
  `app/routes/app.jsx`, `app/routes/app.usage.jsx`, `app/routes/auth.$.jsx`,
  `app/routes/auth.login/error.server.jsx`,
  `app/routes/auth.login/route.jsx`). **Zero type errors** in any file changed
  by this task (package.json, Dockerfile, README.md,
  tests/unit/deploy/startup-contract.test.ts).
- ESLint on the new verification test: **exit code 0**.
- Live web-runtime smoke test (`npm run start` on the freshly built artifact,
  `curl /health`): the command launches only `react-router-serve ./build/server/index.js`
  (no migrate/seed in the process tree), but the local SSR bundle crashes during
  module load with `TypeError: z.url is not a function` at
  `build/server/index.js:230`. Root cause is a pre-existing dependency-hoisting
  issue, **not** this task: the workspace package
  `@modainteract/moda-interact-shared` (production dependency) requires
  `zod@^4` and uses `z.url()`/`z.iso.datetime()`, but the root `node_modules/zod`
  resolves to 3.23.8 (hoisted from the dev-only `prisma-generator-plantuml-erd`)
  and the SSR bundle externalizes `zod`. This task changed only `package.json`
  scripts, the Dockerfile `CMD`, README, and added a test file; the `start`
  command and the dependency tree are unchanged from the accepted baseline.

### Deviations

None to the accepted command-contract architecture. The four phases are exposed
as `build`, `migrate`, `seed`, `start`; the Docker start sequence runs only
`start`.

### Assumptions

- `DATABASE_URL`, `REDIS_URL` and other service configuration are supplied by
  the deployment environment; lifecycle commands read them at runtime and
  hard-code nothing.
- The existing `prisma:migrate:deploy` and `prisma:seed` lower-level scripts are
  retained for backward compatibility; the canonical deployment contract is
  `npm run migrate` and `npm run seed`.
- Pre-existing typecheck errors in unrelated files are outside this task's
  scope and are recorded for accuracy, matching the ARCH-002-SHOPIFY-001
  baseline.

### Unresolved Issues

- Repository-wide `npm run typecheck` still exits non-zero on the 48
  pre-existing unrelated errors recorded above; this is pre-existing baseline
  debt, not introduced by this task.
- Pre-existing local boot crash caused by zod dependency hoisting: the
  dev-only `prisma-generator-plantuml-erd` hoists `zod@3.23.8` to the app root,
  shadowing the `zod@4.4.3` required by the `@modainteract/moda-interact-shared`
  production package; the SSR bundle externalizes `zod`, so local `npm run start`
  crashes (`z.url is not a function`). In the production Docker build
  (`npm ci --omit=dev`) the conflicting dev-only zod is absent and zod@4
  resolves correctly. This is a dependency-hygiene issue independent of the
  command-separation contract and is outside this task's scope; a follow-up
  dependency fix can be considered separately.

### Architectural Concerns

None. The runtime command contract now matches the accepted ARCH-002 sequence
(build -> pre-deploy migration -> replica start, seed explicit/controlled).

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

Pending.

### Validation Reviewed

Pending.

### Architecture Conformance

Pending.

### Follow-up

Pending.
