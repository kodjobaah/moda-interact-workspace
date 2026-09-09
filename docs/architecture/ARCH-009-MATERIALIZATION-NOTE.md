# ARCH-009 materialisation note

This overlay creates architecture/task definitions only.

It does not create Git branches/worktrees.

Therefore:

- no `task/ARCH-009-*` branch is assumed to exist;
- no task is already claimed;
- use the normal mirrored task launcher/worktree workflow when a task becomes
  Ready;
- parent workspace and implementation repository use the same branch name:
  `task/<TASK_ID>`;
- Changes Requested continue on those same mirrored task branches/worktree;
- task YAML state remains authoritative.
