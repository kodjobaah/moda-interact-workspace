# Moda Interact Task Workflow Quick Start

## Purpose

This is the onboarding entry point for architecture-task execution in Moda
Interact. It explains the normal path without duplicating every policy detail.

Read the deeper documents when you need exact rules:

```text
docs/task-definition-materialization.md
docs/developer-task-workflow.md
docs/coding-agent-workflow.md
docs/agent-worktree-isolation-policy.md
docs/agent-vcs-ownership-policy.md
docs/task-worktree-review-archive-helper.md
```

## One task system, multiple execution paths

Moda Interact does not maintain a separate informal workflow for human changes.
All architecture work uses the same task IDs, dependency graph, worktrees,
branches, attempts, Completion Reports and review history.

The four supported entry paths are:

```text
Architect defines -> Agent implements
Architect defines -> Developer implements
Developer defines -> Developer implements
Developer reopens -> Developer implements next attempt
```

The task frontmatter separates implementation ownership from completion authority:

```yaml
execution_mode: agent | developer
completion_mode: automatic | developer
```

Legacy tasks that omit these fields behave as:

```yaml
execution_mode: agent
completion_mode: automatic
```

`assigned_agent` remains the architectural/domain owner even when the developer is
implementing the task.

## Definition is not materialisation

An architecture task can be defined in a conversation that has no access to a
workspace or Git checkout.

That definition may exist as a portable canonical Markdown task while all of these
are still absent:

```text
parent task branch
parent task worktree
implementation task branch
implementation task worktree
```

This is valid.

When a development environment becomes available, the task is **materialised**:
its canonical task file is placed on the parent `task/<TASK_ID>` branch and
committed/pushed. The implementation worktree is created only when execution
actually starts.

Do not add `defined` or `materialised` as YAML task statuses. The task status model
remains:

```text
pending -> ready -> in_progress -> review -> complete
```

See `docs/task-definition-materialization.md` for the exact portable-definition
contract.

## Canonical task topology

The launcher resolves the canonical workspace from the actual checkout and derives
all paths. Never assume another developer's `/Users/...`, `~/project`, `/home/...`
or other directory layout.

Every executable task eventually uses:

```text
parent task worktree:
  <workspace-parent>/<workspace-name>-task-<TASK_ID>

implementation task worktree:
  <workspace-parent>/<workspace-name>.worktrees/<TASK_ID>

branch in both repositories:
  task/<TASK_ID>
```

First execution:

```text
expected worktree absent + no conflicting registration
    -> create it
```

Later attempt/re-entry:

```text
expected worktree exists + correct repository/branch
    -> reuse it
```

Inconsistent mapping:

```text
wrong repository / wrong branch / another task's physical worktree
    -> workflow isolation error
    -> STOP
```

A clean shared checkout is not a substitute for a dedicated task worktree.

## Commands

### Agent implementation

```text
/moda-task <TASK_ID>
```

Use this for `execution_mode: agent`.

The command resolves/materialises the task when necessary, creates or reuses the
canonical task worktrees, synchronises branches, checks eligibility, claims the
next attempt and hands execution to the assigned logical repository agent.

The repository agent implements, validates, updates the Completion Report, commits
and pushes task-owned task branches, moves the task to `review`, then stops for the
authorised review path. It does not merge or push `main`.

### Developer implementation

```text
/moda_developer_create <TASK_ID>
```

Use this when the developer will implement the task.

It can cover all of these cases:

```text
missing task definition
  -> architect-definition phase
  -> materialise
  -> prepare worktrees
  -> claim

existing ready developer task
  -> prepare/reuse worktrees
  -> synchronise
  -> claim

existing in_progress developer task
  -> verify/reuse current worktrees
  -> resume without inventing another attempt
```

If an architect previously defined the task outside the development environment,
provide the portable definition to this flow; no worktree is assumed to exist merely
because the architecture session defined the task.

### Reconcile/review developer work

```text
/moda_developer_update <TASK_ID>
```

This analyses the actual implementation rather than relying on commit-message
summaries. It considers source/diff, working state, tests, validation, task scope,
acceptance criteria, Git publication and assistance evidence, then updates the task
record and developer self-review.

A developer may make any number of commits, fixes, experiments and reverts within
one workflow attempt. Git remains version control; the task remains the semantic
work/review record.

### Explicit developer completion

```text
/moda_developer_update <TASK_ID> complete
```

For `completion_mode: developer`, successful analysis/review does not itself take
completion authority away from the developer. Explicit `complete` records the
developer's acceptance decision and results in:

```yaml
status: complete
executor: null
claimed_at: null
attempt: <accepted attempt number>
```

For `completion_mode: automatic`, the authorised review path may complete a task
after acceptance. Repository implementation agents still do not self-approve.

## Reopening completed work

Any completed task may be explicitly reopened by the developer:

```text
/moda_developer_update <TASK_ID> reopen
```

Reopen deliberately separates the architecture decision from the next claim:

```text
complete (Attempt N)
    |
    | reopen
    v
ready (Attempt N, executor null, claimed_at null)
    |
    | /moda_developer_create <TASK_ID>
    v
in_progress (Attempt N+1, executor developer)
```

The previous accepted attempt/review is historical evidence and is never deleted.
The same canonical worktrees and `task/<TASK_ID>` branches are reused.

Reopening also triggers dependency-frontier review:

- unclaimed downstream `ready` tasks may safely return to `pending` if a dependency
  is no longer Complete;
- downstream tasks already `in_progress`, `review` or `complete` are not silently
  regressed; they require explicit dependency-regression assessment.

## Assigned-agent assistance during developer execution

A developer task keeps its normal `assigned_agent`. The developer may ask that agent
for assistance.

The assigned agent may, when explicitly asked:

- inspect and explain code;
- debug failures;
- make bounded edits in the canonical developer implementation worktree;
- add/fix tests;
- run validation.

Assistance does not change task ownership. The task remains:

```yaml
execution_mode: developer
executor: developer
```

The assisting agent must not claim, increment attempts, change completion authority,
submit, accept, complete, reopen or merge the task. Assistance should be recorded in
the Completion Report when material to the implementation.

## Synchronisation and Git publication

At the start of each attempt, both task repositories are synchronised using the
same directional rule:

```text
fetch origin --prune
    -> fast-forward local task branch from origin/task/<TASK_ID> when possible
    -> merge current origin/main INTO task/<TASK_ID>
```

Allowed:

```text
origin/main -> task/<TASK_ID>
```

Forbidden to task executors:

```text
task/<TASK_ID> -> main
push/update main
force-push
remote merge action
```

When implementation/submission is finished, task-owned changes are committed and
pushed on the mirrored task branches:

```text
implementation repository: task/<TASK_ID>
parent workspace:          task/<TASK_ID>
```

The parent workspace task/report commit must not stage an implementation submodule
Gitlink merely to record the implementation commit.

Mainline integration remains a separate developer/repository-owner operation after
acceptance.

## Architect-created tasks

### Architect defines -> Agent implements

The architect may create/materialise the task inside a development environment, or
may return a portable definition from an external architecture session.

When execution begins:

```text
/moda-task <TASK_ID>
```

If necessary, the task is materialised first; then implementation worktrees are
prepared and the assigned agent claims it.

### Architect defines -> Developer implements

The architect writes:

```yaml
execution_mode: developer
completion_mode: developer
```

unless the developer explicitly requests another completion mode.

If the architecture session has no workspace access, no branch/worktree is claimed
to exist. Later:

```text
/moda_developer_create <TASK_ID>
```

materialises/prepares/claims the task for developer execution.

### Developer defines -> Developer implements

When the developer invokes `/moda_developer_create` for a missing task, the workflow
first performs the architecture/task-definition phase, then materialises and claims
that same normal architecture task. It does not create a second developer-only task
format.

## System-test gate

System-test tasks are terminal/manual-gated validation. Dependency satisfaction may
make such a task `ready`, but `ready` does not itself authorise execution. Expensive
or environment-dependent system-test work is run only when explicitly invoked by
the developer according to the architecture's gate.

## Review archives

A developer may optionally run the external `compress-workspace-work-tree` helper
from the parent directory of the canonical workspace to create a combined review
ZIP. The archive is a review convenience only; it omits Git metadata and is not
proof of branch ancestry, commit/push state or worktree conformance.

See `docs/task-worktree-review-archive-helper.md`.

## New contributor checklist

Before implementing architecture work:

1. Read this quick start.
2. Read the task and parent architecture document.
3. Use `/moda-task` or `/moda_developer_create`; do not manually repurpose a shared
   checkout.
4. Confirm the launcher-resolved parent and implementation worktree paths.
5. Keep task work on `task/<TASK_ID>` in both repositories.
6. Synchronise before each attempt.
7. Commit/push task branches; never merge/push `main` from task execution.
8. Use `/moda_developer_update` for developer reconciliation/completion/reopen.
9. Preserve attempt/review history rather than rewriting previous accepted work.
10. Follow system-test manual gates where defined.
