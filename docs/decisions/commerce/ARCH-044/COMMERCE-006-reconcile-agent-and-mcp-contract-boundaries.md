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
status: in_progress
priority: 30
executor: copilot
claimed_at: 2026-11-01T17:08:25Z
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

## Work Items

- [ ] Resolve and document `invalid_collection_path` versus `invalid_result_path` semantics with current validator and consumer evidence.
- [ ] Add/update exact typed-validation tests while retaining rejection behavior.
- [ ] Inventory `@modelcontextprotocol/sdk` use and the current Commerce/MCP boundary; decide remove/move/retain with evidence.
- [ ] Correct the boundary test and any justified dependency/package-lock entry.
- [ ] Run the complete nearby contract and extraction regression tests.

## Interfaces / Contracts

Agent/response-template validation issue codes and result-path schema; ARCH-032 standalone MCP extraction boundary; existing `@modelcontextprotocol/sdk`/`@shopify/dev-mcp` package roles. Escalate missing Shared reusable functionality rather than duplicate it.

## Dependencies

None.

## Enables

None directly. The architecture-level integrated validation remains after all eight tasks.

## Acceptance Criteria

- [ ] Both original failing tests pass with defensible source/contract evidence.
- [ ] Unknown scalar/collection paths remain invalid and produce safe typed diagnostics.
- [ ] No embedded MCP route/server or forbidden Commerce execution path is reintroduced.
- [ ] Relevant SDK dependence is reconciled against actual imports and runtime ownership; package-lock is consistent if changed.
- [ ] No scope expansion to new MCP product behavior.

## Validation

- [ ] `npx vitest run tests/agent-contract-validation.test.ts tests/commerce-mcp-extraction-boundary.test.ts tests/result-template-authoring.test.ts tests/nunjucks-template.test.ts`.
- [ ] `npm run typecheck`, `npm run schema:sync`, changed-file lint, `git diff --check`.
- [ ] Check package manifests/lockfile dependency ownership if any dependency changes.

## Stop Condition

After all scoped Work Items and Acceptance Criteria are demonstrably satisfied, record exact commands and results in the Completion Report, set task `status: review`, clear execution claim as required by launcher protocol, return for architect review and **STOP**. Do not execute or close downstream work. If validation is blocked, record it accurately rather than claiming PASS.

## Implementation Notes

`invalid_result_path` and `unsupported_template_construct` are actual observed baseline outputs; `invalid_collection_path` was a historical expectation. Treat them as a contract decision, not a string-replacement exercise. The package currently declares SDK 1.30.0; the snapshot alone does not prove whether it is required at runtime.

### Exact failing tests

- `tests/agent-contract-validation.test.ts` — `rejects unknown scalar paths and non-list items paths`.
- `tests/commerce-mcp-extraction-boundary.test.ts` — `does not ship an embedded MCP route or server, and keeps only a private thin live client`.

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
