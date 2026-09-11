---
id: ARCH-007-DATABASE-003
architecture_id: ARCH-007
title: Add platform/shop billing policy, allowance adjustment and audit persistence
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on: 
  - ARCH-007-DATABASE-002
enables: 
  - ARCH-007-SHARED-001
  - ARCH-007-ADMIN-001
  - ARCH-007-BACKGROUND-001
created: 2026-09-07
updated: 2026-09-07
---

> **ARCH-010 supersession notice (2026-09-11):** This file is retained as ARCH-007 implementation/review history. Do **not** infer the current merchant subscription, recovery-capacity, Free-credit, automatic-overage, top-up, refund or lifecycle contract from this file. For current behaviour use [`ARCH-010`](../../../architecture/ARCH-010-merchant-lifecycle-state-transitions.md), the [`current pricing/billing model`](../../../product/pricing-and-billing-model.md), and the [`supersession map`](../../../architecture/ARCH-010-supersession-map.md). Historical task status, code evidence and non-superseded message/provider safety work remain valid.

# ARCH-007-DATABASE-003: Add platform/shop billing policy, allowance adjustment and audit persistence

## Architecture

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Create typed persistent Admin control-plane state for application-wide safety, per-shop overrides, Free allowance adjustments and privileged billing audit.

## Context

The merchant-facing bill is controlled by Shopify, but Moda needs local operational controls that can pause/cap autonomous messaging and grant support credits without rewriting usage history.

## Scope

Modify canonical Prisma schema/generated artifacts for one platform billing policy, one effective shop override row per shop, append-only allowance adjustments and audit events. Create the normal Prisma migration for this schema slice; no production data-preservation/backfill compatibility is required.

## Out of Scope

- Admin UI/actions.
- Plan price/tier configuration in Shopify.
- Runtime effective-policy computation.
- Exact Meta rate catalog.

## Requirements

- PlatformBillingPolicy must have a singleton-safe identity, global pause-new-recoveries, global pause-automated-WhatsApp, finite absolute outbound hard cap, warning-percent or equivalent bounded threshold, integer version and timestamps.
- ShopBillingPolicyOverride is unique by shop and stores nullable override values (soft/hard message limit, pause flags, optional recovery safety ceiling), required reason for any active override, optional expiresAt and modifying PlatformAdmin relation.
- A shop hard-cap override never changes the platform absolute maximum; enforcement belongs to BACKGROUND-001.
- BillingAllowanceAdjustment is append-only, shop-scoped, typed to Free lifetime counter, signed non-zero quantity at service layer, reason, PlatformAdmin and createdAt. Reversal is another signed row.
- BillingAuditEvent uses a typed action enum covering plan catalog changes, platform policy changes, shop override changes/expiry, Free allowance adjustment, automation pause/resume, billing-event retry and billing correction creation. Bounded Json before/after snapshots are allowed only for audit evidence, not entitlement execution.
- Add indexes for active/expiring overrides, shop adjustment aggregation and recent audit lookup by shop/admin/action.
- Do not add new billing runtime raw SQL (`$queryRaw`, `$executeRaw`, `Prisma.sql`, raw driver SQL). The normal Prisma-generated migration SQL artifact required by this task is allowed and required.

## Work Items

- [x] Add policy/override/adjustment/audit enums/models and relations.
- [x] Add bounded lookup indexes.
- [x] Create/apply the normal Prisma migration for this schema slice using the repository workflow.
- [x] Regenerate Prisma client and ERD artifacts after migration generation/application.
- [x] Validate that deleting a Shop/Admin does not silently destroy required financial audit history; choose safe relation/onDelete semantics consistent with existing admin registry.

- If this schema slice invalidates repository seed/fixture code, update that seed/fixture in the same task and validate the normal development reset path.

## Interfaces / Contracts

Effective policy inputs exposed to later services:

```text
PlatformBillingPolicy
BillingPlan defaults
ShopBillingPolicyOverride (ignored when expired)
BillingAllowanceAdjustment SUM for FREE_RECOVERY_LIFETIME
```

## Dependencies

Explicit task dependencies are authoritative in YAML frontmatter. Do not begin unless every listed dependency is architect-accepted `complete` and any accepted Shared/database artifact required by this repository is available to consume.

## Enables

- ARCH-007-SHARED-001
- ARCH-007-ADMIN-001
- ARCH-007-BACKGROUND-001

## Acceptance Criteria

- [x] Platform singleton and shop override uniqueness are enforceable through Prisma schema/service conventions.
- [x] Audit history is durable and separate from operational structured logs.
- [x] Allowance adjustment history is append-only and aggregatable.
- [x] Expired overrides can be queried/ignored without deleting the audit trail.
- [x] No billing runtime limit is stored only as free-form JSON.
- [x] Prisma/ERD validation passes with the normal Prisma migration artifact present.

## Validation

Inspect the repository `package.json` first. Run the focused tests required by this task plus the repository-declared typecheck/lint/build/Prisma validation that actually exists, and `git diff --check`. Do not invent missing npm scripts.

## Implementation Notes


Luna deterministic-execution guardrails:

- Treat this task file as the complete implementation contract. Do not infer additional product policy from old billing code.
- Inspect the named current implementation before editing, but if old code conflicts with ARCH-007, implement ARCH-007.
- Do not start an enabled/dependent task. Return only this task to `review` and STOP.
- Do not modify another repository except an explicitly permitted database submodule/package dependency pointer in this task.
- Do not add new billing raw SQL (`$queryRaw`, `$executeRaw`, `Prisma.sql`, raw driver SQL) to compensate for an unavailable Prisma delegate. Adopt/regenerate the accepted Prisma schema instead.
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-DATABASE-003` branch and the mirrored parent-workspace `task/ARCH-007-DATABASE-003` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.


## Completion Report

### Status

Ready for Review

### Files Changed

`prisma/schema.prisma`, `prisma/migrations/20260907182005_add_billing_policy_overrides_audit/migration.sql`, `docs/generated/prisma-erd.puml`, and `docs/generated/erd.png`.

### Work Completed

- Added singleton-safe `PlatformBillingPolicy`, unique `ShopBillingPolicyOverride`, append-only `BillingAllowanceAdjustment`, typed `BillingAuditAction`, and `BillingAuditEvent` models with Shop/PlatformAdmin relations.
- Added bounded expiry, shop/counter aggregation, and shop/admin/action audit indexes.
- Used restrictive foreign keys for allowance/admin and audit/admin history; audit Shop links are nullable with `SetNull`, while operational overrides remain cascadeable/reassignable.
- Generated and applied the normal DATABASE-003 Prisma migration without unrelated historical drift operations.

### Validation Results

- `npm run format` — passed.
- `npm run validate` — passed.
- `npm run prisma:generate` — passed; Prisma Client v6.19.3 generated.
- `npm run erd` — passed; PlantUML and PNG regenerated.
- `npx prisma migrate deploy` against local `moda_interact_shadow_attempt2` — passed; all 23 migrations applied.
- PostgreSQL catalog verification — passed for singleton/override, expiry, allowance aggregation, and audit lookup indexes.
- PostgreSQL foreign-key verification — passed for restrictive financial-history relations and nullable audit/override admin relations.
- Prisma-only deletion safety check — passed; Shop/Admin deletion was blocked and the audit row remained preserved.
- `git diff --check` — passed after normalizing generated PlantUML trailing whitespace.
- Repository `package.json` declares no test, typecheck, lint, or build scripts.

### Deviations

The existing development database was not reset or modified; migration validation used the isolated local disposable shadow database. Prisma's generated migration included unrelated historical rename drift, which was excluded to keep this migration scoped to DATABASE-003.

### Assumptions

`BillingAllowanceAdjustment.quantity` is signed and non-zero at the service layer, as required by the task; Prisma does not encode that conditional value constraint.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Accepted

### Review Notes

- Attempt 1 accepted. The implementation adds the typed ARCH-007 control-plane persistence required by this task: `PlatformBillingPolicy`, unique per-shop `ShopBillingPolicyOverride`, append-only `BillingAllowanceAdjustment`, typed `BillingAuditAction`, and durable `BillingAuditEvent`.
- The platform policy uses the canonical `id = "default"` singleton convention. Later Admin/Background services must address that canonical identity only; no consumer may create or infer alternate platform-policy identities.
- Shop override lookup/expiry, allowance aggregation, and recent audit lookup are covered by bounded indexes.
- Financial/audit deletion semantics are architecture-conformant: allowance history and admin-attributed audit history are protected with restrictive foreign keys; audit shop identity can be retained as historical evidence even if the live Shop relation is removed.
- The normal Prisma migration is present and scoped to DATABASE-003. The stale task sentence that said "Do not add migrations/raw SQL" has been corrected: normal Prisma migration SQL is required; new runtime billing raw SQL remains prohibited.
- No seed change was required because these additive control-plane models do not invalidate the existing development seed/reset path.

### Reviewed Files

- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20260907182005_add_billing_policy_overrides_audit/migration.sql`
- `moda-interact-database/docs/generated/prisma-erd.puml`
- `moda-interact-database/docs/generated/erd.png`
- `docs/decisions/database/ARCH-007/DATABASE-003-billing-policy-overrides-audit.md`

### Validation Reviewed

Reviewed the submitted validation evidence for Prisma format/validate/generate, fresh 23-migration deployment, ERD regeneration, PostgreSQL index/foreign-key verification, Prisma deletion-safety verification, and `git diff --check`. Independently inspected the schema delta and migration DDL against the architect-accepted DATABASE-002 baseline; no unrelated schema drift or new runtime raw-SQL path was found.

### Architecture Conformance

Conformant. DATABASE-003 completes the ARCH-007 database foundation required before canonical Shared billing contracts are defined.

### Follow-up

`ARCH-007-SHARED-001` is unblocked and must be returned to `ready` with no active claim and `attempt: 0`. `ARCH-007-ADMIN-001` and `ARCH-007-BACKGROUND-001` remain Pending because each still depends on architect-accepted `ARCH-007-SHARED-002`.
