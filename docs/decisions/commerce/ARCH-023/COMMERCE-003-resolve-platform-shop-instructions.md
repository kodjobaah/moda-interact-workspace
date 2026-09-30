---
id: ARCH-023-COMMERCE-003
architecture_id: ARCH-023
title: Resolve additive Platform and Shop Instructions
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-DATABASE-001
  - ARCH-023-SHARED-002
  - ARCH-023-ADMIN-003
enables: []
created: 2026-09-29
updated: 2026-09-30
---

# Resolve additive Platform and Shop Instructions

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Replace Shop-overrides-Platform prompt resolution with deterministic additive canonical-English:

```text
Platform Instructions
+ optional Shop Instructions
```

while preserving independent model-selection behavior.

Expose those trusted resolved instructions through the existing Commerce MCP prompt mechanism using fixed reserved prompt names so the Background Commerce host can consume them before invoking the Shared runner.

At the same ownership boundary, remove Platform/Shop instruction mutation from Commerce Studio after ADMIN-003 is available. Capability-local prompt/tool/release authoring remains Commerce Studio-owned.

## Context

The Shared runner already provides the immutable Level-1 kernel and accepts trusted `hostInstructions` before response/capability instructions.

The production runner invocation currently lives in `moda-interact-background`, not in the Commerce service. Commerce therefore owns resolution/publication of the trusted Platform/Shop text, while a later bounded Background host task will fetch the two reserved MCP prompts and append them to trusted `hostInstructions` in order before `runCommerceTurn`.

This Commerce task does not edit Background.

## Scope

Primary authorized implementation surface:

```text
src/commerce/agent-configuration/effective-configuration.ts
src/studio/agent-configuration/effective-contracts.ts
src/studio/agent-configuration/effective-server-actions.ts

src/commerce/mcp/ports.ts
src/commerce/mcp/authorization.ts
src/commerce/mcp/service.ts
src/commerce/integration/backend.ts

src/studio/agent-configuration/agent-configuration-screen.tsx
src/studio/agent-configuration/platform-prompt-configuration.tsx
src/studio/agent-configuration/shop-agent-configuration.tsx
src/studio/agent-configuration/prompt-server-actions.ts

app/agent-configuration/page.tsx

tests/agent-configuration-effective.test.ts
tests/agent-configuration-screen-state.test.tsx
tests/agent-configuration-platform-prompt-ui.test.tsx
tests/agent-configuration-shop-ui.test.tsx
tests/agent-configuration-server-actions.test.ts
tests/mcp-authorization.test.ts
tests/mcp-service.test.ts
tests/agent-instructions-mcp.test.ts
```

Remove files/components only where they are exclusively obsolete mutation UI and no longer imported. Do not delete durable prompt services/tables needed by Admin/runtime.

## Out of Scope

- Admin Platform/Shop authoring.
- capability-local prompt editing.
- Tool authoring.
- model configuration editing.
- Merchant Knowledge lookup/bootstrap.
- Background host consumption.
- changing customer conversation language.
- translated Platform/Shop instruction rows.
- new private HTTP endpoint.

## Requirements

### R1 — preserve model-selection semantics exactly

Existing model behavior remains:

```text
valid enabled Shop model selection
  -> use Shop model

otherwise valid enabled Platform model
  -> use Platform model

otherwise
  -> model unavailable
```

This task changes prompt composition only.

### R2 — exact prompt resolution semantics

For current:

```text
environment
shop.id
```

resolve independently:

Platform:

```text
CommerceAgentConfiguration:
  environment = current
  scope = PLATFORM
  shopId = null
  activePromptRevisionId != null
```

Require active revision:

```text
status = PUBLISHED
prompt.scope = PLATFORM
prompt.shopId = null
promptText.trim() != ""
```

Shop:

```text
CommerceAgentConfiguration:
  environment = current
  scope = SHOP
  shopId = current shop
  activePromptRevisionId != null
```

When present require active revision:

```text
status = PUBLISHED
prompt.scope = SHOP
prompt.shopId = current shop id
promptText.trim() != ""
```

Platform is required.

Shop is optional.

Do not read Store Category template current text.
Do not translate either prompt.
Do not inspect customer conversation language.

### R3 — fail closed on ambiguous/invalid configuration

Within the current repeatable-read transaction:

```text
>1 PLATFORM configuration for environment -> UNAVAILABLE
>1 SHOP configuration for environment/shop -> UNAVAILABLE
invalid PLATFORM pointer/revision           -> UNAVAILABLE
present but invalid SHOP pointer/revision   -> UNAVAILABLE
```

Do not silently fall back from an invalid Shop configuration to Platform.

A genuinely absent Shop configuration/pointer means "no Shop Instructions" and is valid.

### R4 — replace single effective prompt contract

Replace:

```ts
EffectiveAgentConfiguration.prompt: EffectivePrompt
```

with exactly:

```ts
EffectiveAgentConfiguration.instructions: {
  platform: EffectivePrompt;
  shop: EffectivePrompt | null;
  ordered: Array<{
    source: "PLATFORM" | "SHOP";
    revisionId: string;
    text: string;
  }>;
}
```

`ordered` must be exactly:

```text
[PLATFORM]
or
[PLATFORM, SHOP]
```

and is derived from the same resolved revisions.

Do not retain the old Shop-overrides-Platform `prompt` field as a compatibility alias. ARCH-023 is pre-production for this behavior.

### R5 — include sourceTemplate edit provenance in effective prompt metadata

Extend effective revision metadata with:

```text
sourceTemplateEditVersion: number | null
```

in addition to existing:

```text
sourceTemplateId
```

This is provenance only; resolution never re-reads the template.

### R6 — fixed reserved MCP prompt names

Define exactly:

```text
commerce/platform-instructions
commerce/shop-instructions
```

These names are reserved and cannot collide with capability prompt names generated from release ids/capability keys/revisions.

Do not change existing capability prompt names.

### R7 — extend authorization snapshot with trusted instruction texts

Extend MCP authorization snapshot with:

```ts
trustedInstructions: {
  platform: {
    name: "commerce/platform-instructions";
    revisionId: string;
    text: string;
  };
  shop: {
    name: "commerce/shop-instructions";
    revisionId: string;
    text: string;
  } | null;
}
```

Populate it from R2/R3 for the authenticated:

```text
context.shopId
context.environment
```

inside the same server-side authorization data load.

Never accept these texts/revision ids from MCP request headers or client body.

### R8 — MCP `prompts/list`

Existing eligible capability prompts remain listed unchanged.

Additionally list:

```text
commerce/platform-instructions
```

always when authorization snapshot is valid, and:

```text
commerce/shop-instructions
```

only when a valid Shop instruction exists.

Each reserved prompt descriptor has bounded static description:

```text
Platform Instructions:
  Trusted published platform instructions for this CommerceAgent turn.

Shop Instructions:
  Trusted published shop-specific instructions for this CommerceAgent turn.
```

No prompt arguments.

### R9 — MCP `prompts/get`

For exact reserved names:

```text
commerce/platform-instructions
commerce/shop-instructions
```

return one text message containing exactly the resolved `text`.

No interpolation.

No customer-language transformation.

No template lookup.

No capability text concatenation.

Unknown/unavailable reserved prompt -> normal bounded MCP NOT_FOUND/UNAVAILABLE behavior.

Existing capability `prompts/get` remains unchanged.

### R10 — trusted instruction order for future host consumption

The authoritative order exported by Commerce is:

```text
Platform
Shop (when present)
```

A later Background host task MUST fetch these and append them after any true host-owned Level-2 instructions:

```text
Shared immutable kernel
true hostInstructions
Platform Instructions
Shop Instructions
release response instruction
capability-local prompts
```

This task must add a documentation/code comment next to the reserved prompt names identifying this required order.

Do not modify Background in this task.

### R11 — Commerce preview consumes the same resolver

Where Commerce preview has a concrete selected Shop and invokes the Shared runner, resolve the same trusted instruction bundle and pass:

```text
hostInstructions = [
  ...existing preview-only trusted host instructions,
  platform.text,
  ...(shop ? [shop.text] : [])
]
```

Do not copy runtime Tool results into this array.

Preview must fail closed when Platform Instructions are unavailable/invalid.

### R12 — runtime-data trust boundary remains Shared-owned

Consume the published Shared runner where:

```text
RUNTIME_DATA_AUTHORITY_INSTRUCTION
```

is immutable kernel instruction zero.

Do not duplicate/paraphrase that instruction in Commerce.

Tool/provider/Merchant Knowledge output remains Tool-result/message context only.

### R13 — retire Platform/Shop mutation from Commerce Studio

After ADMIN-003 exists, Commerce Studio must no longer provide mutations for:

```text
PLATFORM prompt DRAFT create/update/publish/activate
SHOP prompt DRAFT create/update/publish/activate
prompt-template category/template business authoring now owned by Admin
```

Remove/disable corresponding mutation controls and Server Actions from the Agent Configuration screen.

Do not delete the underlying Commerce prompt service/database persistence used by Admin/runtime.

### R14 — retain read-only effective context

The Agent Configuration page may retain:

```text
model configuration editing
read-only effective Platform Instructions metadata/text
read-only effective Shop Instructions metadata/text
source template provenance
```

Label them:

```text
Managed in Admin
```

Do not provide an edit/publish button/link that mutates them from Commerce Studio.

### R15 — capability authoring stays unchanged

Do not alter:

```text
Capability promptTemplate authoring
Capability Tool bindings
Tool authoring/testing/publication
Release authoring
```

Those remain Commerce Studio responsibilities.

### R16 — no Store Category runtime dependence

Runtime instruction resolution uses only:

```text
CommerceAgentConfiguration active prompt pointers
published CommerceAgentPromptRevision rows
```

It does NOT require:

```text
CommerceShopProfile.activeCategoryId
CommercePromptTemplateCategory
current template.promptText
ShopSettings.defaultLanguageTag
customer language
```

Store Category is authoring/provenance state, not a runtime instruction layer.

### R17 — exact tests

Tests must prove:

```text
Platform only -> ordered [PLATFORM]
Platform + Shop -> ordered [PLATFORM, SHOP]
Shop no longer replaces Platform
missing Platform -> UNAVAILABLE
invalid present Shop pointer -> UNAVAILABLE, not Platform fallback
absent Shop -> valid Platform-only
Shop model still overrides Platform model exactly as before
customer language does not alter instruction resolution
sourceTemplateEditVersion returned as provenance
MCP prompts/list includes reserved Platform and optional Shop names
MCP prompts/get returns exact published canonical-English text
reserved prompts tenant/environment scoped
capability prompts remain unchanged
preview order = preview host, Platform, Shop
Tool results never promoted into reserved prompts/hostInstructions
Studio mutation actions for Platform/Shop denied/absent
capability prompt/tool/release authoring regressions remain green
```

## Work Items

- [ ] Refactor effective configuration to additive Platform + optional Shop instructions.
- [ ] Extend effective metadata with template edit provenance.
- [ ] Add fixed reserved MCP prompts backed by trusted resolution.
- [ ] Integrate same instruction bundle into Commerce preview.
- [ ] Remove Platform/Shop mutation UI/actions from Studio.
- [ ] Retain model editing/read-only effective instruction view.
- [ ] Add MCP/effective/preview/Studio regression tests.
- [ ] Record Background host consumption as a required follow-up.

## Interfaces / Contracts

Commerce exposes two standard MCP prompt names:

```text
commerce/platform-instructions
commerce/shop-instructions
```

No new custom JSON resource/protocol is introduced.

A later Background task consumes these via the existing MCP `prompts/get` mechanism.

## Dependencies

- `ARCH-023-DATABASE-001`
- `ARCH-023-SHARED-002`
- `ARCH-023-ADMIN-003`

Resolved Shared release for this task: `@modainteract/moda-interact-shared@1.0.1`. Do not substitute a range, `latest`, workspace link or later release without architect reconciliation.

## Enables

A required bounded Background host-integration task that fetches the reserved trusted instruction prompts before `runCommerceTurn`.

## Acceptance Criteria

- [ ] Platform and Shop Instructions are additive and deterministic.
- [ ] Platform is required; Shop is optional.
- [ ] Model override semantics are unchanged.
- [ ] Standard MCP prompt mechanism exposes exact trusted texts tenant/environment-safely.
- [ ] Commerce preview uses the same order.
- [ ] Commerce Studio can no longer mutate Platform/Shop Instructions.
- [ ] Capability prompt/tool/release authoring remains intact.
- [ ] No translation/template/category runtime lookup is introduced.
- [ ] Runtime-data trust instruction remains Shared-owned.

## Validation

- [ ] effective configuration tests
- [ ] MCP authorization/service tests
- [ ] Commerce preview instruction-order tests
- [ ] Agent Configuration UI/action negative mutation tests
- [ ] Capability/tool/release authoring regression set
- [ ] `npm run typecheck`
- [ ] `npm run lint`
- [ ] `npm run build`
- [ ] `git diff --check`
- [ ] changed-file diagnostics clean

## Stop Condition

Set status to `review`, complete Completion Report, return to `moda_architect` and STOP.

Do not edit Background to consume the new reserved prompts.

## Implementation Notes

Using standard MCP prompts avoids a second private protocol. The two reserved prompt names are Commerce-owned runtime resources; capability prompt names and ordinary MCP tool/resource behavior remain unchanged.

The later Background host task is required for production runtime adoption because `runCommerceTurn` is currently invoked in `moda-interact-background`.

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
Pending.
### Reviewed Files
Pending.
### Validation Reviewed
Pending.
### Architecture Conformance
Pending.
### Follow-up
Pending.
