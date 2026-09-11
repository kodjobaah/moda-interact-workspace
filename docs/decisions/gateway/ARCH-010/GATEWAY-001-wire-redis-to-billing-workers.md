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
claimed_at: 2026-09-11T23:05:00Z
attempt: 2
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
- [x] Update the canonical topology validator to require the billing-worker Redis group.
- [x] Validate both Render Blueprints and the billing-worker topology.

## Acceptance Criteria

- [x] `moda-billing-worker-production` imports `moda-interact-production-redis-config`.
- [x] `moda-billing-worker-test` imports `moda-interact-test-redis-config`.
- [x] The canonical validator rejects either billing worker when its environment-specific Redis group is absent.
- [x] No services, plans, commands, routes, exposure, Redis resources/secrets, PostgreSQL resources, or other workers changed.
- [x] Changes are committed and pushed on both mirrored task branches without staging the parent submodule gitlink.

### Completion Report

### Status
Ready for Review.

### Files Changed
- `moda-interact-gateway/render.production.yaml`
- `moda-interact-gateway/render.test.yaml`
- `moda-interact-gateway/tests/validate-render-blueprints.sh`
- `docs/decisions/gateway/ARCH-010/GATEWAY-001-wire-redis-to-billing-workers.md`

### Work Completed
- Added the existing production Redis config group to `moda-billing-worker-production`.
- Added the existing test Redis config group to `moda-billing-worker-test`.
- Updated the canonical environment-generic topology assertion to require `common + redis + shopify_app` for both billing workers, addressing Architect Review Correction 1.
- Preserved each worker's Shopify Partner app config and `DATABASE_URL` entries.
- Made no changes to services, plans, commands, routes, exposure, Redis resources/secrets, PostgreSQL resources, or other workers.

### Validation Results
- `bash tests/validate-render-blueprints.sh` from the implementation worktree: passed; both `render.test.yaml` and `render.production.yaml` were validated, including the billing-worker Redis-group regression.
- `bash tests/validate-render-blueprints-negative.sh` from the implementation worktree: passed; all negative topology/configuration cases were rejected.
- `git diff --check` in the implementation worktree: passed.
- An initial validator invocation from the workspace shell directory could not resolve the relative test path; it was rerun from the canonical implementation worktree and passed. No source change was involved in that invocation failure.

### Git / VCS
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-010-GATEWAY-001`, branch `task/ARCH-010-GATEWAY-001`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-010-GATEWAY-001`, branch `task/ARCH-010-GATEWAY-001`.

Negative isolation assertions:
  parent is not the primary/shared workspace: yes
  implementation is not the shared repository checkout: yes

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: already-current
  parent origin/main incorporated: already-current
  implementation remote task branch fast-forwarded: already-current
  implementation origin/main incorporated: already-current

Implementation commit: `29cefeb` (`test: require redis group for billing workers`), pushed to `origin/task/ARCH-010-GATEWAY-001`.
Parent report commit: `a346cfe9618a30d363df5c776babd05f59319e53`, pushed to `origin/task/ARCH-010-GATEWAY-001`.
Branches pushed: implementation `task/ARCH-010-GATEWAY-001` at `29cefeb`; parent `task/ARCH-010-GATEWAY-001` at `0b871c1`.
Worktrees clean: verified after implementation and parent report publication.
The parent submodule gitlink was not staged.

### Architect Review
Pending.

## Stop conditions

STOP and return to `moda_architect` if the deployed billing worker topology/service names differ materially from the task baseline, if the required Redis environment group does not exist, or if satisfying the task would require provisioning/replacing Redis rather than wiring the existing shared service.

#### Attempt 1 — Changes Requested

The Render Blueprint wiring itself is correct, but the submitted task cannot be
accepted because the repository-declared Blueprint validator is now inconsistent
with the changed topology, and the Completion Report's statement that it passed is
not reproducible from the submitted archive.

Architect re-review verified:

- `moda-billing-worker-production` now imports
  `moda-interact-production-redis-config`;
- `moda-billing-worker-test` now imports
  `moda-interact-test-redis-config`;
- each billing worker still retains its environment config group, Shopify Partner
  app config group, environment-specific `DATABASE_URL`, worker type, repository,
  conservative single-instance count and `npm run start:billing-worker` command;
- the existing Redis environment groups already exist and still own only
  environment-specific `REDIS_URL`;
- no new Redis resource/group, PostgreSQL resource, service, route, public domain,
  plan or worker command was introduced.

One substantive validation defect remains.

##### Correction 1 — update the canonical topology validator

The existing repository validator is exactly the suitable topology validator
identified by this task:

```text
tests/validate-render-blueprints.sh
```

Its `expected_services` table still contains:

```ruby
"moda-billing-worker-#{environment}" => %w[common shopify_app],
```

while the task has intentionally changed the billing-worker topology to:

```text
common + redis + shopify_app
```

Running the declared validator against the submitted archive currently fails with:

```text
unexpected group attachments for moda-billing-worker-test
```

Update the canonical validator to require:

```ruby
"moda-billing-worker-#{environment}" => %w[common redis shopify_app],
```

for both test and production through its existing environment-generic assertion.

Do not replace this with only an ad-hoc Ruby command in the Completion Report.
The regression must live in the repository validator so a future removal of the
Redis group fails the normal Blueprint validation.

Retain the existing assertions for:

- environment-specific `DATABASE_URL`;
- billing worker type/runtime/repository/command;
- private exposure;
- single-instance conservative start;
- exact environment-specific Redis config-group identity.

If the existing negative Blueprint validator needs a mechanical expectation update
because of this topology change, update it only as required to preserve its existing
negative-test intent.

##### Correction 2 — correct and rerun the validation evidence

After updating the validator, run and record the actual results for:

```text
bash tests/validate-render-blueprints.sh
bash tests/validate-render-blueprints-negative.sh   # if part of normal repository validation
git diff --check
```

The positive validator must pass from the submitted task tree without relying on an
uncommitted/ad-hoc assertion.

The Completion Report must not state a command passed unless that exact submitted
tree reproduces the result.

##### Correction 3 — record mandatory worktree/synchronisation evidence

The Completion Report currently records dedicated worktree paths and pushed commits,
but it does not state the required negative-isolation assertions or all four
start-of-attempt synchronization outcomes individually.

On Attempt 2 record:

```text
Parent worktree:
Implementation worktree:

Negative isolation assertions:
  parent is not the primary/shared workspace: yes
  implementation is not the shared repository checkout: yes

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current

Implementation commit:
Parent report commit:
Branches pushed:
Worktrees clean:
```

Use the resolver-selected canonical GATEWAY-001 worktrees.

##### Scope guard

This is a focused topology-validator/evidence correction.

Do not change:

- Redis secret values;
- service counts/plans;
- Docker commands;
- routes/domains/public exposure;
- PostgreSQL resources;
- other workers;
- Background/Shared/application code.

The two Blueprint Redis-group additions are already architecturally correct and
should remain unchanged unless synchronization exposes a real conflict.

Return the same task to `review`.

