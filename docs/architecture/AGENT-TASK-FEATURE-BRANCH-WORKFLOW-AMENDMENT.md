# Task feature-branch execution workflow amendment

Effective 2026-09-08, repository tasks use **mirrored task branches**.

For task:

```text
<TASK_ID>
```

use the same branch name in both Git repositories:

```text
parent workspace:
  task/<TASK_ID>

assigned implementation repository:
  task/<TASK_ID>
```

This solves the parent-docs problem directly.

The parent workspace owns:

```text
docs/decisions/<domain>/<ARCH>/<TASK>.md
```

The implementation repository owns its code/tests.

The branches are correlated by `<TASK_ID>` but have separate Git commits because
they are separate repositories.

## Repository agent permissions

The agent MUST commit/push both mirrored task branches during the normal claim/review lifecycle:

```text
implementation task/<TASK_ID>
parent workspace task/<TASK_ID>
```

The parent commit is restricted to the current task report/state file and
explicitly task-owned evidence.

The agent may not merge either branch into `main`.

## Architect ownership

Repository agents do not independently update:

```text
domain _index.md
canonical parent architecture
workspace state rollup
dependency frontier
architect acceptance records
```

Those are reconciled by `moda_architect`.

## Submodule pointer

The agent must not stage the implementation submodule gitlink in the parent
workspace while it points at the feature branch commit.

After architect acceptance, the developer merges the implementation feature
branch first, then updates the parent workspace gitlink to the final merged
implementation-main commit, then merges the parent task branch.

This prevents the parent workspace from pointing permanently at an unmerged
feature commit.

## Dedicated physical task worktrees

Every executable repository task uses dedicated physical parent and
implementation worktrees, even when tasks run sequentially. Agents do not decide
whether isolation is necessary based on perceived concurrency.

The canonical `/moda-task` launcher derives the exact paths from the resolved
workspace root. Missing worktrees are created on first claim; existing correct
worktrees are reused for later attempts/Changes Requested; inconsistent mappings
are a hard stop.

Read `docs/agent-worktree-isolation-policy.md` for the canonical create/reuse,
synchronization and physical-isolation rules.
