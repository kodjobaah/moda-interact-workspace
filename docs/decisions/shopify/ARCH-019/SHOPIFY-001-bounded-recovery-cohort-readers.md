---
id: ARCH-019-SHOPIFY-001
architecture_id: ARCH-019
title: Implement bounded recovery cohort metrics and list readers
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 20
executor: codex
claimed_at: 2026-09-20T12:12:28Z
attempt: 1
depends_on:
  - ARCH-019-DATABASE-001
enables:
  - ARCH-019-SHOPIFY-003
  - ARCH-019-SHOPIFY-005
  - ARCH-019-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
---

# Implement bounded recovery cohort metrics and list readers

## Architecture

Architecture ID: ARCH-019

Architecture document: docs/architecture/ARCH-019-merchant-recovery-experience.md

Coordinator: moda_architect. Read the complete parent architecture and referenced dependency tasks before execution; it supplies exact data, route, access, compatibility and rollout contracts.

## Objective

Return correct tenant-scoped recovery cohort metrics and cursor pages without loading conversation history.

## Context

This task contributes one bounded capability to the recovery-first merchant journey. The previous UI mixed billing-period navigation, all-time recovery figures and a customer modal. The new design separates recovery performance, recovery conversation history and billing usage.

## Scope

New app/services/recoveries cohort/query/list modules and local DTOs; focused tests; database Gitlink update to the architect-accepted DATABASE-001 commit in this implementation task only.

## Out of Scope

Other repository implementation; billing/credit/provider semantics; new automated messages; reply/takeover controls; unrelated refactoring; main merges/pushes; live deployment. Do not start enabled tasks. Parent architecture/index reconciliation belongs to moda_architect.

## Requirements

The parent architecture's behavioural contracts are binding. Preserve current tenant/lifecycle rules and accepted ARCH-017 onboarding behaviour; do not restore stale ARCH-013 permissions. Follow repo-local AGENTS.md and the assigned logical agent definition. Never copy mockup sample data into production. Preserve unrelated changes by using canonical task worktrees.

## Work Items

- [ ] Implement the shared app-local date/filter parser, merchant-zone half-open cohort predicate and query contracts in the parent architecture.
- [ ] Aggregate cohort counts/statuses and completed checkout values by currency in PostgreSQL with decimal-safe money handling and explicit unknown-value counts.
- [ ] Implement deterministic (detectedAt DESC, id DESC) keyset recovery pages of 25 rows (maximum 50) plus one lookahead, and a five-row overview preview.
- [ ] Implement bounded, parameterized customer name/email search using the architecture-defined semantics, safe projection and shop scope; validate cursor/filter binding.
- [ ] Return a fixed-size summary plus bounded rows; exclude messages, lineItems, checkoutToken, checkoutUrl and accounting identifiers from list DTOs.

## Interfaces / Contracts

App-local recovery-query and recovery-list DTOs from the parent architecture. No new shared package contract or Shopify API call.

## Dependencies

- ARCH-019-DATABASE-001

All listed dependencies must be Complete and architect-accepted. Consume actual accepted source revisions; a copied initial task snapshot is not acceptance evidence. The architect must reconcile accepted dependency metadata into this parent task branch before promotion; the prepared launcher gates dependencies from this branch, not directly from sibling worktrees. Unmerged accepted implementation prerequisites require the normal developer integration or explicit approved dependency-commit consumption before this task can use their code.

## Enables

- ARCH-019-SHOPIFY-003
- ARCH-019-SHOPIFY-005
- ARCH-019-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Summary and preview/list use the same detectedAt cohort; zero denominator produces null rate, not a misleading 0% value.
- [ ] DST boundaries, inclusive date inputs, null money/currency, multiple currencies and end-date exclusion behave as specified.
- [ ] Duplicate timestamps paginate deterministically; malformed or mismatched cursors cannot read another shop or trigger an unbounded fetch.
- [ ] Search does not hydrate all customers/recoveries; aggregate counts ignore list search/status filters, as documented, and rows reflect the filters.
- [ ] Money aggregation retains decimal precision and no cross-currency sum is returned.
- [ ] Accepted index dependency is consumed deliberately without staging a parent-workspace service Gitlink.

## Validation

- [ ] Run npm test -- tests/unit/recovery-cohort-readers.test.ts (create this focused suite).
- [ ] Run npm run typecheck and git diff --check; record existing baseline failures separately.
- [ ] Prove generated query bounds/selects with local tests and supply the exact local PostgreSQL fixture command for query-result validation if the suite requires long infrastructure startup.

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

Execution branch: task/ARCH-019-SHOPIFY-001. Attempt: 0. No implementation claim, worktree, commit or validation is asserted. At execution submission record canonical workspace, both physical worktrees/branches, start-of-attempt synchronization, recursive submodule evidence, implementation and parent commit/push evidence, and confirmation that no parent service Gitlink or main branch was changed.

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
