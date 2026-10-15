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
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
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

Replace hardcoded MCP execution policy constants with a mandatory environment-scoped PostgreSQL policy.

## Context

Current src/mcp/execution.ts uses TOOL_DEADLINE_MS=10000 and MAX_PROVIDER_REQUESTS=12; src/mcp/service.ts uses MAX_RESPONSE_BYTES=256 KiB. These application execution controls must come from the platform policy. Published tools and Studio draft previews use the same enforcement path.

## Scope

Inject a bounded policy reader through the MCP composition/ports layer. Load and validate the configured environment’s policy before tool/provider execution; enforce per-call total deadline, per-provider-response timeout, provider request count and result-byte cap. Preserve existing cancellation and fixed protocol/body parsing safety independent of the dynamic policy. Support bounded fresh policy refresh/version observation without redeploy or stale indefinite success. Do not silently use hardcoded execution defaults.

## Out of Scope

No new Admin page, Prisma schema, service-local generic incident subsystem or feature-specific policy. No new Studio preview-only limits, no _index.md edits.

## Requirements

When a required record is missing, invalid or unavailable, mark readiness unavailable and reject tool execution before provider calls with stable MCP_EXECUTION_POLICY_MISSING, MCP_EXECUTION_POLICY_INVALID, or MCP_EXECUTION_POLICY_UNAVAILABLE semantics. Structured log with original per-occurrence errorId; create platform-wide generic ARCH-033 incident via shared reporter (shopId=null), aggregate repeats by environment/reason, and isolate reporting failures without converting a refusal into success. Do not leak DB/provider internals to clients. Distinguish infra policy failures from ordinary budget exhaustion.

## Work Items

- [ ] Inspect call budget and response-size enforcement in MCP service, Shopify/WooCommerce/knowledge providers and preview core.
- [ ] Inject policy reader and apply one shared execution enforcement path to published/preview calls.
- [ ] Wire generic platform-wide incident reporting and fail-closed readiness.
- [ ] Add focused unit tests for policy change, missing/corrupt/outage scenarios, and cancellation.

## Interfaces / Contracts

Consumes ARCH-032-DATABASE-001 policy model and @modainteract/moda-interact-shared/incidents; uses existing service.name and environment logging conventions. No new cross-service policy payload unless a reusable contract is specifically justified.

## Dependencies

- ARCH-032-DATABASE-001

## Enables

- ARCH-032-MCP-016

## Acceptance Criteria

- [ ] No provider request occurs when policy is missing, invalid or unavailable.
- [ ] All four configured limits are enforced and updates take effect without redeploy.
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
Not Started

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
