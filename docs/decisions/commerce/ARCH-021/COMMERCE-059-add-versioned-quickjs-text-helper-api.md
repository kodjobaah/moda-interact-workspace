---
id: ARCH-021-COMMERCE-059
architecture_id: ARCH-021
title: Add versioned QuickJS text helpers for JavaScript response authoring
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 73
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-021-COMMERCE-045
  - ARCH-021-COMMERCE-046
  - ARCH-021-COMMERCE-047
enables: []
created: 2026-09-27
updated: 2026-09-27
---

# Add versioned QuickJS text helpers for JavaScript response authoring

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Add one versioned, immutable Moda helper namespace to JavaScript **response** processing so authors can safely reuse an approved HTML-to-text helper as `moda.text.stripHtml(value)` without imports, `require`, DOM APIs or host callbacks. Package the helper implementation into the existing standalone QuickJS runtime at build time, preserve existing `quickjs-sync.v1` response definitions, make new JavaScript response authoring use `quickjs-sync.v2`, and expose concise helper documentation in both new-Tool and persisted-DRAFT Response authoring.

## Context

The accepted JavaScript Response contract deliberately runs inside a bounded QuickJS-NG/WASI guest with no package loader:

```text
transform(response)
  -> packaged Node worker
  -> QuickJS-NG guest
  -> bounded JSON object result
```

User-authored source cannot and must not gain:

```text
import
require
fetch
XMLHttpRequest
DOM
filesystem
Node process APIs
host callbacks
```

That isolation is correct, but it means common response-cleanup operations are currently reimplemented ad hoc in Tool source. HTML cleanup is the first concrete requirement.

The helper API must therefore be a **Moda-owned guest contract**, not direct access to an npm package:

```text
Tool source
  -> moda.text.stripHtml(value)
  -> immutable Moda wrapper
  -> build-time bundled string-strip-html implementation
```

The public Tool contract is `moda.text.stripHtml`, not `string-strip-html`. The package may be replaced in a later runtime version without changing authored Tool source for this runtime version.

The current accepted runtime is `quickjs-sync.v1`. Adding globals to that runtime would change its observable execution environment, so this task introduces **response runtime `quickjs-sync.v2`** instead of silently mutating v1.

Request JavaScript remains on `quickjs-sync.v1` and receives no helpers in this task.

## Scope

The task owns the complete bounded capability required to make the helper usable from Response JavaScript authoring:

```text
exact npm dependencies
  -> deterministic helper bundle
  -> packaged QuickJS runtime asset
  -> version-aware worker/kernel execution
  -> response-processing v1/v2 compatibility
  -> v2 default/upgrade authoring UX
  -> focused runtime + UI proof
```

Expected implementation surfaces include only files needed by that capability, principally:

```text
moda-interact-commerce/package.json
moda-interact-commerce/package-lock.json

moda-interact-commerce/src/commerce/code-runtime/
moda-interact-commerce/src/commerce/code-response/
moda-interact-commerce/src/commerce/tool-definition/contracts.ts
moda-interact-commerce/src/commerce/external-publication/

moda-interact-commerce/scripts/code-runtime-manifest.mjs
moda-interact-commerce/scripts/code-runtime-packaged-smoke.mjs

moda-interact-commerce/src/studio/external-http/
moda-interact-commerce/src/studio/tools/

moda-interact-commerce/tests/
```

A new source entry dedicated to the v2 guest helper bundle is expected under `src/commerce/code-runtime/` or a child directory.

## Out of Scope

- Arbitrary npm imports from Tool source.
- `require`, dynamic import or a guest package loader.
- Node/QuickJS host callbacks for helper execution.
- Exposing `string-strip-html` directly as the public API.
- User-configurable `string-strip-html` options in this task.
- DOM APIs or an HTML DOM/parser surface in the guest.
- Request-JavaScript helper availability; `buildRequest({ args })` remains `quickjs-sync.v1`.
- Additional helper methods such as entity decoding, Markdown conversion, CSV parsing or date libraries.
- Changing External HTTP provider/network behavior.
- Database, Prisma, Shared, Gateway or Background changes.
- Publication-policy redesign or live-test receipt redesign.
- Reworking the JavaScript editor component beyond the bounded helper/runtime affordance.

## Requirements

### R1 — pin the exact implementation dependencies

Install the helper implementation in `moda-interact-commerce` with exact versions:

```text
runtime dependency:
  string-strip-html@13.6.2

dev/build dependency:
  esbuild@0.28.2
```

The resulting `package.json` entries MUST be exact strings, not ranges:

```json
"string-strip-html": "13.6.2"
"esbuild": "0.28.2"
```

Update `package-lock.json` through npm; do not hand-edit lockfile package metadata.

Equivalent installation commands are:

```bash
npm install --save-exact string-strip-html@13.6.2
npm install --save-dev --save-exact esbuild@0.28.2
```

`string-strip-html` is an implementation dependency only. Tool source never imports it.

### R2 — introduce response runtime `quickjs-sync.v2` without mutating v1

The response-processing contract MUST support:

```text
quickjs-sync.v1
  existing accepted guest environment
  no `moda` helper namespace

quickjs-sync.v2
  same isolation/resource model
  immutable `moda.text.stripHtml`
```

Existing persisted/source-fixture v1 JavaScript response definitions remain valid and execute with v1 semantics.

New JavaScript **response** drafts use:

```text
quickjs-sync.v2
```

Request JavaScript remains exactly:

```text
quickjs-sync.v1
```

Do not broaden the Request contract to v2 merely because the worker is shared.

The implementation must have explicit response-runtime support checks rather than one global runtime constant whose value is assumed for every request and response execution.

### R3 — Commerce owns the v2 response runtime contract; Shared stays unchanged

Do NOT modify or publish `moda-interact-shared` for this capability.

Shared `ResponseProcessingSchema` still reflects the historical v1 cross-package contract and MUST NOT be expanded merely to carry this Commerce-local authoring/runtime capability.

Where the Commerce code-response processor currently relies on Shared's v1 `ResponseProcessingSchema` / `CodeResponseProcessorInput` solely to validate JavaScript response processing, replace that dependency with the corresponding Commerce-owned JavaScript-response contract needed to accept v1/v2 while continuing to reuse the existing Shared `TransformResponseSchema` boundary where appropriate.

No duplicate Visual-processing contract is introduced by this task.

### R4 — expose exactly one immutable helper API in v2

The v2 guest MUST expose exactly this new public helper contract:

```ts
moda.text.stripHtml(value: string): string
```

Semantics:

```text
input
  must be a JavaScript string

implementation
  string-strip-html@13.6.2
  call stripHtml(value) with package defaults

return
  the package result.result string only
```

For example, this authored source must work in v2:

```js
function transform(response) {
  return {
    value: moda.text.stripHtml(response.bodyText)
  };
}
```

The documented package example:

```text
Some text <b>and</b> text.
```

must produce:

```text
Some text and text.
```

Do not expose the package's complete result object, option surface or internal functions.

A non-string helper argument must fail inside the guest as a normal bounded JavaScript execution failure; do not coerce arbitrary objects with `String(...)`.

### R5 — helper namespace is immutable and cannot weaken the sandbox

Install the v2 namespace as non-writable/non-configurable and freeze every exposed layer:

```text
globalThis.moda
moda.text
moda.text.stripHtml
```

Authored source must not be able to replace or mutate the helper implementation for later calls in the same execution.

The v2 bootstrap MUST NOT re-enable or expose:

```text
fetch
XMLHttpRequest
require
process
WebAssembly
importScripts
eval
Function
Math.random
DOM
filesystem
network
```

No Node function is called back from the guest when `stripHtml` executes. The entire approved helper implementation executes as guest JavaScript under the existing QuickJS heap/stack/interrupt/supervisor/output limits.

### R6 — bundle the npm implementation at build/package time

`string-strip-html` is pure ESM and may have its own package dependencies. QuickJS does not resolve npm modules.

Use the pinned `esbuild@0.28.2` as a build-time bundler to emit one self-contained guest helper artifact:

```text
build/code-runtime/helpers-v2.js
```

The source helper entry may import `stripHtml` from `string-strip-html`; the **generated guest artifact must contain no unresolved imports or require calls**.

The bundle configuration is fixed for this task:

```text
bundle: true
platform: browser
format: iife
target: es2020
sourcemap: false
legalComments: none
```

Do not emit a source map.

The generated artifact must establish only the approved immutable `moda` public namespace; bundle-internal symbols must not intentionally become Tool-facing globals.

If `string-strip-html@13.6.2` cannot be bundled into code that executes correctly under the existing QuickJS-NG/WASI guest and limits, STOP and return the task Blocked to `moda_architect`. Do not solve that by introducing host callbacks, a Node-side transform, a second JavaScript engine or a different HTML package without an architecture change.

### R7 — package one deterministic runtime directory

After:

```bash
npm run code-runtime:package
```

`build/code-runtime/` MUST contain exactly:

```text
helpers-v2.js
manifest.json
quickjs.wasm
worker.mjs
```

The manifest must continue to identify/hash the packaged QuickJS WASM bytes and additionally record enough deterministic v2 helper evidence to audit the packaged runtime:

```text
supported response runtime versions:
  quickjs-sync.v1
  quickjs-sync.v2

default response runtime:
  quickjs-sync.v2

request runtime:
  quickjs-sync.v1

helper artifact:
  helpers-v2.js

helper artifact SHA-256:
  SHA-256 of exact packaged helpers-v2.js bytes

helper implementation package:
  string-strip-html@13.6.2

helper bundler:
  esbuild@0.28.2
```

Exact manifest key names may follow repository style, but all facts above are required and the smoke test must verify them against the actual packaged bytes/dependencies rather than hard-coded unrelated values.

### R8 — worker/kernel select the guest contract by runtime version

The requested response `runtimeVersion` must reach the sandbox kernel/worker explicitly.

For response execution:

```text
quickjs-sync.v1
  -> do not load/evaluate helpers-v2.js
  -> `typeof moda` remains "undefined"

quickjs-sync.v2
  -> read adjacent helpers-v2.js
  -> evaluate trusted helper bootstrap inside the new guest VM
  -> establish/freeze `moda`
  -> then compile/run authored transform(response)
```

For request execution:

```text
quickjs-sync.v1 only
```

A request for an unsupported runtime returns the existing bounded runtime-unavailable/invalid contract. Never silently fall back from v2 to v1.

Helper bootstrap evaluation failure is an operational runtime-initialization failure, not an authored syntax error. Preserve existing structured operational logging rules and do not log helper source, guest source, response bodies, credentials or host filesystem paths.

### R9 — compile and run use the same v2 environment

Response `compile(...)` for `quickjs-sync.v2` must validate the authored source against the same global environment used by v2 run execution.

Compilation must still be compile-only: top-level authored side effects are not executed merely to validate source.

The trusted helper bootstrap may initialise the guest before the compile check; authored source itself must retain the accepted COMMERCE-046 compile-only semantics.

### R10 — response processing/publication accepts both response runtime versions

Update Commerce-owned contracts/callers that currently hard-code response JavaScript to only `quickjs-sync.v1` so they intentionally support v1 and v2, including as applicable:

```text
Commerce Tool-definition parsing
authoring validation
code-response compile/process
live Test execution
external preview/publication compile path
publication receipt runtime allow-list
fixture/test definitions
```

Publication/test receipt identity continues to include `runtimeVersion`; a v1 receipt must not satisfy a v2 definition and vice versa.

Do not change `visual.v1` receipt semantics.

### R11 — new Response JavaScript authoring defaults to v2

Any newly-created Response JavaScript draft/default produced by Studio must use:

```text
runtimeVersion: quickjs-sync.v2
```

This applies whether JavaScript is the initial response mode or the author switches into JavaScript from another Response mode.

Do not silently mutate an existing persisted/local v1 JavaScript definition merely because the editor renders.

### R12 — provide an explicit local v1 -> v2 upgrade affordance

When the active JavaScript Response draft is v1, present a bounded authoring affordance equivalent to:

```text
Runtime: quickjs-sync.v1
Moda helpers are available in quickjs-sync.v2.
[Upgrade to v2 helpers]
```

Activating it MUST:

```text
preserve JavaScript source
preserve response format
preserve processed result schema
change only responseProcessing.runtimeVersion to quickjs-sync.v2
mark the local definition dirty
invalidate prior Response validation
perform no persistence by itself
```

There is no downgrade requirement in this task. Existing v1 definitions remain valid until the author chooses to upgrade.

### R13 — make the helper discoverable in both Response authoring compositions

For v2 JavaScript Response authoring, both new-Tool and persisted-DRAFT UI must show concise read-only help near the code editor:

```text
Available helper
moda.text.stripHtml(value)
Strips HTML tags and returns plain text.
```

Provide the exact illustrative snippet:

```js
function transform(response) {
  return {
    value: moda.text.stripHtml(response.bodyText)
  };
}
```

This help is documentation only. It must not execute code, import a package or create a second editor.

Do not advertise the helper as available while a v1 Response definition remains active.

### R14 — preserve all accepted resource and isolation limits

The helper executes inside the existing accepted bounds, including:

```text
source <= 16 KiB UTF-8
response JSON <= 2 MiB
response body <= 256 KiB UTF-8
result <= 48 KiB
guest heap <= 16 MiB
QuickJS stack <= 512 KiB
guest interrupt <= 500 ms
supervisor <= 2000 ms
max array items 20
max output depth 20
max concurrent workers 4
```

Do not add a helper-specific host execution path to bypass these bounds.

If the bundled helper cannot operate within them for the focused test corpus, return Blocked rather than silently increasing limits in this task.

## Work Items

- [ ] Install exact `string-strip-html@13.6.2` and `esbuild@0.28.2` in their required dependency classes and update the lockfile through npm.
- [ ] Add the Commerce-owned v2 response runtime contract while retaining v1 response support and v1-only request JavaScript.
- [ ] Add one guest helper-entry source exposing only `moda.text.stripHtml(value)`.
- [ ] Bundle that helper source deterministically to `build/code-runtime/helpers-v2.js` during `code-runtime:package`.
- [ ] Extend the packaged runtime manifest with supported/default/request runtime identity and helper artifact/package/hash evidence.
- [ ] Make kernel/worker compile and run response source under the selected v1/v2 environment with no fallback.
- [ ] Preserve all accepted sandbox globals restrictions, worker isolation and resource limits.
- [ ] Decouple Commerce v2 response processing from Shared's v1-only response-processing validator/type without modifying Shared.
- [ ] Update response validation/live execution/publication/receipt code paths that legitimately consume response JavaScript runtime identity.
- [ ] Default new Response JavaScript drafts to v2.
- [ ] Add a non-persisting explicit v1 -> v2 upgrade affordance for existing Response JavaScript drafts.
- [ ] Add v2 helper documentation/example to both new-Tool and persisted-DRAFT JavaScript Response authoring.
- [ ] Add focused runtime, packaging, processor, publication and UI regressions.
- [ ] Update `moda-interact-commerce/docs/code-runtime-proof.md` to describe v1/v2 response behavior, v1 request behavior and packaged helper proof.

## Interfaces / Contracts

### Public authored guest API

`quickjs-sync.v2` JavaScript Response source receives:

```ts
declare const moda: {
  readonly text: {
    readonly stripHtml: (value: string) => string;
  };
};
```

No other `moda` methods are introduced by this task.

### Runtime-version matrix

```text
                              quickjs-sync.v1    quickjs-sync.v2
Response transform                  yes                 yes
moda.text.stripHtml                  no                  yes
Request buildRequest                 yes                  no
imports / require                    no                   no
host callbacks                       no                   no
```

### Package ownership

```text
string-strip-html@13.6.2
  installed in moda-interact-commerce dependencies
  build-time bundled into guest artifact
  never imported by authored Tool source

esbuild@0.28.2
  installed in moda-interact-commerce devDependencies
  used only to produce the self-contained guest helper artifact
```

### Shared boundary

`moda-interact-shared` remains pinned/unchanged. No Shared publication is part of this task.

## Dependencies

- `ARCH-021-COMMERCE-045` — accepted JavaScript Response authoring surface.
- `ARCH-021-COMMERCE-046` — accepted packaged QuickJS-NG/WASI runtime.
- `ARCH-021-COMMERCE-047` — accepted bounded QuickJS compiler-diagnostic boundary.

All are Complete, so this task is Ready independently of the live-Test, provider-diagnostic and Agent-contract follow-up workstreams.

## Enables

None.

Future helper additions must be separately architected. Do not add unrelated helpers opportunistically merely because the helper namespace now exists.

## Acceptance Criteria

- [ ] `package.json` pins exactly `string-strip-html: "13.6.2"` and dev dependency `esbuild: "0.28.2"`; lockfile is npm-generated and consistent.
- [ ] Response JavaScript accepts both `quickjs-sync.v1` and `quickjs-sync.v2`; Request JavaScript remains v1-only.
- [ ] A valid existing v1 Response definition still compiles and runs with `typeof moda === "undefined"`.
- [ ] A v2 Response transform can call `moda.text.stripHtml(response.bodyText)` successfully.
- [ ] `moda.text.stripHtml("Some text <b>and</b> text.")` returns exactly `Some text and text.`.
- [ ] Passing a non-string to `moda.text.stripHtml` produces a bounded guest execution failure rather than coercion or a host exception.
- [ ] `globalThis.moda`, `moda.text` and the helper cannot be replaced/configured by authored source in a way that changes helper behavior.
- [ ] v2 still has no `fetch`, `XMLHttpRequest`, `require`, `process`, `WebAssembly`, `importScripts`, `eval`, `Function`, DOM or host-callback capability.
- [ ] `code-runtime:package` emits exactly `helpers-v2.js`, `manifest.json`, `quickjs.wasm`, `worker.mjs`.
- [ ] `helpers-v2.js` has no unresolved `import`/`require` and no source map is emitted.
- [ ] Manifest helper SHA-256 equals the SHA-256 of the actual packaged `helpers-v2.js` bytes.
- [ ] Manifest/package evidence identifies `string-strip-html@13.6.2` and `esbuild@0.28.2` and the required v1/v2 runtime matrix.
- [ ] Packaged smoke proves v1 response behavior, v2 helper behavior, request v1 behavior and compile-only behavior through the exact packaged worker.
- [ ] Unsupported runtime versions fail closed with the existing bounded invalid/runtime-unavailable semantics; there is no v2 -> v1 fallback.
- [ ] Response Tool-definition/authoring/live-test/publication paths consume v2 where applicable without modifying Shared contracts.
- [ ] Publication/Test receipt identity distinguishes v1 and v2 and retains `visual.v1` behavior.
- [ ] New JavaScript Response authoring defaults to v2.
- [ ] Existing v1 authoring is not silently upgraded on render.
- [ ] Explicit v1 -> v2 upgrade preserves source/format/result schema, marks the local draft dirty and invalidates prior Response validation without persistence.
- [ ] New-Tool and persisted-DRAFT v2 Response editors show the exact helper name, one-sentence purpose and example without introducing another editing surface.
- [ ] No runtime/resource limit is increased and helper execution remains inside the existing guest/supervisor bounds.
- [ ] No new generic logger, host callback, filesystem/network guest capability, database change or Shared change is introduced.

## Validation

Run from `moda-interact-commerce` after inspecting the declared scripts:

- [ ] `npm run code-runtime:package`
- [ ] `npm run code-runtime:smoke`
- [ ] `npm run test:arch020-code-runtime-proof`
- [ ] `npm run test:arch020-code-processor`
- [ ] `npm run test:arch020-external-tools-ui`
- [ ] focused publication/authoring validation covering v1/v2 response runtime identity and receipt separation
- [ ] focused tests proving immutable helper namespace, v1 absence, v2 availability, non-string failure and sandbox restrictions
- [ ] source audit: packaged `helpers-v2.js` contains no unresolved module import/require and no source map exists
- [ ] source audit: Request Tool contract still accepts only `quickjs-sync.v1`
- [ ] targeted ESLint for task-owned changed source/tests/scripts
- [ ] repository typecheck; record any known unrelated baseline diagnostics and prove zero diagnostics in task-owned changed files
- [ ] `node --check src/commerce/code-runtime/worker.mjs`
- [ ] `git diff --check`

Do not treat a missing unrelated repository script as proof that the underlying capability failed; follow the repository's actual declared scripts and the durable development-baseline rules.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not add more helper libraries or begin unrelated JavaScript-authoring improvements.

## Implementation Notes

The intended packaging/execution boundary is:

```text
npm dependency graph
  string-strip-html@13.6.2
           |
           v
src/commerce/code-runtime/<v2 helper entry>
           |
           | esbuild@0.28.2 at code-runtime:package
           v
build/code-runtime/helpers-v2.js
           |
           v
worker creates QuickJS VM
           |
           +-- v1 response: skip helper bootstrap
           |
           +-- v2 response: evaluate trusted helper bootstrap
                              -> freeze moda.text.stripHtml
                              -> compile/run authored transform(response)
```

Do not bundle the helper into author-authored source and do not concatenate package source into each Tool definition.

The helper bundle is trusted application runtime code, not Tool source. It may initialise before authored source, but authored compile validation must remain non-executing as required by COMMERCE-046.

If exact local names differ, preserve the contracts above rather than inventing another runtime/helper model.

## Completion Report

### Status

Not Started

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation review.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Pending.

### Follow-up

None.
