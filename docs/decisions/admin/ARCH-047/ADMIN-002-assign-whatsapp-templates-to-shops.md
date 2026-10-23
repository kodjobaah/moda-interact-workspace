---
id: ARCH-047-ADMIN-002
architecture_id: ARCH-047
title: Assign and update WhatsApp templates across shops
task_kind: implementation
domain: admin
repository: moda-interact-admin
assigned_agent: moda_admin
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-047-ADMIN-001
enables:
  - ARCH-047-SYSTEM-TEST-001
created: 2026-10-23
updated: 2026-10-23
---

# Assign and update WhatsApp templates across shops

## Architecture

`ARCH-047` — `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`; coordinator `moda_architect`. Source snapshot: 23 October 2026, 16:40.

## Objective

Extend the WhatsApp Templates Admin screen with explicit **Assign to one / selected / all shops** and **Update one / selected / all shops** operations using the existing per-shop variant rows.

## Context

The database has no global template entity. A source template is an existing `WhatsAppTemplateVariant` row with an optional last-import Meta snapshot; its metadata and confirmed snapshot can be propagated as an assignment for other shops. ADMIN-001 distinguishes new provider templates from provider changes before any write. “Update all” must target the stable WABA/purpose/canonical-language **slot**, not a mutable provider template name, so a previous shop-specific override is included when the platform administrator deliberately chooses a global overwrite.

## Scope

- Add `src/lib/admin/whatsapp-template-assignments.ts` for server-owned target-scope resolution, affected-shop preview, bounded idempotent batch writes and audit. Use the catalogue service from ADMIN-001, not a second independent template-mutation implementation.
- Add `src/app/actions/whatsapp-template-assignments.ts` with `SUPER_ADMIN` validation on preview and mutation. Include preview/confirmation UI under `src/components/admin/whatsapp-templates/` (e.g. `assignment-preview.tsx`, `merchant-assignments.tsx`) on the existing catalogue page.
- Scopes: one specified eligible shop; a bounded explicit selection of current eligible shops; or **all currently eligible shops**. Eligibility: `Shop.status=ACTIVE`; Woo platform requires `WooCommerceInstallation.status=ACTIVE`. Shop recovery entitlements remain separate from template assignment.
- Show the exact shop count and platform breakdown before confirmation, separating **new assignment** (no existing slot), **update of the same Meta template** (same provider identity, changed snapshot), **unchanged** (no write), **untracked legacy** (explicit first-baseline decision), **individual override** (explicit overwrite), **identity conflict/replacement** (must resolve), excluded and ambiguous conflicts. Server independently recomputes scope/impact against current database state; stale previews require confirmation again.
- **Assign to all** creates/reconciles each target shop's slot and writes a copied, confirmed import snapshot for source templates imported from Meta. **Update one/selected/all** refreshes existing same-identity assignments while preserving each Moda row ID and historical message references; a provider edit is **not** another template to create. **Update for all** replaces the selected WABA/purpose/canonical-language slot even if a shop has a different template name/ID from an earlier individual change. An individual edit affects only that shop. Disable/enable operations can likewise target one, selected or all eligible shops.
- Commit bounded shop batches with per-shop serialisation, deterministic `operationId`, retry-safe idempotency, clear progress and explicit partial-failure reporting; durable `CommerceAuditEvent` records for each change and a bounded operation summary. Do not use a single unbounded transaction/HTTP request or Redis background scheduling unless an actual measured need is returned to the architect.

## Out of Scope

- No automatic template installation for future shops, background sending, provider metadata API calls, Meta template submission, customisations at the merchant storefront, new global master/assignment or bulk-operation database table.
- No implicit "global wins" on later independent changes; overwriting customisations requires explicit admin confirmation per bulk operation.

## Requirements

- [ ] Source provider identity, last-applied snapshot and target WABA/purpose/language slot are resolved on server; never use client-supplied shop eligibility as an authority. Same Meta ID updates existing assigned rows; a changed ID with a colliding name/language requires manual resolution.
- [ ] Preview is required before all/selected-shop imports/updates; it explicitly counts NEW, UPDATED, UNCHANGED, UNTRACKED and identity conflicts per shop, as well as individual overrides that will be replaced.
- [ ] One-shop edits cannot change unrelated shops. Update-all includes individually overridden rows of the same slot, even with different template names.
- [ ] Concurrent individual and bulk operations use the same slot lock/transaction discipline from ADMIN-001.
- [ ] Writes across large cohorts are bounded and idempotent; partial successes and failures remain observable and retryable, not falsely reported as atomic all-or-nothing.
- [ ] Updates of the same provider template preserve `WhatsAppTemplateVariant.id`, historical message references and local shop assignment; no-op refreshes do not churn timestamps or audit rows. Do not blindly delete templates or alter prior audit entries. Only rows with matching WABA/purpose/language slot are affected.

## Work Items

- [ ] Implement exact target discovery/paginated preview and confirmation with fresh server-side eligibility.
- [ ] Add single/selected/all assign, update, disable operations against current per-shop variant data.
- [ ] Add per-shop operation audit, deterministic idempotent retry and conflict/overlapping-mutation handling.
- [ ] Build UI for selection/impact summary/progress/error states; test new-versus-updated Meta identities, changed components with stable ID, legacy missing snapshot, individual overrides plus global intentional replacement.

## Interfaces / Contracts

Consumes ADMIN-001's existing catalogue server service, existing Shop/Installation/WhatsAppTemplateVariant and DATABASE-001 audit action variants. No new Shared queue/API or database table. A source template is a trusted Admin-scoped existing shop row with an optional Admin-only Meta import snapshot; its active assignment can be copied into other shops' corresponding WABA/purpose/language slots. Runtime uses only local `APPROVED`/`enabled`, never the import fingerprint.

## Dependencies

- `ARCH-047-ADMIN-001`

## Enables

- `ARCH-047-SYSTEM-TEST-001`

## Acceptance Criteria

- [ ] Assign one, selected and all current eligible Shopify/WooCommerce shops correctly, with idempotent repeat and no duplicate row when a previously imported template's body/category/status changes under the same Meta ID.
- [ ] Update for all replaces a previously customised Shop B assignment of the same slot while leaving another purpose, WABA and locale untouched.
- [ ] Admin sees distinct NEW/UPDATED/UNCHANGED/UNTRACKED/conflicting counts and exact affected/excluded shops; a stale Meta import snapshot or assignment preview cannot silently mutate an unreviewed cohort.
- [ ] Concurrent operations do not create two active approved templates in a slot. Every actual shop mutation has a durable audit including actor, reason, operationId and before/after metadata.
- [ ] Batch interruption reports partial outcome and resumes safely; newly installed shops after the operation are not silently assigned.

## Validation

- [ ] PostgreSQL integration tests for single/all new import and same-ID changed-content updates, source identity conflicts, per-shop override replacement, duplicate/no-op refresh, concurrency, stale preview, noneligible shops and partial failure/retry.
- [ ] Guarded Admin UI/action tests, responsive layout and support for paging through large shop sets; declared lint/typecheck/build checks and `git diff --check`.

## Stop Condition

After completing the defined Work Items, Acceptance Criteria and required Validation, record task-isolated parent and implementation worktrees, start-of-attempt synchronisation and relevant commit evidence in the Completion Report; set `status: review`, return control to `moda_architect`, and **STOP**. Do not implement dependent tasks or modify domain `_index.md` files.

## Implementation Notes

Respect `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/task-definition-materialization.md` and `docs/developer-task-workflow.md`. `/moda-task` owns preparation and the canonical claim; never infer worktrees from a previous task or operate in shared/default checkouts. Existing application code has evolved: inspect current implementation immediately before claiming and return cross-domain contract gaps to `moda_architect`. Use the shared structured logger where new runtime domain logging is needed, not a duplicate generic logger. All tasks are portable definitions until materialised in the developer's real workspace.


Additional task-specific guidance:

Use `Shop.domain` in all merchant-visible choices; never show only `shopId`. Disable repeat clicks while a confirmed operation is in flight. Do not enable auto-refresh in the selection workflow that would erase the administrator's pending choices.

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
