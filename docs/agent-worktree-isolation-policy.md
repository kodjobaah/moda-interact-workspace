# Moda Interact Task Worktree Isolation Policy

## Decision

Every executable repository task uses two dedicated physical Git worktrees for
its entire lifetime:

```text
parent task worktree:
  <WORKSPACE_PARENT>/<WORKSPACE_NAME>-task-<TASK_ID>

implementation task worktree:
  <WORKSPACE_PARENT>/<WORKSPACE_NAME>.worktrees/<TASK_ID>
```

Both worktrees use the same branch identity:

```text
task/<TASK_ID>
```

This rule applies even when only one agent is running. A clean branch in a
shared/default checkout is not equivalent to a dedicated task worktree.

The canonical `/moda-task` launcher renders the absolute paths for the current
machine. Those launcher-supplied paths are authoritative. Agents must not infer
paths from `$PWD`, user names, home-directory conventions or examples from
another developer's machine.

## Canonical topology

The only filesystem root the workflow treats as canonical is the resolved Moda
Interact workspace root. The launcher derives everything else from it:

```text
WORKSPACE_ROOT
  = directory containing scripts/start-agent-task.py

WORKSPACE_PARENT
  = parent of WORKSPACE_ROOT

WORKSPACE_NAME
  = basename of WORKSPACE_ROOT

TASK_BRANCH
  = task/<TASK_ID>

PARENT_TASK_WORKTREE
  = WORKSPACE_PARENT / (WORKSPACE_NAME + "-task-" + TASK_ID)

IMPLEMENTATION_TASK_WORKTREE
  = WORKSPACE_PARENT / (WORKSPACE_NAME + ".worktrees") / TASK_ID
```

No rule may assume `/Users/...`, `~/project`, `/home/...` or another fixed
checkout location.

The canonical implementation repository path inside `WORKSPACE_ROOT` is a Git
source/reference checkout used to create and inspect implementation worktrees.
It is not an authorized task implementation checkout.

## Task-worktree state machine

### State A — first claim / worktree absent

A missing canonical task-worktree directory is normal.

After fetching remote refs, create the missing worktree at the exact
launcher-supplied path:

1. If the local `task/<TASK_ID>` branch already exists and is not checked out at
   another path, attach the new worktree to it.
2. Else if `origin/task/<TASK_ID>` exists, create the local task branch from that
   remote branch and attach the canonical worktree.
3. Else create `task/<TASK_ID>` from current `origin/main` and attach the
   canonical worktree.

Do this independently for the parent workspace repository and the assigned
implementation repository.

Do not use `git switch` in a shared checkout as a substitute for creating the
canonical worktree.


### Canonical first-use creation procedure

Use the launcher-resolved paths exactly. The following procedure is normative
for each repository; substitute the parent workspace source/reference repository
for `<SOURCE_REPOSITORY>` when creating the parent worktree and the launcher's
`repository_path` when creating the implementation worktree:

```bash
TASK_BRANCH="task/<TASK_ID>"
SOURCE_REPOSITORY="<SOURCE_REPOSITORY>"
TASK_WORKTREE="<LAUNCHER_RESOLVED_TASK_WORKTREE>"

git -C "$SOURCE_REPOSITORY" fetch origin --prune
git -C "$SOURCE_REPOSITORY" worktree list --porcelain
```

Before creation, verify that `TASK_BRANCH` is not registered at any other
physical path and that `TASK_WORKTREE` is not an existing inconsistent checkout.
Then:

```bash
if git -C "$SOURCE_REPOSITORY" show-ref --verify --quiet "refs/heads/$TASK_BRANCH"; then
  git -C "$SOURCE_REPOSITORY" worktree add "$TASK_WORKTREE" "$TASK_BRANCH"
elif git -C "$SOURCE_REPOSITORY" show-ref --verify --quiet "refs/remotes/origin/$TASK_BRANCH"; then
  git -C "$SOURCE_REPOSITORY" worktree add --track -b "$TASK_BRANCH" \
    "$TASK_WORKTREE" "origin/$TASK_BRANCH"
else
  git -C "$SOURCE_REPOSITORY" worktree add -b "$TASK_BRANCH" \
    "$TASK_WORKTREE" origin/main
fi
```

For the implementation worktree, creating the containing
`<WORKSPACE_NAME>.worktrees` directory with `mkdir -p` is allowed. Do not create
or switch the task branch in the shared/default implementation checkout.

### State B — later attempt / canonical worktree exists

Reuse the same physical worktree and the same `task/<TASK_ID>` branch.

Changes Requested, retries and re-entry do not create attempt-specific branches
or replacement worktrees.

### State C — directory missing but stale Git worktree registration remains

This is not the ordinary first-claim case. Git still associates the task branch
or canonical path with a previous worktree registration.

Report:

```text
MODA_WORKTREE_REGISTRATION_STALE
```

and STOP. Do not run broad `git worktree prune`, delete Git metadata, or force a
replacement worktree automatically; those operations can affect other task
worktrees. The developer may explicitly clean the stale registration, after
which the normal State A creation rule applies.

### State D — inconsistent mapping

An inconsistent mapping is a hard stop. Examples:

- the canonical path exists but belongs to the wrong Git repository;
- the canonical path is checked out on another task branch;
- `task/<TASK_ID>` is checked out at a different task's worktree;
- `task/<TASK_ID>` is checked out in a shared/default implementation checkout;
- another task's physical worktree is being reused;
- the worktree contains unrelated uncommitted work.

Emit/report:

```text
MODA_WORKTREE_ISOLATION_ERROR
```

Include the expected path/repository/branch and the actual
path/repository/branch. STOP. Do not repair the problem by switching a shared
checkout, using `--force`, resetting another task, deleting another worktree or
moving another task's branch.

## Mandatory start-of-attempt synchronization

Every attempt, including Changes Requested, starts by synchronizing both task
worktrees before implementation changes.

For each repository, operate from the canonical task worktree after it has been
created/restored:

1. `git fetch origin --prune`.
2. Verify the task worktree is clean. Do not silently stash, discard, reset or
   overwrite uncommitted work. If it is dirty unexpectedly, STOP and report the
   exact state.
3. If `origin/task/<TASK_ID>` exists, fast-forward the local task branch from its
   own remote branch. Unexpected divergence is a hard stop; do not rebase or
   force-push published task history.
4. Merge current `origin/main` **into** `task/<TASK_ID>` when the task branch does
   not already contain it.
5. If the mainline merge conflicts, STOP and report the conflict. Do not merge
   the task branch into `main` to resolve it.

Allowed direction:

```text
origin/main -> task/<TASK_ID>
```

Forbidden direction for repository agents:

```text
task/<TASK_ID> -> main
```

First-claim worktrees created directly from current `origin/main` already satisfy
step 4 until `origin/main` advances again.


A deterministic synchronization sequence is:

```bash
git -C "$TASK_WORKTREE" fetch origin --prune

test -z "$(git -C "$TASK_WORKTREE" status --porcelain)" || {
  echo "MODA_WORKTREE_DIRTY_ERROR" >&2
  exit 1
}

if git -C "$TASK_WORKTREE" show-ref --verify --quiet \
  "refs/remotes/origin/$TASK_BRANCH"; then
  git -C "$TASK_WORKTREE" merge --ff-only "origin/$TASK_BRANCH" || {
    echo "MODA_TASK_BRANCH_DIVERGENCE" >&2
    exit 1
  }
fi

if ! git -C "$TASK_WORKTREE" merge-base --is-ancestor origin/main HEAD; then
  if ! git -C "$TASK_WORKTREE" merge --no-edit origin/main; then
    git -C "$TASK_WORKTREE" merge --abort || true
    echo "MODA_MAIN_SYNC_CONFLICT" >&2
    exit 1
  fi
fi
```

The agent must record whether each fast-forward/mainline merge was performed or
already unnecessary in the Completion Report.

## Claim and publication boundaries

The parent task branch is the durable task-state/claim history. The
implementation task branch is the durable implementation history.

A normal repository-agent attempt ends only after:

```text
implementation task worktree
  -> validate
  -> commit current-task implementation
  -> push origin/task/<TASK_ID>

parent task worktree
  -> update Completion Report + status: review
  -> commit current task file
  -> push origin/task/<TASK_ID>

STOP for moda_architect review
```

Repository agents MUST NOT:

- merge either task branch into `main`;
- push/update `main`;
- force-push task history unless the developer explicitly authorizes that exact
  operation;
- stage an unmerged implementation submodule gitlink in the parent workspace;
- use a shared/default checkout for task implementation.

The developer/user owns accepted-branch integration into `main`.

## Completion Report evidence

Every repository task Completion Report must record:

```text
Physical worktree isolation:
  canonical workspace root: <absolute launcher-resolved path>
  parent worktree: <absolute launcher-resolved path>
  parent branch: task/<TASK_ID>
  implementation worktree: <absolute launcher-resolved path>
  implementation branch: task/<TASK_ID>
  shared workspace checkout switched/mutated for task work: no
  shared implementation checkout switched/mutated for task work: no
  another task worktree reused: no

Start-of-attempt synchronization:
  parent remote task branch fast-forwarded: yes|not-needed
  parent origin/main incorporated: yes|already-current
  implementation remote task branch fast-forwarded: yes|not-needed
  implementation origin/main incorporated: yes|already-current
```

Missing or contradictory evidence is workflow non-conformance. Branch cleanliness
alone is not evidence of physical isolation.

## Architect review rule

`moda_architect` must verify the physical worktree evidence when reviewing a
repository task. If the implementation was performed in a shared/default
checkout or another task's worktree, the architect must record the workflow
violation. A clean branch, successful push or passing tests does not make shared
physical execution conformant.

The architect may still evaluate the implementation itself. When the code is
otherwise reviewable, the required remediation is normally to recreate/restore
the canonical task worktree, check out the already-pushed task branch there,
rerun the required validation from that worktree and record corrected physical
execution evidence. Do not require reimplementation solely to manufacture new
code changes.

## Developer-side combined review archives

The canonical task worktrees may optionally be combined into a single review
ZIP by the external developer helper `compress-workspace-work-tree` after the
worktrees exist. This helper is deliberately outside the launcher/agent
lifecycle and does not create, repair, synchronize, claim, commit or push task
worktrees.

Its contract, expected parent-directory placement, archive semantics and VCS
evidence limitations are documented in:

```text
docs/task-worktree-review-archive-helper.md
```

A review ZIP is a filesystem convenience only. It does not replace the two
published task branches, Completion Report evidence, or architect verification
of the actual Git histories.
