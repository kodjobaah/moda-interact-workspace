---
id: ARCH-076-BACKGROUND-001
architecture_id: ARCH-076
title: Allocate immutable conversation senders under recipient serialization
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 20
executor: codex
claimed_at: 2026-11-15T14:04:07Z
attempt: 1
depends_on: [ARCH-076-DATABASE-001]
enables: [ARCH-076-BACKGROUND-002]
created: 2026-11-13
updated: 2026-11-15
---

# Allocate immutable conversation senders under recipient serialization

## Architecture

[ARCH-076](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md), coordinator moda_architect.

## Objective

Allocate immutable conversation senders under recipient serialization.

## Context

15 November user-selected design retains five explicit sender entities plus the R15 evidence amendment. Sender attribution and conversation-credit renewal are independent streams. The user has authorized implementation of this reviewed design. Preserve prepared claims; execute only through the owning task launcher and accepted dependency frontier.

## Scope

Owning Background services and focused unit/provider-fixture/disposable PostgreSQL tests.

## Out of Scope

Other repository implementation, live settings, production migration and activation. Sender tasks must not implement allowance renewal; allowance tasks must not implement sender allocation. The SYSTEM-TEST task is deferred at the user's request.

## Requirements

- [x] Use inventory, explicit recipient/sender Thread, shop Route, immutable Conversation Assignment and unresolved RoutingTurn from the parent exact schema.
- [x] Preserve Conversation.checkoutRecoveryId uniqueness and existing recovery/consent/history/STOP semantics.
- [x] Never filter ownership candidates or select another checkout based on credits, allowance, model capacity or paid plan.
- [x] Use one transaction-scoped advisory lock keyed canonical recipient across replicas; lock ordering is recipient then local owner records.
- [x] Reuse live same-shop route and add immutable assignment even on drained sender; otherwise choose enabled verified sender with fewest distinct live shops for recipient, then priority and phone ID C order.
- [x] Release only terminal/expired assignment; close route after last live assignment and thread after last live route under recipient serialization. Never move pending originals to a new generation or reset history.
- [x] Handle last-assignment release racing same-shop/new-shop allocation; zero enabled inventory uses existing original-attempt capacity repair marker without new outreach identity.

## Work Items

- [x] Inspect the exact latest accepted repository pin and existing owning mechanisms.
- [x] Implement only this task's scope and requirements.
- [x] Complete the focused checks below and record exact commands and evidence.
- [x] Return the isolated implementation branch and parent Completion Report for review.

## Interfaces / Contracts

The parent architecture's Explicit sender storage, Independent allowance storage and Configurable routing sections are authoritative. Existing published Shared remains reusable structural machinery. Applications own routing, funding, eligibility and authorization. Do not add compatibility paths for the superseded three-table draft or an unreviewed schema.

## Dependencies

ARCH-076-DATABASE-001

## Enables

Recalculate from dependent task metadata after architect acceptance; no implicit implementation handoff.

## Acceptance Criteria

- [x] Use inventory, explicit recipient/sender Thread, shop Route, immutable Conversation Assignment and unresolved RoutingTurn from the parent exact schema.
- [x] Preserve Conversation.checkoutRecoveryId uniqueness and existing recovery/consent/history/STOP semantics.
- [x] Never filter ownership candidates or select another checkout based on credits, allowance, model capacity or paid plan.
- [x] Use one transaction-scoped advisory lock keyed canonical recipient across replicas; lock ordering is recipient then local owner records.
- [x] Reuse live same-shop route and add immutable assignment even on drained sender; otherwise choose enabled verified sender with fewest distinct live shops for recipient, then priority and phone ID C order.
- [x] Release only terminal/expired assignment; close route after last live assignment and thread after last live route under recipient serialization. Never move pending originals to a new generation or reset history.
- [x] Handle last-assignment release racing same-shop/new-shop allocation; zero enabled inventory uses existing original-attempt capacity repair marker without new outreach identity.

## Validation

- [x] Focused unit tests for every requirement, lint/typecheck/build as declared for changed code.
- [x] Disposable PostgreSQL race/replay/restart tests with two recipients, two shops, multiple checkouts and shared sender.
- [x] Provider HTTP fixtures for exact sender, failed initial delivery, unknown result, duplicate/foreign statuses and no network inside transactions.

Inspect the repository package.json before selecting actual commands. Required disposable PostgreSQL checks are task-local repository checks, not execution of the deferred system-test task. No live customer/provider calls belong to these checks.

## Stop Condition

After Work Items, Acceptance Criteria and Validation pass, set review, return the Completion Report and STOP. Do not execute another task or deploy.

## Implementation Notes

Existing published Shared remains reusable structural machinery. Applications own routing, funding, eligibility and authorization. Do not add compatibility paths for the superseded three-table draft or an unreviewed schema.

## Completion Report

### Status

Ready for Review. All required owner-scope checks passed; source and report committed/pushed for architect review.

### Files Changed

- `src/services/recovery-sender-pool/recipient-lock.ts` and `sender-pool.service.ts`.
- Shopify recovery initiation, Woo initial outreach service/adapter and existing recovery-expiry cleanup.
- Task-local PostgreSQL allocation/race tests and focused recipient-lock, initial hold and lifecycle regression tests.
- Package test script and `docs/architecture/arch076-sender-allocation.md`.
- Nested Database gitlink consumes accepted D001 main `a7c204618c6b0ad83952a7b661482cfd03acf899`.
- Authorized validation-only cleanup removes one unused import and three unreferenced obsolete offer-budget constants in preexisting baseline files; no runtime/configuration values changed.

### Work Completed

- Actual allocation/release service serializes by canonical recipient across replicas. Stable Conversation owner locks precede recovery locks; owner lookup uses live-recipient assignment IDs rather than an all-Conversation correlated scan.
- Same-shop live route and existing Conversation assignment stay immutable, including drained inventory and current-credential configuration outages. A different recipient cannot take over an existing assignment. No new Conversation, history reset or allowance/credit/model/plan predicate.
- New routes select enabled verified inventory from the server-validated current WABA only, ranked by distinct live shops for this recipient, priority and C-collated phone ID. Configuration is validated/unsealed outside locks. A new route requires the same deployment/row/version under FOR SHARE, fencing concurrent credential-account CAS. No provider/model/Redis I/O inside transactions.
- Inclusive lifetime/terminal release closes only the last live route/thread generation. Future-dated activity alone is not expiry. Allocation and explicit release share the same recipient lock; the existing expiry tick reconciles terminal cleanup after crashes without a new worker.
- Shopify and Woo initial gates allocate before new credit/provider admission. Zero inventory marks only the same unsent initial attempt CAPACITY_BLOCKED with bounded SENDER_INVENTORY_UNAVAILABLE reason and existing recovery capacity-repair marker. Success clears only that inventory-owned marker; retry preserves attempt/Conversation identity.
- Existing consent, STOP, mode, service-window and final permit checks remain authoritative. Allocation is not send permission or contacted-candidate proof. Exact provider dispatch sender/status, failed/unknown initial contact evidence are explicitly handed to BACKGROUND002/003 rather than duplicated here; root confirmed that scope division.

### Validation Results

- Focused affected initial/expiry/Woo checks: 102 passed.
- Expanded affected checkout-recovery/Woo suites plus new recipient serialization unit checks: 41 files, 564 tests passed.
- `npm run test:arch076-sender-pool:postgres`: 12 passed against the actual service on disposable full-migration PostgreSQL. Covers same-shop concurrent allocation, drain/restart immutable identity, least-load/priority/C ordering, independent recipients, actual last-member release racing same/new-shop allocation, live siblings, inclusive expiry/future activity, terminal restart repair, zero-inventory same-attempt no-reservation/no-provider hold and success cleanup, foreign WABA exclusion, current-account CAS blocked-session fence and configuration outage reuse. Runner removed owned infrastructure.
- First PostgreSQL run had one fixture-only duplicate Shop ID under Promise.all; fixture IDs corrected before final passing runs. Earlier 10/11 and 11/11 runs are superseded by final 12/12.
- Initial `npx tsc --noEmit`: passed. Final `npm run lint` and `npm run build` passed (exit0) on the committed tree. Build includes Prisma generation, source TypeScript and provisioning TypeScript. Final19 expiry/recipient tests passed after the tiny cutoff cleanup edit; generated build output contains that edit (source14:24:39, compiled14:25:53). Interrupted/failed checks are not counted as passing.
- `git diff --check`: passed. No hosted database, provider/customer call, live settings, deployment, Shared publication or deferred SYSTEM-TEST execution.

### Physical Worktree and Publication Evidence

- Canonical primary workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-076-BACKGROUND-001`; implementation: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-076-BACKGROUND-001`.
- Both task branches: `task/ARCH-076-BACKGROUND-001`. Shared/default checkouts not switched/mutated; no other task worktree reused.
- Prepared packet `/tmp/arch076-background001-prepared.json`: both worktrees newly created; remote task fast-forward not-needed; origin/main already-current; recursive submodule sync/update/status ready at recorded Database6f42b711. Claim15ed711ce attempt1, executorcodex, claimed2026-11-15T14:04:07Z, committed/pushed by launcher. No repeated preparation or claim.
- Root explicitly authorized nested Database update to accepted D001a7c2046. No Database source edited or parent gitlink staged by this repository agent.
- Implementation commit `f8d8e418049d081856e52a2d01e4e8ee3b7c48b6` committed/pushed on the task branch. Source PR publication and parent report commit follow below. Root owns all main merges and acceptance; no acceptance decision is made by this agent.

### Deviations

Provider HTTP sender/status behavior belongs to subsequent BACKGROUND002/003; task-local allocation fixtures prove database-only/no-send hold and retry behavior. Root approved this boundary and the bounded unused-symbol lint cleanup. No scope expansion into allowance accounting. Subsequent BG002 handoff must include the newly reconciled PR1071 old-singleton/nonpooled provider-admission fences before any pool inventory is enabled.

### Assumptions

Current verified inventory is authored by ADMIN001. Provider send time revalidates pinned sender credential membership in BACKGROUND002. Existing policy, consent and lifecycle services remain authoritative.

### Unresolved Issues

None within allocation ownership; final checks passed. Runtime activation remains root-owned after dependent sender transport/routing tasks and test verification. Do not enable an empty/partial test pool during this task.

### Architectural Concerns

Independent BG005 funding changes may advance the nested Database pin beyond D001; accepted combined integration must preserve that later pin and rerun relevant checks. This branch does not implement funding or provider dispatch.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Awaiting implementation.

### Follow-up

None.

## Reconciliation provenance — 15 November 2026

Reconciled from the later local sender-pool revision formerly labelled ARCH-069. The completed chronological-input architecture and its ARCH-069 task identities are unchanged. ARCH-076 was already reserved for the earlier sender-pool proposal; this revision updates that proposal in place, retaining its Git history. These are definition changes, not implementation or deployment evidence. All execution remains Pending until compatibility review and dependency promotion.


### 15 November definition amendment

Historical fixed SQL must be regenerated for the restored five-entity contract plus R15 evidence; hardcoded router policy remains superseded. Historical claim/review evidence above is retained as history, not approval of the replacement implementation. No runtime source or migration has been implemented. User has authorized implementation; runtime acceptance and rollout verification remain pending.
