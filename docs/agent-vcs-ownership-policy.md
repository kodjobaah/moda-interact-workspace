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
