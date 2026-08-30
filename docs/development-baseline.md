# Moda Interact Development Baseline

## Purpose

This file records durable development-environment and dependency facts that
coding agents must not repeatedly rediscover.

It is not a list of problems to ignore. Each condition has a disposition:

```text
EXPECTED
    intentional and valid

FIX
    invalid state that should be corrected by the owning repository/task

WARN
    non-blocking condition that should remain visible

PRODUCTION GATE
    acceptable for local development but forbidden for production validation
```

Before investigating a Node/toolchain/dependency-resolution failure, run:

```bash
source scripts/bootstrap-node.sh
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --quick
```

For production/deployment work:

```bash
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --production
```

For deeper Zod tree output:

```bash
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --full
```

<!-- MODA-WORKSPACE-ROOT-CONTRACT:START -->
## ENV-PATH-001 — Stable workspace support paths

**Disposition:** EXPECTED

IntelliJ is opened using the `moda-interact-workspace` root. At task startup,
before changing directories, agents run:

```bash
source scripts/bootstrap-node.sh
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --quick
```

The bootstrap resolves the workspace once and exports:

```text
MODA_WORKSPACE_ROOT
```

This variable is the stable path anchor for the lifetime of the task shell.

After changing into a service repository, use:

```bash
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --quick
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --production
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --full
```

and refer to the baseline as:

```text
$MODA_WORKSPACE_ROOT/docs/development-baseline.md
```

Agents must not search for those files or repeatedly rediscover the workspace
root after the variable has been established.

If an agent task unexpectedly starts outside the workspace root and the variable
is not already defined, the correct response is to return to the IntelliJ-opened
workspace project root rather than perform broad filesystem searches.

<!-- MODA-WORKSPACE-ROOT-CONTRACT:END -->

## ENV-NODE-001 — Non-interactive agent shells

**Disposition:** EXPECTED

Codex/Claude shells may not load the user's interactive NVM initialisation.

An initial `node not found` / `npm not found` does not establish that Node is not
installed. The workspace `.nvmrc` is the only selected development Node version
source of truth.

Agents must run:

```bash
source scripts/bootstrap-node.sh
```

before searching for Node, installing Node, or reporting the toolchain missing.

Do not hardcode a Node version into agent definitions.

## DEP-ZOD-001 — Shared runtime schemas use the shared package's Zod contract

**Disposition:** FIX if violated

`moda-interact-shared/package.json` is the source of truth for the Zod runtime
range required by `@modainteract/moda-interact-shared`.

Any deployable service that imports the shared package as a runtime dependency
and executes its schemas must directly provide a compatible runtime Zod
dependency.

The workspace installer derives the consumer range from the shared package. It
does not hardcode a concrete Zod patch version.

Do not change shared Zod APIs to older syntax merely because an unrelated
development dependency has installed an older Zod major.

## DEP-ZOD-002 — ERD generator may carry its own older Zod

**Disposition:** EXPECTED when isolated

`prisma-generator-plantuml-erd` is development tooling and may depend on a
different Zod major.

That is acceptable only when the tool's Zod remains isolated inside that tool's
dependency tree and the deployable application's root/runtime Zod satisfies the
shared package contract.

Agents do not need to re-investigate the ERD generator's nested Zod on every
task. Use the doctor result.

## NPM-CONFIG-001 — `shamefully-hoist`

**Disposition:** WARN

If `.npmrc` contains `shamefully-hoist=...`, npm currently reports it as an
unknown project configuration option.

Do not attribute dependency resolution to this setting without evidence. The
workspace doctor reports the condition once so unrelated implementation tasks
do not spend time rediscovering it.

Removal or migration should be handled deliberately if the workspace
standardises exclusively on npm.

## SHARED-DIST-001 — Local shared-package link

**Disposition:** EXPECTED locally / PRODUCTION GATE

Local development may use a sibling link such as:

```text
file:../moda-interact-shared
```

when useful.

Production deployment validation must use the architecture-approved published
npm artifact and must not require a sibling shared repository in the deployment
build context.

Therefore:

```bash
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --quick
```

reports a local link as informational, while:

```bash
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --production
```

treats it as a failure.

The distribution-boundary migration remains owned by the relevant architecture
tasks; the development-baseline installer does not silently rewrite it.

## Agent investigation rule

When the doctor identifies a condition already documented here:

- do not repeat broad filesystem searches or dependency archaeology;
- do not re-derive an already documented explanation unless observed state
  materially differs;
- record the doctor/baseline result in the task Completion Report when relevant;
- continue the assigned task if the condition is EXPECTED/WARN and unrelated;
- do not reclassify a documented FIX or PRODUCTION GATE as harmless baseline
  debt;
- return to `moda_architect` when the condition requires work outside the
  assigned repository/task scope.

The source code, package manifests and current doctor output remain
authoritative if this document becomes stale.

<!-- MODA-TYPECHECK-001:START -->
## TYPECHECK-001 — Existing `moda-interact` repository-wide TypeScript errors

**Disposition:** KNOWN BASELINE DEBT

**Repository:**

```text
moda-interact/
```

**Current observed baseline:**

```text
npm run typecheck
    -> exits non-zero
    -> 48 known pre-existing TypeScript errors
```

These repository-wide errors pre-date the current ARCH-002 implementation work
and were observed during:

```text
ARCH-002-SHOPIFY-001
ARCH-002-SHOPIFY-002
```

### Meaning

`KNOWN BASELINE DEBT` means the condition is known and unresolved, but it does
not automatically block unrelated bounded architecture work. It must never be
used to excuse a regression introduced by the current task.

### Agent rule

Do not re-investigate these 48 repository-wide errors from first principles on
every unrelated task.

If the assigned task does not modify files involved in the baseline errors:

1. run the validation required by the assigned task;
2. ensure files changed by the task introduce no new TypeScript errors;
3. if repository-wide typecheck is run and still matches this baseline, record
   `TYPECHECK-001` briefly in the Completion Report;
4. continue the assigned task when its own Acceptance Criteria are satisfied.

Investigate when:

- the error count increases above the documented baseline;
- a changed file produces a new TypeScript error;
- the error scope materially changes;
- an existing baseline error becomes directly relevant to the task;
- the task explicitly requires a clean repository-wide typecheck; or
- `moda_architect` explicitly requests investigation.

If the observed count decreases, record that the baseline may be stale and
return the documentation update to `moda_architect` when appropriate.

### Preferred reporting

```text
Typecheck:
  repository-wide: non-zero — TYPECHECK-001 known baseline
  current task changed files: 0 new TypeScript errors
```

Do not copy the full compiler output into this baseline document.

The authoritative current error list remains the actual output of:

```bash
cd "$MODA_WORKSPACE_ROOT/moda-interact"
npm run typecheck
```

when that command is genuinely required by the task.

### Resolution

When fully resolved, change the disposition to:

```text
RESOLVED
```

and remove any exemptions that depend on the old baseline count.

<!-- MODA-TYPECHECK-001:END -->
