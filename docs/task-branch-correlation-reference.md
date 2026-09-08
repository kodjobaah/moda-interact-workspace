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
