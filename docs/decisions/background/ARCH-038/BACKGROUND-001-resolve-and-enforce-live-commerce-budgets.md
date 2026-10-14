---
id: ARCH-038-BACKGROUND-001
architecture_id: ARCH-038
title: Resolve and enforce LIVE per-turn CommerceAgent budgets
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 20
executor: developer
claimed_at: 2026-10-14T11:33:12Z
attempt: 1
depends_on:
  - ARCH-038-DATABASE-001
enables:
  - ARCH-038-SYSTEM-TEST-001
created: 2026-10-13
updated: 2026-10-14
---
# Resolve and enforce LIVE per-turn CommerceAgent budgets

## Architecture

- Architecture ID: `ARCH-038`
- Architecture document: `docs/architecture/ARCH-038-commerce-agent-execution-budget-policies.md`
- Coordinator: `moda_architect`
- Assigned agent: `moda_background`
- Repository: `moda-interact-background`

## Objective

Resolve the exact LIVE Platform/Price Plan/Merchant precedence on each admitted Background CommerceAgent turn and enforce the frozen effective limits.

## Context

The existing Background Commerce host sends a 90-second remaining envelope and no merchant-specific output-token budget to Shared; this must be replaced or reconciled, not masked by partial logging changes.

## Scope

- Load environment-scoped `CommerceModelPolicy` LIVE rows for trusted Shop and current Subscription; validate `budgetSchemaVersion`, overlay sparse JSON keys in Platform → Price Plan → Shop precedence, and resolve each value with independent source/edit-version details.
- Match eligible current ACTIVE/TRIALING Subscription.plan -> BillingPlan.shopifyPlanHandle -> MerchantPricingPlan.shopifyPlanHandle; ignore pending plans.
- Freeze policy for the admitted turn/retry and pass exact supported deadlineMs/outputTokens to runCommerceTurn.
- Reconcile worker lease, job timeout, cancellation and existing execution envelope with configured deadline; reject unsupported configuration explicitly rather than silently clipping.
- Use shared structured logging and focused database-backed integration tests.

## Out of Scope

- Do not alter Shopify/Woo merchant UI or edit Admin policy.
- Do not reimplement Shared runner or introduce a Background-local generic logger.
- Do not consult PREVIEW policy or Environment variables intended for Studio Preview.

## Requirements

- Merchant -> current Price Plan -> Platform per field; missing JSON budget key inherits, explicit null/invalid/unknown-version policy fails closed.
- No effective plan from pending/cancelled/unmatched plans. Preserve existing subscription lifecycle rules and Woo canonical plan mapping.
- Policy changes during an active turn cannot mutate its frozen limits; retry/resumption identity is explicit.
- No hidden 90-second cap remaining when accepted configuration specifies a different supported deadline.
- Log chosen limits, sources, environment and bounded identifiers; no customer text or secrets.

## Work Items

- [ ] Implement indexed read + precedence resolver and snapshot.
- [ ] Wire effective budgets to runtime and reconcile worker/timeouts.
- [ ] Add per-field inheritance, plan-switch/race, tenant, provider and deadline integration cases.

## Interfaces / Contracts

Consumes DATABASE-001 `CommerceModelPolicy` rows filtered to `context=LIVE`, with a versioned `budget` object and provenance, together with the published `@modainteract/moda-interact-shared` `runCommerceTurn` budget contract.

## Dependencies

- `ARCH-038-DATABASE-001`

## Enables

- `ARCH-038-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Each turn uses exact effective limits and verified source labels.
- [ ] Plan changes affect only subsequently admitted turns.
- [ ] Wrong-shop or pending-plan override never applies.
- [ ] Deadline/lease mismatches produce a clear error rather than silent truncation.

## Validation

- [ ] Focused resolver unit tests
- [ ] Disposable PostgreSQL plan/policy integration
- [ ] Worker deadline/cancellation/retry regression
- [ ] Relevant typecheck/build and git diff --check

## Stop Condition

Once all defined work items, acceptance criteria and required validation are satisfied, submit the Completion Report and return for authorised review. Do **not** start enabled or neighbouring tasks. Required evidence unavailable in this environment must be recorded as unverified, not claimed passed.

## Implementation Notes

Use the launcher-resolved dedicated parent and implementation worktrees with matching `task/ARCH-038-BACKGROUND-001` branches and record physical isolation, synchronization and submodule evidence in the Completion Report. This definition is portable and **not yet materialised** in the developer's Git workspace. Follow the actual repository scripts rather than assuming uniform package commands. No `docs/decisions/**/_index.md` changes until the developer explicitly ends this architecture session. Preserve unrelated ARCH-037 and other in-progress changes; reconcile newer checkouts before implementation.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-14T11:33:12Z. Attempt 0 review history is preserved below.

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

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

Pending implementation

### Follow-up

None
