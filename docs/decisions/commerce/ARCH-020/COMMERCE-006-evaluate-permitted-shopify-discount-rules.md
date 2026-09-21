---
id: ARCH-020-COMMERCE-006
architecture_id: ARCH-020
title: Read merchant discount policy and normalise Shopify rules
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 100
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-COMMERCE-001
  - ARCH-020-DATABASE-001
  - ARCH-020-SHARED-001
  - ARCH-016-BACKGROUND-001
  - ARCH-016-DATABASE-001
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-013
  - ARCH-020-COMMERCE-016
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-21
---

# Read merchant discount policy and normalise Shopify rules

## Architecture

ARCH-020. [Parent architecture](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).
Binding [implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md):
C4/C5/C7/C8/C9/C14/C16/C18 as applicable, and exact ownership/interfaces in **C19**.

## Objective

Own current discount-policy resolution, permission-aware offer listing and provider rule normalization. Do not calculate qualification or savings.

## Context

This is the canonical narrowed definition from the 2026-09-21 task split, replacing
the former combined scope. No prior attempt or implementation is discarded. Normal
launcher/worktree/review policies apply. No task is claimed by this definition.

## Scope

Own current discount-policy resolution, permission-aware offer listing and provider rule normalization. Do not calculate qualification or savings.

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

- [ ] Reuse accepted ARCH-016 merchant policy/catalogue: NONE/FIXED/AI_BEST_APPLICABLE, admin precedence and Free/Paid availability. Do not add another catalogue or synchronizer.
- [ ] Implement discounts.getOptions and DiscountRuleReader under C19. Verify canonical offer/shop ownership before provider requests; fixed mode cannot read a different offer.
- [ ] Inspect actual pinned Admin API/schema/scopes and document exact static query -> normalized-field mappings in docs/discount-support-matrix.md. Missing scope returns UNAVAILABLE; no OAuth scope expansion.
- [ ] Normalize native basic percentage/fixed conditions, targets, minimums, dates and provider semantics; unresolved or unsupported clauses remain explicit and cannot be discarded.
- [ ] Share injected provider-request budget across pagination/retries; <=50 offers and C8 bounds. No eligibility calculation, Evidence generation or recommendation ranking.

## Interfaces / Contracts

Own `src/commerce/discounts/reader/`. C19 DiscountRuleSnapshot is the sole input contract for016.016 owns calculation;013 connects discounts.getOptions to014. Provider schema evidence is an implementation deliverable, not permission to invent Shopify semantics.


## Dependencies

- ARCH-020-COMMERCE-001
- ARCH-020-DATABASE-001
- ARCH-020-SHARED-001
- ARCH-016-BACKGROUND-001
- ARCH-016-DATABASE-001

All listed prerequisites must be Complete and architect-accepted before a claim.
Use dedicated launcher worktrees and accepted source; do not launch enabled work.

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-013
- ARCH-020-COMMERCE-016
- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] D01: NONE lists none; FIXED permits only its offer; AI listing is bounded and discloses truncation; wrong tenant/offer yields zero provider calls.
- [ ] D02: provider fixtures map percentage/fixed/all/product/variant/collection/minimum/date fields to the exact C19 DTO; incomplete fields never become defaults claiming support.
- [ ] D03: unsupported app/Function/BXGY/shipping/combination restrictions remain UNSUPPORTED; unverified customer/usage facts remain UNKNOWN.
- [ ] D04: missing scopes, provider outage, stale catalogue and pagination/retry ceilings return bounded errors; semantic fingerprint excludes observation timestamps.
- [ ] D05: every supported normalization profile has cited pinned provider-schema evidence; unproven allocation/rounding becomes UNSUPPORTED, not a guessed formula.

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
