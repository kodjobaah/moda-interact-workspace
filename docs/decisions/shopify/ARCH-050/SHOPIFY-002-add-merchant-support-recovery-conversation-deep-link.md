---
id: ARCH-050-SHOPIFY-002
architecture_id: ARCH-050
title: Add Shopify Support View conversation action and recovery-section anchor
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: pending
priority: 30
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-050-DATABASE-001
enables:
  - ARCH-050-SYSTEM-TEST-001
created: 2026-10-26
updated: 2026-10-26
---

# Add Shopify Support View conversation action and recovery-section anchor

## Architecture

Architecture ID: `ARCH-050`. Architecture document: `docs/architecture/ARCH-050-merchant-recovery-initial-outreach-support-notifications.md`. Coordinator: `moda_architect`.

## Objective

Render a secure local View conversation action for the new SYSTEM Support notice and focus the matching transcript inside the protected Shopify recovery detail page.

## Context

`app/services/merchant-support/merchant-support.service.ts` reads Support messages, `system-message-actions.ts` currently resolves billing codes, `app/routes/app/merchant-support/route.jsx` renders actions; `app/routes/app/recovery-detail/` owns the recovery transcript.

## Scope

**Modify in `moda-interact/`:**

- `app/services/merchant-support/merchant-support.service.ts` — extend `MessageRow`, raw SQL projection and `MerchantSupportPage.items` to return a nullable tenant-safe `checkoutRecoveryId`.
- `app/services/merchant-support/system-message-actions.ts` — add a strictly gated recovery-specific action resolver, retaining existing billing action logic.
- `app/routes/app/merchant-support/route.jsx` — include recovery action in `MessageCard`, passing `systemVersion`, `checkoutRecoveryId`, `merchantExperienceState`; use `<Link>` for internal navigation.
- `app/routes/app/recovery-detail/recovery-conversation-thread.tsx` — put `id="recovery-conversation"` on stable transcript section/heading; preserve existing `transcript-heading` and paging/focus.
- `app/i18n/locales/*.json` — add `support.viewRecoveryConversation` (and short notice UI text only if needed) in all 20 supported merchant locales.
- Tests: `tests/unit/merchant-support-service.test.ts`, `tests/unit/merchant-support-route.test.ts`, a focused resolver/access test, and relevant recovery detail anchor test.

Do not modify unrelated billing notices, create new recovery query API or redirect to an external URL.

## Out of Scope

- WooCommerce support projections, message writer, human-takeover redesign, phone/basket data in Support.

## Requirements

- Extend the existing Support history SQL with a **left join only** to `"commerce"."CheckoutRecovery" r` such that `r.id = m.checkoutRecoveryId AND r.shopId = t.shopId`, and project nullable recovery ID **only** when `m.kind='SYSTEM'`, `m.state='AVAILABLE'`, `m.systemCode='RECOVERY_INITIAL_OUTREACH_SENT'`, `m.systemVersion='1'` and linked row/shop match. For all other items project `checkoutRecoveryId:null`.
- Do not expose raw FK values from unrelated support messages, references to deleted recoveries, cross-tenant poisoned records or unrecognised system codes. Continue existing Support paging, translated-body, unread and message-mark-read behaviour.
- Recovery action href is built in first-party server/client code as `/app/recoveries/${encodeURIComponent(checkoutRecoveryId)}#recovery-conversation`; validate same recovery ID regex as app's recovery routes (nonempty, no path separators, max 191) before using it.
- Gate action by `canAccessMerchantSurface(merchantExperienceState,"RECOVERY_HISTORY")`. `SUPPORT_ONLY`, `REINSTALLING`, `ONBOARDING`, `SIGNED_OUT` do not get a working recovery link; existing billing actions still work as before.
- `app/routes/app/recovery-detail/loader.server.ts` must continue to invoke existing `requireRecoveryHistory` and tenant-scoped read; Support link is not an authorization token.
- Keep the existing billing `getMerchantSystemMessageAction()` resolver unchanged for billing codes. Add a new recovery resolver (or optional structured argument) without changing billing handling for existing messages.
- Anchor should focus/scroll to the loaded transcript without breaking existing message section lazy loading/pagination; if the heading mounts asynchronously, account for anchor focus on initial load. Use all 20 merchant locale keys.
- Use existing Shopify server-side `@modainteract/moda-interact-shared/logging` facilities if adding a catch for Support SQL/read or recovery detail navigation failures. An actual SQL/authorization infrastructure failure must log a bounded `merchant.support.recovery_action.read.failed` event (validated `shopId` when known, operation, safe error category and `{error}`) and propagate to existing error handling; **never** return an empty Support page, a fabricated `checkoutRecoveryId:null` or a successful page for a database exception. Expected absence, mismatch, unauthorized access, deleted recovery and invalid link IDs are explicitly handled non-error outcomes.
- No new browser logger, console dumping of route errors, or messages containing customer/checkout data. If no new catch is introduced in a particular pure renderer or resolver, preserve normal error propagation rather than adding a catch solely to suppress it.

## Work Items

- [ ] Extend Support SQL/history typing and strict recovery target projection using `r.shopId=t.shopId`.
- [ ] Add recovery action resolver with `systemCode`, string version `"1"`, target validation, route guard.
- [ ] Render localized action in `MessageCard` and stable `#recovery-conversation` anchor on transcript section.
- [ ] Add negative security/availability tests, action routing tests, and 20-locale coverage.
- [ ] Cover actual Support SQL failure separately from expected missing/unauthorised targets: fail through the existing server boundary with Shared structured failure visibility, never silently fall back to an empty/valid response.

## Interfaces / Contracts

- Shopify internal `MerchantSupportPage.items[]` adds required `checkoutRecoveryId: string | null`; fields already returned remain unchanged.
- Proposed new pure helper in `system-message-actions.ts`:

```ts
export function getRecoverySupportMessageAction(input: {
  systemCode: string | null;
  systemVersion: string | null;
  checkoutRecoveryId: string | null;
  merchantExperienceState: MerchantExperienceState;
}): { href: string; labelKey: "support.viewRecoveryConversation" } | null;
```

- Action is present only for `SYSTEM + AVAILABLE + RECOVERY_INITIAL_OUTREACH_SENT + "1" + tenant-validated id + RECOVERY_HISTORY route access`; `MessageCard` may separately check state.
- Destination is precisely `/app/recoveries/<encoded recovery ID>#recovery-conversation`. No stored URL, provider-supplied target, cross-merchant redirect or new permission.
- Server-side failure event (where an owning catch handles a new read failure): `merchant.support.recovery_action.read.failed`, via Shared logger; no client-side Shared/Node imports.

## Dependencies

- `ARCH-050-DATABASE-001` must be `complete` in canonical task metadata before claim.

## Enables

- `ARCH-050-SYSTEM-TEST-001` may become eligible only after architect acceptance and Complete state.

## Acceptance Criteria

- [ ] Correct merchant sees a localized View conversation action only on matching available ARCH-050 SYSTEM notice.
- [ ] Clicking navigates within Shopify to the correct existing Recovery Detail and focuses/scrolls to transcript; page still loads historical conversation.
- [ ] Missing, deleted, mismatched-tenant, malformed ID, wrong systemVersion, non-SYSTEM code or inaccessible recovery state causes no action.
- [ ] Direct URL to another merchant recovery remains forbidden by existing loader; pagination/unread and billing action links regressions are absent.

## Validation

- [ ] Focused tests: `tests/unit/merchant-support-service.test.ts`, `tests/unit/merchant-support-route.test.ts`, new action-resolver and recovery anchor tests.
- [ ] Run declared Shopify typecheck/lint/build commands and locale completeness tests; `git diff --check`.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, update this task to `review`, provide the Completion Report, return control to `moda_architect`, and **STOP**. Do not start dependent work. A system-test task is terminal and cannot be used as a prerequisite for implementation.

## Implementation Notes

Treat the recovery FK as a **reference to validate**, never as an authorization grant. The `merchant-support` loader already authenticates Shopify merchant and guards Support; recovery deep link must still pass the separate existing `requireRecoveryHistory` loader. Do not change billing notice handling or `MessageCard` translation behavior.

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
