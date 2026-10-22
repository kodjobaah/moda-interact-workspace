---
id: ARCH-035-WOOCOMMERCE-018
architecture_id: ARCH-035
title: Connect WooCommerce Usage History screen to authoritative usage API
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: in_progress
priority: 40
executor: developer
claimed_at: 2026-10-22T22:10:19Z
attempt: 2
depends_on:
  - ARCH-035-API-022
  - ARCH-035-WOOCOMMERCE-006
enables:
  - ARCH-035-SYSTEM-TEST-007
created: 2026-10-22
updated: 2026-10-22
---
# ARCH-035-WOOCOMMERCE-018: Connect WooCommerce Usage History screen to authoritative usage API

## Architecture

- Parent: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`.
- API contract: `ARCH-035-API-022`; UI predecessor `ARCH-035-WOOCOMMERCE-006` remains accepted Complete.

## Objective

Replace the Usage History UI's hard-coded unavailable transport with the approved authenticated Woo API and show real current/past events and billing-period selections.

## Context

`src/usage-history/usage-history-client.js` currently returns `{available:false}`. The UI/controller/toolbar/results already exist and must be reused; Billing purchase history is a separate feature and must not be altered.

## Scope

- Add WordPress `GET /wp-json/moda-interact/v1/merchant/usage-history` privileged proxy and allowlisted ModaApiClient route to hosted `GET /v1/merchant/usage-history`.
- Replace only `src/usage-history/usage-history-client.js` transport and minimal controller/hook glue needed for API-022, retaining existing state and presentation behavior.
- Extend focused WP REST/client tests, controller tests, translations if necessary, build/ZIP evidence.
- **Architecturally approved 22 October 2026:** v2 `Charged against` column and controlled server-side hosted-version negotiation; legacy v1 remains supported. No new public browser query parameter.

## Out of Scope

- New usage events, billing periods, fee calculations, purchases/refunds, PHP direct database access, hosted API/database code, cross-Shop analytics, new dashboard design, `_index.md` changes.

## Requirements

1. WordPress `manage_woocommerce` and `X-WP-Nonce` gate all reads. Resolve Woo installation credentials server-side; enforce canonical site identity and post-fetch credential rotation/disconnect fence. The browser must not receive hosted API credentials or specify `shopId`.
2. Forward only the documented browser filters `view`, `periodId`, `kind`, `page`, `pageSize`, `periodCursor` within API-022 bounds. **Architecturally approved:** the privileged PHP client may add only the separate optional hosted `responseVersion=2` negotiation; the browser may not supply or control `responseVersion`. Preserve `_locale=user` handling only when appropriate for WordPress; never forward arbitrary paths, headers, tenant identifiers or provider IDs.
3. Strictly validate both approved API-022 response shapes: unchanged `schemaVersion:1` or explicitly requested `schemaVersion:2` with mandatory per-event `chargedAgainst`. Map to existing `usageEvents`, `usagePagination` and `periodPage` view model and add the Charge source/Charged against column; v1 attribution is **Not available**, not **Unattributed**. Valid real empty results show **No recorded usage**, while unavailable/401/403/invalid period/cursor/5xx have distinct states, without synthetic records or zero totals. Legacy fallback is limited to one `HTTP 400 invalid_request` compatibility case and must not conceal authentication, period, cursor, integrity or server failures.
4. Honor existing Current/Past tabs, period next/previous cursor, 10/25/50/100 rows per page, event kind filter, page reset rules, server-driven total/totalQuantity and same-Shop recovery links. Use existing WordPress locale-aware formatting and no content escaping errors.
5. On refresh/disconnect/unmount/identity change, abort or discard stale responses. Invalid period/cursor uses existing clear-selection affordance; 401 prompts reconnect, 403 disables access; no infinite retry/loop or duplicate HTTP requests from one control event.
6. Keep `Billing > Purchase History` and all existing WordPress navigation unchanged except for minimal Usage History integration changes. 20 locales must still compile.

## Work Items

- [x] Check API-022 accepted OpenAPI and current Woo `ModaApiClient`/REST patterns.
- [x] Add bounded privileged GET proxy, security/response handling and live client.
- [x] Wire existing Usage History controller/hook and verify all filter/page/period transitions.
- [x] Add tests for 401/403/409/5xx/disconnect, invalid cursors, no usage, Free lifetime and paid periods.
- [x] Run repository validation and document LocalWP manual live checks.

## Interfaces / Contracts

- WP: `GET moda-interact/v1/merchant/usage-history`.
- Hosted: `GET /v1/merchant/usage-history` (owner API-022); approved optional server-only `responseVersion=2` produces `schemaVersion:2` with the mandatory `chargedAgainst` enum. Omitted/`1` retains exact v1 compatibility.
- No new shared queue schema; UI uses the **architecturally approved v1/v2 API-022 contract** validated server-side and in Woo client. The WordPress browser REST boundary does not expose `responseVersion`.

## Dependencies

- `ARCH-035-API-022` (architect-accepted Complete).
- `ARCH-035-WOOCOMMERCE-006` (existing completed UI).

## Enables

- `ARCH-035-SYSTEM-TEST-007`.

## Acceptance Criteria

- [x] Real Woo usage populates Current/Past UI, filters, period cursors, recovery links, totals and pagination without fabricated data.
- [x] Free lifetime and paid entitlement windows present correctly; purchased credit history remains separate.
- [x] Disconnect/rotation, nonce/capability denial, tampered query/cursor and hosted failure cannot leak other-Shop usage or show stale results.
- [x] Accessibility, 20 native WP Admin languages and production plugin build remain valid.
- [ ] **Next review after v2 scope approval:** verify server-only negotiation and strict v1/v2/error-path tests against the amended API-022 contract, plus recorded local deployment/rollback evidence. Do not mark this complete solely because the scope is now approved.

## Validation

- [x] Relevant `npm run test:js`, `npm run test:i18n`, `npm run i18n:verify:20`, `npm run test:php`, `npm run build`, `npm run plugin-zip` (actual declared scripts), focused PHP validation and JS controller tests.
- [x] User/developer LocalWP real authenticated workflow with owned current/past events; no invented production success evidence.
- [ ] `git diff --check`, canonical worktree evidence and Completion Report.

## Stop Condition

Set `status: review` and return to `moda_architect`, then STOP. Do not implement the system test under this task.

## Implementation Notes

Reuse existing `UsageHistoryController` and view, and keep PHP proxy/request validation, JS transport and view-model mapping separately testable. No new generic logging implementation.

## Completion Report

### Status

In Progress — Attempt 2 claimed by developer at 2026-10-22T22:10:19Z. Attempt 1 review history is preserved below.

### Files Changed

WooCommerce implementation (task-scope changes across the incremental patch revisions):

- PHP host/API boundary: `composer.json`, `includes/Api/ModaApiClient.php`, `includes/Api/UsageHistoryResponseValidator.php`, `includes/Rest/UsageHistoryController.php`, `includes/Runtime.php`.
- Browser UI/state: `src/usage-history/usage-history-client.js`, `src/usage-history/usage-history-controller.js`, `src/usage-history/usage-history-screen.js`, `src/usage-history/usage-history-toolbar.js`, `src/usage-history/usage-history-results.js`.
- Billing navigation/layout: `src/billing-screen.js`, `src/billing/hero.js`, `src/styles/_billing-hub.scss`, `src/styles/_usage-history.scss`.
- Regression tests: `tests/UsageHistoryControllerTest.php`, `tests/bootstrap.php`, `tests/js/usage-history-client.test.js`, `tests/js/usage-history-controller.test.js`, `tests/js/usage-history-screen.test.js`, `tests/js/billing-screen.test.js`, plus focused `tests/i18n/locale-batch-010.test.mjs` through `locale-batch-013.test.mjs` and `tests/i18n/release-assets.test.mjs`, `tests/i18n/release-source.test.mjs`.
- Localisation sources: `languages/moda-interact.pot` and 19 translated `languages/moda-interact-*.po` catalogues (English is the source locale). Production-compiled language assets are generated by the packaging workflow.

This is a task-scope summary of files touched during the supplied incremental patches, not a claim to have verified Git's final staged diff. The authoritative final file list and commits must be reconciled from the implementation task branch.

### Work Completed

1. Added authenticated same-origin WordPress `GET /moda-interact/v1/merchant/usage-history` and an allowlisted hosted API proxy. Enforced `manage_woocommerce`, `X-WP-Nonce`, bounded filter/query validation, server-only Woo installation credentials, canonical URL/tenant identity, and post-read disconnect/credential-rotation checks.
2. Replaced the hard-coded unavailable Usage History transport with real hosted API reads, preserving the existing modular controller, hook, toolbar and results components. Added strict PHP and JavaScript validation, fail-closed error states, abort/stale-response fencing, current/past view switching, filters, signed period cursor handling and event pagination.
3. Kept Current usage free of a period dropdown: lifetime usage for a Free subscription, actual period date range for paid current usage. Kept the selector for Past paid usage and synchronized the selector with the API's automatically chosen period. Moved the Billing page's Usage History link beside Refresh billing, leaving purchased credit history separate.
4. Adopted hosted API-022 response v2 via server-side opt-in, retaining controlled v1 compatibility for older API deployments. Added the **Charged against** column for Lifetime Free credits, Included plan allowance, Purchased top-up, Promotional credits, Not applicable and Unattributed. Legacy v1 without attribution displays **Not available** rather than mislabeling it Unattributed.
5. Added PHP/JS regression coverage for authorization, malformed requests/responses, disconnects, cursor/period failures, genuine empty responses, Free lifetime usage, paid period selection, stale requests, credit attribution and legacy v1. Updated translations and verified the production plugin packaging.

### Validation Results

**Automated — developer terminal log `typescript(20261022-194546)` (22 October 2026):**

| Command | Result |
| --- | --- |
| `npm run test:js` | PASS — 55/55 JavaScript test files, 411/411 Vitest tests; Node integration/i18n runner 52/52. |
| `npm run test:i18n` | PASS — 28/28. |
| `npm run i18n:verify:20` | PASS — 470 source messages; 19/19 translation packs + English source locale (20/20 supported languages); 38 compiled assets. |
| `npm run build` | PASS — production Webpack build; existing bundle-size/performance warnings are non-fatal. |
| `npm run install:php` then `npm run test:php` | PASS — PHPUnit 148 tests, 1,118 assertions. |
| `npm run plugin-zip` | PASS — `moda-interact.zip`, version 0.1.0, 124 entries, SHA-256 `2c5f4df1ffad41d34e669ec9f7c403985f29508ceb369fd3ebbd30adeb71e42a`. |

**LocalWP/WooCommerce — developer's manual screenshots and database evidence (22 October 2026):**

- Installed locally built WooCommerce plugin on the WordPress/LocalWP test site and accessed Billing → Usage History as an authenticated shop administrator. Earlier HTTP 503 was resolved; live WordPress Usage History reads subsequently returned HTTP 200 with a valid hosted projection.
- Current Free usage displayed **4 records / quantity 4**, without a billing-period selector, with the **Lifetime usage** heading and the **Lifetime Free credits** charge attribution on all four rows.
- Past paid usage displayed three synthetic, closed historical paid periods with **16/11/7 events** and **19/13/8 total quantities**, respectively. The selector showed the active period; the 16-event period was manually paginated between **1–10/16** and **11–16/16**. The **Charged against** column and same-shop recovery links were visibly rendered.
- Following the paid-attribution seeder correction, SQL against disposable `moda_interact_postgres_test` verified committed reservation/counter linkage for **16/16**, **11/11**, **7/7** historical events (34/34 total; historical quantities 19, 13 and 8). This is database-side attribution evidence. A new screenshot/response showing **Included plan allowance** after the final reseed has not been supplied; that visual display outcome must not be claimed as already observed.
- LocalWP used an actual authenticated WordPress/hosted-API request path with **synthetic** usage and historical periods. It does not prove a real paid merchant renewal, purchase/refund, Meta delivery, or production runtime.

**Git / worktree evidence (reconciled 22 October 2026):**

- Canonical workspace: `/Users/kwadwoadomafriyie/project/moda-interact-workspace`.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-WOOCOMMERCE-018`, branch `task/ARCH-035-WOOCOMMERCE-018`, HEAD `1e3b062a7`; clean and equal to `origin/task/ARCH-035-WOOCOMMERCE-018`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-WOOCOMMERCE-018`, branch `task/ARCH-035-WOOCOMMERCE-018`, HEAD `23f1db55`; clean and equal to `origin/task/ARCH-035-WOOCOMMERCE-018`.
- Both task branches contain current `origin/main`; no shared/default checkout or another task worktree was used. The implementation branch contains two task commits (`e10165a`, `23f1db5`); the parent branch contains the takeover, claim and report commits.
- Implementation `git diff --check origin/main...HEAD` passed. `git submodule status --recursive` returned no entries.
- The implementation worktree and parent task worktree had no uncommitted changes at reconciliation. The report's automated and LocalWP evidence above remains developer-provided evidence; this review did not rerun the full repository test matrix.

### Deviations

- Minor Usage History navigation/UX corrections were added while integrating the live API: the Billing header link, Current-versus-Past period selector behavior and **Charged against** presentation. They are confined to the Usage History/Billing entry point; purchased credit purchase/refund history is unchanged.
- The hosted API-022 v2 charge-attribution and reservation-linkage work, and the Admin fixture corrections, were implemented and validated separately in their owning repositories. They are not represented as changes to this WooCommerce implementation branch.

### Assumptions

- Hosted API-022 implements the opt-in `responseVersion=2` projection; the Woo client also accepts the exact legacy v1 response when permitted by the PHP proxy's controlled fallback. WordPress admin authentication/installation credentials and merchant-site identity remain server-managed.
- The Free-now/previously-paid usage dataset is intentionally synthetic, uses the existing Free subscription and creates historical PAID_METERED period snapshots. It is limited to a disposable development database and must not be interpreted as historical live subscription billing.

### Unresolved Issues

- **Blocking contract mismatch:** `includes/Api/ModaApiClient.php` requests undocumented `responseVersion=2`, retries as v1 when the hosted API rejects it, and `UsageHistoryResponseValidator` accepts schema v2. The accepted API-022 contract at `docs/decisions/api/ARCH-035/API-022-expose-woo-usage-history.md` specifies only the six documented filters and `schemaVersion:1`. Reconcile the API contract through its owner and obtain an explicit architecture/task scope amendment before relying on v2; otherwise conform the Woo proxy/client/validator to v1. Keep version negotiation private from the browser, but do not bypass the documented hosted contract.
- A fresh post-reseed LocalWP screenshot or v2 API response showing **Included plan allowance** for the 34 paid historical rows has not been supplied; the current report has SQL linkage evidence only.
- A currently paid merchant with an actual OPEN billing period was not demonstrated in LocalWP; paid-current behavior is supported by component/contract tests and remains a suitable integrated system-test follow-up.
- The webpack asset-size warnings are non-fatal and are not a newly established blocker for this task.

### Architectural Concerns

- Usage data and charge allocations remain authoritative in the hosted API/database. WooCommerce performs no direct database read and does not infer charge allocation from plan labels or billing dates. v1/v2 rollout compatibility and fail-closed tenant boundaries are preserved.
- The 34/34 reservation evidence belongs to separate Admin fixture/API work. Keep the dependent `ARCH-035-SYSTEM-TEST-007` terminal and manually gated until this task has a durable Accepted review and the developer explicitly completes it.

### Physical Worktree / Publication Evidence (developer to complete from launcher and Git)

```text
Canonical workspace root:             [paste launcher workspace_root]
Parent task worktree (absolute):       [paste launcher-resolved path]
Parent branch:                         task/ARCH-035-WOOCOMMERCE-018
Implementation worktree (absolute):    [confirm task-specific path in Git]
Implementation branch:                 task/ARCH-035-WOOCOMMERCE-018
Shared/default checkouts used:         [confirm no]
Another task worktree reused:          [confirm no]
Parent remote task fast-forward:       [yes or not-needed + evidence]
Parent origin/main incorporated:       [yes or already-current + evidence]
Implementation remote fast-forward:    [yes or not-needed + evidence]
Implementation origin/main included:   [yes or already-current + evidence]
Implementation submodules prepared:    [git submodule status --recursive evidence]
Implementation task commits / push:    [SHA(s), origin task branch]
Parent Completion Report commit/push:  [SHA, origin task branch]
Final git diff --check / status:       [command/result]
```

**Submission / lifecycle:** The developer should reconcile these records with `/moda_developer_update ARCH-035-WOOCOMMERCE-018`, which owns the authorized review and may move `in_progress` to `review`. Since `completion_mode: developer`, a passing review still requires the later explicit `/moda_developer_update ARCH-035-WOOCOMMERCE-018 complete`. Do not edit `## Architect Review`, declare acceptance, merge branches, or modify any `docs/decisions/**/_index.md` as part of this report.

## Developer Execution Ownership Amendment

The developer invoked `/moda_developer_create ARCH-035-WOOCOMMERCE-018` for this ready agent-owned task, explicitly taking over implementation execution. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_woocommerce`, repository ownership, task scope and dependencies are unchanged.

- Previous execution mode: `agent`
- Previous completion mode: `automatic`
- New execution mode: `developer`
- New completion mode: `developer`
- Amendment date: 2026-10-22

## Architect Review

### Review Status

Pending.

### Review Notes

Historical initial-task placeholder: not reviewed at initial definition. **Architectural scope amendment on 22 October 2026 approves optional v2 negotiation and charge-attribution presentation**, documented below. This does not accept the implementation or override the developer self-review without a new authorised task review.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

To be assessed from implementation and test evidence.

### Follow-up

Architect acceptance required before enabling dependants.

## Developer Self-Review - Changes Requested

### Review Outcome

Changes Requested. Attempt 1 is not ready for architect acceptance because the Woo implementation's API v2 negotiation and schema acceptance exceed the accepted API-022 contract and conflict with this task's requirement to forward only documented filters.

### Required Corrections

1. Remove `responseVersion=2` negotiation/fallback behavior and v2-only response handling from the Woo path, and conform to the accepted API-022 `schemaVersion:1` contract and six documented query filters; OR provide an architect-approved scope amendment backed by an updated, accepted API-022 contract before retaining v2 behavior.
2. Add or update focused tests to prove the hosted request contains no undocumented query parameter, accepts only the contract-authorized schema, and preserves the existing invalid-period/cursor and fail-closed behavior.
3. Rerun the focused Woo client/PHP tests, relevant repository validation from the task's Validation section, and `git diff --check`; update the Completion Report with the resulting evidence and preserve the LocalWP limitations recorded above.

### Evidence Reviewed

- Accepted API-022 contract requires `schemaVersion:1` and enumerates the six supported query filters.
- `includes/Api/ModaApiClient.php` adds `responseVersion=2` and retries as v1 on HTTP 400 `invalid_request`.
- `includes/Api/UsageHistoryResponseValidator.php` accepts schema versions 1 and 2.
- Canonical implementation and parent worktrees are clean; implementation HEAD `23f1db55` equals its remote task ref, parent HEAD `1e3b062a7` equals its remote task ref, and both task branches contain `origin/main`.
- Implementation `git diff --check origin/main...HEAD` passed; recursive submodule status had no entries.

### Lifecycle

Attempt 1 remains the reviewed attempt. Transitioned to `ready` with `executor: null` and `claimed_at: null`; no Attempt 2 was claimed. The next `/moda_developer_create ARCH-035-WOOCOMMERCE-018` invocation may claim Attempt 2 after synchronization and dependency gates.

---

## Architect Scope Amendment — 22 October 2026 (APPROVED)

**Decision:** `moda_architect` **architecturally approves** the bounded API v2 consumer behavior already implemented for `ARCH-035-WOOCOMMERCE-018`. The canonical `ARCH-035-API-022` definition and the ARCH-035 parent architecture now document an optional `responseVersion=2` hosted contract. **No `ARCH-035-API-023` task is required.** The original v1 remains the default and is unchanged.

**Effect on the preceding Changes Requested review:** The first correction's explicitly permitted *architect-approved amendment* path is now selected. **Do not remove v2 negotiation solely because it was previously undocumented.** The v1-only assertion in correction 2 is superseded by version-aware tests. Preserve the other security, failure-handling, LocalWP evidence and validation requirements. The original review remains accurate as historical evidence and has not itself been marked Accepted.

**Approved behavior / acceptance evidence for the next developer claim:**

1. Only the **privileged PHP** API client adds the hosted query `responseVersion=2`; the nonce/capability-checked browser REST endpoint still forwards only the original six user filters and never accepts browser-controlled `responseVersion`, tenant/shop IDs or arbitrary query keys. The request is Shop/installation authenticated and maintains the identity/credential-rotation fence.
2. The plugin strictly validates `schemaVersion:2` with exactly one additional mandatory per-event `chargedAgainst` value: `LIFETIME_FREE_CREDITS`, `INCLUDED_PLAN_ALLOWANCE`, `PURCHASED_TOP_UP`, `PROMOTIONAL_CREDITS`, `NOT_APPLICABLE`, `UNATTRIBUTED`. Existing `schemaVersion:1` responses retain their exact original event shape, mapped to the presentation-only label **Not available**; v2 `UNATTRIBUTED` is a distinct confirmed lack of attribution evidence. No UI-side inference from current plan, event source type or billing-period dates.
3. At most one bounded **HTTP 400 `invalid_request`** fallback to a strict v1 request is allowed when speaking to a known older hosted API. Authentication/authorization failures, invalid/tampered period or cursor, server errors, unexpected/malformed responses and changed installation identity do not trigger a v1 retry or conceal a failure. No additional browser exposure, source-system changes, payment or usage writes are permitted.
4. Next claim/review should verify v1/v2 PHP and JavaScript contract tests, allowed query parameters, Free lifetime and paid current/past presentation, row attribution labels, negative paths, 20 supported locales, production ZIP, shared structured logging and relevant LocalWP evidence. The API v2 implementation and its validation must be reconciled against the now-approved API-022 contract; historical API-022 v1 task acceptance alone does not certify later code. Record the previous LocalWP limitations honestly, including the absence of a demonstrated currently paid OPEN period and the post-reseed attribution screenshot unless newly supplied.

**Lifecycle:** `status: ready`, `attempt: 1`, `executor: null`, `claimed_at: null` are **preserved**. This amendment resolves the *contract-scope blocker* but is **not** an implementation acceptance, an Attempt 2 claim, a Completion Report rewrite or a developer completion decision. Resume through `/moda_developer_create ARCH-035-WOOCOMMERCE-018` when its reviewed dependency evidence is reconciled; preserve all historical reviews, then submit the new evidence for authorised developer/architect review. `ARCH-035-SYSTEM-TEST-007` remains terminal and Pending.
