---
id: ARCH-023-SYSTEM-TEST-002
architecture_id: ARCH-023
title: Validate Merchant Knowledge merchant activation end to end
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
  - ARCH-023-SHARED-002
  - ARCH-023-ADMIN-004
  - ARCH-023-SHOPIFY-004
  - ARCH-023-SHOPIFY-005
  - ARCH-023-BACKGROUND-004
  - ARCH-023-BACKGROUND-005
  - ARCH-023-COMMERCE-002
  - ARCH-023-COMMERCE-004
  - ARCH-023-GATEWAY-001
enables: []
created: 2026-09-27
updated: 2026-09-30
---

# Validate Merchant Knowledge merchant activation end to end

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Validate the final Merchant Knowledge lifecycle end to end, with explicit merchant activation as a hard boundary:

```text
subscription/current plan grants configuration access
        +
ShopFeaturePreference merchant_knowledge = enabled
after merchant action
        -> Background ingestion permitted
        -> Commerce retrieval permitted
```

The test must prove OFF is non-destructive and fail-closed at both ingestion and retrieval boundaries.

## Scope

- current-plan C2 source limits and Purpose/Data Format entitlement;
- existing Recovery Settings generic FeaturePreferences activation;
- WEB_PAGE and CSV/XLSX source configuration;
- private R2 browser upload path;
- PENDING reconciliation and processing;
- pgvector retrieval and tenant isolation;
- disable/re-enable behaviour;
- source-count/type/content-limit downgrade behaviour;
- multilingual retrieval and runtime-data authority;
- queue-loss repair.

## Requirements

### R1 — starting state

Create/use a shop whose current ACTIVE/TRIALING plan maps `merchant_knowledge` with C2 configuration and whose Feature is:

```text
activationMode = MERCHANT_OPT_IN
systemRequired = false
active = true
```

No `ShopFeaturePreference` row initially.

### R2 — subscription grants configuration, not activation

Prove Recovery Settings exposes Merchant Knowledge configuration and the generic Merchant Knowledge FeaturePreferences toggle, while effective Merchant Knowledge is OFF.

Configure at least one WEB_PAGE source while OFF.

Require:

```text
source/revision persisted
revision = PENDING
no processing promotion occurs while OFF
Commerce lookup denied / Tool not effectively available according to runtime grant
no source data deleted
```

### R3 — explicit merchant ON activates processing/retrieval

Enable `merchant_knowledge` through the existing Recovery Settings feature-preference path.

Prove:

1. exact `ShopFeaturePreference.enabled=true` is persisted;
2. existing periodic PENDING reconciliation discovers the previously staged eligible revision without a new queue type;
3. Background processes `PENDING -> PROCESSING -> ACTIVE`;
4. Commerce retrieves only eligible current-shop ACTIVE chunks;
5. the Tool result remains `UNTRUSTED_REFERENCE`.

### R4 — OFF is non-destructive and immediate at authority boundaries

Disable Merchant Knowledge through the same existing feature-preference path.

Prove:

```text
ShopFeaturePreference.enabled=false
ACTIVE source/revision/chunks/vector rows retained
uploaded asset retained
new PENDING work is not ingested/promoted
Commerce retrieval fails closed before embedding/vector query
```

### R5 — re-enable reuses retained ACTIVE knowledge

Re-enable without refetch/reupload. Previously retained valid ACTIVE knowledge must become retrievable immediately, subject to current plan/source/provenance rules. Any eligible PENDING work may resume through periodic reconciliation.

### R6 — file path

Validate one CSV or XLSX direct-to-private-R2 source through signed browser PUT, finalisation, Background hash/format verification and ACTIVE promotion while Merchant Knowledge is ON.

Validate bucket CORS permits the real deployed application origin PUT/preflight and does not provide public read/list access.

### R7 — entitlement/downgrade behaviour

Prove:

- disallowed source type remains persisted/dormant;
- allowed sources beyond `maxKnowledgeSources` remain persisted/dormant;
- lower content limit creates the normal non-destructive entitlement-change replacement only while effectively enabled;
- plan re-entitlement or merchant re-enable does not by itself require refetch of retained valid ACTIVE content.

### R8 — isolation/security/language

Prove cross-shop lookup returns no foreign chunk; multilingual query/source retrieval works using deployed embedding identity; instruction-like Merchant Knowledge cannot grant/invoke an otherwise unavailable Tool; source language does not control customer reply language.

### R9 — queue repair

Simulate initial enqueue loss for an ON merchant. Durable PENDING reconciliation must later publish the same deterministic C4 job and converge.

## Work Items

- [ ] Add activation OFF -> configure -> ON -> process -> OFF -> deny -> ON scenario.
- [ ] Add WEB_PAGE and upload fixtures.
- [ ] Add real private-R2 CORS/presigned-PUT deployment evidence.
- [ ] Add tenant/language/security/downgrade/queue-repair cases.
- [ ] Capture bounded evidence and cleanup.

## Dependencies

- `ARCH-023-DATABASE-001`
- `ARCH-023-SHARED-002`
- `ARCH-023-ADMIN-004`
- `ARCH-023-SHOPIFY-004`
- `ARCH-023-SHOPIFY-005`
- `ARCH-023-BACKGROUND-004`
- `ARCH-023-BACKGROUND-005`
- `ARCH-023-COMMERCE-002`
- `ARCH-023-COMMERCE-004`
- `ARCH-023-GATEWAY-001`

## Acceptance Criteria

- [ ] Current subscription/plan grants configuration access but Merchant Knowledge starts OFF without preference.
- [ ] OFF blocks Background processing and Commerce retrieval without deleting data.
- [ ] Explicit merchant ON causes eligible PENDING work to be processed and ACTIVE knowledge to be retrievable.
- [ ] Disable then re-enable preserves/reuses retained ACTIVE knowledge.
- [ ] WEB_PAGE and private-R2 CSV/XLSX paths both work.
- [ ] Cross-shop, entitlement, multilingual and runtime-data-authority boundaries hold.
- [ ] Queue loss is repaired by durable PENDING reconciliation.
- [ ] R2 browser PUT CORS is validated from the deployed application origin.

## Validation

- [ ] Integrated system scenario against architecture-approved test topology.
- [ ] Database evidence for preference/source/revision/chunk/provenance lifecycle.
- [ ] Queue reconciliation evidence after simulated enqueue loss.
- [ ] R2 preflight/PUT evidence and no public read/list exposure.
- [ ] `git diff --check`.

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
None
### Reviewed Files
None
### Validation Reviewed
None
### Architecture Conformance
Pending.
### Follow-up
None
