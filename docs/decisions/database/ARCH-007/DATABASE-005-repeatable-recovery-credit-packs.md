---
id: ARCH-007-DATABASE-005
architecture_id: ARCH-007
title: Add repeatable prepaid recovery-credit pack persistence
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
status: complete
priority: 36
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-007-DATABASE-004
enables:
  - ARCH-007-SHARED-005
  - ARCH-007-DATABASE-006
  - ARCH-007-ADMIN-005
  - ARCH-007-SHOPIFY-004
  - ARCH-007-BACKGROUND-009
created: 2026-09-08
updated: 2026-09-08
---

# ARCH-007-DATABASE-005: Add repeatable prepaid recovery-credit pack persistence

## Product contract

All plans may sell repeatable recovery-credit packs.

Consumption order is fixed:

```text
FREE:
  free lifetime allowance
  -> purchased recovery credits
  -> block new recovery

PAID_METERED:
  included recovery units for current Shopify billing period
  -> purchased recovery credits
  -> normal Shopify overage usage
```

Purchased credits:
- are prepaid/explicitly purchased;
- do not expire;
- survive plan changes, billing-cycle changes, uninstall/reinstall of the same durable Shop;
- may be replenished repeatedly by purchasing another pack;
- are never recreated/reset from the Free lifetime allowance.

Shopify remains authoritative for monetary price. Moda stores pack quantity/meter mapping and credit state, not top-up money price.

## Exact Prisma changes

Modify `moda-interact-database/prisma/schema.prisma`.

### Enum additions

Add:

```prisma
enum EntitlementCounter {
  FREE_RECOVERY_LIFETIME
  PURCHASED_RECOVERY_CREDITS
  @@schema("billing")
}
```

Add to `UsageMetric`:

```prisma
RECOVERY_CREDIT_PACK_PURCHASE
```

Add:

```prisma
enum RecoveryCreditPurchaseStatus {
  PENDING_BILLING
  ACTIVE
  NEEDS_ATTENTION
  CANCELLED
  @@schema("billing")
}
```

### BillingPlan fields

Add exactly:

```prisma
includedRecoveryConversationAllowance Int?
recoveryCreditPackEnabled              Boolean @default(false)
recoveryCreditsPerPack                 Int?
shopifyRecoveryCreditPackEventHandle   String?
```

Semantics:
- `includedRecoveryConversationAllowance` is an operational mirror used only for paid included -> top-up -> overage routing. It must be configured to match the Shopify plan policy; Shopify remains authoritative for commercial price/tier configuration.
- It is NOT a price.
- `recoveryCreditsPerPack` is the number of recovery conversations granted by one successfully billed pack.
- `shopifyRecoveryCreditPackEventHandle` is the Shopify App Pricing usage-meter event handle used to charge one pack.
- monetary pack price MUST NOT be added to Prisma.

Add relation:

```prisma
recoveryCreditPurchases RecoveryCreditPurchase[]
```

### ShopEntitlementCounter

Add:

```prisma
grantedQuantity Int @default(0)
```

Rules:
- FREE counter continues to use effective Free allowance and ignores `grantedQuantity`.
- PURCHASED_RECOVERY_CREDITS uses:
  `available = grantedQuantity - committedQuantity - reservedQuantity`.

### RecoveryCreditPurchase model

Add exactly one durable row per merchant top-up request:

```prisma
model RecoveryCreditPurchase {
  id String @id

  shopId String
  shop   Shop @relation(fields: [shopId], references: [id], onDelete: Cascade)

  planId String?
  plan   BillingPlan? @relation(fields: [planId], references: [id], onDelete: SetNull)

  shopifyPlanHandleSnapshot String
  shopifyEventHandleSnapshot String
  creditsGranted Int

  status RecoveryCreditPurchaseStatus @default(PENDING_BILLING)

  usageEventId String @unique
  usageEvent   UsageEvent @relation(fields: [usageEventId], references: [id], onDelete: Restrict)

  activatedAt DateTime?
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@index([shopId, status, createdAt])
  @@index([planId, createdAt])
  @@schema("billing")
}
```

`id` is application supplied. It is the merchant-request idempotency identity. Do NOT add a second request-key column.

Add inverse relations required by Prisma to `Shop`, `BillingPlan`, and `UsageEvent`.

## Required invariants

Application/schema validation must enforce:
- top-up enabled => `recoveryCreditsPerPack > 0`;
- top-up enabled => non-empty `shopifyRecoveryCreditPackEventHandle`;
- paid top-up enabled => `includedRecoveryConversationAllowance >= 0`;
- Free may have a top-up meter while its normal recovery usage handle remains null;
- normal recovery meter handle and top-up pack meter handle must not be the same;
- `creditsGranted > 0`;
- one purchase links to exactly one UsageEvent;
- one UsageEvent links to at most one RecoveryCreditPurchase.

Do not store currency or monetary pack price.

## Migration/tests

Generate the normal Prisma migration. Regenerate normal DB artifacts/ERD.

Focused schema tests must prove:
1. repeated purchase rows for the same shop are legal when IDs differ;
2. the same purchase ID cannot be inserted twice;
3. one UsageEvent cannot activate two purchases;
4. purchased counter supports non-zero `grantedQuantity`;
5. existing Free counter/reservations remain valid;
6. Free plan can have top-up meter mapping without a normal recovery usage meter;
7. paid top-up configuration supports included allowance + normal usage meter + distinct top-up meter.

## Stop condition

Do not implement purchase creation, Shopify billing events, credit activation or recovery admission in this task.

## Luna execution rules

- Treat this file as the complete execution contract. Do not redesign the feature.
- Do not broaden scope into adjacent billing/conversation work.
- Before editing, inspect the exact named current files and repository `package.json`.
- Use only repository scripts that actually exist.
- Do not modify another repository unless this task explicitly authorises a dependency pointer/version update.
- Do not start a task listed under `enables`.
- Return only this task to `review` and STOP.
- Follow `docs/agent-vcs-ownership-policy.md` for all Git/VCS operations.
- Before returning this task to `review`, commit and push the assigned implementation `task/ARCH-007-DATABASE-005` branch and the mirrored parent-workspace `task/ARCH-007-DATABASE-005` branch; the parent commit is limited to the current task file plus explicitly task-owned evidence.
- Do not merge either task branch into `main`, push `main`, force-push, or stage the parent-workspace implementation submodule gitlink.

## Completion Report

### Status
Ready for Review (Attempt 2)

### Files Changed

- `moda-interact-database/prisma/schema.prisma`
- `moda-interact-database/prisma/migrations/20260908081322_add_repeatable_recovery_credit_packs/migration.sql`
- `moda-interact-database/docs/generated/prisma-erd.puml`
- `moda-interact-database/docs/generated/erd.png`
- `moda-interact-database/scripts/validate-recovery-credit-pack-schema.mjs`
- `moda-interact-database/package.json`
- `docs/decisions/database/ARCH-007/DATABASE-005-repeatable-recovery-credit-packs.md`

### Work Completed

- Added typed recovery-credit purchase status and usage/counter enum values.
- Added repeatable pack configuration fields and relations to `BillingPlan`.
- Added `grantedQuantity` to entitlement counters and the durable `RecoveryCreditPurchase` model linked one-to-one with `UsageEvent`.
- Added migration checks for positive credits, enabled-pack configuration, paid included allowance, and distinct normal/top-up meter handles.
- Regenerated Prisma/ERD artifacts and added deterministic focused assertions for the schema and migration invariants.
- Corrected the existing unapplied migration so an enabled recovery-credit pack rejects both NULL and non-positive `recoveryCreditsPerPack` values without making the field globally required.
- Strengthened the focused validator to assert the NULL-safe quantity predicate and preserve repeat-purchase, one-to-one UsageEvent, positive-credit, counter-default, nullable-meter, paid-allowance, distinct-meter, and no-monetary-price invariants.

### Validation Results

- `npm run format`: passed.
- `npm run prisma:validate`: passed.
- `npm run prisma:generate`: passed.
- `npm run test:recovery-credit-packs`: passed.
- `npm run erd`: passed; PlantUML and PNG artifacts regenerated.
- `git diff --check`: passed in the database repository and workspace after normalizing generated ERD text whitespace.
- No repository-declared typecheck/build/test script exists beyond the Prisma/ERD commands above.
- No PostgreSQL integration harness exists in this repository; deterministic schema/migration assertions were used as permitted by the task contract.

### Deviations
None.

### Assumptions

The existing DATABASE-005 schema/migration implementation was retained except for the required in-place correction to the unapplied migration; no application/runtime code or second migration was added.

### Unresolved Issues
None.

### Architectural Concerns
None.

## Architect Review

### Review Status

Accepted

### Review Notes

Attempt 2 is architect-accepted Complete.

The existing unapplied DATABASE-005 migration was corrected in place so an enabled recovery-credit pack now requires `recoveryCreditsPerPack IS NOT NULL AND recoveryCreditsPerPack > 0`. Disabled pack configurations may still leave the quantity null. No second migration was created.

The focused validator now asserts the NULL-safe predicate explicitly and preserves deterministic checks for the required persistence invariants.

The remaining DATABASE-005 contract is intact:

- `PURCHASED_RECOVERY_CREDITS` and `RECOVERY_CREDIT_PACK_PURCHASE` are present;
- `RecoveryCreditPurchaseStatus` is present;
- BillingPlan contains the included allowance, enable flag, pack quantity, and Shopify pack-event handle;
- `ShopEntitlementCounter.grantedQuantity` defaults to zero;
- `RecoveryCreditPurchase.id` remains application supplied;
- `usageEventId` remains required/unique;
- `creditsGranted > 0` remains enforced;
- repeat purchases for one shop remain legal when purchase IDs differ;
- Free may have a pack meter while its normal recovery meter is null;
- paid enabled-pack configuration requires a non-null/non-negative included allowance;
- normal and pack event handles cannot be identical when both are present;
- no monetary pack price/currency field was added;
- DATABASE-004 Conversation schema remains unchanged.

### Validation Reviewed

Repository-agent Completion Report records Prisma format/validate/generate, focused recovery-credit assertions, ERD generation, and `git diff --check` as passing.

Architect independently ran:

```text
node scripts/validate-recovery-credit-pack-schema.mjs
```

and it passed.

Static inspection also verified that only one recovery-credit migration exists and that the corrected CHECK is NULL-safe.

### Architecture Conformance

Accepted.

### Follow-up

`ARCH-007-SHARED-005` is now Ready.

`ARCH-007-DATABASE-006` is now Ready.

`ARCH-007-SHARED-006` remains Pending until SHARED-005 is architect-accepted Complete.

`ARCH-007-BACKGROUND-010` remains Pending until DATABASE-006 is architect-accepted Complete.

No system-test task is automatically started.
