---
id: ARCH-047-ADMIN-006
architecture_id: ARCH-047
title: Confirm Meta template submissions and monitor provider approval
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-047-DATABASE-001
enables: []
created: 2026-10-24
updated: 2026-10-25
---

# Confirm Meta template submissions and monitor provider approval

## Architecture

`ARCH-047` — `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`. Coordinator: `moda_architect`. This is a **defined but not materialised** task until the developer's launcher creates the canonical task branch/worktree.

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

- [ ] Submission records freeze exactly what Admin has reviewed: component content, binding map, source/locale fingerprints and trusted sender account. They are not overwritten by subsequent status reads.
- [ ] Frozen header/body/button binding maps preserve their component/position/`shopBrand.*` semantic keys for each locale; preview, hash verification and submission use the same immutable compiled projection, without substituting merchant brand values.
- [ ] A failed/uncertain provider operation does not cause Admin to create another name/language registration; the existing registration is reconciled before Background retries.
- [ ] A `REJECTED` locale/version cannot be edited or resubmitted with changed content; only Clone as New can correct it. All other approved locale registrations remain intact.
- [ ] Admin status queries remain DB-only and bounded; provider secrets are never returned to client or logs.


All server reads/mutations of template management require the existing authenticated platform-admin boundary; mutations and privileged cross-shop reads require **`SUPER_ADMIN`**, verified server-side (`requirePlatformAdminPage` / `requirePlatformAdminMutation` or repository-equivalent). Reject client-supplied actor identity, WABA ownership, approval and shop eligibility assertions. Persist bounded/redacted audit records using the existing `commerce.CommerceAuditEvent` and ARCH-047 audit enum; do not log tokens, credentials or unnecessary customer/checkout data. Reuse the platform's shared structured logger only for needed semantic logs.


## Work Items

- [ ] Implement trusted sender-WABA lookup, frozen registration creation (including compiled header/body/button binding maps), status/reconcile request and audit in `meta/` service.
- [ ] Build a 20-language submission preview and progress/rejection/drift dashboard with explicit confirmation and no misleading auto-approval.
- [ ] Add idempotency/concurrent submit, auth and provider-identity collision tests with fixture approved locale records.


## Interfaces / Contracts

**Reads:** reviewed `WhatsAppTemplateDefinition`/`Locale.localeAst` prepared Meta projection; its Admin-compiled positional bindings include header/body/button keys and optional `shopBrand.*` references. Never load or freeze `ShopBrand` row values for registration. **Writes:** `WhatsAppTemplateMetaRegistration` with frozen `componentsSnapshot` + `parameterBindingsSnapshot` + `submittedContentHash`, trusted `wabaId`, `providerTemplateName`, `providerLanguageCode` and `submissionState`; bounded `CommerceAuditEvent`. **Reads only:** `WhatsAppTemplateMetaEvent`/registration status and drift for dashboard. Background owns Graph calls and `MetaEvent` status writes. Do not assume the Meta event comes via a Shared-specific ARCH-047 package; the agreed transport is Messaging → existing BullMQ → Background → PostgreSQL.


**Module ownership.** Keep this task modular: put its domain services under `src/lib/admin/whatsapp-templates/meta/`, components under `src/components/admin/whatsapp-templates/meta/`, and its server actions in a task-specific `src/app/actions/whatsapp-template-meta-control.ts`. Avoid a global `whatsapp-templates.ts` catch-all or unrelated edits to sibling modules. Prefer small repository/domain, validation, orchestrator and view components. Only the English authoring task owns the shared navigation/catalogue shell; other tasks provide focused subroutes/panels, not a second editor or shell.


## Dependencies

- `ARCH-047-DATABASE-001` — **the only formal task dependency**. No `ARCH-047-ADMIN-00N`, Background, Messaging or new Shared publication dependency is permitted. Use seeded DB fixtures and injected ports to test independently when upstream/downstream implementations are absent. Status remains Pending until DB001 is confirmed Complete in the canonical task record; do not infer completion from tests alone.

## Enables

None at task-definition time. Completion of this task does not grant permission to start another task or skip an independently required system-test gate.

## Acceptance Criteria

- [ ] React views are composed from separately named, independently testable components; route pages, controller hooks, pure domain helpers, server actions and database services are in separate files with no monolithic screen/action implementation.

- [ ] One confirmed submission creates 20 immutable registration snapshots (one per supported provider locale) in a consistent WABA; repeat submits are no-ops and status polling does not duplicate snapshots or audit.
- [ ] A header variable and a reordered body brand variable are stored with exactly their approved locale-specific positions; a mismatched binding digest prevents submission.
- [ ] Rejected/pending/paused languages display independently, with reason and drift evidence; Meta API success never appears as Meta-approved or automatically published.
- [ ] External Meta templates cannot be imported, and no Admin Graph template create/edit/delete request occurs.
- [ ] Server authorization and transaction concurrency prohibit forged WABA, stale hash, duplicate submit and accidental resubmission of modified content.


## Validation

- [ ] Component/variable digest and trusted WABA identity tests (including header `shopBrand.brandName`, body `shopBrand.logoAltText` and per-language position changes); 20-language registration fixtures; forced partial transaction and concurrent-click tests.
- [ ] Database-only Admin dashboard/action, auth/audit tests with simulated MetaEvent/registration updates from Background; no provider network; typecheck/lint/`git diff --check`.


## Stop Condition

After task-scoped work, acceptance criteria, validation and Completion Report are complete, set `status: review`, return control to `moda_architect` and **STOP**. Do not mark this task Complete yourself, start sibling/Admin/Background tasks, modify `_index.md`, merge branches or push main.

## Implementation Notes

Read `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/task-definition-materialization.md`, `docs/developer-task-workflow.md`, the revised parent ARCH-047 architecture and current Admin repository instructions. Use launcher-prepared dedicated parent/implementation task worktrees and mirrored `task/<TASK_ID>` branches. In the Completion Report record prepared physical worktree isolation, start sync, recursive submodule materialisation, exact test commands/outcomes, changed paths and commits. The implementing agent must not modify `docs/decisions/**/_index.md`, another task, the parent architecture, another repository, or follow-on work. Reuse existing Admin Store Category AST authoring and Merchant Pricing translation UX patterns without copying their domain services or creating a competing generic runtime. Inspect the actual worktree state before implementation; the attached snapshot is not a live Git-branch guarantee.


## Completion Report

### Status

Not Started — portable task definition, not materialised/claimed.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

The consolidated `ARCH-047-DATABASE-001` Attempt 7 model contract is the intended schema; inspect generated Prisma Client and actual accepted database implementation when this task becomes executable. Where the proposed JSONB envelopes are not yet implemented, fixture-based tests use the explicitly documented shape.

### Unresolved Issues

None at definition time. Return any missing persistence capability, provider-account configuration or cross-repository interface problem to `moda_architect` rather than silently changing DB/Background/Messaging ownership.

### Architectural Concerns

None at definition time.


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
