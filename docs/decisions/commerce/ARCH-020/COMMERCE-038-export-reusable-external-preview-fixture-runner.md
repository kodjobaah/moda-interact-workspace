---
id: ARCH-020-COMMERCE-038
architecture_id: ARCH-020
title: Export reusable external preview fixture runner
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 168
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-020-COMMERCE-025
  - ARCH-020-COMMERCE-026
  - ARCH-020-COMMERCE-030
  - ARCH-020-COMMERCE-031
  - ARCH-020-SHARED-002
enables:
  - ARCH-020-COMMERCE-024
created: 2026-09-22
updated: 2026-09-22
---

# Export reusable external preview fixture runner

## Architecture

ARCH-020 C21 sections 2.3, 6, 7 and 9.5.

This correction is created from COMMERCE-024 Attempt-1 architectural review.
COMMERCE-031 correctly owns external preview processing/replay behavior, while
COMMERCE-024 is composition-only and must not duplicate that processing in a
production factory.

## Objective

Export one reusable synthetic external-response fixture runner from the accepted
COMMERCE-031 producer so production Conversation preview can inject it into
`PreviewService` without copying visual/JavaScript processing, schema validation or
rendering logic.

## Context

Accepted COMMERCE-031 provides:

```text
createExternalPreviewService(...)
PreviewService externalFixtureRunner injection hook
server-owned saved definitions
visual/code processor integration
sample media/result validation
```

But its accepted public export does not include a production
`PreviewExternalFixtureRunner`. COMMERCE-024 therefore cannot compose the
Conversation synthetic external fixture path without recreating COMMERCE-031 logic.

This task supplies that missing producer seam only.

## Scope

Only:

```text
src/commerce/external-preview/contracts.ts
src/commerce/external-preview/service.ts
src/commerce/external-preview/index.ts
one new external-preview fixture-runner module when useful
tests/external-preview.test.ts
package.json only if the existing focused command requires no usable target
```

No production integration/factory wiring outside `external-preview/**`.

## Out of Scope

No `integration/external/**`, `lib/preview/runtime.ts`, routes, Studio UI, database,
credentials, HTTP transport, Redis receipt implementation, preview state store,
publication lifecycle, gateway, deployment or system-test work.

Do not add provider HTTP or credential dependencies.

## Requirements

### R1 — export one reusable runner

Export:

```ts
createExternalFixtureRunner(...)
```

or an equivalent architecturally identical symbol from:

```text
src/commerce/external-preview/index.ts
```

The returned value must satisfy the accepted:

```ts
PreviewExternalFixtureRunner
```

contract.

Its input authority is exactly:

```text
principal
toolRevisionId
server-frozen CommerceToolDefinition
server-frozen TransformSample
arguments
AbortSignal
```

It does not load another definition and does not accept browser-authored replacement
definition state.

### R2 — share one processing kernel with runSample

Refactor the accepted COMMERCE-031 sample-processing branch so:

```text
ExternalPreviewService.runSample(...)
and
createExternalFixtureRunner(...)
```

reuse one internal processing implementation for:

```text
MIME normalization
JSON/TEXT handling
resultPath selection
visual processor delegation
JavaScript processor delegation
cancellation
resultSchema validation
ExternalHttpResultData construction
responseTemplate rendering
CommerceToolResult validation
```

Do not maintain two structurally similar processing algorithms.

`runSample(...)` still owns:

```text
previewRunId replay/conflict
external preview quota
COMMERCE-030 validateSampleAndRecord receipt
PreviewResult persistence
```

The reusable fixture runner owns NONE of those.

### R3 — no receipt/quota/live dependency side effects

`createExternalFixtureRunner(...)` must make:

```text
Redis preview quota calls             0
publication receipt reads/writes      0
provider HTTP calls                   0
credential resolution calls           0
credential decryption calls            0
preview run/state writes               0
```

It only processes the supplied frozen synthetic sample.

### R4 — canonical bounded processing

For an EXTERNAL_HTTP definition:

```text
normalize sample MIME by stripping parameters
require saved response-format allowlist match
```

Visual mode:

```text
saved responseFormat.mode must be JSON
parse bounded JSON
apply saved resultPath
call accepted COMMERCE-025 visual processor
```

JavaScript mode:

```text
JSON mode -> parse sample JSON for TransformResponse.json
TEXT mode -> json = null
call accepted COMMERCE-026 code processor
```

Both modes then:

```text
validate output against saved resultSchema with compileSubset(..., "details")
construct ExternalHttpResultData with:
  source = EXTERNAL_HTTP
  saved connectionRevisionId
  bounded observedAt from injected clock
  validated values
render using accepted renderDefinitionResult(...)
parse final value with CommerceToolResultSchema
```

No raw-body/result fallback is permitted.

Cancellation must remain the accepted AbortSignal behavior. A cancelled processor
must not return a successful CommerceToolResult.

### R5 — deterministic tests

Extend:

```text
tests/external-preview.test.ts
```

with these exact scenarios:

```text
reuses the same visual fixture processor for tool-test and conversation execution

reuses the same JavaScript fixture processor for tool-test and conversation execution

normalizes parameterized MIME in the reusable fixture runner

rejects fixture output that fails the saved result schema without raw fallback

aborts the reusable fixture runner without quota receipt provider or credential work
```

For visual and JavaScript positive paths:

```text
run fixture directly through createExternalFixtureRunner
run same frozen definition/sample through ExternalPreviewService.runSample
assert identical validated values/rendered semantics
assert actual accepted processor used
```

Use explicit trap counters and prove:

```text
receipt write only occurs in runSample path
receipt write == 0 in direct fixture-runner path
provider HTTP == 0
credential resolution == 0
credential decryption == 0
```

No arbitrary broad test count is required.

## Work Items

- [x] Extract/share the accepted external fixture processing kernel.
- [x] Export a reusable `PreviewExternalFixtureRunner`.
- [x] Preserve existing COMMERCE-031 runSample replay/quota/receipt behavior.
- [x] Add focused visual/JavaScript/MIME/schema/cancel regressions.

## Interfaces / Contracts

Consumes:

```text
ARCH-020-COMMERCE-025 visual processor
ARCH-020-COMMERCE-026 code processor
ARCH-020-COMMERCE-030 publication validator (runSample only)
ARCH-020-COMMERCE-031 external preview lifecycle
ARCH-020-SHARED-002 external definition/sample/result schemas
```

Produces:

```text
createExternalFixtureRunner(...) -> PreviewExternalFixtureRunner
```

Consumer:

```text
ARCH-020-COMMERCE-024
```

## Dependencies

- ARCH-020-COMMERCE-025
- ARCH-020-COMMERCE-026
- ARCH-020-COMMERCE-030
- ARCH-020-COMMERCE-031
- ARCH-020-SHARED-002

## Enables

- ARCH-020-COMMERCE-024

## Acceptance Criteria

- [x] One exported reusable runner satisfies `PreviewExternalFixtureRunner`.
- [x] Tool-test and conversation synthetic processing share one implementation.
- [x] Visual and JavaScript fixtures produce canonical schema-validated/rendered results.
- [x] Parameterized MIME is normalized identically to accepted C21 behavior.
- [x] Invalid schema/output fails closed without raw fallback.
- [x] Direct runner has zero quota/receipt/provider/credential/state side effects.
- [x] Existing COMMERCE-031 replay/cancel/quota/receipt regressions remain passing.
- [x] No production integration or UI source is modified.

## Validation

Run exactly:

```bash
npm run test:arch020-external-preview
npm run test:arch020-external-publication
npm run test:arch020-code-processor

npx eslint \
  src/commerce/external-preview \
  tests/external-preview.test.ts

npm run typecheck
npm run build
git diff --check
```

Repository-wide typecheck/build may retain only the unchanged documented baseline,
with no diagnostic in task-owned files.

## Stop Condition

After the bounded producer export and focused evidence pass:

```text
update Work Items / Acceptance Criteria / Validation
write exact Completion Report
set status: review
clear executor/claimed_at
push implementation task branch
push parent task branch
return to moda_architect
STOP
```

Do not begin COMMERCE-024.

## Implementation Notes

This is a producer-seam correction, not final composition.

Do not create a production preview singleton, route or factory in this task.
COMMERCE-024 owns final production assembly after this producer is accepted.

## Completion Report

### Status

Ready for Review

### Files Changed

`src/commerce/external-preview/contracts.ts`, `src/commerce/external-preview/fixture-runner.ts`, `src/commerce/external-preview/service.ts`, `src/commerce/external-preview/index.ts`, and `tests/external-preview.test.ts`.

### Work Completed

Extracted the canonical synthetic EXTERNAL_HTTP processing kernel and exported `createExternalFixtureRunner` through the external-preview composition boundary. The runner accepts only the authenticated principal, revision ID, frozen definition, frozen sample, arguments, and signal; it performs bounded MIME normalization, visual/JavaScript processing, result-schema validation, result construction, response-template rendering, and final CommerceToolResult validation. `runSample` retains saved-definition loading, replay/conflict handling, quota, publication receipt validation, cancellation, and legacy preview result shape while routing processing through the shared kernel. Direct runner tests prove no quota, receipt, provider, or credential work.

### Validation Results

`npm run test:arch020-external-preview`: PASS, 18 tests.
`npm run test:arch020-external-publication`: PASS, 11 tests.
`npm run test:arch020-code-processor`: PASS, 6 tests.
`npx eslint src/commerce/external-preview tests/external-preview.test.ts`: PASS.
`git diff --check`: PASS.
`npm run typecheck`: baseline failure with 12 diagnostics in unchanged `components/studio-workspace.tsx`, `src/commerce/connections/command-kernel.ts`, `src/commerce/connections/lifecycle/index.ts`, `src/commerce/integration/backend/executors.ts`, and `tests/code-response-processor.test.ts`; no task-owned diagnostics.
`npm run build`: compilation completed, then failed on the same unchanged baseline type diagnostics; no task-owned diagnostics.

### Deviations

The repository-wide typecheck/build baseline remains unresolved outside this task. Node 24.21.0 was used because it was available; the package declares 24.19.0.

### Assumptions

No live credentials, provider calls, deployments, WhatsApp operations, or merchant calls were used. COMMERCE-024 production composition remains out of scope and is not implemented here.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Created by `moda_architect` from COMMERCE-024 Attempt-1 review.

### Reviewed Files

Not applicable.

### Validation Reviewed

Not applicable.

### Architecture Conformance

Pending implementation.

### Follow-up

After acceptance, architect must re-evaluate COMMERCE-024 together with the accepted
COMMERCE-019 source-integration prerequisite. No automatic launch.

## Architect Review — Attempt 1 — 2026-09-22

### Review Status

Accepted

### Review Notes

Reviewed the exact Attempt-1 implementation identified by the handoff as
`16972af` and parent report `f107b817` against the complete COMMERCE-038 producer
contract created from COMMERCE-024 Attempt-1 review.

The missing producer seam is now implemented without moving final production
composition out of COMMERCE-024.

The accepted export is:

```text
src/commerce/external-preview/index.ts
  createExternalFixtureRunner(...)
```

and the returned value satisfies the existing `PreviewExternalFixtureRunner`
contract.

The reusable runner's input authority is limited to the already-authenticated /
server-frozen preview inputs:

```text
principal
toolRevisionId
CommerceToolDefinition
TransformSample
arguments
AbortSignal
```

It does not load a replacement definition and it has no browser-authored definition
authority.

The implementation also resolves the core ownership requirement from this task:
`ExternalPreviewService.runSample(...)` now invokes the same
`createExternalFixtureRunner(...)` processing path rather than maintaining a second
visual/JavaScript processing algorithm.

The shared runner owns exactly the bounded synthetic processing boundary:

```text
canonical CommerceToolDefinition / TransformSample parsing
EXTERNAL_HTTP requirement
parameterized MIME normalization
saved media allowlist
JSON/TEXT handling
resultPath selection
accepted COMMERCE-025 visual processor
accepted COMMERCE-026 code processor
AbortSignal cancellation
saved resultSchema validation
ExternalHttpResultData construction
accepted response-template rendering
CommerceToolResult validation
```

The reusable runner does not own:

```text
preview replay/conflict
external preview quota
COMMERCE-030 receipt reads/writes
provider HTTP
credential resolution/decryption
preview run/state persistence
production route/factory composition
```

Those boundaries remain with their accepted owners.

The positive visual and JavaScript regressions exercise both:

```text
direct createExternalFixtureRunner(...)
and
ExternalPreviewService.runSample(...)
```

with the same saved definition/sample processing behavior. Parameterized MIME,
schema-fail-closed and cancellation paths are also covered.

Direct source inspection is stronger than the fixture-only zero-side-effect counters:
`ExternalFixtureRunnerDependencies` contains only the accepted code processor, visual
processor and optional clock. It has no Redis, publication validator, provider,
credential or preview-state dependency to call.

No production integration, route, UI, database, credential, provider-HTTP,
publication-lifecycle or preview-store source is modified by this task.

### Reviewed Files

- `moda-interact-commerce/src/commerce/external-preview/contracts.ts`
- `moda-interact-commerce/src/commerce/external-preview/fixture-runner.ts`
- `moda-interact-commerce/src/commerce/external-preview/service.ts`
- `moda-interact-commerce/src/commerce/external-preview/index.ts`
- `moda-interact-commerce/tests/external-preview.test.ts`
- `moda-interact-commerce/package.json`
- COMMERCE-038 task definition
- C21 sections 2.3, 6, 7 and 9.5

### Validation Reviewed

Submitted evidence:

```text
npm run test:arch020-external-preview
  PASS — 18 tests

npm run test:arch020-external-publication
  PASS — 11 tests

npm run test:arch020-code-processor
  PASS — 6 tests

npx eslint src/commerce/external-preview tests/external-preview.test.ts
  PASS

git diff --check
  PASS

npm run typecheck
npm run build
  non-zero only on the unchanged documented repository baseline;
  no COMMERCE-038-owned diagnostic is reported
```

The handoff also records both mirrored branches pushed, clean and claim-cleared.

The review archive does not include installed repository dependencies, so architect
review does not claim another dependency-backed execution. Acceptance is based on
direct inspection of the exact submitted source plus the durable focused validation
evidence.

### Architecture Conformance

Conformant.

Accepted producer boundary:

```text
COMMERCE-031
  createExternalPreviewService(...)
  createExternalFixtureRunner(...)
        |
        +-- tool-test runSample uses shared fixture-processing kernel
        |
        +-- COMMERCE-024 may inject same runner into production Conversation PreviewService
```

The reusable runner is processing-only. Replay/quota/receipt/state and live provider /
credential concerns remain outside it.

### Follow-up

`ARCH-020-COMMERCE-038` is Complete at Attempt 1.

This acceptance satisfies the missing producer-seam blocker identified in
COMMERCE-024 Attempt 1, but **does not yet make COMMERCE-024 Ready**.

The exact submitted implementation base still lacks the accepted COMMERCE-019
production preview source:

```text
src/commerce/integration/preview/adapters.ts
  absent

lib/preview/runtime.ts
  still contains unavailableLoader
```

Therefore COMMERCE-024 remains blocked on the separate developer integration
condition recorded in its Attempt-1 Architect Review:

```text
integrate accepted COMMERCE-019 implementation 8850b55
into the canonical moda-interact-commerce implementation base
```

After that integration is complete, provide a fresh synchronized COMMERCE-024
snapshot. `moda_architect` should verify the accepted COMMERCE-019 source markers and
then transition the authoritative COMMERCE-024 task from Blocked to Ready while
preserving Attempt 1. The next launcher claim then creates Attempt 2 exactly once.

Do not automatically launch COMMERCE-024, COMMERCE-012 or any system-test task.
