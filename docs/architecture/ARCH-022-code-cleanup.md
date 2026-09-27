---
id: ARCH-022
title: Code cleanup
status: agreed
coordinator: moda_architect
created: 2026-09-27
updated: 2026-09-27
---

# ARCH-022: Code cleanup

## Status

Agreed — Phase 1 establishes deterministic repository-local Prettier tooling and performs
one bounded formatting sweep per agent-owned Moda project. Later cleanup phases are not
defined by this document and must be discussed before new work is added.

## Problem

Formatting is inconsistent across the Moda Interact repositories. The inspected snapshot
contains three different states:

- `moda-interact-admin` already pins Prettier `3.9.6` and exposes `format` / `format:check`;
- `moda-interact` already depends on Prettier, but declares `^3.6.2`, has no format scripts,
  and its current `.prettierignore` excludes `package.json` while not explicitly excluding
  the nested `database/` submodule;
- the other agent-owned repositories either have no Prettier dependency or, for Gateway
  and Site, no Node package manifest at all.

A single workspace-wide formatting command would also be unsafe because several application
repositories contain the independently owned `database/` Git submodule. Formatting must stay
inside the owning repository and must not create cross-repository changes accidentally.

## Goals

Phase 1 must:

- establish Prettier `3.9.6` as the exact repository-local formatter version;
- provide a deterministic write command and a non-mutating check command in every affected
  repository;
- preserve existing specialised formatters such as `prisma format`;
- add or reconcile `.prettierignore` so generated output, caches, dependency directories,
  lockfiles and nested Git submodules are not part of the formatting sweep;
- format all repository-owned, Prettier-supported source, configuration and documentation
  files that are not intentionally ignored;
- keep each repository's formatting diff independently reviewable;
- prove that formatting introduced no task-owned syntax, type, test or build regression using
  the repository's existing validation surface.

## Non-Goals

Phase 1 does **not**:

- change runtime behaviour;
- fix lint, typecheck, test or build failures that pre-date the formatting task;
- change ESLint rules or introduce ESLint/Prettier coupling;
- introduce import sorting or another formatter/plugin policy;
- standardise quotes, line width or other style settings beyond Prettier `3.9.6` defaults;
- change Prisma schema semantics or replace Prisma's own formatter;
- refactor code while formatting it;
- format generated output, dependency trees, package lockfiles or nested submodules;
- create a shared formatter package or workspace-root formatter dependency;
- assign `moda-interact-documentation` to an invented logical owner. The supplied agent
  definition has no documentation domain/agent route, so that repository remains an explicit
  ownership gap for a later decision rather than being silently assigned to the wrong agent;
- modify the unmaterialised `shopify-webhook-payloads` helper submodule.

## Current Architecture

The inspected Phase-1 baseline is:

| Repository | Current Prettier state | Phase-1 action |
|---|---|---|
| `moda-interact` | dependency present; no scripts | pin/reconcile, scripts, ignore, format |
| `moda-interact-admin` | `3.9.6`; scripts present | ignore audit and format |
| `moda-interact-background` | absent | install, scripts, ignore, format |
| `moda-interact-commerce` | absent | install, scripts, ignore, format |
| `moda-interact-database` | absent; `format` means Prisma | install beside Prisma, ignore, format supported files |
| `moda-interact-gateway` | no `package.json` | create minimal private formatter manifest, format |
| `moda-interact-messaging` | absent | install, scripts, ignore, format |
| `moda-interact-shared` | absent | install, scripts, ignore, format |
| `moda-interact-site` | no `package.json` | create minimal private formatter manifest, format |
| `moda-interact-system-test` | absent | install, scripts, ignore, format |

`moda-interact-documentation` also lacks Prettier, but the current agent/task ownership model
contains no canonical owner or `docs/decisions/documentation/` route. That is recorded as an
open ownership issue, not worked around by assigning another agent's repository.

## Proposed Architecture

### Repository-local formatter ownership

Each repository owns its own Prettier dependency, scripts, ignore file and formatting diff.
There is no Phase-1 shared configuration package and no cross-repository formatting command.

Canonical version:

```text
prettier = 3.9.6 (exact devDependency)
```

Normal Node repositories expose:

```json
"format": "prettier --write .",
"format:check": "prettier --check ."
```

`moda-interact-database` already owns this command:

```json
"format": "prisma format --schema prisma/schema.prisma"
```

That command must remain semantically unchanged. The database task therefore adds:

```json
"format:prettier": "prettier --write .",
"format:check": "prettier --check ."
```

Gateway and Site may add a minimal private `package.json` plus `package-lock.json` solely to
own the local formatter dependency and scripts. No runtime dependency or start/build command
is introduced by that tooling manifest.

### Ignore boundary

Every affected repository must have a `.prettierignore`. It must, at minimum, exclude:

- `node_modules/`;
- generated/build/cache/test-artifact directories already excluded by the repository's
  `.gitignore`;
- `package-lock.json`;
- minified/generated assets where applicable;
- `database/` in `moda-interact`, `moda-interact-admin`, `moda-interact-background` and
  `moda-interact-commerce` because it is an independently owned Git submodule;
- `i18n/translations.js` in `moda-interact-site` because it is generated byte-for-byte by
  `i18n/build-translations.py`; formatting the generated bundle would make its canonical
  `--check` validation fail.

Existing intentional ignore entries are preserved unless the task demonstrates they are
obsolete. Ordinary repository-owned source/config files, including `package.json`, must not
be excluded merely to avoid formatting them.

### Formatting boundary

The one-time write pass may change only formatting of Prettier-supported repository-owned
files plus the formatter tooling files required by the task. Functional edits, opportunistic
cleanup and unrelated warning fixes are prohibited.

After formatting, `format:check` must pass without writing files, and `git diff --check` must
be clean. Repositories with a nested database submodule must also prove that the submodule
has no task-owned worktree change.

## Request / Event Flow

Not applicable. This architecture changes development tooling only and introduces no runtime
request, event or queue flow.

## Repository Responsibilities

Each repository owner performs only its own formatting task. No agent may format another
repository through a nested submodule or workspace traversal.

## Data Model

None.

## Contracts

The only cross-repository convention is the development-tooling contract documented above:
exact Prettier version `3.9.6`, repository-local write/check scripts, explicit ignore
boundaries, and no semantic changes. It is a coordination convention, not a runtime shared
package contract.

## Consistency and Transactions

None.

## Ordering

All Phase-1 tasks are independent and may execute in parallel because they do not consume
one another's implementation output.

## Failure Handling

A repository task must return `blocked` rather than broadening scope when:

- installing Prettier requires an unexpected package-manager migration;
- formatting changes generated or nested-submodule files that cannot be excluded safely;
- the formatter cannot parse a repository-owned file that should be in scope;
- validation reveals a new task-owned regression that cannot be corrected without a semantic
  code change.

Pre-existing baseline failures are recorded using the normal development-baseline protocol;
they are not fixed inside these formatting tasks unless the formatter itself caused them.

## Scalability

Not applicable to runtime scale. The decomposition deliberately avoids one giant cross-repo
diff so review and integration remain bounded.

## Security

Formatter tooling must not read, rewrite or commit ignored secrets, local environment files,
authentication state or generated credentials. Existing secret-related `.gitignore` entries
must remain respected by `.prettierignore` where relevant.

## Observability

No runtime observability changes are introduced.

## Rollout / Migration

Classification: development-tooling / non-runtime rollout.

There is no production migration or deployment ordering. Each repository task can be merged
independently after architect review. The user may integrate repositories in any order.

## Decisions / Tasks

| Task | Owner | Repository | Status | Depends On |
|---|---|---|---|---|
| ARCH-022-SHOPIFY-001 | moda_app | moda-interact | Ready | - |
| ARCH-022-ADMIN-001 | moda_admin | moda-interact-admin | Ready | - |
| ARCH-022-BACKGROUND-001 | moda_background | moda-interact-background | Ready | - |
| ARCH-022-COMMERCE-001 | moda_commerce | moda-interact-commerce | Ready | - |
| ARCH-022-DATABASE-001 | moda_database | moda-interact-database | Ready | - |
| ARCH-022-GATEWAY-001 | moda_gateway | moda-interact-gateway | Ready | - |
| ARCH-022-MESSAGING-001 | moda_messaging | moda-interact-messaging | Ready | - |
| ARCH-022-SHARED-001 | moda_shared | moda-interact-shared | Ready | - |
| ARCH-022-SITE-001 | moda_site | moda-interact-site | Ready | - |
| ARCH-022-SYSTEM-TEST-001 | moda_system_test | moda-interact-system-test | Ready | - |

No additional integrated system-test task is required for Phase 1 because there is no
cross-service runtime behaviour to validate. `ARCH-022-SYSTEM-TEST-001` is repository
maintenance for the system-test project itself and does not gate another implementation task.

## Open Questions

1. Which logical agent/domain should own `moda-interact-documentation` for future repository
   maintenance tasks? Until that is decided, no canonical formatting task is created for it.
2. Should a later Code Cleanup phase introduce a workspace-wide CI check that invokes each
   repository's `format:check`? This is intentionally not part of Phase 1.

## Change History

- 2026-09-27: Created ARCH-022 and defined Phase 1 repository-local Prettier cleanup tasks.
