---
id: ARCH-075-BACKGROUND-012
architecture_id: ARCH-075
title: Moderate bounded customer history on AI handback
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 5
executor: codex
claimed_at: 2026-11-13T21:51:41Z
attempt: 1
depends_on:
  - ARCH-075-BACKGROUND-011
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Moderate bounded customer history on AI handback

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Safely restore eligible customer messages received during human control to the bounded context of a subsequent genuine AI turn.

## Context

Inspected text/audio ingress persists customer messages but returns before AI enqueue during HUMAN control. ModerationTurnGate runs after the AI control/claim guard and currently examines only the current pending turn. Consequently earlier human-mode customer messages have no ALLOW and history correctly excludes them. BG011 separately corrects the delivered merchant prepared-body moderation identity. Neither issue justifies admitting unmoderated rows or guessing the unrelated earlier product referral cause.

## Scope

Background existing AI-owned moderation gate, bounded prior-history candidate selection shared with Commerce history where needed, and directly related unit/disposable PostgreSQL tests. Reuse PostgresModerationAssessmentService canonical CUSTOMER_MESSAGE authority and existing turn retry lifecycle.

## Out of Scope

Eager moderation or AI invocation during HUMAN control, new queues/events/schema/Shared releases, entire-conversation scans, broader history windows, role/prompt redesign, product search, live data mutations/replays/resets and provider operations.

## Requirements

- At the existing AI-owned moderation gate, consider exactly the same prior 20 visible candidate rows as loadCommerceHistory, plus the existing current-turn candidates; deduplicate by message identity. Preserve visibility predicates, chronological/audio completion boundaries and history 32000-character limit. Do not select 20 CUSTOMER rows beyond the existing 20 mixed-history window.
- Assess only persisted inbound CUSTOMER TEXT or COMPLETED AUDIO transcripts via existing assessText(CUSTOMER_MESSAGE). Canonical stored content, exact tenant/conversation, current configured moderation model/policy and immutable assessment/lease identity remain authoritative. No fabricated ALLOW, raw SQL bypass or allowance inferred from human mode.
- No AI enqueue, model answer or provider send while control remains HUMAN. Existing AI control revision/claim/recheck guards remain intact, including a HUMAN switch while backfill is running.
- Existing cached assessment/lease idempotency and turn release/retry scheduling apply. BLOCK and REVIEW_REQUIRED historical rows stay excluded without incorrectly suppressing an otherwise allowed current customer turn. A historical ALLOW alone must not authorize a blocked current turn. Retry behavior must be bounded and explicit; do not silently admit an unassessed row or introduce a retry storm.
- Existing unsupported/untranscribed audio/media handling remains fail-closed. No audio downloads/transcription duplication in this task; completed transcripts use their authoritative completion timestamp and content.
- Both eligible sides of the merchant/customer exchange appear once after normal resume, retaining merchant untrusted-history label and customer role. Preserve existing deduplication/order/current-turn separation. Changes to immutable evidence or cross-service boundaries require return to architect before widening.
- No new telemetry is required unless a concrete diagnostic gap is found. Any changed structured logs use Shared logging and contain bounded identifiers, never full customer content or credentials. Root alone performs deployment/live verification.

### Bounded historical moderation time (architect amendment)

New historical work cannot consume the full 120-second logical processing lease. Pass the actual existing processing-lease deadline from the turn processor's claim timestamp into the moderation gate; do not reconstruct a fresh lease at gate entry or increase lease duration. Historical assessment has an additional elapsed ceiling of twice the existing MODERATION_TIMEOUT_MS (currently16 seconds). Before starting each historical assessment, require a full existing timeout plus a1-second safety margin within both deadlines; otherwise return existing retry/release. Stop historical work on its first RETRY. Current-turn decision remains first and unchanged, and historical BLOCK/review cannot change it.

Reuse immutable cached assessments and existing attempt/backoff caps: subsequent claims traverse cached rows quickly and progress through remaining prior candidates. No new queue/cursor or caller-supplied allowance. Inject a clock for deterministic deadline/progress tests, including slow successful assessments, insufficient actual remaining lease, no assessment after deadline and cached replay progress. Direct helper tests without a processing lease must still enforce the historical elapsed bound; production invocation must supply the real claim deadline. Final source validation follows this amendment; do not repeat superseded expensive checks before code settles.

## Work Items

- [ ] Prove absent human-mode customer assessment/history exclusion with a focused RED.
- [ ] Implement bounded resume-time moderation using existing canonical assessment and retry/control guards.
- [ ] Prove current-turn outcome isolation, audio/content/tenant/policy/model/replay guards and bounded selection.
- [ ] Run actual disposable ingress HUMAN→resume→moderation→history proof with BG011 merchant context, then publish exact source and report.

## Interfaces / Contracts

Existing Background ModerationTurnGate, PostgresModerationAssessmentService, Commerce history visibility/bounds and conversation control/turn lifecycle. No new cross-service contract or schema.

## Dependencies

ARCH-075-BACKGROUND-011 is Complete/Accepted and integrated: Background main ac2ef244a36a63f13cb794bef41a4d7a27207cb2; parent main1309896672d0b80122e99fae30efe8782d995bb9. Normal launcher preparation may now create the implementation worktree and claim this Ready task.

## Enables

Root genuine merchant/customer exchange→AI handback verification. No implicit follow-on task execution.

## Acceptance Criteria

- [ ] A customer message persisted during HUMAN has no AI send then receives exact valid assessment before inclusion on a genuine resumed AI turn.
- [ ] Eligible merchant and customer context appears once with existing roles, bounds and chronological ordering.
- [ ] BLOCK/review/tampered/foreign/stale-model-or-policy/unsupported/incomplete audio remain excluded; historical outcomes cannot authorize or incorrectly suppress current-turn decisions.
- [ ] Control changes during assessment prevent AI send; duplicate/concurrent/retry handling uses existing leases and bounded scheduling.
- [ ] Focused tests, meaningful actual PG flow and required repository checks pass with exact isolation/report evidence.

## Validation

- [ ] RED/GREEN unit vectors covering bounded mixed-history window, deduplication, current-turn outcome isolation, cached/retry evidence and control races.
- [ ] Actual disposable PostgreSQL/Redis ingress→HUMAN persistence→normal resume→existing moderation→history, both exchange sides and completed-audio/negative cases; no hosted DB fallback or fabricated provider permission.
- [ ] Relevant declared full tests, build/type and changed-file lint; disclose only exact unchanged known baseline failures, with diff/privacy checks.

## Stop Condition

Publish mirrored source/report, set review and return to architect. No merge, live mutation or next-task implementation.

## Implementation Notes

Use normal launcher dedicated sibling worktrees. You are not alone: preserve primary changes and other agents. Bounded selection reuse is repository-local domain policy, not a new Shared mechanism. If assessment retry or current-turn isolation requires a different lifecycle mechanism, report it before implementation expansion.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

### Deviations

None

### Assumptions

Root owns integration and live operational verification.

### Unresolved Issues

Actual post-deployment exchange awareness remains to be verified.

### Architectural Concerns

Return any lifecycle/contract gap before widening.

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

ARCH-075 remains In Progress; no live completion claim.
