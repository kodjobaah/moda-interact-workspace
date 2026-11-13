---
id: ARCH-075-BACKGROUND-001
architecture_id: ARCH-075
title: Implement durable ordered physical delivery lifecycle
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-075-DATABASE-001
  - ARCH-075-SHARED-002
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Implement durable ordered physical delivery lifecycle

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect. Read all frozen contract constants and lifecycle decisions before implementation.

## Objective

Implement durable ordered physical delivery lifecycle.

## Context

User requests logo/shop details before a distinct product image and checkout footer. Existing single-provider-id response cannot safely loop multiple sends. This task owns one bounded prerequisite capability; preserve completed prior behavior.

## Scope

Adopt accepted database submodule and exact published Shared package; owning part freeze/permit/dispatch/ACK/status/reply lookup/reconciliation engine with deterministic tests, no live producer activation.

## Out of Scope

Other repositories/tasks, source main merges/deployment, production sends/replays/resets, billing/usage/cap changes, provider credentials/permissions, unsupported exactly-once assumptions, unbounded fanout/retries, unrelated refactors. Return actual cross-owner gaps.

## Requirements

Implement canonical root logical/perpart physical lifecycle. Atomic immutable manifest/part creation, unique stable identities, perpart same-tenant original control/consent/media/policy checks and no HTTP TX. Admit later part only after durable predecessor DELIVERED/READ; HTTP ACK waits for callback, never synchronously holds a worker/transaction. Immutable deadlineAt from bounded validated policy cancels unadmitted tail via asynchronous queue/repair continuation without resend; one automatic HTTP attempt after ADMITTED, UNKNOWN halts tail and never resends accepted prefix. Recover only PREPARED unattempted tail under original still-valid authority. Persist each MetaID, reconcile status-beforeACK receipt, monotonic duplicate/read-before-delivered aggregation, bounded7day receipt cleanup. Any quoted part resolves exact logical root/recovery safely. RootSENT onlyallACK, DELIVERED onlyall appropriate, READ onlyallREAD; definitive tail fail rootFAILED/partial reason, unknown conservativePENDING. HUMAN command notSENT afterheader. One logical usage/cap admission; retain original usage if prefixaccepted/unknown, no blanket compensation. Preserve old single-plan paths and current sender rate fence. Return any actual App/API projection gap rather than silently changing readers.

### Sender-bound provider correlation

Freeze actual server-selected providerAccountId/providerPhoneNumberId on every physical part. Normalized callback and quote must match both before attaching status/provider IDs or mapping root/recovery. Unknown sender events are not authority to claim a part with the same MetaID. Unmatched receipt dedupe/retention uses these IDs; existing single-message compatibility is preserved.

## Work Items

- [ ] Implement only assigned capability and document compatibility.
- [ ] Complete meaningful required checks and regression/negative evidence.
- [ ] Publish mirrored branch/report and return review, then stop.

## Interfaces / Contracts

Use canonical ARCH075 frozen decisions. Shared owns ordered schema/digest and existing perpart media exports; Database owns durable child/status identity; Background owns provider/current authorization and logical aggregation. Never duplicate validators or fabricate product/provider identity.

## Dependencies

ARCH-075-DATABASE-001
ARCH-075-SHARED-002

## Enables

Only dependent tasks after architect acceptance; never begin them implicitly.

## Acceptance Criteria

- [ ] Assigned bounded capability and frozen contract behavior satisfied.
- [ ] Legacy reads/records remain compatible; no unauthorized cross-owner/billing/security change.
- [ ] Durable/contract identity and fault cases satisfy required checks without silent fallback.
- [ ] Canonical dedicated mirrored worktree, synchronization and recursive evidence recorded; no private proof committed.

## Validation

- [ ] Real PostgreSQL concurrent root/part creation, perpart CAS, crash-before/after permit/ACK, unknown halting, tail resume/control/STOP cancellation, prefix preservation and logical usage tests.
- [ ] Status-beforeACK, duplicate/out-of-order/read-before-delivered, root aggregation and quoted anypart tenant tests.
- [ ] Legacy single-send/reconciliation, package integrity/install, types/scoped lint/build and exact-head full CI.
- [ ] Diff/privacy hygiene and report actual results, no production sends or secrets.

## Stop Condition

After required work and validation, set review, submit Completion Report and STOP. No main merge/deploy or enabled task execution.

## Implementation Notes

You are not alone. Preserve others' edits and canonical prepared isolation. Root owns final merges/deployment. Architecture constants resolve inter-agent assumptions; report genuine gaps before expanding scope.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Pending

### Deviations

None

### Assumptions

None beyond canonical contracts.

### Unresolved Issues

None currently; report concrete gaps.

### Architectural Concerns

No weakening of tenant, immutable outcome or uncertain-provider safety.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual implementation review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
