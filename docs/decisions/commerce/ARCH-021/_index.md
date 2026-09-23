# ARCH-021 Commerce Tasks

Architecture:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Assigned Agent:

`moda_commerce`

Coordinator:

`moda_architect`

## Phase 1 — real Studio service wiring and shop execution context

Phase 1 is deliberately Commerce-only. It does not introduce model/prompt persistence,
Shared contracts, Background changes or live provider execution.

| Task | Description | Status | Dependencies |
|---|---|---|---|
| [COMMERCE-001](COMMERCE-001-expose-production-connections-studio-port.md) | Expose production Connections through Studio server actions | Complete | ARCH-020-COMMERCE-020, 024, 028 |
| [COMMERCE-002](COMMERCE-002-switch-connections-routes-to-production-port.md) | Switch U15/U16 routes from fixtures to production ConnectionPort | Ready | COMMERCE-001, ARCH-020-COMMERCE-022 |
| [COMMERCE-003](COMMERCE-003-expose-studio-shop-execution-context.md) | Expose server-validated selected-shop execution context | Complete | ARCH-020-COMMERCE-013, 018 |
| [COMMERCE-004](COMMERCE-004-add-studio-selected-shop-context.md) | Add Studio-wide selected-shop URL/navigation context | Ready | COMMERCE-003 |
| [COMMERCE-005](COMMERCE-005-wire-real-connections-into-tool-authoring.md) | Wire persisted connection revisions into U06 Tool authoring | Pending | COMMERCE-001, COMMERCE-004, ARCH-020-COMMERCE-023 |
| [COMMERCE-006](COMMERCE-006-install-javascript-response-panel-production-composition.md) | Install production JavaScript response-panel composition | Pending | COMMERCE-005, ARCH-020-COMMERCE-026, 027, 031 |

## Execution frontier

COMMERCE-001 is architect-accepted Complete. The current Ready frontier is:

```text
ARCH-021-COMMERCE-002   install the production ConnectionPort into U15/U16 routes
ARCH-021-COMMERCE-003   server-validated shop execution context
```

They are independent and may execute in parallel in separate canonical task worktrees.
Readiness does not automatically launch either task.
COMMERCE-003 is architect-accepted Complete. The current Ready frontier is:

```text
ARCH-021-COMMERCE-001   production Connections server-boundary correction/review path
ARCH-021-COMMERCE-004   Studio-wide selected-shop navigation context
```

They are independent at this point and may execute/rework in separate canonical task
worktrees. Readiness does not automatically launch either task.

## Phase 1 dependency graph

```text
ARCH-021-COMMERCE-001 ─────> ARCH-021-COMMERCE-002
          |
          +------------------------------+
                                         |
ARCH-021-COMMERCE-003 -> COMMERCE-004 -> COMMERCE-005 -> COMMERCE-006
                                         ^
                                         |
                              COMMERCE-001+
```

Phase 1 is complete only when COMMERCE-001 through COMMERCE-006 are architect-accepted
Complete and the parent ARCH-021 Phase 1 exit criteria are reconciled. Phase 2 is not
materialised by this index.
