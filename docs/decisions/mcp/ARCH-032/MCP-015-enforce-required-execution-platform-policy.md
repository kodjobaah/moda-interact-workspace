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
status: in_progress
priority: 40
executor: developer
claimed_at: 2026-10-15T19:05:44Z
attempt: 1
depends_on:
- ARCH-032-DATABASE-001
enables:
- ARCH-032-MCP-016
created: 2026-10-12
updated: 2026-10-15
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

- [ ] Inspect call budget and response-size enforcement in MCP service, Shopify/WooCommerce/knowledge providers and preview core.
- [ ] Inject policy reader and apply one shared execution enforcement path to published/preview calls.
- [ ] Wire generic platform-wide incident reporting and fail-closed readiness.
- [ ] Add focused unit tests for policy change, missing/corrupt/outage scenarios, and cancellation.

## Interfaces / Contracts

Consumes the existing `PlatformBillingPolicy` model with ARCH-032-DATABASE-001 `mcpExecutionPolicy` JSONB and its global `version`, plus @modainteract/moda-interact-shared/incidents; uses existing service.name and environment logging conventions. No new cross-service policy payload unless a reusable contract is specifically justified.

## Dependencies

- ARCH-032-DATABASE-001

## Enables

- ARCH-032-MCP-016

## Acceptance Criteria

- [ ] No provider request occurs when singleton/JSONB/environment entry is missing, invalid, unknown-schema or unavailable, regardless of other configured environments.
- [ ] All four limits in the selected environment entry are enforced; existing row `version` changes refresh policy without redeploy.
- [ ] Unavailable configuration raises a safe structured log and a deduplicated platform-wide operational incident; reporting failure is isolated.
- [ ] No local preview exceptions or hardcoded execution fallback values remain.

## Validation

- [ ] Focused policy/registry/execution unit tests
- [ ] npm run typecheck; npm run lint; npm test; npm run build
- [ ] npm run typecheck:integration; npm run test:integration:docker

## Stop Condition

After the defined work, criteria and checks are complete, submit the Completion Report, return to architect review, and STOP. Do not start any enabled task. With `completion_mode: developer`, explicit developer completion remains required.

## Implementation Notes

Use the canonical developer workflow and launcher-managed isolated parent and repository task worktrees. This is a **portable task definition**, `defined but not materialised`: no branches, commits, pushes, claims or worktrees have been created by this artifact. Run `/moda_developer_create ARCH-032-MCP-015` after materialisation and dependency verification. Keep all `docs/decisions/**/_index.md` unchanged until the user confirms architecture reconciliation.

## Completion Report

### Status

In Progress — Attempt 1 claimed by developer at 2026-10-15T19:05:44Z. Attempt 0 review history is preserved below.

### Files Changed
None

### Work Completed
None

### Validation Results
Not run

### Deviations
None

### Assumptions
None recorded

### Unresolved Issues
None recorded

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

## 2026-10-15 — Architect dependency reconciliation

**Status preserved:** source presence or prior patch delivery is not acceptance. Reconcile canonical task worktree, parent Completion Report, required checks and review before promoting.

Active `status`: `pending`. Active `depends_on`: `ARCH-032-DATABASE-001`. Active `enables`: `ARCH-032-MCP-016`.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.

## 2026-10-15 — Active JSONB platform-policy storage correction

The user directs reuse of the existing `billing.PlatformBillingPolicy` singleton with an optional environment-keyed MCP JSONB field. This active storage/scope decision supersedes earlier references to a new MCP policy model/table or per-environment rows, while preserving the historical task record, review evidence and existing task dependencies. No task is marked Complete by this definition update.

## 2026-10-15 — Dependency Frontier Reconciliation

`ARCH-032-DATABASE-001` completed Attempt 1 with explicit developer completion and accepted review in parent commit `2d3dbcf9`. This task's sole declared dependency is now satisfied. Promote `pending` to `ready`; preserve `attempt: 0`, `executor: null`, and `claimed_at: null`. This is an eligibility update only, not an implementation claim or completion decision.
