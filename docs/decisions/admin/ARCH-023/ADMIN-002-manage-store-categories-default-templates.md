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
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-DATABASE-001
enables:
  - ARCH-023-ADMIN-003
created: 2026-09-29
updated: 2026-09-29
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

Create/update category fields:

```text
slug         1..128, regex /^[a-z][a-z0-9-]{0,127}$/
displayName  trimmed 1..255
description  trimmed 0..2000
displayOrder integer 0..1_000_000
enabled      boolean
expectedEditVersion positive integer on update
reason       trimmed 1..1000
```

Create initializes:

```text
editVersion = 1
```

Update uses CAS:

```text
WHERE id = ? AND editVersion = expectedEditVersion
editVersion += 1
```

CAS miss returns a bounded stale-write error.

### R5 — category slug stability

Slug can be changed only when both are zero:

```text
activeShopProfiles
pendingShopProfiles
```

If either relation exists, reject slug change:

```text
An in-use Store Category slug is immutable.
```

Changing merchant-facing wording uses Shopify locale files; it does not require changing the slug.

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
in-use slug rename rejected
unused slug rename allowed with CAS
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

- [ ] Adopt database gitlink.
- [ ] Add protected Store Categories route/navigation.
- [ ] Add category/template/taxonomy read model.
- [ ] Add SUPER_ADMIN server actions with CAS.
- [ ] Add exact default-template/enable invariants.
- [ ] Add category/template/taxonomy UI.
- [ ] Add exact audit events.
- [ ] Add focused security/validation/UI tests.
- [ ] Confirm no translation persistence/queue is introduced.

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

- [ ] Admin has one authoritative Store Category management surface.
- [ ] Category/default-template invariants are enforced server-side.
- [ ] Category slug stability respects active/pending profile references.
- [ ] Templates remain mutable current records with editVersion CAS; no revision table reappears.
- [ ] Shopify taxonomy mappings are managed deterministically.
- [ ] No category/template translation database or queue behavior exists.
- [ ] Existing Admin auth/audit conventions are preserved.
- [ ] No Shopify/Commerce runtime implementation is introduced.

## Validation

- [ ] focused category/template/action tests
- [ ] Admin security regressions
- [ ] `npm run test:unit`
- [ ] `npm run lint`
- [ ] `npm run build`
- [ ] `git diff --check`
- [ ] changed-file diagnostics clean

## Stop Condition

Set status to `review`, complete Completion Report, return to `moda_architect` and STOP. Do not begin ADMIN-003.

## Completion Report

### Status
Not Started
### Files Changed
None.
### Work Completed
None.
### Validation Results
None.
### Deviations
None.
### Assumptions
None.
### Unresolved Issues
None.
### Architectural Concerns
None.

## Architect Review

### Review Status
Pending
### Review Notes
Pending.
### Reviewed Files
Pending.
### Validation Reviewed
Pending.
### Architecture Conformance
Pending.
### Follow-up
Pending.
