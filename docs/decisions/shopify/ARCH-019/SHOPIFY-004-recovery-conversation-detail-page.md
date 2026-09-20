---
id: ARCH-019-SHOPIFY-004
architecture_id: ARCH-019
title: Build the read-only recovery conversation page
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 50
executor: codex
claimed_at: 2026-09-20T13:26:33Z
attempt: 1
depends_on:
  - ARCH-019-SHOPIFY-002
  - ARCH-019-SHOPIFY-003
enables:
  - ARCH-019-SHOPIFY-005
  - ARCH-019-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
---

# Build the read-only recovery conversation page

## Architecture

Architecture ID: ARCH-019

Architecture document: docs/architecture/ARCH-019-merchant-recovery-experience.md

Coordinator: moda_architect. Read the complete parent architecture and referenced dependency tasks before execution; it supplies exact data, route, access, compatibility and rollout contracts.

## Objective

Open a recovery directly into an accessible conversation with checkout context and related recoveries.

## Context

This task contributes one bounded capability to the recovery-first merchant journey. The previous UI mixed billing-period navigation, all-time recovery figures and a customer modal. The new design separates recovery performance, recovery conversation history and billing usage.

## Scope

app/routes.ts; new recovery detail/resource route modules and transcript/context components; recovery list link activation; focused tests and merchant locales.

## Out of Scope

Other repository implementation; billing/credit/provider semantics; new automated messages; reply/takeover controls; unrelated refactoring; main merges/pushes; live deployment. Do not start enabled tasks. Parent architecture/index reconciliation belongs to moda_architect.

## Requirements

The parent architecture's behavioural contracts are binding. Preserve current tenant/lifecycle rules and accepted ARCH-017 onboarding behaviour; do not restore stale ARCH-013 permissions. Follow repo-local AGENTS.md and the assigned logical agent definition. Never copy mockup sample data into production. Preserve unrelated changes by using canonical task worktrees.

## Work Items

- [ ] Register /app/recoveries/:recoveryId with its own RECOVERY_HISTORY guard; use sibling routes or an outlet-only layout so the list loader is not unnecessarily run for detail.
- [ ] Render chronological chat bubbles with explicit sender labels, merchant-zone date separators and applicable recorded delivery metadata.
- [ ] Implement bounded message navigation and Jump to latest, plus the same-customer related-recovery selector using SHOPIFY-002.
- [ ] Provide Back to recoveries preserving validated list filters/cursor and router scroll restoration; direct links use a safe default list.
- [ ] Add desktop context column, compact mobile summary and secondary context, no-conversation/unsupported-message and section-local failure/retry states.

## Interfaces / Contracts

SHOPIFY-002 detail/transcript DTOs and SHOPIFY-003 RECOVERY_HISTORY/list context; do not widen lifecycle permissions.

## Dependencies

- ARCH-019-SHOPIFY-002
- ARCH-019-SHOPIFY-003

All listed dependencies must be Complete and architect-accepted. Consume actual accepted source revisions; a copied initial task snapshot is not acceptance evidence. The architect must reconcile accepted dependency metadata into this parent task branch before promotion; the prepared launcher gates dependencies from this branch, not directly from sibling worktrees. Unmerged accepted implementation prerequisites require the normal developer integration or explicit approved dependency-commit consumption before this task can use their code.

## Enables

- ARCH-019-SHOPIFY-005
- ARCH-019-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Opening a recovery never requires a modal or an extra recovery dropdown step.
- [ ] Switching between a customer’s baskets preserves the original list return context; query parameters cannot become an arbitrary external return URL.
- [ ] Transcript remains read-only; no reply, takeover, retry-send, cancellation or new provider call is introduced.
- [ ] Message text is escaped and direction-aware; safe links exclude dangerous schemes; unknown data is represented honestly.
- [ ] Keyboard navigation, long text/URLs, translated labels and RTL content fit narrow layouts without nested modal scrolling.
- [ ] Detail/resource routes independently enforce authorization; foreign IDs look unavailable and never disclose another shop’s name.

## Validation

- [ ] Run npm test -- tests/unit/recovery-detail-route.test.ts tests/unit/recovery-detail-readers.test.ts tests/unit/merchant-route-access-policy.test.ts tests/unit/merchant-i18n.test.ts.
- [ ] Run npm run typecheck, npm run lint and git diff --check.
- [ ] Use local browser fixtures to verify list → detail → related recovery → Back, reload/direct link, 100+ messages, keyboard operation and narrow layout.

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

Execution branch: task/ARCH-019-SHOPIFY-004. Attempt: 0. No implementation claim, worktree, commit or validation is asserted. At execution submission record canonical workspace, both physical worktrees/branches, start-of-attempt synchronization, recursive submodule evidence, implementation and parent commit/push evidence, and confirmation that no parent service Gitlink or main branch was changed.

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
