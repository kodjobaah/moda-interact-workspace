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

- [ ] At allowance boundary emit merchant SYSTEM notice once via existing sourceKey uniqueness; crossing boundary consumes no new credit.
- [ ] Next genuine automated continuation reserves one eligible credit against explicit continuation identity on SAME Conversation/recovery; no fake sequence-two attempt.
- [ ] Count automated message UsageEvents by immutable funded block; never reset lifetime counts/history or globally suppress after historical terminal notice.
- [ ] Canonical paid/included/promotional/purchased/free paths must preserve exact new source identity; existing admit without outreachAttemptId drops custom paid sourceKey and must be explicitly corrected.
- [ ] FOLLOW_UP uses its legitimate exact sequence-two credit once to fund successor block; no second continuation debit, unadmitted followup still cancelled on customer return.
- [ ] Activate successor atomically only on exact confirmed opening receipt; close prior ACTIVE then. Definitive pre-permit failure cancels/releases; unknown result holds exact proof and bounded repair, no resend.
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

- [ ] At allowance boundary emit merchant SYSTEM notice once via existing sourceKey uniqueness; crossing boundary consumes no new credit.
- [ ] Next genuine automated continuation reserves one eligible credit against explicit continuation identity on SAME Conversation/recovery; no fake sequence-two attempt.
- [ ] Count automated message UsageEvents by immutable funded block; never reset lifetime counts/history or globally suppress after historical terminal notice.
- [ ] Canonical paid/included/promotional/purchased/free paths must preserve exact new source identity; existing admit without outreachAttemptId drops custom paid sourceKey and must be explicitly corrected.
- [ ] FOLLOW_UP uses its legitimate exact sequence-two credit once to fund successor block; no second continuation debit, unadmitted followup still cancelled on customer return.
- [ ] Activate successor atomically only on exact confirmed opening receipt; close prior ACTIVE then. Definitive pre-permit failure cancels/releases; unknown result holds exact proof and bounded repair, no resend.
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
