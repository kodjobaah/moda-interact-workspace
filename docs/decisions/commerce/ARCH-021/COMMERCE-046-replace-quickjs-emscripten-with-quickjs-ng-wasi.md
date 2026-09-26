---
id: ARCH-021-COMMERCE-046
architecture_id: ARCH-021
title: Replace the Emscripten QuickJS adapter with QuickJS-NG/WASI
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 59
executor: copilot
claimed_at: 2026-09-26T14:34:02Z
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-017
  - ARCH-021-COMMERCE-040
  - ARCH-021-COMMERCE-041
enables: []
created: 2026-09-26
updated: 2026-09-26
---

# Replace the Emscripten QuickJS adapter with QuickJS-NG/WASI

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Replace the current `quickjs-emscripten` / `@jitl/quickjs-wasmfile-release-sync`
implementation behind the existing Commerce `SandboxKernel` with one packaged
`quickjs-wasi` / QuickJS-NG runtime that is loaded from explicit WASM bytes and
works identically from Vitest, packaged smoke tests, Next.js Server Actions and
production Node workers, while preserving the accepted request/response sandbox
contract, worker isolation, resource bounds and public `quickjs-sync.v1` Tool-definition
identifier.

## Context

Developer manual validation of the accepted External HTTP Request flow exposed a
runtime-only failure when `Validate request` compiles JavaScript through the real
Next.js Server Action:

```text
validateExternalRequestAction(...)
  -> ExternalAuthoringRuntimeError
  -> RUNTIME_UNAVAILABLE
```

The same repository currently proves both of these successfully:

```text
npm run test:arch020-code-runtime-proof
  -> existing SandboxKernel proof passes

npm run code-runtime:package
npm run code-runtime:smoke
  -> packaged worker/request/response proof passes
```

Additional bounded diagnostics isolated the application failure to QuickJS engine
initialisation inside the worker rather than authored JavaScript, connection metadata
or Tool validation:

```text
TypeError / ERR_INVALID_ARG_TYPE
  "path" argument ... Received an instance of URL

then, with an explicit Emscripten module loader:

MODULE_NOT_FOUND
  "Cannot find module as expression is too dynamic"
```

The current runtime has accumulated two different loader assumptions:

```text
Next / SandboxKernel path
  -> build/code-runtime/worker.mjs
  -> quickjs-emscripten variant
  -> runtime dynamic ESM import of emscripten-module.mjs

packaged smoke path
  -> build/code-runtime/worker.mjs
  -> explicit test-supplied wasmModulePath
```

The Next.js server bundling/runtime boundary is therefore participating in engine
module resolution even though authored JavaScript is intended to run in a standalone
Node worker.

`quickjs-wasi` provides a QuickJS-NG WASM runtime where the caller supplies the WASM
bytes directly. The target architecture removes Emscripten module-loader/dynamic-import
resolution from the sandbox entirely:

```text
Next Server Action
  -> SandboxKernel
  -> Node worker_threads Worker
  -> packaged build/code-runtime/worker.mjs
  -> read adjacent build/code-runtime/quickjs.wasm bytes
  -> QuickJS.create({ wasm, memoryLimit, interruptHandler })
  -> QuickJS-NG guest VM
```

This is an engine-adapter correction only. It does not redesign Tool definitions,
Request/Response authoring, bindings, response processing or production provider
execution.

## Scope

Primary files:

```text
moda-interact-commerce/package.json
moda-interact-commerce/package-lock.json
moda-interact-commerce/src/commerce/code-runtime/types.ts
moda-interact-commerce/src/commerce/code-runtime/kernel.ts
moda-interact-commerce/src/commerce/code-runtime/worker.mjs
moda-interact-commerce/scripts/code-runtime-manifest.mjs
moda-interact-commerce/scripts/code-runtime-packaged-smoke.mjs
moda-interact-commerce/tests/code-runtime-proof.test.ts
moda-interact-commerce/tests/code-request-processor.test.ts
moda-interact-commerce/tests/code-response-processor.test.ts
moda-interact-commerce/tests/external-tool-authoring-validation.test.ts
moda-interact-commerce/tests/external-tool-authoring-server-actions.test.ts
```

Update additional directly affected runtime fixtures/tests only where required by the
same bounded adapter migration.

## Out of Scope

- Changing the persisted Tool-definition runtime identifier `quickjs-sync.v1`.
- Changing the COMMERCE-040 JavaScript Request `bindings` contract.
- Changing `buildRequest({ args })` or `transform(response)` authoring signatures.
- Changing External HTTP Request/Response tab presentation.
- Changing COMMERCE-041 Request validation semantics or COMMERCE-042 UI behavior.
- Enabling production JavaScript External HTTP execution; the existing executor gate
  remains authoritative.
- Adding guest networking, filesystem access, environment access or arbitrary host
  callbacks.
- Loading `quickjs-wasi` native extensions such as URL, Crypto, Headers or Encoding.
- Adding a second sandbox implementation or retaining the old Emscripten adapter as a
  compatibility fallback.
- Database schema/migration work.
- Cross-repository contract changes.
- Phase 2 tab gating or live provider testing.
- Adding custom metrics/spans solely for this adapter migration.

## Requirements

### R1 — one pinned QuickJS-NG/WASI dependency

Replace the current direct runtime dependencies:

```text
quickjs-emscripten@0.31.0
@jitl/quickjs-wasmfile-release-sync@0.31.0
```

with exactly:

```text
quickjs-wasi@3.6.2
```

in `package.json` and the lockfile.

After migration, production source/scripts MUST NOT import or require:

```text
quickjs-emscripten
quickjs-emscripten-core
@jitl/quickjs-*
```

Do not install a native `qjs` executable and do not spawn a child process per guest
execution.

`quickjs-wasi` is the Node/TypeScript host adapter; QuickJS-NG remains the guest
engine behind its packaged `quickjs.wasm` artifact.

### R2 — preserve the logical Tool runtime contract

Keep:

```ts
RUNTIME_VERSION = 'quickjs-sync.v1'
```

and preserve the existing `SandboxKernel` API and `KernelResult` codes:

```text
SYNTAX_ERROR
EXECUTION_ERROR
INVALID_OUTPUT
RESOURCE_LIMIT
RUNTIME_UNAVAILABLE
DEADLINE
CANCELLED
THROTTLED
```

Do not require a Tool-definition migration merely because the implementation engine
adapter changes.

Request JavaScript continues to expose only:

```js
function buildRequest({ args }) { ... }
```

where `args` is the already-resolved COMMERCE-040 bounded binding record.

Response JavaScript continues to expose:

```js
function transform(response) { ... }
```

The adapter must not teach QuickJS about Tool schemas, connection credentials,
provider transport or Studio state.

### R3 — one packaged runtime artifact used by every execution path

`code-runtime:package` MUST produce exactly the runtime assets required by the new
adapter under:

```text
build/code-runtime/
  worker.mjs
  quickjs.wasm
  manifest.json
```

It MUST NOT package:

```text
emscripten-module.mjs
emscripten-module.wasm
```

Resolve `quickjs-wasi/quickjs.wasm` through the package export during packaging and
copy its bytes to `build/code-runtime/quickjs.wasm`.

The manifest must hash the actual packaged `quickjs.wasm` bytes and identify the
engine package deterministically, for example:

```json
{
  "runtimeVersion": "quickjs-sync.v1",
  "engine": "quickjs-ng-wasi",
  "enginePackageVersion": "quickjs-wasi@3.6.2",
  "artifactSha256": "..."
}
```

Keep the existing package-first development/build lifecycle:

```text
predev -> code-runtime:package
build  -> code-runtime:package -> code-runtime:smoke -> ...
```

Do not create a test-only engine loader. `SandboxKernel`, runtime proof tests,
packaged smoke and application Server Actions must all execute the same packaged
worker architecture.

### R4 — standalone worker loads explicit WASM bytes, not a module expression

`kernel.ts` must launch the packaged worker through an absolute filesystem path:

```text
<repo>/build/code-runtime/worker.mjs
```

The worker must statically import the host API from:

```ts
import { QuickJS } from 'quickjs-wasi';
```

and load the adjacent WASM bytes as ordinary filesystem data, equivalent to:

```ts
const wasm = await readFile(new URL('./quickjs.wasm', import.meta.url));
```

Then create the guest VM through the caller-supplied WASM boundary:

```ts
QuickJS.create({
  wasm,
  memoryLimit: RUNTIME_LIMITS.heapBytes,
  interruptHandler: ...,
});
```

Implementation may precompile the bytes to a `WebAssembly.Module` inside the worker if
that measurably simplifies/reduces repeated setup, but must not reintroduce dynamic
engine-module resolution.

The worker/runtime source MUST NOT use any engine-loading form equivalent to:

```text
import(pathExpression)
pathToFileURL(...dynamic engine module...)
newVariant(...)
importModuleLoader
RELEASE_SYNC
```

No Next.js/Turbopack/Webpack module loader may be responsible for resolving the
QuickJS engine artifact at guest-execution time.

### R5 — preserve compile-without-execution behavior

Use the `quickjs-wasi` compile API for compile operations rather than evaluating guest
source merely to detect syntax.

`SandboxKernel.compile(...)` must preserve the accepted property that syntax can be
checked without executing arbitrary top-level guest side effects.

At minimum prove for BOTH `request` and `response` modes:

```text
valid function declaration                 -> compile success
syntax error                               -> SYNTAX_ERROR
top-level throw + valid required function  -> compile success, throw not executed
missing required entry function            -> SYNTAX_ERROR
```

Do not broaden accepted authoring syntax beyond the current required named function
contract as part of this migration.

### R6 — preserve sandbox capability restrictions

The migrated VM must preserve the existing guest restrictions. Authored code must not
gain access to:

```text
fetch
XMLHttpRequest
require
process
WebAssembly
importScripts
host filesystem/network APIs
host environment variables
credentials
Node globals/modules
```

Preserve the current deterministic/sandbox hardening around:

```text
eval
Function
Date
Math.random
Proxy during output validation
prototype/accessor/custom-serialization rejection
bounded JSON output
max output depth
max array size
```

Do not register `quickjs-wasi` host callbacks or native extensions for this task.

The existing forbidden-capability and output-shape runtime proof must remain green.

### R7 — preserve worker isolation, cancellation and resource bounds

Retain Node `worker_threads` as the outer isolation/supervision boundary.

Preserve:

```text
maxConcurrentWorkers = 4
supervisor deadline = 2,000 ms
guest interrupt deadline = 500 ms
heap allocation limit = 16 MiB
source/input/body/output bounds from RUNTIME_LIMITS
hard Worker termination on completion/cancellation/deadline
capacity release only after worker termination
```

Use `quickjs-wasi@3.6.2` `memoryLimit` for the guest heap/retained-allocation bound and
`interruptHandler` for the guest execution deadline.

The current Emscripten-only claims:

```text
stackBytes = 512 KiB
wasmMemoryBytes = 64 MiB
```

must NOT remain in `RUNTIME_LIMITS` / manifest as purported enforced limits if the new
adapter cannot enforce those exact values. They currently have no external consumers.
If removed, replace their proof with runtime tests that demonstrate:

```text
excessive retained allocation -> RESOURCE_LIMIT (or bounded worker failure mapped to RESOURCE_LIMIT)
deep/pathological guest execution cannot crash the host process
worker is terminated and subsequent execution succeeds
```

Do not silently weaken resource safety while keeping misleading manifest fields.

### R8 — preserve request/response result semantics

Request execution must continue to accept only the bounded resolved binding object and
return one validated request descriptor:

```text
relative path
scalar query values
safe non-reserved headers
```

Response execution must continue to accept the existing bounded response input and
return one JSON object satisfying existing output validation.

Preserve exact request/response processor behavior and error mapping unless an engine
semantic difference is explicitly surfaced to `moda_architect` before proceeding.

No `RUNTIME_UNAVAILABLE` result may occur for a normal valid Request/Response solely
because the Next.js application is executing the kernel.

### R9 — shared structured logging is mandatory

Read and obey:

```text
docs/observability/shared-logging.md
```

All application/process logging introduced or retained by this migration MUST use:

```ts
@modainteract/moda-interact-shared/logging
```

through the existing shared `createLogger` API.

`kernel.ts` owns the runtime operational logger for:

```text
service.namespace = moda-interact
service.name      = moda-interact-commerce
deployment.environment.name = resolved service environment
```

The standalone worker MUST NOT create a competing generic logger and MUST NOT emit
free-form `console.error` diagnostics. For operational failures it may send one
bounded diagnostic event through `parentPort`; `kernel.ts` converts that event into a
shared structured log.

Remove temporary direct debugging such as:

```text
console.error('[code-runtime] launching worker', ...)
console.error('[code-runtime] worker diagnostic', ...)
console.error('[code-runtime] worker error', ...)
absolute worker/WASM filesystem paths
cwd
import.meta.url
```

Use stable semantic event names. Minimum required operational events are:

```text
commerce.code_runtime.worker_start_failed
commerce.code_runtime.initialization_failed
commerce.code_runtime.worker_failed
commerce.code_runtime.worker_exit_unexpected
```

Equivalent consolidation is acceptable only when the event name remains stable and
`stage` is a bounded enum.

Safe fields may include only bounded operational metadata such as:

```text
runtimeVersion
engine = quickjs-ng-wasi
stage
mode = request | response
operation = compile | run
errorName
errorCode
exitCode
```

MUST NOT log:

```text
guest JavaScript source
Tool arguments
request/response bodies
headers
credentials/tokens
customer data
complete provider payloads
absolute host filesystem paths
```

Expected guest authoring failures such as syntax errors and invalid output are normal
bounded results and MUST NOT be emitted as `error` operational logs merely because the
guest code is invalid.

Logging remains best-effort and MUST NOT change the returned `KernelResult`, worker
termination behavior, Server Action result or business correctness if the log sink
fails.

Preserve the existing higher-level `commerce.tool_authoring.action_failed` logging
boundary. This task may improve safe runtime-stage correlation underneath it, but must
not duplicate complete failure payloads in both layers.

### R10 — remove Emscripten-specific and temporary diagnostic code completely

After migration, repository source (excluding historical docs/task reports) must have
no production runtime dependency on:

```text
quickjs-emscripten
@jitl/quickjs-wasmfile-release-sync
newQuickJSWASMModuleFromVariant
newVariant
RELEASE_SYNC
importModuleLoader
emscripten-module.mjs
emscripten-module.wasm
```

Remove temporary migration/debug fields and dead branches rather than leaving a hidden
fallback.

There must be exactly one sandbox engine adapter in `src/commerce/code-runtime`.

## Work Items

- [ ] Pin `quickjs-wasi@3.6.2`; remove direct Emscripten QuickJS dependencies and update the lockfile.
- [ ] Change runtime packaging to `worker.mjs + quickjs.wasm + manifest.json`.
- [ ] Replace the worker Emscripten variant/module-loader implementation with the QuickJS-NG/WASI adapter.
- [ ] Preserve compile-without-execution semantics with the new compile API.
- [ ] Preserve Request and Response run semantics and KernelResult mapping.
- [ ] Preserve worker cancellation, deadlines, capacity and resource limits without false manifest claims.
- [ ] Replace all temporary/free-form runtime diagnostics with shared structured logging at the kernel boundary.
- [ ] Update packaged smoke to use the exact same engine-loading path as application execution.
- [ ] Update runtime/request/response/authoring tests for the new adapter without weakening assertions.
- [ ] Remove obsolete Emscripten packages/assets/code and run source audits.

## Interfaces / Contracts

Consumes and preserves:

```text
ARCH-021-COMMERCE-017
  SandboxKernel / request+response QuickJS runtime behavior

ARCH-021-COMMERCE-040
  resolved bounded JavaScript Request bindings

ARCH-021-COMMERCE-041
  Request validation/preview Server Action path that exposed the runtime defect

@modainteract/moda-interact-shared/logging
  canonical structured logging API
```

Logical runtime identifier remains:

```text
quickjs-sync.v1
```

New implementation dependency:

```text
quickjs-wasi@3.6.2
  -> QuickJS-NG WASM engine
```

No new cross-repository runtime contract is introduced.

## Dependencies

- ARCH-021-COMMERCE-017
- ARCH-021-COMMERCE-040
- ARCH-021-COMMERCE-041

All dependencies are Complete in the supplied 2026-09-26 workspace snapshot.

## Enables

None.

COMMERCE-042 and COMMERCE-043..045 remain independent manual-validation workstreams and
must not be made dependent on this task solely for scheduling convenience. This task
may execute in parallel with them.

## Acceptance Criteria

- [ ] `quickjs-wasi@3.6.2` is the sole direct QuickJS runtime dependency.
- [ ] Direct `quickjs-emscripten` / `@jitl/quickjs-*` runtime dependencies are removed.
- [ ] `RUNTIME_VERSION` remains `quickjs-sync.v1`.
- [ ] Packaged runtime contains `worker.mjs`, `quickjs.wasm`, `manifest.json` and no Emscripten module artifacts.
- [ ] Manifest SHA-256 is computed from the packaged QuickJS-NG/WASI `quickjs.wasm` bytes.
- [ ] Kernel, runtime proof and packaged smoke use the same packaged worker architecture.
- [ ] Worker reads explicit WASM bytes and does not dynamically import an engine module expression.
- [ ] Request compile checks syntax/entry contract without executing top-level guest effects.
- [ ] Response compile checks syntax/entry contract without executing top-level guest effects.
- [ ] Valid request JavaScript compiles and executes with exact expected descriptor output.
- [ ] Valid response JavaScript compiles and executes with exact expected transformed output.
- [ ] Existing syntax/execution/invalid-output/resource/deadline/cancellation/throttling KernelResult semantics remain proved.
- [ ] Infinite-loop cancellation/deadline and subsequent worker recovery remain proved.
- [ ] Guest memory exhaustion is bounded and the host remains usable afterward.
- [ ] Forbidden host capabilities remain inaccessible.
- [ ] COMMERCE-040 unbound Tool inputs remain absent from JavaScript `args`.
- [ ] Production JavaScript External HTTP executor gate remains disabled/unchanged.
- [ ] A normal valid JavaScript Request validation path no longer returns `RUNTIME_UNAVAILABLE` because of engine initialisation/module loading.
- [ ] All code-runtime operational logs use shared structured logging with stable semantic events.
- [ ] No runtime `console.*` debugging, guest source/input/body logging or absolute filesystem path logging remains.
- [ ] Shared-logger sink failure cannot change KernelResult/business behavior.
- [ ] No Emscripten fallback/second sandbox implementation remains.
- [ ] No database, Shared-contract, Tool-definition shape, Request/Response UI or provider-execution change is introduced.

## Validation

Run exactly from `moda-interact-commerce` after inspecting `package.json` for the declared scripts:

```bash
npm run code-runtime:package
npm run code-runtime:smoke
npm run test:arch020-code-runtime-proof
npm run test:arch021-code-request
npm run test:arch020-code-processor
npm run test:arch021-external-tool-authoring-validation
```

Add/extend focused tests so the packet explicitly covers:

```text
request compile without top-level execution
response compile without top-level execution
request exact run
response exact run
memory exhaustion / recovery
worker cancellation / recovery
concurrency/throttling
forbidden host capability rejection
packaged artifact execution
shared-log operational failure path without payload leakage
```

Then run:

```bash
npm run typecheck

npm exec eslint \
  src/commerce/code-runtime/types.ts \
  src/commerce/code-runtime/kernel.ts \
  src/commerce/tool-authoring/contracts.ts \
  src/studio/tools/external-validation-server-actions.ts \
  tests/code-runtime-proof.test.ts \
  tests/code-request-processor.test.ts \
  tests/code-response-processor.test.ts \
  tests/external-tool-authoring-validation.test.ts \
  tests/external-tool-authoring-server-actions.test.ts

git diff --check
```

Run the production build path:

```bash
npm run build
```

If repository-wide typecheck/build still exits non-zero only because of an established
unrelated baseline, record the exact diagnostics and prove there is no diagnostic or
Next/Webpack module-resolution failure in task-owned code. The build MUST NOT report
Emscripten/dynamic-import/QuickJS module-resolution failures.

Run these source audits:

```bash
! rg -n \
  'quickjs-emscripten|@jitl/quickjs|newQuickJSWASMModuleFromVariant|newVariant|RELEASE_SYNC|importModuleLoader|emscripten-module' \
  src scripts package.json

! rg -n \
  'console\\.(log|info|warn|error|debug)' \
  src/commerce/code-runtime

rg -n \
  '@modainteract/moda-interact-shared/logging' \
  src/commerce/code-runtime/kernel.ts
```

Inspect `build/code-runtime` and record the exact packaged artifact names and manifest
hash/version evidence.

## Stop Condition

After the QuickJS-NG/WASI adapter is the single runtime implementation, all required
runtime/request/response/authoring proofs pass, shared structured logging replaces the
temporary runtime diagnostics, Emscripten-specific source/dependencies/assets are gone,
and validation above is reconciled, set the task to `review`, complete the Completion
Report and STOP.

Do not continue into COMMERCE-042, COMMERCE-043/044/045, Test-tab provider execution or
another manual-validation finding.

## Implementation Notes

Keep the migration below the established processor contracts. Prefer changing the
runtime adapter and package pipeline over modifying callers.

`quickjs-wasi` requires caller-supplied WASM and exposes a compile API, memory limit and
interrupt handler. Use those capabilities directly rather than reconstructing an
Emscripten-like module loader.

The standalone worker is intentionally outside Next.js module transformation. Static
package imports in the copied worker are acceptable; runtime-computed engine-module
`import()` expressions are not.

Do not preserve obsolete `stackBytes` / `wasmMemoryBytes` fields merely to keep the old
manifest visually similar. A limit recorded in the manifest must correspond to an
actually enforced property of the new runtime.

## Completion Report

### Status
Not Started

### Files Changed
None

### Work Completed
None

### Validation Results
None

### Deviations
None

### Assumptions
None

### Unresolved Issues
None

### Architectural Concerns
None

## Architect Review

### Review Status
Pending

### Review Notes
None

### Reviewed Files
None

### Validation Reviewed
None

### Architecture Conformance
Pending

### Follow-up
None
