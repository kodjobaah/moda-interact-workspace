---
id: ARCH-019-SHOPIFY-005
architecture_id: ARCH-019
title: Replace the usage-first home page with the recovery overview
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-019-SHOPIFY-001
  - ARCH-019-SHOPIFY-003
  - ARCH-019-SHOPIFY-004
enables:
  - ARCH-019-SHOPIFY-006
  - ARCH-019-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
---

# Replace the usage-first home page with the recovery overview

## Architecture

Architecture ID: ARCH-019

Architecture document: docs/architecture/ARCH-019-merchant-recovery-experience.md

Coordinator: moda_architect. Read the complete parent architecture and referenced dependency tasks before execution; it supplies exact data, route, access, compatibility and rollout contracts.

## Objective

Make home answer recovery-performance questions with truthful cohort metrics and bounded data loading.

## Context

This task contributes one bounded capability to the recovery-first merchant journey. The previous UI mixed billing-period navigation, all-time recovery figures and a customer modal. The new design separates recovery performance, recovery conversation history and billing usage.

## Scope

app/routes/app/home/route.jsx; overview/dashboard components and styles; relevant home tests and locale catalogues. Existing pending-recovery and billing-setup components may be composed, but their business policy is not owned here.

## Out of Scope

Other repository implementation; billing/credit/provider semantics; new automated messages; reply/takeover controls; unrelated refactoring; main merges/pushes; live deployment. Do not start enabled tasks. Parent architecture/index reconciliation belongs to moda_architect.

## Requirements

The parent architecture's behavioural contracts are binding. Preserve current tenant/lifecycle rules and accepted ARCH-017 onboarding behaviour; do not restore stale ARCH-013 permissions. Follow repo-local AGENTS.md and the assigned logical agent definition. Never copy mockup sample data into production. Preserve unrelated changes by using canonical task worktrees.

## Work Items

- [ ] Render the agreed performance metrics, five recent recoveries and date controls using SHOPIFY-001; link into the list/detail routes with preserved date context.
- [ ] Show current recovery capacity using the existing authoritative billing projection, clearly separate from historical date filters; preserve source/expiry distinctions and unavailable states.
- [ ] Preserve onboarding, billing-setup and restriction banners and the current pending-recoveries capability gate; label pending queue candidates separately from ongoing durable recoveries.
- [ ] Remove the home path’s unbounded recovery/message/usage-event hydration and full-payload debug logging; no synthetic metrics or guessed product details.
- [ ] Redirect authorized legacy /app?view=detail&bill=... requests to /app/usage with validated bill context before performance reads; leave initial onboarding behaviour unchanged.

## Interfaces / Contracts

SHOPIFY-001 aggregate/list DTOs; existing billing capacity and onboarding services remain authorities. No billing mutation or usage-accounting changes.

## Dependencies

- ARCH-019-SHOPIFY-001
- ARCH-019-SHOPIFY-003
- ARCH-019-SHOPIFY-004

All listed dependencies must be Complete and architect-accepted. Consume actual accepted source revisions; a copied initial task snapshot is not acceptance evidence. The architect must reconcile accepted dependency metadata into this parent task branch before promotion; the prepared launcher gates dependencies from this branch, not directly from sibling worktrees. Unmerged accepted implementation prerequisites require the normal developer integration or explicit approved dependency-commit consumption before this task can use their code.

## Enables

- ARCH-019-SHOPIFY-006
- ARCH-019-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Metrics/list cohort definitions match; empty data, unknown values and mixed currencies display without invented totals or percentages.
- [ ] No all-shop messages or usage history is fetched to render Overview; the old customer modal is not reachable from the new home.
- [ ] Historical lifecycle states retain readable performance/history; capacity exhaustion alone does not hide past records.
- [ ] An empty pending queue does not imply recovery is healthy, disabled, or fully complete.
- [ ] Legacy bookmarked billing-detail URLs land on billing usage, not silently on an unrelated date cohort.
- [ ] Overview links work with dates and merchant embed context, and locale keys have parity.

## Validation

- [ ] Run npm test -- tests/unit/home-route.test.ts tests/unit/recovery-overview.test.ts tests/unit/merchant-pricing-usage-overview.test.jsx tests/unit/merchant-i18n.test.ts (update obsolete assertions deliberately).
- [ ] Run npm run typecheck, npm run lint and git diff --check.
- [ ] Verify local browser fixtures for ACTIVE, ONBOARDING, NO_CONTRACT, FROZEN, BILLING_ATTENTION, zero history, capacity unavailable and legacy URL entry.

New test filenames above are required deliverables, not claims that those suites already exist. Use current package.json scripts; do not invent success when a command cannot run. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md: fast local checks are agent-owned; long infrastructure/live commands are developer-owned unless exactly authorized. Required developer evidence may remain pending at review, never at acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's Work Items, Acceptance Criteria, Validation and Completion Report, publish task-owned mirrored branches and return to review. Record exact pending developer-validation commands if needed. Stop; do not start enabled tasks, merge/push main, or mark your own task Complete.

## Implementation Notes

Use scripts/start-agent-task.py through the normal /moda-task preparation path. Task creation has not claimed execution. Dedicated parent and implementation worktrees, synchronization and recursive database submodule preparation are mandatory when execution starts. Follow docs/agent-vcs-ownership-policy.md. The repository agent may update only this task's execution/report fields in parent docs; shared indexes and parent architecture remain architect-owned.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None; task definition only.

### Validation Results

Not run; implementation has not started. Separate agent-executed evidence from developer validation required.

### Deviations

None.

### Assumptions

Use current accepted dependency revisions and the parent architecture; return any contradictory source fact to moda_architect.

### Unresolved Issues

None identified at definition time beyond the parent architecture's recorded evidence gaps.

### Architectural Concerns

None newly reported.

### Git / VCS

Execution branch: task/ARCH-019-SHOPIFY-005. Attempt: 0. No implementation claim, worktree, commit or validation is asserted. At execution submission record canonical workspace, both physical worktrees/branches, start-of-attempt synchronization, recursive submodule evidence, implementation and parent commit/push evidence, and confirmation that no parent service Gitlink or main branch was changed.

## Architect Review

### Review Status

Pending.

### Review Notes

No implementation submitted.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Awaiting implementation review.

### Follow-up

Reconcile task/index/frontier after accepted implementation; terminal system test remains manually invoked.
