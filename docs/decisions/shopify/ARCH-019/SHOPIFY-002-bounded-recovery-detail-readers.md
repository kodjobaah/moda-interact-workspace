---
id: ARCH-019-SHOPIFY-002
architecture_id: ARCH-019
title: Implement tenant-scoped recovery detail and transcript readers
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 30
executor: codex
claimed_at: 2026-09-20T12:08:03Z
attempt: 1
depends_on:
  - ARCH-019-DATABASE-001
enables:
  - ARCH-019-SHOPIFY-004
  - ARCH-019-SYSTEM-TEST-001
created: 2026-09-20
updated: 2026-09-20
---

# Implement tenant-scoped recovery detail and transcript readers

## Architecture

Architecture ID: ARCH-019

Architecture document: docs/architecture/ARCH-019-merchant-recovery-experience.md

Coordinator: moda_architect. Read the complete parent architecture and referenced dependency tasks before execution; it supplies exact data, route, access, compatibility and rollout contracts.

## Objective

Read one owned recovery and bounded conversation context without exposing unrelated or cross-shop data.

## Context

This task contributes one bounded capability to the recovery-first merchant journey. The previous UI mixed billing-period navigation, all-time recovery figures and a customer modal. The new design separates recovery performance, recovery conversation history and billing usage.

## Scope

New app/services/recoveries detail/transcript/related-read modules and local DTOs; focused tests; accepted database dependency synchronization as needed.

## Out of Scope

Other repository implementation; billing/credit/provider semantics; new automated messages; reply/takeover controls; unrelated refactoring; main merges/pushes; live deployment. Do not start enabled tasks. Parent architecture/index reconciliation belongs to moda_architect.

## Requirements

The parent architecture's behavioural contracts are binding. Preserve current tenant/lifecycle rules and accepted ARCH-017 onboarding behaviour; do not restore stale ARCH-013 permissions. Follow repo-local AGENTS.md and the assigned logical agent definition. Never copy mockup sample data into production. Preserve unrelated changes by using canonical task worktrees.

## Work Items

- [ ] Apply the accepted DATABASE-001 plan finding: resolve the owned recovery/conversation once, then paginate messages using equality-bound conversationId and createdAt/id keys (or prove an equivalent bounded plan). Avoid the fixture's join-driven sort over 760/1,000 messages and repeated ownership lookup; retain tenant authorization and fixed query count.

- [ ] Load recovery by authenticated shopId plus recoveryId, then constrain every transcript/related read through that owned recovery.
- [ ] Provide first/next/previous/latest transcript windows of 50 messages with chronological display and (createdAt,id) tie-breaking.
- [ ] Map all sender/status/content enum values honestly, including AUTOMATION, HUMAN, AUDIO and unavailable/rejected/failed transcription; expose only safe merchant-facing content and recorded delivery evidence.
- [ ] Read related recoveries for the same shop/customer in pages of five, excluding the current recovery; do not group guest/null customer records.
- [ ] Project recorded recovery timestamps and allowlisted milestone reasons, not arbitrary statusHistory metadata, provider IDs or internal diagnostics.

## Interfaces / Contracts

Parent architecture Detail contract. Reuse existing persisted schema and merchant-local date formatting; do not reconstruct absent runtime events.

## Dependencies

- ARCH-019-DATABASE-001

All listed dependencies must be Complete and architect-accepted. Consume actual accepted source revisions; a copied initial task snapshot is not acceptance evidence. The architect must reconcile accepted dependency metadata into this parent task branch before promotion; the prepared launcher gates dependencies from this branch, not directly from sibling worktrees. Unmerged accepted implementation prerequisites require the normal developer integration or explicit approved dependency-commit consumption before this task can use their code.

## Enables

- ARCH-019-SHOPIFY-004
- ARCH-019-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] Missing and foreign recovery identifiers produce indistinguishable unavailable results after authentication.
- [ ] Forged cursors, conversation IDs or customer IDs cannot cross tenant boundaries; no unbounded nested relation include exists.
- [ ] First/latest and adjacent message windows have stable ordering for tied timestamps; newest messages do not make previously visited windows duplicate older records.
- [ ] Inbound message statuses are not misrepresented as outbound delivery receipts; unknown sender and missing metadata are not invented.
- [ ] No provider media URLs, raw media IDs, credentials, internal prompts or arbitrary metadata leak into response DTOs.
- [ ] A recovery without a conversation, a guest recovery and a long/multilingual transcript have valid bounded responses.

## Validation

- [ ] Record representative local EXPLAIN (ANALYZE, BUFFERS) for actual chronological/latest reader queries on a long transcript; demonstrate index cursor traversal without work proportional to the entire transcript. Follow the existing developer-owned execution policy for long rehearsals.

- [ ] Run npm test -- tests/unit/recovery-detail-readers.test.ts (create this focused suite).
- [ ] Run npm run typecheck and git diff --check.
- [ ] Use local fixtures for two-shop access, tied timestamps, all sender/content states and >100-message windows; do not call Meta or Shopify.

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

Execution branch: task/ARCH-019-SHOPIFY-002. Attempt: 0. No implementation claim, worktree, commit or validation is asserted. At execution submission record canonical workspace, both physical worktrees/branches, start-of-attempt synchronization, recursive submodule evidence, implementation and parent commit/push evidence, and confirmation that no parent service Gitlink or main branch was changed.

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
