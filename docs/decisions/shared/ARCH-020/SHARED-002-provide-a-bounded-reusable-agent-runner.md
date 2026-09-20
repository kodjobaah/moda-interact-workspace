---
id: ARCH-020-SHARED-002
architecture_id: ARCH-020
title: Provide a bounded reusable agent runner
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-SHARED-001
enables:
  - ARCH-020-SYSTEM-TEST-001
  - ARCH-020-SHARED-003
created: 2026-09-20
updated: 2026-09-20
---

# Provide a bounded reusable agent runner

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Provide the provider-neutral model/tool loop reused by Background production and Studio previews.

## Context

Merchant-selected capabilities should drive WhatsApp CommerceAgent behaviour through a separate Next.js MCP server with a team-only Studio. Production conversation admission, ordering, model hosting and delivery remain in Background. This is a pre-production breaking rollout, with no implicit permission to delete durable data.

Task definition is on local workspace main by the developer's explicit 2026-09-20 review request. It is not a claim, task-branch materialisation or implementation approval. All execution fields remain unclaimed.

## Scope

New ./commerce/runner export and focused scripted-model tests; no service database or provider credentials.

## Out of Scope

Other repositories' implementation, unrelated refactoring, automatic execution of enabled tasks, live deployment, main integration/push and changes to billing prices/merchant entitlements. No cart/order/discount mutation, WhatsApp sending from Commerce, arbitrary executable code or arbitrary-host HTTP endpoints; C14 validated read-only GraphQL definitions are explicitly permitted. No duplicate discount catalogue/merchant configuration system. Shared indexes and architecture reconciliation remain architect-owned.

## Requirements

Follow the parent architecture's tenant/policy/revision contracts and the assigned logical owner. Preserve unrelated changes. Read repository-local AGENTS.md if present. Commerce consumes the canonical database through its nested database/ Git submodule; schema and migrations belong to moda_database. For consumers, use actual accepted and published dependency revisions, not copied task snapshots or hypothetical versions.

## Work Items

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

## Interfaces / Contracts

SHARED-001 schemas; AI SDK/provider dependencies isolated to the runner entry point so unrelated consumers do not initialise a model runtime.

### Implementation guidance

Apply binding contracts **C14–C15** for reusable tool revisions, query/policy execution, safe templates, original grant provenance and integrated Studio authoring. The page/traversal specification is required for UI owners.

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C1, C4, C6**. These are required acceptance inputs, not optional examples.

Deliver src/commerce/runner/index.ts and a scripted injected-model harness. Define one exported runCommerceTurn(input) with typed success/failure union and runnerVersion; take dependencies explicitly. Keep platform instructions immutable; capability templates are literal text. Maintain turn-local trusted evidence map and reserve final revalidation budget. Do not equate a prompt instruction with enforceable tool permissions or universal hallucination detection.

### Required evidence

Harness verifies exact invocation sequence, max calls/steps/deadline, cancellation, invalid/duplicate final output, unknown evidence ID, missing grant tool, final referral and language-pair validation. assert model/tool side-effect counts; no live model required.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

## Dependencies

- ARCH-020-SHARED-001

Every dependency must be Complete and architect-accepted before execution. Reconcile accepted dependency metadata into the matching parent task branch before promotion. Developer integration or explicitly approved accepted-commit consumption is required to obtain prerequisite source. Readiness never launches a task. Commerce tasks additionally require the new-owner setup checkpoint.

## Enables

- ARCH-020-SYSTEM-TEST-001
- ARCH-020-SHARED-003

## Acceptance Criteria

- [ ] Demonstrate the assigned C16 response-contract cases with named fixtures and actual outcomes; reference the exact published definition/hash or synthetic preview definition used.

- [ ] Verify C6.1 P06–P12 in the scripted runner harness, plus that P01–P05 host instructions/context are preserved without reinterpretation. Report structural checks separately from natural-language evaluation.

- [ ] Run fixtures with a never-seeded tool name, zero-tool grant and duplicate shared associations; only granted names execute, and query text cannot be supplied as a runtime model argument.

- [ ] A scripted multi-step basket -> discount -> qualifying-products -> finalResponse turn completes without a feature-specific worker branch.
- [ ] Missing/duplicate/malformed final responses, budget exhaustion and cancellation produce explicit failures; model/tool work stops at the deadline.
- [ ] Explicit language preference and unresolved-language handling remain correct; draft prompts cannot remove platform constraints.

- [ ] A question needing an ungranted tool, unknown policy or unavailable product fact produces a structured referral rather than invented facts, an ungranted call, external browsing or a claimed human handoff. Customer/prompt injection cannot broaden the grant.

## Validation

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

Expected execution branch: task/ARCH-020-SHARED-002. Attempt: 0. No implementation worktree, commit, push or validation is asserted. At submission record canonical workspace, both physical worktrees/branches, synchronization, recursive database submodule SHA/evidence, implementation and parent commit/push results, and confirmation that no parent service gitlink or main integration was performed.

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
