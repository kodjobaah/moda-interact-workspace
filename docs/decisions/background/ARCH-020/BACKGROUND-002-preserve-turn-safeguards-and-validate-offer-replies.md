---
id: ARCH-020-BACKGROUND-002
architecture_id: ARCH-020
title: Preserve turn safeguards and validate offer replies
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 160
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-BACKGROUND-001
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-SYSTEM-TEST-001
  - ARCH-020-GATEWAY-002
created: 2026-09-20
updated: 2026-09-21
---

# Preserve turn safeguards and validate offer replies

## Architecture

Architecture ID: ARCH-020.

Architecture document: docs/architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md.

Coordinator: moda_architect. Read the complete parent architecture and relevant dependency/contract tasks. Execution handoff: docs/architecture/ARCH-020-implementation-handoff.md.

## Objective

Keep MCP-backed replies within existing conversation, permission and outbound safety boundaries.

## Context

Merchant-selected capabilities should drive WhatsApp CommerceAgent behaviour through a separate Next.js MCP server with a team-only Studio. Production conversation admission, ordering, model hosting and delivery remain in Background. This is a pre-production breaking rollout, with no implicit permission to delete durable data.

Task definition is on local workspace main by the developer's explicit 2026-09-20 review request. It is not a claim, task-branch materialisation or implementation approval. All execution fields remain unclaimed.

## Scope

Background turn processor/result validation, live permission recheck and offer-evidence integration tests.

## Out of Scope

Other repositories' implementation, unrelated refactoring, automatic execution of enabled tasks, live deployment, main integration/push and changes to billing prices/merchant entitlements. No cart/order/discount mutation, WhatsApp sending from Commerce, arbitrary executable code or arbitrary-host HTTP endpoints; C14 validated read-only GraphQL definitions are explicitly permitted. No duplicate discount catalogue/merchant configuration system. Shared indexes and architecture reconciliation remain architect-owned.

## Requirements

Follow the parent architecture's tenant/policy/revision contracts and the assigned logical owner. Preserve unrelated changes. Read repository-local AGENTS.md if present. Commerce consumes the canonical database through its nested database/ Git submodule; schema and migrations belong to moda_database. For consumers, use actual accepted and published dependency revisions, not copied task snapshots or hypothetical versions.

## Work Items

### Independent implementation contract

Binding **C18** in the implementation contracts is the single producer/consumer
specification, including the linked JSON seed and EC01–EC12 matrix.
Consumer: implement the C18 strict extractor, immutable call provenance, exact
refresh comparison and delivery decision. Use a contract-faithful MCP double;
COMMERCE-007 implementation is not a prerequisite. Existing BACKGROUND-001 and
its accepted Shared version remain prerequisites. Do not implement Commerce
ranking/evaluation. Component acceptance uses EC01–EC12 with call/send/usage/state
assertions; actual service pairing is SYSTEM-TEST-001-owned.


- [ ] Treat generic public query data as ordinary facts, never signed/validated discount Evidence. Current offer-policy verification still uses exact originally granted policy helpers; absence of suitable evidence causes referral.

- [ ] Keep final answer composition in CommerceAgent: a tool rendered template is not an instruction to send immediately. Validate structured facts/offer evidence and normal admission before WhatsApp delivery.

- [ ] Preserve C13 no-response follow-up suppression and credit semantics. Test reply-to-initial before follow-up, reply-to-initial after follow-up, reply-to-follow-up, ordinary single-recovery reply, duplicate audio engagement repair, and engagement racing final send recheck. No new recovery credit/attempt for continuation, no sequence3 or grant reset.

- [ ] Recheck current shop/capability permission and discount evidence before an offer reply is sent; pinning must not bypass revocation.
- [ ] Preserve per-conversation ordering, stale-version suppression, language mutation guards, outbound reservations and exactly the existing delivery ownership.
- [ ] Prevent cross-turn or expired/tampered offer evidence from supporting a customer claim; distinguish known-rule qualification from checkout guarantees.
- [ ] Exercise MCP timeout/throttle/cancellation and lease-loss paths without duplicate sends or leaked reservations.
- [ ] Provide host semantic telemetry for release/evidence outcomes using existing tracing/logging infrastructure.

- [ ] Handle REFER_TO_STORE as the single normal admitted reply, localised to the resolved language. Render its verified contact/store URL from trusted server context; otherwise say to contact the store directly. Do not trust model-supplied contact details, assert human notification, open a ticket or send an additional fallback message. Preserve current stale-turn/admission checks for referrals.

## Interfaces / Contracts

Existing ARCH-007/010/005 safeguards and the binding C18 producer/consumer contract. Do not redesign general billing policy.

### Implementation guidance

Apply binding contracts **C14–C15** for reusable tool revisions, query/policy execution, safe templates, original grant provenance and integrated Studio authoring. The page/traversal specification is required for UI owners.

Binding companion: [ARCH-020 implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md), sections **C2, C3, C4, C6, C11**. Also apply **C13** for outreach/continuation semantics. These are required acceptance inputs, not optional examples.

Own final-delivery admission, evidence refresh, status handling and worker failure regression coverage. Preserve the existing unknown-message provider-status path for unpersisted guidance; no guidance receipt table/status handler or merchant usage. For normal replies recheck processing version/lease and current permissions immediately before send; revalidation failure replaces the proposed answer with one admitted referral.

### Deterministic review clarification

Implement the C4 Exact-call evidence refresh contract and its named fixtures.
Business MCP names remain arbitrary. Background captures/replays actual calls;
Commerce policy adapters return bounded structured evidence. No hard-coded
evaluator discovery, extra grant, new Shared field or new database table. Apply
C18 host call/deadline budgets; C8 internal provider counters and ranking remain
Commerce-owned and are represented by contract fixtures here.

### Required evidence

Add controllable barriers for new-message-during-model, lease loss, revocation-before-send, unknown provider acceptance and duplicate job delivery. Verify no stale language write or double reservation; actual send status uncertainty is not treated as safe automatic retry. History inclusion is tested in BACKGROUND-001; do not substitute prompt snapshots.

For this task, record a requirement-to-fixture matrix with expected side effects, actual commands and results in the Completion Report. Do not implement another repository's changes to bypass a dependency.

## Dependencies

- ARCH-020-BACKGROUND-001

Every dependency must be Complete and architect-accepted before execution. Reconcile accepted dependency metadata into the matching parent task branch before promotion. Developer integration or explicitly approved accepted-commit consumption is required to obtain prerequisite source. Readiness never launches a task. Commerce tasks additionally require the new-owner setup checkpoint.

## Enables

- ARCH-020-COMMERCE-012

- ARCH-020-SYSTEM-TEST-001
- ARCH-020-GATEWAY-002

## Acceptance Criteria

- [ ] An authored template/query cannot authorize a discount by imitating evidence fields or a reserved helper name; normal factual product queries remain usable.

- [ ] A newer customer message or lost lease suppresses the older result without a WhatsApp send or stale language update.
- [ ] Disabling a feature/shop or changing an offer before delivery prevents an invalid offer reply.
- [ ] MCP failures and retries do not double-charge, double-send, bypass abuse limits or start an unbounded fallback loop.

- [ ] Unknown answers and unusable originally granted tools produce a factual bounded store referral without extra WhatsApp sends, fabricated contacts or unsupported offers. Revoked tools cannot be replaced by newly enabled ones.

## Validation

- [ ] Injection/unsupported claims in renderedText cannot replace verified contacts or evidence; multiple tool results still produce one normal admitted final response.

- [ ] Add focused multi-turn grant and unanswerable-question fixtures for the scoped acceptance criteria; assert granted tool IDs/versions and referral output, not just prompt text.
- [ ] Run focused turn/admission/evidence Vitest regressions with deterministic concurrent-turn and revoked-policy fixtures.
- [ ] Run declared build and git diff --check; provide any long integration command separately for developer execution.

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

Expected execution branch: task/ARCH-020-BACKGROUND-002. Attempt: 0. No implementation worktree, commit, push or validation is asserted. At submission record canonical workspace, both physical worktrees/branches, synchronization, recursive database submodule SHA/evidence, implementation and parent commit/push results, and confirmation that no parent service gitlink or main integration was performed.

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


### Architect readiness amendment — 2026-09-21

Ready, unclaimed, attempt0. Accepted BACKGROUND-001 is the start prerequisite;
C18 fixes the interface. COMMERCE-007 is removed as a code/start dependency.
Component acceptance uses contract fixtures; terminal SYSTEM-TEST-001 owns real
producer/consumer integration. No task is launched or implementation accepted here.
