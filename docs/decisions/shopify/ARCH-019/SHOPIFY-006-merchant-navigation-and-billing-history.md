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
status: review
priority: 70
executor: null
claimed_at: null
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

- [x] Apply the exact state-aware navigation order from the parent architecture: Overview, Recoveries, Billing, Promotions, Support, Recovery settings when allowed; onboarding retains Home and Support.
- [x] Rename merchant-support navigation to localized Support while preserving unread count and existing inbox behaviour.
- [x] Add Billing → Usage history entry using the existing USAGE guard, keep /app/usage URL, and change its breadcrumbs to Billing → Usage history.
- [x] Bound /app/usage period selection to cursor pages of 25 plus one lookahead, retrieve selected period directly by shop, aggregate its usage in SQL, and resolve source recoveries only for the current usage-event page.
- [x] Remove unbounded all-recovery/message-ID hydration and period usageEvents includes from /app/usage; support recovery/conversation/message source IDs with batched tenant-constrained joins and safe unresolved fallback.
- [x] Remove now-unreferenced old UsageOverview/RecoveryChart/Dashboard wiring only after import/test checks; preserve functional billing, promotions, settings and support destinations.

## Interfaces / Contracts

Parent architecture Navigation, Billing bridge and Access sections; existing usage event semantics remain intact. This task owns only bounded read/presentation integration, not the billing engine.

## Dependencies

- ARCH-019-SHOPIFY-005

All listed dependencies must be Complete and architect-accepted. Consume actual accepted source revisions; a copied initial task snapshot is not acceptance evidence. The architect must reconcile accepted dependency metadata into this parent task branch before promotion; the prepared launcher gates dependencies from this branch, not directly from sibling worktrees. Unmerged accepted implementation prerequisites require the normal developer integration or explicit approved dependency-commit consumption before this task can use their code.

## Enables

- ARCH-019-SYSTEM-TEST-001

## Acceptance Criteria

- [x] Every advertised navigation item is allowed by the current server policy; ONBOARDING does not regain billing/history access from stale ARCH-013 prose.
- [x] Frozen/no-contract/billing-attention merchants retain approved history access with mutations unchanged; support-only states see only Support.
- [x] Usage history still supports current/past period and billId selection without exposing another shop’s period or requiring a full period/event history load.
- [x] Existing /app/usage URLs remain functional and old detail redirects do not loop.
- [x] Accounting quantities/period scope remain unchanged; recovery-performance numbers are never substituted for billed usage.
- [x] Old unbounded dashboard paths and full recovery/message debug logging are absent from active overview/history routes.

## Validation

- [x] Run npm test -- tests/unit/merchant-route-access-policy.test.ts tests/unit/usage-route.test.ts tests/unit/home-route.test.ts tests/unit/merchant-i18n.test.ts plus new navigation/link fixtures.
- [x] Run npm run typecheck, npm run lint and git diff --check.
- [x] Developer-owned if long: npm run build against the final implementation revision; record exact result before acceptance.
- [x] Verify navigation and billing history in local browser fixtures for every experience state, including past-period and unknown billId entry.

New test filenames above are required deliverables, not claims that those suites already exist. Use current package.json scripts; do not invent success when a command cannot run. Follow docs/agent-validation-execution-policy.md and docs/agent-live-validation-execution-policy.md: fast local checks are agent-owned; long infrastructure/live commands are developer-owned unless exactly authorized. Required developer evidence may remain pending at review, never at acceptance.

## Stop Condition

After scoped work and agent-owned checks, update this task's Work Items, Acceptance Criteria, Validation and Completion Report, publish task-owned mirrored branches and return to review. Record exact pending developer-validation commands if needed. Stop; do not start enabled tasks, merge/push main, or mark your own task Complete.

## Implementation Notes

Use scripts/start-agent-task.py through the normal /moda-task preparation path. Task creation has not claimed execution. Dedicated parent and implementation worktrees, synchronization and recursive database submodule preparation are mandatory when execution starts. Follow docs/agent-vcs-ownership-policy.md. The repository agent may update only this task's execution/report fields in parent docs; shared indexes and parent architecture remain architect-owned.

## Completion Report

### Status

Attempt 1 implemented and submitted for moda_architect review. No architect acceptance decision has been made by this agent.

### Files Changed

Implementation commit `39054cec8179870b6df2e629b5a23ffacf89a63b` contains the app shell and MerchantNavigation, route access navigation policy, Billing options history entry, usage route and new bounded usage/history.server reader, typed UsageEvents UI/CSS, 20 locale additions, focused unit fixtures and local browser evidence. Removed obsolete Dashboard, Stats, RecoveryChart and UsageOverview after reference checks; replaced UsageEvents.jsx with UsageEvents.tsx.

### Work Completed

- Applied exact state-aware navigation order and localized Home/Overview/Billing/Support; retained unread count and existing destinations. Existing surface permissions and lifecycle mutations are unchanged.
- Added USAGE-guarded Billing entry and Billing → Usage history breadcrumb with validated embed context. Existing /app/usage and accepted legacy bridge behavior remain supported.
- Period selector uses shop/status-scoped keyset pages of 25 plus one, with periodStart/id ordering and validated shop/view-scoped cursors. Explicit owned period lookup is independent of the selector page; missing/foreign/malformed/repeated explicit IDs never select a default.
- Usage events remain offset-paged with a 100-row cap; count and quantity sum are database aggregates. One bounded parameterized query resolves current-page recovery/conversation/message source IDs using tenant-constrained commerce and whatsapp joins. Unresolved or ambiguous sources stay unlinked; message bodies and whole recovery histories are not hydrated.
- Preserved accounting quantity semantics, added localized loading/error/empty/unavailable presentation, and linked identifiable recovery labels to recovery detail.

### Validation Results

Agent-executed against final implementation source:

- `npm test -- tests/unit/merchant-route-access-policy.test.ts tests/unit/usage-route.test.ts tests/unit/home-route.test.ts tests/unit/merchant-i18n.test.ts tests/unit/billing-period-compatibility.test.ts tests/unit/merchant-navigation-history.test.tsx`: **104 passed, six suites**.
- `npm run typecheck`: **fails with 78 existing diagnostics in 20 unchanged files**. No task-owned file diagnostics. Obsolete removed modules account for reduced baseline diagnostics.
- `npm run lint`: **fails with 20 existing errors and two warnings in 15 unchanged files**. No task-owned diagnostics.
- `npm run build`: **passed**, final server build completed in 2.29s. This was a fast local agent-owned build; no pending developer build command.
- `git diff --check`: passed. All 20 locale files retain existing parsed values and add the same 11 keys.
- Local browser fixtures verified all eight experience-state navigation sets, current/past selection, 25-period selector and next page, usage pagination preserving selected bill and embed context, explicit unknown-period unavailable state, linked/unlinked source presentation and recovery destination URL. Desktop 1024px and mobile 320/390px have no document horizontal overflow; table overflow remains in its container. Evidence and reproduction instructions: `tests/browser/usage-history/README.md` and `evidence/`.

Browser fixtures use synthetic loader data and local Shopify link stand-ins. They do not establish live Shopify/App Bridge or real PostgreSQL query execution. SQL schema and joins were checked against the pinned Prisma schema; tenant predicates and bounded query shapes are unit-tested. System-test execution remains manually gated and was not started.

### Deviations

No scope deviation. Repository-wide typecheck/lint are not green because of the unchanged baseline findings above; passing task checks do not imply global success.

### Assumptions

Used the prepared, accepted SHOPIFY-005 dependency and current architecture contracts. No provider API or billing engine behavior changed.

### Unresolved Issues

Existing global typecheck/lint failures remain. No known task-owned defect from focused checks or local browser validation. Live integration evidence belongs to the separately gated system-test task.

### Architectural Concerns

No new concern. Cursor scope validation never substitutes for tenant predicates; every period/event/source read retains shop ownership constraints.

### Git / VCS

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-019-SHOPIFY-006`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-019-SHOPIFY-006`.
- Both branches: `task/ARCH-019-SHOPIFY-006`; execution mode agent, Attempt 1, claimed by codex at `2026-09-20T16:07:30Z`.
- Prepared launcher reused parent and created implementation worktree; fetch/prune/synchronization completed, remote task fast-forward not needed and origin/main already incorporated. Dependency gate passed. Parent initial HEAD `c064ed8a3e76c9b04ee9bbf74fdc36673e97292b`; implementation initial HEAD `5a7d923ce316746e3b6ca470b873a1a19c5031b7`.
- Recursive submodule sync/update verified database at `9c6a4d8402a01840e2ea8dc18e89171f00564d29`; no submodule update --remote used and no database/gitlink change made.
- Durable parent claim committed/pushed: `e1931e83e047759a0d37e8cb8541967977423f6d`.
- Implementation committed/pushed: `39054cec8179870b6df2e629b5a23ffacf89a63b`, origin/task/ARCH-019-SHOPIFY-006 at the configured moda-interact remote.
- This report is committed/pushed on the matching parent task branch; its containing Git commit is the authoritative report revision. Only this task document changes in the parent.
- No parent service Gitlink, shared index, architecture, or main branch changed. No main merge/push, live deployment, or enabled-task execution.

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
