# Moda Interact Git / VCS Ownership Policy

## Decision

The developer/user owns Git commit and push operations for Moda Interact.

This is a workspace-wide execution rule.

Unless the developer explicitly grants one-off permission for a specific task,
logical repository agents must **not** run:

```text
git commit
git push
```

This applies to:

```text
moda_app
moda_admin
moda_background
moda_database
moda_gateway
moda_messaging
moda_shared
moda_site
moda_system_test
```

`moda_architect` also must not commit or push repository implementation changes
on the developer's behalf.

## Required task lifecycle

Repository implementation tasks use:

```text
Ready
  -> repository agent claims task
  -> In Progress
  -> inspect
  -> implement
  -> validate
  -> Completion Report
  -> Review
  -> STOP
  -> moda_architect reviews actual changes
  -> architect accepts/rejects
  -> developer chooses commit boundary/message
  -> developer commits
  -> developer pushes
```

The repository agent's responsibility ends at `review`.

Architect acceptance does not itself create a Git commit.


## Repository-agent task authority hard stop

This section is a workspace-wide execution gate and is mandatory for every
repository agent listed above. It is intentionally redundant with individual
agent instructions because task-status ownership must never be inferred.

### One invocation, one architecture task

A repository-agent invocation may claim and execute **at most one** architecture
task. Once that task is returned to `review` or `blocked`, the invocation is
over except for the final user-facing summary.

The agent must **not**, in the same invocation:

- discover another task for execution;
- claim another Ready task;
- continue into a task named by the current task's `enables` list;
- begin a downstream task because its dependency now appears satisfied;
- change any downstream task from `pending`/`blocked` to `ready`;
- update another task's execution state;
- update a domain `_index.md` or architecture execution table to promote work.

`enables` is descriptive dependency metadata only. It means **moda_architect may
recalculate readiness after review**; it is never permission for the repository
agent to promote or execute the enabled task.

Todo/progress systems are also non-authoritative. Completing the last local todo
item does not change task ownership and does not authorize another task.

### Status transitions owned by repository agents

For the single task the agent has successfully claimed, the only architecture
status transitions it may perform are:

```text
ready -> in_progress
in_progress -> review
in_progress -> blocked
```

No other architecture-task status transition is permitted. In particular, a
repository agent must never perform:

```text
review -> complete
pending -> ready
blocked -> ready
applicable state -> superseded
```

and must never perform a status transition on a different task.

Those transitions belong to `moda_architect`.

### Architect-owned text is write-protected

A repository agent must not create, replace, or edit the substantive
`## Architect Review` decision for its current task. It must not write phrases
such as:

```text
Accepted by moda_architect
Architect accepted
Architect-approved
status: complete
```

as though architect review has occurred.

The repository agent owns the Completion Report. The architect owns the
Architect Review and acceptance/rejection decision. Existing Architect Review
text from an earlier attempt must be preserved unless the task explicitly
authorizes an architect-owned correction overlay.

### Mandatory end-of-task sequence

When implementation and repository-owned validation are finished, the agent
must perform exactly this sequence:

```text
1. finish the Completion Report
2. set Completion Report status to Ready for Review
3. set only the current task status to review
4. update the current task's updated timestamp
5. do not modify downstream task/index/architecture readiness
6. do not run task discovery again
7. send the final summary
8. STOP
```

The final summary should say that implementation was completed and the task was
**returned to architect review**. It must not claim the task itself is Complete
or architect-accepted.

Even when the repository agent can prove that a downstream dependency would be
satisfied if the current work is accepted, it must stop. `moda_architect` first
reviews the actual implementation, then owns `review -> complete`, dependency
recalculation, `_index.md`/architecture-plan updates, and any downstream
`pending -> ready` transition.

If a repository agent encounters a task/index that already contains a
self-authored false Complete/Ready/architect-accepted state, it must not use that
state as authority to continue. It must stop and report the coordination drift
to `moda_architect`.


## Final-response authority gate

The repository-agent authority boundary applies to **chat/prose output as well as
durable task files**. A repository agent must never simulate, infer, role-play or
announce an architect decision for its own current task. Passing tests, satisfying
Acceptance Criteria, completing local todos or believing the implementation is
correct does not grant architect authority.

For the current task, the repository agent MUST NOT use wording such as:

```text
Architect review decision: accepted
Architect review: accepted
Architect accepted this task
architect-accepted
approved by moda_architect
this task is Complete
```

unless that wording is a verbatim quotation of a **pre-existing architect decision
about a different dependency** and the context makes that distinction explicit.

The repository agent must not perform an "architect review" step in its plan or
final response. The correct step is **return for architect review**. Self-review is
allowed only when described as repository validation/self-check and must never be
labelled architect review.

Before sending its final response, the agent MUST perform a final authority check:

```text
current task status == review or blocked
no current-task architect acceptance/approval claim
no downstream promotion claim
no claim that the current task is Complete
```

For a successfully implemented task returned to review, the final response MUST end
with this exact sentence:

```text
Task status: review. Awaiting moda_architect review; no architect acceptance decision has been made by this agent.
```

This final-response rule is mandatory even when the agent has already written a
valid Completion Report and even when the durable task state remains correctly set
to `review`. A prose-only self-acceptance is still a workflow violation.

## Permitted Git usage

Agents may use read-only or inspection-oriented Git commands when needed, for
example:

```text
git status
git diff
git diff --check
git log
git show
git branch --show-current
git submodule status
git remote -v
git fetch
```

Agents may also perform repository-owned working-tree changes required by the
task, including checking out an architect-approved submodule commit and leaving
the resulting gitlink change for developer commit.

## Prohibited automatic publication

Without explicit one-off developer authorization, agents must not:

```text
git commit
git push
git push --force
git push --force-with-lease
git tag
git push --tags
```

Agents must not create a commit merely because:

- a task acceptance criterion says "committed/pushed";
- a Completion Report requests a commit hash;
- a dependency needs a published commit;
- a submodule pointer changed;
- a build/release step would be easier after committing.

If a task requires publication before a downstream task can execute:

```text
repository agent -> review -> architect acceptance -> STOP
developer -> commit/push
architect -> verify publication -> promote downstream task
```

## Stale task wording

Any task criterion that requires the repository agent itself to commit or push
is coordination drift.

The agent must not satisfy such wording by committing.

Instead:

1. complete implementation and validation;
2. leave the changes ready for developer commit/push;
3. record the stale criterion in the Completion Report;
4. return the task to `review`;
5. allow `moda_architect` to reconcile the task wording.

Stale VCS wording is not, by itself, a reason to mark an otherwise-complete
implementation task Blocked.

## Completion Report

Use factual wording such as:

```text
### Git / VCS

Implementation ready for developer commit/push.
Repository agent did not commit or push.
```

If a submodule pointer changed:

```text
Nested submodule updated in the working tree to architect-approved commit
<hash>. Parent repository gitlink change is ready for developer commit/push.
```

## Architect review

`moda_architect` reviews the actual uncommitted implementation.

When accepted:

```text
task: review -> complete
```

The architect then gives the developer an appropriate commit message when
requested.

The developer remains responsible for:

```text
git add
git commit
git push
```

## Explicit exception

The developer may explicitly authorize an agent to commit or push for one
specific task.

That exception must be clear and task-specific. It does not change this
workspace-wide default for later tasks.
