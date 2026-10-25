---
id: ARCH-047-ADMIN-006
architecture_id: ARCH-047
title: Confirm Meta template submissions and monitor provider approval
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 20
executor: developer
claimed_at: 2026-10-25T16:05:41Z
attempt: 1
depends_on:
  - ARCH-047-DATABASE-001
enables: []
created: 2026-10-24
updated: 2026-10-25
---

# Confirm Meta template submissions and monitor provider approval

## Architecture

`ARCH-047` — `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`. Coordinator: `moda_architect`. The task has been materialised and claimed through the developer workflow; the task-specific worktree paths are recorded in the Completion Report.

## Objective

Provide the privileged **submission confirmation and approval dashboard** for already compiled Moda-authored Meta recovery templates, leaving all provider network requests and event interpretation to Background.

## Context

The adopted ARCH-047 design is **Moda Admin-only authoring**. A saved English source definition and its corresponding language content are immutable: corrections create a different definition using **Clone as New**. There are six Meta recovery purposes (`INITIAL`/`FOLLOW_UP` × `NO_OFFER`/`CODE_OFFER`/`AUTOMATIC_OFFER`) and one internally published `MODA_CONVERSATION_WRAPPER` family with `SHARED`, `AI` and `HUMAN` audiences. No template authored externally in Meta may be adopted.

`ARCH-047-DATABASE-001` defines the eleven-table persistence boundary, including `WhatsAppTemplateDefinition`, `WhatsAppTemplateLocale`, translation Run/Item/Batch/BatchItem, `WhatsAppTemplateMetaRegistration`, `WhatsAppTemplateMetaEvent`, publication Operation/Target and `WhatsAppConversationWrapperActiveSlot`, plus the nullable link to existing shop `WhatsAppTemplateVariant` and existing `CommerceAuditEvent` actions. Database stores technical relations/JSONB but does **not** enforce template lifecycle/business rules. Admin must enforce those rules transactionally. This Admin task never modifies Prisma schema or the existing database migration.

The six Admin tasks have **only `ARCH-047-DATABASE-001` as a formal dependency**. They own separate route/action/service/component modules, use stable documented persistence payloads, and must prove their capability with fixtures or injected dependencies when a sibling Admin/Background implementation is not yet complete. The end-to-end system test, not an artificial task chain, verifies their integration.


## Scope

- Own `meta/` module and `/system-controls/whatsapp-templates/[definitionId]/meta/` route with per-language provider status dashboard.
- Preserve the prepared compiler's **header as well as body/button positional variable bindings**, including canonical `shopBrand.*` identifiers where supported. The registration snapshot contains semantic binding metadata, never merchant-specific `ShopBrand` values; `ShopBrand` images represented as text URL variables do not create media-header components.
- Read the definition and all 20 reviewed locale `localeAst.prepared` projections (English included at initial save) and show exactly what will be sent for each provider language code. Confirm that each submitted language has one unambiguous **provider account WABA** from trusted `messaging.sender` configuration (not browser payload), immutable name/category/components and matching frozen variable bindings/content digests; any unsupported WABA/locale/Meta category fails before submission.
- Require an explicit `SUPER_ADMIN` submission confirmation after preview. Transactionally create idempotent `WhatsAppTemplateMetaRegistration` rows (per WABA, name, provider-language identity) with frozen `componentsSnapshot`, `parameterBindingsSnapshot`, `submittedContentHash`, category and `submissionState=READY_TO_SUBMIT` (or the agreed literal). Persist request/audit evidence; **no Graph API call from Admin** and no template editing endpoint. `BACKGROUND-003` subsequently claims and submits these registration records asynchronously via Meta's create endpoint.
- Display `READY_TO_SUBMIT`, `SUBMITTING`, `PENDING`, `APPROVED`, `REJECTED`, `PAUSED`, `DISABLED`, unknown/failure/retry states based on persisted registrations/events, distinguishing transport submission from approval. UI periodically reads while active, may be revisited, and never invents approval based on submission success.
- Provide a bounded **Reconcile status** request that flags a registration for Background reconciliation using existing durable state/approved work handoff; Admin must not fetch external templates or call Meta directly. Allow retry of **technical uncertain submissions only** after Background reconciliation, never in-place content correction of a rejected template. Clone as New is the only content-correction action.
- Show Meta status events/rejection reason and provider drift warning separately; a provider-status webhook never changes source content, snapshots or merchant assignments. No external template import/registration, no automatic publication. Prevent double-confirmation and stale confirmed content.


### Required React component decomposition

Use a thin protected Server Component route, with **separate** client components under `src/components/admin/whatsapp-templates/meta/`:

- `MetaSubmissionReview` — read-only compiled components and current WABA/language information before confirming.
- `MetaSubmissionConfirmation` — explicit irreversible submit action, duplicate-click disable and error state.
- `MetaApprovalSummary` — overall status counters, clearly separating submitted from approved.
- `MetaLocaleStatusTable` — per-language provider status, rejection reason and retry/reconciliation history.
- `MetaDriftNotice` — provider-content drift/mismatch and blocked eligibility explanations.

Use a `useMetaTemplateStatus` controller hook for bounded status refresh and stale-request handling (do not poll continuously after the admin selects a particular record). Split WABA resolution, payload fingerprint validation, registration snapshot transaction, status read-model queries and audit into **distinct server-only files** in `src/lib/admin/whatsapp-templates/meta/`. The action is a thin authorised adapter; React components never invoke Graph API or access PostgreSQL directly. Reuse already-compiled read-only preview data, not an independent AST compiler.

## Out of Scope

- Background Meta Graph API client, webhook signature validation, BullMQ consumption, app/provider polling, translation or reconstruction, shop publication, template content mutation, new Shared event contracts.


## Requirements

- [x] Submission records freeze exactly what Admin has reviewed: component content, binding map, source/locale fingerprints and trusted sender account. They are not overwritten by subsequent status reads.
- [x] Frozen header/body/button binding maps preserve their component/position/`shopBrand.*` semantic keys for each locale; preview, hash verification and submission use the same immutable compiled projection, without substituting merchant brand values.
- [x] A failed/uncertain provider operation does not cause Admin to create another name/language registration; the existing registration is reconciled before Background retries.
- [x] A `REJECTED` locale/version cannot be edited or resubmitted with changed content; only Clone as New can correct it. All other approved locale registrations remain intact.
- [x] Admin status queries remain DB-only and bounded; provider secrets are never returned to client or logs.


All server reads/mutations of template management require the existing authenticated platform-admin boundary; mutations and privileged cross-shop reads require **`SUPER_ADMIN`**, verified server-side (`requirePlatformAdminPage` / `requirePlatformAdminMutation` or repository-equivalent). Reject client-supplied actor identity, WABA ownership, approval and shop eligibility assertions. Persist bounded/redacted audit records using the existing `commerce.CommerceAuditEvent` and ARCH-047 audit enum; do not log tokens, credentials or unnecessary customer/checkout data. Reuse the platform's shared structured logger only for needed semantic logs.


## Work Items

- [x] Implement trusted sender-WABA lookup, frozen registration creation (including compiled header/body/button binding maps), status/reconcile request and audit in `meta/` service.
- [x] Build a 20-language submission preview and progress/rejection/drift dashboard with explicit confirmation and no misleading auto-approval.
- [x] Add idempotency/concurrent submit, auth and provider-identity collision tests with fixture approved locale records.


## Interfaces / Contracts

**Reads:** reviewed `WhatsAppTemplateDefinition`/`Locale.localeAst` prepared Meta projection; its Admin-compiled positional bindings include header/body/button keys and optional `shopBrand.*` references. Never load or freeze `ShopBrand` row values for registration. **Writes:** `WhatsAppTemplateMetaRegistration` with frozen `componentsSnapshot` + `parameterBindingsSnapshot` + `submittedContentHash`, trusted `wabaId`, `providerTemplateName`, `providerLanguageCode` and `submissionState`; bounded `CommerceAuditEvent`. **Reads only:** `WhatsAppTemplateMetaEvent`/registration status and drift for dashboard. Background owns Graph calls and `MetaEvent` status writes. Do not assume the Meta event comes via a Shared-specific ARCH-047 package; the agreed transport is Messaging → existing BullMQ → Background → PostgreSQL.


**Module ownership.** Keep this task modular: put its domain services under `src/lib/admin/whatsapp-templates/meta/`, components under `src/components/admin/whatsapp-templates/meta/`, and its server actions in a task-specific `src/app/actions/whatsapp-template-meta-control.ts`. Avoid a global `whatsapp-templates.ts` catch-all or unrelated edits to sibling modules. Prefer small repository/domain, validation, orchestrator and view components. Only the English authoring task owns the shared navigation/catalogue shell; other tasks provide focused subroutes/panels, not a second editor or shell.


## Dependencies

- `ARCH-047-DATABASE-001` — **the only formal task dependency**. No `ARCH-047-ADMIN-00N`, Background, Messaging or new Shared publication dependency is permitted. Use seeded DB fixtures and injected ports to test independently when upstream/downstream implementations are absent. Status remains Pending until DB001 is confirmed Complete in the canonical task record; do not infer completion from tests alone.

## Enables

None at task-definition time. Completion of this task does not grant permission to start another task or skip an independently required system-test gate.

## Acceptance Criteria

- [x] React views are composed from separately named, independently testable components; route pages, controller hooks, pure domain helpers, server actions and database services are in separate files with no monolithic screen/action implementation.

- [x] One confirmed submission creates 20 immutable registration snapshots (one per supported provider locale) in a consistent WABA; repeat submits are no-ops and status polling does not duplicate snapshots or audit.
- [x] A header variable and a reordered body brand variable are stored with exactly their approved locale-specific positions; a mismatched binding digest prevents submission.
- [x] Rejected/pending/paused languages display independently, with reason and drift evidence; Meta API success never appears as Meta-approved or automatically published.
- [x] External Meta templates cannot be imported, and no Admin Graph template create/edit/delete request occurs.
- [x] Server authorization and transaction concurrency prohibit forged WABA, stale hash, duplicate submit and accidental resubmission of modified content.


## Validation

- [x] Component/variable digest and trusted WABA identity tests (including header `shopBrand.brandName`, body `shopBrand.logoAltText` and per-language position changes); 20-language registration fixtures; forced partial transaction and concurrent-click tests.
- [x] Database-only Admin dashboard/action, auth/audit tests with simulated MetaEvent/registration updates from Background; no provider network; typecheck/lint/`git diff --check`.


## Stop Condition

After task-scoped work, acceptance criteria, validation and Completion Report are complete, set `status: review`, return control to `moda_architect` and **STOP**. Do not mark this task Complete yourself, start sibling/Admin/Background tasks, modify `_index.md`, merge branches or push main.

## Implementation Notes

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/task-definition-materialization.md`, `docs/developer-task-workflow.md`, the revised parent ARCH-047 architecture and current Admin repository instructions. Use launcher-prepared dedicated parent/implementation task worktrees and mirrored `task/<TASK_ID>` branches. In the Completion Report record prepared physical worktree isolation, start sync, recursive submodule materialisation, exact test commands/outcomes, changed paths and commits. The implementing agent must not modify `docs/decisions/**/_index.md`, another task, the parent architecture, another repository, or follow-on work. Reuse existing Admin Store Category AST authoring and Merchant Pricing translation UX patterns without copying their domain services or creating a competing generic runtime. Inspect the actual worktree state before implementation; the attached snapshot is not a live Git-branch guarantee.


## Completion Report

### Status

Ready for Review — developer execution Attempt 1, claimed 2026-10-25T16:05:41Z. The final implementation incorporates code patch revisions through Attempt 3; these are **not** three separate task claims. `status: review` is a handoff, **not** architect acceptance or developer completion.

### Files Changed

Implementation repository `moda-interact-admin` — 28 files committed on `task/ARCH-047-ADMIN-006`:

- `package.json`; `package-lock.json` (Shared package alignment and test scripts).
- `scripts/test-arch047-admin-meta-postgres.mjs`.
- `src/app/(protected)/system-controls/whatsapp-templates/[definitionId]/meta/page.tsx`.
- `src/app/actions/whatsapp-template-meta-control.ts`.
- `src/components/admin/whatsapp-templates/meta/`: `meta-approval-summary.tsx`, `meta-drift-notice.tsx`, `meta-locale-status-table.tsx`, `meta-submission-confirmation.tsx`, `meta-submission-review.tsx`, `meta-template-dashboard.tsx`, `use-meta-template-status.ts`.
- `src/lib/admin/whatsapp-templates/meta/`: `audit.ts`, `contracts.ts`, `languages.ts`, `reads.ts`, `reconcile.ts`, `repository.ts`, `sender.ts`, `snapshot.ts`, `status.ts`, `submission.ts`, `technical-retry.ts`.
- `tests/helpers/arch047-template-meta-fixture.ts`.
- `tests/integration/arch047-template-meta.postgres.test.ts`.
- `tests/unit/`: `arch047-template-meta-components.test.mjs`, `arch047-template-meta-service.test.ts`, `arch047-template-meta-snapshots.test.ts`.

Parent-workspace change for submission: **this task file only**. Do not stage or modify any domain `_index.md`, parent architecture, or implementation submodule gitlink.

### Work Completed

- Implemented privileged DB-only Meta submission preview, using the existing authoring AST compiler and frozen `localeAst.prepared` projection. All 20 supported provider languages, trusted sender WABA, source/locale content fingerprints, immutable component snapshots and positional header/body/button bindings are checked before submission. Merchant `ShopBrand` values are not frozen.
- Implemented serializable, atomic registration creation with exact-identity replay and conflict handling; only one set of 20 `READY_TO_SUBMIT` registrations is created for a confirmed content digest. Audits are committed in the same transaction; a forced audit failure rolls back registrations.
- Implemented a thin, server-authorised action and protected route, composed from separate preview, confirmation, summary, locale status, drift and status-refresh UI components. Provider submission state is displayed independently from Meta approval; polling reads only stored registration and event state.
- Implemented bounded reconciliation and tightly gated technical retry intent persisted for Background, with no Admin Graph API call, no external-template adoption and no rejected-content mutation.
- Added injected-port unit tests, UI-structure test and disposable PostgreSQL integration tests covering concurrent confirmation, repeat submission, stale digests, WABA spoofing, full transaction rollback, event history, provider status, drift and reconciliation audit.
- Refined the previous implementation patch revisions to align Admin's published Shared dependency with its language export, correct the test loader, resolve new ESLint findings and fix the PostgreSQL fixture's explicit database-port typing.

### Validation Results

Evidence source: developer's attached terminal transcript `typescript(20261025-170412)` and the accompanying combined worktree archive, captured 2026-10-25. Results below were observed in that environment, not rerun on the developer's macOS environment by this reviewer.

- `git apply --check --whitespace=error-all "$PATCH"` — succeeded for the Attempt 3 incremental correction (no reported error).
- `git apply --whitespace=error-all "$PATCH"` — succeeded; `git diff --check` — no errors reported.
- `npm run test:arch047-admin-meta:unit` — 12/12 behavioural tests and 1/1 UI-structure test passed; Prisma Client 6.19.3 generated by the script prehook.
- `npm run test:arch047-admin-meta:postgres` — 2/2 disposable PostgreSQL integration tests passed; script reported `PASS ARCH-047 ADMIN-006 disposable PostgreSQL`.
- `npx tsc --noEmit` — no TypeScript diagnostics in the captured command sequence.
- `npm run lint` — 0 errors; 1 warning in the pre-existing `database/eslint.config.mjs` (anonymous default export).
- Commit/push shown in transcript: `0ea4128` (`feat(arch-047-admin-006)`) was pushed to `origin/task/ARCH-047-ADMIN-006` in `moda-interact-admin`.
- No full integrated Meta Graph API/system test is claimed; provider operations belong to Background and terminal system testing is a separate architectural gate.

### Deviations

No scope expansion into Prisma migrations, Meta Graph API, external template imports, or Background processing. Package/lockfile alignment and test-runner fixes were required to validate the Admin task.

### Assumptions

- The completed `ARCH-047-DATABASE-001` Prisma model/migration in the supplied workspace is the accepted persistence contract (task frontmatter reads `status: complete`).
- Background consumes durable registration/reconciliation/retry records and records provider events; this Admin task does not claim that cross-service consumption has passed end-to-end validation.

### Unresolved Issues

- **Start-of-attempt worktree preparation evidence needs to be attached or confirmed for architect review.** The supplied transcript and archive identify both task-specific worktree paths and the implementation branch, but do not contain the launcher's prepared execution packet proving parent/implementation synchronization and recursive submodule preparation. Those details are marked unverified below rather than invented.
- The parent task/report branch still requires the developer to apply, commit and push this documentation-only review-submission patch. Until then the durable task branch remains `in_progress` in the uploaded snapshot.
- A local untracked `typescript` terminal log appears in the implementation repository's pre-commit `git status`; it was not in the reported implementation commit. Do not stage it as task code.

### Architectural Concerns

Background owns provider submission, reconciliation and event interpretation; independent system testing must still verify the cross-repository workflow. This does not add a formal dependency to the present Admin task.

### Git / VCS

Task branch: `task/ARCH-047-ADMIN-006` (mirrored task-branch contract).

Physical worktree isolation (as far as the uploaded evidence supports):

- Canonical workspace root: **not supplied in the terminal evidence; verify from launcher packet**.
- Parent worktree reported by the archive helper: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-047-ADMIN-006`.
- Parent branch: `task/ARCH-047-ADMIN-006` expected by task metadata; **not directly shown by a parent-worktree Git command**.
- Implementation worktree reported by the archive helper: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-047-ADMIN-006`.
- Implementation branch: `task/ARCH-047-ADMIN-006` confirmed by `git status` / commit / push transcript.
- Shared workspace checkout switched/mutated for task work: **not shown; launcher evidence required**.
- Shared implementation checkout switched/mutated for task work: **not shown; launcher evidence required**.
- Another task worktree reused: **not shown; launcher evidence required**.

Start-of-attempt synchronization: **not captured** in supplied transcript; verify from prepared execution packet whether parent task branch and implementation task branch were fast-forwarded and each incorporated `origin/main`. Recursive submodule preparation likewise requires the packet.

Implementation repository:

- Repository: `moda-interact-admin`.
- Commit: `0ea4128` (`feat(arch-047-admin-006)`).
- Remote branch: `origin/task/ARCH-047-ADMIN-006`.
- Pushed: **yes**, confirmed by transcript.

Parent workspace:

- Task file: `docs/decisions/admin/ARCH-047/ADMIN-006-submit-and-monitor-meta-template-approvals.md`.
- Commit: **pending developer application/commit of this patch**.
- Remote branch: `origin/task/ARCH-047-ADMIN-006` — **push pending/not verified**.
- Implementation submodule gitlink staged: **no change included in this documentation-only patch**.

Merged to implementation `main`: no merge shown. Merged to workspace `main`: no merge shown.

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

- Date: 2026-10-25
- Change: The developer explicitly invoked `/moda_developer_create` for this Ready agent-owned task. Execution ownership is transferred to the developer, and completion is set to developer review.
- Preserved: `assigned_agent: moda_admin`, coordinator, repository, dependency, task scope, acceptance criteria and validation requirements.
- Claim state: This amendment does not claim an implementation attempt; the canonical launcher records the claim after dependency and worktree preparation.
