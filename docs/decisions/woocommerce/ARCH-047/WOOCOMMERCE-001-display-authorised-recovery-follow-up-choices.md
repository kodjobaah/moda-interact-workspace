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
status: review
priority: 45
executor: codex
claimed_at: 2026-10-27T18:09:11Z
attempt: 1
depends_on:
  - ARCH-047-API-001
enables:
  - ARCH-047-SYSTEM-TEST-001
created: 2026-10-26
updated: 2026-10-27
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

- [x] Add authenticated WordPress REST proxy and bounded response contract, with PHP tests.
- [x] Extend the existing dedicated JS client/hook/controller and separate React picker component with language, loading, empty and error states.
- [x] Wire template submission through existing immutable idempotent command client and response polling; update Woo tests.
- [x] Replace dead `canTemplate` logic, validate React/PHP/build and record isolated worktree evidence.

## Interfaces / Contracts

Hosted API-001 GET v1 response: `{schemaVersion:1, templates:[{name,language}]}` (max 30). Browser talks only to nonce-protected WordPress proxy. POST retains existing plugin command wire schema with `templateParameters: []`. No dynamic runtime parameter binding in Woo plugin. BG007 owns final read-only provider resolution and send.

## Dependencies

- `ARCH-047-API-001`.

## Enables

- `ARCH-047-SYSTEM-TEST-001`.

## Acceptance Criteria

- [x] Woo merchant can select an authorised eligible follow-up template outside the service window when due; inside window only free-text reply is available.
- [x] An unknown or stale template, missing eligibility, duplicate request, expired window, consent or STOP change is rejected by current server-side guards; no unauthorized provider parameter injection.
- [x] Cross-shop query, installation authentication and CSRF/nonce failure cannot return eligible choices or submit commands.
- [x] `canTemplate: false` hardcode and dead UI/tests are gone; independently modular React/presentation, controller and transport files remain small and testable.

## Validation

- [ ] Focused PHP tests for GET proxy and authentication, JS tests for human composer/state/polling and build lint according to repo scripts, `git diff --check`.

## Stop Condition

Set status `review`, record Completion Report and STOP; no API or Background code edits, no `_index.md` updates.

## Implementation Notes

Use canonical Woo task parent/implementation worktrees and preserve existing native WordPress localisation in all supported merchant UI languages. No merchant Meta account is required; hosted Moda already owns sender configuration.

## Completion Report

### Status
Ready for Review. The authenticated WooCommerce catalogue proxy, eligible template picker and idempotent submission are implemented and pushed on task/ARCH-047-WOOCOMMERCE-001.

### Files Changed
- includes/Rest/RecoveryConversationCommandController.php
- includes/Api/ModaApiClient.php
- includes/Api/ConversationCommandContracts.php
- src/recoveries/detail/human/conversation-command-client.js
- src/recoveries/detail/human/conversation-command-contract.js
- src/recoveries/detail/human/human-conversation-controller.js
- src/recoveries/detail/human/use-human-conversation.js
- src/recoveries/detail/human/human-reply-composer.js
- src/recoveries/detail/human/follow-up-template-picker.js
- tests/RecoveryConversationCommandControllerTest.php
- tests/js/recovery-human-conversation.test.js
- languages/moda-interact.pot and all 19 existing WordPress .po catalogues

### Work Completed
- Added nonce- and manage_woocommerce-protected GET /moda-interact/v1/merchant/recoveries/{recoveryId}/conversation/follow-up-templates. The controller derives conversationId from the authenticated recovery detail, uses installation authentication, rejects query parameters and returns a strict schemaVersion 1 catalogue capped at 30 entries with private, no-store headers.
- Added the hosted catalogue client and exact schema validation. The UI requests choices only for a HUMAN-controlled recovery with a known closed service window, active human messaging and unused sequence two. The picker has loading, empty and error/retry states and displays only returned name/language choices.
- Wired template sends through the existing command and polling path. A selected choice must still exist in the current catalogue; command parameters are always empty, the server remains authoritative for stale or unknown eligibility, and the existing immutable idempotency key prevents duplicate pending sends and is reused on uncertain retry.
- Removed the hardcoded canTemplate false branch while retaining free-text/window handling and command polling.
- Added translated UI labels to the source POT and every existing locale catalogue.
- Architect Review was Pending with no requested corrections; no Architect Review content was changed.

### Validation Results
- WooCommerce bootstrap passed; PHP 8.5.11, Composer 2.10.3 and Docker daemon available.
- Focused PHP: php vendor/bin/phpunit tests/RecoveryConversationCommandControllerTest.php — 5 tests, 39 assertions passed.
- Focused JavaScript: npx vitest run tests/js/recovery-human-conversation.test.js tests/js/recovery-human-ui-parity.test.js — 10 tests passed.
- Changed-file JavaScript lint passed.
- PHP syntax checks for the changed API contract, API client, REST controller and PHP test passed.
- npm run lint:php passed.
- npm run build passed, including strict i18n verification for 565 source strings, 19/19 locale packs and 38 generated assets. Webpack emitted bundle-size warnings for the 304 KiB index.js asset.
- git diff --check passed.
- Repository-wide npm run lint:js reported lint errors in unrelated existing files, including integration test files. The changed JavaScript files pass targeted lint.

### Deviations
- No scope deviations. Repository-wide JavaScript lint remains blocked by unrelated existing lint findings; focused changed-file lint and build pass.

### Assumptions
- The completed API-001 dependency serves the task-defined authenticated follow-up catalogue contract. WooCommerce consumes and revalidates that hosted response without duplicating eligibility logic.

### Unresolved Issues
- None for this task.

### Architectural Concerns
- None.

### Physical Worktree Isolation
- Canonical workspace root: /Users/kwadwoadomafriyie/project/moda-interact-workspace
- Parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-047-WOOCOMMERCE-001
- Parent branch: task/ARCH-047-WOOCOMMERCE-001
- Implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-047-WOOCOMMERCE-001
- Implementation branch: task/ARCH-047-WOOCOMMERCE-001
- Shared workspace checkout switched or mutated for task work: no
- Shared implementation checkout switched or mutated for task work: no
- Another task worktree reused: no

### Start-of-Attempt Synchronization
- Parent remote task branch fast-forwarded: not-needed
- Parent origin/main incorporated: yes
- Implementation remote task branch fast-forwarded: not-needed
- Implementation origin/main incorporated: already-current

### Recursive Implementation Submodules
- git submodule sync --recursive: passed
- git submodule update --init --recursive: passed
- Recorded submodule commits: none

### Commits
- Implementation: 550d468 — pushed to origin/task/ARCH-047-WOOCOMMERCE-001
- Parent claim: 2258afab6ef62e3feb31b7caad27a286f6954a37 — launcher committed and pushed
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
