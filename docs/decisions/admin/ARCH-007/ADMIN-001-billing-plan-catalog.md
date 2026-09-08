---
id: ARCH-007-ADMIN-001
architecture_id: ARCH-007
title: Build SUPER_ADMIN billing plan catalog and Shopify-handle mapping
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
status: complete
priority: 60
executor: null
claimed_at: null
attempt: 2
depends_on: 
  - ARCH-007-SHARED-002
  - ARCH-007-DATABASE-003
enables: 
  - ARCH-007-ADMIN-002
created: 2026-09-07
updated: 2026-09-08
---
# ARCH-007-ADMIN-001: Build SUPER_ADMIN billing plan catalog and Shopify-handle mapping

## Architecture

Canonical: `docs/architecture/ARCH-007-shopify-billing-usage-cost-control.md`

## Objective

Create the Admin control plane for registering Shopify-created pricing plans into Moda without a code deploy and managing typed Moda entitlement/safety mapping.

## Context

The agreed workflow is: configure the plan/meter in Shopify first, then use Moda Admin to register the immutable Shopify plan handle and internal policy. Admin does not create or price Shopify plans.

## Scope

Protected Admin billing plan list/create/edit/activate/deactivate routes/components/server actions and tests. Use Prisma typed models and existing Admin auth/role conventions.

## Out of Scope

- Calling Shopify to create/change plan prices or meter tiers.
- Platform/shop operational policy (ADMIN-002).
- Billing event retry/correction (ADMIN-004).

## Requirements

- Add Billing navigation/page following existing Admin UI/component conventions.
- Plan create form requires exact Shopify plan handle, display name, kind FREE|PAID_METERED, feature toggles, plan default soft/hard automated outbound limits.
- FREE validation: lifetime conversation allowance required positive (initial product row = 5), Shopify usage event handle must be empty/not reportable.
- PAID_METERED validation: exact Shopify usage event/meter handle required; Free lifetime allowance must be null/not used.
- Plan handle is immutable after creation. To correct a mistaken handle, deactivate bad mapping and create a new one; do not mutate history under existing subscriptions.
- Usage event handle changes are financially sensitive: require explicit SUPER_ADMIN action, reason/audit and warn that existing UsageEvents snapshot their old handle; no retroactive rewrite.
- Only SUPER_ADMIN may create/activate/deactivate/edit catalog mappings. Read access may follow existing ADMIN operational policy.
- Every mutation writes typed BillingAuditEvent with actor/reason/bounded before/after.
- Do not expose secret Shopify credentials in UI/actions/logs.
- Do not offer Basic price/included/overage inputs as Moda-authoritative values. Those are Shopify-owned; optional read-only descriptive fields must be clearly non-authoritative if added.

## Work Items

- [x] Add Admin Billing plan catalog page/routes/actions.
- [x] Implement strict server-side validation and immutable handle rule.
- [x] Implement feature/default-safety editing.
- [x] Write audit events in same transaction as mutation where practical.
- [x] Add auth/role/security tests and validation tests for Free/paid/meter/immutability.
- [x] Any components created make sure icu internationalization is supported using the same approach as the current components.
## Interfaces / Contracts

Workflow contract:

```text
Shopify Partner/Dev Dashboard: create plan + meter/tier
SUPER_ADMIN Moda: register exact plan_handle + meter_handle + Moda features/safety
next subscription reconciliation: plan becomes mapped
```

## Dependencies

Explicit task dependencies are authoritative in YAML frontmatter. Do not begin unless every listed dependency is architect-accepted `complete` and any accepted Shared/database artifact required by this repository is available to consume.

## Enables

- ARCH-007-ADMIN-002

## Acceptance Criteria

- [x] A newly Shopify-created plan can be recognized after Admin mapping with no app code deploy.
- [x] Admin cannot silently create/change Shopify commercial price/tier.
- [x] Plan handle cannot be edited in place.
- [x] Free/paid kind-specific validation is enforced server-side.
- [x] Every mutation is audited.
- [x] Unauthorized roles cannot mutate catalog.
- [x] Tests/build/validation pass.

## Validation

Inspect the repository `package.json` first. Run the focused tests required by this task plus the repository-declared typecheck/lint/build/Prisma validation that actually exists, and `git diff --check`. Do not invent missing npm scripts.

## Implementation Notes

Exact Shared dependency: `@modainteract/moda-interact-shared@0.7.3`. Adopt the accepted database revision and Shared billing types; do not recreate plan-kind or billing enums locally.


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

- `moda-interact-admin/src/app/actions/billing-plan.ts`
- `moda-interact-admin/src/components/admin/billing-plan-catalog.tsx`
- `moda-interact-admin/src/lib/admin/billing-plan-audit.ts`
- `moda-interact-admin/tests/security/admin-billing-plan.test.mjs`

### Work Completed

- Corrected update audit snapshots to derive `beforeValue` from the persisted BillingPlan row and its enabled feature rows, while `afterValue` reflects the validated resulting values.
- Preserved the immutable plan handle, explicit usage-handle confirmation, bounded reason, and same-transaction mutation/audit behavior.
- Corrected existing paid-plan form defaults so a null Free lifetime allowance remains empty instead of being submitted as `5`.
- Added focused behavioral regressions for persisted before/after audit values and paid-plan edit defaults.

### Validation Results

- Focused billing/security tests: 6 passed, 0 failed.
- Full Admin test suite: 109 passed, 0 failed.
- `npx tsc --noEmit`: passed with no diagnostics.
- `npm run prisma:validate`: passed.
- `npm run lint`: passed with 2 existing queue-monitor React hook warnings.
- `npm run build`: passed; `/billing` remains a dynamic route.
- Targeted Prettier check for changed billing files: passed.
- `git diff --check`: passed.
- Full `npm run format:check` was not rerun; targeted formatting passed.

### Deviations

None.

### Assumptions

- Shopify remains authoritative for commercial plan pricing and tiers; Admin stores only the immutable handles and Moda entitlement/safety policy.
- Existing merchant-support worktree changes are pre-existing and were preserved.

### Unresolved Issues

- Node test runs emit existing module-type warnings because the package does not declare `type: module`.
- Production build emits existing Next workspace-root and BullMQ optional/dynamic dependency warnings.

### Architectural Concerns

- None identified for this task. No commit or push was performed; implementation is ready for developer commit/push after architect acceptance.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 is architect-accepted Complete.

The two Attempt 1 corrections are implemented correctly.

#### Persisted before/after audit snapshots

Update audit state now uses:

```text
beforeValue
  -> actual existing Prisma BillingPlan row
  -> actual existing enabled BillingPlanFeature rows

afterValue
  -> validated requested/resulting plan values
```

The new `billingPlanAuditSnapshot()` helper captures:

```text
shopifyPlanHandle
name
kind
active
shopifyUsageEventHandle
freeLifetimeConversationAllowance
defaultOutboundSoftLimit
defaultOutboundHardLimit
terminalMessageReservedSlots
enabled features
```

Therefore a financially sensitive usage-handle change such as:

```text
meter-v1 -> meter-v2
```

is represented as a real before/after transition rather than recording the new
value on both sides.

The mutation and its BillingAuditEvent remain in the same Prisma transaction.

The immutable Shopify plan handle and explicit usage-handle-change confirmation
remain intact.

#### Existing paid-plan form default

An existing plan now uses:

```text
plan.freeLifetimeConversationAllowance ?? ""
```

rather than falling back to the new-Free-plan default of `5`.

Therefore an existing PAID_METERED plan with a persisted null Free allowance no
longer submits an artificial Free allowance when edited.

The create form may retain `5` as the initial FREE-plan default; server-side
FREE/PAID_METERED validation remains authoritative.

### Accepted ADMIN-001 behavior

The accepted implementation provides:

- protected Admin `/billing` catalog;
- existing platform-admin read authorization;
- SUPER_ADMIN-only mutation;
- immutable Shopify plan handle;
- strict FREE vs PAID_METERED validation;
- paid normal Shopify usage-event handle mapping;
- Free lifetime allowance mapping;
- finite outbound soft/hard/terminal-slot policy fields;
- feature toggles;
- explicit confirmation before changing a usage-event handle;
- transactional PLAN_CATALOG_CHANGED audit writes;
- bounded mutation reason;
- existing Admin ICU/i18n usage;
- Prisma-first database access;
- no Shopify monetary price/tier editing.

### Pre-feature-branch workflow exception

The developer explicitly requested that ADMIN-001 and BACKGROUND-010 finish
architect review before enabling the new mirrored feature-branch workflow.

ADMIN-001 Attempt 2 was therefore correctly completed without task-branch,
commit or push evidence.

This is accepted as a legacy-workflow task and must not be reopened merely to
retrofit feature-branch history.

The new feature-branch workflow remains deferred until BACKGROUND-010 is also
architect-accepted.

### Reviewed Files

- `moda-interact-admin/src/app/actions/billing-plan.ts`
- `moda-interact-admin/src/components/admin/billing-plan-catalog.tsx`
- `moda-interact-admin/src/lib/admin/billing-plan-audit.ts`
- `moda-interact-admin/src/lib/admin/billing-plan-validation.ts`
- `moda-interact-admin/tests/security/admin-billing-plan.test.mjs`
- `docs/decisions/admin/ARCH-007/ADMIN-001-billing-plan-catalog.md`

Architect comparison against Attempt 1 verified that the implementation changes
for Attempt 2 are bounded to the requested billing audit/form corrections plus
their focused test/helper.

### Validation Reviewed

Repository-agent Completion Report records:

```text
focused billing/security tests: 6 passed
full Admin suite: 109 passed
typecheck: passed
Prisma validation: passed
build: passed
targeted formatting: passed
lint: passed with 2 unchanged queue-monitor hook warnings
git diff --check: passed
```

Architect static inspection verified the corrected before/after snapshot source
and existing-paid-plan allowance default.

### Architecture Conformance

Accepted.

### Follow-up

`ARCH-007-ADMIN-001` is Complete.

The following tasks now have all of their dependencies Complete and become
Ready:

```text
ARCH-007-ADMIN-002
  depends_on ADMIN-001

ARCH-007-ADMIN-005
  depends_on ADMIN-001, DATABASE-005, SHARED-006
```

`ARCH-007-ADMIN-003` remains Pending behind ADMIN-002.

`ARCH-007-SHOPIFY-004` remains Pending behind ADMIN-005.

System-test tasks remain terminal/manual-gated and are not automatically
started.
