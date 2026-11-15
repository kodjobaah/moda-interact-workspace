---
id: ARCH-076-BACKGROUND-005
architecture_id: ARCH-076
title: Renew the existing conversation allowance
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-076-DATABASE-002]
enables: []
created: 2026-11-15
updated: 2026-11-15
---

# Renew the existing conversation allowance

## Architecture

[ARCH-076](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md), coordinator moda_architect.

## Objective

Fund a fresh automated allowance on genuine continuation without changing routing.

## Context

15 November user-selected design retains five explicit sender entities plus the R15 evidence amendment. Sender attribution and conversation-credit renewal are independent streams. The user has authorized implementation of this reviewed design. Preserve prepared claims; execute only through the owning task launcher and accepted dependency frontier.

## Scope

Existing recovery credit admission/settlement/compensation, outbound admission counts and merchant SYSTEM notice; no sender allocation.

## Out of Scope

Other repository implementation, live settings, production migration and activation. Sender tasks must not implement allowance renewal; allowance tasks must not implement sender allocation. The SYSTEM-TEST task is deferred at the user's request.

## Requirements

- [ ] At the live normal boundary keep current block ACTIVE and emit advisory merchant SYSTEM notice once; no new credit solely for crossing. Follow the parent ACTIVE-until-renewal protocol.
- [ ] Next genuine automated continuation reserves one eligible credit against explicit continuation identity on SAME Conversation/recovery; no fake sequence-two attempt.
- [ ] Count automated message UsageEvents by immutable funded block; never reset lifetime counts/history or globally suppress after historical terminal notice.
- [ ] Canonical paid/included/promotional/purchased/free paths must preserve exact new source identity; existing admit without outreachAttemptId drops custom paid sourceKey and must be explicitly corrected.
- [ ] FOLLOW_UP uses its legitimate exact sequence-two credit once to fund successor block; no second continuation debit, unadmitted followup still cancelled on customer return.
- [ ] Activate successor atomically only on exact confirmed opening settlement; mark prior EXHAUSTED for CONTINUATION or CLOSED for genuine FOLLOW_UP. Definitive pre-permit failure cancels/releases; unknown result holds exact proof and bounded repair, no resend.
- [ ] Late opening failure compensates block only if no other provider-admitted consumption; otherwise preserve funding and expose incident.
- [ ] Zero credits holds same request and existing capacity repair resumes; no auto-purchase, reroute, cap reset, extra Conversation or unfunded model/provider call.
- [ ] HUMAN/STOP/clarification/window/closed/expiry paths never consume continuation funding; cap does not change controlMode.

## Work Items

- [ ] Inspect the exact latest accepted repository pin and existing owning mechanisms.
- [ ] Implement only this task's scope and requirements.
- [ ] Complete the focused checks below and record exact commands and evidence.
- [ ] Return the isolated implementation branch and parent Completion Report for review.

## Interfaces / Contracts

The parent architecture's Independent allowance storage and lifecycle sections are authoritative. Existing published Shared remains reusable structural machinery. Applications own routing, funding, eligibility and authorization. Do not add compatibility paths for the superseded three-table draft or an unreviewed schema.

## Dependencies

ARCH-076-DATABASE-002

## Enables

Recalculate from dependent task metadata after architect acceptance; no implicit implementation handoff.

## Acceptance Criteria

- [ ] At the live normal boundary keep current block ACTIVE and emit advisory merchant SYSTEM notice once; no new credit solely for crossing. Follow the parent ACTIVE-until-renewal protocol.
- [ ] Next genuine automated continuation reserves one eligible credit against explicit continuation identity on SAME Conversation/recovery; no fake sequence-two attempt.
- [ ] Count automated message UsageEvents by immutable funded block; never reset lifetime counts/history or globally suppress after historical terminal notice.
- [ ] Canonical paid/included/promotional/purchased/free paths must preserve exact new source identity; existing admit without outreachAttemptId drops custom paid sourceKey and must be explicitly corrected.
- [ ] FOLLOW_UP uses its legitimate exact sequence-two credit once to fund successor block; no second continuation debit, unadmitted followup still cancelled on customer return.
- [ ] Activate successor atomically only on exact confirmed opening settlement; mark prior EXHAUSTED for CONTINUATION or CLOSED for genuine FOLLOW_UP. Definitive pre-permit failure cancels/releases; unknown result holds exact proof and bounded repair, no resend.
- [ ] Late opening failure compensates block only if no other provider-admitted consumption; otherwise preserve funding and expose incident.
- [ ] Zero credits holds same request and existing capacity repair resumes; no auto-purchase, reroute, cap reset, extra Conversation or unfunded model/provider call.
- [ ] HUMAN/STOP/clarification/window/closed/expiry paths never consume continuation funding; cap does not change controlMode.

## Validation

- [ ] Unit and real PostgreSQL races: duplicate inbound, concurrent last slots, renewal once, zero credits/resume, restart and third funded block.
- [ ] Provider fixtures: exact opening settlement, definitive failure, timeout unknown, foreign receipt and late failure after subsequent consumption.
- [ ] Existing credit-bucket/followup/accounting tests plus declared typecheck/build.

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

Pending

### Review Notes

Definition only; implementation not started.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending implementation review.

### Follow-up

None


### 15 November definition amendment

This is a new independently scoped definition, not implementation evidence. No runtime source or migration has been implemented. User has authorized implementation; runtime acceptance and rollout verification remain pending.

## Funded allowance boundary — ACTIVE until renewal admission

This application protocol supersedes earlier wording that marked EXHAUSTED as soon as reserved usage reached a cap. No SQL/schema change is required. The normal-message allowance is the frozen `hardMessageLimit - terminalReservedSlots`; do not hardcode 19/20. Reserved terminal slots are only for genuine permitted terminal notices, never ordinary answers, and no customer terminal notice is forced merely to spend the reserve. Test zero reserve and variable valid limits.

1. Usage reservations count for ordinary admission, so potentially consumed/inflight slots cannot be oversubscribed. Merely reserved usage, HTTP200/provider ID or SENT can later fail and be compensated; none justifies irreversible exhaustion alone. When the live normal cap prevents another ordinary answer, keep the existing block ACTIVE and emit at most one merchant SYSTEM advisory notice keyed by that block. Explain that a further recovery credit may be required if the limit still holds at the next genuine continuation; no debit occurs solely at the boundary.
2. On the next genuine customer automated continuation, create one PENDING successor intent under owner lock before external credit reservation, using the same deterministic block identity and canonical credit paths. No new routing decision, Conversation or reset. An unresolved pending provider outcome gates parallel successors; bounded repair reconciles exact evidence rather than declaring timeout a failure.
3. Immediately BEFORE the final durable provider permit, re-lock/revalidate actual surviving normal usage/reservations, block ownership/control/eligibility and exact funding proof. If compensation freed old capacity, cancel/release the unadmitted pending successor and admit the original customer continuation using the still-ACTIVE old block. Never retag an immutable prepared message pin: if preparation already pinned a successor row, preserve/cancel it and create a fresh logical row for old capacity without a duplicate provider send. No manual-incident hold is the default for an ordinary freed slot.
4. Once that successor's exact provider permit is admitted, its funding choice is frozen. Do not re-evaluate old capacity after permit or rewind this decision because a late old message failure removes an old event. UNKNOWN opening stays PENDING, with exact reservation/permit identity, preventing another successor or automatic resend.
5. On confirmed funded opening settlement, atomically transition predecessor ACTIVE→EXHAUSTED for CONTINUATION (already-EXHAUSTED predecessor is retained on a proved replacement lineage), or predecessor ACTIVE→CLOSED for a genuine FOLLOW_UP, and activate the successor. The followup's exact sequence-two credit funds it once. CONTINUATION eligibility before permit is actual live cap proof, not a requirement that the predecessor already be EXHAUSTED.
6. Definitive opening failure BEFORE activation cancels/releases/refunds the PENDING intent only with exact no-success/compensation proof; predecessor remains ACTIVE. After activation, a late opening failure follows existing exact compensation and the no-other-provider-consumption guard: retain cancelled lineage where cancellation/refund is eligible, retry with a fresh monotonic ordinal and exact source, never reopen an EXHAUSTED predecessor. If other successor messages already consumed its funding, preserve that funding and its evidence as previously required. Old-block late failure compensates only its own exact usage, not the completed successor renewal.

Required owner checks: variable hard/reserve snapshots (including reserve0), provisional reserved/unknown slots versus compensated slots, advisory notice once, compensation before final permit cancels/releases successor and reuses old capacity, compensation after permit cannot rewind funding, unknown opening excludes parallel charge/resend, definitive preactivation opener failure, eligible late opener cancellation plus retained lineage/new ordinal retry, and ineligible late opener refund after other admitted consumption. Check actual provider calls, pins and canonical credit counts, not only block state. Existing service-window/STOP/HUMAN/routing exclusions remain; SYSTEM-TEST stays deferred.
