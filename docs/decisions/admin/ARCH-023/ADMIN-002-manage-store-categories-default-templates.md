---
id: ARCH-023-ADMIN-002
architecture_id: ARCH-023
title: Manage Store Categories and default templates
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
enables:
  - ARCH-023-ADMIN-003
created: 2026-09-29
updated: 2026-09-30
---

# Manage Store Categories and default templates

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Create the authoritative Admin catalogue surface for:

```text
CommercePromptTemplateCategory
CommercePromptTemplate
CommerceStoreCategoryTaxonomyMapping
CommercePromptTemplateCategory.defaultTemplateId
```

The task owns canonical-English category/template authoring and Shopify-taxonomy mappings only. Merchant-facing category translations remain source-controlled in the Shopify application's locale catalogues and are not persisted or dispatched by Admin.

## Context

ARCH-023 removed the earlier database-backed category/template translation design.

A merchant-selectable Store Category requires:

```text
enabled category
+ enabled default template in that same category
+ Shopify application locale keys shipped for that category slug
```

Admin can enforce the first two because they are database state. Shopify owns the source-controlled localization-key gate.

## Scope

Primary authorized implementation surface:

```text
database                         # gitlink update only

src/app/(protected)/system-controls/store-categories/page.tsx
src/app/actions/store-categories.ts

src/components/admin/store-categories/store-category-catalog.tsx
src/components/admin/store-categories/store-category-editor.tsx
src/components/admin/store-categories/prompt-template-editor.tsx
src/components/admin/store-categories/taxonomy-mapping-editor.tsx

src/lib/admin/store-categories.ts
src/components/admin/sidebar.tsx

tests/unit/store-categories.test.ts
tests/unit/store-category-actions.test.ts
```

Existing Admin-shell/security tests may be extended.

## Out of Scope

- database-backed category/template translations.
- translation queues/workers.
- Shopify locale-file edits.
- Merchant onboarding.
- Shop prompt revision publication.
- Merchant Knowledge source configuration.
- Commerce Studio capability prompts.
- deleting historical/in-use prompt/category rows.
- arbitrary Admin creation of Merchant Knowledge Purpose/Data Format keys.

## Requirements

### R1 — adopt the accepted ARCH-023 database revision

Advance the Admin `database` submodule gitlink to the accepted/merged `ARCH-023-DATABASE-001` commit if ADMIN-001 has not already done so.

Do not edit database schema/migrations from this task.

### R2 — exact Admin route/navigation

Add protected page:

```text
/system-controls/store-categories
```

Extend AdminShell/Sidebar active navigation with:

```text
store-categories
```

Place link under existing `System controls`:

```text
Store Categories
```

All reads use existing `requirePlatformAdminPage` / `requirePlatformAdminRead` conventions.

All mutations use existing `requirePlatformAdminMutation` and additionally require:

```text
principal.role === SUPER_ADMIN
```

Development bypass follows the repository's existing durable-admin provisioning convention.

### R3 — category server model

`src/lib/admin/store-categories.ts` must provide a deterministic read model ordered:

```text
category.displayOrder ASC
category.displayName ASC
category.id ASC
```

Each category includes:

```text
id
slug
displayName
description
enabled
displayOrder
editVersion
defaultTemplateId
defaultTemplate summary
template summaries ordered displayName ASC, id ASC
taxonomy mappings ordered shopifyTaxonomyCategoryId ASC
activeShopProfile count
pendingShopProfile count
```

Do not load complete Shop rows.

### R4 — exact category input rules

Create category fields:

```text
slug         1..128, regex /^[a-z][a-z0-9-]{0,127}$/
displayName  trimmed 1..255
description  trimmed 0..2000
displayOrder integer 0..1_000_000
enabled      boolean
reason       trimmed 1..1000
```

Create initializes:

```text
editVersion = 1
```

Update category fields:

```text
displayName         trimmed 1..255
description         trimmed 0..2000
displayOrder        integer 0..1_000_000
enabled             boolean
expectedEditVersion positive integer
reason              trimmed 1..1000
```

`slug` is create-only and MUST NOT be accepted by the category update contract.

Update uses CAS:

```text
WHERE id = ? AND editVersion = expectedEditVersion
editVersion += 1
```

CAS miss returns a bounded stale-write error.

### R5 — category slug identity is immutable after creation

`CommercePromptTemplateCategory.slug` is a stable category/localization identity and is
immutable after INSERT, whether or not any active or pending Shop Profile references the
category.

Admin MUST NOT expose a slug rename control and no Admin update path may write `slug`.
The existing database category-identity guard remains the authoritative persistence
backstop; this task MUST NOT alter or bypass that guard.

Changing merchant-facing wording uses Shopify locale files while retaining the same slug.
A different slug means a different category identity: create the new category/slug, ship
its required Shopify locale keys before enabling it, and migrate any mappings/selections
through an explicitly authorised workflow rather than renaming the existing row in place.

### R6 — category enable/disable rules

To transition category:

```text
enabled: false -> true
```

require:

```text
defaultTemplateId != null
default template exists
default template.categoryId == category.id
default template.enabled == true
default template.promptText.trim() != ""
```

Do not attempt to inspect Shopify locale files from Admin at runtime.

The UI must show:

```text
Shopify localization keys must exist before merchants can select this category.
```

Enabling means "Admin catalogue enabled", not proof that Shopify has shipped localization.

Disabling a category is allowed even if referenced by active/pending profiles; it prevents new selection but does not rewrite existing profile rows.

### R7 — prompt template identity and input rules

Create template fields:

```text
key          1..128, regex /^[a-z][a-z0-9_]{0,127}$/
categoryId   required
displayName  trimmed 1..255
description  trimmed 0..2000
promptText   trimmed non-empty, max 100_000 characters
enabled      boolean
reason       trimmed 1..1000
```

Template `key` is immutable after creation.

`categoryId` is immutable after creation.

Update fields:

```text
displayName
description
promptText
enabled
expectedEditVersion
reason
```

CAS update:

```text
WHERE id = ? AND editVersion = expectedEditVersion
editVersion += 1
```

Do not create a Prompt Template revision table.

`promptText` remains mutable current canonical-English template content.

### R8 — default template selection

Action input:

```text
categoryId
templateId
expectedCategoryEditVersion
reason
```

In one transaction:

1. lock/re-read category;
2. require category editVersion matches;
3. load template;
4. require:
   ```text
   template.categoryId == category.id
   template.enabled == true
   template.promptText.trim() != ""
   ```
5. set:
   ```text
   category.defaultTemplateId = template.id
   category.editVersion += 1
   ```
6. audit.

Do not copy template text into any Shop prompt in this task.

### R9 — default-template disable protection

A template may not transition:

```text
enabled: true -> false
```

while it is the `defaultTemplateId` of any **enabled** category.

Required message:

```text
Choose another enabled default template before disabling this template.
```

For a disabled category, its default template may also be disabled; re-enabling the category later requires R6 again.

### R10 — Shopify taxonomy mapping lifecycle

Create/update mapping fields:

```text
categoryId
shopifyTaxonomyCategoryId trimmed 1..255
weight integer 1..1_000_000
reason trimmed 1..1000
```

The database unique constraint remains authoritative for `shopifyTaxonomyCategoryId`.

Admin supports:

```text
create mapping
update weight
move mapping to another category
remove mapping
```

Every mutation is transactional and SUPER_ADMIN-only.

Do not create taxonomy mappings from Shopify automatically.

### R11 — exact audit actions

Use existing `CommerceAuditEvent`.

Category:

```text
create  -> CREATE_PROMPT_TEMPLATE_CATEGORY
update/default/taxonomy change -> UPDATE_PROMPT_TEMPLATE_CATEGORY
enable  -> ENABLE_PROMPT_TEMPLATE_CATEGORY
disable -> DISABLE_PROMPT_TEMPLATE_CATEGORY
```

Template:

```text
create -> CREATE_PROMPT_TEMPLATE
metadata update -> UPDATE_PROMPT_TEMPLATE
promptText update -> UPDATE_PROMPT_TEMPLATE_CONTENT
enable -> ENABLE_PROMPT_TEMPLATE
disable -> DISABLE_PROMPT_TEMPLATE
```

When a template mutation changes both metadata and `promptText`, emit exactly one:

```text
UPDATE_PROMPT_TEMPLATE_CONTENT
```

and include changed-field names in audit `metadata`.

For taxonomy/default changes, use:

```text
UPDATE_PROMPT_TEMPLATE_CATEGORY
```

with audit metadata:

```json
{"changeKind":"DEFAULT_TEMPLATE"}
```

or:

```json
{"changeKind":"TAXONOMY_MAPPING"}
```

Set relevant `promptTemplateCategoryId` / `promptTemplateId`.

Do not add a new CommerceAuditAction enum.

### R12 — UI behavior

The Store Categories page must provide:

```text
category list
create category
edit category metadata
enable/disable category
view profile-reference counts

within selected category:
  template list
  create/edit/enable-disable template
  select default template

taxonomy mappings:
  add
  edit weight/category
  remove
```

Prompt text uses a multiline textarea large enough for canonical-English instructions.

No translation-status/progress UI exists.

### R13 — deterministic category suggestion data

The read model must make available the persisted mapping data exactly as:

```text
shopifyTaxonomyCategoryId
weight
category.displayOrder
category.id
```

but this Admin task does not implement merchant suggestion scoring. Shopify will consume the database records later.

### R14 — regressions

Tests must prove:

```text
non-SUPER_ADMIN mutation denied
duplicate slug rejected
slug malformed rejected
category update contract cannot rename slug, including when the category is unused
stale category/template write rejected
category cannot enable without valid enabled default
default template must belong to category
enabled default cannot be disabled
template key/category immutable
promptText cannot be blank
taxonomy weight <= 0 rejected
duplicate Shopify taxonomy id rejected
category disable does not mutate CommerceShopProfile
no translation row/job created
audit action/entity metadata correct
```

## Work Items

- [x] Adopt database gitlink.
- [x] Add protected Store Categories route/navigation.
- [x] Add category/template/taxonomy read model.
- [x] Add SUPER_ADMIN server actions with CAS.
- [x] Add exact default-template/enable invariants.
- [x] Add category/template/taxonomy UI.
- [x] Add exact audit events.
- [x] Add focused security/validation/UI tests.
- [x] Confirm no translation persistence/queue is introduced.

## Interfaces / Contracts

Reads/writes the ARCH-023 database models:

```text
CommercePromptTemplateCategory
CommercePromptTemplate
CommerceStoreCategoryTaxonomyMapping
CommerceShopProfile reference counts
CommerceAuditEvent
```

Produces no cross-repository event.

## Dependencies

- `ARCH-023-DATABASE-001`

## Enables

- `ARCH-023-ADMIN-003`

Planned Shopify onboarding/profile tasks will also depend on this catalogue after their definitions are created.

## Acceptance Criteria

- [x] Admin has one authoritative Store Category management surface.
- [x] Category/default-template invariants are enforced server-side.
- [x] Category slug is immutable after creation and no Admin update path can rename it.
- [x] Templates remain mutable current records with editVersion CAS; no revision table reappears.
- [x] Shopify taxonomy mappings are managed deterministically.
- [x] No category/template translation database or queue behavior exists.
- [x] Existing Admin auth/audit conventions are preserved.
- [x] No Shopify/Commerce runtime implementation is introduced.

## Validation

- [x] Focused category/template/action tests: 23 passed.
- [x] Focused Admin catalogue/security/navigation regressions: 8 passed.
- [x] `npm run test:unit` executed; 157 passed and 2 unrelated existing merchant-pricing translation tests failed.
- [x] `npm run lint` executed; 3 unrelated existing errors remain in billing/promotions files. Changed-file ESLint passed with zero errors.
- [x] `npm run build` passed; existing optional BullMQ dependency warnings were emitted.
- [x] `git diff --check` passed.
- [x] TypeScript check and changed-file diagnostics clean.

## Stop Condition

Set status to `review`, complete Completion Report, return to `moda_architect` and STOP. Do not begin ADMIN-003.

## Completion Report

### Status
Implemented and returned for Architect Review (Attempt 2).
### Files Changed
Added the protected Store Category catalogue route, mutation actions, validation/read models, category/template/taxonomy editors, navigation integration, and focused unit/security coverage. In the parent worktree, only this report changed; no database schema, migration, or gitlink changes were made.
### Work Completed
Implemented the authoritative Admin catalogue for categories, current default templates, and Shopify taxonomy mappings. Every mutation independently authenticates and requires `SUPER_ADMIN`, validates its contract, provisions the durable development admin within its transaction, uses the required transaction/CAS/locking rules, writes exact audit metadata, and revalidates the route. Category slug is create-only and immutable. The required Shopify localization-key warning is shown for enabled and disabled categories; Admin does not inspect locale files or persist translation state.
### Validation Results
- TypeScript: `npx tsc --noEmit --pretty false` passed.
- Focused unit/action/validation tests: 23 passed.
- Focused Admin catalogue/security/navigation regressions: 8 passed.
- Changed-file ESLint: zero errors; the ESLint configuration warns that `.mjs` and some Node test files are ignored.
- Production build passed and includes `/system-controls/store-categories`.
- `git diff --check` passed; changed-file diagnostics are clean.
- Broad unit suite: 157 passed, 2 unrelated existing merchant-pricing translation tests failed (`merchant-pricing-translation-workbook.test.ts` and `merchant-pricing-translations.test.ts`).
- Broad lint: 3 unrelated existing errors remain in billing/promotions files; 6 warnings were also reported.
- Broad security suite: 9 unrelated existing failure markers, including Tenant Directory KPI, purchase-status, ICU, catalogue, ARCH-014, economics, shared-release, and auth assertions. Focused catalogue/security/navigation tests passed.
### Deviations
None. Attempt 2 follows the architect-corrected immutable-slug contract. The required localization notice was made unconditional during final contract review.
### Assumptions
The existing initialized database submodule at `2eb17ee910491e8f9df82736fc0a843844415947` is authoritative and remains unchanged.
### Unresolved Issues
No ADMIN-002 implementation blockers. The unrelated broad-suite baseline failures listed above remain outside this task's scope.
### Architectural Concerns
None identified. Returned to `moda_architect` as required; ADMIN-003 was not started.

### Attempt 2 Launcher Preparation Evidence

```text
canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-023-ADMIN-002
parent branch: task/ARCH-023-ADMIN-002
parent synchronized HEAD before claim: 4ec8bb9b390ddfd95ff285a35800dc07066ca861
implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-023-ADMIN-002
implementation branch: task/ARCH-023-ADMIN-002
implementation synchronized HEAD before claim: abb828dd9f42e510627474f3048426102d9c2938
recursive submodule sync/update/init: passed
database submodule: 2eb17ee910491e8f9df82736fc0a843844415947 (initialized; unchanged)
dependency gate: passed (ARCH-023-DATABASE-001 status complete)
claim executor: copilot
claimed_at: 2026-09-30T08:21:30Z
claim attempt: 2 (previous attempt 1)
claim commit: 7ab51b07850811b2388c716553a2d076fabf5828 (committed and pushed)
implementation commits: 00156c9 and 255a346 (pushed to origin/task/ARCH-023-ADMIN-002)
final implementation HEAD: 255a34651c8184683270493d082b956652c77898
```

### Attempt 1 Launcher Preparation Evidence (historical)

```text
canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-023-ADMIN-002
parent branch: task/ARCH-023-ADMIN-002
parent remote task-branch fast-forwarded: not-needed
parent origin/main incorporated: already-current
parent synchronized HEAD: de270f1b1526c60671f9731674cd6669c78861fb
implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-023-ADMIN-002
implementation branch: task/ARCH-023-ADMIN-002
implementation remote task-branch fast-forwarded: not-needed
implementation origin/main incorporated: already-current
implementation synchronized HEAD: abb828dd9f42e510627474f3048426102d9c2938
recursive submodule sync: passed
recursive submodule update/init: passed
recursive submodule status: ready
database submodule commit: 2eb17ee910491e8f9df82736fc0a843844415947 (initialized)
dependency gate: passed (ARCH-023-DATABASE-001 status complete)
claim executor: copilot
claimed_at: 2026-09-30T07:48:10Z
claim attempt: 1 (previous attempt 0)
claim commit: 81dbf731203bbbcde1e0b2472503ecfd218060f8 (committed and pushed)
```

### Attempt 1 Slug Immutability Conflict Evidence (resolved by Architect Review)

- At `database/prisma/migrations/20260923150000_arch021_agent_configuration/migration.sql`, `commerce.arch021_prompt_template_category_guard()` raises `ARCH021 category identity immutable` when `NEW.slug IS DISTINCT FROM OLD.slug` on any update.
- The trigger is installed for insert/update/delete on `commerce."CommercePromptTemplateCategory"`.
- The later `database/prisma/migrations/20260929160000_arch023_merchant_knowledge_schema/migration.sql` adds `defaultTemplateId`, taxonomy mappings, and profile references, but does not replace or relax the slug trigger.
- The authoritative initialized submodule commit is `2eb17ee910491e8f9df82736fc0a843844415947`.
- Requirement R5 explicitly requires an unused category slug rename to be allowed with CAS, and R14 requires a regression for that case. Application-layer count checks cannot make the database update succeed while the trigger remains unconditional.
- Attempted Admin source changes: none. Submodule gitlink staged: no.

## Architect Review

### Review Status

Accepted — Attempt 2

### Review Notes

#### Attempt 2 review — Accepted — 2026-09-30

Reviewed implementation `255a34651c8184683270493d082b956652c77898` and the submitted
parent report at `303db168` against the complete Attempt 1 correction contract and the
original ADMIN-002 acceptance criteria.

Attempt 2 is accepted.

The immutable Store Category identity correction is implemented end-to-end. Category
creation accepts the bounded canonical `slug`; category update parsing rejects any `slug`
field; the category mutation service never writes `slug`; and the editor presents the
persisted slug only as immutable identity. The existing ARCH-021 database category guard
is unchanged and remains the persistence backstop.

The protected `/system-controls/store-categories` surface is wired into the existing
Admin shell. Reads use the platform-admin page/read guards. Every mutation enters through
`requirePlatformAdminMutation()`, requires `SUPER_ADMIN`, provisions the durable
development admin only inside the mutation transaction, and executes in a Serializable
transaction.

The catalogue read model uses the required deterministic category/template/taxonomy
ordering, exposes only active/pending Shop Profile counts rather than complete Shop rows,
and provides the persisted taxonomy-suggestion inputs required by R13.

Category/default-template lifecycle rules conform: a new category cannot start enabled;
enabling requires an enabled, non-empty default template in the same category; default
selection locks/re-reads the category and applies edit-version CAS; disabling a category
does not rewrite Shop Profile rows; and an enabled category's current default template
cannot be disabled until another valid default is selected.

Prompt-template identity and CAS rules conform. `key` and `categoryId` are create-only,
`promptText` remains mutable bounded canonical-English content, stale writes are rejected,
and content-changing mutations emit exactly one `UPDATE_PROMPT_TEMPLATE_CONTENT` audit
with changed-field metadata. Category, template, default-template and taxonomy mutations
use the required existing audit actions without adding a new enum.

Taxonomy mappings support create, weight/category/Shopify-taxonomy-id update, move and
remove while retaining the database unique constraint as the authoritative duplicate-ID
backstop. No translation persistence, translation queue, merchant onboarding or Commerce
runtime behavior is introduced.

The Shopify localization warning is rendered unconditionally in the selected category
editor, so it remains visible for both enabled and disabled categories as required by the
Attempt 2 handoff. Admin does not attempt to inspect source-controlled Shopify locale
catalogues at runtime.

The returned task file left the nine Work Items unchecked even though the Acceptance
Criteria, Validation section, Completion Report and inspected source show those items are
complete. This is stale coordination state rather than missing implementation. The
architect reconciliation therefore marks those Work Items complete instead of forcing a
code-less Attempt 3. The database-gitlink item is satisfied by the recorded initialized
accepted DATABASE-001 commit; no gitlink advance was necessary in this attempt.

The review archive intentionally omits Git metadata. The Completion Report nevertheless
records the launcher-resolved dedicated parent and implementation worktrees, matching task
branches, Attempt 2 synchronization/claim evidence, recursive submodule preparation,
pushed implementation commits and clean handoff. The archive limitation therefore does
not block cross-environment review.

### Reviewed Files

Implementation repository:

- `src/app/(protected)/system-controls/store-categories/page.tsx`
- `src/app/actions/store-categories.ts`
- `src/components/admin/admin-shell.tsx`
- `src/components/admin/sidebar.tsx`
- `src/components/admin/store-categories/store-category-catalog.tsx`
- `src/components/admin/store-categories/store-category-editor.tsx`
- `src/components/admin/store-categories/prompt-template-editor.tsx`
- `src/components/admin/store-categories/taxonomy-mapping-editor.tsx`
- `src/lib/admin/store-categories.ts`
- `src/lib/admin/store-category-validation.ts`
- `tests/unit/store-categories.test.ts`
- `tests/unit/store-category-actions.test.ts`
- `tests/unit/store-category-validation.test.ts`
- `tests/security/admin-store-categories.test.mjs`
- `tests/security/admin-sidebar-navigation.test.mjs`
- `database/prisma/schema.prisma`
- `database/prisma/migrations/20260923150000_arch021_agent_configuration/migration.sql`
- `database/prisma/migrations/20260929160000_arch023_merchant_knowledge_schema/migration.sql`

Parent workspace:

- `docs/decisions/admin/ARCH-023/ADMIN-002-manage-store-categories-default-templates.md`
- `docs/decisions/admin/ARCH-023/ADMIN-003-author-platform-shop-instructions.md`
- `docs/decisions/admin/ARCH-023/_index.md`
- `docs/decisions/database/ARCH-023/_index.md`
- `docs/architecture/ARCH-023-merchant-knowledge.md`

### Validation Reviewed

- Independently re-ran the three focused unit/action/validation files: **23/23 passed**.
- Independently re-ran the focused Store Categories security test plus Admin sidebar
  navigation test: **8/8 passed**.
- Confirmed the update parser rejects `slug`, template `key` and `categoryId` identity
  changes and the mutation service does not write those identities.
- Confirmed the existing ARCH-021 category trigger still rejects any `slug` update and the
  accepted ARCH-023 migration does not replace or relax that trigger.
- Confirmed the localization-key warning is unconditional in the category editor rather
  than gated on `category.enabled`.
- Inspected the recorded TypeScript pass, changed-file ESLint pass, production build pass,
  `git diff --check` pass, 23 focused unit tests and 8 focused security/navigation checks.
- The review archive does not contain installed `node_modules`, so TypeScript, ESLint and
  the production build were not independently re-run in the review container. Their
  recorded results and the generated build/typecheck evidence were inspected instead.
- The reported broad-suite failures are outside the task-owned Store Categories paths and
  were recorded by the implementing agent as existing and unrelated. They are not treated as new ARCH-023 baseline entries;
  no inspected ADMIN-002 change couples to those failing merchant-pricing, billing,
  promotions or legacy security assertions.

### Architecture Conformance

Conforms. ADMIN-002 remains an Admin-owned catalogue/authoring boundary over the accepted
ARCH-023 persistence model. Store Category `slug` is stable localization identity,
canonical-English template content stays Admin-owned, source-controlled Shopify locale
catalogues remain outside Admin persistence, and no new cross-repository runtime contract,
queue, schema migration or Commerce execution behavior was introduced.

The implementation preserves tenant/security boundaries: catalogue mutation remains
SUPER_ADMIN-only and Shop Profile data is observed only as aggregate reference counts.
The task does not weaken the database category-identity guard or create a second identity
mutability rule.

### Follow-up

`ARCH-023-ADMIN-002` is **Complete / Accepted at Attempt 2**.

Dependency reconciliation makes exactly this newly satisfied dependant Ready:

```text
ARCH-023-ADMIN-003
```

`ARCH-023-SHARED-001` remains independently Ready from DATABASE-001 acceptance. All other
ARCH-023 implementation/system-test tasks remain Pending/Superseded according to their
declared dependencies. No downstream implementation is started implicitly by this
review.

#### Historical Attempt 1 — Changes Requested — 2026-09-30

##### Review Notes

The repository agent correctly stopped before implementation. The submitted blocker is
real: the existing database guard rejects every `CommercePromptTemplateCategory.slug`
change, while the Attempt 1 ADMIN-002 R5/R14 text incorrectly required an unused slug
rename to succeed.

The conflict is resolved by correcting ADMIN-002 rather than weakening the database
guard. ARCH-021 established category `id/slug` as immutable after INSERT and the existing
category-authoring surface treated the slug as stable identity rather than mutable display
metadata. ARCH-023 D9 also defines the slug as the stable merchant-facing localization
identity and requires a different semantic category identity to use a new category/slug.
The conditional unused-slug rename rule was therefore an over-permissive task-level drift
from the durable identity contract.

The authoritative Attempt 2 correction contract is now:

1. `slug` is accepted only when a category is created.
2. Category update input contains only mutable display/order/enabled metadata plus
   `expectedEditVersion` and `reason`; it does not accept `slug`.
3. Admin does not render or implement a slug-rename mutation path.
4. `activeShopProfiles` / `pendingShopProfiles` counts remain part of the read model, but
   they do not make slug identity mutable.
5. The existing database category-identity guard remains unchanged and MUST NOT be
   bypassed or edited by ADMIN-002.
6. The regression requirement is to prove the Admin update contract cannot rename a slug,
   including for an otherwise unused category.

No Admin implementation defect is recorded for Attempt 1 because no implementation was
started. No database correction task is required.

##### Reviewed Files

- `docs/decisions/admin/ARCH-023/ADMIN-002-manage-store-categories-default-templates.md`
- `docs/decisions/admin/ARCH-023/_index.md`
- `docs/architecture/ARCH-023-merchant-knowledge.md`
- `docs/decisions/database/ARCH-021/DATABASE-001-persist-agent-configuration-schema.md`
- `docs/decisions/commerce/ARCH-021/COMMERCE-013-build-platform-prompt-template-ui.md`
- `moda-interact-admin/database/prisma/schema.prisma`
- `moda-interact-admin/database/prisma/migrations/20260923150000_arch021_agent_configuration/migration.sql`
- `moda-interact-admin/database/prisma/migrations/20260929160000_arch023_merchant_knowledge_schema/migration.sql`

##### Validation Reviewed

- Confirmed the ARCH-021 migration guard raises `ARCH021 category identity immutable`
  whenever `NEW.slug IS DISTINCT FROM OLD.slug`.
- Confirmed the accepted ARCH-023 migration does not replace or relax that guard.
- Confirmed ARCH-021's database contract explicitly made category `id/slug` immutable
  after INSERT.
- Confirmed the existing ARCH-021 category-authoring task treated the slug as stable
  identity and did not expose it as renameable metadata.
- Confirmed ARCH-023 D9 defines `slug` as the stable merchant-facing localization identity
  and uses a new category/slug for an identity change.
- Reviewed the submitted launcher/claim evidence and the recorded clean unchanged Admin
  implementation worktree.
- Reviewed the recorded parent `git diff --check` pass. Feature validation was correctly
  not run because Attempt 1 stopped before implementation.

##### Architecture Conformance

The database behavior is architecture-conformant and remains unchanged. The inconsistent
piece was ADMIN-002's conditional slug-mutability requirement. Correcting R4/R5/R14
restores the stable identity contract without introducing a new migration, trigger, raw
SQL bypass or cross-repository implementation dependency.

##### Follow-up

`ARCH-023-ADMIN-002` returns to **Ready** for Attempt 2 with `attempt: 1` preserved and no
active executor/claim. The next normal claim increments it to Attempt 2.

Attempt 2 must implement the full ADMIN-002 scope against the corrected immutable-slug
contract and then return the same task for Architect Review. `ARCH-023-DATABASE-001`
remains **Complete / Accepted at Attempt 2**. `ARCH-023-ADMIN-003` remains Pending until
ADMIN-002 is accepted Complete.
