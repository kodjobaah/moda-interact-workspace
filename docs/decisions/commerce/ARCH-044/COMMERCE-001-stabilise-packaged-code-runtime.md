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
status: in_progress
priority: 10
executor: copilot
claimed_at: 2026-11-01T15:43:45Z
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

- [ ] Record exact package manager, Node version, resolved package versions, hashes and environment for the baseline and task runs.
- [ ] Reproduce and isolate the v2 compile-only smoke discrepancy; inspect package artifact and manifest content.
- [ ] Reproduce and isolate the `onExecutionStart` race (single worker and concurrent suite).
- [ ] Apply a bounded correction only if a real implementation/harness defect is established.
- [ ] Add deterministic regression tests and document unchanged guest security invariants.

## Interfaces / Contracts

Local Code Runtime `quickjs-sync.v1`/`quickjs-sync.v2` response/runtime version matrix; `quickjs-sync.v1` request runtime; Code Runtime package manifest and Worker messages; no new cross-repository contract. Shared structured logging must be reused for any new generic diagnostics.

## Dependencies

None.

## Enables

None directly. The architecture-level integrated validation remains after all eight tasks.

## Acceptance Criteria

- [ ] Clean installed `npm run code-runtime:package && npm run code-runtime:smoke` passes consistently.
- [ ] Existing 12 Code Runtime proof tests pass in isolation and under repository concurrency; startup and deadline assertions are deterministic.
- [ ] Compile-only, frozen helper namespace, no-host-capability, timeout, cancellation, and worker-slot-reuse behavior have direct regression evidence.
- [ ] Artifact provenance and toolchain differences are documented with exact hashes; generated output is not committed unless explicitly required by packaging architecture.
- [ ] No unrelated consumer behavior changes or additional guest permissions.

## Validation

- [ ] `npm ci` with repository-approved Node/toolchain (note actual version and `.nvmrc` selection).
- [ ] `npm run code-runtime:package && npm run code-runtime:smoke` from a clean generation state, repeated.
- [ ] `npx vitest run tests/code-runtime-proof.test.ts --maxWorkers=1`, repeated, then under `--maxWorkers=4`/the full suite.
- [ ] `npm run typecheck`, `npm run build`, and `git diff --check` where affected.

## Stop Condition

After all scoped Work Items and Acceptance Criteria are demonstrably satisfied, record exact commands and results in the Completion Report, set task `status: review`, clear execution claim as required by launcher protocol, return for architect review and **STOP**. Do not execute or close downstream work. If validation is blocked, record it accurately rather than claiming PASS.

## Implementation Notes

Known smoke location: `scripts/code-runtime-packaged-smoke.mjs` checks v2 compile-only at its end (line 68 in the snapshot). Do not diagnose the 400 ms test as "flaky" unless the operation start/worker scheduling evidence proves it. Avoid tests that only compare runtime return codes while missing proof of entering guest execution.

## Completion Report

### Status

Not Started

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run. Record each exact command, environment, exit code, test totals and any known-baseline differences. Baseline failures may not be silently treated as task successes.

### Worktree / Synchronisation Evidence

Not yet materialised. Record launcher-resolved canonical workspace root, dedicated parent and implementation worktrees, initial branch/commit identities and recursive submodule state when execution begins.

### Deviations

None yet.

### Assumptions

Task definition based on the 2026-10-18 source snapshot and supplied baseline/task logs; re-inspect current implementation when executing.

### Unresolved Issues

None beyond the explicitly described diagnostics to investigate.

### Architectural Concerns

Report new cross-service contracts, database schema/owner changes, secret handling issues, or deployment requirements to `moda_architect` without expanding scope.

## Architect Review

### Review Status

Pending

### Review Notes

Awaiting implementation evidence.

### Reviewed Files

None yet.

### Validation Reviewed

None yet.

### Architecture Conformance

Not assessed.

### Follow-up

None yet.
