---
id: ARCH-023-SHOPIFY-002
architecture_id: ARCH-023
title: Select Store Category and persist pending Shop profile
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 50
executor: null
claimed_at: null
attempt: 2
depends_on:
  - ARCH-023-DATABASE-001
  - ARCH-023-SHARED-002
enables:
  - ARCH-023-SHOPIFY-003
created: 2026-09-29
updated: 2026-09-30
---

# Select Store Category and persist pending Shop profile

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Implement one reusable merchant Store Category selection lifecycle and expose it on both:

```text
existing onboarding page
existing Recovery Settings -> Store Profile section
```

A selection must pin the selected category's exact current canonical-English default template into one pending Shop prompt DRAFT and persist `CommerceShopProfile` pending state.

Selection never directly activates a category or publishes a prompt.

## Context

Initial onboarding selection and later post-onboarding category changes are the same durable operation and must not be implemented twice.

The existing first-install CTA already targets:

```text
/app/billing/select
```

That route must remain the Managed Pricing destination. The onboarding page now requires a valid pending category selection before its plan CTA can continue.

Later category changes occur on Recovery Settings and remain pending until Admin publishes the exact DRAFT.

## Scope

Primary authorized implementation surface:

```text
database                         # gitlink update only
package.json
package-lock.json

app/services/store-profile/store-category.server.ts
app/services/store-profile/store-category-selection.server.ts
app/services/store-profile/shopify-taxonomy-suggestion.server.ts
app/services/store-profile/store-category-localization.ts

app/components/onboarding/Onboarding.jsx

app/routes/app/recovery-settings/route.tsx
app/routes/app/recovery-settings/RecoverySettingsView.tsx
app/components/settings/StoreProfileSection.tsx

app/routes/app/store-profile/category/route.ts       # exact action endpoint

app/i18n/locales/*.json
scripts/validate-arch023-store-category-locales.mjs

tests/unit/store-category-selection.test.ts
tests/unit/shopify-taxonomy-suggestion.test.ts
tests/unit/store-profile-section.test.tsx
tests/unit/onboarding-store-category.test.tsx
tests/integration/store-category-selection.integration.test.ts
```

Use the repository's existing authenticated Shopify route/session/access helpers.

## Out of Scope

- publishing/activating the pending Shop prompt.
- subscription activation.
- Admin category/template CRUD.
- capability-local prompt authoring.
- Merchant Knowledge source CRUD.
- database-backed category translations.
- a new onboarding route.
- changing `/app/billing/select` destination semantics.
- a second Store Profile page/navigation item.

## Requirements

### R1 — adopt exact dependencies

Advance the `database` gitlink to accepted `ARCH-023-DATABASE-001`, pin exactly `@modainteract/moda-interact-shared@1.0.1` from Architect-Accepted `ARCH-023-SHARED-002` (no range, `latest`, workspace link or later release without architect reconciliation), and regenerate Prisma Client.

Do not edit database submodule schema/migrations.

### R2 — exact category eligibility read model

A category is merchant-selectable only when:

```text
category.enabled = true
category.defaultTemplateId != null
defaultTemplate exists
defaultTemplate.enabled = true
defaultTemplate.categoryId = category.id
defaultTemplate.promptText.trim() != ""
category slug has source-controlled merchant localization keys
```

Order selectable categories:

```text
displayOrder ASC
id ASC
```

Return only:

```ts
{
  id,
  slug,
  localizedDisplayName,
  localizedDescription,
  defaultTemplate: {
    id,
    key,
    displayName,
    editVersion
  }
}
```

Do not return `promptText` to the browser unless the UI explicitly displays a read-only preview. The server transaction always re-reads the authoritative template on selection.

### R3 — source-controlled localization gate

Use exact merchant-facing keys:

```text
storeProfile.categories.<slug>.displayName
storeProfile.categories.<slug>.description
```

The English catalogue is the canonical source-controlled slug manifest:

```text
app/i18n/locales/en.json
```

A database category slug absent from those English keys is not selectable.

Create:

```text
scripts/validate-arch023-store-category-locales.mjs
```

It must derive Store Category slugs from matching English key pairs and require the same two keys for every derived slug in all 20 ARCH-023 supported locale catalogues.

Unexpected runtime missing key uses existing English catalogue fallback and emits a bounded diagnostic.

Do not create translation rows/queue jobs.

### R4 — exact Shopify taxonomy evidence query

Create a bounded suggestion adapter using the authenticated Shopify Admin GraphQL client.

Query exactly one deterministic page:

```graphql
query ModaStoreCategorySuggestionProducts {
  products(first: 250, sortKey: ID) {
    nodes {
      category {
        id
      }
    }
  }
}
```

Do not paginate beyond 250 in v1.

Ignore products with null category.

A taxonomy evidence read failure must not block category selection; continue with no taxonomy evidence and use the fallback in R5.

Do not persist product/category evidence.

### R5 — exact category suggestion scoring

Load current `CommerceStoreCategoryTaxonomyMapping` rows for selectable categories.

For every product taxonomy `category.id` returned by R4:

- find the mapping with exact `shopifyTaxonomyCategoryId`;
- add its positive `weight` to that mapped Moda category's score.

Repeated products in the same Shopify taxonomy category contribute repeatedly.

Choose:

```text
highest total score
then category.displayOrder ASC
then category.id ASC
```

If no evidence matches any mapping, choose the first selectable category by:

```text
displayOrder ASC, id ASC
```

Suggestion is advisory. Merchant can select any selectable category.

### R6 — one reusable selection action/service

Implement:

```ts
selectPendingStoreCategory({
  shopId,
  categoryId,
  expectedPendingSelectionGeneration,
})
```

The browser never supplies prompt/template ids.

Run in one transaction.

### R7 — exact selection transaction

1. lock the Shop row for `shopId`;
2. load/create `CommerceShopProfile`;
3. require:
   ```text
   profile.pendingSelectionGeneration == expectedPendingSelectionGeneration
   ```
   on update; initial absent profile expects generation `0`;
4. re-read selected category + default template and re-validate R2 eligibility;
5. resolve the unique Shop prompt lineage:
   ```text
   scope = SHOP
   shopId = exact shop
   ```
6. if more than one lineage exists -> configuration conflict;
7. create lineage if absent;
8. resolve pending DRAFT:
   - if `profile.pendingPromptRevisionId` exists, load that exact revision and require same Shop lineage + `status=DRAFT`;
   - if no pending pointer, require there is no other DRAFT on the lineage; if an unrelated DRAFT exists, fail conflict rather than overwrite it;
   - otherwise create next revision number as one DRAFT;
9. write exact DRAFT content/provenance:
   ```text
   promptText                = exact current defaultTemplate.promptText
   sourceTemplateId          = defaultTemplate.id
   sourceTemplateEditVersion = defaultTemplate.editVersion
   ```
10. for an existing pending DRAFT, increment its `editVersion` by one;
11. write profile:
   ```text
   pendingCategoryId          = category.id
   pendingPromptRevisionId    = draft.id
   pendingSelectedAt          = now
   pendingSelectionGeneration = previous + 1
   ```
12. leave:
   ```text
   activeCategoryId
   activeCategoryActivatedAt
   CommerceAgentConfiguration.activePromptRevisionId
   ```
   unchanged;
13. commit.

Do not publish the DRAFT.

### R8 — repeat selection behavior

Selecting the same category again is allowed and is still a new explicit selection:

```text
pendingSelectionGeneration += 1
pendingSelectedAt = now
```

The exact current default template snapshot is re-pinned into the same pending DRAFT.

A stale `expectedPendingSelectionGeneration` rejects with conflict.

### R9 — onboarding UI

Modify the existing `Onboarding.jsx`; do not create a second onboarding route.

The page loads:

```text
selectable categories
current pending profile selection
taxonomy-based suggestion
merchant UI locale
```

Selection precedence:

```text
persisted pending category if still selectable
else taxonomy suggestion
else first selectable category
```

The merchant may change it.

Before navigation to `/app/billing/select`, persist the currently selected category through R6.

Both existing plan CTAs must use this behavior.

If no selectable category exists:

```text
disable Choose Plan
show bounded configuration unavailable message
```

Do not navigate to Shopify Managed Pricing without successful pending persistence.

### R10 — later Store Profile UI

Add a `Store Profile` section to the existing Recovery Settings page.

Show:

```text
active category localized label/description, if any
pending category localized label/description, if any
pending state indicator
template provenance metadata (displayName/key + edit version; never prompt text required)
Change category control
```

Submitting another category uses the same R6 service/action.

The currently active category and active Shop prompt remain effective until Admin publication.

### R11 — language behavior

Merchant-facing category labels use the current merchant UI locale/catalogue.

Prompt text copied into the DRAFT is always canonical English from:

```text
CommercePromptTemplate.promptText
```

Never translate template prompt text.

### R12 — no activation authority

This task must not inspect Subscription to decide whether a pending category becomes active.

It only persists pending selection.

`ShopSettings.onboardingCompleted` is not activation authority.

### R13 — ARCH-023 merchant localization foundation

In the same locale-catalogue change, add the exact key families required later by Merchant Knowledge UI for every Shared C3 key:

```text
merchantKnowledge.purposes.<PURPOSE_KEY>.label
merchantKnowledge.dataFormats.<DATA_FORMAT_KEY>.label
```

Required Purpose keys:

```text
COMPANY_INFORMATION
CUSTOMER_SUPPORT
POLICIES
FAQ
PRODUCT_INFORMATION
SHIPPING_AND_DELIVERY
PRICING
```

Required Data Format keys:

```text
WEB_PAGE
CSV
XLSX
```

All 20 supported locale files must contain every key.

Human-readable translations should follow the existing catalogue language conventions. This task fixes key identity/presence, not translation prose style.

Extend the validator to require these exact keys in all 20 catalogues.

### R14 — tests

Prove:

```text
category without valid default template excluded
slug missing from English localization manifest excluded
locale validator catches missing category/knowledge keys
taxonomy query is bounded to first 250 sorted by ID
weighted scoring + tie-break deterministic
taxonomy failure uses fallback
pending selection creates one Shop prompt lineage + one DRAFT
same pending DRAFT updated on category reselection
unrelated existing DRAFT blocks selection rather than being overwritten
stale selection generation rejects
active category/prompt pointer never changes
onboarding restores pending choice
onboarding persists before /app/billing/select
later Recovery Settings change uses same service
promptText copied exactly in canonical English
```

## Work Items

- [x] Adopt database/Shared revisions.
- [x] Add category eligibility/localization read model.
- [x] Add locale catalogue keys + validator.
- [x] Add bounded Shopify taxonomy suggestion adapter.
- [x] Implement one transactional pending-category selection service.
- [x] Integrate selection into existing onboarding CTAs.
- [x] Add Store Profile section to Recovery Settings.
- [x] Add route/action and focused tests.

## Interfaces / Contracts

Consumes ARCH-023 database models and Shared locale contract.

Writes:

```text
CommerceShopProfile pending fields
CommerceAgentPrompt
CommerceAgentPromptRevision DRAFT
```

Produces no queue/event.

## Dependencies

- `ARCH-023-DATABASE-001`
- `ARCH-023-SHARED-002`

Admin Store Category authoring may be implemented in parallel against the same database contract.

## Enables

- `ARCH-023-SHOPIFY-003`

## Acceptance Criteria

- [x] Initial and later category selection use one service/transaction.
- [x] Selection pins exact template text/editVersion into one pending Shop DRAFT.
- [x] No selection directly changes active category/prompt.
- [x] Taxonomy suggestion is bounded, deterministic and advisory.
- [x] Existing onboarding route structure and `/app/billing/select` destination are preserved.
- [x] Category and Merchant Knowledge localization keys exist across all 20 catalogues.
- [x] No database translation lifecycle exists.

## Validation

- [x] focused service/action/component tests
- [x] disposable PostgreSQL integration for the R7/R8 selection transaction, rollback and row-lock concurrency (Attempt 2 Testcontainers proof passed 5/5)
- [x] locale-catalogue validator
- [x] existing onboarding and Recovery Settings regressions
- [x] `npm run typecheck`
- [x] `npm run lint` (task-owned files clean; repository-wide command has unrelated existing failures)
- [x] `npm run build`
- [x] `git diff --check`
- [x] changed-file diagnostics clean

## Stop Condition

Set status to `review`, complete Completion Report, return to `moda_architect` and STOP. Do not begin SHOPIFY-003.

## Implementation Notes

The Product GraphQL category field is Shopify Standard Product Taxonomy identity. Do not attempt to map product titles/types heuristically when `category.id` is absent.

## Completion Report

### Status
Review requested; awaiting `moda_architect`. No architect acceptance decision has been made by this agent.
### Files Changed
`moda-interact`: `package.json`, `package-lock.json`; onboarding and Recovery Settings route/view integration; the shared category action, read model, selection service, localization helper, and Shopify taxonomy suggestion service; all 20 locale catalogues; locale validator; focused Store Category, onboarding, Recovery Settings, locale, and home-route tests. Shared v1 API compatibility updates were made to feature-preference selection and its existing integration test.

Attempt 2 adds only `tests/integration/store-category-selection.postgres.integration.test.ts` in the implementation repository; no production source, dependency, schema, migration, locale, or database gitlink changes were made in this attempt.
### Work Completed
Implemented one authenticated selection endpoint backed by one Shop-row-locked transaction. It validates the pending generation, pins the exact canonical-English default template text and source-template version to one pending Shop DRAFT, reuses that DRAFT on reselection, and leaves active category/prompt configuration unchanged. Added category eligibility and localized read models, bounded one-page Shopify taxonomy suggestion/scoring, onboarding persistence before Managed Pricing navigation, and the Store Profile section in Recovery Settings. Added localized category, Store Profile UI, and Merchant Knowledge labels, plus a validator that derives category slugs from English key pairs and checks all required keys across the 20 supported locales.
Attempt 2 adds a task-owned Testcontainers integration against real PostgreSQL 17 with pgvector and the real generated Prisma Client. It verifies initial profile/SHOP lineage/DRAFT creation and exact canonical-template provenance, preserves existing active category and configuration during reselection, increments the same DRAFT and selection generation, rejects stale generations without committed mutation, rolls back a newly created profile when an unrelated DRAFT causes conflict, and serializes concurrent generation-zero calls so exactly one succeeds.
### Validation Results
Passed: 49 focused and adjacent tests; locale validator (20 locales, 12 required category/knowledge keys); merchant ICU runtime loading for all 20 locales; `npm run typecheck`; changed-file ESLint; `npm run build`; `git diff --check`; changed-file diagnostics.

Repository-wide `npm run lint` still reports 20 errors and 2 warnings in unrelated existing files. The existing opt-in PostgreSQL merchant-settings tests were skipped (6 tests) because `MODA_SETTINGS_POSTGRES` was not enabled; transaction behavior is covered by focused service tests, and action scoping/input validation by route-level tests.

The Shared dependency is pinned exactly to `1.0.1`. The database submodule was already at accepted ARCH-023-DATABASE-001 commit `2eb17ee910491e8f9df82736fc0a843844415947`; no database schema, migration, or gitlink changes were made. Prisma Client generation completed during the production build.

Attempt 2 real PostgreSQL proof:

- Testcontainers image: `pgvector/pgvector:pg17` (`pgvector/pgvector@sha256:cf134a767f474095eeba57e0117be8e568e011a63f33fbf252f14c9b760f8e6f`). Testcontainers generated isolated per-run database credentials and a dynamically mapped port.
- Migration command, run by integration setup against that fresh database: `npx prisma migrate deploy --schema database/prisma/schema.prisma`; all accepted repository migrations applied successfully.
- Test command: `DOCKER_HOST="unix:///Users/kwadwoadomafriyie/.colima/default/docker.sock" TESTCONTAINERS_RYUK_DISABLED=true MODA_DISPOSABLE_INTEGRATION=1 npm test -- tests/integration/store-category-selection.postgres.integration.test.ts`.
- Result: exit code 0; `Test Files 1 passed (1)`, `Tests 5 passed (5)`. The cases use the real generated Prisma Client and independent clients for the concurrent calls.
- Teardown: the test's `afterAll` stopped the Testcontainers PostgreSQL instance; `docker ps -a --filter ancestor=pgvector/pgvector:pg17 --format '{{.Names}} {{.Status}}'` returned no containers.
- Additional Attempt 2 checks: `npm run typecheck` passed; `npm test -- tests/unit/store-category-selection.test.ts` passed 5/5; Prettier check and changed-file ESLint passed; `git diff --cached --check` passed. ESLint emitted only the repository's existing TypeScript-version support warning.

Testcontainers could not infer the active Colima context from the default environment. Supplying its Docker socket and disabling Ryuk's unsupported socket bind allowed Testcontainers to start; the integration test retained and verified its own explicit PostgreSQL teardown. No runtime or test infrastructure was changed.
### Deviations
No functional scope deviations. Repository-wide lint still reports the 20 unrelated errors and 2 warnings recorded in Attempt 1; changed-file lint passes. The real PostgreSQL requirement is satisfied in Attempt 2.
### Assumptions
The existing accepted Admin task fixture supplies the currently manifested stable category slug `home-goods`; additional Admin-authored slugs remain unselectable until their English key pair and locale translations are shipped.
### Unresolved Issues
No known implementation blockers. The A1-R1 real PostgreSQL transaction proof and A1-R2 durable workflow provenance are recorded for architect review.
### Architectural Concerns
None identified. Selection remains pending-only and does not activate or publish a prompt.

### Git / VCS

Task branch: `task/ARCH-023-SHOPIFY-002` in both repositories.

Dependency gate from the prepared Attempt 2 packet: passed; `ARCH-023-DATABASE-001` and `ARCH-023-SHARED-002` were both `complete`.

Physical worktree isolation:
- canonical workspace root: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`
- parent worktree and branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-023-SHOPIFY-002`, `task/ARCH-023-SHOPIFY-002`
- implementation worktree and branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-023-SHOPIFY-002`, `task/ARCH-023-SHOPIFY-002`
- shared workspace/source-reference checkout switched or mutated: no
- another task worktree reused: no; the launcher-reused canonical worktrees belong to this task

Start-of-attempt synchronization from the prepared packet:
- parent remote task branch fast-forwarded: not-needed
- parent `origin/main` incorporated: already-current
- implementation remote task branch fast-forwarded: not-needed
- implementation `origin/main` incorporated: already-current

Recursive implementation submodules from the prepared packet:
- `git submodule sync --recursive`: passed
- `git submodule update --init --recursive`: passed
- status: ready; database submodule at `2eb17ee910491e8f9df82736fc0a843844415947`
- no database files or submodule gitlink changes were made

Attempt 2 claim: launcher commit `b60ae301577a78740eb84b649aa2b8bea5ec710f`, timestamp `2026-09-30T11:18:13Z`; committed and pushed before implementation. Parent report branch at claim: `b60ae301577a78740eb84b649aa2b8bea5ec710f`.

Implementation submission:
- repository: `moda-interact`
- commit: `e287ba7b246dc1fd40e752512c47ad823fc18d0a`
- branch: `origin/task/ARCH-023-SHOPIFY-002`; pushed
- changed file: `tests/integration/store-category-selection.postgres.integration.test.ts`
- final implementation worktree: clean

Parent report submission:
- task file: `docs/decisions/shopify/ARCH-023/SHOPIFY-002-select-store-category-pending-profile.md`
- branch: `task/ARCH-023-SHOPIFY-002`; this Attempt 2 report update is committed and pushed with the review submission
- final parent worktree: clean after report submission

Merged to implementation `main`: no. Merged to workspace `main`: no.

## Architect Review

### Review Status
Changes Requested — Attempt 1.

### Review Notes
The implementation is structurally aligned with the ARCH-023 Store Category contract, but two bounded acceptance gaps remain.

**A1-R1 — prove the R7/R8 transaction against real PostgreSQL.** The core service uses `PrismaClient.$transaction`, a raw `SELECT ... FOR UPDATE` Shop-row lock and database-enforced relations/uniqueness, but the submitted transaction tests replace `$transaction`, `$queryRaw` and all Prisma repositories with mocks. The route-level integration test also mocks `selectPendingStoreCategory`. The six opt-in PostgreSQL tests reported as skipped belong to the pre-existing merchant-settings suite and do not execute this task's selection transaction. Mock coverage therefore does not prove that the exact raw SQL, migration/schema shape, rollback behaviour and row-lock serialization work together.

Attempt 2 must add a task-owned disposable PostgreSQL/Testcontainers integration for `selectPendingStoreCategory` using the accepted database migrations and the real generated Prisma Client. It must prove at minimum:

```text
initial generation 0 selection -> one CommerceShopProfile, one SHOP lineage and one DRAFT
DRAFT promptText/sourceTemplateId/sourceTemplateEditVersion exactly match the selected canonical template
activeCategoryId / activeCategoryActivatedAt and active prompt configuration remain unchanged
repeat selection reuses the same pending DRAFT and increments DRAFT editVersion + selection generation
stale expected generation rejects and commits no partial mutation
unrelated existing DRAFT with no pending profile pointer rejects without overwrite
two concurrent calls with the same expected generation serialize on the Shop row: exactly one succeeds, one conflicts, generation increments once, and no duplicate lineage/DRAFT is created
```

Do not change the accepted database schema/migration to manufacture the proof. The existing `@testcontainers/postgresql` pattern may be reused. Under the workspace validation policy, the repository agent may add the bounded test and report the exact developer command; developer-supplied command/result/exit-code evidence is acceptable and does not need an architect rerun.

**A1-R2 — persist canonical task-worktree/start-of-attempt provenance.** The Completion Report currently records neither launcher-resolved task paths nor the prepared synchronization packet. Before acceptance it must durably record:

```text
launcher-resolved parent task worktree
launcher-resolved moda-interact implementation worktree
branch task/ARCH-023-SHOPIFY-002 in both worktrees
start-of-attempt fetch / task-branch fast-forward / origin/main containment-or-merge result for both
recursive implementation-submodule preparation/status
dependency gate showing DATABASE-001 and SHARED-002 architect-accepted
clean final state and exact submitted implementation/report HEADs
```

If Attempt 1 was not executed in the canonical launcher-resolved implementation worktree, restore/reuse that canonical worktree on the already-pushed task branch and rerun the task-required validation there. Do not introduce implementation churn solely to create another commit.

The repository-wide lint result (20 unrelated errors and 2 warnings) is non-blocking because changed-file lint passed and no reported diagnostic is in task-owned files. The Shared `1.0.1` compatibility adjustment to existing feature-preference code is also acceptable as bounded dependency-adoption work; no further change is requested there.

### Reviewed Files
Reviewed the task contract/report plus the submitted implementation surfaces, including:

```text
package.json
package-lock.json
app/services/store-profile/store-category.server.ts
app/services/store-profile/store-category-selection.server.ts
app/services/store-profile/shopify-taxonomy-suggestion.server.ts
app/services/store-profile/store-category-localization.ts
app/routes/app/store-profile/category/route.ts
app/routes/app/home/route.jsx
app/components/onboarding/Onboarding.jsx
app/routes/app/recovery-settings/route.tsx
app/routes/app/recovery-settings/RecoverySettingsView.tsx
app/components/settings/StoreProfileSection.tsx
scripts/validate-arch023-store-category-locales.mjs
tests/unit/store-category-selection.test.ts
tests/integration/store-category-selection.integration.test.ts
tests/unit/shopify-taxonomy-suggestion.test.ts
tests/unit/onboarding-store-category.test.jsx
tests/unit/store-profile-section.test.tsx
tests/unit/store-category-locales.test.mjs
app/services/feature-preferences/feature-preferences.server.ts
tests/integration/merchant-feature-preferences.test.ts
```

All 20 locale catalogues were also inspected through the validator contract.

### Validation Reviewed
Submitted evidence records 49 passing focused/adjacent tests, typecheck, production build, changed-file ESLint, locale/ICU validation and diff checks. The ARCH-023 locale validator was independently executed against the submitted archive and passed for all 20 locales / 12 currently-derived required keys. The review archive does not include installed dependencies, so the TypeScript/build suite was not redundantly rerun.

The missing acceptance evidence is the task-owned real PostgreSQL transaction proof described in A1-R1, not the unrelated skipped merchant-settings PostgreSQL suite.

### Architecture Conformance
The implementation design conforms by inspection to the required pending-only lifecycle: category eligibility is server-authoritative, Shopify taxonomy evidence is bounded/advisory, prompt text is not exposed by the category DTO, onboarding and Recovery Settings share one selection endpoint/service, the canonical-English template is re-read inside the transaction, and no activation/publication authority is introduced. Acceptance is withheld only for A1-R1 and A1-R2.

### Follow-up
Return this same task to `ready` for Attempt 2. Preserve Attempt 1 and this review history. Attempt 2 should be limited to the PostgreSQL proof/test plus durable workflow evidence unless that proof exposes a real implementation defect. `ARCH-023-SHOPIFY-003` remains Pending; it also still depends on `ARCH-023-SHOPIFY-001`.
