---
id: ARCH-020-COMMERCE-016
architecture_id: ARCH-020
title: Evaluate normalised discount rules and produce evidence
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 105
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-COMMERCE-006
  - ARCH-020-COMMERCE-015
  - ARCH-020-SHARED-001
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-007
  - ARCH-020-COMMERCE-013
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-21
updated: 2026-09-21
---

# Evaluate normalised discount rules and produce evidence

## Architecture

ARCH-020. [Parent architecture](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).
Binding [implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md):
C4/C5/C7/C8/C9/C14/C16/C18 as applicable, and exact ownership/interfaces in **C19**.

## Objective

Own deterministic eligibility/savings evaluation and discounts.evaluate adapter using006 normalized rules and015 basket/product facts.

## Context

This is the canonical narrowed definition from the 2026-09-21 task split, replacing
the former combined scope. No prior attempt or implementation is discarded. Normal
launcher/worktree/review policies apply. No task is claimed by this definition.

## Scope

Own deterministic eligibility/savings evaluation and discounts.evaluate adapter using006 normalized rules and015 basket/product facts.

## Out of Scope

Other C19 owners' modules; new Shared wire versions or database schema; live
deployment/provider calls; unrelated refactors; cart/order writes or WhatsApp sends.
Do not implement missing dependencies or substitute production fixtures to finish.

## Requirements

Use accepted auth/Shared/database source, canonical types and C19 ports. Preserve
others' changes. Exact business names remain database-authored. Fixtures are injected
only by tests; production missing adapters fail closed. Each case below has an
expected side effect, not just a screenshot/typecheck. C19 assigns final wiring.

## Work Items

- [ ] Implement the pure C19 evaluator with injected now and exact decimal/currency metadata; no network/DB access inside arithmetic.
- [ ] Apply C8 condition precedence, startsAt<=now<endsAt, native supported rule scope, minimum bases/allocation/rounding only where006 evidence proves semantics.
- [ ] Implement discounts.evaluate orchestration: re-read current policy/rule, load exact basket/proposal facts, enforce NONE/FIXED and caller ownership, and share request budget across adapters.
- [ ] Generate C4/C18 Evidence/digest/fingerprints/lifetime for exact proposal; UNKNOWN/UNSUPPORTED/unresolved never qualifies. No checkout guarantee or mutation.
- [ ] Export evaluator for007 and operation adapter for013 registration. Accept rule-reader/product fixtures plus actual pure evaluator tests;013 verifies real reader/provider composition.

## Interfaces / Contracts

Own `src/commerce/discounts/evaluator/`.006 owns DiscountRuleSnapshot/provider semantics;015 owns basket/current facts;007 owns recommendations.013 owns their real registration/composition.


## Dependencies

- ARCH-020-COMMERCE-006
- ARCH-020-COMMERCE-015
- ARCH-020-SHARED-001

All listed prerequisites must be Complete and architect-accepted before a claim.
Use dedicated launcher worktrees and accepted source; do not launch enabled work.

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-007
- ARCH-020-COMMERCE-013
- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] V01: percentage/fixed rule matrix includes quantity/subtotal boundaries, product/variant/collection scope and exact decimal rounding/allocation; expected money is explicitly calculated in fixtures.
- [ ] V02: time/disabled/failure -> nonqualification precedes unsupported/missing facts; unknown semantics and customer/usage restrictions never qualify.
- [ ] V03: wrong currency, absent variants, partial memberships and stale/changed rules fail closed; exact proposal operation order and fingerprints are preserved.
- [ ] V04: canonical C18 seed parses; producer evidence lifetime/digest, renamed evaluator, NONE/FIXED and revoked policy cases have zero unauthorized reads.
- [ ] V05: re-evaluation of changed basket/rule produces changed semantic evidence; provider ceiling includes all nested reads; pure arithmetic makes zero I/O calls.

## Validation

Implement the named cases above as focused tests. Record case -> fixture -> command
-> expected/actual effects in the Completion Report. Check shared contract examples
where applicable; include malformed and denied inputs with zero side effects.
Run focused tests while developing, then typecheck/lint/build once before submission;
repeat broader checks only for new failures or changed concerns. Use actual repository
commands and record them. Local browser/component evidence is task-owned where a UI
is in scope. Follow agent-validation/live-validation policies; separate pending
required developer database/container evidence and never claim fixture tests prove
live service behavior. No minimum screenshot/test count substitutes for coverage.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; consume the accepted COMMERCE-001 foundation.

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

Expected execution branch: task/ARCH-020-COMMERCE-016. Attempt: 0. No implementation worktree, commit, push or validation is asserted. At submission record canonical workspace, both physical worktrees/branches, synchronization, recursive database submodule SHA/evidence, implementation and parent commit/push results, and confirmation that no parent service gitlink or main integration was performed.

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
