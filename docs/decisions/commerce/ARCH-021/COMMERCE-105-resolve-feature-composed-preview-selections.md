---
id: ARCH-021-COMMERCE-105
architecture_id: ARCH-021
title: Superseded - Feature-composed Preview selections
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: superseded
priority: 100
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-09-29
updated: 2026-10-01
superseded_by: ARCH-024-COMMERCE-004
---

# Resolve Feature-composed Preview selections

> **Superseded 2026-10-01. Do not execute.** ARCH-024-COMMERCE-004 replaces this unstarted Feature-composition task.
> The remaining content is retained as historical design context only.

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Add one server-authoritative Preview selection kind in which Studio supplies **Feature IDs only**, and Commerce resolves each selected Feature to **all of its direct current Capabilities**, each Capability's current published Tool revision, and the Feature Behaviour prompt required by the CommerceAgent manifest.

## Context

The current Test Conversations implementation is source/release centred. `PreviewSelectionSchema` accepts `RELEASE` or `DRAFT`; the browser currently derives `capabilityIds` from a selected Release, and the DRAFT saved-selection adapter resolves Capabilities while writing `behaviourPrompt: ''` into each member.

The agreed Phase-6 product model is different:

```text
user selects Features
        |
        v
server resolves every Capability directly owned by each selected Feature
        |
        v
server resolves each Capability's current published Tool revision
        |
        v
server snapshots Feature Behaviour once per selected Feature
        |
        v
Preview manifest is frozen for the conversation
```

**Product decision:** selecting a Feature means **all Capabilities under that Feature**. There is no per-Capability checkbox/exclusion in Test Conversations.

This task owns only composition resolution and the frozen manifest inputs. Selected-shop model/prompt freezing is COMMERCE-106, the human-facing Feature picker is COMMERCE-107, selected-shop real Tool execution is COMMERCE-108, and deletion of old human-facing release/fixture/tool-test controls is COMMERCE-109.

## Scope

Primary implementation areas:

```text
src/commerce/preview/types.ts
src/commerce/integration/backend.ts
src/commerce/integration/preview/adapters.ts
```

Focused tests may include:

```text
tests/preview-service.test.ts
tests/preview-integration.test.ts
tests/backend-integration.test.ts
new/adjacent saved-selection tests where appropriate
```

Changes to another Commerce file are allowed only when mechanically required to carry the new typed selection/result through the existing Preview boundary. Do not implement the Feature-selection UI, effective model/prompt resolution, or live selected-shop Tool execution in this task.

## Out of Scope

- Feature-selection UI.
- Shop selection or shop authorization changes.
- Effective Agent Configuration/model/prompt freezing.
- LLM provider credential selection.
- Changing the selected Feature set according to billing plans, shop preferences, active release membership or runtime entitlement.
- Per-Capability selection in Preview.
- Real Shopify/External/Policy Tool execution.
- Removing legacy `RELEASE`/`DRAFT` Preview support; COMMERCE-109 owns that cutover after the replacement path is complete.
- Database migrations.
- Shared-package changes.

## Requirements

### R1 — add the exact Feature selection contract

Extend the Preview selection contract with this strict shape:

```ts
{
  kind: 'FEATURES';
  featureIds: string[];
}
```

Authoritative validation:

```text
1 <= featureIds.length <= 32
all IDs satisfy the existing saved-ID contract
duplicate Feature IDs are rejected
unknown Feature ID => NOT_FOUND
```

Do not accept browser-supplied `capabilityIds`, `toolIds`, `toolRevisionIds`, Feature Behaviour text or Tool definitions for `FEATURES`.

Keep existing `RELEASE` and `DRAFT` shapes temporarily for compatibility until COMMERCE-109. Do not broaden either legacy shape.

### R2 — Feature order is browser-selected order; Capability order is deterministic server order

The `featureIds` array order is semantically significant for deterministic authoring Preview composition and MUST be preserved exactly.

For each Feature, resolve its direct `CommerceCapability` rows in this exact order:

```text
displayName ASC
id ASC
```

Flatten Capabilities in:

```text
selected Feature 0 capabilities
selected Feature 1 capabilities
...
```

Assign manifest positions `0..N-1` in that flattened order.

Do not depend on database `IN (...)` result order.

### R3 — selected Feature means all direct Capabilities

For a selected Feature, include every direct current `CommerceCapability` row owned by that Feature.

Do **not** silently remove a Capability because of any of the following:

```text
Feature.active
Capability.enabled
Tool.enabled
shop Feature preference
subscription state
pricing-plan Feature membership
active Release membership
current production entitlement
```

Those are production/runtime eligibility concepts, not authoring composition selectors. The user chose the Feature and therefore the Preview composition contains all of its direct Capabilities.

A selected Feature with zero Capabilities is valid and remains represented by its Feature Behaviour entry.

### R4 — every selected Capability must resolve one current published Tool revision

For each selected Capability's `toolId`, resolve the current published Tool revision using exactly:

```text
status = PUBLISHED
revisionNumber DESC
id ASC
take 1
```

Required failure behaviour:

```text
Capability Tool identity missing      -> UNAVAILABLE
no published revision                 -> UNAVAILABLE
published definition fails schema     -> UNAVAILABLE
```

The whole `FEATURES` selection fails closed. Never omit only the invalid Capability and never substitute another Tool.

If two Capabilities reference the same Tool identity, both Capability members remain in the manifest but the Tool definition/revision snapshot is deduplicated by exact revision identity in the existing manner.

### R5 — Feature Behaviour is explicit and once per selected Feature

Extend the saved-selection result/Preview loader boundary so Feature Behaviour is represented explicitly as:

```ts
featureBehaviours: Array<{
  featureId: string;
  behaviourPrompt: string;
}>
```

For `FEATURES`, emit exactly one entry per selected Feature, including Features with zero Capabilities and Features with an empty Behaviour prompt.

Order `featureBehaviours` in exact `featureIds` input order.

Do not derive the Feature list from selected Capabilities: doing so would lose zero-Capability Features and can duplicate Feature Behaviour.

The Preview manifest must consume this explicit list. Any temporary fallback used for legacy `RELEASE`/`DRAFT` selection must be identified in code/tests as legacy and be removable by COMMERCE-109; do not create a second permanent Behaviour source.

### R6 — Feature-composed Preview uses the empty response contract

For `FEATURES`, use the canonical shared:

```text
EMPTY_RESPONSE_CONTRACT
```

and its canonical hash.

Do not borrow a response contract from the active Release, a selected Release or the browser.

### R7 — freeze exact Tool definitions and Feature Behaviour

`createPreviewBundleLoader()` must freeze into the existing Preview snapshot/manifest:

```text
exact selected Feature IDs/order
exact Capability IDs/keys/positions
exact Tool IDs
exact published Tool revision IDs
the parsed Tool definitions for those revisions
exact Feature Behaviour text once per selected Feature
```

After conversation creation, later Feature Behaviour edits, Capability additions/removals or Tool publication must not mutate that conversation's frozen composition.

This task does not yet freeze the selected shop/effective model/prompt; COMMERCE-106 owns those fields.

### R8 — no durable authoring write

Resolving a `FEATURES` selection is read-only. It must not:

```text
create/update Feature rows
create/update Capability rows
create/publish Tool revisions
create a Release
activate a Release
change shop Feature preferences
write billing/subscription state
```

Normal Preview Redis conversation state is outside this resolver and remains owned by PreviewService.

### R9 — preserve legacy Preview behaviour until cutover

Existing `RELEASE` and `DRAFT` tests must remain behaviourally intact except for the mechanical saved-selection-result addition required by R5.

Do not remove their browser UI or routes here. COMMERCE-109 is the explicit subtractive task.

## Work Items

- [ ] Add strict `FEATURES { featureIds }` validation to the Preview selection types.
- [ ] Extend the Commerce saved-selection input/result types for Feature composition and explicit Feature Behaviour.
- [ ] Implement server-side Feature lookup preserving selected Feature order.
- [ ] Resolve all direct Capabilities per selected Feature in `displayName ASC, id ASC` order.
- [ ] Resolve exactly one latest published Tool revision per Capability and fail the whole selection when unavailable.
- [ ] Emit explicit Feature Behaviour once per selected Feature, including zero-Capability Features.
- [ ] Use canonical `EMPTY_RESPONSE_CONTRACT` for Feature composition.
- [ ] Make the Preview bundle loader consume the explicit Feature Behaviour list and freeze exact revisions/definitions.
- [ ] Add regressions for duplicate/unknown Feature IDs, zero-Capability Feature, shared Tool, missing published Tool revision and post-freeze source changes.
- [ ] Prove no billing/entitlement/active-release filtering changes the selected composition.

## Interfaces / Contracts

New Commerce-internal Preview selection:

```ts
type PreviewSelection =
  | existing RELEASE
  | existing DRAFT
  | { kind: 'FEATURES'; featureIds: string[] };
```

Saved-selection output must expose one authoritative `featureBehaviours` list consumed by Preview manifest construction.

No cross-repository/public Shared contract changes are introduced.

## Dependencies

- ARCH-021-COMMERCE-092

## Enables

- ARCH-021-COMMERCE-106

COMMERCE-107 and COMMERCE-108 additionally depend on COMMERCE-106 and therefore become eligible only after the selected-shop configuration freeze boundary is complete.

## Acceptance Criteria

- [ ] `FEATURES` accepts Feature IDs only and rejects duplicate/empty/oversized/unknown selections deterministically.
- [ ] Each selected Feature contributes all direct Capabilities with no billing/shop/active-release eligibility filtering.
- [ ] Capability ordering is deterministic and matches the exact stated rule.
- [ ] Every selected Capability pins exactly one current published Tool revision or the whole selection fails `UNAVAILABLE`.
- [ ] A Feature with zero Capabilities remains present through its Feature Behaviour entry.
- [ ] Feature Behaviour appears exactly once per selected Feature and in selected Feature order.
- [ ] Shared Tool identities remain multiple Capability members but one exact frozen Tool definition/revision where applicable.
- [ ] Feature-composed Preview uses `EMPTY_RESPONSE_CONTRACT`.
- [ ] Later Feature/Capability/Tool changes do not mutate an already loaded/frozen composition.
- [ ] Existing RELEASE/DRAFT Preview behaviour remains available until COMMERCE-109.
- [ ] Resolution performs no durable authoring/business mutation.

## Validation

- [ ] focused Preview selection/bundle tests
- [ ] focused Prisma saved-selection/backend tests
- [ ] regression proving all direct Capabilities are included for selected Features
- [ ] regression proving no eligibility filtering is applied
- [ ] regression for zero-Capability Feature Behaviour
- [ ] regression for missing/invalid published Tool revision fail-closed behaviour
- [ ] regression for deterministic Feature/Capability ordering
- [ ] targeted ESLint
- [ ] repository typecheck or changed-file diagnostics per current baseline policy
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin COMMERCE-106/107/108.

## Implementation Notes

This is an authoring Preview composition boundary. Do not reuse `CommerceInspection` production eligibility filtering merely because it already knows about Feature preferences/plans. The selected Feature set is explicit user authoring input and must resolve literally to all direct Capabilities.

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
