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

The standalone MCP service previously used fixed tool deadlines, provider-request budgets, and response-size caps. These controls must come from the platform policy for **every standalone MCP published `tools/call`**, including calls made by Background and Commerce Live Test. Under the authoritative 2026-10-13 execution model, Commerce Local Preview executes directly inside `moda-interact-commerce`, not through standalone MCP; ARCH-038 owns its separate Preview runner budgets and Commerce retains its local provider safeguards.

## Scope

Inject a bounded policy reader through the **standalone MCP** composition/ports layer. Read the existing singleton `PlatformBillingPolicy.mcpExecutionPolicy` JSONB, validate `schemaVersion` and the selected canonical Commerce environment before **published `tools/call`** execution; enforce per-call total deadline, per-provider-response timeout, provider request count and result-byte cap. Preserve existing cancellation and fixed protocol/body parsing safety independent of the dynamic policy. Observe policy updates for subsequent calls without redeploy or indefinitely stale successful reads. Do not silently use hardcoded execution defaults in standalone MCP.

## Out of Scope

No new Admin page, Prisma schema, service-local generic incident subsystem or feature-specific policy. No `moda-interact-commerce` source changes, no direct Commerce Local Preview budget management, no Fixture-mode policy, and no `_index.md` edits. Commerce Preview’s independent runner budgets are governed by ARCH-038 and are not a bypass of standalone MCP policy for published MCP calls.

## Requirements

When the singleton row, JSONB, or configured environment entry is missing, when JSONB/schema/required fields are invalid, or when the database is unavailable, mark readiness unavailable and reject tool execution before provider calls with stable MCP_EXECUTION_POLICY_MISSING, MCP_EXECUTION_POLICY_INVALID, or MCP_EXECUTION_POLICY_UNAVAILABLE semantics. Structured log with original per-occurrence errorId; create platform-wide generic ARCH-033 incident via shared reporter (shopId=null), aggregate repeats by environment/reason, and isolate reporting failures without converting a refusal into success. Do not leak DB/provider internals to clients. Distinguish infra policy failures from ordinary budget exhaustion.

## Work Items

- [x] Inspect call budget and response-size enforcement in MCP service, Shopify/WooCommerce/knowledge providers and preview core.
- [x] Inject the policy reader and apply a single execution-enforcement path to standalone MCP published `tools/call`, including Background/Commerce Live Test consumers. Commerce Local Preview is excluded because it does not invoke this service.
- [x] Wire generic platform-wide incident reporting and fail-closed readiness.
- [x] Add focused unit tests for policy change, missing/corrupt/outage scenarios, and cancellation.

## Interfaces / Contracts

Consumes the existing `PlatformBillingPolicy` model with ARCH-032-DATABASE-001 `mcpExecutionPolicy` JSONB and its global `version`, plus @modainteract/moda-interact-shared/incidents; uses existing service.name and environment logging conventions. No new cross-service policy payload unless a reusable contract is specifically justified.

## Dependencies

- ARCH-032-DATABASE-001

## Enables

- ARCH-032-MCP-016

## Acceptance Criteria

- [x] For standalone MCP published `tools/call`, no provider request occurs when the policy singleton, JSONB or selected environment is missing, invalid, unknown-schema or unavailable; other configured environments do not act as fallback.
- [x] Standalone MCP enforces all four limits from the selected environment, and a subsequent invocation observes persisted policy changes without redeploy; no local hardcoded business-limit fallback is used.
- [x] Standalone MCP policy refusal has safe structured logging and platform-scoped incident reporting; incident-reporting failures remain isolated from the refusal.
- [x] Commerce Local Preview and Fixture are not invoked through standalone MCP; they do not need to read its policy to satisfy MCP-015. This exception does **not** permit published MCP calls to bypass enforcement or authorise unbounded provider execution in Commerce.

## Validation

- [x] Focused policy/registry/execution unit tests — passed in the recorded Attempt 1 implementation report.
- [x] npm run typecheck; npm run lint; npm test; npm run build — passed in the recorded Attempt 1 report.
- [x] npm run typecheck:integration; npm run test:integration:docker — recorded 16 passing PostgreSQL tests, one opt-in live Shopify test skipped.

These checks are **recorded implementation evidence**, not fresh execution or an architect acceptance decision. If the canonical implementation has changed, rerun affected validation before completion.

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


## 2026-10-15 — Active architect scope correction: published standalone MCP only

**Decision (superseding the Local Preview part of the earlier Changes Requested self-review):** The 2026-10-13 three-mode Studio execution model is authoritative. `ARCH-032-MCP-015` owns policy enforcement only for requests executed by the **standalone `moda-interact-mcp` service**, including published calls from Background and Commerce Live Test. Commerce Local Preview executes real authorised provider calls directly in `moda-interact-commerce` and is **not a transport into the standalone MCP**. Fixture mode is simulated. Neither is required to call MCP-015's policy reader.

Commerce Preview retains its independent ARCH-038 Preview runner-budget contract and existing Commerce-owned provider safety checks. This correction does not certify or modify those safeguards, does not authorise unlimited Local Preview calls, and does not introduce an unowned change in Commerce. MCP JSONB limits and ARCH-033 incident reporting apply only at standalone MCP execution boundaries. Published MCP calls may **never** bypass policy validation on the basis that the caller is Commerce.

The original Attempt 1 Completion Report and Developer Self-Review remain verbatim historical evidence. The previously reported uncovered Local Preview criterion is **no longer part of MCP-015 acceptance**. The revised active Scope, Work Items, Acceptance Criteria, and Validation sections above define the task contract. Existing passing Attempt 1 validation is cited from the implementation report; no tests have been rerun by this documentation correction.

**State unchanged:** `status: ready`, `attempt: 1`, `executor: null`, `claimed_at: null`, `completion_mode: developer`, and `Architect Review: Pending`. Re-review the already-pushed implementation commit `bb0f41ba81b92b3ea9f23a3129b700c0cf5df447` against the narrowed task; developer completion remains an explicit later decision. Preserve the dependency on `ARCH-032-DATABASE-001` and the enablement of `ARCH-032-MCP-016` until accepted completion.
