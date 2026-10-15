---
id: ARCH-032-MCP-015
architecture_id: ARCH-032
title: Enforce mandatory platform MCP execution policy
task_kind: implementation
domain: mcp
repository: moda-interact-mcp
assigned_agent: moda_mcp
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-032-DATABASE-001
enables:
- ARCH-032-MCP-016
created: 2026-10-12
updated: '2026-10-15'
---

# ARCH-032-MCP-015 — Enforce mandatory platform MCP execution policy

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md` (ARCH-032). Coordinator: `moda_architect`.

## Objective

Replace hardcoded MCP execution policy constants with the mandatory environment-scoped JSONB entry of the existing PostgreSQL `PlatformBillingPolicy`.

## Context

Current src/mcp/execution.ts uses TOOL_DEADLINE_MS=10000 and MAX_PROVIDER_REQUESTS=12; src/mcp/service.ts uses MAX_RESPONSE_BYTES=256 KiB. These application execution controls must come from the platform policy. Published tools and Studio draft previews use the same enforcement path.

## Scope

Inject a bounded policy reader through the MCP composition/ports layer. Read the existing singleton `PlatformBillingPolicy.mcpExecutionPolicy` JSONB, validate `schemaVersion` and exactly the configured canonical Commerce environment entry before tool/provider execution; enforce per-call total deadline, per-provider-response timeout, provider request count and result-byte cap. Preserve existing cancellation and fixed protocol/body parsing safety independent of the dynamic policy. Support bounded fresh policy refresh/version observation without redeploy or stale indefinite success. Do not silently use hardcoded execution defaults.

## Out of Scope

No new Admin page, Prisma schema, service-local generic incident subsystem or feature-specific policy. No new Studio preview-only limits, no _index.md edits.

## Requirements

When the singleton row, JSONB, or configured environment entry is missing, when JSONB/schema/required fields are invalid, or when the database is unavailable, mark readiness unavailable and reject tool execution before provider calls with stable MCP_EXECUTION_POLICY_MISSING, MCP_EXECUTION_POLICY_INVALID, or MCP_EXECUTION_POLICY_UNAVAILABLE semantics. Structured log with original per-occurrence errorId; create platform-wide generic ARCH-033 incident via shared reporter (shopId=null), aggregate repeats by environment/reason, and isolate reporting failures without converting a refusal into success. Do not leak DB/provider internals to clients. Distinguish infra policy failures from ordinary budget exhaustion.

## Work Items

- [x] Inspect call budget and response-size enforcement in MCP service, Shopify/WooCommerce/knowledge providers and preview core.
- [ ] Inject policy reader and apply one shared execution enforcement path to published/preview calls. Standalone MCP published calls are covered; Commerce Local Preview still executes directly with local hardcoded budgets.
- [x] Wire generic platform-wide incident reporting and fail-closed readiness.
- [x] Add focused unit tests for policy change, missing/corrupt/outage scenarios, and cancellation.

## Interfaces / Contracts

Consumes the existing `PlatformBillingPolicy` model with ARCH-032-DATABASE-001 `mcpExecutionPolicy` JSONB and its global `version`, plus @modainteract/moda-interact-shared/incidents; uses existing service.name and environment logging conventions. No new cross-service policy payload unless a reusable contract is specifically justified.

## Dependencies

- ARCH-032-DATABASE-001

## Enables

- ARCH-032-MCP-016

## Acceptance Criteria

- [ ] No provider request occurs when singleton/JSONB/environment entry is missing, invalid, unknown-schema or unavailable, regardless of other configured environments. Standalone MCP calls pass; direct Commerce Local Preview does not read the policy.
- [ ] All four limits in the selected environment entry are enforced; existing row `version` changes refresh policy without redeploy. Standalone MCP calls pass; Local Preview still uses local deadline/request-count constants.
- [ ] Unavailable configuration raises a safe structured log and a deduplicated platform-wide operational incident; reporting failure is isolated. Standalone MCP policy failures pass; Local Preview has no policy-read/failure path.
- [ ] No local preview exceptions or hardcoded execution fallback values remain. Commerce Local Preview bypasses standalone MCP and retains independent hardcoded execution budgets.

## Validation

- [ ] Focused policy/registry/execution unit tests
- [ ] npm run typecheck; npm run lint; npm test; npm run build
- [ ] npm run typecheck:integration; npm run test:integration:docker

## Stop Condition

After the defined work, criteria and checks are complete, submit the Completion Report, return to architect review, and STOP. Do not start any enabled task. With `completion_mode: developer`, explicit developer completion remains required.

## Implementation Notes

Use the canonical developer workflow and launcher-managed isolated parent and repository task worktrees. Attempt 1 was claimed through the canonical launcher after dependency verification. Keep all `docs/decisions/**/_index.md` unchanged until the user confirms architecture reconciliation.

## Completion Report

### Status

Changes Requested — Attempt 1 implements and validates standalone MCP policy enforcement, but does not cover the direct Commerce Local Preview path required by this task's shared-enforcement contract. Claim released without incrementing the attempt.

### Files Changed
- `database` gitlink, advanced to `139765042baad3901682cfe9c54a3d6bba73e75c` (ARCH-032-DATABASE-001)
- `src/composition.ts`
- `src/connections/ports.ts`
- `src/connections/resolver.ts`
- `src/connections/shopify/provider.ts`
- `src/connections/woocommerce/provider.ts`
- `src/execution/merchant-knowledge/retrieval.ts`
- `src/execution/shopify/execute.ts`
- `src/mcp/execution.ts`
- `src/mcp/limits.ts`
- `src/mcp/policy.ts`
- `src/mcp/ports.ts`
- `src/mcp/registration.ts`
- `src/mcp/service.ts`
- `src/openapi/spec.ts`
- `src/operational/notifications.ts`
- `src/runtime/prisma.ts`
- `src/runtime/service-ports.ts`
- `tests/fixtures/capabilities.ts`
- `tests/unit/composition-protocol.test.ts`
- `tests/unit/composition.test.ts`
- `tests/unit/connections/resolver.test.ts`
- `tests/unit/connections/shopify/provider.test.ts`
- `tests/unit/connections/woocommerce/provider.test.ts`
- `tests/unit/mcp/execution-policy.test.ts`
- `tests/unit/mcp/operational-reporting.test.ts`
- `tests/unit/mcp/service.test.ts`
- `tests/unit/mcp/structured-results.test.ts`
- `tests/unit/openapi/spec.test.ts`

### Work Completed
- Added a strict environment-scoped JSON policy reader for `PlatformBillingPolicy.mcpExecutionPolicy`; selected policy is read for every published `tools/call`, with no stale-success cache or hardcoded business-budget fallback.
- Enforced total call deadline, provider response timeout, provider request count and response-byte limits across the standalone MCP Shopify, WooCommerce and Merchant Knowledge execution paths.
- Made missing/invalid/unavailable policy fail closed before shop/provider execution; connected readiness probing and safe per-occurrence structured logging.
- Added platform-wide ARCH-033 incident reporting with null shop identity, stable environment/reason grouping, unique occurrence IDs, and isolated reporting failures.
- Advanced the implementation repository's database gitlink from `12c3bee` to the completed ARCH-032-DATABASE-001 commit containing the policy JSONB field.

### Validation Results
- Passed: `npm test` — 161 passed, 0 failed.
- Passed: `npm run typecheck`.
- Passed: `npm run lint` (`--max-warnings=0`).
- Passed: `npm run build`.
- Passed: `npm run typecheck:integration`.
- Passed: `npm run test:integration:docker` — 16 passed, 0 failed, 1 opt-in live Shopify test skipped. Used disposable pgvector PostgreSQL; all 49 migrations applied, including `20261015160000_arch032_mcp_platform_policy_jsonb`, and the container/volume/network were removed.
- Passed: `git diff --check`; implementation worktree was clean at reconciliation.
- Published implementation branch: `task/ARCH-032-MCP-015`, commit `bb0f41ba81b92b3ea9f23a3129b700c0cf5df447`, including database gitlink `139765042baad3901682cfe9c54a3d6bba73e75c`.

### Deviations
The standalone MCP service is implemented and validated. Commerce Local Preview executes directly without the standalone MCP service and remains outside this repository's implementation boundary; its policy ownership/contract must be resolved before the shared published/preview criterion can be accepted.

### Assumptions
None recorded

### Unresolved Issues
The current architecture separates Commerce Local Preview (direct real-provider calls) from standalone MCP Live Test/published calls. Commerce `src/commerce/preview/service.ts` defaults `TOOL_DEADLINE_MS` to 30,000 ms, and `src/commerce/preview/local-selected-shop-executor.ts` applies a 10,000 ms deadline and 12-request budget; neither path reads `PlatformBillingPolicy` or enforces the configured provider-response timeout/response-byte limits. Decide whether Commerce Local Preview must consume this policy and which task/repository owns that integration. No Commerce files were changed.

### Architectural Concerns
None recorded

## Architect Review

### Review Status
Pending

### Review Notes
Not reviewed

### Reviewed Files
None

### Validation Reviewed
None

### Architecture Conformance
Pending

### Follow-up
None

## Developer Self-Review — Changes Requested

### Outcome
Changes Requested for Attempt 1. The standalone MCP implementation is committed, pushed, clean, and passes all required unit, lint, typecheck, build and Docker integration validations. The explicit shared published/preview requirement is not met because the current Commerce Local Preview path bypasses standalone MCP.

### Required Corrections
- Resolve with `moda_architect` whether Local Preview must use the same environment-scoped `PlatformBillingPolicy` limits. The current task body and ARCH-032 policy decision require shared enforcement, while Local Preview runs direct provider calls in `moda-interact-commerce`.
- If shared Local Preview enforcement remains required, assign/update the Commerce-owned task or a cross-repository contract to read the same policy and enforce all four limits, fail closed on missing/invalid/unavailable policy, and cover that path with focused tests. Do not make an unowned Commerce edit from this MCP task.
- If the requirement is intentionally narrowed to standalone MCP, amend the active task scope/acceptance criteria through architect reconciliation, then review this already-pushed MCP implementation against that revised contract.

### Review Evidence
- MCP implementation commit `bb0f41ba81b92b3ea9f23a3129b700c0cf5df447` is pushed on `task/ARCH-032-MCP-015`; canonical implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-032-MCP-015` was clean.
- The commit pins database submodule `139765042baad3901682cfe9c54a3d6bba73e75c`, which contains `PlatformBillingPolicy.mcpExecutionPolicy`; the disposable PostgreSQL run applied the corresponding migration.
- Validation: `npm test` 161/161; `npm run typecheck`; `npm run lint`; `npm run build`; `npm run typecheck:integration`; `npm run test:integration:docker` 16 passed, 1 opt-in live Shopify test skipped.
- Commerce inspection found the direct local-preview deadlines described in Unresolved Issues and no `mcpExecutionPolicy`/provider-timeout/response-byte reader in its preview path.
- Parent task branch synchronization incorporated `origin/main` at `6a3c9d90c1ba0f328085f16a4c8c9c7292731cbd`; the implementation branch was based on `dac8b03986686ec5450c56742815c27ff7e7face` and remains published at `bb0f41ba81b92b3ea9f23a3129b700c0cf5df447`.

## 2026-10-15 — Architect dependency reconciliation

**Status preserved:** source presence or prior patch delivery is not acceptance. Reconcile canonical task worktree, parent Completion Report, required checks and review before promoting.

Active `status`: `pending`. Active `depends_on`: `ARCH-032-DATABASE-001`. Active `enables`: `ARCH-032-MCP-016`.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.

## 2026-10-15 — Active JSONB platform-policy storage correction

The user directs reuse of the existing `billing.PlatformBillingPolicy` singleton with an optional environment-keyed MCP JSONB field. This active storage/scope decision supersedes earlier references to a new MCP policy model/table or per-environment rows, while preserving the historical task record, review evidence and existing task dependencies. No task is marked Complete by this definition update.

## 2026-10-15 — Dependency Frontier Reconciliation

`ARCH-032-DATABASE-001` completed Attempt 1 with explicit developer completion and accepted review in parent commit `2d3dbcf9`. This task's sole declared dependency is now satisfied. Promote `pending` to `ready`; preserve `attempt: 0`, `executor: null`, and `claimed_at: null`. This is an eligibility update only, not an implementation claim or completion decision.
