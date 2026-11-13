---
id: ARCH-075-SHARED-001
architecture_id: ARCH-075
title: Define bounded ordered recovery multipart contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Define bounded ordered recovery multipart contracts

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect. Read all frozen contract constants and lifecycle decisions before implementation.

## Objective

Define bounded ordered recovery multipart contracts.

## Context

User requests logo/shop details before a distinct product image and checkout footer. Existing single-provider-id response cannot safely loop multiple sends. This task owns one bounded prerequisite capability; preserve completed prior behavior.

## Scope

Additive browser-safe ordered schema/type/digest reusing current perpart schemas, pure composition/order helper only if needed, exported entrypoint, package metadata candidate5.13.8 and packed artifact tests.

## Out of Scope

Other repositories/tasks, source main merges/deployment, production sends/replays/resets, billing/usage/cap changes, provider credentials/permissions, unsupported exactly-once assumptions, unbounded fanout/retries, unrelated refactors. Return actual cross-owner gaps.

## Requirements

Exact frozen shape/constants from architecture: max3, roles HEADER/PRODUCT/ANSWER and schemaVersion1 kindRECOVERY_MULTIPART parts[{role,plan}]. Existing media validators unchanged. Enforce permitted role/plan/order combinations and no duplicate roles; HEADER thenPRODUCT with optionalANSWER, HEADER+ANSWER, or singleANSWER TEXT fallback. Each physical part carries complete exact trusted checkout footer; builder accepts trusted URL explicitly and validates no truncation, all body/caption bounds. Keep product pair/brand provenance honest; no fake IDs or mixing roles. Preserve legacy exports/digests exactly. Host authorization/current evidence stays outside Shared. Candidate5.13.8 only if current version free; source builds exact immutable consumable tarball, no publication in this task.

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

- [ ] Roles/order/maxpart/footer/Unicode bounds/tampered source/duplicate and long-answer2vs3part golden cases; legacy contracts/digest fixtures unchanged.
- [ ] Full package tests/types/ESM+DTS, exact packed installed public JS/types/browser exports and immutable artifact hash.
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
