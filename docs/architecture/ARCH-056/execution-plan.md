# ARCH-056 execution and delivery plan

## What is ready

This package defines six canonical tasks. None has been claimed, implemented, accepted or materialised in the developer's real Git workspace by this architecture session. Four have snapshot-derived `ready` status; the two consumers are `pending`. The normal launcher must recheck the current task states, source changes and architecture-ID allocation.

| Phase | Task | Required direct predecessors | Start condition |
|---|---|---|---|
| 1 | ARCH-056-API-001 | ARCH-055-DATABASE-001; ARCH-055-API-005 | Both existing tasks Complete; inspect actual accepted Database history |
| 1 | ARCH-056-BACKGROUND-001 | ARCH-054-BACKGROUND-001 | Existing task Complete |
| 1 | ARCH-056-BACKGROUND-002 | ARCH-028-BACKGROUND-004; ARCH-028-BACKGROUND-009 | Both existing tasks Complete |
| 1 | ARCH-056-BACKGROUND-003 | ARCH-040-BACKGROUND-008; ARCH-046-BACKGROUND-004; ARCH-052-BACKGROUND-018 | All existing tasks Complete |
| 2 | ARCH-056-BACKGROUND-004 | New BACKGROUND-002 and BACKGROUND-003, plus its named existing accepted owners | Both new interfaces accepted and Complete |
| 3 | ARCH-056-SYSTEM-TEST-001 | All five ARCH-056 implementation tasks | All five accepted and Complete, exact executed revisions available |

Phase 1 production touchpoints do not overlap. The shared logical `moda_background` owner may execute its tasks in separate launcher-prepared physical worktrees; each executor works only its claimed task. A read-only dependency is not edit permission. Merge/rebase coordination follows the existing workflow and does not broaden any allowlist.

## Package contents

The patch is additive. It adds the parent architecture, four support files and six task definitions. It does not modify application code, migrations, previous task reviews/statuses or any `_index.md`.

```text
docs/architecture/ARCH-056-background-persistence-and-recovery-progress.md
docs/architecture/ARCH-056/execution-plan.md
docs/architecture/ARCH-056/finding-task-map.md
docs/architecture/ARCH-056/deterministic-execution-map.json
docs/architecture/ARCH-056/source-baseline.json
docs/decisions/api/ARCH-056/API-001-align-accepted-database-dependency.md
docs/decisions/background/ARCH-056/BACKGROUND-001-serialize-inbound-conversation-persistence.md
docs/decisions/background/ARCH-056/BACKGROUND-002-settle-confirmed-initial-outreach-credit.md
docs/decisions/background/ARCH-056/BACKGROUND-003-resume-owned-initial-template-admission.md
docs/decisions/background/ARCH-056/BACKGROUND-004-continue-durable-initial-recovery-progress.md
docs/decisions/system-test/ARCH-056/SYSTEM-TEST-001-validate-background-persistence-and-recovery-progress.md
```

Delivery files use the unique stem `ARCH-056-touchpoint-task-definitions-attempt2-logging`. The ZIP contains exactly the identical `.patch` file; it is an alternative download, not another patch to apply. This is definition revision 2 (delivery attempt 2), superseding the unapplied attempt-1 package with explicit logging requirements and emitted-record tests. Apply only this replacement package. It is not an accepted implementation/review patch. It does not replace `ARCH-028-BACKGROUND-012-attempt3-accepted.patch` or change that task's Complete status.

The consolidated task pack contains the complete human-readable architecture, execution plan, coverage register and all canonical task bodies. The execution-map JSON supplies the exact machine-readable file/contract/dependency map. The validation file records only checks actually performed on this definition delivery.

## Prepare the correct parent definition worktree

Use `docs/task-definition-materialization.md` and the architect/launcher workflow. Resolve the first definition route from the actual canonical workspace:

```bash
python3 scripts/start-agent-task.py ARCH-056-API-001 --route-only
```

Route-only is read-only and does not create a worktree or claim a task. The architect uses the returned topology to create/reuse and synchronize the canonical **parent** `task/ARCH-056-API-001` worktree. Check live ARCH-056 allocation before writing. Do not infer its path from the previous ARCH-028 task directory, reuse that old task branch, or create an implementation worktree merely to publish definitions.

The commands below are run **inside that verified parent worktree**. The exact `cd` path is supplied by the real route result, not asserted by this snapshot-only session. The worktree must be on `task/ARCH-056-API-001`; the index must contain no unrelated staged changes. Stop if ARCH-056 already exists with different content or current lifecycle state. Do not force-apply, reverse-apply, overwrite an existing task review, or reset user changes.

## Apply the patch

Download either the patch or the ZIP and extract the single patch into Downloads. From the verified parent definition worktree:

```bash
pwd
git branch --show-current
git status --short
git apply --check --whitespace=error-all \
  ~/Downloads/ARCH-056-touchpoint-task-definitions-attempt2-logging.patch
git apply --whitespace=error-all \
  ~/Downloads/ARCH-056-touchpoint-task-definitions-attempt2-logging.patch
git diff --check
```

Because these are new files, `git diff --check` alone does not inspect untracked content. The staged check below is also mandatory. Review the added paths and the definition diff before committing.

## Stage, commit and push the definition package

Stage only the eleven new files:

```bash
git add \
  docs/architecture/ARCH-056-background-persistence-and-recovery-progress.md \
  docs/architecture/ARCH-056/execution-plan.md \
  docs/architecture/ARCH-056/finding-task-map.md \
  docs/architecture/ARCH-056/deterministic-execution-map.json \
  docs/architecture/ARCH-056/source-baseline.json \
  docs/decisions/api/ARCH-056/API-001-align-accepted-database-dependency.md \
  docs/decisions/background/ARCH-056/BACKGROUND-001-serialize-inbound-conversation-persistence.md \
  docs/decisions/background/ARCH-056/BACKGROUND-002-settle-confirmed-initial-outreach-credit.md \
  docs/decisions/background/ARCH-056/BACKGROUND-003-resume-owned-initial-template-admission.md \
  docs/decisions/background/ARCH-056/BACKGROUND-004-continue-durable-initial-recovery-progress.md \
  docs/decisions/system-test/ARCH-056/SYSTEM-TEST-001-validate-background-persistence-and-recovery-progress.md
git diff --cached --check
git diff --cached --name-only
git diff --cached --stat
git diff --cached -- \
  docs/architecture/ARCH-056-background-persistence-and-recovery-progress.md \
  docs/architecture/ARCH-056 \
  docs/decisions/api/ARCH-056 \
  docs/decisions/background/ARCH-056 \
  docs/decisions/system-test/ARCH-056
git commit -m "docs(ARCH-056): define touchpoint tasks with logging acceptance"
git push origin task/ARCH-056-API-001
```

Before the commit, the staged name list must be exactly the eleven paths above. These commands publish definitions only. They do not accept an implementation, merge to main, deploy, change another task's lifecycle, or prove the API task's tests pass.

Publishing the bundle on this first canonical parent branch materialises that task's definition. The other five definitions are available in the bundle but are not thereby materialised on their own canonical task branches.

## Materialise and launch each task

Once a definition is visible to the canonical launcher, use the normal command for one eligible task:

```text
/moda-task ARCH-056-API-001
/moda-task ARCH-056-BACKGROUND-001
/moda-task ARCH-056-BACKGROUND-002
/moda-task ARCH-056-BACKGROUND-003
```

These are separate eligible launches, not an instruction for one executor to claim four tasks. When a task file is absent from its canonical parent branch, use the existing portable-definition exception:

```text
/moda-task <TASK_ID> --definition <absolute-path-to-its-canonical-task-file.md>
```

Supply the exact task file from this package, together with the parent architecture and four support files. The materialising architect makes those referenced architecture files available unchanged in that task's parent worktree, using the established definition commit/push flow before the claim. If the shared documents already exist identically, reuse them. If later accepted definitions/task states exist, use the current authoritative task rather than replaying an attempt-0 file over it. Do not assume the launcher copies sibling architecture documents just because `--definition` names one task file.

After BACKGROUND-002 and BACKGROUND-003 are accepted and Complete, the architect makes BACKGROUND-004 Ready through the normal dependency review, then launches:

```text
/moda-task ARCH-056-BACKGROUND-004
```

After all five implementation tasks are Complete and their accepted revisions are available, make the terminal validator Ready and launch:

```text
/moda-task ARCH-056-SYSTEM-TEST-001
```

The launcher performs the actual synchronization, dependency gate, recursive dependency materialisation and claim. Executors use its startup packet and do not rerun preparation. After implementation, they report and return to `moda_architect` in review status. They never self-accept or begin an enabled task.

## Boundaries retained during execution

ARCH-028-BACKGROUND-013 stays Blocked; no charge is inferred from a pre-HTTP permit or unknown outcome. API-001 does not absorb unfinished ARCH-055 endpoint/readiness work. Woo's new-send production gate remains closed. Existing sequence-two behavior and accepted checkout options-object/update rescheduling remain owned by their completed tasks.

The new suite is terminal proof for this selected package. It neither replaces all earlier architecture suites nor closes deferred findings in the wider review. Runtime/test outputs must identify exact source/image/schema revisions, actual migrated data-plane use, executed/blocked cases and cleanup. This definition package has no application-test or deployed-capacity result to carry forward.

## Logging handoff before production

Acceptance requires the revision-2 emitted-record assertions and the terminal run's `arch056-logging.json`, including original safe message, truthful stage, available correlation IDs and both component messages for selected paired failures. Record the installed Shared version and capture method. A passing source probe or mock logger assertion cannot replace this evidence.

Actual worker stdout/stderr proves application emission. Where production debugging depends on a configured collector, release readiness additionally requires a harmless known failure fixture in the approved preproduction environment to be searchable in that collector by its event and correlation identity, with the expected safe message intact. Record the environment, image revision, event/query evidence and any missing or truncated diagnostic. This is a deployment-specific verification handoff, not a new harness, scenario, transport implementation or authorisation to deploy. This snapshot review has not tested collector delivery or searchability.
