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

## Concurrent tasks

Sequential tasks can safely reuse the same physical checkout after both branches
for the earlier task have been committed/pushed and the checkout is clean.

Literal simultaneous tasks require separate workspace/repository worktrees or
clones.
