# ARCH-023 background tasks

Architecture: [`ARCH-023`](../../../architecture/ARCH-023-merchant-knowledge.md).

Assigned agent: `moda_background`.

Repository: `moda-interact-background`.

Coordinator: `moda_architect`.

The current Background decomposition follows runtime/security boundaries rather than file count:

```text
ARCH-023-DATABASE-001 + ARCH-023-SHARED-002
                 |
                 v
          BACKGROUND-001
      worker/entitlement/repair
          /      |       \
         v       v        v
BACKGROUND-002 BACKGROUND-003 BACKGROUND-006
WEB_PAGE       R2 + CSV/XLSX merchant opt-in
acquisition    acquisition   eligibility gate
         \       |        /
          \      |       /
           \     |      /
              v   v
DATABASE-005 -> BACKGROUND-007
 lease enum       lease cadence
          \       /
           \     /
            v   v
          BACKGROUND-004
      normalize/chunk/embed/
       promote + final entrypoint
                 |
                 v
          BACKGROUND-005
       entitlement reconciliation
                 |
                 v
        planned GATEWAY-001
```

Individual task YAML is authoritative.

| Task | Outcome | Status | Depends on |
|---|---|---|---|
| [BACKGROUND-001](BACKGROUND-001-establish-merchant-knowledge-worker-foundation.md) | Dedicated worker foundation, current entitlement and durable PENDING reconciliation | Complete — Accepted Attempt 4 | DATABASE-001, SHARED-002 |
| [BACKGROUND-002](BACKGROUND-002-acquire-merchant-knowledge-web-pages.md) | SSRF-safe WEB_PAGE acquisition and extraction | Complete — Accepted Attempt 3 | BACKGROUND-001 |
| [BACKGROUND-003](BACKGROUND-003-acquire-merchant-knowledge-uploads.md) | Private R2 CSV/XLSX acquisition/extraction and safe asset cleanup | Complete — Accepted Attempt 2 | BACKGROUND-001 |
| [BACKGROUND-006](BACKGROUND-006-respect-merchant-knowledge-activation.md) | Require merchant opt-in in ingestion eligibility and PENDING reconciliation | Complete — Accepted Attempt 1 | BACKGROUND-001, ADMIN-004 |
| [BACKGROUND-007](BACKGROUND-007-add-merchant-knowledge-runtime-lease-cadences.md) | Add fixed global cadence handling for the two Merchant Knowledge runtime leases | Pending | DATABASE-005 |
| [BACKGROUND-004](BACKGROUND-004-process-and-promote-merchant-knowledge-revisions.md) | Common normalization/chunk/embed/promote pipeline and final dedicated entrypoint | Blocked — Attempt 1 lease prerequisites | BACKGROUND-002, BACKGROUND-003, BACKGROUND-006, DATABASE-005, BACKGROUND-007 |
| [BACKGROUND-005](BACKGROUND-005-reconcile-merchant-knowledge-entitlements.md) | Non-destructive plan entitlement/content-limit reconciliation | Pending | BACKGROUND-004 |

## Execution frontier

DATABASE-001, SHARED-002 and BACKGROUND-001 are Complete/architect-accepted. Attempt 4
closed the final queue-loss validation gate against a task-local disposable pgvector PostgreSQL
database without changing runtime infrastructure or shared test helpers.

BACKGROUND-002 is Complete/architect-accepted at Attempt 3, BACKGROUND-003 is Complete/architect-accepted at Attempt 2, and BACKGROUND-006 is Complete/architect-accepted at Attempt 1. BACKGROUND-004 Attempt 1 then exposed a cross-ownership scheduler-lease prerequisite: the database enum lacks both Merchant Knowledge lease names and the shared Background lease service lacks their cadence mappings.

Current prerequisite sequence:

```text
DATABASE-005   Ready
    |
    v
BACKGROUND-007 Pending
    |
    v
BACKGROUND-004 Blocked — Attempt 1 preserved
    |
    v
BACKGROUND-005 Pending
```

BACKGROUND-004 must not be returned to Ready until DATABASE-005 and BACKGROUND-007 are Complete/architect-accepted and their accepted changes are available on its execution baseline. Gateway deployment must not begin before BACKGROUND-005 is Complete/architect-accepted.

## Merchant opt-in reconciliation

`BACKGROUND-006` is Complete / Accepted Attempt 1. It extends the accepted BACKGROUND-001 eligibility service so missing/false `ShopFeaturePreference` leaves PENDING work dormant. BACKGROUND-004 consumes that activation-aware service before acquisition and promotion; no new queue or scheduler is introduced.
