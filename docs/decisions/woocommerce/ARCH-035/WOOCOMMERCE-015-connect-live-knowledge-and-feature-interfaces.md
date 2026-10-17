---
id: ARCH-035-WOOCOMMERCE-015
architecture_id: ARCH-035
title: Connect W003 and W004 to real feature and knowledge services
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 52
executor: null
claimed_at: null
attempt: 0
depends_on: [ARCH-035-WOOCOMMERCE-003, ARCH-035-WOOCOMMERCE-004, ARCH-035-WOOCOMMERCE-014]
enables: [ARCH-035-SYSTEM-TEST-004]
created: 2026-10-16
updated: 2026-10-16
---

# ARCH-035-WOOCOMMERCE-015 — Connect W003 and W004 to real feature and knowledge services

## Architecture

- Parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`, approved 16 October functional knowledge extension.
- Owner: `moda_woocommerce`, repository `moda-interact-woocommerce`; coordinator: `moda_architect`.
- **Defined but not materialised.** This portable task definition did not create a parent/implementation worktree, branch, commit, push or claim. The real `/moda-task ARCH-035-WOOCOMMERCE-015` launcher owns canonical materialisation and start-of-attempt evidence.

## Objective

Replace fixture-only unavailable feature and Merchant Knowledge adapters with approved live WordPress data and actions without changing their existing UX architecture.

## Context

W003 supplies the conversation feature controls and W004 supplies the Merchant Knowledge section. Their UI-only acceptance allowed honest disabled states; API-014..017 and WOO-014 now make these states live.

## Scope

- Wire production `feature-preferences-client.js` to WOO-014; reconcile W003 controller body `preferences` to API-014 `changes` and stale CAS handling while showing effective vs optional feature state.
- Wire W004 knowledge client/controller to live read/add/edit/delete/refresh/reorder/upload/replace/reprocess; ensure configured sources remain accessible while merchant feature is off.
- Maintain source list statuses and cap counts from authoritative data, no fake success, dedupe actions, manual confirmation for destructive operations and local form validation; refresh after server ack.
- Preserve signed file privacy (browser sends file only to same-origin WordPress), handle long uploads and stale disconnect/credential rotation without showing results from prior installation.
- Match Shopify two-column web/file controls, status/capacity, source edit/reorder presentation and existing native 20-language admin locale; no duplicate Recovery Settings sections.

## Out of Scope

- New hosted service APIs, background business processing, Shopify UI changes and new database models.
- Enabling knowledge tools outside existing plan/provider eligibility or overriding feature preference server policy.

## Requirements

- Preserve existing tenant, credential, platform, entitlement and transaction boundaries; use the source-inspected contracts and Shared package where applicable, not independently guessed interfaces.
- Fail closed on missing or malformed configuration, unauthorised operations and external provider failures. W015 is browser-side WordPress JavaScript and must not import `@modainteract/moda-interact-shared/logging` or introduce a competing generic logger. Display bounded, localised user-facing errors; optional PHP diagnostics belong to WOO-014, and hosted Node.js structured logging belongs to the API owners.
- Keep production components modular and independently testable; no monolithic files or cross-repository implementation changes. Preserve Shopify runtime and existing Woo merchant Billing, recovery and navigation behaviour.
- If implementation discovers a genuine missing Background/Shared/Gateway capability, stop and return the precise evidence to `moda_architect` rather than extending another repository's scope.

## Work Items

- [ ] Wire production `feature-preferences-client.js` to WOO-014; reconcile W003 controller body `preferences` to API-014 `changes` and stale CAS handling while showing effective vs optional feature state.
- [ ] Wire W004 knowledge client/controller to live read/add/edit/delete/refresh/reorder/upload/replace/reprocess; ensure configured sources remain accessible while merchant feature is off.
- [ ] Maintain source list statuses and cap counts from authoritative data, no fake success, dedupe actions, manual confirmation for destructive operations and local form validation; refresh after server ack.
- [ ] Preserve signed file privacy (browser sends file only to same-origin WordPress), handle long uploads and stale disconnect/credential rotation without showing results from prior installation.
- [ ] Match Shopify two-column web/file controls, status/capacity, source edit/reorder presentation and existing native 20-language admin locale; no duplicate Recovery Settings sections.
- [ ] Add focused positive and negative coverage and complete the required validation/Completion Report.

## Interfaces / Contracts

- Consume WOO-014 WordPress responses based on approved API-014..017 OpenAPI; read `effectiveEnabled` separately from plan entitlement and `merchantEnabled`.
- Keep source language independent of WordPress admin locale, and use generated WordPress i18n assets.

## Dependencies

- `ARCH-035-WOOCOMMERCE-003` (must be Complete and architect accepted)
- `ARCH-035-WOOCOMMERCE-004` (must be Complete and architect accepted)
- `ARCH-035-WOOCOMMERCE-014` (must be Complete and architect accepted)

## Enables

- `ARCH-035-SYSTEM-TEST-004`

## Acceptance Criteria

- [ ] Feature toggle can be read/changed and persisted for eligible optional features; required features are non-editable and conflicts return actionable feedback.
- [ ] An entitled merchant can configure sources when feature off; toggle-off does not erase sources and no pending/active result is spoofed.
- [ ] Web source, CSV/XLSX upload, edit, refresh/reprocess, reorder, delete and processing state are reflected by actual API state; errors preserve drafts.
- [ ] Automated desktop/narrow component/DOM-layout and interaction assertions reflect the Shopify reference; WordPress two-stage navigation, category and recovery settings remain intact; all 20 locales pass. Live LocalWP visual confirmation is a separate developer-owned checkpoint, not an agent acceptance criterion.
- [ ] No `_index.md` files or unrelated domains modified; canonical dual-worktree/branch validation evidence recorded in real development workspace.

## Validation

- [ ] Focused React controller/component tests with real client contract fixtures, 401/403/409/503, disabled feature, disconnect, stale responses and duplicate click cases.
- [ ] `npm run test:js`, `npm run test:i18n`, `npm run i18n:verify:20`, PHP facade tests if relevant, lint, build, plugin ZIP, automated responsive/browser fixtures where supported, `git diff --check`. Do not launch or operate LocalWP in agent validation.
- [ ] Record concrete commands and results, implementation and parent task branch/commit evidence, canonical physical-isolation/synchronisation evidence, plus deviations and unresolved issues.

## Stop Condition

When this bounded task's Work Items, Acceptance Criteria and required Validation are satisfied, update Completion Report, set `status: review`, return to `moda_architect` and STOP. Do not start tasks listed under Enables.

## Implementation Notes

### Reconciled WooCommerce-structure handoff (2026-10-16 22:56 snapshot)

- This snapshot shows `WOOCOMMERCE-003` as `complete` with `src/recovery-settings/feature-preferences-{client,controller,panel}.js`, but `WOOCOMMERCE-004` as `ready`, and **no** `src/recovery-settings/merchant-knowledge/` files in the included Woo checkout. The previous W004 patch delivery is not proof that this revision is merged. Do not claim WOO-015 Ready until W004 is formally Complete **and** its accepted source is present in the launcher's implementation baseline; if absent, reconcile the source/gitlink rather than rebuilding W004 as part of WOO-015.
- After W004 is present, wire the existing `src/recovery-settings/feature-preferences-client.js` and W004's knowledge client/controller through the `includes/Rest/` and `includes/Api/` contracts completed by WOO-014. Preserve `src/recovery-settings/recovery-settings-screen.js` composition and existing `src/page/connected-workspace.js` connection-identity reset; do not implement hosted database/R2 business rules in React.
- The W003 controller currently submits `{expectedRevision, preferences:[{featureId,enabled}]}`, whereas API-014 defines `{expectedRevision, changes:[{featureId,enabled}]}`. Adapt the client contract without changing entitlement meaning. Extend the strict read parser for `schemaVersion`, `required` and `planEligible` (and bounded source DTO validation) without silently trusting missing/unknown fields.
- Keep configuration available for entitled shops even if the Merchant Knowledge feature is off, while clearly identifying current retrieval/processing eligibility. Preserve manual actions, stale read suppression, cancel/draft state and 20 native WordPress locales. Agent validation uses authenticated WordPress/API test fixtures and automated desktop/narrow/feature-off/feature-on assertions. **Only the developer** launches LocalWP, exercises authenticated live sessions and captures comparative screenshots. Treat that manual check as a separate checkpoint; do not block agent `review`/architect acceptance on LocalWP access or claim that the agent performed it.

The historical superseded ARCH-035-API-003/004/005 must **not** be revived; this task follows the newly agreed architecture amendment and consumes only approved contract owners. An unimplemented API or feature must never be represented as operational. Do not update any `docs/decisions/**/_index.md` until the developer closes the architectural session.

Logging/runtime boundary: W015 connects React components to authenticated same-origin WordPress REST responses. It must not bundle or call the Node-only `@modainteract/moda-interact-shared/logging` package or add a separate browser logging transport. Preserve existing UI error-handling and display safe, actionable, localised messages. Never log installation credentials, authorisation headers, signed upload URLs, uploaded file contents or customer data. WordPress/PHP diagnostics are owned by WOO-014; hosted API structured logging belongs to the API owners.

## Completion Report

### Status

Not Started.

### Files Changed

None.

### Work Completed

None.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

The uploaded ZIP represents a portable design baseline, not the developer's current on-disk branches. Confirm source, task status and dependency state with the launcher before execution.

### Unresolved Issues

None evidenced beyond the explicit implementation and test dependencies above.

### Architectural Concerns

Report any cross-repository contract, R2 identity, reconciliation or security mismatch to `moda_architect`.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting implementation and validation evidence.

### Reviewed Files

None.

### Validation Reviewed

Not run.

### Architecture Conformance

Pending.

### Follow-up

None until implementation submission.
