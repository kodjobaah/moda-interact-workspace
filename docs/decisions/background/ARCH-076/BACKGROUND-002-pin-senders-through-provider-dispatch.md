---
id: ARCH-076-BACKGROUND-002
architecture_id: ARCH-076
title: Carry the immutable assignment through each provider permit
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 30
executor: codex
claimed_at: 2026-11-15T14:58:50Z
attempt: 1
depends_on: [ARCH-076-BACKGROUND-001]
enables: [ARCH-076-BACKGROUND-003]
created: 2026-11-13
updated: 2026-11-15
---

# Carry the immutable assignment through each provider permit

## Architecture

[ARCH-076](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md), coordinator moda_architect.

## Objective

Carry the immutable assignment through each provider permit.

## Context

15 November user-selected design retains five explicit sender entities plus the R15 evidence amendment. Sender attribution and conversation-credit renewal are independent streams. The user has authorized implementation of this reviewed design. Preserve prepared claims; execute only through the owning task launcher and accepted dependency frontier.

## Scope

Owning Background services and focused unit/provider-fixture/disposable PostgreSQL tests.

## Out of Scope

Other repository implementation, live settings, production migration and activation. Sender tasks must not implement allowance renewal; allowance tasks must not implement sender allocation. The SYSTEM-TEST task is deferred at the user's request.

## Requirements

- [ ] Use inventory, explicit recipient/sender Thread, shop Route, immutable Conversation Assignment and unresolved RoutingTurn from the parent exact schema.
- [ ] Preserve Conversation.checkoutRecoveryId uniqueness and existing recovery/consent/history/STOP semantics.
- [ ] Never filter ownership candidates or select another checkout based on credits, allowance, model capacity or paid plan.
- [ ] Initial/follow-up/AI/human paths all use pinned sender; ordinary text/image/template transport must not resolve singleton sender again.
- [ ] Recheck sender/WABA/recipient/consent/owner/control/service window immediately before permit; no network in DB transactions.
- [ ] Use existing ordered delivery parts and immutable sender pair for receipts/status; preserve exact credit lineage and admission behavior without renewing allowance.
- [ ] Unknown provider results remain uncertain; never retry send automatically based on timeout.

## Work Items

- [ ] Inspect the exact latest accepted repository pin and existing owning mechanisms.
- [ ] Implement only this task's scope and requirements.
- [ ] Complete the focused checks below and record exact commands and evidence.
- [ ] Return the isolated implementation branch and parent Completion Report for review.

## Interfaces / Contracts

The parent architecture's Explicit sender storage, Independent allowance storage and Configurable routing sections are authoritative. Existing published Shared remains reusable structural machinery. Applications own routing, funding, eligibility and authorization. Do not add compatibility paths for the superseded three-table draft or an unreviewed schema.

## Dependencies

ARCH-076-BACKGROUND-001

## Enables

Recalculate from dependent task metadata after architect acceptance; no implicit implementation handoff.

## Acceptance Criteria

- [ ] Use inventory, explicit recipient/sender Thread, shop Route, immutable Conversation Assignment and unresolved RoutingTurn from the parent exact schema.
- [ ] Preserve Conversation.checkoutRecoveryId uniqueness and existing recovery/consent/history/STOP semantics.
- [ ] Never filter ownership candidates or select another checkout based on credits, allowance, model capacity or paid plan.
- [ ] Initial/follow-up/AI/human paths all use pinned sender; ordinary text/image/template transport must not resolve singleton sender again.
- [ ] Recheck sender/WABA/recipient/consent/owner/control/service window immediately before permit; no network in DB transactions.
- [ ] Use existing ordered delivery parts and immutable sender pair for receipts/status; preserve exact credit lineage and admission behavior without renewing allowance.
- [ ] Unknown provider results remain uncertain; never retry send automatically based on timeout.

## Validation

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


## Existing singleton cutover proof boundary

BG002 must retain the approved non-pooled send-versus-enrollment fence, not merely change recovery transport endpoints. Before a new standalone/non-pooled provider permit, acquire the same transaction advisory membership key as Admin enrollment: `pg_advisory_xact_lock(hashtextextended('whatsapp-pool-membership:' || phoneId::text, 0))`. Under that lock reject the non-pooled permit if any inventory row exists for that exact phone, even allocation-disabled. Freeze the exact dispatchProviderAccountId/dispatchProviderPhoneNumberId pair on the durable root permit and current delivery parts; no network inside the lock. Enrollment collision preflight and permit must serialize on that key. Existing already-admitted/unknown provider work retains exact proof and must not be resent after cutover. Recovery initial/followup/AI/human sends use their existing assignment's sender; non-pooled sends may use only the permitted current credential identity and never bypass enrolled inventory.

BG003 must distinguish newly pooled routing from exact preexisting unassigned singleton evidence. An authentic quoted prior outbound, persisted inbound replay or exact status receipt may resolve its original existing Conversation using immutable recorded root/part sender evidence and matching authenticated WABA/phone/recipient. If old root pair is NULL, accept only the established singleton proof allowed by the approved cutover policy while the configured singleton identity is unchanged/provable; unknown identity after credential change remains ambiguous/held. Never fabricate sender proof, backfill assignment, bind old history to a new route generation or use recipient-only fallback to select an owner. Closed/expired history remains history and never reopens recovery or bypasses STOP/window/control/cap. Foreign sender statuses/quotes have no effects. This preserves production evidence, not a compatibility path for obsolete new schema formats.

Owner checks: concurrent standalone permit versus first disabled enrollment (either permit wins and enrollment reports protected use, or enrollment wins and permit is refused); inventory disabled still blocks new non-pooled permit; pooled endpoints never fall back to singleton; exact preexisting singleton quote/replay/status succeeds only with matching stable proof, wrong/changed/unknown account proof refuses, no assignment backfill or repeated provider admission. Partial BG001 may hold zero-inventory initial work, but inventory cannot activate until complete pinning/ownership path is test-verified and old consumers/inflight work are drained. Production auto-deploy holds remain.
