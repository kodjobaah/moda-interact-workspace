---
id: ARCH-032-DATABASE-001
architecture_id: ARCH-032
title: Persist required environment-scoped MCP execution policy
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on: []
enables:
- ARCH-032-ADMIN-001
- ARCH-032-MCP-015
created: 2026-10-12
updated: '2026-10-15'
---

# ARCH-032-DATABASE-001 — Persist required environment-scoped MCP execution policy

## Architecture

`docs/architecture/ARCH-032-standalone-commerce-mcp-extraction.md` (ARCH-032). Coordinator: `moda_architect`.

## Objective

Extend the existing singleton `PlatformBillingPolicy` with environment-scoped MCP execution-policy JSONB, without adding a new policy table.

## Context

The standalone MCP runtime currently hardcodes TOOL_DEADLINE_MS=10000, MAX_PROVIDER_REQUESTS=12 and MAX_RESPONSE_BYTES=256 KiB. The user requires database-backed platform policy without execution fallbacks, stored on the existing `billing.PlatformBillingPolicy` singleton. This task owns persistence, not runtime enforcement.

## Scope

Modify the **existing** Prisma `PlatformBillingPolicy` model in `moda-interact-database/prisma/schema.prisma` by adding `mcpExecutionPolicy Json? @db.JsonB`, with a forward-only `ALTER TABLE "billing"."PlatformBillingPolicy"` migration. Do not create another table, policy model, separate environment-identity column or a second version field. Store a versioned JSON object (`schemaVersion: 1`) containing `environments` keyed by existing `CommerceEnvironment` labels (`LOCAL`, `TEST`, `DEVELOPMENT`, `STAGING`, `PRODUCTION`). Every configured entry has positive bounded integer `toolDeadlineMs`, `providerResponseTimeoutMs`, `maxProviderRequests` and `maxResponseBytes`; provider timeout may not exceed total deadline. Validate the complete configured environment entry at the write boundary and again at the MCP read boundary. Preserve all existing billing fields, singleton identity, current migrations and policy-row provisioning. Do not seed a JSON policy or backfill sample limits. Reuse the existing singleton `version` as the optimistic concurrency token for all edits.

## Out of Scope

Do not add MCP runtime calls, Admin UI, Shared incident runtime, policy default constants, a second policy table, or a separate Prisma model. No schema edits in implementation repositories, no _index.md changes.

## Requirements

The existing singleton may be present while `mcpExecutionPolicy` is null or a given environment entry is absent; these represent **unconfigured** MCP policy and must remain distinguishable from a valid policy. Missing singleton is also not a valid policy; do not create a default singleton as part of MCP configuration. Document the JSON schema/version, supported environment keys, numeric caps and `providerResponseTimeoutMs <= toolDeadlineMs` constraint. Database shape checks where practical must not auto-insert an environment; application/reader validators must reject invalid nested values and unknown schema versions. Updates must use the existing row's monotonically increasing `version` and preserve unrelated billing fields and other environment entries. Clearing an environment must increment `version` even if the MCP JSON becomes null, preventing stale create-clear-replay.

## Work Items

- [ ] Inspect existing `PlatformBillingPolicy` singleton, its guaranteed/default-row provisioning, version mutation paths, migrations and the Commerce environment enum.
- [ ] Add nullable `mcpExecutionPolicy` JSONB to the existing model and a column-only forward migration; define the versioned JSON shape and validated numeric bounds without provisioning MCP values.
- [ ] Add fresh/upgrade disposable PostgreSQL tests proving the row's existing billing data survives, unconfigured MCP remains unconfigured, environment isolation, CAS updates across billing/MCP writes, and stale create-clear-replay rejection.

## Interfaces / Contracts

Existing Prisma `PlatformBillingPolicy` (`billing.PlatformBillingPolicy`, singleton `id="default"`, existing `version`) with one nullable `mcpExecutionPolicy` JSONB value: `{"schemaVersion":1,"environments":{"DEVELOPMENT":{"toolDeadlineMs":...,"providerResponseTimeoutMs":...,"maxProviderRequests":...,"maxResponseBytes":...}}}`. Environment keys derive from `CommerceEnvironment`; the illustrative JSON is a wire-shape description, not seeded runtime values. No secrets or shop-specific credentials.

## Dependencies

None

## Enables

- ARCH-032-ADMIN-001
- ARCH-032-MCP-015

## Acceptance Criteria

- [ ] Fresh and upgrade migrations add only the nullable JSONB column; no new policy table, no MCP data seed, and existing `PlatformBillingPolicy` row/fields remain intact.
- [ ] Existing billing configuration and unrelated environment JSON entries are preserved through MCP writes and clears.
- [ ] Missing/invalid/unknown-schema MCP JSON cannot be mistaken for a valid environment policy; numeric caps and timeout relation are enforced by validators.
- [ ] Whole-row CAS uses the existing `version`, increments on successful create/update/clear, and rejects stale billing-vs-MCP updates and stale create-clear-replay.

## Validation

- [ ] npm run validate (if declared by repository)
- [ ] Disposable PostgreSQL fresh and upgrade policy tests
- [ ] git apply --check --whitespace=error-all; git diff --check

## Stop Condition

After the defined work, criteria and checks are complete, submit the Completion Report, return to architect review, and STOP. Do not start any enabled task. With `completion_mode: developer`, explicit developer completion remains required.

## Implementation Notes

The task definition was already published on parent `origin/main` in commit
`df2a560c`. Developer Attempt 1 was claimed and implemented on the canonical
database worktree. Self-review found blocking contract deviations; the task is
returned to `ready` for corrections without incrementing the attempt. The
canonical parent and database implementation worktrees remain on
`task/ARCH-032-DATABASE-001`. Keep all `docs/decisions/**/_index.md` unchanged
until the user confirms architecture reconciliation.

## Completion Report

### Status
Changes Requested

### Files Changed
`docs/ARCH-032-mcp-execution-policy-jsonb.md`; `package.json`;
`prisma/migrations/20261015160000_arch032_mcp_platform_policy_jsonb/migration.sql`;
`prisma/schema.prisma`; `prisma/seed.mjs`;
`scripts/test-arch032-mcp-platform-policy-postgres.mjs`;
`scripts/validate-arch032-mcp-platform-policy-schema.mjs`.

### Work Completed
Added the nullable Prisma JSONB field, a migration, policy documentation, seed
changes, and schema/PostgreSQL tests in implementation commit `85eca46`.
Implementation branch is pushed. The migration and tests currently provision
and seed MCP policy values, contrary to the task contract; see the self-review.

### Validation Results
`npm run validate` passed. `npm run test:arch032-mcp-platform-policy-schema`,
`npm run test:arch032-mcp-platform-policy:postgres:fresh`, and
`npm run test:arch032-mcp-platform-policy:postgres:upgrade` passed, but their
assertions require the prohibited singleton/default-policy seeding and therefore
do not demonstrate task acceptance. `git diff --check` passed.

### Deviations
The migration inserts the platform singleton on fresh databases and backfills
MCP defaults for all five environments on upgrades; `prisma/seed.mjs` also
supplies MCP defaults. The documentation and tests describe/require this
behavior although the task explicitly forbids it.

### Assumptions
None recorded

### Unresolved Issues
Column-only migration, null/unconfigured behavior, and corresponding test
expectations need correction before this attempt can pass review.

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

## Developer Self-Review - Changes Requested

### Review Result
Changes Requested

### Blocking Corrections
1. Make the migration column-only: add nullable `mcpExecutionPolicy JSONB` and
   remove the singleton `INSERT`, JSON defaults, null-row `UPDATE`, and version
   bump. On both fresh and upgrade databases, a missing singleton must remain
   missing and an existing singleton with `mcpExecutionPolicy IS NULL` must
   remain unconfigured; do not modify its existing fields or version as a side
   effect of adding the column.
2. Remove MCP policy values from `prisma/seed.mjs`. Preserve the repository's
   existing billing-policy provisioning separately, but do not create or repair
   MCP configuration through the demo seed.
3. Correct the Prisma field comment and
   `docs/ARCH-032-mcp-execution-policy-jsonb.md` so they describe the nullable,
   unconfigured-by-default contract rather than seeded defaults or migration
   provisioning.
4. Rewrite the schema and disposable PostgreSQL assertions to prove the
   required behavior: no MCP JSON seed, no singleton creation by this
   migration, SQL NULL remains unconfigured, existing billing data and version
   are unchanged by the column-only upgrade, and later explicit writes/clears
   use the shared version CAS and reject stale replay. Keep fresh and upgrade
   test modes.
5. Do not treat the static regex schema test as validation of nested JSON
   values. Ensure the documented contract remains aligned with the write/read
   validators owned by the applicable Admin/MCP boundaries, including unknown
   schema versions, unknown fields, bounds and timeout ordering; leave any
   boundary validation criterion incomplete until it has executable evidence.

### Validation Evidence
Prisma validation and all three new test commands passed. The PostgreSQL tests
passed against expectations that conflict with the task requirements, so these
results are not acceptance evidence. `git diff --check` passed.

### State Transition
Returned to `ready`; `executor` and `claimed_at` cleared; attempt remains `1`.
The next `/moda_developer_create ARCH-032-DATABASE-001` claim should increment
the attempt once after the corrections are made.

## 2026-10-15 — Architect dependency reconciliation

**Status preserved:** source presence or prior patch delivery is not acceptance. Reconcile canonical task worktree, parent Completion Report, required checks and review before promoting.

Active `status`: `ready`. Active `depends_on`: None. Active `enables`: `ARCH-032-ADMIN-001`, `ARCH-032-MCP-015`.

The YAML frontmatter above is authoritative for task eligibility. This clarification supersedes conflicting historical `Dependencies`, `Enables`, `Execution hold` and remote-preview references in the body; it does not rewrite or erase historical Completion Reports or Architect Reviews. No branch, commit, test acceptance or deployment is asserted by this documentation change.

## 2026-10-15 — Active JSONB platform-policy storage correction

The user directs reuse of the existing `billing.PlatformBillingPolicy` singleton with an optional environment-keyed MCP JSONB field. This active storage/scope decision supersedes earlier references to a new MCP policy model/table or per-environment rows, while preserving the historical task record, review evidence and existing task dependencies. No task is marked Complete by this definition update.
