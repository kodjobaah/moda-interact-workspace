---
id: ARCH-019-SYSTEM-TEST-001
architecture_id: ARCH-019
title: Validate the integrated merchant recovery experience
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 80
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-019-DATABASE-001
  - ARCH-019-SHOPIFY-001
  - ARCH-019-SHOPIFY-002
  - ARCH-019-SHOPIFY-003
  - ARCH-019-SHOPIFY-004
  - ARCH-019-SHOPIFY-005
  - ARCH-019-SHOPIFY-006
enables: []
created: 2026-09-20
updated: 2026-09-20
---

# Validate the integrated merchant recovery experience

## Architecture

Architecture ID: ARCH-019

Architecture document: docs/architecture/ARCH-019-merchant-recovery-experience.md

Coordinator: moda_architect. Read the complete parent architecture and referenced dependency tasks before execution; it supplies exact data, route, access, compatibility and rollout contracts.

## Objective

Prove the complete merchant recovery journey and tenant/lifecycle boundaries against the accepted implementation.

## Context

This task contributes one bounded capability to the recovery-first merchant journey. The previous UI mixed billing-period navigation, all-time recovery figures and a customer modal. The new design separates recovery performance, recovery conversation history and billing usage.

## Scope

Architecture-specific system scenario/evidence harness, local fixtures and documentation in moda-interact-system-test; no implementation repository fixes.

## Out of Scope

Other repository implementation; billing/credit/provider semantics; new automated messages; reply/takeover controls; unrelated refactoring; main merges/pushes; live deployment. Do not start enabled tasks. Parent architecture/index reconciliation belongs to moda_architect.

## Requirements

The parent architecture's behavioural contracts are binding. Preserve current tenant/lifecycle rules and accepted ARCH-017 onboarding behaviour; do not restore stale ARCH-013 permissions. Follow repo-local AGENTS.md and the assigned logical agent definition. Never copy mockup sample data into production. Preserve unrelated changes by using canonical task worktrees.

## Work Items

- [ ] Create repeatable fixtures for two shops, guest and multiple-basket customers, multiple currencies, date/DST boundaries, null values, all message sender/content/status states, >50 recoveries and >100 messages.
- [ ] Provide a documented deterministic scenario for Overview → filtered list → detail → related recovery → Back, plus direct links, reloads, first/latest transcript windows and billing-history legacy entry.
- [ ] Cover all lifecycle restrictions, foreign recovery/cursor/period attacks and read-only behaviour without real outbound Shopify/Meta/LLM effects.
- [ ] Capture responsive and keyboard evidence, translated/RTL samples, bounded response/query counts, and the exact database/app revisions and environment.
- [ ] Register and document the new validator command in package.json if no existing command fits; identify local vs deployed execution explicitly and redact evidence.

## Interfaces / Contracts

All ARCH-019 contracts and accepted implementation commits. Terminal manual gate; no non-system-test task may depend on this task.

## Dependencies

- ARCH-019-DATABASE-001
- ARCH-019-SHOPIFY-001
- ARCH-019-SHOPIFY-002
- ARCH-019-SHOPIFY-003
- ARCH-019-SHOPIFY-004
- ARCH-019-SHOPIFY-005
- ARCH-019-SHOPIFY-006

All listed dependencies must be Complete and architect-accepted. Consume actual accepted source revisions; a copied initial task snapshot is not acceptance evidence. The architect must reconcile accepted dependency metadata into this parent task branch before promotion; the prepared launcher gates dependencies from this branch, not directly from sibling worktrees. Unmerged accepted implementation prerequisites require the normal developer integration or explicit approved dependency-commit consumption before this task can use their code.

## Enables

None; terminal validation feeds architect completion.

## Acceptance Criteria

- [ ] All implementation dependencies are Complete and architect-accepted before this task becomes Ready; explicit developer invocation is still required to claim it.
- [ ] Integrated evidence demonstrates date/metric correctness, cross-shop denial, all supported historical states, preserved billing behaviour and bounded pagination.
- [ ] 320px/390px/1024px layouts, keyboard focus, error/empty states and readable transcript ordering are demonstrated with real browser evidence.
- [ ] No real customer message is sent, no billing mutation is performed and no production/shared resource is altered by default.
- [ ] Failures are routed to the owning existing implementation task; the system-test agent does not silently repair application/database code.

## Validation

- [ ] Run npm test, npm run typecheck, npm run lint and git diff --check for local harness checks as appropriate to changed files.
- [ ] Developer-owned: execute the documented architecture scenario after accepted deployment/fixture setup and provide exact command, revision, result and exit code.
- [ ] Live execution requires current authorization for the exact command/environment under the live-validation policy; Ready alone is not permission.

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

Execution branch: task/ARCH-019-SYSTEM-TEST-001. Attempt: 0. No implementation claim, worktree, commit or validation is asserted. At execution submission record canonical workspace, both physical worktrees/branches, start-of-attempt synchronization, recursive submodule evidence, implementation and parent commit/push evidence, and confirmation that no parent service Gitlink or main branch was changed.

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
