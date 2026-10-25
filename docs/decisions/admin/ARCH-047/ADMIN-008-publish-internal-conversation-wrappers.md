---
id: ARCH-047-ADMIN-008
architecture_id: ARCH-047
title: Approve and activate internal AI and human conversation wrappers
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 20
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-047-DATABASE-001
enables: []
created: 2026-10-24
updated: 2026-10-25
---

# Approve and activate internal AI and human conversation wrappers

## Architecture

`ARCH-047` — `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`. Coordinator: `moda_architect`. This task is materialised in its canonical parent task worktree; the developer has completed implementation Attempt 1 in the dedicated implementation worktree and submitted it for architect review.

## Objective

Provide internal review and explicit activation of prepared, multilingual conversation wrappers for `SHARED`, `AI` and `HUMAN` response sources, without any Meta submission or merchant assignment.

## Context

The adopted ARCH-047 design is **Moda Admin-only authoring**. A saved English source definition and its corresponding language content are immutable: corrections create a different definition using **Clone as New**. There are six Meta recovery purposes (`INITIAL`/`FOLLOW_UP` × `NO_OFFER`/`CODE_OFFER`/`AUTOMATIC_OFFER`) and one internally published `MODA_CONVERSATION_WRAPPER` family with `SHARED`, `AI` and `HUMAN` audiences. No template authored externally in Meta may be adopted.

`ARCH-047-DATABASE-001` defines the eleven-table persistence boundary, including `WhatsAppTemplateDefinition`, `WhatsAppTemplateLocale`, translation Run/Item/Batch/BatchItem, `WhatsAppTemplateMetaRegistration`, `WhatsAppTemplateMetaEvent`, publication Operation/Target and `WhatsAppConversationWrapperActiveSlot`, plus the nullable link to existing shop `WhatsAppTemplateVariant` and existing `CommerceAuditEvent` actions. Database stores technical relations/JSONB but does **not** enforce template lifecycle/business rules. Admin must enforce those rules transactionally. This Admin task never modifies Prisma schema or the existing database migration.

The six Admin tasks have **only `ARCH-047-DATABASE-001` as a formal dependency**. They own separate route/action/service/component modules, use stable documented persistence payloads, and must prove their capability with fixtures or injected dependencies when a sibling Admin/Background implementation is not yet complete. The end-to-end system test, not an artificial task chain, verifies their integration.


## Scope

- Own `wrappers/` module and `/system-controls/whatsapp-templates/wrappers/` route/panel. Consume existing definition/locale records and the **Admin-compiled prepared runtime wrapper projection** in `TemplateLocale.localeAst`; never implement a second editor, translation extraction or AST compiler.
- A wrapper has a required `response.body` insertion slot, optional header/footer, typed shop/customer variables and checkout-aware conditional URL sections. Provide a full example preview using an illustrative AI/human response, with disabled/stale checkout-link sections omitted. The inserted response is authored by AI/human at runtime, **never** stored in the template.
- Enforce application-only publication checks: centrally created template, correct wrapper kind/audience, immutable source/review hashes, all expected 20 reviewed locales and presence of a validated prepared runtime projection. No Meta registration or marketing template approval is required.
- Explicit SUPER_ADMIN action selects activation audience(s): `SHARED` default, optional `AI` and `HUMAN` override. For each audience update `WhatsAppConversationWrapperActiveSlot.definitionId` with an optimistic compare-and-swap `editVersion` and transactional audit; no database business CHECK or second pointer table. Do not overwrite a concurrent newer activation without re-review.
- Show existing versus proposed full wrapper (header, response slot, footer and conditional checkout link) in the selected language with audience, first-published time and rollback/replace impact. A new version is created with Clone as New; changing an active template's content in place is forbidden. An older already-reviewed definition can be reactivated through an explicit audited action without modifying its content.
- Publishing is a platform-level pointer change, **not** copying 20 wrappers into every Shop. Background owns SHARED/AI/HUMAN fallback precedence and final rendering/send eligibility. Admin must not create out-of-window Meta sends or modify the customer checkout.


## Out of Scope

- No Meta template submission/status, per-shop recovery assignments, Background AST rendering, AI generation, human message authorship, moderation or checkout mutations.


## Requirements

- [x] Exactly one row per activated audience is maintained via technical `audience` PK and versioned CAS; semantic audience-kind/approval checks live in Admin.
- [x] No `response.body` insertion slot, invalid projection, unmatched 20 languages or incorrect family prevents activation; existing pointer remains unchanged on failure.
- [x] The global `SHARED` pointer is fallback; optional AI/HUMAN overrides are explicitly selected and the UI shows which audience resolves to which definition.


All server reads/mutations of template management require the existing authenticated platform-admin boundary; mutations and privileged cross-shop reads require **`SUPER_ADMIN`**, verified server-side (`requirePlatformAdminPage` / `requirePlatformAdminMutation` or repository-equivalent). Reject client-supplied actor identity, WABA ownership, approval and shop eligibility assertions. Persist bounded/redacted audit records using the existing `commerce.CommerceAuditEvent` and ARCH-047 audit enum; do not log tokens, credentials or unnecessary customer/checkout data. Reuse the platform's shared structured logger only for needed semantic logs.


## Work Items

- [x] Implement activation eligibility/compare-and-swap and audit service for current pointers in `wrappers/`.
- [x] Create review/activation preview and concurrency/conflict UI without duplicating `authoring/` or `compilation/`.
- [x] Add audited activation/replacement/reactivation and unsafe/invalid projection tests using stubbed compiled locale records.


## Interfaces / Contracts

**Reads:** `WhatsAppTemplateDefinition`/20 reviewed `WhatsAppTemplateLocale` prepared `localeAst` projections and existing `WhatsAppConversationWrapperActiveSlot`. **Writes:** slot `definitionId`, `editVersion`, `updatedByAdminId`, `updatedAt`, optionally definition `publishedAt` for first successful activation, and bounded `CommerceAuditEvent`. No `MetaRegistration`, `PublicationTarget` or `WhatsAppTemplateVariant` writes. Consumer `BACKGROUND-005` reads the prepared projection only; no Background authoring AST parser is required.


**Module ownership.** Keep this task modular: put its domain services under `src/lib/admin/whatsapp-templates/wrappers/`, components under `src/components/admin/whatsapp-templates/wrappers/`, and its server actions in a task-specific `src/app/actions/whatsapp-template-wrapper-publication.ts`. Avoid a global `whatsapp-templates.ts` catch-all or unrelated edits to sibling modules. Prefer small repository/domain, validation, orchestrator and view components. Only the English authoring task owns the shared navigation/catalogue shell; other tasks provide focused subroutes/panels, not a second editor or shell.


## Dependencies

- `ARCH-047-DATABASE-001` — **the only formal task dependency**. No `ARCH-047-ADMIN-00N`, Background, Messaging or new Shared publication dependency is permitted. Use seeded DB fixtures and injected ports to test independently when upstream/downstream implementations are absent. Status remains Pending until DB001 is confirmed Complete in the canonical task record; do not infer completion from tests alone.

## Enables

None at task-definition time. Completion of this task does not grant permission to start another task or skip an independently required system-test gate.

## Acceptance Criteria

- [x] Platform admin can activate SHARED/AI/HUMAN slots independently, preview fully translated wrapper content and see the effective override/fallback selection.
- [x] Stale CAS, wrong kind/audience or incomplete translations cannot silently replace a current wrapper; no Meta call is made.
- [x] Activating new or previous immutable definition changes pointers/audit only; already sent AI/human response contents and checkout records are untouched.


## Validation

- [x] Schema-backed CAS race/replay tests, semantic eligibility and complete-locale fixture tests, exact preview/conditional section UI tests.
- [x] Auth/audit/rollback and no-provider-network tests; declared lint/typecheck and `git diff --check`.


## Stop Condition

After task-scoped work, acceptance criteria, validation and Completion Report are complete, set `status: review`, return control to `moda_architect` and **STOP**. Do not mark this task Complete yourself, start sibling/Admin/Background tasks, modify `_index.md`, merge branches or push main.

## Implementation Notes

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/task-definition-materialization.md`, `docs/developer-task-workflow.md`, the revised parent ARCH-047 architecture and current Admin repository instructions. Use launcher-prepared dedicated parent/implementation task worktrees and mirrored `task/<TASK_ID>` branches. In the Completion Report record prepared physical worktree isolation, start sync, recursive submodule materialisation, exact test commands/outcomes, changed paths and commits. The implementing agent must not modify `docs/decisions/**/_index.md`, another task, the parent architecture, another repository, or follow-on work. Reuse existing Admin Store Category AST authoring and Merchant Pricing translation UX patterns without copying their domain services or creating a competing generic runtime. Inspect the actual worktree state before implementation; the attached snapshot is not a live Git-branch guarantee.


## Completion Report

### Status

Complete — developer-executed Attempt 1. The Admin implementation was committed as `30cc9ef` (`feat(arch-047-admin-008)`) and pushed to `origin/task/ARCH-047-ADMIN-008`. Developer self-review passed and the developer explicitly authorized completion; the attempt number remains `1`. This task is complete without merging its task branch to `main`.

### Files Changed

Implementation repository: `moda-interact-admin` — 21 files in commit `30cc9ef`:

- `package.json`
- `scripts/test-arch047-admin-wrappers-postgres.mjs`
- `src/app/(protected)/system-controls/whatsapp-templates/wrappers/page.tsx`
- `src/app/actions/whatsapp-template-wrapper-publication.ts`
- `src/components/admin/whatsapp-templates/wrappers/use-wrapper-publication.ts`
- `src/components/admin/whatsapp-templates/wrappers/wrapper-activation-confirmation.tsx`
- `src/components/admin/whatsapp-templates/wrappers/wrapper-active-slot-summary.tsx`
- `src/components/admin/whatsapp-templates/wrappers/wrapper-audience-selector.tsx`
- `src/components/admin/whatsapp-templates/wrappers/wrapper-before-after-preview.tsx`
- `src/components/admin/whatsapp-templates/wrappers/wrapper-publication-workspace.tsx`
- `src/lib/admin/whatsapp-templates/wrappers/contracts.ts`
- `src/lib/admin/whatsapp-templates/wrappers/eligibility.ts`
- `src/lib/admin/whatsapp-templates/wrappers/preview.ts`
- `src/lib/admin/whatsapp-templates/wrappers/reads.ts`
- `src/lib/admin/whatsapp-templates/wrappers/repository.ts`
- `src/lib/admin/whatsapp-templates/wrappers/service.ts`
- `tests/fixtures/arch047-wrapper-fixture.ts`
- `tests/integration/arch047-template-wrappers.postgres.test.ts`
- `tests/unit/arch047-template-wrappers-components.test.tsx`
- `tests/unit/arch047-template-wrappers-service.test.ts`
- `tests/unit/arch047-template-wrappers.test.ts`

Only this canonical parent task definition is changed by the review-submission patch. No `_index.md`, parent architecture or other repository implementation changes are included in that patch.

### Work Completed

- Implemented a dedicated SUPER_ADMIN-only wrapper publication route, read model and mutation action; the server determines the actor identity and does not accept client-supplied authorisation assertions.
- Reused persisted, compiled wrapper projections and enforced immutable source/review hashes, family/audience compatibility, the required `response.body` insertion slot and complete, validated 20-language projections with protected ShopBrand variables.
- Implemented independent `SHARED`, `AI`, and `HUMAN` active-slot activation with the existing `WhatsAppConversationWrapperActiveSlot` table; preview exposes `SHARED` fallback for unset audience-specific overrides.
- Implemented optimistic `editVersion` compare-and-swap, idempotent replay, replacement and reactivation of previously approved immutable definitions within a serializable transaction; first-publication state and bounded `CommerceAuditEvent` persist with the pointer or roll back together.
- Added before/after multilingual preview, conditional checkout-link suppression, first-publication display, deliberate confirmation with a reason, audit-history display and stale-pointer conflict handling.
- Added focused service/eligibility, UI component and disposable PostgreSQL integration tests; no Meta publication integration, checkout writes, per-shop copying or Background runtime changes were introduced.

### Validation Results

Recorded in the developer's 2026-10-25 validation terminal log (`typescript(20261025-182106)`) and follow-up implementation Git log (`typescript(20261025-183601)`):

- `npm run prisma:generate` — **PASS** after materialising the Admin `database/` submodule; Prisma Client `6.19.3` generated. An earlier attempt failed because `database/prisma/schema.prisma` was absent before submodule initialisation.
- `git apply --check --whitespace=error-all ~/Downloads/ARCH-047-ADMIN-008-attempt1.patch` followed by `git apply --whitespace=error-all ...` — **PASS on the subsequent attempt**; first attempt could not locate the patch in `~/Downloads`.
- `npm run test:arch047-admin-wrappers:unit` — **PASS, 7/7**. Covers approval/eligibility checks, protected projections, non-SUPER_ADMIN rejection, immutable locale data, CAS, replay and audit rollback.
- `npm run test:arch047-admin-wrappers:components` — **PASS, 3/3**. Covers audience/fallback display, full before/after preview with conditional URL and deliberate confirmation/conflict handling.
- `npm run test:arch047-admin-wrappers:postgres` — **PASS, 3/3**, disposable PostgreSQL. Covers independent audience slots, actual DB CAS concurrency, replay/replacement/reactivation, audit writes and transaction rollback.
- `npm run lint` — **PASS, 0 errors, 1 warning** in `database/eslint.config.mjs` (`import/no-anonymous-default-export`, outside the new wrapper implementation).
- `npm run build` — **PASS** with Prisma generation, Next.js compilation, TypeScript checks and page generation. Non-blocking BullMQ dynamic-dependency and optional `@valkey/valkey-glide` warnings originate from queue-monitor/merchant-support imports.
- `git diff --check` — command is present in the patch-application transcript with no whitespace error reported. The review-submission patch is separately checked for whitespace and clean application before handoff.
- No Meta API/client or provider network calls appear in the added wrapper activation code. Unit and PostgreSQL test execution exercises the path without a provider dependency; the supplied test log does not show a distinct network-spy/interception test.
- Git: implementation commit `30cc9ef` created with **21 files changed, 1,217 insertions, 1 deletion**, followed by successful push of `task/ARCH-047-ADMIN-008` to `origin` in `moda-interact-admin`.
- Independent developer self-review rerun from the canonical implementation worktree: `npm run test:arch047-admin-wrappers:unit` **PASS, 7/7**; `npm run test:arch047-admin-wrappers:components` **PASS, 3/3**; `npm run test:arch047-admin-wrappers:postgres` **PASS, 3/3** against disposable PostgreSQL; `npm run lint` **PASS, 0 errors, 1 existing warning** in `database/eslint.config.mjs`; `npx tsc --noEmit` **PASS**; `git diff --check origin/main...HEAD` **PASS**. Search of the added wrapper action/service/UI paths found no provider-network call patterns.

### Deviations

No task-scope deviation reported. Initial Prisma generation required database-submodule setup; the initial patch application failed because the patch had not yet been placed in `~/Downloads`. Both conditions were resolved before the successful tests/build. The terminal capture file `typescript` was untracked in the pre-commit status and was not included in implementation commit `30cc9ef`.

### Assumptions

The accepted `ARCH-047-DATABASE-001` data model and existing Admin authoring/compilation projections are the contracts for this implementation. The six Admin tasks remain independently scoped to their single formal database dependency; no additional task dependency was introduced.

### Unresolved Issues

No failing implementation tests are recorded. The canonical task's **Execution Ownership Amendment** records the dedicated parent and implementation worktree paths, task branches, initial synchronization and claim. The uploaded validation/commit logs do **not** include the full launcher-preparation packet or recursive-submodule/start-of-attempt synchronization transcript; the architect must confirm that evidence against the launcher/worktree policy before acceptance. The supplied logs also do not establish a clean post-commit Git status.

Developer reconciliation update (2026-10-25): the evidence gaps noted above are resolved for this self-review. Canonical parent and implementation worktree registrations, expected task branches, matching local/remote refs, initialized recursive database submodule, and clean post-validation status were independently verified. The focused unit, component and PostgreSQL suites, lint, TypeScript check and committed diff check were rerun successfully. One existing, out-of-scope database ESLint warning remains.

### Architectural Concerns

No new database tables, shared contracts, Meta submission calls, merchant assignments or Background delivery semantics were introduced. Runtime fallback precedence and final WhatsApp send eligibility remain Background responsibilities. This is submitted for architect verification, not architect acceptance.


## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.

## Execution Ownership Amendment

- Date: 2026-10-25.
- Change: The developer explicitly invoked `/moda_developer_create` for this Ready agent-owned task. Execution ownership is transferred to the developer, and completion is set to developer review.
- Preserved: `assigned_agent: moda_admin`, coordinator, repository, dependency, task scope, acceptance criteria and validation requirements.
- Dependency check: `ARCH-047-DATABASE-001` is `complete` in its canonical task record.
- Claim: Attempt 1 is claimed by `developer` at `2026-10-25T18:14:30Z` after canonical worktree preparation and synchronization.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-047-ADMIN-008`, branch `task/ARCH-047-ADMIN-008`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-047-ADMIN-008`, branch `task/ARCH-047-ADMIN-008`, created from current Admin `origin/main` because no ADMIN-008 task branch existed locally or remotely.
- No implementation changes were made during preparation. No branch was merged into `main`.

## Developer Self-Review Passed

### Review Decision

Attempt 1 passes developer self-review. Required Work Items, Acceptance Criteria and task validation are complete; the implementation is committed and pushed, focused suites pass, and canonical worktree and dependency evidence has been reconciled. Completion remains pending because `completion_mode: developer`.

### Evidence

- Unit: wrapper domain/service suite, 7/7 passing.
- Components: wrapper UI suite, 3/3 passing.
- PostgreSQL: disposable schema-backed suite, 3/3 passing, including concurrent CAS and rollback.
- Repository checks: lint passed with one existing out-of-scope warning; TypeScript and committed diff whitespace checks passed. The recorded production build passed.
- Isolation: parent and implementation task worktrees are registered on the canonical task branch, their local/remote refs match, the recursive database submodule is initialized, and both worktrees are clean after validation.
- Scope: no provider-network calls were found in the new wrapper paths; no Meta submission, merchant assignment, checkout mutation or Background behavior was added.

### State Transition

Transition to `complete` with `executor: null`, `claimed_at: null`, and Attempt 1 unchanged. No branch was merged to `main`.

## Developer Completion Decision

- Date: 2026-10-25
- Decision: The developer explicitly invoked `/moda_developer_update ARCH-047-ADMIN-008 complete` after the durable passing self-review.
- Accepted attempt: 1; unchanged.
- Implementation: Commit `30cc9ef6e6eb5df90e29214051918d314894164d` is committed and pushed on `task/ARCH-047-ADMIN-008`.
- State: `complete`, `executor: null`, `claimed_at: null`.
- Dependency frontier: No active task has `ARCH-047-ADMIN-008` in its explicit `depends_on`; no downstream task state required adjustment.
- Branch policy: No task branch was merged to or pushed to `main`.
