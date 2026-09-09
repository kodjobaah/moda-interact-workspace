---
name: moda_developer_create
description: Define, materialise, prepare, resume, or claim a Moda Interact architecture task for developer execution.
disable-model-invocation: true
---

Use this skill when the developer invokes either:

```text
/moda_developer_create <TASK_ID>
/moda_developer_create <TASK_ID> --definition <portable-task.md>
```

The optional `--definition` notation identifies a portable architect task
handoff. A matching attached/current-session task definition may be used without
an explicit filesystem path.

This is the canonical developer-execution entry point. It does not create a
second task format. Read and obey:

```text
docs/developer-task-workflow.md
docs/task-definition-materialization.md
docs/agent-worktree-isolation-policy.md
docs/agent-vcs-ownership-policy.md
docs/agent-executor-normalization-policy.md
```

## 1. Resolve canonical route/topology first

Extract exactly one fully-qualified task ID. Resolve the canonical workspace in
the same location-independent way as `/moda-task`, then invoke:

```bash
python3 "$MODA_WORKSPACE_ROOT/scripts/start-agent-task.py" \
  "$TASK_ID" --route-only --json
```

The returned route is authoritative for:

```text
workspace_root
workspace_parent
task_branch
parent_worktree_path
implementation_worktree_path
repository
repository_path
agent
task_directory
task_pattern
task_file
task_exists
task_materialized
task_definition_state
status
execution_mode
completion_mode
```

Do not derive replacements from `$PWD`, a username/home directory, or a guessed
checkout layout. When `task_materialized: false`, `execution_mode` and
`completion_mode` may be `null`; do not substitute defaults before validating or
authoring the actual task definition.

## 2. If the task is not materialised

A task may already have been **defined by an architect outside the development
environment** even though no task file, branch or worktree exists locally.

Do not assume a missing task file means no architecture exists.

### 2A. Portable architect definition is available

If the current invocation/session contains a matching portable task definition,
or `--definition <path>` was supplied:

1. validate it using `docs/task-definition-materialization.md`;
2. require its filename to match the resolver `task_pattern`;
3. require frontmatter identity/ownership to match the resolver route;
4. create/reuse only the canonical **parent task worktree** required for
   materialisation;
5. establish/synchronise parent `task/<TASK_ID>` according to the worktree/VCS
   policy;
6. write the portable definition into the canonical `task_directory` without
   redesigning or weakening it;
7. commit and push the parent task definition on `task/<TASK_ID>`;
8. rerun the normal launcher/resolver so the now-materialised task file becomes
   authoritative.

Do not claim that the external architect created worktrees/commits unless the
handoff contains real evidence from a workspace-enabled architecture session.
The materialisation commit is the first real Git publication when the external
handoff had none.

### 2B. No portable architect definition is available

Task authorship is an architect responsibility even when the developer will
implement it.

Adopt `moda_architect` task-definition rules using the developer request/current
architecture context. Create a normal complete architecture task; do not invent
an empty task from its ID.

Default a newly developer-created task to:

```yaml
execution_mode: developer
completion_mode: developer
executor: null
claimed_at: null
attempt: 0
```

Choose `status: pending` or `status: ready` from the real explicit dependency
state. Preserve the normal domain `assigned_agent`, `repository` and
`coordinator: moda_architect`.

Create/reuse the canonical parent task worktree, write the task there, commit and
push the parent task definition, then rerun the resolver.

### Materialisation boundary

Materialisation creates durable task governance. It does NOT itself require the
implementation worktree.

However this command continues directly into execution preparation when the
materialised task is eligible, so step 4 below may create the implementation
worktree in the same invocation.

If the materialised task is `pending`, report the blocking dependencies and STOP.
Do not rewrite it to `ready` merely because the developer wants to start.

## 3. Existing/materialised task state handling

### `ready` + `execution_mode: developer`

Prepare and claim the next developer attempt.

### `ready` + `execution_mode: agent`

Treat this explicit command as a developer takeover request. Append a durable
execution-ownership amendment, set:

```yaml
execution_mode: developer
completion_mode: developer
```

unless the developer explicitly requests preservation of automatic completion.
Do not change `assigned_agent`.

### `in_progress` + `executor: developer`

This is a resume/preparation invocation. Reuse/synchronise the same worktrees.
Do not increment the attempt and do not create another claim.

### `review`

Do not silently reclaim. Direct the current cycle through:

```text
/moda_developer_update <TASK_ID>
```

### `complete`

Do not reopen implicitly. Use:

```text
/moda_developer_update <TASK_ID> reopen
```

### another active executor

Do not steal the claim. Report the active claim and STOP.

## 4. Establish/reuse canonical worktrees

Use the launcher paths exactly.

Parent worktree:

```text
parent_worktree_path
```

Implementation worktree:

```text
implementation_worktree_path
```

The parent worktree may already exist because materialisation/authorship needed
it. The implementation worktree may correctly be absent until actual execution.

Apply the canonical state machine:

```text
missing + no conflicting registration -> create
existing and correct                  -> reuse
existing wrong mapping                -> MODA_WORKTREE_ISOLATION_ERROR / STOP
stale Git registration                -> report / STOP; do not broad-prune
```

Synchronise each execution worktree before a new claim:

```text
fetch origin --prune
fast-forward from origin/task/<TASK_ID> when present
merge current origin/main INTO task/<TASK_ID> when needed
```

Never reverse the merge direction, rebase/reset published task history merely to
synchronise, force-push, or merge/push `main`.

## 5. Verify dependencies

Before a new claim verify:

```text
status: ready
execution_mode: developer
all explicit depends_on tasks: complete
```

System-test manual gates remain governed by their normal policy.

## 6. Claim as developer

For a new attempt transition:

```text
ready, attempt N, executor null
        ->
in_progress, attempt N+1, executor developer
```

Set `claimed_at` and `updated`, update Completion Report status to In Progress,
commit only the task-owned parent record and push the parent task branch. The
remote parent task branch is the durable claim.

For resume of an already-active developer attempt, do not increment or duplicate
the claim.

## 7. Hand control back to the developer

Do not implement the feature merely because preparation succeeded. Report:

- task ID and current attempt;
- whether an external definition was materialised in this invocation;
- canonical implementation worktree path;
- task branch;
- current completion mode;
- synchronisation result;
- any relevant validation commands specified by the task.

The developer now works normally in the implementation worktree and may make any
number of commits/fixes/reverts during the attempt.

When ready for reconciliation/review, use:

```text
/moda_developer_update <TASK_ID>
```
