---
id: ARCH-047-WOOCOMMERCE-001
architecture_id: ARCH-047
title: Display authenticated recovery follow-up template choices in WooCommerce
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 45
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-047-API-001
enables:
  - ARCH-047-SYSTEM-TEST-001
created: 2026-10-26
updated: 2026-10-26
---

# Display authenticated recovery follow-up template choices in WooCommerce

## Architecture

Architecture: `ARCH-047` — `docs/architecture/ARCH-047-admin-managed-whatsapp-template-catalogue.md`; coordinator `moda_architect`. The task definition is materialised on its canonical parent branch. The current architecture document was not edited as part of this dependency-frontier update.

## Objective

Enable merchant-controlled, eligible **post-window sequence-two** selection of approved Moda-authored Follow-up templates in the existing WooCommerce recovery conversation UI, consuming the hosted authenticated catalogue and preserving one-send idempotency.

## Context

`src/recoveries/detail/human/conversation-command-contract.js` currently hardcodes `canTemplate: false` because the plugin has no authenticated eligible-template list. `human-reply-composer.js` currently supports in-window free text only. The hosted API's existing message command already models `RECOVERY_FOLLOW_UP_TEMPLATE`, but API-001 must provide the safe catalogue and reject untrusted parameters first.

## Scope

- Add a nonce-authenticated WordPress REST proxy route `GET /moda-interact/v1/merchant/recoveries/{recoveryId}/conversation/follow-up-templates`, using the existing installation-authenticated outgoing API client to call `GET /v1/merchant/conversations/{conversationId}/follow-up-templates`. Resolve `conversationId` from the current authorised recovery detail; do not accept arbitrary client-provided shop IDs or provider account IDs.
- Extend the existing dedicated `src/recoveries/detail/human/` client, hook/controller and small React composer components to load/display server-authorised choices when HUMAN control is active, the window is closed, and the sequence-two follow-up is due and unused. Preserve native WordPress i18n and modular components.
- Submit the existing `RECOVERY_FOLLOW_UP_TEMPLATE` command with selected `templateName`, `templateLanguage` and strictly `templateParameters: []`; never embed merchant-supplied brand, checkout or discount parameters. Preserve retry with the *same* idempotency key and no second click while command pending.

## Out of Scope

- No new CheckoutRecovery, new merchant staff identities, provider API/Meta credentials, direct database access, AST authoring, additional follow-ups, Woo cart mutation or Media R2 processing.

## Requirements

**R1 — Tenant-controlled proxy.** Verify WordPress Admin/nonce/installation/shop/recovery access exactly as existing RecoveryConversationCommandController paths; return no-store bounded v1 list or explicit error. Never expose hosted internal tokens or redirect to arbitrary merchant URLs.

**R2 — Correct UI state.** Show a template picker only when the authenticated hosted list is non-empty and the current recovery conversation is HUMAN-controlled, outside the rolling 24h service window and sequence two eligible. Hide/disable stale or unavailable candidates, and revalidate server-side on submit. In-window human replies remain unchanged.

**R3 — Accurate intent.** No customer-specific saving is promised merely because a CODE/AUTOMATIC template exists; if verified eligibility is missing, show only allowed No Offer candidates. The Background BG007 service remains authoritative for the actual prepared template and late admission.

**R4 — Old code cleanup.** Remove the hardcoded `canTemplate: false` dead branch and related obsolete tests/fixtures, but do not remove current human-text, window-safety or command polling mechanics. Do not duplicate a giant recovery-detail component.

## Work Items

- [ ] Add authenticated WordPress REST proxy and bounded response contract, with PHP tests.
- [ ] Extend the existing dedicated JS client/hook/controller and separate React picker component with language, loading, empty and error states.
- [ ] Wire template submission through existing immutable idempotent command client and response polling; update Woo tests.
- [ ] Replace dead `canTemplate` logic, validate React/PHP/build and record isolated worktree evidence.

## Interfaces / Contracts

Hosted API-001 GET v1 response: `{schemaVersion:1, templates:[{name,language}]}` (max 30). Browser talks only to nonce-protected WordPress proxy. POST retains existing plugin command wire schema with `templateParameters: []`. No dynamic runtime parameter binding in Woo plugin. BG007 owns final read-only provider resolution and send.

## Dependencies

- `ARCH-047-API-001`.

## Enables

- `ARCH-047-SYSTEM-TEST-001`.

## Acceptance Criteria

- [ ] Woo merchant can select an authorised eligible follow-up template outside the service window when due; inside window only free-text reply is available.
- [ ] An unknown or stale template, missing eligibility, duplicate request, expired window, consent or STOP change is rejected by current server-side guards; no unauthorized provider parameter injection.
- [ ] Cross-shop query, installation authentication and CSRF/nonce failure cannot return eligible choices or submit commands.
- [ ] `canTemplate: false` hardcode and dead UI/tests are gone; independently modular React/presentation, controller and transport files remain small and testable.

## Validation

- [ ] Focused PHP tests for GET proxy and authentication, JS tests for human composer/state/polling and build lint according to repo scripts, `git diff --check`.

## Stop Condition

Set status `review`, record Completion Report and STOP; no API or Background code edits, no `_index.md` updates.

## Implementation Notes

Use canonical Woo task parent/implementation worktrees and preserve existing native WordPress localisation in all supported merchant UI languages. No merchant Meta account is required; hosted Moda already owns sender configuration.

## Completion Report

### Status
Ready — materialised in the canonical parent task worktree on `task/ARCH-047-WOOCOMMERCE-001` from fetched `origin/main`. Its sole dependency, `ARCH-047-API-001`, resolves `complete`. No executor or claim is set; implementation worktree has not been created.

### Files Changed
None.

### Work Completed
None.

### Validation Results
Not run.

### Deviations
None.

### Assumptions
Authenticated hosted API-001 route is available by the time this task executes.

### Unresolved Issues
Provider-specific verified offers are a separate dependency for promising positive discount benefits.

### Architectural Concerns
None additional.

## Architect Review

### Review Status
Pending.

### Review Notes
No implementation reviewed.

### Reviewed Files
None.

### Validation Reviewed
None.

### Architecture Conformance
Not assessed.

### Follow-up
System test validates Shopify/Woo merchant parity after integration.
