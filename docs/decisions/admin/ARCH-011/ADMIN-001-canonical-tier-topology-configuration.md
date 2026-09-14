---
id: ARCH-011-ADMIN-001
architecture_id: ARCH-011
title: Enforce canonical topology in Admin plan-catalog mutations
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 55
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-011-DATABASE-002
- ARCH-011-SHARED-002
- ARCH-010-ADMIN-009
enables:
- ARCH-011-ADMIN-002
created: 2026-09-14
updated: 2026-09-14
---
# ARCH-011-ADMIN-001

## Authorized implementation surface
```text
src/app/actions/billing-plan.ts
src/lib/admin/billing-plan-mutation.ts
src/lib/admin/billing-plan-topology.ts           # new
src/components/admin/billing-plan-catalog.tsx    # topology display/input only
src/i18n/locales/en.json
src/i18n/required-keys.ts
tests/security/admin-billing-plan.test.mjs
tests/security/admin-billing-topology.test.mjs   # new
```
No tenant audit UI here.

## Exact mutation sequence
Create `billing-plan-topology.ts` adapter that loads complete active plans + active edges inside the caller's Prisma transaction and maps them to Shared `validateCanonicalPlanTopology`; it must not implement its own graph algorithm.

For every create/update/toggle action that can change `active`, plan economics or edge final state:
1. require existing SUPER_ADMIN authorization;
2. construct/propose final plan/edge state inside the same Prisma transaction;
3. Shared topology preflight;
4. run existing ARCH-010 economics guardrail (`assertBillingUpgradeEconomicsPass`) exactly where it currently applies;
5. perform writes;
6. rely on DATABASE-002 deferred DB constraint at commit;
7. retain existing `PLAN_CATALOG_CHANGED` and `UPGRADE_ECONOMICS_EVALUATED` audit events;
8. catch only the bounded topology DB error prefix and map to safe Admin error; rethrow unknown DB errors.

Do not add rank/order column. Direction preview uses Shared classifier and displays canonical chain only.

## Validation
```text
node --test tests/security/admin-billing-plan.test.mjs tests/security/admin-billing-topology.test.mjs
npm run test:unit
npm test
npx tsc --noEmit --pretty false
npm run lint
npm run prisma:validate
npm run build
npm run format:check
git diff --check
```

## Completion protocol

After all Work Items, Acceptance Criteria and Validation pass: update the Completion Report, set task status to `review`, clear the active claim according to the normal launcher protocol, return control to `moda_architect`, and **STOP**. Do not start an enabled/follow-on task.
