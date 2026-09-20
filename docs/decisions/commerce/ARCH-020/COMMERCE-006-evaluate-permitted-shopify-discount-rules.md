---
id: ARCH-020-COMMERCE-006
architecture_id: ARCH-020
title: Evaluate permitted Shopify discount rules
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 100
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-COMMERCE-005
  - ARCH-016-BACKGROUND-001
  - ARCH-016-DATABASE-001
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-008
  - ARCH-020-COMMERCE-007
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
---

# Evaluate permitted Shopify discount rules

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Produce evidence-backed eligibility results for the supported native discount subset.

## Context

Merchant-selected capabilities should drive WhatsApp CommerceAgent behaviour through a separate Next.js MCP server with a team-only Studio. Production conversation admission, ordering, model hosting and delivery remain in Background. This is a pre-production breaking rollout, with no implicit permission to delete durable data.

Task definition is on local workspace main by the developer's explicit 2026-09-20 review request. It is not a claim, task-branch materialisation or implementation approval. All execution fields remain unclaimed.

## Scope

Commerce discount rule reader, permission-aware offer listing and deterministic eligibility evaluator.

## Out of Scope

Other repositories' implementation, unrelated refactoring, automatic execution of enabled tasks, live deployment, main integration/push and changes to billing prices/merchant entitlements. No cart/order/discount mutation, WhatsApp sending from Commerce, arbitrary executable code or arbitrary-host HTTP endpoints; C14 validated read-only GraphQL definitions are explicitly permitted. No duplicate discount catalogue/merchant configuration system. Shared indexes and architecture reconciliation remain architect-owned.

## Requirements

Follow the parent architecture's tenant/policy/revision contracts and the assigned logical owner. Preserve unrelated changes. Read repository-local AGENTS.md if present. Commerce consumes the canonical database through its nested database/ Git submodule; schema and migrations belong to moda_database. For consumers, use actual accepted and published dependency revisions, not copied task snapshots or hypothetical versions.

## Work Items

- [ ] Preserve authoritative discount policy/Evidence as a platform helper usable by dynamic tools. Generic public query results and configurable templates cannot establish offer eligibility or bypass NONE/FIXED/current permissions.

- [ ] Implement discounts.getOptions and discounts.evaluate executor operations. Policy checks live in these adapters regardless of configurable tool name/feature mapping; read-only database tool definitions cannot bypass NONE or fixed-offer restrictions.

- [ ] Resolve NONE/FIXED/AI_BEST_APPLICABLE and admin-override precedence from the canonical current merchant policy; preserve Free/Paid availability.
- [ ] Inspect installed Shopify scopes and pinned API schema; read complete supported rule detail on demand rather than parsing catalogue summaries.
- [ ] Implement basic percentage/fixed-amount product/variant/collection conditions and minimum quantity/subtotal with exact decimal/currency handling.
- [ ] Return qualifies-for-known-rules, does-not-qualify, unknown or unsupported with rule/basket fingerprints and unresolved conditions.
- [ ] Fail conservatively for unsupported app/Function/BXGY/shipping/stacking/customer/usage conditions; document the support matrix and live-scope validation command.

## Interfaces / Contracts

ARCH-016 policy/catalogue plus shared evaluation evidence. Missing provider capability returns to architect before scope changes.

### Implementation guidance

Apply binding contracts **C14–C15** for reusable tool revisions, query/policy execution, safe templates, original grant provenance and integrated Studio authoring. The page/traversal specification is required for UI owners.

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C1, C4, C8**. These are required acceptance inputs, not optional examples.

Implement discounts.getOptions and discounts.evaluate operation adapters; use current accepted recovery-policy resolver and canonical catalogue IDs. Deliver docs/discount-support-matrix.md with exact provider field/query mappings for each supported rule and a fixture for each support/unknown case. New OAuth scopes are not in this task: missing scope is a typed unavailable result and a concrete architect gap.

### Deterministic review clarification

Implement the C4 Exact-call evidence refresh contract and its named fixtures.
Business MCP names remain arbitrary. Background captures/replays actual calls;
Commerce policy adapters return bounded structured evidence. No hard-coded
evaluator discovery, extra grant, new Shared field or new database table. Apply
C8 shared provider-request counter (including retries) and deterministic ranking
where recommendations are involved.

### Required evidence

Prove percentage/fixed semantics against recorded official schema/rule evidence; if a rule cannot be calculated exactly, its fixture must assert UNSUPPORTED. Include equality at startsAt/endsAt, threshold boundaries, quantity/collection rules, decimal/currency precision, omitted customer/usage facts and offer policy changes.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

## Dependencies

- ARCH-020-COMMERCE-005
- ARCH-016-BACKGROUND-001
- ARCH-016-DATABASE-001

Every dependency must be Complete and architect-accepted before execution. Reconcile accepted dependency metadata into the matching parent task branch before promotion. Developer integration or explicitly approved accepted-commit consumption is required to obtain prerequisite source. Readiness never launches a task. Commerce tasks additionally require the new-owner setup checkpoint.

## Enables

- ARCH-020-COMMERCE-012

- ARCH-020-COMMERCE-008
- ARCH-020-COMMERCE-007
- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] A renamed/reused discount tool remains policy checked, and an authored public query cannot manufacture usable discount Evidence.

- [ ] FIXED evaluates only its configured usable offer; NONE exposes no discount assistance; AI mode compares only supported current offers.
- [ ] Unresolved eligibility, stale/mismatched facts or unsupported discount families never produce a guaranteed checkout claim.
- [ ] Expiry, minimum thresholds, collection membership, currency and customer restrictions are covered by fixtures; no new catalogue synchroniser is created.

## Validation

- [ ] Expose the same operation through another database-defined tool name and prove policy/evidence checks remain identical; template text must not turn UNKNOWN into qualifying structured evidence.

- [ ] Run deterministic rule-matrix tests including quantity boundaries, decimal totals, collection/variant exclusions, dates, unknown conditions and stale catalogue/provider reads.
- [ ] Provide exact developer-owned Shopify read-validation steps for the pinned API/scopes and anonymised evidence; no agent live calls implied.

Use package.json commands actually provided by the repository. New Commerce scripts and test fixtures are deliverables, not claims that they exist today. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md. Separate local evidence from pending developer-owned long/live validation; required evidence must exist before acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; the actual repository must be provisioned before execution preparation.

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

Commerce repository/submodule provisioning is complete; consume the accepted
COMMERCE-001 foundation. No additional provisioning prerequisite is introduced.

### Architectural Concerns

None newly reported.

### Git / VCS

Expected execution branch: task/ARCH-020-COMMERCE-006. Attempt: 0. No implementation worktree, commit, push or validation is asserted. At submission record canonical workspace, both physical worktrees/branches, synchronization, recursive database submodule SHA/evidence, implementation and parent commit/push results, and confirmation that no parent service gitlink or main integration was performed.

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
