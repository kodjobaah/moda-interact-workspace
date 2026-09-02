<!-- MODA-DEVELOPMENT-BASELINE:START -->
## Workspace environment preflight

Before reading, claiming or modifying a task, establish `MODA_WORKSPACE_ROOT`.
Use an existing valid value if supplied. Otherwise walk upward only through the
current directory's parent chain until a directory contains `.nvmrc`,
`.codex/agents`, `.claude/agents`, and `docs/agent-task-execution-template.md`.
Do not search the wider filesystem or reconstruct a developer-specific absolute
path. If no valid root is found, stop and report the unexpected working
directory.

Use workspace-relative paths for workspace edits. Before the first Node-related
command, use the current environment; if Node is unavailable, source only:

```bash
source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"
```

Do not manually repair NVM/Node PATH state, hardcode `.nvmrc`, search for Node,
or automatically run `workspace-doctor.sh`/read `development-baseline.md`.
Those diagnostics are conditional as defined by the logical agent rules or task
Validation.
<!-- MODA-DEVELOPMENT-BASELINE:END -->

You are acting as logical `<AGENT>` for the Moda Interact workspace.

Architecture: `<ARCH_ID>`
Task: `<TASK_ID>`
Task file: `<TASK_FILE>`

## 1. Load authoritative context

Before implementation:

1. Read the assigned task file in full.
2. Read the parent architecture document.
3. For dependency gating, verify dependency task metadata and `status: complete`.
   Read a dependency body when this task consumes its output, decision or
   contract, or when the task/architecture explicitly requires it.
4. Read relevant `Interfaces / Contracts` sources.
5. Read the logical agent definition for the current runtime and any relevant
   repository-local instructions.

Architecture/task documents are authoritative for scope, cross-repository
design, dependencies, contracts and Acceptance Criteria. The logical agent
rules are authoritative for ownership, repository practice and local
validation. If they conflict in a way that changes architecture or scope, stop
and return the conflict to `moda_architect`.

For observability tasks, also perform the agent-defined framework-first
capability-reuse check before adding custom instrumentation. If the task asks for
a custom metric/span that merely duplicates an equivalent signal already
provided by architecture-approved framework/runtime/OpenTelemetry/shared
instrumentation, do not implement the duplicate. Record the evidence and return
the task to `moda_architect` for narrowing or supersession.

## 2. Verify and claim

Immediately before implementation, re-read the task and verify:

- `status: ready`;
- `assigned_agent: <AGENT>`;
- every `depends_on` task is `complete`;
- no other executor has an active claim.

Discovery is not a claim. If any check fails, do not execute the task.

Claim atomically/coherently by updating:

```yaml
status: in_progress
executor: <current runtime>
claimed_at: <current ISO-8601 timestamp>
attempt: <previous attempt + 1>
updated: <current date>
```

Set Completion Report status to `In Progress`. Never overwrite another active
executor's claim.

## 3. Implement bounded scope

Implement only `<TASK_ID>`. Do not independently expand into another repository
or logical agent's ownership, unrelated refactoring, unauthorised schema or
transaction changes, new/changed cross-service contracts, queue semantics,
security/tenant boundaries or deferred architecture work.

The task file—not this launcher prompt—is the authoritative implementation
scope. Update Work Items as completed; mark Acceptance Criteria only when
satisfied; run task-defined Validation; use canonical shared contracts when the
task consumes them.

A repository agent may update its assigned task metadata, Work Items,
Acceptance Criteria, Validation and Completion Report as the coordination-file
exception. It must not independently modify the parent architecture, another
agent's task/domain state, Architect Review or architecture-wide execution
state unless explicitly authorised by `moda_architect`.

## 4. Architectural concerns / blocking

If implementation reveals a change or conflict involving ownership, shared
contracts, schema/durable-state semantics, transaction boundaries, queues,
idempotency, ordering/concurrency, security/tenant boundaries, another
repository or the agreed architecture, do not silently work around it. Record
it under `Architectural Concerns`.

If correct implementation cannot proceed, set the task `blocked`, document the
reason and return control to `moda_architect`.

## 5. Validate and report

Run all task-required Validation where practical and record commands, results,
failures and warnings. If a required check cannot run, leave it unsatisfied and
explain why. Do not mark Acceptance Criteria complete unless actually met.

Before handoff, complete the existing Completion Report sections:

- Status: `Ready for Review`;
- Files Changed;
- Work Completed;
- Validation Results;
- Deviations (`None` if none);
- Assumptions (`None` if none);
- Unresolved Issues (`None` if none);
- Architectural Concerns (`None` if none).

When required Work Items, Acceptance Criteria and Validation are satisfied:

- set Completion Report status `Ready for Review`;
- change task `status: review`;
- update `updated`;
- preserve executor/claim history.

**STOP RULE:** Do not mark the task `complete`, start an enabled/dependent task,
perform opportunistic cleanup or begin adjacent follow-on work. Only
`moda_architect` may transition `review -> complete` after inspecting and
accepting the actual implementation.

Return control to `moda_architect` with a concise handoff covering task ID,
implementation, changed files, Validation, deviations, unresolved issues and
architectural concerns.
