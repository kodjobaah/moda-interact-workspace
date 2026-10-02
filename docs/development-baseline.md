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

For ordinary tasks, do **not** run the workspace doctor or read this baseline
as a startup ritual. Use the current environment first.

When a Node-related command is needed, check whether Node is already available:

```bash
command -v node >/dev/null 2>&1
```

If Node is missing, recover the workspace Node environment only through:

```bash
source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"
```

Run the doctor only when an actual environment/dependency issue is being
investigated, relevant toolchain/dependency state changed, task validation
requires it, or `moda_architect` requests it.

For production/deployment diagnostics when relevant:

```bash
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --production
```

For deliberate deep dependency/Zod diagnostics when relevant:

```bash
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --full
```

<!-- MODA-WORKSPACE-ROOT-CONTRACT:START -->
## ENV-PATH-001 — Stable workspace support paths

**Disposition:** EXPECTED

Agent tasks are **not required to start with `$PWD` equal to the canonical
workspace root**. They may be invoked from the canonical workspace, a parent
workspace task worktree, an implementation task worktree, or a nested repository
path.

The canonical workspace root is resolved by the Moda task launchers and
`scripts/start-agent-task.py`. `/moda-task`, `/moda_developer_create` and
`/moda_developer_update` share this topology contract. For agent execution the
resolver canonicalizes marker-bearing candidates through Git `--git-common-dir`
identity so a linked parent task worktree is mapped back to the primary workspace
before new paths are derived. Agents/developer workflow commands must not derive
a new task path from `$PWD`, a previous task worktree basename, or a
machine-specific path.

When the launcher skill itself must locate `scripts/start-agent-task.py`, it may
use only:

1. a valid `MODA_WORKSPACE_ROOT` supplied by the runtime/developer;
2. the current directory's ancestor chain; or
3. the current Git repository's absolute `--git-common-dir` ancestor chain.

This supports invocation from dedicated parent/implementation worktrees without
assuming `/Users/...`, `~/project`, `/home/...`, or any fixed checkout parent.
When a parent-chain candidate is itself a linked task worktree, it must be
canonicalized through its Git common directory before acceptance. If those
bounded mechanisms cannot establish the primary workspace, report
`MODA_TASK_ERROR` rather than searching the wider filesystem.

Once resolved, `MODA_WORKSPACE_ROOT` is the stable shell anchor for the lifetime
of the task. The launcher's `workspace_root`, `repository_path`,
`parent_worktree_path`, and `implementation_worktree_path` values are
authoritative; do not recompute them from `$PWD`.

An architecture task may have been defined outside this development environment.
In that case no local task branch/worktree is expected until the portable task
definition is materialised according to
`docs/task-definition-materialization.md`. Workspace-root resolution must not
assume that a conceptual architect-created task already has local Git state.

When diagnostic tooling is actually needed, invoke it through the resolved
workspace root:

```bash
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --quick
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --production
"$MODA_WORKSPACE_ROOT/scripts/workspace-doctor.sh" --full
```

and refer to the baseline as:

```text
$MODA_WORKSPACE_ROOT/docs/development-baseline.md
```

Task source changes must occur only in the launcher-resolved dedicated task
worktrees described by `docs/agent-worktree-isolation-policy.md`. The fact that
an agent started in a shared/default checkout does not authorize mutation of
that checkout.

<!-- MODA-WORKSPACE-ROOT-CONTRACT:END -->

## ENV-NODE-001 — Non-interactive agent shells

**Disposition:** EXPECTED

Codex/Claude shells may not load the user's interactive NVM initialisation.

An initial `node not found` / `npm not found` does not establish that Node is not
installed. The workspace `.nvmrc` is the only selected development Node version
source of truth.

For an ordinary task, first use the current shell:

```bash
command -v node >/dev/null 2>&1
```

If Node is available, continue without bootstrapping. If Node is missing, recover
it once through the workspace-owned bootstrap:

```bash
source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"
```

Node environment recovery is owned exclusively by that bootstrap. Agents must
not manually add `$HOME/.nvm/versions/node/.../bin` to `PATH`, call `nvm use` as
a substitute, infer/hardcode the `.nvmrc` version, search the filesystem for a
Node binary, or silently install/select another Node version.

If the bootstrap reports that the `.nvmrc` version is not installed, report that
precise condition.

Do not hardcode a Node version into agent definitions or active toolchain
documentation.

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

### Revision-specific observation — 2026-09-20

ARCH-019-SHOPIFY-001 baseline `c4fd514` and reviewed implementation `08af00b` contain identical `tests/unit/merchant-route-access-policy.test.ts`. Full typechecking currently stops at seven parser errors at lines 201 and 219–220 of that unchanged file, before a complete semantic diagnostic inventory is available. The historical 48-error count above must not be presented as the current result or as resolved. Focused recovery-reader TypeScript passes with unrelated JavaScript diagnostics disabled; this does not certify the whole repository. Syntax cleanup belongs to separate owning-repository work.

### After access-policy test repair — 2026-09-20

At SHOPIFY-003 `37c62cd`, the task-relevant access-policy syntax repair allows full typechecking to reach 171 existing diagnostics in 27 untouched files. Full lint reports 20 errors and 2 warnings, also only in untouched files. Architect reruns confirmed these totals and byte-identical diagnostic files relative to starting `30c69f8` (37 distinct files across both checks). No changed-file diagnostics remain. Older 48-error and seven-parser-error observations above are historical; neither describes this revision's current full result. Other task branches may still contain the parser blocker until they consume this repair. This is baseline documentation, not a clean-check exemption for future regressions.

<!-- MODA-TYPECHECK-001:END -->

<!-- MODA-ARCH025-TEST-001:START -->
## ARCH025-TEST-001 — ARCH-025 frozen BillingService and full-suite pre-task failures

**Disposition:** WARN

**Repository:**

```text
moda-interact/
```

**Scope:**

```text
ARCH-025 Shopify BillingService maintainability refactor
```

**Reference evidence — 2026-10-01:**

```text
pre-task commit:       b6d1fd6d362f2a6a302a735e0a54abd8ee677782
SHOPIFY-001 commit:    ed1e4ebe00f29e16e4acb1d799784a6b60b23531
frozen test SHA-256:   bb7c0f4d16e2745abe2dcdb3eb32aa4e247a770daf2e1adf7dfb45833810c7e4
frozen suite:          213 total; 18 failed / 195 passed on both commits
full pre-task suite:   997 total; 24 failed / 940 passed / 33 skipped
full submitted suite:  1008 total; 24 failed / 951 passed / 33 skipped
```

The submitted suite has 11 additional passing tests because SHOPIFY-001 adds the
focused billing-period projection suite. Attempt 2 compared sorted failing test
identifiers directly and proved there is no failing identifier present only on
the submitted commit.

### Frozen-suite failing identifiers

The byte-identical `tests/unit/services/billing.service.test.ts` currently has
these 18 known failures on both reference commits:

```text
BillingService subscription projection > schedules the next pre-close reconciliation for a pack-enabled Free cycle
BillingService recovery credit packs > creates a pending pack request for a mapped FREE plan
BillingService recovery credit packs > creates a pending pack request for a mapped PAID_METERED plan
BillingService recovery credit packs > uses Serializable isolation and locks Subscription before single-flight lookup
BillingService recovery credit packs > returns the existing purchase without creating another usage event
BillingService recovery credit packs > blocks a second unresolved purchase for the same provider context
BillingService recovery credit packs > replays an existing purchase without provider availability
BillingService recovery credit packs > fails closed when the durable configuration changes after provider verification
BillingService recovery credit packs > fails closed when live provider evidence changes before the transaction
BillingService recovery credit packs > fails closed when the transaction re-read changes the billing period identity
BillingService recovery credit packs > fails closed when the transaction re-read changes the billing period boundary
BillingService recovery credit packs > ignores legacy singular top-up configuration fields
BillingService recovery credit packs > persists fractional provider-before quantity and derived identity when legacy subscription ID is null
BillingService recovery credit packs > blocks an unresolved purchase from a previous period or provider identity for the same offer
BillingService recovery credit packs > allows independent unresolved purchases for different event handles
BillingService recovery credit packs > ignores client-supplied plan and pricing fields
BillingService recovery credit packs > recovers a concurrent same-id unique conflict by returning the committed purchase
BillingService recovery credit packs > verifies Shopify before opening the Prisma write transaction
```

The observed trigger is date-sensitive fixture data around
`2026-10-01T00:00:00.000Z` combined with the unchanged production default
`now = new Date()`. This baseline records the proven failure set; it does not
change production phase semantics and it does not authorize editing the frozen
ARCH-025 regression asset.

### Additional full-suite failing identifiers

The same six non-frozen failures were also present on both reference commits:

```text
tests/unit/billing-ui.test.ts > canonical merchant billing UI > sends onboarding plan CTAs to Shopify plan selection
tests/unit/merchant-knowledge-read-model.test.ts > limits the catalogue to supported WEB_PAGE pairs and filters source types before the cap
tests/unit/merchant-navigation-history.test.tsx > merchant navigation and history links > renders localized navigation without stale Messages label for ACTIVE
tests/unit/merchant-pricing-renderer.test.jsx > Onboarding merchant pricing renderer > renders structured DTO card content and hides raw usage pricing mechanics
tests/unit/merchant-pricing-renderer.test.jsx > Onboarding merchant pricing renderer > renders a generic unavailable state for an empty catalogue
tests/unit/merchant-pricing-renderer.test.jsx > Onboarding merchant pricing renderer > omits the Free proof item when the active catalogue has no Free plan
```

### ARCH-025 agent rule

For ARCH-025 tasks:

1. keep `tests/unit/services/billing.service.test.ts` byte-identical and verify
   the exact SHA-256 above;
2. run the complete frozen suite;
3. if its failing identifiers are exactly a subset of the 18 identifiers above,
   reference `ARCH025-TEST-001` and continue when the task introduces no other
   regression;
4. if any failing identifier is new, changed or otherwise worse, investigate it
   as a potential task regression before review;
5. if an upstream change resolves a baseline failure, do not reintroduce it;
6. run full `npm test` and do not use this baseline to excuse any task-only
   failure;
7. do not edit the frozen suite, add bypasses, or weaken production behaviour to
   preserve this baseline.

The known baseline never substitutes for a task's focused tests, typecheck,
targeted lint, build, or other explicitly required validation.

### Resolution

When these failures are corrected by their owning work, update this entry rather
than requiring ARCH-025 extraction tasks to recreate the old failure set.
<!-- MODA-ARCH025-TEST-001:END -->

<!-- MODA-ARCH025-BACKGROUND-TEST-001:START -->
## ARCH025-BACKGROUND-TEST-001 — ARCH-025 Background full-suite pre-task failures

**Disposition:** WARN

**Repository:**

```text
moda-interact-background/
```

**Scope:**

```text
ARCH-025 Background maintainability tranches
```

**Reference evidence — 2026-10-02:**

```text
pre-task commit:          670fbad4d52308c96ef41a6a4d29116f1ad42f1a
BACKGROUND-001 commit:    b3c7a1264a22baf498b14916a341686a751de869
package-lock SHA-256:     24b51056b787611cc08f854679c6570ad823c345e03f24101847d7b4829334bc
Node:                     v24.21.0
full pre-task suite:      8 failed / 1,392 passed / 38 skipped + 1 suite-loading failure
full submitted suite:     8 failed / 1,414 passed / 38 skipped + 1 suite-loading failure
```

The submitted tree adds the passing focused classification suite. Attempt 2 ran
the exact pre-task and submitted commits under the same dependency/environment
state and compared failure identities directly. There is no failing test or
suite identity present only on the submitted commit.

### Failing test identifiers present on both reference commits

```text
tests/unit/services/billing-reconciliation.service.test.ts > persists rotating provider-cycle lag and enqueues the existing +60 second job
tests/unit/services/billing-reconciliation.service.test.ts > repairs a missing Paid cycle schedule during rotating provider-cycle lag
tests/unit/services/billing-reconciliation.service.test.ts > repairs a missing pack-enabled Free cycle schedule during rotating provider-cycle lag
tests/unit/services/matured-candidate.materialization.test.ts > creates a recovery from current Shopify data when the lookup is found and recoverable
tests/integration/translation-enum-bindings.integration.test.ts > persists submission failure statuses through the real enum column
tests/integration/translation-enum-bindings.integration.test.ts > persists terminal poll Batch and translation statuses through real enum columns
tests/integration/translation-enum-bindings.integration.test.ts > persists failed provider results through the real translation enum column
tests/integration/translation-enum-bindings.integration.test.ts > persists SUBMISSION_UNKNOWN correlation adoption through the real Batch enum column
```

The four translation-enum integration failures reported the same:

```text
Can't reach database server at localhost:5432
```

on both reference commits. The three billing-reconciliation assertions and the
one matured-candidate assertion also had identical expected/actual differences
on both commits.

### Suite-loading failure present on both reference commits

```text
tests/unit/commerce/evidence.test.ts
ENOENT opening:
/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-BACKGROUND-002/docs/architecture/ARCH-020-evidence-contract-fixtures.json
```

This entry records proven pre-task development state. It does **not** make a
missing PostgreSQL service or missing ARCH-020 fixture desirable, and it does
not waive production/deployment validation. If those environment conditions are
repaired and any baseline failure disappears, later tasks must not recreate it.

### ARCH-025 Background agent rule

For ARCH-025 tasks in `moda-interact-background`:

1. run the task-required focused/frozen/entrypoint validation normally;
2. run full `npm test` when the task requires it;
3. when failures are a subset of the identities above and no new failing test or
   suite identity appears, reference `ARCH025-BACKGROUND-TEST-001` rather than
   rediscovering the pre-task condition;
4. investigate every new, changed or worsened failure as a possible task
   regression before review;
5. if PostgreSQL/fixture availability improves and baseline failures disappear,
   treat that as an improvement and do not preserve the old failure;
6. do not edit tests, add bypasses, weaken production behaviour or deliberately
   break the environment to reproduce this baseline.

This baseline never substitutes for focused tests, frozen-asset hash checks,
entrypoint isolation, build, lint/typecheck or any other explicit task gate.

### Resolution

When the underlying environment/test conditions are repaired, update this entry
to the smaller observed set or mark it resolved.
<!-- MODA-ARCH025-BACKGROUND-TEST-001:END -->

<!-- MODA-ARCH025-ADMIN-BUILDER-TEST-001:START -->
## ARCH025-ADMIN-BUILDER-TEST-001 — Inherited Admin failures during pricing-plan builder extraction

**Disposition:** WARN

**Repository:**

```text
moda-interact-admin/
```

**Scope:**

```text
ARCH-025 ADMIN-001..008 MerchantPricingPlanBuilder structural extraction chain
```

**Reference evidence — 2026-10-02:**

```text
pre-task commit:
  b8da632a1fcaef7e364be1dc5cca40dfafde4703

ADMIN-001 accepted implementation:
  0cd5c010926acfbfaf808fb5d727df9269b30fdb

comparison environment:
  Node v24.21.0
  npm 11.19.0
  database gitlink cfeeb12456b4e05067a96857a8c47837d7e33bbd
  equivalent installed dependency set
```

`npm run test:unit`:

```text
baseline:
  228 passed / 2 failed

submitted:
  242 passed / 2 failed
```

Exact failures on both revisions:

```text
tests/unit/merchant-pricing-translation-workbook.test.ts
  rejects stale metadata, locale/header changes, and highlight identity changes

tests/unit/merchant-pricing-translations.test.ts
  returns all bounded validation issues in canonical order
```

`npm test`:

```text
baseline:
  223 passed / 9 failed / 3 skipped

submitted:
  226 passed / 9 failed / 0 skipped
```

Exact failing identifiers/categories on both revisions:

```text
tests/observability/shared-runtime-ownership.test.mjs
  no Moda-owned span/metric creation exists in application code

tests/security/admin-billing-controls.test.mjs
  accepts strict non-negative lifetime Free defaults

tests/security/admin-billing-pack-status.test.mjs
  every RecoveryCreditPurchaseStatus has an ICU label and filter support

tests/security/admin-billing-pack-status.test.mjs
  purchase-status rendering uses the bounded presenter rather than dynamic ICU lookups

tests/security/admin-internationalization.test.mjs
  Admin validates and consumes the published Shared ICU runtime

tests/security/admin-internationalization.test.mjs
  Admin canonical catalogue keys are independent and intentionally aligned

tests/security/admin-merchant-support.test.mjs
  consumes the published shared release without a local declaration shim

tests/security/admin-security-boundary.test.mjs
  identity, revocation, mutation, session, and route contracts are wired

tests/security/admin-tenant-business-kpis.test.mjs
  Tenant Directory KPIs are derived from durable business state
```

ADMIN-001 adds fourteen passing controller tests. No new or worsened failure was found.

### ARCH-025 builder-chain rule

For ADMIN-002..008:

1. continue to execute the task-required `npm run test:unit` and `npm test`;
2. this baseline may cover only the exact documented failing identifiers with
   equivalent failure reasons;
3. any new failing identifier, changed failure reason, increased failure severity or
   regression in an accepted/frozen builder-chain test remains task-blocking;
4. if an upstream change fixes one of the documented failures, do not recreate it and
   do not treat its absence as baseline drift;
5. frozen pricing-plan pure/domain tests, accepted ADMIN-001 security assertions,
   focused draft/controller tests, task-specific extraction tests, targeted lint,
   production build and `git diff --check` retain their normal required status;
6. this entry never authorizes skipping tests, weakening assertions or modifying
   unrelated Admin code merely to obtain a green suite.

### Resolution

Remove or narrow this baseline as the owning Admin/i18n/billing/security work fixes
the documented failures.
<!-- MODA-ARCH025-ADMIN-BUILDER-TEST-001:END -->
