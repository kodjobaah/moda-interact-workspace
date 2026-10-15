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

Extend the existing singleton `PlatformBillingPolicy` with environment-scoped MCP execution-policy JSONB and guarantee that a fresh database/reset provisions all Platform Policy defaults, including MCP limits for every Commerce environment, without creating a new policy table.

## Context

The standalone MCP runtime historically uses TOOL_DEADLINE_MS=10000, MAX_PROVIDER_REQUESTS=12 and MAX_RESPONSE_BYTES=256 KiB. The developer explicitly requires a database reset to populate the singleton Platform Billing Policy and all MCP environment policies with current defaults. Persisted values, not hardcoded runtime fallback values, are authoritative after migration. This task owns the migration/seed contract; MCP-015 owns runtime read-time validation and enforcement.

## Scope

Modify only the **existing** Prisma `PlatformBillingPolicy` model by adding nullable `mcpExecutionPolicy Json? @db.JsonB`; retain its singleton identity (`id="default"`), existing `version` and other billing fields. The forward-only ARCH-032 migration must:

1. Add the nullable JSONB column; create **no** separate table, model, environment column or version column.
2. On a **fresh database or `prisma migrate reset`**, ensure the `billing.PlatformBillingPolicy` singleton exists with its existing billing defaults: `globalPauseNewRecoveries=false`, `globalPauseAutomatedWhatsapp=false`, `lifetimeFreeRecoveryAllowance=5`, `minimumUpgradePremiumBps=2000`, `absoluteOutboundHardLimit=2000`, `defaultWarningPercent=80`, `defaultOutboundSoftLimit=1000`, `defaultOutboundHardLimit=2000`, `terminalMessageReservedSlots=1`, and `whatsappRecipientSuppressionDays=7`.
3. Populate the versioned MCP JSONB (`schemaVersion: 1`) for **all five** existing `CommerceEnvironment` labels: `LOCAL`, `TEST`, `DEVELOPMENT`, `STAGING`, `PRODUCTION`. Each receives the current runtime defaults: `toolDeadlineMs=10000`, `providerResponseTimeoutMs=10000`, `maxProviderRequests=12`, `maxResponseBytes=262144`.
4. On **upgrade**, retain existing billing values and any existing non-null MCP JSONB. Backfill the five MCP environment defaults only when `mcpExecutionPolicy IS NULL`, incrementing the existing whole-row `version` once for that backfill. Use conflict-safe singleton insertion (`ON CONFLICT DO NOTHING`) rather than overwriting an existing policy row.
5. Keep repeated development/demo seed runs non-destructive: do not overwrite operator changes or recreate policy entries that an operator subsequently clears. Policy creation must not depend on a Shopify demo session.

The JSONB field remains nullable for explicit later clears; an absent/invalid environment must still fail closed at runtime. The seeded defaults are **initial configuration**, not application-side fallbacks. Define the schema version, permitted keys, positive bounded integer fields and `providerResponseTimeoutMs <= toolDeadlineMs`; Admin validates writes and MCP validates reads under their own tasks. Reuse the existing singleton `version` as the monotonic optimistic-concurrency token for all later billing and MCP edits.

## Out of Scope

Do not add MCP runtime calls, Admin UI, Shared incident runtime, a second policy table, or a separate Prisma model. Do not introduce runtime hardcoded fallback policy or silently auto-repair deliberately cleared environment entries. No schema edits in implementation repositories and no `_index.md` changes.

## Requirements

The database reset contract requires a populated policy singleton with all billing and MCP defaults. After initial provision, explicit operator clears are allowed and must **not** be repaired by MCP, Admin reads or repeated demo seeding. Missing singleton, SQL NULL, absent environment or malformed JSON remains invalid/unconfigured at runtime, with fail-closed handling by MCP-015. Document the exact versioned JSON schema, supported environment keys, numeric safety caps and `providerResponseTimeoutMs <= toolDeadlineMs`; the database JSONB column by itself does **not** validate nested field names/types, unknown schema versions or numeric bounds. Ensure the seeded JSON parses and satisfies the agreed shape and caps; runtime/write-boundary rejection is owned and tested by ADMIN-001/MCP-015/MCP-016, not asserted by a static migration regex check. All later edits must preserve unrelated billing values and other environment entries while using the existing monotonic whole-row `version`, including clears and create-clear-replay protection.

## Work Items

- [ ] Inspect the existing `PlatformBillingPolicy` singleton defaults, migration ordering, version mutation paths and `CommerceEnvironment` labels.
- [ ] Add nullable `mcpExecutionPolicy` JSONB and a forward migration that provisions the complete default singleton on reset and conditionally backfills missing MCP JSONB on upgrade, without overwriting operator data.
- [ ] Keep the development seed consistent with the migration, idempotent and safe when no Shopify demo session exists; do not repair operator clears.
- [ ] Add focused schema/JSON-shape checks and disposable PostgreSQL fresh/reset and upgrade tests proving seeded defaults, preserved billing/configured MCP values, version increments on actual backfill, and later CAS/clear/replay safety.
- [ ] Record explicitly that Admin write-validation and MCP read-validation are dependent tasks, not evidence supplied by the database's nullable JSONB type.

## Interfaces / Contracts

Existing Prisma `PlatformBillingPolicy` (`billing.PlatformBillingPolicy`, singleton `id="default"`, existing `version`) with nullable `mcpExecutionPolicy` JSONB, shape `{"schemaVersion":1,"environments":{"DEVELOPMENT":{"toolDeadlineMs":10000,"providerResponseTimeoutMs":10000,"maxProviderRequests":12,"maxResponseBytes":262144}}}`. The migration seeds these values for **all five** canonical Commerce environments; the single-environment example illustrates their common shape. No credentials or shop-specific secrets. Admin/MCP must not treat the migration values as fallback constants after a policy is explicitly cleared.

## Dependencies

None

## Enables

- ARCH-032-ADMIN-001
- ARCH-032-MCP-015

## Acceptance Criteria

- [ ] Fresh migration / disposable reset creates exactly one `PlatformBillingPolicy` `default` row with the documented billing defaults and seeded MCP defaults for **LOCAL, TEST, DEVELOPMENT, STAGING, PRODUCTION**; no second table is created and no Shopify demo session is necessary.
- [ ] Upgrade of an existing singleton leaves billing fields and non-null MCP JSONB untouched; an existing SQL NULL MCP policy is backfilled once, advancing the row-wide `version` once. Conflict-safe inserts do not reset existing policy values.
- [ ] Repeated development seed does not overwrite operator edits, including explicitly cleared MCP environments; initial database defaults are not runtime fallback defaults.
- [ ] Migration-produced JSON validates against the documented schema version, exact field/key set, numeric bounds and provider-timeout ordering. The database column alone is not claimed to enforce nested JSON constraints; Admin/MCP runtime validation remains an explicitly owned dependency.
- [ ] Disposable PostgreSQL tests show that explicit later environment writes/clears preserve unrelated values and use monotonic whole-row CAS, rejecting stale billing/MCP updates and stale create-clear-replay.

## Validation

- [ ] npm run validate (if declared by repository)
- [ ] Disposable PostgreSQL fresh/reset and upgrade policy tests, including idempotence and default-value checks
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

## 2026-10-15 — Developer-approved default-seeding contract (ACTIVE; supersedes prior review corrections)

**Authoritative scope decision:** The developer explicitly requests that a database reset populate *all* platform policies with their default values, **including MCP**. The existing `PlatformBillingPolicy` singleton is the only policy store. Initial database provisioning is required, not prohibited.

This section supersedes the **scope assumptions and blocking corrections 1–4** of the historical `Developer Self-Review - Changes Requested` above, specifically the column-only/no-row/no-seed/no-backfill acceptance rules. Preserve that self-review and the original Completion Report as historical evidence; do not erase their findings or pretend that validation proved the earlier contract. The previously implemented migration/seed behaviour in database implementation commit `85eca46` is now in scope, subject to verifying its exact defaults, upgrade preservation, idempotence and version/CAS behaviour against the revised criteria.

**Correction 5 remains relevant, but its ownership boundary is clarified:** static schema checks cannot establish nested runtime JSON validation. The Database task must prove the seeded JSON shape and PostgreSQL persistence. Authorised Admin writes and MCP runtime reads must independently reject unknown versions/keys/fields, invalid bounds and timeout ordering in `ARCH-032-ADMIN-001`, `ARCH-032-MCP-015` and `ARCH-032-MCP-016`. Do not block database acceptance on completion of these dependent tasks or misstate their validation as performed here.

Keep `status: ready`, `attempt: 1`, `executor: null` and `claimed_at: null` until the developer's canonical task workflow performs the next authorised claim/review. Do not automatically mark the implementation Accepted/Complete or fabricate new validation, Git commits or branch updates. Existing dependency IDs remain unchanged; no `_index.md` changes.
