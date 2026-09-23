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
| [COMMERCE-002](COMMERCE-002-switch-connections-routes-to-production-port.md) | Switch U15/U16 routes from fixtures to production ConnectionPort | Complete | COMMERCE-001, ARCH-020-COMMERCE-022 |
| [COMMERCE-003](COMMERCE-003-expose-studio-shop-execution-context.md) | Expose server-validated selected-shop execution context | Complete | ARCH-020-COMMERCE-013, 018 |
| [COMMERCE-004](COMMERCE-004-add-studio-selected-shop-context.md) | Add Studio-wide selected-shop URL/navigation context | Complete | COMMERCE-003 |
| [COMMERCE-005](COMMERCE-005-wire-real-connections-into-tool-authoring.md) | Wire persisted connection revisions into U06 Tool authoring | Complete | COMMERCE-001, COMMERCE-004, ARCH-020-COMMERCE-023 |
| [COMMERCE-006](COMMERCE-006-install-javascript-response-panel-production-composition.md) | Install production JavaScript response-panel composition | Ready | COMMERCE-005, ARCH-020-COMMERCE-026, 027, 031 |

## Execution frontier

COMMERCE-001 through COMMERCE-005 are architect-accepted Complete. The sole remaining
Phase 1 implementation task is now Ready:

```text
ARCH-021-COMMERCE-006   install the production JavaScript response-panel composition
```

COMMERCE-006 Attempt 2 resolved the previously requested Tool-draft edit-version/CAS
continuity and JavaScript validation/publication handoff. Architect re-review identified one
remaining bounded production-functional saved-vs-unsaved defect: the JavaScript panel save can
clear the shared U06 dirty state while independently buffered Input JSON Schema or Response
template edits remain unpersisted. COMMERCE-006 is Ready for Attempt 3; preserve the accepted
Attempt 2 CAS/publication fixes and correct only this draft-identity boundary.
Phase 2 remains intentionally unmaterialised until Phase 1 is reconciled.

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
