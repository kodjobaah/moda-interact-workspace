---
id: ARCH-007-DATABASE-001
architecture_id: ARCH-007
title: Replace billing plan and subscription catalog with the typed ARCH-007 target schema
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
status: complete
priority: 10
executor: null
claimed_at: null
attempt: 2
depends_on: []
enables: 
  - ARCH-007-DATABASE-002
created: 2026-09-07
updated: 2026-09-07
---

# ARCH-007-DATABASE-001: Replace billing plan and subscription catalog with the typed ARCH-007 target schema

## Architecture

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Create the final pre-production Prisma representation for configurable Shopify plan mappings, plan features, typed subscription projection and Shopify billing-cycle state.

## Context

The current schema stores `BillingPlan.entitlements`/`limits` as JSON and subscription provider/status/plan details as strings. ARCH-007 requires deploy-free plan registration through Admin and explicit FlatRate/Tiered item mapping. This is a development reset: target schema correctness matters more than compatibility with existing development billing rows.

## Scope

Modify only the canonical `moda-interact-database` Prisma schema, its normal Prisma migration artifact, `prisma/seed.mjs` where required for development-reset compatibility, and generated Prisma/ERD artifacts for BillingPlan, BillingPlanFeature, Subscription and BillingPeriod.

## Out of Scope

- Usage reservation/outbox fields (DATABASE-002).
- Platform/shop overrides, allowance adjustments or audit tables (DATABASE-003).
- Admin/application/background implementation.
- Any production-style data-preserving backfill, dual-read compatibility adapter, or legacy billing runtime support.

## Requirements

- Use Prisma enums for plan kind (`FREE`, `PAID_METERED`), subscription projection status (`ACTIVE`, `TRIALING`, `NO_CONTRACT`, `UNMAPPED`, `SYNC_ERROR`), billing-period status, and feature identifiers shared with the existing product feature semantics.
- Replace JSON entitlement/limit runtime fields with typed BillingPlan columns plus a unique `(planId, feature)` BillingPlanFeature relation. Audit JSON is not part of this task.
- BillingPlan must have an exact unique Shopify plan handle. Treat it as immutable at service layer; schema must support Admin lookup by handle and active state.
- `PAID_METERED` plan rows require a place for the exact Shopify usage event/meter handle; `FREE` plans require a place for the lifetime conversation allowance. Schema alone cannot express kind-dependent nullability if Prisma cannot model it; service validation belongs to Admin-001.
- Plan default automated outbound-message soft/hard limits must be typed integer columns. Hard limit must be capable of finite values only; platform hard ceiling is DATABASE-003.
- Subscription remains one durable projection per shop (`shopId` unique), keeps the observed Shopify plan handle even when unmapped, and permits `planId = null` for NO_CONTRACT/UNMAPPED/SYNC_ERROR.
- Persist current `billingPeriod`, exact Shopify cycle start/end, trial end, cancel-at-end flag, provider subscription ID when returned, `lastSyncedAt`, bounded sync-error fields, pending observed plan handle/mapped plan ID/effective time.
- BillingPeriod uniqueness must use exact shop/start/end semantics and be indexed for current/recent shop periods; no calendar-month assumptions.
- Add all relations on Shop/Platform models required by Prisma integrity. Preserve unrelated schemas/models.
- Create the normal Prisma migration for this target schema through the repository migration workflow. Generated `migration.sql` is expected; do not add application/runtime raw SQL (`$queryRaw`, `$executeRaw`, `Prisma.sql`, direct driver SQL).
- The migration may destructively replace disposable development billing state; do not add compatibility/backfill machinery solely to preserve old development rows.
- Update `prisma/seed.mjs` so it uses the new typed BillingPlan/Subscription/BillingPeriod fields and can run after a normal development reset. Do not leave obsolete `handle`, `entitlements`, `limits`, `planHandle`, or invalid billing-period status values.
- Do not retain old JSON fields merely for backwards compatibility.

## Work Items

- [x] Inspect current BillingPlan/Subscription/BillingPeriod schema and Shop relations.
- [x] Implement enums/models/relations/indexes in `prisma/schema.prisma`.
- [x] Remove obsolete JSON/string billing runtime fields that ARCH-007 replaces.
- [x] Run Prisma format/validate/generate and regenerate ERD artifacts using repository scripts.
- [x] Create/apply the normal Prisma migration for the ARCH-007 typed billing catalog using the repository migration workflow. Development reset is allowed if Prisma requires it.
- [x] Update `prisma/seed.mjs` to the typed ARCH-007 schema and verify the seed no longer references removed billing fields/statuses.
- [x] Regenerate the normal DB artifacts after the migration/seed correction (Prisma client and ERD artifacts) and rerun schema validation.
- [x] Check for repository schema-level tests; none are declared in `package.json`.

## Interfaces / Contracts

Durable contract:

```text
Shop 1 -> 1 Subscription projection
BillingPlan.shopifyPlanHandle UNIQUE
BillingPlan 1 -> N BillingPlanFeature UNIQUE(planId, feature)
Subscription.planId nullable for NO_CONTRACT/UNMAPPED/SYNC_ERROR
BillingPeriod UNIQUE(shopId, periodStart, periodEnd)
```

No consumer implementation is authorized by this task.

## Dependencies

Explicit task dependencies are authoritative in YAML frontmatter. Do not begin unless every listed dependency is architect-accepted `complete` and any accepted Shared/database artifact required by this repository is available to consume.

## Enables

- ARCH-007-DATABASE-002

## Acceptance Criteria

- [x] A normal Prisma migration exists for the accepted ARCH-007 typed billing-catalog schema; no production-preservation backfill/compatibility machinery is added.
- [x] BillingPlan no longer relies on JSON entitlements/limits for ARCH-007 runtime semantics.
- [x] Plan handle, kind, usage meter handle, Free allowance and message defaults have typed schema representation.
- [x] Subscription can faithfully represent mapped current plan, unmapped handle, no contract, sync error and pending plan change.
- [x] BillingPeriod uses Shopify cycle boundaries without calendar-month defaults.
- [x] `prisma/seed.mjs` is valid against the new generated Prisma client and no longer references removed billing fields or invalid BillingPeriod enum values.
- [x] Prisma migration/schema validation, Prisma generation, ERD regeneration and `git diff --check` pass after the correction.

## Validation

Inspect the repository `package.json` first. Run the focused tests required by this task plus the repository-declared typecheck/lint/build/Prisma validation that actually exists, and `git diff --check`. Do not invent missing npm scripts.

## Implementation Notes

Development reset is explicitly authorized. Do not spend time preserving existing development billing rows.
Luna deterministic-execution guardrails:

- Treat this task file as the complete implementation contract. Do not infer additional product policy from old billing code.
- Inspect the named current implementation before editing, but if old code conflicts with ARCH-007, implement ARCH-007.
- Do not start an enabled/dependent task. Return only this task to `review` and STOP.
- Do not modify another repository except an explicitly permitted database submodule/package dependency pointer in this task.
- Do not add new billing raw SQL (`$queryRaw`, `$executeRaw`, `Prisma.sql`, raw driver SQL) to compensate for an unavailable Prisma delegate. Adopt/regenerate the accepted Prisma schema instead.
- Do not run `git commit` or `git push`.


## Completion Report

### Status

Ready for Review

### Files Changed

- `prisma/schema.prisma`
- `prisma/migrations/20260907171500_replace_arch007_typed_billing_catalog/migration.sql`
- `prisma/seed.mjs`
- `docs/generated/prisma-erd.puml`
- `docs/generated/erd.png`

### Work Completed

- Replaced legacy BillingPlan JSON fields with typed plan kind, Shopify handle, usage meter, Free allowance, outbound defaults, reserved terminal slots, and feature mappings.
- Added typed subscription projection statuses, current billing-cycle relation, observed/pending plan mappings, provider subscription identity, sync timestamps, and bounded sync-error fields.
- Added exact BillingPeriod shop/start/end uniqueness and typed period status, with Shop-to-Subscription one-to-one integrity.
- Added the normal destructive development-reset Prisma migration for the typed billing catalog.
- Updated development seed plans, feature mappings, subscription projection, cycle statuses, and reset ordering for the generated Prisma client.
- Regenerated Prisma client and ERD artifacts after the correction.

### Validation Results

- `npm run format` — passed.
- `npm run validate` — passed; Prisma schema valid.
- `npm run prisma:generate` — passed; Prisma Client v6.19.3 generated.
- `npm run erd` — passed; PlantUML and PNG regenerated.
- `node --check prisma/seed.mjs` — passed.
- `npx prisma migrate deploy` against a fresh local `moda_interact_shadow` database — passed; all 21 migrations, including ARCH-007-DATABASE-001, applied successfully.
- `node prisma/seed.mjs` against the migrated shadow database with a temporary Shopify session — passed; 3 typed plans and 80 demo usage events seeded.
- `git diff --check` — passed after normalizing generated PlantUML trailing whitespace.
- `npx prisma migrate dev --create-only` against the local development database — blocked by pre-existing checksum drift in `20260827154131_add_shopify_webhook_receipt_outbox` and `20260905195000_add_whatsapp_template_variants`; no reset or history rewrite was performed.
- Repository `package.json` declares no test, typecheck, lint, or build scripts.

### Deviations

The normal `prisma migrate dev --create-only` command could not run against the existing development database because Prisma detected previously applied migration checksum drift. The migration was generated from the repository's pre-ARCH-007 schema snapshot and validated by applying the complete migration chain to a fresh local shadow database.

### Assumptions

The development seed's existing `growth` plan remains the demo active subscription, while `starter` is seeded as the typed Free plan and `pro` as another paid metered mapping.

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Accepted.

### Findings

- Attempt 2 resolves both requested corrections. A normal Prisma migration now exists at `prisma/migrations/20260907171500_replace_arch007_typed_billing_catalog/migration.sql`, and `prisma/seed.mjs` has been updated to the typed ARCH-007 BillingPlan/Subscription/BillingPeriod schema.
- The final Prisma schema remains limited to the DATABASE-001 billing catalog/projection boundary and preserves unrelated models. BillingPlan uses typed plan kind/features/limits and an exact unique Shopify plan handle; Subscription remains one-per-shop and represents mapped, unmapped, no-contract, sync-error and pending-plan states; BillingPeriod uses exact Shopify cycle start/end semantics.
- Independent diff review against the pre-ARCH-007 workspace found no unrelated schema or historical-migration drift. The two historical migration files reported by local Prisma checksum drift are byte-identical to the pre-ARCH-007 workspace snapshot, so that local checksum condition was not introduced by this task.
- The generated migration is permitted to be destructive to disposable development billing data under ARCH-007's pre-production/breaking rollout. The agent validated the complete migration chain on a fresh database and successfully ran the updated seed against that migrated schema.
- No new application/runtime raw-SQL path (`$queryRaw`, `$executeRaw`, `Prisma.sql`, direct driver SQL) was introduced. Generated Prisma `migration.sql` is the expected database artifact.
- Prisma client/PlantUML/PNG ERD artifacts were regenerated and the generated PlantUML reflects the accepted typed billing catalog.
- The reported local `prisma migrate dev --create-only` checksum drift is non-blocking for DATABASE-001 because fresh-chain migration and seed validation passed and independent review confirmed the flagged historical migration files were not changed by this implementation.

### Reviewed Files

- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20260907171500_replace_arch007_typed_billing_catalog/migration.sql`
- `moda-interact-database/prisma/seed.mjs`
- `moda-interact-database/docs/generated/prisma-erd.puml`
- `moda-interact-database/docs/generated/erd.png`
- `moda-interact-database/package.json`
- `docs/decisions/database/ARCH-007/DATABASE-001-typed-plan-subscription-catalog.md`
- parent `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

### Validation Reviewed

Agent-reported Attempt 2 validation:

- `npm run format` — passed.
- `npm run validate` — passed.
- `npm run prisma:generate` — passed.
- `npm run erd` — passed.
- `node --check prisma/seed.mjs` — passed.
- full `prisma migrate deploy` chain on a fresh local database — passed, including DATABASE-001 migration.
- updated seed on that migrated fresh database — passed.
- `git diff --check` — passed.
- local existing development database `prisma migrate dev --create-only` — blocked only by pre-existing historical checksum drift; no history rewrite/reset was performed.

Independent architect inspection additionally compared the changed schema and historical migrations with the pre-ARCH-007 workspace snapshot and checked for new runtime raw-SQL APIs.

### Decision

`ARCH-007-DATABASE-001` is architect-accepted and Complete.

`ARCH-007-DATABASE-002` is now unblocked and Ready for its first claim. It starts with `attempt: 0`; the claiming agent increments it to Attempt 1.

The local development-database checksum drift is not an ARCH-007-DATABASE-001 defect. If it recurs during later database tasks, validate the new migration against a fresh disposable development database rather than rewriting historical migration files merely to satisfy a drifted local database.
