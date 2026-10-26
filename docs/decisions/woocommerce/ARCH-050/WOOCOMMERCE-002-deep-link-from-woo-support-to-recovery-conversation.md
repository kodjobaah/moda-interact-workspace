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
status: pending
priority: 40
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-050-API-002
enables:
  - ARCH-050-SYSTEM-TEST-002
created: 2026-10-26
updated: 2026-10-26
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

## Work Items

- [ ] Upgrade PHP history validator and JS page validator to exact Support v2 item shape; preserve v1 command receipts.
- [ ] Add pure safe `recoveryConversationHref(recoveryId)` based on current `recoveryDetailHref`; extend Support card action/label without altering billing actions.
- [ ] Set transcript anchor and post-mount focus/scroll (if required by lazy render).
- [ ] Test malformed, missing, cross-shop/null, wrong code/version, billing link regression and WordPress capability/nonce restrictions.

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

## Dependencies

- `ARCH-050-API-002` must be `complete` in canonical task metadata before claim.

## Enables

- `ARCH-050-SYSTEM-TEST-002` may become eligible only after architect acceptance and Complete state.

## Acceptance Criteria

- [ ] Recognised notification displays localized View conversation and opens the exact Woo recovery conversation panel.
- [ ] Malformed/null ID, unrelated/wrong-version code, non-SYSTEM or unavailable message produces no recovery link.
- [ ] PHP/browser validators both accept complete v2 history and reject malformed versions/unknown fields; v1 compose/read still work.
- [ ] No billing action regression and no unauthorized recovery access through manually changed WP URL.
- [ ] Async loading still lands at the transcript; WordPress auth/nonce/install checks stay unchanged.

## Validation

- [ ] Focused Support/recovery detail JS tests via `npm run test:js:unit` and `npm run test:php` for PHP strict validator/controller.
- [ ] `npm run i18n:verify:20`, `npm run build`, targeted lint, `git diff --check`.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, update this task to `review`, provide the Completion Report, return control to `moda_architect`, and **STOP**. Do not start dependent work. A system-test task is terminal and cannot be used as a prerequisite for implementation.

## Implementation Notes

Use the already-existing WP `recoveryDetailHref` sanitization instead of constructing a route from a provider URL or full href returned by hosted API. The hosted read already nulls cross-shop references; PHP/JS must **still** validate the exact shape and build only local first-party links. This task is limited to Support + recovery detail, not Settings (WOOCOMMERCE-001).

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
