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
attempt: 0
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

- [ ] Consume DATABASE-003 schema through the Commerce database submodule.
- [ ] Define the Feature-centric read contract with nested direct Capabilities/Tools.
- [ ] Implement direct Feature reads without publication snapshots or billing/subscription eligibility reads.
- [ ] Implement CAS Feature behaviour update/upsert with audit/replay semantics.
- [ ] Implement atomic narrow `createFeatureCapability` persistence.
- [ ] Validate Feature, enabled Tool, at least one published Tool revision and unique Capability key on final create.
- [ ] Return the created Capability directly without rereading the whole publication aggregate.
- [ ] Add exact replay/conflicting replay/ambiguous-result reconciliation tests.
- [ ] Add focused authorization and concurrency tests.
- [ ] Keep any temporary legacy Capability API clearly isolated for COMMERCE-092 removal.

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

- [ ] Feature reads show direct Capability -> Tool relationships and no revision state.
- [ ] Feature authoring reads/writes do not consult subscription/billing-plan eligibility.
- [ ] Feature behaviour uses one current CAS row, not drafts/revisions.
- [ ] Capability creation performs exactly one durable create transaction after final submission.
- [ ] No Capability row exists when a would-be authoring session is abandoned before final create.
- [ ] One Capability stores one Tool identity; no Tool revision is selected by the authoring mutation.
- [ ] Tool identity may be reused by multiple Capabilities.
- [ ] Final server validation rejects missing Feature, missing/disabled Tool, Tool with no published revision and duplicate Capability key.
- [ ] Exact replay returns the original result without duplicate rows/audits.
- [ ] New contracts contain none of the removed Capability concepts listed in R7.

## Validation

- [ ] focused Feature/Capability service tests
- [ ] focused narrow persistence/replay tests
- [ ] focused authorization tests
- [ ] `npm run lint -- <changed files>` or repository-supported targeted ESLint equivalent
- [ ] changed-file TypeScript diagnostics / `npm run typecheck` evidence according to repository baseline policy
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report and STOP. Do not implement the Feature UI or release/runtime migration.

## Implementation Notes

Model this after the successful narrow initial Tool creation boundary, not after the legacy whole-publication Capability transaction.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
