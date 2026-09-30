---
id: ARCH-021-SYSTEM-TEST-004
architecture_id: ARCH-021
title: Validate Feature-composed selected-shop Test Conversations
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 130
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-105
  - ARCH-021-COMMERCE-106
  - ARCH-021-COMMERCE-107
  - ARCH-021-COMMERCE-108
  - ARCH-021-COMMERCE-109
  - ARCH-021-GATEWAY-002
enables: []
created: 2026-09-29
updated: 2026-09-29
---

# Validate Feature-composed selected-shop Test Conversations

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Validate end to end that an authorised Studio user selects a shop and Features, receives every Capability under those Features, starts a CommerceAgent conversation frozen to the shop's effective Model/Prompt and exact Tool revisions, executes permitted Tools against that selected shop, and no longer encounters the superseded Release/fixture/Tool-test human Preview controls.

## Context

This is terminal Phase-6 architecture validation. It executes only after all Feature-composition, selected-shop configuration, UI, real Tool-execution, cleanup and Gateway credential-wiring tasks are architect-accepted Complete.

System-test validates the integrated product; it must not repair implementation defects.

## Scope

Create deterministic system-test fixtures/scenarios for at least:

```text
one selected shop with Shopify offline session
Platform effective model/prompt baseline
shop override case for either model or prompt
>= 2 Features
Feature A with >= 2 Capabilities
Feature B with >= 1 Capability
at least one unselected Feature/Capability/Tool
published Tool revisions
one Shopify Admin read Tool
one External read Tool where existing test topology supports it
```

Use the deployed/test provider configuration supplied by GATEWAY-002. Keep secrets outside test evidence.

## Out of Scope

- Product-code fixes.
- Production Background parity (Phase 7).
- Customer/WhatsApp delivery.
- Fabricating production entitlement rules into authoring Feature selection.
- Exposing credentials in test artifacts.

## Requirements

### R1 — selected Feature means every Capability

Select one Feature containing at least two Capabilities and prove the frozen Preview manifest contains both without a per-Capability selection step.

Select a second Feature and prove all of its Capabilities are added.

Prove a Capability belonging only to an unselected Feature is absent/not authorized.

### R2 — Feature order and Feature Behaviour are deterministic

Select Features in a known non-alphabetical order and prove the server composition preserves selected Feature order and deterministic Capability order.

Prove Feature Behaviour appears once per selected Feature, including a selected zero-Capability Feature if practical in the system fixture.

### R3 — exact Tool revision freeze

Start a conversation, then publish a newer revision of one selected Tool (or mutate the source fixture equivalently without changing the already-started conversation).

Prove the running conversation remains pinned to the original frozen revision while a new conversation may resolve the newer published revision.

### R4 — selected shop + effective Model/Prompt freeze

Prove conversation start freezes:

```text
selected shop identity/domain
effective Model source + exact providerModelId
effective published Prompt source + revision
```

Exercise both Platform fallback and a shop override across deterministic cases where practical.

After conversation start, change the effective Model/Prompt pointer and prove the existing conversation keeps the prior snapshot; a new conversation picks up the new effective configuration.

### R5 — real selected-shop Tool execution

Prove the CommerceAgent can call an allowed Shopify Admin read Tool and that the data originates from the selected test shop's real Shopify Admin execution boundary/offline session rather than synthetic `preview.myshopify.com` fixture generation.

Where External HTTP is present in the system-test topology, prove an allowed External Tool uses its server-owned connection boundary.

Prove an unselected Tool cannot be called even if it exists in another Feature/Release.

### R6 — Policy Operation missing-context behaviour is safe

If a selected Feature includes a Policy Operation that requires durable recovery/customer state not present in Test Conversations, prove it returns the canonical missing/unavailable result without creating fake recovery state or failing the whole service.

### R7 — multi-turn state is retained

Send at least two user turns in one Preview conversation and prove:

```text
same frozen composition/configuration is reused
prior conversation history is visible to the second turn
one active-run/busy semantics remain enforced
cancel/check-original-operation behaviour remains available
```

### R8 — old human Preview controls are absent

Prove the normal Test Conversations UI does not expose:

```text
Tool source
Release source
Tool test
Saved selection
Draft revisions
Fixture scenario
Model mode
```

Prove the Release composer no longer offers the old `Test conversation` handoff to `/preview`.

### R9 — secrets/customer delivery are isolated

Validate that Preview responses/UI/log evidence do not contain:

```text
COMMERCE_OPENAI_API_KEY
COMMERCE_GROQ_API_KEY
Shopify access token
Authorization headers
connection secrets
```

Prove Preview does not send WhatsApp/customer messages or create a production conversation grant/Background job merely by running this scenario.

### R10 — no authoring entitlement filter changes the explicit Feature set

Use a deterministic Feature/shop setup where a selected Feature is not part of the shop's normal current entitlement/preference when practical, and prove explicit Studio Feature composition is not silently altered by production eligibility filtering.

This validates authoring composition only; it does not change production entitlement behaviour.

## Work Items

- [ ] Build selected-shop + Model/Prompt + multi-Feature deterministic fixture setup.
- [ ] Validate all-Capabilities-per-selected-Feature and unselected-Feature exclusion.
- [ ] Validate deterministic selected Feature/Capability ordering and one Behaviour per Feature.
- [ ] Validate exact Tool revision freeze across later publication.
- [ ] Validate effective Model/Prompt freeze and new-conversation refresh.
- [ ] Validate real Shopify Admin selected-shop Tool execution.
- [ ] Validate External execution where supported by system topology.
- [ ] Validate safe Policy Operation missing-durable-context behaviour where applicable.
- [ ] Validate multi-turn history, busy, cancel/check semantics.
- [ ] Validate old human Preview controls/Release handoff are absent.
- [ ] Validate secret and customer-delivery isolation.
- [ ] Validate explicit Feature composition is not changed by production entitlement filtering.

## Interfaces / Contracts

Validates the integrated outputs of:

```text
ARCH-021-COMMERCE-105
ARCH-021-COMMERCE-106
ARCH-021-COMMERCE-107
ARCH-021-COMMERCE-108
ARCH-021-COMMERCE-109
ARCH-021-GATEWAY-002
```

System-test owns none of those implementation contracts.

## Dependencies

- ARCH-021-COMMERCE-105
- ARCH-021-COMMERCE-106
- ARCH-021-COMMERCE-107
- ARCH-021-COMMERCE-108
- ARCH-021-COMMERCE-109
- ARCH-021-GATEWAY-002

## Enables

None

## Acceptance Criteria

- [ ] Every Capability under each selected Feature is present; unselected Feature Capabilities are absent.
- [ ] No per-Capability opt-out exists in the human flow.
- [ ] Feature/Capability ordering and one Feature Behaviour per selected Feature are deterministic.
- [ ] Running conversation remains pinned to exact Tool revisions across later publication.
- [ ] Running conversation remains pinned to selected shop's effective Model/Prompt snapshot across later config changes.
- [ ] Shopify Admin execution reaches the selected shop's real offline-session boundary, not synthetic fixture data.
- [ ] External/Policy execution follows accepted production executor semantics where applicable.
- [ ] Unselected Tools are not authorized.
- [ ] Multi-turn history, busy/cancel/check semantics remain correct.
- [ ] Superseded Tool/Release/Fixture/Model-mode human controls and Release Preview handoff are absent.
- [ ] Preview exposes no provider/Shopify/connection secrets and sends no customer messages/production jobs.
- [ ] Explicit Feature composition is not silently filtered by production entitlement state.

## Validation

- [ ] integrated system-test scenario suite
- [ ] deployed Preview provider credential/configuration check without secret-value output
- [ ] database/Redis assertions for frozen composition/configuration where system harness exposes them
- [ ] selected-shop Shopify Admin fixture assertion
- [ ] negative unselected Tool/old UI/secret-leak assertions
- [ ] repository-required system-test lint/typecheck/build checks

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report and STOP. Return defects to the owning implementation repository/task; do not fix product code in system-test.

## Implementation Notes

This is terminal architecture validation. No implementation/publication/Gateway task may depend on SYSTEM-TEST-004.

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
