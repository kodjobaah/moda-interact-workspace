---
id: ARCH-073-SHARED-001
architecture_id: ARCH-073
title: Define additive prepared brand-image conversation delivery contracts
task_kind: implementation
domain: shared
repository: moda-interact-shared
assigned_agent: moda_shared
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 15
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Define additive prepared brand-image conversation delivery contracts

## Architecture

ARCH-073; docs/architecture/ARCH-073-tenant-recovery-shop-headers.md; coordinator moda_architect.

## Objective

Define additive prepared brand-image conversation delivery contracts.

## Context

User explicitly requests a shop logo where WhatsApp supports it. Existing canonical product-image plans cannot represent a brand image honestly; preserve product identity and the completed text baseline.

## Scope

Pure additive canonical brand-image schema/type/plan/digest and installed public exports under commerce/presentation. Preserve existing ConversationDeliveryPlan TEXT/IMAGE and product-image contracts unchanged. Candidate patch version 5.13.7, verify current package before selecting; if conflict return version gap. No network/runtime orchestration.

## Out of Scope

Other tasks, source main merges/deployment, live sends, hardcoded merchant assets, fake product IDs, extra unsolicited messages, HTML image markup, database schema/new namespace/credential changes. No production permission mutation inside implementation.

## Requirements

Explicit BRAND_IMAGE or equivalent distinct discriminant with genuine brand provenance: exact shop identity, domain/role, current source generation/fingerprint, ready content digest/key/public URL/media facts sufficient for Background freshness validation. Never product IDs. Strict bounded safe HTTPS/auth/port/control and canonical media identity checks; reuse established Shared media/hash primitives. Pure contract does not grant authorization or trust arbitrary URLs. Additive union export may combine legacy product plans with brand variant; do not silently widen old product schema. Full body retained, image caption max1024 Unicode codepoints; invalid/missing media means host-controlled full text fallback, never truncated checkout URL. Public browser-safe exports cannot import Node-only runtime. Background current READY/tenant checks remain mandatory. Keep schema generation/version compatibility and old consumers tests. No new media fetch/transform or separate branding message.

## Work Items

- [ ] Implement only the bounded capability and document compatibility/rollout.
- [ ] Add meaningful prior-behavior red and regression/concurrency/security coverage.
- [ ] Complete required validation and mirrored task report/push.

## Interfaces / Contracts

Published @modainteract/moda-interact-shared/commerce/presentation for reusable media schemas/digests; Background owns live provider access, tenant/domain/READY evidence and lifecycle.

## Dependencies

None

## Enables

Dependent tasks only after architect acceptance.

## Acceptance Criteria

- [ ] Required bounded behavior works without hardcoded identity or broader permissions.
- [ ] Tenant/domain, immutable state, authorization and concurrent-update boundaries remain enforced.
- [ ] Existing unrelated media/frozen content is preserved; no secret/private proof committed.
- [ ] Canonical dedicated mirrored worktree/synchronization/recursive submodule evidence recorded.

## Validation

- [ ] Contract tests reject fake product provenance, unsafe/tampered/cross-shape data, bounds and overlong captions; legacy schemas/digests unchanged.
- [ ] Full package tests/types/build/declarations, immutable packed installed JS/types/public export smoke and exact artifact hashes.
- [ ] Diff/secret hygiene and canonical isolated mirrored execution/report evidence.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation complete, submit review report and STOP. Do not merge/deploy or begin enabled work.

## Implementation Notes

You are not alone. Preserve others' changes. Use prepared canonical packet. Root owns final merges/deployment; architect owns acceptance. Read historical code as evidence, not permission to restore unrelated behavior or stale API assumptions.

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

None beyond explicit prerequisite gates.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual source review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
