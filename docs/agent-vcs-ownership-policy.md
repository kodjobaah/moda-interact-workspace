# Moda Interact Git / VCS Ownership Policy

## Decision

Every executable repository task uses a **mirrored task-branch pair**:

```text
parent workspace repository:
  task/<TASK_ID>

assigned implementation repository:
  task/<TASK_ID>
```

The two branches have the same name because the same architecture task owns
both histories, but they are independent Git branches with independent commits.

During the normal task lifecycle, the repository agent MUST commit and push
both mirrored `task/<TASK_ID>` branches: the implementation branch and the
parent-workspace task/report branch. If a push is technically impossible, the
agent must record the exact failure in the Completion Report rather than omit
publication silently.

The developer/user retains exclusive ownership of merging either branch into
`main` and of pushing/updating `main`.

An optional combined review archive produced from the two physical task
worktrees is not a third VCS history and does not change these ownership rules.
See `docs/task-worktree-review-archive-helper.md`.

This is the workspace-wide VCS execution rule.

Physical task isolation is also mandatory. Read and obey:

```text
docs/agent-worktree-isolation-policy.md
```

Every executable repository task uses its launcher-resolved dedicated parent
worktree and dedicated implementation worktree. This is required even for
sequential/single-agent execution. A clean shared checkout does not satisfy the
policy.

## Why two task branches are required

Moda Interact keeps architecture/task state in the parent workspace:

```text
moda-interact-workspace/
  docs/decisions/**
  docs/architecture/**
  .codex/**
  .claude/**
```

while implementation lives in repository/submodule directories such as:

```text
moda-interact-background/
moda-interact/
moda-interact-admin/
moda-interact-database/
...
```

A branch inside `moda-interact-background` cannot contain a change to:

```text
../docs/decisions/background/...
```

because the parent workspace and Background repository have separate Git
histories.

Therefore one task uses the same branch identity in both repositories.

Example:

```text
ARCH-007-BACKGROUND-010

parent workspace:
  task/ARCH-007-BACKGROUND-010
    -> task YAML claim
    -> Completion Report
    -> review state

moda-interact-background:
  task/ARCH-007-BACKGROUND-010
    -> worker/service/test implementation
```

The common `<TASK_ID>` is the correlation key.

## Core task lifecycle

```text
parent main
  |
  +-- task/<TASK_ID> -------------------------------+
        claim commit                                 |
        task report / review commit                  |
                                                     |
implementation main                                  |
  |                                                  |
  +-- task/<TASK_ID>                                 |
        implementation commit(s)                     |
        push feature branch                          |
                                                     v
                                              moda_architect review
                                                     |
                         +---------------------------+-------------------+
                         |                                               |
                   Changes Requested                                Accepted
                         |                                               |
                         v                                               v
              same task branches continue                       developer merges
              correction commits pushed                         implementation branch
                                                                into implementation main
                                                                       |
                                                                       v
                                                                developer applies/
                                                                commits acceptance docs
                                                                on parent task branch
                                                                       |
                                                                       v
                                                                developer updates parent
                                                                submodule pointer to the
                                                                final merged implementation
                                                                main commit when applicable
                                                                       |
                                                                       v
                                                                developer merges parent
                                                                task branch into parent main
```

Repository agents never perform the final merge.

## Canonical branch name

Both repositories use:

```text
task/<TASK_ID>
```

Example:

```text
task/ARCH-007-BACKGROUND-010
```

Do not create separate names such as:

```text
docs/ARCH-007-BACKGROUND-010
implementation/ARCH-007-BACKGROUND-010
task/ARCH-007-BACKGROUND-010-attempt-2
fix/ARCH-007-BACKGROUND-010
```

The repository itself distinguishes which history the branch belongs to.

## One stable branch per task

A task keeps the same branch pair across all attempts:

```text
Attempt 1
  parent:         task/<TASK_ID>
  implementation task/<TASK_ID>

Changes Requested

Attempt 2
  parent:         same task/<TASK_ID>
  implementation same task/<TASK_ID>
```

Later attempts append corrective commits to the same branches.

## Parent workspace branch authority

The repository agent MUST commit/push the matching parent workspace task branch
at claim and review-submission boundaries, but its write authority there is
intentionally narrow.

The repository agent MAY stage/commit:

```text
the current task file:
  docs/decisions/<domain>/<ARCH>/<TASK>.md
```

and, only when the current task contract explicitly owns it, a directly
task-local evidence/report artifact.

The repository agent MUST NOT independently stage/commit:

```text
docs/decisions/<domain>/<ARCH>/_index.md
docs/architecture/**
docs/product/**
WORKSPACE-CURRENT-TASK-STATE.md
another task file
.codex/**
.claude/**
.gitmodules
a submodule gitlink/pointer
```

Those are architect/developer coordination surfaces unless the task explicitly
assigns ownership.

This restriction is important: repository agents report the task they executed;
`moda_architect` reconciles shared indexes, parent architecture frontiers,
dependency promotion and architect-review state.

## Never stage the submodule gitlink from the task agent

Checking out `task/<TASK_ID>` inside a submodule/repository can make the parent
workspace show that submodule path as modified.

That is expected.

For example, the parent may show:

```text
 M moda-interact-background
 M docs/decisions/background/ARCH-007/BACKGROUND-010-....md
```

The repository agent may stage:

```bash
git add docs/decisions/background/ARCH-007/BACKGROUND-010-....md
```

It MUST NOT stage:

```bash
git add moda-interact-background
```

and MUST NOT use:

```bash
git add -A
git add .
```

from the parent workspace when that would stage a changed submodule pointer or
unrelated coordination files.

The parent workspace task branch must not point at an unmerged implementation
feature commit.

The developer updates the parent submodule pointer only **after** the accepted
implementation branch has been merged into the implementation repository's
`main` (or other protected integration branch).

This remains true even if the implementation feature commit itself is later
squashed/rebased during developer-owned integration.

## Claim protocol

The remote parent task branch is part of the durable claim mechanism. Physical
branch establishment and synchronization MUST follow
`docs/agent-worktree-isolation-policy.md`.

Use the launcher-resolved values rather than substituting a current/shared
checkout:

```text
WORKSPACE_ROOT
TASK_BRANCH
PARENT_TASK_WORKTREE
IMPLEMENTATION_TASK_WORKTREE
REPOSITORY_PATH
```

Before claiming, establish or restore the canonical parent task worktree. A
missing directory is the normal first-claim case and must be created. An
existing correct task worktree is reused. An inconsistent mapping is
`MODA_WORKTREE_ISOLATION_ERROR` and must not be repaired by switching the shared
workspace checkout.

Synchronize the parent task branch before reading/claiming:

```text
fetch origin --prune
fast-forward from origin/task/<TASK_ID> when present
merge current origin/main INTO task/<TASK_ID> when needed
```

Do not rebase, reset or force published task history merely to synchronize.

Read the task file from the canonical parent task worktree. If it contains an
active claim by another executor, do not claim it.

Then set the task YAML to `in_progress`, populate executor/claimed_at/attempt,
commit **only the task file** in the parent task worktree, and push the parent
task branch promptly:

```bash
git -C <PARENT_TASK_WORKTREE> add <TASK_FILE>
git -C <PARENT_TASK_WORKTREE> diff --cached -- <TASK_FILE>
git -C <PARENT_TASK_WORKTREE> commit -m "task(<TASK_ID>): claim task"
git -C <PARENT_TASK_WORKTREE> push -u origin "task/<TASK_ID>"
```

That pushed parent branch is the durable remote claim.

Only after the claim is durable should implementation begin.

## Implementation task worktree

Implementation MUST occur only in the launcher-resolved implementation task
worktree. `<REPOSITORY_PATH>` is the canonical repository source/reference
checkout used to create/inspect Git worktrees; it is not the implementation
execution checkout.

A missing implementation task worktree is normal on first claim and must be
created from the task branch according to
`docs/agent-worktree-isolation-policy.md`. Existing correct task worktrees are
reused for later attempts.

Before implementation, synchronize it:

```text
fetch origin --prune
fast-forward from origin/task/<TASK_ID> when present
merge current origin/main INTO task/<TASK_ID> when needed
```

Do not create the task branch from a sibling task branch. Do not use `git switch`
in the shared/default implementation checkout as a substitute for a dedicated
worktree. If the task branch is registered at a non-canonical task path, STOP
with `MODA_WORKTREE_ISOLATION_ERROR`.

## Implementation commit authority

Repository agents may use task-local commands including:

```text
git status
git diff
git diff --check
git log
git show
git fetch
git worktree list --porcelain
git add <specific-files>
git restore --staged
git commit
git push -u origin task/<TASK_ID>
git pull --ff-only
```

Before committing:

```bash
git status --short
git diff --cached
```

Verify that the staged diff contains only the current task.

Never use broad staging when it could absorb sibling work:

```text
git add .
git add -A
```

unless the agent has positively verified the entire repository diff belongs to
the current task.

Preferred implementation commit:

```text
task(<TASK_ID>): <short implementation summary>
```

Changes Requested correction:

```text
task(<TASK_ID>): address architect review
```

## Completion / review submission

When implementation and validation are complete:

### Assigned implementation repository

Commit and push the implementation branch:

```bash
git add <current-task implementation files>
git diff --cached
git commit -m "task(<TASK_ID>): <summary>"
git push -u origin "task/<TASK_ID>"
```

### Parent workspace repository

Update only the current task file:

```text
Completion Report
status: review
updated
```

Then commit and push only that file:

```bash
git add <TASK_FILE>
git diff --cached -- <TASK_FILE>
git commit -m "task(<TASK_ID>): submit for architect review"
git push -u origin "task/<TASK_ID>"
```

Do not stage the implementation repository/submodule path.

The agent then returns control to `moda_architect` and STOPs.

## Required Completion Report VCS evidence

The task Completion Report must record both repositories plus physical
worktree/synchronization evidence:

```text
### Git / VCS

Task branch:
  task/<TASK_ID>

Physical worktree isolation:
  canonical workspace root: <launcher-resolved path>
  parent worktree: <launcher-resolved path>
  parent branch: task/<TASK_ID>
  implementation worktree: <launcher-resolved path>
  implementation branch: task/<TASK_ID>
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current

Implementation repository:
  repository: <repo>
  commit: <implementation-sha>
  remote branch: origin/task/<TASK_ID>
  pushed: yes|no

Parent workspace:
  task file: <TASK_FILE>
  commit: <workspace-doc-sha>
  remote branch: origin/task/<TASK_ID>
  pushed: yes|no
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no
```

If a remote push cannot be performed, state the exact failure. Do not invent
evidence.

## Changes Requested

When `moda_architect` returns Changes Requested:

- keep the same branch name in both repositories;
- do not create attempt-specific branches;
- make only the requested implementation corrections on the implementation task
  branch;
- update the same parent task file on the parent task branch;
- append commits;
- push both task branches;
- return to review.

Architect acceptance/Changes Requested overlays should be applied to the
matching parent workspace `task/<TASK_ID>` branch, not blindly to `main`.

`moda_architect` does not commit/push those overlays. The developer applies and
commits/pushes them, or explicitly delegates that mechanical parent-branch
operation.

## Merge prohibition

Repository agents must never:

```text
merge implementation task branch into implementation main
merge parent workspace task branch into parent main
push directly to main
push task/<TASK_ID>:main
use a remote "Merge pull request" action
```

They must never force-push:

```text
git push --force
git push --force-with-lease
git push --mirror
```

unless the developer explicitly authorizes that exact operation.

The developer/user owns all final integration decisions.

## Developer merge order for submodule tasks

For an accepted task in a submodule/repository, the recommended integration
order is:

```text
1. Merge task/<TASK_ID> into implementation repository main.
2. Push implementation repository main.
3. Determine the final merged implementation main commit.
4. On parent workspace task/<TASK_ID>, apply/commit architect acceptance docs.
5. Update the parent submodule gitlink to the final merged implementation main
   commit.
6. Commit that gitlink update on the parent workspace task branch.
7. Merge parent workspace task/<TASK_ID> into parent workspace main.
8. Push parent workspace main.
```

This ordering prevents the parent workspace from permanently pointing at an
unmerged feature commit.

If the developer uses squash/rebase merge, step 3 is especially important
because the final implementation main SHA may differ from the agent's feature
branch SHA.

## Dedicated worktrees across sequential and concurrent tasks

Dedicated task worktrees are mandatory for every executable repository task,
not only when agents run concurrently.

Once a task has committed/pushed both mirrored branches, leave its canonical
worktrees associated with that task while it waits for review. A later Changes
Requested attempt reuses those same physical paths and branches.

A different task receives its own different canonical parent and implementation
worktree paths. Do not switch the waiting task worktree onto the next task and do
not switch a shared/default checkout onto the next task.

This produces natural concurrency isolation without requiring agents to decide
whether concurrent execution is likely:

```text
TASK-A
  <workspace>-task-TASK-A
  <workspace>.worktrees/TASK-A

TASK-B
  <workspace>-task-TASK-B
  <workspace>.worktrees/TASK-B
```

The developer may remove obsolete worktrees after accepted branch integration,
but active/review/rework task worktrees must not be repurposed for another task.

## Architect authority

`moda_architect` reviews:

```text
implementation repository task branch/commit
+
parent workspace task branch/task report
+
physical worktree/synchronization evidence
```

Missing/mismatched physical worktree evidence is workflow non-conformance. A
clean branch or passing validation does not prove dedicated physical isolation.

and decides:

```text
review -> complete
```

or Changes Requested on the same task.

`moda_architect` must not:

```text
implement repository task code
commit/push implementation branches
merge branches
push main
```

Architect-owned shared-state synchronization includes:

```text
domain _index.md
canonical parent architecture
implementation handoff
workspace task-state rollup
dependency promotions
architect review/acceptance overlays
```

## VCS instruction precedence

For Git/VCS workflow, this file is authoritative over generic task boilerplate,
architecture summaries, handoff prose and domain-index summaries.

A repository agent executing a normal task MUST therefore:

```text
create/reuse the launcher-resolved dedicated task worktrees
synchronize both task branches from their remote task branch and current origin/main
commit + push implementation task/<TASK_ID>
commit + push parent-workspace task/<TASK_ID>
STOP at review
```

and MUST NOT:

```text
merge either task branch into main
push/update main
stage the parent submodule gitlink to an unmerged feature commit
```

Only a current, explicit developer instruction or a task-specific VCS exception
that clearly identifies itself as such may override this policy.

Executable/current task files must not retain generic wording that says
repository agents never commit/push. Historical Completion Reports may continue
to record that an older execution did not commit/push; those statements are
historical evidence, not instructions for a new execution.

## Publication tasks

Git branch publication and package/service publication are separate.

A release task may publish its approved package/service when its task contract
authorizes that external publication, and it still MUST commit/push its mirrored
task branches as part of the normal task lifecycle.

It still must not merge/push `main`.

## Parent-workspace-only tasks

If a task's assigned repository is the parent workspace itself, there is only
one Git repository involved.

Use:

```text
task/<TASK_ID>
```

there and apply the same no-merge/no-main-push rule.

## Developer/user authority

The developer/user owns:

- merging accepted implementation branches into implementation `main`;
- merging accepted parent task branches into workspace `main`;
- squash/rebase/reword choices;
- integration conflict resolution;
- final submodule gitlink selection;
- pushing `main`;
- deleting feature branches after integration;
- removing obsolete task worktrees after accepted branch integration.

The design deliberately makes the correlation explicit:

```text
TASK_ID
  -> implementation task branch
  -> parent task/report branch
  -> architect review
  -> developer-owned integration
```
