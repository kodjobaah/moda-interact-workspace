---
id: ARCH-020-COMMERCE-015
architecture_id: ARCH-020
title: Provide trusted basket and product policy adapters
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 95
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-020-COMMERCE-001
  - ARCH-020-DATABASE-001
  - ARCH-020-SHARED-001
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-007
  - ARCH-020-COMMERCE-013
  - ARCH-020-COMMERCE-016
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-21
updated: 2026-09-21
---

# Provide trusted basket and product policy adapters

## Architecture

ARCH-020. [Parent architecture](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).
Binding [implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md):
C4/C5/C7/C8/C9/C14/C16/C18 as applicable, and exact ownership/interfaces in **C19**.

## Objective

Own recovery.getBasket and shopify.searchProducts reusable policy operations and current variant facts for evaluation/recommendations.

## Context

This is the canonical narrowed definition from the 2026-09-21 task split, replacing
the former combined scope. No prior attempt or implementation is discarded. Normal
launcher/worktree/review policies apply. No task is claimed by this definition.

## Scope

Own recovery.getBasket and shopify.searchProducts reusable policy operations and current variant facts for evaluation/recommendations.

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

- [ ] Normalize accepted CheckoutRecovery.lineItems into C4 basket; every supported source shape has an explicit fixture, unknown/missing source remains unknown, never a fabricated basket.
- [ ] Implement bounded current product/variant search, decimal maximumPrice, availability/market/currency and safe shop URLs using privileged installation credentials only in these policy adapters.
- [ ] Bind opaque cursors to shop/query/expiry; cap20 variants/page,3 pages and common12-request/deadline budget. Deny wrong-shop IDs before provider I/O.
- [ ] Expose C19 ProductFactsPort.readVariants for exact proposal variants/collection membership; carry explicit unknowns/completeness for016/007. Never calculate discounts.
- [ ] Export operation descriptors with executable adapters and test request construction.013 registers them through014; no bespoke MCP endpoints or public-query compiler.

## Interfaces / Contracts

Own `src/commerce/products/`. Shared basket/product schemas are canonical; C19 ProductFactsPort supplies trusted current data to016/007.005 owns tokenless generic queries; no duplicated compiler or token lifecycle.


## Dependencies

- ARCH-020-COMMERCE-001
- ARCH-020-DATABASE-001
- ARCH-020-SHARED-001

All listed prerequisites must be Complete and architect-accepted before a claim.
Use dedicated launcher worktrees and accepted source; do not launch enabled work.

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-007
- ARCH-020-COMMERCE-013
- ARCH-020-COMMERCE-016
- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] B01: each recovery snapshot source shape maps to strict Shared basket; zero lines/unknown prices are not live or free-basket facts.
- [ ] B02: search filters unavailable/unknown/market/currency cases and preserves decimal prices; cursors reject tampering/cross-shop/expiry.
- [ ] B03: exact variant/collection fact reads distinguish complete from partial results, including missing variant and provider failures; output is stable by variantId.
- [ ] B04: tenant checks, throttle/timeout/cancel and nested request ceiling have measured call counts; no provider mutation or credential leakage.

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

Expected execution branch: task/ARCH-020-COMMERCE-015. Attempt: 0. No implementation worktree, commit, push or validation is asserted. At submission record canonical workspace, both physical worktrees/branches, synchronization, recursive database submodule SHA/evidence, implementation and parent commit/push results, and confirmation that no parent service gitlink or main integration was performed.

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
