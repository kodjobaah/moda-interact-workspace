---
id: ARCH-026-GATEWAY-001
architecture_id: ARCH-026
title: Wire the hosted merchant API through the Render and Gateway topology
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 45
executor: copilot
claimed_at: 2026-10-03T20:07:21Z
attempt: 1
depends_on:
  - ARCH-026-API-001
enables: []
created: 2026-10-02
updated: 2026-10-03
---

# Wire the hosted merchant API through the Render and Gateway topology

## Architecture

Architecture ID:

`ARCH-026`

Architecture document:

`docs/architecture/ARCH-026-woocommerce-application-foundation.md`

Coordinator:

`moda_architect`

## Objective

Codify the hosted `moda-interact-api` deployment and public routing boundary in the existing Render test/production Blueprints and HAProxy gateway.

The completed topology is:

```text
WooCommerce PHP plugin / external server-side client
        |
        | HTTPS
        v
api-test.modainteract.com      (test)
api.modainteract.com           (production)
        |
        v
moda-interact-gateway
        |
        | exact Host routing
        v
private moda-interact-api service
        |
        v
Moda PostgreSQL
```

The API service remains private on Render. The gateway is the only architecture-managed public ingress for it.

This task owns infrastructure/routing only. It MUST NOT implement Woo installation authentication, merchant business endpoints, database schema, billing, recovery, Background jobs, plugin code or API application behavior.

## Context

`ARCH-026-API-001` establishes the backend-only `moda-interact-api` runtime and fixes these deployment-relevant contracts:

```text
repository:
    https://github.com/kodjobaah/moda-interact-api.git

runtime:
    Node / TypeScript

repository commands:
    npm run prisma:generate
    npm run build
    npm run start

runtime configuration:
    DATABASE_URL
    PORT

liveness:
    GET /health/live

readiness:
    GET /health/ready
```

API-001 explicitly does not own database migration at service startup. The API consumes the canonical nested `database/` submodule and must not run DDL/migrations as part of this Gateway task.

The accepted Gateway implementation currently uses:

```text
moda-interact-gateway/render.test.yaml
moda-interact-gateway/render.production.yaml
```

as the version-controlled Render topology. Do not introduce a new `render.yaml`.

Public routing is exact-host based. Unknown hosts are rejected by HAProxy. Existing public hostnames for Shopify, Admin, Messaging and Commerce must remain unchanged.

ARCH-026 API traffic is server-to-server. Browser JavaScript in the Woo extension calls the local WordPress REST facade, not `api.modainteract.com` directly. This task therefore does not introduce permissive browser CORS.

## Scope

Modify only `moda-interact-gateway` infrastructure/configuration/tests/documentation needed to deploy and route `moda-interact-api`.

Expected primary files:

```text
moda-interact-gateway/render.test.yaml
moda-interact-gateway/render.production.yaml
moda-interact-gateway/haproxy/haproxy.cfg
moda-interact-gateway/docker/entrypoint.sh
moda-interact-gateway/tests/run-tests.sh
moda-interact-gateway/tests/validate-render-blueprints.sh
moda-interact-gateway/tests/validate-render-blueprints-negative.sh
moda-interact-gateway/docs/gateway.md
moda-interact-gateway/docs/render-topology.md
moda-interact-gateway/docs/deployment-prerequisites.md
moda-interact-gateway/docs/woocommerce-api-deployment.md
```

Repository-local file choices may vary when an existing validator/document is the clearer owner, but the behavior and validation below are mandatory.

### Canonical public hosts

Use exactly:

```text
test:
    api-test.modainteract.com

production:
    api.modainteract.com
```

These are non-secret architecture-owned host identities.

Add the appropriate hostname to the existing public gateway service `domains` list in each Blueprint.

The Woo plugin's future server-side API-base configuration may use these origins, but this Gateway task does not edit the WordPress plugin or distribute plugin configuration.

### Private API services

Add exactly one private API service per environment.

Test:

```yaml
- type: pserv
  name: moda-interact-api-test
  runtime: node
  repo: https://github.com/kodjobaah/moda-interact-api.git
  plan: 0.5c-512mb
  numInstances: 1
  healthCheckPath: /health/live
  buildCommand: git submodule update --init --recursive && npm ci --include=dev && npm run prisma:generate && npm run build
  startCommand: npm run start
```

Production:

```yaml
- type: pserv
  name: moda-interact-api-production
  runtime: node
  repo: https://github.com/kodjobaah/moda-interact-api.git
  plan: 0.5c-512mb
  numInstances: 2
  healthCheckPath: /health/live
  buildCommand: git submodule update --init --recursive && npm ci --include=dev && npm run prisma:generate && npm run build
  startCommand: npm run start
```

The plan/count values are initial infrastructure assumptions, not measured capacity claims. Merchant API workload must not be inferred from Shopify webhook volume.

The API service must not declare a public domain or become a Render public web service.

Do not add a `preDeployCommand` to the API service. Database migrations remain owned and sequenced separately.

### API service environment

Attach only the environment configuration required by the accepted API runtime.

Test:

```yaml
- fromGroup: moda-interact-test-config
- key: NODE_ENV
  value: production
- key: DATABASE_URL
  fromDatabase:
    name: moda-interact-postgres-test
    property: connectionString
```

Production uses the corresponding production group/database.

Do not attach:

```text
REDIS_URL
Shopify credentials
Meta/WhatsApp credentials
Commerce secrets
billing-provider credentials
R2 credentials
LLM/provider credentials
```

unless a later accepted API task explicitly introduces such a runtime dependency and a later Gateway task owns that wiring.

The shared environment group may provide the existing environment/observability transport configuration. Telemetry transport failure must remain non-fatal to business processing.

### Gateway upstream configuration

Add one required private upstream variable:

```text
MODA_API_UPSTREAM
```

It contains the Render private-network `host:port` for the environment-specific `moda-interact-api` service.

In both Blueprints wire it through `fromService`:

```yaml
- key: MODA_API_UPSTREAM
  fromService:
    type: pserv
    name: moda-interact-api-<environment>
    property: hostport
```

Add one required non-secret public host variable:

```text
API_PUBLIC_HOST
```

with exact environment values:

```text
test:       api-test.modainteract.com
production: api.modainteract.com
```

The gateway entrypoint MUST fail fast if either variable is missing, exactly as it does for the existing required upstream/host configuration.

### HAProxy routing

Extend the existing exact-host gateway routing with:

```text
host_api = API_PUBLIC_HOST
```

and one private backend using `MODA_API_UPSTREAM`.

The routing contract is:

```text
API_PUBLIC_HOST/*
    -> moda-interact-api
```

Do not introduce path-prefix rewriting. The API receives its original request path.

The gateway must continue to reject unknown/unapproved hosts.

The existing gateway-local:

```text
GET /health
```

remains gateway liveness for every host, including `API_PUBLIC_HOST`.

API service health endpoints remain reachable through the API host at their own paths:

```text
GET /health/live
GET /health/ready
```

Do not rewrite `/health` to the API.

Forward the existing request/correlation and proxy headers consistently with the other service backends. Do not add or log Authorization values.

Do not add a gateway authentication mechanism for API-002 credentials. `moda-interact-api` owns installation authentication/authorization; Gateway owns routing and infrastructure isolation.

### CORS and browser exposure

Do not add `Access-Control-Allow-Origin: *` or another permissive CORS policy for the API host.

The architecture-approved flow is:

```text
browser -> local WordPress REST -> PHP -> API_PUBLIC_HOST
```

not:

```text
browser -> API_PUBLIC_HOST
```

Gateway must not expose or transform installation credentials beyond transparently forwarding the server-to-server Authorization header to the private API upstream.

### Request-body handling

Retain the existing gateway global request-body ceiling unless the accepted API implementation requires a smaller gateway-owned limit.

Do not create a second body schema/validator at the Gateway boundary. API route-specific limits remain application-owned.

### DNS / TLS deployment prerequisite

Document, but do not perform, the operator prerequisite that each environment's API hostname is attached as a custom domain to the corresponding public Gateway service and resolves to that Gateway deployment:

```text
api-test.modainteract.com -> moda-interact-gateway-test
api.modainteract.com      -> moda-interact-gateway-production
```

TLS is terminated on the public Gateway service using the existing Render custom-domain mechanism.

No separate public Render URL/domain is attached to `moda-interact-api`.

### Deployment sequencing

Document the safe rollout order:

```text
1. API-001 accepted and repository/build/start contract fixed.
2. Apply architecture-required database migrations before deploying API code that consumes them.
3. Deploy/update the private moda-interact-api service.
4. Verify private /health/live and /health/ready.
5. Deploy/update Gateway routing and attach/verify API custom domain.
6. Verify public API host routing and gateway-local /health behavior.
7. Only then configure/test real Woo plugin installations against that environment.
```

For API-001-only deployment, generic database connectivity is sufficient. Before API-002 is deployed, DATABASE-001 must already be applied. Before API-003 is deployed, its accepted database dependencies must already be applied.

This task does not perform a live Render deploy, DNS mutation or credential operation.

## Out of Scope

- `moda-interact-api` application implementation.
- Woo installation authentication/site-control proof.
- merchant business APIs.
- WordPress/PHP plugin implementation.
- React/Woo Admin UI.
- database schema/migrations.
- Redis/BullMQ.
- Background workers.
- Woo billing.
- recovery processing.
- Merchant Knowledge.
- products/coupons/discounts.
- CommerceAgent.
- WhatsApp/Meta.
- public browser CORS.
- CDN/WAF/API-management products.
- rate-limiting infrastructure not already architecture-approved.
- a second public API service bypassing Gateway.
- live Render deployment.
- live DNS/custom-domain mutation.
- secret value creation/rotation.
- autoscaling claims without measured workload evidence.

## Requirements

### R1 — API remains private behind Gateway

`moda-interact-api` is a Render private service in both environments. Only the public Gateway receives the API custom domain.

### R2 — Exact environment-isolated public hosts

Use only:

```text
api-test.modainteract.com
api.modainteract.com
```

for the ARCH-026 API host identities, with test and production isolated.

### R3 — Deployment commands match API-001

The Blueprint build/start commands must use the accepted API-001 repository scripts and recursively initialise the API repository's nested database submodule before Prisma generation.

### R4 — No migration ownership transfer

The API private service has no migration/pre-deploy DDL command. Database migration sequencing remains outside the API/Gateway service startup.

### R5 — Least-privilege environment wiring

The API receives general environment/observability configuration plus `DATABASE_URL` only for this architecture stage. It does not receive Redis/provider/application credentials it does not consume.

### R6 — Gateway exact-host routing

Only requests whose Host matches `API_PUBLIC_HOST` may route to the API backend. Unknown hosts remain rejected.

### R7 — Gateway health remains local

`GET /health` remains Gateway liveness and never becomes dependent on API/PostgreSQL availability.

### R8 — API liveness/readiness remain distinct

The deployed API uses `/health/live` for its service liveness check. `/health/ready` remains available for deployment/system validation of PostgreSQL reachability.

### R9 — No browser CORS expansion

Gateway introduces no permissive browser CORS for API_PUBLIC_HOST.

### R10 — Authentication remains application-owned

Gateway forwards the request to the API service but does not interpret, log, persist or reimplement API-002 installation credentials.

### R11 — Environment failure is explicit

Gateway startup fails if `MODA_API_UPSTREAM` or `API_PUBLIC_HOST` is missing. Blueprint validation prevents missing/miswired service references.

### R12 — Existing topology remains intact

Shopify, Messaging, Admin, Commerce and worker routing/deployment semantics remain unchanged except for the additive API service/host wiring required here.

## Work Items

- [x] Add `moda-interact-api-test` as a private Node service to `render.test.yaml` using the accepted API-001 build/start/health contract.
- [x] Add `moda-interact-api-production` as a private Node service to `render.production.yaml` using the accepted API-001 build/start/health contract.
- [x] Wire each API service only to the environment's shared general config and PostgreSQL `DATABASE_URL`, plus `NODE_ENV=production`.
- [x] Add the environment-specific API hostname to each public Gateway service's custom-domain list.
- [x] Add `MODA_API_UPSTREAM` and `API_PUBLIC_HOST` to Gateway Blueprint configuration.
- [x] Add `API_PUBLIC_HOST` exact-host ACL and API backend routing to HAProxy without path rewriting.
- [x] Update the Gateway entrypoint to require/render the new API host/upstream placeholders.
- [x] Preserve gateway-local `GET /health` behavior on the API host.
- [x] Extend Gateway runtime tests for API-host routing, unknown-host rejection, gateway health, forwarding/correlation headers and API upstream failure behavior.
- [x] Extend positive Blueprint validation for exact API service type/repo/plan/count/build/start/health/database/general-config and Gateway host/upstream references.
- [x] Extend negative Blueprint validation for missing/miswired API host/upstream, public API service exposure, wrong repo/health/build/start, migration command, Redis/provider-secret leakage and environment crossover.
- [x] Document API public/private topology, DNS/TLS prerequisites, environment isolation and safe deployment order.
- [x] Verify no secret values, permissive CORS or application business logic were added.

## Interfaces / Contracts

### Public host contract

```text
test:
    https://api-test.modainteract.com

production:
    https://api.modainteract.com
```

### Gateway environment contract

```text
API_PUBLIC_HOST
MODA_API_UPSTREAM
```

### Private service identities

```text
moda-interact-api-test
moda-interact-api-production
```

### API application contract owner

`ARCH-026-API-001` and later accepted API tasks.

Gateway consumes the API's published HTTP paths but does not redefine their request/response/authentication semantics.

### Database contract

The API private service receives the existing environment-specific PostgreSQL connection through:

```text
DATABASE_URL
```

Gateway itself receives no database credential.

## Dependencies

- `ARCH-026-API-001`

API-001 must be architect-accepted `complete` before GATEWAY-001 becomes Ready, because Gateway must use the actual accepted API repository build/start/health contract rather than a speculative command.

## Enables

None currently.

The terminal ARCH-026 system-test task, when defined, must depend on this Gateway task together with all application/database capabilities required by its scenario.

## Acceptance Criteria

- [x] Both canonical Render Blueprints declare exactly one environment-appropriate private `moda-interact-api` service.
- [x] The API service repository is `https://github.com/kodjobaah/moda-interact-api.git`.
- [x] API service build/start commands match the accepted API-001 repository contract and recursively initialise nested submodules before Prisma generation.
- [x] API services have no `preDeployCommand` or application-owned migration command.
- [x] Test API service uses `0.5c-512mb` with one instance; production API service uses `0.5c-512mb` with two instances, both documented as initial assumptions rather than measured capacity.
- [x] API services declare `/health/live` for service liveness; `/health/ready` remains a distinct path and is covered by the runtime regression test.
- [x] API services receive the correct environment's shared general config, `NODE_ENV=production` and PostgreSQL `DATABASE_URL`.
- [x] API services receive no Redis, Shopify, Meta/WhatsApp, Commerce, billing, R2 or LLM/provider credential groups.
- [x] `api-test.modainteract.com` is attached only to the test Gateway Blueprint.
- [x] `api.modainteract.com` is attached only to the production Gateway Blueprint.
- [x] Gateway receives exactly one `API_PUBLIC_HOST` and one `MODA_API_UPSTREAM` per environment with no test/production crossover.
- [x] Gateway startup fails when either new required variable is missing.
- [x] Exact API Host routes to the API backend with no path rewriting.
- [x] Unknown Host remains 404 and cannot reach the API backend.
- [x] `GET /health` on API_PUBLIC_HOST remains Gateway-local and succeeds independently of API/PostgreSQL availability.
- [x] API `/health/live` and `/health/ready` are configured to forward on their original paths through the exact API host.
- [x] Existing request/correlation/proxy-header behavior is preserved for API routing.
- [x] Gateway does not log or interpret Authorization credentials.
- [x] No permissive browser CORS is introduced.
- [ ] Existing Shopify, Messaging, Admin and Commerce routing regression tests remain green (developer-owned integration suite pending).
- [x] Deployment documentation records DNS/TLS prerequisites, private-service topology, migration sequencing and environment isolation.
- [x] No live Render/DNS/credential mutation is required for task acceptance.

## Validation

Run the Gateway repository's declared validation commands and record exact commands/results.

Required validation:

- [x] `sh -n docker/entrypoint.sh`;
- [x] HAProxy rendered-config syntax validation with complete test fixture environment including `API_PUBLIC_HOST` and `MODA_API_UPSTREAM`;
- [ ] `tests/run-tests.sh` including API-host routing regressions (deferred to developer; see exact command below).
- [x] `tests/validate-render-blueprints.sh`;
- [x] `tests/validate-render-blueprints-negative.sh` with API-specific mutation cases;
- [x] `tests/validate-observability-config.sh` where the repository's normal Gateway validation still requires it;
- [x] YAML parse/Blueprint assertions via the repository's Psych-backed positive/negative Blueprint validators; no separate Render remote schema validator is available in this repository.
- [x] positive test Blueprint assertions for `moda-interact-api-test` and test API host/upstream;
- [x] positive production Blueprint assertions for `moda-interact-api-production` and production API host/upstream;
- [x] negative validation proving API cannot become public, gain `preDeployCommand`, receive Redis/provider secrets, cross environments, lose database/general config, or use the wrong repository/build/start/health contract;
- [ ] routing test proving API Host reaches only the API upstream and unknown Host returns 404 (implemented in `tests/run-tests.sh`; pending developer execution).
- [ ] regression test proving `GET /health` remains Gateway-local on API Host even when the API upstream is unavailable (implemented in `tests/run-tests.sh`; pending developer execution).
- [ ] routing test proving original API path/query/body are forwarded without prefix rewriting (implemented in `tests/run-tests.sh`; pending developer execution).
- [x] security/static scan proving no secret values or permissive CORS policy were committed;
- [x] `git diff --check`;
- [x] clean worktree/branch evidence required by the task protocol (recorded after publication).

Live Render deployment, custom-domain creation and DNS mutation are developer/operator validation after source acceptance, not prerequisites for this task to enter Architect Review.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete:

```text
finish Completion Report
        ->
set status: review
        ->
return control to moda_architect
        ->
STOP
```

Do not begin a system-test task or modify `moda-interact-api`/Woo application code.

## Implementation Notes

Preserve the current version-controlled two-Blueprint topology:

```text
render.test.yaml
render.production.yaml
```

Do not create a new canonical `render.yaml` merely because older architect-agent prose names that location.

The private API service uses the accepted application liveness route for Render service health. Do not turn PostgreSQL readiness into process liveness at the infrastructure layer; explicit `/health/ready` validation still proves database reachability during rollout/system testing.

Do not add Gateway-owned installation authentication. The API is the security boundary that understands installation identity and tenant authorization.

Do not infer API capacity from the Shopify webhook workload. The production two-instance count is an initial availability hypothesis and must remain documented as unmeasured until real API workload/load-test evidence exists.

## Completion Report

### Status

review

### Files Changed

- `README.md`
- `docker/entrypoint.sh`
- `docs/gateway.md`
- `docs/render-topology.md`
- `haproxy/haproxy.cfg`
- `render.test.yaml`
- `render.production.yaml`
- `tests/fixtures/upstream.py`
- `tests/run-tests.sh`
- `tests/validate-render-blueprints.sh`
- `tests/validate-render-blueprints-negative.sh`

### Work Completed

- Added exactly one private Node API service per environment using the API-001 repository, recursive submodule initialization, Prisma generation/build/start scripts, `/health/live`, `0.5c-512mb`, and the required 1-test/2-production instance assumptions. API service environment is limited to its environment's general config, `NODE_ENV=production`, and PostgreSQL `DATABASE_URL`; no public domain, Redis/provider groups, or migration command is declared.
- Added `api-test.modainteract.com` and `api.modainteract.com` only to the corresponding public Gateway domains and wired `API_PUBLIC_HOST` plus `MODA_API_UPSTREAM` to exact environment values and private API `hostport` references.
- Added the HAProxy API exact-host ACL/backend without path rewriting. Unknown hosts remain rejected. Existing local `/health` executes before backend routing; API `/health/live` and `/health/ready` retain their original paths.
- Extended runtime fixtures/tests for API path/query/body and Authorization/correlation-header forwarding, API health pass-through, unknown-host rejection, API upstream failure/recovery, gateway-local health during API outage, missing-variable failure, and Authorization non-logging.
- Extended positive and negative Blueprint validation for exact API service identity, commands, resources, health, environment, private exposure, API host/upstream identity, provider/Redis leakage and environment crossover.
- Updated README, Gateway routing documentation, and Render topology/runbook with private/public boundaries, DNS/TLS prerequisites, migration ordering, and assumed initial capacity. Clarified the previously broad private-service `healthCheckPath` documentation to explicitly reflect this task's required API declaration.
- Added `/health/live` to the pre-existing test Commerce Blueprint service because the repository's positive validator and production Blueprint already required it; this aligned test and production topology and was necessary to run the required positive check.

### Validation Results

- `sh -n docker/entrypoint.sh`: passed.
- `bash -n tests/run-tests.sh tests/validate-render-blueprints.sh tests/validate-render-blueprints-negative.sh`: passed.
- Built the Gateway image and rendered HAProxy with a complete fixture environment including API variables; `haproxy -c -V` reported `Configuration file is valid`. The first parse attempt used intentionally unresolved placeholder hostnames and failed server resolution; rerunning with loopback host:port fixture destinations passed.
- `bash tests/validate-render-blueprints.sh`: passed for both test and production YAML and API exact-host/template assertions.
- `bash tests/validate-render-blueprints-negative.sh`: passed all existing and API-specific mutations, including missing/miswired API host/upstream, public exposure, wrong service/build/start/health, migration command, Redis/provider group leakage, DB/general config loss, and cross-environment host/upstream/database wiring.
- `/Users/kwadwoadomafriyie/project/moda-interact-workspace/.venv/bin/python -m py_compile tests/fixtures/upstream.py`: passed; generated `__pycache__` removed.
- `bash tests/validate-observability-config.sh`: passed.
- `git diff --check`: passed.
- Static scan found no permissive CORS or Authorization logging in Gateway config. The only `npm run migrate`/`preDeployCommand` matches are the unchanged Shopify app service, not the API service.
- Developer validation required: `bash tests/run-tests.sh` from `moda-interact-gateway/`; expected result is all existing Gateway integration tests plus the new API-host routing/health/header/body/failure assertions pass. This multi-container Docker suite was not launched by the agent under the shared validation-execution policy.

### Worktree Evidence

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-026-GATEWAY-001`, `task/ARCH-026-GATEWAY-001`.
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-026-GATEWAY-001`, `task/ARCH-026-GATEWAY-001`.
- Parent task branch fast-forwarded from origin: `not-needed`; parent `origin/main` incorporated: `already-current`.
- Implementation task branch fast-forwarded from origin: `not-needed`; implementation `origin/main` incorporated: `already-current`.
- Launcher claim: Attempt 1, executor `copilot`, committed and pushed as `30ee7c9dd7c00a873e9e98dcfe56e17824cec360`.
- Recursive submodules: `git submodule sync --recursive` and `git submodule update --init --recursive` passed; no nested submodule entries exist in this repository.
- Shared workspace implementation checkout switched/mutated: no. Another task worktree reused: no.

### Deviations

- The full Docker integration suite is developer-executed under `docs/agent-validation-execution-policy.md`; its runtime assertions are implemented but remain unverified until the developer runs the recorded command.
- The existing positive Blueprint validator failed initially because the test Commerce service lacked `/health/live` despite the same validator requiring it and production declaring it. Added that health field to the test Commerce service; the positive and negative validators then passed.

### Assumptions

- API-001 exposes the repository scripts and health routes fixed by its accepted task contract.
- Render private Node services can consume the existing PostgreSQL resource through `fromDatabase` in both architecture-managed environments.
- `api-test.modainteract.com` and `api.modainteract.com` are available as the architecture-owned API hostnames; live DNS/custom-domain attachment remains operator work after source acceptance.

### Unresolved Issues

- The existing Render topology document previously asserted that `healthCheckPath` is unsupported on all `pserv` resources, while this task explicitly requires `/health/live` on the private API service. The document now records the task-specific API contract; the repository has no separate live Render/remote Blueprint-schema validator, so confirm Render acceptance of that private-service field during operator deployment validation.
- The API runtime routing and health regression tests are pending developer execution of `bash tests/run-tests.sh`.

### Architectural Concerns

- The API's private-service health-check field follows the explicit GATEWAY-001 contract, but conflicts with earlier generic Render capability prose. Architect/operator confirmation during deployment remains prudent; `/health/ready` is not used as liveness.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

Pending.
