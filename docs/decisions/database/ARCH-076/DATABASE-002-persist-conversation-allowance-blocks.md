---
id: ARCH-076-DATABASE-002
architecture_id: ARCH-076
title: Persist independent funded conversation allowances
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: [ARCH-076-BACKGROUND-005]
created: 2026-11-15
updated: 2026-11-15
---

# Persist independent funded conversation allowances

## Architecture

[ARCH-076](../../../architecture/ARCH-076-whatsapp-sender-pool-and-checkout-reply-routing.md), coordinator moda_architect.

## Objective

Persist exact funded-block lineage without resetting conversation history.

## Context

15 November user-selected design retains five explicit sender entities plus the R15 evidence amendment. Sender attribution and conversation-credit renewal are independent streams. The user has authorized implementation of this reviewed design. Preserve prepared claims; execute only through the owning task launcher and accepted dependency frontier.

## Scope

One independent allowance migration, Prisma relations, integrity guards, ERD and disposable PostgreSQL checks; no sender schema dependency.

## Out of Scope

Other repository implementation, live settings, production migration and activation. Sender tasks must not implement allowance renewal; allowance tasks must not implement sender allocation. The SYSTEM-TEST task is deferred at the user's request.

## Requirements

- [ ] Implement exact Independent allowance storage fields/constraints in parent architecture.
- [ ] Existing messages with NULL allowanceBlockId remain original block-zero history; no rewriting UsageEvents or mass retagging.
- [ ] Lazy initial block adoption requires proven original funding; unknown historical proof holds for reconciliation, never fabricates funding or charges again.
- [ ] One ACTIVE and one PENDING successor per Conversation; cancelled intents retained and monotonic ordinal never reused.
- [ ] Freeze message block pin at insert and immutable funding identity; independent repair lease survives turn lease expiry.

## Work Items

- [ ] Inspect the exact latest accepted repository pin and existing owning mechanisms.
- [ ] Implement only this task's scope and requirements.
- [ ] Complete the focused checks below and record exact commands and evidence.
- [ ] Return the isolated implementation branch and parent Completion Report for review.

## Interfaces / Contracts

The parent architecture's Independent allowance storage section is authoritative. Existing published Shared remains reusable structural machinery. Applications own routing, funding, eligibility and authorization. Do not add compatibility paths for the superseded three-table draft or an unreviewed schema.

## Dependencies

None

## Enables

Recalculate from dependent task metadata after architect acceptance; no implicit implementation handoff.

## Acceptance Criteria

- [ ] Implement exact Independent allowance storage fields/constraints in parent architecture.
- [ ] Existing messages with NULL allowanceBlockId remain original block-zero history; no rewriting UsageEvents or mass retagging.
- [ ] Lazy initial block adoption requires proven original funding; unknown historical proof holds for reconciliation, never fabricates funding or charges again.
- [ ] One ACTIVE and one PENDING successor per Conversation; cancelled intents retained and monotonic ordinal never reused.
- [ ] Freeze message block pin at insert and immutable funding identity; independent repair lease survives turn lease expiry.

## Validation

- [ ] Fresh/full-history upgrade, Prisma validate/generate and scoped ERD.
- [ ] Real PostgreSQL FK/uniqueness/owner trigger/message-pin immutability and ACTIVE+inflight concurrency tests.
- [ ] Preserve all historical messages, UsageEvents/reservations and Conversation.checkoutRecoveryId uniqueness.

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
