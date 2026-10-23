---
id: ARCH-047-ADMIN-001
architecture_id: ARCH-047
title: Create and import Meta WhatsApp templates in Admin
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

# Create and import Meta WhatsApp templates in Admin

## Architecture

`ARCH-047` — `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`; coordinator `moda_architect`. Source snapshot: 23 October 2026, 16:40.

## Objective

Implement one `SUPER_ADMIN`-only WhatsApp Templates screen that **imports/refreshes existing Meta templates**, distinguishes **new versus updated versus unchanged** items, and creates, views, edits, enables or disables shop-scoped `WhatsAppTemplateVariant` records as Moda's operational catalogue.

## Context

The table has shop/WABA/purpose/language/provider-name/provider-ID/status/enabled columns, but currently lacks imported provider component/category snapshots. DATABASE-001 adds a nullable `metaImportSnapshot` used solely for Admin change detection; it does **not** add runtime template validation. The Admin repository uses `AdminShell`, server actions, `requirePlatformAdminPage` and `requirePlatformAdminMutation`, with no existing WhatsApp Templates screen. Creating a template means registering an existing externally approved provider template in Moda for at least one shop; this task does not create a Meta template.

## Scope

- Create an Admin page at `src/app/(protected)/system-controls/whatsapp-templates/page.tsx`; add the System Controls navigation item to `src/components/admin/sidebar.tsx` and corresponding Admin i18n keys.
- Add a repository-local service `src/lib/admin/whatsapp-templates.ts` for paginated read, single-shop CRUD, enable/disable, shop/WABA scoping and `CommerceAuditEvent` writes. Add `src/lib/admin/meta-whatsapp-template-import.ts` for a server-only, explicitly invoked Meta list operation, and `src/lib/admin/whatsapp-template-import-diff.ts` for deterministic identity/snapshot comparison. Add server-side parsing in `src/lib/admin/whatsapp-template-validation.ts`, a server action `src/app/actions/whatsapp-templates.ts`, and small UI components under `src/components/admin/whatsapp-templates/`.
- Inputs: eligible Shop, provider WABA, purpose (including checkout-recovery), canonical `languageTag`, `providerLanguageCode`, `providerTemplateName`, optional provider template ID, `status`, `enabled`, admin reason. Validate structural formats, supported Shop identity/WABA ownership and local slot uniqueness only. **Only the Admin-initiated Import/Refresh action may read Meta metadata**; manual local catalogue operations and every runtime sending operation use existing database state.
- Add an **Import from Meta / Refresh from Meta** action using the configured WABA and existing securely managed Meta access token, entirely on the server. Fetch the Meta `message_templates` list with `id,name,language,category,status,components`; follow every page with bounded safeguards and reject partial/cyclic/failed pagination. Return sanitised metadata only. Do not create/edit Meta templates or send Meta metadata requests outside explicitly authorised Admin actions.
- Match `(WABA, Meta template ID)` first; then use `(WABA, name, provider language)` for legacy/fallback identity and possible ID replacements. Different IDs with the same name/language are **identity conflicts** until explicitly reconciled; different WABAs cannot be matched. Distinguish Meta template identity from the many shop assignment rows it can have.
- Compare each matched assignment's versioned `metaImportSnapshot` against a normalised current Meta projection of `id/name/language/status/category/components`. Fingerprint must be deterministic despite JSON key order, preserve component/button order, and be insensitive to irrelevant API response ordering. Strip example customer/secret data; cap snapshot size.
- Present **NEW**, **UPDATED**, **UNCHANGED**, **UNTRACKED** (legacy/missing baseline), **IDENTITY_CONFLICT** and **MISSING_FROM_META** (only on complete fetch). For UPDATED, show old-versus-new content/status/category diffs and highlight changed variables/buttons. For conflicts, require manual identity resolution; never create a second active row automatically.
- **Preview first; no writes on fetch.** Import/refresh of a NEW or UPDATED template requires explicit SUPER_ADMIN confirmation and a server-side recheck of current row/fingerprint; unchanged is a no-op. A same-ID update retains the existing Moda `WhatsAppTemplateVariant.id`; imported templates must be assigned to at least one shop (no new global master row). Legacy UNTRACKED rows require explicit first-baseline confirmation, never silently count as NEW.
- Derive grouped catalogue display from assigned shop rows, showing current assignments, languages, active status and provider-import comparison state. A new record requires at least one target shop; no separate persistent global master is created.
- Audit every actual mutation using DATABASE-001's new `CommerceAuditAction` values in the same transaction, with `actorAdminId`, `shopId`, `operationId` and redacted bounded before/after metadata. Use existing Admin authorisation and shared structured logger.

## Out of Scope

- No bulk selected/all-shop mutation UI (ADMIN-002), Background template reads (BACKGROUND-001), Prisma work beyond DATABASE-001, Meta **template create/edit/delete** operations, automatic background Meta polling, new Shop roles, merchant storefront UI or global master-template entity.
- No Meta template category or approval **preflight during a message send**. The Admin import may display Meta status/category for a human to review, but only the locally confirmed `APPROVED` and `enabled` assignment decides runtime eligibility.

## Requirements

- [ ] Both protected page, **import/refresh reads**, and each mutating server action enforce `SUPER_ADMIN`; client-provided shop/actor/provider account state is never trusted by itself.
- [ ] A non-Admin user cannot enumerate cross-tenant templates or mutate any shop's assignment.
- [ ] List/group/paginate by source WABA/template identity and shop. Import UI shows visible NEW/UPDATED/UNCHANGED/UNTRACKED/CONFLICT counts and per-template changes before actions; form provides inline errors, success/reload state and explicit enable/disable with breadcrumb to System Controls.
- [ ] Use the configured actual sender WABA; never place access tokens in forms, logs or rendered data.
- [ ] Define one selectable slot `(shopId, providerAccountId, purpose, canonical(languageTag))`. Prevent two simultaneously enabled+APPROVED assignments per slot using per-shop database locking/serialisation; current unique key on name/language is insufficient alone.
- [ ] If an existing slot is ambiguous, reject a silently arbitrary selection and provide a safe, explicitly confirmed correction/update path.
- [ ] Local `APPROVED` is Admin-maintained catalogue state. Meta listing is invoked **only on explicit Admin Import/Refresh**, never as an implicit validation during ordinary creation, saving, selection or sending. Provider PENDING/REJECTED status cannot be silently promoted into approved enabled recovery assignments.

## Work Items

- [ ] Build guarded route, navigation, paginated catalogue service, and server-only paginated Meta import/refresh service.
- [ ] Implement create/edit/enable/disable and canonical locale/form validation with transactional per-shop slot reconciliation; classify and preview new versus updated provider templates using the import-snapshot fingerprint.
- [ ] Reuse CommerceAuditEvent and new typed action enum for atomic write+audit; include reason and previous/updated metadata.
- [ ] Add focused UI, authorisation, duplicate/concurrent-writer, audit, input-validation and WABA-scope tests; include Meta page-2, API outage, changed body/buttons with identical template ID, same-ID unchanged replay, ID/name collision, and legacy row with null snapshot.

## Interfaces / Contracts

Consumes existing Prisma `WhatsAppTemplateVariant`, its DATABASE-001 nullable `metaImportSnapshot`, `Shop`, configured sender WABA and DATABASE-001 enum on `CommerceAuditEvent`. Provider source is `GET /{WABA_ID}/message_templates` and its paginated `id/name/language/category/status/components` fields, invoked only within this Admin task. Identity and snapshot comparisons are Admin-local code, not a new Shared runtime/queue contract. Produces an Admin-owned read/mutation service for ADMIN-002 and a populated database catalogue for BACKGROUND-001. No new queue/Shared contract.

## Dependencies

- `ARCH-047-DATABASE-001`

## Enables

- `ARCH-047-ADMIN-002`
- `ARCH-047-BACKGROUND-001`

## Acceptance Criteria

- [ ] Admin can fetch existing Meta templates and correctly label a truly NEW template versus an UPDATED same-ID template (including a body/buttons-only edit), UNCHANGED template, UNTRACKED legacy record and identity CONFLICT. It can register, import, refresh, disable or re-enable an assignment for a selected Shop.
- [ ] `APPROVED` plus enabled is local operator-maintained state; no provider metadata call on any runtime send or unrelated Admin mutation. Import snapshot/category is used only for Admin comparison, never as a second runtime validation or eligibility field.
- [ ] Concurrent Admin saves cannot leave multiple selectable records for one slot; ambiguous pre-existing records are detected, not silently used.
- [ ] Every real mutation has one durable shop/actor/operation/reason/before-after audit within its transaction; identical re-imports do not write or create duplicate audit entries; denied mutations leave no data change.
- [ ] Readable page with explicit field errors, shop domain rather than opaque shop ID, current assignment/status displays and an explicit before/after comparison for UPDATED templates.

## Validation

- [ ] Focused new Admin read/action/component tests, server-role enforcement (including import request forgery), local identity/diff/canonical-fingerprint and concurrency tests.
- [ ] PostgreSQL import baseline/refresh+audit transaction test, project-declared build/type/lint as applicable, `git diff --check`.
- [ ] Verify ordinary platform Admin login/access is unaffected and route is linked in navigation.

## Stop Condition

After completing the defined Work Items, Acceptance Criteria and required Validation, record task-isolated parent and implementation worktrees, start-of-attempt synchronisation and relevant commit evidence in the Completion Report; set `status: review`, return control to `moda_architect`, and **STOP**. Do not implement dependent tasks or modify domain `_index.md` files.

## Implementation Notes

Respect `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/task-definition-materialization.md` and `docs/developer-task-workflow.md`. `/moda-task` owns preparation and the canonical claim; never infer worktrees from a previous task or operate in shared/default checkouts. Existing application code has evolved: inspect current implementation immediately before claiming and return cross-domain contract gaps to `moda_architect`. Use the shared structured logger where new runtime domain logging is needed, not a duplicate generic logger. All tasks are portable definitions until materialised in the developer's real workspace.


Additional task-specific guidance:

Prefer existing `src/app/(protected)/system-controls/store-categories`, `src/lib/admin/store-categories.ts` and `src/app/actions/store-categories.ts` conventions. Use approved server-side platform configuration reading for Meta token/WABA; if no safe Admin reader is available, report a narrowly scoped dependency gap instead of calling Meta from the browser or copying secrets. Avoid 300+ line catch-all components: split read, form, mutation and view components as existing Admin UX does. Do not use irreversible delete to disable a template that may be referenced by past messages.

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
