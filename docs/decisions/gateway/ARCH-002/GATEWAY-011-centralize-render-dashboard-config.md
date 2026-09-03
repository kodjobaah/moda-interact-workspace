---
id: ARCH-002-GATEWAY-011
architecture_id: ARCH-002
title: Move externally supplied Render configuration into reusable environment groups
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
status: complete
priority: 5
executor: copilot
claimed_at: 2026-09-03T15:30:00Z
attempt: 2
depends_on:
  - ARCH-002-GATEWAY-010
enables:
  - ARCH-002-GATEWAY-009
  - ARCH-002-SYSTEM-TEST-006
  - ARCH-002-SYSTEM-TEST-009
created: 2026-09-03
updated: 2026-09-03
---

# Move Externally Supplied Render Configuration into Reusable Environment Groups

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Current Execution State

This task is **Complete**.

Attempt 1 was reviewed against the actual post-GATEWAY-010 Blueprint and the
pre-GATEWAY-011 accepted configuration.

The Environment Group model is generally correct, but one least-privilege
regression must be corrected before acceptance.

`ARCH-002-GATEWAY-010` is architect-accepted Complete.

The canonical deployment configuration group names now exist in source:

```text
moda-interact-test-config
moda-interact-production-config
```

This task may now be claimed by `moda_gateway`.

## Deployment Evidence

During real Render test deployment, the Blueprint prompted the developer for
service-level variables declared as:

```yaml
- key: SOME_SECRET
  sync: false
```

The values were entered, but the affected builds/deployments did not become
reliable until the same required values were placed in a Render Environment
Group attached to the services.

The deployment model must therefore stop depending on repeated service-level
`sync: false` placeholders for long-lived externally supplied configuration.

Render Environment Group variables must not use `sync: false`; those values are
populated in the Render Dashboard before Blueprint creation/sync.

## Objective

Make the canonical Blueprints reflect the deployment model that actually works:

```text
Dashboard-managed values
        ↓
purpose-scoped Render Environment Groups
        ↓
fromGroup
        ↓
only the services that consume those values
```

Remove the corresponding duplicated service-level `sync: false` declarations.

Do not put all secrets into one global group. Preserve least privilege by
grouping variables according to their actual consumer set.

## Canonical Group Model

Use the following test groups and mirror the same structure for production by
replacing `test` with `production`.

### 1. Common deployment/telemetry config

```text
moda-interact-test-config
```

Keys:

```text
DEPLOYMENT_ENVIRONMENT_NAME=test
OTEL_EXPORTER_OTLP_ENDPOINT
OTEL_EXPORTER_OTLP_HEADERS
LOKI_URL
LOKI_USERNAME
LOKI_PASSWORD
```

Consumers:

```text
moda-interact-test
moda-interact-messaging-test
moda-interact-admin-test
moda-shopify-event-worker-test
moda-recovery-worker-test
moda-messaging-worker-test
```

The five externally supplied OTEL/LOKI keys must be group variables with no
secret values committed to YAML.

### 2. Redis config

```text
moda-interact-test-redis-config
```

Key:

```text
REDIS_URL
```

Consumers:

```text
moda-interact-test
moda-interact-messaging-test
moda-shopify-event-worker-test
moda-recovery-worker-test
moda-messaging-worker-test
```

Admin and gateway must not receive `REDIS_URL` unless actual code/runtime
evidence proves they consume it.

### 3. Shared Shopify API credentials

```text
moda-interact-test-shopify-api-config
```

Keys:

```text
SHOPIFY_API_KEY
SHOPIFY_API_SECRET
```

Consumers must match the current Blueprint/runtime contract. Based on the
accepted ARCH-002 Blueprint this is expected to include:

```text
moda-interact-test
moda-recovery-worker-test
moda-messaging-worker-test
```

Do not broaden consumers merely for convenience.

### 4. Shopify application-only config

```text
moda-interact-test-shopify-app-config
```

Externally supplied keys:

```text
SCOPES
SHOPIFY_PARTNER_ORG_ID
SHOPIFY_PARTNER_ACCESS_TOKEN
SHOPIFY_APP_ID
```

Consumer:

```text
moda-interact-test
```

For the test environment, prefer infrastructure-owned non-secret URL
configuration rather than asking the Dashboard for a value:

```text
SHOPIFY_APP_URL=https://app-test.modainteract.com
```

This hostname is the already-agreed ARCH-002 test Shopify hostname and will be
codified as a gateway custom domain by `ARCH-002-GATEWAY-009`.

For production, do **not** invent a Shopify application hostname. If the
production Shopify hostname is still unresolved, keep `SHOPIFY_APP_URL`
externally supplied in the production Shopify-app group and document that
difference.

### 5. Admin authentication config

```text
moda-interact-test-admin-auth-config
```

Keys:

```text
AUTH_SECRET
AUTH_GOOGLE_ID
AUTH_GOOGLE_SECRET
```

Consumer:

```text
moda-interact-admin-test
```

Use the known non-secret test URL directly in the Blueprint:

```text
AUTH_URL=https://admin-test.modainteract.com
```

Production continues to use:

```text
AUTH_URL=https://admin.modainteract.com
```

Do not place Admin OAuth credentials in groups consumed by Shopify, Messaging
or Background workers.

### 6. Meta webhook verification config

```text
moda-interact-test-meta-webhook-config
```

Keys:

```text
WHATSAPP_VERIFY_TOKEN
META_APP_SECRET
```

Consumer:

```text
moda-interact-messaging-test
```

### 7. WhatsApp outbound API config

```text
moda-interact-test-whatsapp-api-config
```

Keys:

```text
WHATSAPP_ACCESS_TOKEN
WHATSAPP_PHONE_NUMBER_ID
```

Expected consumers:

```text
moda-recovery-worker-test
moda-messaging-worker-test
```

Preserve actual runtime evidence if the current accepted Blueprint differs.

### 8. AI provider config

```text
moda-interact-test-ai-config
```

Key:

```text
GROQ_API_KEY
```

Consumer:

```text
moda-messaging-worker-test
```

## Gateway-Owned Non-Secret Configuration

Do not attach the secret-bearing groups to the public gateway merely to supply
one hostname.

Use the known test Admin host directly:

```yaml
- key: ADMIN_PUBLIC_HOST
  value: admin-test.modainteract.com
```

Production remains:

```yaml
- key: ADMIN_PUBLIC_HOST
  value: admin.modainteract.com
```

The public gateway therefore receives no application/provider secrets through
this refactor.

## Database Wiring

Do not move:

```text
DATABASE_URL
```

into an Environment Group.

It remains canonical Render resource wiring:

```yaml
- key: DATABASE_URL
  fromDatabase:
    name: <environment PostgreSQL resource>
    property: connectionString
```

This is generated by Render from the correct database and must retain the
environment-isolation guarantees accepted in `SYSTEM-TEST-007`.

Likewise, gateway upstreams remain `fromService` references.

## Blueprint Representation

Environment-group secret/config keys must be declared without committed secret
values.

Example:

```yaml
envVarGroups:
  - name: moda-interact-test-redis-config
    envVars:
      - key: REDIS_URL
```

Do **not** write:

```yaml
sync: false
```

inside an `envVarGroup`.

Do **not** commit the actual value.

Services consume the groups with:

```yaml
envVars:
  - fromGroup: moda-interact-test-config
  - fromGroup: moda-interact-test-redis-config
```

and should no longer repeat:

```yaml
- key: REDIS_URL
  sync: false
```

for a key now owned by a group.

Avoid key collisions: each externally supplied key should have one canonical
source for a given service.

## Clean Recreation Order

The old Blueprint instance and old test Environment Group were already deleted.

After this task and the remaining gateway tasks are architect-accepted, the
developer should create/populate the required test Environment Groups in the
Render Dashboard **before** creating/syncing the Blueprint.

The task Completion Report must list every required test Environment Group and
every key the developer needs to populate, but must never include secret values.

Operational order:

```text
accepted Blueprints
    ↓
create required test Environment Groups in Render
    ↓
populate Dashboard values
    ↓
verify key names
    ↓
create/sync Blueprint
    ↓
verify group attachments
    ↓
verify builds/startup
```

## Scope

Owned repository:

```text
moda-interact-gateway
```

Expected implementation files:

```text
moda-interact-gateway/render.test.yaml
moda-interact-gateway/render.production.yaml
moda-interact-gateway/tests/validate-render-blueprints.sh
moda-interact-gateway/tests/validate-observability-config.sh
```

Update other gateway-owned deterministic validation only where required.

The task document may be updated under the normal coordination-document
exception.

Do not modify application repositories.

## Work Items

- [x] inspect the post-GATEWAY-010 canonical Blueprints;
- [x] define the purpose-scoped test Environment Groups above;
- [x] mirror them for production;
- [x] move duplicated external OTEL/LOKI variables into the common config group;
- [x] move Redis into its consumer-scoped group;
- [x] move Shopify API credentials into their shared consumer-scoped group;
- [x] move Shopify app-only config into its app-only group;
- [x] move Admin secrets into their Admin-only group;
- [x] move Meta webhook secrets into their Messaging-only group;
- [x] move WhatsApp outbound credentials into the worker consumer group;
- [x] move the AI provider key into the Messaging-worker-only group;
- [x] remove corresponding service-level `sync: false` duplicates;
- [x] preserve `DATABASE_URL` as `fromDatabase`;
- [x] preserve gateway upstreams as `fromService`;
- [x] make known test Admin/Auth/Shopify URLs infrastructure-owned values;
- [x] do not invent an unresolved production Shopify hostname;
- [x] ensure no `sync: false` exists inside an Environment Group;
- [x] validate least-privilege attachments;
- [x] produce a Dashboard recreation checklist without values;
- [x] return the task to `review`.

## Acceptance Criteria

- [x] service-level `sync: false` is no longer used for keys migrated to a
      Render Environment Group;
- [x] each migrated key has exactly one effective source per consumer service;
- [x] common OTEL/LOKI values are entered once per environment;
- [x] Redis is supplied only to Redis consumers;
- [x] Admin auth secrets are not exposed to non-Admin workloads;
- [x] Meta webhook secrets are not exposed outside the Messaging service;
- [x] WhatsApp outbound credentials are not exposed outside their worker
      consumers;
- [x] GROQ_API_KEY is not exposed outside the Messaging worker;
- [x] Shopify app-only partner configuration is not exposed to Background or
      Messaging;
- [x] shared Shopify API credentials are attached only to workloads that already
      require them;
- [x] no secret value is committed;
- [x] no `sync: false` appears inside an Environment Group;
- [x] `DATABASE_URL` remains exact environment-specific `fromDatabase` wiring;
- [x] test services never consume production config groups and vice versa;
- [x] gateway receives no provider/application secrets through a group;
- [x] test `ADMIN_PUBLIC_HOST`, `AUTH_URL` and `SHOPIFY_APP_URL` use their known
      ARCH-002 hostnames in source;
- [x] production Shopify hostname is not guessed;
- [x] gateway deterministic tests reject missing/wrong group attachments and
      service-level duplicates.

## Required Negative Validation

Add deterministic regression cases proving failure when:

1. a migrated key is restored as service-level `sync: false`;
2. an Environment Group variable contains `sync: false`;
3. Admin receives a Shopify/Meta/WhatsApp/AI secret group;
4. Messaging receives Admin auth secrets;
5. a worker receives the Admin auth group;
6. a test service references any production config group;
7. a production service references any test config group;
8. DATABASE_URL stops using the correct environment-specific Render Postgres;
9. a secret value is hardcoded in the Blueprint fixture used by validation.

Do not implement brittle validation that requires literal secret values.

## Validation

At minimum:

```text
bash tests/run-tests.sh
bash tests/validate-observability-config.sh
bash tests/validate-render-blueprints.sh
git diff --check
```

Also inspect the canonical Blueprints and report:

```text
test Environment Groups
production Environment Groups
group -> service attachment matrix
remaining service-level sync:false keys
```

The expected remaining service-level `sync: false` count for variables covered
by this task is zero.

If another genuine external variable exists in the actual post-GATEWAY-010
Blueprint that is not listed above, do not silently drop it. Classify it by
consumer set, place it in a least-privilege group, and document the deviation.

## System-Test Follow-On

`ARCH-002-SYSTEM-TEST-009` must validate the resulting group structure after
this task is architect-accepted.

Do not modify `moda-interact-system-test` from this gateway task.

## Non-Goals

- entering secret values in Render;
- recreating the Blueprint;
- changing application code;
- changing database topology;
- changing Render plans/counts;
- production capacity proof;
- provider secret rotation;
- custom-domain implementation (`GATEWAY-009`).


## Architect Correction — Attempt 2

### Issue

Attempt 1 incorrectly attached:

```text
moda-interact-test-shopify-api-config
```

to:

```text
moda-shopify-event-worker-test
```

and the production equivalent:

```text
moda-interact-production-shopify-api-config
```

to:

```text
moda-shopify-event-worker-production
```

This broadens access to:

```text
SHOPIFY_API_KEY
SHOPIFY_API_SECRET
```

beyond the accepted pre-GATEWAY-011 contract.

Immediately before GATEWAY-011, the Shopify event worker had:

```text
REDIS_URL
DATABASE_URL
OTEL/LOKI configuration
```

but did **not** have:

```text
SHOPIFY_API_KEY
SHOPIFY_API_SECRET
```

The original GATEWAY-011 task explicitly states that the expected Shopify API
credential consumers are:

```text
moda-interact-<environment>
moda-recovery-worker-<environment>
moda-messaging-worker-<environment>
```

and:

> Do not broaden consumers merely for convenience.

### Required Correction

For both test and production:

1. remove the Shopify API group from the Shopify event worker;
2. keep its common/telemetry and Redis groups;
3. keep `DATABASE_URL` as the existing environment-specific `fromDatabase`
   wiring;
4. update `tests/validate-render-blueprints.sh` so the accepted attachment
   matrix no longer requires Shopify API credentials on the Shopify event
   worker;
5. add a deterministic negative regression proving that attaching the Shopify
   API group to the Shopify event worker is rejected;
6. preserve all other GATEWAY-011 group definitions and attachments unless the
   correction itself requires a mechanical validator update.

Expected event-worker groups:

```text
test:
  moda-interact-test-config
  moda-interact-test-redis-config

production:
  moda-interact-production-config
  moda-interact-production-redis-config
```

The event worker must not receive:

```text
SHOPIFY_API_KEY
SHOPIFY_API_SECRET
AUTH_*
META_APP_SECRET
WHATSAPP_*
GROQ_API_KEY
```

### Revalidation

Run:

```text
bash tests/validate-render-blueprints.sh
bash tests/validate-render-blueprints-negative.sh
bash tests/validate-observability-config.sh
bash tests/run-tests.sh
git diff --check
```

The negative validation must include an explicit case equivalent to:

```text
shopify event worker + shopify-api-config -> FAIL
```

Return the same task to `review` after correction.

Do not create another task for this issue.

## Completion Report

### Status

Complete

### Files Changed

[render.test.yaml](../../../../moda-interact-gateway/render.test.yaml), [render.production.yaml](../../../../moda-interact-gateway/render.production.yaml), [validate-render-blueprints.sh](../../../../moda-interact-gateway/tests/validate-render-blueprints.sh), and [validate-render-blueprints-negative.sh](../../../../moda-interact-gateway/tests/validate-render-blueprints-negative.sh) were updated. No application repositories were modified.

### Work Completed

Both canonical Blueprints now define eight purpose-scoped groups per environment and attach them only to their consumer services. Migrated service-level placeholders were removed; gateway upstreams remain `fromService`, and database URLs remain environment-specific `fromDatabase` wiring. Test `SHOPIFY_APP_URL`, `AUTH_URL`, and `ADMIN_PUBLIC_HOST` use agreed hostnames. Production `SHOPIFY_APP_URL` remains externally supplied because its hostname is unresolved.

### Validation Results

`bash tests/validate-render-blueprints.sh`: passed.

`bash tests/validate-render-blueprints-negative.sh`: passed; all nine required invalid fixtures and the event-worker Shopify API attachment fixture were rejected.

`bash tests/run-tests.sh`: passed, 49 tests passed and 0 failed.

`bash tests/validate-observability-config.sh`: passed.

`git diff --check`: passed.

`npm run validate:arch002-production-readiness`: blocked because the system-test repository does not have the `yaml` Node module installed (`MODULE_NOT_FOUND`).

### Dashboard Recreation Checklist

Create and populate these groups in each environment before Blueprint sync:

- `moda-interact-test-config`: `DEPLOYMENT_ENVIRONMENT_NAME`, `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_EXPORTER_OTLP_HEADERS`, `LOKI_URL`, `LOKI_USERNAME`, `LOKI_PASSWORD`
- `moda-interact-test-redis-config`: `REDIS_URL`
- `moda-interact-test-shopify-api-config`: `SHOPIFY_API_KEY`, `SHOPIFY_API_SECRET`
- `moda-interact-test-shopify-app-config`: `SCOPES`, `SHOPIFY_PARTNER_ORG_ID`, `SHOPIFY_PARTNER_ACCESS_TOKEN`, `SHOPIFY_APP_ID`
- `moda-interact-test-admin-auth-config`: `AUTH_SECRET`, `AUTH_GOOGLE_ID`, `AUTH_GOOGLE_SECRET`
- `moda-interact-test-meta-webhook-config`: `WHATSAPP_VERIFY_TOKEN`, `META_APP_SECRET`
- `moda-interact-test-whatsapp-api-config`: `WHATSAPP_ACCESS_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`
- `moda-interact-test-ai-config`: `GROQ_API_KEY`

Repeat the same key sets with `production` replacing `test`; production also includes `SHOPIFY_APP_URL` in `moda-interact-production-shopify-app-config`. Never commit values to the Blueprint.

Attachment matrix:

- App: common, Redis, Shopify API, Shopify app
- Messaging: common, Redis, Meta webhook
- Admin: common, Admin auth
- Shopify event worker: common, Redis
- Recovery worker: common, Redis, Shopify API, WhatsApp
- Messaging worker: common, Redis, Shopify API, WhatsApp, AI

The public gateway receives no Environment Group. Remaining service-level `sync: false` keys covered by this task: zero.

### Deviations

Production `SHOPIFY_APP_URL` remains Dashboard-managed until an accepted task establishes the production Shopify hostname. The negative regression cases, including the event-worker Shopify API attachment case, are implemented in a separate gateway-owned validator script and must be run alongside the positive Blueprint validator.

### Assumptions

The post-GATEWAY-010 Blueprints retain the external-variable set represented by
the accepted ARCH-002 gateway configuration. The Render Dashboard groups will
be populated by the deployment operator before Blueprint creation/sync.

### Unresolved Issues

The production Shopify application hostname remains unresolved unless a later
accepted task establishes it.

### Architectural Concerns

Render Environment Groups improve reconstruction reliability, but a single
global secret-bearing group would violate least privilege. Group attachments
must follow actual consumer sets. The system-test readiness check still needs
the missing `yaml` dependency installed before it can verify the new structure.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 is accepted.

Architect reviewed the actual submitted gateway workspace and confirmed the
requested least-privilege correction:

- `moda-shopify-event-worker-test` no longer receives
  `moda-interact-test-shopify-api-config`;
- `moda-shopify-event-worker-production` no longer receives
  `moda-interact-production-shopify-api-config`;
- both event workers retain only the common/telemetry group, Redis group and
  environment-specific Render `DATABASE_URL` wiring;
- the positive attachment matrix now encodes that accepted boundary;
- negative validation includes an explicit
  `event_worker_shopify_api_group` case and rejects it;
- no migrated service-level `sync: false` declarations remain.

Architect independently executed:

```text
bash tests/validate-render-blueprints.sh
bash tests/validate-render-blueprints-negative.sh
bash tests/validate-observability-config.sh
```

All passed.

The submitted archive is not a Git working tree, so `git diff --check` cannot
be independently reproduced from the ZIP. The architect environment also does
not provide Docker, so the Docker-backed integration suite cannot be rerun
independently here. The repository agent reported 49/49 gateway checks passing
and `git diff --check` passing.

The Environment Group model and attempt-2 least-privilege correction satisfy
GATEWAY-011 acceptance criteria.
