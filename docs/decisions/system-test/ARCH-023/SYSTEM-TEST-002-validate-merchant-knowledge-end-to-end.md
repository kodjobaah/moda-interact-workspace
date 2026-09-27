---
id: ARCH-023-SYSTEM-TEST-002
architecture_id: ARCH-023
title: Validate Merchant Knowledge end to end
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 91
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-DATABASE-001
  - ARCH-023-DATABASE-003
  - ARCH-023-SHARED-004
  - ARCH-023-ADMIN-004
  - ARCH-023-SHOPIFY-003
  - ARCH-023-SHOPIFY-004
  - ARCH-023-BACKGROUND-003
  - ARCH-023-BACKGROUND-004
  - ARCH-023-COMMERCE-001
  - ARCH-023-COMMERCE-002
  - ARCH-023-GATEWAY-001
enables: []
created: 2026-09-27
updated: 2026-09-27
---

# Validate Merchant Knowledge end to end

## Architecture

Architecture ID:

`ARCH-023`

Architecture document:

`docs/architecture/ARCH-023-merchant-knowledge-store-aware-commerce-agent.md`

Coordinator:

`moda_architect`

## Objective

Validate Merchant Knowledge from plan entitlement and merchant URL configuration through Background ingestion/pgvector retrieval to CommerceAgent use, including tenant isolation, multilingual behaviour, refresh and security boundaries.

## Context

This terminal task validates the complete Merchant Knowledge architecture after implementation, infrastructure wiring and developer manual validation.

## Scope

- Configure `merchant_knowledge` Feature on a plan with bounded logical-entry/content-unit limits.
- Publish one FEATURE-bound Merchant Knowledge capability/tool through normal Commerce Studio workflow for the test environment.
- Create logical entries with at least two locale variants and ingest public fixture HTML/plain sources.
- Validate content-unit truncation/chunk/vector provenance and exact pgvector lookup.
- Validate manual Refresh success/failure preserving old active revision.
- Validate downgrade exclusion/re-upgrade restoration without refetch.
- Validate cross-shop isolation and malicious multilingual page instructions cannot grant an unavailable capability/tool.
- Validate shop-language knowledge selection independent of customer reply language.

## Out of Scope

- Redis vector search.
- Automatic scheduled crawling.
- Headless-browser content.

## Requirements

- Use the deployed embedding config for both ingestion and lookup.
- System evidence must not log full source body/vector/credentials.
- Any external fixture source must be controlled and deterministic for system test.

## Work Items

- [ ] Add deterministic public-page fixture and merchant knowledge system scenario.
- [ ] Execute ingestion/reconcile/lookup/security/language/downgrade/refresh cases.
- [ ] Capture bounded evidence and cleanup.

## Interfaces / Contracts

Terminal integrated validation of Merchant Knowledge.

## Dependencies

- ARCH-023-DATABASE-001
- ARCH-023-DATABASE-003
- ARCH-023-SHARED-004
- ARCH-023-ADMIN-004
- ARCH-023-SHOPIFY-003
- ARCH-023-SHOPIFY-004
- ARCH-023-BACKGROUND-003
- ARCH-023-BACKGROUND-004
- ARCH-023-COMMERCE-001
- ARCH-023-COMMERCE-002
- ARCH-023-GATEWAY-001

## Enables

None

## Acceptance Criteria

- [ ] One logical entry with multiple locale URLs consumes one entry entitlement.
- [ ] Cross-shop lookup returns no foreign chunk.
- [ ] Unsafe/failed refresh leaves previous active knowledge usable.
- [ ] English customer can receive an English answer derived from shop-language French knowledge.
- [ ] Knowledge content cannot add/refund/execute an ungranted tool.
- [ ] Embedding provenance mismatch fails closed.

## Validation

- [ ] Integrated system scenario against architecture-approved Render/local topology.
- [ ] Database evidence for revision/chunk/provenance lifecycle.
- [ ] Queue reconciliation evidence after simulated enqueue loss.
- [ ] `git diff --check` for system-test repository changes.

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
