---
id: ARCH-015-DATABASE-002
architecture_id: ARCH-015
title: Add typed automatic refund correction evidence and UsageEvent linkage
task_kind: implementation
domain: database
repository: moda-interact-database
assigned_agent: moda_database
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 65
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-015-DATABASE-001
enables:
- ARCH-015-BACKGROUND-003
created: 2026-09-16
updated: 2026-09-16
---

# ARCH-015-DATABASE-002

## Objective

Add the minimum typed persistence required for ARCH-015 automatic recovery-credit refund corrections.

The automatic correction workflow must not place authoritative provider baseline/expected settlement evidence in generic JSON metadata. `UsageEvent` owns provider event submission; `RecoveryCreditRefund` owns refund settlement/provenance.

This task adds **no new model, enum, queue, catalogue or entitlement type**.

## Existing evidence that MUST be reused

Do not duplicate these existing `RecoveryCreditRefund` fields:

```text
billingPeriodIdSnapshot
providerSubscriptionIdSnapshot
planHandleSnapshot
eventHandleSnapshot
purchaseProviderAmountSnapshot
purchaseProviderCurrencySnapshot
finalCreditQuantity
expectedProviderAmount
expectedProviderCurrency
```

Their ARCH-015 meaning remains:

```text
providerSubscriptionIdSnapshot = canonical provider-context identity
planHandleSnapshot             = original/current-at-request Shopify plan provenance
billingPeriodIdSnapshot        = refund purchase billing-period provenance
eventHandleSnapshot            = exact Shopify usage-meter handle
finalCreditQuantity            = frozen Moda credits being refunded
expectedProviderAmount         = frozen monetary refund expected
expectedProviderCurrency       = one currency for baseline cost, expected cost-after and refund amount
```

Do not create JSON copies or renamed duplicate columns for the same facts.

## Exact schema changes

### RecoveryCreditRefund

Add exactly these nullable fields:

```prisma
automaticCorrectionUsageEventId                String?  @unique
providerUsageQuantityBeforeCorrection           Decimal?
providerUsageCostBeforeCorrection               Decimal?
expectedProviderUsageQuantityAfterCorrection    Decimal?
expectedProviderUsageCostAfterCorrection        Decimal?
```

Add an explicit one-to-one relation from `RecoveryCreditRefund.automaticCorrectionUsageEventId` to `UsageEvent.id` using a named relation. Use `onDelete: Restrict` so financial correction evidence cannot be detached by deleting the linked provider event.

Equivalent relation shape:

```prisma
automaticCorrectionUsageEvent UsageEvent? @relation(
  "RecoveryCreditRefundAutomaticCorrection",
  fields: [automaticCorrectionUsageEventId],
  references: [id],
  onDelete: Restrict
)
```

Format it according to repository Prisma conventions; semantics are binding.

### UsageEvent

Add only the inverse optional relation required by Prisma, equivalent to:

```prisma
automaticRecoveryCreditRefund RecoveryCreditRefund?
  @relation("RecoveryCreditRefundAutomaticCorrection")
```

Do **not** add `metadata`, `Json`, refund amount, provider context, plan, period, event-handle, baseline or expected-after duplicate fields to `UsageEvent`.

`UsageEvent.quantity` already represents the exact negative/fractional correction value and remains `Decimal`.

## Database integrity

Create migration:

```text
20260916083000_arch015_refund_correction_evidence
```

If that exact timestamp is already occupied in the implementation checkout, choose the next lexically ordered timestamp on 2026-09-16 and record the reason in the Completion Report. Do not edit historical migrations.

Add a database CHECK constraint on `billing.RecoveryCreditRefund` enforcing the automatic-correction evidence group is all-null or all-present.

Binding group:

```text
automaticCorrectionUsageEventId
providerUsageQuantityBeforeCorrection
providerUsageCostBeforeCorrection
expectedProviderUsageQuantityAfterCorrection
expectedProviderUsageCostAfterCorrection
finalCreditQuantity
expectedProviderAmount
expectedProviderCurrency
```

Required truth table:

```text
no automatic correction prepared
  -> automaticCorrectionUsageEventId IS NULL
  -> all four new Decimal evidence fields IS NULL
  -> existing finalCreditQuantity/expectedProviderAmount/expectedProviderCurrency may
     still be populated by the manual PROVIDER_ACTION_REQUIRED path

an automatic correction is prepared
  -> automaticCorrectionUsageEventId IS NOT NULL
  -> all four new Decimal evidence fields IS NOT NULL
  -> finalCreditQuantity IS NOT NULL
  -> expectedProviderAmount IS NOT NULL
  -> expectedProviderCurrency IS NOT NULL
```

Do not require the existing final/expected refund fields to be null merely because no automatic correction exists; the manual fallback legitimately uses them.

Add numeric integrity for an automatic correction:

```text
providerUsageQuantityBeforeCorrection >= 0
providerUsageCostBeforeCorrection >= 0
expectedProviderUsageQuantityAfterCorrection >= 0
expectedProviderUsageCostAfterCorrection >= 0
finalCreditQuantity > 0
expectedProviderAmount >= 0
```

Do not encode pricing arithmetic such as `expected after = before + correction quantity` as a cross-table CHECK; the correction quantity lives on `UsageEvent` and provider pricing proof belongs in Background service validation/tests.

The unique FK ensures one correction UsageEvent cannot be linked to two refunds.

## Naming contract

Do not add `Snapshot` to the four new correction fields.

ARCH-015 naming distinguishes:

```text
...Snapshot
  existing immutable provenance captured for the original purchase/refund context

...BeforeCorrection
  provider state actually observed before preparing the automatic correction

expected...AfterCorrection
  provider state that must later be observed before automatic completion
```

## Decimal semantics

Use Prisma `Decimal` / PostgreSQL numeric representation consistent with existing billing Decimal fields.

Do not use scaled integers and do not convert Moda entitlement counters to Decimal.

Examples that must remain exact:

```text
4      -> 4
3.75   -> 3.75
20.00  -> 20
17.50  -> 17.5
```

The four evidence fields store provider quantities/costs only; `finalCreditQuantity` remains an integer Moda recovery-credit quantity.

## Migration safety

All new fields are nullable, so existing refunds require no fabricated backfill.

The migration must:

1. add the five columns;
2. add the unique FK/index required for `automaticCorrectionUsageEventId`;
3. add the named relation FK with `ON DELETE RESTRICT`;
4. add the grouped evidence/numeric CHECK constraint(s);
5. leave every existing row semantically unchanged.

Do not populate an automatic correction link for historical refunds.

## Authorized implementation surface

```text
prisma/schema.prisma
prisma/migrations/20260916083000_arch015_refund_correction_evidence/migration.sql
scripts/validate-arch015-refund-correction-evidence.mjs      # new
scripts/generate-erd.mjs                                    # invoke; modify only if generator genuinely requires
/docs/generated/prisma-erd.puml                              # generated output
/docs/generated/prisma-erd.png                               # generated output when repository generator produces it
package.json                                                 # only if adding validator script follows current convention
```

Do not alter ARCH-014 `MerchantPricing*`, purchase entitlement quantities, refund status enums, `UsageEvent.quantity`, or any historical migration.

## Required validation/tests

The current-schema validator must prove at minimum:

1. all five new `RecoveryCreditRefund` fields exist with exact types/nullability;
2. the automatic correction FK is unique;
3. relation points to `UsageEvent.id` with `ON DELETE RESTRICT`;
4. inverse Prisma relation exists;
5. no `UsageEvent.metadata` field was added;
6. existing provenance/refund amount fields remain present and unchanged;
7. all-null automatic evidence is valid;
8. complete automatic evidence is valid;
9. linked correction with one missing Decimal evidence field fails;
10. negative quantity/cost evidence fails;
11. existing manual fallback row with no automatic correction link but populated final/expected fields remains valid;
12. entitlement credit quantities remain `Int`;
13. `UsageEvent.quantity` remains `Decimal`;
14. existing database contents migrate without backfill fabrication.

Run repository-equivalent validation:

```text
npm run prisma:validate
npm run prisma:generate
npx prisma migrate deploy
node scripts/validate-arch015-fractional-provider-usage-snapshots.mjs
node scripts/validate-arch015-refund-correction-evidence.mjs
npm run erd        # or exact current ERD command from package.json
git diff --check
```

Inspect `package.json` first and use exact available script names rather than inventing aliases.

## Completion Report

### Physical Worktree Isolation

- Canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent report worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-015-DATABASE-002` on `task/ARCH-015-DATABASE-002`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-015-DATABASE-002` on `task/ARCH-015-DATABASE-002`.
- Launcher preparation and claim were already complete for attempt 1; preparation, worktree creation, routing and re-claim were not rerun.
- Dependency `ARCH-015-DATABASE-001` was complete before execution.

### Implementation

- Added the five nullable `RecoveryCreditRefund` fields with exact Prisma types, including the unique `automaticCorrectionUsageEventId`.
- Added the named one-to-one `RecoveryCreditRefundAutomaticCorrection` relation with `ON DELETE RESTRICT` and the required `UsageEvent` inverse relation.
- Preserved `UsageEvent.quantity` as `Decimal`, Moda recovery-credit quantities as `Int`, existing refund provenance/final fields, and all existing models/enums/statuses/catalogue types.
- Added migration `20260916083000_arch015_refund_correction_evidence` with five nullable columns, unique FK/index, named restrict FK, all-null/all-present evidence-group CHECK, and conditional nonnegative/positive integrity CHECK.
- The evidence group permits existing manual `PROVIDER_ACTION_REQUIRED` rows to retain final/expected refund fields without an automatic correction link.
- Added `scripts/validate-arch015-refund-correction-evidence.mjs` and the matching package script. It covers schema types/nullability, uniqueness, relation actions, inverse relation, preserved fields, forbidden `UsageEvent` duplicates/metadata, truth-table cases, numeric failures, integer/Decimal preservation, and no fabricated backfill DML.
- Regenerated `docs/generated/prisma-erd.puml` and `docs/generated/erd.png`.
- No historical migration, application repository, queue, enum, entitlement type, or `scripts/generate-erd.mjs` was changed.

### Validation Evidence

- `npm run prisma:validate`: passed.
- `npm run prisma:generate`: passed with Prisma 6.19.3.
- `node scripts/validate-arch015-fractional-provider-usage-snapshots.mjs`: passed.
- `npm run test:arch015-refund-correction-evidence`: passed.
- `npm run erd`: passed; PlantUML and PNG artifacts regenerated.
- `git diff --check`: passed.
- `DATABASE_URL=postgresql://postgres:postgres@localhost:5432/moda_interact npm run migrate:deploy`: blocked by the known pre-existing P3009 failure for `20260915140000_arch015_fractional_provider_usage_snapshots`, which started at `2026-09-15 13:16:50.597229 UTC`; no unrelated migration was repaired or marked resolved.
- The migration contains no standalone `UPDATE` or `INSERT`, and all added columns are nullable, so no historical evidence or automatic correction link is fabricated.

### Publication

- Implementation commit: `e54cd3fe5a21bab31037826c56fd3f62717d9cfd`.
- Implementation branch pushed: `origin/task/ARCH-015-DATABASE-002`.
- Implementation worktree is clean after commit. Its inherited upstream still names `origin/main`, so publication used the explicit matching task ref; no main branch was changed.
- Parent report branch is ready for its report commit and push.

### Completion Report Status

- Ready for architect review.
- Claim cleared; task lifecycle is `review`.
- No Architect Review section was added or modified.

## Stop conditions

STOP and return evidence to `moda_architect` if:

- another schema change is required to implement the typed evidence contract;
- an additional refund status/enum is required;
- the relation cannot be expressed without altering `UsageEvent` submission semantics;
- current rows violate a constraint unless business values are fabricated/backfilled;
- implementation would require adding generic `UsageEvent.metadata` JSON;
- implementation would require changing Moda recovery-credit quantities from integer to Decimal.

## Completion protocol

Update Completion Report, set `status: review`, clear claim, return to `moda_architect`, STOP.
