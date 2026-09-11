---
id: ARCH-010-GATEWAY-001
architecture_id: ARCH-010
title: Wire Redis into deployed billing workers
task_kind: implementation
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 31
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-002-GATEWAY-001
enables:
  - ARCH-010-SYSTEM-TEST-001
created: 2026-09-11
updated: 2026-09-11
---

# ARCH-010-GATEWAY-001: Wire Redis into deployed billing workers

## Objective

Make the existing `moda-billing-worker-test` and `moda-billing-worker-production` capable of hosting the ARCH-010 BullMQ reconciliation consumer by supplying the already-defined environment-specific Redis config groups.

## Inspected baseline

In the supplied workspace:

```text
moda-interact-gateway/render.production.yaml
  moda-billing-worker-production
    has production-config + production-shopify-app-config + DATABASE_URL
    does NOT import moda-interact-production-redis-config

moda-interact-gateway/render.test.yaml
  moda-billing-worker-test
    has test-config + test-shopify-app-config + DATABASE_URL
    does NOT import moda-interact-test-redis-config
```

Other workers already use those Redis groups. Do not create new Redis resources/groups or secret values.

## Required change

In `render.production.yaml`, add exactly:

```yaml
- fromGroup: moda-interact-production-redis-config
```

to `moda-billing-worker-production.envVars`.

In `render.test.yaml`, add exactly:

```yaml
- fromGroup: moda-interact-test-redis-config
```

to `moda-billing-worker-test.envVars`.

Preserve existing Shopify Partner app config and DATABASE_URL wiring.

Do not change service counts/plans, Docker commands, Redis secret values, other workers, routes, public/private exposure or PostgreSQL resources.

## Validation

Run the repository's declared Render Blueprint/config validation tests/scripts that cover test and production YAML, then `git diff --check`. Add/update a focused regression asserting both billing workers receive the correct Redis group if a suitable existing topology validator exists.

## Non-goals

No Background code, Shared package, database, application UI, new Render service, Redis provisioning or credential changes.

## Completion Report

### Status
Not started.

### Files Changed
Populate during implementation.

### Work Completed
Populate during implementation.

### Validation Results
Populate during implementation.

### Git / VCS
Populate canonical isolated worktree/branch/commit/push evidence.

### Architect Review
Pending.

## Stop conditions

STOP and return to `moda_architect` if the deployed billing worker topology/service names differ materially from the task baseline, if the required Redis environment group does not exist, or if satisfying the task would require provisioning/replacing Redis rather than wiring the existing shared service.
