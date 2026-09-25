---
id: ARCH-021-COMMERCE-019
architecture_id: ARCH-021
title: Establish Phase 3 authoring validation and publication gate
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 34
executor: null
claimed_at: null
attempt: 3
depends_on:
  - ARCH-021-COMMERCE-016
  - ARCH-021-COMMERCE-027
  - ARCH-020-COMMERCE-030
enables:
  - ARCH-021-COMMERCE-023
  - ARCH-021-COMMERCE-024
created: 2026-09-23
updated: 2026-09-25
---

# Establish Phase 3 authoring validation and publication gate

## Architecture

Architecture ID: ARCH-021

Architecture document: `docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator: moda_architect

## Objective

Define one common server-side validation/result/authorization contract for Phase 3 Tool authoring and install the fail-closed `LIVE_TEST_REQUIRED` publication gate, consuming the simplified Auth.js role hierarchy and explicit error model without introducing another auth layer, function-valued production port or generic `unknown` validation result.

## Context

COMMERCE-016 owns the canonical Commerce-local Tool definition. COMMERCE-027 established the hierarchical Studio authorization model:

```text
PLATFORM_SUPER_ADMIN > PLATFORM_ADMIN > MERCHANT_ADMIN > MERCHANT_EDITOR > MERCHANT_VIEWER
```

Phase 3 Tools remain platform-owned in this phase. Merchant Tool ownership is not introduced here. The simplification terminal system test remains Ready by developer choice and is not a dependency of this implementation task.

The existing ARCH-020 external publication validator uses synthetic response samples/receipts. ARCH-021 requires a successful real selected-shop/provider test for the exact saved revision before a newly authored Phase 3 Tool can publish. Phase 4 owns that live-test receipt.

## Scope

Primary files:

```text
src/commerce/tool-authoring/contracts.ts
src/commerce/external-publication/index.ts
src/commerce/external-publication/contracts.ts
src/commerce/publication/validation.ts            # only exact gate/error propagation needed
lib/auth/merchant-access.ts                       # consume existing helper; no new role model
lib/auth/role-hierarchy.ts                        # consume only; modify only if a task-owned defect is proven
tests/tool-authoring-common-validation.test.ts
tests/tool-authoring-authorization.test.ts
package.json
```

Do NOT create `src/commerce/tool-authoring/auth.ts` or another authorization matrix. Use the accepted COMMERCE-027 helpers directly.

## Out of Scope

- Compiling or previewing request JavaScript (COMMERCE-023).
- Validating connection revisions (COMMERCE-023).
- Compiling Shopify Admin GraphQL (COMMERCE-024).
- Real Shopify/external requests.
- Live-test receipt implementation (Phase 4).
- Tool editor UI.
- Merchant-owned Tool libraries.
- Provider credentials in browser/client contracts.
- Replacing historical ARCH-020 publication evidence for already-published development revisions.

## Requirements

### R1 — exact common validation result

Export exactly one bounded structural-validation envelope:

```ts
type ToolAuthoringValidation =
  | { valid: true; schemaHash: string | null; issues: [] }
  | {
      valid: false;
      schemaHash: string | null;
      issues: Array<{
        path: string;
        code: string;
        message: string;
        line?: number | null;
        column?: number | null;
      }>;
    };
```

Maximum 32 issues. Each `path`, `code` and `message` is bounded to 512 UTF-8 bytes. Messages MUST NOT contain credentials, access tokens, authorization headers, provider response payloads or raw database connection details.

### R2 — exact Phase 3 authorization policy

Every new Phase 3 platform Tool authoring Server Action MUST use the already-accepted helper:

```ts
requireStudioPlatformRole('ADMIN')
```

from `lib/auth/merchant-access.ts`.

This means:

```text
PLATFORM_ADMIN        allowed
PLATFORM_SUPER_ADMIN  allowed through hierarchy
MERCHANT_ADMIN        denied
MERCHANT_EDITOR       denied
MERCHANT_VIEWER       denied
```

`developmentBypass === true` is already resolved by COMMERCE-027 to the development `PLATFORM_SUPER_ADMIN`; Phase 3 MUST NOT re-check bypass id, role, email, provider subject or `PlatformAdmin` membership.

Publishing/enabling/disabling remains subject to the existing lifecycle `SUPER_ADMIN` requirement. This task MUST NOT weaken that requirement.

### R3 — exact Server Action failure contract

For non-mutating Phase 3 validation/metadata/request-preview Server Actions, export/reuse this exact envelope:

```ts
type ToolAuthoringActionCode =
  | 'FORBIDDEN'
  | 'INVALID_INPUT'
  | 'NOT_FOUND'
  | 'DATABASE_UNAVAILABLE'
  | 'INTERNAL_ERROR';

type ToolAuthoringActionResult<T> =
  | { kind: 'ok'; value: T }
  | {
      kind: 'error';
      code: ToolAuthoringActionCode;
      message: string;
      retryable: boolean;
    };
```

Rules:

1. known validation errors are `INVALID_INPUT`;
2. missing durable authoring resources are `NOT_FOUND`;
3. authorization denial is `FORBIDDEN`;
4. Prisma connectivity/timeout/disconnect classes `P1001`, `P1002`, `P1008`, `P1017` are `DATABASE_UNAVAILABLE` with `retryable: true`;
5. unexpected exceptions are logged server-side through the approved shared structured logger and returned as bounded `INTERNAL_ERROR`;
6. the result MUST NOT contain `kind: 'unknown'`;
7. a validation/read action MUST NOT create UI `UNCONFIRMED` state because it makes no durable mutation.

Transport uncertainty for Tool mutations is owned by COMMERCE-020 and is reconciled through `CommerceAuditEvent.operationId`; it is not represented by this validation result.

### R4 — exact Phase 3 publication gate

For an otherwise structurally valid DRAFT using either canonical Phase 3 kind:

```text
EXTERNAL_HTTP
SHOPIFY_ADMIN_GRAPHQL
```

`validateForPublication` MUST preserve/return exactly:

```text
code: LIVE_TEST_REQUIRED
path: /liveTest
message: Run a successful live tool test for the current saved revision before publishing.
```

The publication lifecycle must preserve `LIVE_TEST_REQUIRED` as an identifiable failure code through the Server Action/UI boundary; do not collapse it into a generic `UNAVAILABLE`/`INTERNAL_ERROR` message.

Phase 4 will replace this fail-closed gate with exact live-test receipt validation.

### R5 — synthetic evidence cannot satisfy publication

Synthetic fixture/sample validation MUST NOT create, translate into or reuse a receipt that satisfies the Phase 3 publication gate. Existing automated fixture utilities remain test assets only.

Already-published historical revisions are read-only history; this task MUST NOT retroactively unpublish them.

### R6 — domain-validator boundary

COMMERCE-023 and COMMERCE-024 MUST return `ToolAuthoringActionResult<ToolAuthoringValidation>` from their named Server Actions and use `requireStudioPlatformRole('ADMIN')` directly. This common task MUST NOT import or invoke either domain compiler and MUST perform zero provider I/O.

### R7 — focused validation

Add `test:arch021-tool-authoring-common` proving all of:

- validation result is bounded to 32 safe issues;
- PLATFORM_ADMIN is admitted;
- PLATFORM_SUPER_ADMIN is admitted through hierarchy;
- all merchant roles are denied for platform Tool authoring;
- development bypass is admitted without a second identity/role lookup;
- `DATABASE_UNAVAILABLE` is returned explicitly and is not converted to unknown;
- unexpected errors are logged and returned as bounded `INTERNAL_ERROR`;
- canonical EXTERNAL_HTTP publication returns exact `LIVE_TEST_REQUIRED`;
- canonical SHOPIFY_ADMIN_GRAPHQL publication returns exact `LIVE_TEST_REQUIRED`;
- synthetic ARCH-020 evidence cannot satisfy either gate;
- already-published historical revisions are not retroactively invalidated;
- no request-JS/Admin compiler/provider transport is invoked by this common layer.

## Work Items

- [x] Add the bounded common validation and action-result contracts.
- [x] Consume COMMERCE-027 `requireStudioPlatformRole('ADMIN')`; create no alternate auth helper.
- [x] Install/preserve exact `LIVE_TEST_REQUIRED` propagation for both canonical Phase 3 kinds.
- [x] Ensure synthetic evidence cannot satisfy the new gate.
- [x] Add hierarchy/error/publication focused tests.

## Interfaces / Contracts

Consumes COMMERCE-016 Tool-definition contracts, COMMERCE-027 authorization hierarchy and the accepted ARCH-020 publication lifecycle.

Produces `ToolAuthoringValidation` and `ToolAuthoringActionResult<T>` consumed by COMMERCE-023/024 and surfaced by COMMERCE-021/022.

## Dependencies

- ARCH-021-COMMERCE-016
- ARCH-021-COMMERCE-027
- ARCH-020-COMMERCE-030

## Enables

- ARCH-021-COMMERCE-023
- ARCH-021-COMMERCE-024

## Acceptance Criteria

- [x] Phase 3 platform Tool authoring uses the accepted role hierarchy and no duplicate auth model.
- [x] Validation/read failures are explicit; no common validation path returns generic unknown.
- [x] External and Admin validators evolve independently behind one bounded validation result.
- [x] Both canonical Phase 3 kinds fail publication with exact `LIVE_TEST_REQUIRED` until Phase 4.
- [x] Synthetic evidence cannot satisfy the gate.
- [x] Common validation/publication code performs zero provider I/O.

## Validation

- [x] `npm run test:arch021-tool-authoring-common` (7 files, 77 tests passed, zero skipped; includes the executable zero-provider-I/O proof)
- [x] `npm run test:arch021-tool-authoring-validation` (1 file, 6 tests passed)
- [x] `npm run test:arch020-external-publication` (1 file, 13 tests passed)
- [x] `npm run test -- --run tests/auth-role-requirements.test.ts tests/auth-permissions.test.ts` (2 files, 14 tests passed)
- [x] `npm run lint` (0 errors; 6 existing warnings in unrelated files)
- [x] `npm run typecheck` (known unrelated baseline failures only; 16 errors in 8 unrelated files; no task-owned diagnostic)
- [x] `git diff --check`

## Stop Condition

Set task to `review`, return Completion Report and STOP. Do not implement either domain validator, Tool UI or live tests.

## Implementation Notes

The simplification `ARCH-021-SYSTEM-TEST-001` remains a terminal Ready task and is intentionally not a dependency. The developer is holding terminal system tests until the implementation phases are finished.

## Completion Report

### Status
Ready for Review

### Attempt 2 Launcher and Worktree Evidence
- Task: `ARCH-021-COMMERCE-019`, attempt `2`, logical agent `moda_commerce`, execution mode `agent`, completion mode `automatic`.
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-019`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-019`.
- Parent branch and implementation branch: `task/ARCH-021-COMMERCE-019`.
- Start-of-attempt parent synchronization: launcher completed; parent head after claim `99223bd8ad937c4c46ba2365101deaa4f6148ccd`; origin-main incorporation `yes`; task-branch fast-forward `not-needed`.
- Start-of-attempt implementation synchronization: launcher completed; implementation head after preparation `bbc106afdbe17cdc2b87bad78ed5cc9e9890330b`; origin-main incorporation `yes`; task-branch fast-forward `not-needed`.
- Attempt 2 claim evidence: parent claim commit `b63f716028d2ff0bffde4603041c9f004d7055f1`, pushed.
- Recursive submodule materialization: launcher recursive sync/update passed.
- Database submodule commit: `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.

### Files Changed
- `package.json`
- `src/commerce/external-publication/index.ts`
- `src/commerce/tool-authoring/contracts.ts`
- `src/commerce/tool-authoring/server-actions.ts`
- `tests/auth-role-requirements.test.ts`
- `tests/commerce-lifecycle.test.ts`
- `tests/external-publication.test.ts`
- `tests/studio-integration.test.ts`
- `tests/tool-authoring-server-actions.test.ts`
- `tests/tool-authoring-validation.test.ts`

### Correction-to-File/Test Mapping
- A1-R1: removed the historical DIRECT prohibition so canonical DIRECT, OBJECT/LIST and JAVASCRIPT EXTERNAL_HTTP modes reach exact `LIVE_TEST_REQUIRED`; covered in `tests/external-publication.test.ts` and `tests/commerce-lifecycle.test.ts`.
- A1-R2: replaced byte-slice decoding with code-point-safe UTF-8 truncation retaining the 32-issue cap; covered in `tests/tool-authoring-validation.test.ts` with multibyte boundary and replacement-character assertions.
- A1-R3: classified only the known `mapToolArguments()` validation TypeErrors as `INVALID_INPUT`; covered by real Server Action calls in `tests/tool-authoring-server-actions.test.ts` for invalid definition, invalid input value, missing mapping and invalid external scalar.
- A1-R4: common command now executes the accepted hierarchy tests; `tests/auth-role-requirements.test.ts` directly proves PLATFORM_ADMIN, PLATFORM_SUPER_ADMIN, all merchant roles denied, and development bypass without identity lookups.
- A1-R5: executable lifecycle coverage proves exact gate code/message for EXTERNAL_HTTP and SHOPIFY_ADMIN_GRAPHQL; Studio translation preserves `{ kind: 'unavailable', code: 'LIVE_TEST_REQUIRED', ... }`; published history remains readable in `tests/commerce-lifecycle.test.ts` and `tests/studio-integration.test.ts`.
- A1-R6: existing synthetic receipt rejection remains covered; common authoring files have no request-JavaScript/Admin compiler, external transport or Shopify transport invocation.
- A1-R7: `test:arch021-tool-authoring-common` executes all focused Commerce-019 contract suites with zero skipped tests; required validation results are below.
- A1-R8: this report records the exact Attempt 2 launcher packet, implementation/report commit hashes, push parity and clean-worktree evidence.

### Work Completed
- Preserved the accepted bounded validation/action contracts and platform-role authorization boundary.
- Enforced exact Phase 3 fail-closed publication behavior for both canonical kinds and all EXTERNAL_HTTP response modes.
- Kept synthetic receipts from satisfying publication and did not alter already-published history or add provider/publication wiring beyond scope.

### Validation Results
- `npm run test:arch021-tool-authoring-common`: passed, 75 tests across 6 files, zero skipped.
- `npm run test:arch021-tool-authoring-validation`: passed, 6 tests.
- `npm run test:arch020-external-publication`: passed, 13 tests.
- `npm run test -- --run tests/auth-role-requirements.test.ts tests/auth-permissions.test.ts`: passed, 14 tests across 2 files.
- `npm run lint`: passed with 0 errors and 6 existing warnings in unrelated files: `scripts/code-runtime-manifest.mjs`, `src/studio/code-response/code-response-panel.tsx`, `tests/agent-configuration-model.test.ts`, and `tests/mcp-service.test.ts`.
- `npm run typecheck`: known unrelated baseline failures only, 16 errors in `app/api/studio/code-response/validate/route.ts`, `tests/agent-configuration-effective.test.ts`, `tests/agent-configuration-prompts-postgres.test.ts`, `tests/browser-evidence/vite.config.ts`, `tests/c20-integration-fixture.test.ts`, `tests/external-wiring.test.ts`, `tests/local-external-mcp-diagnostic.test.ts`, and `tests/selected-shop-context.test.ts`; no task-owned diagnostic remains.
- `git diff --check`: passed.
- Source audit: no provider transport/compiler invocation in the common authoring layer or Server Actions.

### Implementation and VCS Evidence
- Implementation commit: `47fa255`, pushed to `origin/task/ARCH-021-COMMERCE-019`.
- Implementation worktree was clean after the implementation commit.
- Parent report commit: `93b3bdef`, pushed to `origin/task/ARCH-021-COMMERCE-019`.
- Push parity: implementation push and parent report push both passed.

### Deviations
- None from the Attempt 2 correction contract. Full typecheck remains limited by the unrelated baseline diagnostics listed above.

### Assumptions
- The injected external publication validator remains the accepted Phase 3 boundary; this task does not implement COMMERCE-023/024 validators or Phase 4 live-test receipts.

### Unresolved Issues
- None task-owned.

### Architectural Concerns
- None.

### Attempt 3 Completion Report

#### Status
Ready for Review

#### Launcher and Worktree Evidence
- Task: `ARCH-021-COMMERCE-019`, attempt `3`, logical agent `moda_commerce`, execution mode `agent`, completion mode `automatic`.
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-019`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-019`.
- Parent and implementation branches: `task/ARCH-021-COMMERCE-019`.
- Start-of-attempt parent synchronization: launcher completed; origin-main incorporation `already-current`; task-branch fast-forward `not-needed`; parent head after claim `6c5c10dfcbd7ba86e212377f35b964a1e8ffd996`.
- Start-of-attempt implementation synchronization: launcher completed; origin-main incorporation `already-current`; task-branch fast-forward `not-needed`; prepared implementation head `8375766c0c188e365903d5214c40b38779ba7bf3`.
- Required package-script merge resolution: implementation merge commit `8375766c0c188e365903d5214c40b38779ba7bf3`; both Commerce-019 authoring scripts and origin/main Shopify compiler/oracle scripts are preserved.
- Attempt 3 claim evidence: parent claim commit `6d179f2a613d865f4095ac9f708016c8abd07b99`, pushed.
- Recursive submodule materialization: launcher recursive sync/update passed.
- Database submodule commit: `0a8d3b9feade69690b6c1e33aeda051ea588bd45`.

#### Correction-to-File/Test Mapping
- A2-R1: added `tests/tool-authoring-no-provider-io.test.ts`; it executes the real `validateToolDefinitionAction()` and `validateToolArgumentsAction()` with the existing role mock, asserts successful results, and proves a throwing `globalThis.fetch` spy is untouched. The same test audits `contracts.ts` and `server-actions.ts` for request-JS, Admin compiler, provider transport, integration backend, session and `/admin/api/` references.
- A2-R2: updated `package.json` so `test:arch021-tool-authoring-common` runs all prior six focused files plus the new provider-boundary file; all 77 tests execute with zero skips and all prior authorization, publication, lifecycle, Studio, UTF-8 and `INVALID_INPUT` proofs remain green.
- A2-R3: this report records the fresh Attempt 3 packet, implementation commit `fe3bcf40ed928c1ee5b668a02d83b4a177d01067`, final parent report commit after publication, push parity, and clean worktrees.

#### Work Completed
- Added only the review-required executable proof and focused script registration. No runtime/publication behavior or out-of-scope domain validator was changed.
- Preserved exact `LIVE_TEST_REQUIRED` behavior, synthetic-receipt rejection, bounded UTF-8 issues, explicit action errors, hierarchy authorization, client-safe DTOs, and zero provider I/O in the common layer.

#### Validation Results
- `npm run test:arch021-tool-authoring-common`: passed, 7 files and 77 tests, zero skipped.
- `npm run test:arch021-tool-authoring-validation`: passed, 6 tests.
- `npm run test:arch020-external-publication`: passed, 13 tests.
- `npm run test -- --run tests/auth-role-requirements.test.ts tests/auth-permissions.test.ts`: passed, 14 tests across 2 files.
- `npm run lint`: passed with 0 errors and 6 existing warnings in unrelated files: `scripts/code-runtime-manifest.mjs`, `src/studio/code-response/code-response-panel.tsx`, `tests/agent-configuration-model.test.ts`, and `tests/mcp-service.test.ts`.
- `npm run typecheck`: known unrelated baseline failures only, 16 errors in 8 unrelated files; no diagnostic in `src/commerce/tool-authoring/**`, `tests/tool-authoring-validation.test.ts`, `tests/tool-authoring-server-actions.test.ts` or `tests/tool-authoring-no-provider-io.test.ts`.
- `git diff --check`: passed.

#### Implementation and VCS Evidence
- Implementation commit: `fe3bcf40ed928c1ee5b668a02d83b4a177d01067`, pushed to `origin/task/ARCH-021-COMMERCE-019`.
- Implementation worktree: clean after the implementation commit.
- Final parent report commit: recorded after this report edit and pushed to `origin/task/ARCH-021-COMMERCE-019`.
- Parent worktree: clean after the parent report commit.
- Push parity: implementation and parent report pushes passed.

#### Deviations
- None from the Attempt 3 correction contract.

#### Assumptions
- The existing mocked `requireStudioPlatformRole('ADMIN')` seam is the accepted test boundary; this proof does not introduce a second authorization path or fake compiler module.

#### Unresolved Issues
- None task-owned.

#### Architectural Concerns
- None.

## Architect Review

### Review Status
Changes Requested — Attempt 2

### Review Notes

#### Attempt 2 review — 2026-09-25

Reviewed implementation `47fa255b` and the submitted Attempt 2 report against the
complete Attempt 1 correction contract.

The substantive Attempt 1 defects are corrected and must be preserved:

- structurally valid EXTERNAL_HTTP `DIRECT`, `OBJECT/LIST` and `JAVASCRIPT` response
  modes now reach the exact Phase 3 `LIVE_TEST_REQUIRED` gate;
- validation issue `path`, `code` and `message` values are truncated on Unicode
  code-point boundaries and remain <= 512 UTF-8 bytes without replacement-character
  truncation;
- known `mapToolArguments()` validation TypeErrors map to `INVALID_INPUT` rather than
  `INTERNAL_ERROR`;
- the common focused command executes PLATFORM_ADMIN, PLATFORM_SUPER_ADMIN, all three
  merchant-role denials and development bypass, including proof that bypass performs
  no auth/platform/merchant identity lookup;
- executable lifecycle tests preserve the exact `LIVE_TEST_REQUIRED` code/message for
  EXTERNAL_HTTP and SHOPIFY_ADMIN_GRAPHQL, and the Studio translation preserves the
  identifiable code;
- an already-published revision remains readable history;
- ARCH-020 sample/publication receipts do not satisfy the Phase 3 publication gate;
- submitted `tsconfig.tsbuildinfo` contains no semantic diagnostic in the task-owned
  COMMERCE-019 source/test surfaces;
- the Attempt 2 Completion Report contains the launcher-resolved worktree,
  synchronization, claim, recursive submodule and database-submodule evidence.

Attempt 2 is not accepted only because A1-R6 explicitly required a **focused
spy/assertion** proving the common authoring validation layer performs zero provider
I/O/domain-compiler invocation. The submitted report records a source audit, but the
focused tests do not execute such a proof.

The following is the complete Attempt 3 correction contract. It is intentionally
proof/report-only. Do not redesign runtime/publication behavior and do not begin
COMMERCE-021/022/023/024.

##### A2-R1 — add one focused zero-provider-I/O proof

Create:

```text
tests/tool-authoring-no-provider-io.test.ts
```

The test must invoke the real:

```text
validateToolDefinitionAction(...)
validateToolArgumentsAction(...)
```

from:

```text
src/commerce/tool-authoring/server-actions.ts
```

Use the existing Vitest mock seam for `requireStudioPlatformRole` so the calls execute
as an admitted platform ADMIN without requiring real auth/database access.

The test MUST:

1. install a `globalThis.fetch` spy that throws if called;
2. invoke `validateToolDefinitionAction()` with one valid canonical definition;
3. invoke `validateToolArgumentsAction()` with one valid definition/input pair;
4. assert both actions return their expected non-provider results;
5. assert the fetch spy was never called.

Also add a deterministic dependency-boundary assertion over:

```text
src/commerce/tool-authoring/contracts.ts
src/commerce/tool-authoring/server-actions.ts
```

proving those common-layer files do **not** import or reference any of:

```text
src/commerce/code-request
createCodeRequestProcessor
src/commerce/external-http
createExternalHttpExecutionPort
createNodeHttpsTransport
Shopify Admin compiler implementation
src/commerce/integration/backend
prisma.session
/admin/api/
```

Do not invent a fake COMMERCE-018 compiler module merely for this proof. COMMERCE-018
may not yet exist in the current branch; absence from the common-layer dependency
boundary is the intended invariant.

The dependency-boundary assertion may use `readFileSync` because it proves an import /
reference invariant. The fetch assertion must remain executable and must invoke the
real Server Actions.

Do not apply this audit to `src/commerce/external-publication/index.ts`: that accepted
ARCH-020 boundary may compile response JavaScript for structural publication
validation. A2-R1 concerns the new **common Tool authoring layer** only.

##### A2-R2 — keep the entire Attempt 2 focused contract green

Update:

```text
test:arch021-tool-authoring-common
```

so it also executes:

```text
tests/tool-authoring-no-provider-io.test.ts
```

Retain every current focused file. Do not remove any existing authorization,
publication, lifecycle, Studio, UTF-8 or `INVALID_INPUT` proof.

Then run exactly:

```bash
npm run test:arch021-tool-authoring-common
npm run test:arch021-tool-authoring-validation
npm run test:arch020-external-publication
npm run test -- --run \
  tests/auth-role-requirements.test.ts \
  tests/auth-permissions.test.ts
npm run lint
npm run typecheck
git diff --check
```

All focused tests must execute with zero skips.

No diagnostic in:

```text
src/commerce/tool-authoring/**
tests/tool-authoring-validation.test.ts
tests/tool-authoring-server-actions.test.ts
tests/tool-authoring-no-provider-io.test.ts
```

may be classified as baseline.

No runtime source change is required for Attempt 3 unless the new executable
zero-provider-I/O proof fails and demonstrates a task-owned defect.

##### A2-R3 — reconcile Attempt 3 report metadata

The final user handoff for Attempt 2 identifies parent report commit `8be86bae`, while
the embedded Completion Report currently records `93b3bdef`. The review archive
contains no Git metadata with which to reconstruct that relationship.

Attempt 3 must record the exact final parent report commit that is actually pushed,
along with the fresh Attempt 3 prepared-execution packet:

```text
parent worktree path
implementation worktree path
parent branch = task/ARCH-021-COMMERCE-019
implementation branch = task/ARCH-021-COMMERCE-019
start-of-attempt parent synchronization
start-of-attempt implementation synchronization
Attempt 3 claim evidence / commit
recursive submodule materialization
database submodule commit
implementation commit
final parent report commit
push parity
clean parent worktree
clean implementation worktree
```

Also reconcile the human-readable `## Validation` text/counts to the current focused
commands/results instead of retaining the older Attempt 1 counts.

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
real common Server Actions execute with fetch spy untouched
AND common-layer dependency audit shows no request-JS/Admin/provider transport/session dependency
AND every Attempt 2 correction proof remains green
AND all focused tests execute with zero skips
AND no task-owned type diagnostic remains
AND the fresh Attempt 3 launcher/report evidence is complete
```

Then push both branches, return control to `moda_architect`, and STOP.

Do not start COMMERCE-021, COMMERCE-022, COMMERCE-023 or COMMERCE-024.

#### Historical Attempt 1 review

#### Attempt 1 review — 2026-09-25

Reviewed implementation `a20397d3` and parent report `80ca697e` against the exact
COMMERCE-019 task contract and ARCH-021 Phase 3 invariants.

The implementation direction is correct and must be preserved:

- the bounded `ToolAuthoringValidation` / `ToolAuthoringActionResult<T>` contracts
  exist under `src/commerce/tool-authoring/`;
- the new validation Server Actions call the accepted
  `requireStudioPlatformRole('ADMIN')` helper directly;
- there is no new authorization matrix or browser/provider credential path;
- synthetic ARCH-020 external-publication receipts no longer satisfy the Phase 3
  gate;
- `LIVE_TEST_REQUIRED` is carried as an identifiable lifecycle/Studio failure code;
- Shopify Admin publication is fail-closed before provider I/O;
- common validation performs no live provider request;
- submitted typecheck metadata contains no semantic diagnostic in the COMMERCE-019
  task-owned source/test files.

Attempt 1 is not accepted because the exact R1/R3/R4/R7 contracts still have
observable gaps. The following is the complete Attempt 2 correction contract. Do
not implement COMMERCE-023/024 domain validators or Phase 4 live testing.

##### A1-R1 — every structurally valid EXTERNAL_HTTP response mode must reach LIVE_TEST_REQUIRED

Change:

```text
src/commerce/external-publication/index.ts
tests/external-publication.test.ts
```

ARCH-021 Phase 3 explicitly includes all three EXTERNAL_HTTP response-processing
modes:

```text
DIRECT
OBJECT/LIST
JAVASCRIPT
```

and R4 requires an otherwise structurally valid Phase 3 EXTERNAL_HTTP DRAFT to fail
publication with exactly:

```text
code: LIVE_TEST_REQUIRED
path: /liveTest
message: Run a successful live tool test for the current saved revision before publishing.
```

The current `validateForPublication()` still contains:

```ts
if (processing.kind === 'DIRECT')
  return invalid([
    issue('/execution/responseProcessing', 'DIRECT processing is not publishable yet')
  ]);
```

That is no longer valid under ARCH-021 Phase 3.

Remove that historical ARCH-020 DIRECT prohibition. Preserve all structural
definition, saved-definition identity, connection metadata, JavaScript compilation
and response-template validation performed before the gate.

Add an active regression constructing a canonical, structurally valid
`EXTERNAL_HTTP` definition with:

```ts
responseFormat: { mode: 'JSON', ... }
responseProcessing: { kind: 'DIRECT' }
```

and assert `validateForPublication()` returns exactly the `LIVE_TEST_REQUIRED`
envelope above.

Do not make DIRECT publishable. It must be blocked by `LIVE_TEST_REQUIRED`, not by
`INVALID_DEFINITION`.

##### A1-R2 — enforce the 512-byte limit by UTF-8 bytes, including multibyte boundaries

Change:

```text
src/commerce/tool-authoring/contracts.ts
tests/tool-authoring-validation.test.ts
```

The current implementation performs:

```ts
new TextDecoder().decode(bytes.slice(0, 512))
```

When byte 512 cuts a multibyte code point, `TextDecoder` inserts U+FFFD and the
returned UTF-8 string can become 513/514 bytes. This violates R1.

Replace `bounded()` with deterministic code-point-safe UTF-8 truncation:

```text
for each Unicode code point:
  compute encoded byte length
  append only when total remains <= 512
```

or another implementation that produces the same observable guarantee.

Do not truncate by UTF-16 code units.

Add exact regressions for `path`, `code` and `message` containing multibyte input
near the boundary. At minimum prove:

```ts
new TextEncoder().encode(resultField).byteLength <= 512
```

for input equivalent to:

```text
"x" repeated 510 times + "😀"
```

Also prove the returned string does not end with the replacement character `�`
introduced solely by truncation.

Retain the 32-issue cap.

##### A1-R3 — known argument-mapping failures are INVALID_INPUT, not INTERNAL_ERROR

Change:

```text
src/commerce/tool-authoring/server-actions.ts
tests/tool-authoring-server-actions.test.ts   # create if absent
```

`mapToolArguments()` intentionally rejects invalid authoring arguments with
validation-domain `TypeError`s such as:

```text
Missing mapped input
Invalid external mapped scalar
Validated input must be an object
```

Those are known authoring validation failures. R3 requires known validation failures
to return:

```ts
{
  kind: 'error',
  code: 'INVALID_INPUT',
  retryable: false
}
```

The current action handles `ZodError` as `INVALID_INPUT` but sends mapping
`TypeError` through `toolAuthoringActionError()`, which returns `INTERNAL_ERROR`.

Wrap only the definition/argument parsing/mapping boundary needed to distinguish
these expected validation failures. Do not convert arbitrary unexpected application
`TypeError`s globally into `INVALID_INPUT`.

Add Server Action regressions that invoke the real action with
`requireStudioPlatformRole` mocked/controlled and prove:

```text
invalid definition schema -> INVALID_INPUT
invalid input schema value -> INVALID_INPUT
missing mapped input      -> INVALID_INPUT
invalid external scalar   -> INVALID_INPUT
```

No case above may produce `INTERNAL_ERROR` or `kind:'unknown'`.

##### A1-R4 — prove the authorization contract through the actual accepted hierarchy

The focused common validation script must directly prove every R7 authorization
bullet, not only inspect source text.

Update/add focused tests so `npm run test:arch021-tool-authoring-common` proves:

```text
PLATFORM_ADMIN       -> allowed
PLATFORM_SUPER_ADMIN -> allowed
MERCHANT_ADMIN       -> denied
MERCHANT_EDITOR      -> denied
MERCHANT_VIEWER      -> denied
development bypass   -> allowed as PLATFORM_SUPER_ADMIN
```

Use the accepted COMMERCE-027 `requireStudioPlatformRole('ADMIN')` boundary. Do not
create another role matrix.

The development-bypass proof must also prove that platform/merchant database identity
lookups are not performed after the development bypass has resolved.

It is acceptable for the common script to run an existing authorization test file in
addition to the COMMERCE-019-specific test files, but all six cases above must execute
under the `test:arch021-tool-authoring-common` command.

##### A1-R5 — replace static gate-source checks with executable lifecycle/Studio propagation proof

Add focused executable coverage for both canonical Phase 3 kinds:

```text
EXTERNAL_HTTP
SHOPIFY_ADMIN_GRAPHQL
```

For each structurally valid DRAFT, prove publication produces the exact lifecycle
code/message:

```text
LIVE_TEST_REQUIRED
Run a successful live tool test for the current saved revision before publishing.
```

Also prove the existing Studio translation boundary preserves the identifiable code:

```ts
{
  kind: 'unavailable',
  code: 'LIVE_TEST_REQUIRED',
  message: 'Run a successful live tool test for the current saved revision before publishing.'
}
```

Do not satisfy this item with `readFileSync(...).toContain(...)` assertions alone.

The test may extend an existing lifecycle/Studio service test rather than creating a
new fixture framework.

Also add explicit proof that a revision which is already `PUBLISHED` remains readable
history and is not retroactively changed/unpublished by this Phase 3 validation
policy.

##### A1-R6 — retain synthetic-receipt rejection and zero-provider-I/O behavior

Keep the existing external-publication regressions proving that a successfully
recorded synthetic visual/code sample receipt still results in
`LIVE_TEST_REQUIRED`.

Add/retain a focused spy/assertion showing the common authoring validation layer does
not invoke:

```text
request-JavaScript processor/compiler
Shopify Admin compiler
external HTTP transport
Shopify transport/session
```

COMMERCE-019 defines the common contract only. COMMERCE-023/024 own the independent
domain validators.

##### A1-R7 — deterministic validation commands

Update `test:arch021-tool-authoring-common` so it executes every focused
COMMERCE-019 contract test required above.

Then run exactly:

```bash
npm run test:arch021-tool-authoring-common
npm run test:arch020-external-publication
npm run test -- --run \
  tests/auth-role-requirements.test.ts \
  tests/auth-permissions.test.ts
npm run lint
npm run typecheck
git diff --check
```

The common focused command must have zero skipped tests.

No TypeScript diagnostic in these task-owned surfaces may be classified as baseline:

```text
src/commerce/tool-authoring/**
src/commerce/external-publication/contracts.ts
src/commerce/external-publication/index.ts
src/commerce/publication/lifecycle.ts
src/commerce/integration/studio/services.ts
src/studio/contracts.ts
tests/tool-authoring-validation.test.ts
tests/tool-authoring-server-actions.test.ts
tests/external-publication.test.ts
```

Other diagnostics may remain documented only when their exact file/error is unrelated
to COMMERCE-019.

##### A1-R8 — record the exact Attempt 2 launcher/worktree packet

The submitted Attempt 1 Completion Report records commits and validation but does not
record the mandatory prepared-execution packet.

Attempt 2 must record the exact launcher-provided:

```text
parent worktree path
implementation worktree path
parent branch = task/ARCH-021-COMMERCE-019
implementation branch = task/ARCH-021-COMMERCE-019
start-of-attempt parent synchronization
start-of-attempt implementation synchronization
Attempt 2 claim evidence / commit
recursive submodule materialization
database submodule commit
implementation commit
parent report commit
push parity
clean parent worktree
clean implementation worktree
```

Do not reuse/infer Attempt 1 values.

Before handoff set exactly:

```yaml
status: review
attempt: 2
executor: null
claimed_at: null
```

##### Attempt 2 stop condition

Return to architect review only when:

```text
DIRECT EXTERNAL_HTTP -> exact LIVE_TEST_REQUIRED
AND UTF-8 issue fields are <=512 bytes without replacement-character truncation
AND known argument mapping failures -> INVALID_INPUT
AND all six required authorization cases execute
AND executable EXTERNAL_HTTP + SHOPIFY_ADMIN lifecycle/Studio gate propagation passes
AND synthetic receipts still cannot satisfy the gate
AND zero provider I/O is proved
AND all required focused/regression suites pass
AND no task-owned type diagnostic remains
AND the exact Attempt 2 launcher/report packet is recorded
```

Then push both task branches, return control to `moda_architect`, and STOP.

Do not start COMMERCE-021, COMMERCE-022, COMMERCE-023 or COMMERCE-024.

### Reviewed Files

- `src/commerce/tool-authoring/contracts.ts`
- `src/commerce/tool-authoring/server-actions.ts`
- `src/commerce/external-publication/contracts.ts`
- `src/commerce/external-publication/index.ts`
- `src/commerce/publication/lifecycle.ts`
- `src/commerce/integration/studio/services.ts`
- `src/studio/contracts.ts`
- `lib/auth/merchant-access.ts`
- `lib/auth/role-hierarchy.ts`
- `tests/tool-authoring-validation.test.ts`
- `tests/external-publication.test.ts`
- `tests/auth-role-requirements.test.ts`
- `tests/auth-permissions.test.ts`
- `package.json`
- submitted `tsconfig.tsbuildinfo`
- Attempt 1 Completion Report

### Validation Reviewed

Submitted evidence:

```text
authoring tests:             6 passed
external publication tests: 12 passed
authorization tests:        10 passed
targeted ESLint:            PASS
git diff --check:           PASS
full typecheck:             unrelated baseline diagnostics reported
```

Independent inspection confirms no semantic TypeScript diagnostic in the
COMMERCE-019 task-owned source/test files.

However, the submitted focused test does not execute all R7 bullets and relies on
source-text assertions for the lifecycle gate. It also does not cover UTF-8
multibyte truncation, known `mapToolArguments()` validation errors, DIRECT-mode
publication, or executable Studio propagation.

### Architecture Conformance

Changes Requested. The common authorization/result direction conforms, but the exact
R1 byte bound, R3 validation classification and R4 all-mode publication gate are not
yet satisfied. No cross-repository or schema redesign is required.

### Follow-up

Return this same task through `/moda-task ARCH-021-COMMERCE-019` for Attempt 2.
COMMERCE-023 and COMMERCE-024 remain dependency-gated until COMMERCE-019 is
architect-accepted Complete. Do not start downstream work.
