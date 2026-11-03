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
status: complete
priority: 30
executor: null
claimed_at: null
attempt: 1
depends_on:
  - ARCH-050-DATABASE-001
enables:
  - ARCH-050-SYSTEM-TEST-001
created: 2026-10-26
updated: 2026-10-27
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

- [x] Extend Support SQL/history typing and strict recovery target projection using `r.shopId=t.shopId`.
- [x] Add recovery action resolver with `systemCode`, string version `"1"`, target validation, route guard.
- [x] Render localized action in `MessageCard` and stable `#recovery-conversation` anchor on transcript section.
- [x] Add negative security/availability tests, action routing tests, and 20-locale coverage.
- [x] Cover actual Support SQL failure separately from expected missing/unauthorised targets: fail through the existing server boundary with Shared structured failure visibility, never silently fall back to an empty/valid response.

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

- [x] Correct merchant sees a localized View conversation action only on matching available ARCH-050 SYSTEM notice.
- [x] Clicking navigates within Shopify to the correct existing Recovery Detail and focuses/scrolls to transcript; page still loads historical conversation.
- [x] Missing, deleted, mismatched-tenant, malformed ID, wrong systemVersion, non-SYSTEM code or inaccessible recovery state causes no action.
- [x] Direct URL to another merchant recovery remains forbidden by existing loader; pagination/unread and billing action links regressions are absent.

## Validation

- [x] Focused tests passed across seven files (98 tests): Support service/query projection, Support route, Shared observability, action resolver/access, transcript anchor, all 20 locale labels, and existing recovery-detail route authorization behavior.
- [x] `npm run typecheck` passed.
- [x] `npm run lint` passed.
- [x] `npm run build` passed. The build emitted non-fatal bundler warnings about Zod annotation comments and chunk size.
- [x] `git diff --check` passed.

## Stop Condition

After Work Items, Acceptance Criteria and required Validation are complete, update this task to `review`, provide the Completion Report, return control to `moda_architect`, and **STOP**. Do not start dependent work. A system-test task is terminal and cannot be used as a prerequisite for implementation.

## Implementation Notes

Treat the recovery FK as a **reference to validate**, never as an authorization grant. The `merchant-support` loader already authenticates Shopify merchant and guards Support; recovery deep link must still pass the separate existing `requireRecoveryHistory` loader. Do not change billing notice handling or `MessageCard` translation behavior.

## Completion Report

### Status

Accepted by architect at Attempt 1; task completed automatically. Attempt 1 implements the localized Support action and transcript deep link while preserving existing billing action behavior and recovery authorization.

### Files Changed

- `app/services/merchant-support/merchant-support.service.ts`
- `app/services/merchant-support/merchant-support-observability.server.ts`
- `app/services/merchant-support/system-message-actions.ts`
- `app/routes/app/merchant-support/route.jsx`
- `app/routes/app/recovery-detail/recovery-conversation-thread.tsx`
- `app/i18n/locales/*.json` (20 supported merchant locales)
- `tests/unit/merchant-support-service.test.ts`
- `tests/unit/merchant-support-route.test.ts`
- `tests/unit/merchant-support-observability.test.ts`
- `tests/unit/merchant-system-message-actions.test.ts`
- `tests/unit/recovery-conversation-anchor.test.ts`
- `tests/unit/merchant-support-recovery-i18n.test.ts`

### Work Completed

Extended the Support history result with a nullable recovery target. The query uses a left join on both recovery ID and thread shop ID and projects the ID only for an AVAILABLE SYSTEM notice with code `RECOVERY_INITIAL_OUTREACH_SENT`, version `1`, and a matching recovery row. Count, unread, paging, translation and mark-read behavior remain unchanged.

Added a separate recovery action resolver. It requires the expected system code/version, an ID of 1–191 characters without path separators/control characters, and `RECOVERY_HISTORY` access. The route renders it only for AVAILABLE SYSTEM messages and uses an internal React Router `Link` to the existing recovery route. The recovery loader still calls `requireRecoveryHistory` and performs its existing tenant-scoped read.

Added the stable `recovery-conversation` section anchor and initial-fragment focus/scroll behavior for the existing transcript heading. Added the localized action label in all 20 merchant locales. Existing billing action resolution is unchanged.

Added a server-only Shared logger adapter. Support SQL failures log a bounded `merchant.support.recovery_action.read.failed` event with validated shop ID, operation, error category and serialized error, then rethrow to the existing route error handling. Unexpected compose failures and best-effort translation dispatch failures also log through Shared; invalid authored bodies are rejected before persistence/logging.

### Validation Results

- Passed: seven focused test files, 98 tests total. Coverage includes query join/projection shape, propagated read failures and Shared logs, guarded action links, billing mapping, anchor focus, locale completeness, and existing recovery-detail access checks.
- Passed: `npm run typecheck`.
- Passed: `npm run lint`.
- Passed: `npm run build`; only non-fatal bundler warnings were emitted.
- Passed: `git diff --check`.

### Deviations

Added structured Shared logging for the pre-existing Support compose and best-effort translation-dispatch catches to satisfy the developer's instruction not to silently swallow exceptions. Authored-body validation remains an expected 400 path and is not logged as an internal failure.

### Assumptions

The Support projection is a navigation hint only. The existing recovery detail loader remains the authorization and tenant-ownership boundary.

### Unresolved Issues

None known within this task's validation contract.

### Architectural Concerns

None identified. The action does not introduce a new query endpoint, permission, stored URL or authorization token.

### Task Branch / Worktree Evidence

Physical worktree isolation:
- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent task worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-050-SHOPIFY-002`, `task/ARCH-050-SHOPIFY-002`.
- Implementation worktree/branch: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-050-SHOPIFY-002`, `task/ARCH-050-SHOPIFY-002`.
- Shared workspace and shared implementation checkouts were not switched or used for task edits; no other task worktree was reused.

Start-of-attempt synchronization:
- Parent remote task branch fast-forwarded: not needed; parent `origin/main` was already incorporated.
- Implementation remote task branch fast-forwarded: not needed; implementation `origin/main` was already incorporated.
- Recursive implementation submodules: `git submodule sync --recursive` passed; `git submodule update --init --recursive` passed; `database` was initialized at `f16d5fc955b1fa1215177cc89fb6fd326bfa65c8`.
- Launcher claim: Attempt 1, executor `codex`, claimed at `2026-10-27T14:24:29Z`, parent claim commit `83ef12853d80e20ec2e2be68f102c1522e727af5` pushed.

No task branch is merged to `main`.

## Architect Review — Attempt 1 — Accepted — 27 October 2026

### Review Status

Accepted.

### Review Notes

The Support query adds only a left join to CheckoutRecovery, joined by both recovery ID and thread shop ID, and projects a target only for the matching AVAILABLE SYSTEM initial-outreach notice at version 1. Other and deleted/mismatched targets remain null; existing count, unread, paging, translation, and read behavior is retained. The recovery action validates the identifier, notice code/version, and RECOVERY_HISTORY access before building an encoded first-party link. The route renders it only for AVAILABLE SYSTEM messages, while the recovery detail loader continues to enforce `requireRecoveryHistory` and tenant-scoped access.

The transcript anchor is stable and focuses/scrolls the existing heading on fragment navigation without changing lazy message loading or pagination. All 20 merchant locales contain the action label, and the existing billing action resolver remains unchanged. Support SQL failures are logged through the Shared server logger with bounded context and rethrown to existing error handling. No new authorization, endpoint, external redirect, or unrelated Support data exposure was introduced.

### Reviewed Files

- `moda-interact/app/services/merchant-support/merchant-support.service.ts`
- `moda-interact/app/services/merchant-support/merchant-support-observability.server.ts`
- `moda-interact/app/services/merchant-support/system-message-actions.ts`
- `moda-interact/app/routes/app/merchant-support/route.jsx`
- `moda-interact/app/routes/app/recovery-detail/recovery-conversation-thread.tsx`
- `moda-interact/app/routes/app/recovery-detail/loader.server.ts`
- All 20 changed locale files and focused Support/action/anchor/authorization tests.
- Attempt 1 Completion Report and canonical worktree/publication evidence.

### Validation Reviewed

- Seven focused test files: 98 tests passed, per the task report.
- `npm run typecheck`, `npm run lint`, and `npm run build` passed; the build emitted non-fatal Zod annotation and chunk-size warnings.
- `git diff --check` passed.
- Implementation branch `task/ARCH-050-SHOPIFY-002` is clean and published at `7a4fccac6b0c38a70b695adbbbc841a090d44732`; database submodule was initialized at `f16d5fc955b1fa1215177cc89fb6fd326bfa65c8`. Neither task branch was merged to `main`.

### Architecture Conformance

Conforms to ARCH-050 ownership and security boundaries. The Support projection supplies a navigation hint only; the existing recovery detail loader remains the authorization boundary. Billing actions and existing recovery detail behavior are preserved.

### Dependency Frontier

This task uses `completion_mode: automatic`; architect acceptance completes Attempt 1. `ARCH-050-SYSTEM-TEST-001` remains pending because its other declared prerequisite `ARCH-050-SHOPIFY-001` is still `ready`, not complete. System testing remains terminal and does not gate implementation.

### Lifecycle

`status: complete`, `executor: null`, `claimed_at: null`, `attempt: 1`. Neither task branch was merged to `main`.
