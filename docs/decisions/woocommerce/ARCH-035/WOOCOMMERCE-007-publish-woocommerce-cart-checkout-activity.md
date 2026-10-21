---
id: ARCH-035-WOOCOMMERCE-007
architecture_id: ARCH-035
title: Capture Woo checkout snapshots
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 56
executor: null
claimed_at: null
attempt: 3
depends_on: [ARCH-035-API-008]
enables: [ARCH-035-WOOCOMMERCE-008, ARCH-035-BACKGROUND-001]
created: 2026-10-11
updated: 2026-10-21
---

# ARCH-035-WOOCOMMERCE-007: Capture Woo checkout snapshots

## Developer Takeover

On 2026-10-20, the developer explicitly took ownership of Attempt 1 for implementation. The logical repository owner remains `moda_woocommerce`; this amendment changes only execution and completion authority to developer mode. The task scope, dependencies, acceptance criteria and architectural ownership are unchanged.

## Architecture

- Architecture: `ARCH-035`; document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`.
- Coordinator: `moda_architect`; baseline: `moda-interact-workspace(20261018-121025).zip`, revised 2026-10-20.
- Former task was superseded under the UI-only revision; this definition reopens only the explicitly approved **capture-only** scope. The task is materialised on the canonical parent branch; Attempt 2 reuses the existing canonical implementation worktree.

## Objective

Capture WooCommerce checkout updates and submit bounded events through the installed plugin server-to-server to the accepted API route.

## Context

The plugin owns merchant-controlled Woo hooks and connected installation credentials. Capture must be non-blocking for shoppers and cover Classic and Checkout Blocks with minimal implementation.

## Scope

**Developer-approved scope amendment — 2026-10-21, Attempt 3.** The developer explicitly elects to include and approve **the entire already-published WooCommerce implementation task-branch net change set through commit `95c305d0599837fc6eded75286dfd0724ef41772`**, including the previously disputed `319f033` changes. This approval removes the requirement to separate or revert these changes solely on scope grounds. The finite set comprises checkout capture and its test harness, billing-screen/summary changes, usage-history interface and tests, connected-workspace/controller changes, Merchant Knowledge upload UI, store-category save reconciliation, supporting general JavaScript/internationalisation/integration tests, and the repository-wide ESLint configuration migration (`.eslintrc.js`, `eslint.config.mjs`, `package.json`). It applies to this identified published diff, **not** arbitrary later changes or another repository.

The additional interface/test/lint work is accepted as a deliberate developer-approved expansion of **this WooCommerce task**. The original capture-only safety rules still govern the checkout event pathway: capturing checkout activity does not itself authorise recovery creation, WhatsApp outreach, consent collection, or charging for the capture event. This amendment does not change the API contract, ownership of other repositories, or existing task dependencies.

- Observe Woo checkout events through supported Classic and Checkout Blocks extension points and capture guest/customer checkouts.
- Keep one stable checkoutKey through repeated updates, and attach it to subsequently created orders using HPOS-compatible Woo metadata.
- Form bounded checkout snapshots with eventId, occurredAt, amounts, currency, items, optional contact and recovery URL only when actually available.
- Use an existing Woo background delivery facility; if no suitable durable retry exists, use the WooCommerce-bundled Action Scheduler rather than new queues/tables.
- Deliver through the existing connected-installation PHP API client and published API-008 contract.

## Out of Scope

- Customer WhatsApp opt-in/consent forms, permission evidence or allowlist management.
- Recovery materialisation, scheduling, outreach, WhatsApp, AI, charging or offer selection.
- New Woo activity receipts/lineage tables, new Shared contracts or Shopify-event impersonation.
- Changes to another repository or any `docs/decisions/**/_index.md` file.
- WordPress browser-exposed installation credential or synchronous mandatory HTTP delivery from the checkout request.

These exclusions continue to constrain checkout capture. They do not exclude the separately approved existing WooCommerce UI, test, and lint changes identified in the scope amendment above.

## Requirements

- Same eventId/payload must be preserved for retries; a new genuine checkout change gets a new eventId.
- Protect the customer checkout path: a failed Moda request may log/schedule retry but must not fail checkout.
- No invented consent or phone number. No client-provided Shop ID.
- Bound retries and payload size using existing Woo facilities; identify exhausted retries without exposing personal data.
- Classic, Blocks and HPOS pathways must use supported WooCommerce APIs/hooks; do not assume they share the same hook.

## Work Items

- [x] Implement checkout hook adapter and small bounded event publisher, reusing the existing PHP Moda API client. Published on implementation task branch at `5c4df4c`.
- [x] Persist the checkoutKey in appropriate Woo checkout/session/order metadata without a new custom WordPress table. Session and order-object metadata handling are published on the implementation task branch at `5c4df4c`.
- [x] Add Classic and Blocks integration tests, retry/deduplication cases and plugin regression tests. The focused scenario passed on 2026-10-21; the full WordPress integration runner also completed after the Action Scheduler HybridStore test-harness correction (see latest evidence addendum).

## Interfaces / Contracts

**API-owned `woo.activity.v1` contract** (published as strict OpenAPI + integration fixtures, not a new Shared package in this bounded scope):

```json
{
  "schemaVersion": "woo.activity.v1",
  "eventId": "stable-opaque-event-id",
  "eventType": "CHECKOUT_UPDATED",
  "checkoutKey": "stable-shop-scoped-key",
  "occurredAt": "2026-10-20T12:00:00.000Z",
  "checkout": { "currency": "GBP", "total": "29.99", "items": [] }
}
```

`eventType` is one of `CHECKOUT_UPDATED`, `ORDER_PLACED`, `ORDER_PAID`, `ORDER_CANCELLED`. For orders, use an `order` object with `orderId`, status and same `checkoutKey`; `checkout` is absent. A Woo producer sends no shop ID: API resolves Shop from installation credentials. Bounded customer/contact fields and line-item fields must be explicitly defined in the authoritative API schema; omit unavailable fields rather than fabricating them. Correlation key is `(authenticated shopId, checkoutKey)`. Stable `eventId` is retained on retries of the **same emitted event**; later genuine updates use a new `eventId`.

The hosted API owns `POST /v1/woocommerce/activity`. Checkouts are implemented by API-008; order event types are enabled by API-019 on the same route. Queue payloads retain `schemaVersion`, authenticated `shopId`, event identity, kind, checkout key and bounded validated snapshot. Background must validate the queued payload again and must **not** call the Shopify event parser. These contracts are specific to this API/Background integration; if a published cross-service primitive becomes necessary, stop and return the new ownership requirement to the architect rather than implement a competing Shared module.

## Dependencies

- `ARCH-035-API-008` — must be Complete and accepted before claiming.

## Enables

- `ARCH-035-WOOCOMMERCE-008`
- `ARCH-035-BACKGROUND-001`

## Acceptance Criteria

- [x] Classic and Blocks flows each emit correct checkout events for guests and logged-in users. Verified in both the focused checkout-only run and the later successful full WordPress integration run on 2026-10-21; see the latest evidence reconciliation.
- [x] Updates share checkoutKey but have distinct eventIds; retries preserve both identity and content. Verified by the focused checkout-only assertions and reproduced in the successful full WordPress integration run (guest and customer Blocks scenarios).
- [x] Shopper checkout proceeds during an API outage. The focused and successful full runs exercised the isolated HTTPS 503 fixture and retry assertions while checkout remained successful.
- [x] No consent UI, recovery scheduler or WhatsApp workflow is introduced.

## Validation

- [x] Plugin JS tests, PHP syntax checks, and production build. Attempt 2 reran the complete JS suite, Node integration/i18n tests, and PHP syntax checks. PHPUnit execution was unavailable because `vendor/bin/phpunit` is absent; prior passing PHPUnit evidence covers unchanged PHP implementation files.
- [x] **Focused checkout-only** WordPress integration: Classic + Blocks + HPOS correlation metadata, API failure/retry, checkout non-blocking proof. `MODA_CHECKOUT_TEST_DISPOSABLE=1 npm run test:integration:wordpress -- --checkout-only` reported PASS for both guest and customer paths on 2026-10-21; see evidence addendum.
- [x] **Full** WordPress regression: `MODA_CHECKOUT_TEST_DISPOSABLE=1 npm run test:integration:wordpress` on 2026-10-21 progressed through Classic/Blocks guest and customer checkout, 503/retry/HPOS, WOO-014 localisation, WOO-008 category, WOO-007 store context and WOO-003 REST/HTTPS, then cleaned up without a reported failure. The terminal recording does not print a separate aggregate PASS line or numeric exit code; see evidence reconciliation.
- [x] Production ZIP/package smoke test and diff check. Attempt 2 generated and audited the production archive; prior Docker-backed fresh/upgrade lifecycle evidence is preserved separately. The focused checkout-only and the later full WordPress runner results are evidenced independently on 2026-10-21.

## Stop Condition

After work items, acceptance criteria and required validation are satisfied, finish the Completion Report, transition the task to `review`, return it to `moda_architect`, and STOP. Do not proceed to enabled tasks.

## Implementation Notes

Avoid normalising a Woo contact to a Shopify customer ID. Inspect current WooCommerce plugin hooks before selecting implementation points; if Blocks do not expose the assumed lifecycle, use supported Woo Blocks hooks, not undocumented hacks.

## Completion Report

### Status

**Ready for Review — Accepted at Attempt 3, awaiting explicit developer completion.** The implementation is published and the documented validation evidence is reconciled. On 2026-10-21, the developer explicitly approved the complete existing implementation diff including `319f033`, resolving the sole outstanding scope objection without code separation or a new execution attempt. `status: review`, `attempt: 3`, `executor: null`, `claimed_at: null`, and `completion_mode: developer` remain the authoritative state until `/moda_developer_update ARCH-035-WOOCOMMERCE-007 complete` is invoked.

### Files Changed

Implementation task branch commits `5c4df4c`, `319f033`, `8cea08f`, and `95c305d` are published at `origin/task/ARCH-035-WOOCOMMERCE-007`; the implementation worktree is clean at `95c305d0599837fc6eded75286dfd0724ef41772`, equal to its remote. `5c4df4c` adds the checkout publisher/capture/key/snapshot, API client and Runtime wiring, Composer classmap configuration, and PHPUnit tests. `319f033` adds the WordPress checkout scenario and runner support, plus unrelated billing, usage-history, connected-workspace, recovery-knowledge UI, store-category, i18n/test, and global ESLint changes. These additional paths remain in the net diff from `afe307401664efdc11efe833e0da841013116e74` and are **now explicitly approved under the 2026-10-21 finite task-scope amendment**. They do not require separation into another task for W007 acceptance. The previously observed untracked `typescript` artifact is absent from the current worktree.

### Work Completed

Checkout hooks, bounded checkout snapshot/event publishing through the existing API client, Action Scheduler retry handling, and session/order-object checkout-key persistence are implemented and published. Commit `95c305d` commits the previously tested hook-only Action Scheduler CLI selection: it retains `--hooks=moda_interact_dispatch_checkout_activity`, removes `--group=moda-interact-activity`, and keeps stored-group assertions. The supplied full WordPress run reported Classic/Blocks guest/customer, 503/retry/HPOS and later Woo scenario PASS markers; it completed cleanup without a visible error, though its recording has no explicit numeric exit code or aggregate PASS line. The focused checkout run also has reported PASS evidence. These results support checkout capture behaviour; the previously questioned extra branch paths are now approved within this task by the developer's 2026-10-21 scope amendment. No further checkout changes are required solely for acceptance.

### Validation Results

Attempt 2 validation on the reviewed implementation commit: `npm run test:js` passed (49 Vitest files / 314 tests; Node phase 45/45), `node --test tests/integration/checkout-session.test.mjs` passed (4/4), PHP syntax checks passed for checkout files/API client/PHPUnit test, `npm run build` passed with two webpack asset-size/performance warnings, `npm run package:production` passed and generated a 120-entry archive (SHA-256 `aa858960606572ee87ff9a3ffaddab6fc2dded3ae7126a4a0b1c0d8998319a8f`), and `git diff --check origin/main...HEAD` passed. `composer test -- tests/CheckoutCaptureTest.php` could not execute because `vendor/bin/phpunit` is absent; prior PHPUnit evidence is recorded above for unchanged PHP implementation files. At the time of Attempt 2 review, the live WordPress scenario had not been run: the runner explicitly required `MODA_CHECKOUT_TEST_DISPOSABLE=1`, and the wp-env had not been confirmed disposable. That was the **historical** Attempt 2 limitation; later developer-supplied 2026-10-21 focused and full-run results are recorded in the new addendum below. Docker-backed package lifecycle evidence from the prior capture is retained but not repeated.

**Final Attempt 3 validation reconciliation (2026-10-21):** Published implementation HEAD `95c305d` was reported clean and identical to `origin/task/ARCH-035-WOOCOMMERCE-007`; `git diff --check origin/main...HEAD` passed. This commit includes the previously uncommitted hook-only Action Scheduler test correction. The focused checkout-only WordPress integration reported PASS; the later full WordPress integration shows all expected Classic/Blocks guest/customer, 503/retry/HPOS and subsequent Woo scenario PASS markers with cleanup and no visible failure (the terminal capture does not show a separate numeric exit code). The earlier checkout PHP/tests and Composer/PHPUnit configuration were confirmed equivalent to the baseline with historical focused **5 tests / 44 assertions PASS** and full **125 tests / 878 assertions PASS**; no fresh PHPUnit run is claimed because the current local PHP lacked `dom`, `mbstring`, and `xmlwriter`. Previously recorded JS/lint/build/production package validation remains the documented evidence. No new runtime validation is claimed by this scope-approval documentation patch.

### Deviations

Commit `319f033` combined checkout integration work with other WooCommerce UI, JS/test and ESLint changes. This was the reason for the historical Attempt 2/3 Changes Requested reviews. **Resolved by the developer's explicit 2026-10-21 scope approval**: those already-published paths are now authorised within W007. No file separation, rebasing, force-push or unrelated code churn is required. Older review records below remain intact as historical evidence.

### Assumptions

The implementation commit `5c4df4c` is durable on `origin/task/ARCH-035-WOOCOMMERCE-007`, and the implementation worktree is clean. Parent task record changes are committed and pushed separately on the matching parent task branch.

### Unresolved Issues

No remaining **review blocker** is recorded for the finite, developer-approved implementation diff through `95c305d`. The last scope objection is resolved by the developer's express authorisation. The historical PHPUnit passes apply only to the unchanged audited PHP baseline; no fresh PHPUnit execution is claimed. The task still requires its separate **explicit developer completion decision**, and no downstream dependency or index state is changed by this acceptance patch.

### Architectural Concerns

Capture-only is not permanent event archiving. Completed BullMQ jobs can expire; future recovery enablement must consider that captured past events may be unavailable.


## Validation Evidence Addendum — 2026-10-20 (developer-supplied, not architect acceptance)

The developer supplied terminal capture `typescript(20261020-132334)` from the dedicated `ARCH-035-WOOCOMMERCE-007` implementation worktree. The following validation was performed **before this documentation-only update**. Preserve the terminal capture as review evidence; the snapshot ZIP is not itself a Git-branch/commit verification. No application code or checkout test implementation is changed by this addendum.

| Command | Recorded outcome |
| --- | --- |
| `npm ci` | Completed; peer-dependency warnings were emitted. |
| `npm run build` | PASS; 20-locale verification and webpack build completed, with two webpack warnings. |
| `npm run test:js` | PASS; 49 Vitest files / 314 tests; an additional Node test phase reported 37 passed, 0 failed. |
| `npm run package:production` | PASS; production plugin package generated and audited. |
| `npm run test:integration:package-lifecycle` | PASS as reported by runner; WordPress 7.1.2, WooCommerce 11.1.2, PHP 8.1; fresh/upgrade/plugin lifecycle evidence. Candidate 0.1.0 archive SHA-256 `b1f16f40fa1b1114167fe90db2f9906b495f2a8b16030d049a1004b7c1bffeed`. A CLI command exited with code 1 *inside* the lifecycle sequence; the harness recovered/continued and reported the aggregate passing result. The reviewer should examine that individual failure if material to checkout capture, rather than describing every command as passed. |
| `git diff --check` | Invoked at the end of the captured shell sequence; no whitespace diagnostic was shown. This is not a substitute for validating any newly delivered patch. |
| `composer lint`, focused `composer test` and full `composer test` | Previously documented as passing in the Attempt 1 Completion Report (focused 5 tests / 44 assertions; full 125 tests / 878 assertions); **not newly run in this terminal capture**. |

### Reviewer reuse / non-duplication instruction

- **Do not repeat** the already-passing full JS suite, build, production package creation, or Docker-backed package-lifecycle run solely for the architect review. Inspect this recorded evidence and the implementation diff instead. Focused checks may be executed where they establish a specific changed behaviour or investigate the recorded intermediate CLI failure.
- Reuse applies only if the reviewed implementation commit, relevant lockfiles, packaged inputs, and test harness are unchanged from the tested baseline. If they changed or evidence cannot be reconciled to the commit under review, record the mismatch and rerun only the affected validation.
- The **live checkout-specific** integration remains unproven: Classic and Blocks, guest and authenticated customer, stable checkoutKey/eventId/deduplication, HPOS order correlation, API 503/outage non-blocking operation and identical retry. The existing package-lifecycle harness does **not** establish these facts. Add/run this focused WordPress integration coverage before ticking that work item or the checkout-related Acceptance Criteria.
- Task remains `ready`, Attempt 1, with no active claim. The developer's normal launcher owns the next attempt claim/increment. Neither this evidence addendum nor the passing package tests constitute architect acceptance or developer completion.

## Live Checkout Validation Evidence Addendum — 2026-10-21 (developer-supplied; not architect acceptance)

This supersedes **only the earlier statements that the live checkout-specific integration had not run**. Earlier Attempt 1/2 Completion Report and review observations remain as historical evidence; no earlier acceptance or Git publication is inferred. The source captures are `typescript(20261021-020232)` (focused run) and `typescript(20261021-100748)` (full run). Both were produced by the developer in the `ARCH-035-WOOCOMMERCE-007` execution context; the recordings do not establish the current branch HEAD, commit history or clean worktree. No application or test implementation is changed by this document-only evidence update.

| Execution | Observed result | Evidence boundary |
| --- | --- | --- |
| `MODA_CHECKOUT_TEST_DISPOSABLE=1 npm run test:integration:wordpress -- --checkout-only` | **PASS**: `ARCH-035 Classic guest: checkout AJAX capture PASS`; `ARCH-035 Blocks guest: capture, dedup, change, 503, retry and HPOS PASS`; corresponding Classic/Blocks customer PASS lines; `ARCH-035 checkout-only integration PASS`. | Demonstrates the checkout-only scenario's real Classic/Blocks guest/customer, checkout identity, mocked HTTPS 503, retry and HPOS assertions in the disposable integration environment. The runner's PASS does not establish hosted production API processing or prove the broader WordPress suite passes. |
| `MODA_CHECKOUT_TEST_DISPOSABLE=1 npm run test:integration:wordpress` (no `--checkout-only`) | **FAIL**: full runner starts wp-env at `http://localhost:8888`; Classic guest AJAX capture PASS; Blocks guest cart/update/checkout PATCH calls reached HTTP 200; then `wp action-scheduler run --hooks=moda_interact_dispatch_checkout_activity --group=moda-interact-activity --batch-size=20 --batches=1` failed: `The group "moda-interact-activity" does not exist`. | No Blocks guest completion, 503/retry verification, customer scenario or full-suite PASS was emitted by this run. Fixture cleanup executed; the root cause of the missing Action Scheduler group is **not established** by the log. |

### Subsequent lint and full-run evidence — 2026-10-21

The developer supplied `typescript(20261021-103458)` (terminal session recorded 2026-10-21 11:26–11:34 local), following the previously documented checkout-only PASS and first full-run failure. The new capture does **not** show a new checkout-only run or a passing full WordPress suite.

| Execution | Observed outcome | Scope / caveat |
| --- | --- | --- |
| `npm exec -- eslint --fix tests/integration/checkout-actions.test.mjs tests/integration/checkout-customer-update.test.mjs tests/integration/checkout-wordpress.mjs` | Command was invoked; the capture does not show a per-file change report. | This **may have edited** the three named integration tests. Inspect the actual working-tree diff before associating prior passing evidence with the final test revision. |
| `npm run lint:js` | **PASS: 0 errors, 6 warnings**, all reported in `tests/js/billing-screen.test.js` under `@wordpress/no-global-active-element` (lines 565, 570, 597, 602, 612 and 617). | Lint passed with warnings; no general zero-warning claim and no newly demonstrated PHP test results. |
| `npm run test:integration:wordpress` | **FAIL**, again at `wp action-scheduler run --hooks=moda_interact_dispatch_checkout_activity --group=moda-interact-activity --batch-size=20 --batches=1` with `The group "moda-interact-activity" does not exist`. WordPress started at `http://localhost:8888`; Classic guest checkout emitted PASS; Blocks guest requests progressed to PATCH, then the CLI command failed. | The runner executed cleanup and stopped WordPress. No Blocks guest completion, 503/retry assertion, customer flow, HPOS verification or full-suite PASS was emitted in this capture. The failure is **repeated, not resolved**. |

Action Scheduler's named-group error is emitted during group resolution for a claimed batch; it is **not equivalent to a valid empty queue**. This capture does not establish whether the group row was absent from the database, the runtime was using a different Action Scheduler store, or another lifecycle/race condition changed visibility. The correction contract remains to inspect the group/action state at the moment of failure, not disable the plugin's production identity checks or silently bypass the issue. The task remains `ready`, `attempt: 2`, `executor: null`, `claimed_at: null`, with the prior Changes Requested review unresolved.

### Later Action Scheduler diagnosis and passing full-suite evidence — 2026-10-21

After the previously documented failures, developer-provided terminal diagnostics `typescript(20261021-104534)`, `typescript(20261021-105126)` and `typescript(20261021-105233)` recorded the Action Scheduler `ActionScheduler_HybridStore`, a modern `moda-interact-activity` group (ID `4`) with `10` pending checkout actions, and no matching legacy `action-group` taxonomy term. This evidence supports the test CLI's `--group` selection encountering the HybridStore legacy lookup, rather than a missing modern group or a demonstrated production checkout-publisher defect.

The test-only `ARCH-035-WOOCOMMERCE-007-attempt8-accepted.patch` removed `--group=moda-interact-activity` from the **Action Scheduler CLI invocation** in `tests/integration/checkout-wordpress.mjs` while retaining `--hooks=moda_interact_dispatch_checkout_activity` and the test's stored-group assertions. Its filename is a delivered patch revision, **not** architect acceptance or a formal developer attempt. The record does not independently prove that the patch was committed/pushed; reconcile implementation worktree and branch state before review.

Developer-supplied recording `typescript(20261021-110444)` then ran `MODA_CHECKOUT_TEST_DISPOSABLE=1 npm run test:integration:wordpress` on 2026-10-21. Its observable results were:

| Full-run observation | Result |
| --- | --- |
| `ARCH-035 Classic guest: checkout AJAX capture PASS` | PASS |
| `ARCH-035 Blocks guest: capture, dedup, change, 503, retry and HPOS PASS` | PASS |
| `ARCH-035 Classic customer: checkout AJAX capture PASS` | PASS |
| `ARCH-035 Blocks customer: capture, dedup, change, 503, retry and HPOS PASS` | PASS |
| `WOO-014` 20-language and Shop-state, `WOO-008` category, `WOO-007` store context, `WOO-003` REST/HTTPS fixture checks | Each reported passed |
| Cleanup | Temporary Moda API config and locale options removed; WordPress stopped; no error/stack trace reported |

The capture shows completion and a returned shell prompt, but it does **not** explicitly record a numeric shell exit code or a single aggregate `full WordPress integration PASS` line. Accordingly this is a **successful developer-reported full integration run with all expected scenario PASS markers and no visible failure**, not independent production-provider validation. Earlier full-run failures remain historical evidence rather than ongoing defects.

**Remaining acceptance boundary:** obtain current Git HEAD, physical dedicated worktree status, exact source/test changes used by the successful run and whether Attempts 3/4/8 and the later `eslint --fix` edits were committed; reconcile relevant PHP test evidence, and separate/approve unrelated `319f033` files. Preserve production site-identity enforcement and the capture-only architecture. No formal task status or claim transition follows solely from this log.

### Evidence interpretation and required correction

- The focused and full WordPress integration runs now support the W007 checkout-specific acceptance behaviours. Historical full-run Action Scheduler failures are resolved at the test CLI boundary; the modern database group, retained hook restriction, and stored-group assertions remain intact.
- No further full WordPress rerun is required just to restate this PASS if the reviewed implementation and test fixture match the successful evidence. If the branch/test code is different or the evidence cannot be tied to the exact revision under review, rerun only the affected validation on an explicitly disposable environment. Do not weaken production site-identity enforcement or contact the live Moda API.
- The test-harness patch deliveries (`attempt3` asynchronous WP-CLI fixture handling, `attempt4` HPOS data-store assertion and `attempt8` Action Scheduler hook-only selection) are **not** formal task attempt increments, acceptance, or proof of Git commits. Reconcile the files currently present on the implementation task branch before final review.
- Preserve prior unit/JS/build/package evidence only to the extent it applies to the final reviewed implementation. PHPUnit setup/evidence and unrelated changes in `319f033` remain outstanding review issues.
- No branch/worktree/commit/push was performed by this evidence update. Keep `status: ready`, `attempt: 2`, `executor: null`, `claimed_at: null`, `execution_mode: developer`, and `completion_mode: developer`; developer completion and downstream dependency promotion are **not authorised**.

## Architect Review

### Review Status

**Accepted — Attempt 3, 2026-10-21.** The developer explicitly approved the entire already-published implementation diff through `95c305d`, including the additional changes introduced by `319f033`. This task-specific scope amendment resolves the final outstanding review objection. The prior Changes Requested decisions remain historical evidence rather than operative scope-separation requirements. The task is in `review` awaiting the separately authorised developer completion decision; it is **not yet `complete`**.

### Review Notes

The original checkout-capture safety and API boundaries are preserved. The developer-approved expansion also includes existing billing/usage-history/connected-workspace/merchant-knowledge/store-category UI work, general JS/i18n/integration test updates and the global ESLint migration from the reviewed branch diff. No new development attempt, implementation-source change, dependency change, or history rewrite is required to recognise this approval. The published Attempt 3 Changes Requested parent review `ae6b64e9` is superseded **only as to its open scope objection and resulting disposition**; all earlier observations remain traceable.

### Reviewed Files

Reviewed the captured final Git diff inventory and audit, `5c4df4c` checkout implementation, `319f033` mixed additions, and the clean, published `95c305d` hook-only Action Scheduler test correction as recorded in the developer Attempt 3 review. The approved finite scope is defined by the implementation branch's net diff through `95c305d`; the present documentation patch does not independently re-fetch the remote or imply validation of hypothetical subsequent changes.

### Validation Reviewed

Developer-supplied focused checkout-only WordPress integration PASS and full WordPress integration expected scenario PASS markers and cleanup without visible failure; previously recorded JS and lint (0 errors, 6 warnings), build, production ZIP/package lifecycle evidence; PHP syntax checks; recorded historical focused PHPUnit **5/44 PASS** and full **125/878 PASS** reused only for unchanged PHP source/test and Composer/PHPUnit baseline. The full-run terminal recording lacks an explicit numeric exit code. No new tests are claimed by this document-only review amendment.

### Architecture Conformance

**Accepted within the developer-authorised W007 scope amendment.** Checkout publishing preserves the existing API and site-identity protection, background Action Scheduler delivery, stable checkout identity, non-blocking checkout and capture-only boundaries. The extra WooCommerce-owned changes are accepted as within the user's explicit intended task scope; their inclusion is not a claim of separate feature-specific live end-to-end validation. Other repository boundaries and downstream task gates are unchanged.

### Follow-up

Commit/push this parent task review on `task/ARCH-035-WOOCOMMERCE-007`. Because `completion_mode: developer`, leave `status: review`, `attempt: 3`, and cleared claim fields. The developer may then explicitly invoke `/moda_developer_update ARCH-035-WOOCOMMERCE-007 complete`; only that step marks `complete` and recalculates dependent-task eligibility. Do not update `docs/decisions/**/_index.md` in this patch.

### Historical Attempt 1 review (preserved; superseded where stated)

#### Review Status

Changes Requested — this explicit completion request cannot pass because live integration/checkout-outage evidence and the remaining plugin validations are outstanding; no prior accepted review exists. The task was returned to `ready` with executor/claimed_at cleared and attempt unchanged at 1.

#### Review Notes

Scope reopened from Superseded only for the 20 October 2026 WooCommerce checkout/order capture exception. Historical supersession remains in Git. No architectural acceptance of implementation is implied.

#### Reviewed Files

Reviewed the published checkout capture/publisher/key/snapshot implementation, API client/runtime wiring, focused test file, and published API activity schema. Implementation task commit: `5c4df4c`.

#### Validation Reviewed

PHP lint passed; production build passed with bundle-size warnings; focused PHPUnit passed (5 tests, 44 assertions); full PHP suite passed (125 tests, 878 assertions). Plugin JS, live WordPress integration, and package smoke validation remain outstanding.

#### Architecture Conformance

Not accepted. The implementation uses the existing API client and Action Scheduler and avoids checkout-path HTTP. PHPUnit and production build pass, and implementation publication is verified; required live integration, outage proof, JS, and package validation remain outstanding.

#### Developer Self-Review - Changes Requested

1. Add and run a WordPress/WooCommerce integration check proving Classic and Checkout Blocks guest and logged-in checkout updates emit valid `woo.activity.v1` events, preserve checkoutKey through HPOS order metadata, and continue checkout during API failure while retrying the identical event.
2. Run the plugin JS test suite and the ZIP/plugin smoke test; record exact commands and results.
3. Update the Work Items, Acceptance Criteria, and Validation checkboxes only after the corresponding evidence passes. Then submit the task for review again. Do not increment attempt in this review; the next claim performs the single increment.

The explicit completion request was not accepted. Task state is `ready`; executor and claimed_at are null; attempt remains 1. No downstream dependency-frontier reconciliation was performed because the task did not complete.

#### Follow-up

None.

#### Review Evidence Reconciliation — 2026-10-20

The earlier `Validation Reviewed` and `Developer Self-Review - Changes Requested` subsections record findings **at the time of the Attempt 1 review**. They are preserved as historical observations. Subsequent developer-supplied validation now closes the **JS/build/package lifecycle/diff smoke** evidence items as detailed in the Validation Evidence Addendum above. The only required live checkout-specific WordPress integration evidence remains open. Do not repeat prior long-running passing validations just to refresh this review, subject to baseline equivalence. Review Status remains **Changes Requested** pending checkout integration and authorized completion.

## Developer Claim — Attempt 2

**Claimed — 2026-10-20T19:49:42Z.** The task transitioned from `ready`, Attempt 1, null executor to `in_progress`, Attempt 2, `executor: developer`.

- Dependency gate: `ARCH-035-API-008` was resolved through the canonical launcher as `complete` before claim.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-WOOCOMMERCE-007`, branch `task/ARCH-035-WOOCOMMERCE-007`. Existing task history was preserved; current `origin/main` was merged into the task branch before claim. The worktree had no working-tree edits before this claim.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-WOOCOMMERCE-007`, branch `task/ARCH-035-WOOCOMMERCE-007`, reused at `319f03384f9aae73b471f89cc20b1d4d05344f6a`. It was clean, matched `origin/task/ARCH-035-WOOCOMMERCE-007`, and included current Woo `origin/main` before claim.
- Synchronization: parent refs fetched and `origin/main` merged into the parent task branch; implementation refs fetched and the task branch was already synchronized with its remote and current `origin/main`.
- Scope remains capture-only. The remaining required work is checkout-specific WordPress integration evidence covering Classic and Blocks, guest/logged-in identity, HPOS order correlation, stable checkout/event identity, and API-outage non-blocking retry behavior. Do not begin tasks listed under Enables.

## Developer Self-Review - Changes Requested — Attempt 2

1. Run `npm run test:integration:wordpress -- --checkout-only` only against an explicitly disposable wp-env configured with the isolated Moda integration connection fixture. Set `MODA_CHECKOUT_TEST_DISPOSABLE=1` only after confirming that the target environment contains no user data. Record the exact result; the current environment was not modified.
2. Make PHPUnit available in the implementation worktree and run the focused checkout test plus relevant PHP regression tests, or record the exact setup blocker and reuse prior passing evidence only for unchanged PHP sources.
3. Separate the unrelated billing, usage-history, connected-workspace, recovery-knowledge UI, and general JS test changes in `319f033` into their owning task/branch, or obtain and record an explicit architecture-approved scope amendment. Preserve published history; do not force-push.
4. Update the remaining Acceptance Criteria and WordPress integration Validation checkbox only after live Classic/Blocks/guest/customer/HPOS/outage/retry assertions pass. Then submit the task for review again.

Review failed on required runtime evidence and unexplained scope expansion. Task state is `ready`; `executor` and `claimed_at` are null; attempt remains 2. The next `/moda_developer_create` claim increments the attempt exactly once.

### 2026-10-21 Evidence Reconciliation — Changes Requested remain open

The focused checkout-only validation is now evidenced as PASS, so do **not** rerun that long integration exercise solely to restate the same result if the implementation and fixture remain unchanged. The subsequent full WordPress runner passed the observed scenarios after the test-harness fix. Items still requiring bounded reconciliation before an Accepted review:

1. **Resolved (integration):** Action Scheduler HybridStore modern group/legacy taxonomy mismatch was inspected; the test CLI retains the checkout-hook filter but omits the `--group` filter. The subsequent full WordPress integration run contains the expected checkout scenario PASS markers and passes its later Woo checks. Do not reopen this without a changed baseline or new failure.
2. Reconcile test-only harness changes and the implementation branch HEAD/working-tree state with the passing focused **and full** integration logs. Record which exact test/code revisions were run, and preserve dedicated worktree evidence. Do not assume the `attempt3`/`attempt4` patch filenames imply task-claim or review acceptance.
3. Reconcile the focused PHPUnit/setup limitation using the last accepted unchanged-source evidence, or rerun the affected PHP tests if final reviewed source changed. Do not repeat unrelated previously passing suites without a changed baseline.
4. Separate the unrelated `319f033` billing/usage-history/workspace/recovery-knowledge/JS changes into their owning scope or obtain an explicit architecture-approved amendment. Do not rewrite published task history or force-push to conceal that drift.

**Disposition:** Integration testing is now evidenced as passing, but `Changes Requested` remains in force pending code-scope/PHP/Git review, with task state `ready` and recorded attempt 2 unchanged. No new developer claim, formal architect acceptance, task completion, index changes or dependency promotion is implied by the evidence addendum.

### 2026-10-21 Full WordPress Integration PASS — Evidence Reconciliation (not acceptance)

`typescript(20261021-110444)` shows a complete full WordPress integration invocation after the Action Scheduler CLI hook-only correction, with Classic/Blocks guest and logged-in PASS markers, 503/retry/HPOS checks, WOO-014/008/007/003 PASS markers and cleanup without a reported error. Supersedes the earlier full-run failure only as a *current integration-validation result*. The changes-required item to obtain a successful full WordPress integration run is satisfied.

**Still required before Authorized Review/Completion:** reconcile the actual checked-out implementation/test revision and dedicated worktree evidence; the test-only Attempts 3/4/8 and any ESLint changes; the unchanged-PHP prior PHPUnit evidence or focused rerun; and unrelated files in `319f033`. Do not mark this task `complete`, claim an additional attempt or promote its dependants from this evidence-only update. This record does not substitute for developer-completion authority.

### 2026-10-21 Final implementation Git audit and PHPUnit reconciliation — Changes Requested

This reconciliation follows developer-provided `ARCH-035-WOOCOMMERCE-007-final-git-audit(1).txt`, `ARCH-035-WOOCOMMERCE-007-final-implementation(1).diff`, and `ARCH-035-WOOCOMMERCE-007-uncommitted(1).diff`. It is a review of the physical implementation task worktree, **not** a new developer attempt, a code modification, an Accepted review, or an instruction to complete the task.

**Verified branch and commit boundary.** The audited implementation worktree is `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-WOOCOMMERCE-007`, on `task/ARCH-035-WOOCOMMERCE-007`; `HEAD` and `origin/task/ARCH-035-WOOCOMMERCE-007` are `8cea08f465ebb2e638ee3c0aef338492e1d92132`. `origin/main` and the merge base are `afe307401664efdc11efe833e0da841013116e74`. Branch commits are `5c4df4c`, `319f033`, and `8cea08f`; the final net diff contains **44 paths, 3,158 insertions and 877 deletions**. Both audited committed-range and uncommitted-range `git diff --check` passed. This establishes current task-branch evidence, but the physical worktree is **not clean**.

**PHPUnit evidence is reconciled for the audited PHP baseline.** The audit reports zero difference from `5c4df4c` for relevant checkout PHP source/tests and PHPUnit/Composer configuration, and SHA-256 MATCH against the uploaded snapshot (6) for `includes/Checkout/CheckoutKey.php`, `CheckoutSnapshot.php`, `CheckoutActivityPublisher.php`, `CheckoutCapture.php`, `includes/Api/ModaApiClient.php`, `includes/Runtime.php`, `tests/CheckoutCaptureTest.php`, `composer.json`, `composer.lock`, and `phpunit.xml.dist`. The historic task Completion Report records focused **5 tests / 44 assertions PASS** and full **125 tests / 878 assertions PASS**. Those are **reused historic passing results, not tests rerun during this review**. The audit's PHP 8.5.11 installation has `vendor/bin/phpunit` but lacks `dom`, `mbstring`, and `xmlwriter`, preventing a new PHPUnit run. The earlier report that the binary was absent described its earlier worktree/environment only. No repeat PHPUnit run is required solely to restate the unchanged-source evidence; relevant subsequent PHP/configuration changes must trigger focused reconsideration.

**Confirmed source-control scope deficiency.** `319f033` still contributes out-of-scope changes in the *net* branch diff: `src/billing-screen.js`, `src/billing/summary.js`, `src/page/connected-workspace.js`, `src/page/controller-factory.js`, Merchant Knowledge upload UI, store-category save reconciliation, `src/styles/_usage-history.scss`, `src/usage-history/*`, usage-history JS tests, general i18n/integration tests, and a repository-wide ESLint migration (`.eslintrc.js`, `eslint.config.mjs`, `package.json`). These are not authorised by the W007 capture-only scope merely because some are formatting/lint changes. Distinguish checkout-specific `tests/integration/checkout-*`, `tests/integration/run-wordpress.mjs`, and `tests/integration/wp-env-status*` from unrelated test/UI changes when separating the diff. Preserve any useful unrelated work for its owning task; do not broaden W007, silently discard unrelated work, rewrite published commits, or force-push.

**Confirmed uncommitted passing-test revision.** `git status --short` lists modified `tests/integration/checkout-actions.test.mjs`, `tests/integration/checkout-customer-update.test.mjs`, and `tests/integration/checkout-wordpress.mjs` and an untracked `typescript` artifact. The first two tracked diffs are formatting-only; the third includes formatting **and the essential hook-only Action Scheduler CLI correction**, removing `--group=moda-interact-activity` while retaining `--hooks=moda_interact_dispatch_checkout_activity`. Thus the previously successful full WordPress integration ran against **uncommitted test code**; the pushed `HEAD` still contains the old failing group selection. Preserve and commit the tested correction into the dedicated implementation task branch before acceptance. Keep or safely relocate the untracked artifact outside the repository; do not assume it is disposable without inspection.

**Required bounded correction contract, in order:**

1. Preserve the current mixed-commit diff and any unrelated changes as review/owner handoff evidence. Use the authorised `/moda_developer_create ARCH-035-WOOCOMMERCE-007` path to claim the next developer attempt **once**, after safeguarding the currently dirty worktree and satisfying launcher preparation. Keep published history intact; no reset/force-push to conceal `319f033`.
2. Commit the checkout-specific tested Action Scheduler correction and associated formatting changes (or deliberately trim formatting without altering behaviour and revalidate the affected tests). Record the resulting commit SHA and confirm the CLI no longer supplies `--group`.
3. Separate all net out-of-scope UI/billing/knowledge/usage/i18n/global-lint changes into their owning branch or use a new additive correction commit restoring the W007 branch's *net* out-of-scope paths to the pinned merge-base. If global lint migration is genuinely required, obtain and record a bounded architecture-approved scope/dependency exception before retaining it here. Avoid reverting checkout runner helpers or required API/checkout PHP files.
4. Produce final `git status --short`, `git diff --name-status afe307401664efdc11efe833e0da841013116e74...HEAD`, `git diff --check`, relevant checkout test checks, and evidence that no untracked test artifacts remain. Correlate the final checkout test code with the previously successful disposable `wp-env` run; rerun live integration only if functional test behaviour/fixtures changed or the passing evidence no longer maps to the committed code.
5. Update the developer Completion Report with the separation and validation evidence, transition to review through the authorised developer workflow, and return for architect acceptance. **Only after Accepted review** may developer completion and downstream dependency promotion be considered.

**Disposition:** Checkout live behaviour and the unchanged-PHP historic PHPUnit gate are evidenced; final branch scope and clean, committed tested-source gates remain **Changes Requested**. Preserve `status: ready`, `attempt: 2`, `executor: null`, `claimed_at: null`, `completion_mode: developer`. No `_index.md`, implementation code, new task, or dependency state is modified by this review addendum.

## Developer Claim — Attempt 3

**Claimed — 2026-10-21T11:48:42Z.** The task transitioned from `ready`, Attempt 2, null executor to `in_progress`, Attempt 3, `executor: developer` after the prior Changes Requested review.

- Dependency gate: `ARCH-035-API-008` resolved through the canonical launcher as `complete` before claim.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-WOOCOMMERCE-007`, branch `task/ARCH-035-WOOCOMMERCE-007`. Worktree was clean. Current `origin/main` was merged into the task branch at `dd999fe89a1b08683691cbb693ff6609940ca539`; the remote task branch tip `e1926c1ba9cd4bb9fdebecdcf35b122332ce1e50` is an ancestor of that synchronized branch.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-WOOCOMMERCE-007`, branch `task/ARCH-035-WOOCOMMERCE-007`, reused at clean commit `95c305d0599837fc6eded75286dfd0724ef41772`. HEAD matches `origin/task/ARCH-035-WOOCOMMERCE-007` and includes current implementation `origin/main` `afe307401664efdc11efe833e0da841013116e74`.
- Synchronization: parent refs fetched and task branch merged from current `origin/main`; implementation refs fetched and the task branch was already synchronized with its remote and current `origin/main`.
- The prior audit's reported implementation HEAD `8cea08f` and dirty tested harness/artifact state differ from the present clean worktree at `95c305d`. Reconcile the actual commit diff, task scope, and validation-to-commit relationship during this attempt before resubmitting for review. Do not rewrite published history or discard unrelated changes.
- Scope remains capture-only. Do not begin tasks listed under Enables.

## Developer Self-Review - Changes Requested — Attempt 3

The implementation worktree is clean and published at `95c305d0599837fc6eded75286dfd0724ef41772`; `HEAD` matches `origin/task/ARCH-035-WOOCOMMERCE-007`, and `git diff --check origin/main...HEAD` passed. The current commit includes the test-only Action Scheduler correction associated with the supplied successful full WordPress integration evidence. Historic PHPUnit results remain applicable only to PHP source/configuration unchanged from the audited baseline; a fresh PHPUnit run was not available because the installed PHP lacks `dom`, `mbstring`, and `xmlwriter`.

Review does not pass because the implementation branch's net diff from `afe307401664efdc11efe833e0da841013116e74` still includes out-of-scope billing, usage-history, connected-workspace, recovery-knowledge, store-category, general i18n/test and repository-wide ESLint changes introduced by `319f033`. These are not required for checkout capture, and no architect-approved scope amendment is recorded. A clean worktree and passing checkout integration evidence do not make those changes part of this task's scope.

Required correction before resubmission:

1. Preserve published history; do not rewrite commits or force-push. Separate the unrelated net changes to their owning task/branch, or obtain and record an explicit architecture-approved scope amendment before retaining any of them here.
2. Verify the final net diff against `afe307401664efdc11efe833e0da841013116e74` contains only capture-task files and necessary checkout-specific test harness support. Record `git status --short`, `git diff --name-status`, `git diff --check`, and exact implementation HEAD/upstream evidence.
3. Retain the successful disposable WordPress checkout evidence only where the committed test code matches it. If separating or changing checkout behavior/fixtures, rerun the affected focused validation on an explicitly disposable environment and record its exit result. Do not contact the live Moda API.
4. Do not mark this task complete or promote enabled tasks until the scope issue is resolved and the task receives its required review.

Disposition: Changes Requested. Transition to `ready`, clear `executor` and `claimed_at`, and preserve Attempt 3. The next developer claim increments once. No implementation files, unrelated changes, or downstream task records were modified during this review.

## Developer Self-Review — Accepted — Attempt 3 (2026-10-21)

**Disposition: Accepted.** This supersedes the immediately preceding Attempt 3 Changes Requested disposition **only because** the developer explicitly approved the complete existing WooCommerce implementation branch diff through `95c305d` as the intended W007 task scope. The prior request to separate `319f033` changes is withdrawn. Preserve the original Attempt 3 review as historical evidence; no force-push, source reversion, additional task claim or rerun of unchanged passing tests is required for scope reconciliation.

The clean/published implementation HEAD, committed checkout-harness correction, successful focused and full WordPress integration evidence, PHP source equivalence and recorded PHPUnit results form the reviewed implementation basis. The approval encompasses existing additional WooCommerce UI, JS/i18n/tests and ESLint changes identified above. It does not expand checkout capture into recovery creation, customer messaging, consent collection or charges triggered solely by capture, and it is not a blanket approval of future commits.

**Completion authority:** `completion_mode: developer`. The current task state is `review`, formal Attempt 3, with `executor: null` and `claimed_at: null`. The developer must make the separate explicit `/moda_developer_update ARCH-035-WOOCOMMERCE-007 complete` decision to transition to `complete` and allow downstream dependency reconciliation. No `_index.md` or downstream task is changed by this review.
