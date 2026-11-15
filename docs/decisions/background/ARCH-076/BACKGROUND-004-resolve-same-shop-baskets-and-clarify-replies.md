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
status: pending
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-076-BACKGROUND-003, ARCH-076-ADMIN-002, ARCH-076-ADMIN-003]
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

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run; definition only.

### Deviations

None

### Assumptions

None

### Unresolved Issues

Use owning task launcher at the accepted dependency frontier.

### Architectural Concerns

None

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

## Mandatory same-conversation allowance renewal amendment

Historical renewal amendment is superseded for this sender task: allowance work belongs only to independent DATABASE-002/BACKGROUND-005 and does not gate sender routing. Never filter ownership by credit or cap.


### 15 November definition amendment

Historical fixed SQL must be regenerated for the restored five-entity contract plus R15 evidence; hardcoded router policy remains superseded. Historical claim/review evidence above is retained as history, not approval of the replacement implementation. No runtime source or migration has been implemented. User has authorized implementation; runtime acceptance and rollout verification remain pending.

Parent relationship correction: persist input before model/classification; bind parentProviderMessageId NULL→exact ID once after role classification, then never clear/rebind. Selected Conversation and frozen decision associate atomically. Retention operates on eligible request cohorts under deferred parent FK, never orphaning a pending original/child.
