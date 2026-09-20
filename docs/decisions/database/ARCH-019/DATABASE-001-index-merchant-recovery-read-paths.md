---
id: ARCH-019-DATABASE-001
architecture_id: ARCH-019
title: Index tenant-scoped recovery browsing and transcript pagination
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
  - ARCH-019-SHOPIFY-001
  - ARCH-019-SHOPIFY-002
  - ARCH-019-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
---

# Index tenant-scoped recovery browsing and transcript pagination

## Architecture

Architecture ID: ARCH-019

Architecture document: docs/architecture/ARCH-019-merchant-recovery-experience.md

Coordinator: moda_architect. Read the complete parent architecture and referenced dependency tasks before execution; it supplies exact data, route, access, compatibility and rollout contracts.

## Objective

Provide indexes aligned with the bounded recovery readers without changing durable business semantics.

## Context

This task contributes one bounded capability to the recovery-first merchant journey. The previous UI mixed billing-period navigation, all-time recovery figures and a customer modal. The new design separates recovery performance, recovery conversation history and billing usage.

## Scope

prisma/schema.prisma; one additive migration; focused schema/migration validation; generated schema documentation where required by the repository.

## Out of Scope

Other repository implementation; billing/credit/provider semantics; new automated messages; reply/takeover controls; unrelated refactoring; main merges/pushes; live deployment. Do not start enabled tasks. Parent architecture/index reconciliation belongs to moda_architect.

## Requirements

The parent architecture's behavioural contracts are binding. Preserve current tenant/lifecycle rules and accepted ARCH-017 onboarding behaviour; do not restore stale ARCH-013 permissions. Follow repo-local AGENTS.md and the assigned logical agent definition. Never copy mockup sample data into production. Preserve unrelated changes by using canonical task worktrees.

## Work Items

- [ ] Add CheckoutRecovery B-tree indexes on (shopId, detectedAt, id), (shopId, status, detectedAt, id), and (shopId, customerId, detectedAt, id); ascending definitions may serve matching reverse traversal.
- [ ] Add ConversationMessage index on (conversationId, createdAt, id) for deterministic transcript traversal. Retain existing indexes unless equivalence and all consumers are proven; no unrelated index cleanup.
- [ ] Inspect the exact accepted schema before editing; do not duplicate equivalent indexes if an intervening accepted migration already added them.
- [ ] Document migration application and index-only rollback, lock/build behaviour, and the accepted database commit for downstream nested Gitlink consumption.

## Interfaces / Contracts

Architecture sections Query contract, Data architecture and Rollout. Existing CheckoutRecovery and ConversationMessage ownership remains unchanged.

## Dependencies

None.

All listed dependencies must be Complete and architect-accepted. Consume actual accepted source revisions; a copied initial task snapshot is not acceptance evidence. The architect must reconcile accepted dependency metadata into this parent task branch before promotion; the prepared launcher gates dependencies from this branch, not directly from sibling worktrees. Unmerged accepted implementation prerequisites require the normal developer integration or explicit approved dependency-commit consumption before this task can use their code.

## Enables

- ARCH-019-SHOPIFY-001
- ARCH-019-SHOPIFY-002
- ARCH-019-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Migration is additive, preserves all rows/constraints and can be applied to an existing populated schema.
- [ ] The migration and Prisma schema describe equivalent index definitions with deterministic query tie-breakers.
- [ ] Representative two-tenant, status-filtered, related-customer and transcript queries have recorded EXPLAIN plans on a sufficiently populated local fixture; no fabricated throughput or forced index-selection claims.
- [ ] No new entity, provider interaction, billing rule or queue payload is introduced.

## Validation

- [ ] Run npm run prisma:validate and git diff --check.
- [ ] Add and run a bounded schema-contract check covering the required columns/order and additive migration.
- [ ] Developer-owned: apply the migration to an isolated populated PostgreSQL fixture and record exact command, exit code and EXPLAIN (ANALYZE, BUFFERS) evidence. Do not access shared databases without exact authorization.

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

Execution branch: task/ARCH-019-DATABASE-001. Attempt: 0. No implementation claim, worktree, commit or validation is asserted. At execution submission record canonical workspace, both physical worktrees/branches, start-of-attempt synchronization, recursive submodule evidence, implementation and parent commit/push evidence, and confirmation that no parent service Gitlink or main branch was changed.

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
