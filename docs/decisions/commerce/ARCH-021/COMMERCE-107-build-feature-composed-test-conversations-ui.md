---
id: ARCH-021-COMMERCE-107
architecture_id: ARCH-021
title: Build Feature-composed Test Conversations UI
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 102
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-105
  - ARCH-021-COMMERCE-106
enables:
  - ARCH-021-COMMERCE-109
created: 2026-09-29
updated: 2026-09-29
---

# Build Feature-composed Test Conversations UI

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Replace the normal Test Conversations composition controls with a selected-shop, multi-Feature authoring UI where selecting a Feature means all Capabilities under that Feature, and start a multi-turn CommerceAgent Preview using Feature IDs only.

## Context

The current `/preview` page is headed "Synthetic preview" and presents Tool source, Release source, Tool test/Conversation tabs, Saved selection, Fixture scenario and Model mode. That UI exposes implementation/test concepts instead of the product concept being validated.

The intended user flow is:

```text
select Studio shop
        |
        v
inspect effective Model + Prompt
        |
        v
select one or more Features
        |
        v
see all Capabilities/Tools contained by those Features (read-only)
        |
        v
Start conversation
        |
        v
multi-turn CommerceAgent conversation with that frozen composition
```

COMMERCE-105 supplies the Feature-ID composition contract. COMMERCE-106 supplies selected-shop effective configuration freezing. This task owns only the human-facing replacement UI and browser payload. COMMERCE-109 performs final deletion of superseded UI/code after COMMERCE-108 establishes real Tool execution.

## Scope

Primary implementation areas:

```text
app/preview/page.tsx
src/studio/preview/preview-screen.tsx
src/studio/preview/client.ts
existing Feature/effective-configuration server action/read model imports
focused Preview page/screen/client tests
```

A small extracted Feature-selection component is allowed if it keeps `PreviewScreen` bounded and does not create a second state store.

## Out of Scope

- Resolving Feature IDs to Capabilities/Tool revisions server-side (C105).
- Model/prompt selection/freeze logic (C106).
- DefinitionExecutor/live Tool execution (C108).
- Final deletion of legacy fixture/release/tool-test implementation seams (C109).
- Feature/Capability editing from this screen.
- Per-Capability opt-out.
- Pricing-plan/private-plan eligibility filtering.
- Release creation/activation.

## Requirements

### R1 — page purpose and selected shop are explicit

The normal `/preview` human-facing page is Test Conversations, not generic fixture Preview.

Use user-facing semantics equivalent to:

```text
TEST CONVERSATIONS
Test CommerceAgent
Select Features and test the CommerceAgent for the selected shop.
```

The existing Studio Authoring shop selector remains the authoritative place to choose a shop.

Inside the Test Conversations content, show the resolved target shop at minimum as:

```text
Shop: <domain or label + domain>
```

If no validated shop is selected, Feature selection may still be inspected if useful, but **Start conversation must be disabled** with clear guidance to select an Authoring shop. Do not silently select the first shop.

### R2 — show effective Agent Configuration read-only

For a valid selected shop, load/display the effective configuration already resolved by C106/effective Agent Configuration APIs:

```text
Model
  displayName
  provider
  source: PLATFORM | SHOP

Prompt
  revision number/identity
  source: PLATFORM | SHOP
```

Do not display Prompt body by default merely to start a test; it may be shown in an existing bounded inspect/details affordance if already consistent with Studio patterns.

Never display provider credentials.

If effective Model or Prompt is unavailable, show the unavailable state and disable Start conversation.

### R3 — load the Feature authoring catalogue, not Releases/Tools

The Preview page must load the existing Feature authoring summaries needed to render:

```text
Feature id
Feature displayName/key
Feature Behaviour presence/text indicator as appropriate
Capability id/key/displayName/description
Capability Tool name/displayName
```

Do not require `listReleases()` or `listTools()` to build the new normal Conversation composer.

C109 owns deleting now-unused imports/legacy path after live execution lands; this task should stop using them in the supported UI.

### R4 — multi-select Features; no Capability selector

Render all available Features as an explicit multi-select control suitable for keyboard/mouse use.

For each Feature, render its Capabilities read-only beneath/alongside it so the author can see exactly what selecting the Feature means.

The UI must not render a checkbox/toggle/remove control for individual Capabilities.

Canonical rule:

```text
selected Feature => all of its Capabilities
```

A Feature with zero Capabilities remains selectable and must visibly show that it currently has no Capabilities.

Do not hide a Feature/Capability because of shop plan, subscription, shop Feature preference, Feature.active, Capability.enabled or Tool.enabled. The server remains authoritative for composition/failure.

### R5 — deterministic selected Feature order

Maintain selected Feature IDs in **first-selection order**:

```text
select A -> [A]
select C -> [A, C]
deselect A -> [C]
reselect A -> [C, A]
```

Do not sort selected IDs after selection. Send that exact order to the server so C105's deterministic composition rule is observable.

### R6 — exact start payload

For the supported Feature-composed human flow, `PreviewClient.startConversation` sends only:

```ts
{
  previewConversationId,
  shopId,
  selection: {
    kind: 'FEATURES',
    featureIds,
  },
}
```

Do not send:

```text
mode
fixtureId
releaseId
capabilityIds
toolRevisionIds
responseContract
model provider/model id
prompt/revision/text
shop domain
credentials
```

The browser is not the source of truth for those values.

### R7 — start admission

`Start conversation` is enabled iff all are true:

```text
validated selected shop exists
>= 1 Feature selected
effective Model available
effective Prompt available
no conversation-start request is in flight
no unresolved/unknown conversation-start outcome exists
```

Use the existing synchronous/single-flight interaction pattern where applicable so same-tick double activation cannot create multiple Preview conversation operations.

### R8 — freeze composition controls after successful start

After `startConversation` succeeds:

```text
shop target is fixed
selected Feature set/order is fixed
Feature selection controls disabled
new Start conversation disabled/hidden as appropriate
conversation message/send/cancel/check controls remain active
```

Do not let changing checkboxes mutate a running conversation.

`Reset conversation` must clear local conversation/run history and return to composition mode. It does not mutate Feature/Capability/Tool/configuration records.

### R9 — preserve multi-turn and uncertain-outcome UX

Retain the accepted Preview behaviour for:

```text
conversation history
send message
one active run
cancel
check original operation after uncertain outcome
history limits/status messaging
```

The replacement composer must not reimplement these mechanisms independently if the current `PreviewScreen` already owns them.

### R10 — normal human UI no longer renders old composition controls

Once this task is implemented, the normal Test Conversations screen must not render:

```text
Tool source
Release source
Tool test tab
Saved selection: Draft revisions / release
Fixture scenario
Model mode checkbox/toggle
```

The underlying legacy service/test code may remain temporarily and unreachable until COMMERCE-109. This task's UI tests must prove the old controls are absent from the supported screen.

## Work Items

- [ ] Change `/preview` normal data loading from Tool/Release sources to Feature authoring + effective selected-shop configuration.
- [ ] Present target shop and effective Model/Prompt read-only.
- [ ] Render Feature multi-selection with all Capabilities/Tools visible read-only and no per-Capability exclusion.
- [ ] Preserve first-selection Feature order exactly.
- [ ] Send the exact C106 Feature conversation-start payload.
- [ ] Gate start on shop + Feature + effective config + operation state.
- [ ] Freeze composition controls after successful start until Reset.
- [ ] Preserve existing multi-turn/send/cancel/check/reset semantics.
- [ ] Remove old Tool/Release/fixture/model controls from the supported rendered UI.
- [ ] Add keyboard/direct-selection and double-activation regressions.

## Interfaces / Contracts

Consumes:

```text
FeatureAuthoringSummary
EffectiveAgentConfiguration
COMMERCE-105 PreviewSelection { kind: 'FEATURES'; featureIds }
COMMERCE-106 Feature conversation-start request
```

The browser sends Feature IDs and selected shop ID only; all composition/configuration expansion remains server-authoritative.

## Dependencies

- ARCH-021-COMMERCE-105
- ARCH-021-COMMERCE-106

## Enables

- ARCH-021-COMMERCE-109

COMMERCE-108 executes independently in parallel after C106 and must also be Complete before C109.

## Acceptance Criteria

- [ ] Test Conversations clearly identifies the validated target shop.
- [ ] Effective Model/Prompt identity/source are visible read-only and unavailable config blocks Start.
- [ ] Features, not Releases/Tools, are the normal composition selector.
- [ ] Selecting a Feature visually represents all its Capabilities and offers no per-Capability opt-out.
- [ ] Feature selection order follows the exact first-selection/deselect/reselect rule.
- [ ] Start payload contains only previewConversationId, shopId and ordered Feature IDs.
- [ ] Start is impossible without selected shop, selected Feature and effective Model/Prompt.
- [ ] Same-tick repeated Start activation admits at most one operation.
- [ ] Running conversation composition cannot be changed until Reset.
- [ ] Multi-turn/send/cancel/check/reset behaviour remains functional.
- [ ] Tool source, Release source, Tool test, Saved selection, Fixture scenario and Model mode are absent from the supported UI.

## Validation

- [ ] focused `preview-screen` UI tests
- [ ] `/preview` page data-loading tests
- [ ] Feature selection order tests
- [ ] exact start-payload test
- [ ] zero-Capability Feature presentation test
- [ ] selected-shop/effective-config unavailable tests
- [ ] repeated Start activation test
- [ ] locked-after-start/reset tests
- [ ] negative assertions that legacy controls are not rendered
- [ ] targeted ESLint
- [ ] repository typecheck or changed-file diagnostics per baseline policy
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin COMMERCE-109.

## Implementation Notes

Do not create a second global/session state store for Feature composition. This is local Preview-composer state until conversation start; the server/Preview state store owns the frozen execution snapshot after start.

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
