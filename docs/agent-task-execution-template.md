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


## Git / VCS Ownership

Read and obey:

```text
docs/agent-vcs-ownership-policy.md
```

The developer/user owns commit and push.

Unless explicitly authorised by the developer for this specific task, the
repository agent must not run:

```text
git commit
git push
```

Repository-agent lifecycle:

```text
implement -> validate -> review -> STOP
```

Developer lifecycle after architect review:

```text
git add -> git commit -> git push
```

A task criterion requiring agent-side commit/push is coordination drift, not
permission to publish and not a blocker. Leave the implementation ready for the
developer and record the drift in the Completion Report.

The Completion Report should normally contain:

```text
### Git / VCS

Implementation ready for developer commit/push.
Repository agent did not commit or push.
```

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
