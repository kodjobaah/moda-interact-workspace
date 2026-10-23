---
id: ARCH-047-ADMIN-001
architecture_id: ARCH-047
title: Create the Admin WhatsApp template catalogue
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 20
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-047-DATABASE-001
enables:
  - ARCH-047-ADMIN-002
  - ARCH-047-BACKGROUND-001
created: 2026-10-23
updated: 2026-10-23
---

# Create the Admin WhatsApp template catalogue

## Architecture

`ARCH-047` — `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`; coordinator `moda_architect`. Source snapshot: 23 October 2026, 16:40.

## Objective

Implement one `SUPER_ADMIN`-only WhatsApp Templates screen that creates, views, edits, enables and disables **existing shop-scoped `WhatsAppTemplateVariant` records** as Moda's operational catalogue.

## Context

The table already has the necessary shop/WABA/purpose/language/provider-name/provider-ID/status/enabled columns. The Admin repository uses `AdminShell`, server actions, `requirePlatformAdminPage` and `requirePlatformAdminMutation`, with no existing WhatsApp Templates screen. Creating a template means registering an existing externally approved provider template in Moda for at least one shop; this task does not create a Meta template.

## Scope

- Create an Admin page at `src/app/(protected)/system-controls/whatsapp-templates/page.tsx`; add the System Controls navigation item to `src/components/admin/sidebar.tsx` and corresponding Admin i18n keys.
- Add a repository-local service `src/lib/admin/whatsapp-templates.ts` for paginated read, single-shop CRUD, enable/disable, shop/WABA scoping and `CommerceAuditEvent` writes. Add server-side parsing in `src/lib/admin/whatsapp-template-validation.ts`, a server action `src/app/actions/whatsapp-templates.ts`, and small UI components under `src/components/admin/whatsapp-templates/`.
- Inputs: eligible Shop, provider WABA, purpose (including checkout-recovery), canonical `languageTag`, `providerLanguageCode`, `providerTemplateName`, optional provider template ID, `status`, `enabled`, admin reason. Validate structural formats, supported Shop identity/WABA ownership and local slot uniqueness only; **do not call Meta for approval/category**.
- Derive grouped catalogue display from assigned shop rows, showing current assignments, languages and active status. A new record requires at least one target shop; no separate persistent global master is created.
- Audit every actual mutation using DATABASE-001's new `CommerceAuditAction` values in the same transaction, with `actorAdminId`, `shopId`, `operationId` and redacted bounded before/after metadata. Use existing Admin authorisation and shared structured logger.

## Out of Scope

- No bulk selected/all-shop mutation UI (ADMIN-002), Background template reads (BACKGROUND-001), Prisma table/model redesign, Meta `message_templates` API, external provider template creation, new Shop roles, merchant storefront UI, or global master-template entity.
- No template category preflight; an operator records `APPROVED` locally and remains responsible for provider accuracy.

## Requirements

- [ ] Both protected page and each mutating server action enforce `SUPER_ADMIN`; client-provided shop/actor/provider account state is never trusted by itself.
- [ ] A non-Admin user cannot enumerate cross-tenant templates or mutate any shop's assignment.
- [ ] List/group/paginate by source template identity and shop. Form provides inline errors, success/reload state and explicit enable/disable actions, with breadcrumb to System Controls.
- [ ] Use the configured actual sender WABA; never place access tokens in forms, logs or rendered data.
- [ ] Define one selectable slot `(shopId, providerAccountId, purpose, canonical(languageTag))`. Prevent two simultaneously enabled+APPROVED assignments per slot using per-shop database locking/serialisation; current unique key on name/language is insufficient alone.
- [ ] If an existing slot is ambiguous, reject a silently arbitrary selection and provide a safe, explicitly confirmed correction/update path.
- [ ] A template marked APPROVED is treated as Admin-maintained catalogue state; no Meta category/approval HTTP request occurs while authoring.

## Work Items

- [ ] Build guarded route, navigation and query/pagination service.
- [ ] Implement create/edit/enable/disable and canonical locale/form validation with transactional per-shop slot reconciliation.
- [ ] Reuse CommerceAuditEvent and new typed action enum for atomic write+audit; include reason and previous/updated metadata.
- [ ] Add focused UI, authorisation, duplicate/concurrent-writer, audit, input-validation and WABA-scope tests.

## Interfaces / Contracts

Consumes existing Prisma `WhatsAppTemplateVariant`, `Shop`, configured sender WABA and DATABASE-001 enum on `CommerceAuditEvent`. Produces an Admin-owned read/mutation service for ADMIN-002 and a populated database catalogue for BACKGROUND-001. No new queue/Shared contract.

## Dependencies

- `ARCH-047-DATABASE-001`

## Enables

- `ARCH-047-ADMIN-002`
- `ARCH-047-BACKGROUND-001`

## Acceptance Criteria

- [ ] Admin can register and edit an already-approved Meta template's metadata against a selected Shop, and disable or re-enable a shop's variant.
- [ ] `APPROVED` plus enabled is a local operator-maintained state; no provider metadata call, category field or background verification required.
- [ ] Concurrent Admin saves cannot leave multiple selectable records for one slot; ambiguous pre-existing records are detected, not silently used.
- [ ] Every real mutation has one durable shop/actor/operation/reason/before-after audit within its transaction; denied mutations leave no data change.
- [ ] Readable page with explicit field errors, shop domain rather than opaque shop ID, and current assignment/status displays.

## Validation

- [ ] Focused new Admin read/action/component tests, server-role enforcement tests (including request forgery), slug/locale/schema and concurrency tests.
- [ ] PostgreSQL write+audit transaction test, project-declared build/type/lint as applicable, `git diff --check`.
- [ ] Verify ordinary platform Admin login/access is unaffected and route is linked in navigation.

## Stop Condition

After completing the defined Work Items, Acceptance Criteria and required Validation, record task-isolated parent and implementation worktrees, start-of-attempt synchronisation and relevant commit evidence in the Completion Report; set `status: review`, return control to `moda_architect`, and **STOP**. Do not implement dependent tasks or modify domain `_index.md` files.

## Implementation Notes

Respect `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/task-definition-materialization.md` and `docs/developer-task-workflow.md`. `/moda-task` owns preparation and the canonical claim; never infer worktrees from a previous task or operate in shared/default checkouts. Existing application code has evolved: inspect current implementation immediately before claiming and return cross-domain contract gaps to `moda_architect`. Use the shared structured logger where new runtime domain logging is needed, not a duplicate generic logger. All tasks are portable definitions until materialised in the developer's real workspace.


Additional task-specific guidance:

Prefer existing `src/app/(protected)/system-controls/store-categories`, `src/lib/admin/store-categories.ts` and `src/app/actions/store-categories.ts` conventions. Avoid 300+ line catch-all components: split read, form, mutation and view components as existing Admin UX does. Do not use irreversible delete to disable a template that may be referenced by past messages.

## Completion Report

### Status

Not Started — portable definition; not materialised or claimed.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

Based on `moda-interact-workspace(20261023-164023).zip`; revalidate against launcher-resolved task worktree when execution begins.

### Unresolved Issues

None recorded at definition time.

### Architectural Concerns

None recorded at definition time.

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
