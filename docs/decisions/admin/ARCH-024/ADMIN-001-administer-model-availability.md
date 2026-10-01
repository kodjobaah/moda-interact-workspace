---
id: ARCH-024-ADMIN-001
architecture_id: ARCH-024
title: Administer Commerce model availability
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-024-DATABASE-001
  - ARCH-024-SHARED-002
enables:
  - ARCH-024-ADMIN-002
created: 2026-09-30
updated: 2026-10-01
---

# Administer Commerce model availability

## Architecture

Architecture ID:

`ARCH-024`

Architecture document:

`docs/architecture/ARCH-024-commerce-agent-model-runtime-and-test-conversations.md`

Coordinator:

`moda_architect`

## Objective

Add the Admin control-plane surface for viewing and managing the ARCH-024 `CommerceModelAvailability` scopes that determine **where Model Catalogue entries may be selected**.

The completed Admin behaviour must be exactly:

```text
PLATFORM availability
    one bootstrap row created by ARCH-024-DATABASE-001
    visible to Platform Admin readers
    SUPER_ADMIN may enable / disable it
    cannot be recreated, deleted, moved or retargeted

SHOP availability
    zero or one row per existing Shop
    SUPER_ADMIN may create it for a Shop that does not already have one
    SUPER_ADMIN may enable / disable it
    cannot be deleted, moved to another Shop or changed to PLATFORM
```

This task administers Availability containers only.

It MUST NOT create, edit, enable, disable, move or otherwise mutate any `CommerceModelCatalogueEntry`. `ARCH-024-ADMIN-002` owns Model Catalogue entries.

It MUST NOT select the active Agent model. Commerce Studio owns active-model selection after `ARCH-024-COMMERCE-002/003`.

## Context

ARCH-024-DATABASE-001 establishes the durable relationship:

```text
CommerceModelAvailability
        1
        |
        *
CommerceModelCatalogueEntry
```

Availability is global Platform/Shop eligibility and is intentionally **not environment-scoped**.

The database contract is:

```text
CommerceModelAvailability
    id
    scope = PLATFORM | SHOP
    shopId?
    enabled
    editVersion
    createdByAdminId?
    updatedByAdminId?
    createdAt
    updatedAt
```

with exactly these identity rules:

```text
PLATFORM
    shopId = NULL
    at most one row
    deterministic bootstrap id:
        arch024-platform-model-availability

SHOP
    shopId != NULL
    at most one row per Shop
```

and immutable:

```text
id
scope
shopId
```

The database rejects Availability deletion.

ARCH-024-SHARED-001 defines the canonical runtime-safe `CommerceModelAvailability` contract and ARCH-024-SHARED-002 publishes the combined accepted Shared package. Admin MUST consume the exact published Shared contract rather than inventing a structurally similar local cross-service Availability type.

The current Admin application already provides the required platform patterns:

```text
requirePlatformAdminPage()
requirePlatformAdminRead()
requirePlatformAdminMutation()
SUPER_ADMIN mutation gating
ensureDevelopmentPlatformAdmin(...)
AdminShell / Sidebar
AdminDetailDrawer
Serializable Prisma mutations
CAS-style editVersion updates
CommerceAuditEvent
Tenant Directory Shop identity
```

Reuse those patterns. Do not introduce a second Admin authorization, audit or Shop identity mechanism.

## Scope

Primary implementation targets:

```text
moda-interact-admin/src/app/(protected)/commerce-models/availability/page.tsx
moda-interact-admin/src/app/actions/model-availability.ts
moda-interact-admin/src/lib/admin/model-availability.ts
moda-interact-admin/src/lib/admin/model-availability-validation.ts
moda-interact-admin/src/components/admin/model-availability/model-availability-catalog.tsx
moda-interact-admin/src/components/admin/model-availability/model-availability-editor.tsx
moda-interact-admin/src/components/admin/model-availability/model-availability-submit-button.tsx
moda-interact-admin/src/components/admin/sidebar.tsx
moda-interact-admin/src/components/admin/admin-shell.tsx

moda-interact-admin/tests/unit/model-availability-validation.test.ts
moda-interact-admin/tests/unit/model-availability-service.test.ts
moda-interact-admin/tests/security/admin-model-availability.test.mjs
moda-interact-admin/tests/security/admin-sidebar-navigation.test.mjs

moda-interact-admin/package.json
moda-interact-admin/package-lock.json
```

The nested Admin `database/` submodule/gitlink may move only to the architect-accepted `ARCH-024-DATABASE-001` database commit required by this task.

Additional Admin files may be changed only when required to integrate this exact Availability surface or keep the focused validation/build green. Every additional file MUST be named and justified in the Completion Report.

Do not modify the database schema/migration inside this task.

## Out of Scope

- Creating or editing `CommerceModelCatalogueEntry`; `ARCH-024-ADMIN-002` owns it.
- Assigning/moving a Catalogue Entry between Availability scopes; `ARCH-024-ADMIN-002` owns it.
- Validating model `configuration` JSON; `ARCH-024-ADMIN-002` owns Catalogue entry configuration.
- OpenRouter credential administration; `ARCH-024-ADMIN-003` owns it.
- Agent model selection.
- Commerce Studio changes.
- Test Conversation changes.
- Background runtime changes.
- Merchant-facing model selection; merchants do not select models under ARCH-024.
- Creating another Platform Availability.
- Deleting an Availability.
- Changing an Availability `scope` or `shopId` after creation.
- Automatically creating a Shop Availability when a Shop is installed.
- Automatically clearing or changing `CommerceAgentConfiguration.modelId` when Availability is disabled.
- Preventing Admin from disabling an Availability merely because it contains selected models. Broken explicit Agent selections must remain representable so Commerce can fail closed as `UNAVAILABLE`.
- Requiring an Availability to contain at least one Catalogue Entry.
- Environment-specific Availability. Availability remains global; Agent Configuration remains environment-specific.
- A new audit store or authorization framework.

## Requirements

### R1 — Consume accepted Database and Shared dependencies first

Before implementation:

1. synchronize the nested `database/` submodule to the architect-accepted `ARCH-024-DATABASE-001` implementation;
2. update `@modainteract/moda-interact-shared` to the exact version published and architect-accepted by `ARCH-024-SHARED-002`;
3. regenerate Prisma using the repository's declared command:

```bash
npm run prisma:generate
```

4. validate Prisma using:

```bash
npm run prisma:validate
```

Admin MUST import the canonical Availability contract from:

```text
@modainteract/moda-interact-shared/commerce/model
```

At minimum consume:

```ts
CommerceModelAvailabilitySchema
CommerceModelAvailability
CommerceModelAvailabilityScopeSchema
```

Do not define a second local `PLATFORM | SHOP` Availability contract.

### R2 — Add the Admin navigation boundary exactly

Add a new protected Admin route:

```text
/commerce-models/availability
```

Extend `AdminShell` and `Sidebar` with the active key:

```text
model-availability
```

Add a nested sidebar group with exact visible labels:

```text
Commerce models
    Availability
```

The group root and Availability link both target:

```text
/commerce-models/availability
```

For ADMIN-001 the group contains **only** the implemented `Availability` destination. Do not add dead Catalogue or Credential links before their owning tasks implement them.

The group is visible to all authenticated Platform Admin readers. Mutation controls inside the page are SUPER_ADMIN-only.

Use an existing Admin icon; do not introduce an icon dependency solely for this task.

Update `tests/security/admin-sidebar-navigation.test.mjs` to prove:

1. `Commerce models` is present;
2. `/commerce-models/availability` is present;
3. `AdminShell` accepts `model-availability`;
4. the Availability page renders `<AdminShell active="model-availability">`;
5. no `/commerce-models/catalogue` or `/commerce-models/credentials` link is introduced by this task.

### R3 — Protect the page and every mutation independently

The page MUST call:

```ts
await requirePlatformAdminPage();
```

Reads MUST execute through a service that independently calls:

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

Development bypass mutation transactions MUST call:

```ts
await ensureDevelopmentPlatformAdmin(transaction, principal);
```

Do not rely on hidden buttons or page authorization as the mutation security boundary.

### R4 — Implement the read model exactly

Create:

```ts
export type ModelAvailabilityAdminItem = {
  availability: CommerceModelAvailability;
  shopDomain: string | null;
  shopStatus: string | null;
  modelCount: number;
  enabledModelCount: number;
  createdAt: Date;
  updatedAt: Date;
};

export type ModelAvailabilityCatalogue = {
  platform: ModelAvailabilityAdminItem;
  shops: ModelAvailabilityAdminItem[];
};

export async function getModelAvailabilityCatalogue(): Promise<ModelAvailabilityCatalogue>;
```

`getModelAvailabilityCatalogue()` MUST:

1. call `requirePlatformAdminRead()`;
2. read all `CommerceModelAvailability` rows in one bounded query;
3. select only the fields required for the Admin read model;
4. select Shop `id`, `domain`, `status` for Shop-scoped rows;
5. select Catalogue Entry `id` + `enabled` only for counts; do not load full model configuration in this task;
6. validate each base Availability object with `CommerceModelAvailabilitySchema` before returning it to the UI;
7. calculate:

```text
modelCount        = all direct entries

enabledModelCount = direct entries where entry.enabled = true
```

8. require exactly one Platform Availability in the result.

If the database does not contain exactly one Platform Availability, fail the read with:

```text
Platform Model Availability is not configured correctly.
```

Do **not** repair/create the Platform row from Admin application code.

Return deterministic order:

```text
platform
    the single PLATFORM row

shops
    shop.domain ASC (case-insensitive compare)
    then shopId ASC
    then availability.id ASC
```

The Platform row MUST have:

```text
shopDomain = null
shopStatus = null
```

A SHOP row whose referenced Shop cannot be read is an invariant violation and MUST fail the read; do not render an "Unknown Shop" placeholder.

### R5 — Implement bounded Shop candidate search for creation

Do not load every Shop into a giant client-side select.

Create:

```ts
export type ModelAvailabilityShopCandidate = {
  id: string;
  domain: string;
  status: string;
};

export async function searchModelAvailabilityShopCandidates(
  search: string,
): Promise<ModelAvailabilityShopCandidate[]>;
```

The function MUST:

1. call `requirePlatformAdminRead()`;
2. trim input and bound it to 120 characters;
3. return `[]` when the trimmed search contains fewer than 2 characters;
4. search existing `Shop.domain` case-insensitively;
5. return only Shops where:

```text
commerceModelAvailability IS NULL
```

regardless of whether any historical Availability might otherwise have been disabled;
6. order by:

```text
domain ASC
id ASC
```

7. return at most 25 candidates;
8. return only `id`, `domain`, `status`.

Do not search by or accept a free-form replacement Shop identity. The mutation ultimately receives canonical `Shop.id`.

### R6 — Define mutation inputs exactly

In `src/lib/admin/model-availability-validation.ts` define exact bounded inputs:

```ts
export type CreateShopModelAvailabilityInput = {
  shopId: string;
  reason: string;
};

export type SetModelAvailabilityEnabledInput = {
  id: string;
  expectedEditVersion: number;
  enabled: boolean;
  reason: string;
};
```

Validation rules:

```text
shopId
    trimmed
    1..128 characters

id
    trimmed
    1..128 characters

expectedEditVersion
    positive integer

enabled
    exact boolean derived from form value "true" | "false"

reason
    trimmed
    1..1000 characters
```

Export:

```ts
parseCreateShopModelAvailabilityForm(formData)
parseSetModelAvailabilityEnabledForm(formData)
```

`parseCreateShopModelAvailabilityForm` MUST NOT accept caller-supplied:

```text
scope
id
editVersion
enabled
```

The service fixes new Availability values to:

```text
scope       = SHOP
enabled     = true
editVersion = 1
```

`parseSetModelAvailabilityEnabledForm` MUST reject form data containing either:

```text
scope
shopId
```

with:

```text
Model Availability scope and Shop are immutable.
```

Do not accept deletion, retargeting or scope-conversion intents.

### R7 — Implement exactly two mutation kinds

Define:

```ts
export type ModelAvailabilityMutation =
  | {
      kind: "create-shop";
      input: CreateShopModelAvailabilityInput;
    }
  | {
      kind: "set-enabled";
      input: SetModelAvailabilityEnabledInput;
    };
```

Implement:

```ts
export async function mutateModelAvailability(
  transaction: Prisma.TransactionClient,
  mutation: ModelAvailabilityMutation,
  actorAdminId: string,
): Promise<void>;
```

No third mutation kind is allowed in ADMIN-001.

There is no:

```text
create-platform
update-scope
change-shop
delete
```

mutation.

### R8 — Create Shop Availability deterministically

For `kind === "create-shop"`:

1. load the Shop by exact `input.shopId` selecting only:

```text
id
domain
status
commerceModelAvailability.id
```

2. if Shop does not exist, throw:

```text
Shop not found.
```

3. if the Shop already has any `CommerceModelAvailability`, enabled or disabled, throw:

```text
Model Availability already exists for this Shop.
```

4. create exactly:

```ts
{
  scope: "SHOP",
  shopId: shop.id,
  enabled: true,
  editVersion: 1,
  createdByAdminId: actorAdminId,
  updatedByAdminId: actorAdminId,
}
```

Do not populate Catalogue Entries.

Do not create an Agent Configuration.

Do not check Shop plan, billing status, Feature preferences or current Agent configuration.

5. create a `CommerceAuditEvent` in the same transaction using:

```text
action                 = CREATE_MODEL_AVAILABILITY
actorAdminId           = actorAdminId
modelAvailabilityId    = created Availability id
shopId                  = shop.id
reason                  = input.reason
metadata.scope          = "SHOP"
metadata.shopDomain     = shop.domain
```

No credential/model configuration belongs in this audit event.

### R9 — Enable/disable with CAS and preserve all selections

For `kind === "set-enabled"`:

1. load Availability by exact `id` selecting:

```text
id
scope
shopId
enabled
editVersion
```

2. if missing, throw:

```text
Model Availability not found.
```

3. if `existing.editVersion !== expectedEditVersion`, throw:

```text
Model Availability changed; reload and retry.
```

4. if `existing.enabled === input.enabled`, throw exactly one of:

```text
Model Availability is already enabled.
Model Availability is already disabled.
```

5. execute a CAS update using:

```text
WHERE id = input.id
  AND editVersion = input.expectedEditVersion
```

and set:

```text
enabled          = input.enabled
editVersion      = editVersion + 1
updatedByAdminId = actorAdminId
```

6. if update count is not exactly 1, throw:

```text
Model Availability changed; reload and retry.
```

7. write one audit event in the same transaction:

```text
action = input.enabled
    ? ENABLE_MODEL_AVAILABILITY
    : DISABLE_MODEL_AVAILABILITY

actorAdminId        = actorAdminId
modelAvailabilityId = existing.id
shopId              = existing.shopId (null for PLATFORM)
reason              = input.reason
metadata.scope      = existing.scope
```

Do not mutate any `CommerceModelCatalogueEntry`.

Do not mutate any `CommerceAgentConfiguration`.

In particular, disabling an Availability MUST NOT clear a selected `modelId` or automatically fall back to another model. Later Commerce resolution owns fail-closed `UNAVAILABLE` behaviour.

### R10 — Run mutations in the standard Admin transaction boundary

Add one Server Action:

```ts
export async function mutateModelAvailabilityAction(
  formData: FormData,
): Promise<void>;
```

Supported exact form intents:

```text
create-shop
set-enabled
```

The Server Action MUST:

1. authorize with `requirePlatformAdminMutation()`;
2. require `SUPER_ADMIN` before parsing/executing the mutation;
3. parse the exact mutation based on `intent`;
4. execute through:

```ts
await prisma.$transaction(
  async (transaction) => {
    await ensureDevelopmentPlatformAdmin(transaction, principal);
    await mutateModelAvailability(transaction, mutation, principal.id);
  },
  { isolationLevel: "Serializable" },
);
```

5. map Prisma `P2002` for Shop Availability uniqueness to:

```text
Model Availability already exists for this Shop.
```

6. map Prisma `P2034` serialization conflict to:

```text
Model Availability changed; reload and retry.
```

7. otherwise preserve the bounded service error;
8. revalidate:

```text
/commerce-models/availability
```

Do not revalidate unrelated Billing/System Controls routes.

### R11 — Build the page around the existing Admin shell/drawer pattern

Create:

```text
src/app/(protected)/commerce-models/availability/page.tsx
```

The page search parameters are exactly:

```text
drawer
availabilityId
shopSearch
```

Supported drawer states:

```text
drawer=create-shop

drawer=manage&availabilityId=<id>
```

Unknown drawer values are treated as no drawer.

The page MUST:

1. call `requirePlatformAdminPage()` and retain the returned principal;
2. call `getModelAvailabilityCatalogue()`;
3. call `searchModelAvailabilityShopCandidates(shopSearch)` only when `drawer=create-shop`;
4. render `<AdminShell active="model-availability">`;
5. pass `canMutate={principal.role === "SUPER_ADMIN"}` to the Availability UI;
6. never perform a Prisma query directly inside a client component.

### R12 — Render Availability information exactly

The page heading is:

```text
Model availability
```

and the explanatory copy must state both concepts clearly:

```text
Availability controls which catalogue models may be selected for Platform or a Shop. It does not select the active CommerceAgent model.
```

Render Platform Availability first in its own section/card showing:

```text
Scope           Platform
Status          Enabled | Disabled
Models          <modelCount> total · <enabledModelCount> enabled
Updated         <updatedAt>
```

Render Shop Availability below in a table/list with columns:

```text
Shop
Shop status
Availability
Models
Updated
Actions
```

Shop label is the canonical `Shop.domain`.

Availability status labels are exactly:

```text
Enabled
Disabled
```

Do not label `enabled` as "Active model" or "Selected model".

If there are no Shop Availability rows, render a bounded empty state explaining that no Shop-specific model availability has been configured.

### R13 — SUPER_ADMIN-only creation UI

Only when `canMutate === true` show:

```text
Create Shop availability
```

The Create drawer MUST:

1. identify the operation as Shop Availability creation; there is no Platform creation UI;
2. provide a GET Shop search form using `shopSearch` and preserving `drawer=create-shop`;
3. explain that at least 2 search characters are required;
4. render at most the 25 server-returned candidates;
5. show Shop `domain` + `status`;
6. submit canonical `shopId`, not domain text;
7. require an audit `reason` textarea/input with max length 1000;
8. submit `intent=create-shop`.

If no candidate matches, render:

```text
No Shops without Model Availability match this search.
```

A non-SUPER_ADMIN can read the page but MUST NOT receive a create form.

### R14 — Management drawer is identity-read-only

The Manage drawer MUST display:

```text
Availability id
Scope
Shop domain / Platform
Status
Model counts
Edit version
```

`scope` and Shop identity are read-only text, never editable inputs.

For `SUPER_ADMIN`, render exactly one state-change form for the opposite state:

```text
Enabled  -> Disable availability
Disabled -> Enable availability
```

The form MUST submit:

```text
intent=set-enabled
id
expectedEditVersion
enabled=<opposite boolean>
reason
```

and MUST NOT submit `scope` or `shopId`.

Use exact warnings:

For Platform disable:

```text
Disabling Platform availability removes Platform catalogue models from every Shop's effective available set. Existing Agent model selections are not rewritten.
```

For Shop disable:

```text
Disabling this Shop availability removes its private catalogue models from this Shop's effective available set. Existing Agent model selections are not rewritten.
```

Do not offer Delete.

### R15 — Mutation submit buttons must visibly prevent repeat submission

Create a local client component:

```text
src/components/admin/model-availability/model-availability-submit-button.tsx
```

using `useFormStatus()`.

While `pending === true`, the button MUST:

```text
disabled = true
```

and show a bounded pending label such as:

```text
Creating…
Enabling…
Disabling…
```

Server-side uniqueness/CAS remains the correctness boundary; the pending button is UX protection and MUST NOT replace R8/R9 concurrency controls.

### R16 — Do not expose Catalogue Entry or Agent model mutations from this route

A source-level regression test MUST prove the ADMIN-001 route/components/actions do not call:

```text
commerceModelCatalogueEntry.create
commerceModelCatalogueEntry.update
commerceModelCatalogueEntry.updateMany
commerceAgentConfiguration.create
commerceAgentConfiguration.update
commerceAgentConfiguration.updateMany
commerceOpenRouterCredential
```

Reads of direct Catalogue Entry `id` + `enabled` for count calculation are allowed.

No Model Catalogue editor, model selector or credential input may be rendered on `/commerce-models/availability`.

### R17 — No deletion path

There MUST be no:

```text
deleteModelAvailability
removeModelAvailability
intent=delete
commerceModelAvailability.delete
commerceModelAvailability.deleteMany
```

in the ADMIN-001 implementation.

The database identity guard remains authoritative and Admin must not attempt to work around it.

## Work Items

- [ ] Synchronize the Admin database submodule to the architect-accepted `ARCH-024-DATABASE-001` commit.
- [ ] Consume the exact Shared package version published by `ARCH-024-SHARED-002`.
- [ ] Run Prisma validate/generate before implementing the Admin model layer.
- [ ] Add `model-availability-validation.ts` with the exact two input parsers.
- [ ] Add `model-availability.ts` with the exact read model, Shop candidate search and two mutation kinds.
- [ ] Add `mutateModelAvailabilityAction()` with independent SUPER_ADMIN authorization and Serializable transaction semantics.
- [ ] Add `/commerce-models/availability` protected page.
- [ ] Add `Commerce models -> Availability` sidebar navigation and the `model-availability` AdminShell active key.
- [ ] Add Platform-first Availability presentation and Shop Availability list.
- [ ] Add bounded Shop search/create drawer.
- [ ] Add identity-read-only management drawer with CAS enable/disable action.
- [ ] Add `useFormStatus()` mutation submit protection.
- [ ] Add focused parser/service/action/security/navigation regression tests.
- [ ] Confirm there is no deletion, Catalogue mutation, Agent Configuration mutation or credential mutation in this task.
- [ ] Complete the task Completion Report and return control to `moda_architect`.

## Interfaces / Contracts

### Shared contract owner

`ARCH-024-SHARED-001`

Published by:

`ARCH-024-SHARED-002`

Package:

```text
@modainteract/moda-interact-shared/commerce/model
```

Consumed exports:

```text
CommerceModelAvailabilityScopeSchema
CommerceModelAvailabilitySchema
CommerceModelAvailability
```

### Database entities consumed

```text
commerce.CommerceModelAvailability
commerce.CommerceModelCatalogueEntry   // id + enabled counts only
commerce.Shop
commerce.CommerceAuditEvent
public.PlatformAdmin
```

### Durable Availability relationship

```text
PLATFORM
    one global CommerceModelAvailability
    shopId = NULL

SHOP
    zero or one CommerceModelAvailability per Shop
    shopId = exact Shop.id
```

### Mutation contract

```ts
type ModelAvailabilityMutation =
  | {
      kind: "create-shop";
      input: {
        shopId: string;
        reason: string;
      };
    }
  | {
      kind: "set-enabled";
      input: {
        id: string;
        expectedEditVersion: number;
        enabled: boolean;
        reason: string;
      };
    };
```

### Audit actions

```text
CREATE_MODEL_AVAILABILITY
ENABLE_MODEL_AVAILABILITY
DISABLE_MODEL_AVAILABILITY
```

`UPDATE_MODEL_AVAILABILITY` exists in the database architecture but is intentionally unused by ADMIN-001 because Availability identity is immutable and there is no other editable metadata in the target schema.

## Dependencies

- `ARCH-024-DATABASE-001`
- `ARCH-024-SHARED-002`

Both dependencies MUST be `complete` and architect-accepted before this task becomes Ready.

## Enables

- `ARCH-024-ADMIN-002`

ADMIN-002 adds Model Catalogue entry administration under the Availability scopes created/read by this task.

## Acceptance Criteria

- [ ] `/commerce-models/availability` is protected and readable by authenticated Platform Admins.
- [ ] All Availability mutations independently require `SUPER_ADMIN`.
- [ ] Sidebar exposes only the implemented `Commerce models -> Availability` destination from ARCH-024 Admin work.
- [ ] Exactly one Platform Availability is required by the read model and is never auto-created by Admin runtime code.
- [ ] Platform Availability can be inspected and enabled/disabled but cannot be recreated, deleted, retargeted or converted to SHOP.
- [ ] A Shop Availability can be created only for an existing canonical Shop without an existing Availability.
- [ ] Shop candidate search requires at least 2 characters, returns at most 25 results, and excludes Shops that already have any Availability.
- [ ] Shop Availability identity cannot be changed after creation.
- [ ] Availability enable/disable uses `editVersion` CAS and increments it exactly once on success.
- [ ] A stale enable/disable request is rejected without audit/state mutation.
- [ ] Create/enable/disable writes the required `CommerceAuditEvent` in the same transaction.
- [ ] Disabling an Availability does not mutate Catalogue Entries or Agent Configuration selections.
- [ ] Platform/Shop model counts are informational only and require no Catalogue mutation.
- [ ] The page clearly distinguishes Availability from active Agent model selection.
- [ ] No Availability delete operation exists.
- [ ] No Model Catalogue editor/selector or OpenRouter credential field appears on the Availability page.
- [ ] Repeated form submissions are visibly disabled while pending and remain server-safe through uniqueness/CAS.
- [ ] Admin uses the published Shared Availability contract rather than a duplicate local cross-service type.
- [ ] Focused tests, typecheck/lint, production build and `git diff --check` pass, subject only to documented unchanged baseline conditions.

## Validation

Before running Node-related commands, follow the workspace Node bootstrap policy from the architect/agent instructions.

Inspect `package.json` first and use the scripts actually present in this repository.

Required validation:

- [ ] Prisma schema validates against the accepted ARCH-024 database submodule:

```bash
npm run prisma:validate
```

- [ ] Prisma client regenerates:

```bash
npm run prisma:generate
```

- [ ] Focused unit tests pass:

```bash
node --experimental-strip-types --test \
  tests/unit/model-availability-validation.test.ts \
  tests/unit/model-availability-service.test.ts
```

The service tests MUST exercise at minimum:

```text
create Shop Availability
missing Shop rejection
existing Availability rejection
CAS enable success
CAS disable success
stale editVersion rejection
same-state rejection
required audit action/targets
no Agent Configuration mutation
```

- [ ] Focused Admin security/navigation tests pass:

```bash
node --test \
  tests/security/admin-model-availability.test.mjs \
  tests/security/admin-sidebar-navigation.test.mjs
```

`admin-model-availability.test.mjs` MUST prove at minimum:

```text
page requirePlatformAdminPage
read service requirePlatformAdminRead
action requirePlatformAdminMutation
SUPER_ADMIN mutation gate
ensureDevelopmentPlatformAdmin inside transaction
Serializable transaction
no deletion path
no Catalogue mutation path
no Agent Configuration mutation path
no credential mutation path
```

- [ ] TypeScript passes:

```bash
npx tsc --noEmit --pretty false
```

- [ ] Focused ESLint passes for every changed TypeScript/TSX file. Use the repository-declared `lint` script and pass the changed paths; do not invent another lint configuration.

- [ ] Production build passes:

```bash
npm run build
```

- [ ] Whitespace validation passes:

```bash
git diff --check
```

If a validation command encounters a documented unchanged baseline condition, record its baseline ID in the Completion Report. A changed-file regression introduced by this task is not excused by baseline status.

## Stop Condition

After the defined Work Items, Acceptance Criteria and required Validation are complete:

1. set the task Completion Report to `Ready for Review`;
2. set task status to `review`;
3. clear no architectural dependency yourself;
4. return the implementation and evidence to `moda_architect`;
5. **STOP**.

Do not begin `ARCH-024-ADMIN-002`, OpenRouter credential administration, Commerce Studio changes or any other follow-on task.

## Implementation Notes

### Exact ownership distinction

Use these terms consistently in code/UI/tests:

```text
Availability
    which catalogue models may be selected for Platform or one Shop

Catalogue Entry
    one configured model definition inside exactly one Availability

Agent Configuration
    which one available model is selected for a runtime environment
```

Do not call an enabled Availability the "active model".

### Platform bootstrap provenance

ARCH-024-DATABASE-001 intentionally creates the Platform Availability with nullable creator/updater provenance because there is no synthetic PlatformAdmin actor in the migration.

ADMIN-001 MUST NOT rewrite creator provenance merely because the page is opened.

On the first successful enable/disable mutation, update `updatedByAdminId` normally. `createdByAdminId` remains the original durable value.

### Disabled Availability with selected models

This task intentionally permits:

```text
Availability disabled
        +
Agent Configuration still references one of its entries
```

That is not an Admin database-repair opportunity. `ARCH-024-COMMERCE-002` owns effective model resolution and must surface an invalid explicit selection as `UNAVAILABLE`.

## Completion Report

### Status

Not Started

### Files Changed

None

### Work Completed

None

### Validation Results

None

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

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

None
