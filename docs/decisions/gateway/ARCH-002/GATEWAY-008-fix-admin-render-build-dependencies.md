---
id: ARCH-002-GATEWAY-008
architecture_id: ARCH-002
title: Fix Admin Render build dependency installation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
status: complete
priority: 5
executor: copilot
claimed_at: 2026-09-03T11:20:04Z
attempt: 1
depends_on:
  - ARCH-002-GATEWAY-003
  - ARCH-002-ADMIN-004
  - ARCH-002-ADMIN-009
enables:
  - ARCH-002-SYSTEM-TEST-006
created: 2026-09-03
updated: 2026-09-03
---

# Fix Admin Render Build Dependency Installation

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Current Execution State

This task is **Complete** after architect acceptance.

Both canonical Admin Render services now use:

```yaml
buildCommand: npm ci --include=dev && npm run build
startCommand: npm run start
```

while retaining:

```yaml
- key: NODE_ENV
  value: production
```

This allows the Next/PostCSS/Tailwind build toolchain to remain available
during Render builds without changing Admin runtime semantics or
reclassifying application dependencies.

A fresh deployment of `moda-interact-admin-test` is still required before
`SYSTEM-TEST-006` can execute its live deployed-topology assertions.

## Objective

Make both Render Admin services install the complete locked build dependency
set during the build while preserving production runtime semantics.

Target services:

```text
moda-interact-admin-test
moda-interact-admin-production
```

## Required Solution

Change the Admin `buildCommand` in **both** canonical Blueprints from:

```yaml
buildCommand: npm ci && npm run build
```

to:

```yaml
buildCommand: npm ci --include=dev && npm run build
```

or an equivalent explicit npm command that guarantees development/build
dependencies are installed even when `NODE_ENV=production`.

Keep:

```yaml
startCommand: npm run start
```

and keep:

```yaml
- key: NODE_ENV
  value: production
```

for runtime.

Do not solve this by:

- moving Tailwind/PostCSS/TypeScript build tooling into Admin runtime
  `dependencies` merely to satisfy Render;
- removing `NODE_ENV=production`;
- changing Admin source code;
- bypassing `npm ci` lockfile installation;
- hard-coding environment-specific package behavior.

The Admin build itself already runs:

```text
npm run prisma:generate
next build --webpack
```

so the build environment must retain the tooling required by that command.

## Scope

Owned repository:

```text
moda-interact-gateway
```

Expected implementation files:

```text
moda-interact-gateway/render.test.yaml
moda-interact-gateway/render.production.yaml
```

Focused gateway validation may be updated where necessary.

Do not modify:

```text
moda-interact-admin
```

unless architect review later proves the repository dependency declaration is
itself incorrect.

## Work Items

- [x] change the Admin test Blueprint build command to explicit dev-inclusive
      locked installation;
- [x] change the Admin production Blueprint build command identically;
- [x] preserve Admin runtime `NODE_ENV=production`;
- [x] preserve `startCommand: npm run start`;
- [x] add/extend deterministic Blueprint validation for the Admin build command;
- [x] run gateway validation;
- [ ] run the accepted ARCH-002 static production-readiness validator against
      the changed Blueprints;
- [x] update Completion Report and return to `review`.

## Interfaces / Contracts

Consumes the accepted Admin repository build contract:

```text
package.json:
  build = npm run prisma:generate && next build --webpack

postcss.config.mjs:
  @tailwindcss/postcss
```

Consumes canonical infrastructure ownership:

```text
moda-interact-gateway/render.test.yaml
moda-interact-gateway/render.production.yaml
```

Enables:

```text
ARCH-002-SYSTEM-TEST-006
```

after the Admin test service is successfully redeployed.

## Dependencies

- `ARCH-002-GATEWAY-003` — Complete.
- `ARCH-002-ADMIN-004` — Complete.
- `ARCH-002-ADMIN-009` — Complete.

## Acceptance Criteria

- [x] `moda-interact-admin-test` explicitly installs dev/build dependencies
      during the Render build;
- [x] `moda-interact-admin-production` uses the same build contract;
- [x] both use locked `npm ci` installation;
- [x] runtime `NODE_ENV=production` remains configured;
- [x] runtime start remains `npm run start`;
- [x] no Admin package/source changes are required;
- [x] no secret value is committed;
- [ ] static Blueprint/readiness validation still passes.

## Validation

Inspect the existing gateway validation scripts before running commands.

At minimum run:

```text
bash tests/run-tests.sh
bash tests/validate-observability-config.sh
git diff --check
```

Also run the accepted static production-readiness validation from the workspace:

```text
cd ../moda-interact-system-test
npm run validate:arch002-production-readiness
```

if its dependencies are already installed/available.

If that command cannot run because the local system-test environment is not
prepared, record the exact limitation rather than changing another repository.

Finally inspect both Blueprints and prove the two Admin declarations contain:

```yaml
buildCommand: npm ci --include=dev && npm run build
startCommand: npm run start
...
- key: NODE_ENV
  value: production
```

## Live Deployment Follow-up

A successful static task does not itself prove Render deployment.

After architect acceptance, the developer should redeploy:

```text
moda-interact-admin-test
```

The previous:

```text
Cannot find module '@tailwindcss/postcss'
```

failure must no longer occur.

Any subsequent deployment failure should be treated as new evidence and
returned to `moda_architect`; do not broaden this task pre-emptively.

## Non-Goals

- changing Admin application code;
- changing Tailwind/PostCSS configuration;
- reclassifying Admin npm dependencies;
- changing Render plans;
- changing Admin authentication;
- changing gateway NGINX routing;
- production deployment execution;
- load testing.

## Completion Report

### Status

Ready for Review

### Files Changed

`moda-interact-gateway/render.test.yaml`; `moda-interact-gateway/render.production.yaml`; `moda-interact-gateway/tests/validate-render-blueprints.sh`.

### Work Completed

Updated both Admin Render services to install the locked development/build
dependencies with `npm ci --include=dev` while preserving production runtime
semantics. Added deterministic YAML contract validation for both Blueprints.

### Validation Results

`bash tests/run-tests.sh` — passed, 49 gateway checks.

`bash tests/validate-observability-config.sh` — passed.

`bash tests/validate-render-blueprints.sh` — passed for test and production
Admin declarations.

`git diff --check` — passed.

`cd ../moda-interact-system-test && npm run validate:arch002-production-readiness`
— failed because the local system-test environment is missing the `yaml` module
(`MODULE_NOT_FOUND`).

### Deviations

The required workspace production-readiness validator could not execute because
its existing local dependency installation is incomplete. No dependency was
added or changed in another repository.

### Assumptions

The observed Render build uses the Blueprint-provided `NODE_ENV=production`
during dependency installation, consistent with the missing build-only
PostCSS dependency.

### Unresolved Issues

The workspace production-readiness validator remains unverified locally until
the system-test repository's declared `yaml` dependency is installed.

### Architectural Concerns

The fix remains identical between test and production so successful test
deployment exercises the same Admin build contract intended for production.

Repository agent did not commit or push. Implementation is ready for developer
commit/push after architect acceptance.

## Architect Review

### Review Status

Accepted

### Review Notes

Architect review confirmed that:

- `moda-interact-admin-test` and `moda-interact-admin-production` both use
  `npm ci --include=dev && npm run build`;
- both retain locked `npm ci` installation;
- both retain `startCommand: npm run start`;
- both retain runtime `NODE_ENV=production`;
- no Admin source code or package dependency classification was changed;
- no secret values were committed;
- the focused Blueprint validator mechanically checks the Admin build command,
  start command and production `NODE_ENV` contract for both environments;
- `bash tests/validate-observability-config.sh` passes;
- `bash tests/validate-render-blueprints.sh` passes;
- the repository agent reported the full gateway suite passing 49 checks and
  `git diff --check` passing;
- the workspace production-readiness validator could not execute because the
  local system-test dependency installation lacked its declared `yaml` module.
  The task explicitly permits this validation limitation to be recorded when
  that repository is not locally prepared, and the agent correctly did not
  modify another repository to work around it;
- no commit or push was performed.

`ARCH-002-GATEWAY-008` is Complete.

The next operational step is to redeploy `moda-interact-admin-test`. The
previous `Cannot find module '@tailwindcss/postcss'` failure must no longer
occur. Any new deployment failure is new evidence and should be returned to
`moda_architect`.

`ARCH-002-SYSTEM-TEST-006` remains Blocked until the corrected Render test
services are healthy and the five required live test inputs are supplied.
