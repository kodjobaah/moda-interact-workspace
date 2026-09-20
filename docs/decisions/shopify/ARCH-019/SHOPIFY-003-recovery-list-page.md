---
id: ARCH-019-SHOPIFY-003
architecture_id: ARCH-019
title: Build the recovery browsing page and guarded route
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-019-SHOPIFY-001
enables:
  - ARCH-019-SHOPIFY-004
  - ARCH-019-SHOPIFY-005
  - ARCH-019-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
---

# Build the recovery browsing page and guarded route

## Architecture

Architecture ID: ARCH-019

Architecture document: docs/architecture/ARCH-019-merchant-recovery-experience.md

Coordinator: moda_architect. Read the complete parent architecture and referenced dependency tasks before execution; it supplies exact data, route, access, compatibility and rollout contracts.

## Objective

Let merchants browse recovery records using accessible search, date/status filters and server pagination.

## Context

This task contributes one bounded capability to the recovery-first merchant journey. The previous UI mixed billing-period navigation, all-time recovery figures and a customer modal. The new design separates recovery performance, recovery conversation history and billing usage.

## Scope

app/routes.ts; new app/routes/app/recoveries list route/components/styles; app/services/shop/merchant-route-access-policy.ts for RECOVERY_HISTORY only; app-local query helpers from SHOPIFY-001; associated tests and all merchant locale catalogues.

## Out of Scope

Other repository implementation; billing/credit/provider semantics; new automated messages; reply/takeover controls; unrelated refactoring; main merges/pushes; live deployment. Do not start enabled tasks. Parent architecture/index reconciliation belongs to moda_architect.

## Requirements

The parent architecture's behavioural contracts are binding. Preserve current tenant/lifecycle rules and accepted ARCH-017 onboarding behaviour; do not restore stale ARCH-013 permissions. Follow repo-local AGENTS.md and the assigned logical agent definition. Never copy mockup sample data into production. Preserve unrelated changes by using canonical task worktrees.

## Work Items

- [ ] Register /app/recoveries under the embedded app layout with independent authentication and RECOVERY_HISTORY authorization before recovery business reads.
- [ ] Add RECOVERY_HISTORY permission only for ACTIVE, NO_CONTRACT, FROZEN and BILLING_ATTENTION; retain every other existing surface rule.
- [ ] Build the date presets/custom range, customer search, status filters and one-recovery-per-row presentation using SHOPIFY-001.
- [ ] Serialize filter and cursor state in safe URLs; reset pagination when filters change and preserve context for future detail navigation.
- [ ] Implement loading, read-error/retry, never-used and filtered-empty states; localize labels and date/money formatting; make row actions keyboard links.

## Interfaces / Contracts

SHOPIFY-001 list DTO and query parser; parent architecture route/access matrix. Keep authenticated embed context intact in links.

## Dependencies

- ARCH-019-SHOPIFY-001

All listed dependencies must be Complete and architect-accepted. Consume actual accepted source revisions; a copied initial task snapshot is not acceptance evidence. The architect must reconcile accepted dependency metadata into this parent task branch before promotion; the prepared launcher gates dependencies from this branch, not directly from sibling worktrees. Unmerged accepted implementation prerequisites require the normal developer integration or explicit approved dependency-commit consumption before this task can use their code.

## Enables

- ARCH-019-SHOPIFY-004
- ARCH-019-SHOPIFY-005
- ARCH-019-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Each visible row represents one recovery, with customer fallback, checkout value, accurate status and started date/time; no opaque database ID is the primary label.
- [ ] All visible filters are functional and backed by server constraints; search/filter navigation cannot introduce cross-tenant reads.
- [ ] No mutation controls or new top-level navigation item are added in this task; detail links are enabled only once SHOPIFY-004 provides the destination.
- [ ] Mobile 320px/390px and desktop 1024px layouts remain usable; labels, focus and empty/error paths are accessible.
- [ ] Locale catalogue parity and ICU syntax hold for every newly added key; no hard-coded English statuses remain.

## Validation

- [ ] Run npm test -- tests/unit/recovery-list-route.test.ts tests/unit/merchant-route-access-policy.test.ts tests/unit/merchant-i18n.test.ts (create the new route suite).
- [ ] Run npm run typecheck, npm run lint and git diff --check; document baseline-only failures.
- [ ] Verify keyboard search/filter/pagination and responsive layout with local deterministic fixtures; record screenshots and actual browser evidence.

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

Execution branch: task/ARCH-019-SHOPIFY-003. Attempt: 0. No implementation claim, worktree, commit or validation is asserted. At execution submission record canonical workspace, both physical worktrees/branches, start-of-attempt synchronization, recursive submodule evidence, implementation and parent commit/push evidence, and confirmation that no parent service Gitlink or main branch was changed.

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
