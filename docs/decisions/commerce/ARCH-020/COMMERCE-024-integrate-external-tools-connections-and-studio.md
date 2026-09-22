---
id: ARCH-020-COMMERCE-024
architecture_id: ARCH-020
title: Wire accepted external API components into production factories
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 170
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-020-COMMERCE-020
  - ARCH-020-COMMERCE-021
  - ARCH-020-COMMERCE-022
  - ARCH-020-COMMERCE-023
  - ARCH-020-COMMERCE-025
  - ARCH-020-COMMERCE-013
  - ARCH-020-COMMERCE-018
  - ARCH-020-COMMERCE-019
  - ARCH-020-COMMERCE-026
  - ARCH-020-COMMERCE-027
  - ARCH-020-COMMERCE-028
  - ARCH-020-COMMERCE-030
  - ARCH-020-COMMERCE-031
  - ARCH-020-COMMERCE-032
  - ARCH-020-COMMERCE-036
  - ARCH-020-COMMERCE-038
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-SYSTEM-TEST-002
created: 2026-09-21
updated: 2026-09-22
---

# Wire accepted external API components into production factories

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Composition only: src/commerce/integration/external/**, minimal accepted backend/Studio/preview factory wiring, approved Server Action bindings and panel insertion. All connection, credential, HTTP, validation/receipt, preview and availability behavior must already exist in accepted producers.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Composition only: src/commerce/integration/external/**, minimal accepted backend/Studio/preview factory wiring, approved Server Action bindings and panel insertion. All connection, credential, HTTP, validation/receipt, preview and availability behavior must already exist in accepted producers.

## Out of Scope

Writes, OAuth, unsandboxed code, customer-specific lookups, live credentials or
WhatsApp sends, pricing/merchant feature overrides, automatic API discovery,
external-result caching and other owners' implementation files. No live deployment.

## Requirements

Use C21 named interfaces and bounded examples. All dependencies must be accepted
Complete before claim. Readiness is not execution. Component tasks may prove their
ports with fixtures; only024 and SYSTEM-TEST-002 claim real assembled flow.
Protect every UI command against double clicks, preserve same-operation retries,
and never expose secrets or raw external response data in errors/logs.

## Work Items

- [x] Wire020 lifecycle +028 credentials +021 transport +025/026 processors +030 publication +032 availability into the accepted external integration and backend executor/registry factories without recreating business logic.
- [x] Bind the accepted backend execution and publication ports while preserving method/result/operation identity and tenant/pin/validation/cancel boundaries.
- [x] Demonstrate the assembled XN01–XN03 path with controlled external HTTP and verify the external executor has no cache layer.
- [x] Record the concrete 031 production-composition gap; preview is not represented as an unavailable success path.

## Interfaces / Contracts

C21 sections1–8 retain data/behavior requirements. [Section9](../../../architecture/ARCH-020-external-api-tools.md#9-tightened-implementation-boundaries-and-evidence) is authoritative for the narrowed ownership, factory signatures, scenario IDs and handoff rules. Consume accepted exports; no consumer may repair a missing producer by weakening the contract. Record actual dependency commits and published package versions.

## Dependencies

- ARCH-020-COMMERCE-020
- ARCH-020-COMMERCE-021
- ARCH-020-COMMERCE-022
- ARCH-020-COMMERCE-023
- ARCH-020-COMMERCE-025
- ARCH-020-COMMERCE-013
- ARCH-020-COMMERCE-018
- ARCH-020-COMMERCE-019
- ARCH-020-COMMERCE-026
- ARCH-020-COMMERCE-027
- ARCH-020-COMMERCE-028
- ARCH-020-COMMERCE-030
- ARCH-020-COMMERCE-031
- ARCH-020-COMMERCE-032
- ARCH-020-COMMERCE-036
- ARCH-020-COMMERCE-038

## Enables
- ARCH-020-COMMERCE-012
- ARCH-020-SYSTEM-TEST-002


## Acceptance Criteria

- [ ] WI01: new connection/credential->external tool->visual/code sample->publish->release->merchant->real MCP call succeeds through configured no-argument production factories.
- [ ] WI02: actual composition preserves tenant/pin/validation/cancel boundaries and preview has zero provider/decrypt calls; field mapping tests invoke actual producers.
- [ ] WI03: report identifies each producer export and accepted SHA plus test evidence;024 introduces no new business algorithm or duplicated engine.

## Validation

Provide `test:arch020-external-wiring` and scenario IDs from C21 section9. Start with the named positive path through the actual owned implementation. Add the specified rejection/race cases. Each report maps criterion -> test file/test name -> command -> observable result, not just a suite count. No claimed success based only on safe rejection or missing-config tests. Preserve each review reproduction as a committed regression alongside adjacent allowed/denied cases.

Use focused checks while implementing, then existing typecheck/build/lint where defined. Record unrun developer-owned PostgreSQL/container checks accurately; executable scenarios must still exist. No repeated unrelated full suites or screenshot quotas. No live credentials/WhatsApp delivery.

## Stop Condition

Submit implementation and parent report through normal mirrored task branches,
then stop at Review for moda_architect. Never self-accept, launch downstream tasks,
merge main, publish service deployments or update workspace service gitlinks.
Shared's package publication is required only for SHARED-002 as explicitly scoped.
SYSTEM-TEST-002 requires explicit developer invocation even when Ready.

## Implementation Notes

Use /moda-task launcher-resolved dedicated worktrees and preparation packet.
Task authoring on main is the user's documentation exception, not permission for
implementation on main. Preserve unrelated work and existing task claims.

## Completion Report

### Status

Implementation complete; submitted for Architect Review.

### Files Changed

Implementation branch `task/ARCH-020-COMMERCE-024`, commit
`1814f82c5828de50f1ae9f040da623f4ceba0ca7`:

- `src/commerce/integration/external/index.ts`
- `lib/preview/runtime.ts`
- `app/api/studio/preview/tool-tests/route.ts`
- `tests/external-wiring.test.ts`
- `package.json`

The Attempt-1 producer-owned connection changes were reverted from the task branch.
After submission, accepted COMMERCE-036 was merged into canonical Commerce main and
both COMMERCE-024 worktrees were synchronized; the accepted
`CompatibleRevisionInputSchema` producer implementation is now present and must not
be edited by the next COMMERCE-024 attempt.

### Work Completed

Composed the accepted credential command kernel, saved-tool loader, COMMERCE-038
external fixture runner, COMMERCE-031 external preview service, external HTTP
executor, publication validation and availability resolver.

Preview runtime injection preserves one `PreviewService` state-store identity for
ordinary and external tool-test requests. The tool-test POST route dispatches only a
validated request containing `externalResponseFixture` to the external preview
service; ordinary requests retain the accepted preview path.

Acceptance mapping submitted by Attempt 2:

- WI02: `tests/external-wiring.test.ts`, `XN01-XN03` and `XN04` exercise assembled
  credential isolation, provider transport boundaries, publication receipt storage,
  visual/JavaScript fixture processing, preview state identity and provider-free
  synthetic execution.
- WI03: composition consumes accepted producer exports and introduces no duplicate
  connection, credential, HTTP, publication, response-processing, preview,
  availability or fixture-runner algorithm.
- WI01: not claimed; the full connection -> tool -> publish -> release -> merchant ->
  MCP production path was not executed.

### Validation Results

Submitted Attempt-2 evidence:

```text
npm run test:arch020-external-wiring
  PASS — 2/2

npm run test:arch020-external-preview
  PASS — 18/18

npm run test:arch020-external-publication
  PASS — 11/11

npm run test:arch020-external-http
  PASS — 13/13

npm run test:arch020-external-credentials
  PASS — 9/9

npm run test:arch020-external-availability
  PASS — 4/4

targeted ESLint
  PASS

git diff --check
  PASS

build
  webpack compilation and packaged code-runtime smoke completed;
  final exit remains on 12 documented pre-existing TypeScript diagnostics

npm run typecheck
  non-zero on the same documented repository baseline;
  no submitted Attempt-2-owned file was reported in the remaining diagnostics
```

No live third-party credentials, Shopify calls, WhatsApp delivery, paid model calls
or deployment validation were used.

### Deviations

Attempt 2 followed the post-unblock composition direction after COMMERCE-019 and
COMMERCE-038 became available. It uses a composition-local accepted connection
command kernel because the accepted lifecycle does not expose its private kernel.

The submitted XN04 test does not actually traverse the production preview runtime; it
constructs an `InMemoryPreviewStateStore` PreviewService directly. WI01 is also not
implemented. Those points are resolved by the following Architect Review rather than
being treated as accepted deviations.

### Assumptions

C21 read-only scope. Visual rules and generic JavaScript remain inside their accepted
processors/runtime. Controlled provider transport and synthetic credentials are test
fixtures only.

Accepted producer source was synchronized before review. Developer verification after
the Attempt-2 submission confirms:

```text
COMMERCE-019 accepted preview adapters/runtime: present
COMMERCE-036 CompatibleRevisionInputSchema: present in Commerce main
COMMERCE-038 createExternalFixtureRunner: present
```

### Unresolved Issues

See **Architect Review — Attempt 2 — 2026-09-22** below.

### Architectural Concerns

The previous statement that COMMERCE-031 lacked the required reusable producer seam
is superseded. COMMERCE-038 is accepted and integrated. The remaining issues are
COMMERCE-024-owned composition/validation/evidence defects described by the current
Architect Review.

### Git / VCS

Implementation commit:

```text
1814f82c5828de50f1ae9f040da623f4ceba0ca7
```

Original Attempt-2 parent report commit supplied at handoff:

```text
34a8a8e5
```

The parent/docs branch was subsequently synchronized with workspace main and supplied
for this review at:

```text
230b567f099ef0a1d70daf9384148f2fce98514b
```

Both implementation and parent worktrees were reported clean after synchronization.

## Architect Review

### Review Status

Pending.

### Review Notes

Definition only; no implementation acceptance.

### Reviewed Files

Not applicable.

### Validation Reviewed

Not applicable.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile readiness/indexes after prerequisite acceptance; no automatic launch.

## Architect Review — Attempt 1 — 2026-09-22

### Review Status

Blocked

### Review Notes

Reviewed the exact Attempt-1 submission identified by the Completion Report as
implementation `900df37` and parent report `07c9e30c` against C21 sections 7, 8,
9.5 and 9.6.

The current submission is not accepted. It is blocked on an accepted-source
integration prerequisite and one newly identified producer seam.

The following Attempt-1 work is useful and must be preserved in substance after the
blockers are resolved:

```text
src/commerce/integration/external/** composition direction
backend EXTERNAL_HTTP executor/registry wiring
controlled DNS/transport injection for assembled tests
PER_SHOP credential isolation evidence
shop-A positive request using the resolved credential
shop-B CREDENTIAL_MISSING exclusion
test:arch020-external-wiring command
```

Do not discard those pieces merely because the task is blocked.

#### B1 — the implementation baseline does not contain accepted COMMERCE-019 source

The task declares:

```text
ARCH-020-COMMERCE-019 Complete
```

and the accepted COMMERCE-019 implementation is:

```text
implementation: 8850b55
```

The exact architect-accepted COMMERCE-019 snapshot contains:

```text
src/commerce/integration/preview/adapters.ts

lib/preview/runtime.ts:
  imports getCommerceBackend
  imports createPreviewBundleLoader
  imports createPreviewPromptLoader
  imports createPreviewToolExecutor
  imports createPreviewModel
  imports readConfig
  constructs PreviewService with:
    RedisPreviewStateStore
    real saved bundle loader
    authored prompt loader
    fixture tool executor
    optional accepted preview model
```

The submitted COMMERCE-024 implementation snapshot instead contains:

```text
src/commerce/integration/preview/adapters.ts
  ABSENT

lib/preview/runtime.ts
  still constructs:
    PreviewService({
      store: RedisPreviewStateStore(...),
      loader: unavailableLoader,
      environment,
    })
```

Therefore Attempt 1 did not actually compose against the accepted COMMERCE-019
implementation source.

This is not permission for COMMERCE-024 to recreate COMMERCE-019.

Before COMMERCE-024 can return to Ready, the developer must integrate the accepted
COMMERCE-019 implementation (`8850b55`) into `moda-interact-commerce/main` (or the
canonical implementation base used by the launcher), then provide a fresh
synchronized COMMERCE-024 implementation worktree.

The resumed worktree must prove these exact source markers before any 024 edit:

```text
src/commerce/integration/preview/adapters.ts exists

lib/preview/runtime.ts:
  does NOT contain unavailableLoader
  imports createPreviewBundleLoader
  imports createPreviewPromptLoader
  imports createPreviewToolExecutor
  imports readConfig
```

If those markers are still absent after launcher synchronization, COMMERCE-024 stays
Blocked. Do not copy the files manually into the task branch as a workaround.

#### B2 — COMMERCE-031 lacks one reusable producer seam needed by production conversation preview

C21 section 9.5 correctly defines COMMERCE-031's accepted public service:

```text
createExternalPreviewService(...)
```

Attempt 5 completed that contract.

However, the accepted conversation `PreviewService` also requires:

```ts
PreviewExternalFixtureRunner
```

to execute a frozen synthetic external response during Conversation preview.

COMMERCE-031 currently implements the processing logic inside its tool-test
`runSample(...)` path and exposes an injected `externalFixtureRunner` hook on
`PreviewService`, but it does not export a reusable production fixture runner that
COMMERCE-024 can inject without copying the processor/schema/rendering algorithm.

C21 explicitly says:

```text
024 binds already-complete producers
024 cannot invent processor/receipt/quota/runtime logic
a missing producer is returned to its owner
```

Therefore this review creates:

```text
ARCH-020-COMMERCE-038
Export reusable external preview fixture runner
```

COMMERCE-024 now depends on COMMERCE-038.

Do not make COMMERCE-024 copy the current `runSample(...)` visual/JavaScript
processing branch into `integration/external/**`.

### Scope correction for the resumed COMMERCE-024 attempt

The current submission also edits producer-owned files:

```text
src/commerce/connections/command-kernel.ts
src/commerce/connections/lifecycle/index.ts
```

Those edits are outside COMMERCE-024 composition ownership.

Comparison with the accepted COMMERCE-036 producer source shows COMMERCE-024 changed
Prisma typing/generic execution and removed the accepted
`CompatibleRevisionInputSchema` composition from create/revision request parsing.

On the resumed attempt:

```text
DO NOT carry COMMERCE-024-owned edits in:
  src/commerce/connections/command-kernel.ts
  src/commerce/connections/lifecycle/index.ts
```

Restore/consume the architect-accepted producer versions from the synchronized
implementation base.

If final composition still exposes a real command-kernel/lifecycle producer defect,
return the concrete reproduction to `moda_architect`; do not repair that producer
inside COMMERCE-024.

The following one publication binding is explicitly authorized inside the resumed
024 scope because WI01 requires 030 to gate actual publication:

```text
src/commerce/publication/lifecycle.ts
```

The permitted diff in that file is ONLY:

```text
add an injected external publication validation port
for EXTERNAL_HTTP publish:
  call validateForPublication(...)
  fail closed on invalid/unavailable
continue to existing executor-registry availability check
```

No receipt logic, schema validation, processor implementation or other publication
algorithm may be added there.

### Post-unblock Attempt-2 composition contract

After BOTH conditions are true:

```text
COMMERCE-038 status == complete
accepted COMMERCE-019 implementation is present in the launcher implementation base
```

`moda_architect` may return COMMERCE-024 from Blocked to Ready. Preserve
`attempt: 1`; the next launcher claim creates Attempt 2 exactly once.

Attempt 2 is composition-only.

Permitted implementation files are:

```text
src/commerce/integration/external/**
src/commerce/integration/backend.ts
src/commerce/integration/backend/executors.ts
lib/preview/runtime.ts
app/api/studio/preview/tool-tests/route.ts
src/commerce/publication/lifecycle.ts   # only the exact binding above
package.json                            # focused command only
tests/external-wiring.test.ts
```

Do not modify 020/021/025/026/028/030/031/032 producer implementation files.

#### 1. Build the external integration from accepted producers

`createExternalIntegration(...)` must compose:

```text
COMMERCE-020 lifecycle
COMMERCE-020 command kernel
COMMERCE-028 credentials
COMMERCE-021 HTTP execution
COMMERCE-025 visual processor
COMMERCE-026 code processor
COMMERCE-030 publication validator/receipt store
COMMERCE-032 availability resolver
COMMERCE-038 external fixture runner
```

Do not obtain the credential command kernel by adding a new property to the accepted
lifecycle object.

Instantiate the accepted `createConnectionCommandKernel(...)` as its own composition
dependency with the same:

```text
Prisma client
command HMAC key
clock
```

and pass that kernel to the accepted credential service.

The lifecycle service and credential service may use separate kernel instances
because the durable command/audit ledger and HMAC contract are shared; do not add
process-local coordination.

Any Prisma type adaptation required by the accepted producer API must occur inside
`integration/external/**`, not by editing producer source.

#### 2. Expose one production external-preview composition seam

Extend the external integration object with exact composition ports equivalent to:

```ts
savedTools: PreviewSavedToolLoader;
externalFixtureRunner: PreviewExternalFixtureRunner;
createPreview(
  previewService: Pick<
    PreviewService,
    'runToolTest' | 'runExternalToolTest' | 'getToolTest' | 'cancelToolTest'
  >
): ExternalPreviewService;
```

Equivalent naming is allowed, but the behaviors must be identical.

`savedTools` must load the exact persisted tool revision through the accepted
server-owned revision source, parse it with `CommerceToolDefinitionSchema`, and
return no browser/caller definition authority.

`externalFixtureRunner` must be the exact COMMERCE-038 exported runner. Do not wrap it
with alternate visual/code processing.

`createPreview(...)` must create COMMERCE-031's accepted
`createExternalPreviewService(...)` using the SAME accepted:

```text
publication validator
visual processor
code processor
staff liveness port
Redis transport
savedTools loader
clock/environment
```

used by the external integration.

`ExternalIntegrationRedis` may be extended from `get/set` to also expose the accepted
Redis `eval(...)` operation required by COMMERCE-031. Do not add another Redis client
or process-local quota.

#### 3. Extend the accepted COMMERCE-019 production PreviewService composition

Start from accepted COMMERCE-019 `lib/preview/runtime.ts`, not the old
`unavailableLoader` version.

The production `PreviewService` must retain:

```text
RedisPreviewStateStore
createPreviewBundleLoader(backend)
createPreviewPromptLoader()
createPreviewToolExecutor(backend, environment)
accepted preview model when enabled
```

and add only:

```text
savedTools: backend.external?.savedTools
externalFixtureRunner: backend.external?.externalFixtureRunner
```

or equivalent accepted external-integration accessors.

When the external integration is unavailable because required external secret
configuration is absent, existing Shopify/FIXTURE preview must remain operational;
external fixture execution must fail bounded/unavailable rather than replacing the
base preview service.

#### 4. Route external U14 tool tests through COMMERCE-031

The existing POST:

```text
/api/studio/preview/tool-tests
```

must continue to use the normal COMMERCE-019 PreviewService for non-external fixture
requests.

When the validated `ToolTestBody` contains:

```text
externalResponseFixture
```

route that request to the production COMMERCE-031 ExternalPreviewService built from
the SAME production PreviewService instance.

Do not create a second preview state store.

GET/cancel for tool-test run IDs must continue to observe the same
`RedisPreviewStateStore` identity regardless of whether the run was ordinary or
external.

#### 5. Bind publication without bypass

For a saved EXTERNAL_HTTP draft publication:

```text
CommerceLifecycle.publishToolRevision
  -> COMMERCE-030 validateForPublication
  -> only on success continue to accepted registry availability
  -> existing lifecycle performs the one publication write/audit
```

The 024 integration must never write a receipt or publication row itself.

#### 6. Real assembled X07 / WI01 evidence

`tests/external-wiring.test.ts` must use actual application services/producers and
controlled provider/model transports only.

At minimum commit these named scenarios.

```text
XN01-XN03 assembles accepted producers and preserves per-shop credentials and provider boundaries
```

Preserve and strengthen the existing case so it proves:

```text
connection/revision through real lifecycle
credential through real credential service
shop A available
shop B CREDENTIAL_MISSING
external HTTP connects only for shop A
resolved secret only reaches controlled transport
zero external-result cache read/write
```

Add:

```text
XN04 runs visual and JavaScript synthetic preview through the production preview composition
```

Prove through the production-composed services:

```text
visual fixture -> COMMERCE-025 -> schema/rendered result
JavaScript fixture -> COMMERCE-026 -> schema/rendered result
COMMERCE-030 sample receipt recorded
same preview Redis identity supports read/cancel/replay
conversation frozen external fixture uses COMMERCE-038 runner
provider HTTP calls == 0
credential resolution/decryption calls == 0 for synthetic preview
```

Add:

```text
WI01 publishes activates and executes an external tool through the real MCP backend
```

Using synthetic/test-only keys and controlled HTTPS transport:

```text
create connection/revision
configure credential
create external tool draft
run sample
publish external tool through COMMERCE-030 gate
bind published tool to capability/release
activate release
inspect availability for merchant
create/consume immutable grant through existing accepted backend path
execute real MCP tool call
assert schema-validated/rendered external result
assert exact pinned toolRevisionId and connectionRevisionId
assert no EXTERNAL_HTTP cache layer
```

Do not call live third-party endpoints, Shopify, WhatsApp or paid model providers.

If an accepted producer cannot support one of these exact compositions after
COMMERCE-038 and accepted COMMERCE-019 are present, stop and return that concrete
producer gap to `moda_architect`; do not add a local fallback.

### Validation after unblock

Run:

```bash
npm run test:arch020-external-wiring
npm run test:arch020-external-preview
npm run test:arch020-external-publication
npm run test:arch020-external-http
npm run test:arch020-external-credentials
npm run test:arch020-external-availability

npx eslint \
  src/commerce/integration/external \
  src/commerce/integration/backend.ts \
  src/commerce/integration/backend/executors.ts \
  lib/preview/runtime.ts \
  app/api/studio/preview/tool-tests/route.ts \
  tests/external-wiring.test.ts

npm run typecheck
npm run build
git diff --check
```

Repository-wide baseline failures remain non-blocking only when unchanged and no
diagnostic points at Attempt-2-owned files.

### Reviewed Files

- `moda-interact-commerce/src/commerce/integration/external/index.ts`
- `moda-interact-commerce/src/commerce/integration/backend.ts`
- `moda-interact-commerce/src/commerce/integration/backend/executors.ts`
- `moda-interact-commerce/tests/external-wiring.test.ts`
- `moda-interact-commerce/lib/preview/runtime.ts`
- `moda-interact-commerce/src/commerce/integration/preview/model-provider.ts`
- `moda-interact-commerce/src/commerce/external-preview/**`
- `moda-interact-commerce/src/commerce/connections/command-kernel.ts`
- `moda-interact-commerce/src/commerce/connections/lifecycle/index.ts`
- `moda-interact-commerce/src/commerce/publication/lifecycle.ts`
- accepted COMMERCE-019 implementation snapshot (`8850b55`)
- C21 sections 7, 8, 9.5 and 9.6

### Validation Reviewed

Submitted Attempt-1 evidence:

```text
test:arch020-external-wiring
  PASS — 1 scenario

external HTTP producer regression
  PASS

credential producer regression
  PASS

availability producer regression
  PASS

lint
  PASS with pre-existing warnings

git diff --check
  PASS

typecheck/build
  non-zero only on two documented baseline diagnostics
```

Those checks are useful but cannot establish WI01/XN04 while the accepted preview
composition source is absent and the synthetic conversation fixture runner has no
reusable producer export.

### Architecture Conformance

Blocked.

COMMERCE-024 correctly refused to hide the preview gap behind an unavailable success
path, but its diagnosis was too broad: COMMERCE-019 already owns and has an accepted
production PreviewService assembly; that accepted source simply is not present in the
submitted implementation base. Separately, COMMERCE-031 genuinely lacks the reusable
external fixture-runner producer seam required for composition.

The task also currently contains out-of-scope edits to accepted connection producer
files. Those must not be carried forward.

### Follow-up

`ARCH-020-COMMERCE-024` remains Blocked at Attempt 1.

Do not reclaim it yet.

Unblock sequence:

```text
1. developer integrates accepted COMMERCE-019 implementation 8850b55
   into the canonical moda-interact-commerce implementation base

2. ARCH-020-COMMERCE-038 executes and is architect-accepted Complete

3. architect verifies both conditions in a fresh synchronized COMMERCE-024 snapshot

4. architect transitions COMMERCE-024:
     blocked -> ready
     attempt remains 1

5. next /moda-task ARCH-020-COMMERCE-024 claim creates Attempt 2 exactly once
```

No downstream task is promoted. COMMERCE-012 and SYSTEM-TEST-002 remain gated.

## Architect Unblock Review — 2026-09-22

### Review Status

Ready

### Verification

The two independent blockers recorded by the Attempt-1 Architect Review are now
satisfied.

#### U1 — accepted COMMERCE-019 source is integrated into canonical Commerce main

Developer verification against canonical `moda-interact-commerce/main` reports:

```text
MAIN=4e01e20ea3f94e6125b8017340d869d5198db6d0

src/commerce/integration/preview/adapters.ts
  PRESENT

lib/preview/runtime.ts:
  unavailableLoader              ABSENT
  createPreviewBundleLoader      PRESENT
  createPreviewPromptLoader      PRESENT
  createPreviewToolExecutor      PRESENT
  readConfig                     PRESENT

git merge-base --is-ancestor 8850b55 HEAD
  PASS
```

Therefore the accepted COMMERCE-019 implementation `8850b55` is now part of the
canonical implementation base from which the launcher may create the next
COMMERCE-024 worktree.

Do not recreate COMMERCE-019 source inside COMMERCE-024.

#### U2 — COMMERCE-038 producer seam is accepted and integrated

`ARCH-020-COMMERCE-038` is architect-accepted Complete at Attempt 1:

```text
implementation: 16972af
parent report:  f107b817
```

Developer verification against canonical Commerce main reports:

```text
src/commerce/external-preview/index.ts:
  createExternalFixtureRunner PRESENT

git merge-base --is-ancestor 16972af HEAD
  PASS
```

Therefore the reusable `PreviewExternalFixtureRunner` producer required by
COMMERCE-024 is present in the canonical implementation base.

### State Transition

The authoritative task is transitioned:

```yaml
status: ready
attempt: 1
executor: null
claimed_at: null
```

The next successful:

```text
/moda-task ARCH-020-COMMERCE-024
```

claim creates Attempt 2 exactly once.

Attempt 2 must implement only the existing **Post-unblock Attempt-2 composition
contract** in the Attempt-1 Architect Review. That contract remains authoritative.

### Start-of-Attempt Guards

Before making any Attempt-2 source edit, the launcher-resolved implementation
worktree must prove:

```bash
test -f src/commerce/integration/preview/adapters.ts

grep -Fq "createPreviewBundleLoader" lib/preview/runtime.ts
grep -Fq "createPreviewPromptLoader" lib/preview/runtime.ts
grep -Fq "createPreviewToolExecutor" lib/preview/runtime.ts
grep -Fq "readConfig" lib/preview/runtime.ts

if grep -Fq "unavailableLoader" lib/preview/runtime.ts; then
  echo "BLOCKED: stale COMMERCE-019 source" >&2
  exit 1
fi

grep -Fq "createExternalFixtureRunner" \
  src/commerce/external-preview/index.ts
```

Also record:

```bash
git merge-base --is-ancestor 8850b55 HEAD
git merge-base --is-ancestor 16972af HEAD
```

If any guard fails, make no COMMERCE-024 source edit and return the task Blocked with
the exact failed guard.

### Scope Reminder

Attempt 2 is composition-only.

In particular, do not carry forward Attempt-1 edits to:

```text
src/commerce/connections/command-kernel.ts
src/commerce/connections/lifecycle/index.ts
```

Consume the synchronized accepted producer versions instead.

The exact narrowly authorized publication binding and all XN01-XN04/WI01 evidence
requirements remain as written in the Attempt-1 Architect Review.

### Local Worktree Hygiene

The developer's verification output also showed one untracked local file:

```text
?? typescript
```

That file is not part of either accepted implementation and does not invalidate the
source-integration verification above. Before launching Attempt 2, the developer
should preserve/move or intentionally remove that untracked local artifact so the
canonical main worktree is clean. Do not commit it merely to satisfy cleanliness.

### Follow-up

COMMERCE-024 is Ready at Attempt 1.

Do not automatically launch the task. The developer may now invoke the launcher; the
launcher must create Attempt 2 exactly once.

COMMERCE-012 and SYSTEM-TEST-002 remain gated until COMMERCE-024 is architect-accepted
Complete.

## Architect Review — Attempt 2 — 2026-09-22

### Review Status

Changes Requested

### Review Notes

Reviewed the synchronized Attempt-2 source at implementation
`1814f82c5828de50f1ae9f040da623f4ceba0ca7` together with the submitted parent
report (`34a8a8e5`, later synchronized to parent HEAD
`230b567f099ef0a1d70daf9384148f2fce98514b`).

The previous producer blockers are resolved:

```text
COMMERCE-019 accepted production preview composition  PRESENT
COMMERCE-036 accepted CompatibleRevisionInputSchema   PRESENT
COMMERCE-038 reusable external fixture runner          PRESENT
```

Do not reopen those producers from COMMERCE-024.

Attempt 2 has useful composition work that must be preserved:

```text
accepted COMMERCE-019 preview runtime is retained
COMMERCE-038 externalFixtureRunner is injected
COMMERCE-031 ExternalPreviewService is composed from the same PreviewService identity
U14 externalResponseFixture POST requests dispatch to the external preview service
ordinary U14 tool tests retain the accepted normal preview path
XN01-XN03 per-shop credential/provider-boundary direction is sound
```

The task is not accepted because four COMMERCE-024-owned requirements remain.

### A2-R1 — fix saved DRAFT definition identity without changing producer contracts

Primary file:

```text
src/commerce/integration/external/index.ts
```

Current code returns:

```ts
definitionHash: revision.contentHash ?? '',
enabled: revision.status === 'PUBLISHED',
```

for COMMERCE-030 definition identity.

That makes the required pre-publication workflow impossible:

```text
saved DRAFT
-> synthetic sample
-> COMMERCE-030 receipt
-> publish
```

A DRAFT normally has:

```text
revision.contentHash == null
revision.status == DRAFT
```

so the current adapter supplies an empty definition hash and marks the tool disabled.

Use the canonical saved definition identity instead.

Import the already-accepted hash function:

```ts
import { toolContentHash } from '../../publication/validation';
```

The exact found identity must be equivalent to:

```ts
const definition = parsed.data;

return {
  kind: 'found' as const,
  value: {
    toolRevisionId,
    definition,
    definitionHash:
      revision.contentHash ?? toolContentHash(definition),
    connectionRevisionId:
      definition.execution.kind === 'EXTERNAL_HTTP'
        ? definition.execution.connectionRevisionId
        : '',
    enabled: revision.tool.enabled,
  },
};
```

Keep:

```text
include: { tool: true }
```

Do not infer tool enablement from publication status.

Semantics:

```text
DRAFT + contentHash null + tool.enabled true
  -> canonical toolContentHash(saved definition)
  -> enabled true
  -> sample/receipt path is allowed

PUBLISHED + stored contentHash
  -> stored contentHash remains authoritative

tool.enabled false
  -> disabled regardless of revision publication state
```

Add focused regression coverage in:

```text
tests/external-wiring.test.ts
```

The test must use a real saved revision fixture with:

```text
status: DRAFT
contentHash: null
tool.enabled: true
```

and prove both visual and JavaScript sample execution can reach COMMERCE-030 receipt
validation.

Then set only:

```text
tool.enabled: false
```

and prove the sample is rejected as disabled.

Do not modify COMMERCE-030 to accommodate the bad adapter value.

### A2-R2 — EXTERNAL_HTTP publication validation must fail closed

Primary file:

```text
src/commerce/publication/lifecycle.ts
```

The narrowly authorized COMMERCE-024 publication binding currently contains:

```ts
if (
  definition.execution.kind === 'EXTERNAL_HTTP' &&
  this.dependencies.externalPublication
) {
  await this.dependencies.externalPublication.validateForPublication(...);
}
```

This is fail-open. An EXTERNAL_HTTP executor can be available while
`externalPublication` is absent, allowing publication to continue without the
COMMERCE-030 gate.

For `EXTERNAL_HTTP`, absence of the validator must fail before registry availability
or publication mutation.

Required behavior is equivalent to:

```ts
if (definition.execution.kind === 'EXTERNAL_HTTP') {
  const validator = this.dependencies.externalPublication;

  if (!validator) {
    throw new LifecycleError(
      'VALIDATOR_UNAVAILABLE',
      'external publication validation is unavailable',
    );
  }

  const validation = await validator.validateForPublication({
    principal,
    toolRevisionId: revision.id,
    definition,
    signal: new AbortController().signal,
  });

  if (!validation.ok) {
    throw new LifecycleError(
      validation.code === 'VALIDATOR_UNAVAILABLE'
        ? 'VALIDATOR_UNAVAILABLE'
        : 'INVALID_DEFINITION',
      validation.issues[0]?.message ?? validation.code,
    );
  }
}
```

Only after successful EXTERNAL_HTTP validation may the existing:

```ts
await this.registry.isAvailable(definition)
```

check and existing one publication mutation continue.

Add focused regression evidence proving:

```text
EXTERNAL_HTTP + registry/executor available + validator absent
  -> VALIDATOR_UNAVAILABLE
  -> draft remains DRAFT
  -> registry publication path is not admitted

validator returns invalid
  -> no publication mutation

validator succeeds
  -> existing registry check occurs
  -> exactly one publication mutation/audit
```

Do not move receipt storage, response processing or any COMMERCE-030 algorithm into
the publication lifecycle.

### A2-R3 — XN04 must traverse the actual production preview composition

The submitted XN04 test is named:

```text
XN04 runs visual and JavaScript synthetic preview through the production preview composition
```

but constructs:

```ts
new PreviewService({
  store: new InMemoryPreviewStateStore(),
  ...
})
```

and passes it directly to:

```ts
integration.createPreview(previewService)
```

That proves the integration factory in isolation, not the production composition
owned by this task.

Primary files:

```text
tests/external-wiring.test.ts
lib/preview/runtime.ts            # test seam only if required
src/commerce/integration/backend.ts  # existing reset/config seam only if required
app/api/studio/preview/tool-tests/route.ts
```

Do not replace the production PreviewService implementation or create a second
preview state store.

Add/replace the XN04 regression with exact title:

```text
XN04 routes saved DRAFT external samples through the production preview runtime
```

The test must traverse the actual exported composition seam:

```text
configured/cached Commerce backend
-> getPreviewService()
-> getExternalPreviewService()
-> POST /api/studio/preview/tool-tests with externalResponseFixture
-> same underlying PreviewService run identity
-> read the same previewRunId through the accepted tool-test read path/service
```

Use the repository's existing test injection/reset mechanisms and controlled local
Redis/test transport as needed. No live third-party provider is allowed.

The external revision used by this scenario must be a real pre-publication fixture:

```text
status: DRAFT
contentHash: null
tool.enabled: true
```

Prove:

```text
visual synthetic sample -> COMPLETED
JavaScript synthetic sample -> COMPLETED
COMMERCE-030 receipt exists for each validated sample
GET/read observes the same terminal previewRunId/result
provider HTTP calls == 0
credential resolution/decryption calls == 0 for synthetic preview
ordinary non-external tool-test routing remains unchanged
```

If a minimal test-only reset/install seam is genuinely missing, add only that seam;
do not add a second production preview factory.

### A2-R4 — implement WI01 through the assembled backend/MCP path

WI01 is an Acceptance Criterion, not an optional deployment check:

```text
new connection/credential
-> external tool
-> visual/code sample
-> publish
-> release
-> merchant
-> real MCP call
succeeds through configured production factories
```

No live deployment or third-party credential is required. Use synthetic credentials
and the controlled HTTPS/provider transport already used by XN01-XN03.

Add exact named regression:

```text
WI01 publishes activates grants and executes an external tool through the assembled MCP backend
```

Primary file:

```text
tests/external-wiring.test.ts
```

Use actual accepted application services/producers rather than calling isolated
helpers.

The scenario must perform, in order:

```text
1. create external connection
2. create immutable connection revision
3. configure PER_SHOP synthetic credential for shop A
4. create external tool
5. create saved DRAFT external tool revision
6. run at least one synthetic sample on that DRAFT
7. prove COMMERCE-030 sample receipt for the exact canonical DRAFT identity
8. publish the DRAFT through CommerceLifecycle.publishToolRevision
9. create/publish the required capability binding
10. create release containing the published external tool revision
11. activate that release for the test environment
12. resolve merchant availability for shop A
13. create/consume the existing immutable merchant/conversation grant path
14. invoke the assembled backend MCP tools/call path for the external tool
15. execute exactly one controlled external HTTPS request
16. assert the schema-validated/rendered CommerceToolResult
```

Require exact immutable pins:

```text
toolRevisionId == the published revision used by the release/grant
connectionRevisionId == the configured immutable connection revision
```

Require:

```text
shop A credential is the credential reaching the controlled transport
another shop cannot borrow that credential
controlled HTTPS transport called exactly once
publication was admitted only after the COMMERCE-030 receipt/validator gate
no EXTERNAL_HTTP result-cache read/write layer is introduced
no Shopify, WhatsApp, paid model or live third-party endpoint is called
```

The scenario may use controlled in-memory/database test adapters already accepted by
the repository, but must invoke the assembled Commerce backend/MCP service rather than
calling the HTTP executor directly as the final assertion.

### A2-R5 — preserve accepted producers and reconcile the durable report

The synchronized implementation base now contains the accepted COMMERCE-036 producer:

```text
src/commerce/connections/lifecycle/index.ts
  CompatibleRevisionInputSchema PRESENT
```

Attempt 3 must contain **no COMMERCE-024-owned diff** in:

```text
src/commerce/connections/command-kernel.ts
src/commerce/connections/lifecycle/index.ts
```

Before implementation, record these guards:

```bash
grep -Fq "const CompatibleRevisionInputSchema" \
  src/commerce/connections/lifecycle/index.ts

grep -Fq "revision: CompatibleRevisionInputSchema" \
  src/commerce/connections/lifecycle/index.ts
```

If either fails in the launcher-resolved Attempt-3 worktree, STOP and return Blocked;
do not repair COMMERCE-036 from COMMERCE-024.

Also preserve the accepted COMMERCE-019/038 guards:

```bash
test -f src/commerce/integration/preview/adapters.ts
! grep -Fq "unavailableLoader" lib/preview/runtime.ts
grep -Fq "createExternalFixtureRunner" \
  src/commerce/external-preview/index.ts
```

At resubmission:

1. remove/supersede the old statement that COMMERCE-031 lacks a producer seam;
   COMMERCE-038 resolved it;
2. check WI01 only after A2-R4 passes;
3. check WI02 only after the real production-composition XN04 evidence passes;
4. check WI03 only if the final task diff remains composition-only;
5. map every claimed criterion to exact test file, exact test title, command and
   observed result;
6. record the final implementation SHA and final parent report SHA;
7. record both synchronized worktrees clean and pushed.

Return exactly:

```yaml
status: review
attempt: 3
executor: null
claimed_at: null
```

Then STOP. Do not launch COMMERCE-012 or SYSTEM-TEST-002.

### Allowed Attempt-3 Source Scope

Expected task-owned files:

```text
src/commerce/integration/external/index.ts
src/commerce/publication/lifecycle.ts
lib/preview/runtime.ts                    # only if a minimal test/reset seam is needed
app/api/studio/preview/tool-tests/route.ts # only if the production route proof exposes a routing defect
tests/external-wiring.test.ts
package.json                              # focused command only if required
```

The final diff must not contain accepted producer rewrites under:

```text
src/commerce/connections/**
src/commerce/external-preview/**
src/commerce/external-publication/**
src/commerce/external-http/**
src/commerce/external-response/**
src/commerce/code-response/**
```

If an exact regression demonstrates a defect in one of those accepted producers,
return the concrete reproduction to `moda_architect` rather than fixing it in 024.

### Required Validation

Run:

```bash
npm run test:arch020-external-wiring
npm run test:arch020-external-preview
npm run test:arch020-external-publication
npm run test:arch020-external-http
npm run test:arch020-external-credentials
npm run test:arch020-external-availability

npx eslint \
  src/commerce/integration/external \
  src/commerce/publication/lifecycle.ts \
  lib/preview/runtime.ts \
  app/api/studio/preview/tool-tests/route.ts \
  tests/external-wiring.test.ts

npm run typecheck
npm run build
git diff --check
```

Repository-wide typecheck/build may remain non-zero only for a materially unchanged
documented baseline, and only if no diagnostic points at an Attempt-3-owned file.

The final focused evidence must include the exact named XN04 and WI01 scenarios above;
an aggregate suite count is not sufficient.

### Reviewed Files

- `moda-interact-commerce/src/commerce/integration/external/index.ts`
- `moda-interact-commerce/src/commerce/publication/lifecycle.ts`
- `moda-interact-commerce/lib/preview/runtime.ts`
- `moda-interact-commerce/app/api/studio/preview/tool-tests/route.ts`
- `moda-interact-commerce/tests/external-wiring.test.ts`
- `moda-interact-commerce/src/commerce/connections/lifecycle/index.ts`
- synchronized Attempt-2 Completion Report
- C21 post-unblock COMMERCE-024 composition contract

### Validation Reviewed

Submitted Attempt-2 evidence:

```text
external wiring:       2 PASS
external preview:     18 PASS
publication:          11 PASS
external HTTP:        13 PASS
credentials:           9 PASS
availability:          4 PASS
targeted ESLint:       PASS
git diff --check:      PASS
typecheck/build:       documented repository baseline remains
```

Those tests establish useful composition progress but do not prove the required WI01
assembled path, and the current XN04 does not traverse the production runtime despite
its title.

### Architecture Conformance

Partial.

The accepted preview/fixture-runner producer blockers are resolved. Remaining defects
are now within COMMERCE-024's final composition ownership: canonical DRAFT definition
identity mapping, fail-closed publication binding, real production-preview composition
evidence and the required end-to-end assembled MCP path.

No downstream task is promoted.

### Follow-up

Return the same task to `ready`, preserve `attempt: 2`, clear the claim.

The next successful:

```text
/moda-task ARCH-020-COMMERCE-024
```

claim creates Attempt 3 exactly once.

Implement only A2-R1 through A2-R5, return to Review and STOP.
