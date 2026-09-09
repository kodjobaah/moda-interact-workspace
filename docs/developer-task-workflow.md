# Developer-Executed Architecture Task Workflow

> New contributor? Start with [`docs/task-workflow-quickstart.md`](task-workflow-quickstart.md) for the concise end-to-end flow, then return here for the detailed rules.

## Purpose

Moda Interact uses one architecture-task system for repository-agent work and
developer-executed work.

Developer mode is not a bypass around architecture governance. It changes who
implements a task and/or who has final completion authority while preserving the
same:

- task IDs and domain ownership;
- architecture/task definitions;
- dependency graph;
- task-specific parent and implementation worktrees;
- mirrored `task/<TASK_ID>` branches;
- attempt history;
- validation expectations;
- Completion Report and review record;
- prohibition on task executors merging to `main`.

Read this document together with:

```text
docs/task-definition-materialization.md
docs/agent-worktree-isolation-policy.md
docs/agent-vcs-ownership-policy.md
```

The durable execution distinction is expressed with task frontmatter:

```yaml
execution_mode: agent | developer
completion_mode: automatic | developer
```

Legacy tasks that omit these fields are interpreted as:

```yaml
execution_mode: agent
completion_mode: automatic
```

New tasks SHOULD write both fields explicitly.

`assigned_agent` remains the logical/domain owner even when
`execution_mode: developer`. For example, a developer-executed Background task
still records:

```yaml
assigned_agent: moda_background
repository: moda-interact-background
execution_mode: developer
```

This preserves architectural ownership and allows the assigned agent to provide
bounded assistance without taking over the task lifecycle.

## Git is version control; the task is the semantic work record

Git and the architecture task deliberately have different responsibilities.

Git records:

- exact source versions;
- commits, corrections, experiments and reverts;
- source-change sequence;
- branch publication and ancestry.

The task document records:

- why the work exists;
- what contract/scope it must satisfy;
- dependencies and architectural ownership;
- what was ultimately implemented;
- validation and review evidence;
- deviations, assistance and architectural decisions;
- completion/reopen decisions and attempt history.

A developer may make any number of normal Git commits during one task attempt.
Attempts are workflow/review cycles, not commit units. Do not require one commit
per attempt, rewrite ordinary developer history for reporting, or require commit
messages to duplicate the Completion Report.

## Definition, materialisation and execution are separate

A central invariant is:

```text
TASK DEFINITION
      !=
TASK MATERIALISATION
      !=
TASK EXECUTION
```

An architect may define a task in a session with no access to the developer's
workspace. In that state:

```text
task specification:          exists
parent task worktree:        may not exist
parent task branch:          may not exist
implementation worktree:    may not exist
implementation task branch: may not exist
```

That is valid.

When the architect has no workspace access, use the portable canonical task-file
handoff described by `docs/task-definition-materialization.md`. Do not claim that
Git/worktree state exists.

A task becomes **materialised** only when its canonical task file has been placed,
committed and pushed on parent `task/<TASK_ID>` through the canonical parent task
worktree.

The implementation worktree remains an execution artifact and is created/reused
only when `/moda-task` or `/moda_developer_create` actually starts an attempt.

Therefore this is also valid:

```text
materialised task definition: yes
parent task worktree:         yes
implementation worktree:     no
status: pending or ready
```

No new YAML statuses are introduced for definition/materialisation. The normal
state machine remains:

```text
pending -> ready -> in_progress -> review -> complete
```

## Two independent authorities

### `execution_mode`

`agent`
: The normal `/moda-task` path prepares/claims the task through the assigned
  repository agent.

`developer`
: The developer owns the implementation attempt. `/moda_developer_create`
  materialises if necessary, prepares/claims the attempt and hands the canonical
  implementation worktree to the developer.

### `completion_mode`

`automatic`
: A successful **authorized review** performs the completion transition. For
  agent execution this is normally `moda_architect`. For developer execution,
  `/moda_developer_update` performs developer-as-architect review and may
  complete a passing task automatically.

`developer`
: A passing review does not make the task Complete. The task remains `review`
  until the developer explicitly invokes:

```text
/moda_developer_update <TASK_ID> complete
```

`automatic` never means a repository implementation agent may self-complete its
own architecture task.

## Four supported entry workflows

### 1. Architect creates -> Agent implements

There are two valid architect environments.

#### Architect has workspace access

The architect may immediately materialise the task:

```text
architect defines task
      -> route-only resolution
      -> create/reuse parent task worktree
      -> write canonical task file
      -> commit/push parent task/<TASK_ID>
      -> status pending/ready according to dependencies
      -> STOP
```

Use:

```yaml
execution_mode: agent
completion_mode: automatic
```

Do not create the implementation worktree merely to author the task.

Later:

```text
/moda-task <TASK_ID>
      -> reuse/synchronise parent task worktree
      -> create/reuse implementation worktree
      -> verify dependencies/manual gates
      -> assigned agent claims next attempt
      -> agent implements
```

#### Architect has no workspace access

The architect produces a portable canonical task definition and states:

```text
defined:       yes
materialised:  no
Git worktrees: none claimed
Git commits:   none claimed
```

Later, in the development environment:

```text
/moda-task <TASK_ID> [--definition <portable-task.md>]
      -> route-only resolution
      -> validate portable definition
      -> create/reuse parent task worktree
      -> materialise + commit/push task definition
      -> rerun normal resolver
      -> create/reuse implementation worktree
      -> verify dependencies
      -> assigned agent claims
      -> agent implements
```

`/moda-task` may materialise a supplied architect definition but MUST NOT invent
an architecture task from the ID alone.

### 2. Architect creates -> Developer implements

Again the architect may or may not have workspace access.

Use normal domain ownership plus, by default:

```yaml
execution_mode: developer
completion_mode: developer
executor: null
claimed_at: null
attempt: 0
```

`status` is `pending` or `ready` according to real dependency eligibility.

#### Architect has workspace access

The architect may materialise the parent task definition immediately and stop.
The implementation worktree may correctly not exist yet.

Execution starts later with:

```text
/moda_developer_create <TASK_ID>
```

which reuses the parent worktree, creates/reuses the implementation worktree,
synchronises, verifies dependencies and claims the next attempt as developer.

#### Architect has no workspace access

The architect returns a portable canonical task definition. No branches or
worktrees are implied.

Later:

```text
/moda_developer_create <TASK_ID> [--definition <portable-task.md>]
      -> route-only resolution
      -> materialise architect definition into parent task branch
      -> commit/push task definition
      -> rerun normal resolver
      -> create/reuse implementation worktree
      -> verify dependencies
      -> claim as developer
      -> hand control to developer
```

This is the canonical answer to the case where the task exists conceptually but
neither corresponding worktree exists on the developer's machine.

### 3. Developer creates -> Developer implements

The developer invokes:

```text
/moda_developer_create <TASK_ID>
```

and there is no materialised task and no portable architect definition.

The command performs:

```text
route-only resolution
      -> architect task-definition phase using developer intent/current context
      -> produce normal canonical task file
      -> materialise it in parent task worktree
      -> commit/push parent task branch
      -> create/reuse implementation worktree
      -> synchronise both task branches
      -> verify explicit dependencies
      -> claim as developer
      -> hand implementation control to developer
```

A task must not be fabricated from its ID alone. There must be enough intent to
write meaningful scope, work items, acceptance criteria and validation.

Default new developer-created tasks to:

```yaml
execution_mode: developer
completion_mode: developer
executor: null
claimed_at: null
attempt: 0
```

with `pending`/`ready` chosen from actual dependency state.

### 4. Developer reopens -> Developer implements next attempt

A developer may reopen any completed task:

```text
/moda_developer_update <TASK_ID> reopen
```

Reopen is a workflow-state decision, not a claim.

It transitions:

```text
complete, attempt N
        |
        | developer override
        v
ready, attempt N, executor null, claimed_at null
```

It MUST NOT set `in_progress` and MUST NOT increment the attempt.

The prior accepted attempt remains historical.

Then:

```text
/moda_developer_create <TASK_ID>
      -> reuse same parent/implementation worktrees
      -> synchronise
      -> claim
      -> in_progress, attempt N+1, executor developer
```

If the developer instead wants the assigned agent to perform the next attempt
and the task remains `execution_mode: agent`, `/moda-task <TASK_ID>` may claim it.
Using `/moda_developer_create` on a `ready` agent task is an explicit developer
takeover and must be recorded durably.

## `/moda_developer_create <TASK_ID>`

Canonical forms:

```text
/moda_developer_create <TASK_ID>
/moda_developer_create <TASK_ID> --definition <portable-task.md>
```

The second form is useful when an architect defined the task outside the
development environment. An attached/current-session portable definition may be
used without an explicit filesystem path.

The command means **define/materialise/prepare/resume/claim developer execution**.
It is idempotent for an already-active developer task and uses the same task ID,
branches and physical worktrees on every attempt.

### Step 1: resolve route/topology

Use:

```text
scripts/start-agent-task.py <TASK_ID> --route-only --json
```

The route is authoritative for workspace, repository, branch and expected
worktree paths. Never infer them from `$PWD` or a hard-coded machine layout.

### Step 2: task is not materialised

If `task_materialized: false`:

1. if a matching portable architect definition is supplied/attached/current in
   the session, validate and materialise it according to
   `docs/task-definition-materialization.md`;
2. otherwise enter architect task-definition mode using the developer's request
   and current architecture context, create a complete canonical task file, and
   materialise it;
3. commit/push the parent task definition on `task/<TASK_ID>`;
4. rerun the normal launcher so the materialised task becomes authoritative;
5. if the materialised task is `pending`, stop after reporting the dependency
   gate; do not manufacture `ready`;
6. if it is eligible, continue to implementation preparation.

### Step 3: existing-task state handling

#### `ready` + `execution_mode: developer`

Prepare and claim the next developer attempt.

#### `ready` + `execution_mode: agent`

Treat this explicit command as a developer takeover request. Append a durable
execution-ownership amendment, set `execution_mode: developer`, and default
`completion_mode: developer` unless the developer explicitly chooses otherwise.
Do not change `assigned_agent`.

#### `in_progress` + `executor: developer`

Resume/preparation invocation. Reuse/synchronise the same worktrees. Do not
increment the attempt and do not duplicate the claim.

#### `review`

Do not silently reclaim. Use `/moda_developer_update <TASK_ID>` first.

#### `complete`

Do not reopen implicitly. Use `/moda_developer_update <TASK_ID> reopen`.

#### another active executor

Do not steal the claim.

### Step 4: establish/reuse canonical worktrees

The parent task worktree may already exist from materialisation. The
implementation worktree may correctly be absent until this step.

Apply the canonical state machine:

```text
missing + no conflicting registration -> create
existing and correct                  -> reuse
existing wrong mapping                -> MODA_WORKTREE_ISOLATION_ERROR / STOP
stale Git registration                -> report / STOP; do not broad-prune
```

Before a new claim synchronise both task branches:

```text
fetch origin --prune
fast-forward from origin/task/<TASK_ID> when present
merge current origin/main INTO task/<TASK_ID> when needed
```

Never reverse merge direction, rebase/reset published task history merely to
synchronise, force-push, or merge/push `main`.

### Step 5: dependency gate

Before a new claim verify:

```text
status: ready
execution_mode: developer
all explicit depends_on tasks: complete
```

System-test manual gates remain governed by their normal policy.

### Step 6: claim

For a new attempt:

```text
ready, attempt N, executor null
        ->
in_progress, attempt N+1, executor developer
```

Set `claimed_at`/`updated`, record the active attempt, commit the parent task
record and push the parent task branch. The remote parent task branch is the
durable claim.

For an already-active developer attempt, do not increment or duplicate the
claim.

### Step 7: hand control to developer

Do not implement the feature merely because preparation succeeded. Report:

- task ID and current attempt;
- canonical implementation worktree path;
- task branch;
- current completion mode;
- synchronisation result;
- task validation commands where specified.

The developer now works normally and may make any number of commits/fixes/reverts.

When ready for reconciliation/review:

```text
/moda_developer_update <TASK_ID>
```

## `/moda_developer_update <TASK_ID>`

With no action suffix, this command means **reconcile and review the current
implementation cycle**.

It inspects the actual task state rather than relying on commit messages or the
developer's recollection. At minimum it reconciles:

- current task definition and attempt;
- implementation changes relative to the appropriate task/mainline baseline;
- uncommitted task-owned changes;
- task-branch commit history and publication state;
- changed behavior and files;
- required/focused tests and validation;
- deviations/scope amendments discovered during implementation;
- material assistance from the assigned agent;
- physical worktree and synchronisation evidence.

It updates Work Items, Acceptance Criteria, Validation, Completion Report and the
review record to describe the implementation that actually exists.

### Review fails / more work required

Record **Developer Self-Review - Changes Requested** and transition:

```yaml
status: ready
executor: null
claimed_at: null
attempt: <attempt just reviewed>
```

Do not create Attempt N+1 here. The next `/moda_developer_create` claim increments
exactly once.

### Review passes with `completion_mode: automatic`

After task-owned implementation/report changes are committed and pushed, record
Developer Self-Review Accepted and transition:

```yaml
status: complete
executor: null
claimed_at: null
attempt: <accepted attempt; unchanged>
```

Then perform architect dependency-frontier reconciliation.

### Review passes with `completion_mode: developer`

Record a durable passing/Accepted review, but do not decide completion for the
developer. Leave:

```yaml
status: review
executor: null
claimed_at: null
attempt: <reviewed attempt>
```

The explicit completion command is:

```text
/moda_developer_update <TASK_ID> complete
```

## Explicit developer completion

`/moda_developer_update <TASK_ID> complete` is the developer's completion
authority, not permission to fabricate a passing review.

Require:

- the task is materialised;
- the current attempt has a durable passing/Accepted review;
- required Work Items/Acceptance Criteria are not knowingly incomplete;
- task-owned implementation changes are committed/pushed;
- parent task/report changes can be committed/pushed;
- no merge to `main` is required for task completion.

Then record the developer Completion Decision and set:

```yaml
status: complete
executor: null
claimed_at: null
attempt: <accepted attempt; unchanged>
```

Commit/push the parent task branch and recalculate the dependency frontier.
System-test tasks may become dependency-ready but remain manual-gated.

## Explicit reopen

`/moda_developer_update <TASK_ID> reopen` may reopen any `complete` task,
regardless of how it was completed.

Append a durable Developer Override record containing the previous accepted
attempt and reason for reopening. Preserve prior acceptance history.

Transition only to:

```yaml
status: ready
executor: null
claimed_at: null
attempt: <previous accepted attempt; unchanged>
```

Reopen does not claim and does not increment the attempt.

By default preserve `execution_mode` and `completion_mode`. The next execution
command chooses the next executor/attempt.

## Reopen and downstream dependency safety

Reopening a completed dependency can invalidate the dependency frontier.

For downstream tasks still unclaimed (`pending` or `ready`, with no history that
requires preservation), recompute eligibility. A `ready` task whose explicit
dependency is no longer Complete becomes `pending`.

For affected downstream tasks already `in_progress`, `review` or `complete`, do
not silently regress status. Record/report a **dependency regression** and
identify each affected task. The developer acting as architect decides whether
those tasks require another attempt after the reopened dependency is corrected.

Historical acceptance is never deleted merely because a dependency was later
reopened.

## Architect-created developer tasks

`moda_architect` may create tasks for developer execution whenever the developer
asks during an architecture session.

The architect creates the same normal architecture task used by every other
execution path. It MUST NOT create a separate informal developer format.

Unless the developer requests otherwise:

```yaml
assigned_agent: <normal logical domain owner>
execution_mode: developer
completion_mode: developer
executor: null
claimed_at: null
attempt: 0
```

`status` follows real dependency eligibility.

### With development-workspace access

The architect may materialise the parent task definition immediately and
commit/push it. It should not create the implementation worktree merely for
authorship.

### Without development-workspace access

The architect produces the complete portable canonical task definition and
states that it is **defined but not materialised**. It must not claim branch,
worktree, commit or push state that it cannot observe/create.

The developer later runs `/moda_developer_create <TASK_ID>` with the handoff
available; that command materialises it and then prepares execution.

## Assigned-agent assistance during developer execution

`execution_mode: developer` does not prohibit the assigned repository agent from
helping.

When explicitly asked by the developer, the task's `assigned_agent` may enter
**developer-assistance mode** in the existing canonical implementation worktree.
It may:

- inspect the task/implementation;
- explain/debug behavior;
- propose changes;
- make explicitly requested source/test/documentation edits;
- run focused/repository validation;
- help diagnose failed approaches.

Assistance does not transfer lifecycle ownership. The assisting agent MUST NOT:

- claim the task or increment its attempt;
- change `execution_mode`, `completion_mode`, `executor`, `claimed_at` or task
  lifecycle status;
- create replacement/shared task worktrees;
- self-submit, self-accept, complete or reopen the task;
- merge task branches into `main`;
- autonomously commit/push developer work unless the developer explicitly asks
  for that exact publication action.

The developer remains `executor: developer`. `/moda_developer_update` remains the
normal reconciliation/review/completion interface and records material assistance
in the Completion Report.

## Canonical worktrees and synchronisation

All paths come from the launcher's verified workspace root. Never hard-code or
assume `/Users/...`, `~/project`, a username, or a fixed checkout location.

For every executable task there are two task-specific worktrees:

```text
parent task worktree
  -> parent workspace task/<TASK_ID>

implementation task worktree
  -> assigned repository task/<TASK_ID>
```

Definition/materialisation may create the parent worktree before execution.
Implementation worktree creation is deferred until actual execution preparation.

Missing worktrees are normal first-use state; correct existing worktrees are
reused; inconsistent mappings are a hard stop.

Before every newly claimed attempt:

```text
fetch origin --prune
fast-forward from origin/task/<TASK_ID> when present
merge current origin/main INTO task/<TASK_ID> when needed
```

Never merge the task branch into `main` as part of create/update/assistance.

## Publication

Before a task is completed, all task-owned implementation changes and the final
parent task record must be committed and pushed to their respective
`task/<TASK_ID>` branches.

Developer and agent execution may use multiple commits naturally. Publication
of the task branch does not imply integration into `main`.

Final integration into `main` remains a separate developer/user action outside
these execution commands.

## State summary

```text
EXTERNAL ARCHITECTURE SESSION
        |
        v
portable task definition
(no Git/worktrees required)
        |
        | materialise in development environment
        v
pending / ready
        |
        | normal claim
        v
in_progress (Attempt N)
        |
        | review
        v
      review
       /  \
      /    \
changes   accepted
required     |
   |         +--> completion_mode: automatic -> complete
   |         |
   |         +--> completion_mode: developer -> review awaiting explicit complete
   v
 ready
attempt N preserved
   |
   | next claim
   v
in_progress Attempt N+1

complete
   |
   | developer reopen
   v
ready (same accepted attempt number)
   |
   | next claim
   v
in_progress Attempt N+1
```
