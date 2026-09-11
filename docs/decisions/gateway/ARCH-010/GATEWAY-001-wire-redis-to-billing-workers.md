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
status: review
priority: 31
executor: copilot
claimed_at: 2026-09-11T22:41:25Z
attempt: 1
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

## Work Items

- [x] Add `moda-interact-production-redis-config` to the production billing worker.
- [x] Add `moda-interact-test-redis-config` to the test billing worker.
- [x] Preserve Shopify Partner app configuration and `DATABASE_URL` wiring.
- [x] Validate both Render Blueprints and the billing-worker topology.

## Acceptance Criteria

- [x] `moda-billing-worker-production` imports `moda-interact-production-redis-config`.
- [x] `moda-billing-worker-test` imports `moda-interact-test-redis-config`.
- [x] No services, plans, commands, routes, exposure, Redis resources/secrets, PostgreSQL resources, or other workers changed.
- [x] Changes are committed and pushed on both mirrored task branches without staging the parent submodule gitlink.

### Completion Report

### Status
Ready for Review.

### Files Changed
- `moda-interact-gateway/render.production.yaml`
- `moda-interact-gateway/render.test.yaml`
- `docs/decisions/gateway/ARCH-010/GATEWAY-001-wire-redis-to-billing-workers.md`

### Work Completed
- Added the existing production Redis config group to `moda-billing-worker-production`.
- Added the existing test Redis config group to `moda-billing-worker-test`.
- Preserved each worker's Shopify Partner app config and `DATABASE_URL` entries.
- Made no changes to services, plans, commands, routes, exposure, Redis resources/secrets, PostgreSQL resources, or other workers.

### Validation Results
- `bash tests/validate-render-blueprints.sh` from the implementation worktree: passed; both `render.test.yaml` and `render.production.yaml` were validated.
- Focused Ruby topology assertion over both Blueprints: passed; both billing workers have the environment config group, matching Redis group, Shopify app group, and `DATABASE_URL`.
- `git diff --check` in the implementation worktree: passed.

### Git / VCS
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-GATEWAY-001`, branch `task/ARCH-010-GATEWAY-001`, claim commit `492fdb4`, pushed to `origin/task/ARCH-010-GATEWAY-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-GATEWAY-001`, branch `task/ARCH-010-GATEWAY-001`, implementation commit `b96f24318c2cf5f47147fe6f7c4b8cdcfdd9f5c4`, pushed to `origin/task/ARCH-010-GATEWAY-001`.
- Both task worktrees are dedicated physical checkouts and clean after publication. The parent submodule gitlink was not staged.

### Architect Review
Pending.

## Stop conditions

STOP and return to `moda_architect` if the deployed billing worker topology/service names differ materially from the task baseline, if the required Redis environment group does not exist, or if satisfying the task would require provisioning/replacing Redis rather than wiring the existing shared service.
