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
status: review
priority: 55
executor: copilot
claimed_at: 2026-10-08T11:57:19Z
attempt: 2
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

- [x] Confirm the three prerequisites are Complete before task claim.
- [x] Record dedicated launcher-resolved parent and implementation worktree,
      start-of-attempt sync and recursive submodule evidence.
- [x] Internationalise the authenticated shell logo alt text.
- [x] Internationalise all scoped merchant-support UI text and stable action
      error-code presentation without changing behaviour.
- [x] Add the full revised manifest key set to all 20 locale catalogues.
- [x] Update/add focused regressions described below.
- [x] Run the declared validation, record results, complete the report and
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

- [x] Logo alt and scoped merchant-support UI contain no specified residual
      merchant-facing English literals.
- [x] The page heading uses `merchantNav.support`; no new navigation locale key
      or second shop/settings query is introduced.
- [x] All 20 locale files have identical complete key sets and valid ICU
      MessageFormat, including every new manifest key.
- [x] Translation values are natural for each locale, preserving invariant
      brands, placeholder names and regional distinction.
- [x] Merchant-support unsupported-intent and compose-failure responses expose
      only the stated stable codes, with localised display text.
- [x] Message bodies remain `dir="auto"` and no message content is retranslated.
- [x] Existing tenant isolation, auth, billing, support services, unread/read
      processing and system CTA navigation remain unchanged.
- [x] No retired route, previously localised Guest/billing component, runtime,
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

Implementation submitted for architect review. No architect acceptance decision
has been made by this agent.

### Files Changed

- `moda-interact/app/routes/app/route.jsx`
- `moda-interact/app/routes/app/merchant-support/route.jsx`
- `moda-interact/app/i18n/locales/*.json` (20 catalogues)
- `moda-interact/tests/unit/merchant-i18n.test.ts`
- `moda-interact/tests/unit/merchant-support-route.test.ts`
- `moda-interact/tests/unit/shopify-ui-i18n-coverage.test.ts`
- This task report in the parent worktree.

### Work Completed

- Localised the authenticated app-shell logo alt text and all scoped support UI
  using the existing merchant UI context and Shared ICU translator.
- Reused `merchantNav.support`; retained date/number formatting, pagination
  URLs, read/unread processing, system-action routing and `dir="auto"` message
  bodies.
- Applied `i18n.formatNumber` to support pagination page arguments and both
  values in the live grapheme counter, without changing validation or URLs.
- Replaced raw unsupported-action and compose exception messages with stable
  `UNSUPPORTED_ACTION` and `SEND_FAILED` codes; presentation maps both codes to
  the new translated messages.
- Added all 21 manifest keys to the existing 20 catalogues, preserving previous
  entries, exact English source values, ICU placeholders and regional variants.
- Added manifest, locale, route-error and scoped source-coverage regressions.

### Validation Results

Prepared execution evidence:

```text
task: ARCH-005-SHOPIFY-004
executor / attempt: copilot / 2
Attempt 1 claim: committed and pushed; 3ed4ea8a8f5b877bd408c086730b5a0af006c888
Attempt 2 claim: committed and pushed; 74431153d4bcbfe24913a2314b7d4ec6661a0ac5
implementation base: af38bf8c948c213deb857663d85ce34caaf4563a
prior implementation commit: 92cd5ca8e024146b14c4167b0df263b30f6cd013
dependency gate: passed (ARCH-005-SHOPIFY-002, ARCH-006-SHOPIFY-003,
  ARCH-007-SHOPIFY-002 all complete)
canonical workspace: /Users/kwadwoadomafriyie/project/moda-interact-workspace
parent worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-005-SHOPIFY-004
parent branch: task/ARCH-005-SHOPIFY-004
Attempt 2 parent start sync: remote task branch fast-forward not-needed;
  origin/main already-current; head 9efd1090925e30386035a2680740a2d386c3b9b2
implementation worktree: /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-005-SHOPIFY-004
implementation branch: task/ARCH-005-SHOPIFY-004
Attempt 2 implementation start sync: remote task branch fast-forward not-needed;
  origin/main already-current; head 92cd5ca8e024146b14c4167b0df263b30f6cd013
recursive submodules: sync passed; update/init passed; database at
  eee35a220b1803b7488e715e108724937ce69e8b
```

Validation:

- Focused task command after Attempt 2 correction: 3 files passed, 29 tests
  passed.
- Attempt 2 `npm run build`: passed; Prisma Client generated. Existing bundle-size and
  dependency warnings remain informational.
- `npm run prisma:validate`: passed.
- `npm run typecheck`: passed.
- `git diff --check`: passed.
- Targeted ESLint on all changed JavaScript/TypeScript source and test files:
  passed.
- `npm test`: 92 test files passed, 8 skipped; 4 files failed. Totals: 1,103
  passed, 24 failed, 33 skipped. Eighteen `billing.service.test.ts` failures
  and the `merchant-knowledge-read-model.test.ts` failure match documented
  `ARCH025-TEST-001`. Five additional failures are in unchanged
  `shared-international-context-authority.test.ts` (1) and
  `services/shop.service.test.ts` (4); no matching baseline entry was found.
- `npm run lint`: failed with 17 errors in unchanged files; none of the task's
  changed source/test files appears in the diagnostics. The focused lint above
  is clean. The workspace baseline records historical untouched-file lint debt
  under `TYPECHECK-001` (20 errors at that observation).
- A1-R2 comparison used the same Node/npm environment, Vitest 4.1.11, and the
  exact installed `node_modules` tree. A disposable detached worktree at
  `af38bf8c948c213deb857663d85ce34caaf4563a` and the submitted source both ran
  `tests/unit/shared-international-context-authority.test.ts` and
  `tests/unit/services/shop.service.test.ts`: each run had 5 failed / 15
  passed. The exact failures and causes match:
  - `does not read merchant language, timezone, or country from ShopSettings`:
    the unchanged authority test reports `app/services/shop/shop.service.ts`.
  - `creates shared and compatibility context from the primary Shopify locale`,
    `preserves a valid provider locale without requiring Moda translation coverage`,
    `does not change the shop lifecycle status during resolution`, and
    `stores null for missing or invalid optional Shopify values`: each throws
    `TypeError` reading `shopifyShopId` from undefined at
    `ShopService.resolveShopifyShop` in unchanged `shop.service.ts`.
- A1-R3 `git diff --name-status af38bf8c948c213deb857663d85ce34caaf4563a
  92cd5ca8e024146b14c4167b0df263b30f6cd013` lists the implementation's 25
  intended locale/source/test files and does not list
  `shopify.app.moda-interact.toml`. The scoped diff for that file is empty
  (`git diff --quiet` exit 0); its observed difference is not in the submitted
  implementation commit.

The first focused test invocation could not load Vitest because the isolated
worktree had no `node_modules`; `npm ci --no-audit --no-fund` installed the
locked dependencies, after which the focused command passed.

### Deviations

The first prepare attempt for Attempt 1 encountered a task/manifest glob
collision; a temporary resolver workaround was reverted and not committed.
Attempt 2's normal canonical launcher preparation succeeded without any
launcher modification, reused the canonical dedicated worktrees and durably
claimed the attempt.

### Assumptions

The five unchanged shop/international-context failures were reproduced at both
the pre-task base and submitted source with identical failure names and causes;
they are pre-existing, not task-introduced. The full suite and repository-wide
lint remain non-green due to those documented/inherited unrelated failures.

### Unresolved Issues

No unresolved implementation-scope issue remains from A1-R1 through A1-R3.
The five pre-existing shop/international-context failures and 17 unrelated
repository-wide lint errors remain visible as validation limitations.

### Architectural Concerns

None.

## Architect Review

### Review Status

**Changes Requested — Attempt 1 (2026-10-08).** The same task is Ready for
Attempt 2, with the accepted-attempt counter preserved at `attempt: 1` until
an authorized executor reclaims it. No implementation has been accepted.

### Review Notes

The submitted implementation is largely architecture-conformant:

- Reuses the existing authenticated `merchantUi` and Shared ICU runtime.
- Changes the app-shell logo alt and scoped support UI, without adding another
  settings query or changing tenant authentication, message bodies, CTA routes,
  unread processing, or the billing boundary.
- Replaces unsupported-intent/compose exceptions with local stable `errorCode`
  values `UNSUPPORTED_ACTION` and `SEND_FAILED`, translated at presentation.
- All 20 submitted locale catalogues add precisely the 21 manifest keys, retain
  their pre-existing keys/values, have equal 581-key sets, and preserve the
  exact `{page}`, `{totalPages}`, and `{max}` placeholders. English sources
  match the canonical key manifest and regional variants remain distinct.

**A1-R1 — Finish number formatting in the scoped support UI (source + test).**
The support message counter in
`moda-interact/app/routes/app/merchant-support/route.jsx` still renders the
unformatted JSX `{graphemeCount}/500`. Pagination also interpolates raw page
numbers. The requirement to preserve locale-aware numeric presentation is not
fully met. Use the existing `i18n.formatNumber` for presentation-only numeric
values in the support page, including the counter/current-page display, while
retaining the exact ICU placeholder identifiers and numeric validation bound.
Do not alter the support service, grapheme-counting logic, pagination URLs,
validation semantics or manifest values. Extend the focused scoped-coverage
regression to assert localized number presentation.

**A1-R2 — Attribute five undocumented full-suite failures (validation evidence).**
The Completion Report records 24 full-suite failures: 18 frozen billing
failures and 1 merchant-knowledge failure known under `ARCH025-TEST-001`, plus
five failures in unchanged
`tests/unit/shared-international-context-authority.test.ts` (1) and
`tests/unit/services/shop.service.test.ts` (4) without a matching baseline
identifier. Their unchanged file status is useful but is not by itself a
reproducible before/after failure-set comparison. Record the five exact failing
test names and compare pre-task implementation base
`af38bf8c948c213deb857663d85ce34caaf4563a` with the submitted commit
`92cd5ca` under comparable dependency/toolchain state; focused reruns or
deterministic dependency/behavior evidence are acceptable. Distinguish
pre-existing, environment-sensitive and task-introduced failures. If the
identifiers also fail on the pre-task base, record the evidence and do not make
unrelated source changes. If caused by this task, correct the original bounded
scope or return a cross-repository issue to the architect. Preserve the
17-errors-in-unchanged-files lint result as explicit inherited validation
information, not a passing repository-wide lint result.

**A1-R3 — Verify unrelated Shopify app-config drift (evidence only unless owned).**
The provided task ZIP's `moda-interact/shopify.app.moda-interact.toml` differs
from the earlier 2026-10-08 source snapshot (dev URL update setting and webhook
ordering), although the Completion Report does not list that file. Because the
ZIP has no Git metadata, this comparison does not prove the implementation
commit changed the config. Provide `git diff --name-status` and a scoped
`git diff` between the recorded pre-task implementation HEAD and `92cd5ca` to
show whether the change is inherited, local export state, or task-induced.
Do not silently alter Shopify configuration as part of this i18n task.

**Workflow issue, separate from A1-R1/R2/R3.** The normal launcher resolver
matches both `SHOPIFY-004-complete-merchant-ui-internationalisation.md` and
`SHOPIFY-004-i18n-key-manifest.md` via `SHOPIFY-004-*.md`. The report describes
a temporary resolver modification and its subsequent removal, plus otherwise
canonical dedicated-worktree paths and start synchronization. Fix the general
manifest-vs-task discovery defect under workflow ownership before a normal
Attempt 2 launcher preparation, without changing the Shopify implementation
scope or using another task's worktree.

### Reviewed Files

- `moda-interact/app/routes/app/route.jsx`
- `moda-interact/app/routes/app/merchant-support/route.jsx`
- `moda-interact/app/utils/merchant-i18n.js`
- `moda-interact/app/i18n/catalogues.js` and all 20 `app/i18n/locales/*.json`
- `moda-interact/tests/unit/merchant-i18n.test.ts`
- `moda-interact/tests/unit/merchant-support-route.test.ts`
- `moda-interact/tests/unit/shopify-ui-i18n-coverage.test.ts`
- Unchanged `tests/unit/shared-international-context-authority.test.ts` and
  `tests/unit/services/shop.service.test.ts`
- Parent `ARCH-005` architecture, key manifest, task Completion Report,
  launcher resolver and worktree isolation policy

### Validation Reviewed

- Independent source and JSON-diff review against the earlier uploaded
  workspace snapshot: 20 locale catalogues; exactly 21 additions each;
  identical 581-key sets; no deleted or altered pre-existing catalogue
  entries; exact required placeholder names and English manifest values.
- Submitted Completion Report: 29/29 focused tests, build, typecheck, Prisma
  validate, and changed-file lint PASS, not independently rerun here.
- Submitted full suite: 24 FAIL (19 matching documented baseline and 5 not yet
  attributed). Submitted repository-wide lint: 17 errors in unchanged files.
- ZIP snapshots contain no Git history, so exact pushed commit scope,
  branch/worktree cleanliness, and remote-push claims cannot be independently
  verified from this archive alone.

### Architecture Conformance

Core reuse, localization contracts, tenant boundaries, stable action errors,
locale manifests, and preserved support behavior conform. Acceptance is deferred
for the bounded numeric-display correction and the failure/config provenance
evidence in A1-R1 through A1-R3.

### Follow-up

The repository agent must read this complete latest Architect Review before
claiming Attempt 2. Reuse the canonical dedicated parent/implementation task
worktrees; retain the previous implementation commit where no code churn is
needed. Once the launcher discovery issue is resolved, claim the *same* task,
apply only the bounded A1-R1 source/test adjustment, resolve A1-R2 and A1-R3
with proof, rerun task-relevant validation, update the Completion Report and
return status to `review`. No `_index.md` reconciliation, system-test execution,
or dependent-task promotion is authorized by this review.
