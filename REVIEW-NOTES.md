# ARCH-021 initial Tool creation refactor — review bundle

These are portable canonical task definitions prepared for review from the supplied 2026-09-25 workspace/Commerce snapshots. They are **defined but not materialised**: no canonical developer Git branch/worktree, commit or push has been created from this environment.

## Proposed execution graph

```text
COMMERCE-016 Complete ----+
COMMERCE-020 Complete ----+--> COMMERCE-036 Ready
                                  |
                                  v
                            COMMERCE-037 Pending
                                  |
                                  v
                            COMMERCE-038 Pending
                                  |
                                  +-------------------------+
                                                            |
COMMERCE-021 Ready -----------------------------------------+
COMMERCE-022 Complete --------------------------------------+
                                                            |
                                                            v
                                                      COMMERCE-039 Pending
```

## Task intent

- **COMMERCE-036** establishes one atomic lifecycle operation: Tool + revision 1 DRAFT + one operation/audit identity.
- **COMMERCE-037** gives only that operation a narrow PostgreSQL transaction; no whole publication snapshot/diff or global publication lock.
- **COMMERCE-038** exposes one named Studio mutation and exact audit reconciliation result, without post-write snapshot reconstruction.
- **COMMERCE-039** makes new-Tool authoring local-only until final Create. It explicitly excludes Phase 2 tab gating.

## Deliberately deferred until approval/materialisation

The existing ARCH-021 parent architecture document and Commerce `_index.md` have **not** been modified in this review bundle. After the task contracts are approved, `moda_architect` should reconcile those architect-owned documents when the task definitions are materialised in the canonical workspace.
