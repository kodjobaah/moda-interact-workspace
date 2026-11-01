---
id: ARCH-044-COMMERCE-001
architecture_id: ARCH-044
title: Make packaged Code Runtime deterministic and preserve compile-only semantics
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 10
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables: []
created: '2026-10-18'
updated: 2026-11-01
---

# Make packaged Code Runtime deterministic and preserve compile-only semantics

## Architecture

- Parent: `ARCH-044` — `docs/architecture/ARCH-044-commerce-baseline-stabilisation.md`.
- Repository: `moda-interact-commerce` (owner: `moda_commerce`).
- Baseline evidence: unchanged baseline `baseline-vitest.log` compared with ARCH-043 task run `typescript(20261018-183033)` on 2026-10-18. These are external validation artefacts, not committed files.
- Architecture relationship: this repairs pre-existing Commerce issues; it does not change the requirements of `ARCH-043-COMMERCE-002`.

## Objective

Make Commerce Code Runtime v1/v2 packaging, smoke checks and bounded-worker proof deterministic and independently reproducible without relaxing guest security or compile-only behavior.

## Context

The unchanged Commerce baseline passed `npm run code-runtime:package` and `npm run code-runtime:smoke`. The ARCH-043 task worktree instead previously failed `scripts/code-runtime-packaged-smoke.mjs:68` with `packaged v2 compile did not preserve compile-only behavior`. Observed SHA-256 of `quickjs.wasm` matched across runs (prefix `d4c9375f`); `helpers-v2.js` differed (baseline prefix `83fe8b71`, task prefix `070d8bd1`). These are diagnostic observations, not proof of cause. The baseline's Code Runtime proof test passed (12/12); the task worktree added one full-suite failure at `tests/code-runtime-proof.test.ts:120`, where `started` was `false` before a 400 ms deadline. The repository declares Node 24.19.0 while an operator log shows 24.21.0. Preserve the actual, pinned Node/toolchain contract instead of attributing the cause to Node without evidence.

## Scope

- Trace helper provenance through `scripts/code-runtime-manifest.mjs`, generated `build/code-runtime/helpers-v2.js`, `scripts/code-runtime-packaged-smoke.mjs` and installed/package-locked `string-strip-html@13.6.2`, `esbuild@0.28.2`, `quickjs-wasi@3.6.2`.
- Reproduce `compile-response` v2 failing or passing in a clean installation with recorded Node, dependency versions, helper/engine hashes and a specific mismatch report.
- Investigate the `onExecutionStart`/deadline race at `tests/code-runtime-proof.test.ts:112-123` and `src/commerce/code-runtime/kernel.ts` without raising timeouts blindly or changing the semantics of deadline enforcement.
- Implement only the smallest code, harness or packaging correction that evidence requires; add regression coverage for compiled-but-not-executed source, immutable helper namespace and guest host-capability denial.

## Out of Scope

- No general rewrite of QuickJS sandboxing, no extending guest permissions, no host/network access, no speculative dependency upgrades and no changes to ARCH-043 configuration consumers.
- No blanket increase to test timeouts as a substitute for proving the event ordering.

## Requirements

1. `compile-response` for `quickjs-sync.v2` must **never** execute top-level guest statements or return an execution payload; a thrown top-level `Error` in source must still compile without executing.
2. `quickjs-sync.v1` must not expose `moda`; v2's `moda.text.stripHtml` must stay frozen/non-configurable, and forbidden globals remain inaccessible.
3. Manifest hashes and runtime bytes must be reproducible under the approved toolchain; differences must be explicitly explained, not silently ignored.
4. Worker termination must enforce deadlines/cancellation and release capacity; regression tests must prove the operation actually started before asserting supervisor termination.
5. Preserve existing `build` script's packaging/smoke gate. Document whether Node/dependency/environment variation is causal using evidence.

## Work Items

- [x] Record exact package manager, Node version, resolved package versions, hashes and environment for the current clean task run; retain the unavailable historical artifact as an attribution limitation.
- [x] Reproduce and isolate the v2 compile-only smoke discrepancy; inspect package artifact and manifest content.
- [x] Reproduce and isolate the `onExecutionStart` race (single worker and concurrent suite).
- [x] Apply a bounded correction only if a real implementation/harness defect is established; current implementation passed the focused evidence, so no additional correction was warranted.
- [x] Verify deterministic regression tests and unchanged guest security invariants already present in the implementation.

## Interfaces / Contracts

Local Code Runtime `quickjs-sync.v1`/`quickjs-sync.v2` response/runtime version matrix; `quickjs-sync.v1` request runtime; Code Runtime package manifest and Worker messages; no new cross-repository contract. Shared structured logging must be reused for any new generic diagnostics.

## Dependencies

None.

## Enables

None directly. The architecture-level integrated validation remains after all eight tasks.

## Acceptance Criteria

- [x] Clean installed `npm run code-runtime:package && npm run code-runtime:smoke` passes consistently.
- [x] Code Runtime proof and helper-provenance tests pass repeatedly in isolation and under four-worker concurrency; the full four-worker repository run had no Code Runtime failures.
- [x] Compile-only, frozen helper namespace, no-host-capability, timeout, cancellation, and worker-slot-reuse behavior have direct regression evidence.
- [x] Current artifact provenance and toolchain are documented with exact hashes; generated output is not committed.
- [x] No unrelated consumer behavior changes or additional guest permissions were introduced in this attempt.

## Validation

- [x] `npm ci` with repository-approved Node/toolchain (actual version and `.nvmrc` selection recorded below).
- [x] `npm run code-runtime:package && npm run code-runtime:smoke` from a clean generation state, repeated.
- [x] `npx vitest run tests/code-runtime-proof.test.ts tests/code-runtime-helper-bundle.test.ts --maxWorkers=1`, repeated, then under `--maxWorkers=4` and the full suite.
- [x] `npm run build` passed; `npm run typecheck` ran after Prisma generation and reported one unrelated existing test typing error; `git diff --check` recorded below.

## Stop Condition

After all scoped Work Items and Acceptance Criteria are demonstrably satisfied, record exact commands and results in the Completion Report, set task `status: review`, clear execution claim as required by launcher protocol, return for architect review and **STOP**. Do not execute or close downstream work. If validation is blocked, record it accurately rather than claiming PASS.

## Implementation Notes

Known smoke location: `scripts/code-runtime-packaged-smoke.mjs` checks v2 compile-only at its end (line 68 in the snapshot). Do not diagnose the 400 ms test as "flaky" unless the operation start/worker scheduling evidence proves it. Avoid tests that only compare runtime return codes while missing proof of entering guest execution.

## Completion Report

### Status

Complete — Attempt 1. Architect acceptance is recorded. The historical
`070d8bd1` helper artifact remains unattributed because its original bytes and
environment are unavailable; current pinned-toolchain reproducibility is
verified and matches the unchanged-baseline artifact.

### Files Changed

No implementation source or generated artifact files changed in this attempt. The current checked-in Code Runtime implementation already contains the evidenced packaging, compile-only and worker-start behavior. This task file is the only intended change for this attempt.

### Work Completed

Verified the clean package and smoke path under the exact repository-pinned toolchain. Packaging and smoke use the same `bundleCodeRuntimeHelper()` function, the smoke independently rebuilds and compares helper bytes to the package and manifest, and v2 compile-only source containing a top-level throw returns `{ ok: true, outputJson: null }`.

Verified the current worker proof distinguishes guest and host enforcement: the real interruptible built-in operation announces execution start and returns `RESOURCE_LIMIT` at the guest budget; a started, intentionally nonresponsive worker is terminated by the unchanged host supervisor with `DEADLINE`, and capacity is reusable. No timeout or guest permission was changed.

The previously reported historical task artifact helper digest prefix `070d8bd1` could not be reproduced because its original artifact and environment are not present. The current clean task install reproduces the unchanged-baseline helper digest exactly; therefore the historical difference is not attributed to Node or a dependency without evidence.

### Validation Results

Environment: Darwin/x64; `.nvmrc` selected Node `v24.19.0` and npm `11.17.0`; package manager npm. `package-lock.json` SHA-256: `01830b46804ace6e92f148f892b7a54d4b918673ff780ee01390c097548fdf14`. Locked and installed versions: `quickjs-wasi@3.6.2`, `string-strip-html@13.6.2`, `esbuild@0.28.2`.

| Command | Result |
|---|---|
| `npm ci` | PASS; 905 packages installed. npm reported 44 audit findings (27 moderate, 16 high, 1 critical); no dependency changes were made in this task. |
| `npm run code-runtime:package` + `npm run code-runtime:smoke`, twice after `rm -rf build/code-runtime` | PASS both times; smoke verified v1/v2 matrix, v1 helper absence, v2 helper output/frozen namespace, forbidden capabilities, request v1, and compile-only behavior. |
| Packaged artifact SHA-256, both runs | Identical: `helpers-v2.js` `83fe8b710c646680781e605baa64f77ef215cea9bd7aa7df4133afd358c9c31a`; `manifest.json` `57e71653c06592e3e322eb03b1038bc112cff05af8fae3939b041671fd27d7c4`; `quickjs.wasm` `d4c9375f2b1ca4dc95f72c8aa2982a7a9951ac8011490d79c6582df732b4bbd9`; `worker.mjs` `172204db71c55a812f228d4d6aa7615d8d26a719cdc414a8ee0b2e65cb23ba31`. |
| `npx vitest run tests/code-runtime-proof.test.ts tests/code-runtime-helper-bundle.test.ts --maxWorkers=1` | PASS, 16 tests; repeated twice, both passed. |
| Same focused Vitest command with `--maxWorkers=4` | PASS, 16 tests. |
| `npx vitest run --maxWorkers=4` | 173 files passed, 22 failed, 6 skipped; 1,453 tests passed, 19 failed, 16 skipped. No Code Runtime proof/helper failure was reported. Failures include missing disposable database/Redis fixtures, unrelated UI timeout and Prisma/mock issues. |
| `npm run build` | PASS, including package/smoke, Prisma client generation and Next.js production build. Existing Nunjucks dynamic-loader warning only. |
| `npm run typecheck` after build/Prisma generation | FAIL with one unrelated diagnostic: `tests/system-commerce-tool-sync.test.ts:305` passes `{}` where current Next.js `ProcessEnv` typing requires `NODE_ENV`. |
| Focused `npx eslint` over Code Runtime kernel, worker, packaging, smoke and proof files | PASS; no diagnostics. |
| `git diff --check` | PASS for the task report change. |

The smoke manifest reported engine `quickjs-ng-wasi`, WASM digest `d4c9375f2b1ca4dc95f72c8aa2982a7a9951ac8011490d79c6582df732b4bbd9`, helper digest `83fe8b710c646680781e605baa64f77ef215cea9bd7aa7df4133afd358c9c31a`, and the exact locked package versions above. These current bytes match the supplied unchanged-baseline hashes. An earlier operator using Node `v24.21.0`/npm `11.19.0` also reported the same current digests and passing smoke, but that does not prove the missing historical `070d8bd1` artifact was caused by the Node variation.

### Worktree / Synchronisation Evidence

Launcher-prepared canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`. Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-044-COMMERCE-001`, branch `task/ARCH-044-COMMERCE-001`, prepared head `d70081a49fdd91a85336d303fcac75502e42eea7`. Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-044-COMMERCE-001`, branch `task/ARCH-044-COMMERCE-001`, prepared head `15d505ef0f84e8cab57af43dee0d78a83d969f93`; recursive submodule sync/update passed and `database` was initialized at `af77c594ecbfc78c26d01c0021a090830884bbff`. Dependency gate passed; no task dependencies. npm install/build outputs and generated Code Runtime package are ignored/untracked build state, not task source changes.

### Deviations

No implementation edit was necessary: the current checked-in implementation already satisfies the focused package, compile-only, security, guest-budget, supervisor, cancellation and capacity-reuse tests. The broad repository suite and standalone typecheck remain non-green for failures outside this task; those failures were not modified or represented as passing.

### Assumptions

The reported `070d8bd1` helper digest came from a separate historical task worktree whose generated bytes and exact environment are unavailable in this execution. Current reproducibility evidence applies to the clean task worktree and pinned toolchain only.

### Unresolved Issues

The historical `070d8bd1` helper artifact cannot be causally attributed without the original artifact, lock/install state and environment. Current pinned-toolchain output is reproducible and matches the unchanged-baseline artifact; the unavailable historical artifact is recorded as a provenance limitation, not attributed to Node or a dependency. The full Commerce suite still has unrelated failures, and standalone typecheck has the single unrelated `ProcessEnv` diagnostic identified above.

### Architectural Concerns

Report new cross-service contracts, database schema/owner changes, secret handling issues, or deployment requirements to `moda_architect` without expanding scope.

## Architect Review

### Review Status

Accepted — Attempt 1. With `completion_mode: automatic`, the task transitions
to `status: complete`; executor and claim are clear, and the attempt remains 1.

### Review Notes

The current package and smoke path reproduce identical helper, manifest,
WASM and worker hashes across clean runs under the pinned Node/npm and locked
dependencies. The packaged v2 compile-only test includes a throwing top-level
statement and returns no execution payload. Focused Code Runtime proof/helper
tests pass repeatedly at one and four workers, and the full four-worker run
reports no Code Runtime failures. The missing historical `070d8bd1` artifact
prevents causal attribution of that earlier difference, but it does not
contradict the current reproducibility evidence and is transparently documented.

### Reviewed Files

- `scripts/code-runtime-packaged-smoke.mjs`
- `src/commerce/code-runtime/kernel.ts`
- `src/commerce/code-runtime/worker.mjs`
- `src/commerce/code-runtime/helpers-v2-entry.js`
- `tests/code-runtime-proof.test.ts`
- `tests/code-runtime-helper-bundle.test.ts`
- The task Completion Report and provenance/validation evidence.

### Validation Reviewed

- Packaged smoke passed twice from a clean generated-artifact state with
  identical recorded hashes.
- Focused proof/helper tests passed twice at one worker and once at four
  workers (16 tests per run); the four-worker repository run had no
  Code Runtime failures.
- Production build and focused lint passed. Typecheck reports one unrelated
  `ProcessEnv` diagnostic; broad-suite failures are documented as unrelated
  and no Code Runtime tests failed.
- Architect verified the implementation branch is clean and synchronized at
  `15d505e`, with the published task ref present. `git diff --check
  origin/main...HEAD` passed.

### Architecture Conformance

Conforms to the current Commerce Code Runtime contract: compile-only remains
non-executing, v1/v2 helper exposure remains frozen, guest host capabilities
remain denied, and worker deadlines/cancellation preserve capacity semantics.
No production runtime or cross-service contract changes were introduced by this
task attempt.

### Follow-up

Accepted and Complete at Attempt 1. The documented inability to attribute the
missing historical helper artifact is not a blocker because the current clean
package is reproducible and matches the unchanged-baseline bytes. No downstream
task declares this task as a dependency; no dependency status changed.
