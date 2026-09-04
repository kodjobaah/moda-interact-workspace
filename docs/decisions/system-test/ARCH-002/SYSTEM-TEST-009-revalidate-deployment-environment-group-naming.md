---
id: ARCH-002-SYSTEM-TEST-009
architecture_id: ARCH-002
title: Revalidate deployment environment-group naming, ownership and isolation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
status: complete
priority: 47
executor: copilot
claimed_at: 2026-09-03T17:06:55Z
attempt: 3
depends_on:
  - ARCH-002-GATEWAY-010
  - ARCH-002-GATEWAY-011
  - ARCH-002-GATEWAY-012
  - ARCH-002-SYSTEM-TEST-007
enables:
  - ARCH-002-SYSTEM-TEST-008
---

# Revalidate Deployment Environment-Group Naming and Isolation

This task is **Ready — Architect Changes Requested remain applicable**.

The upstream Render Blueprint schema defect is resolved by
`ARCH-002-GATEWAY-012`, which is architect-accepted Complete.

The corrected gateway contract now uses explicit placeholder values in
Blueprint-managed Environment Groups:

```text
__SET_IN_RENDER_DASHBOARD__
```
`DEPLOYMENT_ENVIRONMENT_NAME` retains its real environment value.

The test placeholder literals intentionally remain in `render.test.yaml`.
Dashboard overrides remain operationally editable but require redeployment to
take effect; a later Blueprint sync may reset those test values to the
placeholder, which is an accepted test-environment trade-off.

Attempt 1's Architect Changes Requested still must be completed:

```text
cross-environment isolation must reject every opposite-environment
purpose-scoped Moda Interact config group, for both declarations and
fromGroup references, while unrelated groups remain allowed.
```

Update SYSTEM-TEST-009 against the final GATEWAY-012 placeholder-bearing
representation and return the same task to `review`.

`GATEWAY-013` is production-only and does not block this task.

## Current Gateway Context

`ARCH-002-GATEWAY-009` is also architect-accepted Complete. The canonical test
gateway now owns:

```text
admin-test.modainteract.com
app-test.modainteract.com
```

This task remains focused on the Environment Group naming/ownership/isolation
contract introduced by GATEWAY-010/GATEWAY-011. Do not broaden it into live
DNS/TLS validation; that belongs to SYSTEM-TEST-006.

## Objective

Update the accepted static readiness validator to recognize and enforce the new
concrete deployment configuration resource names:

```text
moda-interact-test-config
moda-interact-production-config
```

without weakening any of the isolation checks accepted in `SYSTEM-TEST-007`.

## Required Changes

Update the system-test static validator and focused tests so that it requires:

```text
test:
  moda-interact-test-config

production:
  moda-interact-production-config
```

for every service/worker already covered by the accepted environment-group
attachment checks.

Preserve the accepted cross-environment contamination behavior:

```text
test service + production config group      -> FAIL
production service + test config group      -> FAIL
```

Also require the deprecated feature-based resource names to fail:

```text
moda-observability-test
moda-observability-production
```

if they appear as active Blueprint environment-group declarations or
`fromGroup` references.

Historical task prose is not runtime configuration and should not be treated as
a failure.


## GATEWAY-011 Ownership Contract

In addition to the renamed common groups, validate the purpose-scoped
Dashboard-backed groups introduced by `GATEWAY-011`.

The validator must prove:

- no migrated variable remains duplicated as service-level `sync: false`;
- no Environment Group variable uses `sync: false`;
- each group is attached only to its accepted consumer set;
- Admin auth, Meta webhook, WhatsApp API and AI provider groups remain
  least-privilege;
- Redis and Shopify shared groups are attached only to actual consumers;
- `DATABASE_URL` remains exact `fromDatabase` wiring;
- test and production groups never cross environments;
- no secret values are required by the validator.

Preserve every other accepted SYSTEM-TEST-007 readiness check.

## Scope

Repository:

```text
moda-interact-system-test
```

Expected files:

```text
src/render-blueprint-validation.js
test/render-blueprint-validation.test.js
```

and task documentation.

Do not modify gateway Blueprints in this task.

## Work Items

- [x] update expected test config-group name;
- [x] update expected production config-group name;
- [x] preserve cross-environment contamination rejection;
- [x] add regression coverage rejecting old feature-based group names;
- [x] preserve unrelated non-observability/non-config group allowance;
- [x] run focused static readiness tests;
- [x] run full repository tests/typecheck/lint;
- [x] run the production-readiness command against the actual gateway files;
- [x] return to `review`.

## Acceptance Criteria

- [x] valid renamed test/production Blueprints pass;
- [x] old `moda-observability-*` active group names fail;
- [x] production referencing test config group fails;
- [x] test referencing production config group fails;
- [x] all existing PostgreSQL/Redis/provider/capacity/rollback readiness checks
      remain intact;
- [x] actual current gateway files pass the static readiness command after
      `GATEWAY-010`;
- [x] no gateway/application files are modified.

## Validation

Run:

```text
node --test test/render-blueprint-validation.test.js
npm test
npm run typecheck
npm run lint
npm run validate:arch002-production-readiness
git diff --check
```

## Non-Goals

- changing Render Dashboard values;
- changing Blueprint environment-variable membership;
- changing custom domains;
- live Render validation;
- capacity testing.


## Architect Correction — Attempt 2

### Issue

Attempt 1 rejects cross-environment use of the common groups:

```text
moda-interact-test-config
moda-interact-production-config
```

but does not reject the opposite environment's purpose-scoped configuration
groups.

For example, the submitted validator accepts this invalid production state:

```yaml
moda-recovery-worker-production:
  envVars:
    # valid production groups remain attached
    - fromGroup: moda-interact-production-config
    - fromGroup: moda-interact-production-redis-config
    - fromGroup: moda-interact-production-shopify-api-config
    - fromGroup: moda-interact-production-whatsapp-api-config

    # INVALID cross-environment attachment
    - fromGroup: moda-interact-test-whatsapp-api-config
```

Architect directly invoked the submitted `validateProductionReadiness`
implementation with the current accepted gateway Blueprints plus that mutation.

Actual result:

```json
{
  "valid": true,
  "errors": []
}
```

This violates the task's accepted ownership contract:

> test and production groups never cross environments.

The same gap applies to purpose-scoped group declarations. For example, a test
Blueprint must not be allowed to declare an active
`moda-interact-production-redis-config` group simply because the common
production group is absent.

### Required Correction

Generalize environment isolation across **all canonical Moda Interact
configuration groups**, including:

```text
moda-interact-<environment>-config
moda-interact-<environment>-redis-config
moda-interact-<environment>-shopify-api-config
moda-interact-<environment>-shopify-app-config
moda-interact-<environment>-admin-auth-config
moda-interact-<environment>-meta-webhook-config
moda-interact-<environment>-whatsapp-api-config
moda-interact-<environment>-ai-config
```

For a test Blueprint:

```text
any active moda-interact-production-*-config declaration/reference -> FAIL
```

For a production Blueprint:

```text
any active moda-interact-test-*-config declaration/reference -> FAIL
```

The common group without an intermediate purpose segment is included in this
rule.

Do not implement this as a loose substring test that rejects unrelated groups.
The task explicitly requires unrelated non-observability/non-config groups to
remain allowed.

A robust implementation should inspect active `envVarGroups[].name` and
service `envVars[].fromGroup` values and identify the opposite environment's
Moda Interact configuration-group namespace.

### Required Regression Coverage

At minimum add deterministic tests proving:

1. production service + test purpose group -> FAIL, e.g.
   `moda-interact-test-whatsapp-api-config`;
2. test service + production purpose group -> FAIL, e.g.
   `moda-interact-production-redis-config`;
3. test Blueprint declaration of a production purpose group -> FAIL;
4. production Blueprint declaration of a test purpose group -> FAIL;
5. existing common-group contamination tests continue to fail;
6. an unrelated non-MODA config/environment group remains allowed.

Keep all existing least-privilege consumer-set tests intact.

### Revalidation

Run:

```text
node --test test/render-blueprint-validation.test.js
npm test
npm run typecheck
npm run lint
npm run validate:arch002-production-readiness
git diff --check
```

Return the same task to `review` after the correction.

Do not create another task for this issue.


## Resolved Upstream Block — GATEWAY-012

GATEWAY-012 is architect-accepted Complete.

SYSTEM-TEST-009 must now validate the actual accepted representation:

```text
Blueprint-managed purpose-scoped Environment Groups
  DEPLOYMENT_ENVIRONMENT_NAME = real test/production value
  all externally supplied keys = __SET_IN_RENDER_DASHBOARD__

service fromGroup attachments
  exact least-privilege consumer matrix
```

The test Shopify app group includes:

```text
SCOPES
SHOPIFY_PARTNER_ORG_ID
SHOPIFY_PARTNER_ACCESS_TOKEN
SHOPIFY_APP_ID
SHOPIFY_APP_URL
```

The previously requested generalized cross-environment contamination tests
remain required.



## Architect Correction — Attempt 3

### Remaining Issue

Attempt 2 correctly rejects all currently enumerated canonical purpose groups,
but the implementation still encodes a closed whitelist:

```text
redis
shopify-api
shopify-app
admin-auth
meta-webhook
whatsapp-api
ai
```

The accepted architect requirement is namespace-based:

```text
test Blueprint:
  any active moda-interact-production-*-config
  declaration/reference -> FAIL

production Blueprint:
  any active moda-interact-test-*-config
  declaration/reference -> FAIL
```

The common group:

```text
moda-interact-test-config
moda-interact-production-config
```

is included as the zero-purpose form.

The current implementation does not satisfy that wildcard rule.

For example:

```text
moda-interact-test-new-provider-config
```

is a Moda Interact test configuration group by namespace, but the submitted
`isModaConfigurationGroup()` / `oppositeGroupPattern` whitelist does not
recognize it.

That means an invalid production attachment such as:

```yaml
- fromGroup: moda-interact-test-new-provider-config
```

would not be rejected by the cross-environment isolation check.

### Required Correction

Replace the purpose whitelist used for **environment isolation** with a
namespace-safe matcher.

The matcher should recognise:

```text
moda-interact-test-config
moda-interact-test-<purpose>-config

moda-interact-production-config
moda-interact-production-<purpose>-config
```

where `<purpose>` is one or more valid name segments.

It must reject the opposite environment regardless of whether that purpose is
currently known to the consumer-matrix validator.

Do not weaken the separate exact canonical-group validation. The exact
GATEWAY-012 group names/key sets/consumer sets should still be enforced by the
existing contract checks.

In other words:

```text
environment isolation:
  namespace-based / future-safe

canonical group ownership:
  exact known set
```

### Required Regression Coverage

Add deterministic tests proving at minimum:

```text
production service + moda-interact-test-new-provider-config -> FAIL
test service + moda-interact-production-new-provider-config -> FAIL

production Blueprint declaration:
  moda-interact-test-new-provider-config -> FAIL

test Blueprint declaration:
  moda-interact-production-new-provider-config -> FAIL

third-party-monitoring-config -> allowed
other unrelated non-MODA group -> allowed
```

Keep the existing tests for all current canonical groups.

### Full-Suite Note

Attempt 2 reported one WhatsApp emulator deserialization failure only when the
full suite is run, while that file passes independently.

This is not the reason for the current Changes Requested decision.

After the namespace correction, rerun the required validation. If the same
unrelated full-suite failure persists, preserve:

```text
full-suite failure output
isolated whatsapp-emulator test result
```

in the Completion Report rather than changing unrelated emulator code in this
task.

### Revalidation

Run:

```text
node --test test/render-blueprint-validation.test.js
npm test
npm run typecheck
npm run lint
npm run validate:arch002-production-readiness
git diff --check
```

Return the same task to `review`.

Do not create a new correction task.

## Completion Report

### Status

Ready for Review

### Files Changed

`moda-interact-system-test/src/render-blueprint-validation.js`; `moda-interact-system-test/test/render-blueprint-validation.test.js`; this task document.

### Work Completed

Updated static readiness validation for renamed common configuration groups and purpose-scoped Dashboard-backed groups. Added exact consumer ownership, group key/sync hygiene, rejection of migrated service-level `sync: false` declarations, deprecated observability-name rejection, and future-safe namespace-based cross-environment configuration-group isolation across declarations and `fromGroup` references. The validator now accepts the canonical GATEWAY-012 `__SET_IN_RENDER_DASHBOARD__` placeholders while preserving real deployment identity checks. Preserved existing database, Redis, provider, capacity, migration, rollback, routing and secret checks.

### Validation Results

`node --test test/render-blueprint-validation.test.js`: 23 passed, 0 failed. `npm test`: 40 passed, 0 failed, 2 opt-in Docker tests skipped. `npm run typecheck`: passed. `npm run lint`: passed. `npm run validate:arch002-production-readiness`: passed with `{ "valid": true, "errors": [] }`. `git diff --check`: passed.

### Deviations

Repository dependencies were absent initially; declared dependencies were installed locally without intentional manifest changes. No gateway or application files were modified. Repository agent did not commit or push.

### Assumptions

`GATEWAY-010`, `GATEWAY-011`, and `GATEWAY-012` are accepted before this task executes. Both environments own `SHOPIFY_APP_URL` through their Shopify app Environment Group.

### Unresolved Issues

The two live Docker validations remain opt-in and were skipped.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 3 is architect-accepted Complete.

Architect reviewed the actual submitted implementation and confirmed:

- `isModaConfigurationGroup()` is namespace-based rather than a closed purpose
  whitelist;
- the opposite-environment matcher rejects both the common group and arbitrary
  future purpose-scoped Moda Interact configuration groups;
- future unknown group references are tested in both test -> production and
  production -> test directions;
- future unknown group declarations are tested in both directions;
- unrelated configuration groups such as `third-party-monitoring-config`
  remain allowed;
- unrelated non-MODA groups remain allowed;
- exact canonical GATEWAY-012 group names, keys and consumer sets remain
  independently enforced;
- the accepted GATEWAY-012 placeholder representation remains valid.

The repository agent reports:

```text
focused tests: 23 passed
full suite: 40 passed, 2 opt-in skips
typecheck: passed
lint: passed
production readiness: passed
git diff --check: passed
```

The architect review container does not contain the repository's installed
dependencies and provides Node 22 rather than the repository-declared Node 24+
runtime, so the npm suite was not independently rerun from the submitted ZIP.
The implementation and regression changes were inspected directly.

A task-document coordination typo was corrected during acceptance:
`ARCH-002-SYSTEM-TEST-008` had accidentally been placed under `depends_on`
instead of `enables`, which would have created a cycle because SYSTEM-TEST-008
already depends on SYSTEM-TEST-009. The canonical relationship is restored:

```text
SYSTEM-TEST-009 -> enables SYSTEM-TEST-008
```
