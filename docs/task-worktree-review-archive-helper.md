# Task Worktree Review Archive Helper

## Purpose

`compress-workspace-work-tree` is a developer-side review convenience for Moda
Interact task worktrees. It is **not** part of `/moda-task`, task claiming,
agent routing, task execution, validation, Git publication or architect
acceptance.

The helper creates one ZIP that combines:

1. the task-specific parent workspace worktree; and
2. the matching task-specific implementation-repository worktree overlaid at
   the repository/submodule path inside a temporary copy of the parent
   worktree.

This is useful when a reviewer needs one self-contained filesystem snapshot of
both sides of a task without changing either source worktree.

## Location and invocation

The helper is intentionally kept **outside** the canonical workspace Git
repository. It is expected to live in the same parent directory as the
workspace and the task worktree directories:

```text
<WORKSPACE_PARENT>/
  compress-workspace-work-tree
  moda-interact-workspace/
  moda-interact-workspace-task-<TASK_ID>/
  moda-interact-workspace.worktrees/
    <TASK_ID>/
```

The developer may clone `moda-interact-workspace` under any filesystem parent;
no `/Users/...`, `~/project`, `/home/...` or other machine-specific absolute
path is part of the contract.

The current helper implementation uses its **own script directory** as the
worktree parent. Therefore the script must be located beside the workspace/task
worktree layout shown above. The normal invocation is from that parent
directory:

```bash
cd <WORKSPACE_PARENT>
./compress-workspace-work-tree <TASK_ID>
```

For example:

```bash
./compress-workspace-work-tree ARCH-007-ADMIN-003
```

The helper currently expects the standard Moda workspace directory names
`moda-interact-workspace-task-<TASK_ID>` and
`moda-interact-workspace.worktrees/<TASK_ID>`. This external utility is not the
source of truth for those paths; `/moda-task` and
`scripts/start-agent-task.py` remain authoritative for task execution.

## Preconditions

The compression helper consumes an already-established task topology. Before
running it, both physical task worktrees must exist:

```text
parent task worktree:
  <WORKSPACE_PARENT>/moda-interact-workspace-task-<TASK_ID>

implementation task worktree:
  <WORKSPACE_PARENT>/moda-interact-workspace.worktrees/<TASK_ID>
```

If either worktree is absent, the helper exits with an error. It must not be
used as a mechanism for creating, repairing, switching or synchronising Git
worktrees.

Creation/reuse/synchronisation of task worktrees remains governed exclusively
by:

```text
docs/agent-worktree-isolation-policy.md
```

## Archive construction

The helper:

1. determines the implementation repository from the component embedded in the
   task ID;
2. copies the parent task worktree into a temporary staging directory;
3. removes only the staged copy of the normal repository/submodule path;
4. overlays the task-specific implementation worktree at that path;
5. creates `moda-interact-workspace-<TASK_ID>.zip` beside the helper; and
6. deletes the temporary staging directory.

Neither source worktree is modified.

The repository mapping currently covers:

```text
SHOPIFY      -> moda-interact
ADMIN        -> moda-interact-admin
BACKGROUND   -> moda-interact-background
DATABASE     -> moda-interact-database
GATEWAY      -> moda-interact-gateway
MESSAGING    -> moda-interact-messaging
SHARED       -> moda-interact-shared
SITE         -> moda-interact-site
SYSTEM-TEST  -> moda-interact-system-test
```

## Exclusions and secret handling

The archive intentionally excludes common generated/runtime material including
`.git`, `node_modules`, build output, coverage, caches and temporary validation
artifacts.

Real environment files are excluded:

```text
.env
.env.*
```

Safe environment templates are retained where their names match the helper's
allow-list, for example:

```text
.env.example
.env.sample
.env.template
.env.*.example
.env.*.sample
.env.*.template
```

The helper is a convenience filter, not a secret-scanning system. The developer
remains responsible for ensuring task-owned source files do not contain secrets
before distributing an archive.

## Relationship to Git evidence

A generated ZIP is **not** authoritative VCS evidence.

In particular:

- `.git` metadata is intentionally excluded;
- the implementation task worktree is overlaid into the staged parent tree even
  though the parent task branch intentionally does not stage an unmerged
  submodule gitlink;
- the archive does not prove that either task branch was committed or pushed;
- the archive does not prove branch ancestry, remote synchronization or
  `origin/main` incorporation; and
- the archive does not replace the Completion Report's commit/branch/worktree
  evidence.

Architect review may use the archive to inspect the combined filesystem state,
but Git publication and workflow conformance must still be verified from the
actual repositories/branches or recorded VCS evidence.

## Agent boundary

Repository agents are not required to run this helper to complete a task.
Failure to create a ZIP is not a task implementation failure and must not block
a task from being returned to `review` after its required validation, commits
and pushes succeed.

Agents also must not treat the helper as permission to mutate the parent folder
or external developer utilities. Unless an architecture task explicitly owns
this helper, it remains developer-maintained tooling outside the workspace
repository.

A typical developer/reviewer flow is therefore:

```text
/moda-task <TASK_ID>
  -> agent creates/reuses canonical task worktrees
  -> agent synchronizes, claims, implements and validates
  -> agent commits + pushes both task branches
  -> task status: review
  -> agent stops

optional developer action:
  <WORKSPACE_PARENT>/compress-workspace-work-tree <TASK_ID>
  -> combined review ZIP
  -> architect/reviewer may inspect snapshot
```
