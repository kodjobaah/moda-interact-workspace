---
id: ARCH-044-COMMERCE-006
architecture_id: ARCH-044
title: Reconcile deprecated Agent template validation and MCP extraction boundaries
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables: []
created: '2026-10-18'
updated: 2026-11-01
---

# Reconcile deprecated Agent template validation and MCP extraction boundaries

## Architecture

- Parent: `ARCH-044` — `docs/architecture/ARCH-044-commerce-baseline-stabilisation.md`.
- Repository: `moda-interact-commerce` (owner: `moda_commerce`).
- Baseline evidence: unchanged baseline `baseline-vitest.log` compared with ARCH-043 task run `typescript(20261018-183033)` on 2026-10-18. These are external validation artefacts, not committed files.
- Architecture relationship: this repairs pre-existing Commerce issues; it does not change the requirements of `ARCH-043-COMMERCE-002`.

## Objective

Bring two obsolete contract-boundary assertions into conformity with canonical runtime behavior while correcting any actual Agent template validation or embedded-MCP dependency violation.

## Context

Two baseline failures are independent signs of stale contract assertions: (1) `tests/agent-contract-validation.test.ts` expects `invalid_collection_path` for a missing collection inside `{% for %}`, but the canonical validator returned `invalid_result_path` plus `unsupported_template_construct`; and (2) `tests/commerce-mcp-extraction-boundary.test.ts` asserts `package.json.dependencies` must not contain `@modelcontextprotocol/sdk`, yet the package declares version `1.30.0`. The test also verifies embedded MCP routes/server are absent. We must establish whether this SDK remains legitimately used by current Commerce runtime or is a stray undeleted dependency before removing it.

## Scope

- Inspect `src/commerce/tool-authoring/agent-contract-validation.ts`, current Shared/Commerce Nunjucks/result-template path validators, related error-code consumers, and the two failing tests.
- Decide which validation error semantics are canonical; preserve stable typed errors and reject unknown/unsafe paths. Update the obsolete test only if canonical behavior is correct; otherwise fix the validator with proof.
- Trace `@modelcontextprotocol/sdk` imports from Commerce runtime, tooling and `package.json`/lockfile; check `ARCH-032` extraction contract and whether dependency is genuinely required, dev-only or obsolete.
- Correct the minimum dependency/test boundary needed while preserving the standalone MCP architecture and Shopify schema-generation tooling.

## Out of Scope

- No reintroducing an embedded Commerce MCP route/server or inlining standalone MCP source.
- No changes to published Shared contracts without a separate architecture decision; no unrelated dependency churn.

## Requirements

1. Validation must reject missing scalar or collection paths with stable bounded issue codes consistent with the authoritative runtime validator; no unchecked template code or sensitive parser detail.
2. Commerce must not resurrect an embedded MCP server, client execution path or API route. A dependency assertion must reflect verified imports/ownership rather than assume absence solely from a package name.
3. `@shopify/dev-mcp` remains a dev-only schema generation input; any packaging/dependency changes must retain documented reproducible schema sync.
4. Every corrected test must demonstrate the actual contract, not merely avoid the assertion.

### Work Items

- [x] Resolve and document `invalid_collection_path` versus `invalid_result_path` semantics with current validator and consumer evidence.
- [x] Verify exact typed-validation tests retain rejection behavior for unknown paths, unresolved loop aliases, resolved non-array loop sources and unsafe paths.
- [x] Inventory `@modelcontextprotocol/sdk` use and the current Commerce/MCP boundary; confirm the SDK is used only transitively by Shopify's dev-only schema-generation tooling.
- [x] Verify the boundary test and package manifest/lockfile reflect actual imports and ownership; no further dependency edit is justified.
- [x] Run the complete nearby contract and extraction regression tests.

## Interfaces / Contracts

Agent/response-template validation issue codes and result-path schema; ARCH-032 standalone MCP extraction boundary; existing `@modelcontextprotocol/sdk`/`@shopify/dev-mcp` package roles. Escalate missing Shared reusable functionality rather than duplicate it.

## Dependencies

None.

## Enables

None directly. The architecture-level integrated validation remains after all eight tasks.

### Acceptance Criteria

- [x] Both original failing tests pass with defensible source/contract evidence.
- [x] Unknown scalar/collection paths remain invalid and produce safe typed diagnostics.
- [x] No embedded MCP route/server or forbidden Commerce execution path is reintroduced.
- [x] Relevant SDK dependence is reconciled against actual imports and runtime ownership; package-lock is consistent if changed.
- [x] No scope expansion to new MCP product behavior.

### Validation

- [x] `npx vitest run tests/agent-contract-validation.test.ts tests/commerce-mcp-extraction-boundary.test.ts tests/result-template-authoring.test.ts tests/nunjucks-template.test.ts`.
- [x] `npm run typecheck`, `npm run schema:sync`, focused ESLint, `git diff --check` (typecheck result and unrelated diagnostic recorded below).
- [x] Verify package manifests/lockfile dependency ownership; no package or lockfile change was needed.

## Stop Condition

After all scoped Work Items and Acceptance Criteria are demonstrably satisfied, record exact commands and results in the Completion Report, set task `status: review`, clear execution claim as required by launcher protocol, return for architect review and **STOP**. Do not execute or close downstream work. If validation is blocked, record it accurately rather than claiming PASS.

## Implementation Notes

`invalid_result_path` and `unsupported_template_construct` are actual observed baseline outputs; `invalid_collection_path` was a historical expectation. Treat them as a contract decision, not a string-replacement exercise. The package currently declares SDK 1.30.0; the snapshot alone does not prove whether it is required at runtime.

### Exact failing tests

- `tests/agent-contract-validation.test.ts` — `rejects unknown scalar paths and non-list items paths`.
- `tests/commerce-mcp-extraction-boundary.test.ts` — `does not ship an embedded MCP route or server, and keeps only a private thin live client`.

## Completion Report

### Status

Accepted and Complete — Attempt 1

### Files Changed

No implementation source, test, package manifest or lockfile files changed in this attempt; the prepared Commerce snapshot already contains the behavior and regression assertions required by this task. This task definition is the only intended parent-worktree change.

### Work Completed

Confirmed the canonical validator delegates Agent response-template validation through `validateResponseTemplateAuthoring` to the bounded Nunjucks AST validator. Unknown paths, including a missing collection path, resolve as `invalid_result_path`; the attempted loop alias remains unbound and is reported as `unsupported_template_construct`. `invalid_collection_path` is reserved for a path that resolves to a non-array schema (the test covers an existing object used as a loop source). Unsafe paths remain rejected with bounded typed issues. The deprecated compatibility adapter preserves these canonical issues.

Verified the extraction boundary against current code and dependency state: the Commerce manifest has no direct `@modelcontextprotocol/sdk` dependency; source under `app/`, `lib/`, `src/` and `scripts/` has no SDK imports; the only installed SDK is nested under dev-only `@shopify/dev-mcp@1.15.4`. The boundary test also checks the embedded route/server/executor are absent and retained local, private-live-client and fixture flows remain present. Shopify schema synchronization succeeds using the pinned dev package, so that dev-only dependency remains necessary.

Both original failing test identities and neighboring result-template/Nunjucks contract tests pass. No validator behavior change, dependency removal or test weakening was needed because the prepared snapshot already expresses the verified contract.

### Validation Results

Environment: macOS, Node/npm selected from the workspace toolchain; `npm ci` installed 905 packages from the existing lockfile. npm reported 44 audit findings (27 moderate, 16 high, 1 critical); no dependency changes were made. Install scripts were awaiting approval, so the Prisma client was generated directly from the already-initialized pinned schema before the final typecheck.

| Command | Result |
|---|---|
| `npx vitest run tests/agent-contract-validation.test.ts tests/commerce-mcp-extraction-boundary.test.ts tests/result-template-authoring.test.ts tests/nunjucks-template.test.ts` | PASS, 4 files, 26 tests. |
| `npm run schema:sync` | PASS; Shopify Admin `2026-07` artifact matched the pinned `@shopify/dev-mcp@1.15.4` source (SHA-256 `2b507dc1f74c6157e0eb98500db0f3c3e238d69eaf0d98fd7657ac7ed3f6900b`). |
| `npm ls @modelcontextprotocol/sdk --all` | PASS; only `@shopify/dev-mcp@1.15.4 -> @modelcontextprotocol/sdk@1.29.0` is present. |
| `npx prisma generate --schema database/prisma/schema.prisma` | PASS; generated Prisma Client v6.19.3 from the pinned database submodule schema. |
| `npm run typecheck` | FAIL with one unrelated TS2345 at `tests/system-commerce-tool-sync.test.ts:305`: `{}` omits required `NODE_ENV` from Next.js `ProcessEnv`. Initial generated-client errors disappeared after Prisma generation. |
| Focused `npx eslint` over the Agent validator, Nunjucks/result-template validators and the four focused tests | PASS, no diagnostics. |
| `git diff --check` | PASS. |

The focused validation covers both originally failing tests and the neighboring contract suites. No full repository test suite was run for this bounded task.

### Worktree / Synchronisation Evidence

Launcher preparation packet: canonical workspace root `/Users/kwadwoadomafriyie/project/moda-interact-workspace`; parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-044-COMMERCE-006`, branch `task/ARCH-044-COMMERCE-006`, prepared head `22de3c80c93f2a09b9839bdedb18dc9649dd6321`; implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-044-COMMERCE-006`, branch `task/ARCH-044-COMMERCE-006`, head `15d505ef0f84e8cab57af43dee0d78a83d969f93`.

The launcher reported parent remote-task fast-forward `not-needed`, parent `origin/main` already current before claim and incorporated during final sync; implementation remote-task fast-forward `not-needed`, implementation `origin/main` already current. Claim Attempt 1 was committed and pushed as `1f8a068b179f497d02f5eef7fb8002705070d4b2`; final parent sync head was `405aa38541cfc613871edd5cd487f69c86f0510d`. Recursive `git submodule sync` and `git submodule update --init` passed; `database` is initialized at `af77c594ecbfc78c26d01c0021a090830884bbff`. The shared workspace checkout was not switched or mutated for task implementation, and no other task worktree was reused.

### Deviations

No source or test edits were necessary because the prepared snapshot already contains the corrected validation assertions and package boundary, and all focused tests pass. The required typecheck remains blocked by the unrelated `ProcessEnv` test typing diagnostic stated above.

### Assumptions

The 2026-10-18 baseline expectations describe issues already reconciled in the current prepared Commerce snapshot; this attempt verified the live source, consumers, dependency tree and tests rather than recreating the historical failures.

### Unresolved Issues

`npm run typecheck` is not fully green because of the unrelated `tests/system-commerce-tool-sync.test.ts:305` `ProcessEnv` diagnostic. No task-owned source or test regression was found.

### Architectural Concerns

Report new cross-service contracts, database schema/owner changes, secret handling issues, or deployment requirements to `moda_architect` without expanding scope.

## Architect Review

### Review Status

Accepted — Attempt 1. With `completion_mode: automatic`, the task transitions
to `status: complete`; executor and claim are clear, and Attempt 1 is preserved.

### Review Notes

The two reported baseline failures are reconciled against current canonical
behavior. The Agent validator delegates to the bounded Nunjucks validator:
unknown paths return `invalid_result_path`, an unresolved loop alias is
rejected as `unsupported_template_construct`, and `invalid_collection_path`
is reserved for a schema path that resolves to a non-array value. The tests
retain checks for invalid and unsafe paths.

The MCP extraction boundary also conforms to the current architecture. Commerce
has no direct SDK dependency or runtime SDK import; the only SDK package is
nested under the pinned dev-only Shopify schema tool. The schema sync path
remains reproducible, and the boundary regression keeps the embedded server,
route and execution path absent while preserving the private standalone client.
No validator, test, package or lockfile change was needed because the prepared
snapshot already satisfies these contracts.

The reported typecheck failure is the unchanged, unrelated TS2345 in
`tests/system-commerce-tool-sync.test.ts:305`; it does not undermine these
focused contract checks.

### Reviewed Files

- `src/commerce/tool-authoring/agent-contract-validation.ts`
- `src/commerce/tool-authoring/nunjucks-template.ts`
- `tests/agent-contract-validation.test.ts`
- `tests/commerce-mcp-extraction-boundary.test.ts`
- `tests/result-template-authoring.test.ts`
- `tests/nunjucks-template.test.ts`
- `package.json`, `package-lock.json`, and the Shopify schema sync script.
- The task Completion Report and validation evidence.

### Validation Reviewed

- Four focused suites passed: 26 tests across Agent contract validation,
  Commerce MCP extraction boundary, result-template authoring and Nunjucks.
- Shopify schema synchronization passed against pinned
  `@shopify/dev-mcp@1.15.4`; dependency inspection showed the MCP SDK only as
  its nested dev dependency.
- Focused ESLint, Prisma generation and `git diff --check` passed.
- Typecheck completed with the documented unrelated TS2345 diagnostic.
- Implementation branch is published and clean at `15d505e`; the parent task
  report was clean and synchronized before this review update.

### Architecture Conformance

Conforms to ARCH-044 and ARCH-032. Validation remains bounded and typed, the
standalone MCP service remains the only MCP runtime, and Shopify's schema
source remains a dev-only build input. No new runtime contract or dependency
change was introduced.

### Follow-up

Accepted and Complete at Attempt 1. The unrelated typecheck diagnostic remains
with its owning task. No downstream task depends on or is enabled by this task,
so no dependency status changed.
