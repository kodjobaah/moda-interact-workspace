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
status: review
priority: 60
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-023-DATABASE-001
  - ARCH-023-SHARED-002
  - ARCH-023-ADMIN-003
enables: []
created: 2026-09-29
updated: 2026-10-01
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

- [x] Refactor effective configuration to additive Platform + optional Shop instructions.
- [x] Extend effective metadata with template edit provenance.
- [x] Add fixed reserved MCP prompts backed by trusted resolution.
- [x] Integrate same instruction bundle into Commerce preview.
- [x] Remove Platform/Shop mutation UI/actions from Studio.
- [x] Retain model editing/read-only effective instruction view.
- [x] Add MCP/effective/preview/Studio regression tests.
- [x] Record Background host consumption as a required follow-up.

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

- [x] Platform and Shop Instructions are additive and deterministic.
- [x] Platform is required; Shop is optional.
- [x] Model override semantics are unchanged.
- [x] Standard MCP prompt mechanism exposes exact trusted texts tenant/environment-safely.
- [x] Commerce preview uses the same order.
- [x] Commerce Studio can no longer mutate Platform/Shop Instructions.
- [x] Capability prompt/tool/release authoring remains intact.
- [x] No translation/template/category runtime lookup is introduced.
- [x] Runtime-data trust instruction remains Shared-owned.

## Validation

- [x] effective configuration tests
- [x] MCP authorization/service tests
- [x] Commerce preview instruction-order tests
- [x] Agent Configuration UI/action negative mutation tests
- [x] Capability/tool/release authoring regression set
- [x] `npm run typecheck`
- [x] `npm run lint`
- [x] `npm run build`
- [x] `git diff --check`
- [x] changed-file diagnostics clean

## Stop Condition

Set status to `review`, complete Completion Report, return to `moda_architect` and STOP.

Do not edit Background to consume the new reserved prompts.

## Implementation Notes

Using standard MCP prompts avoids a second private protocol. The two reserved prompt names are Commerce-owned runtime resources; capability prompt names and ordinary MCP tool/resource behavior remain unchanged.

The later Background host task is required for production runtime adoption because `runCommerceTurn` is currently invoked in `moda-interact-background`.

## Completion Report

### Status
Ready for Review — Attempt 2
### Files Changed
Attempt 1 implementation is preserved without source changes in the dedicated `moda-interact-commerce` task worktree. It covers effective instruction resolution/contracts, MCP authorization and reserved prompts, Preview selection/revalidation, Agent Configuration read-only context, removal of Studio-only mutation adapters, and related tests. This Attempt 2 changes only this parent task report and lifecycle metadata.
### Work Completed
Attempt 1 implementation remains unchanged after the required synchronization. It provides deterministic additive Platform plus optional Shop instruction resolution. Platform is required; an invalid present Shop configuration fails closed. Existing Shop-over-Platform model selection semantics are preserved, and effective metadata includes source template edit-version provenance.

Exact resolved text is exposed through the fixed `commerce/platform-instructions` and `commerce/shop-instructions` MCP prompt names, scoped through the authenticated authorization snapshot. Capability prompt behavior and names remain unchanged.

Commerce Preview treats the selected shop ID only as a selector, revalidates it through server-side inspection for the authenticated principal, resolves the same trusted instruction bundle, freezes it for the conversation, and passes Preview safety, Platform, then optional Shop instructions to the runner.

Platform/Shop and template authoring mutations are removed from Commerce Studio while retaining model editing and a read-only effective-instructions/provenance view labeled “Managed in Admin”. Durable Commerce prompt/template services remain available to Admin/runtime.

Attempt 2 correction dispositions:
- Synchronization and start-of-attempt evidence: implemented by the prepared launcher; both canonical task worktrees were synchronized before any Attempt 2 source inspection or validation.
- Canonical worktree/provenance evidence: recorded below from the prepared launcher packet and final submission.
- Completion-report bookkeeping and refreshed validation inventory: implemented here; all Work Items, Acceptance Criteria and Validation checkboxes reflect the completed focused checks, the lint count is corrected, and the refreshed full-suite failures are listed below.
### Validation Results
Prepared launcher evidence (2026-09-30T23:36:50Z):

```text
canonical workspace: /Users/kwadwoadomafriyie/project/moda-interact-workspace
parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-023-COMMERCE-003
parent branch: task/ARCH-023-COMMERCE-003
implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-023-COMMERCE-003
implementation branch: task/ARCH-023-COMMERCE-003
shared/default checkout used for edits: no
previous task worktree reused: no
parent remote task fast-forward: not-needed
parent origin/main incorporated: yes; synchronized head 00e6e1afc53c7975450dd2ebc91c66b82990d9c4
implementation remote task fast-forward: not-needed
implementation origin/main incorporated: already-current; synchronized head 669e8ffd6c415b67b34d3dea34dd4e43e841f760
recursive submodule sync/update: passed / passed
database submodule: 6a8602e67d2308189af81ee0091e5189f1ffd71a (initialized, recursive)
claim: Attempt 2, copilot, committed and pushed as 95234fddef40bf37ddd2349debdcaff8d7f41bce
```

`npm run typecheck`: passed.

Focused task tests plus synchronized backend-bootstrap regressions: 19 files passed, 118 tests passed. An additional focused resolver/model UI/MCP/Preview run passed 5 files, 63 tests. The declared `test:arch021-tool-authoring-common` regression target passed 7 files, 84 tests. C20/PostgreSQL integration suites require disposable database/Redis targets and could not be fully exercised in this environment.

`npm run lint`: passed with 0 errors and 4 warnings (two React Hook dependency warnings in `src/studio/code-response/code-response-panel.tsx`; two unused declarations in `tests/agent-configuration-model.test.ts`).

`npm run build`: passed on retry, including manual/runtime packaging smoke steps, Prisma generation and Next production compilation. The build emitted the existing Nunjucks dynamic-dependency warning. Standalone runtime smoke invocations were intermittent under concurrent test/process load; this task does not change the runtime, and the complete build sequence passed.

`git diff --check`: passed. Changed-file diagnostics: no errors. Implementation worktree was clean after validation; recursive database submodule remained at the launcher-recorded commit.

Full `npm test`: not clean. Vitest summary reported 29 failed files, 121 passed, 4 skipped; 48 failed tests, 1,290 passed, 8 skipped. A structured reporter run listed these 26 unique failing file paths (including suite setup/collection failures):

```text
tests/admin-explorer.test.tsx
tests/agent-configuration-model-postgres.test.ts
tests/agent-configuration-model-ui.test.tsx
tests/agent-configuration-prompts-postgres.test.ts
tests/agent-configuration-shop-ui.test.tsx
tests/agent-contract-validation.test.ts
tests/auth-entrypoints.test.ts
tests/backend-postgres-rehearsal.test.ts
tests/c20-integration-fixture.test.ts
tests/code-response-processor.test.ts
tests/code-runtime-proof.test.ts
tests/discount-evaluator.test.ts
tests/discovery-limits.test.ts
tests/discovery-process.test.ts
tests/external-tools-ui.test.tsx
tests/health.test.ts
tests/local-external-mcp-diagnostic.test.ts
tests/merchant-knowledge-embedding.test.ts
tests/policy-operation-authoring-server-actions.test.ts
tests/policy-operation-result-template.test.ts
tests/preview-model-provider.test.ts
tests/readiness-docker.test.ts
tests/shop-execution-context.test.ts
tests/studio-integration-c20.test.ts
tests/studio-services-errors.test.ts
tests/studio-workspace.test.tsx
```

The structured reporter counted 47 failed suite results, 40 failed assertions, 1,298 passed assertions and 8 pending; its suite/assertion accounting differs from Vitest's terminal summary. Setup/collection failures include the PostgreSQL, C20 and local external-MCP integration suites. Remaining reported failures span Admin Explore, unrelated tool/release authoring, health/readiness, response/runtime, discount, discovery, and Studio workflows. `agent-configuration-model-ui.test.tsx` and `agent-configuration-shop-ui.test.tsx` appeared in the package run but passed in the focused reruns (including the 63-test rerun); no task-owned assertion failure reproduced in focused validation. The package-wide failures are retained for Architect attribution, not silently treated as passing.
### Deviations
No implementation-source changes were needed for Attempt 2. Work remained within Commerce and did not modify Background. C20/PostgreSQL integration validation was limited by the unavailable disposable test targets.
### Assumptions
The reserved MCP prompts are the production-facing Commerce contract; a separate bounded Background task must fetch them and append Platform then Shop after true host-owned Level-2 instructions before invoking `runCommerceTurn`.
### Unresolved Issues
The package-wide failures listed above remain for Architect attribution; the Shop/model UI failures did not reproduce in focused reruns. C20/PostgreSQL integration requires configured disposable database and Redis targets. Standalone packaged-runtime smoke results were intermittent, although the complete production build passed.
### Architectural Concerns
Production conversation execution remains Background-owned, so these resolved prompts are not consumed by the production runner until the required Background host-integration task is completed. No Background files were edited here.

## Architect Review

### Review Status
Changes Requested — Attempt 1

### Review Notes
No implementation-source correction is requested. The submitted Commerce implementation is architecturally conformant for this attempt: additive Platform + optional Shop resolution, fixed reserved MCP prompts, Preview ordering, Studio mutation retirement, model-selection preservation and the Background ownership boundary are all within the task contract. No Background files were changed.

Attempt 1 cannot be accepted because the task execution/report evidence does not satisfy the repository workflow contract:

1. **Start-of-attempt synchronization is not proven and the implementation branch is stale.** At review, `task/ARCH-023-COMMERCE-003` is five commits behind current `origin/main`; two of those mainline commits pre-date the recorded Attempt 1 claim. This is incompatible with the mandatory start-of-attempt rule requiring both canonical task worktrees to fetch, fast-forward their own remote task branch when applicable, and merge current `origin/main` before implementation work begins.
2. **Canonical worktree/provenance evidence is missing.** The Completion Report does not durably record the launcher-resolved parent and implementation worktree paths, branch identities, shared-checkout/non-reuse attestations, start-of-attempt synchronization outcomes for both repositories, recursive submodule preparation, or final submitted heads.
3. **Completion-report bookkeeping is incomplete.** The Work Items, Acceptance Criteria and Validation checkboxes must reflect the validation actually completed. The lint result is 0 errors / 4 warnings, not 5. The full-suite result must identify the failing files/suites (or a bounded categorized list from the refreshed run) and distinguish task-owned failures from unrelated baseline failures instead of only stating the aggregate 61-test failure count.

Submitted Attempt 1 checkpoints reviewed:

```text
implementation: c5f40a4e
parent report:  3218da44
```

### Reviewed Files
Reviewed the COMMERCE-003 task/completion report and the task-owned implementation surfaces for effective instruction resolution, MCP authorization/service reserved prompts, Preview host-instruction composition, Agent Configuration read-only presentation/mutation retirement, and focused regression coverage.

### Validation Reviewed
The following evidence is sufficient for code-level review and does not itself block acceptance:

```text
npm run typecheck                         PASS
focused Commerce tests                    101 PASS
additional MCP service tests               18 PASS
npm run lint                              PASS (0 errors, 4 warnings)
npm run build                             PASS
git diff --check                          PASS
changed-file diagnostics                  PASS
```

The package-wide suite is not clean (61 failed tests) and the C20 integration suite could not start without disposable PostgreSQL/Redis configuration. These results are not, by themselves, an Attempt 1 implementation blocker because the task-owned focused validation is green; Attempt 2 must rerun after synchronization and record the exact remaining full-suite failure set clearly enough for architect attribution.

### Architecture Conformance
No code-level architecture blocker was found. Platform and Shop Instructions are additive and deterministic, trusted text is exported through the reserved MCP prompt contract, Preview consumes the same order, model-selection semantics remain independent, and Platform/Shop authoring is retired from Commerce Studio without moving runtime ownership into Commerce.

The required Background host-consumption follow-up remains mandatory before final ARCH-023 system acceptance. It is an architect coordination follow-up, not an implementation-source correction for this task.

### Follow-up
Return the same task to `ready` with `attempt: 1`, `executor: null`, and `claimed_at: null`. Then start Attempt 2 only through:

```text
/moda-task ARCH-023-COMMERCE-003
```

The launcher must reuse the canonical dedicated task worktrees, synchronize both against their remote task refs and current `origin/main`, and record the exact synchronization packet in the Completion Report. Preserve the current implementation unless the required mainline merge or refreshed validation exposes a real regression. Do not make speculative source changes merely to create a new attempt.

Attempt 2 must also reconcile the completion checkboxes, record the correct lint warning count, enumerate/classify the refreshed full-suite failures, rerun the required focused/typecheck/lint/build/diff/diagnostic validation, clear the claim, set `status: review`, leave this Architect Review history unchanged, and return to `moda_architect`.
