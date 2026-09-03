---
id: ARCH-002-GATEWAY-012
architecture_id: ARCH-002
title: Bootstrap Render Environment Groups with explicit placeholder values
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
status: complete
priority: 5
executor: copilot
claimed_at: 2026-09-03T16:10:12Z
attempt: 2
depends_on:
  - ARCH-002-GATEWAY-009
  - ARCH-002-GATEWAY-011
enables:
  - ARCH-002-SYSTEM-TEST-009
  - ARCH-002-SYSTEM-TEST-006
  - ARCH-002-GATEWAY-013
created: 2026-09-03
updated: 2026-09-03T16:24:14Z
---

# Bootstrap Render Environment Groups with Explicit Placeholder Values

## Current Execution State

This task is **Complete**.

A real Render Blueprint creation attempt failed with errors such as:

```text
envVarGroups[0].envVars[1] must have a key and value
envVarGroups[1].envVars[0] must have a key and value
...
```

The current Blueprint contains key-only entries inside top-level Environment
Groups.

The required immediate correction is to give every externally supplied
Environment Group variable an explicit, non-secret placeholder `value`.

## Objective

Keep the purpose-scoped Blueprint-managed Environment Groups introduced by
GATEWAY-011, but make the Blueprint schema-valid by supplying an explicit
bootstrap placeholder for every externally managed value.

Use the canonical sentinel:

```text
__SET_IN_RENDER_DASHBOARD__
```

Example:

```yaml
envVarGroups:
  - name: moda-interact-test-redis-config
    envVars:
      - key: REDIS_URL
        value: "__SET_IN_RENDER_DASHBOARD__"
```

The sentinel is not a credential and must be identical everywhere an external
value is awaiting Dashboard replacement.

## Non-Placeholder Values

Infrastructure-owned non-secret values remain real values.

In particular:

```yaml
- key: DEPLOYMENT_ENVIRONMENT_NAME
  value: test
```

and:

```yaml
- key: DEPLOYMENT_ENVIRONMENT_NAME
  value: production
```

must not use the placeholder.

Known non-secret service values already owned by the Blueprint remain real
values where they are intentionally infrastructure-owned, including:

```text
ADMIN_PUBLIC_HOST
AUTH_URL
```

`SHOPIFY_APP_URL` is operationally editable application configuration and is
owned by the Shopify app Environment Group in both test and production.

Do not invent the unresolved production Shopify URL; its group entry receives
the bootstrap sentinel.

## Canonical Group Model

Preserve all accepted GATEWAY-011 group names, key sets and least-privilege
consumer sets.

Test:

```text
moda-interact-test-config
moda-interact-test-redis-config
moda-interact-test-shopify-api-config
moda-interact-test-shopify-app-config
moda-interact-test-admin-auth-config
moda-interact-test-meta-webhook-config
moda-interact-test-whatsapp-api-config
moda-interact-test-ai-config
```

Production mirrors those names with `production`.

Do not broaden group consumers.

The Shopify event worker remains excluded from Shopify API credentials.

## Required Blueprint Changes

Update:

```text
render.test.yaml
render.production.yaml
```

so every current key-only Environment Group variable has a value.

For externally supplied variables:

```yaml
value: "__SET_IN_RENDER_DASHBOARD__"
```

For environment identity:

```yaml
DEPLOYMENT_ENVIRONMENT_NAME=test
DEPLOYMENT_ENVIRONMENT_NAME=production
```

No:

```yaml
sync: false
```

may appear inside an Environment Group.

No real secret may be committed.

## Required Validation

Gateway validation must prove:

1. no key-only Environment Group entry remains;
2. every external group variable has exactly the sentinel value;
3. `DEPLOYMENT_ENVIRONMENT_NAME` has its real environment value;
4. no secret-looking or arbitrary literal is committed for an external key;
5. no `sync: false` appears inside an Environment Group;
6. existing purpose-scoped `fromGroup` attachment matrix remains exact;
7. Shopify event workers remain excluded from Shopify API groups;
8. test/production group isolation remains exact;
9. custom-domain contract remains intact;
10. database/service Render wiring remains intact.

Add negative cases for:

```text
missing placeholder value
wrong placeholder value
real-looking hardcoded secret
sync:false in group
```

while preserving the accepted GATEWAY-011/GATEWAY-009 negative cases.

## Live Test Bootstrap Sequence

After architect acceptance:

```text
1. developer commits/pushes GATEWAY-012
2. create Blueprint using render.test.yaml
3. Render creates the Environment Groups with placeholder values
4. Blueprint schema must pass
5. replace every __SET_IN_RENDER_DASHBOARD__ value
   in the Render test Environment Groups with the real test value
6. verify DEPLOYMENT_ENVIRONMENT_NAME=test
7. allow affected services to rebuild/redeploy
8. verify no placeholder remains in the live test Environment Groups
   before running live system validation
```

The placeholder literals remain permanently in `render.test.yaml`.

A later Blueprint sync may therefore restore those placeholder values in the
test Dashboard groups. That is an accepted trade-off for the test environment.
If it happens, re-enter the test values before running live integration/system
tests again.

The first service deploy may fail while placeholder values are active. That is
acceptable during bootstrap; the task must not claim runtime health until the
real Dashboard values have replaced every live placeholder.

## Test Environment Placeholder Policy

For **test**, the placeholders are intentionally permanent source values.

The canonical test policy is:

```text
render.test.yaml
    keeps __SET_IN_RENDER_DASHBOARD__
        ↓
Blueprint creation/sync may reset Dashboard overrides
        ↓
developer re-enters test values when necessary
        ↓
live test validation proceeds only when Dashboard values are real
```

This is acceptable because the test environment is disposable and operational
re-entry of test secrets/configuration is tolerable.

Do not create a test finalization task that removes placeholders from
`render.test.yaml`.

### Production policy

Production is treated separately.

Do not assume the test placeholder policy is acceptable for production.
`ARCH-002-GATEWAY-013` is a **production-only** hardening/design task that will
establish the final production secret/config ownership model before production
deployment is considered ready.

`GATEWAY-013` does **not** block the test path:

```text
SYSTEM-TEST-009
SYSTEM-TEST-006
```

Those test tasks wait only for GATEWAY-012 plus their existing dependencies.

## Scope

Repository:

```text
moda-interact-gateway
```

Expected files:

```text
render.test.yaml
render.production.yaml
tests/validate-render-blueprints.sh
tests/validate-render-blueprints-negative.sh
```

Do not modify application or system-test repositories.

## Acceptance Criteria

- [x] Render's reported key-and-value schema defect is eliminated;
- [x] all external Environment Group variables use
      `__SET_IN_RENDER_DASHBOARD__`;
- [x] environment identity remains real `test` / `production`;
- [x] no secret value is committed;
- [x] no `sync: false` exists inside a group;
- [x] accepted least-privilege consumer matrix is unchanged;
- [x] Shopify event workers receive no Shopify API credentials;
- [x] test custom domains remain exact;
- [x] positive and negative gateway validation passes;
- [x] live test bootstrap sequence and accepted re-entry-on-sync behavior are documented;
- [x] task returns to `review`.

## Validation

Run:

```text
bash tests/validate-render-blueprints.sh
bash tests/validate-render-blueprints-negative.sh
bash tests/validate-observability-config.sh
bash tests/run-tests.sh
git diff --check
```

Also report:

```text
key-only env-group entries: 0
external placeholder entries: <expected count>
group sync:false entries: 0
real secret values committed: 0
```


## Architect Correction — Attempt 2

### Issue

The test Shopify application currently consumes:

```yaml
- fromGroup: moda-interact-test-shopify-app-config
- key: SHOPIFY_APP_URL
  value: https://app-test.modainteract.com
```

while `moda-interact-test-shopify-app-config` contains the other Shopify
application settings:

```text
SCOPES
SHOPIFY_PARTNER_ORG_ID
SHOPIFY_PARTNER_ACCESS_TOKEN
SHOPIFY_APP_ID
```

This splits one operational configuration boundary across both a Dashboard-
editable Environment Group and a hard-coded service-level value.

For the test environment, that is undesirable because `SHOPIFY_APP_URL` needs
to be editable from Render without changing the Blueprint source.

### Required Correction

Move:

```text
SHOPIFY_APP_URL
```

into:

```text
moda-interact-test-shopify-app-config
```

with the canonical test placeholder:

```yaml
- key: SHOPIFY_APP_URL
  value: "__SET_IN_RENDER_DASHBOARD__"
```

Then remove the direct service-level test entry:

```yaml
- key: SHOPIFY_APP_URL
  value: https://app-test.modainteract.com
```

from:

```text
moda-interact-test
```

The effective test Shopify application configuration should therefore be owned
entirely by:

```text
moda-interact-test-shopify-app-config
```

for:

```text
SCOPES
SHOPIFY_PARTNER_ORG_ID
SHOPIFY_PARTNER_ACCESS_TOKEN
SHOPIFY_APP_ID
SHOPIFY_APP_URL
```

### Why This Is Not a Group Merge

Do **not** merge:

```text
moda-interact-test-shopify-api-config
moda-interact-test-shopify-app-config
```

They serve different consumer boundaries.

`moda-interact-test-shopify-api-config` remains:

```text
SHOPIFY_API_KEY
SHOPIFY_API_SECRET
```

and is shared only with workloads that actually require Shopify API
credentials.

`moda-interact-test-shopify-app-config` remains app-only and now additionally
owns `SHOPIFY_APP_URL`.

### Production

Do not change the production ownership model merely for symmetry if it already
has:

```text
SHOPIFY_APP_URL
```

inside:

```text
moda-interact-production-shopify-app-config
```

The goal is to bring test into the same ownership pattern.

### Validator Changes

Update positive validation so it requires:

```text
moda-interact-test-shopify-app-config
    includes SHOPIFY_APP_URL
    with __SET_IN_RENDER_DASHBOARD__
```

and rejects any direct service-level `SHOPIFY_APP_URL` on
`moda-interact-test`.

Preserve the existing production expectation.

Add deterministic negative regression coverage proving:

1. test Shopify app group missing `SHOPIFY_APP_URL` -> FAIL;
2. test `SHOPIFY_APP_URL` has a non-placeholder group value -> FAIL;
3. test service restores direct `SHOPIFY_APP_URL` -> FAIL;
4. existing group/least-privilege/schema negative cases still pass.

### Dashboard Checklist

Update the test recreation checklist to include:

```text
moda-interact-test-shopify-app-config:
  SCOPES
  SHOPIFY_PARTNER_ORG_ID
  SHOPIFY_PARTNER_ACCESS_TOKEN
  SHOPIFY_APP_ID
  SHOPIFY_APP_URL
```

The operator will set:

```text
SHOPIFY_APP_URL=https://app-test.modainteract.com
```

in the Render Dashboard after Blueprint creation.

Do not commit that URL as the test service's direct runtime value in this task.

### Revalidation

Run:

```text
bash tests/validate-render-blueprints.sh
bash tests/validate-render-blueprints-negative.sh
bash tests/validate-observability-config.sh
bash tests/run-tests.sh
git diff --check
```

Also report:

```text
test Shopify app group keys
direct test SHOPIFY_APP_URL entries
placeholder count
```

Expected:

```text
test Shopify app group contains SHOPIFY_APP_URL
direct test SHOPIFY_APP_URL entries: 0
```

Return the same task to `review`.

Do not create a new task for this correction.

## Completion Report

### Status

Ready for Review

### Files Changed

`render.test.yaml`; `render.production.yaml`; `tests/validate-render-blueprints.sh`; `tests/validate-render-blueprints-negative.sh`; this task document.

### Work Completed

Added the canonical Render Dashboard bootstrap sentinel to all 42 externally supplied Environment Group variables while retaining real test/production deployment identity values and Blueprint-owned non-secret service values. Moved test `SHOPIFY_APP_URL` into `moda-interact-test-shopify-app-config` and removed its direct service-level value. Extended positive validation to reject missing or incorrect placeholders and split test URL ownership, and added negative fixtures for missing placeholders, wrong placeholders, hardcoded values, group `sync: false`, and the three Attempt 2 URL regressions. Existing consumer, domain, database, and security checks remain intact.

### Validation Results

`bash tests/validate-render-blueprints.sh`: passed. `bash tests/validate-render-blueprints-negative.sh`: passed with 17 rejected cases. `bash tests/validate-observability-config.sh`: passed. `bash tests/run-tests.sh`: 49 passed, 0 failed. `git diff --check`: passed. Counts: key-only env-group entries: 0; external placeholder entries: 42; group sync:false entries: 0; real secret values committed: 0. Test Shopify app group keys: `SCOPES`, `SHOPIFY_PARTNER_ORG_ID`, `SHOPIFY_PARTNER_ACCESS_TOKEN`, `SHOPIFY_APP_ID`, `SHOPIFY_APP_URL`; direct test `SHOPIFY_APP_URL` entries: 0; test placeholder count: 21.

### Live Bootstrap Checklist

Not executed by the repository agent.

### Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 is architect-accepted Complete.

Architect reviewed the actual submitted gateway workspace and confirmed:

- all canonical Environment Group entries have a Render-valid `value`;
- `DEPLOYMENT_ENVIRONMENT_NAME` remains the real environment identity;
- all externally supplied values use the canonical
  `__SET_IN_RENDER_DASHBOARD__` sentinel;
- there are 21 external placeholders in test and 21 in production;
- there are no key-only group variables and no group-level `sync: false`;
- `SHOPIFY_APP_URL` is now owned by
  `moda-interact-test-shopify-app-config`;
- the direct test service-level `SHOPIFY_APP_URL` entry is absent;
- the test Shopify app group contains exactly:
  `SCOPES`, `SHOPIFY_PARTNER_ORG_ID`,
  `SHOPIFY_PARTNER_ACCESS_TOKEN`, `SHOPIFY_APP_ID`,
  `SHOPIFY_APP_URL`;
- the Shopify API and Shopify app groups remain separate least-privilege
  boundaries;
- Shopify event workers remain excluded from Shopify API credentials;
- database and gateway resource wiring remains intact;
- the test custom-domain contract remains intact.

Architect independently executed:

```text
bash tests/validate-render-blueprints.sh
bash tests/validate-render-blueprints-negative.sh
bash tests/validate-observability-config.sh
```

All passed. The negative suite rejected all 17 submitted regression fixtures.

The architect environment does not provide Docker, so
`tests/run-tests.sh` cannot be independently reproduced here. The repository
agent reported 49 passed, 0 failed, and `git diff --check` passing.

Live evidence supplied by the developer also confirms that Render now accepts
the test Blueprint and has instantiated the complete test topology: gateway,
private application services, workers, PostgreSQL, and all eight test
Environment Groups. The live Shopify app group shows five variables, consistent
with the accepted Attempt 2 ownership model.

This acceptance covers the test placeholder policy only. GATEWAY-013 remains a
separate production-only hardening/design task and does not block the test
validation path.
