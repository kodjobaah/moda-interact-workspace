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
status: complete
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

### Startup fixture correction (architect amendment)

The existing arch047-meta-messaging-startup unit intentionally mocks runtime lifecycles under fake timers to test scheduler start/close, but omitted startMultipartRepair and imported the real DB/runtime graph. Two full runs timed out while the isolated test passed. Permit only a test-local multipart lifecycle stub with exactly-once start/close assertions alongside unchanged due/pending-repair checks. No production startup edits, timeout increase or policy waiver. Record observed failure and final rerun.

## Work Items

- [x] Prove absent human-mode customer assessment/history exclusion with a focused RED.
- [x] Implement bounded resume-time moderation using existing canonical assessment and retry/control guards.
- [x] Prove current-turn outcome isolation, audio/content/tenant/policy/model/replay guards and bounded selection.
- [x] Run actual disposable ingress HUMAN→resume→moderation→history proof with BG011 merchant context, then publish exact source and report.

## Interfaces / Contracts

Existing Background ModerationTurnGate, PostgresModerationAssessmentService, Commerce history visibility/bounds and conversation control/turn lifecycle. No new cross-service contract or schema.

## Dependencies

ARCH-075-BACKGROUND-011 is Complete/Accepted and integrated: Background main ac2ef244a36a63f13cb794bef41a4d7a27207cb2; parent main1309896672d0b80122e99fae30efe8782d995bb9. Normal launcher preparation may now create the implementation worktree and claim this Ready task.

## Enables

Root genuine merchant/customer exchange→AI handback verification. No implicit follow-on task execution.

## Acceptance Criteria

- [x] A customer message persisted during HUMAN has no AI send then receives exact valid assessment before inclusion on a genuine resumed AI turn.
- [x] Eligible merchant and customer context appears once with existing roles, bounds and chronological ordering.
- [x] BLOCK/review/tampered/foreign/stale-model-or-policy/unsupported/incomplete audio remain excluded; historical outcomes cannot authorize or incorrectly suppress current-turn decisions.
- [x] Control changes during assessment prevent AI send; duplicate/concurrent/retry handling uses existing leases and bounded scheduling.
- [x] Focused tests, meaningful actual PG flow and required repository checks pass with exact isolation/report evidence.

## Validation

- [x] RED/GREEN unit vectors covering bounded mixed-history window, deduplication, current-turn outcome isolation, cached/retry evidence and control races.
- [x] Actual disposable PostgreSQL/Redis ingress→HUMAN persistence→normal resume→existing moderation→history, both exchange sides and completed-audio/negative cases; no hosted DB fallback or fabricated provider permission.
- [x] Relevant declared full tests, build/type and changed-file lint; disclose only exact unchanged known baseline failures, with diff/privacy checks.

## Stop Condition

Publish mirrored source/report, set review and return to architect. No merge, live mutation or next-task implementation.

## Implementation Notes

Use normal launcher dedicated sibling worktrees. You are not alone: preserve primary changes and other agents. Bounded selection reuse is repository-local domain policy, not a new Shared mechanism. If assessment retry or current-turn isolation requires a different lifecycle mechanism, report it before implementation expansion.

## Completion Report

### Status

Ready for Review. Exact pushed implementation `cbe926522d318953217480932c97233eafd61752` (runtime31ce5e6 plus approved startup-fixture follow-up), draft https://github.com/kodjobaah/moda-interact-background/pull/223. No main merge or live operation by executor.

### Files Changed

- `src/commerce/history-selection.ts` and `history.ts`: one repository-local authoritative prior20 mixed visible selection; existing chronology/audio boundaries and32000 history bound unchanged.
- `src/services/conversation-moderation/moderation-turn-gate.ts`: current decisions first; only allowed current turn backfills persisted prior CUSTOMER TEXT/completed AUDIO, deduplicated. Historical BLOCK/review cannot suppress it; historical ALLOW cannot authorize blocked current. Canonical assessment service, model/policy, content/tenant evidence and cached leases remain authoritative.
- `src/services/conversation-turn-processor.service.ts`: passes original claim timestamp plus existing PROCESSING_LEASE_MS, never recapturing/increasing the lease.
- Unit handback/gate/processor tests; real `arch075-common-layout` and `conversation-moderation` PG regressions; narrowly amended `arch047-meta-messaging-startup` fixture.

### Work Completed

New historical work has a16-second elapsed ceiling beginning before its query, and each assessment requires a complete existing8-second timeout plus1-second margin within both that deadline and the actual original processing lease. First historical RETRY stops the batch and uses existing turn release/requeue. Cached immutable assessments permit progress on subsequent claims; no queue/cursor/schema/Shared mechanism added. Existing45-second assessment leases,10/30-second backoffs and three-attempt terminal review cap remain unchanged.

This is a bound on newly added historical assessment starts, not a guarantee that the whole existing current-turn moderation/model stage fits120 seconds. Existing current-turn moderation cost/decision and control-revision checks remain unchanged. Direct helper calls still have the historical ceiling; production invocation supplies the real original claim deadline.

Actual disposable ingress persists a customer question during HUMAN control with no AI enqueue, classifier assessment or outbound send; default HUMAN dispatcher then sends a genuinely prepared/moderated reply. A subsequent genuine AI inbound is claimed, moderated using its original lease deadline, and actual loadCommerceHistory includes both eligible sides exactly once with existing customer and untrusted merchant user roles. Duplicate reads/claims reuse assessments and do not duplicate provider sends/usage.

### Validation Results

- Final declared `vitest run`, alone after all generators/PG runs ended:393files PASS/1 existing configured skipped;4344tests PASS/10 existing configured skipped,202.35s. Final source/fixture frozen before this run.
- Final focused98tests/4files PASS, including mixed-window/dedup, current outcome isolation, completed/incomplete audio, historical retry, slow successful assessment/cached replay progress, insufficient/invalid original lease, query consuming deadline, and HUMAN takeover during moderation preventing model/admission/send. Processor test asserts original claim deadline propagation.
- Amended real disposable PostgreSQL/Redis:2suites48tests PASS/0skip,176.75s. Actual ingress/default HUMAN preparation/moderation/delivery/AI claim/history path, completed historical transcript, blocked history/current isolation, canonical tamper/foreign refusal, cached concurrent replay and existing policy/model/provider fences. Only loopback providers; no hosted DB fallback.
- Build PASS after runtime timing amendment: Prisma6.19.3, both TypeScript compilers, sample packaging. The only later change was the approved test-local startup lifecycle fixture. Final scoped ESLint all9changed files and diff check PASS.
- Exact unchanged ac2ef244 gate RED:3unit failures/5passes; actual ingress handback PG RED1failure/36name-filter skips because historical customer assessment remained null. GREEN corrected both.
- Known full-lint baseline remains the four unchanged unused-variable errors previously proven/documented in BG010: candidate-index.store.ts:9 readRecoveryExecutionPolicy; recovery-offer-resolver.service.ts:23–25 MAX_CANDIDATES/VERIFICATION_TIMEOUT_MS/AI_TIMEOUT_MS. Both files unchanged; no full-lint-green claim.

### Validation Corrections / Evidence

Superseded traces are retained and not substituted for final checks. An initial full run overlapped Prisma generation and saw invalid generated client package.json; final artifact JSON/import validated and isolated billing22tests passed. Subsequent checks were serialized around generators.

Two amended full attempts observed the unchanged startup case exceeding its5-second limit (including once with no other test runner); original isolated case passed in1.77s. Inspection found its fake-timer entrypoint lifecycle test omitted the multipart runtime mock and imported the real DB/engine graph. Architect amendment2781e59ee explicitly permitted only a test-local lifecycle stub plus exactly-once start/close assertions, retaining due/pending-repair checks and the same timeout. Controlled isolated stubbed case passed in54ms; final complete full run passed. No production startup changes or timeout inflation.

Evidence under `local-backups/arch075-live-20261113/`: bg012-unit-red, postgres-red, final-focused, budget-postgres, budget-build, final-full, final-lint, generated-artifact-check, billing-isolated, startup-isolated and startup-stubbed-isolated logs; stopped/superseded traces retained separately. No real customer/provider payload committed.

### Isolation / Publication Evidence

Normal launcher packet bg012-prepared.json: canonical primary workspace; dedicated parent and implementation on mirrored task/ARCH-075-BACKGROUND-012; BG011 dependency Complete; parent348744f565760d6e462bcd98787f3a8fcaf48a25 and implementationac2ef244a36a63f13cb794bef41a4d7a27207cb2 synchronized; recursive database6f42b71112efe7ac63654d55f41cd74ca569b1ae exact ready. Attempt1codex claimed2026-11-13T21:51:41Z, pushed claim297c4d79c069552f9e8ba2272de566327cf32579. Read and applied coordinator timing amendment768525f7d and startup fixture amendment2781e59ee. Implementation clean after push. No primary/sibling edits or parent gitlink/index staged.

### Deviations / Assumptions / Unresolved Issues

Only the two explicit architect amendments expanded validation/timing detail. No eager HUMAN-mode classification, new model/provider send, new queue/schema/Shared release, broader history scan or product-referral change. Root owns independent review, merge, deployment and genuine live exchange verification. No whole-conversation awareness beyond the existing bounded window, live verification or architect acceptance is claimed here.

## Architect Review

### Review Status

Accepted

### Review Notes

Reviewed exact source cbe926522d318953217480932c97233eafd61752 and report46c139f1feb98ed0a0bc1ddc4286f70fda28fa13. No findings. Prior selection exactly preserves the existing mixed20 window; current decisions remain authoritative before historical assessment. Canonical stored-subject moderation/cache/lease authority is reused, and BLOCK/review history remains excluded. Original claim deadline is passed without lease reset; historical16-second ceiling begins before selection, full timeout plus1-second margin is checked before calls, first RETRY stops and existing release scheduling progresses through cached rows. This does not assert a new bound on the pre-existing current moderation loop.

The startup unit fixture amendment was independently inspected against actual entrypoint purpose: missing multipart lifecycle mock is now isolated with exactly-once start/close assertions; due/pending repair assertions and original timeout remain unchanged. No production startup edits.

### Reviewed Files

history-selection.ts, history.ts, moderation-turn-gate.ts, conversation-turn-processor.service.ts; focused handback/processor tests; actual common-layout/moderation PG regressions; arch047-meta-messaging-startup unit fixture.

### Validation Reviewed

Final full4344 PASS/10 existing configured skips;98focused;48actual disposable PG/0skips; runtime build/both TypeScript compilers;9-file scoped lint/diff. Original exact gate unit/PG RED captured. Superseded generator/startup traces and narrow correction rationale disclosed. Four unchanged full-lint baseline findings not claimed green. Dedicated mirrored launcher worktree, synchronization, dependency, recursive database and clean publication evidence reviewed.

### Architecture Conformance

Conforms to Background-local bounded handback moderation without queue/schema/Shared change, HUMAN-mode AI work, control/billing weakening, whole-conversation scans or source role elevation. Source accepted independently of live integration.

### Follow-up

Root owns main integration and genuine post-deployment both-sides handback proof. ARCH-075 remains In Progress. User-approved composite layout is a separate design; prior two-bubble group definitions remain unexecuted pending supersession.

## Developer Integration

Root merged Background PR223 at exact reviewed source cbe926522d318953217480932c97233eafd61752 after both hosted unit checks succeeded and architect acceptance68ed58859. Actual implementation main merge is dd29c40545794ee4ec0997333c064a55ef9bb9f2; this parent gitlink records that merge. Local evidence:4344 full unit tests,98 focused tests,48 actual PostgreSQL tests, build and scoped lint passed. Historical four full-lint findings remain disclosed. Live deployment and genuine post-deployment handback verification remain outstanding; no customer message replay or reset performed. Composite-image layout remains separate work.
