---
id: ARCH-021-COMMERCE-106
architecture_id: ARCH-021
title: Freeze selected-shop CommerceAgent configuration in Preview
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 101
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-010
  - ARCH-021-COMMERCE-105
enables:
  - ARCH-021-COMMERCE-107
  - ARCH-021-COMMERCE-108
created: 2026-09-29
updated: 2026-09-29
---

# Freeze selected-shop CommerceAgent configuration in Preview

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Make a Feature-composed Preview conversation require one server-authoritatively validated Studio shop, resolve that shop's effective CommerceAgent model and published prompt, and freeze the exact shop/model/prompt identity and prompt text into the Preview conversation before the first turn.

## Context

The current Preview route resolves a Studio shop for page chrome, but Conversation Preview does not carry that shop into `PreviewService`. Runtime identity is currently synthetic (`preview-<admin>`, `preview.myshopify.com`), `FIXTURE`/`MODEL` is a browser choice, and MODEL mode uses one environment-wide `COMMERCE_PREVIEW_PROVIDER`/`COMMERCE_PREVIEW_MODEL`/`COMMERCE_PREVIEW_API_KEY` tuple.

ARCH-021 already has a server-authoritative effective configuration resolver:

```text
selected shop
  -> shop override when present
  -> otherwise Platform default
  -> exact enabled Model catalogue entry
  -> exact published Prompt revision
```

Phase 6 requires Preview to run the same effective configuration the user is intending to test. The browser may identify the shop and Features; it must not nominate a model provider/model ID/prompt revision or send credentials.

## Scope

Primary implementation areas:

```text
src/commerce/preview/types.ts
src/commerce/preview/service.ts
src/commerce/integration/preview/adapters.ts
src/commerce/integration/preview/model-provider.ts
src/commerce/agent-configuration/effective-configuration.ts (consume/reuse; change only if a narrow reusable port is required)
lib/preview/runtime.ts
lib/server/config.ts
app/api/studio/preview/conversations/route.ts only if request wiring requires it
```

Focused tests include existing Preview/effective-configuration/config suites and new selected-shop freeze regressions.

## Out of Scope

- Feature picker UI (COMMERCE-107).
- Mapping Feature IDs to Capabilities/Tools (COMMERCE-105).
- Executing Tools against the real shop (COMMERCE-108).
- Gateway/Render secret wiring (ARCH-021-GATEWAY-002).
- Production Background grant changes (later Phase 7).
- Database migrations.
- Browser-supplied provider/model/prompt selection.
- Automatic provider fallback.

## Requirements

### R1 — Feature-composed conversation start requires selected shop ID

Introduce/extend the Feature Preview conversation-start contract so the supported replacement path accepts exactly:

```ts
{
  previewConversationId: string;
  shopId: string;
  selection: {
    kind: 'FEATURES';
    featureIds: string[];
  };
}
```

Do not require or accept these legacy human-choice fields on the `FEATURES` start shape:

```text
mode
fixtureId
releaseId
capabilityIds
toolRevisionIds
model provider/model ID
prompt ID/revision/text
shopDomain
access token/API key
```

Legacy RELEASE/DRAFT request parsing may remain temporarily for old tests/UI until COMMERCE-109; keep the `FEATURES` shape strict and separately testable.

### R2 — re-resolve shop server-side; never trust page/browser shop metadata

At conversation creation, resolve `shopId` through the existing server-authoritative Studio shop execution-context boundary.

Required failures:

```text
missing/invalid shopId        -> INVALID_INPUT
unknown/stale shop            -> NOT_FOUND or canonical translated not-found
unauthorised principal        -> DENIED
```

Use the resolved server value for frozen:

```text
shop.id
shop.domain
shop.label
shop.plan
```

Never accept those fields from the browser.

### R3 — resolve effective model/prompt at conversation creation

Using the validated shop and current Preview environment, call/reuse the existing `resolveEffectiveConfiguration` semantics.

Conversation creation must fail closed with `UNAVAILABLE` unless **both** are available:

```text
effective.model.source in { PLATFORM, SHOP }
effective.model.model != null

effective.prompt.source in { PLATFORM, SHOP }
effective.prompt.revision != null
```

No fallback to a Preview-only default model or empty prompt is permitted.

### R4 — freeze exact effective Agent Configuration

Extend the Preview frozen conversation state with a bounded typed snapshot containing at minimum:

```text
shop:
  id
  domain
  label
  plan

model:
  source
  environment
  selectionEditVersion
  model.id
  model.provider              OPENAI | GROQ
  model.providerModelId
  model.displayName
  model.editVersion

prompt:
  source
  environment
  pointerEditVersion
  prompt.id
  prompt.scope
  prompt.shopId
  revision.id
  revision.promptId
  revision.revisionNumber
  revision.editVersion
  revision.contentHash
  revision.promptText
```

The snapshot MUST NOT contain provider API keys, Shopify access tokens, auth headers or other credentials.

After `startConversation` claims the conversation, later model selection changes or Prompt publication/pointer changes must not affect that conversation.

### R5 — provider execution is chosen from the frozen Model, not old Preview defaults

Replace the supported `FEATURES` model invocation decision with the frozen model's:

```text
provider
providerModelId
```

Server-only credential inputs are:

```text
COMMERCE_OPENAI_API_KEY
COMMERCE_GROQ_API_KEY
```

Rules:

```text
OPENAI -> COMMERCE_OPENAI_API_KEY only
GROQ   -> COMMERCE_GROQ_API_KEY only
missing required provider credential -> UNAVAILABLE
unknown provider -> UNAVAILABLE
no cross-provider fallback
```

Keep `COMMERCE_PREVIEW_ENABLED` as the Preview kill switch. A disabled Preview remains unavailable regardless of model selection.

Do not expose secret values through frozen state, API responses, logs or errors.

Gateway wiring for those names and removal of obsolete Blueprint Preview provider/model/key variables is ARCH-021-GATEWAY-002 after Commerce cutover.

### R6 — global prompt enters the runner exactly once

For `FEATURES` Preview turns, build runner `hostInstructions` in this exact semantic order:

```text
1. immutable Preview safety instruction(s)
2. frozen effective global Prompt revision text
```

The shared runner then appends its existing response-contract and Feature Behaviour instructions according to its canonical order.

Do not also add the same global prompt through `PreviewPrompt[]`, Feature Behaviour, model context or browser fields.

Retain the safety invariant that Preview must not send outbound customer messages or perform unapproved mutations.

### R7 — selected-shop conversation identity replaces synthetic shop identity

For the `FEATURES` conversation bundle/grant/turn, use the frozen selected shop ID/domain as the authoring execution context rather than:

```text
preview-<adminId>
preview.myshopify.com
```

Preview-specific grant/conversation IDs may remain synthetic/ephemeral where they are identifiers rather than merchant identity.

Do not fabricate a production CheckoutRecovery row/ID. Real Policy Operation behaviour when no such durable entity exists is handled by COMMERCE-108.

### R8 — Feature-composed Preview does not use fixture-derived conversation context

The supported `FEATURES` path must not require a Fixture selection to start.

Initial language may be the existing explicit null language state:

```ts
{ tag: null, source: null }
```

unless the existing selected-shop context provides a real authoritative language field already in scope. Do not invent a language.

Runner context for this task should contain only bounded Preview telemetry/execution metadata available without synthetic fixture business data. COMMERCE-108 owns real Tool calls, not synthetic product/recovery context.

Legacy fixture-backed paths may remain temporarily for automated/legacy tests until COMMERCE-109.

### R9 — preserve Preview idempotency, history and uncertain-outcome semantics

The new shop/configuration fields are part of the canonical conversation-start payload hash/frozen state.

Existing guarantees remain:

```text
same previewConversationId + same payload => replay/idempotent success
same previewConversationId + different shop/features => ID_CONFLICT
multi-turn history bounds unchanged
one active run/conversation busy semantics unchanged
cancel semantics unchanged
unknown-outcome reconciliation unchanged
```

### R10 — no database persistence of Preview configuration

Do not add a database migration/table for Preview. Frozen configuration remains in the bounded Preview state store with the existing Preview lifetime/cleanup model.

## Work Items

- [ ] Add strict Feature conversation-start shape with required `shopId` and no fixture/model selector fields.
- [ ] Add a server-side shop/effective-configuration resolver dependency to Preview runtime.
- [ ] Freeze bounded selected-shop/model/prompt metadata + prompt text into conversation state.
- [ ] Fail closed when selected shop/effective model/effective prompt is unavailable.
- [ ] Select Preview LLM provider/model from the frozen model entry.
- [ ] Add server-only Commerce OpenAI/Groq credential lookup with no provider fallback.
- [ ] Add the frozen global Prompt exactly once after immutable Preview safety instructions.
- [ ] Remove fixture dependence from the supported `FEATURES` conversation path while retaining legacy/test seams until C109.
- [ ] Preserve payload-hash/idempotency/history/cancel/unknown-outcome semantics.
- [ ] Add regressions proving configuration changes after start do not affect the running conversation.
- [ ] Add secret-leak negative coverage.

## Interfaces / Contracts

Consumes:

```text
ARCH-021-COMMERCE-105 FEATURES selection
existing Studio shop execution context
existing EffectiveAgentConfiguration resolution
```

Introduces server-only configuration names consumed by Commerce:

```text
COMMERCE_OPENAI_API_KEY
COMMERCE_GROQ_API_KEY
```

Deployment wiring is owned by `ARCH-021-GATEWAY-002`; do not edit Gateway from this task.

## Dependencies

- ARCH-021-COMMERCE-010
- ARCH-021-COMMERCE-105

## Enables

- ARCH-021-COMMERCE-107
- ARCH-021-COMMERCE-108

## Acceptance Criteria

- [ ] Supported Feature Preview cannot start without one server-resolved selected shop.
- [ ] Browser cannot select/send the effective provider/model/prompt revision or any provider credential.
- [ ] Conversation creation freezes exact effective model and exact published prompt revision/text.
- [ ] Missing effective model or prompt fails `UNAVAILABLE`; there is no Preview default fallback.
- [ ] OPENAI/GROQ invocation uses only the frozen selected provider/model and matching server-only credential.
- [ ] Global Prompt is supplied to the runner exactly once and after immutable Preview safety instructions.
- [ ] Frozen selected-shop identity replaces synthetic merchant identity for the Feature path.
- [ ] Feature path starts without Fixture/Model-mode input or synthetic Fixture business context.
- [ ] Later shop config/model/prompt changes do not change a running Preview conversation.
- [ ] Existing idempotency/history/cancel/unknown-outcome guarantees remain intact.
- [ ] No secret/API key is persisted in Preview state, returned to browser or logged.
- [ ] No database migration is introduced.

## Validation

- [ ] focused PreviewService conversation-start/turn tests
- [ ] effective-configuration freeze tests with SHOP and PLATFORM sources
- [ ] OPENAI provider/model selection + missing-credential test
- [ ] GROQ provider/model selection + missing-credential test
- [ ] no-fallback regression
- [ ] frozen-after-start model/prompt mutation regression
- [ ] payload-hash shop/Feature conflict regression
- [ ] secret-leak negative assertions
- [ ] targeted ESLint
- [ ] repository typecheck or changed-file diagnostics per baseline policy
- [ ] `git diff --check`

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin COMMERCE-107/108.

## Implementation Notes

Do not add a second effective-configuration algorithm inside Preview. Reuse the accepted Agent Configuration resolution semantics so Studio tests the model/prompt that the selected shop would actually inherit at conversation creation.

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
