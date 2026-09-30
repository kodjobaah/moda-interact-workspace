---
id: ARCH-023-ADMIN-003
architecture_id: ARCH-023
title: Author and publish Platform and Shop Instructions
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 41
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-023-DATABASE-001
  - ARCH-023-ADMIN-002
enables: []
created: 2026-09-29
updated: 2026-09-30
---

# Author and publish Platform and Shop Instructions

## Architecture

Architecture ID: `ARCH-023`

Architecture document: `docs/architecture/ARCH-023-merchant-knowledge.md`

Coordinator: `moda_architect`

## Objective

Make Admin the authoritative product-management UI for canonical-English Platform Instructions and shop-scoped Shop Instructions while preserving the existing ARCH-021 prompt lineage/revision/configuration lifecycle.

This task must support:

```text
Platform prompt lineage:
  create/open DRAFT
  CAS edit
  publish
  activate in current environment

Shop prompt lineage:
  select shop
  create/open DRAFT
  CAS edit
  publish
  activate in current environment

ARCH-023 pending Store Category draft:
  edit exact pending DRAFT
  publish exact pending DRAFT
  atomically activate prompt + pending category
```

Capability-local prompts remain Commerce Studio-owned.

## Context

Existing durable models already provide:

```text
CommerceAgentPrompt
CommerceAgentPromptRevision
CommerceAgentConfiguration
CommerceAuditEvent
```

ARCH-023-DATABASE-001 additionally provides:

```text
CommerceShopProfile.pendingCategoryId
CommerceShopProfile.pendingPromptRevisionId
CommerceShopProfile.activeCategoryId
CommerceAgentPromptRevision.sourceTemplateEditVersion
```

Published revisions are immutable at the database boundary.

Admin must not create a second prompt store or call Commerce Studio through a new private HTTP API.

## Scope

Primary authorized implementation surface:

```text
database                         # gitlink update only

src/app/(protected)/system-controls/agent-instructions/page.tsx
src/app/actions/agent-instructions.ts

src/components/admin/agent-instructions/agent-instructions-console.tsx
src/components/admin/agent-instructions/platform-instructions-editor.tsx
src/components/admin/agent-instructions/shop-instructions-editor.tsx
src/components/admin/agent-instructions/prompt-revision-history.tsx

src/lib/admin/commerce-environment.ts
src/lib/admin/agent-instructions.ts

src/components/admin/sidebar.tsx

tests/unit/agent-instructions.test.ts
tests/unit/agent-instruction-actions.test.ts
```

## Out of Scope

- capability-local prompt authoring.
- Tool authoring.
- model-selection changes.
- category/template CRUD (ADMIN-002).
- merchant onboarding/category selection (Shopify).
- translation of Platform/Shop instructions.
- database schema changes.
- arbitrary prompt layers.
- removing Commerce Studio screens; that is Commerce-owned follow-up work.

## Requirements

### R1 — exact Admin route/navigation

Add protected page:

```text
/system-controls/agent-instructions
```

Add under `System controls`:

```text
Agent Instructions
```

Extend Sidebar/AdminShell active type with:

```text
agent-instructions
```

All reads use existing platform-admin read/page guards.

All mutations require existing platform-admin mutation authorization and:

```text
SUPER_ADMIN
```

### R2 — exact Commerce environment mapping

Create:

```text
src/lib/admin/commerce-environment.ts
```

Export:

```ts
resolveAdminCommerceEnvironment(): CommerceEnvironment
```

Use existing `resolveDeploymentEnvironmentName()` and map exactly:

```text
local       -> LOCAL
test        -> TEST
development -> DEVELOPMENT
staging     -> STAGING
production  -> PRODUCTION
```

Any other value throws:

```text
Commerce environment is unavailable.
```

Do not default unknown environments to DEVELOPMENT/PRODUCTION.

### R3 — one prompt lineage per scope in Admin behavior

For Platform:

```text
scope = PLATFORM
shopId = null
```

For Shop:

```text
scope = SHOP
shopId = exact selected Shop.id
```

The read/service layer must fail closed if more than one lineage exists for the same logical Platform scope or same Shop.

Do not silently choose one by createdAt/id.

When no lineage exists and the admin chooses Create Draft:

1. create one `CommerceAgentPrompt` lineage;
2. audit `CREATE_AGENT_PROMPT`;
3. create revision 1 DRAFT;
4. audit `CREATE_AGENT_PROMPT_DRAFT`.

The two writes occur in one transaction.

### R4 — draft allocation

When a lineage exists and no DRAFT exists, Create Draft:

1. lock the lineage row;
2. calculate:
   ```text
   revisionNumber = max(existing revisionNumber) + 1
   ```
3. seed `promptText`:
   - from currently active published revision for this environment if present;
   - else from latest published revision;
   - else `""`;
4. copy from seed revision:
   ```text
   sourceTemplateId
   sourceTemplateEditVersion
   ```
5. create one DRAFT with:
   ```text
   editVersion = 1
   contentHash = null
   publishedAt = null
   ```
6. audit `CREATE_AGENT_PROMPT_DRAFT`.

Do not create a second DRAFT when one already exists. Return the existing DRAFT.

### R5 — ARCH-023 pending category draft has priority in Shop UI

For selected Shop, load `CommerceShopProfile`.

If:

```text
pendingPromptRevisionId != null
```

then the Shop Instructions editor MUST open that exact revision as the current DRAFT and display:

```text
Pending Store Category: <category displayName>
Seed template: <template displayName/key>
Seed template edit version: <sourceTemplateEditVersion>
```

Do not create another Shop DRAFT while an ARCH-023 pending category DRAFT exists.

The pending revision must satisfy:

```text
revision.id == pendingPromptRevisionId
revision.status == DRAFT
revision.prompt.scope == SHOP
revision.prompt.shopId == selected shop
revision.sourceTemplateId == pendingCategory.defaultTemplateId snapshot identity expected by persisted profile/revision
sourceTemplateEditVersion != null
```

If not, fail with bounded configuration-conflict UI; do not repair silently.

### R6 — CAS draft update

Server action input:

```text
revisionId
expectedEditVersion
promptText
reason
```

Validation:

```text
promptText trimmed non-empty
promptText <= 100_000 characters
reason trimmed 1..1000
```

Transaction:

```text
UPDATE CommerceAgentPromptRevision
WHERE id = revisionId
  AND status = DRAFT
  AND editVersion = expectedEditVersion
SET promptText = exact submitted canonical-English text,
    editVersion = editVersion + 1
```

Do not change:

```text
promptId
revisionNumber
sourceTemplateId
sourceTemplateEditVersion
contentHash
publishedAt
```

CAS miss -> stale-write error.

Audit:

```text
UPDATE_AGENT_PROMPT_DRAFT
```

with exact prompt/revision/shop references.

### R7 — content hash

Publishing uses:

```text
lowercase SHA-256 of exact UTF-8 promptText
```

No whitespace normalization is performed before hashing.

Blank/whitespace-only prompt cannot publish.

### R8 — ordinary Platform/Shop publish + activate is one Admin transaction

For a DRAFT that is not the ARCH-023 `pendingPromptRevisionId`, Publish action input:

```text
revisionId
expectedRevisionEditVersion
expectedConfigurationPromptEditVersion
reason
```

In one transaction:

1. load revision + lineage;
2. require `status=DRAFT`;
3. require revision editVersion matches;
4. require nonblank promptText;
5. resolve current environment from R2;
6. locate the exact `CommerceAgentConfiguration` for:
   - Platform environment/scope; or
   - Shop environment/scope/shopId;
7. if configuration exists, require:
   ```text
   promptEditVersion == expectedConfigurationPromptEditVersion
   ```
8. if absent, require expected configuration edit version exactly `1`;
9. publish revision:
   ```text
   status = PUBLISHED
   contentHash = R7 hash
   publishedAt = now
   editVersion += 1
   ```
10. create/update configuration:
   ```text
   activePromptRevisionId = published revision.id
   promptEditVersion = previous + 1
   ```
   while preserving `modelId` and `modelEditVersion`;
11. write `PUBLISH_AGENT_PROMPT_REVISION` audit;
12. write `SET_AGENT_PROMPT` audit referencing `agentConfigurationId`;
13. commit.

Do not publish first and activate in a separate request.

### R9 — pending Store Category Shop publish is one larger atomic transaction

When:

```text
CommerceShopProfile.pendingPromptRevisionId == revisionId
```

perform R8 plus these exact checks/changes in the same transaction.

Before publish require:

```text
profile.pendingCategoryId != null
profile.pendingSelectedAt != null
profile.pendingPromptRevisionId == revision.id
revision.sourceTemplateId != null
revision.sourceTemplateEditVersion != null
revision.prompt.scope == SHOP
revision.prompt.shopId == profile.shopId
```

Do not re-read the current template text and do not reset promptText from the template.

After publishing and setting the Shop configuration pointer:

```text
profile.activeCategoryId          = profile.pendingCategoryId
profile.activeCategoryActivatedAt = now

profile.pendingCategoryId       = null
profile.pendingPromptRevisionId = null
profile.pendingSelectedAt       = null
```

Preserve:

```text
pendingSelectionGeneration
```

as the monotonic selection generation counter; do not reset it.

The exact DRAFT that Admin reviewed is what becomes active.

If any CAS/profile invariant fails, the entire transaction rolls back:

```text
draft remains DRAFT
active prompt remains unchanged
active category remains unchanged
pending category remains pending
```

### R10 — initial onboarding activation remains Shopify-owned

Do not automatically publish every pending category DRAFT from Admin.

The ARCH-023 initial onboarding flow may publish the exact pending DRAFT when the current Subscription becomes ACTIVE/TRIALING through Shopify/reconciliation.

Admin only publishes when a SUPER_ADMIN explicitly presses Publish from the Agent Instructions UI.

### R11 — Platform and Shop are additive, not replacement policy

Admin persistence must maintain independent:

```text
PLATFORM prompt/configuration
SHOP prompt/configuration
```

Publishing Shop Instructions must not delete/clear/replace Platform configuration.

Publishing Platform Instructions must not mutate Shop configurations.

Effective runtime composition is Commerce-owned and not implemented here.

### R12 — revision history

UI shows for each scope:

```text
revisionNumber
status
editVersion
publishedAt
contentHash
sourceTemplate provenance when present
ACTIVE marker when configuration points to revision
```

PUBLISHED revisions are read-only.

Allow opening/viewing historical published text.

Do not implement rollback as mutation of an immutable revision. If activation of an older published revision is needed, provide separate `Activate published revision` action using the same configuration CAS, without changing revision.

### R13 — activate an existing published revision

Action input:

```text
promptRevisionId
expectedConfigurationPromptEditVersion
reason
```

Require exact scope/shop match and `status=PUBLISHED`.

CAS update only:

```text
CommerceAgentConfiguration.activePromptRevisionId
CommerceAgentConfiguration.promptEditVersion += 1
```

Do not modify `CommerceShopProfile` category fields when activating an arbitrary historical Shop revision.

Audit:

```text
SET_AGENT_PROMPT
```

### R14 — no prompt-template translation lifecycle

Admin displays `sourceTemplateId` and `sourceTemplateEditVersion` as provenance only.

It does not:

```text
translate promptText
dispatch translation work
create translation snapshots
re-read current template on publish
```

All Platform/Shop/capability instructions remain canonical English under ARCH-023.

### R15 — exact audit requirements

Use existing `CommerceAuditEvent` and a fresh operationId per mutation.

Required actions:

```text
CREATE_AGENT_PROMPT
CREATE_AGENT_PROMPT_DRAFT
UPDATE_AGENT_PROMPT_DRAFT
PUBLISH_AGENT_PROMPT_REVISION
SET_AGENT_PROMPT
```

For a pending-category publish, `PUBLISH_AGENT_PROMPT_REVISION` metadata must include:

```json
{"changeKind":"PENDING_STORE_CATEGORY_PROMOTION"}
```

and the pointer audit remains `SET_AGENT_PROMPT`.

Do not add CommerceAuditAction values.

### R16 — UI

The Agent Instructions page contains:

```text
Platform Instructions
Shop Instructions
```

Platform section shows current environment, active revision, one DRAFT editor and history.

Shop section provides deterministic shop search/selection using existing tenant/admin data access conventions, then the same active/DRAFT/history UI.

For pending category drafts, show a visible banner:

```text
Publishing this draft will activate the pending Store Category.
```

Save and Publish are separate actions.

Publish button is disabled while local text differs from the last successfully saved DRAFT editVersion.

### R17 — exact regression cases

Tests must prove:

```text
non-SUPER_ADMIN mutations denied
unknown deployment environment rejects
duplicate Platform/Shop lineage fails closed
only one DRAFT reused
draft CAS conflict rejects
published revision immutable
publish hashes exact UTF-8 text
ordinary publish atomically sets active pointer
configuration CAS conflict rolls back publish
Shop publish never mutates Platform pointer
Platform publish never mutates Shop pointer

pending category:
  exact pending revision shown
  edit preserves template provenance
  publish promotes category + prompt atomically
  publish does not re-read current template text
  stale profile/revision/config CAS rolls everything back
  pendingSelectionGeneration preserved

historical published activation changes pointer only
no translation data/job is created
```

## Work Items

- [ ] Adopt database gitlink if required.
- [ ] Add deterministic Commerce environment resolver.
- [ ] Add prompt read/lifecycle service with one-lineage/one-draft rules.
- [ ] Add exact CAS save/publish/activate transactions.
- [ ] Add pending Store Category atomic promotion.
- [ ] Add protected Agent Instructions route/navigation.
- [ ] Add Platform and selected-Shop editors/history.
- [ ] Add exact Commerce audits.
- [ ] Add focused lifecycle/security/UI regressions.

## Interfaces / Contracts

Reads/writes:

```text
CommerceAgentPrompt
CommerceAgentPromptRevision
CommerceAgentConfiguration
CommerceShopProfile
CommercePromptTemplate provenance
CommerceAuditEvent
Shop
```

No cross-repository event/API is introduced.

## Dependencies

- `ARCH-023-DATABASE-001`
- `ARCH-023-ADMIN-002`

## Enables

Planned Shopify Store Profile/category-change and Commerce prompt-ownership cleanup tasks may depend on this task after their definitions are created.

## Acceptance Criteria

- [ ] Admin is the authoritative UI for Platform and Shop Instructions.
- [ ] Platform and Shop use one existing durable prompt lifecycle, not duplicate storage.
- [ ] CAS protects both mutable DRAFTs and active configuration pointer.
- [ ] Published revisions remain immutable.
- [ ] Pending Store Category promotion is atomic with exact reviewed Shop prompt publication.
- [ ] Template provenance is preserved and never re-resolved at publish.
- [ ] Platform/Shop persistence remains independent/additive.
- [ ] No translation lifecycle or capability-prompt authoring is introduced.
- [ ] Existing Commerce prompt tables/constraints remain authoritative.

## Validation

- [ ] focused prompt lifecycle/action tests
- [ ] pending-category transaction integration test
- [ ] Admin security regressions
- [ ] `npm run test:unit`
- [ ] `npm run lint`
- [ ] `npm run build`
- [ ] `git diff --check`
- [ ] changed-file diagnostics clean

## Stop Condition

Set status to `review`, complete Completion Report, return to `moda_architect` and STOP.

Do not begin Shopify or Commerce follow-up work.

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
