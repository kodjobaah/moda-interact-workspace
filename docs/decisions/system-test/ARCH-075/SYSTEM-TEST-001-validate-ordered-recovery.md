---
id: ARCH-075-SYSTEM-TEST-001
architecture_id: ARCH-075
title: Validate ordered recovery delivery across worker restarts
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: in_progress
priority: 10
executor: codex
claimed_at: 2026-11-13T05:35:26Z
attempt: 1
depends_on:
  - ARCH-075-BACKGROUND-004
  - ARCH-075-ADMIN-004
  - ARCH-075-ADMIN-003
  - ARCH-075-BACKGROUND-003
  - ARCH-075-SHARED-003
  - ARCH-075-SHARED-004
  - ARCH-075-ADMIN-001
  - ARCH-075-ADMIN-002
  - ARCH-075-DATABASE-001
  - ARCH-075-SHARED-001
  - ARCH-075-SHARED-002
  - ARCH-075-BACKGROUND-001
  - ARCH-075-BACKGROUND-002
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Validate ordered recovery delivery across worker restarts

## Architecture

ARCH-075; docs/architecture/ARCH-075-ordered-recovery-message-layout.md; coordinator moda_architect. Read all frozen contract constants and lifecycle decisions before implementation.

## Objective

Validate ordered recovery delivery across worker restarts.

## Context

User requests logo/shop details before a distinct product image and checkout footer. Existing single-provider-id response cannot safely loop multiple sends. This task owns one bounded prerequisite capability; preserve completed prior behavior.

## Scope

Terminal independent integrated fixtures/validation only after all dependencies accepted and developer manual checkpoint; actual PostgreSQL/Redis with provider simulator.

## Out of Scope

Other repositories/tasks, source main merges/deployment, production sends/replays/resets, billing/usage/cap changes, provider credentials/permissions, unsupported exactly-once assumptions, unbounded fanout/retries, unrelated refactors. Return actual cross-owner gaps.

## Requirements

Also prove common editable Admin revision custom header/footer parity across compiled approved Meta projection and actual AI/HUMAN runtime receipts, checkout-last/opt-out preservation, stale common reference/activation refusal and legacy frozen compatibility. Never send freeform product tail outside the valid customer window.

Exercise real accepted contracts/migration/worker producer+status queue+part engine, ordered2/3 sends, quoted eachpart, exactfooter, one logical usage, callbackbeforeACK/readbefore-delivered, process death/restart, unknown/no prefix resend and takeovercancel. Validate legacy compatibility and absence of customer/secret telemetry. No source implementation, paid service or unauthorized live send. This terminal test never gates unfinished implementation tasks.

## Work Items

- [ ] Implement only assigned capability and document compatibility.
- [ ] Complete meaningful required checks and regression/negative evidence.
- [ ] Publish mirrored branch/report and return review, then stop.

## Interfaces / Contracts

Use canonical ARCH075 frozen decisions. Shared owns ordered schema/digest and existing perpart media exports; Database owns durable child/status identity; Background owns provider/current authorization and logical aggregation. Never duplicate validators or fabricate product/provider identity.

## Dependencies

ARCH-075-DATABASE-001; ARCH-075-SHARED-001; ARCH-075-SHARED-002; ARCH-075-SHARED-003; ARCH-075-SHARED-004; ARCH-075-ADMIN-001; ARCH-075-ADMIN-002; ARCH-075-ADMIN-003; ARCH-075-BACKGROUND-001; ARCH-075-BACKGROUND-002; ARCH-075-BACKGROUND-003.

The developer manual checkpoint is satisfied. Independent disposable integrated fixtures may run while live translation review/provider approval is pending; simulator validation does not claim live activation or delivery.

## Enables

Only dependent tasks after architect acceptance; never begin them implicitly.

## Acceptance Criteria

- [ ] Assigned bounded capability and frozen contract behavior satisfied.
- [ ] Legacy reads/records remain compatible; no unauthorized cross-owner/billing/security change.
- [ ] Durable/contract identity and fault cases satisfy required checks without silent fallback.
- [ ] Canonical dedicated mirrored worktree, synchronization and recursive evidence recorded; no private proof committed.

## Validation

- [ ] Deterministic integrated realPG/Redis/worker provider-fault scenarios and independently recorded accepted revision/package/migration evidence.
- [ ] Isolation/privacy checks and report measured outcomes/limits; no genuine production send unless separately authorized.
- [ ] Diff/privacy hygiene and report actual results, no production sends or secrets.

## Stop Condition

After required work and validation, set review, submit Completion Report and STOP. No main merge/deploy or enabled task execution.

## Implementation Notes

Admin004 is now Accepted; preserve this same active claim and independent fixture progress. Root merged corrected Admin source c765be827cd6086157d38060ab5a200745b25052; validate that accepted revision before final completion. No reset or re-claim is authorized.

You are not alone. Preserve others' edits and canonical prepared isolation. Root owns final merges/deployment. Architecture constants resolve inter-agent assumptions; report genuine gaps before expanding scope.

### Bounded test build-resource accommodation

The exact pinned Background Docker build encountered a V8 heap exhaustion (exit 134) during TypeScript compilation. A reversible test-only Dockerfile overlay is authorized: derive from the exact pinned Dockerfile and change only `RUN npm run build` to `RUN NODE_OPTIONS=--max-old-space-size=3072 npm run build`. Keep Node base, lockfiles, source/submodule bytes, runtime ENV and CMD unchanged; do not persist NODE_OPTIONS or change Docker host resource settings. Record the initial failure, exact one-line overlay diff/hash and resulting image identity. Verify the resulting runtime environment has no heap override. This supports integrated correctness under adjusted build resources, not byte-identical production-image or production build-memory parity. If the bounded increase fails, return evidence before further changes; do not invent a source correction.

### Host-compiled correctness-image fallback

The bounded 3072 MiB compiler override also exhausted Docker build resources. Further memory/VM changes are not authorized. For integrated correctness only, compile exact pinned source and lockfile with its declared TypeScript 6.0.2 ES2022/NodeNext commands under observed host Node24.19, then copy only audited dist/dist-cli JavaScript, source maps and declared fixed JPEG assets into a test image. Retain exact pinned Node22.23.5 base and its own Linux npm dependencies, Prisma generation/binary, sharp, observability/scripts/assets/database, runtime ENV and CMD. Never copy host node_modules, generated Prisma clients/native binaries, credentials, environment files, symlinks or arbitrary config. Runtime NODE_OPTIONS must be absent.

Record source/database commits, compiler and host/runtime versions, exact base digest, overlay diff and output allowlist hashes/sizes, published Shared integrity and both failed Docker build diagnostics. Execute tests inside the actual Node22 runtime. This validates source-derived runtime behavior under adjusted test build mechanics; it does not prove production Docker build reproducibility or host/runtime build parity and must not produce/promote a production artifact. Any actual incompatible output returns as evidence, not normalization or source changes.

## Completion Report

### Status

In Progress — partial checkpoint only; acceptance criteria are not satisfied.

### Files Changed

Implementation checkpoint `806f251` on `task/ARCH-075-SYSTEM-TEST-001`:
image builder and focused tests; work-in-progress independent Admin/provider/worker
fixture modules; `docs/validation/ordered-recovery-progress.md` with measured limits.
No implementation submodule gitlink or other task files changed.

### Work Completed

Preserved prepared canonical mirrored worktrees and claim. Added the explicitly
authorized reversible build-stage-only 3072 MiB heap option, exact Dockerfile hash
and separate image tag; focused coverage refuses a larger heap. Began independent
Admin common-source activation and actual worker producer fixture adapters.
These fixture modules are unfinished and have no executable integration entry point.

### Validation Results

- 6/6 focused image-builder tests passed.
- `npm run typecheck` and `npm run lint` passed; `git diff --check` passed.
- Disposable PostgreSQL owning migration deployment succeeded during Admin-only
  setup; the Admin fixture itself did not execute due to harness ESM/Prisma
  packaging. Adapter correction is not yet rerun.
- Exact Background `d7a9bd1b0d1cceb908dd8ee23942dc93a9cf0417` production build
  failed at TypeScript compilation with V8 heap exhaustion, exit 134.
- Authorized 3072 MiB temporary Dockerfile attempt failed with Docker exit 102,
  ResourceExhausted / cannot allocate memory after 61.73 s. No resulting runtime
  image exists; runtime heap-environment inspection and integrated tests remain
  pending. No resource escalation attempted.
- Disposable PostgreSQL containers were cleaned. No deployed-environment or
  live provider requests, sends, replays or counters were used.

### Deviations

Only the architect-authorized one-line test build-resource accommodation was
attempted. It also failed; no successful production-image parity claim is made.
Original/derived Dockerfile hashes and exact measured evidence are recorded in
implementation progress documentation. Raw diagnostic logs are local `/tmp`
artifacts, not committed private proof.

### Assumptions

Synthetic media metadata and APPROVED fixtures are local integration inputs only;
they do not prove Meta approval, R2 media delivery or production activation.

### Unresolved Issues

Docker compilation resources block the real worker image and all required
PG/Redis/worker fault scenarios. Root reported a new Admin staging/footer source
correction prerequisite; independent integrated execution is held pending its
acceptance and architect task amendment. Await architecture decision on any
host-compiled-output alternative; read-only build mapping was supplied to root.

### Architectural Concerns

No cross-owner implementation, weakened validators, synthetic production claim,
source/main merge or billing/security change. Task stays in progress; this is not
Ready for Review and must not be accepted as completed system validation.

## Architect Review

### Review Status

Pending

### Review Notes

Pending actual implementation review.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
