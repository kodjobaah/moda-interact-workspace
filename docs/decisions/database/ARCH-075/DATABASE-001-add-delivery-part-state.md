---
id: ARCH-075-DATABASE-001
architecture_id: ARCH-075
title: Persist bounded physical delivery parts and early status receipts
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-11-13T00:38:32Z
attempt: 1
depends_on: []
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Persist bounded physical delivery parts and early status receipts

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect. Read all frozen contract constants and lifecycle decisions before implementation.

## Objective

Persist bounded physical delivery parts and early status receipts.

## Context

User requests logo/shop details before a distinct product image and checkout footer. Existing single-provider-id response cannot safely loop multiple sends. This task owns one bounded prerequisite capability; preserve completed prior behavior.

## Scope

Prisma schema/additive PostgreSQL migration, necessary constraints/indexes/relations/immutable fields and owning migration tests/ERD. Existing ConversationMessage stays logical root; no new root status enum.

## Out of Scope

Other repositories/tasks, source main merges/deployment, production sends/replays/resets, billing/usage/cap changes, provider credentials/permissions, unsupported exactly-once assumptions, unbounded fanout/retries, unrelated refactors. Return actual cross-owner gaps.

## Requirements

Implement ConversationDeliveryPart and minimal ConversationDeliveryStatusReceipt per canonical architecture. Max3 via ordinal0..2 CHECK + unique(root,ordinal). Root FK/cascade, unique perpart dispatch/provider IDs, immutable frozen payload/digest/ordinal/root identity. Persist PREPARED/ADMITTED/ACKNOWLEDGED/DELIVERED/READ/FAILED/UNKNOWN/CANCELLED child states, ACK/status/failure timestamps and bounded codes. Do not invent provider state transitions in source service. Status receipts dedupe providerID/status/provider timestamp, attach optional part, indexed unmatched receivedAt for7day bounded cleanup; no raw webhook/customer JSON. Existing root/command provider columns remain compatible and untouched. Protect known provider evidence and immutable preparation against updates; migration safe for populated tables. No application/provider logic or network in migration. Coordinate exact generated field/enum names to architect before consumers.

## Work Items

- [ ] Implement only assigned capability and document compatibility.
- [ ] Complete meaningful required checks and regression/negative evidence.
- [ ] Publish mirrored branch/report and return review, then stop.

## Interfaces / Contracts

Use canonical ARCH075 frozen decisions. Shared owns ordered schema/digest and existing perpart media exports; Database owns durable child/status identity; Background owns provider/current authorization and logical aggregation. Never duplicate validators or fabricate product/provider identity.

## Dependencies

None

## Enables

Only dependent tasks after architect acceptance; never begin them implicitly.

## Acceptance Criteria

- [ ] Assigned bounded capability and frozen contract behavior satisfied.
- [ ] Legacy reads/records remain compatible; no unauthorized cross-owner/billing/security change.
- [ ] Durable/contract identity and fault cases satisfy required checks without silent fallback.
- [ ] Canonical dedicated mirrored worktree, synchronization and recursive evidence recorded; no private proof committed.

## Validation

- [ ] Prisma validate/generate and real PostgreSQL migration on populated legacy baseline.
- [ ] Duplicate ordinal/provider/dispatch IDs, ordinal bounds, FK/cascade, immutable payload/provider evidence and indexed status lookup/dedupe tests; no destructive rollback assumptions.
- [ ] Repository-required schema/migration checks and diff/ERD validation, inspect package scripts.
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
