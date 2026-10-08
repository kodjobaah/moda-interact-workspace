---
id: ARCH-005-SHOPIFY-004
architecture_id: ARCH-005
title: Complete authenticated Shopify merchant UI internationalisation coverage
task_kind: implementation
domain: shopify
repository: moda-interact
assigned_agent: moda_app
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: ready
priority: 55
executor: null
claimed_at: null
attempt: 0
depends_on:
  - ARCH-005-SHOPIFY-002
  - ARCH-006-SHOPIFY-003
  - ARCH-007-SHOPIFY-002
enables:
  - ARCH-005-SYSTEM-TEST-001
created: 2026-09-08
updated: 2026-10-08
---

# ARCH-005-SHOPIFY-004: Complete authenticated Shopify merchant UI internationalisation coverage

## Architecture

Canonical architecture: `docs/architecture/ARCH-005-global-internationalisation-whatsapp-markets.md`.
Coordinator: `moda_architect`.

## Objective

Finish residual *authenticated* Shopify app-shell and merchant-support
internationalisation using the existing Shared ICU runtime and existing 20
merchant locale catalogues; preserve tenant, messaging and billing behaviour.

## Context

This task follows architect-accepted `ARCH-005-SHOPIFY-002`,
`ARCH-006-SHOPIFY-003` and `ARCH-007-SHOPIFY-002`; all three are Complete in
this snapshot. It is Ready for Attempt 1, not yet implemented.

The Shopify app has since moved to an explicit React Router v7 nested directory
layout (`app/routes.ts`). Its navigation is already translated by
`app/components/dashboard/MerchantNavigation.tsx`; `merchantUi` already comes
from the authenticated parent loader in `app/routes/app/route.jsx`.

The old example/additional route has been removed, the Usage/Recovery Guest
fallback is already presentation-owned, and billing options no longer render
the raw subscription `ACTIVE`/`TRIALING` status as a merchant-facing label.
Do not recreate, re-internationalise or refactor any of those completed/retired
mechanisms merely to satisfy the superseded September file list.

Source inspection on 2026-10-08 identified these remaining specific gaps:
- `app/routes/app/route.jsx`: logo `alt` text is still English.
- `app/routes/app/merchant-support/route.jsx`: heading, support controls,
  sender/status labels and translation toggles still contain English literals.
- That support action still returns raw exception text and an English
  unsupported-intent response directly to the merchant component.

The canonical new key names and exact English meanings are specified **only** in:
`docs/decisions/shopify/ARCH-005/18n-key-SHOPIFY-004-imanifest.md`.

## Scope

Only the following implementation/test surfaces may change, unless a directly
required import or test fixture forces a small explained adjacent edit:

```text
moda-interact/app/routes/app/route.jsx
moda-interact/app/routes/app/merchant-support/route.jsx
moda-interact/app/i18n/locales/*.json
moda-interact/tests/unit/merchant-i18n.test.ts
moda-interact/tests/unit/merchant-support-route.test.ts
moda-interact/tests/unit/shopify-ui-i18n-coverage.test.ts   # create
```

## Out of Scope

- Removed `app.additional` route and any `additional.*` translation keys.
- `MerchantNavigation.tsx`: its existing `merchantNav.*` labels and number
  formatting are already correct; do not duplicate `navigation.*` keys.
- Home/usage loaders and `UsageEvents.tsx`: they already use null customer data
  and `chart.guest` at the presentation boundary.
- Billing status UI, billing policy, entitlements, provider verification and
  `billing.statusActive`/`billing.statusTrialing` keys; no current scoped UI
  renders the former raw enum label.
- Pre-authentication routes, privacy/legal copy, deprecated PlanSelector and
  other dead components, health/webhook/resource routes, internal diagnostics.
- Database, Shared, Admin, Background, Messaging and Gateway implementation.
- Existing message-body translation pipeline and arbitrary merchant content.

## Requirements

### Reuse the existing runtime and locale precedence

Use `createMerchantI18n(...)` and the existing
`@modainteract/moda-interact-shared/internationalization` runtime. Preserve
`merchantUiContext(shop, session)` in the authenticated parent loader and
`merchantUiContext(...)` in the support route. Do **not** query a second
ShopSettings record, introduce Outlet context or a new locale/translator/runtime.
Preserve current Shop-scoped authentication, guard and redirect semantics.

### App shell: logo alt text

In `app/routes/app/route.jsx`, use the existing `merchantUi` loader payload
and `createMerchantI18n(merchantUi)` to change only the logo alt text from
`Moda Interact logo` to `i18n.t("common.logoAlt")`. Retain the image asset,
`AppProvider`, `MerchantNavigation` and Outlet unchanged.

### Merchant support page

In `app/routes/app/merchant-support/route.jsx`, reuse its existing `i18n`
instance and use the existing `merchantNav.support` key for the page heading
(instead of `dashboard.messagesSent`, which describes a metric, not Support).
Use the manifest `support.*` keys for the thread heading, empty state, page
pagination/aria labels, contact/compose controls, sender labels, translation
status and the original/translation toggle.

For pagination call `i18n.t("support.page", {page, totalPages})`. For client
1–500-grapheme validation call
`i18n.t("support.messageLengthError", {max: 500})`.
Keep `i18n.formatDateTime` and locale-aware number formatting. Preserve
unread/read semantics, 500-grapheme validation, route URLs, system-action
label keys/CTA routing, `markUnreadMessages` and `dir="auto"` for arbitrary
message bodies; never translate stored body text again.

Do not expose service exceptions to the UI. For unsupported intents return
`{ errorCode: "UNSUPPORTED_ACTION" }` with status 400; for exceptions thrown by
`composeMerchantMessage`, return `{ errorCode: "SEND_FAILED" }` with status
400. Map both codes at *presentation time* to `support.unsupportedAction`
and `support.sendFailed`. Do not alter the support service validation contract.

### Add translations to all 20 existing catalogues

For every new key in the separate manifest, add the exact source English
value to `en.json` and a natural translation to each other locale file.
Retain all existing keys and values, add no keys beyond the manifest, and the exact ICU
placeholders `{page}`, `{totalPages}` and `{max}`. Brand tokens remain
invariant while surrounding wording is translated. Do not leave supported
catalogues with intentionally English filler strings. Regional variants are
independent translations.

## Work Items

- [ ] Confirm the three prerequisites are Complete before task claim.
- [ ] Record dedicated launcher-resolved parent and implementation worktree,
      start-of-attempt sync and recursive submodule evidence.
- [ ] Internationalise the authenticated shell logo alt text.
- [ ] Internationalise all scoped merchant-support UI text and stable action
      error-code presentation without changing behaviour.
- [ ] Add the full revised manifest key set to all 20 locale catalogues.
- [ ] Update/add focused regressions described below.
- [ ] Run the declared validation, record results, complete the report and
      return only this task to `review`.

## Interfaces / Contracts

- Existing `createMerchantI18n`, `merchantUiContext` and Shared ICU runtime.
- New catalogue keys: architect-owned `SHOPIFY-004-i18n-key-manifest.md`.
- Merchant-support action errors: `UNSUPPORTED_ACTION`, `SEND_FAILED`; these
  are local presentation error codes, not cross-service contracts.
- No database or cross-repository contract change.

## Dependencies

- `ARCH-005-SHOPIFY-002` — Complete.
- `ARCH-006-SHOPIFY-003` — Complete.
- `ARCH-007-SHOPIFY-002` — Complete.

## Enables

- `ARCH-005-SYSTEM-TEST-001` only after this task is architect-accepted
  Complete and all other system-test implementation dependencies are Complete.

## Acceptance Criteria

- [ ] Logo alt and scoped merchant-support UI contain no specified residual
      merchant-facing English literals.
- [ ] The page heading uses `merchantNav.support`; no new navigation locale key
      or second shop/settings query is introduced.
- [ ] All 20 locale files have identical complete key sets and valid ICU
      MessageFormat, including every new manifest key.
- [ ] Translation values are natural for each locale, preserving invariant
      brands, placeholder names and regional distinction.
- [ ] Merchant-support unsupported-intent and compose-failure responses expose
      only the stated stable codes, with localised display text.
- [ ] Message bodies remain `dir="auto"` and no message content is retranslated.
- [ ] Existing tenant isolation, auth, billing, support services, unread/read
      processing and system CTA navigation remain unchanged.
- [ ] No retired route, previously localised Guest/billing component, runtime,
      unrelated repository, or `_index.md` file is modified.
- [ ] Focused tests and declared repository validations pass, with any known
      external baseline clearly identified without hiding new regressions.

## Validation

Inspect `moda-interact/package.json` before execution; these scripts exist in
the 2026-10-08 snapshot:

```bash
npx vitest run tests/unit/merchant-i18n.test.ts tests/unit/merchant-support-route.test.ts tests/unit/shopify-ui-i18n-coverage.test.ts
npm test
npm run build
npm run prisma:validate
npm run lint
npm run typecheck
git diff --check
```

Focused test obligations:
- `merchant-i18n.test.ts`: reuse the complete-key/ICU check and assert
  meaningful non-English translations of representative `common.logoAlt` and
  `support.*` copy, including ICU placeholder preservation.
- `merchant-support-route.test.ts`: retain all existing tenant/provenance,
  read/unread and CTA cases; change compose-failure expectation to `SEND_FAILED`
  and add an unsupported-intent `UNSUPPORTED_ACTION` regression.
- `shopify-ui-i18n-coverage.test.ts`: examine only the two scoped source files
  for specified keys/visible literals, ensure `dir="auto"`, and check the
  unchanged navigation/route wiring. Do not invent a generic English-text
  scanner across the repository.

Tests requiring dependencies or a live environment must be run by the actual
repository task executor; a documentation-only snapshot review does not prove
the app build or integration tests have passed.

## Implementation Notes

This is **one bounded presentation and translation capability** owned by
`moda_app`, not a cross-repository refactor. The September implementation
recipe had obsolete flat file paths, a retired example page and redundant
work for already-localised navigation/Guest/billing UI. Follow this updated
contract and the separate, corrected key manifest instead.

Use `docs/agent-vcs-ownership-policy.md`,
`docs/agent-worktree-isolation-policy.md`, and the standard `/moda-task`
launcher. Do not execute in the shared/default source checkout. For this task,
commit/push the implementation and mirrored parent task branches using the
canonical launcher-resolved dedicated worktrees. Do not merge/push main or
stage parent implementation gitlink changes.

**Stop condition:** After the Work Items, Acceptance Criteria and Validation
are finished, populate Completion Report, set `status: review`, return control
to `moda_architect`, and STOP. Do not start any system-test task.

## Completion Report

### Status

Pending

### Files Changed

None yet.

### Work Completed

None yet.

### Validation Results

Not run.

### Deviations

None.

### Assumptions

None.

### Unresolved Issues

None.

### Architectural Concerns

None.

## Architect Review

### Review Status

Pending — implementation not submitted.

### Review Notes

2026-10-08 pre-implementation definition review: re-scoped to the actual
React Router v7 source tree, removed retired/already-localised surfaces,
and corrected the accidentally inlined i18n manifest. This is a task-
definition correction, **not** implementation acceptance.

### Reviewed Files

`app/routes.ts`, `app/routes/app/route.jsx`,
`app/routes/app/merchant-support/route.jsx`,
`app/components/dashboard/MerchantNavigation.tsx`,
`app/components/dashboard/UsageEvents.tsx`,
`app/routes/app/home/route.jsx`, `app/routes/app/usage/route.jsx`,
`app/routes/app/billing/options/route.tsx`,
`app/i18n/locales/en.json`, and named task tests.

### Validation Reviewed

Source/metadata review only. Implementation tests and builds have not run.

### Architecture Conformance

Updated task definition conforms to current Shopify ownership and Shared ICU
runtime boundaries. Implementation conformance remains unverified.

### Follow-up

Execute this Ready task with the canonical `/moda-task` launcher and submit its
implementation/Completion Report for an independent architect review.
