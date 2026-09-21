---
id: ARCH-020-COMMERCE-029
architecture_id: ARCH-020
title: Prove and package bounded code runtime
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
  - ARCH-020-COMMERCE-001
enables:
  - ARCH-020-COMMERCE-026
  - ARCH-020-COMMERCE-012
  - ARCH-020-GATEWAY-003
created: 2026-09-21
updated: 2026-09-21
---

# Prove and package bounded code runtime

## Architecture

ARCH-020. Binding specification: [C21 external API tools](../../../architecture/ARCH-020-external-api-tools.md).
Read C21 in full and existing [contracts](../../../architecture/ARCH-020-implementation-contracts.md)
C7/C14/C20 where extended. C21 resolves this task's exact fields, interfaces,
limits, errors, ownership and acceptance IDs. No model-selected replacement design.

## Objective

Own src/commerce/code-response/runtime/**, runtime artifact/build manifest and minimal direct runtime tests. Deliver a reusable bounded QuickJS worker kernel, not a paper evaluation or throwaway prototype. No Shared schemas, business validation, UI or production factory wiring.

## Context

The user approved read-only non-Shopify APIs, visual response filtering and sandboxed response code. Existing
Shopify/policy execution and Background MCP protocol remain supported. Future
external tool definitions require publication, not another Background handler.
This is new scope, not a correction to an accepted task.

## Scope

Own src/commerce/code-response/runtime/**, runtime artifact/build manifest and minimal direct runtime tests. Deliver a reusable bounded QuickJS worker kernel, not a paper evaluation or throwaway prototype. No Shared schemas, business validation, UI or production factory wiring.

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

- [x] Build/pin the synchronous QuickJS WASM variant with enforceable finite memory maximum and worker entry; record dependency/artifact hashes and supported runtime profile quickjs-sync.v1.
- [x] Implement the section9 SandboxKernel compile/run entry points and bounded JSON-text result. Prove C21 memory/time/abort/concurrency constraints with real execution.
- [x] Run positive text transform, infinite-loop, built-in long operation, allocation/serialization attack, forbidden capability and post-failure recovery scenarios before architecture acceptance.
- [x] Publish docs/code-runtime-proof.md with actual limits/results and artifact loading in the repository production build; if a required limit is not enforceable report that concrete gap and do not mark Complete or weaken it.

## Interfaces / Contracts

C21 sections1–8 retain data/behavior requirements. [Section9](../../../architecture/ARCH-020-external-api-tools.md#9-tightened-implementation-boundaries-and-evidence) is authoritative for the narrowed ownership, factory signatures, scenario IDs and handoff rules. Consume accepted exports; no consumer may repair a missing producer by weakening the contract. Record actual dependency commits and published package versions.

## Dependencies

- ARCH-020-COMMERCE-001

## Enables

- ARCH-020-COMMERCE-026
- ARCH-020-COMMERCE-012
- ARCH-020-GATEWAY-003

## Acceptance Criteria

- [x] SB01: actual pinned worker/WASM executes synthetic transform and produces exact output; production build can load bundled artifact without network download.
- [x] SB02: heap/stack/WASM maximum and supervisor termination are demonstrated, including infinite loop and memory pressure; process remains usable afterward.
- [x] SB03: no guest network/filesystem/environment/module loader; distinct concurrent inputs remain isolated; fifth run throttles; slots/handles reclaimed on every terminal path.

## Validation

Ready for Review.

Use focused checks while implementing, then existing typecheck/build/lint where defined. Record unrun developer-owned PostgreSQL/container checks accurately; executable scenarios must still exist. No repeated unrelated full suites or screenshot quotas. No live credentials/WhatsApp delivery.

`moda-interact-commerce/src/commerce/code-response/runtime/types.ts`
`moda-interact-commerce/src/commerce/code-response/runtime/kernel.ts`
`moda-interact-commerce/src/commerce/code-response/runtime/worker.mjs`
`moda-interact-commerce/tests/code-runtime-proof.test.ts`
`moda-interact-commerce/scripts/code-runtime-manifest.mjs`
`moda-interact-commerce/docs/code-runtime-proof.md`
`moda-interact-commerce/package.json` and `package-lock.json`

Submit implementation and parent report through normal mirrored task branches,
then stop at Review for moda_architect. Never self-accept, launch downstream tasks,
Added `quickjs-emscripten@0.31.0` with the synchronous release WASM profile `quickjs-sync.v1`.
Added fresh-worker `SandboxKernel` compile/run entry points with 16 MiB QuickJS heap, 512 KiB stack, 64 MiB WASM linear-memory maximum, 500 ms guest interrupt, 2,000 ms supervisor/turn deadline, 64/16 MiB worker V8 limits, four active workers with no queue, cancellation, and `finally` capacity cleanup.
Disabled guest module loading, network/filesystem/environment/timer/credential host surfaces and deterministic clock/random access; validated object-only JSON output with depth, array, prototype/accessor, cycle-compatible serialization, and 48 KiB bounds.
Added deterministic fixtures for valid text transformation, syntax failure, infinite loop and recovery, allocation/output pressure, forbidden capability, deadline, cancellation, concurrent tenant-input isolation, and fifth-run throttling.
Added artifact manifest/hash command and proof documentation with actual runtime limits and requirement-to-fixture matrix.
Shared's package publication is required only for SHARED-002 as explicitly scoped.
SYSTEM-TEST-002 requires explicit developer invocation even when Ready.

Agent-executed:

- `npm run test:arch020-code-runtime-proof` -> PASS, 1 file and 6 tests.
- `npm run lint` -> PASS.
- `npm run build` -> PASS; Prisma client generation and Next.js webpack production build completed successfully.
- `npm run code-runtime:manifest` -> PASS; `quickjs-emscripten@0.31.0`, `@jitl/quickjs-wasmfile-release-sync@0.31.0`, SHA-256 `0c031dd404df00f2d1ed9491a6590d014e88a50424996e5fd70feff1c931c045`, configured WASM maximum `67108864` bytes.
- `git diff --check` -> PASS.
- Historical Attempt 1 `npm run typecheck` -> FAIL only in pre-existing unrelated Prisma client typing surfaces: `lib/auth/development-platform-admin.ts` (four `Prisma.Sql`/`Prisma.sql` errors) and `lib/server/connections.ts` (implicit `tx` any). No runtime-owned file was reported; the Attempt 2 rerun passed with no diagnostics, as recorded below.

Requirement-to-fixture matrix is committed in `docs/code-runtime-proof.md`; the focused command observes actual QuickJS execution, not safe-rejection-only mocks. No PostgreSQL, container, live provider, credential, DNS, or deployment validation was required or claimed for this bounded runtime task.

Use /moda-task launcher-resolved dedicated worktrees and preparation packet.
Task authoring on main is the user's documentation exception, not permission for
Attempt 2 validation superseded that historical baseline observation: `npm run typecheck` passed with no diagnostics, and the production build's TypeScript phase passed.
Runtime code is not wired into the future typed adapter or production factory; those are explicitly owned by COMMERCE-026/024.

## Completion Report

Attempt 2 corrections are complete in the dedicated implementation worktree
`/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-029`
on `task/ARCH-020-COMMERCE-029`, committed and pushed as `b4e8d05`
(`fix(commerce): complete bounded runtime proof`). The parent report is being
submitted on the mirrored parent branch. No service gitlink, main branch,
database schema, architecture/index file or Architect Review text was modified.

### Attempt 2 Correction Checklist

- **A1-R1 implemented:** Replaced the producer surface with the exact C21 section 9.4
  `compile({source, signal, deadlineAt})` and
  `run({source, responseJson, signal, deadlineAt})` contracts and flat
  `{ok, code, line, column}` failures. Compile now honors cancellation and
  expired deadlines; serialized input is bounded at 2 MiB and raw bodies at
  256 KiB.
- **A1-R2 implemented:** Captured trusted QuickJS validation/serialization intrinsics before guest
  source executes, froze the relevant built-ins, rejected accessors,
  prototypes, custom `toJSON` and invalid values, and added regression cases
  for guest replacement of `JSON.stringify` and `Object.keys`.
- **A1-R3 implemented:** Awaited worker termination before resolving and releasing capacity, retained
  the post-registration abort check, and added a cancellation-capacity proof
  that a fifth run remains throttled until a worker termination settles.
- **A1-R4 implemented:** Added the reusable manifest `{runtimeVersion, artifactSha256,
  enginePackageVersion, limits}`, deterministic `code-runtime:package` output,
  and `code-runtime:smoke` that loads only copied worker/loader/WASM files,
  executes a positive transform, and proves the 64 MiB WASM ceiling without a
  source-tree fallback or network download.
- Added direct evidence for allocation pressure, bounded built-in serialization
  terminated by the supervisor deadline, WASM memory ceiling, compile
  cancellation and post-failure recovery. Generated `build/code-runtime/` is
  ignored and was not committed.

### Validation Results

- `npm run test:arch020-code-runtime-proof` -> PASS, 1 file, 8 tests.
- `npm run code-runtime:manifest` -> PASS; `quickjs-emscripten@0.31.0`,
  artifact SHA-256
  `0c031dd404df00f2d1ed9491a6590d014e88a50424996e5fd70feff1c931c045`, and
  configured WASM maximum `67108864` bytes.
- `npm run code-runtime:package` -> PASS; copied worker, Emscripten loader,
  WASM and manifest into `build/code-runtime/`.
- `npm run code-runtime:smoke` -> PASS; packaged transform output was
  `{"availability":"available"}` and the memory probe reported
  `67108864` bytes.
- `npm run lint -- --quiet` -> PASS.
- `npm run typecheck` -> PASS; no diagnostics.
- `npm run build` -> PASS; package/smoke, Prisma client generation, Next
  webpack compilation, TypeScript phase, static generation and build tracing
  completed successfully.
- `git diff --check` -> PASS.

### Scope and Evidence

The updated `docs/code-runtime-proof.md` records the exact limits and complete
SB01/SB02/SB03 fixture matrix. All scenarios use actual QuickJS execution and
synthetic inputs; no live credentials, provider, DNS, WhatsApp, deployment,
PostgreSQL, container or assembled cross-service flow was run or claimed.
Runtime wiring into the typed adapter and production factory remains owned by
COMMERCE-026/024. Shared package publication remains SHARED-002 scope.

### Git / VCS and Remaining Validation

Dependency/worktree evidence: the dedicated physical implementation worktree
and mirrored task branch were used; implementation `b4e8d05` is pushed. The
parent branch is `task/ARCH-020-COMMERCE-029`; this report is its only intended
workspace change. The recursive database submodule state was not changed.
Remaining live validation: developer-invoked provider, deployment, DNS,
credential, database, container and assembled cross-service checks remain
pending; this bounded task did not inspect secrets or launch those environments.
Architecture review is pending; no downstream task was launched. The task is
ready for `moda_architect` review.

## Architect Review

### Attempt 2 — Changes Requested (2026-09-21)

Reviewer: moda_architect. Reviewed implementation `b4e8d05c0f2ef74de96d7ee3e3611e593bd9a6f1` and parent report `92403d3c4089000b413d097dd925d56ba104ade9`; both submitted dedicated worktrees clean and remote heads verified. **Changes Requested; Ready, Attempt 2 retained; executor/claimed_at null.**

A1-R1's serialized C21 kernel interface is now present, including caller compile cancellation/deadline and flat errors. A1-R3's capacity ownership now awaits termination and rechecks cancellation. Packaging runs in the build and produces the named manifest plus copied worker/loader/WASM; the packaged smoke and memory ceiling probe pass locally. Preserve these improvements. Two narrowly scoped corrections remain from the existing output-isolation and SB02 requirements.

#### A2-R1 — Reject non-enumerable serialization hooks before serialization

File: `src/commerce/code-response/runtime/worker.mjs`, trusted __walk and __stringify path.

Capturing/fixing the intrinsics closes the earlier mutation cases, but __walk enumerates Object.keys only. JSON.stringify still discovers non-enumerable toJSON methods. This actual kernel invocation returns `{ok:true,outputJson:'[]'}`:

```js
function transform() {
  return Object.defineProperty({}, 'toJSON', { value: () => [] });
}
```

The validated root was a plain object; the guest method replaced it during serialization. This violates C21's custom-toJSON rejection and object-root contract. The new temporary fixture reproduces the bypass; a normal transform succeeds beside it.

Inspect the complete own-property descriptor set with pristine intrinsics, including non-enumerable and symbol properties as appropriate to the JSON-only contract. Reject custom toJSON regardless of enumerability before invoking serialization; retain descriptor-based accessor rejection and nested-object validation. Ensure the same path prevents custom serialization from replacing nested validated data or silently dropping invalid members. Serialize only the validated representation under the existing sandbox budget; do not invoke guest hooks in the host or rely solely on a post-parse root check. Keep the exact C21 string result interface.

Commit this short reproduction and its ordinary-object permitted case as focused regressions. A nested/non-enumerable hook must not receive a separate permissive path. No broader test quota is requested.

#### A2-R2 — Demonstrate the stated supervisor scenario instead of a startup deadline

Files: `tests/code-runtime-proof.test.ts`, `docs/code-runtime-proof.md` SB02 matrix and completion evidence.

The matrix says large built-in serialization reaches the 2,000 ms supervisor deadline, but that fixture passes `deadlineAt: Date.now() + 50`. Its only assertion is DEADLINE. It can pass by timing out during worker/WASM startup without entering JSON.stringify; it does not establish the long built-in/serialization behavior required by A1-R4/SB02. The ordinary infinite loop tests the QuickJS interrupt, which is a separate mechanism.

Add a controlled execution-start observation in the test/worker harness (no new guest host capability) or equivalent deterministic evidence that the relevant guest operation began. Demonstrate the supervisor terminating that bounded built-in operation when the interrupt cannot finish it, retaining the real production supervisor and capacity cleanup. Use an input that actually reaches that path and keep an overall bounded harness deadline. Verify a following normal transform succeeds. If allocation fails earlier instead, report that observed resource result rather than relabeling it supervisor proof. Correct the matrix's timing and evidence claims to match actual observations.

This is completion of the already-required SB02 scenario, not a request for exhaustive sandbox coverage or live deployment. Do not loosen production limits to make the test pass.

#### Verification and disposition

Reran `npm run test:arch020-code-runtime-proof`: **8/8 passed**. Reran `npm run code-runtime:package` and `npm run code-runtime:smoke`: **passed**, including copied artifact execution and the 67,108,864-byte ceiling probe. Manifest SHA-256 remains `0c031dd404df00f2d1ed9491a6590d014e88a50424996e5fd70feff1c931c045`. Temporary architect harness `/tmp/c029-review/review.test.ts`: **1 passed, 1 failed**, reproducing hidden-toJSON acceptance with outputJson `[]` while normal object output passes. Submitted lint/typecheck/build/diff evidence reviewed; no redundant full-suite run.

No implementation edit, main merge, gitlink update, live deployment or downstream promotion. Ready for corrections, Attempt 2 retained, claims cleared. COMMERCE-026 remains Pending until its prerequisites are accepted. SYSTEM-TEST-002 remains explicitly developer-invoked. Prior reviews are retained below.


### Attempt 1 — Changes Requested (2026-09-21)

Reviewer: moda_architect. Reviewed implementation `39e636f01775edce38296b283eae3ffadfbfd666` and parent report `8af402088996abd563ecb8b60f9e28bb8d86b0af`; both dedicated worktrees clean and heads verified against remote. **Changes Requested; Ready, Attempt 1 retained; executor/claimed_at null.** The fresh QuickJS worker does execute the positive synthetic transform, and the submitted six tests pass. Four producer corrections are required before COMMERCE-026 can consume this kernel. They concern functional contracts, guest isolation, resource ownership and packaging, not an exhaustive test quota.

#### A1-R1 — Implement the exact C21 section 9.4 kernel interface

Files: runtime/types.ts and kernel.ts.

The required interface is `compile({source,signal,deadlineAt})` and `run({source,responseJson,signal,deadlineAt})`, returning the common KernelResult: successful outputJson string (null for compile), or the closed direct code/line/column failure fields. The implementation instead requires contentHash, accepts a host response object, returns values/contentHash and nests a processor-style diagnostic. An actual call with the required responseJson throws TypeError in validResponse. Compile ignores caller cancellation/deadline. This is not an adapter detail to delegate to026: section9.4 explicitly supersedes the earlier combined ownership.

Replace the producer types and implementation with that exact interface. Enforce the 2 MiB serialized input bound before transferring input and the 256 KiB raw-body bound within the kernel's bounded processing; source/output bounds remain unchanged. Return bounded typed errors on startup/worker failures rather than allowing constructor/input failures to escape. Compile must honor the caller's abort and remaining deadline and return outputJson:null on success. Source/content identity and Shared/business-schema validation remain026's responsibility. Verify one positive invocation through the exact interface plus cancelled/expired compile; retain the normal transform result.

#### A1-R2 — Protect validation and serialization from guest mutation

File: runtime/worker.mjs, source evaluation and validator.

The validator runs after authored source in the same mutable global realm and calls guest-replaceable Object.keys/getPrototypeOf/getOwnPropertyDescriptor, Array.isArray, Number.isFinite and JSON.stringify. Two actual reproductions return success:

- `JSON.stringify = () => "[]"; function transform() { return {}; }` returns an accepted array through the host JSON.parse despite the object-root requirement.
- `Object.keys = () => []; function transform() { return { invalid: undefined }; }` silently strips the invalid member and succeeds.

Establish a trusted validation/extraction boundary before executing source. Capture pristine intrinsic operations in inaccessible bindings or otherwise prevent authored code from replacing the operations used by validation; do not merely freeze the current two reproduced names. Keep inspection/serialization inside the sandbox budget. Reject accessors/custom toJSON/prototypes and invalid values without invoking them in the host or silently dropping them. A host-side root check alone would not fix the second case. Return only a validated, bounded JSON string to the host under R1. Retain a normal JSON transform and these two short adversarial cases as regression checks; the downstream result schema cannot substitute for this producer guarantee.

#### A1-R3 — Retain the capacity slot until the worker has actually terminated

File: runtime/kernel.ts, runWorker finish and capacity finally.

finish calls `void worker.terminate()` and immediately resolves. The caller's finally releases capacity while termination is still in progress. Repeated abort/timeout calls can admit replacement workers while the previous workers still exist, violating the process-wide maximum of four and weakening the aggregate memory bound.

Make terminal settlement/cleanup idempotent, initiate termination promptly and await confirmed termination/exit before resolving and releasing the slot. Cover success, error, timeout, abort and startup failure without double release; remove listeners/timers. Recheck abort after listener registration so cancellation during worker startup is not missed. Use a focused delayed-termination fixture to prove a fifth worker stays throttled until a slot's worker actually exits, plus a real cancel/recovery run. Do not queue work or reduce the contract's capacity.

#### A1-R4 — Deliver a consumable runtime manifest and prove packaged artifact loading

Files: runtime export/build manifest, scripts/code-runtime-manifest.mjs, package/build configuration, docs/code-runtime-proof.md.

C21 requires an exported manifest `{runtimeVersion,artifactSha256,enginePackageVersion,limits}` for026. The current CLI only prints a differently shaped record, and the unchanged build command does not consume it. No worker/WASM references were found in the current Next artifact traces. The kernel is intentionally not wired into production factories yet, so a successful unrelated Next build does not prove this new entry or WASM was bundled/loaded. The report's claim that the build loaded the runtime artifact is unsupported by the submitted script/build path.

Provide the exact reusable manifest tied to the pinned artifact and a deterministic build/package step that includes the worker entry and its runtime/WASM dependencies at paths the kernel resolves. Add a production-artifact smoke using that packaged output without a source-tree worker fallback or network download; it must execute the positive transform. This stays within029's artifact ownership and does not require024 factory wiring or live deployment.

Keep the 64 MiB imported-memory configuration: static inspection shows the WASM imports memory and the loader accepts the supplied memory, so the source configuration is meaningful. However, the current tests do not demonstrate the stated WASM maximum, built-in long operation or serialization attack; a million-item result rejected by max-array validation is not that proof. Record a direct assertion on the actual memory used by the loaded artifact (growth beyond the configured ceiling fails), a bounded non-interruptible/built-in operation terminated by the supervisor, and serialization under the same budget, followed by recovery. These are the named SB02 deliverables, not unrelated coverage. Update the proof matrix and completion claims to the scenarios actually executed.

#### Verification and disposition

Reran `npm run test:arch020-code-runtime-proof`: **6/6 passed**. Temporary architect harness `/tmp/c029-review/review.test.ts`: **3/3 failed**, reproducing the two output-validation bypasses and exact-interface rejection. Reviewed source, manifest, build configuration and existing artifact traces; read the installed loader and inspected the WASM memory import. Submitted lint/build/manifest evidence reviewed; full typecheck's five unrelated Prisma diagnostics are not an acceptance blocker for these runtime corrections. No live provider, database, container or deployment action performed.

Ready for corrections; Attempt 1 retained, claims cleared. No implementation edits, main merge, gitlink update or downstream promotion. COMMERCE-026 remains Pending until this kernel and its other prerequisite are accepted. SYSTEM-TEST-002 remains explicitly developer-invoked. Preserve historical definition/review notes below.


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
