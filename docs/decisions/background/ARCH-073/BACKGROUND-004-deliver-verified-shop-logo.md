---
id: ARCH-073-BACKGROUND-004
architecture_id: ARCH-073
title: Deliver verified shop logos within existing recovery messages
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 15
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-073-BACKGROUND-002
  - ARCH-073-BACKGROUND-003
  - ARCH-073-SHARED-002
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Deliver verified shop logos within existing recovery messages

## Architecture

ARCH-073; docs/architecture/ARCH-073-tenant-recovery-shop-headers.md; coordinator moda_architect.

## Objective

Deliver verified shop logos within existing recovery messages.

## Context

User explicitly requests a shop logo where WhatsApp supports it. Existing canonical product-image plans cannot represent a brand image honestly; preserve product identity and the completed text baseline.

## Scope

Exact published Shared contract adoption, optional brand-image preparation for eligible AI/HUMAN/notices, local verified media receipts, HUMAN persisted frozen media/final permit/provider support and regression/docs.

## Out of Scope

Other tasks, source main merges/deployment, live sends, hardcoded merchant assets, fake product IDs, extra unsolicited messages, HTML image markup, database schema/new namespace/credential changes. No production permission mutation inside implementation.

## Requirements

One message only. Existing verified product image always takes priority. Otherwise-plain eligible replies may use verified current-generation same-shop/domain READY logo with complete branded text/header/footer as caption only within1024 Unicode codepoints; missing/unready/unsafe/config-unavailable/oversize image falls back full text with no logo loss of body. No extra logo message, HTML, raw client supplied logo URL, fake product IDs or unsupported plan coercion. Consume exact published Shared bytes, never sibling source. Resolve through existing tenant READY media adapter; bind selected asset provenance/digest and full body to immutable preparation, moderation, takeover/version/control fences, final committed permit and provider dispatch. HUMAN evidence must freeze text+media and replay same bytes/plan; no post-permit lookup selecting a different image. Final permit revalidates current asset/domain/source as needed outside-network-insideTX prohibition. Preserve old text/product plans and old HUMAN commands unchanged, explicit old-reader drain if incompatible. Approved template bodies and all forbidden/unbound sends unchanged. No new schema unless concrete gap returned before change.

## Work Items

- [ ] Implement only the bounded capability and document compatibility/rollout.
- [ ] Add meaningful prior-behavior red and regression/concurrency/security coverage.
- [ ] Complete required validation and mirrored task report/push.

## Interfaces / Contracts

Published @modainteract/moda-interact-shared/commerce/presentation for reusable media schemas/digests; Background owns live provider access, tenant/domain/READY evidence and lifecycle.

## Dependencies

ARCH-073-BACKGROUND-002
ARCH-073-BACKGROUND-003
ARCH-073-SHARED-002

## Enables

Dependent tasks only after architect acceptance.

## Acceptance Criteria

- [ ] Required bounded behavior works without hardcoded identity or broader permissions.
- [ ] Tenant/domain, immutable state, authorization and concurrent-update boundaries remain enforced.
- [ ] Existing unrelated media/frozen content is preserved; no secret/private proof committed.
- [ ] Canonical dedicated mirrored worktree/synchronization/recursive submodule evidence recorded.

## Validation

- [ ] Product-priority, logo/plain text, HUMAN configured/passthrough/notices, missing/stale/foreign/tampered logo, caption/Unicode/full text fallback.
- [ ] Actual PostgreSQL HUMAN frozen media/replay/moderation/final permit/provider identity and competing asset/control/domain changes; legacy text/product evidence.
- [ ] Fresh public-registry package install/integrity, focused + full CI, types/scoped lint/declared build; no live sends.
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
