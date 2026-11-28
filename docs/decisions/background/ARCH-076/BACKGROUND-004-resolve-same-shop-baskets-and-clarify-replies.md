---
id: ARCH-076-BACKGROUND-004
architecture_id: ARCH-076
title: Resolve each original question to its intended checkout with configured routing policy
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 45
executor: codex
claimed_at: 2026-11-15T19:19:04Z
attempt: 1
depends_on:
  [
    ARCH-076-BACKGROUND-003,
    ARCH-076-ADMIN-002,
    ARCH-076-ADMIN-003,
    ARCH-076-COMMERCE-001,
  ]
enables: []
created: 2026-11-13
updated: 2026-11-15
---

# Resolve each original question to its intended checkout with configured routing policy

## Architecture

[ARCH-076](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md), coordinator moda_architect.

## Objective

Resolve each original question to its intended checkout with configured routing policy.

## Context

15 November user-selected design retains five explicit sender entities plus the R15 evidence amendment. Sender attribution and conversation-credit renewal are independent streams. The user has authorized implementation of this reviewed design. Preserve prepared claims; execute only through the owning task launcher and accepted dependency frontier.

## Scope

Owning Background services and focused unit/provider-fixture/disposable PostgreSQL tests.

## Out of Scope

Other repository implementation, live settings, production migration and activation. Sender tasks must not implement allowance renewal; allowance tasks must not implement sender allocation. The SYSTEM-TEST task is deferred at the user's request.

## Requirements

- [ ] Support the parent explicit R15 two-stage star relation: Q2 shop choice and Q3 basket choice both parent Q1 substantive original; Q3 names exact basket prompt Q2, whose parent is Q1. Prompt may be Q1 or its explicitly identified direct child, not necessarily original itself.

- [ ] Follow the parent R15 evidence privacy amendment: routingDecision contains only message IDs, clause offsets/hashes and structural evidence, no exact clause plaintext. Preserve exact wording through pending inputJson then atomic existing ConversationMessage association.
- [ ] Freeze input/candidate/config/parent scope; permit only explicit destructive terminal value→NULL scrub and real FK SET NULL cleanup, never rebind or payload resurrection. Terminal scrub removes ephemeral customer/candidate/prompt payloads without deleting authentic owned Conversation history.

- [ ] Implement the parent R15 four-role decision contract: SELECT_ONLY, NEW_QUESTION, SELECT_AND_QUESTION, CLARIFY; persist routingDecision independently of configurationSnapshot.
- [ ] A uniquely evidenced “running shoes” selection resumes the pending Friday question; “Do the shoes come in black?” is independent and leaves it pending.
- [ ] Verified “2. Can I collect on Saturday?” preserves original plus exact independently moderated new clause; ambiguous “2” clarifies, ordinary numeric input stays authentic input.
- [ ] Freeze original/prompt/candidate/config/template/moderation/control evidence before admission; crash/retry reuses the decision and terminal replay never readmits. Changed pre-admission evidence holds/reclarifies without reinterpretation.

- [ ] Use inventory, explicit recipient/sender Thread, shop Route, immutable Conversation Assignment and unresolved RoutingTurn from the parent exact schema.
- [ ] Preserve Conversation.checkoutRecoveryId uniqueness and existing recovery/consent/history/STOP semantics.
- [ ] Never filter ownership candidates or select another checkout based on credits, allowance, model capacity or paid plan.
- [ ] Persist original moderated text/verified transcript and immutable candidate assignment identities before clarification; multiple originals remain independent.
- [ ] Before verified shop use only neutral ROUTER template, no tenant variables or merchant history/catalogue reads.
- [ ] After verified shop compare complete eligible same-shop baskets using configured routing agent; validate offered key and configured confidence threshold; no recency/cap/credit tie-breaker.
- [ ] Never silently truncate candidates/items; configured input limit overflow asks clarification. Quoted prompt/request token selects exact original; ambiguous bare number cannot guess.
- [ ] Revalidate candidate ownership at final admission. Closed assignment expires original choice; never attach to newer same-shop recovery.
- [ ] Use Admin-published ROUTER selector separate from normal Shared chooseSlot; configured model/prompt/threshold/budgets/retries/input bounds come from recovery.routingAgent; snapshot exact revisions.
- [ ] Resolve original once with authentic question/selection transcript; selection-only reply never replaces substantive original question.

## Work Items

- [ ] Inspect the exact latest accepted repository pin and existing owning mechanisms.
- [ ] Implement only this task's scope and requirements.
- [ ] Complete the focused checks below and record exact commands and evidence.
- [ ] Return the isolated implementation branch and parent Completion Report for review.

## Interfaces / Contracts

The parent architecture's Explicit sender storage, Configurable routing and R15 question and clarification sections are authoritative. Allowance renewal is independent. Existing published Shared remains reusable structural machinery. Applications own routing, funding, eligibility and authorization. Do not add compatibility paths for the superseded three-table draft or an unreviewed schema.

## Dependencies

ARCH-076-BACKGROUND-003, ARCH-076-ADMIN-002, ARCH-076-ADMIN-003

## Enables

Recalculate from dependent task metadata after architect acceptance; no implicit implementation handoff.

## Acceptance Criteria

- [ ] Implement the parent R15 four-role decision contract: SELECT_ONLY, NEW_QUESTION, SELECT_AND_QUESTION, CLARIFY; persist routingDecision independently of configurationSnapshot.
- [ ] A uniquely evidenced “running shoes” selection resumes the pending Friday question; “Do the shoes come in black?” is independent and leaves it pending.
- [ ] Verified “2. Can I collect on Saturday?” preserves original plus exact independently moderated new clause; ambiguous “2” clarifies, ordinary numeric input stays authentic input.
- [ ] Freeze original/prompt/candidate/config/template/moderation/control evidence before admission; crash/retry reuses the decision and terminal replay never readmits. Changed pre-admission evidence holds/reclarifies without reinterpretation.

- [ ] Use inventory, explicit recipient/sender Thread, shop Route, immutable Conversation Assignment and unresolved RoutingTurn from the parent exact schema.
- [ ] Preserve Conversation.checkoutRecoveryId uniqueness and existing recovery/consent/history/STOP semantics.
- [ ] Never filter ownership candidates or select another checkout based on credits, allowance, model capacity or paid plan.
- [ ] Persist original moderated text/verified transcript and immutable candidate assignment identities before clarification; multiple originals remain independent.
- [ ] Before verified shop use only neutral ROUTER template, no tenant variables or merchant history/catalogue reads.
- [ ] After verified shop compare complete eligible same-shop baskets using configured routing agent; validate offered key and configured confidence threshold; no recency/cap/credit tie-breaker.
- [ ] Never silently truncate candidates/items; configured input limit overflow asks clarification. Quoted prompt/request token selects exact original; ambiguous bare number cannot guess.
- [ ] Revalidate candidate ownership at final admission. Closed assignment expires original choice; never attach to newer same-shop recovery.
- [ ] Use Admin-published ROUTER selector separate from normal Shared chooseSlot; configured model/prompt/threshold/budgets/retries/input bounds come from recovery.routingAgent; snapshot exact revisions.
- [ ] Resolve original once with authentic question/selection transcript; selection-only reply never replaces substantive original question.

## Validation

- [ ] Positive Q1 unknown-shop→Q2 shop selection and basket prompt→Q3 exact basket selection→Q1 resolution/admission flow; reject foreign original/prompt/thread/route scope and missing confirmation, with replay/concurrency tests. No extra table/column or recursive/newest prompt lookup.

- [ ] Verify exact clause survives association/retry through authentic message IDs and offsets/hash; routingDecision contains no customer plaintext. Test frozen payload replacement rejection, terminal destructive scrub, FK cleanup and resurrection/rebinding rejection.

- [ ] Unit fixtures cover every R15 table row, ordinary numeric input, multiple matching prompts, unavailable receipt, distinct simultaneous originals and exact clause preservation/moderation.
- [ ] Disposable PostgreSQL crash/retry tests prove decision freeze plus atomic original admission, duplicate delivery, changed configuration/template/control/assignment between decision and admission, human→AI transition and terminal replay.

- [ ] Focused unit tests for every requirement, lint/typecheck/build as declared for changed code.
- [ ] Disposable PostgreSQL race/replay/restart tests with two recipients, two shops, multiple checkouts and shared sender.
- [ ] Provider HTTP fixtures for exact sender, failed initial delivery, unknown result, duplicate/foreign statuses and no network inside transactions.

Inspect the repository package.json before selecting actual commands. Required disposable PostgreSQL checks are task-local repository checks, not execution of the deferred system-test task. No live customer/provider calls belong to these checks.

## Stop Condition

After Work Items, Acceptance Criteria and Validation pass, set review, return the Completion Report and STOP. Do not execute another task or deploy.

## Implementation Notes

Existing published Shared remains reusable structural machinery. Applications own routing, funding, eligibility and authorization. Do not add compatibility paths for the superseded three-table draft or an unreviewed schema.

## Completion Report

### Status

Implementation in progress in the prepared isolated task worktrees. Source draft PR243: https://github.com/kodjobaah/moda-interact-background/pull/243, head `1db5f785dec9eb1cdd4be4580261021bcaef2b96`. Final acceptance is held on the owning Database correction for canonical exact-clause moderation; no schema bypass is implemented.

### Files Changed

- New routing policy/classifier, durable neutral prompt, R15 store/runtime and role projection modules under `src/services/recovery-sender-pool`.
- Actual inbound routing, existing repair tick, scalar provider status, Commerce history and moderation owner integrations.
- Focused unit/provider fixtures and task-local disposable PostgreSQL R15 integration suite; no SYSTEM-TEST execution.

### Work Completed

- Configured policy/model/prompt revision snapshots with no hidden AI defaults; separate ROUTER selector and durable no-resend prompt permit.
- Explicit original/shop-child/basket-child star relation, immutable structural role decisions, exact authentic message association and role projection before history/latest limits.
- Sender/recipient/current owner/control/STOP/window/candidate/config/template/moderation rechecks; ephemeral payload scrub and retained role evidence while owned history survives.
- Canonical full-current-message moderation plus independent clause moderation use the existing PENDING→CHECKING→ALLOW lease lifecycle.
- Verified voice uses existing configured media/speech adapters under the routing lease, captures one immutable transcript/moderation snapshot, binds the Database-owned raw-input hash, and materializes authentic AUDIO/COMPLETED plus canonical TRANSCRIPT assessments at owned admission.

### Validation Results

- Combined focused final unit/provider/history/moderation/inbound/media/speech command:20 files,322 tests passed (`/tmp/bg004-focused-final2.log`). Audio proof/helper focused36 tests and targeted lint also passed.
- Full repository lint and explicit TypeScript noEmit passed (`/tmp/bg004-voice-final-lint.log`, `/tmp/bg004-voice-final-types.log`). Declared `npm run build` passed (`/tmp/bg004-build.log`, exit0). Final exact-head CI and accepted Database-pin PostgreSQL checks remain pending.
- Actual PostgreSQL checkpoint:18/19 pass, including full runtime Q1→neutral shop Q2→basket Q3→exactly-once original admission and projection. Sole failure is PostgreSQL23514 `ARCH040 moderation message text digest mismatch` for the independently moderated new clause. The current27-case suite adds voice full/clause TRANSCRIPT admission, UTF-16 emoji/combining offsets, provenance refusal and replay; it is not claimed passed until rerun.

### Deviations

None

### Assumptions

None

### Unresolved Issues

Existing ARCH040 SQL subject integrity validates only the full stored message digest, whereas R15 retains that authentic message and independently assesses its exact clause. The coordinator is preparing the owning Database correction; Background does not alter triggers, omit canonical assessments or fake an ALLOW. The exact-clause positive test and all final gates must pass against the accepted Database pin before review return.

### Architectural Concerns

None

### Final acceptance reconciliation — 15 November 2026

This addendum supersedes the in-progress status, pending-gate statements and 18/19 PostgreSQL checkpoint above; those paragraphs are retained as historical execution evidence, not current blockers.

- Accepted Background source: [PR #243](https://github.com/kodjobaah/moda-interact-background/pull/243), exact head `4834efde0e0e1ccc5919e97189d582b0d2eea251`. The PR remained **open and Draft** when reviewed; this is source acceptance, not a claim of merge or deployment.
- Accepted Database R15 migration: [Database PR #80](https://github.com/kodjobaah/moda-interact-database/pull/80), merged Database pin `0a9edc7c0c30e0a405d89efec624bc9338b4ac17`. The user's disposable PostgreSQL run passed 684 assertions across fresh installation and upgrade; no hosted migration was claimed.
- Focused corrective regression tests: 62/62 passed locally. Task-local disposable PostgreSQL routing-resolution integration: 28/28 passed locally, including text/audio clarification, separate clause moderation, exact original Q1 admission, UTF-16 offsets, ownership isolation, concurrency, replay and retention.
- The supplied terminal log reported successful lint, `tsc --noEmit`, Prisma generation and `npm run build`; those checks were not independently executed by the architect.
- [Exact-head GitHub Actions Unit tests #1094](https://github.com/kodjobaah/moda-interact-background/actions/runs/43773500532) completed successfully on commit `4834efde0e0e1ccc5919e97189d582b0d2eea251`.
- Architectural correction review checked prompt/original scope before model history, authorized neutral Q1 → shop Q2 → basket Q3, understandable overflow clarification and redaction-aware original error diagnostics. No further source changes were requested for those reviewed findings.

The prior SQL clause digest blocker is resolved by the merged R15 migration. This review does **not** execute or waive ARCH-076-SYSTEM-TEST-001, authorize live routing activation, apply a hosted migration, or change independent allowance funding. The coordinator must separately reconcile the Background source merge and parent workspace gitlink.

## Architect Review

### Review Status

Accepted — Background source implementation only (15 November 2026).

### Review Notes

Accepted the exact BG004 correction head `4834efde0e0e1ccc5919e97189d582b0d2eea251`, subject to normal PR merge safeguards. The prior cross-shop quoted-prompt, overflow clarification and original diagnostic logging findings were addressed in the reviewed source and focused tests.

### Reviewed Files

BG004 routing runtime, policy, prompt, classifier, store, Commerce history/projection, moderation integration, inbound/sender ownership wiring, affected unit tests and the task-local routing-resolution PostgreSQL suite on PR #243.

### Validation Reviewed

62/62 focused correction tests; 28/28 task-local PostgreSQL integration cases; local lint, TypeScript and build evidence; accepted Database R15 pin; exact-head GitHub Actions Unit tests #1094 (success). Earlier 18/19 test results above are superseded.

### Architecture Conformance

Accepted for source implementation: original-question fidelity, sender/shop isolation, frozen R15 evidence, separate clause moderation, bounded safe clarification and replay safety. No production activation is approved.

### Follow-up

Merge Background PR #243 through normal checks, reconcile its accepted main gitlink in the parent workspace, and keep the separately deferred ARCH-076-SYSTEM-TEST-001 and production rollout on their own authorization paths.

## Reconciliation provenance — 15 November 2026

Reconciled from the later local sender-pool revision formerly labelled ARCH-069. The completed chronological-input architecture and its ARCH-069 task identities are unchanged. ARCH-076 was already reserved for the earlier sender-pool proposal; this revision updates that proposal in place, retaining its Git history. These are definition changes, not implementation or deployment evidence. All execution remains Pending until compatibility review and dependency promotion.

## Mandatory same-conversation allowance renewal amendment

Historical renewal amendment is superseded for this sender task: allowance work belongs only to independent DATABASE-002/BACKGROUND-005 and does not gate sender routing. Never filter ownership by credit or cap.

### 15 November definition amendment

Historical fixed SQL must be regenerated for the restored five-entity contract plus R15 evidence; hardcoded router policy remains superseded. Historical claim/review evidence above is retained as history, not approval of the replacement implementation. No runtime source or migration has been implemented. User has authorized implementation; runtime acceptance and rollout verification remain pending.

Parent relationship correction: persist input before model/classification; bind parentProviderMessageId NULL→exact ID once after role classification, then never clear/rebind. Selected Conversation and frozen decision associate atomically. Retention operates on eligible request cohorts under deferred parent FK, never orphaning a pending original/child.

R15 positive resolution lifecycle correction: classifier routingDecision and later original-request resolution are separate. Add nullable resolutionInboundProviderMessageId TEXT self-FK NO ACTION DEFERRABLE INITIALLY DEFERRED (no global UNIQUE). Q1 frozen CLARIFY stays unchanged; confirmed prompt + Q2 frozen exact-parent SELECT_ONLY/SELECT_AND_QUESTION permits Q1's initial selectedConversationId+witness=Q2 bind atomically with original admission and terminal scrub. Direct NEW_QUESTION may use self witness and leaves older pending originals alone. Bound witness is immutable; a preexisting CLARIFY decision must not block valid first resolution. Validate same-thread/route original/prompt/candidate and current owner/control/moderation under lock. Required positive PostgreSQL original→CLARIFY→confirmed prompt→child selection→original admission case, plus simultaneous selections/replay/crash, forged witness, separate new question, exact additional clause and retention-cohort deletion. Do not rewrite classifier decisions or infer resolver by reverse-child lookup.

The parent R15 explicit two-stage shop then basket clarification section is authoritative. Preserve Q1/Q2 CLARIFY decisions; Q3 exact role decision and Q1 resolution witness provide later admission evidence. Prior wording requiring promptTurnId equal originalTurnId is superseded by the direct-child star contract.

Architecture dependency correction: ARCH-076-COMMERCE-001 must be Complete before BG004 acceptance/live routing activation. Studio normal prompt activation must reject routing-tagged revisions. This does not block ADMIN003 source acceptance. SYSTEM-TEST remains deferred.
