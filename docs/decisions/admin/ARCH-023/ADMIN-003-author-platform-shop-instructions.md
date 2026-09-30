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
attempt: 1
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
promptText <= 32_000 characters
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

- [x] Adopt database gitlink if required (already at the required dependency revision; no update needed).
- [x] Add deterministic Commerce environment resolver.
- [x] Add prompt read/lifecycle service with one-lineage/one-draft rules.
- [x] Add exact CAS save/publish/activate transactions.
- [x] Add pending Store Category atomic promotion.
- [x] Add protected Agent Instructions route/navigation.
- [x] Add Platform and selected-Shop editors/history.
- [x] Add exact Commerce audits.
- [x] Add focused lifecycle/security/UI regressions.

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

- [x] Admin is the authoritative UI for Platform and Shop Instructions.
- [x] Platform and Shop use one existing durable prompt lifecycle, not duplicate storage.
- [x] CAS protects both mutable DRAFTs and active configuration pointer.
- [x] Published revisions remain immutable.
- [x] Pending Store Category promotion is atomic with exact reviewed Shop prompt publication.
- [x] Template provenance is preserved and never re-resolved at publish.
- [x] Platform/Shop persistence remains independent/additive.
- [x] No translation lifecycle or capability-prompt authoring is introduced.
- [x] Existing Commerce prompt tables/constraints remain authoritative.

## Validation

- [x] focused prompt lifecycle/action tests
- [ ] pending-category transaction integration test (transaction-double coverage added; live database integration remains a documented deviation)
- [x] Admin security regressions (focused authorization tests; broader existing suite failures recorded below)
- [x] `npm run test:unit` (two unrelated pre-existing failures recorded below)
- [x] `npm run lint` (unrelated baseline errors/warnings recorded below)
- [x] `npm run build`
- [x] `git diff --check`
- [x] changed-file diagnostics clean

## Stop Condition

Set status to `review`, complete Completion Report, return to `moda_architect` and STOP.

Do not begin Shopify or Commerce follow-up work.

## Completion Report

### Status
Ready for Architect Review
### Files Changed
Implementation repository `moda-interact-admin`:
- `src/app/(protected)/system-controls/agent-instructions/page.tsx`
- `src/app/actions/agent-instructions.ts`
- `src/components/admin/agent-instructions/agent-instructions-console.tsx`
- `src/components/admin/admin-shell.tsx`
- `src/components/admin/sidebar.tsx`
- `src/lib/admin/agent-instructions.ts`
- `src/lib/admin/commerce-environment.ts`
- `tests/unit/agent-instruction-actions.test.ts`
- `tests/unit/agent-instructions.test.ts`

Task report: this file only.
### Work Completed
- Added the protected System Controls Agent Instructions page and navigation, including Platform and selected-Shop authoring, revision history, active markers, pending Store Category provenance/banner, and historical published-revision activation.
- Added strict deployment environment mapping and fail-closed lineage/configuration/DRAFT checks.
- Added SUPER_ADMIN-authorized Serializable mutations for draft allocation/edit CAS, exact UTF-8 SHA-256 publish, environment/scope/shop configuration-pointer CAS, and historical activation.
- Pending Store Category publication validates and promotes the exact pending DRAFT in the same transaction as prompt publication and pointer activation, retaining `pendingSelectionGeneration` and recording required audits.
- Added 15 focused Agent Instructions tests, including transaction-double success and rollback cases for stale configuration and profile CAS.
- Launcher evidence: `ARCH-023-ADMIN-003` was prepared and claimed as Attempt 1 by `copilot`; dependency gate passed for `ARCH-023-DATABASE-001` and `ARCH-023-ADMIN-002`; dedicated parent and implementation worktrees were created; recursive submodule checks passed; durable claim commit is `9cce2e1df1d4be3e5022eedff995ef7d439918c8`.
- Implementation commit `4587e4b7433ed5f4b10d9d5e48cdf481b411a52b` is pushed to `origin/task/ARCH-023-ADMIN-003` in `moda-interact-admin`. The database submodule was already at `2eb17ee910491e8f9df82736fc0a843844415947`; no schema or submodule change was needed.
### Validation Results
- Focused lifecycle/action suite: 15 passed, 0 failed.
- `npx tsc --noEmit --pretty false`: passed.
- Changed production-file ESLint: passed.
- `npm run test:unit`: 175 tests, 173 passed, 2 failed in existing merchant-pricing translation-workbook tests (`merchant-pricing-translation-workbook.test.ts` and `merchant-pricing-translations.test.ts`); no Agent Instructions test failed.
- `npm test`: existing security/observability suite has 9 unrelated contract failures; no Agent Instructions files are involved.
- Repository-wide `npm run lint`: 3 existing errors and 6 warnings in unrelated billing, promotion, queue, and recovery-credit files. Changed production files lint cleanly.
- `npm run build`: passed and includes `/system-controls/agent-instructions`; emitted existing BullMQ optional-dependency/critical-dependency warnings.
- `npm run prisma:validate`: passed.
- `git diff --check`: passed.
### Deviations
- The requested pending-category transaction integration coverage is implemented as behavior-level tests using a rollback-capable transaction double, not a live PostgreSQL integration test. This Admin repository has no integration-test runner or disposable PostgreSQL/Testcontainers harness. The tests exercise the actual mutation service and verify success plus rollback on configuration/profile CAS loss; Architect Review should decide whether a shared disposable-database harness is required.
### Assumptions
- Existing platform-admin read/page guards are sufficient for authenticated reads; all mutation actions additionally require the `SUPER_ADMIN` role.
- Existing ARCH-023 database models and audit actions are authoritative; no schema change is necessary.
### Unresolved Issues
- The pre-existing two unit-test failures, nine security/observability contract failures, and repository-wide lint findings remain outside this task's changed files.
### Architectural Concerns
- No product/schema architecture change was introduced. The absence of a live database integration harness limits the pending-promotion test to a transaction-aware double; see Deviations.

## Architect Review

### Review Status
Changes Requested — Attempt 1

### Review Notes
The protected route, environment mapping, lineage/DRAFT handling, CAS mutations, pending-category promotion shape, revision history, SUPER_ADMIN mutation gate and additive Platform/Shop configuration model are substantively aligned with the task. Attempt 1 is not acceptable yet because the submitted implementation conflicts with accepted database invariants and the required live transaction proof remains open.

Correction contract for Attempt 2:

1. **A1-R1 — Do not reuse one `CommerceAuditEvent.operationId` across multiple audit rows.** The accepted ARCH-021 database migration has the partial unique index `CommerceAuditEvent_operation_id_unique` on every non-null `operationId`. `allocateDraft()` currently reuses one UUID for `CREATE_AGENT_PROMPT` and `CREATE_AGENT_PROMPT_DRAFT`; publish currently reuses one UUID for `PUBLISH_AGENT_PROMPT_REVISION` and `SET_AGENT_PROMPT`. Those flows fail on the real database. Preserve every required audit event, but give each inserted `CommerceAuditEvent` its own fresh non-null `operationId`. Do not change the database schema or remove the unique index. Add focused regressions proving paired audit rows receive distinct operation IDs.
2. **A1-R2 — Align the Admin prompt-text bound with the accepted database guard.** The accepted schema retains `CommerceAgentPromptRevision_prompt_text_check` with `length("promptText") <= 32000`, while Attempt 1 accepts/UI-advertises up to 100,000 characters. ARCH-023 has no architecture-level requirement for a 100,000-character Platform/Shop prompt and this task explicitly excludes schema changes. The task contract is therefore corrected to **32,000 characters**. Update server validation, UI `maxLength` and focused tests so 32,000 is accepted and 32,001 is rejected before Prisma/database execution.
3. **A1-R3 — Complete the required real-PostgreSQL pending-category transaction proof.** Run the production Prisma mutation path against a task-local disposable PostgreSQL instance with the accepted database migrations applied. Using a task-local disposable container/command is sufficient; do not create a shared permanent Admin database harness solely for this task. The proof must cover at minimum: successful pending-category publish, exact reviewed prompt publication, active configuration pointer update, category promotion, pending-field clearing with `pendingSelectionGeneration` preserved, and complete rollback on stale configuration/profile CAS. It must also exercise the paired audit writes so the `operationId` uniqueness correction is proven against the real schema. If the disposable database cannot be provisioned/executed, return the task `blocked` with this Validation item unchecked rather than returning to review.
4. **A1-R4 — Make execution provenance durable.** Before returning Attempt 2 to review, record in the Completion Report the exact launcher-resolved parent and implementation worktree paths/branches, start-of-attempt synchronization results for both, and recursive submodule preparation/evidence. General statements that dedicated worktrees existed or were clean are not sufficient for the architect worktree-isolation policy.

No unrelated refactor, database migration, Commerce change, Shopify change or follow-on task is authorized by this review.

### Reviewed Files
- `moda-interact-admin/src/app/(protected)/system-controls/agent-instructions/page.tsx`
- `moda-interact-admin/src/app/actions/agent-instructions.ts`
- `moda-interact-admin/src/components/admin/agent-instructions/agent-instructions-console.tsx`
- `moda-interact-admin/src/components/admin/admin-shell.tsx`
- `moda-interact-admin/src/components/admin/sidebar.tsx`
- `moda-interact-admin/src/lib/admin/agent-instructions.ts`
- `moda-interact-admin/src/lib/admin/commerce-environment.ts`
- `moda-interact-admin/tests/unit/agent-instructions.test.ts`
- `moda-interact-admin/tests/unit/agent-instruction-actions.test.ts`
- `moda-interact-admin/database/prisma/schema.prisma`
- `moda-interact-admin/database/prisma/migrations/20260923150000_arch021_agent_configuration/migration.sql`
- `moda-interact-admin/database/prisma/migrations/20260924103000_arch021_simplify_agent_configuration/migration.sql`
- this task Completion Report

### Validation Reviewed
- Submitted focused Agent Instructions result: 15/15 passed.
- Submitted TypeScript, changed-production-file ESLint, Prisma validation, production build and `git diff --check`: passed.
- Submitted broad-suite failures were inspected as reported and are outside the Agent Instructions changed surface.
- Required pending-category real-database integration validation remains unchecked.
- The supplied review archive contains no installed dependency tree or live PostgreSQL runtime, so dependency-backed validation was not represented as independently rerun by the architect.

### Architecture Conformance
The implementation follows the intended Admin ownership boundary and reuses the existing Commerce prompt/revision/configuration tables rather than introducing duplicate durable state or a private Commerce HTTP API. However, Attempt 1 cannot be accepted while its audit writes violate an accepted database uniqueness constraint, its prompt length validation exceeds the accepted database constraint, and the explicitly required real transaction proof remains incomplete.

### Follow-up
Return the same task to `ready` with `attempt: 1` preserved and the execution claim cleared. The next authorized claim becomes Attempt 2. No downstream task becomes Ready from this review.
