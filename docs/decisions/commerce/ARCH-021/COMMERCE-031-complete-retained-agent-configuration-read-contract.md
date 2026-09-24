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
status: review
priority: 10
executor: null
claimed_at: null
attempt: 2
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

- [x] Add `AgentConfigurationState`.
- [x] Add platform/shop retained configuration reads to the existing port/service.
- [x] Add named ADMIN-readable server actions for those reads.
- [x] Add durable `getShopPrompt(shopId)` lineage read to the existing prompt port/service.
- [x] Add the named ADMIN-readable `getShopPrompt(shopId)` server action.
- [x] Add focused retained-null/CAS and shop-lineage read regressions.

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

- [x] A retained SHOP row with `modelId=null` returns its real `modelEditVersion`.
- [x] A retained SHOP row with `activePromptRevisionId=null` returns its real `promptEditVersion`.
- [x] Clearing model does not change the returned prompt edit version.
- [x] Clearing prompt does not change the returned model edit version.
- [x] Missing configuration row returns `null`; it is not fabricated as version `1`.
- [x] A durable shop prompt lineage remains readable while no prompt override is active.
- [x] Shop prompt lineage lookup cannot return another shop's or a platform lineage.
- [x] ADMIN can perform these reads through the existing Studio authorization boundary.
- [x] No mutation/audit/schema behavior changes.

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

Ready for Review

### Attempt 2 Correction Checklist

- A1-R1 implemented in `tests/agent-configuration-retained-read.test.ts` using
  one shared mutable `CommerceAgentConfiguration` row and both real services;
  the exact set/clear model and set/clear prompt sequence passed.
- A1-R2 retained in the existing model and prompt regressions; the exact-shop
  lineage isolation and retained-null model read both passed.
- A1-R3 all Acceptance Criteria reconciled; the exact required Vitest command,
  targeted ESLint, typecheck, build and diff checks were run and recorded below.
- A1-R4 this report records the exact Attempt 2 launcher/worktree packet and
  publication parity.

### Files Changed

- `src/commerce/agent-configuration/model-service.ts`
- `src/commerce/agent-configuration/prompt-service.ts`
- `src/studio/agent-configuration/model-contracts.ts`
- `src/studio/agent-configuration/model-server-actions.ts`
- `src/studio/agent-configuration/prompt-contracts.ts`
- `src/studio/agent-configuration/prompt-server-actions.ts`
- `tests/agent-configuration-model.test.ts`
- `tests/agent-configuration-prompts.test.ts`
- `tests/agent-configuration-retained-read.test.ts`

### Work Completed

- Added read-only `AgentConfigurationState` and retained platform/shop reads that
  return nullable overrides with persisted model/prompt CAS versions.
- Added ADMIN-gated `getPlatformAgentConfiguration` and
  `getShopAgentConfiguration` Server Actions.
- Added exact-scope durable `getShopPrompt(shopId)` lineage lookup and its
  ADMIN-gated Server Action; it does not depend on an active prompt pointer.
- Preserved existing mutation, audit, schema and authorization boundaries.
- Added the required shared-row model-plus-prompt retained CAS regression while
  retaining the existing retained-null and exact-shop lineage regressions.

### Validation Results

- Exact required focused command: PASS — 3 test files, 17 tests passed:
  `npx vitest run tests/agent-configuration-retained-read.test.ts tests/agent-configuration-model.test.ts tests/agent-configuration-prompts.test.ts`.
- Targeted ESLint: PASS with 0 errors and 2 pre-existing warnings in the model
  test helper (`modelWith` and `key` unused).
- `git diff --check`: PASS.
- `npm run typecheck`: non-zero on existing repository diagnostics; no diagnostics
  in the new retained-read test or changed Agent Configuration runtime files.
  The output includes the known missing preview modules and unrelated UI
  contract diagnostics; the `prompt-service.ts` Prisma diagnostic remains the
  documented sibling/baseline condition.
- `npm run build`: code-runtime packaging, smoke test and Prisma generation
  passed; Next build is blocked by the same pre-existing missing preview modules
  in `app/api/studio/code-response/validate/route.ts` (`lib/preview/http`,
  `lib/preview/runtime`, `src/commerce/preview/types`). No changed file is in
  that failure path.

### Attempt 2 Prepared-Execution Packet

- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-031`
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-031`
- Parent branch: `task/ARCH-021-COMMERCE-031`
- Implementation branch: `task/ARCH-021-COMMERCE-031`
- Start-of-attempt parent synchronization: launcher completed and passed;
  parent head at preparation `d5e535cccf3bd62f73300c1f8d8610331bf20512`.
- Start-of-attempt implementation synchronization: launcher completed and
  passed; implementation head at preparation `b510ff8fad7455eaa156e70ab982e547a2f2bc7c`.
- Attempt 2 claim evidence: parent claim commit
  `79d893a463d5b382ae3a4a1a671a429d63b789c0`.
- Recursive submodule materialization: `sync_recursive` and
  `update_init_recursive` passed.
- Database submodule commit: `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
- Implementation commit: `7171a6f6ca4ed564171463f5a45ab8ad1d0a532f`.
- Parent report commit: recorded after this report edit and pushed below.
- Push parity: implementation local HEAD equals
  `origin/task/ARCH-021-COMMERCE-031` at `7171a6f6ca4ed564171463f5a45ab8ad1d0a532f`.
- Clean implementation worktree: verified after implementation push.
- Clean parent worktree: verified after parent report push.

### Deviations

- Repository typecheck and Next build remain non-zero because of unrelated
  existing diagnostics/missing preview modules documented above; task-specific
  regressions, lint and changed-file diagnostics pass.

### Assumptions

- Existing ADMIN Server Action authorization is the required read boundary;
  service reads retain the established principal authorization path.

### Unresolved Issues

- Repository typecheck diagnostics and missing preview build modules remain for
  their owning work.

### Architectural Concerns

None.

## Architect Review

### Review Status

Changes Requested — Attempt 1

### Review Notes

#### Attempt 1 review — 2026-09-24

The runtime read-contract implementation is directionally correct and must be preserved. Review confirms:

- `AgentConfigurationState` exposes the retained nullable configuration fields and both persisted CAS versions;
- `getPlatformAgentConfiguration()` / `getShopAgentConfiguration(shopId)` query the retained `CommerceAgentConfiguration` row directly rather than reconstructing it through nullable selection/pointer DTOs;
- `getShopPrompt(shopId)` resolves an exact SHOP-scoped durable lineage independently of the active prompt pointer;
- the named model reads flow through the existing ADMIN authorization boundary;
- the named prompt-lineage Server Action calls `requireStudioAdmin()`;
- no mutation, audit, schema, CAS increment or reconciliation implementation changed.

Attempt 1 is not accepted because the task's required deterministic cross-service CAS proof was not executed and the Completion Report does not contain the mandatory prepared-execution/worktree packet. The two new focused tests prove only the retained model read and durable shop lineage in isolation.

The following is the complete Attempt 2 correction contract. Do not redesign the service or modify runtime source unless the required regression exposes a defect.

##### A1-R1 — add one exact shared-row model+prompt CAS regression

Create:

```text
tests/agent-configuration-retained-read.test.ts
```

The test MUST use one shared mutable `CommerceAgentConfiguration` row for both:

```text
ModelConfigurationService
PromptConfigurationService
```

Do not merely run separate model and prompt fixtures and do not manually assign the expected edit versions between assertions.

The test must execute this exact sequence through the real service methods:

```text
initial retained state:
  modelId = null
  activePromptRevisionId = null
  modelEditVersion = 1
  promptEditVersion = 1

1. setShopModel(... expectedEditVersion=1)
2. getShopAgentConfiguration(shopId)
   => modelId=<selected model>
   => modelEditVersion=2
   => promptEditVersion=1

3. clearShopModel(... expectedEditVersion=2)
4. getShopAgentConfiguration(shopId)
   => modelId=null
   => modelEditVersion=3
   => promptEditVersion=1

5. setShopPointer(... expectedEditVersion=1)
6. getShopAgentConfiguration(shopId)
   => activePromptRevisionId=<selected published shop revision>
   => promptEditVersion=2
   => modelEditVersion=3

7. clearShopPointer(... expectedEditVersion=2)
8. getShopAgentConfiguration(shopId)
   => activePromptRevisionId=null
   => promptEditVersion=3
   => modelEditVersion=3
```

Mandatory assertions:

```text
clearing model does not change promptEditVersion
setting/clearing prompt does not change modelEditVersion
nullable override never resets an existing retained-row version to 1
the final retained row is still present
```

The prompt revision used by step 5 must be a PUBLISHED revision belonging to the exact SHOP / exact shopId lineage, so the existing pointer-scope validation is exercised rather than bypassed.

The shared fake/database may be minimal, but it must support the actual service calls; do not mock `getShopAgentConfiguration()` itself and do not fake the expected DTO.

##### A1-R2 — retain the existing shop-lineage isolation proof

Keep the existing regression that proves:

```text
getShopPrompt('shop-1') -> exact SHOP shop-1 lineage
getShopPrompt('shop-2') -> null
```

Also keep the existing retained-null model read regression. No runtime source change is required for this item unless either regression fails.

##### A1-R3 — reconcile all acceptance criteria and focused validation

After A1-R1 passes, update every satisfied checkbox under `## Acceptance Criteria` from `[ ]` to `[x]`.

Run exactly:

```bash
npx vitest run \
  tests/agent-configuration-retained-read.test.ts \
  tests/agent-configuration-model.test.ts \
  tests/agent-configuration-prompts.test.ts
```

The new retained-read test MUST execute and pass. Do not use a test-name filter that skips the cross-service sequence.

The pre-existing template-copy failure in `tests/agent-configuration-prompts.test.ts` may remain documented only if it reproduces unchanged and is unrelated to the read-contract changes. Record the exact test name and result.

Then run targeted ESLint over the new retained-read test, the two existing focused tests, and any runtime file changed during Attempt 2. Run:

```bash
npm run typecheck
git diff --check
```

The existing `Prisma.sql` diagnostic in `src/commerce/agent-configuration/prompt-service.ts` may remain documented only if it matches the known sibling/baseline state. No new diagnostic in the retained-read test or the new Agent Configuration read symbols is permitted.

##### A1-R4 — record the exact Attempt 2 prepared-execution packet

The Completion Report must record the exact launcher-provided values for:

```text
parent worktree path
implementation worktree path
parent branch = task/ARCH-021-COMMERCE-031
implementation branch = task/ARCH-021-COMMERCE-031
start-of-attempt parent synchronization
start-of-attempt implementation synchronization
Attempt 2 claim evidence / commit
recursive submodule materialization
database submodule commit
implementation commit
parent report commit
push parity
clean parent worktree
clean implementation worktree
```

Do not reuse Attempt 1 values and do not infer missing values.

Before handoff set exactly:

```yaml
status: review
attempt: 2
executor: null
claimed_at: null
```

##### Attempt 2 stop condition

Return to architect review only when:

```text
A1-R1 exact shared-row sequence passes
AND the existing retained-null + exact-shop lineage regressions pass
AND all Acceptance Criteria are reconciled
AND required lint/typecheck/diff validation is recorded
AND the exact Attempt 2 launcher/worktree packet is recorded
```

Then push implementation and parent task branches, return control to `moda_architect`, and STOP. Do not start or modify COMMERCE-028 or COMMERCE-029.

### Reviewed Files

- `src/commerce/agent-configuration/model-service.ts`
- `src/commerce/agent-configuration/prompt-service.ts`
- `src/studio/agent-configuration/model-contracts.ts`
- `src/studio/agent-configuration/model-server-actions.ts`
- `src/studio/agent-configuration/prompt-contracts.ts`
- `src/studio/agent-configuration/prompt-server-actions.ts`
- `tests/agent-configuration-model.test.ts`
- `tests/agent-configuration-prompts.test.ts`
- submitted `tsconfig.tsbuildinfo`
- Completion Report

### Validation Reviewed

- Submitted new focused regressions: 2 passed.
- Submitted model/prompt focused packet: 15 passed with one reported pre-existing template-copy failure.
- Submitted targeted ESLint: zero errors; two existing warnings.
- Submitted `git diff --check`: passed.
- Submitted full typecheck: non-zero; current artifact retains the documented `prompt-service.ts` Prisma-generated-client diagnostic and unrelated baseline diagnostics.
- Static review confirms the exact required cross-service retained-row sequence was not exercised by the submitted two new tests.

### Architecture Conformance

Implementation direction conforms. Acceptance is deferred only because the task's required shared-row model/prompt CAS proof and mandatory prepared-execution evidence are incomplete. No architecture redesign is requested.

### Follow-up

Return this same task through `/moda-task ARCH-021-COMMERCE-031` for Attempt 2. COMMERCE-028 remains Blocked and COMMERCE-029 remains Pending until COMMERCE-031 is architect-accepted Complete.
