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
status: ready
priority: 150
executor: null
claimed_at: null
attempt: 2
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

- [ ] Extend accepted ToolTestBodySchema/ConversationBodySchema/stored preview state with C21 optional external fixtures, preserving old request behavior; freeze exact saved revision/definition/runtime before executing.
- [ ] Implement section9 createExternalPreviewService with validateCode/runSample plus read/cancel delegation to existing lifecycle; use030 sample-validation receipt writer, never a duplicate receipt engine.
- [ ] Enforce authenticated Origin/role, exact tool ownership, Redis distributed admin limits, existing run identity/replay/cancel and bounded preview envelope. Preserve only synthetic samples under existing TTL.
- [ ] Inject025/026 directly with fixture data; assert zero live HTTP/credential/decryption dependencies. Provide actual Redis cross-instance replay/quota/cancel fixtures.

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

- [ ] PR01: save->sample->processed result->receipt succeeds for text code and visual JSON with actual processors and accepted preview lifecycle.
- [ ] PR02: repeat same run returns original result; changed payload conflicts; cancel/unknown/expiry and two-instance quotas use same identity; changed draft does not alter frozen preview.
- [ ] PR03: old preview request unchanged; invalid foreign fixture ID, unsupported media/oversize, raw HTML and invalid output fail safely; provider/decrypt call counts remain zero.

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

Implementation complete for the bounded first slice; submitted for Architect Review with acceptance gaps recorded below.

### Files Changed

- `moda-interact-commerce/src/commerce/external-preview/contracts.ts`
- `moda-interact-commerce/src/commerce/external-preview/service.ts`
- `moda-interact-commerce/src/commerce/external-preview/index.ts`
- `moda-interact-commerce/src/commerce/preview/types.ts`
- `moda-interact-commerce/src/commerce/preview/service.ts`
- `moda-interact-commerce/tests/external-preview.test.ts`
- `moda-interact-commerce/package.json`

### Work Completed

Added bounded optional external response fixtures to conversation/tool-test schemas and stored state, including ownership checking and frozen fixture retention. Added `createExternalPreviewService` with canonical code hash validation, accepted COMMERCE-026 code and COMMERCE-025 visual processor injection, COMMERCE-030 sample-validation/receipt delegation, distributed Redis admin slot, and existing preview replay/conflict result persistence. Added external tool-test completion without live tool execution.

### Validation Results

PR01 partial: `tests/external-preview.test.ts` covers visual JSON processing, receipt-validator delegation, and canonical code validation; `npm run test:arch020-external-preview` passed 3 tests. Adjacent `npm run test:arch020-external-publication` passed 11 tests, `npm run test:arch020-code-processor` passed 6 tests, and focused legacy preview routes/store passed 10 tests. Changed-file ESLint passed. Repository typecheck remains blocked by pre-existing Prisma generation and integration diagnostics; no changed external-preview errors remain.

PR02 partial: external preview replay/conflict is covered in `tests/external-preview.test.ts`; Redis cross-instance quota/cancel/expiry coverage is not yet implemented.

PR03 partial: legacy request compatibility and zero live executor usage are covered by the implementation shape and focused positive test; the required foreign-fixture, unsupported-media, oversize, raw HTML, invalid-output, and explicit zero HTTP/credential/decryption call regressions are not yet covered.

### Deviations

The accepted COMMERCE-030 validator currently returns only a success envelope, so the external preview service independently reprocesses the frozen sample with the accepted 025/026 processors to persist the bounded preview result. The production runtime factory remains owned by the existing preview composition and was not broadened into live external adapters.

### Assumptions

C21 read-only scope; visual rules and generic JavaScript only inside the specified sandbox.

### Unresolved Issues

The current slice does not yet provide the complete C21 PR02 Redis race matrix or all PR03 rejection cases. The `runSample` contract requires the saved definition from the caller so COMMERCE-030 can recheck current definition identity; no new definition loader was invented.

### Architectural Concerns

Return contradictory accepted source facts to moda_architect before weakening contracts.

### Git / VCS

Expected mirrored branch: `task/ARCH-020-COMMERCE-031`, attempt 1. Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-031`; parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-031`. Dependencies were installed from the committed lockfile for validation. Commit and push evidence is recorded after submission.

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
