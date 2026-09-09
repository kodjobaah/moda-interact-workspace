# Mirrored task branch quick reference

For:

```text
ARCH-007-BACKGROUND-010
```

the task is represented by two independent feature branches:

```text
moda-interact-workspace.git
└── task/ARCH-007-BACKGROUND-010
    └── docs/decisions/background/ARCH-007/BACKGROUND-010-....md

moda-interact-background.git
└── task/ARCH-007-BACKGROUND-010
    ├── src/...
    └── tests/...
```


## Physical task worktrees

The branches above must be checked out in two task-specific physical worktrees
whose absolute paths are supplied by `scripts/start-agent-task.py` through the
`/moda-task` launcher:

```text
parent task worktree:
  <WORKSPACE_PARENT>/<WORKSPACE_NAME>-task-<TASK_ID>

implementation task worktree:
  <WORKSPACE_PARENT>/<WORKSPACE_NAME>.worktrees/<TASK_ID>
```

The launcher derives these paths from the actual workspace checkout, so no
user-home or parent-directory layout is assumed. An architect may first define a
task outside Git with **no branch/worktree at all**; see
`docs/task-definition-materialization.md`. Materialisation creates/reuses the
parent worktree/branch. The implementation worktree is created on first execution
and later attempts reuse it. Never switch a shared checkout or a different
task's worktree onto the branch as a substitute.

Developer execution uses exactly the same branch pair. See
`docs/developer-task-workflow.md` for `/moda_developer_create`,
`/moda_developer_update`, explicit completion and reopen semantics.

## Agent completion

```text
implementation branch
  commit code/tests
  push

parent branch
  commit task Completion Report / status=review
  push
  DO NOT stage moda-interact-background gitlink

STOP
```

## Architect acceptance

```text
review both branches
  -> acceptance overlay for parent workspace task branch
```

## Developer integration

```text
1. merge implementation task branch -> implementation main
2. push implementation main
3. apply/commit architect acceptance docs on parent task branch
4. update parent submodule pointer -> final merged implementation main SHA
5. merge parent task branch -> workspace main
6. push workspace main
```

If squash/rebase merging the implementation branch, always use the final merged
main SHA for the parent gitlink, not the old feature-branch SHA.
