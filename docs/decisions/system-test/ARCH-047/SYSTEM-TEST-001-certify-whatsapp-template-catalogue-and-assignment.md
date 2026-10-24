---
id: ARCH-047-SYSTEM-TEST-001
architecture_id: ARCH-047
title: Certify Meta import classification and database-only template sending
task_kind: implementation
domain: system-test
repository: moda-interact-system-test
assigned_agent: moda_system_test
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-047-ADMIN-002
  - ARCH-047-BACKGROUND-001
enables: []
created: 2026-10-23
updated: 2026-10-23
---

# Certify Meta import classification and database-only template sending

## Architecture

`ARCH-047` — `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`; coordinator `moda_architect`. Source snapshot: 23 October 2026, 16:40.

## Objective

Independently certify that Admin distinguishes **new** and **updated** Meta templates, safely imports/refreshes shop-scoped assignments individually and globally, and that the integrated recovery sending paths use only approved assigned database rows without Meta metadata validation.

## Context

Implementation prerequisites are completed Admin CRUD, bulk management, and Background read-only selection (plus DATABASE-001). Tests must validate the operational merchant and customer workflow, not merely whether an Admin React component renders.

## Scope

- Add black-box scenarios in `moda-interact-system-test` with self-contained fixtures for at least three shops (two Shopify and one WooCommerce installation where applicable), one WABA, multiple locales, enabled/disabled templates and an individually customised variant.
- Exercise SUPER_ADMIN Meta Import/Refresh through an authenticated Admin-only Meta-list emulator: complete multi-page retrieval; brand-new Meta ID; same-ID body/buttons-only edit; status/category change; unchanged re-import; legacy manual row with no snapshot; ID collision under same WABA/name/language; missing provider ID on a complete listing; incomplete listing failure. Verify accurate NEW/UPDATED/UNCHANGED/UNTRACKED/CONFLICT/MISSING classification and **browser-visible complete labelled Previous (last applied)/Current (fresh Meta) template panels** for UPDATED, with identity/language, category/status, HEADER/BODY/FOOTER/BUTTONS and highlighted changed variables/buttons, not only a change count. Assert previous content comes from the stored snapshot and preview does not write it. Verify UNTRACKED shows unavailable prior content instead of inventing a baseline.
- Exercise authenticated single creation/assignment, selected/all-shop assignment, individual edit, global update of an imported template, disable-all and duplicate/ambiguous/stale-preview rejection; assert existing Moda row identity, per-shop snapshots, PostgreSQL assignments and audit records. For a bulk update with distinct shop baselines/overrides, verify each affected shop's browser-visible complete **previous-shop versus proposed-confirmed-source** preview and explicit overwrite confirmation without an extra Meta listing request.
- Exercise Shopify recovery initial outreach, scheduled follow-up and merchant post-window template paths against a Meta send emulator. Assert **no Meta template metadata/listing requests**, but actual approved template send attempts still occur through the existing send interface.
- Exercise race where an Admin disables/reassigns a template after selection and before the SQL final send permit; assert no provider send or committed recovery credit.
- Preserve consent/STOP, no-checkout-recovery-without-consent, billing/idempotency, template-language fallback, provider-send rejection compensation, platform/tenant scoping and in-window free-text handling.
- Produce evidence/coverage report and identify any environmental or provider-emulation limitation without claiming live Meta validation.

## Out of Scope

- No reimplementation of Admin, Background, Meta SDK or database schema in system-test fixtures; tests must use public/authenticated Admin boundaries and application-owned data contracts.
- No live Meta approval tests or assertions that `APPROVED` guarantees the provider still approves the template; Admin is the trusted local catalogue authority.
- No new Shopify/WooCommerce consent or recovery engine task and no simulation of production deployment without evidence.

## Requirements

- [ ] Run only after all `depends_on` tasks are architect-accepted Complete.
- [ ] Tests prove a new Meta template creates an assignment only when confirmed, a provider content change under the **same Meta ID** updates the existing Moda row rather than creating another, and one-shop mutations leave other shops untouched while confirmed Update-all overwrites a chosen individual override. The Admin UI exposes the full previous/current content for UPDATED and full previous/proposed per-shop content before bulk overwrite, including meaningful component/variable/button highlights.
- [ ] Tests prove all-shop scope includes all current eligible shops and excludes inactive/uninstalled shops; a future new shop is not automatically assigned. Repeated unchanged imports are no-ops with no mutation audits.
- [ ] Meta template-listing requests occur **only** on explicit authenticated Admin import/refresh, and no provider template-category/listing operation is invoked on successful or negative recovery paths; actual send requests remain observable.
- [ ] Approved/disabled/ambiguous/stale catalogue rows produce the expected action/no-action/billing results.
- [ ] Every tested mutation is securely authorised, durably audited and idempotent where appropriate.

## Work Items

- [ ] Define fixture shop/provider/template/locale variants, changed-components snapshots (HEADER/BODY/FOOTER/BUTTONS, variables, provider status/category) and realistic Admin Meta-import operations that exercise visible old/new component comparisons, including different shop baselines.
- [ ] Execute Admin mutation and bulk assignment scenarios via their real authenticated boundaries.
- [ ] Execute end-to-end recovery selection, final-send/no-Meta-metadata, error-compensation and safety regression scenarios.
- [ ] Save deterministic logs/results under approved system-test evidence paths and write Completion Report.

## Interfaces / Contracts

Consumes approved published implementation and existing Admin/Background/PostgreSQL/Meta-send interfaces. No new Shared schema, Kafka queue or provider metadata client. System-test dependencies are terminal: no implementation task depends on this test.

## Dependencies

- `ARCH-047-ADMIN-002`
- `ARCH-047-BACKGROUND-001`

## Enables

None.

## Acceptance Criteria

- [ ] New-versus-updated classification agrees with complete Meta fixture data, including stable-ID body-only edit, category/status change, legacy UNTRACKED and ID collision, and requires explicit confirmation. UPDATED shows full labelled side-by-side previous-applied/current-fetched components and highlighted changes; bulk overwrite shows the corresponding full per-shop previous/proposed components and labels source provenance honestly. Single/selected/all assignment and intentional overwrite of Shop B's custom entry alter DB selection only for intended shops.
- [ ] Recovery for a shop with an approved enabled variant may proceed when all existing consent/STOP/billing guards pass; disallowed or stale variant cannot send or charge.
- [ ] Runtime performs zero Meta `message_templates`/category lookup operations, while Meta send emulator receives expected names/languages for eligible assignments.
- [ ] Concurrent or duplicate bulk actions and repeat Meta refresh cannot produce multiple active approved choices, false new-template classification or false full-success outcomes; audit evidence identifies actor/scope/operation.
- [ ] A provider delivery error is surfaced through existing failed-send/compensation workflow; no template metadata API is required even on error.

## Validation

- [ ] Use the repository's real scenario runner/fixture layout and declared validation commands (inspect its `package.json` before executing; do not invent unsupported flags).
- [ ] Black-box Admin/Background integration evidence, Meta import-page emulator plus runtime send-only request capture, billing/STOP regression, `git diff --check`.
- [ ] Attach status/results, skipped environment-dependent scenarios and clear release gate to Completion Report.

## Stop Condition

After completing the defined Work Items, Acceptance Criteria and required Validation, record task-isolated parent and implementation worktrees, start-of-attempt synchronisation and relevant commit evidence in the Completion Report; set `status: review`, return control to `moda_architect`, and **STOP**. Do not implement dependent tasks or modify domain `_index.md` files.

## Implementation Notes

Respect `docs/agent-vcs-ownership-policy.md`, `docs/agent-worktree-isolation-policy.md`, `docs/task-definition-materialization.md` and `docs/developer-task-workflow.md`. `/moda-task` owns preparation and the canonical claim; never infer worktrees from a previous task or operate in shared/default checkouts. Existing application code has evolved: inspect current implementation immediately before claiming and return cross-domain contract gaps to `moda_architect`. Use the shared structured logger where new runtime domain logging is needed, not a duplicate generic logger. All tasks are portable definitions until materialised in the developer's real workspace.


Additional task-specific guidance:

Do not run automatically when task becomes Ready: developer/user may manually validate the Admin feature first, as required by the architecture's terminal system-test protocol.

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
