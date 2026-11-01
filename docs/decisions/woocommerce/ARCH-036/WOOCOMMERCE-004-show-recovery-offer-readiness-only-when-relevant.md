---
id: ARCH-036-WOOCOMMERCE-004
architecture_id: ARCH-036
title: Scope coupon loading and display provider-identifiable Woo coupons
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 30
executor: null
claimed_at: null
attempt: 2
depends_on: ["ARCH-036-API-004"]
enables: []
created: 2026-10-15
updated: 2026-11-01
---

# ARCH-036-WOOCOMMERCE-004 — Mode-scoped UX with merchant-controlled coupon selection

## Architecture

- Parent: `docs/architecture/ARCH-036-shared-commerce-discount-catalogue.md`.
- Bounded follow-up to `ARCH-036-WOOCOMMERCE-003`, using the corrected settings-read contract from `ARCH-036-API-004`.
- Owner: `moda_woocommerce`, repository `moda-interact-woocommerce`; coordinator: `moda_architect`.
- API-004 is Complete. This task is materialised and has completed Developer Attempt 1; automated implementation checks pass and one manual validation scenario remains.

## Observed defect

The Woo Recovery Settings screenshot shows **Do not offer a discount** selected, followed by `WooCommerce coupon selection is not yet available.` and an unexplained **Refresh** button with a large empty coupon pane and disabled actions. This is misleading when the merchant has deliberately selected `NONE`. API-002 previously refused the independent offer-settings GET when the catalogue was ERROR; API-004 removes that coupling. The presentation must also respect the selected mode.

## Objective

Render one clear Recovery Offer configuration UI that shows only the controls and error/loading states relevant to the **draft mode**. NONE and AI modes must not imply that the merchant needs a coupon catalogue refresh. FIXED must show real multi-select controls for **all identifiable, code-usable Woo coupons returned by API-004**, without treating expiry, usage, amount or unknown discount type as Moda-made selection restrictions. WooCommerce decides redemption validity.

## Required behaviour

1. **NONE**: show the selected mode card and a concise no-discount explanation; do not render coupon list, coupon loading state, coupon error, or coupon **Refresh** button. If persisted NONE matches the draft, Save/Discard stay disabled because there is nothing to save; if the merchant changed from another saved mode, Save becomes enabled even if coupon GET is unavailable.
2. **AI_BEST_APPLICABLE**: show mode configuration and a concise explanation that this only saves preferences (no CommerceAgent/offer-execution claim). No coupon checkbox list or catalogue Refresh required for this mode; provide Save/Discard when dirty.
3. **FIXED**: render bounded search, accessible multi-checkbox list, pagination and count from the API coupon catalogue via the existing privileged WordPress proxy; show a clear `Waiting for coupon synchronisation` or `Coupon catalogue unavailable` state and a **Retry coupons** control only when list loading fails or readiness is missing. An authentically empty catalogue is distinct from a failing catalogue. Do not hide or disable an otherwise deliverable coupon merely because its Woo type is unknown, amount zero, expired, exhausted or restricted.
4. **State isolation**: load saved offer preferences using API-004 independently of the coupon-list query. A coupon-list `503` must not replace the saved NONE/AI mode with an unavailable state or disable changing mode. Do not show a generic `WooCommerce coupon selection is not yet available` banner under NONE.
5. **Manual Save**: preserve staged mode/checkbox edits and full selected-ID set across filters/pages; Save only on explicit action with duplicate-click prevention. FIXED with zero checked coupon rows has inline validation. Do not preselect a coupon without merchant action. After a failed Save preserve draft and report the error; Cancel restores persisted settings. A non-current list should block choosing NEW FIXED items, not reintroduce business eligibility validation in API PUT. Do not lose saved selected IDs just because coupon metadata or catalogue status changes.
6. **Preserve UX**: keep the existing two-stage WordPress navigation `WooCommerce > Moda Interact` entry and active `Moda Interact > Recovery settings` submenu; keep Recovery start, No-response follow-up, Store Category and existing recovery-policy controls unchanged. Do not create a second Recovery Offer section.
7. **Transparent status, no merchant veto**: optionally display Woo expiry/usage/type metadata as **information**, never as a disabled checkbox or an invented claim that the provider coupon is invalid. Clearly explain that WooCommerce validates coupon redemption. Treat a coupon missing a safely deliverable code as a technical sending problem, not an unsupported discount type; never truncate a provider code to fit UI.
8. **Localise** all added/changed copy through WordPress native i18n in all 20 supported locales. Update POT/PO/compiled release assets and strict message-count tests to actual extracted source, without bypassing the 20-locale gate.

## ASCII page states

```text
WordPress Admin > WooCommerce > Moda Interact
  > Moda Interact > Recovery settings
+----------------------------------------------------------------------+
| 1  Recovery offer                                                    |
|                                                                      |
| (o) No discount    ( ) Specific discount    ( ) AI-selected          |
|                                                                      |
| No discount will be offered.                                         |
|                                    No changes to save                |
+----------------------------------------------------------------------+

When FIXED is selected and current:
+----------------------------------------------------------------------+
| ( ) No discount    (o) Specific discount    ( ) AI-selected          |
| Search coupons [____________________] [Search]                       |
| [x] SAVE10          10%                 (merchant selected)          |
| [ ] SAVE20          custom Woo type     (not selected)             |
| [Previous]              Page 1 of N           [Next]                 |
| 1 selected                        [Discard] [Save recovery offer]     |
+----------------------------------------------------------------------+

When FIXED is selected but catalogue unavailable:
+----------------------------------------------------------------------+
| ( ) No discount    (o) Specific discount    ( ) AI-selected          |
| Coupons are not ready. Synchronisation is pending or unavailable.    |
| [Retry coupons]                                                       |
| You can still select No discount or AI-selected mode.                |
+----------------------------------------------------------------------+
```

## Scope and exclusions

- Only WooCommerce plugin React controller/component/presentation, privileged WordPress proxy if required for error differentiation, styling, native translation assets and focused tests.
- No changes to Background, API, Prisma, Shopify, CommerceAgent, billing, coupon redemption or outbound recovery; no `_index.md` changes.
- Do not add duplicate menu entries or move the canonical two-stage navigation.

## Work Items

- [x] Separate saved offer preferences from coupon catalogue status; render NONE, AI and FIXED states independently.
- [x] Add bounded coupon search/pagination, persistent staged selection, manual save/discard, duplicate-save protection, scoped readiness and retry behavior.
- [x] Validate the authenticated WordPress proxy and strict API payload contracts, including long coupon codes and provider-identifiable custom coupon types.
- [x] Update native translation sources and all 20 supported locale release assets.
- [x] Pass focused controller/component, PHP proxy, localization, lint, build and package checks listed below.
- [x] Complete the human-run LocalWP FIXED + catalogue ERROR walkthrough at desktop and narrow widths; retain evidence and verify both menu stages during that run.

## Acceptance criteria

- [x] When **NONE** is saved, there is no coupon Refresh button, coupon-unavailable warning, empty placeholder box, or demand for catalogue readiness. Controller/view tests pass; the installed current build was observed in saved NONE with no coupon controls and disabled save/discard.
- [x] Changing NONE -> AI and back enables/disables Save based only on real edits even when coupon catalogue GET fails. Controller tests cover isolated catalogue failure; the AI preference-only state was also observed in LocalWP.
- [x] FIXED with CURRENT catalogue presents provider-identified, code-usable Woo rows including unchecked rows, regardless of type/amount/expiry/usage, with persistent selection across page/search and manual Save/Cancel. Controller and view tests cover these rows and selection; LocalWP displayed five current coupons.
- [x] FIXED with non-current catalogue shows one actionable inline readiness message and a scoped Retry control, never an unexplained global Refresh button. Automated view/controller tests cover NOT_READY and retry; the Attempt 2 LocalWP ERROR-state walkthrough passed and evidence is retained below.
- [x] Automated tests cover empty catalogue, catalogue failures, permission denial, 409 conflict, 503 mapping, duplicate save prevention, selection reset/discard, unknown types, zero/expired/exhausted metadata, and long codes; see focused JS and PHP tests.
- [x] 20-locale support and existing recovery-policy/Store Category controls pass automated checks. LocalWP showed both WordPress menu stages and the recovery form at desktop and narrow widths without observed overflow.

## Required validation

- [x] React controller/component tests cover NONE/AI/FIXED with current/unavailable catalogues, paging, selection, discard, no autosave, failed saves, retry, unusual coupon metadata and long-code rendering.
- [x] PHP WordPress proxy tests cover authenticated calls, authorization, rejected caller identity/revision/provider fields, and distinct unavailable/error status mapping; no browser-to-hosted credentials are sent.
- [x] `npm run i18n:verify:20`, `npm run test:js`, `npm run test:php`, `npm run lint:js`, `npm run lint:css`, `npm run lint:php`, `npm run plugin-zip`, and `git diff --check` pass. `plugin-zip` also ran the production build and strict locale gate.
- [x] Manual LocalWP screenshot/interaction evidence is complete for FIXED + catalogue ERROR. On the disposable Colima site, the initial catalogue request returned catalogue_not_current, the page showed exactly one inline status and a scoped Retry coupons button, and Retry loaded SAVE10 and removed the Retry button. Both WooCommerce > Moda Interact and Moda Interact > Recovery settings menu stages were verified. Desktop 1440 px and narrow 390 px layouts had no horizontal overflow. Screenshots: [desktop](evidence/WOOCOMMERCE-004-localwp-fixed-error-desktop.png), [narrow](evidence/WOOCOMMERCE-004-localwp-fixed-error-narrow.png).

## Stop condition

After bounded validated work, submit the developer Completion Report and mark this task `review`; return to `moda_architect`. No dependent-task execution, incidental refactors or `_index.md` edits.

## Completion Report

### Status

Ready for architect review — Developer Attempt 2. The outstanding manual
validation is complete. Developer self-review passed; architect acceptance and
the explicit developer completion decision remain pending.

### Files Changed

- No application source changed during Attempt 2. The implementation branch
  already contains the completed Attempt 1 source. It was fast-forwarded to
  current origin/main at d6a7709 and pushed to
  task/ARCH-036-WOOCOMMERCE-004.
- Added the two LocalWP evidence screenshots in this task's evidence folder.
- Updated this task record with the walkthrough results and review lifecycle.

### Work Completed

- Completed the required LocalWP FIXED + catalogue ERROR walkthrough on the
  disposable Colima environment.
- Confirmed the FIXED draft remains selected while the catalogue is not current,
  one inline readiness message appears, and the Retry coupons action is scoped
  to the coupon panel.
- Confirmed Retry makes a second catalogue request, then displays SAVE10 and
  removes the retry control after the fixture recovers.
- Verified WooCommerce > Moda Interact and Moda Interact > Recovery settings
  through the rendered WordPress menu hierarchy.
- Captured desktop and narrow screenshots. No implementation source changes or
  dependency changes were made in this attempt.

### Validation Results

- Attempt 1 automated validation remains applicable because no implementation
  source changed: 234 JavaScript unit tests and 37 integration/i18n tests,
  105 PHP tests with 643 assertions, JS/CSS/PHP lint, strict 20-locale checks,
  plugin ZIP, and diff checks passed on the published implementation.
- Attempt 2 production build passed using Node 24.19.0 and the canonical
  WooCommerce dependency installation. Strict i18n verification passed with
  568 source messages, 19/19 packs and 38 generated assets. Webpack emitted
  three bundle-size advisory warnings.
- Manual LocalWP walkthrough passed. The fixture returned 503
  catalogue_not_current for the first catalogue request; the page rendered one
  role=status message and Retry coupons. At both 1440 px desktop and 390 px
  narrow widths, the panel remained visible and document width matched the
  viewport. After Retry, the fixture returned SAVE10 and the Retry control was
  removed.
- The WordPress navigation DOM showed Moda Interact under WooCommerce and
  Recovery settings under Moda Interact.
- Evidence: [desktop screenshot](evidence/WOOCOMMERCE-004-localwp-fixed-error-desktop.png)
  and [narrow screenshot](evidence/WOOCOMMERCE-004-localwp-fixed-error-narrow.png).
- The LocalWP fixture only implemented the installation probe and offer/catalogue
  endpoints; unrelated panels reported unavailable from the stub. The task site
  was stopped after validation, and the unrelated ARCH-046 site was left running.
- The task-specific implementation source is clean; the implementation task
  branch tracks its published remote at d6a7709.

### Deviations

No scope deviation. Attempt 2 completed the manual validation left open by
Attempt 1 without changing application source.

### Assumptions

Hosted API deployment and end-to-end media behavior remain outside this task and
are covered by their existing downstream architecture gates.

### Unresolved Issues

None for this task's required implementation or validation.

### Architectural Concerns

None. The prior attempt's source changes remain within the task's WooCommerce
ownership boundary.

## Developer Self-Review - Passed — Attempt 2

The required LocalWP FIXED + catalogue ERROR scenario now passes with Retry
recovery at desktop and narrow widths. Both menu levels were verified and
screenshots are retained. The implementation task branch is clean and published.
Lifecycle is transitioned to review; executor and claimed_at are cleared and
attempt 2 is preserved. Because completion_mode is developer, explicit
developer completion remains pending after architect acceptance. No downstream
tasks declare this task as a dependency, so no dependency status changed.

## Developer Claim — Attempt 1

- Claimed by developer at `2026-10-16T00:55:02+01:00`; `status: in_progress`, `executor: developer`, `attempt: 1`.
- Dependency `ARCH-036-API-004` was verified Complete through its canonical launcher route before claim.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-036-WOOCOMMERCE-004`, branch `task/ARCH-036-WOOCOMMERCE-004`, created clean at `a09a22db0bba1d46f47de9186040ca2c115434b1` from current `origin/main`. No remote task branch existed before claim.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-036-WOOCOMMERCE-004`, repository `moda-interact-woocommerce`, branch `task/ARCH-036-WOOCOMMERCE-004`, created clean at `ba0b6be7f1150e8e3f6f8228eebf155e17adda95` from current `origin/main`. No remote task branch existed before claim.
- Start-of-attempt synchronization: fetched `origin --prune` in both canonical worktrees; each task branch starts at current `origin/main`, so no merge was required. Shared/default checkouts were not switched or used as substitutes. No other task worktree was reused.
- No implementation files were changed by claim preparation. The developer now owns implementation in the canonical WooCommerce worktree. No branch was merged to `main`.

## Architect Review

### Review Status

**Developer Self-Review - Changes Requested (manual validation pending).** The implementation and automated checks are verified, but the required LocalWP FIXED + catalogue ERROR scenario was intentionally left for human testing. The task remains `ready`; `executor` and `claimed_at` are cleared; Attempt 1 is unchanged. Do not mark Complete until the manual validation checkbox is satisfied.

### Review Evidence

- Implementation commits: `be153a9` and `15d78a8e229b62a1dd864399816fd7815e97133f`, published on `origin/task/ARCH-036-WOOCOMMERCE-004`.
- Parent task branch synchronization: `dc14d08d08f16ae8c2bd27a5b40d49a1812035dc` merged the latest `origin/main` task-definition additions before this report update. No implementation branch was merged to `main`.
- Implementation worktree was clean at review; only the canonical task definition is changed by this report update.
- No material assistance from `moda_woocommerce` or another agent was used in this developer attempt.

### Required Follow-up

Have a human run and record the outstanding LocalWP FIXED + catalogue ERROR check at desktop and narrow widths, including the inline readiness message, Retry behavior and both WordPress menu stages. Then reconcile the task again; keep this attempt number unless a new implementation claim is actually started.


## Developer Override - Reopened

The task metadata previously marked this task complete at Attempt 1, but its
Completion Report and review record state that the required LocalWP FIXED +
catalogue ERROR validation remains outstanding. At the developer's request, the
task is reopened for implementation takeover and completion of that required
scenario. Attempt 1 history and all prior review evidence are preserved.

Lifecycle transition: status ready; executor and claimed_at cleared; attempt 1
preserved. Reopening did not claim a new attempt.

Dependency frontier audit: no task definition declares ARCH-036-WOOCOMMERCE-004
in depends_on, and this task has no enables entries. No downstream task status
required regression.


## Developer Claim — Attempt 2

- Reopened on the developer's request after Attempt 1's required LocalWP
  FIXED + catalogue ERROR walkthrough remained outstanding; Attempt 1 history
  and its review decision were preserved.
- Developer claimed Attempt 2 at 2026-11-01T15:12:56Z. Parent task branch:
  task/ARCH-036-WOOCOMMERCE-004; durable claim commit 3c00de988.
- Implementation worktree:
  /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-036-WOOCOMMERCE-004.
  At claim it was on the current origin/main snapshot; the previous
  implementation task commit 15d78a8 was already an ancestor of main.
- No implementation source changed during Attempt 2. After validation, the
  task branch was fast-forwarded to current origin/main d6a7709 and published.
- Dependency ARCH-036-API-004 remains Complete. No tasks declare this task in
  depends_on, so the downstream frontier required no status changes.
