---
id: ARCH-046-WOOCOMMERCE-007
architecture_id: ARCH-046
title: Manage merchant Woo customer recovery selection
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 35
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-046-API-005
  - ARCH-035-WOOCOMMERCE-016
enables:
  - ARCH-046-SYSTEM-TEST-001
  - ARCH-046-SYSTEM-TEST-002
created: '2026-10-21'
updated: 2026-10-23
---
# Manage merchant Woo customer recovery selection

## Architecture

Architecture ID: `ARCH-046`
Architecture document: `docs/architecture/ARCH-046-woocommerce-whatsapp-consent-gated-recovery.md`
Coordinator: `moda_architect`
**Lifecycle:** Developer-owned Attempt 1 was claimed on 2026-10-23. Implementation commit `3bfa02658e2ba45df69745b906bd4eaa11ba9e0f` is pushed to `task/ARCH-046-WOOCOMMERCE-007`; repository validation, accepted developer self-review and explicit developer completion are recorded below. No task branch was merged to `main`.

## Objective

Let the existing WooCommerce merchant admin select/deselect which consented customers are eligible for recovery and record off-channel customer STOP, without treating merchant selection as customer consent.

## Context

Merchant-operated Support/Recovery UI exists; a request received outside WhatsApp must be recorded and enforced through hosted CustomerPhone instead of temporary reachability suppression.

## Scope

- Extend existing privileged Woo Support/Recovery surface with enable/disable recovery controls and a customer STOP action on one merchant-scoped unambiguous CustomerPhone; re-use WP capability checks, REST nonce and current installation auth.
- Proxy only to authenticated API-005, with double-click prevention, safe error state and clear result; use canonical phone lookup under the authenticated installation/shop, refuse ambiguous matches and never treat selecting a phone as a grant.
- Make the action available only to authorised Woo merchant administrators; retain existing localisation and no-new-role policy.

## Out of Scope

- No external customer consent grants, new staff assignment model or standalone inbox.
- No LocalWP environment deployment, live WordPress/WooCommerce browser operation, live hosted API-005 interoperability, real customer/tenant end-to-end exercise, or HPOS/Classic/Blocks live certification inside this repository implementation task. Those activities belong to the terminal ARCH-046 system-test programme, not WOOCOMMERCE-007's implementation acceptance gate.

## Requirements

- [x] Merchant can deselect a customer to suppress recovery, reselect only a currently consented customer to remove the merchant suppression, and record an outside-channel customer STOP, with tenant/capability checks at the WordPress boundary; verified using mocked hosted responses and PHP/JavaScript tests.
- [x] Action cannot create or schedule recovery, grant consent, clear customer STOP or modify another tenant; verified at the plugin contract/transport boundary in automated tests.

These checked items report repository-implementation behaviour, not live LocalWP or hosted-system certification.

## Work Items

- [x] Extend the existing privileged Woo Recoveries surface with enable/disable controls and customer STOP on one merchant-scoped canonical-phone lookup; reuse WP capability checks, REST nonce and installation auth.
- [x] Proxy only to authenticated API-005 using validated contracts, duplicate-submission prevention, safe error state and explicit result; refuse ambiguous matches and never convert merchant selection into a consent grant.
- [x] Restrict the actions to Woo merchant administrators without new staff roles; add and validate the source translations across all 20 supported locales.
- [x] Add focused PHP and JavaScript tests and preserve checkout-consent functionality owned by concurrent WOOCOMMERCE-001 work.

## Interfaces / Contracts

Owner: `moda-interact-woocommerce` (`moda_woocommerce`). Use the canonical Database/Shared contracts named in this architecture; authorise only this repository's implementation. No consent-triggered checkout recovery job, new merchant role, or raw personally identifiable logging.

## Dependencies

- `ARCH-046-API-005`
- `ARCH-035-WOOCOMMERCE-016`

## Enables

- `ARCH-046-SYSTEM-TEST-001`
- `ARCH-046-SYSTEM-TEST-002`

**Terminal system-test boundary:** Any LocalWP deployment, real WooCommerce admin/checkout operation, API-005/installation interoperability, live Shop-scoped lookup, STOP persistence, tenant isolation or HPOS behaviour must be verified by the applicable ARCH-046 system-test task after all its dependencies have been accepted. WOOCOMMERCE-007 does not need LocalWP to be installed or deployed for repository implementation review. `ARCH-046-SYSTEM-TEST-002` retains its independent blocked/eligibility gate; this task does not promote or execute it.

## Acceptance Criteria

- [x] Merchant suppression, conditional re-enable and support-ticket-backed customer STOP are exposed through the existing Woo Recoveries UI and authenticated API-005 proxy; capability, nonce, tenant-scoped contract and stale-state failure tests pass.
- [x] Plugin code cannot grant consent, clear customer STOP, create/schedule recovery or issue cross-Shop commands through the selected contract; failure and duplicate-submit safeguards are tested.
- [x] No new merchant identity/role or separate inbox is created; all source translation catalogues and the plugin build validate.

These criteria are bounded to code plus repository-controlled test evidence. Live LocalWP/hosted end-to-end proof is not an acceptance criterion for WOOCOMMERCE-007 and remains the responsibility of system testing.

## Validation

- [x] Focused PHP controller contract tests (`composer test -- tests/RecoverySelectionControllerTest.php`): **6/6 tests, 43 assertions**; capability, REST nonce, installation-scoped forwarding and hosted failures exercised using test doubles.
- [x] Full repository PHP suite (`npm run test:php`): **166/166 tests, 1,252 assertions**.
- [x] JavaScript unit suite (`npm run test:js`): **445/445 WordPress JS tests** and **52/52 Node integration/localisation tests** passed, including merchant-selection behaviour.
- [x] Source localisation (`npm run test:i18n` and `npm run i18n:verify:20`): **28/28 localisation tests**, 512 source messages, and strict compilation of **19/19 translation packs** for the 20 supported locales including English.
- [x] Production plugin build (`npm run build`): passed; webpack bundle-size warnings noted, no build failure.
- [x] `git diff --check`: passed in local validation.

**Not required for this implementation task:** starting/deploying LocalWP, installing a plugin into a live WP/Woo store, live Classic/Blocks/HPOS manual checkout/admin tests, or live hosted API-005/PostgreSQL/tenant integration. Those checks are deferred to the applicable terminal ARCH-046 system-test tasks. They must not be represented as passed on the strength of repository tests alone.

## Stop Condition

After defined Work Items, Acceptance Criteria and required Validation, record dedicated parent/implementation task worktree and start-of-attempt synchronisation evidence, set `status: review`, submit Completion Report to `moda_architect`, and STOP. No dependent task may start before architect acceptance.

## Implementation Notes

Use the architect-approved consent model: no initial CheckoutRecovery without verified current permission, no arbitrary consent timeout, and consent changes do not trigger checkout reconciliation. Follow the current `/moda-task` launcher and exact published Shared/Database contracts. Preserve `docs/decisions/**/_index.md` until architecture session completion is confirmed. Use Shared structured logging on Node; bounded WordPress-safe diagnostics in PHP. Any missing cross-repository capability returns to architect rather than being implemented outside repository ownership.

## Completion Report

### Status

**Complete — developer Attempt 1.** The developer explicitly completed this task on 2026-10-23 after the durable Accepted Attempt 1 self-review and required validation. The implementation was committed as `3bfa02658e2ba45df69745b906bd4eaa11ba9e0f` and pushed to `origin/task/ARCH-046-WOOCOMMERCE-007`. No task branch was merged to `main`.

### Developer Completion Decision — Attempt 1 (2026-10-23)

The developer explicitly completed ARCH-046-WOOCOMMERCE-007 after the durable Accepted Attempt 1 self-review. All Work Items, Acceptance Criteria and required repository validation items are complete. The implementation branch and parent task branch are clean and published; no merge to `main` was performed. Architect acceptance remains a separate lifecycle decision.

### Dependency Frontier Update

- `ARCH-046-API-005`: complete on its task branch; parent completion decision is published.
- `ARCH-035-WOOCOMMERCE-016`: complete.
- Both declared dependencies are satisfied and were verified before completion.
- Dependency-frontier reconciliation found no ordinary downstream task that became claimable solely from this completion. `ARCH-046-SYSTEM-TEST-001` remains `pending` because other declared dependencies are incomplete; `ARCH-046-SYSTEM-TEST-002` remains intentionally `blocked` by its independent approved Woo recovery-engine gate. Neither system-test task was started or modified.

### Files Changed

Implementation commit `3bfa02658e2ba45df69745b906bd4eaa11ba9e0f` contains exactly 41 changed files:

- `moda-interact-woocommerce/includes/Api/ModaApiClient.php`
- `moda-interact-woocommerce/includes/Api/RecoverySelectionContracts.php`
- `moda-interact-woocommerce/includes/Rest/RecoverySelectionController.php`
- `moda-interact-woocommerce/includes/Runtime.php`
- `moda-interact-woocommerce/languages/moda-interact-cs_CZ.po`
- `moda-interact-woocommerce/languages/moda-interact-da_DK.po`
- `moda-interact-woocommerce/languages/moda-interact-de_DE.po`
- `moda-interact-woocommerce/languages/moda-interact-es_ES.po`
- `moda-interact-woocommerce/languages/moda-interact-fi.po`
- `moda-interact-woocommerce/languages/moda-interact-fr_FR.po`
- `moda-interact-woocommerce/languages/moda-interact-it_IT.po`
- `moda-interact-woocommerce/languages/moda-interact-ja.po`
- `moda-interact-woocommerce/languages/moda-interact-ko_KR.po`
- `moda-interact-woocommerce/languages/moda-interact-nb_NO.po`
- `moda-interact-woocommerce/languages/moda-interact-nl_NL.po`
- `moda-interact-woocommerce/languages/moda-interact-pl_PL.po`
- `moda-interact-woocommerce/languages/moda-interact-pt_BR.po`
- `moda-interact-woocommerce/languages/moda-interact-pt_PT.po`
- `moda-interact-woocommerce/languages/moda-interact-sv_SE.po`
- `moda-interact-woocommerce/languages/moda-interact-th.po`
- `moda-interact-woocommerce/languages/moda-interact-tr_TR.po`
- `moda-interact-woocommerce/languages/moda-interact-zh_CN.po`
- `moda-interact-woocommerce/languages/moda-interact-zh_TW.po`
- `moda-interact-woocommerce/languages/moda-interact.pot`
- `moda-interact-woocommerce/src/index.scss`
- `moda-interact-woocommerce/src/recoveries/customer-selection/_selection.scss`
- `moda-interact-woocommerce/src/recoveries/customer-selection/selection-client.js`
- `moda-interact-woocommerce/src/recoveries/customer-selection/selection-contract.js`
- `moda-interact-woocommerce/src/recoveries/customer-selection/selection-controller.js`
- `moda-interact-woocommerce/src/recoveries/customer-selection/selection-messages.js`
- `moda-interact-woocommerce/src/recoveries/customer-selection/selection-panel.js`
- `moda-interact-woocommerce/src/recoveries/customer-selection/use-selection.js`
- `moda-interact-woocommerce/src/recoveries/recoveries-screen.js`
- `moda-interact-woocommerce/tests/RecoverySelectionControllerTest.php`
- `moda-interact-woocommerce/tests/i18n/locale-batch-010.test.mjs`
- `moda-interact-woocommerce/tests/i18n/locale-batch-011.test.mjs`
- `moda-interact-woocommerce/tests/i18n/locale-batch-012.test.mjs`
- `moda-interact-woocommerce/tests/i18n/locale-batch-013.test.mjs`
- `moda-interact-woocommerce/tests/i18n/release-assets.test.mjs`
- `moda-interact-woocommerce/tests/i18n/release-source.test.mjs`
- `moda-interact-woocommerce/tests/js/customer-recovery-selection.test.js`

### Work Completed

- Implemented a WordPress REST controller behind existing Woo administrator capability, nonce and installation authentication, with a typed/validated client proxy to hosted API-005 and strict response checks.
- Added a modular Recoveries screen customer-selection panel, transport, DTO validation and state controller for canonical-phone lookup, merchant suppression/re-enable and off-channel STOP with a support reference.
- Preserved consent/source ownership: no implied grant from merchant re-enable, no customer STOP clearance, no recovery scheduling, and no new merchant roles.
- Added PHP/JavaScript behaviour tests, merchant-safe errors and duplicate/stale command handling.
- Updated 19 `.po` source catalogues, the `.pot` template and localisation assertions to 512 messages while preserving parallel WOOCOMMERCE-001 checkout-consent work. Generated `.mo` and locale JavaScript `.json` outputs were intentionally excluded from the source commit.

### Validation Results

- `composer test -- tests/RecoverySelectionControllerTest.php`: **6/6 passed**, 43 assertions.
- `npm run test:php`: **166/166 passed**, 1,252 assertions.
- `npm run test:js`: **445/445 WordPress JS** and **52/52 Node integration/localisation** tests passed.
- `npm run test:i18n`: **28/28 passed**.
- `npm run i18n:verify:20`: **512 messages**, strict **19/19** translated packs, 38 generated assets; generated outputs not committed.
- `npm run build`: passed with non-blocking webpack performance/bundle-size warnings.
- `git diff --check`: passed on local implementation diff before commit.
- Published commit `3bfa02658e2ba45df69745b906bd4eaa11ba9e0f` on `origin/task/ARCH-046-WOOCOMMERCE-007` (push confirmed by developer).
- **LocalWP/live WordPress/Woo, hosted API-005 and real tenant end-to-end validation not run and expressly outside this task's gate**; those belong to ARCH-046 system testing.

### Deviations

- No repository-owned implementation scope deviation. The checkout-consent changes already present from WOOCOMMERCE-001 were preserved when rebasing the implementation patch; this did not transfer checkout-consent ownership to WOOCOMMERCE-007.
- LocalWP deployment and live validation are deliberately excluded from this task by developer instruction and assigned to terminal system testing.

### Assumptions

- Published ARCH-046-API-005 and ARCH-035-WOOCOMMERCE-016 are the accepted dependencies; repository mocks validate the WordPress-to-hosted contract but do not substitute for a live provider environment.
- Dedicated worktree was used as shown by developer's command prompt and task claim; launcher-resolved isolation/start-of-attempt synchronisation evidence should be checked in the developer self-review record before acceptance.

### Unresolved Issues

- Live LocalWP/hosted-API interoperability, real tenant/phone persistence, STOP precedence and browser behaviour remain unverified until system-test execution; not blocking repository-owned completion.
- Concurrent WOOCOMMERCE-001/007 changes to `Runtime.php` and translation catalogues require integration reconciliation when merging their branches; no generated assets should be force-added.

### Architectural Concerns

- No new cross-repository contract, database mutation or consent grant mechanism introduced. The plugin delegates merchant decisions to hosted API-005 and maintains WordPress authorization boundaries. Terminal ARCH-046 system tests own live operational verification; SYSTEM-TEST-002's separate blocked condition must not be bypassed.

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

## Developer Self-Review - Accepted (2026-10-23)

The implementation branch is clean and published at `3bfa02658e2ba45df69745b906bd4eaa11ba9e0f`. The initial JavaScript/build validation was blocked because the isolated worktree's ignored `node_modules` lacked the declared `@wordpress/scripts` binary; `package.json` and `package-lock.json` both pin `@wordpress/scripts` 36.0.0. Running `npm ci --ignore-scripts` restored the locked dependency set without changing tracked files. The review then found and corrected Prettier/ESLint violations in the new customer-selection JavaScript and SCSS; no behavioral scope changed.

Final review evidence from the canonical implementation worktree:

- Focused PHP controller tests: **6/6 passed**, 43 assertions.
- Full PHP suite: **166/166 passed**, 1,252 assertions.
- Full JavaScript and integration/localisation suite: **445/445 WordPress JS tests** and **52/52 Node tests** passed.
- Strict i18n verification: **512 messages**, **19/19 translation packs**, 38 generated assets.
- JavaScript lint: no errors; six pre-existing billing-screen warnings remain.
- CSS lint and PHP lint: passed.
- Production build: passed with three non-blocking webpack bundle-size warnings.
- `git diff --check origin/main...HEAD`: passed.

No live LocalWP, hosted API-005, or real tenant end-to-end certification was claimed; those checks remain assigned to the ARCH-046 system-test tasks. The implementation satisfies the repository-scoped Work Items and Acceptance Criteria. Since `completion_mode: developer`, `status: review`, `executor: null`, `claimed_at: null`, and `attempt: 1` are durable; explicit developer completion and architect acceptance remain pending.

## Developer Takeover

On 2026-10-23, `/moda_developer_create ARCH-046-WOOCOMMERCE-007` was invoked while this task was ready and agent-owned. This is an explicit developer takeover. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_woocommerce`, repository ownership, dependencies, scope and acceptance criteria are unchanged. Attempt 1 was subsequently claimed as `developer` at 2026-10-23T10:49:59Z, as recorded in canonical task metadata. The developer self-review must confirm the launcher-resolved physical worktree isolation and start-of-attempt synchronisation evidence; the implementation commit and repository tests alone do not replace that evidence.
