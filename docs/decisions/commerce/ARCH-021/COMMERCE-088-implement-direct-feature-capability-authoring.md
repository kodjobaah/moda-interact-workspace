---
id: ARCH-021-COMMERCE-088
architecture_id: ARCH-021
title: Implement direct Feature capability authoring backend
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 90
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-021-DATABASE-003
enables:
  - ARCH-021-COMMERCE-089
  - ARCH-021-COMMERCE-090
created: 2026-09-29
updated: 2026-09-29
---

# Implement direct Feature capability authoring backend

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Expose a narrow Commerce Studio backend for reading Admin-owned Features, updating one Feature behaviour prompt, and atomically creating a Capability only when a Feature and existing Tool have been selected.

## Context

The current Studio service creates a durable Capability shell first, then routes the user into a Capability revision editor to create a draft containing prompt/configuration/multiple Tool bindings. Reads and writes are routed through the broad publication snapshot/transaction aggregate.

The new authoring model is direct:

```text
Feature                read-only Admin identity
Feature behaviour      one current Commerce prompt
Capability             metadata + exactly one Feature + exactly one Tool
```

Before final Capability creation, authoring state belongs in the browser. The server action must therefore represent one final atomic create operation rather than a staged identity/draft lifecycle.

## Scope

Primary areas include:

```text
database/                                      # consume accepted DATABASE-003 gitlink only
src/commerce/integration/studio/services.ts
src/commerce/integration/backend/* persistence needed for narrow writes
src/studio/contracts.ts or a new feature-domain contract module
src/studio/server-actions.ts / server-services.ts or new feature-domain actions
src/studio/testing/in-memory-studio-services.ts only as required by current tests
focused Studio/lifecycle/persistence tests
```

New feature-specific contracts/actions should be extracted into `src/studio/features/` rather than adding more Capability authoring logic to the generic Studio contract if practical.

## Out of Scope

- Feature creation/editing; Admin owns `billing.Feature`.
- Billing plan, subscription or merchant entitlement authoring.
- React Feature/Capability flow (COMMERCE-090/091).
- Release creation/runtime manifest changes (COMMERCE-089).
- Background/Shared contract changes.
- Permanent retention of old Capability draft/revision APIs; final removal is COMMERCE-092.

## Requirements

### R1 — consume the accepted simplified database schema

Update the Commerce database submodule/gitlink to the accepted DATABASE-003 implementation through the normal task workflow. Do not edit the nested database schema in this task.

### R2 — Feature reads come directly from the Feature/Commerce configuration model

Expose a Feature read model containing the information needed by the new UI, including:

```text
Feature id/key/display name/active state
current Feature behaviour prompt + editVersion (blank/default when absent)
current Capabilities
for each Capability: identity/display metadata/enabled/tool identity/tool display metadata
```

Do not calculate `DRAFT_ONLY` / capability revision publication status.

Do not read billing plan/subscription eligibility merely to render or author this screen.

### R3 — add one CAS Feature behaviour mutation

Expose a narrow authenticated mutation for the current Feature `behaviourPrompt`.

- An absent configuration is represented as blank text and may be created with the documented initial CAS value.
- A present configuration uses monotonic `editVersion` CAS.
- The supported lifecycle does not delete/recreate the configuration row.
- The operation is audited with the existing immutable audit/operation-reconciliation convention.

No Feature behaviour draft/revision/publication API is introduced.

### R4 — add one atomic `createFeatureCapability` mutation

The final create input is conceptually:

```ts
{
  operationId: string;
  reason: string;
  featureId: string;
  key: string;
  displayName: string;
  description: string;
  toolId: string;
}
```

The mutation must validate server-side that:

1. the Feature exists;
2. the Tool exists and is enabled;
3. the Tool has at least one PUBLISHED revision at create time;
4. the Capability key is available;
5. the actor is authorised.

Then one narrow database transaction creates the Capability and immutable audit/replay receipt. There is no preceding persistent shell, draft, Tool-binding array or capability revision.

### R5 — exact replay and ambiguous-result reconciliation

Follow the accepted narrow Tool-creation mutation pattern: same `operationId` + same payload reconciles to the original successful result; conflicting replay fails deterministically; an unknown client result may be reconciled without creating a second Capability.

Do not route this operation through a read-all/write-all publication state transaction merely because the legacy lifecycle does.

### R6 — one Tool per Capability in authoring contracts

The new contract exposes `toolId`, not `toolBindings[]`, and does not expose Tool revision selection. Release creation owns exact published Tool revision pinning.

### R7 — removed concepts do not appear in the new API

The new Feature/Capability authoring contracts must not contain:

```text
selectionBinding
type: BASE | FEATURE | RECOVERY_POLICY
CapabilityRevision
promptTemplate per Capability
configuration
maxSearchResults
maxRecommendations
toolBindings[]
```

### R8 — bound legacy API exposure until final cleanup

If old Capability APIs must remain temporarily so the pre-refactor UI compiles before COMMERCE-090/091, keep them isolated as legacy-only paths. New Feature authoring must not call them. Do not create adapters that implement the new create operation by chaining old `createCapability` + `createDraft` + `publishRevision` calls.

COMMERCE-092 owns complete deletion once all consumers have moved.

## Work Items

- [x] Consume DATABASE-003 schema through the Commerce database submodule.
- [x] Define the Feature-centric read contract with nested direct Capabilities/Tools.
- [x] Implement direct Feature reads without publication snapshots or billing/subscription eligibility reads.
- [x] Implement CAS Feature behaviour update/upsert with audit/replay semantics.
- [x] Implement atomic narrow `createFeatureCapability` persistence.
- [x] Validate Feature, enabled Tool, at least one published Tool revision and unique Capability key on final create.
- [x] Return the created Capability directly without rereading the whole publication aggregate.
- [x] Add exact replay/conflicting replay/ambiguous-result reconciliation tests.
- [x] Add focused authorization and concurrency tests.
- [x] Keep any temporary legacy Capability API clearly isolated for COMMERCE-092 removal.

## Interfaces / Contracts

Produces backend contracts consumed by COMMERCE-090/091 and release/runtime work:

```text
list/get Feature configuration
updateFeatureBehaviour
createFeatureCapability
```

The final names may follow established Studio feature-domain naming, but semantics above are fixed.

## Dependencies

- ARCH-021-DATABASE-003

## Enables

- ARCH-021-COMMERCE-089
- ARCH-021-COMMERCE-090

## Acceptance Criteria

- [x] Feature reads show direct Capability -> Tool relationships and no revision state.
- [x] Feature authoring reads/writes do not consult subscription/billing-plan eligibility.
- [x] Feature behaviour uses one current CAS row, not drafts/revisions.
- [x] Capability creation performs exactly one durable create transaction after final submission.
- [x] No Capability row exists when a would-be authoring session is abandoned before final create.
- [x] One Capability stores one Tool identity; no Tool revision is selected by the authoring mutation.
- [x] Tool identity may be reused by multiple Capabilities.
- [x] Final server validation rejects missing Feature, missing/disabled Tool, Tool with no published revision and duplicate Capability key.
- [x] Exact replay returns the original result without duplicate rows/audits.
- [x] New contracts contain none of the removed Capability concepts listed in R7.

## Validation

- [x] focused Feature/Capability service tests
- [x] focused narrow persistence/replay tests
- [x] focused authorization tests
- [x] `npm run lint -- <changed files>` or repository-supported targeted ESLint equivalent
- [x] changed-file TypeScript diagnostics / `npm run typecheck` evidence according to repository baseline policy
- [x] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report and STOP. Do not implement the Feature UI or release/runtime migration.

## Implementation Notes

Model this after the successful narrow initial Tool creation boundary, not after the legacy whole-publication Capability transaction.

## Completion Report

### Status

Ready for review

### Files Changed

- `src/studio/features/contracts.ts`
- `src/studio/features/persistence.ts`
- `src/studio/features/services.ts`
- `src/studio/features/reconciliation-server-actions.ts`
- `src/studio/server-actions.ts`
- `tests/feature-authoring.test.ts`
- `tests/feature-operation-reconciliation.test.ts`

### Work Completed

- Consumed the prepared DATABASE-003 submodule at `e9fb60221f1532205650154dfff2aadb6270b14c`; no nested database schema changes were made.
- Added direct list/get Feature reads with current behaviour prompt/editVersion and nested Capability-to-Tool identity/display data. The new read model does not expose Capability revision or publication state and does not query subscription/billing eligibility.
- Added authenticated `updateFeatureBehaviour` using initial version 0 for an absent configuration, monotonic CAS updates, immutable audit receipts, exact replay, and stale/conflicting replay results.
- Added authenticated atomic `createFeatureCapability` with Feature, enabled Tool, published Tool revision, and unique key validation; writes one direct Feature/Tool Capability plus audit receipt in one narrow transaction and returns the created result without a publication snapshot.
- Added exact-result operation reconciliation for Feature behaviour and Capability creation. Kept existing generic Capability lifecycle APIs available for their current consumers; the new Feature APIs do not call them.
- Added coverage for direct reads, initial and concurrent CAS, authorization, missing/disabled/unpublished identities, duplicate keys, same-Tool reuse, exact replay, conflicting replay, and reconciliation.
- Implementation commits: `47b1c4a` (`Implement direct Feature capability authoring backend`) and `be6a71e` (`Avoid redundant revision read in Capability result`).

### Validation Results

- `npx vitest run tests/feature-authoring.test.ts tests/feature-operation-reconciliation.test.ts tests/studio-integration.test.ts tests/tool-authoring-server-actions.test.ts`: passed, 31 tests across 4 files. The dedicated C088 pair also passed 12 tests.
- Focused ESLint on all changed source and test files: passed with no warnings.
- Pylance changed-file diagnostics: no errors in any changed file.
- `git diff --check`: passed.
- New Feature API retired-concept scan (`selectionBinding`, `CapabilityRevision`, per-Capability prompt/configuration, capability limits, `toolBindings`): no matches.
- `npm run typecheck`: non-zero with 144 diagnostics in 15 files, all outside C088 changed files. The failures include legacy Commerce references incompatible with the accepted DATABASE-003 schema and unrelated existing tests. The workspace baseline document's historical 48-error count does not match this observed run; no baseline documentation was changed.
- Live PostgreSQL rehearsal was not run because the repository rehearsal requires a developer-confirmed isolated `DATABASE_URL`; the available environment was not assumed disposable.

### Deviations

The existing generic `StudioServices` legacy Capability surface remains for current UI consumers, as allowed by R8; the new feature-domain contract and actions are isolated under `src/studio/features/` for COMMERCE-090/091 consumption.

### Assumptions

An absent `CommerceFeatureConfiguration` is treated as blank at version 0. Its first successful mutation creates that initial row and advances it to version 1 in the same transaction, consistent with the accepted schema's default version and no-delete lifecycle.

### Unresolved Issues

Repository-wide TypeScript validation remains blocked by 144 diagnostics outside this task's changed files; remediation is outside C088 scope.

### Architectural Concerns

No C088-specific architecture deviation identified. Production database behavior should still be exercised against an isolated PostgreSQL target during the owning integration validation.

## Architect Review

### Review Status

Changes Requested

### Review Notes

Attempt 1 implementation is technically and architecturally conformant. No C088 implementation-source or test change is required at this stage.

The new Feature-domain API is correctly isolated under `src/studio/features/`. Feature reads consume the direct Feature -> Capability -> Tool model and do not derive Capability revision/publication state or consult billing/subscription eligibility. Feature behaviour uses one current `CommerceFeatureConfiguration` row with version-0 creation semantics, monotonic CAS, immutable audit receipt/replay, and no draft/revision lifecycle.

`createFeatureCapability` is a narrow atomic transaction. It validates Feature existence, Tool existence/enabled state, presence of at least one PUBLISHED Tool revision and Capability-key uniqueness, then creates one direct Capability plus immutable audit/replay receipt. The new contract carries one `toolId`, not Tool bindings or Tool-revision selection. Same-operation exact replay returns the original result and conflicting reuse fails without duplicate Capability rows. Legacy Capability APIs remain separate for existing consumers and are not used as adapters by the new Feature path.

The focused unit/service/replay/authorization evidence is sufficient for the implementation-level review. The unrun PostgreSQL rehearsal is not a C088 acceptance blocker because it is not listed as required task Validation and requires a developer-confirmed isolated `DATABASE_URL`; the Completion Report records this limitation transparently. The production PostgreSQL behavior should still be exercised during the owning integration/system validation.

#### A1-R1 — record mandatory task-worktree and synchronization evidence

The Completion Report does not contain the durable physical-isolation/start-of-attempt evidence required by `docs/agent-worktree-isolation-policy.md`.

For Attempt 2, recover the original launcher/preparation packet if retained and record the actual values. If the original packet is unavailable, say so explicitly and perform a fresh canonical-worktree reconciliation verification rather than inventing historical outcomes.

Record at minimum:

```text
Physical worktree isolation:
  canonical workspace root: <actual launcher/current verified path>
  parent worktree: <actual path>
  parent branch: task/ARCH-021-COMMERCE-088
  implementation worktree: <actual path>
  implementation branch: task/ARCH-021-COMMERCE-088
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current

Recursive implementation submodule:
  database path: <actual path>
  database commit: e9fb60221f1532205650154dfff2aadb6270b14c
  clean/current for task worktree: yes|no

Published task state:
  implementation commits:
    - 47b1c4a
    - be6a71e
  implementation remote branch: origin/task/ARCH-021-COMMERCE-088
  implementation pushed: yes

  parent task-report commit: <actual commit>
  parent remote branch: origin/task/ARCH-021-COMMERCE-088
  parent pushed: yes

  merged to implementation main: no
  merged to workspace main: no
```

If the original synchronization packet is unavailable, replace the four historical synchronization lines with an explicitly labelled current reconciliation block covering local/remote task equality and `origin/main` ancestry/state for both repositories.

#### A1-R2 — reconcile cleared-claim metadata

The submitted task is in `review` but still records an active executor and claim timestamp. Reconcile the durable task metadata so the returned task is reclaimable:

```text
status: ready
executor: null
claimed_at: null
```

No implementation-source change is required for A1-R2.

After recording A1-R1/A1-R2, rerun only the task-required focused validation needed to substantiate the canonical-worktree record, return the task to `review`, clear the claim, and STOP.

### Reviewed Files

- `src/studio/features/contracts.ts`
- `src/studio/features/persistence.ts`
- `src/studio/features/services.ts`
- `src/studio/features/reconciliation-server-actions.ts`
- `src/studio/server-actions.ts`
- `tests/feature-authoring.test.ts`
- `tests/feature-operation-reconciliation.test.ts`
- `database/prisma/schema.prisma` at the prepared DATABASE-003 submodule state
- `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

### Validation Reviewed

- Focused Feature/Capability packet: 31/31 passed across four files.
- Dedicated C088 Feature tests: 12 passed.
- Focused ESLint over all changed files: passed with no warnings.
- Changed-file/Pylance diagnostics: no errors.
- New Feature API retired-concept scan: no prohibited R7 concepts found.
- `git diff --check`: passed.
- Repository `npm run typecheck`: 144 diagnostics in 15 files, all outside the C088 changed-file set.
- Live PostgreSQL rehearsal: not run because no developer-confirmed isolated `DATABASE_URL` was available; not a required C088 validation item.

### Architecture Conformance

Conforms at the implementation level.

C088 establishes the direct Feature authoring backend required by ARCH-021: Admin-owned Features remain identity/read sources, Commerce owns one current Feature behaviour configuration, direct Capabilities bind exactly one Feature to exactly one Tool, authoring creates no durable shell before final create, and release/runtime Tool-revision pinning remains outside this task.

Acceptance is withheld only until the mandatory task-worktree/synchronization and cleared-claim evidence is durably recorded.

### Follow-up

Return the same task through `/moda-task` for Attempt 2. Reconcile A1-R1 and A1-R2 in the Completion Report/task metadata, rerun the necessary focused validation from the canonical implementation worktree, return to `review`, clear the claim, and STOP.

Do not start COMMERCE-089 or COMMERCE-090 until C088 is architect-accepted Complete.
