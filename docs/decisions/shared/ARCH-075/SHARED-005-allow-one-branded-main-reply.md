---
id: ARCH-075-SHARED-005
architecture_id: ARCH-075
title: Allow one complete branded main recovery reply
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 5
executor: codex
claimed_at: 2026-11-13T19:58:00Z
attempt: 1
depends_on:
  - ARCH-075-SHARED-004
enables:
  - ARCH-075-SHARED-006
created: 2026-11-13
updated: 2026-11-13
---

# Allow one complete branded main recovery reply

## Architecture

ARCH075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect.

## Objective

Add the single HEADER order to the existing recovery multipart contract so a complete short branded reply can be delivered in one physical message.

## Context

Actual common AI delivery sends logo/header/footer with no answer, then answer/footer, creating adjacent dividers and duplicate framing. Shared schema currently rejects HEADER-only even though existing HEADER accepts trusted BRAND_IMAGE or TEXT and existing media validation bounds captions. Background cannot emit one logo-bearing complete answer without this additive allowed order. Product images must stay separate; every physical part retains checkout footer.

## Scope

Existing recovery-multipart.ts allowed order plus inseparable tests/docs. One additive HEADER-only order; no new fields/schemaVersion/roles/codecs.

## Out of Scope

Background composition/adoption; version/publication (separate SHARED006); Admin/common source changes; provider/live operations; relaxed image, URL, role, tenant, footer or hash limits.

## Requirements

- Add only HEADER to allowedOrders. Existing HEADER role plan restrictions (TEXT or verified LOGO/SQUARE_LOGO BRAND_IMAGE), caption/body limits and trusted final checkout URL remain unchanged. Do not permit PRODUCT-only, reordered/duplicate parts or arbitrary role/media combinations.
- Existing valid ANSWER, HEADER+ANSWER, HEADER+PRODUCT and HEADER+PRODUCT+ANSWER bytes/digests remain accepted unchanged. A new single HEADER must obey the same trusted footer, provenance and bounded media validation as HEADER in existing plans.
- Browser-safe published entrypoint unchanged. No Node-only import/new validator implementation. No producer use before accepted publication and consumer rollout.
- This is production-compatible additive parsing, but old readers reject HEADER-only. Root must drain/quiesce old workers before new consumer emits this order; frozen old plans remain readable by new consumer. Document limitation, no false universal old-reader compatibility.

## Work Items

- [ ] Capture failing single branded HEADER regression.
- [ ] Add minimal allowed order preserving all old invariants.
- [ ] Run focused/full relevant checks and prepare exact source/report for review; no release.

## Interfaces / Contracts

@modainteract/moda-interact-shared/commerce/presentation RecoveryMultipartDeliveryPlanSchema/parse/build/digest, existing v1 fields and roles unchanged.

## Dependencies

ARCH-075-SHARED-004 Complete.

## Enables

ARCH-075-SHARED-006 publication after independent acceptance.

## Acceptance Criteria

- [ ] Single valid branded HEADER and TEXT HEADER pass unchanged footer/provenance limits.
- [ ] Old valid order/digest vectors remain exact; invalid roles/orders/media/URLs/size/tenant cases still reject.
- [ ] Required checks and normal prepared worktree evidence recorded; no runtime adoption/release.

## Validation

- [ ] Focused RED/GREEN contract vectors, caption1024 boundary/Unicode/trusted footer and old digest/order compatibility negatives.
- [ ] Declared relevant full tests/lint/type/build and package-browser export checks; inspect actual package scripts.
- [ ] Diff/privacy and exact source publication, normal launcher isolation/synchronization evidence.

## Stop Condition

Publish implementation and mirrored report, set review, return and stop. Do not version/publish, merge or implement consumer.

## Implementation Notes

Normal dedicated launcher worktrees; you are not alone, preserve current main and other edits. Return actual dependency gaps before widening. Root owns merges/rollout.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

### Deviations

None

### Assumptions

Root controls rollout and publication authorization.

### Unresolved Issues

Publication/consumer/live proof separate.

### Architectural Concerns

Old readers cannot accept new HEADER-only order; drain gate required.

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

No implicit publication or architecture completion.
