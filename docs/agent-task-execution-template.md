You are acting as the logical `<AGENT>` agent for the Moda Interact workspace.

Implement the following architectural task:

Architecture:
`<ARCH_ID>`

Task:
`<TASK_ID>`

Task file:
`<TASK_FILE>`

## Startup

Before making any implementation changes:

1. Read the assigned task file in full.

2. Read the parent architecture document referenced by the task.

3. Read every task/document referenced under:

   * `Dependencies`
   * `Interfaces / Contracts`
     where relevant.

4. Read your logical agent definition for the current execution environment:

   * Codex: `.codex/agents/<AGENT>.toml`
   * Claude: `.claude/agents/<AGENT>.agent.md`

5. Read any relevant repository-local development instructions.

6. Read `docs/agent-vcs-ownership-policy.md` and establish/restore the
   mirrored `task/<TASK_ID>` branch in both:
   * the parent workspace repository; and
   * the assigned implementation repository.


The architecture/task documents are authoritative for:

* scope;
* cross-repository design;
* dependencies;
* contracts;
* acceptance criteria.

The repository agent definition is authoritative for:

* repository ownership;
* repository-specific development practice;
* local validation/testing requirements.

If these conflict in a way that changes architecture or scope, stop and return the conflict to `moda_architect`.

## Verify Before Claiming

Immediately before starting implementation, re-read the task file and verify:

* `status: ready`
* `assigned_agent: <AGENT>`
* every task listed in `depends_on` has `status: complete`

Dependency gating is metadata-first. Only tasks explicitly listed in the current task's `depends_on` participate in the dependency-completion gate.

A task recorded as `superseded` elsewhere in the parent architecture, an index, a historical note, an `enables` list, or another task does **not** block the current task merely because it is mentioned there.

A superseded task is relevant to the current task only when either:

* it is still explicitly listed in the current task's `depends_on`, which is coordination drift and must be returned to `moda_architect`; or
* the current task's own scope would directly implement the capability that was superseded, creating a genuine scope conflict.

Do not infer additional dependency gates from historical, superseded, informational, transitive, or sibling-task references in the parent architecture. Do not turn an intentional supersession record into a blocker for an otherwise executable task.

If a parent-architecture statement appears inconsistent with the current task, distinguish between:

* a real conflict affecting the current task's scope, contract, ownership, or explicit dependencies; and
* historical/coordination context that does not change the current task.

Only the former blocks claiming. When in doubt, cite the exact current-task field or requirement that conflicts; do not block solely because another task is marked `superseded`.

If the task is no longer Ready, has already been claimed, or its explicit dependencies are not Complete, do not execute it.

### Manual-gated system-test exception

If `assigned_agent: moda_system_test` and the task/architecture marks the task as
terminal/manual-gated, `status: ready` means **dependency-ready only**. Do not
claim or execute it merely because its dependencies are Complete. A current,
explicit developer invocation of that system-test task is additionally required.
This manual gate never blocks implementation/publication/infrastructure tasks.

## Establish the Mirrored Task Branches

Before claiming, establish or restore the same branch name:

```text
task/<TASK_ID>
```

in **both** Git repositories:

```text
parent workspace repository
assigned implementation repository
```

These are separate Git histories. The shared `<TASK_ID>` is the correlation key.

The parent workspace branch owns only the current task report/state file during
repository-agent execution.

The implementation branch owns the implementation code/tests.

Do not stage the implementation repository/submodule gitlink in the parent
workspace.

If `origin/task/<TASK_ID>` already exists in the parent workspace, inspect that
branch before claiming. It may contain an existing active claim or review state.

Do not claim while another task's uncommitted work is present in either checkout.

## Claim the Task

Read and obey:

```text
docs/agent-executor-normalization-policy.md
```

Normalize the current runtime to one canonical Moda executor value:

```text
GitHub Copilot / github-copilot / copilot -> copilot
Codex                                  -> codex
Claude Code / claude-code / claude     -> claude
Continue                               -> continue
```

Claim the task according to the workspace execution protocol.

Update together:

* `status: in_progress`
* `executor: <copilot|codex|claude|continue>`
* `claimed_at: <current timestamp>`
* increment `attempt`
* update `updated`
* set Completion Report status to `In Progress`

Never persist a provider-specific display label such as `github-copilot` or
`claude-code`.

When checking an existing active claim, compare executor values after
normalization. Alias-equivalent values represent the same executor identity.

Do not reset or overwrite another executor's active claim.


## Git / VCS Isolation and Ownership

Read and obey:

```text
docs/agent-vcs-ownership-policy.md
```

For VCS workflow, that policy supersedes legacy generic task boilerplate saying
repository agents may never commit/push.

### Parent workspace branch

Use:

```text
task/<TASK_ID>
```

The agent MUST commit/push the **current task file only** (plus an explicitly
task-owned evidence artifact) at the claim and review-submission boundaries.

Do not independently commit:

```text
domain _index.md
parent architecture/frontier
workspace state rollup
another task
.codex/.claude definitions
submodule gitlink
```

`moda_architect` owns shared-state reconciliation.

The initial task claim should be committed/pushed promptly on the parent task
branch so the remote branch acts as the durable claim.

### Implementation repository branch

Use the same branch name:

```text
task/<TASK_ID>
```

Implement, validate, commit and push that branch.

### No merge authority

The repository agent MUST push both mirrored feature branches before returning
the task to `review` (unless the push fails and that exact failure is recorded),
but must not:

```text
merge either branch into main
push directly to main
force-push unless the developer explicitly authorizes that exact operation
stage/publish another task's work
```

The developer/user owns both final merges and every push/update of `main`.

### Submodule rule

When the implementation repository is a submodule, checking out its feature
branch may make the parent workspace report the submodule path as modified.

That is expected.

Stage the task file explicitly:

```bash
git add <TASK_FILE>
```

Never stage the submodule path while the feature branch is unmerged.

The developer updates the parent gitlink only after the implementation feature
branch has been accepted and merged into the implementation repository's main.

### Changes Requested

Continue on the SAME mirrored branch pair:

```text
parent task/<TASK_ID>
implementation task/<TASK_ID>
```

Append correction commits; do not create Attempt-specific branches.

### Literal concurrency

If two task agents run at the same time in the same repository, use separate
workspace/repository worktrees or clones. One physical checkout cannot host two
checked-out task branches simultaneously.

### Completion Report

Record both repositories:

```text
### Git / VCS

Task branch: task/<TASK_ID>

Implementation repository:
  repository: <repo>
  commit: <sha>
  remote branch: origin/task/<TASK_ID>
  pushed: yes|no

Parent workspace:
  task file: <TASK_FILE>
  commit: <sha>
  remote branch: origin/task/<TASK_ID>
  pushed: yes|no
  submodule gitlink staged: no

Merged to implementation main: no
Merged to workspace main: no
```

Pushing either feature branch is not architect acceptance.

## Implementation

Implement only the scope defined by `<TASK_ID>`.

Do not independently expand the task into:

* another repository;
* another logical agent's responsibilities;
* unrelated refactoring;
* database/schema changes not authorised by the architecture/task;
* new cross-service contracts;
* changed transaction boundaries;
* changed queue semantics;
* changed security or tenant boundaries;
* deferred architectural work.

The task file, rather than this conversational instruction, is the authoritative implementation scope.

As work progresses:

* update the task Work Items;
* check completed Acceptance Criteria;
* run the Validation specified by the task;
* keep changes within the assigned repository and task scope.

Where the task consumes a shared cross-service contract, use the canonical contract defined by the architecture/task rather than creating a repository-local duplicate.

## Architectural Concerns

If implementation reveals something affecting:

* repository ownership;
* shared contracts;
* database schema;
* transaction boundaries;
* durable-state semantics;
* queue/event behaviour;
* idempotency;
* ordering/concurrency;
* security boundaries;
* another repository;
* the agreed architecture itself;

do not silently work around it.

Record the issue under `Architectural Concerns`.

If it prevents correct implementation, change the task status to `blocked`, document why, and return control to `moda_architect`.

## Validation

Run every validation check required by the task where practical.

Record:

* command executed;
* result;
* failures;
* warnings.

If a required validation cannot be executed, leave it unchecked and explain why in the Completion Report.

Do not mark an Acceptance Criterion complete unless it is actually satisfied.

## Completion Report

Before returning the task, complete:

### Status

`Ready for Review`

### Files Changed

List every significant file modified.

### Work Completed

Describe what was actually implemented.

### Validation Results

Record commands and results.

### Deviations

Record any deviation from the task, or `None`.

### Assumptions

Record implementation assumptions, or `None`.

### Unresolved Issues

Record remaining issues, or `None`.

### Architectural Concerns

Record architectural concerns, or `None`.

## Submit for Architect Review

When all required Work Items, Acceptance Criteria and Validation are complete:

* in the assigned implementation repository:
  * stage only current-task implementation files;
  * inspect the staged diff;
  * commit on `task/<TASK_ID>`;
  * push `origin/task/<TASK_ID>`;
* in the parent workspace:
  * update only the current task file with the Completion Report and `status: review`;
  * stage that task file explicitly;
  * verify the submodule/repository gitlink is NOT staged;
  * commit on the matching `task/<TASK_ID>` parent branch;
  * push the matching parent task branch;
* record both branch commits/push results in the Completion Report;
* update `updated`;
* leave executor/execution history intact;
* return control to `moda_architect`;
* STOP.

Do NOT mark the task `complete`.

Only `moda_architect` may transition:

`review -> complete`

after inspecting and accepting the actual implementation.

Return control to `moda_architect` with a concise summary of:

* task ID;
* implementation completed;
* files changed;
* validation performed;
* deviations;
* unresolved issues;
* architectural concerns.
