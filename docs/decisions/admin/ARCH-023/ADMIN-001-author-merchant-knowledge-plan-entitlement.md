---
id: ARCH-023-ADMIN-001
architecture_id: ARCH-023
title: Author Merchant Knowledge plan entitlement
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: complete
priority: 40
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-023-DATABASE-001
  - ARCH-023-SHARED-002
enables: []
created: 2026-09-29
updated: 2026-09-30
---

# Author Merchant Knowledge plan entitlement

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Extend the existing Merchant Pricing Plan authoring transaction so every plan created or updated through the supported Admin workflow contains the ordinary `merchant_knowledge` Feature and one validated `MerchantPricingPlanFeature.configuration`.

The same feature mapping/configuration must be copied unchanged into an already-materialised matching `BillingPlanFeature` by the existing plan-save materialisation path.

This task owns the Admin product-management surface for:

```text
maxKnowledgeSources
maxContentUnitsPerSource
allowedSourceTypes
```

It must not create a second billing-plan materialisation mechanism.

## Context

The current Admin pricing builder already:

- authors `MerchantPricingPlan`;
- selects generic Features;
- rewrites `MerchantPricingPlanFeature` mappings;
- mirrors feature membership into an already-materialised `BillingPlan`;
- uses platform-admin authorization and billing audit events.

ARCH-023 adds generic JsonB configuration to both plan-feature mapping tables. The Merchant Knowledge configuration is validated by Shared C2 and by the active database Purpose/Data Format catalogue.

`merchant_knowledge` remains an ordinary Feature:

```text
key            = merchant_knowledge
displayName    = Merchant Knowledge
activationMode = ALWAYS_ENABLED
systemRequired = false
active         = true
```

It is included by application/domain plan policy, not by a database required-feature constraint.

## Scope

Primary authorized implementation surface:

```text
database                         # gitlink update only
package.json
package-lock.json

src/lib/admin/merchant-knowledge-plan-policy.ts
src/lib/admin/merchant/pricing-builder-payload.ts
src/lib/admin/merchant/pricing-plan.ts

src/app/actions/merchant-pricing-plan.ts
src/app/actions/feature-catalogue.ts

src/components/admin/merchant/merchant-pricing-plan-builder.tsx

tests/unit/merchant-knowledge-plan-policy.test.ts
tests/unit/merchant-pricing-builder-payload.test.ts
tests/unit/merchant-pricing-plan-merchant-knowledge.test.ts
```

Existing pricing-plan tests may be extended rather than duplicated.

## Out of Scope

- Merchant Knowledge source CRUD/upload.
- Billing subscription projection logic outside the existing Admin plan-save mirror.
- Purpose/Data Format catalogue CRUD.
- hard-coded Free/Starter/Growth configuration.
- Store Categories/templates.
- Platform/Shop Instructions.
- Background processing.
- Commerce lookup/bootstrap.
- database schema/migration edits.
- retroactively inventing plan configuration values for existing plans.

## Requirements

### R1 — adopt accepted database and Shared revisions

Before implementation:

1. advance the Admin `database` submodule gitlink to the accepted/merged `ARCH-023-DATABASE-001` commit;
2. do not edit schema/migrations inside the Admin repository's database submodule;
3. use exactly `@modainteract/moda-interact-shared@1.0.1`, the Architect-Accepted revision published by `ARCH-023-SHARED-002`;
4. pin Admin to `1.0.1` exactly; do not substitute a range, `latest`, workspace link or later release without architect reconciliation;
5. regenerate Prisma Client through the existing repository script.

If either accepted dependency is unavailable, STOP.

### R2 — define the fixed Admin product-policy descriptor

Create `src/lib/admin/merchant-knowledge-plan-policy.ts`.

Export exactly:

```ts
export const MERCHANT_KNOWLEDGE_FEATURE_KEY = "merchant_knowledge" as const;

export const MERCHANT_KNOWLEDGE_FEATURE_DESCRIPTOR = {
  key: "merchant_knowledge",
  displayName: "Merchant Knowledge",
  description:
    "Allow the CommerceAgent to use merchant-managed knowledge sources.",
  activationMode: "ALWAYS_ENABLED",
  systemRequired: false,
  active: true,
} as const;
```

Do not make `systemRequired = true`.

### R3 — ensure the ordinary Feature inside the existing plan mutation transaction

Create an internal helper:

```ts
ensureMerchantKnowledgeFeature(
  transaction: Prisma.TransactionClient,
  platformAdminId: string,
): Promise<Feature>
```

Behavior:

1. find Feature by key `merchant_knowledge`;
2. if absent, create exactly R2 and write one existing `BillingAuditAction.PLAN_CATALOG_CHANGED` audit event:
   ```text
   relatedEntityType = Feature
   relatedEntityId   = feature.id
   reason            = Created Feature merchant_knowledge
   ```
3. if present, require:
   ```text
   activationMode == ALWAYS_ENABLED
   systemRequired == false
   active == true
   ```
4. if any required identity/state differs, fail with a bounded configuration-conflict error;
5. do not silently rewrite the conflicting row.

Display name/description differences are not identity conflicts; keep the persisted wording.

The helper is called from the existing Merchant Pricing Plan create/update transaction before desired feature mappings are calculated.

Do not introduce a startup hook or side effect on a GET/read path.

### R4 — prevent ordinary Feature UI from deactivating this fixed product feature

In the existing generic Feature catalogue mutation:

```text
intent = toggle
Feature.key = merchant_knowledge
current active = true
```

must reject:

```text
Merchant Knowledge is included by pricing-plan product policy and cannot be deactivated here.
```

Do not set `systemRequired=true`.

Generic Feature create/update behavior for other keys remains unchanged.

### R5 — extend the plan builder payload with one explicit Merchant Knowledge configuration field

Do not replace the existing generic `supportedFeatureKeys` mechanism.

Add to the pricing builder payload exactly:

```ts
merchantKnowledgeConfiguration: {
  schemaVersion: 1;
  maxKnowledgeSources: number;
  maxContentUnitsPerSource: number;
  allowedSourceTypes: Array<{
    purposeKey: MerchantKnowledgePurposeKey;
    dataFormatKey: MerchantKnowledgeDataFormatKey;
  }>;
};
```

The field is required on every create/update submitted through the current Admin builder after this task.

Do not serialize the configuration as an opaque JSON string from the browser.

The existing builder-payload parser must validate primitive shape before the server action performs authoritative Shared/database validation.

### R6 — load the selectable source-type catalogue from PostgreSQL

For the pricing-plan builder read model, load only active rows where:

```text
MerchantKnowledgePurpose.active = true
MerchantKnowledgeDataFormat.active = true
MerchantKnowledgePurposeDataFormat row exists
```

Return deterministic presentation rows ordered:

```text
purpose.displayOrder ASC
purpose.key ASC
dataFormat.displayOrder ASC
dataFormat.key ASC
```

Expose:

```ts
{
  purposeKey,
  purposeDisplayName,
  dataFormatKey,
  dataFormatDisplayName
}
```

Do not hard-code the supported pair matrix in React or Shared.

### R7 — exact plan-builder UI behavior

Inside the existing Merchant Pricing Plan builder's "Supported features" step:

1. `merchant_knowledge` is always rendered checked;
2. its checkbox is disabled/locked;
3. label suffix:
   ```text
   (Included by product policy)
   ```
4. render an indented `Merchant Knowledge configuration` panel directly below it;
5. render numeric inputs:
   ```text
   Maximum knowledge sources
   Maximum content units per source
   ```
6. render source-type checkboxes grouped by Purpose using the R6 active catalogue;
7. checked source types exactly represent `allowedSourceTypes`;
8. do not branch on:
   ```text
   planKind
   displayName
   shopifyPlanHandle
   FREE / PAID_METERED
   ```
9. do not preselect plan-specific values.

For an existing plan:

- if it has a valid Merchant Knowledge configuration, populate it;
- if mapping/configuration is absent/invalid, show an explicit configuration-required state and block Save until the admin supplies valid values;
- never invent defaults.

### R8 — validate C2 and active pair compatibility server-side

Inside the plan create/update transaction:

1. parse submitted config with published `MerchantKnowledgeFeatureConfigurationSchema`;
2. query the active Purpose/Data Format compatibility rows inside the same transaction;
3. require every selected `(purposeKey,dataFormatKey)` exists in that active catalogue;
4. reject any stale/inactive/unsupported pair;
5. do not require `allowedSourceTypes` to be non-empty beyond Shared C2;
6. do not infer source types from plan kind/name/handle.

Client validation is convenience only; server validation is authoritative.

### R9 — calculate desired feature mappings without destroying unrelated configuration

Replace the current "feature ids only" desired set with deterministic mapping objects:

```ts
type DesiredPlanFeature = {
  featureId: string;
  configuration: Prisma.InputJsonValue;
};
```

Rules:

1. `merchant_knowledge` is always present exactly once with the validated C2 object;
2. existing inactive mappings retained by current behavior retain their existing `configuration`;
3. other requested existing feature mappings retain their existing `configuration`;
4. newly-added non-Merchant-Knowledge features use `{}`;
5. current `systemRequired` behavior remains unchanged;
6. duplicate feature keys/ids reject.

Do not reset another Feature's configuration merely because the pricing plan was edited.

### R10 — persist MerchantPricingPlanFeature configuration exactly

For create/update, persist each desired mapping as:

```text
featureId
configuration
```

If the current implementation uses nested `deleteMany/create`, it may continue doing so only when R9 has already preserved the correct configuration for every desired mapping.

The committed `merchant_knowledge` JSON must be exactly the parsed C2 object; no extra Admin-only keys.

### R11 — existing BillingPlan mirror remains generic and copies configuration unchanged

When the pricing plan is already materialised and the existing action updates the matching `BillingPlan`, modify that existing feature-mirror block so it operates on R9 mapping objects.

For every desired mapping:

```text
BillingPlanFeature.featureId     = mapping.featureId
BillingPlanFeature.enabled       = true
BillingPlanFeature.configuration = mapping.configuration
```

For removed mappings, keep the current delete behavior.

There must be no special `if feature.key === "merchant_knowledge"` branch inside the BillingPlan materialisation/mirror block.

The same mapping object produced for `MerchantPricingPlanFeature` is copied to `BillingPlanFeature`.

### R12 — no preference mutation

This task must not create/update/delete:

```text
ShopFeaturePreference
```

A pricing-plan Feature change never reconstructs merchant preference rows.

### R13 — active existing-plan rollout is explicit, not guessed

This task must add an Admin read/report helper that identifies existing Merchant Pricing Plans where:

```text
merchant_knowledge mapping missing
OR configuration fails C2
OR configured pair is not active in current catalogue
```

Show a warning in the Merchant Pricing Plan catalogue:

```text
Merchant Knowledge configuration required
```

Do not automatically invent configuration/backfill values.

A plan is repaired by opening and saving it through the supported builder with explicit values.

### R14 — audit

The existing plan save audit remains authoritative:

```text
BillingAuditAction.PLAN_CATALOG_CHANGED
relatedEntityType = MerchantPricingPlan
```

Its `afterValue`/reason behavior should continue according to existing conventions.

Feature auto-provision, if it occurs, receives the R3 Feature audit in the same overall transaction.

Do not add a new database enum solely for ARCH-023.

### R15 — required regressions

Tests must prove:

```text
new plan always receives merchant_knowledge mapping
admin cannot uncheck merchant_knowledge
generic Feature toggle cannot deactivate merchant_knowledge
no Free/Starter/Growth branch exists
C2-invalid config rejects
database-inactive/unsupported pair rejects
duplicate pair rejects through Shared C2
existing non-MK feature configuration survives plan edit
existing inactive feature mapping/config survives current retention behavior
MerchantPricingPlanFeature gets exact C2 JSON
materialised BillingPlanFeature gets byte/semantic-equivalent JSON
no ShopFeaturePreference write occurs
existing invalid/missing plan is reported, not silently defaulted
```

## Work Items

- [x] Adopt accepted database gitlink and Shared package.
- [x] Add Merchant Knowledge product-policy helper.
- [x] Protect fixed feature from generic deactivation.
- [x] Extend pricing builder payload/read model.
- [x] Load active Purpose/Data Format catalogue.
- [x] Add explicit configuration UI.
- [x] Add authoritative C2/catalogue validation.
- [x] Preserve generic mapping configuration across plan edits.
- [x] Copy generic feature configuration into existing BillingPlan mirror.
- [x] Add rollout warning/report for existing plans needing explicit config.
- [x] Add focused tests.

## Interfaces / Contracts

Consumes:

```text
ARCH-023-DATABASE-001
@modainteract/moda-interact-shared/merchant-knowledge
```

Writes:

```text
Feature
MerchantPricingPlanFeature.configuration
BillingPlanFeature.configuration
```

Does not write Merchant Knowledge source tables.

## Dependencies

- `ARCH-023-DATABASE-001`
- `ARCH-023-SHARED-002`

## Enables

Planned downstream Shopify billing/materialisation and Merchant Knowledge configuration tasks may depend on this task after those task definitions are created.

## Acceptance Criteria

- [x] `merchant_knowledge` remains ordinary (`systemRequired=false`) but is product-policy locked into supported plan authoring.
- [x] Every newly-created/updated Merchant Pricing Plan receives one valid Merchant Knowledge mapping.
- [x] Source-type selection is data-driven from active database catalogue rows.
- [x] No plan-name/plan-kind source-type rules exist.
- [x] Existing unrelated Feature configuration is preserved.
- [x] Existing materialised BillingPlan receives identical generic configuration through the existing mirror path.
- [x] Existing unconfigured plans are surfaced for explicit repair rather than assigned guessed defaults.
- [x] No ShopFeaturePreference is mutated.
- [x] No DB schema or consumer-runtime work is introduced.

## Validation

- [x] focused pricing-policy/payload/action tests
- [x] existing Merchant Pricing Plan tests
- [x] `npm run prisma:validate`
- [ ] `npm run test:unit`
- [ ] `npm run lint`
- [x] `npm run build`
- [x] `git diff --check`
- [x] changed-file diagnostics clean

## Stop Condition

Set status to `review`, complete Completion Report, return to `moda_architect` and STOP. Do not begin other ARCH-023 Admin tasks.

## Completion Report

### Status
Ready for Architect Review (Attempt 2)
### Files Changed
Pricing-plan action and builder, Merchant Knowledge feature-control and persistence helpers, focused plan-save unit coverage, and the pricing-plan security contract test. No package, database gitlink, schema, or migration change was made in Attempt 2.
### Work Completed
Addressed A1-R1 by deriving all Supported features controls from one tested model: an existing Merchant Knowledge mapping now contributes no second generic control, while the single product-policy control remains checked and disabled. Addressed A1-R2 by extracting the existing transaction's mapping persistence and BillingPlan mirror into a helper used by the current create/update action; behavioral tests prove exact Merchant Knowledge JSON persistence, preservation of requested and inactive mappings, identical mirror configuration, and no preference writes. Addressed A1-R3/A1-R4 with both attempts' verified launcher provenance and evidence-aligned task checklists.
### Validation Results
Attempt 2 focused Merchant Knowledge policy/payload/save tests: 19/19 passed. Focused pricing security: 12/12 passed. `npm run prisma:validate`, `npx tsc --noEmit --pretty false`, changed-file diagnostics, `git diff --check`, and `npm run build` passed. The build emitted existing BullMQ optional-dependency warnings. Changed production-file ESLint reported no errors; the two explicitly passed test files are ignored by the repository ESLint configuration.

The full `npm run test:unit` run completed with 168 passed and 2 unrelated failures: `tests/unit/merchant-pricing-translation-workbook.test.ts` / “rejects stale metadata, locale/header changes, and highlight identity changes” failed its existing `assert.ok` at line 207; `tests/unit/merchant-pricing-translations.test.ts` / “returns all bounded validation issues in canonical order” did not produce the expected `PLAN_HANDLE_MISMATCH` issue at line 211. Both are outside the changed files and match the two translation failures recorded in Attempt 1. The full `npm run lint` remains blocked by three errors outside this task: `src/components/admin/billing-drawers.tsx:178` (`react-hooks/purity`, `Date.now` during render), `src/components/admin/promotions/promotion-campaign-reactivation-drawer.tsx:31` (`react-hooks/purity`, `Date.now` during render), and `src/components/admin/promotions/promotion-campaign-reactivation.tsx:74` (`react-hooks/set-state-in-effect`). Changed production files were independently checked with ESLint; no changed-file diagnostics were reported. The task-relevant validation therefore passes without changing unrelated translation, billing, or promotions code.
### Deviations
Updated existing source-contract security assertions to follow the production transaction helper/control-model boundary, and extracted the existing plan-feature write sequence so the required create/update/mirror behavior can be tested without adding a separate materialization path.
### Assumptions
The downstream Architect Review will assess the repeatable, unrelated translation-unit and billing/promotions lint failures separately; no corresponding diagnostics occur in the changed production files.
### Unresolved Issues
The two repository-wide translation unit failures and three billing/promotions lint errors listed above remain unresolved and outside ADMIN-001 scope. The full broad security suite was not repeated in Attempt 2; its unrelated Attempt 1 failures remain documented above in the original report history.
### Architectural Concerns
None identified; no schema, consumer-runtime, preference, or second materialization mechanism was introduced.

### Launcher Preparation Evidence (Attempt 1)

Recorded from the Attempt 1 launcher packet; preparation was not rerun to create this historical evidence.

```text
canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-023-ADMIN-001
parent branch: task/ARCH-023-ADMIN-001
parent remote task-branch fast-forward: not-needed
parent origin/main incorporated: already-current
parent synchronized HEAD: 1bd4cf4306dbe31c504a212a7df869faf0d125db
implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-023-ADMIN-001
implementation branch: task/ARCH-023-ADMIN-001
implementation remote task-branch fast-forward: not-needed
implementation origin/main incorporated: already-current
implementation synchronized HEAD: abb828dd9f42e510627474f3048426102d9c2938
recursive submodule sync: passed
recursive submodule update/init: passed
recursive submodule status: ready
database recorded commit: 2eb17ee910491e8f9df82736fc0a843844415947 (initialized)
claim executor: copilot
claimed_at: 2026-09-30T08:56:24Z
Attempt 1 claim commit: 4b868fdd366ebfaf438e92982d077473f9c1b6d7 (committed and pushed)
```

### Launcher Preparation Evidence (Attempt 2)

```text
canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-023-ADMIN-001
parent branch: task/ARCH-023-ADMIN-001
parent remote task-branch fast-forward: not-needed
parent origin/main incorporated: yes (already-current at final parent synchronization)
parent synchronized HEAD before claim: 3c63add1d0af6789acfc7ac4703acec4a37d8022
implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-023-ADMIN-001
implementation branch: task/ARCH-023-ADMIN-001
implementation remote task-branch fast-forward: not-needed
implementation origin/main incorporated: yes
implementation synchronized HEAD: 2162216a58c3d6d40e935104e6ef95d39fa04ace
recursive submodule sync: passed
recursive submodule update/init: passed
recursive submodule status: ready
database recorded commit: 2eb17ee910491e8f9df82736fc0a843844415947 (initialized)
claim executor: copilot
claimed_at: 2026-09-30T12:08:44Z
Attempt 2 claim commit: 8c0048dbea8179f8375fd8e6d487ca537ed376fa (committed and pushed)
shared workspace checkout switched/mutated for task work: no
shared implementation checkout switched/mutated for task work: no
another task worktree reused: no
```

## Architect Review

### Review Status
Accepted — Attempt 2

### Review Notes

#### Attempt 2 review — Accepted — 2026-09-30

Reviewed the returned Attempt 2 implementation snapshot identified by the handoff as
implementation commit `c9b26aa` and parent report commit `598af8d8` against the original
ADMIN-001 contract and the complete Attempt 1 correction contract. Attempt 2 is accepted.

A1-R1 is resolved. Supported-feature rendering is now derived from one bounded control
model that combines catalogue and existing-plan Feature rows and filters
`merchant_knowledge` only after that combined identity set is built. The builder therefore
renders exactly one Merchant Knowledge control for both new and existing plans; that
control is checked, disabled and labelled as included by product policy. No second generic
editable Merchant Knowledge checkbox remains.

A1-R2 is resolved through the production persistence boundary rather than a test-only
materialisation path. Both create and update invoke
`persistMerchantPricingPlanFeatures()` inside the existing Merchant Pricing Plan
transaction. The helper persists the deterministic desired mapping objects to
`MerchantPricingPlanFeature`; when an operational BillingPlan already exists it uses the
same objects to delete removed mappings and upsert enabled `BillingPlanFeature` rows with
identical configuration. The helper contains no `ShopFeaturePreference` mutation.

The focused behavioral regression exercises that helper with the real desired-feature
builder and proves exact Merchant Knowledge JSON persistence, preservation of unrelated
requested configuration, preservation of inactive retained configuration, identical
BillingPlan mirror configuration and absence of preference writes. The existing-plan UI
regression proves there is exactly one locked Merchant Knowledge product-policy control.

The remainder of the original implementation remains architecture-conformant by
inspection: the ordinary `merchant_knowledge` Feature remains `ALWAYS_ENABLED`, active and
`systemRequired=false`; conflicting persisted identity/state fails closed; the generic
Feature toggle cannot deactivate it; C2 parsing uses the published Shared contract; every
selected purpose/data-format pair is revalidated against active PostgreSQL catalogue
rows inside the save transaction; no plan-kind/name/handle-specific Merchant Knowledge
policy exists; invalid or missing existing configuration is surfaced for explicit repair;
and the rollout helper does not invent defaults.

The Admin package and lockfile pin exactly
`@modainteract/moda-interact-shared@1.0.1`. The accepted ARCH-023 database revision is the
recorded initialized submodule commit `2eb17ee910491e8f9df82736fc0a843844415947`; no schema
or migration edit is part of this task.

A1-R3/A1-R4 are also resolved. The Completion Report now records the launcher-resolved
dedicated parent and implementation worktrees, matching task branches, start-of-attempt
synchronization, recursive submodule preparation, shared-checkout non-use and claim
evidence for both attempts. Work Items and Acceptance Criteria match the completed task
surface. The two broad unit failures and three broad lint errors remain unchecked only as
explicit unrelated repository-wide failures; changed production files have no matching
lint/type diagnostics and the focused task suites pass.

The review archive intentionally omits Git metadata and installed `node_modules`.
Accordingly the architect did not claim to re-run dependency-backed validation from the
archive; the submitted validation record was inspected alongside the actual returned
source and tests.

### Reviewed Files

Implementation repository:

- `package.json`
- `package-lock.json`
- `src/lib/admin/merchant-knowledge-plan-policy.ts`
- `src/lib/admin/merchant/pricing-builder-payload.ts`
- `src/lib/admin/merchant/pricing-plan.ts`
- `src/lib/admin/merchant/pricing-plan-feature-controls.ts`
- `src/lib/admin/merchant/merchant-pricing-plan-feature-persistence.ts`
- `src/app/actions/merchant-pricing-plan.ts`
- `src/app/actions/feature-catalogue.ts`
- `src/components/admin/merchant/merchant-pricing-plan-builder.tsx`
- `src/components/admin/merchant/merchant-pricing-plan-catalog.tsx`
- `src/app/(protected)/billing/page.tsx`
- `tests/unit/merchant-knowledge-plan-policy.test.ts`
- `tests/unit/merchant-pricing-builder-payload.test.ts`
- `tests/unit/merchant-pricing-plan-merchant-knowledge.test.ts`
- `tests/security/admin-merchant-pricing-plan.test.mjs`
- accepted ARCH-023 schema exposed through the Admin `database` submodule snapshot

Parent workspace:

- `docs/decisions/admin/ARCH-023/ADMIN-001-author-merchant-knowledge-plan-entitlement.md`
- `docs/decisions/admin/ARCH-023/_index.md`
- `docs/architecture/ARCH-023-merchant-knowledge.md`

### Validation Reviewed

- Attempt 2 focused Merchant Knowledge policy/payload/save suites: **19/19 passed**.
- Attempt 2 focused pricing security suite: **12/12 passed**.
- Submitted `npm run prisma:validate`, `npx tsc --noEmit --pretty false`, production build,
  changed-file diagnostics and `git diff --check` all passed.
- Changed production-file ESLint reported no errors; the two explicitly invoked test files
  are ignored by the repository ESLint configuration.
- Full `npm run test:unit` recorded **168 passed / 2 unrelated failures** in the existing
  merchant-pricing translation suites. Neither failure is in a changed ADMIN-001 file.
- Full `npm run lint` recorded three unrelated existing errors in billing/promotions UI;
  none is in the changed production surface.
- Confirmed by source inspection that create/update both invoke the same persistence
  helper, the BillingPlan mirror is generic, and there is no `ShopFeaturePreference`
  operation in that helper.
- Confirmed the package manifest and lockfile pin exact Shared `1.0.1`.
- The review archive has no installed `node_modules`; dependency-backed commands were not
  independently re-run in the review container.

### Architecture Conformance

Conforms. ADMIN-001 remains an Admin-owned pricing-catalogue authoring boundary over the
accepted ARCH-023 database and Shared contracts. Merchant Knowledge remains an ordinary
Feature selected by product policy rather than a schema-level required Feature. Plan
configuration is validated against C2 plus the active Purpose/Data Format catalogue and is
copied generically into an already-materialised BillingPlan without semantic
transformation.

No second BillingPlan materialisation mechanism, plan-specific Merchant Knowledge
default, preference reconstruction, schema/migration change, source CRUD, Background
processing or Commerce runtime behavior is introduced. PostgreSQL remains authoritative
for the selectable source-type catalogue and explicit existing-plan repair state.

### Follow-up

`ARCH-023-ADMIN-001` is **Complete / Accepted at Attempt 2**.

This acceptance satisfies one prerequisite of `ARCH-023-COMMERCE-002`, but does not make
that task Ready because `ARCH-023-COMMERCE-001` is still Ready rather than Complete in the
current snapshot. No task becomes newly Ready solely from ADMIN-001 acceptance. The
existing executable frontier therefore retains `ARCH-023-ADMIN-003`,
`ARCH-023-BACKGROUND-002`, `ARCH-023-BACKGROUND-003`, `ARCH-023-COMMERCE-001` and
`ARCH-023-SHOPIFY-001`. No downstream implementation is started implicitly by this
review.

#### Historical Attempt 1 — Changes Requested — 2026-09-30

##### Review Notes


The implementation is substantially aligned with the ARCH-023 plan-entitlement design, but Attempt 1 is not yet acceptable.

A1-R1 — Existing-plan UI reintroduces `merchant_knowledge` into the generic editable Feature list. The dedicated Merchant Knowledge row is correctly rendered checked and disabled, but the generic list filters `merchant_knowledge` only from `featureCatalogue` before concatenating `plan.features`. An existing plan therefore contributes its Merchant Knowledge Feature again after the filter. Because the Feature is active and `systemRequired=false`, that second row is rendered unchecked and editable. Correct the generic list so `merchant_knowledge` is excluded after all catalogue/existing-plan sources are combined, or equivalently exclude it from every source before combination. Add a regression proving an existing plan renders exactly one Merchant Knowledge Feature control and that control is the locked product-policy control.

A1-R2 — R15 requires behavioral tests for the plan-save contract, but the submitted focused coverage does not include the task-authorized `tests/unit/merchant-pricing-plan-merchant-knowledge.test.ts`. `merchant-knowledge-plan-policy.test.ts` proves the pure mapping policy and C2/catalogue validation; the security test only source-matches the action/mirror implementation. Add focused behavioral coverage that exercises the Merchant Pricing Plan save/mirroring boundary (using repository-local test doubles or a bounded extracted helper where necessary) and proves at minimum: one exact Merchant Knowledge mapping is persisted on create/update; unrelated requested Feature configuration survives; inactive retained Feature configuration survives; a materialised `BillingPlanFeature` receives the same Merchant Knowledge configuration through the generic mirror path; and no `ShopFeaturePreference` mutation is performed. Do not introduce a second materialisation mechanism merely to make the test convenient.

A1-R3 — The durable Completion Report does not record the launcher-resolved parent/implementation worktree paths or the start-of-attempt synchronization/preparation evidence required by `docs/agent-worktree-isolation-policy.md`. Record the actual Attempt 1 provenance already used; do not fabricate or rerun launcher preparation merely to create different evidence. If the original preparation evidence is unavailable, restore/verify the canonical task worktrees, rerun the required validation there, and record that evidence.

A1-R4 — Before returning Attempt 2 to review, update the task-owned Work Items, Acceptance Criteria and Validation checkboxes to match the evidence actually completed. Required repository-wide checks that remain blocked by established unrelated baseline failures may remain unchecked only when the Completion Report identifies the exact failure/baseline evidence and demonstrates that changed files introduce no corresponding regression.

No database/schema change, new Shared release, plan-specific defaults, preference reconstruction, or downstream ARCH-023 task is authorised by these corrections. Production changes should be limited to A1-R1 unless the new behavioral tests expose a defect within ADMIN-001 scope.

##### Reviewed Files

- `src/lib/admin/merchant-knowledge-plan-policy.ts`
- `src/lib/admin/merchant/pricing-builder-payload.ts`
- `src/lib/admin/merchant/pricing-plan.ts`
- `src/app/actions/merchant-pricing-plan.ts`
- `src/app/actions/feature-catalogue.ts`
- `src/components/admin/merchant/merchant-pricing-plan-builder.tsx`
- `src/components/admin/merchant/merchant-pricing-plan-catalog.tsx`
- `src/app/(protected)/billing/page.tsx`
- `src/components/admin/billing-drawers.tsx`
- `tests/unit/merchant-knowledge-plan-policy.test.ts`
- `tests/unit/merchant-pricing-builder-payload.test.ts`
- `tests/security/admin-merchant-pricing-plan.test.mjs`
- `package.json` / `package-lock.json`
- accepted ARCH-023 database schema exposed through the Admin `database` submodule snapshot

##### Validation Reviewed

Submitted evidence records: focused pricing security 12/12 passed; focused policy/payload tests 16/16 passed; Prisma validation, TypeScript, changed-file diagnostics, `git diff --check`, and production build passed. The submitted report also records broader unrelated translation/security/lint failures. These results are not sufficient for acceptance because R15's action-level plan-save/mirror behavioral proof is missing.

##### Architecture Conformance

The server-side product-policy, C2/catalogue validation, configuration-preserving desired mapping, generic BillingPlan mirror, rollout-warning helper and no-preference-write design conform to ARCH-023 by inspection. The existing-plan builder rendering described in A1-R1 does not conform to R7 because it exposes a second editable Merchant Knowledge control. Workflow evidence is also incomplete under the architect worktree-isolation protocol.

##### Follow-up

Return the same task to the normal `/moda-task ARCH-023-ADMIN-001` execution path. The next successful claim is Attempt 2. Complete A1-R1 through A1-R4, rerun the focused/required validation appropriate to the changed surface, update the Completion Report, set status to `review`, and STOP. Do not start another ARCH-023 Admin task.
