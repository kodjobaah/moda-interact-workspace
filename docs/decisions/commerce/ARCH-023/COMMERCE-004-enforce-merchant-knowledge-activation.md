---
id: ARCH-023-COMMERCE-004
architecture_id: ARCH-023
title: Enforce Merchant Knowledge merchant activation
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 62
executor: copilot
claimed_at: 2026-10-01T08:27:30Z
attempt: 1
depends_on:
  - ARCH-023-COMMERCE-002
  - ARCH-023-ADMIN-004
enables: []
created: 2026-09-30
updated: 2026-10-01
---

# Enforce Merchant Knowledge merchant activation

## Objective

Enforce request-time Merchant Knowledge merchant activation after the accepted COMMERCE-002 bootstrap and ADMIN-004 product-policy reconciliation.

COMMERCE-002 is already accepted with the exact `MERCHANT_OPT_IN` bootstrap prerequisite. This task therefore owns only the remaining runtime correction: extend `merchantKnowledge.lookup` operation-level authority so an enabled `ShopFeaturePreference` is required independently of capability association.

Canonical invariant:

```text
retrievable = planEntitled && merchantEnabled
```

## Scope

Expected bounded surface:

```text
src/commerce/merchant-knowledge/entitlement.ts
merchantKnowledge.lookup operation tests
existing generic capability-selection integration only where needed for defence in depth
```

Do not modify or redesign the accepted COMMERCE-002 Tool/Capability/release bootstrap. Do not redesign pgvector retrieval.

## Requirements

### R1 — preserve accepted COMMERCE-002 bootstrap

COMMERCE-002 is Complete / Accepted Attempt 4 with the exact fixed Feature prerequisite:

```text
key = merchant_knowledge
active = true
activationMode = MERCHANT_OPT_IN
systemRequired = false
```

This task MUST NOT reopen, duplicate or replace that bootstrap guard and MUST NOT add any `ShopFeaturePreference` write to bootstrap.

### R2 — operation-level merchant activation authority

Extend current Merchant Knowledge entitlement resolution to require the exact current Feature preference:

```text
ShopFeaturePreference.shopId = trusted shopId
ShopFeaturePreference.featureId = merchant_knowledge Feature id
enabled = true
```

Missing/false preference -> `DENIED`, `retryable=false`, before query embedding or vector lookup.

Continue to ignore browser/model-supplied shop identity and pending future plans.

### R3 — defence in depth independent of capability grant

Even if the same Tool revision is granted through another eligible Capability, `merchantKnowledge.lookup` must still deny when Merchant Knowledge is OFF.

The generic Commerce capability selector may also remove the feature-bound capability because `MERCHANT_OPT_IN` is OFF; operation-level re-check remains mandatory.

### R4 — OFF is non-destructive

Commerce performs no source/revision mutation when disabled. Re-enabling immediately makes retained eligible ACTIVE chunks retrievable again, subject to current plan/source/provenance rules.

### R5 — tests

Prove:

```text
plan entitled + missing preference -> DENIED before embedding/vector query
plan entitled + false preference -> DENIED
plan entitled + true preference -> existing lookup path unchanged
Tool granted through another Capability cannot bypass preference gate
re-enable makes retained ACTIVE knowledge retrievable without re-ingestion
no ShopFeaturePreference row is created by Commerce
```

## Dependencies

- `ARCH-023-COMMERCE-002`
- `ARCH-023-ADMIN-004`

## Acceptance Criteria

- [ ] Accepted COMMERCE-002 bootstrap remains unchanged and preference-neutral.
- [ ] Lookup independently requires explicit merchant activation.
- [ ] Disabled Merchant Knowledge cannot cause embedding or pgvector retrieval.
- [ ] Re-enable reuses retained ACTIVE knowledge.

## Validation

- [ ] focused Merchant Knowledge entitlement/operation tests
- [ ] live PostgreSQL/pgvector proof where existing COMMERCE-001 test contract requires it
- [ ] `npm run typecheck`
- [ ] targeted lint/diagnostics
- [ ] `npm run build`
- [ ] `git diff --check`

## Stop Condition

Set status `review`, complete Completion Report, return to `moda_architect` and STOP.

## Completion Report

### Status
Not Started
### Files Changed
None.
### Work Completed
None.
### Validation Results
None.
### Deviations
None.
### Assumptions
None.
### Unresolved Issues
None.
### Architectural Concerns
None.

## Architect Review

### Review Status
Pending
### Review Notes
Pending.
### Reviewed Files
Pending.
### Validation Reviewed
Pending.
### Architecture Conformance
Pending.
### Follow-up
Pending.
