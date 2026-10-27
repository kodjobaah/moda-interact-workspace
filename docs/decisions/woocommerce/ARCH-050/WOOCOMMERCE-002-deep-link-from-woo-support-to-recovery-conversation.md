---
id: ARCH-050-WOOCOMMERCE-002
architecture_id: ARCH-050
title: Add WooCommerce Support View conversation action and transcript anchor
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 40
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-050-API-002
enables:
  - ARCH-050-SYSTEM-TEST-002
created: 2026-10-26
updated: 2026-10-27
---

# Add WooCommerce Support View conversation action and transcript anchor

## Architecture

Architecture ID: `ARCH-050`. Architecture document: `docs/architecture/ARCH-050-merchant-recovery-initial-outreach-support-notifications.md`. Coordinator: `moda_architect`.

## Objective

Render a safe recovery-specific action in Woo Support and navigate inside the existing WordPress Recovery Detail conversation section.

## Context

`src/support/support-contract.js` and `src/support/support-message-card.js` own Support data/action rendering; `src/recoveries/detail/detail-navigation.js` exports `recoveryDetailHref()`; Woo recovery conversation is rendered within the existing Woo admin page.

## Scope

**Modify in `moda-interact-woocommerce/`:**

- `includes/Api/SupportResponseValidator.php` — update **history** page validator to v2 and add exact `checkoutRecoveryId` item property; preserve compose/read receipt version 1.
- `includes/Api/ModaApiClient.php` — ensure `merchantSupportHistory()` passes v2 response through the strict updated PHP validator; leave other Support request behaviour unchanged.
- `src/support/support-contract.js` — strict `parseSupportPage()` v2, required nullable validated recovery ID on every item; compose/read v1 validators untouched.
- `src/support/support-message-card.js` — extend `supportSystemHref(message)` with recovery action only on `SYSTEM`, `AVAILABLE`, recognised code, version `"1"`, valid ID.
- `src/recoveries/detail/detail-navigation.js` — reuse `recoveryDetailHref()` (no extra arbitrary query/page input) to construct local recovery URL with `#recovery-conversation`; optionally add `recoveryConversationHref(id)` pure helper.
- `src/recoveries/detail/conversation/conversation-panel.js` — stable `id="recovery-conversation"` on conversation section, retaining its existing accessible heading ID `moda-recovery-conversation-title`.
- If necessary for lazy detail mounting, minimally update `src/recoveries/detail/connected-recovery-detail-screen.js` or the nearest existing controller to scroll/focus after the section becomes available.
- Tests: `tests/js/support-client.test.js`, `tests/js/support-screen.test.js`, `tests/js/recovery-detail-integration.test.js`, `tests/SupportControllerTest.php` and PHP validator tests.

No new Woo public endpoint or background-provider callback is allowed.

## Out of Scope

- Saving the opt-in, hosted API projection, extending system message writer, bypassing WP capabilities or exposing new external checkout reads.

## Requirements

- Mirror **API-002 v2** exactly: successful Support history page `schemaVersion:2`, each item includes `checkoutRecoveryId:string|null`; `composeReceipt` and `readReceipt` remain v1.
- Update both `SupportResponseValidator::history()` and `parseSupportPage()` exact keys to reject missing/extra property, wrong type, unsafe ID. Allow `null` for unrelated/deleted/rejected references; validate non-null ID with the same `[A-Za-z0-9_-]{1,191}` recovery-ID format already used in `detail-navigation.js`.
- In `supportSystemHref(message)` detect `kind=SYSTEM`, `state=AVAILABLE`, `systemCode="RECOVERY_INITIAL_OUTREACH_SENT"`, `systemVersion="1"`, and valid non-null `checkoutRecoveryId`. Use `recoveryDetailHref(id)` to generate *only* `admin.php?page=moda-interact-recoveries&recoveryId=<encoded>` then append `#recovery-conversation`. Preserve existing `BILLING_*` fixed action targets and billing action labels.
- Render a localized **View conversation** label for recovery notices (not View billing); keep WordPress `__()` translations and accessible link text. No HTML injected from message content; href never from remote provider/body.
- Conversation panel section must have stable `id="recovery-conversation"`. If the detail is rendered asynchronously after initial navigation, ensure scrolling/heading focus executes once the panel is mounted; invalid/missing recovery still shows safe unavailable shell.
- Existing WordPress `manage_woocommerce`, REST nonce and installation protections remain. Deep link does not bypass hosted recovery-details tenant authorization. Do not expose inaccessible recovery IDs if API returned null.
- PHP/JS must **not** import the Node Shared logger. The hosted API-002 uses the canonical `@modainteract/moda-interact-shared/logging` logger for unexpected Support-history failures. If plugin PHP introduces a `\Throwable` catch around `SupportController.php` / `ModaApiClient.php`, use the existing Woo/WordPress logger (`wc_get_logger()` source `moda-interact`) with stable operation and redacted error code/class, then preserve the existing protected `WP_Error`/HTTP response. Avoid a competing generic PHP logger.
- For browser errors, the current Support controller must show its existing error/retry state on transport or rejected strict-v2 contract responses; do not `catch {}` and return an empty successful Support inbox. A missing/deleted/other-shop recovery is an expected *null link*, while a failed API read is an exceptional error. No raw customer message, token, hosted response or full exception payload in client telemetry.

## Work Items

- [x] Upgrade PHP history validator and JS page validator to exact Support v2 item shape; preserve v1 command receipts.
- [x] Add pure safe `recoveryConversationHref(recoveryId)` based on current `recoveryDetailHref`; extend Support card action/label without altering billing actions.
- [x] Set transcript anchor and post-mount focus/scroll after the async detail component mounts.
- [x] Test malformed, missing, null/cross-shop reference, wrong code/version, billing link regression and WordPress capability/nonce restrictions.
- [x] Add failure-path tests distinguishing intentionally unavailable recovery links from thrown Support transport/contract errors; verify plugin error state and non-swallowing PHP error boundary.

## Interfaces / Contracts

- Consume API-002 `SupportPageV2` where `item.checkoutRecoveryId` is a nullable validated same-shop recovery ID.
- New optional local navigation helper:

```js
export function recoveryConversationHref(recoveryId) {
  const base = recoveryDetailHref(recoveryId);
  return base ? `${base}#recovery-conversation` : null;
}
```

- Navigation target must be `admin.php?page=moda-interact-recoveries&recoveryId=<encoded>#recovery-conversation`; generated locally in WP admin. Billing SYSTEM hrefs remain fixed at their existing pages.
- No server-to-WordPress push, new polling mechanism or public webhook.
- Logging/exception ownership: hosted route shared `StructuredLogger` (API-002) logs backend errors; PHP logs newly caught operational exceptions through existing Woo/WP logger; JS surfaces failures via Support error UI. Browser and PHP must not import Node Shared logging.

## Dependencies

- `ARCH-050-API-002` must be `complete` in canonical task metadata before claim.

## Enables

- `ARCH-050-SYSTEM-TEST-002` may become eligible only after architect acceptance and Complete state.

## Acceptance Criteria

- [x] Recognised notification displays localized View conversation and opens the exact Woo recovery conversation panel.
- [x] Malformed/null ID, unrelated/wrong-version code, non-SYSTEM or unavailable message produces no recovery link.
- [x] PHP/browser validators both accept complete v2 history and reject malformed versions/unknown fields; v1 compose/read still work.
- [x] No billing action regression and no unauthorized recovery access through manually changed WP URL.
- [x] Async loading still lands at the transcript; WordPress auth/nonce/install checks stay unchanged.
- [x] Real Support read/contract failure is shown as failure rather than silently replaced with an empty page; intentional null recovery references simply omit the link.

## Validation

- [x] Focused Support/recovery detail JS tests via `npm run test:js:unit` and `npm run test:php` for PHP strict validator/controller.
- [x] Negative browser/PHP test verifies failed v2 history/transport does not show a successful empty inbox; check bounded PHP logging when a new catch is introduced.
- [x] `npm run i18n:verify:20`, `npm run build`, targeted lint, `git diff --check`.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, update this task to `review`, provide the Completion Report, return control to `moda_architect`, and **STOP**. Do not start dependent work. A system-test task is terminal and cannot be used as a prerequisite for implementation.

## Implementation Notes

Use the already-existing WP `recoveryDetailHref` sanitization instead of constructing a route from a provider URL or full href returned by hosted API. The hosted read already nulls cross-shop references; PHP/JS must **still** validate the exact shape and build only local first-party links. This task is limited to Support + recovery detail, not Settings (WOOCOMMERCE-001).

## Completion Report

### Status

Ready for architect review.

### Files Changed

Support PHP/JS contracts and controller logging; recovery detail navigation and conversation section; Support and recovery detail tests; gettext POT and all 19 PO catalogs.

### Work Completed

Woo Support history now strictly validates schema v2 with a required nullable, safe `checkoutRecoveryId` on every message. Compose/read receipts remain v1. Eligible recovery outreach notices get a local, validated conversation link and translated label; the existing billing destinations and labels remain intact. The conversation section has a stable anchor, and the connected detail screen scrolls to it after mount when the URL carries the anchor. Unexpected Support proxy exceptions are logged through `wc_get_logger()` with a stable operation and bounded class/code context; logger failures preserve the sanitized 503 response. PHP and browser failure paths are covered.

### Validation Results

`npm run test:js:unit`: passed, 61 files / 464 tests. `npm run test:php`: passed, 217 tests / 1,670 assertions with one warning. `npm run i18n:verify:20`: passed as part of `npm run build` (558 source messages; 19/19 translation packs); build passed with existing webpack bundle-size warnings. PHP lint passed. Targeted JS lint passed on all changed JS files. `git diff --check` passed. Full-repository JS lint reports existing issues in unrelated integration files; changed task files pass targeted lint.

### Deviations

No `ModaApiClient.php` change was needed because `merchantSupportHistory()` already routes successful history responses through `SupportResponseValidator::history()`.

### Assumptions

The completed API-002 schema is the source of truth for the v2 history shape. Existing Woo `wc_get_logger()` is the appropriate plugin-side exception logger; the Node Shared logger is not imported into the PHP plugin.

### Unresolved Issues

The repository-wide JS lint command reports pre-existing formatting/rule violations in unrelated integration files. All changed task JavaScript files pass targeted lint.

### Architectural Concerns

None discovered. Existing capability, REST nonce, installation identity and hosted tenant authorization paths remain unchanged.

### Task Branch / Worktree Evidence

Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-050-WOOCOMMERCE-002`, branch `task/ARCH-050-WOOCOMMERCE-002`. Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-050-WOOCOMMERCE-002`, branch `task/ARCH-050-WOOCOMMERCE-002`. The original launcher claim was durable; a later prepare correctly refused to overwrite the active Attempt 1.

## Architect Review

### Attempt 1 Architect Review

#### Review Status

Changes Requested — report/evidence only

#### Review Notes

The implementation diff and recorded functional validation conform to the task
scope. The strict Support history v2 validators, same-site local conversation
link, existing fixed billing links, transcript anchor, async detail mount, and
failure-path handling are consistent with the task and the accepted
`ARCH-050-API-002` dependency. No implementation change is requested.

Acceptance is withheld because the Completion Report does not include the
required start-of-attempt synchronization evidence. It records the launcher
worktree paths and task branch names, but not the starting HEADs or the task
branch / `origin/main` synchronization outcomes for both repositories. The
statement that a later prepare refused to overwrite Attempt 1 is not a substitute
for the original prepared packet evidence. The PHP test report also says “one
warning” without identifying or classifying that warning.

#### Reviewed Files

- Implementation commit `540a36533071cd9e51a5b8a817877839e97aa049` and its 32-file diff from `origin/main`.
- `includes/Api/SupportResponseValidator.php`
- `includes/Rest/SupportController.php`
- `src/support/support-contract.js`
- `src/support/support-message-card.js`
- `src/recoveries/detail/detail-navigation.js`
- `src/recoveries/detail/connected-recovery-detail-screen.js`
- `src/recoveries/detail/conversation/conversation-panel.js`
- The task’s PHP and JavaScript tests and Completion Report.
- `ARCH-050` architecture and `ARCH-050-API-002` dependency record.

#### Validation Reviewed

The report records passing `npm run test:js:unit` (61 files / 464 tests),
`npm run test:php` (217 tests / 1,670 assertions), `npm run build` and
`npm run i18n:verify:20`, PHP lint, targeted JS lint, and `git diff --check`.
The implementation branch is clean at the pushed commit. I did not rerun the
checks. The PHP test warning is not described, so its significance cannot yet
be assessed.

#### Architecture Conformance

The code changes stay within WooCommerce ownership and implement the API-002 v2
contract without exposing an external URL or bypassing recovery authorization.
The claimed dependency `ARCH-050-API-002` is Complete in this task branch. The
implementation worktree and parent worktree paths match the launcher-resolved
canonical task locations. Workflow evidence remains incomplete pending the
prepared packet synchronization details and warning classification.

#### Follow-up

Return this same task to the existing execution path for a report-only
correction. Preserve the implementation at `540a36533071cd9e51a5b8a817877839e97aa049`
and the recorded validation; no code changes or test reruns are requested unless
the warning investigation shows a validation failure. Add to the Completion
Report, from the original Attempt 1 prepared packet:

1. The parent and implementation starting HEADs.
2. For each repository, the remote task-branch fast-forward result and whether
   `origin/main` was already incorporated.
3. Recursive submodule synchronization/update outcome and commit evidence, or
   explicitly state that the implementation repository has no registered
   submodules.
4. The exact `npm run test:php` warning and why it is non-blocking or how it was
   resolved.

The Attempt 1 claim remains historical. Task status is Ready, executor/claim are
cleared, and `attempt: 1` is preserved so the next authorized claim increments
it once. No dependent task is promoted.
