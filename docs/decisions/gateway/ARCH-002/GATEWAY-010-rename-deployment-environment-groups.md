---
id: ARCH-002-GATEWAY-010
architecture_id: ARCH-002
title: Establish concrete Moda Interact deployment configuration groups
domain: gateway
repository: moda-interact-gateway
assigned_agent: moda_gateway
coordinator: moda_architect
status: complete
priority: 5
executor: copilot
claimed_at: 2026-09-03T14:35:13Z
attempt: 1
depends_on:
  - ARCH-002-GATEWAY-008
enables:
  - ARCH-002-GATEWAY-009
  - ARCH-002-SYSTEM-TEST-006
  - ARCH-002-SYSTEM-TEST-009
created: 2026-09-03
updated: 2026-09-03
---

# Establish Concrete Moda Interact Deployment Configuration Groups

## Architecture

Architecture ID:

`ARCH-002`

Architecture document:

`docs/architecture/ARCH-002-render-production-gateway-infrastructure.md`

Coordinator:

`moda_architect`

## Current Execution State

This task is **Complete**.

The previous Render Blueprint instance and the previous
`moda-observability-test` Environment Group have both been deleted by the
developer before this task started.

There is therefore no live Render Environment Group to rename or preserve.

The code-level naming correction remains required:

```text
moda-observability-test
    -> moda-interact-test-config

moda-observability-production
    -> moda-interact-production-config
```

The operational model is now a clean recreation:

```text
1. moda_gateway updates the canonical Blueprints and validators.
2. moda_architect reviews/accepts this task.
3. The developer creates the new Render Environment Group:
      moda-interact-test-config
4. The developer repopulates the required test values in Render.
5. The developer recreates/syncs the Blueprint.
6. Render services attach to the new canonical group.
```

No old Dashboard-held group values remain in Render and this task must not
assume otherwise.

Secret/config values still remain outside Git and must not be invented or
committed by the agent.

## Objective

Rename the shared Render deployment environment groups and all canonical
Blueprint references from feature-oriented names to concrete deployment
configuration resource names without changing the currently working variable
membership.

Mapping:

```text
moda-observability-test
    -> moda-interact-test-config

moda-observability-production
    -> moda-interact-production-config
```

## Clean Recreation Constraint

The previous Blueprint instance and old test Environment Group no longer exist.

This task therefore does **not** perform or document a live rename.

Instead, it prepares the canonical source state for clean recreation.

The agent must:

- rename the canonical Blueprint group declarations and references;
- preserve the environment identity values declared in YAML;
- keep secret/config values out of source control;
- document the exact new Environment Group names the developer must create;
- not assume any old Render group/value state survives.

After architect acceptance, the developer will create:

```text
moda-interact-test-config
```

in Render and repopulate the required test-environment values manually before
recreating/syncing the Blueprint.

For production, the canonical name becomes:

```text
moda-interact-production-config
```

but no production secret/config values are to be created or modified by this
task.

If the new Blueprint would cause Render to create an empty group before the
developer has populated the required test configuration, do not publish/sync it
yet. The developer-owned publication order is:

```text
accepted source
  ->
create/populate Render Environment Group
  ->
publish/sync Blueprint
```

## Required Blueprint Changes

In:

```text
moda-interact-gateway/render.test.yaml
```

rename:

```yaml
envVarGroups:
  - name: moda-observability-test
```

to:

```yaml
envVarGroups:
  - name: moda-interact-test-config
```

and change every:

```yaml
- fromGroup: moda-observability-test
```

to:

```yaml
- fromGroup: moda-interact-test-config
```

Do the corresponding production rename in:

```text
moda-interact-gateway/render.production.yaml
```

using:

```text
moda-interact-production-config
```

Preserve:

```yaml
DEPLOYMENT_ENVIRONMENT_NAME: test
DEPLOYMENT_ENVIRONMENT_NAME: production
```

exactly by environment.

## Variable Ownership Boundary

This task is a **resource naming correction**, not a secret redistribution.

Do not:

- delete currently required service-local `sync: false` declarations;
- move new secret values into YAML;
- remove manually held Render values;
- broaden or narrow which services receive the group;
- split the group into additional groups;
- change application environment-variable requirements.

The current deployment has produced useful evidence that Dashboard-managed
values are necessary for the already-created Blueprint instance. Preserve that
working state.

Least-privilege decomposition may be evaluated separately with deployment
evidence; it must not be mixed into this rename and risk breaking the now-live
test environment.

## Scope

Owned repository:

```text
moda-interact-gateway
```

Expected implementation files:

```text
moda-interact-gateway/render.test.yaml
moda-interact-gateway/render.production.yaml
moda-interact-gateway/tests/validate-observability-config.sh
moda-interact-gateway/tests/validate-render-blueprints.sh
```

Only update a validator if it contains the old resource names.

Do not modify application repositories.

## Work Items

- [x] rename the test environment group declaration;
- [x] rename every test `fromGroup` reference;
- [x] rename the production environment group declaration;
- [x] rename every production `fromGroup` reference;
- [x] preserve test/production `DEPLOYMENT_ENVIRONMENT_NAME`;
- [x] preserve existing service-local variable declarations;
- [x] remove feature-oriented `moda-observability-*` group-name assumptions
      from gateway-owned validators;
- [x] add regression validation that the old group names are rejected;
- [x] prove no service references an environment's opposite config group;
- [x] run gateway validation;
- [x] record the clean Render Environment Group recreation requirement;
- [x] return to `review`.

## Acceptance Criteria

- [x] canonical test group is `moda-interact-test-config`;
- [x] canonical production group is `moda-interact-production-config`;
- [x] no canonical Blueprint service references `moda-observability-test`;
- [x] no canonical Blueprint service references `moda-observability-production`;
- [x] test services reference only `moda-interact-test-config`;
- [x] production services reference only `moda-interact-production-config`;
- [x] `DEPLOYMENT_ENVIRONMENT_NAME=test` remains test-only;
- [x] `DEPLOYMENT_ENVIRONMENT_NAME=production` remains production-only;
- [x] existing service-local secret/config declarations are not removed by this
      task;
- [x] no secret value is added to Git;
- [x] validators fail if the old feature-based names are restored;
- [x] the operator clean-recreation sequence is documented in the Completion Report.

## Validation

Inspect repository-local instructions/scripts first.

At minimum run:

```text
bash tests/run-tests.sh
bash tests/validate-observability-config.sh
bash tests/validate-render-blueprints.sh
git diff --check
```

Also search the gateway-owned canonical configuration:

```text
moda-observability-test
moda-observability-production
```

and prove neither remains as an environment-group resource/reference after the
change.

Do not treat historical architecture/task prose as runtime configuration for
this grep check.

The accepted SYSTEM-TEST-007 validator is expected to require a follow-on
system-test update because it currently encodes the old names. That update is
owned by `ARCH-002-SYSTEM-TEST-009`; do not modify the system-test repository
from this task.

## Live Follow-up

After architect acceptance, the developer should **not** look for or rename an
old Render Environment Group.

Instead:

```text
1. Create Render Environment Group:
      moda-interact-test-config

2. Re-enter the required test environment values in the Render Dashboard.

3. Verify:
      DEPLOYMENT_ENVIRONMENT_NAME=test

4. Publish/sync the accepted Blueprint.

5. Confirm the test services reference:
      moda-interact-test-config

6. Confirm no active Blueprint resource/reference uses:
      moda-observability-test

7. Verify all required test services deploy successfully.
```

The developer/user owns the Render Dashboard values and Blueprint publication.
The agent must not claim those live steps occurred.

## Non-Goals

- custom-domain implementation (`GATEWAY-009`);
- changing environment-variable values;
- secret rotation;
- least-privilege group decomposition;
- application changes;
- deployment execution;
- production load testing.

## Completion Report

### Status

Complete

### Files Changed

`moda-interact-gateway/render.test.yaml`; `moda-interact-gateway/render.production.yaml`; `moda-interact-gateway/tests/validate-render-blueprints.sh`.

### Work Completed

Renamed the test and production Render configuration groups to
`moda-interact-test-config` and `moda-interact-production-config`, including
all service references. Preserved environment identity and service-local
configuration declarations. Extended validation to reject legacy and opposite
environment group references.

Clean recreation after architect acceptance: create and populate
`moda-interact-test-config` in Render, then publish/sync the accepted Blueprint.
The production group name is `moda-interact-production-config`; production
values are not created or changed by this task.

### Validation Results

`bash tests/run-tests.sh` — passed, 49 checks.

`bash tests/validate-observability-config.sh` — passed.

`bash tests/validate-render-blueprints.sh` — passed.

Legacy-name regression check — passed: validator rejected restored
`moda-observability-test` with `missing canonical environment group`.

Canonical Blueprint search — passed: no legacy group names remain.

`git diff --check` — passed.

`cd ../moda-interact-system-test && npm run validate:arch002-production-readiness`
— failed because the local environment is missing the `yaml` module
(`MODULE_NOT_FOUND`).

### Deviations

The accepted system-test readiness validator could not run because its existing
local dependency installation is incomplete. No other repository was modified.

### Assumptions

The previous test Environment Group has been deleted. The new canonical test
Environment Group must be recreated and repopulated by the developer after
architect acceptance.

### Unresolved Issues

The new Render test Environment Group must be created and repopulated by the
developer/user before Blueprint publication.

### Architectural Concerns

Publishing the Blueprint before the developer recreates and repopulates the
new test Environment Group could create an empty configuration dependency and
regress deployment. Repository agent did not commit or push; implementation is
ready for developer commit/push after architect acceptance.

## Architect Review

### Review Status

Accepted

### Review Notes

Architect reviewed the actual post-task gateway workspace.

Accepted findings:

- `render.test.yaml` declares `moda-interact-test-config`;
- `render.production.yaml` declares `moda-interact-production-config`;
- all existing `fromGroup` references were renamed consistently;
- `DEPLOYMENT_ENVIRONMENT_NAME` remains correctly isolated by environment;
- existing service-local configuration declarations were preserved as required
  by GATEWAY-010;
- no secret value was introduced into source;
- gateway validation rejects the legacy group names and cross-environment group
  references;
- local architect execution confirmed
  `tests/validate-render-blueprints.sh` and
  `tests/validate-observability-config.sh` pass.

The architect container does not provide Docker, so the Docker-backed full
gateway suite could not be independently rerun here. The repository agent
reported 49 checks passing and `git diff --check` passing.

The remaining service-level `sync: false` model is intentionally not a
GATEWAY-010 defect. It is addressed by the newly promoted
`ARCH-002-GATEWAY-011`.

Coordination cleanup performed at acceptance: the stale task-body execution
state was reconciled with the authoritative frontmatter, and the gateway task
index was corrected to include GATEWAY-010.
