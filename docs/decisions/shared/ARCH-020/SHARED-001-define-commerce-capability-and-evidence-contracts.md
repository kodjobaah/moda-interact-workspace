---
id: ARCH-020-SHARED-001
architecture_id: ARCH-020
title: Implement and publish commerce contracts and reusable runner
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-016-SHARED-001
enables:
  - ARCH-020-BACKGROUND-001
  - ARCH-020-COMMERCE-003
  - ARCH-020-COMMERCE-004
  - ARCH-020-COMMERCE-009
  - ARCH-020-COMMERCE-011
  - ARCH-020-SHOPIFY-001
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
---

# Implement and publish commerce contracts and reusable runner

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Implement, validate and publish one installable Shared package version containing the Commerce contracts and reusable runner. Downstream consumers require the verified published version before this task is Complete.

## Context

Merchant-selected capabilities should drive WhatsApp CommerceAgent behaviour through a separate Next.js MCP server with a team-only Studio. Production conversation admission, ordering, model hosting and delivery remain in Background. This is a pre-production breaking rollout, with no implicit permission to delete durable data.

Task definition is on local workspace main by the developer's explicit 2026-09-20 review request. It is not a claim, task-branch materialisation or implementation approval. All execution fields remain unclaimed.

## Scope

src/commerce schemas, pure selection helpers, ./commerce/runner implementation, package exports, focused tests, release metadata, publication and clean registry installation verification.

## Out of Scope

Other repositories' implementation, unrelated refactoring, automatic execution of enabled tasks, live deployment, main integration/push and changes to billing prices/merchant entitlements. No cart/order/discount mutation, WhatsApp sending from Commerce, arbitrary executable code or arbitrary-host HTTP endpoints; C14 validated read-only GraphQL definitions are explicitly permitted. No duplicate discount catalogue/merchant configuration system. Shared indexes and architecture reconciliation remain architect-owned.

## Requirements

Follow the parent architecture's tenant/policy/revision contracts and the assigned logical owner. Preserve unrelated changes. Read repository-local AGENTS.md if present. Commerce consumes the canonical database through its nested database/ Git submodule; schema and migrations belong to moda_database. For consumers, use actual accepted and published dependency revisions, not copied task snapshots or hypothetical versions.

### Runner implementation

Follow the parent architecture's tenant/policy/revision contracts and the assigned logical owner. Preserve unrelated changes. Read repository-local AGENTS.md if present. Commerce consumes the canonical database through its nested database/ Git submodule; schema and migrations belong to moda_database. For consumers, use actual accepted and published dependency revisions, not copied task snapshots or hypothetical versions.

## Work Items

- [ ] Extend CommerceManifest with required C16 responseContract/hash and CommerceFinalResponse with details. Export strict definition/envelope types and generic pure subset/hash validation contracts. Keep release-specific properties out of compiled types; document fixed envelope versus configurable details.

- [ ] Export the separate bounded structural draft definition schema and strict publishable definition schema from C14; draft-save acceptance is not execution/publication approval.

- [ ] Export C14 strict reusable tool identity/revision/binding/grant-provenance schemas and discriminated SHOPIFY_STOREFRONT_QUERY/POLICY_OPERATION execution definitions; no fixed MCP tool-name enum. Export the schema/compiler interface consumed by Commerce, not a provider process in Shared.
- [ ] Implement exact capability/tool hash inputs and deduplication: same tool revision across selected capabilities produces one entry with sorted original capabilityKeys; conflicting revisions reject. Allow zero remote tools for conversation_core.
- [ ] Keep Admin feature keys dynamic and existing effective-billing semantics; no mandatory product_search feature or tool.

- [ ] Define/export CommerceToolDefinitionSchema, the bounded C14 input-schema/mapping/template validators, typed operation descriptors, and schema-to-MCP descriptor conversion. Separate definitionVersion from executor operationVersion. Preserve the existing WhatsApp schemas.

- [ ] Define versioned manifest, capability binding, release identity, authenticated turn identity, basket, tool input/output, evidence and final-response schemas with bounded examples. Distinguish resolve-only assertions with no release from execute assertions bound to the persisted release pin.
- [ ] Require checkoutRecoveryId on authenticated turn identity and validate real non-sentinel recovery references; no nullable/standalone recovery context is supported. Define names and schemas for the six v1 commerce tools; distinguish missing basket, unknown facts, unsupported offers, denied permissions and transient provider errors.
- [ ] Implement a pure capability/feature selection helper that accepts authoritative facts supplied by repository adapters; preserve existing active feature/plan and opt-in semantics.
- [ ] Provide fixed/base/feature/recovery-policy bindings and decimal money/currency/freshness evidence; exclude secrets and model-controlled shop identity.
- [ ] Export ./commerce with supported schema/runner compatibility rules and fixture manifests; publish both exports together through this task’s release stage.

- [ ] Define CommerceConversationGrantSchema with unique conversation identity, initialInboundVersion, pinned release, selectedCapabilityKeys and exact C14 grantedTools identities/revisions and original capabilityKeys provenance. Execute claims include grantId plus current inboundVersion. Add answerKind=ANSWER|REFER_TO_STORE and referralReason=null|INSUFFICIENT_TOOLS|UNVERIFIABLE_FACTS|TOOL_UNAVAILABLE|TOOL_REVOKED; enforce ANSWER requires null and referral requires a reason.

### Runner implementation

- [ ] Implement C16 dynamic finalResponse schema construction and pinned definition validation/instruction composition. Fixed envelope rules remain reusable; no detail-name switch or Commerce fetch. Cover R01–R05/R08/R11/R12.

- [ ] Implement C6.1 reusable fixed grounding, language and finalResponse rules. Accept host-owned recovery instructions/context separately from editable capability prompts; Shared must not load recovery records or own a checkout-status policy. Enforce instruction ordering, original-grant restrictions and the exact null-pair/final-output validation contract.

- [ ] Accept arbitrary C14 tool descriptors/results without a six-tool switch. Empty remote-tool grants can still produce a grounded store referral through host-local finalResponse. Generic query facts never create discount Evidence.

- [ ] Consume discovered database-definition descriptors generically; no switch on MCP tool name. Keep structured result facts/evidence authoritative and treat renderedText as untrusted presentation.

- [ ] Accept injected model, validated prompt bundle, tools, clock and cancellation signal; keep domain lookup and provider selection in callers.
- [ ] Compose immutable platform instructions and capability prompts deterministically; retain language and structured finalResponse rules.
- [ ] Enforce parent step/tool/output/deadline ceilings; remove the current forced-final-after-one-product-search constraint in the reusable loop.
- [ ] Validate final results and referenced offer evidence; return bounded typed errors without customer messages or secrets in exception text.
- [ ] Expose runner version for preview/publication compatibility; support deterministic fixture models without live network calls.

- [ ] Run with the immutable conversation grant and expose only originally granted tools still authorised now. Never dynamically acquire a new tool to answer a question. Require factual answers to be supported by granted-tool results or trusted recovery facts; missing/unknown/unsupported/unavailable information produces REFER_TO_STORE. Greetings/clarification need no fabricated facts. Keep these platform instructions outside editable capability prompts.

### Publication and consumer verification

- [ ] After implementing and passing the combined contracts/runner checks, select the compatible package version through the existing repository release policy. No package version is invented in this definition.
- [ ] Publish the exact validated source through the existing release mechanism. Record source commit, version, registry, tarball URL/integrity and both ./commerce and ./commerce/runner exports. If the repository requires reviewed/integrated source before release, keep this same task open through that checkpoint; do not create another publication task or bypass required review.
- [ ] Install that exact version from the intended registry in a clean temporary consumer, without workspace links or provider/database credentials. Import both public entry points and execute a schema validation plus scripted runner finalResponse smoke case. Record commands and results. A local pack alone is not publication evidence.
- [ ] Treat missing exports or registry/install failures as unresolved work in this task. Fix scoped defects and rerun affected checks. Do not mark Complete or promote downstream consumers until the published artifact is verified and architect acceptance is recorded.

## Interfaces / Contracts

Read the binding schema contract in docs/decisions/database/ARCH-020/DATABASE-001-persist-capability-releases-and-turn-revision-pins.md. Its exact field names/types, enum values, JSON shapes/bounds, immutable release membership and selectedCapabilityKeys/grantedTools conversation grants are the persistence contract; do not invent alternative representations. Shared APIs serialize dates as ISO strings and map database environment enums to lower case.

Canonical @modainteract/moda-interact-shared/commerce; existing billing and recovery-policy exports.

### Implementation guidance

Apply binding contracts **C14–C15** for reusable tool revisions, query/policy execution, safe templates, original grant provenance and integrated Studio authoring. The page/traversal specification is required for UI owners.

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C0, C1, C4, C5**. These are required acceptance inputs, not optional examples.

Deliver src/commerce/index.ts plus schema/selection/canonical-json modules and tsup/package exports. Export strict named schemas from C4 and valid/invalid fixtures for every remote tool and final response. Reuse ./whatsapp and ./billing status contracts unchanged. Validation distinguishes shape checks from runtime database authorisation. No promised database lookup in a Zod parser.

### Required evidence

Deliver scripts/validate-commerce-entrypoints.mjs and package script validate:commerce-entrypoints; after npm run build, import both public exports in a clean process with provider/database env unset. Run npm run typecheck and focused node:test/tsx fixtures using existing repository conventions.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

### Runner implementation

SHARED-001 schemas; AI SDK/provider dependencies isolated to the runner entry point so unrelated consumers do not initialise a model runtime.

### Implementation guidance

Apply binding contracts **C14–C15** for reusable tool revisions, query/policy execution, safe templates, original grant provenance and integrated Studio authoring. The page/traversal specification is required for UI owners.

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C1, C4, C6**. These are required acceptance inputs, not optional examples.

Deliver src/commerce/runner/index.ts and a scripted injected-model harness. Define one exported runCommerceTurn(input) with typed success/failure union and runnerVersion; take dependencies explicitly. Keep platform instructions immutable; capability templates are literal text. Maintain turn-local trusted evidence map and reserve final revalidation budget. Do not equate a prompt instruction with enforceable tool permissions or universal hallucination detection.

### Required evidence

Harness verifies exact invocation sequence, max calls/steps/deadline, cancellation, invalid/duplicate final output, unknown evidence ID, missing grant tool, final referral and language-pair validation. assert model/tool side-effect counts; no live model required.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

## Dependencies

- ARCH-016-SHARED-001

Every dependency must be Complete and architect-accepted before execution. Reconcile accepted dependency metadata into the matching parent task branch before promotion. Developer integration or explicitly approved accepted-commit consumption is required to obtain prerequisite source. Readiness never launches a task. Commerce tasks additionally require the new-owner setup checkpoint.

## Enables

- ARCH-020-BACKGROUND-001
- ARCH-020-COMMERCE-003
- ARCH-020-COMMERCE-004
- ARCH-020-COMMERCE-009
- ARCH-020-COMMERCE-011
- ARCH-020-SHOPIFY-001
- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] One exact package version is available in the intended registry, contains both accepted exports and passes clean installation/import/schema/runner smoke verification. Report publication metadata and tested source SHA; implementation-only completion does not satisfy this task.

- [ ] Demonstrate the assigned C16 response-contract cases with named fixtures and actual outcomes; reference the exact published definition/hash or synthetic preview definition used.

- [ ] A previously unknown feature key and query-based tool survive validation/manifest creation. Same shared revision deduplicates; different revisions conflict; grant provenance never widens after creation.

- [ ] Cross-tenant references, unknown schema versions, excessive payloads, invalid money/language metadata and malformed evidence fail validation.
- [ ] NONE/FIXED/AI bindings and Free/Paid offer availability match ARCH-016 without a new paid discount gate.
- [ ] Both producer and consumer can use the same runtime validators; no Prisma, Shopify client or network access enters the shared contract.

- [ ] Reject undeclared tools/versions, missing grant IDs, broadened selections and inconsistent answerKind/referralReason pairs; fixtures include immutable grants spanning multiple turns.

### Runner implementation

- [ ] Demonstrate the assigned C16 response-contract cases with named fixtures and actual outcomes; reference the exact published definition/hash or synthetic preview definition used.

- [ ] Verify C6.1 P06–P12 in the scripted runner harness, plus that P01–P05 host instructions/context are preserved without reinterpretation. Report structural checks separately from natural-language evaluation.

- [ ] Run fixtures with a never-seeded tool name, zero-tool grant and duplicate shared associations; only granted names execute, and query text cannot be supplied as a runtime model argument.

- [ ] A scripted multi-step basket -> discount -> qualifying-products -> finalResponse turn completes without a feature-specific worker branch.
- [ ] Missing/duplicate/malformed final responses, budget exhaustion and cancellation produce explicit failures; model/tool work stops at the deadline.
- [ ] Explicit language preference and unresolved-language handling remain correct; draft prompts cannot remove platform constraints.

- [ ] A question needing an ungranted tool, unknown policy or unavailable product fact produces a structured referral rather than invented facts, an ungranted call, external browsing or a claimed human handoff. Customer/prompt injection cannot broaden the grant.

## Validation

- [ ] Validate the combined implementation once, then verify release metadata, registry artifact and clean consumer installation. Re-run implementation checks only for relevant intervening changes; declared prepack builds remain release mechanics.

- [ ] Validate the worked decimal-string maximumPrice example; reject arbitrary expressions/regex/$ref, unknown mappings, credential inputs, name collisions, bad versions and render templates referencing unknown output paths.

- [ ] Add focused multi-turn grant and unanswerable-question fixtures for the scoped acceptance criteria; assert granted tool IDs/versions and referral output, not just prompt text.
- [ ] Run declared focused tests for valid/invalid manifests, selection matrices, basket/evidence parsing and contract evolution.
- [ ] Run the repository-declared type/build/export checks needed to prove both new entry points compile; git diff --check.

Use package.json commands actually provided by the repository. New Commerce scripts and test fixtures are deliverables, not claims that they exist today. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md. Separate local evidence from pending developer-owned long/live validation; required evidence must exist before acceptance.

### Runner implementation

- [ ] A scripted agent discovers a newly named tool over an existing operation and calls it; malicious rendered templates cannot broaden the grant or bypass grounded referrals.

- [ ] Add focused multi-turn grant and unanswerable-question fixtures for the scoped acceptance criteria; assert granted tool IDs/versions and referral output, not just prompt text.
- [ ] Run focused deterministic runner tests covering multi-tool success, prompt injection attempts, language output, invalid evidence and cancellation.
- [ ] Run declared package type/build/export checks and git diff --check; no live LLM run is required.

Use package.json commands actually provided by the repository. New Commerce scripts and test fixtures are deliverables, not claims that they exist today. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md. Separate local evidence from pending developer-owned long/live validation; required evidence must exist before acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; its real repository must be provisioned before execution preparation.

## Completion Report

### Status

Not Started.

### Files Changed

None; implementation has not started.

### Work Completed

None; task definition only.

### Validation Results

Not run. At execution, distinguish agent checks from exact developer validation required.

### Deviations

Task definition authored on local main by explicit developer request. Normal execution policy remains unchanged.

### Assumptions

Use the parent architecture and actual accepted dependency revisions. Return contradictory source facts to moda_architect.

### Unresolved Issues

See parent architecture review assumptions; no implementation evidence asserted.

### Architectural Concerns

None newly reported.

### Git / VCS

Expected execution branch: task/ARCH-020-SHARED-001. Attempt: 0. No implementation worktree, commit, push or validation is asserted. At submission record canonical workspace, both physical worktrees/branches, synchronization, recursive database submodule SHA/evidence, implementation and parent commit/push results, and confirmation that no parent service gitlink or main integration was performed.

## Architect Review

### Review Status

Pending.

### Review Notes

No implementation submitted. This task is a reviewable definition.

### Reviewed Files

None for implementation review.

### Validation Reviewed

None for implementation review.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile task/index/frontier after review; preserve the terminal/manual system-test gate.
