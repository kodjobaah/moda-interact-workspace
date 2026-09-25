---
id: ARCH-021-COMMERCE-017
architecture_id: ARCH-021
title: Implement bounded external request JavaScript processor
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 35
executor: null
claimed_at: null
attempt: 3
depends_on:
  - ARCH-021-COMMERCE-016
  - ARCH-020-COMMERCE-029
  - ARCH-020-COMMERCE-026
enables:
  - ARCH-021-COMMERCE-023
created: 2026-09-23
updated: 2026-09-25
---

# Implement bounded external request JavaScript processor

## Architecture

Architecture ID: ARCH-021

Architecture document: `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator: moda_architect

## Objective

Extend the proven QuickJS runtime with a second bounded entrypoint, `buildRequest({ args })`, that converts already input-schema-validated CommerceAgent arguments into the canonical Commerce-owned `ExternalRequestDescriptor` without performing network or credential operations.

## Context

ARCH-020 proved and packaged the QuickJS response transformer `transform(response)`. Phase 3 must reuse that exact isolation/runtime rather than introducing another JS engine or allowing `fetch()` from authored code.

The 2026-09-24 simplification checkpoint is implementation-complete. Its terminal system test remains Ready by developer choice and is not an implementation dependency. This task is restored to Ready because its source dependencies are Complete and its technical contract is unaffected by the simplification.

## Scope

Refactor the accepted runtime into one generic sandbox kernel while preserving the response processor. Use these target locations:

```text
src/commerce/code-runtime/types.ts
src/commerce/code-runtime/kernel.ts
src/commerce/code-runtime/worker.mjs
src/commerce/code-response/processor.ts
src/commerce/code-request/processor.ts
scripts/code-runtime-manifest.mjs
scripts/code-runtime-packaged-smoke.mjs
tests/code-response-processor.test.ts
tests/code-request-processor.test.ts
package.json
```

The previous `src/commerce/code-response/runtime/*` implementation is moved/replaced by `src/commerce/code-runtime/*`; do not leave two independent sandbox implementations.

## Out of Scope

- HTTP/network execution.
- Connection/credential lookup.
- Shopify GraphQL.
- Studio editor UI.
- Publication policy.

## Requirements

### R1 — exact source entrypoint

Request source is a normal script defining:

```js
function buildRequest({ args }) {
  return {
    path: '/catalogue/search',
    query: { q: args.query },
    headers: { accept: 'application/json' }
  };
}
```

`export default`, ESM imports and async functions are not part of the contract.

Response source remains exactly the existing:

```js
function transform(response) { ... }
```

### R2 — generic worker modes

The single worker MUST support:

```text
compile-response
run-response
compile-request
run-request
memory-probe
```

or an equivalent enum carrying exactly the same distinction. There must be one runtime-limit manifest and one worker implementation.

### R3 — request input

Before invoking QuickJS, `createCodeRequestProcessor().process(...)` MUST:

1. reject aborted/deadline inputs;
2. validate `processing` through the COMMERCE-016 canonical Commerce contract;
3. validate `args` by JSON serialization as a plain bounded object (no functions, prototypes, accessors, symbols, BigInt, non-finite numbers or prototype-pollution keys);
4. bound serialized input to 128 KiB;
5. pass only `{ args }` into the guest.

No environment, shop/session, connection, secret, URL/origin, history or model state enters the guest.

### R4 — request output

The guest return value MUST be parsed with the COMMERCE-016 `ExternalRequestDescriptorSchema`. Any extra/unsafe field therefore fails.

Return exactly `CodeRequestProcessorResult`.

### R5 — sandbox invariants

Preserve the accepted runtime limits and disable at minimum:

```text
eval
Function
Date
fetch
XMLHttpRequest
require
process
importScripts
WebAssembly
Math.random
```

Keep current heap/stack/WASM/guest/supervisor/concurrency limits. No increase is authorized.

### R6 — compiler

`compile({ source, runtimeVersion, ... })` for request JavaScript MUST prove both syntax and existence of a callable `buildRequest` entrypoint. A script containing valid syntax but no `buildRequest` is `SYNTAX_ERROR`/invalid for authoring purposes.

### R7 — packaged runtime proof

Update the existing package/smoke scripts so the packaged worker proves both:

```text
transform(response)
buildRequest({ args })
```

using the same packaged WASM artifact/hash and memory ceiling.

### R8 — focused test cases

`test:arch021-code-request` MUST prove:

- deterministic successful descriptor;
- unknown extra output field rejected;
- absolute URL/origin/method/body rejected by the canonical Commerce descriptor;
- reserved header rejected;
- network/global access unavailable;
- non-finite/prototype/accessor output rejected;
- oversized input/output rejected;
- deadline/cancellation/throttling mapped correctly;
- no `buildRequest` fails compile;
- existing response processor regressions still pass.

## Work Items

- [x] Extract one generic QuickJS runtime.
- [x] Add request compile/run mode and processor.
- [x] Validate request output through the canonical Commerce schema.
- [x] Update packaged runtime proof.
- [x] Add focused request regressions.

## Interfaces / Contracts

Consumes COMMERCE-016 `ExternalRequestConstruction`, `ExternalRequestDescriptor` and local Tool-definition contracts.

Produces a server-only processor consumed by COMMERCE-023. The External HTTP UI reaches request preview through the COMMERCE-023 server validation/preview boundary.

## Dependencies

- ARCH-021-COMMERCE-016
- ARCH-020-COMMERCE-029
- ARCH-020-COMMERCE-026

## Enables

- ARCH-021-COMMERCE-023

## Acceptance Criteria

- [x] One QuickJS sandbox implementation serves response and request code.
- [x] Request code cannot perform I/O or receive secrets/context.
- [x] Only canonical Commerce-valid request descriptors escape the sandbox.
- [x] Existing response code behavior/package proof remains intact.

## Validation

- [x] `npm run test:arch021-code-request` (5/5)
- [x] `npm run test:arch020-code-processor` (6/6)
- [x] `npm run test:arch020-code-runtime-proof` (10/10)
- [x] `npm run code-runtime:package`
- [x] `npm run code-runtime:smoke` (packaged transform/request/memory proof passed)
- [x] targeted lint/typecheck (lint: 0 errors, 4 existing warnings; no task-owned type diagnostics)
- [x] `git diff --check`

## Stop Condition

Set task to `review`, return Completion Report and STOP. Do not wire this processor to live external HTTP.

## Implementation Notes

No second worker implementation is permitted. Preserve the current packaged-runtime contract and safety ceilings.

## Completion Report

### Status
Ready for architect review.
### Files Changed
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-017`
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-017`
- Generic runtime: `src/commerce/code-runtime/{types.ts,kernel.ts,worker.mjs}`; removed the previous response-only runtime.
- Request processor: `src/commerce/code-request/processor.ts` and focused tests.
- Response adapter, packaging manifest/smoke proof, package script, and local request contract type exports.
### Work Completed
- Extracted one mode-aware QuickJS sandbox supporting response/request compile and run modes plus packaged memory probing, preserving the existing limits and host-capability restrictions.
- Added bounded `buildRequest({ args })` processing with canonical Commerce `ExternalRequestConstructionSchema` and `ExternalRequestDescriptorSchema` validation, strict JSON-safe argument admission, cancellation/deadline/throttling mapping, and no HTTP/credential/context wiring.
- Updated the packaged worker proof to execute both `transform(response)` and `buildRequest({ args })` using the same WASM artifact and ceiling.
### Validation Results
- Launcher claim: attempt 1, executor `copilot`, claim commit `6b51809407cb6514821a34ffa15c2c3344c20504`, pushed successfully, claimed `2026-09-24T08:04:15Z`.
- Start synchronization: parent `remote_task_branch_fast_forwarded: not-needed`, `origin_main_incorporated: already-current`, head `658a90db39c07c0c79cca61a65d6792059d00d6b`; implementation `remote_task_branch_fast_forwarded: not-needed`, `origin_main_incorporated: already-current`, head `63d06822385984fc060f21fdb924203f8e71a61f`.
- Recursive submodule sync/update passed; database submodule commit `98fdf715e54fe6df92ac6951facd104e410068f2`.
- Implementation commit pushed: `23bcecc`.
- Focused request, response, runtime-proof, packaging, smoke, lint, and whitespace validation passed as recorded above.
- Full typecheck exits nonzero on unrelated baseline diagnostics; no diagnostics were reported in `src/commerce/code-request`, `src/commerce/code-runtime`, `src/commerce/code-response/processor.ts`, or the focused runtime tests.
### Deviations
- Full repository typecheck remains baseline-non-clean and was not broadened into unrelated remediation. Lint reported four existing warnings and zero errors.
### Assumptions
None
### Unresolved Issues
None
### Architectural Concerns
None

## Architect Review

### Review Status
Changes Requested — Attempt 2

### Review Notes

#### Attempt 2 review — 2026-09-25

Reviewed implementation `87bca07` and the submitted Attempt 2 Completion Report
against the full COMMERCE-017 task contract.

The runtime implementation is architecturally conformant and must be preserved:

- one generic `src/commerce/code-runtime/*` QuickJS sandbox serves request and
  response compile/run modes plus memory probing;
- the previous response-only runtime is removed rather than duplicated;
- request processing validates canonical COMMERCE-016
  `ExternalRequestConstructionSchema` input;
- guest input is limited to JSON-safe `{ args }` with the 128 KiB request ceiling;
- only `ExternalRequestDescriptorSchema`-valid output escapes;
- request compilation proves a callable `buildRequest` entrypoint;
- the sandbox disables the required host/global capabilities and preserves the
  accepted heap/stack/WASM/guest/supervisor/concurrency ceilings;
- package/smoke proof uses the same packaged worker/WASM artifact for response,
  request and memory-ceiling proof;
- the exact release-sync QuickJS WASM dependency is declared;
- there is no live HTTP, credential, Shopify GraphQL, Studio UI or publication
  wiring in this task;
- submitted `tsconfig.tsbuildinfo` contains zero semantic diagnostics in the
  COMMERCE-017 runtime/request/response/script/focused-test surfaces.

Attempt 2 is not accepted because R8 explicitly requires
`test:arch021-code-request` itself to prove several request-output safety cases that
the current 5-test file does not execute. The generic runtime implementation appears
to enforce them, but the mandatory request-focused proof is incomplete.

The following is the complete Attempt 3 correction contract. Do not redesign the
runtime or begin COMMERCE-023.

##### A2-R1 — add the missing request-output safety proofs

Change:

```text
tests/code-request-processor.test.ts
```

Do not change runtime source unless one of these regressions fails and demonstrates
an implementation defect.

Add active request-processor regressions proving all of the following through
`createCodeRequestProcessor().process(...)`:

```text
1. non-finite output is rejected
2. custom/non-plain prototype output is rejected
3. accessor output is rejected
4. serialized output larger than the 48 KiB runtime output ceiling is rejected
```

Use actual QuickJS execution, not a mocked kernel, for these four cases.

Minimum deterministic examples:

```js
// non-finite
function buildRequest({ args }) {
  return { path: '/x', query: { value: NaN }, headers: {} };
}

// prototype
function buildRequest({ args }) {
  const value = Object.create(null);
  value.path = '/x';
  value.query = {};
  value.headers = {};
  return value;
}

// accessor
function buildRequest({ args }) {
  const query = {};
  Object.defineProperty(query, 'q', {
    enumerable: true,
    get() { return 'x'; }
  });
  return { path: '/x', query, headers: {} };
}

// oversized output
function buildRequest({ args }) {
  return {
    path: '/x',
    query: { q: 'x'.repeat(50000) },
    headers: {}
  };
}
```

Each case must return:

```ts
{
  ok: false,
  code: 'INVALID_REQUEST',
  diagnostic: { code: 'INVALID_OUTPUT' }
}
```

or an exact equivalent with the same externally observable error contract.

Do not weaken the worker validator or descriptor schema merely to make the tests
pass.

##### A2-R2 — complete the required host/global unavailability proof

In the existing request-focused host-capability test, explicitly prove all minimum
R5 globals are unavailable:

```text
eval
Function
Date
fetch
XMLHttpRequest
require
process
importScripts
WebAssembly
Math.random
```

Where `typeof <global>` is safe, assert the guest observes `undefined`.
For `Math.random`, preserve the existing proof that it cannot yield a usable request
descriptor.

This is proof-only unless a listed global is unexpectedly available.

##### A2-R3 — preserve the existing required request proofs

Do not remove or weaken the existing request-focused coverage for:

```text
deterministic successful descriptor
nested-array input
unknown/unsafe descriptor fields
absolute URL/origin/method/body rejection
reserved header rejection
oversized input
prototype-pollution input
missing buildRequest compile failure
non-callable buildRequest compile failure
pre-cancelled request
deadline mapping
throttling mapping
```

The response processor and generic runtime proof must continue to pass unchanged.

##### A2-R4 — deterministic validation

Run exactly:

```bash
npm run test:arch021-code-request
npm run test:arch020-code-processor
npm run test:arch020-code-runtime-proof
npm run code-runtime:package
npm run code-runtime:smoke
npm run lint
npm run typecheck
git diff --check
```

`npm run test:arch021-code-request` must execute the new non-finite, prototype,
accessor and oversized-output cases; do not satisfy this contract only through the
response/generic runtime test files.

The request, response and runtime-proof suites must have zero skipped tests.

Full typecheck may retain only diagnostics demonstrably unrelated to:

```text
src/commerce/code-request/**
src/commerce/code-runtime/**
src/commerce/code-response/processor.ts
scripts/code-runtime-manifest.mjs
scripts/code-runtime-packaged-smoke.mjs
tests/code-request-processor.test.ts
tests/code-response-processor.test.ts
tests/code-runtime-proof.test.ts
```

Any diagnostic in those surfaces is task-owned and must be corrected before review.

##### A2-R5 — Attempt 3 execution/report evidence

The Attempt 3 Completion Report must record exact launcher-provided:

```text
parent worktree path
implementation worktree path
parent branch = task/ARCH-021-COMMERCE-017
implementation branch = task/ARCH-021-COMMERCE-017
start-of-attempt parent synchronization
start-of-attempt implementation synchronization
Attempt 3 claim evidence / commit
recursive submodule materialization
database submodule commit
implementation commit
parent report commit
push parity
clean parent worktree
clean implementation worktree
```

Do not reuse Attempt 2 claim/synchronization values.

Before handoff set exactly:

```yaml
status: review
attempt: 3
executor: null
claimed_at: null
```

##### Attempt 3 stop condition

Return to architect review only when:

```text
all four missing request-output cases execute and pass
AND all minimum R5 globals are explicitly proved unavailable
AND existing request/response/runtime proofs remain green
AND package/smoke proof remains green
AND no task-owned type diagnostic exists
AND Attempt 3 launcher/report evidence is complete
```

Then push both task branches, return control to `moda_architect`, and STOP.

Do not start `ARCH-021-COMMERCE-023`.

### Reviewed Files

- `src/commerce/code-runtime/types.ts`
- `src/commerce/code-runtime/kernel.ts`
- `src/commerce/code-runtime/worker.mjs`
- `src/commerce/code-request/processor.ts`
- `src/commerce/code-response/processor.ts`
- `scripts/code-runtime-manifest.mjs`
- `scripts/code-runtime-packaged-smoke.mjs`
- `tests/code-request-processor.test.ts`
- `tests/code-response-processor.test.ts`
- `tests/code-runtime-proof.test.ts`
- `package.json`
- submitted `tsconfig.tsbuildinfo`
- Attempt 2 Completion Report

### Validation Reviewed

Submitted evidence:

```text
request tests: 5/5 PASS
response tests: 6/6 PASS
runtime proof: 10/10 PASS
code-runtime:package PASS
code-runtime:smoke PASS
lint PASS
git diff --check PASS
full typecheck non-zero on unrelated baseline files only
```

Independent inspection of the submitted TypeScript build artifact finds no semantic
diagnostic in the COMMERCE-017-owned runtime/request/response/scripts/focused-test
surfaces.

The missing R8 proof is specific: the request suite currently does not execute
non-finite output, custom-prototype output, accessor output or >48 KiB output cases.

### Architecture Conformance

Runtime architecture conforms. Acceptance is deferred only because mandatory
request-focused safety proof is incomplete. No architecture redesign is requested.

### Follow-up

Return this same task through `/moda-task ARCH-021-COMMERCE-017` for Attempt 3.
`ARCH-021-COMMERCE-023` remains Pending because COMMERCE-017 is not yet Complete and
COMMERCE-019 is also not Complete. Do not start downstream work.

## Developer Override - Reopened

### Previous Status
review

### Previous Attempt
1

### Decision
The developer requested that this task be reopened for another implementation and review cycle. Preserve the existing implementation, completion report, validation evidence and Architect Review history; do not increment the attempt or claim the task as part of this transition.

### Result
The task is ready for the next authorized execution workflow. Execution mode, completion mode, executor and claim state remain unchanged.

## Attempt 2 Completion Report

### Status
Ready for architect review.

### Correction Checklist
- [x] Preserve one generic QuickJS worker and explicit response/request modes; the packaged response proof now invokes `run-response`.
- [x] Prove the request entrypoint is callable during request compilation, not only syntactically present.
- [x] Admit bounded JSON-safe request arguments including nested arrays while retaining prototype, accessor, symbol, non-finite number and pollution-key rejection.
- [x] Declare the exact QuickJS release-sync WASM package required by the worker so local and packaged execution resolve the same runtime artifact.

### Files Changed
- `package.json`
- `scripts/code-runtime-packaged-smoke.mjs`
- `src/commerce/code-request/processor.ts`
- `src/commerce/code-runtime/worker.mjs`
- `tests/code-request-processor.test.ts`

### Validation Results
- `npm run test:arch021-code-request`: passed, 5/5 tests.
- `npm run test:arch020-code-processor`: passed, 6/6 tests.
- `npm run test:arch020-code-runtime-proof`: passed, 10/10 tests.
- `npm run code-runtime:package`: passed; runtime `quickjs-sync.v1`, artifact SHA-256 `0c031dd404df00f2d1ed9491a6590d014e88a50424996e5fd70feff1c931c045`, WASM ceiling `67108864` bytes.
- `npm run code-runtime:smoke`: passed for packaged response transform, request descriptor, and memory ceiling proof using the same artifact/hash.
- `npm run lint`: passed with 0 errors and 6 existing warnings; no task-owned warning was introduced.
- `npm run typecheck`: remains nonzero on known unrelated baseline Prisma/Studio/test diagnostics; no diagnostics were reported for the task-owned runtime, request processor, response adapter, scripts, or focused tests.
- `git diff --check`: passed.

### Git Evidence
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-017`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-017`.
- Implementation branch: `task/ARCH-021-COMMERCE-017`; commit `87bca07`, pushed to `origin/task/ARCH-021-COMMERCE-017`.
- Launcher claim commit: `5a2eae5d5ba7a0a026f61f79baa03d425264947c`, pushed.
- Parent synchronization: remote task branch fast-forward not needed; current `origin/main` incorporated before execution; parent head after claim `cbe7cef2fb11a51a94ce722b79709dd2ff8b4da2`.
- Implementation synchronization: remote task branch fast-forward not needed; current `origin/main` incorporated before execution; prepared implementation head `c33c3633ed733dd5df5745fc3ef363344f25963e`.
- Recursive database submodule sync/update passed at commit `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.

### Deviations and Unresolved Issues
- Full typecheck remains baseline-non-clean as documented above; no unrelated remediation was attempted.
- No network, credential, Shopify GraphQL, Studio UI, publication policy, live HTTP wiring, or downstream ARCH-021-COMMERCE-023 work was added.
- None unresolved.

## Attempt 3 Completion Report

### Status
Ready for architect review.

### Correction Checklist
- [x] A2-R1: Added active request-processor QuickJS regressions for non-finite output, null-prototype output, accessor output, and output larger than the 48 KiB ceiling; all assert `INVALID_REQUEST` with `INVALID_OUTPUT` diagnostics.
- [x] A2-R2: Explicitly proved `eval`, `Function`, `Date`, `fetch`, `XMLHttpRequest`, `require`, `process`, `importScripts`, and `WebAssembly` are unavailable to request code; preserved the existing `Math.random` unusable-descriptor proof and literal `XMLHttpRequest` source rejection proof.
- [x] A2-R3: Preserved deterministic descriptor, nested-array input, unsafe descriptor fields, absolute URL/origin/method/body, reserved header, oversized input, prototype-pollution input, compile-entrypoint, cancellation, deadline and throttling coverage; response and generic runtime proofs remained green.
- [x] A2-R4: Ran every required validation command with zero skipped focused tests and no task-owned type diagnostics.
- [x] A2-R5: Recorded fresh Attempt 3 launcher, worktree, synchronization, submodule, commit and push evidence below.

### Files Changed
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-017`
- Implementation file: `tests/code-request-processor.test.ts`
- Parent report: this task file only.

### Correction-to-Test Mapping
- A2-R1: `tests/code-request-processor.test.ts`, `rejects unsafe request output values through the processor`.
- A2-R2: `tests/code-request-processor.test.ts`, `does not expose network or host capabilities`.
- A2-R3: Existing request test cases were retained; no runtime source was changed.

### Validation Results
- `npm run test:arch021-code-request`: passed, 6/6 tests, 0 skipped; includes all four new output-safety cases.
- `npm run test:arch020-code-processor`: passed, 6/6 tests, 0 skipped.
- `npm run test:arch020-code-runtime-proof`: passed, 10/10 tests, 0 skipped.
- `npm run code-runtime:package`: passed; runtime `quickjs-sync.v1`, artifact SHA-256 `0c031dd404df00f2d1ed9491a6590d014e88a50424996e5fd70feff1c931c045`, WASM ceiling `67108864` bytes.
- `npm run code-runtime:smoke`: passed for packaged response transform, request proof and memory ceiling using the same artifact/hash.
- `npm run lint`: passed with 0 errors and 6 existing warnings; no task-owned lint error was introduced.
- `npm run typecheck`: nonzero on the known unrelated baseline; the captured log had 268 TypeScript diagnostics and zero matches in the task-owned request/runtime/response/script/focused-test surfaces.
- `git diff --check`: passed.
- Focused editor diagnostics for `tests/code-request-processor.test.ts`: no errors.

### Attempt 3 Launcher and VCS Evidence
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-017`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-017`.
- Parent branch: `task/ARCH-021-COMMERCE-017`.
- Implementation branch: `task/ARCH-021-COMMERCE-017`.
- Start-of-attempt parent synchronization: remote task branch fast-forward `not-needed`; `origin/main` incorporation `already-current`; parent head after claim `ed46249bd1f122afca3eb3eeb5a9b429dfb5628d`.
- Start-of-attempt implementation synchronization: remote task branch fast-forward `not-needed`; `origin/main` incorporation `already-current`; implementation head before correction `87bca07d55d259b8c75cf06d978ff5912969c91d`.
- Attempt 3 claim: parent claim commit `f4678f237558fc0718e602d4a6ce4864aea7ffce`, pushed; claimed at `2026-09-25T12:02:40Z`.
- Recursive submodule materialization: sync/update passed; database submodule commit `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.
- Implementation commit: `06416de14bdb91d3de5c4af1c9547e6b81738c4d`, pushed to `origin/task/ARCH-021-COMMERCE-017`; local and remote implementation hashes match.
- Parent report commit: `d0217724`, pushed to `origin/task/ARCH-021-COMMERCE-017`.
- Push parity: implementation task branch is published; parent report branch will be published with this report commit.
- Worktree state before parent report update: implementation worktree clean; parent worktree clean before this report edit.

### Deviations and Unresolved Issues
- Full typecheck remains baseline-non-clean with only unrelated diagnostics; no unrelated remediation was attempted.
- The `XMLHttpRequest` runtime proof uses computed global access because the canonical Commerce-016 source validator intentionally rejects the literal identifier; the existing literal-source rejection test remains unchanged.
- No network, credentials, Shopify GraphQL, Studio UI, publication policy, live HTTP wiring, or downstream ARCH-021-COMMERCE-023 work was added.
- None unresolved.
