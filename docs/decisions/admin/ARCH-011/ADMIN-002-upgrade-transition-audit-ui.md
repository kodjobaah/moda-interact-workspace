---
id: ARCH-011-ADMIN-002
architecture_id: ARCH-011
title: Add read-only ARCH-011 plan-transition audit UI
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 60
executor: null
claimed_at: null
attempt: 0
depends_on:
- ARCH-011-ADMIN-001
- ARCH-011-DATABASE-001
enables:
- ARCH-011-SYSTEM-TEST-001
created: 2026-09-14
updated: 2026-09-14
---
# ARCH-011-ADMIN-002

## Authorized implementation surface
```text
src/lib/admin/data.ts
src/lib/admin/types.ts
src/components/admin/tenant-billing.tsx
src/components/admin/billing-drawers.tsx
src/i18n/locales/en.json
src/i18n/required-keys.ts
tests/security/admin-billing-transition-audit.test.mjs   # new
```
No billing-plan mutations in this task.

## Exact read model
For selected shop, query BillingPeriods newest-first; each period includes segments ordered `effectiveFrom asc` and transitions ordered `createdAt asc`. Read snapshots verbatim; never recompute historical plan names/allowances from current BillingPlan.

Render transition fields: origin/status/applicationMode, from snapshots, requested snapshots or N/A, provider-confirmed snapshots or N/A, provider cycle/event/effective evidence, target/alreadyGranted/delta, timestamps/failureCode. Requested Scale + confirmed Growth must show both and applied plan Growth. PROVIDER_OBSERVED shows requested=N/A. Pending downgrade comes from Subscription.pendingPlan/pendingEffectiveAt in a separate section and has no proration fields.

Never render `providerEvidence` raw JSON, provider tokens, headers or credentials. Only bounded scalar evidence listed above.

## Validation
```text
node --test tests/security/admin-billing-transition-audit.test.mjs
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
