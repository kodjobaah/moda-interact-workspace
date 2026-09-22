---
id: ARCH-020-COMMERCE-031
architecture_id: ARCH-020
title: Implement external response preview backend
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 150
executor: null
claimed_at: null
attempt: 5
depends_on:
  - ARCH-020-COMMERCE-019
  - ARCH-020-COMMERCE-009
  - ARCH-020-SHARED-002
  - ARCH-020-COMMERCE-025
  - ARCH-020-COMMERCE-026
  - ARCH-020-COMMERCE-030
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-024
created: 2026-09-21
updated: 2026-09-22
---

# Implement external response preview backend

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Own src/commerce/external-preview/** and narrowly specified preview request/store/lifecycle extensions. Implement raw fixture freezing, syntax/sample services and quotas. No UI or production HTTP/credential resolver.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Own src/commerce/external-preview/** and narrowly specified preview request/store/lifecycle extensions. Implement raw fixture freezing, syntax/sample services and quotas. No UI or production HTTP/credential resolver.

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

- [x] Extend accepted ToolTestBodySchema/ConversationBodySchema/stored preview state with C21 optional external fixtures, preserving old request behavior; freeze exact saved revision/definition/runtime before executing.
- [x] Implement section9 createExternalPreviewService with validateCode/runSample plus read/cancel delegation to existing lifecycle; use030 sample-validation receipt writer, never a duplicate receipt engine.
- [x] Enforce authenticated Origin/role, exact tool ownership, Redis distributed admin limits, existing run identity/replay/cancel and bounded preview envelope. Preserve only synthetic samples under existing TTL.
- [x] Inject025/026 directly with fixture data; assert zero live HTTP/credential/decryption dependencies. Provide actual Redis cross-instance replay/quota/cancel fixtures.

## Interfaces / Contracts

C21 sections1–8 retain data/behavior requirements. [Section9](../../../architecture/ARCH-020-external-api-tools.md#9-tightened-implementation-boundaries-and-evidence) is authoritative for the narrowed ownership, factory signatures, scenario IDs and handoff rules. Consume accepted exports; no consumer may repair a missing producer by weakening the contract. Record actual dependency commits and published package versions.

## Dependencies

- ARCH-020-COMMERCE-019
- ARCH-020-COMMERCE-009
- ARCH-020-SHARED-002
- ARCH-020-COMMERCE-025
- ARCH-020-COMMERCE-026
- ARCH-020-COMMERCE-030

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-024

## Acceptance Criteria

- [x] PR01: save->sample->processed result->receipt succeeds for text code and visual JSON with actual processors and accepted preview lifecycle.
- [x] PR02: repeat same run returns original result; changed payload conflicts; cancel/unknown/expiry and two-instance quotas use same identity; changed draft does not alter frozen preview.
- [x] PR03: old preview request unchanged; invalid foreign fixture ID, unsupported media/oversize, raw HTML and invalid output fail safely; provider/decrypt call counts remain zero.

## Validation

Provide `test:arch020-external-preview` and scenario IDs from C21 section9. Start with the named positive path through the actual owned implementation. Add the specified rejection/race cases. Each report maps criterion -> test file/test name -> command -> observable result, not just a suite count. No claimed success based only on safe rejection or missing-config tests. Preserve each review reproduction as a committed regression alongside adjacent allowed/denied cases.

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

Attempt 5 implementation submitted for Architect Review. The implementation branch is pushed at `abb02d9`; the executor claim is cleared.

### Files Changed

- `moda-interact-commerce/src/commerce/external-preview/contracts.ts`
- `moda-interact-commerce/src/commerce/external-preview/service.ts`
- `moda-interact-commerce/src/commerce/preview/types.ts`
- `moda-interact-commerce/src/commerce/preview/store.ts`
- `moda-interact-commerce/src/commerce/preview/redis-store.ts`
- `moda-interact-commerce/src/commerce/preview/service.ts`
- `moda-interact-commerce/tests/external-preview.test.ts`
- `moda-interact-commerce/tests/preview-store.test.ts`
- `moda-interact-commerce/tests/preview-redis-lua.test.ts`

### Work Completed

External samples now load and clone/freeze the canonical saved revision, reject non-external or incompatible media, claim the canonical tool-test identity before quota/receipt/processor work, and preserve replay/conflict semantics. Tool-test cancellation state is persisted through memory and Redis stores, cancellation polls the same preview ID, and quota is released only after acquisition. Conversation fixture state has aggregate UTF-8 bounds, rejects foreign keys before persistence, freezes saved definitions, and uses the synthetic runner boundary without live tool execution.

### Acceptance Evidence

- PR01: `runs visual JSON sample through processor receipt and saved preview lifecycle` and `runs JavaScript sample through the accepted code processor and receipt lifecycle` pass in `tests/external-preview.test.ts`; actual COMMERCE-025/026 processors are used, the COMMERCE-030 validator is called once, results are `COMPLETED`, and stored replay returns the same result.
- PR02: `replays the same external preview run across Redis-backed instances without duplicate side effects`, `rejects a changed external preview payload before Redis-backed side effects`, `cancels a blocked external preview processor across Redis-backed instances`, `expires a Redis-backed running external preview to UNKNOWN on the same run id`, and `enforces Redis-backed external preview quota across different new run ids` pass in `tests/preview-redis-lua.test.ts`. The in-memory regressions `races the same preview identity across service instances without duplicate processing` and `cancels a blocked processor on the same preview identity` also pass; remote cancellation waits for the shared run to become terminal.
- PR03: `accepts a parameterized content type when the normalized MIME is allowed`, `runs a frozen conversation external fixture without live provider or credential access`, and `rejects a selected non external conversation fixture before persistence` pass in `tests/external-preview.test.ts`; unsupported media, raw HTML, invalid processor output, oversize samples, and fail-closed counters remain covered. Legacy requests remain unchanged because fixture fields remain optional.

### Validation Results

- `npm run test:arch020-external-preview`: PASS, 13 tests.
- `npm run test:arch020-external-publication`: PASS, 11 tests.
- `npm run test:arch020-code-processor`: PASS, 6 tests.
- Focused preview lifecycle command: PASS, 43 tests, including 9 real Redis Lua tests.
- Focused ESLint: PASS.
- `git diff --check`: PASS.
- Touched-file TypeScript diagnostics: none after final repair.
- Repository `npm run typecheck`: non-zero with 12 baseline diagnostics in studio workspace, connection command/lifecycle, external executor, and processor-test files; none point to the Attempt-5 implementation or tests.
- Repository `npm run build`: non-zero on the same existing diagnostics after successful runtime packaging, smoke validation, Prisma generation, and production compilation.

### Git / VCS

Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-031`. Parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-031`. Implementation commits: `7243937`, `b3dfcb4`, `411970e`, `598d641`, `abb02d9`; launcher claim commit: `d31ee385b762cee4514fd8c39a75556e9459c0e1`. Canonical preparation verified dependency gate passed, origin/main incorporation, and recursive submodule readiness at `7f920e8f2ad523e78e566f4dbdfbb1f68118b082`.

## Architect Review

### Review Status

Submitted for Architect Review; Attempt 5 is complete and the executor claim is cleared.

### Review Notes

Attempt 5 implementation and evidence are submitted for review. No self-acceptance is recorded.

### Reviewed Files

`src/commerce/external-preview/service.ts`, `src/commerce/preview/service.ts`, `tests/external-preview.test.ts`, and `tests/preview-redis-lua.test.ts`.

### Validation Reviewed

Focused suites pass as recorded above. Repository typecheck/build remain blocked by the listed baseline diagnostics.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile readiness/indexes after prerequisite acceptance; no automatic launch.

## Architect Review — Attempt 1 — 2026-09-22

### Review Status

Changes Requested

### Review Notes

Reviewed the submitted Attempt 1 implementation against C21 section 2.3, section 9.5
and PR01-PR03.

The submitted slice establishes a useful foundation and the following work is accepted
in substance and must be preserved:

- additive `TransformSample` fields on preview request/stored state;
- exact selected-tool ownership rejection for unknown conversation fixture keys;
- `validateCode(...)` canonical `{source,runtimeVersion}` hash verification;
- accepted COMMERCE-026 compiler/process adapter reuse;
- accepted COMMERCE-025 visual processor reuse;
- COMMERCE-030 `validateSampleAndRecord(...)` delegation rather than a second receipt
  writer;
- existing `PreviewService.runExternalToolTest(...)` replay/conflict persistence;
- zero direct provider HTTP / credential decrypt dependencies in
  `external-preview/**`;
- old preview request fields remain optional rather than becoming mandatory.

Do not redesign those working boundaries.

The task cannot be accepted as a "bounded first slice" because its own Acceptance
Criteria require PR01-PR03 complete before Review/Complete. The Completion Report
correctly records PR02 and PR03 as partial.

Four bounded functional corrections remain.

### A1-R1 — claim/replay must happen before quota, receipt validation or processing

Files permitted:

```text
src/commerce/external-preview/contracts.ts
src/commerce/external-preview/service.ts
src/commerce/preview/service.ts
tests/external-preview.test.ts
```

The current `runSample(...)` order is incorrect:

```text
active staff
-> external Redis slot
-> publicationValidation.validateSampleAndRecord
-> PreviewService.runExternalToolTest
-> PreviewStateStore.claimToolTest
```

This allows a replay to consume quota and execute the receipt validator before the
canonical `previewRunId` replay/conflict decision. A second instance racing the same
operation can return `QUOTA_EXCEEDED` rather than the original run.

Required order:

```text
parse bounded request
-> active staff
-> load/freeze canonical saved external tool revision (A1-R2)
-> PreviewStateStore.claimToolTest using complete frozen payload identity
   -> CONFLICT: ID_CONFLICT, zero quota/validator/processor calls
   -> REPLAY: return exact stored run, zero quota/validator/processor calls
   -> CREATED:
        acquire external preview quota
        validate sample/record receipt
        process fixture
        complete same previewRunId
        release quota
```

Implement this by placing quota acquisition, COMMERCE-030 validation and processor
execution inside the `process` callback that `PreviewService.runExternalToolTest(...)`
invokes only for a newly CREATED run. Do not duplicate the preview claim engine in
`external-preview`.

The payload hash/claim identity must include the complete frozen:

```text
previewRunId
toolRevisionId
fixtureId
arguments
externalResponseFixture
canonical saved definition identity required by the accepted preview lifecycle
```

A changed fixture, arguments, tool revision or saved-definition identity with the same
run ID must conflict.

Same-operation replay must not create/write a second publication receipt.

### A1-R2 — server-load and freeze the saved external definition; caller may not supply it

Files permitted:

```text
src/commerce/external-preview/contracts.ts
src/commerce/external-preview/service.ts
tests/external-preview.test.ts
```

Current `ExternalPreviewSampleInput` accepts:

```ts
definition?: CommerceToolDefinition
```

from the caller. Remove that field.

Add one injected server-side saved-revision port to
`ExternalPreviewDependencies`:

```ts
savedTools: {
  load(input: {
    principal: PreviewPrincipal;
    toolRevisionId: string;
  }): Promise<{
    toolRevisionId: string;
    definition: CommerceToolDefinition;
  } | null>;
};
```

`runSample(...)` must:

1. call `savedTools.load(...)` once before claiming;
2. require a non-null exact matching `toolRevisionId`;
3. parse the returned definition with the canonical Shared
   `CommerceToolDefinitionSchema`;
4. require `definition.execution.kind === "EXTERNAL_HTTP"`;
5. clone/freeze that exact saved definition;
6. use only that frozen definition for:
   - replay identity;
   - COMMERCE-030 validation;
   - visual/code processing;
   - returned connectionRevisionId/runtime trace.

Missing/mismatched/non-EXTERNAL_HTTP saved revisions fail with bounded
`INVALID_INPUT`/`UNAVAILABLE` according to the existing Preview error convention and
perform zero processor/receipt writes.

Do not introduce a second definition schema or let browser/service callers choose a
different definition for an existing toolRevisionId.

### A1-R3 — complete tool-test status/cancel/expiry on the same preview identity

Files permitted:

```text
src/commerce/preview/types.ts
src/commerce/preview/store.ts
src/commerce/preview/redis-store.ts
src/commerce/preview/service.ts
src/commerce/external-preview/contracts.ts
src/commerce/external-preview/service.ts
tests/external-preview.test.ts
```

C21 requires external sample execution to reuse existing preview
`status/read/cancel/replay` semantics. Attempt 1 exposes read but no tool-test cancel
operation.

Extend `StoredToolTest` with:

```ts
cancelRequested: boolean;
```

and update `StoredToolTestSchema`, in-memory store and Redis transport accordingly.

Add to `PreviewStateStore`:

```ts
requestCancelToolTest(
  environment: string,
  adminId: string,
  id: string,
  now: number,
): Promise<StoredToolTest | null>;
```

Semantics:

```text
missing -> null
RUNNING -> set cancelRequested=true
terminal -> return unchanged terminal record
```

Add to `PreviewService`:

```ts
cancelToolTest(
  principal: PreviewPrincipal,
  runId: string,
): Promise<RunResponse>;
```

Use the same controller/execution ownership pattern already used for conversation
runs. A newly-created external tool test must have an AbortController registered
under its existing `previewRunId`; cancellation aborts the processor signal and the
same stored run becomes `CANCELLED`.

If cancellation wins after the claim but before terminal completion:

```text
status: CANCELLED
same previewRunId
result: null
quota released
```

If a process becomes indeterminate because ownership/Redis completion cannot be
confirmed, retain the same run ID and return/store `UNKNOWN`; do not generate a new
operation.

The existing `PREVIEW_SLOT_MS` expiry behavior for a RUNNING tool test must preserve
the same ID and transition it to UNKNOWN.

Expose corresponding delegation from `ExternalPreviewService`:

```ts
getToolTest(...)
cancelToolTest(...)
```

No new UI route/client is required by this task unless an existing server route must
be minimally extended to expose the already-existing C9 cancel surface. Do not build
COMMERCE-027/024 UI here.

### A1-R4 — conversation external fixtures must be bounded, external-only and actually used

Files permitted:

```text
src/commerce/preview/types.ts
src/commerce/preview/service.ts
src/commerce/external-preview/contracts.ts
src/commerce/external-preview/service.ts
tests/external-preview.test.ts
```

Attempt 1 stores `conversation.externalResponseFixtures`, but
`PreviewService.execute(...)` ignores them and always calls the normal
`toolExecutor.execute(...)`. That does not satisfy C21 and can route a synthetic
external preview toward the live execution boundary.

Correct the conversation fixture path.

#### Request bounds

`ConversationBodySchema.externalResponseFixtures` remains optional and max 32
entries, but must additionally require:

```text
sum UTF-8 byte length of every fixture.bodyText <= 262144
```

Do not raise the individual TransformSample bound or the existing preview envelope.

#### Ownership/type validation

At conversation creation, for every fixture key:

```text
key must be an exact toolRevisionId present in the frozen selected manifest
the exact saved tool revision must resolve server-side
its canonical definition.execution.kind must be EXTERNAL_HTTP
```

Unknown selected IDs and selected-but-non-external tools must fail before conversation
state is stored.

Use the same server-owned saved-tool revision authority established in A1-R2; do not
infer external-ness from the fixture or tool name.

Freeze the validated fixture map and exact saved external definitions for the
conversation's 24-hour preview lifetime so later draft edits cannot alter the active
synthetic conversation.

#### Execution

When a frozen conversation tool descriptor has a matching external fixture:

```text
DO NOT call the normal/live PreviewToolExecutionPort.execute path
DO NOT call provider HTTP
DO NOT resolve/decrypt credentials
```

Process the frozen synthetic fixture using the selected definition's accepted
COMMERCE-025/026 processor exactly as the saved definition requires, validate/render
through the same bounded output path, and return a normal `CommerceToolResult` to the
existing runner.

A selected non-external tool or an external tool without an external fixture retains
the pre-existing preview behavior; do not change old empty-map/no-fixture requests.

The same external fixture is static for that synthetic conversation. A later request
with changed fixture content and the same conversation ID must conflict through the
existing frozen conversation payload identity.

### A1-R5 — finish PR01 and PR03 focused evidence

File:

```text
tests/external-preview.test.ts
```

Keep the current three tests and extend the focused suite. Do not add an arbitrary
broad test quota.

At minimum add the following named scenarios.

#### PR01 — actual processor success in both modes

```text
"runs visual JSON sample through processor receipt and saved preview lifecycle"
```

Preserve/strengthen the existing visual success so it asserts:

```text
actual createResponseProcessor used
COMMERCE-030 validator called once
status COMPLETED
result.data.values exact
same run read returns exact result
```

Add:

```text
"runs JavaScript sample through the accepted code processor and receipt lifecycle"
```

using actual `createCodeResponseProcessor()`, valid saved EXTERNAL_HTTP definition,
JSON/TEXT shape appropriate to that definition, and require COMPLETED bounded values.

#### PR02 — Redis/lifecycle behavior

Use two service instances sharing the same preview Redis/store fixtures and prove:

```text
same previewRunId + same payload raced across two instances
  -> one execution/validator/processor
  -> both observe the same run identity/result
  -> no QUOTA_EXCEEDED replay

same previewRunId + changed fixture
  -> ID_CONFLICT
  -> zero second validator/processor calls

cancel a blocked processor
  -> CANCELLED on same run ID
  -> processor receives aborted signal
  -> quota released
  -> reread remains CANCELLED

expired RUNNING tool test
  -> UNKNOWN on same run ID
```

Also prove two different newly-created runs for the same admin contend on the
distributed external-preview quota as specified; this is separate from same-operation
replay.

#### PR03 — bounded rejection and zero live dependencies

Add explicit regressions for:

```text
caller cannot supply/override saved definition

foreign conversation fixture toolRevisionId
  -> reject

fixture for selected non-EXTERNAL_HTTP tool
  -> reject

conversation fixture total body bytes > 256KiB
  -> reject

unsupported sample media
  -> fail closed

oversize sample/request
  -> fail closed

raw HTML supplied where saved response mode cannot accept it
  -> fail closed

processor invalid output
  -> fail closed
  -> no raw fallback
```

For the successful and rejected external fixture paths assert explicit counters:

```text
provider HTTP calls       == 0
credential resolution     == 0
credential decryption     == 0
```

Use injected trap functions that throw if invoked; do not prove zero calls merely by
the absence of such dependencies in one test factory.

### A1-R6 — durable report and stop condition

Before returning Attempt 2:

1. update Work Items/Acceptance Criteria/Validation only when their named PR evidence
   actually passes;
2. replace the "bounded first slice" Completion Report with the exact Attempt-2
   implementation/report evidence;
3. record implementation commit(s), parent report commit, launcher/worktree
   synchronization evidence and the exact focused test names/results;
4. record repository-wide baseline failures accurately without fixing unrelated code;
5. return:

```yaml
status: review
attempt: 2
executor: null
claimed_at: null
```

6. push both mirrored task branches;
7. STOP.

Do not begin COMMERCE-024, COMMERCE-012 or any system-test task.

### Required Validation

Run exactly once after the corrections:

```bash
npm run test:arch020-external-preview
npm run test:arch020-external-publication
npm run test:arch020-code-processor
npx vitest run \
  tests/preview-service.test.ts \
  tests/preview-store.test.ts \
  tests/preview-routes.test.ts
npx eslint \
  src/commerce/external-preview \
  src/commerce/preview \
  tests/external-preview.test.ts
npm run typecheck
npm run build
git diff --check
```

The focused external-preview suite must prove PR01-PR03 by named scenario, not only
suite count.

Repository typecheck/build may remain non-zero only for the unchanged documented
baseline and only if no diagnostic points at Attempt-2-owned files.

### Reviewed Files

- `moda-interact-commerce/src/commerce/external-preview/contracts.ts`
- `moda-interact-commerce/src/commerce/external-preview/service.ts`
- `moda-interact-commerce/src/commerce/preview/types.ts`
- `moda-interact-commerce/src/commerce/preview/store.ts`
- `moda-interact-commerce/src/commerce/preview/redis-store.ts`
- `moda-interact-commerce/src/commerce/preview/service.ts`
- `moda-interact-commerce/tests/external-preview.test.ts`
- `docs/architecture/ARCH-020-external-api-tools.md`
- this task's Attempt-1 Completion Report

### Validation Reviewed

Submitted Attempt-1 evidence:

```text
external preview focused:       3 PASS
external publication adjacent: 11 PASS
code processor adjacent:        6 PASS
legacy preview adjacent:       10 PASS
changed-file ESLint:            PASS
repository typecheck:           unrelated existing baseline
```

The report itself records PR02 and PR03 as partial. Direct source inspection confirms
the missing behavior described above.

### Architecture Conformance

Partial.

PR01 has a visual positive path but no successful code-sample path. PR02 is missing
same-operation cross-instance replay ordering, tool-test cancellation and explicit
expiry/quota races. PR03 is missing required rejection evidence, and conversation
external fixtures are stored but not consumed by the conversation tool execution
path.

No downstream task may be promoted from this review.

### Follow-up

Return the same task to `ready`, retain Attempt 1 and clear the claim.

The next successful `/moda-task ARCH-020-COMMERCE-031` claim creates Attempt 2
exactly once.

Implement only A1-R1 through A1-R6, return to Review and STOP.

## Architect Review — Attempt 2 implementation checkpoint — 2026-09-22

### Review Status

Changes Requested

### Review Notes

This is an implementation checkpoint, not an acceptance review.

Direct inspection of the current Attempt-2 worktree accepts the lifecycle/source
corrections from A1-R1 through A1-R4 in substance:

```text
server-owned saved tool definitions                         implemented
saved definition frozen into preview identity               implemented
claim/replay before quota/receipt/processor side effects    implemented
tool-test cancel state and AbortSignal propagation           implemented
RUNNING expiry -> UNKNOWN on the same run ID                implemented
aggregate conversation external-fixture byte bound           implemented
conversation saved-definition freezing                       implemented
conversation synthetic external fixture runner hook          implemented
response media/type validation                               implemented
```

Do not redesign or revert those paths merely because this task is returned to Ready.

The task is returned to `ready` only because the required named PR01-PR03 regressions,
Completion Report reconciliation, commits and mirrored pushes remain incomplete.
The next successful `/moda-task ARCH-020-COMMERCE-031` claim creates Attempt 3
exactly once.

Attempt 3 is **proof/handoff focused** unless one of the exact regressions below
exposes a genuine COMMERCE-031-owned production defect.

### A2-R1 — finish PR01 named processor lifecycle proof

Primary file:

```text
tests/external-preview.test.ts
```

Keep the current tests. The focused suite must contain and pass these exact named
scenarios.

#### Visual processor

Use this exact test title:

```text
runs visual JSON sample through processor receipt and saved preview lifecycle
```

It must prove:

```text
actual createResponseProcessor() is used
saved server-owned EXTERNAL_HTTP definition is used
COMMERCE-030 validateSampleAndRecord called exactly once
status == COMPLETED
result.data.values == exact expected processed object
getToolTest(same previewRunId) returns the exact terminal result
provider HTTP calls == 0
credential resolution calls == 0
credential decryption calls == 0
```

#### JavaScript processor

Add this exact test title:

```text
runs JavaScript sample through the accepted code processor and receipt lifecycle
```

Use the actual accepted `createCodeResponseProcessor()` and a saved EXTERNAL_HTTP
definition whose response processing is `JAVASCRIPT`.

Require:

```text
COMMERCE-030 validator called exactly once
status == COMPLETED
bounded processed values equal the expected object
same run reread returns the exact terminal result
provider HTTP calls == 0
credential resolution calls == 0
credential decryption calls == 0
```

Do not replace either processor with a test-only implementation merely to satisfy
the test name.

### A2-R2 — finish PR02 replay/cancel/expiry/quota proof

Use two service instances that share the same PreviewStateStore/Redis-backed test
state where required.

Add these exact test titles:

```text
replays the same preview run across two instances before quota validation and processing

conflicts a changed sample payload before quota validation and processing

cancels a blocked external tool test across instances and releases quota

expires a running external tool test to UNKNOWN on the same run id

enforces distributed external preview quota across different new run ids
```

#### Same-operation replay

For two concurrent calls with the same:

```text
previewRunId
toolRevisionId
arguments
fixture
saved definition identity
```

prove:

```text
savedTools.load may occur as required to establish the frozen identity
one CREATED preview execution
validator calls == 1
processor calls == 1
quota admission for business execution == 1
both callers observe the same previewRunId
both callers observe the same terminal result
neither caller receives QUOTA_EXCEEDED
```

A REPLAY must perform zero second receipt/processor side effects.

#### Changed payload conflict

Reuse the same previewRunId but change at least the fixture body.

Require:

```text
ID_CONFLICT
second validator call count == 0
second processor call count == 0
second business quota admission count == 0
```

#### Cancellation

Make the processor block until its AbortSignal is aborted.

Execution:

```text
instance A -> starts new external preview run and blocks in processor
instance B -> cancelToolTest(principal, same previewRunId)
```

Require:

```text
processor signal becomes aborted
same previewRunId becomes CANCELLED
result == null
quota released
later getToolTest(same previewRunId) remains CANCELLED
```

#### Expiry

Persist/produce a RUNNING tool test, advance the injected clock past
`PREVIEW_SLOT_MS`, then read the same run.

Require:

```text
status == UNKNOWN
previewRunId unchanged
no replacement run created
```

#### Distributed quota

Use two **different** newly-created run IDs for the same admin and prove the accepted
external-preview distributed quota behavior. This scenario is separate from replay;
same-operation replay must never fail only because the quota is already occupied by
its original operation.

### A2-R3 — finish PR03 saved-definition/rejection/zero-live-dependency proof

Add these exact test titles:

```text
uses the server saved definition and ignores a caller definition override

rejects a foreign conversation fixture tool revision before storing the conversation

rejects a fixture for a selected non external tool before storing the conversation

rejects conversation external fixtures above the aggregate byte limit

rejects unsupported external sample media without processing

rejects an oversize external sample without processing

rejects raw HTML when the saved response mode cannot accept it

rejects invalid processor output without raw fallback

runs a frozen conversation external fixture without live provider or credential access
```

#### Saved definition authority

The public Attempt-3 sample request must not have an authoritative `definition`
field.

If necessary, construct a raw/cast request containing a conflicting extra
`definition` property and prove:

```text
server savedTools.load definition determines processing
caller-supplied extra definition has no effect
receipt identity uses server-saved definition
returned connectionRevisionId/runtime trace comes from server-saved definition
```

#### Conversation ownership/type validation

Before conversation state is stored:

```text
foreign toolRevisionId not in frozen manifest
  -> reject

selected toolRevisionId whose saved definition is not EXTERNAL_HTTP
  -> reject

aggregate UTF-8 bytes of all fixture bodyText values > 262144
  -> reject
```

Do not infer EXTERNAL_HTTP ownership from fixture key/name; use the server-owned saved
tool definition.

#### Media/size/output rejection

Explicitly prove:

```text
unsupported media -> fail closed, zero processor call when processing is impossible

oversize sample/request -> fail closed before processing

raw HTML incompatible with saved response mode -> fail closed

processor invalid output -> fail closed
                         -> no raw-body/result fallback
```

#### Zero live dependencies

For both successful external-fixture execution and the relevant rejection paths, use
explicit traps/counters for the live dependencies available at the composition
boundary.

At minimum prove:

```text
provider HTTP calls       == 0
credential resolution     == 0
credential decryption     == 0
```

Trap functions should throw if invoked; do not infer zero calls only because one test
factory happens not to expose a dependency.

#### Conversation synthetic execution

For a frozen conversation tool whose exact toolRevisionId has a matching external
fixture:

```text
externalFixtureRunner is used
normal/live PreviewToolExecutionPort.execute is not used for that tool call
saved/frozen definition is used
normal bounded CommerceToolResult reaches the runner
fixture/definition remains frozen for the conversation lifetime
```

A later changed fixture request using the same conversation identity must conflict
through the existing frozen conversation payload identity.

### A2-R4 — preserve already-implemented Attempt-2 source behavior

Do not proactively edit production source beyond what is required by a failing named
regression.

The following current implementation is accepted in substance and must not regress:

```text
src/commerce/external-preview/**
  server-owned savedTools loader
  no caller-authoritative definition
  claim-before-side-effects execution
  COMMERCE-030 receipt delegation
  COMMERCE-025/026 processor delegation
  bounded media/type validation

src/commerce/preview/**
  cancelRequested stored state
  requestCancelToolTest
  cancelToolTest
  AbortController ownership
  CANCELLED same-ID terminal state
  RUNNING expiry -> UNKNOWN
  aggregate external fixture byte bound
  frozen external definitions for conversation
  externalFixtureRunner synthetic hook
```

If a named regression exposes an actual COMMERCE-031 defect, make the smallest
task-owned source correction, record it in the Completion Report and rerun only the
affected focused proof plus the required validation below.

If the failure is in an accepted producer owned by COMMERCE-025, COMMERCE-026 or
COMMERCE-030, do not modify that producer from this task. Return COMMERCE-031
`blocked` with the exact reproduction for `moda_architect`.

### A2-R5 — exact validation contract

After the named PR01-PR03 regressions are complete, run exactly once:

```bash
npm run test:arch020-external-preview

npm run test:arch020-external-publication

npm run test:arch020-code-processor

npx vitest run \
  tests/preview-service.test.ts \
  tests/preview-store.test.ts \
  tests/preview-routes.test.ts

npx eslint \
  src/commerce/external-preview \
  src/commerce/preview \
  tests/external-preview.test.ts

npm run typecheck
npm run build

git diff --check
```

The external-preview suite must identify the named PR01-PR03 scenarios in its output
or Completion Report. A passing aggregate count without the named evidence is not
sufficient.

Repository `typecheck`/`build` may remain non-zero only when:

```text
diagnostics are materially unchanged from the documented baseline
AND
no diagnostic points at:
  src/commerce/external-preview/**
  src/commerce/preview/**
  tests/external-preview.test.ts
```

Do not fix unrelated Prisma/integration work from COMMERCE-031.

### A2-R6 — implementation commit, Completion Report and mirrored handoff

Once A2-R1 through A2-R5 pass, commit/push the implementation worktree before
reconciling the parent report.

Implementation commit must include only task-owned corrections/proof files, normally:

```text
src/commerce/external-preview/**
src/commerce/preview/**
tests/external-preview.test.ts
package.json / package-lock.json only when actually required by this task
```

Record the resulting implementation SHA.

Then update the canonical Completion Report in this task file.

The Attempt-3 report must contain:

```text
Attempt: 3
implementation commit: <exact SHA>
parent report commit: <filled after parent commit>

launcher-resolved implementation worktree
launcher-resolved parent worktree
start-of-attempt synchronization evidence
both mirrored branches pushed/clean

PR01:
  visual processor lifecycle test name + PASS
  JavaScript processor lifecycle test name + PASS

PR02:
  cross-instance same-operation replay test + PASS
  changed-payload conflict test + PASS
  cancellation test + PASS
  expiry UNKNOWN test + PASS
  different-new-run distributed quota test + PASS

PR03:
  saved-definition authority + PASS
  foreign fixture rejection + PASS
  non-external fixture rejection + PASS
  aggregate byte bound + PASS
  unsupported media + PASS
  oversize input + PASS
  raw HTML fail-closed + PASS
  invalid output/no fallback + PASS
  frozen conversation synthetic fixture + PASS
  explicit zero provider HTTP/credential/decrypt counters + PASS

adjacent validation:
  external publication command/result
  code processor command/result
  legacy preview command/result
  focused ESLint
  typecheck/build exact baseline diagnostics
  git diff --check
```

Only check the Work Items / Acceptance Criteria / Validation items when this evidence
actually exists.

Before handoff set exactly:

```yaml
status: review
attempt: 3
executor: null
claimed_at: null
```

Do not edit this Architect Review.

Commit the parent report, push the parent task branch, confirm both mirrored task
branches are clean and synchronized, then STOP.

Do not begin COMMERCE-024, COMMERCE-012 or any system-test task.

### Reviewed Files

Checkpoint inspection covered:

- `moda-interact-commerce/src/commerce/external-preview/contracts.ts`
- `moda-interact-commerce/src/commerce/external-preview/service.ts`
- `moda-interact-commerce/src/commerce/preview/types.ts`
- `moda-interact-commerce/src/commerce/preview/store.ts`
- `moda-interact-commerce/src/commerce/preview/redis-store.ts`
- `moda-interact-commerce/src/commerce/preview/service.ts`
- `moda-interact-commerce/tests/external-preview.test.ts`
- this task's existing Completion Report and Attempt-1 Architect Review

### Validation Reviewed

Checkpoint handoff reports:

```text
Attempt-2 lifecycle source corrections implemented
focused/adjacent tests: 34/34 plus external suites PASS
changed-boundary ESLint: PASS
git diff --check: PASS
repository typecheck/build: existing unrelated baseline
```

Those results are accepted as implementation-progress evidence but are not yet
sufficient for Architect Review because the named PR01-PR03 regressions and durable
Attempt-3 report do not yet exist.

### Architecture Conformance

Source direction is conformant in substance.

The remaining gate is deterministic proof/handoff, not a new architecture design.

### Follow-up

Return the same task to `ready`, preserve `attempt: 2`, clear the claim.

The next successful `/moda-task ARCH-020-COMMERCE-031` claim creates Attempt 3
exactly once.

Attempt 3 implements only A2-R1 through A2-R6, returns to Review and STOPs.

## Architect Review — Attempt 3 — 2026-09-22

### Review Status

Changes Requested

### Review Notes

Attempt 3 materially completes the lifecycle source corrections requested after
Attempt 1:

```text
server-owned saved definition authority                     accepted in substance
claim-before-quota/receipt/processor ordering               accepted in substance
cross-instance cancel state / AbortSignal propagation       accepted in substance
same-ID tool-test expiry -> UNKNOWN                         accepted in substance
conversation aggregate fixture byte bound                  accepted in substance
frozen conversation external definitions                   accepted in substance
synthetic conversation runner hook                         accepted in substance
visual + JavaScript positive sample paths                  accepted in substance
```

Do not redesign or revert those paths.

This review remains Changes Requested for one real C21 behavior defect and for the
remaining producer-owned proof that the task itself explicitly requires.

### A3-R1 — normalize MIME before saved-format comparison

File:

```text
src/commerce/external-preview/service.ts
```

Current code compares:

```ts
execution.responseFormat.mediaTypes.includes(
  sample.contentType.toLowerCase()
)
```

This incorrectly rejects a valid C21 sample such as:

```text
saved accepted media:
  application/json

sample contentType:
  application/json; charset=utf-8
```

C21 section 2.3 explicitly permits a charset parameter and requires comparison of the
normalized MIME type. COMMERCE-030 already implements the canonical behavior.

Replace the comparison input with exactly:

```ts
const sampleMime = sample.contentType
  .split(';', 1)[0]
  .trim()
  .toLowerCase();

if (!execution.responseFormat.mediaTypes.includes(sampleMime)) {
  throw new PreviewError('INVALID_INPUT');
}
```

Do not duplicate MIME parsing elsewhere and do not weaken the saved response-format
allowlist.

Add a focused regression using a saved JSON external definition whose mediaTypes are:

```ts
['application/json']
```

and a sample:

```ts
{
  status: 200,
  contentType: 'application/json; charset=utf-8',
  bodyText: '{"name":"Moda"}',
}
```

Require COMPLETED with the same processed result as the plain
`application/json` adjacent case.

### A3-R2 — prove PR02 against the actual Redis preview store and external quota

The current cross-instance test shares an `InMemoryPreviewStateStore`; it does not
prove the task Work Item:

```text
Provide actual Redis cross-instance replay/quota/cancel fixtures.
```

Files permitted:

```text
tests/external-preview.test.ts
tests/preview-redis-lua.test.ts
```

Reuse the existing local `redis-server` + `ioredis` harness already committed in
`tests/preview-redis-lua.test.ts`. Do not introduce Docker or a second Redis test
framework.

Add one real-Redis focused block, guarded by the same existing local-server
availability rule, that constructs:

```text
one shared ioredis server
two RedisPreviewStateStore instances with the same key prefix
two PreviewService instances
two ExternalPreviewService instances
the same ioredis client/transport for the external-preview quota
```

Use unique prefixes so the test cannot collide with adjacent preview Redis tests.

#### Same-operation race

Run the same `previewRunId` + same complete payload concurrently through both
ExternalPreviewService instances.

Require:

```text
both callers observe the same previewRunId
both callers observe the same terminal result
COMMERCE-030 validator total calls == 1
processor total calls == 1
business quota acquisition succeeds only for the CREATED execution
the REPLAY does not return QUOTA_EXCEEDED
```

Use counters shared by the two service instances.

#### Changed-payload conflict

After a completed run, reuse the same previewRunId with a changed fixture body.

Require:

```text
ID_CONFLICT
validator total does not increment
processor total does not increment
external business-quota acquisition does not increment
```

#### Cross-instance cancellation

Use a processor that blocks until AbortSignal aborts.

```text
instance A starts the new run
instance B calls cancelToolTest(same run ID)
```

Require:

```text
processor receives aborted signal
stored Redis tool test becomes CANCELLED
same previewRunId retained
result == null
later read through either instance remains CANCELLED
quota released
```

#### Redis expiry

Persist/start a RUNNING external tool-test owner in the real
`RedisPreviewStateStore`, then read after `PREVIEW_SLOT_MS`.

Require:

```text
status == UNKNOWN
same previewRunId
late completion with old owner token == false
```

#### Different-new-run quota

For the same admin, block one newly CREATED external run after quota acquisition and
start a second run with a different previewRunId.

Require:

```text
second new run -> QUOTA_EXCEEDED
first run remains the owner
after first run terminates/cancels -> quota is released
a later distinct run may acquire the quota
```

This is separate from same-operation replay.

If the local `redis-server` prerequisite is unavailable in the execution environment,
do not mark PR02 complete. Return the task `blocked` with that exact infrastructure
condition; do not replace this proof with another in-memory mock.

### A3-R3 — prove conversation external fixtures are actually consumed

Current source correctly stores frozen fixture definitions and contains the
`externalFixtureRunner` branch in `PreviewService.execute(...)`, but the submitted
focused suite does not exercise that behavior.

Primary file:

```text
tests/external-preview.test.ts
```

Add a focused scenario with this exact title:

```text
runs a frozen conversation external fixture without live provider or credential access
```

Construct a valid Preview bundle whose frozen manifest contains one exact external
tool descriptor. Configure:

```text
savedTools.load:
  returns the exact EXTERNAL_HTTP saved definition for that toolRevisionId

externalResponseFixtures:
  contains exactly that toolRevisionId

externalFixtureRunner:
  validates/records the exact:
    toolRevisionId
    frozen saved definition
    frozen TransformSample
    arguments
  returns a valid CommerceToolResult
```

Also install explicit live-path traps/counters:

```text
PreviewToolExecutionPort.execute:
  throws "unexpected live tool execution"

provider HTTP:
  throws "unexpected provider HTTP"

credential resolution:
  throws "unexpected credential resolution"

credential decryption:
  throws "unexpected credential decryption"
```

Where provider/credential traps exist at the composition seam, wire them directly;
do not assert zero calls merely by omitting the dependency.

Execute:

```text
startConversation(...)
startRun(...)
wait/read terminal run
```

Require:

```text
conversation fixture definition is server-loaded before storage
externalFixtureRunner called exactly once
normal/live PreviewToolExecutionPort.execute called 0
provider HTTP calls == 0
credential resolution calls == 0
credential decryption calls == 0
terminal preview run == COMPLETED
normal CommerceToolResult reaches the runner/final response path
```

Then retry `startConversation(...)` with the same conversation ID but changed fixture
content and require the existing frozen conversation identity to conflict or replay
the already-frozen conversation according to the canonical C9 identity contract; it
must never silently replace the stored fixture.

Add adjacent rejection cases through `PreviewService.startConversation(...)`, not
only `ConversationBodySchema.parse(...)`:

```text
fixture key not present in frozen selected manifest
  -> INVALID_INPUT before conversation storage

fixture key selected but saved tool definition is not EXTERNAL_HTTP
  -> INVALID_INPUT before conversation storage
```

The existing aggregate >256KiB schema case may remain as the byte-bound proof.

### A3-R4 — reconcile the focused PR03 fail-closed evidence

The current combined test:

```text
fails closed for unsupported media, raw HTML, and invalid processor output
```

does not separately prove every required side-effect boundary.

Strengthen it or split it so the report can state exactly:

```text
unsupported media:
  INVALID_INPUT
  validator calls == 0
  processor calls == 0

raw HTML incompatible with saved response mode:
  INVALID_INPUT
  no raw fallback result

invalid processor output:
  INVALID_INPUT
  no raw body/result fallback
```

Add an oversize sample/request regression if it is not already directly exercised by
the focused external-preview suite. The rejection must happen before processor work
when the canonical request/schema bound can reject it.

Preserve the existing caller-supplied-definition override test and make the report
state that the extra caller field has no authority over the server-loaded definition.

### A3-R5 — durable task reconciliation is mandatory

The task is currently in Review while all four Work Items and PR01-PR03 Acceptance
Criteria remain unchecked. The Completion Report also compresses required PR02/PR03
evidence into broader suite claims.

After A3-R1 through A3-R4 pass:

1. check each Work Item only if its exact owned behavior is present;
2. check PR01 only when both actual processor positive paths pass;
3. check PR02 only when the **real Redis** replay/quota/cancel/expiry evidence above
   passes;
4. check PR03 only when service-level conversation ownership/type rejection,
   media/size/output fail-closed behavior and zero-live-dependency evidence pass;
5. check the required Validation items truthfully;
6. replace/update the Attempt-3 Completion Report so each PR criterion maps to:
   - committed test file;
   - exact test name;
   - exact command;
   - observed result;
7. record the final implementation commit and parent report commit;
8. record launcher-resolved worktrees, synchronization evidence and clean/pushed
   mirrored branches.

Return metadata must be:

```yaml
status: review
attempt: 4
executor: null
claimed_at: null
```

because the next authorized claim after this review creates Attempt 4 exactly once.

Do not edit this Architect Review.

### Required Validation

After the correction, run exactly:

```bash
npm run test:arch020-external-preview

npm run test:arch020-external-publication

npm run test:arch020-code-processor

npx vitest run \
  tests/preview-service.test.ts \
  tests/preview-store.test.ts \
  tests/preview-redis-lua.test.ts \
  tests/preview-routes.test.ts

npx eslint \
  src/commerce/external-preview \
  src/commerce/preview \
  tests/external-preview.test.ts \
  tests/preview-redis-lua.test.ts

npm run typecheck
npm run build

git diff --check
```

The external-preview/Redis output must identify the actual Redis-backed scenarios;
an aggregate test count alone is not sufficient.

Repository typecheck/build may remain non-zero only for materially unchanged baseline
diagnostics and only when no diagnostic points at:

```text
src/commerce/external-preview/**
src/commerce/preview/**
tests/external-preview.test.ts
tests/preview-redis-lua.test.ts
```

### Reviewed Files

- `moda-interact-commerce/src/commerce/external-preview/contracts.ts`
- `moda-interact-commerce/src/commerce/external-preview/service.ts`
- `moda-interact-commerce/src/commerce/preview/types.ts`
- `moda-interact-commerce/src/commerce/preview/store.ts`
- `moda-interact-commerce/src/commerce/preview/redis-store.ts`
- `moda-interact-commerce/src/commerce/preview/service.ts`
- `moda-interact-commerce/tests/external-preview.test.ts`
- `moda-interact-commerce/tests/preview-service.test.ts`
- `moda-interact-commerce/tests/preview-store.test.ts`
- `moda-interact-commerce/tests/preview-redis-lua.test.ts`
- this task's Attempt-3 Completion Report

### Validation Reviewed

Submitted Attempt-3 evidence:

```text
external preview focused:       9 PASS
external publication adjacent: 11 PASS
code processor adjacent:        6 PASS
preview lifecycle adjacent:     34 PASS
focused ESLint:                 PASS
git diff --check:               PASS
repository typecheck/build:     unrelated existing baseline
```

Those results establish substantial progress but do not satisfy the task's explicit
real-Redis PR02 Work Item or the conversation synthetic-execution PR03 evidence.

### Architecture Conformance

Partial.

The production lifecycle direction is substantially conformant. One C21 MIME
normalization bug remains in `external-preview/service.ts`, and the required
producer-owned Redis/conversation evidence is incomplete.

No downstream task may be promoted from this review.

### Follow-up

Return the same task to `ready`, preserve `attempt: 3`, clear the claim.

The next successful `/moda-task ARCH-020-COMMERCE-031` claim creates Attempt 4
exactly once.

Implement only A3-R1 through A3-R5, return to Review, push both mirrored branches and
STOP. Do not begin COMMERCE-024, COMMERCE-012 or any system-test task.

## Architect Review — Attempt 4 — 2026-09-22

### Review Status

Changes Requested

### Review Notes

Reviewed the exact Attempt 4 snapshot submitted at implementation `598d641` and
parent report `e2bd7d98` against the authoritative Attempt-3 A3-R1..A3-R5 contract.

Attempt 4 adds one valid PR03 regression:

```text
rejects foreign conversation fixtures before persistence
```

That correction is accepted in substance and must be preserved.

The task is not accepted because three previously explicit requirements remain
unimplemented in the submitted source/proof.

This is a narrow correction cycle. Do not redesign the external-preview lifecycle or
repeat already-accepted work.

### A4-R1 — implement the previously requested MIME normalization

Source file:

```text
src/commerce/external-preview/service.ts
```

The submitted source still contains:

```ts
if (!execution.responseFormat.mediaTypes.includes(
  sample.contentType.toLowerCase()
)) {
  throw new PreviewError('INVALID_INPUT');
}
```

This still rejects valid C21 content types with parameters, for example:

```text
saved mediaTypes:
  application/json

sample:
  application/json; charset=utf-8
```

Replace the comparison with exactly:

```ts
const sampleMime = sample.contentType
  .split(';', 1)[0]
  .trim()
  .toLowerCase();

if (!execution.responseFormat.mediaTypes.includes(sampleMime)) {
  throw new PreviewError('INVALID_INPUT');
}
```

Do not change the saved media-type allowlist.

Add one focused regression in:

```text
tests/external-preview.test.ts
```

with exact title:

```text
accepts a parameterized content type when the normalized MIME is allowed
```

Use:

```ts
saved responseFormat.mediaTypes = ['application/json']

sample = {
  status: 200,
  contentType: 'application/json; charset=utf-8',
  bodyText: '{"name":"Moda"}',
}
```

Require:

```text
COMPLETED
processed values == { name: "Moda" }
validator called once
processor called once
```

### A4-R2 — add the required real-Redis PR02 proof

The submitted test:

```text
races the same preview identity across service instances without duplicate processing
```

still shares:

```ts
new InMemoryPreviewStateStore()
```

It therefore does not satisfy the task Work Item requiring:

```text
actual Redis cross-instance replay/quota/cancel fixtures
```

Do not delete the in-memory test; it remains useful.

Add the real-Redis proof to:

```text
tests/preview-redis-lua.test.ts
```

Reuse the existing local `/usr/local/bin/redis-server` + `ioredis` harness already
present in that file. Do not introduce Docker or another Redis harness.

Use one unique prefix for this task, for example:

```text
test:external-preview
```

Construct:

```text
RedisPreviewStateStore A
RedisPreviewStateStore B

PreviewService A
PreviewService B

ExternalPreviewService A
ExternalPreviewService B
```

backed by the same Redis server/state prefix.

The two ExternalPreviewService instances must also share one Redis-backed external
preview quota transport. Do not use independent `redis.eval` mocks for this proof.

Add these exact named scenarios.

#### 1. Same-operation replay

```text
replays the same external preview run across Redis-backed instances without duplicate side effects
```

Run the same complete payload concurrently through service A and B:

```text
same previewRunId
same toolRevisionId
same fixtureId
same arguments
same sample
same saved definition
```

Require:

```text
both responses use the same previewRunId
both responses have the same terminal result
publication validator total calls == 1
processor total calls == 1
REPLAY does not return QUOTA_EXCEEDED
```

#### 2. Changed-payload conflict

```text
rejects a changed external preview payload before Redis-backed side effects
```

After a completed run, reuse the same `previewRunId` with changed fixture body text.

Require:

```text
ID_CONFLICT
validator total does not increment
processor total does not increment
business quota acquisition total does not increment
```

#### 3. Cross-instance cancellation

```text
cancels a blocked external preview processor across Redis-backed instances
```

Make service A's processor block until its AbortSignal is aborted.
Call `cancelToolTest(...)` through service B.

Require:

```text
processor signal aborted
same previewRunId == CANCELLED
result == null
later getToolTest through A == CANCELLED
later getToolTest through B == CANCELLED
quota released
```

#### 4. Redis expiry

```text
expires a Redis-backed running external preview to UNKNOWN on the same run id
```

Create/claim a RUNNING tool test in the Redis store and read it after
`PREVIEW_SLOT_MS`.

Require:

```text
same previewRunId
status == UNKNOWN
late completeToolTest with old owner token == false
```

#### 5. Different-new-run quota

```text
enforces Redis-backed external preview quota across different new run ids
```

For one admin:

```text
run A:
  different new previewRunId
  acquires quota and blocks

run B:
  another new previewRunId
```

Require:

```text
run B -> QUOTA_EXCEEDED
run A remains owner
after A is cancelled/completed -> quota released
run C with another new ID may acquire quota
```

Same-operation replay is not a quota competitor and must not use this expected
`QUOTA_EXCEEDED` behavior.

If `/usr/local/bin/redis-server` is unavailable, return this same task `blocked`.
Do not substitute an in-memory proof.

### A4-R3 — prove the synthetic conversation fixture is actually executed

Primary file:

```text
tests/external-preview.test.ts
```

The submitted suite now proves a foreign fixture is rejected before persistence, but
it still does not execute the successful conversation synthetic-fixture branch in
`PreviewService.execute(...)`.

Add this exact test:

```text
runs a frozen conversation external fixture without live provider or credential access
```

Create a valid preview bundle whose manifest/grant selects one exact external
`toolRevisionId`.

Configure:

```text
savedTools.load:
  returns that exact toolRevisionId
  returns a valid EXTERNAL_HTTP definition

ConversationBody.externalResponseFixtures:
  has exactly that toolRevisionId

externalFixtureRunner:
  asserts exact:
    toolRevisionId
    saved frozen definition
    frozen TransformSample
    arguments
  returns a valid CommerceToolResult
```

Set explicit traps/counters for the live path:

```text
PreviewToolExecutionPort.execute:
  throws "unexpected live tool execution"

provider HTTP:
  throws "unexpected provider HTTP"

credential resolution:
  throws "unexpected credential resolution"

credential decryption:
  throws "unexpected credential decryption"
```

Where provider/credential hooks are not direct PreviewService dependencies, expose
them through the injected externalFixtureRunner composition seam and assert their
counters explicitly. Do not claim zero calls merely because a test factory omits
them.

Execute:

```text
startConversation(...)
startRun(...)
read/wait for terminal run
```

Require:

```text
conversation stored only after saved definition validated
externalFixtureRunner called exactly once
normal PreviewToolExecutionPort.execute called 0
provider HTTP calls == 0
credential resolution calls == 0
credential decryption calls == 0
terminal run == COMPLETED
normal CommerceToolResult reaches the existing runner/final response path
```

Also add this exact adjacent rejection:

```text
rejects a selected non external conversation fixture before persistence
```

The toolRevisionId must be present in the frozen selected manifest, but
`savedTools.load(...)` returns a valid non-EXTERNAL_HTTP definition.

Require:

```text
INVALID_INPUT
conversation not persisted
externalFixtureRunner calls == 0
live tool executor calls == 0
```

Preserve the already-added foreign-ID rejection.

### A4-R4 — make the fail-closed evidence explicit

The current test:

```text
fails closed for unsupported media, raw HTML, and invalid processor output
```

may remain one test, but add explicit counters/assertions so each branch proves its
own side-effect boundary.

For unsupported media:

```text
INVALID_INPUT
publication validator calls == 0
processor calls == 0
```

For raw HTML incompatible with the saved response mode:

```text
INVALID_INPUT
no raw result fallback
```

For invalid processor output:

```text
INVALID_INPUT
no raw body/result fallback
```

Add one explicit oversize external sample/request case through the public
`runSample(...)` boundary if the focused suite does not already contain one.

Require rejection before processor execution when the canonical request/schema bound
can reject it.

Preserve the existing caller-definition override regression.

### A4-R5 — reconcile Work Items, Acceptance Criteria and Completion Report

Attempt 4 is in `review`, but its report claims PR02/PR03 evidence that the exact
submitted tests do not yet contain.

After A4-R1 through A4-R4 pass:

1. keep all four Work Items checked only if their exact behavior is now proven;
2. keep PR01 checked when the existing actual visual and JavaScript positive paths
   still pass;
3. keep PR02 checked only after the real-Redis replay/quota/cancel/expiry scenarios
   above pass;
4. keep PR03 checked only after successful synthetic conversation execution,
   foreign/non-external rejection, byte/media/size/output fail-closed behavior and
   explicit zero-live-dependency assertions pass;
5. update the Completion Report with exact test names rather than only aggregate
   counts;
6. record final implementation commit and parent report commit;
7. record launcher/worktree synchronization and both clean/pushed mirrored branches.

Before handoff set exactly:

```yaml
status: review
attempt: 5
executor: null
claimed_at: null
```

because the next authorized claim after this review creates Attempt 5 exactly once.

Do not edit this Architect Review.

### Required Validation

Run exactly:

```bash
npm run test:arch020-external-preview

npm run test:arch020-external-publication

npm run test:arch020-code-processor

npx vitest run \
  tests/preview-service.test.ts \
  tests/preview-store.test.ts \
  tests/preview-redis-lua.test.ts \
  tests/preview-routes.test.ts

npx eslint \
  src/commerce/external-preview \
  src/commerce/preview \
  tests/external-preview.test.ts \
  tests/preview-redis-lua.test.ts

npm run typecheck
npm run build

git diff --check
```

The report must identify the real-Redis and synthetic-conversation test names
explicitly. Aggregate counts alone are insufficient.

Repository typecheck/build may remain non-zero only for the materially unchanged
baseline and only when no diagnostic points at:

```text
src/commerce/external-preview/**
src/commerce/preview/**
tests/external-preview.test.ts
tests/preview-redis-lua.test.ts
```

### Reviewed Files

- `moda-interact-commerce/src/commerce/external-preview/service.ts`
- `moda-interact-commerce/src/commerce/external-preview/contracts.ts`
- `moda-interact-commerce/src/commerce/preview/service.ts`
- `moda-interact-commerce/src/commerce/preview/store.ts`
- `moda-interact-commerce/src/commerce/preview/redis-store.ts`
- `moda-interact-commerce/src/commerce/preview/types.ts`
- `moda-interact-commerce/tests/external-preview.test.ts`
- `moda-interact-commerce/tests/preview-redis-lua.test.ts`
- this task's Attempt-4 Completion Report

### Validation Reviewed

Submitted Attempt-4 evidence:

```text
external preview focused:       10 PASS
external publication adjacent: 11 PASS
code processor adjacent:        6 PASS
preview lifecycle adjacent:     PASS
focused ESLint:                 PASS
git diff --check:               PASS
repository typecheck/build:     unrelated existing baseline
```

Those results preserve the existing lifecycle work but do not satisfy the exact
Attempt-3 A3-R1 MIME correction, actual Redis PR02 Work Item or successful synthetic
conversation PR03 evidence.

### Architecture Conformance

Partial.

The external-preview architecture remains directionally correct. Remaining work is
one source-level MIME normalization correction and task-owned Redis/conversation
proof.

No downstream task may be promoted from this review.

### Follow-up

Return this same task to `ready`, preserve `attempt: 4`, clear the claim.

The next successful `/moda-task ARCH-020-COMMERCE-031` claim creates Attempt 5
exactly once.

Implement only A4-R1 through A4-R5, return to Review, push both mirrored branches and
STOP. Do not begin COMMERCE-024, COMMERCE-012 or any system-test task.

## Architect Review — Attempt 5 — 2026-09-22

### Review Status

Accepted

### Review Notes

Reviewed the exact Attempt 5 submission at implementation `abb02d9` and parent report
`5f334581` against the complete Attempt-4 A4-R1..A4-R5 correction contract.

Attempt 5 closes all remaining COMMERCE-031-owned functional and evidence gaps.

A4-R1 — MIME normalization — is resolved:

```ts
const sampleMime = sample.contentType
  .split(';', 1)[0]
  .trim()
  .toLowerCase();
```

The focused regression proves
`application/json; charset=utf-8` is accepted when the saved media allowlist contains
`application/json`.

A4-R2 — actual Redis PR02 proof — is resolved using the repository's existing local
`redis-server` + `ioredis` harness and real `RedisPreviewStateStore` instances.
The committed scenarios prove:

```text
same-operation replay across Redis-backed instances
  -> one validator call
  -> one processor call
  -> one business quota acquisition
  -> same terminal result
  -> no replay QUOTA_EXCEEDED

changed payload with same previewRunId
  -> ID_CONFLICT before second validator/processor/quota side effects

cross-instance cancel
  -> blocked processor AbortSignal aborted
  -> same run becomes CANCELLED
  -> later reads remain CANCELLED

RUNNING expiry
  -> same run becomes UNKNOWN
  -> stale owner cannot complete it

different new run IDs
  -> second new run is QUOTA_EXCEEDED while first owns slot
  -> quota releases after terminal cancellation
  -> later distinct run can acquire
```

A4-R3 — synthetic conversation execution — is resolved:

- the frozen conversation external definition is loaded server-side;
- the exact frozen fixture and definition are supplied to `externalFixtureRunner`;
- the normal live `PreviewToolExecutionPort` path is not used for the matching
  external fixture;
- the run reaches terminal `COMPLETED`;
- changed fixture content on the same frozen conversation identity conflicts;
- foreign fixture IDs and selected-but-non-EXTERNAL_HTTP fixture IDs are rejected
  before persistence.

Direct source inspection confirms the external preview/conversation services have no
provider HTTP or credential decrypt dependency of their own; the accepted synthetic
branch bypasses the normal live tool executor. The focused successful conversation
test also records zero live-executor use while exercising the synthetic runner.

A4-R4 fail-closed behavior remains present and is strengthened:

- unsupported media fails before validator/processor work;
- oversize sample is rejected at the public request boundary before processing;
- raw HTML incompatible with the saved response mode fails closed;
- invalid processor output fails closed without raw-result fallback;
- caller-supplied definition data is non-authoritative.

The Work Items and PR01-PR03 Acceptance Criteria are now checked consistently with
the committed evidence.

### Reviewed Files

- `moda-interact-commerce/src/commerce/external-preview/contracts.ts`
- `moda-interact-commerce/src/commerce/external-preview/service.ts`
- `moda-interact-commerce/src/commerce/preview/types.ts`
- `moda-interact-commerce/src/commerce/preview/store.ts`
- `moda-interact-commerce/src/commerce/preview/redis-store.ts`
- `moda-interact-commerce/src/commerce/preview/service.ts`
- `moda-interact-commerce/tests/external-preview.test.ts`
- `moda-interact-commerce/tests/preview-store.test.ts`
- `moda-interact-commerce/tests/preview-redis-lua.test.ts`
- this task's Attempt-5 Completion Report

### Validation Reviewed

Submitted Attempt-5 evidence:

```text
npm run test:arch020-external-preview
  PASS — 13 tests

npm run test:arch020-external-publication
  PASS — 11 tests

npm run test:arch020-code-processor
  PASS — 6 tests

preview lifecycle / Redis / route focused validation
  PASS — 43 tests
  includes 9 real Redis Lua tests

focused ESLint
  PASS

git diff --check
  PASS

repository typecheck/build
  non-zero only on 12 documented pre-existing repository diagnostics
  no Attempt-5-owned file is implicated
```

The uploaded archive does not include installed dependencies, so architect review does
not claim another dependency-backed execution. Acceptance is based on direct
inspection of the exact submitted source plus the durable focused validation evidence.

### Architecture Conformance

Conformant for COMMERCE-031.

Accepted invariants now include:

```text
server-owned saved external definition authority
frozen saved definition included in preview identity
claim/replay before business quota/receipt/processor side effects
same-operation replay with no duplicate side effects
same-ID changed payload conflict
same-ID cancellation and expiry state
real Redis-backed cross-instance replay/quota/cancel proof
normalized MIME comparison
bounded synthetic samples
COMMERCE-025/026 processor reuse
COMMERCE-030 receipt validator reuse
frozen conversation external definitions/fixtures
synthetic conversation fixture execution without live tool execution
foreign/non-external fixture rejection before persistence
fail-closed unsupported media/oversize/raw-output behavior
no publication/runtime validation bypass
```

### Follow-up

`ARCH-020-COMMERCE-031` is Complete at Attempt 5.

`ARCH-020-COMMERCE-024` is promoted from Pending to Ready because all of its declared
dependencies are now Complete.

Do not automatically launch COMMERCE-024.

`ARCH-020-COMMERCE-012` remains Pending behind its later integration/gateway
frontier. No system-test task is launched by this acceptance.
