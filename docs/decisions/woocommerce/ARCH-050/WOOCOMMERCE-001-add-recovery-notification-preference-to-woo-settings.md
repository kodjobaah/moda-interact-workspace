---
id: ARCH-050-WOOCOMMERCE-001
architecture_id: ARCH-050
title: Add the WooCommerce recovery-outreach notification opt-in
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-050-API-001
enables:
  - ARCH-050-SYSTEM-TEST-002
created: 2026-10-26
updated: 2026-10-26
---

# Add the WooCommerce recovery-outreach notification opt-in

## Architecture

Architecture ID: `ARCH-050`. Architecture document: `docs/architecture/ARCH-050-merchant-recovery-initial-outreach-support-notifications.md`. Coordinator: `moda_architect`.

## Objective

Render and persist the merchant opt-in inside the existing WooCommerce Recovery Settings form using the accepted v2 hosted policy contract.

## Context

`src/recovery-policy-client.js`, `src/recovery-policy-controller.js`, `src/recovery-settings/recovery-behaviour-panel.js`, validation helpers and WordPress REST PHP proxy own the existing settings flow.

## Scope

**Modify in `moda-interact-woocommerce/`:**

- `includes/Api/RecoveryPolicyResponseValidator.php` — exact v2 GET/PUT validator including new required top-level preference; `merchant` and `effective` values stay original four fields.
- `includes/Rest/RecoveryPolicyController.php` — retain capability/nonce, endpoint and PHP proxy; accepts new validated request via existing validator.
- `includes/Api/ModaApiClient.php` — retain hosted endpoint, authentication, HTTP error conversion and no-store behaviour; ensure strict response validator accepts v2.
- `src/recovery-policy-client.js` — v2 `parseMerchantRecoveryPolicy()`, required fifth-field `makeRecoveryPolicyUpdate()` and confirmation of saved preference.
- `src/recovery-settings/recovery-behaviour-validation.js` — draft initialization and dirty detection include the new Boolean; existing minute validations untouched.
- `src/recovery-settings/recovery-behaviour-fields.js` — new accessible, translated checkbox section `Notify me when initial recovery outreach starts`, not affected by follow-up toggle.
- `src/recovery-settings/recovery-behaviour-panel.js` — initialize/submit/refresh preference alongside recovery policy with no autosave.
- Update `tests/js/recovery-policy-integration.test.js`, `tests/js/recovery-behaviour-preview.test.js`, `tests/js/recovery-settings-screen.test.js`, `tests/RecoveryPolicyControllerTest.php` and PHP validator tests/fixtures if separate.

No new WordPress REST endpoint, public WordPress callback or schema. Do not change Support inbox here (WOOCOMMERCE-002).

## Out of Scope

- Creating a new Settings REST endpoint, modifying Background, changing billing/discount rules, Support notification action or enabling live Woo outbound.

## Requirements

- Mirror **API-001 v2** exactly: successful `GET|PUT /v1/merchant/recovery-policy` returns top-level `notifyOnInitialRecoveryOutreach: boolean`, `schemaVersion:2` and unmodified four-field `merchant/effective`. Strict PUT from WordPress to API has fifth required Boolean alongside old four fields.
- Update `RecoveryPolicyResponseValidator::isValid()` and `::isUpdate()` to validate v2 and **reject** missing/extra fields, string flags, malformed policy. `ModaApiClient::merchantRecoveryPolicy` must still pass only validated data and use installation credentials.
- In browser, update `parseMerchantRecoveryPolicy()` exact field set, `makeRecoveryPolicyUpdate(current,draft)`, and read-after-save field equality check. A successful save must confirm the Boolean equals the requested value.
- `recoveryBehaviourPreview()` includes `notifyOnInitialRecoveryOutreach: Boolean(effective?.notifyOnInitialRecoveryOutreach)`, but use **top-level policy response** to initialise it, NOT `merchant`/`effective` (which intentionally lack the field). Adjust call signatures appropriately and make `recoveryBehaviourChanged()` compare the toggle even if nothing else changed.
- Add new accessible checkbox in `RecoveryBehaviourFields`; leave `followUpEnabled` and follow-up minute enable/disable independent. Save only on explicit `Save recovery behaviour`; conflicts preserve unsaved local edits, refresh replaces them.
- Preserve `manage_woocommerce` permission, `X-WP-Nonce`, current-installation check and WordPress-to-hosted signature; never expose hosted credentials or use unauthenticated browser direct API calls.
- Use WordPress native `__()` translation and existing plugin i18n extraction/20-language verification. Do not hardcode English-only strings or bypass localisation.

## Work Items

- [ ] Upgrade PHP `RecoveryPolicyResponseValidator` exact v2 request/response and confirm existing controller/client still proxy safely.
- [ ] Upgrade browser `recovery-policy-client.js` v2 parsing/building/saved-value reconciliation.
- [ ] Add preview/dirty/controlled checkbox UI, explicit save and conflict behaviour.
- [ ] Extend PHP/JS tests for default OFF, ON/OFF save, stale revisions, malformed v2, nonce/capability and 20-language i18n checks.

## Interfaces / Contracts

- **Consume API-001**: `MerchantRecoveryPolicyResponseV2.notifyOnInitialRecoveryOutreach: boolean` at top level and `RecoveryPolicyUpdateV2.notifyOnInitialRecoveryOutreach: boolean` in required PUT body.
- WordPress browser REST path unchanged: `/moda-interact/v1/merchant/recovery-policy` GET/PUT; PHP-to-hosted path unchanged: `/v1/merchant/recovery-policy` GET/PUT.
- Draft preview: `{ recoveryDelayMinutes:string, followUpEnabled:boolean, followUpDelayMinutes:string, notifyOnInitialRecoveryOutreach:boolean }`; `makeRecoveryPolicyUpdate` sends this Boolean with revision and other fields.
- No new `ShopRecoveryPolicyOverride` semantics and no separate config row in WordPress options.

## Dependencies

- `ARCH-050-API-001` must be `complete` in canonical task metadata before claim.

## Enables

- `ARCH-050-SYSTEM-TEST-002` may become eligible only after architect acceptance and Complete state.

## Acceptance Criteria

- [ ] Woo merchant can switch ON/OFF independently, save, reload and see persisted value.
- [ ] Preference-only change counts as dirty and is persisted; stale updates fail with policy conflict.
- [ ] Browser JS, WordPress PHP and hosted v2 validators agree on field set; extra/missing or invalid values fail closed.
- [ ] WordPress capability/nonce/installation and no-store security stay enforced; no production outbound sends are triggered merely by enabling setting.
- [ ] 20-language source/compile checks pass.

## Validation

- [ ] `npm run test:js:unit` for focused recovery-policy/behaviour/UI cases, `npm run test:php` for revised PHP validators/controller.
- [ ] `npm run i18n:verify:20`, `npm run build` and targeted `npm run lint:js` / `npm run lint:php` where appropriate, `git diff --check`.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, update this task to `review`, provide the Completion Report, return control to `moda_architect`, and **STOP**. Do not start dependent work. A system-test task is terminal and cannot be used as a prerequisite for implementation.

## Implementation Notes

The hosted API v2 and Woo plugin v2 are a coordinated rollout in development. Do not upgrade just the hosted DTO and leave PHP/browser strict parsers at v1. This task touches recovery settings and its PHP REST proxy **only**, not Support messaging or recovery-detail navigation. Keep plugin-only data at WordPress boundary and hosted DB access at API.

## Completion Report

### Status

Not Started.

### Files Changed

None (definition only).

### Work Completed

None.

### Validation Results

Not executed; no implementation claimed.

### Deviations

None.

### Assumptions

The task is based on the 2026-10-26 uploaded snapshot and must recheck current canonical code during execution.

### Unresolved Issues

None recorded at definition time.

### Architectural Concerns

Return newly discovered cross-repository/schema/security/contract issues to `moda_architect`.

### Task Branch / Worktree Evidence

Not materialised. Launcher-resolved parent/implementation task worktree, synchronization and branch evidence are required at execution.

## Architect Review

### Review Status

Pending.

### Review Notes

Awaiting implementation.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not yet reviewed.

### Follow-up

None.
