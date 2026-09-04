---
id: ARCH-002-SYSTEM-TEST-007
architecture_id: ARCH-002
title: Validate production Blueprint and readiness configuration
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
status: complete
priority: 47
executor: copilot
claimed_at: 2026-09-03T10:29:05Z
attempt: 3
depends_on:
  - ARCH-002-GATEWAY-004
enables:
  - ARCH-002-SYSTEM-TEST-008
  - ARCH-002-SYSTEM-TEST-001
created: 2026-09-03
updated: 2026-09-03
---

# Validate Production Blueprint and Readiness Configuration

## Current Execution State

This task is **Complete** after architect acceptance of attempt 3.

The accepted static production-readiness validator mechanically checks the
actual current Render test/production Blueprints, NGINX template and gateway
deployment documentation. It covers:

- test/production PostgreSQL and observability isolation;
- exact PostgreSQL consumer wiring;
- required external Redis, OTLP, Loki and provider-secret declarations;
- public/private service topology and worker entrypoints/source repository;
- production Admin host routing and ordinary-host `/admin` rejection;
- environment-specific observability-group attachment with cross-environment
  contamination rejection;
- the 22,000 Shopify webhooks/minute target remaining explicitly
  estimated/unmeasured rather than proven;
- migration-before-start sequencing;
- durable-state-safe rollback/recreation evidence.

This is static readiness evidence only. It does not prove live Render
connectivity, DNS/TLS, deployed secret values, migration execution or measured
production capacity.

## Objective

Mechanically validate that the accepted ARCH-002 Render test and production
configuration preserves the agreed service topology, environment isolation,
secret boundaries, production Admin routing, worker separation and
assumption-vs-measurement language before any production-sized capacity run.

Primary inputs:

```text
moda-interact-gateway/render.test.yaml
moda-interact-gateway/render.production.yaml
moda-interact-gateway/nginx/nginx.conf.template
moda-interact-gateway/docs/render-topology.md
moda-interact-gateway/docs/deployment-prerequisites.md
```

Use the actual current files. Do not rely on copied YAML inside the task.

## Required Static Assertions

### A. Environment/resource isolation

Prove mechanically that:

- test and production use distinct PostgreSQL resource names;
- test and production use distinct observability environment identities;
- production declarations do not reference the test PostgreSQL resource;
- test declarations do not reference the production PostgreSQL resource;
- Redis/provider/OTLP credentials remain externally supplied secret values
  rather than committed credential text;
- test and production secret values are not forced to be identical by source
  configuration.

### B. Public/private topology

Validate the production Blueprint declares:

```text
public web:
  moda-interact-gateway-production

private services:
  moda-interact-production
  moda-interact-messaging-production
  moda-interact-admin-production

workers:
  moda-shopify-event-worker-production
  moda-recovery-worker-production
  moda-messaging-worker-production
```

Validate the equivalent boundary shape in the test Blueprint without requiring
identical plan sizes.

### C. Admin routing

Validate production configuration declares:

```text
admin.modainteract.com
```

on the gateway and configures:

```text
ADMIN_PUBLIC_HOST=admin.modainteract.com
```

Validate the gateway NGINX configuration uses host routing to the private Admin
upstream and that the ordinary/default host does not restore `/admin/*` as the
production Admin route.

### D. Worker separation

Validate three independently deployable worker declarations remain present and
use the accepted owning-repository entrypoints for:

```text
Shopify event processing
recovery processing
messaging / CommerceAgent processing
```

Do not introduce or require a fourth worker split in this task.

### E. PostgreSQL/Redis wiring

Validate application/worker components that require PostgreSQL are wired from
the environment-appropriate Render database declaration.

Validate Redis remains an externally supplied infrastructure dependency where
required rather than being silently replaced by a local container in Render.

### F. Observability identity and secrets

Validate test and production have explicit distinguishable deployment
environment identity and that OTLP/Loki credentials remain externally supplied.

Do not require duplicate custom telemetry that accepted framework/shared
instrumentation already provides.

### G. Capacity language

Validate the production Blueprint/documentation continues to represent initial
production plans/counts as **ASSUMED/ESTIMATED/unmeasured** where measured
capacity evidence does not exist.

The static production Blueprint must not itself be treated as proof of:

```text
22,000 Shopify webhooks/minute
```

### H. Deployment/rollback evidence

Validate architecture-approved deployment/pre-deploy/migration and rollback or
recreation guidance exists and does not imply destruction of durable production
state merely because the platform is in development.

If current documentation is missing a required statement, report the concrete
gap to `moda_architect`; do not edit gateway-owned documentation in this task.

## Implementation Guidance for Luna

Prefer a small validator owned by `moda-interact-system-test`, for example:

```text
moda-interact-system-test/src/render-blueprint-validation.js
moda-interact-system-test/scripts/run-arch002-production-readiness.js
moda-interact-system-test/test/render-blueprint-validation.test.js
```

and a package script such as:

```text
validate:arch002-production-readiness
```

The validator may inspect YAML/text from the gateway repository but must not
modify gateway files.

Use the smallest dependency footprint practical. If no YAML parser is already
available and a parser is genuinely required, a system-test-only dependency is
permitted, with package-lock update. Do not implement a fragile pseudo-YAML
parser merely to avoid a reasonable test dependency.

## Scope

- static validation of current test/production Render Blueprints;
- static validation of gateway host-routing configuration where needed;
- test/production isolation checks;
- worker/dependency/observability declarations;
- capacity-assumption labelling;
- deployment/rollback evidence presence.

## Out of Scope

- deploying Render services;
- live Render probes (SYSTEM-TEST-006);
- local observability integration (SYSTEM-TEST-002);
- production load generation (SYSTEM-TEST-008);
- editing gateway/application repositories;
- choosing new production plan sizes;
- claiming measured capacity.

## Work Items

- [x] Inspect current gateway Blueprint/configuration files.
- [x] Implement deterministic static validation in system-test repository.
- [x] Validate test/production PostgreSQL isolation.
- [x] Validate test/production observability identity isolation.
- [x] Validate public gateway/private service boundaries.
- [x] Validate production Admin host routing and absence of `/admin/*` production route.
- [x] Validate three worker declarations/entrypoints.
- [x] Validate external Redis and secret placeholders.
- [x] Validate assumed/unmeasured capacity language.
- [x] Validate deployment/rollback evidence presence.
- [x] Add focused unit tests for positive and negative fixtures/conditions.
- [x] Run repository test/typecheck/lint and static readiness command.
- [x] Record concrete gaps without modifying gateway-owned files.
- [x] Return to `review` and stop.

## Acceptance Criteria

- [x] validator uses actual workspace gateway files rather than copied production configuration;
- [x] test/production durable resources are demonstrably distinct;
- [x] production public/private topology matches ARCH-002;
- [x] Admin host routing contract matches ARCH-002;
- [x] three accepted worker boundaries remain independently declared;
- [x] Redis/provider/OTLP secret values are not committed by the Blueprint;
- [x] production capacity remains labelled unmeasured until SYSTEM-TEST-008 evidence exists;
- [x] deployment/rollback evidence is identified;
- [x] no gateway/application implementation is modified;
- [x] repository validation passes;
- [x] task returns to `review` and stops.

## Validation

Inspect package.json and run the declared repository validation commands plus the
new static readiness command.

The validator must fail on deliberately broken test fixtures/conditions covered
by focused unit tests; it must not be a grep-only script that always succeeds.

## Architect Correction Request — attempt 2

`moda_architect` reviewed the actual attempt-1 validator and accepted its
overall structure. Preserve the YAML parser, runner, existing service/topology
checks and package script.

Harden the validator so it mechanically proves the requirements already stated
by this task rather than merely passing the current happy-path snapshot.

### 1. Prove environment-specific observability group attachment

Attempt 1 verifies that both observability groups exist and have different
`DEPLOYMENT_ENVIRONMENT_NAME` values, but it does not prove the deployable
services actually use the correct group.

For every instrumented private service and worker in each environment, prove:

```text
test       -> fromGroup: moda-observability-test
production -> fromGroup: moda-observability-production
```

and reject cross-environment group attachment.

At minimum this applies to:

```text
moda-interact
moda-interact-messaging
moda-interact-admin
shopify-event worker
recovery worker
messaging worker
```

Do not require OpenTelemetry on the NGINX gateway unless the accepted Blueprint
already declares it.

### 2. Prove PostgreSQL consumer wiring, not only resource existence

Attempt 1 proves that the environment database resource exists and checks for
literal cross-environment resource names, but it does not prove required
consumers have `DATABASE_URL` or that it points to the correct database.

For these services in both test and production:

```text
moda-interact
moda-interact-admin
shopify-event worker
recovery worker
messaging worker
```

require:

```yaml
- key: DATABASE_URL
  fromDatabase:
    name: moda-interact-postgres-<environment>
    property: connectionString
```

A missing `DATABASE_URL`, an arbitrary other database name, or the wrong
property must fail validation.

Do not require PostgreSQL for `moda-interact-messaging` unless its accepted
Blueprint currently declares that dependency.

### 3. Prove required external Redis and observability wiring is present

The attempt-1 secret validator checks safety only when a matching variable is
present. Removing `REDIS_URL`, OTLP, or Loki declarations can therefore pass.

For deployables that require Redis, require `REDIS_URL` to exist and remain
external (`sync: false`, no committed `value`):

```text
moda-interact
moda-interact-messaging
shopify-event worker
recovery worker
messaging worker
```

For the instrumented private services/workers listed in section 1, require the
accepted external observability declarations to remain present:

```text
OTEL_EXPORTER_OTLP_ENDPOINT
OTEL_EXPORTER_OTLP_HEADERS
LOKI_URL
LOKI_USERNAME
LOKI_PASSWORD
```

They must remain externally supplied and must not contain committed values.

Also validate secret-like variables inside `envVarGroups`, not only
service-local `envVars`, so a future committed credential cannot bypass the
secret check by moving into a group.

### 4. Preserve expected provider-secret boundaries

Where the current accepted Blueprint declares provider credentials needed by a
service, prove that those declarations remain present and external rather than
only checking them if they happen to exist.

Use the actual Blueprint as the contract. Relevant examples include the
Shopify app, Meta messaging ingress, recovery/messaging workers and the
CommerceAgent/Groq credential.

Do not invent new provider requirements.

### 5. Strengthen worker source ownership

The task already validates worker entrypoint commands. Also prove the three
worker declarations continue to source the accepted
`moda-interact-background` repository in both test and production.

Do not hardcode developer-specific filesystem paths. Validate the Blueprint
repository declaration.

### 6. Bind capacity labelling to the 22,000/minute target

The current validator succeeds when *any* `ASSUMED`, `ESTIMATED`, `UNKNOWN` or
`unmeasured` word exists anywhere in the supplied documents.

Instead prove that the documentation around the actual:

```text
22,000 Shopify webhooks/minute
```

target explicitly identifies it as estimated/unmeasured/unknown capacity.

A document that calls the 22,000/minute target **PROVEN** while containing the
word `ASSUMED` in an unrelated section must fail.

Do not invent a latency SLO or claim measured capacity.

### 7. Strengthen migration and durable-state rollback evidence

The task requires deployment/pre-deploy/migration and rollback/recreation
evidence.

Mechanically prove at minimum:

- the Shopify app uses the accepted `preDeployCommand: npm run migrate` in test
  and production;
- documentation establishes migration-before-application-start sequencing;
- rollback/recreation guidance explicitly protects durable state (for example,
  `never destroy durable state` / equivalent safety language).

A document that merely contains the words `Rollback` and `durable state` while
instructing the operator to destroy durable state must fail.

Do not modify gateway-owned documentation if a real gap is discovered; report
the gap to `moda_architect`.

### Required regression coverage

Keep the existing tests and add focused negative cases demonstrating at least:

1. wrong/missing production `DATABASE_URL` wiring fails;
2. production service attached to the test observability group fails;
3. missing or committed required Redis/OTLP/Loki declaration fails;
4. wrong worker repository fails;
5. the 22,000/minute target relabelled as proven fails even when unrelated
   assumption language remains;
6. unsafe durable-state rollback wording or missing migration sequencing fails.

Fixtures may be created by cloning/mutating the parsed current Blueprint/text in
memory. Do not copy production YAML into the test repository.

### Validation

Run the actual scripts declared in `moda-interact-system-test/package.json`,
including:

```text
node --test test/render-blueprint-validation.test.js
npm test
npm run typecheck
npm run lint
npm run validate:arch002-production-readiness
git diff --check
```

The static readiness command must still pass against the actual current gateway
files.

### Scope boundary

Do not:

- modify `moda-interact-gateway`;
- modify application repositories;
- deploy Render;
- run production load;
- choose new plan sizes;
- create duplicate telemetry;
- broaden SYSTEM-TEST-007 into live validation.

After validation, update the Completion Report, set `status: review`, and STOP.

## Architect Correction Request — attempt 3

Preserve every attempt-2 change.

### Reject additional cross-environment observability group attachment

The current implementation effectively checks:

```js
service.envVars.some((variable) => variable.fromGroup === expectedGroup)
```

This proves the expected group is present, but a production service can still
contain both:

```yaml
- fromGroup: moda-observability-production
- fromGroup: moda-observability-test
```

and pass validation.

That violates the attempt-2 requirement to:

```text
test       -> moda-observability-test
production -> moda-observability-production
```

**and reject cross-environment group attachment.**

For each instrumented private service and worker already covered by the
validator:

1. require the expected environment observability group;
2. reject any `fromGroup` reference to the opposite environment observability
   group;
3. preferably reject any additional `moda-observability-*` group that does not
   equal the expected group;
4. do not reject unrelated non-observability env-var groups if the Blueprint
   later gains one.

Add focused regression coverage that starts from the valid current production
fixture, **adds** `moda-observability-test` while leaving
`moda-observability-production` present, and proves validation fails.

Also cover the equivalent test-to-production contamination if practical.

### Validation

Run:

```text
node --test test/render-blueprint-validation.test.js
npm test
npm run typecheck
npm run lint
npm run validate:arch002-production-readiness
git diff --check
```

The current real gateway configuration must still pass.

### Scope boundary

Do not:

- modify gateway/application repositories;
- redesign the validator;
- change the accepted attempt-2 PostgreSQL/Redis/provider/capacity/rollback
  checks;
- deploy Render;
- run load tests;
- commit or push.

After the correction, update the Completion Report, set `status: review`, and
STOP.

## Completion Report

### Status

Ready for Review

### Files Changed

- `moda-interact-system-test/src/render-blueprint-validation.js` — parser-backed
  validation of test/production topology, isolation, secrets, routing, workers,
  capacity language and rollback evidence.
- `moda-interact-system-test/scripts/run-arch002-production-readiness.js` —
  runner reading current gateway files.
- `moda-interact-system-test/test/render-blueprint-validation.test.js` —
  positive and negative fixture coverage for attempt-1, attempt-2 and attempt-3
  cases.
- `moda-interact-system-test/package.json` — static readiness script.
- This task record.

### Work Completed

Hardened the parser-backed validator to require environment-specific
observability group attachment, exact PostgreSQL consumer wiring, external Redis
and OTLP/Loki declarations, accepted provider-secret declarations, and the
`moda-interact-background` worker repository. Capacity labeling is now bound to
the 22,000 Shopify webhooks/minute target. The validator also requires the
accepted Shopify pre-deploy migration command, migration-before-start evidence,
and durable-state-safe rollback/recreation guidance. Secret-like variables in
environment groups are checked as well as service-local variables.

Attempt 3 additionally rejects any extra `moda-observability-*` group attached
to an instrumented service when it differs from the expected environment group,
while allowing unrelated env-var groups.

### Blueprint / Configuration Evidence

The validator reads the actual test and production Blueprints, NGINX template,
render-topology documentation and deployment-prerequisites documentation. It
checks environment/resource isolation, public/private/worker boundaries,
production Admin host routing and ordinary-host `/admin` 404 guards, external
secret placeholders and Redis wiring, unmeasured capacity language, and
rollback/recreation evidence.

### Validation Results

- `node --test test/render-blueprint-validation.test.js`: 12 passed.
- `npm test`: 30 passed, 2 existing opt-in Docker tests skipped.
- `npm run typecheck`: passed.
- `npm run lint`: passed.
- `npm run validate:arch002-production-readiness`: passed with no errors.
- Task-owned `git diff --check`: passed.

### Gaps Identified

None within the static scope. Render plan availability, DNS/TLS, deployed
secret values, connectivity, migration execution and measured capacity remain
deployment-time or later system-test concerns.

### Deviations

None. No gateway or application repository was modified, and no production
credentials were used.

### Assumptions

The current accepted Blueprint's provider-secret declarations define the
required provider contract; all such values remain Render-supplied
`sync: false` entries. Existing opt-in Docker tests remain skipped unless their
environment flags are explicitly enabled.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 3 is accepted.

Architect review confirmed that:

- the attempt-2 production-readiness hardening remains intact;
- required test and production observability groups are present on all covered
  instrumented private services/workers;
- an additional wrong `moda-observability-*` group is now rejected even when
  the correct environment group is also present;
- regression coverage proves both production-with-test-group and
  test-with-production-group contamination fail;
- unrelated non-observability env-var groups are not prohibited by this
  correction;
- PostgreSQL consumer wiring, required external Redis/OTLP/Loki declarations,
  provider-secret declarations, worker repository ownership, capacity
  labelling, migration sequencing and durable-state rollback checks remain in
  place;
- the static readiness runner reads the actual current gateway-owned files;
- the repository agent reported 12 focused tests, 30 full-suite passes with 2
  existing opt-in skips, plus passing typecheck, lint, readiness command and
  diff checks;
- no gateway/application repository was modified and no commit/push occurred.

`ARCH-002-SYSTEM-TEST-007` is Complete.

`ARCH-002-SYSTEM-TEST-008` remains Pending because
`ARCH-002-SYSTEM-TEST-006` is still Blocked on external deployed-Render test
inputs.
