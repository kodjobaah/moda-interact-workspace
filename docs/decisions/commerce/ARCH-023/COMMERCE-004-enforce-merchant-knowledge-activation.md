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
status: pending
priority: 62
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-COMMERCE-002
  - ARCH-023-ADMIN-004
enables: []
created: 2026-09-30
updated: 2026-09-30
---

# Enforce Merchant Knowledge merchant activation

## Objective

Apply the final Merchant Knowledge `MERCHANT_OPT_IN` decision **after** the already-in-review COMMERCE-002 completes, without changing COMMERCE-002's review contract.

This bounded follow-up owns two related corrections:

1. update the accepted COMMERCE-002 bootstrap prerequisite/identity guard from the historical `ALWAYS_ENABLED` assumption to `MERCHANT_OPT_IN`; and
2. extend `merchantKnowledge.lookup` operation-level authority so an enabled `ShopFeaturePreference` is required independently of capability association.

Canonical invariant:

```text
retrievable = planEntitled && merchantEnabled
```

## Scope

Expected bounded surface:

```text
COMMERCE-002 bootstrap Feature prerequisite/guard implementation + focused tests
src/commerce/merchant-knowledge/entitlement.ts
merchantKnowledge.lookup operation tests
bootstrap tests affected by Feature activationMode expectation
```

Do not redesign Tool/Capability/release bootstrap or pgvector retrieval.

## Requirements

### R1 — do not rewrite COMMERCE-002 history

COMMERCE-002 remains reviewed/accepted against its original task. This task changes the resulting implementation afterward.

### R2 — bootstrap target Feature mode

The fixed Feature prerequisite is now exactly:

```text
key = merchant_knowledge
active = true
activationMode = MERCHANT_OPT_IN
systemRequired = false
```

Bootstrap reuses it; it does not create/modify the Feature. Wrong mode remains a bounded configuration conflict.

### R3 — operation-level merchant activation authority

Extend current Merchant Knowledge entitlement resolution to require the exact current Feature preference:

```text
ShopFeaturePreference.shopId = trusted shopId
ShopFeaturePreference.featureId = merchant_knowledge Feature id
enabled = true
```

Missing/false preference -> `DENIED`, `retryable=false`, before query embedding or vector lookup.

Continue to ignore browser/model-supplied shop identity and pending future plans.

### R4 — defence in depth independent of capability grant

Even if the same Tool revision is granted through another eligible Capability, `merchantKnowledge.lookup` must still deny when Merchant Knowledge is OFF.

The generic Commerce capability selector may also remove the feature-bound capability because `MERCHANT_OPT_IN` is OFF; operation-level re-check remains mandatory.

### R5 — OFF is non-destructive

Commerce performs no source/revision mutation when disabled. Re-enabling immediately makes retained eligible ACTIVE chunks retrievable again, subject to current plan/source/provenance rules.

### R6 — tests

Prove:

```text
bootstrap accepts MERCHANT_OPT_IN target Feature
bootstrap rejects historical/wrong ALWAYS_ENABLED after ADMIN-004 target state is expected
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

- [ ] COMMERCE-002 implementation is reconciled to the final MERCHANT_OPT_IN Feature prerequisite without changing its historical task/review.
- [ ] Lookup independently requires explicit merchant activation.
- [ ] Disabled Merchant Knowledge cannot cause embedding or pgvector retrieval.
- [ ] Re-enable reuses retained ACTIVE knowledge.

## Validation

- [ ] focused bootstrap regressions
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
