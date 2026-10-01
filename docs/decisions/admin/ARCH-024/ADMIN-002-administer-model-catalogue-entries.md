---
id: ARCH-024-ADMIN-002
architecture_id: ARCH-024
title: Administer Commerce model catalogue entries
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 31
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-024-DATABASE-001
  - ARCH-024-SHARED-002
  - ARCH-024-ADMIN-001
enables:
  - ARCH-024-COMMERCE-003
  - ARCH-024-ADMIN-003
created: 2026-09-30
updated: 2026-10-01
---

# Administer Commerce model catalogue entries

## Architecture

Architecture ID:

`ARCH-024`

Architecture document:

`docs/architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md`

Coordinator:

`moda_architect`

## Objective

Add the Admin control-plane surface for creating, viewing, editing, enabling/disabling and reassigning ARCH-024 `CommerceModelCatalogueEntry` records beneath existing Platform/Shop `CommerceModelAvailability` scopes.

The completed Admin behaviour must preserve these exact ownership boundaries:

```text
Admin
    owns Model Availability
    owns Model Catalogue entry creation and lifecycle
    owns assignment/reassignment of a Catalogue Entry to one Availability

Commerce Studio
    does NOT create/edit/enable/disable Catalogue Entries
    later selects one active model only from the effective available set

Merchant
    does not administer or select models
```

Every Catalogue Entry belongs to exactly one Availability. `provider + providerModelId` is immutable model identity. `availabilityId`, display metadata and validated OpenRouter configuration are mutable under optimistic concurrency control. There is no delete operation.

## Context

`ARCH-024-DATABASE-001` establishes this durable shape:

```text
CommerceModelAvailability
        1
        |
        *
CommerceModelCatalogueEntry
```

with the Catalogue Entry fields:

```text
id
availabilityId
provider
providerModelId
displayName
description
configurationSchemaVersion
configuration
enabled
editVersion
createdByAdminId
updatedByAdminId
createdAt
updatedAt
```

and database identity/lifecycle rules:

```text
immutable:
    id
    provider
    providerModelId

mutable:
    availabilityId
    displayName
    description
    configurationSchemaVersion
    configuration
    enabled
    editVersion
    updatedByAdminId
    updatedAt

DELETE:
    rejected
```

Scoped uniqueness is exactly:

```text
UNIQUE(availabilityId, provider, providerModelId)
```

Therefore the same OpenRouter model identity may intentionally exist as separately configured Catalogue Entries under different Availability scopes, but it may occur only once within a single Availability.

`ARCH-024-SHARED-001` defines the canonical model contracts and `ARCH-024-SHARED-002` publishes the combined accepted package from:

```text
@modainteract/moda-interact-shared/commerce/model
```

including:

```text
CommerceModelAvailabilitySchema
CommerceModelAvailability
CommerceModelCatalogueEntrySchema
CommerceModelCatalogueEntry
CommerceModelProviderSchema
CommerceProviderModelIdSchema
CommerceModelConfigurationSchema
COMMERCE_MODEL_CONFIGURATION_SCHEMA_VERSION
createOpenRouterModelId
```

The persisted `configuration` object uses direct OpenRouter-style request-option semantics. It is intentionally extensible. Admin MUST NOT build its own provider-option allowlist. It MUST parse the JSON and validate it using the exact Shared `CommerceModelConfigurationSchema`, including the Shared size/depth/node bounds and the Shared reserved-runtime-key restrictions.

For example, this is a valid configuration shape when accepted by the published Shared schema:

```json
{
  "temperature": 0.2,
  "top_p": 0.9,
  "reasoning": {
    "effort": "high"
  },
  "provider": {
    "allow_fallbacks": true,
    "sort": "latency",
    "data_collection": "deny",
    "require_parameters": true
  }
}
```

Admin stores this object as JSON. It MUST NOT translate it to LangChain-specific `modelKwargs`, `openrouter_provider`, or other runtime implementation details. Shared/Commerce own that translation.

`ARCH-024-ADMIN-001` establishes:

```text
/commerce-models/availability

Commerce models
    Availability
```

and the canonical Admin read/security patterns for the new Model administration area. This task extends that area with Catalogue management; it does not replace the Availability surface.

## Scope

Primary implementation targets:

```text
moda-interact-admin/src/app/(protected)/commerce-models/catalogue/page.tsx
moda-interact-admin/src/app/actions/model-catalogue.ts
moda-interact-admin/src/lib/admin/model-catalogue.ts
moda-interact-admin/src/lib/admin/model-catalogue-validation.ts
moda-interact-admin/src/components/admin/model-catalogue/model-catalogue-table.tsx
moda-interact-admin/src/components/admin/model-catalogue/model-catalogue-editor.tsx
moda-interact-admin/src/components/admin/model-catalogue/model-catalogue-mutation-form.tsx
moda-interact-admin/src/components/admin/sidebar.tsx
moda-interact-admin/src/components/admin/admin-shell.tsx

moda-interact-admin/tests/unit/model-catalogue-validation.test.ts
moda-interact-admin/tests/unit/model-catalogue-service.test.ts
moda-interact-admin/tests/security/admin-model-catalogue.test.mjs
moda-interact-admin/tests/security/admin-sidebar-navigation.test.mjs

moda-interact-admin/package.json
moda-interact-admin/package-lock.json
```

The nested Admin `database/` submodule/gitlink may move only to the architect-accepted `ARCH-024-DATABASE-001` database commit required by this task.

Additional Admin files may be changed only when required to integrate this exact Catalogue surface or keep focused validation/build green. Every additional file MUST be named and justified in the Completion Report.

Do not modify the database schema/migration inside this task.

## Out of Scope

- Creating/editing `CommerceModelAvailability`; `ARCH-024-ADMIN-001` owns Availability lifecycle.
- Deleting a Model Availability.
- OpenRouter credential administration; `ARCH-024-ADMIN-003` owns it.
- Agent model selection.
- Merchant Pricing Plan -> model association; `ARCH-024-ADMIN-004` owns that product-tier configuration.
- Commerce Studio changes.
- Test Conversation changes.
- Background runtime changes.
- Merchant-facing model selection; merchants do not select models under ARCH-024.
- Calling OpenRouter.
- Calling LangChain.
- Discovering or synchronising OpenRouter's public model catalogue.
- Automatically creating one Catalogue Entry per OpenRouter model.
- Automatically creating Shop Catalogue Entries from Platform entries.
- Duplicating one Catalogue Entry into another Availability during reassignment. Reassignment updates the existing entry's `availabilityId` and preserves its `id`.
- Changing `provider` or `providerModelId` after creation.
- Adding an `openRouterModelId` database column. Runtime identity remains `provider + '/' + providerModelId`.
- Adding credentials, API keys, headers, endpoint/base-URL fields or secrets to Catalogue Entry forms/configuration.
- Adding a delete action for Catalogue Entries.
- Preventing Admin from disabling/reassigning a model merely because Agent Configuration currently references it. Broken explicit selections remain durable and later Commerce resolution fails closed as `UNAVAILABLE`.
- Automatically clearing/changing `CommerceAgentConfiguration.modelId`.
- Interpreting unknown non-reserved OpenRouter configuration options in Admin.
- Creating a second local model/configuration contract instead of consuming Shared.

## Requirements

### R1 — Consume accepted Database, Shared and Availability dependencies first

Before implementation:

1. synchronize the nested `database/` submodule to the architect-accepted `ARCH-024-DATABASE-001` implementation;
2. update `@modainteract/moda-interact-shared` to the exact version published and architect-accepted by `ARCH-024-SHARED-002`;
3. confirm `ARCH-024-ADMIN-001` is architect-accepted Complete and retain its `/commerce-models/availability` route and navigation behaviour;
4. regenerate Prisma using the repository command:

```bash
npm run prisma:generate
```

5. validate Prisma using:

```bash
npm run prisma:validate
```

Admin MUST import the canonical model contracts from:

```text
@modainteract/moda-interact-shared/commerce/model
```

At minimum consume:

```ts
CommerceModelAvailabilitySchema
CommerceModelAvailability
CommerceModelCatalogueEntrySchema
CommerceModelCatalogueEntry
CommerceModelProviderSchema
CommerceProviderModelIdSchema
CommerceModelConfigurationSchema
COMMERCE_MODEL_CONFIGURATION_SCHEMA_VERSION
createOpenRouterModelId
```

Do not recreate those schemas locally.

### R2 — Extend the Admin navigation exactly

Add the protected Admin route:

```text
/commerce-models/catalogue
```

Extend `AdminShell` and `Sidebar` with the active key:

```text
model-catalogue
```

After this task the existing `Commerce models` sidebar group MUST contain exactly these implemented destinations:

```text
Commerce models
    Availability  -> /commerce-models/availability
    Catalogue     -> /commerce-models/catalogue
```

Do NOT add a Credential link yet; `ARCH-024-ADMIN-003` owns that destination.

The group remains visible to authenticated Platform Admin readers. Mutation controls remain SUPER_ADMIN-only.

Update `tests/security/admin-sidebar-navigation.test.mjs` to prove:

1. `Commerce models` remains present;
2. `/commerce-models/availability` remains present;
3. `/commerce-models/catalogue` is present;
4. `AdminShell` accepts `model-catalogue`;
5. the Catalogue page renders `<AdminShell active="model-catalogue">`;
6. no `/commerce-models/credentials` link is introduced by this task.

### R3 — Protect page, reads and every mutation independently

The page MUST call:

```ts
await requirePlatformAdminPage();
```

Every read service MUST independently call:

```ts
await requirePlatformAdminRead();
```

Every mutation Server Action MUST call:

```ts
const principal = await requirePlatformAdminMutation();
if (principal.role !== "SUPER_ADMIN") {
  throw new Error("SUPER_ADMIN access is required.");
}
```

Every mutation transaction MUST call:

```ts
await ensureDevelopmentPlatformAdmin(transaction, principal);
```

before writing Admin-owned provenance/audit rows when the development bypass principal is active.

Do not rely on hidden buttons or page authorization as the mutation security boundary.

### R4 — Define the Admin Catalogue read model exactly

Create these Admin-local presentation types. They may compose Shared types but MUST NOT redefine their runtime semantics:

```ts
export type ModelCatalogueAvailabilityOption = {
  availability: CommerceModelAvailability;
  label: string;
  shopDomain: string | null;
};

export type ModelCatalogueAdminRow = {
  model: CommerceModelCatalogueEntry;
  availability: CommerceModelAvailability;
  availabilityLabel: string;
  shopDomain: string | null;
  selectionCount: number;
};

export type ModelCatalogueStatusFilter = "all" | "enabled" | "disabled";

export type ModelCatalogueAdminPage = {
  rows: ModelCatalogueAdminRow[];
  availabilities: ModelCatalogueAvailabilityOption[];
  page: number;
  pageSize: 50;
  total: number;
};
```

Create:

```ts
export async function getModelCatalogueAdminPage(input: {
  availabilityId?: string;
  query?: string;
  status?: ModelCatalogueStatusFilter;
  page?: number;
}): Promise<ModelCatalogueAdminPage>;
```

Exact read behaviour:

1. call `requirePlatformAdminRead()`;
2. normalize `page` to an integer `>= 1`, default `1`;
3. use exact `pageSize = 50`;
4. trim `query`; empty string means no text filter;
5. if non-empty, `query` may be at most 128 characters or reject it;
6. `status` defaults to `all` and accepts only `all | enabled | disabled`;
7. if `availabilityId` is supplied, require that exact Availability to exist; otherwise reject with `Model Availability not found.`;
8. search `displayName`, `provider` and `providerModelId` case-insensitively;
9. read Catalogue rows using server-side filters and pagination; do not load the whole Catalogue and filter in the browser;
10. include only Availability fields required by `CommerceModelAvailabilitySchema`, plus Shop `domain` for presentation;
11. include `_count.configurations` only to derive `selectionCount`; do not load Agent Configuration records;
12. validate every Availability with `CommerceModelAvailabilitySchema`;
13. validate every Catalogue Entry with `CommerceModelCatalogueEntrySchema` before returning it;
14. return all Availability options so Create/Edit can target any existing Platform/Shop Availability, including a disabled Availability;
15. Availability labels are exactly:

```text
Platform
Shop · <shop.domain>
```

16. append ` · Disabled` to the label when that Availability is disabled;
17. order Availability options:

```text
PLATFORM first
then SHOP by shop.domain ASC (case-insensitive)
then shopId ASC
then availability.id ASC
```

18. order Catalogue rows deterministically:

```text
availability.scope: PLATFORM before SHOP
shop.domain ASC case-insensitive, null first
model.displayName ASC case-insensitive
model.provider ASC
model.providerModelId ASC
model.id ASC
```

If the Prisma query cannot express the case-insensitive ordering deterministically, use a bounded server-side post-sort **only on the 50 returned page rows**. Do not load the entire table to sort it.

### R5 — Add one canonical form parser for create/edit input

Create an Admin-local form/input parser in `model-catalogue-validation.ts` that produces the canonical Shared-compatible values.

Create input fields exactly:

```text
availabilityId
provider
providerModelId
displayName
description
configuration
```

where `configuration` arrives from the form as JSON text.

Create this parsed shape:

```ts
export type ParsedModelCatalogueInput = {
  availabilityId: string;
  provider: string;
  providerModelId: string;
  displayName: string;
  description: string;
  configurationSchemaVersion: typeof COMMERCE_MODEL_CONFIGURATION_SCHEMA_VERSION;
  configuration: CommerceModelConfiguration;
};
```

Validation is exact:

1. `availabilityId`: trimmed non-empty string, maximum 128 characters;
2. `provider`: trim, then validate with `CommerceModelProviderSchema`; do not silently lower-case invalid input;
3. `providerModelId`: trim, then validate with `CommerceProviderModelIdSchema`;
4. `displayName`: trim, 1..160 characters to match the Shared contract;
5. `description`: trim, 0..2000 characters to match the Shared contract;
6. `configuration`: must be syntactically valid JSON;
7. parsed configuration must validate with `CommerceModelConfigurationSchema`;
8. `configurationSchemaVersion` is always set by the server to exactly `COMMERCE_MODEL_CONFIGURATION_SCHEMA_VERSION`; it is not an editable form field;
9. validate the derived OpenRouter ID using:

```ts
createOpenRouterModelId({ provider, providerModelId })
```

10. never accept these as separate form fields:

```text
openRouterModelId
credential
apiKey
headers
baseUrl
model
messages
tools
tool_choice
```

The Shared configuration validator remains authoritative for reserved runtime/security keys and JSON size/depth/node bounds. Do not duplicate those rules in a second Admin allowlist.

Use bounded public form errors. Do not echo the full configuration JSON into thrown error messages.

### R6 — Create Catalogue Entries exactly

Create one Server Action intent for creation:

```text
intent = create
```

Required form inputs:

```text
availabilityId
provider
providerModelId
displayName
description
configuration
```

Creation semantics:

1. authorize mutation according to R3;
2. parse through the one canonical R5 parser;
3. open a Prisma transaction;
4. call `ensureDevelopmentPlatformAdmin(transaction, principal)`;
5. require the target `CommerceModelAvailability.id` to exist;
6. validate the target Availability with `CommerceModelAvailabilitySchema`;
7. do **not** require the Availability to be enabled; Admin may stage models beneath a disabled Availability;
8. create exactly one `CommerceModelCatalogueEntry` with:

```text
availabilityId             = parsed availabilityId
provider                   = parsed provider
providerModelId            = parsed providerModelId
displayName                = parsed displayName
description                = parsed description
configurationSchemaVersion = COMMERCE_MODEL_CONFIGURATION_SCHEMA_VERSION
configuration              = parsed validated JSON object
enabled                    = true
editVersion                = 1
createdByAdminId           = principal.id
updatedByAdminId           = principal.id
```

9. validate the created row through `CommerceModelCatalogueEntrySchema` before returning/using it outside the transaction;
10. create `CommerceAuditEvent` using existing action:

```text
CREATE_MODEL_CATALOGUE_ENTRY
```

with:

```text
actorAdminId          = principal.id
modelCatalogueEntryId = created entry id
modelAvailabilityId   = target Availability id
reason                = "Created Commerce model catalogue entry <provider>/<providerModelId>"
metadata = {
  provider,
  providerModelId,
  availabilityId,
  enabled: true,
  configurationSchemaVersion
}
```

Do NOT copy the full `configuration` JSON into audit metadata.

11. revalidate `/commerce-models/catalogue` and `/commerce-models/availability` because model counts on Availability may change.

If `(availabilityId, provider, providerModelId)` conflicts with an existing row, return exactly:

```text
A model with this provider and model ID already exists in the selected availability.
```

Do not implement create-as-upsert.

### R7 — Provider and providerModelId are immutable after creation

Edit UI MUST display these values as read-only identity:

```text
Provider
Provider model ID
OpenRouter model ID = provider + '/' + providerModelId
```

The update action MUST NOT accept new `provider` or `providerModelId` values.

The only way to represent a genuinely different model identity is to create a new Catalogue Entry.

Do not work around the database `arch024_model_catalogue_guard`.

### R8 — Update metadata, configuration and Availability assignment under CAS

Create one update intent:

```text
intent = update
```

Required inputs:

```text
id
expectedEditVersion
availabilityId
displayName
description
configuration
```

The server MUST load the existing row first to obtain immutable `provider + providerModelId`, then combine those immutable values with the mutable form input and run the same Shared validation used for creation.

Update semantics:

1. authorize according to R3;
2. validate `id` non-empty/max 128 and `expectedEditVersion` positive integer;
3. load the existing Catalogue Entry; missing -> `Model catalogue entry not found.`;
4. require `existing.editVersion === expectedEditVersion`; otherwise -> `Model catalogue entry changed. Refresh and try again.`;
5. require target Availability to exist and validate it with Shared;
6. allow target Availability to be enabled or disabled;
7. perform the row mutation with a CAS predicate on both `id` and `editVersion` using `updateMany` or an equivalent one-row conditional update;
8. if the CAS update count is not exactly `1`, throw `Model catalogue entry changed. Refresh and try again.`;
9. update only:

```text
availabilityId
displayName
description
configurationSchemaVersion = current Shared version
configuration
editVersion = expectedEditVersion + 1
updatedByAdminId = principal.id
updatedAt = database/application current time via normal Prisma semantics
```

10. never update `provider` or `providerModelId`;
11. emit `UPDATE_MODEL_CATALOGUE_ENTRY` with `modelCatalogueEntryId`, the **new** `modelAvailabilityId`, bounded reason, and metadata containing only changed administrative identifiers/flags/schema version, not full configuration;
12. if `availabilityId` changed, additionally emit:

```text
ASSIGN_MODEL_CATALOGUE_ENTRY_AVAILABILITY
```

with:

```text
modelCatalogueEntryId = entry id
modelAvailabilityId   = new Availability id
metadata = {
  previousAvailabilityId,
  newAvailabilityId
}
```

13. moving an entry MUST preserve its entry `id`;
14. do not duplicate/copy the entry into the target Availability;
15. do not update/clear Agent Configuration references even when the move makes a current explicit selection invalid;
16. revalidate `/commerce-models/catalogue` and `/commerce-models/availability`.

If scoped uniqueness conflicts in the target Availability, return the exact duplicate message from R6.

### R9 — Enable/disable Catalogue Entries under CAS

Create one mutation intent:

```text
intent = set-enabled
```

Required inputs:

```text
id
expectedEditVersion
enabled = "true" | "false"
```

Exact behaviour:

1. authorize according to R3;
2. load the entry; missing -> `Model catalogue entry not found.`;
3. validate the row with `CommerceModelCatalogueEntrySchema`;
4. require current `editVersion` to equal `expectedEditVersion`; otherwise use the R8 CAS error;
5. if current `enabled` already equals requested `enabled`, reject with:

```text
Model catalogue entry is already enabled.
```

or:

```text
Model catalogue entry is already disabled.
```

6. update under the same CAS rule;
7. change only:

```text
enabled
editVersion = expectedEditVersion + 1
updatedByAdminId = principal.id
```

8. write exactly one corresponding audit action:

```text
ENABLE_MODEL_CATALOGUE_ENTRY
```

or:

```text
DISABLE_MODEL_CATALOGUE_ENTRY
```

with both `modelCatalogueEntryId` and current `modelAvailabilityId` populated;
9. do not block disable because `selectionCount > 0`;
10. do not clear Agent Configuration;
11. revalidate Catalogue and Availability routes.

There is no DELETE action.

### R10 — Reassignment is allowed and must visibly warn about existing selections

The Edit drawer MUST include an Availability selector containing all existing Platform/Shop Availability options from R4.

When `selectionCount > 0`, render this exact warning near the Availability control:

```text
This model is selected by one or more Agent Configurations. Changing its availability or disabling it may make those selections unavailable until corrected in Commerce Studio.
```

The warning is informational only. It MUST NOT block reassignment or disable.

This preserves the ARCH-024 rule:

```text
Admin may change eligibility
    -> existing explicit Agent selection remains durable
    -> Commerce later resolves it UNAVAILABLE if no longer valid
    -> operator fixes or clears the selection deliberately in Commerce Studio
```

### R11 — Configuration editing is direct OpenRouter-style JSON

The Create/Edit drawer MUST provide one labelled JSON textarea:

```text
OpenRouter configuration
```

Create default text:

```json
{}
```

Edit text MUST be rendered from the stored object using:

```ts
JSON.stringify(configuration, null, 2)
```

The UI MAY provide descriptive helper text and an example, but it MUST NOT:

- maintain an allowlist of OpenRouter options;
- transform the JSON into Moda `parameters` / `routing` wrappers;
- transform the JSON into LangChain `modelKwargs` or `openrouter_provider` fields;
- add a credential/API-key field;
- silently delete unknown non-reserved properties;
- silently rewrite reserved fields rather than rejecting them through Shared validation.

The exact helper text MUST communicate:

```text
Configuration uses OpenRouter request-option field names. Unknown non-reserved OpenRouter options are preserved. Model identity, messages, tools, token budget, credentials, headers and base URL are controlled by Moda and cannot be configured here.
```

Do not display the 32-KiB JSON limit as a browser `maxLength` because the Shared limit is canonical serialized UTF-8 bytes, not JavaScript string length. Server validation remains authoritative.

### R12 — Render the Catalogue page exactly as an Admin control plane

Page heading:

```text
Model catalogue
```

Introductory copy must communicate:

```text
Create and configure the models that Moda can make available to Platform and individual Shops. Commerce Studio selects from this Admin-managed catalogue; it does not create models.
```

Render server-side filters:

```text
Search
Availability
Status
```

Search placeholder:

```text
Search model name, provider or model ID
```

Status options:

```text
All
Enabled
Disabled
```

Catalogue table columns exactly:

```text
Model
OpenRouter model ID
Availability
Status
Configuration
Selections
Actions
```

Column behaviour:

```text
Model
    displayName
    optional description second line

OpenRouter model ID
    createOpenRouterModelId({ provider, providerModelId })

Availability
    Platform
    or Shop · <domain>
    append · Disabled when Availability disabled

Status
    Enabled | Disabled

Configuration
    "Default" when configuration is {}
    otherwise "Configured"
    do not render full JSON in the table

Selections
    selectionCount decimal integer

Actions
    Edit link/drawer for SUPER_ADMIN
    View link/drawer for PLATFORM_ADMIN
```

A SUPER_ADMIN sees:

```text
Create model
```

A non-SUPER_ADMIN does not see mutation controls but can inspect entries and configuration read-only.

When there are no rows after filtering, render:

```text
No model catalogue entries match the current filters.
```

### R13 — Create/Edit drawers are deterministic

Create drawer fields in exact order:

```text
Availability
Provider
Provider model ID
OpenRouter model ID preview (read-only derived display)
Display name
Description
OpenRouter configuration
Create model
```

The derived OpenRouter ID preview is display-only. It MUST NOT be posted as authoritative input.

Edit drawer fields in exact order:

```text
Provider                    read-only
Provider model ID           read-only
OpenRouter model ID         read-only derived
Availability                editable
Display name                editable
Description                 editable
OpenRouter configuration    editable
Selections                  read-only count
Save changes
Enable / Disable            separate mutation control
```

Do not combine Enable/Disable state into `Save changes`; lifecycle mutation remains a separate audited CAS operation.

### R14 — No same-tick duplicate Admin mutation dispatch

Create `model-catalogue-mutation-form.tsx` as the single client-side form wrapper used by Create, Update and Enable/Disable controls.

Required behaviour:

```text
first submit
    -> synchronously acquire a ref-based in-flight gate
    -> allow one Server Action dispatch
    -> render pending/disabled control state

second click / Enter / requestSubmit in same tick while gate held
    -> prevent another dispatch
```

Release the local gate when the action settles and the form remains mounted.

The client gate is UX/re-entry protection only. Database uniqueness and CAS remain the correctness boundaries.

Do not generate a second mutation path or client-side Prisma/API endpoint.

### R15 — Audit metadata must remain bounded and secret-safe

Catalogue audit events MUST NOT contain:

```text
full configuration JSON
OpenRouter credential
API key
Authorization header
provider response
Shopify credential
```

Allowed model audit metadata is limited to identifiers and bounded administrative state such as:

```text
provider
providerModelId
availabilityId
previousAvailabilityId
newAvailabilityId
enabled
configurationSchemaVersion
```

Use `modelCatalogueEntryId` and `modelAvailabilityId` target columns rather than encoding target identity only in free-form metadata.

### R16 — Error mapping is deterministic

At minimum expose these bounded public errors exactly:

```text
SUPER_ADMIN access is required.
Model Availability not found.
Model catalogue entry not found.
Model catalogue entry changed. Refresh and try again.
A model with this provider and model ID already exists in the selected availability.
Model catalogue entry is already enabled.
Model catalogue entry is already disabled.
Model configuration must be valid JSON.
Model configuration is invalid.
```

Shared/Zod validation details may be mapped to a more specific bounded field error when useful, but MUST NOT echo arbitrary configuration contents or stack traces.

Unexpected failures propagate to the normal Admin error boundary/logging path without secret values.

### R17 — Focused tests are mandatory

Add unit coverage proving at minimum:

#### Validation

1. valid provider/providerModelId passes Shared schemas;
2. uppercase/invalid provider is rejected rather than silently lower-cased;
3. providerModelId containing whitespace is rejected;
4. providerModelId containing `/` is rejected;
5. valid `{}` configuration passes;
6. valid nested OpenRouter-style configuration passes;
7. unknown non-reserved OpenRouter option survives parsing unchanged;
8. reserved runtime/security field is rejected through Shared validation;
9. invalid JSON gets the exact bounded invalid-JSON error;
10. configuration schema version comes from Shared constant, not form input;
11. display-name and description bounds are enforced.

#### Read/service behaviour

12. read requires Platform Admin authorization;
13. page size is exactly 50;
14. availability/status/query filters are server-side;
15. all Availability options are available for Create/Edit, including disabled ones;
16. Platform labels and Shop labels follow R4;
17. model and Availability rows are validated through Shared schemas;
18. selectionCount uses Agent Configuration count only and does not load configurations.

#### Mutation behaviour

19. non-SUPER_ADMIN mutation is rejected server-side;
20. development bypass mutation materialises the reserved development PlatformAdmin before provenance/audit writes;
21. create writes configuration version 1, `enabled=true`, editVersion 1 and Admin provenance;
22. create rejects duplicate scoped provider/model identity with exact error;
23. create under a disabled Availability is permitted;
24. update cannot change provider/providerModelId because the action does not accept them;
25. stale update CAS is rejected;
26. update increments editVersion exactly once;
27. reassignment preserves Catalogue Entry ID;
28. reassignment emits `ASSIGN_MODEL_CATALOGUE_ENTRY_AVAILABILITY` with old/new Availability IDs;
29. reassignment does not modify Agent Configuration;
30. disable of a selected entry is permitted and does not clear model selection;
31. enable/disable uses CAS and the correct audit action;
32. no delete mutation exists;
33. no audit event copies full model configuration;
34. no credential field exists in Catalogue mutation input.

#### UI/security behaviour

35. Platform Admin can read Catalogue but sees no Create/Edit/Enable/Disable mutation controls;
36. SUPER_ADMIN sees Create/Edit/lifecycle controls;
37. Sidebar contains Availability + Catalogue and no Credential link yet;
38. table renders derived `provider/providerModelId` OpenRouter identity;
39. table does not render full configuration JSON;
40. Edit drawer warns when `selectionCount > 0`;
41. Create/Edit configuration textarea uses direct OpenRouter-style JSON;
42. repeated same-tick submit/click dispatches one Server Action only;
43. route/page is protected by Platform Admin page authorization.

Do not make a live OpenRouter request in this task.

## Work Items

- [ ] Synchronize the accepted DATABASE-001 Admin database submodule and published SHARED-002 package.
- [ ] Regenerate and validate Admin Prisma.
- [ ] Add `/commerce-models/catalogue` and the `model-catalogue` Admin active key.
- [ ] Extend the `Commerce models` sidebar group with Catalogue while retaining Availability and no dead Credential link.
- [ ] Implement the bounded paginated Catalogue read model from R4.
- [ ] Implement the one canonical Shared-backed form parser from R5.
- [ ] Implement SUPER_ADMIN-only create semantics and audit from R6.
- [ ] Make provider/providerModelId immutable in the Edit path per R7.
- [ ] Implement CAS update and Availability reassignment/audit per R8.
- [ ] Implement separate CAS enable/disable actions per R9.
- [ ] Add selection-count warning behaviour from R10.
- [ ] Add direct OpenRouter-style JSON editor using Shared validation per R11.
- [ ] Implement the Catalogue table/filter/control-plane UI from R12-R13.
- [ ] Add same-tick duplicate mutation protection from R14.
- [ ] Keep audit metadata bounded and secret-safe per R15.
- [ ] Add exact bounded error mapping from R16.
- [ ] Add focused validation, service, mutation, UI and security tests from R17.
- [ ] Run all required Validation below.
- [ ] Complete the Completion Report, set task to review and STOP.

## Interfaces / Contracts

### Database contracts consumed

Owner:

`ARCH-024-DATABASE-001`

Consumed entities:

```text
commerce.CommerceModelAvailability
commerce.CommerceModelCatalogueEntry
commerce.CommerceAgentConfiguration      count/reference only
commerce.CommerceAuditEvent
public.PlatformAdmin
commerce.Shop
```

Consumed audit actions:

```text
CREATE_MODEL_CATALOGUE_ENTRY
UPDATE_MODEL_CATALOGUE_ENTRY
ENABLE_MODEL_CATALOGUE_ENTRY
DISABLE_MODEL_CATALOGUE_ENTRY
ASSIGN_MODEL_CATALOGUE_ENTRY_AVAILABILITY
```

### Shared contracts consumed

Owner:

`ARCH-024-SHARED-001`

Published by:

`ARCH-024-SHARED-002`

Package entrypoint:

```text
@modainteract/moda-interact-shared/commerce/model
```

Required exports:

```text
CommerceModelAvailabilitySchema
CommerceModelAvailability
CommerceModelCatalogueEntrySchema
CommerceModelCatalogueEntry
CommerceModelProviderSchema
CommerceProviderModelIdSchema
CommerceModelConfigurationSchema
CommerceModelConfiguration
COMMERCE_MODEL_CONFIGURATION_SCHEMA_VERSION
createOpenRouterModelId
```

### Admin routes produced

```text
GET /commerce-models/catalogue
```

All mutations remain Next.js Server Actions and are not public HTTP APIs.

### Downstream consumer

`ARCH-024-COMMERCE-003` depends on this task so Commerce Studio can safely remove legacy Catalogue administration only after the Admin-owned replacement is accepted.

## Dependencies

- `ARCH-024-DATABASE-001`
- `ARCH-024-SHARED-002`
- `ARCH-024-ADMIN-001`

## Enables

- `ARCH-024-COMMERCE-003`

## Acceptance Criteria

- [ ] Admin provides `/commerce-models/catalogue` as the authoritative human Model Catalogue administration surface.
- [ ] Platform Admin readers can inspect all Platform/Shop Catalogue Entries but cannot mutate them.
- [ ] SUPER_ADMIN can create a Catalogue Entry under any existing Availability.
- [ ] Create identity is canonical dynamic `provider + providerModelId`; there is no `OPENAI | GROQ` form enum.
- [ ] `provider` and `providerModelId` are immutable after creation.
- [ ] Model configuration is direct OpenRouter-style JSON validated by the exact published Shared schema.
- [ ] Unknown non-reserved OpenRouter options remain valid and are preserved.
- [ ] Reserved Moda-owned runtime/security fields cannot be persisted through Admin configuration.
- [ ] No credential, API-key, headers or base-URL field exists on the Catalogue form.
- [ ] SUPER_ADMIN can update display metadata/configuration and reassign an existing entry to another Availability without changing its ID.
- [ ] Reassignment is audited and does not modify Agent Configuration.
- [ ] SUPER_ADMIN can enable/disable an entry under CAS.
- [ ] Disabling/reassigning a selected model is allowed and does not silently clear selection.
- [ ] No Catalogue Entry delete path exists.
- [ ] Scoped duplicate `(availabilityId, provider, providerModelId)` creation/reassignment is rejected cleanly.
- [ ] Reads are paginated with page size 50 and filtered server-side.
- [ ] Catalogue read rows and configuration inputs are validated through canonical Shared contracts.
- [ ] Audit events use target columns and do not copy full configuration or secrets into metadata.
- [ ] Same-tick repeated mutation activation dispatches one Server Action only.
- [ ] `Commerce models` navigation contains Availability + Catalogue and no Credential link yet.
- [ ] Commerce Studio code is not modified by this task.
- [ ] No live OpenRouter call is required.

## Validation

Before Node-related commands:

```bash
command -v node >/dev/null 2>&1 || \
  source "$MODA_WORKSPACE_ROOT/scripts/bootstrap-node.sh"
```

From the dedicated `moda-interact-admin` task worktree, inspect `package.json` first, then run:

```bash
npm run prisma:generate
npm run prisma:validate
```

Focused unit tests:

```bash
node --experimental-strip-types --test \
  tests/unit/model-catalogue-validation.test.ts \
  tests/unit/model-catalogue-service.test.ts
```

Focused security/UI tests:

```bash
node --test \
  tests/security/admin-model-catalogue.test.mjs \
  tests/security/admin-sidebar-navigation.test.mjs
```

Targeted formatting:

```bash
npx prettier --check \
  'src/app/(protected)/commerce-models/catalogue/page.tsx' \
  src/app/actions/model-catalogue.ts \
  src/lib/admin/model-catalogue.ts \
  src/lib/admin/model-catalogue-validation.ts \
  src/components/admin/model-catalogue/model-catalogue-table.tsx \
  src/components/admin/model-catalogue/model-catalogue-editor.tsx \
  src/components/admin/model-catalogue/model-catalogue-mutation-form.tsx \
  src/components/admin/sidebar.tsx \
  src/components/admin/admin-shell.tsx \
  tests/unit/model-catalogue-validation.test.ts \
  tests/unit/model-catalogue-service.test.ts \
  tests/security/admin-model-catalogue.test.mjs \
  tests/security/admin-sidebar-navigation.test.mjs
```

Targeted ESLint:

```bash
npx eslint \
  'src/app/(protected)/commerce-models/catalogue/page.tsx' \
  src/app/actions/model-catalogue.ts \
  src/lib/admin/model-catalogue.ts \
  src/lib/admin/model-catalogue-validation.ts \
  src/components/admin/model-catalogue/model-catalogue-table.tsx \
  src/components/admin/model-catalogue/model-catalogue-editor.tsx \
  src/components/admin/model-catalogue/model-catalogue-mutation-form.tsx \
  src/components/admin/sidebar.tsx \
  src/components/admin/admin-shell.tsx
```

Production build (the repository has no standalone `typecheck` npm script; the production build remains the declared TypeScript/build gate):

```bash
npm run build
```

Whitespace:

```bash
git diff --check
```

If validation encounters a documented baseline condition, follow `docs/development-baseline.md` according to the architect's baseline policy. Do not expand this task into unrelated baseline repair.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete:

1. finish the Completion Report;
2. set task status to `review`;
3. clear no architect-owned fields;
4. return control to `moda_architect`;
5. STOP.

Do not begin `ARCH-024-COMMERCE-003`, `ARCH-024-ADMIN-003` or any other follow-on task.

## Implementation Notes

- Reuse the existing Admin `AdminShell`, `Sidebar`, `AdminDetailDrawer`, Platform Admin authorization and development-principal materialisation patterns.
- `provider` is dynamic and intentionally not a UI enum.
- The OpenRouter configuration textarea stores provider/model request options only. It does not store the selected model identity or credential.
- Shared validation is the source of truth for the extensible configuration envelope. Admin must not freeze OpenRouter's option surface into local form fields.
- A Catalogue Entry's Availability is assignment and may change. The model identity itself may not.
- A disabled Availability may still contain enabled Catalogue Entries; effective usability is decided later by Commerce from both Availability and entry state.
- The Admin read model may show selection counts for operator awareness but must never use selection count to veto an Availability reassignment or lifecycle change.
- Do not introduce LangChain/OpenRouter runtime imports into browser-safe Admin components.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

Not run

### Deviations

None

### Assumptions

None

### Unresolved Issues

None

### Architectural Concerns

None

## Architect Review

### Review Status

Pending

### Review Notes

Pending implementation.

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending.

### Follow-up

None
