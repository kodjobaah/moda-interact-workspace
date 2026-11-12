---
id: ARCH-073-BACKGROUND-001
architecture_id: ARCH-073
title: Acquire basic Shopify shop name with bounded durable refresh
task_kind: implementation
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables: 
  - ARCH-073-BACKGROUND-002
created: 2026-11-12
updated: 2026-11-12
---

# Acquire basic Shopify shop name with bounded durable refresh

## Architecture

ARCH-073; docs/architecture/ARCH-073-tenant-recovery-shop-headers.md; coordinator moda_architect.

## Objective

Persist authenticated basic Shopify shop names using bounded durable refresh without requiring read_brand.

## Context

Current main lacks preserved Shopify name acquisition; wrappers cannot render a missing ShopBrand name. User requests generic shop branding, never a hardcoded single-shop patch.

## Scope

Selectively adapt preserved BG003 source-reader/scheduler/state/repository patterns into current Background. Own new basic-name reader/service/runner modules or narrowly adapted old module, orchestration JSON preservation/lease helpers, recovery entrypoint lifecycle, tests/package scripts/docs. Do not restore media reads.

## Out of Scope

Logo/media enablement, read_brand/other permission changes, privileged Brand queries, wholesale historical merge, unrelated token refactor, production DB backfill, schema/new namespace/Shared release, other repositories, live sends or deployment. Return genuine cross-owner gaps.

## Requirements

Use current selected-Shop-ID token API (historical getShopifyAccessToken(domain) is now wrong). Basic shop.name query only, bounded response/time/cancellation. Claim and completion lock/revalidate same active SHOPIFY shop/domain; domain/status/platform/installation changes during read reject stale writes. No network in transaction. Durable leases/cadence/backoff must survive multiple workers/restarts; bounded keyset scan handles absent brand row and hot-tenant fairness. Preserve media JSON and source state on every update; no failure may blank known good name or manufacture branding. Current token internals remain unchanged. Basic name succeeds when read_brand is absent. Document source/name refresh cadence and safe retry.

## Work Items

- [ ] Implement only the bounded capability and document compatibility/rollout.
- [ ] Add meaningful prior-behavior red and regression/concurrency/security coverage.
- [ ] Complete required validation and mirrored task report/push.

## Interfaces / Contracts

Background-local current authenticated Shopify token and ShopBrand persistence; existing published Shared schemas/logging remain canonical. No new cross-service wire is planned.

## Dependencies

None

## Enables

ARCH-073-BACKGROUND-002

## Acceptance Criteria

- [ ] Required bounded behavior works without hardcoded identity or broader permissions.
- [ ] Tenant/domain, immutable state, authorization and concurrent-update boundaries remain enforced.
- [ ] Existing unrelated media/frozen content is preserved; no secret/private proof committed.
- [ ] Canonical dedicated mirrored worktree/synchronization/recursive submodule evidence recorded.

## Validation

- [ ] Provider/parser tests: basic name without read_brand, no privileged fields, malformed/oversize/timeouts/revoked token safe failures.
- [ ] Actual PostgreSQL absent-row first sync, duplicate/competing claims, expired lease/stale result, domain/status/platform/installation changes, retry/cadence and concurrent media preservation.
- [ ] Recovery-worker startup/shutdown and bounded scans; existing orchestration tests remain green.
- [ ] Types, task-owned lint, declared build and exact-head full CI; inspect package scripts first.
- [ ] Diff/secret hygiene; synthetic fixtures and mocked providers, no real Meta send or production write.

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

No broader provider grant is available or needed.

### Unresolved Issues

None currently; report new contract gaps.

### Architectural Concerns

No source expansion beyond explicit scope without architect reconciliation.

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
