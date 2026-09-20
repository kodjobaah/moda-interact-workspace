---
id: ARCH-019-SHOPIFY-006
architecture_id: ARCH-019
title: Align merchant navigation and bounded billing-history access
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 70
executor: codex
claimed_at: 2026-09-20T16:07:30Z
attempt: 1
depends_on:
  - ARCH-019-SHOPIFY-005
enables:
  - ARCH-019-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
---

# Align merchant navigation and bounded billing-history access

## Architecture

Architecture ID: ARCH-019

Architecture document: docs/architecture/ARCH-019-merchant-recovery-experience.md

Coordinator: moda_architect. Read the complete parent architecture and referenced dependency tasks before execution; it supplies exact data, route, access, compatibility and rollout contracts.

## Objective

Complete the navigation separation between recovery performance, billing usage and merchant support.

## Context

This task contributes one bounded capability to the recovery-first merchant journey. The previous UI mixed billing-period navigation, all-time recovery figures and a customer modal. The new design separates recovery performance, recovery conversation history and billing usage.

## Scope

App shell/navigation policy; /app/usage loader and breadcrumbs; Billing options history entry link; UsageEvents source recovery links; obsolete dashboard modules only after reference checks; focused tests and locales.

## Out of Scope

Other repository implementation; billing/credit/provider semantics; new automated messages; reply/takeover controls; unrelated refactoring; main merges/pushes; live deployment. Do not start enabled tasks. Parent architecture/index reconciliation belongs to moda_architect.

## Requirements

The parent architecture's behavioural contracts are binding. Preserve current tenant/lifecycle rules and accepted ARCH-017 onboarding behaviour; do not restore stale ARCH-013 permissions. Follow repo-local AGENTS.md and the assigned logical agent definition. Never copy mockup sample data into production. Preserve unrelated changes by using canonical task worktrees.

## Work Items

- [ ] Apply the exact state-aware navigation order from the parent architecture: Overview, Recoveries, Billing, Promotions, Support, Recovery settings when allowed; onboarding retains Home and Support.
- [ ] Rename merchant-support navigation to localized Support while preserving unread count and existing inbox behaviour.
- [ ] Add Billing → Usage history entry using the existing USAGE guard, keep /app/usage URL, and change its breadcrumbs to Billing → Usage history.
- [ ] Bound /app/usage period selection to cursor pages of 25 plus one lookahead, retrieve selected period directly by shop, aggregate its usage in SQL, and resolve source recoveries only for the current usage-event page.
- [ ] Remove unbounded all-recovery/message-ID hydration and period usageEvents includes from /app/usage; support recovery/conversation/message source IDs with batched tenant-constrained joins and safe unresolved fallback.
- [ ] Remove now-unreferenced old UsageOverview/RecoveryChart/Dashboard wiring only after import/test checks; preserve functional billing, promotions, settings and support destinations.

## Interfaces / Contracts

Parent architecture Navigation, Billing bridge and Access sections; existing usage event semantics remain intact. This task owns only bounded read/presentation integration, not the billing engine.

## Dependencies

- ARCH-019-SHOPIFY-005

All listed dependencies must be Complete and architect-accepted. Consume actual accepted source revisions; a copied initial task snapshot is not acceptance evidence. The architect must reconcile accepted dependency metadata into this parent task branch before promotion; the prepared launcher gates dependencies from this branch, not directly from sibling worktrees. Unmerged accepted implementation prerequisites require the normal developer integration or explicit approved dependency-commit consumption before this task can use their code.

## Enables

- ARCH-019-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Every advertised navigation item is allowed by the current server policy; ONBOARDING does not regain billing/history access from stale ARCH-013 prose.
- [ ] Frozen/no-contract/billing-attention merchants retain approved history access with mutations unchanged; support-only states see only Support.
- [ ] Usage history still supports current/past period and billId selection without exposing another shop’s period or requiring a full period/event history load.
- [ ] Existing /app/usage URLs remain functional and old detail redirects do not loop.
- [ ] Accounting quantities/period scope remain unchanged; recovery-performance numbers are never substituted for billed usage.
- [ ] Old unbounded dashboard paths and full recovery/message debug logging are absent from active overview/history routes.

## Validation

- [ ] Run npm test -- tests/unit/merchant-route-access-policy.test.ts tests/unit/usage-route.test.ts tests/unit/home-route.test.ts tests/unit/merchant-i18n.test.ts plus new navigation/link fixtures.
- [ ] Run npm run typecheck, npm run lint and git diff --check.
- [ ] Developer-owned if long: npm run build against the final implementation revision; record exact result before acceptance.
- [ ] Verify navigation and billing history in local browser fixtures for every experience state, including past-period and unknown billId entry.

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

Execution branch: task/ARCH-019-SHOPIFY-006. Attempt: 0. No implementation claim, worktree, commit or validation is asserted. At execution submission record canonical workspace, both physical worktrees/branches, start-of-attempt synchronization, recursive submodule evidence, implementation and parent commit/push evidence, and confirmation that no parent service Gitlink or main branch was changed.

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
