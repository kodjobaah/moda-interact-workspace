# Architecture Task Definition and Materialisation

> New contributor? Start with [`docs/task-workflow-quickstart.md`](task-workflow-quickstart.md) for the concise end-to-end flow, then return here for the detailed rules.

## Purpose

Moda Interact separates **defining work** from **materialising that work in a
specific Git checkout**.

An architect may define a task in a session that has no access to the developer's
workspace, Git remotes, branches or worktrees. That is valid. A task does not
become a durable workspace task until it is materialised later in a development
environment.

This distinction prevents architecture discussions from pretending that local
filesystem or Git state exists when it does not.

The normal task status model remains unchanged:

```text
pending -> ready -> in_progress -> review -> complete
```

`defined` and `materialised` are lifecycle concepts around that state model;
they are **not additional YAML status values**.

## Terms

### Task definition

The complete architectural specification of a task, including its canonical task
frontmatter and body.

A task definition may exist:

- in an architecture conversation;
- as an attached/downloadable Markdown file;
- on another machine;
- in a developer's notes before it has been committed to the workspace;
- or already in the canonical parent task branch.

A task definition alone does not imply that any of the following exist:

```text
parent task branch
parent task worktree
implementation task branch
implementation task worktree
```

### Portable task definition

When an architect does not have access to the development workspace, the
architect SHOULD return the task as a **portable task definition**.

A portable task definition is the exact canonical Markdown task file that should
later be placed under:

```text
docs/decisions/<domain-folder>/<ARCH_ID>/
```

It is not a second task format and requires no conversion before materialisation.

Its filename MUST match the launcher's canonical task pattern, for example:

```text
BACKGROUND-015-<descriptive-slug>.md
ADMIN-006-<descriptive-slug>.md
SYSTEM-TEST-004-<descriptive-slug>.md
```

Its frontmatter/body MUST be complete enough to become the authoritative task
file without inventing missing architecture during materialisation.

At minimum the frontmatter must be consistent with the route resolved from the
task ID, including:

```yaml
id: ARCH-007-BACKGROUND-015
architecture_id: ARCH-007
domain: background
repository: moda-interact-background
assigned_agent: moda_background
coordinator: moda_architect
execution_mode: agent | developer
completion_mode: automatic | developer
status: pending | ready
executor: null
claimed_at: null
attempt: 0
```

`status` is determined by the real dependency state known when the definition is
authored. Do not mark a task `ready` merely because it is being handed to a
developer.

The portable definition must also contain the normal task sections used by the
project, including the objective/purpose, context, dependencies, scope, work
items, acceptance criteria, validation, non-goals where applicable, Completion
Report and Architect Review placeholders.

### Materialised task

A task is materialised when its canonical task file exists in the canonical
**parent task worktree** on parent branch:

```text
task/<TASK_ID>
```

and that task definition has been committed and pushed to the parent workspace
remote task branch.

Materialisation creates durable task governance state. It does not necessarily
start implementation.

### Execution environment

The implementation worktree is an execution artifact. It is created/reused only
when `/moda-task` or `/moda_developer_create` actually prepares an implementation
attempt.

Therefore all of the following states are valid:

```text
1. External definition only
   task definition:             yes
   parent task worktree:        no
   implementation worktree:    no

2. Materialised but not started
   task definition in Git:      yes
   parent task worktree:        yes
   implementation worktree:    no

3. Execution prepared/active
   task definition in Git:      yes
   parent task worktree:        yes
   implementation worktree:    yes
```

## Architect with workspace access

When `moda_architect` has access to the canonical development workspace, it may
materialise a newly authored task immediately.

The architect:

1. resolves the route using `scripts/start-agent-task.py <TASK_ID> --route-only`;
2. creates/reuses the canonical parent task worktree and parent task branch;
3. writes the canonical task definition there;
4. commits and pushes the parent task definition;
5. leaves implementation worktree creation to the execution path unless the
   developer explicitly requested immediate preparation;
6. does not merge the task branch into `main`.

If the task is developer-executed and the developer says **do it later**, stop
once the task is materialised in `pending`/`ready` state.

If the developer says **create and prepare it now**, the architect may hand off
to `/moda_developer_create <TASK_ID>` after publication of the definition.

## Architect without workspace access

When an architecture session cannot access the development workspace, the
architect MUST NOT claim to have created branches, worktrees, commits or pushed
task state.

Instead the architect:

1. designs the task normally;
2. produces a complete portable task definition matching the canonical filename
   pattern;
3. states that the task is **defined but not materialised**;
4. performs no Git/worktree claims;
5. tells the developer which execution command will materialise it later.

For an agent-executed task:

```text
/moda-task <TASK_ID>
```

may materialise the supplied portable definition before normal agent execution.

For a developer-executed task:

```text
/moda_developer_create <TASK_ID>
```

may materialise the supplied portable definition before developer preparation.

The portable definition may be supplied to the development session as an
attachment, pasted source, current-session artifact or explicit file path. When
an explicit path is useful, the workflow may be invoked as:

```text
/moda-task <TASK_ID> --definition <path-to-task.md>
/moda_developer_create <TASK_ID> --definition <path-to-task.md>
```

The optional `--definition` notation is a workflow convention for the interactive
skill; it is not an argument to `scripts/start-agent-task.py`.

## Materialisation procedure

When a task does not yet exist in the workspace but a portable definition is
available, `/moda-task` or `/moda_developer_create` performs the following
materialisation phase before execution:

1. run:

   ```text
   scripts/start-agent-task.py <TASK_ID> --route-only --json
   ```

   and treat the returned route/topology as authoritative;
2. verify `task_materialized: false`; for an unmaterialised task,
   `execution_mode` and `completion_mode` are intentionally `null` because those
   values belong to task frontmatter and cannot be inferred from the ID alone;
3. validate the portable definition:
   - filename matches `task_pattern`;
   - frontmatter `id`, `architecture_id`, `repository` and `assigned_agent`
     match the route;
   - `execution_mode` and `completion_mode` are valid;
   - no conflicting task file already exists;
   - the definition contains meaningful scope/acceptance/validation rather than
     an ID-only placeholder;
4. create/reuse the canonical parent task worktree using the worktree lifecycle
   policy;
5. establish/synchronise parent `task/<TASK_ID>` from its remote task branch when
   present, otherwise from current `origin/main`;
6. write the portable definition to the canonical task directory **without
   changing its architectural meaning**;
7. commit and push the task definition on parent `task/<TASK_ID>`;
8. rerun the normal launcher so the now-materialised task file becomes the
   authoritative source;
9. only then proceed to dependency checks, implementation-worktree preparation
   and claim/execution.

Materialisation is not permission to change `pending` to `ready`, alter
`depends_on`, change ownership or weaken acceptance criteria. Those are
architecture decisions.

## `/moda-task` behavior when a task is not materialised

`/moda-task` is an execution command, not a task-authoring command.

If its normal resolver cannot find the task definition:

1. resolve `--route-only`;
2. if a matching portable architect definition is available, materialise it as
   above and rerun the resolver;
3. if no portable definition is available, STOP with a clear
   `TASK_DEFINITION_NOT_MATERIALIZED` outcome.

`/moda-task` MUST NOT invent a new architecture task from the ID alone.

If the materialised definition has:

```yaml
execution_mode: developer
```

then `/moda-task` must not claim it. Direct execution to
`/moda_developer_create <TASK_ID>` instead.

## `/moda_developer_create` behavior when a task is not materialised

`/moda_developer_create` supports two valid inputs when the workspace does not
already contain the task:

### Existing external architect definition

If a matching portable definition is available, materialise that definition
without redesigning it, then continue with normal developer preparation if the
task is eligible.

### No external definition

If there is no portable definition, enter the architect task-definition phase
using the developer's request/current architecture context. Produce the normal
canonical task definition first, then materialise it and continue.

Do not fabricate a task from its ID when there is insufficient intent to define
meaningful scope and acceptance criteria.

## No filesystem-layout assumption

All materialisation paths are derived from the verified workspace root returned
by the launcher. Never hard-code or assume:

```text
/Users/...
~/project
/home/<user>/...
a fixed checkout parent
```

A developer may clone the workspace anywhere.

## Git and provenance

An externally defined task has no Git provenance until it is materialised.

After materialisation, Git records the canonical task-file versions and branch
history. The task document continues to record the semantic architecture and
review history.

Do not backfill fictional commit/worktree evidence into an externally authored
portable definition. Materialisation records the first real parent task branch
commit/push.

## Relationship to task review archives

`compress-workspace-work-tree` operates only on materialised/execution worktrees.
A portable task definition outside the workspace is not sufficient input to that
helper.

The generated ZIP remains a review convenience and is not evidence of task
materialisation, branch publication or worktree correctness.
