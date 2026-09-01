<!-- MODA-DEVELOPMENT-BASELINE:START -->
## Workspace environment preflight

Agent execution may begin either:

- at the `moda-interact-workspace` root; or
- directly inside one of the repositories contained by the workspace.

Before reading, claiming, validating, or modifying any task, establish the
workspace root.

First check the current directory and, if necessary, its immediate parent:

```bash
if test -f .nvmrc && test -d .codex/agents; then
  export MODA_WORKSPACE_ROOT="$PWD"
elif test -f ../.nvmrc && test -d ../.codex/agents; then
  cd ..
  export MODA_WORKSPACE_ROOT="$PWD"
else
  echo "Unable to establish the moda-interact-workspace root."
  echo "Current directory: $PWD"
  exit 1
fi
```

After normalisation, verify the expected workspace anchors:

```bash
test -f "$MODA_WORKSPACE_ROOT/.nvmrc"
test -d "$MODA_WORKSPACE_ROOT/.codex/agents"
test -d "$MODA_WORKSPACE_ROOT/.claude/agents"
```

Changing from a direct child repository to its parent workspace root is normal
task setup. It is not an implementation change and must not cause the task to
be reported as blocked.

Do not:

- search the wider filesystem for the workspace;
- reconstruct a user-specific absolute path;
- assume a particular username or home directory;
- use `/Users/...`, `/home/...`, or `/mnt/data/...` as the workspace root;
- claim or modify the task until the workspace root has been established.

If neither the current directory nor its immediate parent is the workspace
root, stop and report the unexpected working directory.

Once established, always return to the workspace root with:

```bash
cd "$MODA_WORKSPACE_ROOT"
```

and navigate to repositories using workspace-relative paths.

Do **not** automatically bootstrap Node, run the workspace doctor, or read the
development baseline merely because a task has started.

Before the first Node-related command in the current shell:

```bash
if ! command -v node >/dev/null 2>&1; then
  source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"
fi
```

Node recovery is owned exclusively by `scripts/bootstrap-node.sh`. Do not
manually export an NVM Node directory into `PATH`, call `nvm use` as a
substitute, hardcode the `.nvmrc` version, search for a Node binary, or silently
select/install another Node version.

Use workspace-relative paths for normal repository navigation, for example:

```bash
cd moda-interact-shared
```

Return to the verified root with:

```bash
cd "$MODA_WORKSPACE_ROOT"
```

The workspace doctor is diagnostic/validation tooling. Run it only for an
observed environment/dependency problem, a relevant toolchain/dependency change,
a task Validation requirement, or an explicit `moda_app` request:

```bash
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --quick
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --production
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --full
```

Read `$MODA_WORKSPACE_ROOT/docs/development-baseline.md` only when the current
task or an observed diagnostic condition makes that baseline relevant.

A baseline warning or expected condition does not become part of the current
task merely because it was observed. A baseline FIX/PRODUCTION GATE must not be
silently dismissed as pre-existing debt.

<!-- MODA-DEVELOPMENT-BASELINE:END -->

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

If the task is no longer Ready, has already been claimed, or its dependencies are not Complete, do not execute it.

## Claim the Task

Claim the task according to the workspace execution protocol.

Update together:

* `status: in_progress`
* `executor: codex` or `executor: claude`
* `claimed_at: <current timestamp>`
* increment `attempt`
* update `updated`
* set Completion Report status to `In Progress`

Do not reset or overwrite another executor's active claim.

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

* set Completion Report status to `Ready for Review`;
* change task `status` from `in_progress` to `review`;
* update `updated`;
* leave `executor` and execution history intact.

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

