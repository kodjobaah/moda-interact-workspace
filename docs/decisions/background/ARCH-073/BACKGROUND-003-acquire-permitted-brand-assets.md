---
id: ARCH-073-BACKGROUND-003
architecture_id: ARCH-073
title: Acquire permission-gated Shopify brand assets through existing pipeline
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 15
executor: codex
claimed_at: 2026-11-12T19:19:31Z
attempt: 1
depends_on:
  - ARCH-073-BACKGROUND-001
enables: []
created: 2026-11-12
updated: 2026-11-12
---

# Acquire permission-gated Shopify brand assets through existing pipeline

## Architecture

ARCH-073; docs/architecture/ARCH-073-tenant-recovery-shop-headers.md; coordinator moda_architect.

## Objective

Acquire permission-gated Shopify brand assets through existing pipeline.

## Context

User explicitly requests a shop logo where WhatsApp supports it. Existing canonical product-image plans cannot represent a brand image honestly; preserve product identity and the completed text baseline.

## Scope

Selective restoration of existing BG003 privileged brand reader/mapping alongside accepted basic-name scheduler; existing media source observation/orchestration/runtime pipeline and recovery lifecycle. Tests/docs only owning modules; no new media processor.

## Out of Scope

Other tasks, source main merges/deployment, live sends, hardcoded merchant assets, fake product IDs, extra unsolicited messages, HTML image markup, database schema/new namespace/credential changes. No production permission mutation inside implementation.

## Requirements

Basic shop-name refresh must keep working without read_brand. Privileged brand/logo GraphQL read only after actual current offline-installation read_brand grant and current selected-Shop-ID credential; no self-grant or assumption. Root owns concrete production permission approval. No approved grant => explicit bounded skipped/unavailable status, preserve existing valid brand/media. Claim/commit revalidate active SHOPIFY/domain/installation under locks; no network transaction. Reuse current source generation/R2 transform/verified READY pipeline, safe URL fetching and bounded refresh/backoff; preserve concurrent metadata. Handle absent/null logo truthfully after authorized successful read, never clear assets merely because permission missing/failure. No new public bucket/credentials or provider integration; return concrete readiness/config gaps. Correct stale historical token and pre-lock domain bugs. No wholesale old branch merge.

## Work Items

- [ ] Implement only the bounded capability and document compatibility/rollout.
- [ ] Add meaningful prior-behavior red and regression/concurrency/security coverage.
- [ ] Complete required validation and mirrored task report/push.

## Interfaces / Contracts

Published @modainteract/moda-interact-shared/commerce/presentation for reusable media schemas/digests; Background owns live provider access, tenant/domain/READY evidence and lifecycle.

## Dependencies

ARCH-073-BACKGROUND-001

## Enables

Dependent tasks only after architect acceptance.

## Acceptance Criteria

- [ ] Required bounded behavior works without hardcoded identity or broader permissions.
- [ ] Tenant/domain, immutable state, authorization and concurrent-update boundaries remain enforced.
- [ ] Existing unrelated media/frozen content is preserved; no secret/private proof committed.
- [ ] Canonical dedicated mirrored worktree/synchronization/recursive submodule evidence recorded.

## Validation

- [ ] No-scope/basic-name coexistence; granted reader mapping, missing/revoked scope, failures, absent assets and bounds.
- [ ] Real PostgreSQL duplicate/stale/domain/platform/installation races and media/source JSON preservation.
- [ ] Existing media pipeline unit/integration, types/scoped lint/declared build and exact-head full CI.
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
