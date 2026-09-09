You are acting as the logical `<AGENT>` agent for the Moda Interact workspace.

Implement the following architectural task:

Architecture:
`<ARCH_ID>`

Task:
`<TASK_ID>`

Task file:
`<TASK_FILE>`

## Launcher-resolved execution topology

The launcher has already resolved the canonical workspace and task topology.
These values are authoritative for this execution:

```text
workspace root:                 <WORKSPACE_ROOT>
workspace parent:               <WORKSPACE_PARENT>
task branch:                    <TASK_BRANCH>
parent task worktree:           <PARENT_WORKTREE>
implementation repository:      <REPOSITORY_PATH>
implementation task worktree:  <IMPLEMENTATION_WORKTREE>
```

Do not recompute these paths from `$PWD`, assume a machine-specific checkout
location, or substitute another physical checkout. `<REPOSITORY_PATH>` is the
canonical repository source/reference checkout used for Git worktree
registration; it is NOT the task implementation checkout. Task implementation
may occur only in `<IMPLEMENTATION_WORKTREE>`.

## Startup

Before making any implementation changes:

1. From `<WORKSPACE_ROOT>`, read:

   * `docs/agent-worktree-isolation-policy.md`;
   * `docs/agent-vcs-ownership-policy.md`.

2. Establish or restore the dedicated **parent task worktree** at exactly:

   `<PARENT_WORKTREE>`

   A missing directory is normal on first claim and MUST be created. An existing
   correct task worktree MUST be reused on later attempts. An existing wrong
   repository/branch/path mapping is a hard `MODA_WORKTREE_ISOLATION_ERROR`; do
   not repair it by switching a shared checkout or another task's worktree.

3. Synchronize the parent task worktree according to
   `docs/agent-worktree-isolation-policy.md`:

   * fetch `origin --prune`;
   * fast-forward from `origin/<TASK_BRANCH>` when that remote task branch
     exists;
   * merge current `origin/main` INTO `<TASK_BRANCH>` when needed;
   * never rebase/force/reset published task history merely to synchronize;
   * never merge `<TASK_BRANCH>` into `main`.

4. Read the assigned task file in full from:

   `<PARENT_WORKTREE>/<TASK_FILE>`

5. Read the parent architecture document referenced by the task from the parent
   task worktree.

6. Read every task/document referenced under:

   * `Dependencies`;
   * `Interfaces / Contracts`, where relevant.

7. Read your logical agent definition for the current execution environment
   from `<WORKSPACE_ROOT>`:

   * Codex: `.codex/agents/<AGENT>.toml`;
   * Claude/Copilot: `.claude/agents/<AGENT>.agent.md`.

8. Do not inspect or modify implementation source yet. First complete the
   eligibility gate below, establish/synchronize the dedicated implementation
   worktree, and make the parent claim durable.

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

If these conflict in a way that changes architecture or scope, stop and return
the conflict to `moda_architect`.

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

## Establish the Implementation Task Worktree

Only after the task passes the eligibility/manual gate above, establish or
restore the dedicated implementation worktree at exactly:

`<IMPLEMENTATION_WORKTREE>`

Use `<REPOSITORY_PATH>` only as the canonical Git source/reference repository
for worktree registration. It is not an authorized task implementation checkout.

Apply the same state machine as the parent worktree:

* missing canonical directory + no conflicting registration: create it;
* existing correct canonical worktree: reuse it;
* task branch checked out at another/shared path, wrong repository/branch, or
  unrelated dirty state: `MODA_WORKTREE_ISOLATION_ERROR` and STOP.

Synchronize it before claiming:

* fetch `origin --prune`;
* fast-forward from `origin/<TASK_BRANCH>` when present;
* merge current `origin/main` INTO `<TASK_BRANCH>` when needed;
* on unexpected task-branch divergence or merge conflict, STOP and report; do
  not rebase, reset, force-push, or merge the task branch into `main`.

Do not inspect implementation source until the parent claim has been committed
and pushed.

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

### Physical worktree isolation

Dedicated physical worktrees are mandatory for every executable repository
task, not only for literal concurrency. Branch cleanliness does not substitute
for physical isolation. The agent MUST use the launcher-resolved
`<PARENT_WORKTREE>` and `<IMPLEMENTATION_WORKTREE>` paths for this task and MUST
NOT switch a shared/default checkout onto `<TASK_BRANCH>`.

### Completion Report

Record both repositories and the physical isolation evidence:

```text
### Git / VCS

Task branch: <TASK_BRANCH>

Physical worktree isolation:
  canonical workspace root: <WORKSPACE_ROOT>
  parent worktree: <PARENT_WORKTREE>
  parent branch: <TASK_BRANCH>
  implementation worktree: <IMPLEMENTATION_WORKTREE>
  implementation branch: <TASK_BRANCH>
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
  commit: <sha>
  remote branch: origin/<TASK_BRANCH>
  pushed: yes|no

Parent workspace:
  task file: <TASK_FILE>
  commit: <sha>
  remote branch: origin/<TASK_BRANCH>
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

### UI internationalisation invariant

This rule applies whenever a task adds or changes user-visible UI, components,
forms, buttons, labels, help text, confirmations, empty states, validation
messages or status copy in an application that already has an internationalisation
foundation.

The implementation agent MUST:

* inspect and reuse that application's existing locale resolver, ICU runtime,
  catalogue files and required-key/catalogue-validation convention before adding
  user-visible copy;
* represent every new user-visible string as an application-owned catalogue key
  rather than hard-coded English in JSX/TSX/templates or server-action UI
  responses;
* add every new key to every locale catalogue currently declared by that
  application. If the application currently has only an English catalogue, the
  string still belongs in that catalogue rather than inline code;
* preserve ICU placeholder names and semantics exactly across locale values;
* use the application's existing locale-aware number/date/time/currency/percentage
  formatting helpers rather than introducing a second formatting/localisation
  mechanism;
* add focused regression coverage proving the new keys are available through the
  existing application i18n path and, where the application maintains a
  required-key manifest, update that manifest.

For `moda-interact`, this means the ARCH-005 merchant UI internationalisation
foundation and `app/i18n/locales/*`. For `moda-interact-admin`, this means the
ARCH-005 Admin ICU foundation and `src/i18n/locales/*` plus the repository's
required-key mechanism where present.

Task prose showing required English copy defines source-language meaning; it does
NOT authorise embedding that English literal directly in a component.

Do not create a second i18n runtime, a task-local translation helper, or a new
locale model unless the task explicitly changes the architecture.

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

* in `<IMPLEMENTATION_WORKTREE>`:
  * stage only current-task implementation files;
  * inspect the staged diff;
  * commit on `<TASK_BRANCH>`;
  * push `origin/<TASK_BRANCH>`;
* in `<PARENT_WORKTREE>`:
  * update only the current task file with the Completion Report and `status: review`;
  * stage that task file explicitly;
  * verify the submodule/repository gitlink is NOT staged;
  * commit on the matching `<TASK_BRANCH>` parent branch;
  * push `origin/<TASK_BRANCH>`;
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
