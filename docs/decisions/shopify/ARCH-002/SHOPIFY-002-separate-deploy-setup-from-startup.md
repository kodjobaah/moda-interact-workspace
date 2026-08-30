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
  scripts so no deployment/start path chains migration or seed. During the
  architect-review correction round, `zod: ^4.0.0` was also declared as a
  direct runtime dependency so the application root resolves the same zod@4
  major the `@modainteract/moda-interact-shared` production package requires.
- `moda-interact/package-lock.json` — lockfile updated for the direct `zod
  ^4.0.0` declaration (root `node_modules/zod` resolves to 4.5.4).
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
- Resolved the previously recorded zod hoisting boot failure by declaring `zod
  ^4.0.0` as a direct runtime dependency (matching the shared package's zod@4
  runtime contract). Root zod now resolves to 4.5.4, the ERD-generator's zod
  3.23.8 is isolated, and the SSR bundle boots cleanly.

### Validation Results

Executed 2026-08-30 in `moda-interact` (Node v24.19.0, npm 11.17.0). The
validation below includes the architect-review correction rerun against the
current source state (direct `zod ^4.0.0`, root zod 4.5.4).

- Workspace doctor (`scripts/workspace-doctor.sh --quick`): **PASS — 6 checks,
  0 failures**. Confirms `moda-interact` declares direct Zod `^4.0.0` with
  installed root zod 4.5.4 and the ERD-generator zod 3.23.8 is isolated.
- Clean reproducible install (`npm ci`): **success**; root `node_modules/zod`
  resolves to 4.5.4 and the shared package's zod 4.4.3 remains isolated.
- Full test suite (`npm run test`): **10 test files passed, 66 tests passed**
  (Duration 2.36s). Includes the new
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
- Live web-runtime smoke test (architect-review correction round, against the
  freshly built artifact): **the application starts successfully**. Pre-deploy
  migration was run once as the separate lifecycle step (`npm run migrate`
  against the local `moda-postgres` Docker container, exit 0), then `npm run
  start` launched only `react-router-serve ./build/server/index.js` (confirmed
  via process tree; no migrate/seed in the log). `GET /health` returned
  **HTTP 200** `{"status":"ok"}`; `GET /ready` returned **HTTP 503**
  `{"status":"not_ready","checks":{"redis":false,"postgres":true}}`
  (correct — Redis is not running in this environment; PostgreSQL connectivity
  is confirmed true). The start log shows no migration or seed invocation.

### Deviations

None to the accepted command-contract architecture. The four phases are exposed
as `build`, `migrate`, `seed`, `start`; the Docker start sequence runs only
`start`.

One correction was applied from architect review round 1: `zod ^4.0.0` is now
declared as a direct runtime dependency so the root zod resolution satisfies
the shared package's zod@4 contract and the previously recorded local boot
crash is resolved. No lifecycle-command design change was made.

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

(The previously recorded zod hoisting boot crash is **resolved**: the direct
`zod ^4.0.0` runtime dependency makes the root resolve to zod 4.5.4, and the
live start smoke test now succeeds.)

### Architectural Concerns

None. The runtime command contract now matches the accepted ARCH-002 sequence
(build -> pre-deploy migration -> replica start, seed explicit/controlled).

## Architect Review

### Review Status

Changes Requested

### Review Notes

The implementation was reviewed from the returned source archive rather than
from the Completion Report alone.

The deployment-command separation is structurally correct:

- `package.json` exposes distinct `build`, `migrate`, `seed` and `start`
  commands;
- `start` launches only `react-router-serve ./build/server/index.js`;
- migration is independently callable through `npm run migrate`;
- seed is independently callable through `npm run seed`;
- the Docker `CMD` invokes only `npm run start`;
- no lifecycle command hard-codes a test or production database URL;
- the deterministic startup-contract test checks the intended command
  boundaries;
- repository search found no remaining runtime/documentation references to the
  removed `docker-start` or `setup` scripts outside the contract test itself.

The task cannot yet be architect-accepted because the submitted validation
evidence contradicts a checked Acceptance Criterion.

The task marks:

```text
existing application starts successfully
```

as satisfied, but the Completion Report records that the live `npm run start`
smoke test crashed during SSR module load with:

```text
TypeError: z.url is not a function
```

That failed smoke test is not evidence that startup succeeds.

The returned source has subsequently changed relative to that recorded
diagnosis: `moda-interact/package.json` now directly declares
`zod: ^4.0.0`, and the returned lockfile resolves the application root Zod to
4.5.4. The Completion Report therefore also contains stale statements saying
that the root still resolves to Zod 3.23.8 and that the dependency tree is
unchanged.

This is a narrow validation/documentation correction. Do not redesign the
lifecycle commands.

### Required Correction

Using the current returned source state:

1. bootstrap the workspace environment and run the quick workspace doctor;
2. perform a clean/reproducible application install suitable for the current
   development validation;
3. run `npm run build`;
4. run `npm run start` against that freshly built artifact;
5. probe `GET /health` and record successful startup/response evidence;
6. confirm the started web process does not invoke migration or seed;
7. rerun `tests/unit/deploy/startup-contract.test.ts` and the relevant/full
   test suite required by the task;
8. update the Completion Report so its Zod/runtime description matches the
   actual current package manifest and lockfile;
9. only keep the `existing application starts successfully` Acceptance
   Criterion checked if the rerun actually succeeds.

If the current application still fails to start, record the current failure
accurately and return the task for architectural review rather than marking the
criterion satisfied.

Do not create a separate correction task. Continue with
`ARCH-002-SHOPIFY-002`.

### Reviewed Files

- `moda-interact/package.json`
- `moda-interact/package-lock.json`
- `moda-interact/Dockerfile`
- `moda-interact/tests/unit/deploy/startup-contract.test.ts`
- `moda-interact/README.md`
- `docs/decisions/shopify/ARCH-002/SHOPIFY-002-separate-deploy-setup-from-startup.md`
- `docs/decisions/shopify/ARCH-002/_index.md`

### Validation Reviewed

Architect inspection confirmed:

```text
package scripts:
  build    present
  migrate  present
  seed     present
  start    present
  setup    absent
  docker-start absent

Docker CMD:
  npm run start

current package manifest:
  direct runtime zod = ^4.0.0

current lockfile:
  root node_modules/zod = 4.5.4
```

The prior live-start validation in the Completion Report failed and must be
rerun against this current dependency state before acceptance.

### Architecture Conformance

Command design: Conforms.

Validation evidence: Incomplete/inconsistent with the checked Acceptance
Criteria.

### Follow-up

Return the same task to `moda_app` with `status: in_progress`.

After the corrected validation and Completion Report are returned with
`status: review`, `moda_architect` should review the actual source and evidence
again.
