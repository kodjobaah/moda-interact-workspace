---
id: ARCH-021-COMMERCE-098
architecture_id: ARCH-021
title: Live-test Policy Operation Tool candidates through DefinitionExecutor
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 80
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-021-COMMERCE-096
enables:
  - ARCH-021-COMMERCE-099
created: 2026-09-29
updated: 2026-09-29
---
# Live-test Policy Operation Tool candidates through DefinitionExecutor

## Architecture

Architecture ID:

`ARCH-021`

Architecture document:

`docs/architecture/ARCH-021-commerce-agent-configuration-live-studio-authoring.md`

Coordinator:

`moda_architect`

## Objective

Add one non-durable Commerce Studio live-Test backend for a complete `POLICY_OPERATION` Tool candidate that executes through the normal production `DefinitionExecutor` and registered policy-operation adapter, returning the normal rendered Tool result without bypassing tenant/grant/runtime validation or creating Tool publication proof.

## Context

COMMERCE-096 makes policy registrations canonical and self-describing. The production executor already supports `POLICY_OPERATION`, including argument mapping, operation input validation, adapter execution, output validation, deadline handling and Result Template rendering.

Studio needs a safe candidate-Test boundary equivalent in principle to the accepted External HTTP and Shopify Admin live-Test paths. This task implements the backend only; COMMERCE-099 owns Test-tab UI/freshness integration.

## Scope

Primary implementation boundaries:

```text
src/commerce/tool-authoring/<policy-operation live-test domain service>
src/studio/tools/<policy-operation live-test server action>
src/commerce/integration/backend.ts or existing Studio execution port exposure
focused domain/server-action tests
```

## Out of Scope

- Policy Operation authoring UI; COMMERCE-097 owns it.
- Test-tab UI/state integration; COMMERCE-099 owns it.
- Direct invocation of policy adapters from a Server Action.
- A Studio-only policy executor.
- Durable Tool/ToolRevision writes.
- Publication proof or release membership.
- Implementing new policy operations, including `merchantKnowledge.lookup`.
- Changing existing Policy Operation business logic.

## Requirements

### R1 — exact candidate-Test request contract

Expose one ADMIN-authorized server action/domain boundary equivalent to:

```ts
type PolicyOperationLiveTestInput = {
  definition: CommerceToolDefinition;
  arguments: Record<string, unknown>;
  shopId: string;
};
```

The request must reject before execution when:

```text
definition does not parse through CommerceToolDefinitionSchema
definition.execution.kind !== POLICY_OPERATION
operation/version is not currently registered
shopId is empty/invalid for the selected Studio context
arguments is not a JSON object
serialized arguments exceeds the existing authoring Test input bound (64 KiB unless the accepted common contract has a stricter value)
```

Do not accept shop domain, Shopify token, authorization header, conversation grant id, release id or provider credentials from the browser.

### R2 — selected shop is resolved/authorized server-side

The supplied `shopId` identifies the Studio-selected shop only. The server must apply the existing Studio authorization/selected-shop boundary and construct trusted runtime context server-side.

The browser must not be able to replace trusted:

```text
shop domain
offline session/access token
conversation/tool grant authority
policy credentials/environment
```

with candidate data.

### R3 — execute through the normal DefinitionExecutor

The Test path is exactly:

```text
validated Studio Test request
    -> build bounded trusted test AuthorizedToolCall/context using existing Studio test conventions
    -> existing DefinitionExecutor.execute(...)
    -> registry resolve(operation, operationVersion)
    -> existing mapToolArguments(...)
    -> registration inputValidator
    -> registered PolicyOperationAdapter
    -> registration outputValidator
    -> existing renderDefinitionResult(...)
    -> bounded Test result
```

MUST NOT:

```text
call registration.adapter.execute directly from the Server Action
reimplement mapToolArguments
skip input/output validation
use a fake provider-specific renderer
invent a second response-template implementation
```

### R4 — candidate execution is non-durable

A successful or failed Test performs no write to:

```text
CommerceTool
CommerceToolRevision
CommerceRelease
CommerceConversationGrant
publication proof/audit state that would make the candidate publishable by itself
```

Normal bounded operational telemetry/audit that already applies to Studio live-Test is allowed, but Test must not mutate authoring lifecycle state in PostgreSQL.

### R5 — operation/version is exact and registry-owned

The candidate is executable only when:

```text
definition.execution.operation
+
definition.execution.operationVersion
```

resolve to the current C096 registration.

Unknown/stale/unregistered pairs return a bounded unavailable/incompatible result. Do not fall back to another version and do not choose an operation by Tool name.

### R6 — return the canonical rendered outcome and bounded diagnostics

Return the normal result required by the existing Test UI pattern, including at minimum:

```text
success/failure status
normal CommerceToolResult status/code/retryable fields where applicable
renderedText produced by DefinitionExecutor
bounded diagnostics suitable for Studio
```

Do not return:

```text
adapter/function references
raw credentials
server environment
R2/Shopify/provider secrets
trusted runtime context
```

### R7 — deterministic error classes

Focused tests must prove at least:

```text
invalid candidate definition -> validation failure, no adapter call
non-POLICY_OPERATION candidate -> provider mismatch, no adapter call
unregistered operation/version -> unavailable/incompatible, no adapter call
invalid mapped arguments -> INVALID_INPUT, no adapter call
registered adapter business failure -> canonical CommerceToolResult error
valid registered operation -> canonical rendered success
aborted/deadline call -> canonical DEADLINE behaviour
```

Use existing canonical result/error codes; do not invent Policy-specific business error codes when an existing CommerceToolResult code applies.

## Work Items

- [x] Add the non-durable Policy Operation candidate-Test domain boundary.
- [x] Add the ADMIN-authorized Studio Server Action using the selected-shop authorization pattern.
- [x] Route execution exclusively through `DefinitionExecutor` and C096 registrations.
- [x] Return canonical rendered result/diagnostics without lifecycle writes.
- [x] Add deterministic success/failure/security/no-write tests.
- [x] Record exact validation evidence in the Completion Report.

## Interfaces / Contracts

Consumes:

- canonical `CommerceToolDefinition` / `POLICY_OPERATION` contract;
- COMMERCE-096 policy-operation registry/descriptor registration;
- existing Studio authorization and selected-shop context;
- production `DefinitionExecutor`.

Produces the Commerce-local live-Test action consumed by COMMERCE-099.

## Dependencies

- `ARCH-021-COMMERCE-096`

## Enables

- `ARCH-021-COMMERCE-099`

## Acceptance Criteria

- [x] A valid Policy Operation candidate can be live-tested without persisting it.
- [x] Candidate execution goes through `DefinitionExecutor`; the Server Action never calls an adapter directly.
- [x] The exact registered operation/version is required; there is no fallback or Tool-name inference.
- [x] Browser input cannot supply trusted shop credentials, grant authority or operation secrets.
- [x] Invalid mapped input is rejected through the canonical runtime contract before adapter execution.
- [x] Successful output is validated and rendered through the canonical runtime path.
- [x] Test creates no Tool revision/publication/release/grant state.
- [x] Focused failure cases are deterministic and bounded.
- [x] Existing runtime Policy Operation tests show no regression.

## Validation

- [x] Focused Policy Operation live-Test domain tests.
- [x] Focused Studio Server Action authorization/security tests.
- [x] Explicit no-durable-write assertion.
- [x] Targeted TypeScript diagnostics for changed files.
- [x] Targeted ESLint for changed files.
- [x] `git diff --check`.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete, set the task to `review`, complete the Completion Report, return control to `moda_architect` and STOP. Do not begin COMMERCE-099.

## Implementation Notes

Follow the accepted External/Shopify live-Test architecture for authorization, cancellation and result presentation where equivalent. Do not copy provider-specific request/response logic that `DefinitionExecutor` already owns.

## Completion Report

### Status

Ready for Architect Review.

### Files Changed

Implementation changes are in `moda-interact-commerce` on `task/ARCH-021-COMMERCE-098`:

- `src/commerce/tool-authoring/policy-operation-live-test.ts`
- `src/studio/tools/policy-operation-live-test-server-actions.ts`
- `tests/policy-operation-live-test.test.ts`
- `tests/policy-operation-live-test-action.test.ts`

### Work Completed

- Added a bounded Policy Operation candidate-Test domain service. It strictly parses the request, validates JSON-object arguments against the existing 16 KiB live-Test bound, parses the canonical Commerce Tool definition, requires `POLICY_OPERATION` and an exact current C096 registry entry, then resolves and verifies the selected shop server-side.
- The service constructs a per-run trusted test `AuthorizedToolCall` using only the resolved shop ID/domain, server environment and fresh synthetic test identities; the browser cannot provide shop domain, credentials, grant/release IDs, or execution context. It applies the existing policy provider-call budget and a maximum 10-second deadline.
- Candidate execution is delegated only to `backend.execution` (`DefinitionExecutor`), which retains canonical argument mapping, policy input/output validation, adapter dispatch, result validation, and Result Template rendering. Timeout aborts the call and asks the same executor to return its canonical expired-call result. The Studio service does not invoke adapters or implement result rendering.
- Returned data contains only bounded stage diagnostics and the canonical status/code/retryable outcome with at most 4 KiB of rendered text. It omits structured provider data, credentials, and trusted context.
- Added an ADMIN-authorized Server Action following the Shopify Admin live-Test selected-shop pattern. It supplies the production execution port and registry and resolves the requested shop through `createCommerceStudioServices`; the action has no publication/lifecycle dependency.
- Tests cover invalid definitions, non-policy provider mismatch, unavailable registration, strict request shape, non-JSON and oversized arguments, invalid mapped input before adapter dispatch, successful canonical rendering, adapter business errors, aborted/deadline behavior, selected-shop denial and identity binding, output bounds, ADMIN authorization, and absence of publication writes.

### Validation Results

- `./node_modules/.bin/vitest run tests/policy-operation-live-test.test.ts tests/policy-operation-live-test-action.test.ts tests/definition-execution.test.ts tests/recommendation-contract.test.ts --reporter=dot` — 4 files passed, 27 tests passed.
- Broader adjacent check including C098, DefinitionExecutor/recommendation, Shopify Admin live-Test and External HTTP live-Test suites — 7 of 8 files passed (53 tests passed); 4 tests failed in the existing `tests/shopify-admin-live-test.test.ts` domain suite, where candidate validation failed before shop/provider stages. No Shopify Admin source/test was changed by C098.
- `./node_modules/.bin/eslint` on all four changed files — passed without warnings.
- VS Code/Pylance diagnostics on all four changed files — no errors.
- `git diff --check` — passed.
- `npm run typecheck` initially exposed the expected missing generated Prisma Client after `npm ci` skipped package install scripts, plus unrelated repository diagnostics. Generated the local Client with `./node_modules/.bin/prisma generate --schema database/prisma/schema.prisma`, then reran the declared typecheck; it completed with no diagnostics. No schema or submodule pointer changed.
- `npm ci` used the committed lockfile in the dedicated implementation worktree. npm reported existing peer/deprecation/audit warnings and did not run unapproved install scripts; generated dependency state remains ignored/untracked.

### Deviations

The canonical Commerce definition schema fixes currently supported policy operation versions to `1.0.0`; unsupported versions are therefore rejected during definition validation before registry lookup. A known operation/version absent from the active registry returns `INCOMPATIBLE_VERSION`; there is no version fallback.

### Assumptions

The existing 16 KiB Shopify Admin live-Test request bound is the stricter common Studio authoring Test argument limit. A resolved selected shop must retain the requested `shopId` exactly; synthetic per-run identifiers are internal preview context only and are never returned or persisted.

### Unresolved Issues

The adjacent existing Shopify Admin live-Test domain suite had four candidate-validation/shop/provider-stage failures in the broader regression run. This task does not modify that flow; the required Policy Operation runtime and C098 suites pass. Recorded for Architect review rather than changing out-of-scope Shopify Admin code.

### Architectural Concerns

Policy adapters require a complete `AuthorizedToolCall`. The service creates only a bounded server-side preview context with synthetic turn/grant/release/tool identities; it never accepts those values from the browser or persists them. Runtime production authorization remains owned by the MCP authorization path and is not replaced by this Test boundary.

### Prepared Execution Evidence

- Launcher returned `prepared_execution: true`, `execution_state: claimed`, dependency gate passed (`ARCH-021-COMMERCE-096` complete), and recursive submodules ready.
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-021-COMMERCE-098`, `task/ARCH-021-COMMERCE-098`; prepared head `e61872ff5a853d4195b09cb7844a4ed155f298a3`.
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-021-COMMERCE-098`, `task/ARCH-021-COMMERCE-098`; prepared head `071cfd7be180211df660ba158c0879d80c6ed27f`.
- Attempt 1 claim committed and pushed as `391cba10625731ec267dc1a0e1df179f9b9b08e2` by `copilot` at `2026-09-29T17:35:53Z`.
- Both task worktrees were created at their canonical launcher paths. The implementation branch began at the prepared launcher head; when preparing this completion, its Commerce `origin/main` had advanced five commits beyond that base and no remote Commerce C098 task ref was advertised. Implementation commit `1cf1744bf211e88e3a74e83867fdb5dc688b33ab` was pushed explicitly to `origin/refs/heads/task/ARCH-021-COMMERCE-098`, not to `main`. Parent report commit `c79da454b163e7294265995509615f8d0232278b` was pushed to its mirrored `origin/task/ARCH-021-COMMERCE-098` branch. Recursive `database` submodule initialized at `e9fb60221f1532205650154dfff2aadb6270b14c`.
- Both task worktrees are clean and their task refs match their pushed commits. No main merge, other task, submodule pointer or Architect Review section is changed.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 1 is accepted.

C098 implements the intended non-durable Policy Operation Studio Test boundary without introducing a second policy executor or bypassing the accepted C096 registry/runtime contract.

The submitted implementation satisfies the architectural requirements:

- the Server Action requires the existing Studio `ADMIN` role before backend/service access;
- browser input is a strict candidate/arguments/shop-id object and cannot supply shop domain, access token, Authorization header, grant/release identities or policy credentials;
- the requested Studio shop is resolved server-side through the existing Commerce Studio service and the returned shop identity must match the requested `shopId`;
- candidate parsing uses the canonical `CommerceToolDefinitionSchema`;
- only `POLICY_OPERATION` candidates are admitted;
- the exact `(operation, operationVersion)` must resolve in the active C096 registry before execution;
- there is no version fallback and no Tool-name inference;
- Test arguments must be bounded JSON object data and use the accepted stricter 16 KiB Studio Test limit;
- execution delegates through `DefinitionExecutionPort` / production `DefinitionExecutor`;
- the C098 service does not map Tool arguments, invoke a policy adapter directly, validate adapter output independently or render Result Templates itself;
- `DefinitionExecutor` therefore remains authoritative for argument mapping, registration input validation, adapter dispatch, registration output validation, canonical Commerce result semantics and Result Template rendering;
- the preview call carries server-created synthetic Tool/grant/release/turn identities and `purpose: "preview"` only; those identities are neither browser-controlled nor persisted;
- provider-call budget and a bounded 10-second Test deadline are applied;
- timeout aborts the in-flight call and obtains the canonical `DEADLINE` result through the same executor; the expired second executor entry is rejected at the executor deadline boundary before another adapter dispatch;
- returned output is bounded to safe stage diagnostics plus canonical `status` / `code` / `retryable` and at most 4 KiB of rendered text;
- credentials, trusted runtime context, provider data and synthetic authorization identities are not returned; and
- neither the domain service nor the Server Action writes Tool, ToolRevision, release, grant or publication-proof/lifecycle state.

A Policy Operation that depends on an existing checkout-recovery row may legitimately return canonical `NOT_FOUND` in this Test boundary because C098 intentionally creates a fresh synthetic preview recovery identity. That is correct fail-closed behavior: Studio Test must not fabricate or borrow a production recovery/grant identity merely to manufacture a successful business result. COMMERCE-099 may present that canonical outcome, but must not reinterpret it as a C098 transport failure.

The four failures in the broader adjacent Shopify Admin live-Test domain suite do not block C098. C098 changes only the Policy Operation live-Test service/action and their focused tests; it does not change the Shopify Admin live-Test implementation or fixtures. The required C098 packet plus DefinitionExecutor/recommendation coverage passed, and changed-file diagnostics/typecheck are clean.

### Reviewed Files

- `src/commerce/tool-authoring/policy-operation-live-test.ts`
- `src/studio/tools/policy-operation-live-test-server-actions.ts`
- `tests/policy-operation-live-test.test.ts`
- `tests/policy-operation-live-test-action.test.ts`
- `src/commerce/execution/executor.ts` — consumed canonical execution boundary
- `src/commerce/execution/policy-operation-authoring.ts` — consumed C096 registration contract
- C098 Completion Report

### Validation Reviewed

Submitted Attempt 1 evidence:

- required focused packet: **4 files / 27 tests passed**;
- focused packet includes C098 domain/action plus DefinitionExecutor and recommendation-contract coverage;
- targeted ESLint on all four changed files: passed;
- changed-file diagnostics: clean;
- `git diff --check`: passed;
- after local Prisma Client generation, repository-declared `npm run typecheck`: completed without diagnostics;
- no Prisma schema or submodule pointer changed.

Broader adjacent packet:

- **53 tests passed**;
- 4 failures occurred only in the existing Shopify Admin live-Test domain suite at its candidate-validation/shop/provider expectations;
- no Shopify Admin source or test file is changed by C098, so those failures are recorded as adjacent baseline/integration drift rather than a C098 correction requirement.

Workflow evidence records implementation commit `1cf1744` pushed to the Commerce C098 task ref and a clean synchronized parent/implementation handoff. The Completion Report text names an earlier parent report commit while the final user handoff names `1654680`; this reporting-ref difference does not alter the submitted source/task content or acceptance result.

### Architecture Conformance

Conforms.

C098 is a thin Studio Test boundary over the existing production `DefinitionExecutor` and C096 policy registry. Runtime validation/business behavior remains production-owned, Studio authorization/shop selection remains server-owned, and candidate Test remains non-durable and separate from publication authority.

### Follow-up

C098 is Complete / Accepted — Attempt 1.

COMMERCE-099 remains Pending because it depends on both COMMERCE-097 and COMMERCE-098, and COMMERCE-097 is still Ready rather than Complete.

Do not begin COMMERCE-099 until COMMERCE-097 is architect-accepted Complete.
