---
id: ARCH-017-DATABASE-001
architecture_id: ARCH-017
title: Persist dynamic features, durable MerchantPricingPlan lifecycle and platform-owned billing controls
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 10
executor: null
claimed_at: null
attempt: 0
depends_on: []
enables:
- ARCH-017-BACKGROUND-001
- ARCH-017-SHOPIFY-001
- ARCH-017-ADMIN-001
created: 2026-09-18
updated: 2026-09-18
---

# ARCH-017-DATABASE-001

## Objective

Implement the complete durable database contract for ARCH-017 in `moda-interact-database` only.

This task MUST deliver all schema/migration/seed support required so BACKGROUND, SHOPIFY and ADMIN can execute independently after this task is accepted.

Do not implement application, background or Admin behavior here.

ARCH-011 is out of scope. Do not add BillingPlan segments, prorated transitions or same-cycle upgrade schema.

## Read before editing

Read these exact files before changing anything:

```text
prisma/schema.prisma
prisma/seed.mjs
package.json
prisma/migrations/20260912000000_arch010_first_production_baseline/migration.sql
prisma/migrations/20260915090000_arch014_merchant_pricing_catalogue/migration.sql
docs/architecture/ARCH-017-billing-plan-materialisation-dynamic-features.md
docs/architecture/ARCH-014-admin-managed-merchant-pricing-catalogue.md
docs/architecture/ARCH-010-merchant-lifecycle-state-transitions.md
```

Inspect the latest migration name before choosing the new migration timestamp. Create exactly one new ARCH-017 migration after the latest current migration. Do not edit an already-applied migration.

## Authorized implementation surface

```text
prisma/schema.prisma
prisma/migrations/<new_arch017_migration>/migration.sql
prisma/seed.mjs
scripts/validate-arch017-billing-materialisation-schema.mjs
package.json                            # only to add the validator script
docs/generated/prisma-erd.puml          # regenerated
docs/generated/prisma-erd.png           # regenerated when PlantUML is available
```

Do not edit another repository.

## Exact target schema

### 1. Remove the closed feature enum

Delete this enum completely:

```prisma
enum BillingPlanFeatureIdentifier {
  CHECKOUT_RECOVERY
  AI_CONVERSATIONS
  PRODUCT_SEARCH
  ORDER_SUPPORT

  @@schema("billing")
}
```

Do not replace it with another enum containing feature names.

### 2. Add activation-mode enum

Add this enum in schema `billing`:

```prisma
enum FeatureActivationMode {
  ALWAYS_ENABLED
  MERCHANT_OPT_IN

  @@schema("billing")
}
```

This enum describes stable behavior categories. It is not the feature catalogue.

### 3. Add Feature catalogue

Add exactly this logical model (format with `prisma format`):

```prisma
model Feature {
  id String @id @default(cuid())

  key            String                @unique @db.VarChar(128)
  displayName    String                @db.VarChar(255)
  description    String?               @db.Text
  active         Boolean               @default(true)
  activationMode FeatureActivationMode
  systemRequired Boolean               @default(false)

  merchantPricingPlans MerchantPricingPlanFeature[]
  billingPlans         BillingPlanFeature[]
  shopPreferences      ShopFeaturePreference[]

  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@index([active, displayName])
  @@schema("billing")
}
```

`Feature.key` is the immutable machine identity. The database does not need an enum of all keys.

### 4. Extend MerchantPricingPlan

Preserve the existing unique handle:

```prisma
shopifyPlanHandle String @unique
```

Add:

```prisma
shopifyRecoveryUsageEventHandle String? @db.VarChar(255)
materializedAt                  DateTime?
features                        MerchantPricingPlanFeature[]
```

Do NOT add a `billingPlanId`, `merchantPricingPlanId` on BillingPlan, or any other physical MerchantPricingPlan/BillingPlan relation.

### 5. Add MerchantPricingPlanFeature

```prisma
model MerchantPricingPlanFeature {
  merchantPricingPlanId String
  merchantPricingPlan   MerchantPricingPlan @relation(fields: [merchantPricingPlanId], references: [id], onDelete: Cascade)

  featureId String
  feature   Feature @relation(fields: [featureId], references: [id], onDelete: Restrict)

  createdAt DateTime @default(now())

  @@id([merchantPricingPlanId, featureId])
  @@index([featureId])
  @@schema("billing")
}
```

Presence of the row means the commercial plan supports the feature.

### 6. Replace BillingPlanFeature.feature enum with Feature FK

Keep the current `id`, `planId`, `plan`, and `enabled` fields to minimise unrelated churn. Replace only the enum column with a relation:

```prisma
model BillingPlanFeature {
  id String @id @default(cuid())

  planId String
  plan   BillingPlan @relation(fields: [planId], references: [id], onDelete: Cascade)

  featureId String
  feature   Feature @relation(fields: [featureId], references: [id], onDelete: Restrict)

  enabled Boolean @default(true)

  @@unique([planId, featureId])
  @@index([featureId])
  @@schema("billing")
}
```

Do not keep the old enum column after migration.

### 7. Add shop opt-in state

Add relation to `Shop`:

```prisma
featurePreferences ShopFeaturePreference[]
```

Add:

```prisma
model ShopFeaturePreference {
  id String @id @default(cuid())

  shopId String
  shop   Shop @relation(fields: [shopId], references: [id], onDelete: Cascade)

  featureId String
  feature   Feature @relation(fields: [featureId], references: [id], onDelete: Restrict)

  enabled Boolean @default(false)

  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@unique([shopId, featureId])
  @@index([featureId, enabled])
  @@schema("billing")
}
```

This table is merchant preference. It is deliberately not related to Subscription or BillingPeriod.

### 8. Move outbound limits to PlatformBillingPolicy

Add these fields to `PlatformBillingPolicy`:

```prisma
defaultOutboundSoftLimit     Int @default(1000)
defaultOutboundHardLimit     Int @default(2000)
terminalMessageReservedSlots Int @default(1)
```

Add this optional field to `ShopBillingPolicyOverride`:

```prisma
terminalMessageReservedSlots Int?
```

Remove these fields from `BillingPlan`:

```prisma
defaultOutboundSoftLimit
defaultOutboundHardLimit
terminalMessageReservedSlots
```

Do not replace them with similarly named BillingPlan columns.

### 9. BillingPlan remains physically independent

Do not add any MerchantPricingPlan relation to BillingPlan.

The relevant BillingPlan fields after this task remain logically:

```prisma
shopifyPlanHandle String @unique
name              String
kind              BillingPlanKind
active            Boolean @default(true)

shopifyUsageEventHandle               String?
includedRecoveryConversationAllowance Int?
recoveryCreditPackEnabled             Boolean @default(false)
recoveryCreditsPerPack                Int?
shopifyRecoveryCreditPackEventHandle  String?

features BillingPlanFeature[]
```

ARCH-017 intentionally leaves the legacy credit-pack columns present so this database task does not broaden into the separate purchased-credit refactor. New materialisation will populate them as disabled/null.

## Required migration sequence

Implement the SQL in an order that never needs to cast arbitrary strings back into the removed enum.

### A. Create FeatureActivationMode and Feature

Create the enum/table first.

Seed these four rows in the migration itself so deployment does not depend on running `prisma/seed.mjs`:

| key | displayName | activationMode | systemRequired | active |
|---|---|---|---|---|
| `checkout_recovery` | Checkout Recovery | ALWAYS_ENABLED | true | true |
| `ai_conversations` | AI Conversations | MERCHANT_OPT_IN | false | true |
| `product_search` | Product Search | MERCHANT_OPT_IN | false | true |
| `order_support` | Order Support | MERCHANT_OPT_IN | false | true |

Use `INSERT ... ON CONFLICT ("key") DO NOTHING` or the equivalent deterministic PostgreSQL statement.

### B. Migrate BillingPlanFeature without losing enabled state

Do not drop the old `feature` enum column first.

Required sequence:

1. add nullable `featureId`;
2. map every existing enum value to the seeded Feature key:

```text
CHECKOUT_RECOVERY -> checkout_recovery
AI_CONVERSATIONS  -> ai_conversations
PRODUCT_SEARCH    -> product_search
ORDER_SUPPORT     -> order_support
```

3. assert there is no BillingPlanFeature row with null `featureId`;
4. make `featureId` NOT NULL;
5. add Feature FK `ON DELETE RESTRICT`;
6. drop old `(planId, feature)` unique index;
7. create unique `(planId, featureId)` and `featureId` index;
8. drop old `feature` column;
9. drop PostgreSQL type `billing.BillingPlanFeatureIdentifier`.

Preserve `BillingPlanFeature.enabled` exactly.

### C. Create MerchantPricingPlanFeature and ShopFeaturePreference

Create both tables with the constraints shown above.

### D. Add MerchantPricingPlan runtime-source/durability fields WITHOUT business-state backfill

Add nullable:

```text
shopifyRecoveryUsageEventHandle
materializedAt
```

ARCH-017 is being implemented before production and there are no existing customers whose lifecycle state must be preserved.

Therefore the migration MUST NOT infer either field from an existing same-handle `BillingPlan`.

Required migration behavior:

```text
existing MerchantPricingPlan.materializedAt
    -> remains NULL

existing MerchantPricingPlan.shopifyRecoveryUsageEventHandle
    -> remains NULL unless it already had an explicit value before this migration
```

Do NOT execute SQL that copies:

```text
BillingPlan.createdAt -> MerchantPricingPlan.materializedAt
BillingPlan.shopifyUsageEventHandle -> MerchantPricingPlan.shopifyRecoveryUsageEventHandle
```

`materializedAt` acquires meaning only through the ARCH-017 runtime lifecycle after deployment. The Shopify task owns setting it when a MerchantPricingPlan is actually materialised/associated during subscription resolution.

Do not attempt to derive `shopifyRecoveryUsageEventHandle` from `MerchantPricingUsageEvent`; those rows are top-up offers. Existing development paid MerchantPricingPlans may require explicit Admin correction before they are materialisable.

### E. Establish the mandatory checkout-recovery catalogue invariant only

Every MerchantPricingPlan must support the system-required `checkout_recovery` feature.

The migration MAY insert exactly this mandatory mapping for existing development MerchantPricingPlan rows:

```sql
INSERT INTO billing."MerchantPricingPlanFeature" (...)
SELECT ..., checkout_feature_id, NOW()
FROM billing."MerchantPricingPlan" ...
ON CONFLICT DO NOTHING;
```

This is not a historical inference from BillingPlan state; it establishes the new global invariant that every merchant plan supports checkout recovery.

The migration MUST NOT copy optional feature support from existing `BillingPlanFeature` rows into `MerchantPricingPlanFeature`.

Optional MerchantPricingPlan features must be configured explicitly through the ARCH-017 Admin feature selector.

### F. Do not infer merchant opt-in state

Create `ShopFeaturePreference` with the required schema and constraints, but insert NO preference rows in the migration.

There are no existing customers whose optional-feature choices need preserving.

Specifically, the migration MUST NOT derive `ShopFeaturePreference` from:

```text
Subscription.planId
BillingPlanFeature
existing shop/subscription state
```

After ARCH-017, merchant opt-in state is created only by the merchant-facing feature-preference workflow.

### G. Move billing safety defaults

Add the three PlatformBillingPolicy columns before dropping BillingPlan columns.

This initiative is PRE-PRODUCTION/BREAKING. Use these canonical new default values:

```text
defaultOutboundSoftLimit = 1000
defaultOutboundHardLimit = 2000
terminalMessageReservedSlots = 1
```

For existing `PlatformBillingPolicy(id='default')`, set any newly-added null columns to those values. If no row exists, `prisma/seed.mjs` must create it with these values.

Add migration CHECK constraints on `PlatformBillingPolicy` with stable explicit constraint names:

```text
defaultOutboundSoftLimit >= 1
defaultOutboundHardLimit >= 2
defaultOutboundSoftLimit <= defaultOutboundHardLimit
defaultOutboundHardLimit <= absoluteOutboundHardLimit
terminalMessageReservedSlots >= 1
terminalMessageReservedSlots < defaultOutboundHardLimit
```

Add CHECK for `ShopBillingPolicyOverride.terminalMessageReservedSlots`:

```text
terminalMessageReservedSlots IS NULL OR terminalMessageReservedSlots >= 1
```

Do not attempt a cross-column effective-limit check in SQL when hard limit may be inherited from PlatformBillingPolicy; Background/Admin runtime validation owns that effective check.

After PlatformBillingPolicy is populated, drop the three BillingPlan limit columns.

### H. MerchantPricingPlan meter constraints

Do not make `shopifyRecoveryUsageEventHandle` globally NOT NULL because FREE legitimately has null and existing development catalogue rows may need Admin correction.

Add a database CHECK enforcing only the direction that is safe independent of old data:

```text
planKind = FREE -> shopifyRecoveryUsageEventHandle IS NULL
```

Admin and Shopify tasks enforce:

```text
PAID_METERED + active/materialisable -> nonblank shopifyRecoveryUsageEventHandle
```

Do not guess a paid meter from top-up usage events in the migration.

## Seed update

Update `prisma/seed.mjs` so it compiles and remains repeatable with the new schema.

Required changes:

1. upsert the four initial Feature rows before creating BillingPlans;
2. remove `defaultOutboundSoftLimit`, `defaultOutboundHardLimit`, `terminalMessageReservedSlots` from BillingPlan seed objects;
3. create BillingPlanFeature rows using `feature: { connect: { key: ... } }` or `featureId` obtained from seeded Features, not enum names;
4. map previous enabled seed entries as:

```text
CHECKOUT_RECOVERY -> checkout_recovery
PRODUCT_SEARCH    -> product_search
AI_CONVERSATIONS  -> ai_conversations
ORDER_SUPPORT     -> order_support
```

5. keep `enabled` values from the current seed;
6. seed PlatformBillingPolicy with:

```text
defaultOutboundSoftLimit = 1000
defaultOutboundHardLimit = 2000
terminalMessageReservedSlots = 1
absoluteOutboundHardLimit = 2000
```

7. do not make `prisma/seed.mjs` the only source of mandatory Feature rows; the migration itself must seed them.

## Required validator

Create:

```text
scripts/validate-arch017-billing-materialisation-schema.mjs
```

Add package script:

```json
"test:arch017-billing-materialisation": "node scripts/validate-arch017-billing-materialisation-schema.mjs"
```

The validator MUST fail non-zero unless all of these are true:

- `BillingPlanFeatureIdentifier` no longer exists in Prisma schema;
- `FeatureActivationMode` exists with exactly `ALWAYS_ENABLED`, `MERCHANT_OPT_IN`;
- `Feature` has unique `key`, active, activationMode and systemRequired;
- MerchantPricingPlan still has `shopifyPlanHandle @unique`;
- MerchantPricingPlan has `materializedAt`, `shopifyRecoveryUsageEventHandle`, and `features`;
- MerchantPricingPlanFeature unique identity is `(merchantPricingPlanId, featureId)`;
- BillingPlanFeature references Feature and is unique `(planId, featureId)`;
- ShopFeaturePreference is unique `(shopId, featureId)`;
- BillingPlan does not contain the three outbound/terminal limit fields;
- PlatformBillingPolicy contains all three moved fields;
- ShopBillingPolicyOverride contains optional `terminalMessageReservedSlots`;
- migration contains initial four Feature keys and the enum-to-key backfill;
- migration drops old PostgreSQL `BillingPlanFeatureIdentifier` type;
- migration contains no same-handle BillingPlan -> MerchantPricingPlan `materializedAt` backfill;
- migration contains no BillingPlan -> MerchantPricingPlan `shopifyRecoveryUsageEventHandle` copy;
- migration establishes checkout_recovery as the mandatory MerchantPricingPlan feature for existing development plans;
- migration contains no optional BillingPlanFeature -> MerchantPricingPlanFeature inference;
- migration contains no ShopFeaturePreference inserts;
- migration does not map MerchantPricingUsageEvent to `shopifyRecoveryUsageEventHandle`.

## Required validation

Inspect `package.json` and run exactly the declared equivalents:

```text
npm run format
npm run validate
npm run prisma:generate
npm run test:arch017-billing-materialisation
npm run erd
npm run validate
npm run prisma:generate
git diff --check
```

If PlantUML is unavailable and only PNG generation fails, still run `npm run erd:puml`, record the environment limitation, and do not treat missing PlantUML binary as schema failure.

Also validate the migration on a disposable PostgreSQL database or the repository's existing migration-test mechanism. The migration must apply from the current latest migration, not only to an empty hand-written schema.

## Required tests / evidence

Completion Report MUST explicitly record:

- old enum rows were mapped without loss of `enabled` state;
- `checkout_recovery` exists and is `systemRequired=true`, `ALWAYS_ENABLED`, `active=true`;
- all pre-existing MerchantPricingPlan rows remain `materializedAt=null` after migration;
- no recovery usage-event handle is inferred from BillingPlan or MerchantPricingUsageEvent;
- every existing MerchantPricingPlan gets only the mandatory checkout_recovery feature mapping automatically;
- no optional MerchantPricingPlanFeature rows are inferred from existing BillingPlanFeature rows;
- no ShopFeaturePreference rows are created by the migration;
- duplicate MerchantPricingPlan Shopify handles remain impossible;
- BillingPlan no longer carries the moved policy fields.

## Stop conditions

STOP and return to moda_architect if implementation would require any of the following:

- adding a MerchantPricingPlan <-> BillingPlan foreign key;
- reintroducing feature names as a Prisma enum;
- treating MerchantPricingUsageEvent as the normal recovery meter;
- adding ARCH-011 plan segments/proration;
- adding application/admin/background behavior in this repository.

## Acceptance criteria

- schema matches the target model above;
- migration is deterministic and mechanically preserves existing BillingPlanFeature `enabled` state while converting the enum to Feature FK;
- migration does not infer ARCH-017 durability, optional plan capability, recovery-meter identity, or merchant opt-in state from development data;
- dynamic Feature catalogue is deploy-time seeded but not enum-closed;
- checkout recovery is guaranteed as the system-required plan feature;
- safety defaults are owned by PlatformBillingPolicy, not BillingPlan;
- downstream tasks can compile against the generated Prisma client without needing another database task.

## Completion protocol

Set task to `review` only after all required validation is complete. Include exact commands/results, migration name, implementation commit, parent report commit, physical worktree evidence and dependency evidence in the Completion Report.
