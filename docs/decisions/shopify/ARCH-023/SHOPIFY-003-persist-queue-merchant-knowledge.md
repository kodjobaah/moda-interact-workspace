---
id: ARCH-023-SHOPIFY-003
architecture_id: ARCH-023
title: Persist and queue Merchant Knowledge configuration
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 31
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-DATABASE-001
  - ARCH-023-DATABASE-003
  - ARCH-023-SHARED-004
enables:
  - ARCH-023-SHOPIFY-004
  - ARCH-023-SYSTEM-TEST-002
created: 2026-09-27
updated: 2026-09-27
---

# Persist and queue Merchant Knowledge configuration

## Architecture

Architecture ID:

`ARCH-023`

Architecture document:

`docs/architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md`

Coordinator:

`moda_architect`

## Objective

Implement the merchant-facing server lifecycle for logical Knowledge Entries, locale sources and refresh requests with authoritative plan-entitlement enforcement and best-effort queue publication.

## Context

Merchants create shop-scoped data for one global Merchant Knowledge capability; they never create Commerce capabilities/releases. PostgreSQL is authoritative and Background processes pending source revisions asynchronously.

## Scope

- Load current `merchant_knowledge` feature eligibility/configuration from the active materialised plan and merchant preference.
- Create/update/delete/reorder logical Knowledge Entries within `maxKnowledgeEntries`.
- Create/replace one URL source per supported locale; every URL change creates a new pending revision and updates latest-revision identity without replacing active revision.
- Implement merchant-triggered Refresh as a new pending revision for the same URL/source.
- Publish process jobs best effort and request reconciliation on enqueue failure using Shared job contracts.
- Return statuses needed by the UI without exposing extracted content/vectors.

## Out of Scope

- Fetching URLs or generating embeddings.
- Commerce capability/release publication.
- Vector lookup.
- Automatic scheduled refresh.

## Requirements

- Server revalidates plan feature eligibility/configuration for every mutation; client limits are informational only.
- Logical entry count, not URL count, enforces commercial limits.
- One locale source per entry; locale variants do not consume extra entry slots.
- Only public-HTTPS syntax is accepted at this boundary; SSRF/network validation remains Background responsibility.
- Refresh/replace preserves current active revision until Background succeeds.
- Entries beyond a downgraded current limit remain stored but cannot be newly activated/returned as entitled.

## Work Items

- [ ] Add service/actions and entitlement loader.
- [ ] Add revision creation/latest pointer and best-effort queue publication.
- [ ] Add deterministic reorder/delete/refresh behaviour.
- [ ] Add authorization/entitlement/idempotency tests.

## Interfaces / Contracts

Produces `MerchantKnowledgeProcessJob` and reconciliation requests from ARCH-023-SHARED-002; persists ARCH-023-DATABASE-003 models.

## Dependencies

- ARCH-023-DATABASE-001
- ARCH-023-DATABASE-003
- ARCH-023-SHARED-004

## Enables

- ARCH-023-SHOPIFY-004
- ARCH-023-SYSTEM-TEST-002

## Acceptance Criteria

- [ ] Plan limit enforced on server.
- [ ] Second locale on same entry does not consume another entry slot.
- [ ] URL replace/Refresh creates a new latest pending revision while old active stays unchanged.
- [ ] Queue failure leaves durable pending state for reconciliation.

## Validation

- [ ] Focused service/action tests with database fixture.
- [ ] Entitlement downgrade/upgrade regressions.
- [ ] Queue contract/idempotency tests.
- [ ] Lint/typecheck/build as declared.
- [ ] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin enabled or follow-on tasks.

## Implementation Notes

None

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

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

Pending.

### Follow-up

None
