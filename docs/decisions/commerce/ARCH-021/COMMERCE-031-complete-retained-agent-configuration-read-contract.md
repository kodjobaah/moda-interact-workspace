---
id: ARCH-021-COMMERCE-031
architecture_id: ARCH-021
title: Complete retained Agent Configuration read contract
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: copilot
claimed_at: 2026-09-24T16:44:16Z
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-025
enables:
  - ARCH-021-COMMERCE-028
created: 2026-09-24
updated: 2026-09-24
---

# Complete retained Agent Configuration read contract

## Architecture

Architecture ID:

ARCH-021

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Expose the retained nullable `CommerceAgentConfiguration` state and durable
shop-prompt lineage through the existing Commerce Agent Configuration service
boundary so selected-shop UI can preserve CAS across inheritance/clear without
querying Prisma directly.

## Context

DATABASE-002 deliberately retains one `CommerceAgentConfiguration` row when a shop
model or prompt override is cleared. COMMERCE-025 also defined reduced configuration
reads, but the current accepted implementation exposes model/prompt reads that return
`null` when the nullable override field is absent.

That means a UI cannot distinguish:

```text
no configuration row yet
```

from:

```text
retained configuration row exists
override is null
CAS edit version has advanced
```

COMMERCE-028 review also confirmed that the current prompt read surface cannot
rediscover a durable shop prompt lineage while the shop is inheriting the platform
prompt.

This task restores only those missing read semantics. Mutation, audit, reconciliation,
schema and UI behavior remain owned by their existing tasks.

## Scope

Primary files:

```text
src/commerce/agent-configuration/model-service.ts
src/commerce/agent-configuration/prompt-service.ts
src/studio/agent-configuration/model-contracts.ts
src/studio/agent-configuration/model-server-actions.ts
src/studio/agent-configuration/prompt-contracts.ts
src/studio/agent-configuration/prompt-server-actions.ts
tests/agent-configuration-model.test.ts
tests/agent-configuration-prompts.test.ts
tests/agent-configuration-reduced.test.ts
```

Use exact existing filenames where repository naming differs. Do not create a
parallel Agent Configuration service.

## Out of Scope

- React/Studio UI changes; those remain COMMERCE-028.
- Any Prisma schema or migration change.
- Mutation result changes.
- CAS increment rules.
- Audit receipt/reconciliation changes.
- Prompt draft/publish/set/clear behavior changes.
- Model catalogue changes.
- Generic replay/`unknown` behavior.
- Live model/provider execution.
- COMMERCE-029.

## Requirements

### R1. Add one canonical retained configuration DTO

In the existing Agent Configuration contract, define:

```ts
type AgentConfigurationState = {
  environment: ModelEnvironment;
  scope: 'PLATFORM' | 'SHOP';
  shopId: string | null;
  modelId: string | null;
  activePromptRevisionId: string | null;
  modelEditVersion: number;
  promptEditVersion: number;
};
```

The DTO is read-only and contains no credential, session, prompt text, model secret,
audit metadata or provider token.

### R2. Expose the reduced configuration reads originally required by COMMERCE-025

The existing service/port must expose:

```text
getPlatformAgentConfiguration
getShopAgentConfiguration
```

Semantics:

```text
row exists -> return AgentConfigurationState even when modelId is null
row exists -> return AgentConfigurationState even when activePromptRevisionId is null
row absent -> return null
```

`getShopAgentConfiguration(shopId)` must be scoped to the exact environment and shop.

The returned `modelEditVersion` and `promptEditVersion` are the persisted retained-row
values. Do not synthesize/reset them to `1` when an override is null.

Add named ADMIN-readable Server Actions with the same names. Reuse the existing
Studio authorization boundary; do not add a second auth mechanism.

Existing selection/pointer reads may remain for compatibility with already accepted
surfaces. This task does not remove them.

### R3. Restore durable shop prompt lineage lookup

The existing prompt service/port must expose:

```text
getShopPrompt(shopId)
```

returning the shop-scoped `PromptLineage | null` independently of whether
`CommerceAgentConfiguration.activePromptRevisionId` currently points at one of its
revisions.

Rules:

```text
exact SHOP scope + exact shopId only
durable lineage exists -> return it, including its revisions
no lineage -> null
active override absent -> lineage still discoverable
```

Add the named ADMIN-readable Server Action:

```text
getShopPrompt(shopId)
```

Do not infer a shop lineage from a platform prompt and do not create a lineage during
a read.

### R4. Preserve all mutation semantics

Do not change:

```text
set/clear model mutation inputs or results
set/clear prompt mutation inputs or results
modelEditVersion increment semantics
promptEditVersion increment semantics
first-write baseline
CommerceAuditEvent receipt behavior
reconcileAgentConfigurationOperation
DATABASE_UNAVAILABLE mapping
shared structured logging
```

This task is read-contract completion only.

## Work Items

- [ ] Add `AgentConfigurationState`.
- [ ] Add platform/shop retained configuration reads to the existing port/service.
- [ ] Add named ADMIN-readable server actions for those reads.
- [ ] Add durable `getShopPrompt(shopId)` lineage read to the existing prompt port/service.
- [ ] Add the named ADMIN-readable `getShopPrompt(shopId)` server action.
- [ ] Add focused retained-null/CAS and shop-lineage read regressions.

## Interfaces / Contracts

Consumes:

- DATABASE-002 retained `CommerceAgentConfiguration`;
- accepted COMMERCE-025 model/prompt service and authorization boundaries.

Produces:

```text
AgentConfigurationState
getPlatformAgentConfiguration()
getShopAgentConfiguration(shopId)
getShopPrompt(shopId)
```

for COMMERCE-028.

## Dependencies

- ARCH-021-COMMERCE-025

## Enables

- ARCH-021-COMMERCE-028

## Acceptance Criteria

- [ ] A retained SHOP row with `modelId=null` returns its real `modelEditVersion`.
- [ ] A retained SHOP row with `activePromptRevisionId=null` returns its real `promptEditVersion`.
- [ ] Clearing model does not change the returned prompt edit version.
- [ ] Clearing prompt does not change the returned model edit version.
- [ ] Missing configuration row returns `null`; it is not fabricated as version `1`.
- [ ] A durable shop prompt lineage remains readable while no prompt override is active.
- [ ] Shop prompt lineage lookup cannot return another shop's or a platform lineage.
- [ ] ADMIN can perform these reads through the existing Studio authorization boundary.
- [ ] No mutation/audit/schema behavior changes.

## Validation

Run focused unit/service tests covering all acceptance criteria.

At minimum include a deterministic retained-row sequence equivalent to:

```text
initial row versions: model=1 prompt=1
set model expected=1
read -> modelId=<id>, modelEditVersion=2, promptEditVersion=1
clear model expected=2
read -> modelId=null, modelEditVersion=3, promptEditVersion=1

set prompt expected=1
read -> activePromptRevisionId=<id>, promptEditVersion=2, modelEditVersion=3
clear prompt expected=2
read -> activePromptRevisionId=null, promptEditVersion=3, modelEditVersion=3
```

Also prove:

```text
shop prompt lineage exists
activePromptRevisionId is null
getShopPrompt(exactShop) still returns that lineage
getShopPrompt(otherShop) does not return it
```

Then run targeted ESLint over changed source/tests, `npm run typecheck` and
`git diff --check`.

There must be no task-owned TypeScript diagnostic in the files changed by this task.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are
complete:

```text
finish Completion Report
set status: review
clear executor / claimed_at
push implementation branch
push parent task branch
return control to moda_architect
STOP
```

Do not start COMMERCE-028 or COMMERCE-029.

## Implementation Notes

Prefer one direct `CommerceAgentConfiguration.findFirst`/equivalent read for the
retained configuration DTO. Do not reconstruct the DTO by combining nullable
selection/pointer results because those results intentionally disappear when an
override is absent.

`getShopPrompt(shopId)` is a durable lineage read, not an effective-configuration
resolver and not an active-pointer read.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

None.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

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

Return to `moda_architect` for review and STOP.
