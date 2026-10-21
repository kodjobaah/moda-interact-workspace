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
status: ready
priority: 56
executor: null
claimed_at: null
attempt: 2
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

## Requirements

- Same eventId/payload must be preserved for retries; a new genuine checkout change gets a new eventId.
- Protect the customer checkout path: a failed Moda request may log/schedule retry but must not fail checkout.
- No invented consent or phone number. No client-provided Shop ID.
- Bound retries and payload size using existing Woo facilities; identify exhausted retries without exposing personal data.
- Classic, Blocks and HPOS pathways must use supported WooCommerce APIs/hooks; do not assume they share the same hook.

## Work Items

- [x] Implement checkout hook adapter and small bounded event publisher, reusing the existing PHP Moda API client. Published on implementation task branch at `5c4df4c`.
- [x] Persist the checkoutKey in appropriate Woo checkout/session/order metadata without a new custom WordPress table. Session and order-object metadata handling are published on the implementation task branch at `5c4df4c`.
- [x] Add Classic and Blocks integration tests, retry/deduplication cases and plugin regression tests. The focused live WordPress scenario in `tests/integration/checkout-wordpress.mjs` subsequently passed on 2026-10-21; the separate full WordPress runner remains failed (see Validation and evidence addendum).

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

- [x] Classic and Blocks flows each emit correct checkout events for guests and logged-in users. Verified by the developer-supplied 2026-10-21 **checkout-only** WordPress integration run (see latest evidence addendum); the later **full** WordPress runner failed and is separately recorded below.
- [x] Updates share checkoutKey but have distinct eventIds; retries preserve both identity and content. Verified by the focused checkout-only dedup/change/503/retry assertions; no claim is made about the failed full runner.
- [x] Shopper checkout proceeds during an API outage. The focused run asserted successful checkout HTTP responses while its isolated HTTPS fixture returned 503, then the scheduled retry preserved the event; the full runner did not reach this proof.
- [x] No consent UI, recovery scheduler or WhatsApp workflow is introduced.

## Validation

- [x] Plugin JS tests, PHP syntax checks, and production build. Attempt 2 reran the complete JS suite, Node integration/i18n tests, and PHP syntax checks. PHPUnit execution was unavailable because `vendor/bin/phpunit` is absent; prior passing PHPUnit evidence covers unchanged PHP implementation files.
- [x] **Focused checkout-only** WordPress integration: Classic + Blocks + HPOS correlation metadata, API failure/retry, checkout non-blocking proof. `MODA_CHECKOUT_TEST_DISPOSABLE=1 npm run test:integration:wordpress -- --checkout-only` reported PASS for both guest and customer paths on 2026-10-21; see evidence addendum.
- [ ] **Full** `npm run test:integration:wordpress` regression: the 2026-10-21 run FAILED in the Blocks guest scenario at `wp action-scheduler run` because group `moda-interact-activity` was reported missing. Investigate and rerun on an explicitly disposable fixture; do not equate the checkout-only PASS with a full-run PASS.
- [x] Production ZIP/package smoke test and diff check. Attempt 2 generated and audited the production archive; prior Docker-backed fresh/upgrade lifecycle evidence is preserved separately. The checkout-only live validation is evidenced independently on 2026-10-21; the full WordPress runner is still failed.

## Stop Condition

After work items, acceptance criteria and required validation are satisfied, finish the Completion Report, transition the task to `review`, return it to `moda_architect`, and STOP. Do not proceed to enabled tasks.

## Implementation Notes

Avoid normalising a Woo contact to a Shopify customer ID. Inspect current WooCommerce plugin hooks before selecting implementation points; if Blocks do not expose the assumed lifecycle, use supported Woo Blocks hooks, not undocumented hacks.

## Completion Report

### Status

Changes Requested — the 2026-10-21 developer-supplied **checkout-only** WordPress run passed its live checkout assertions, but the subsequent **full** WordPress integration run failed at Action Scheduler's group lookup. The unresolved full-run regression, PHPUnit/commit-evidence reconciliation and unrelated changes in `319f033` still prevent acceptance. This documentation reconciliation is not a new execution claim or Accepted review: task remains `ready`, `executor` and `claimed_at` null, and recorded `attempt` remains 2.

### Files Changed

Implementation task branch commits `5c4df4c` and `319f033` are published at `origin/task/ARCH-035-WOOCOMMERCE-007`; the implementation worktree is clean. `5c4df4c` adds the checkout publisher/capture/key/snapshot, API client and Runtime wiring, Composer classmap configuration, and PHPUnit tests. `319f033` adds the WordPress checkout scenario and runner support, plus unrelated billing, usage-history, connected-workspace, recovery-knowledge UI, and general JS test changes. Those unrelated changes are outside this task's capture-only scope and require separation or explicit architecture-approved scope amendment. The previously observed untracked `typescript` artifact is no longer present and was not included in the task commits.

### Work Completed

Checkout hooks, bounded checkout snapshot/event publishing through the existing API client, Action Scheduler retry handling, and session/order-object checkout-key persistence are implemented and published. A WordPress scenario drives real Classic AJAX and Blocks Store API requests for guest and authenticated sessions, tests deduplication/change identity and 503 retry, and verifies HPOS order metadata. The focused checkout-only run on 2026-10-21 passed these live assertions. The later full WordPress runner exercised Classic guest capture but failed during Blocks guest delivery before completing the scenario. The integration-test work item and plugin JS regression tests remain complete; the full-run failure is open.

### Validation Results

Attempt 2 validation on the reviewed implementation commit: `npm run test:js` passed (49 Vitest files / 314 tests; Node phase 45/45), `node --test tests/integration/checkout-session.test.mjs` passed (4/4), PHP syntax checks passed for checkout files/API client/PHPUnit test, `npm run build` passed with two webpack asset-size/performance warnings, `npm run package:production` passed and generated a 120-entry archive (SHA-256 `aa858960606572ee87ff9a3ffaddab6fc2dded3ae7126a4a0b1c0d8998319a8f`), and `git diff --check origin/main...HEAD` passed. `composer test -- tests/CheckoutCaptureTest.php` could not execute because `vendor/bin/phpunit` is absent; prior PHPUnit evidence is recorded above for unchanged PHP implementation files. At the time of Attempt 2 review, the live WordPress scenario had not been run: the runner explicitly required `MODA_CHECKOUT_TEST_DISPOSABLE=1`, and the wp-env had not been confirmed disposable. That was the **historical** Attempt 2 limitation; later developer-supplied 2026-10-21 focused and full-run results are recorded in the new addendum below. Docker-backed package lifecycle evidence from the prior capture is retained but not repeated.

### Deviations

The implementation branch's `319f033` commit combines W007 checkout integration work with unrelated UI and general test changes. Separate unrelated changes into their owning task/branch or obtain an explicit architecture-approved scope amendment before resubmitting this task.

### Assumptions

The implementation commit `5c4df4c` is durable on `origin/task/ARCH-035-WOOCOMMERCE-007`, and the implementation worktree is clean. Parent task record changes are committed and pushed separately on the matching parent task branch.

### Unresolved Issues

The checkout-only integration has passed, but the full WordPress runner failed on 2026-10-21 with `The group "moda-interact-activity" does not exist` during Action Scheduler execution; root cause is not yet established. PHPUnit could not execute during Attempt 2 because the Composer PHPUnit binary was absent; no newer PHP test evidence is supplied. The task worktree's current Git diff/commit state after the test-harness patches has not been provided. No durable Accepted review exists. Unrelated files in `319f033` still require scope separation or explicit architect approval.

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

### Evidence interpretation and required correction

- The focused integration proves the W007 checkout-specific acceptance behaviours and closes the original unchecked live-checkout validation item. The broader runner failure is recorded as a separate **open** regression, not silently treated as a passed full suite or a production publisher defect.
- Before completing W007, investigate Action Scheduler group visibility/lifecycle specifically when the checkout scenario is run after the full runner's preceding setup/connection/activation steps. Verify queued action and group state at the failure boundary; correct the owning fixture/test mechanism if confirmed. Retest the full runner on an explicitly disposable WordPress site, without disabling the publisher's installation-identity protection or contacting the live Moda API.
- The two earlier test-harness patch deliveries (as named in the conversation, `attempt3` asynchronous WP-CLI fixture handling and `attempt4` HPOS data-store assertion) are **not** a formal task attempt increment, acceptance, or proof of a Git commit. Reconcile the files currently present on the implementation task branch before final review.
- Preserve prior unit/JS/build/package evidence only to the extent it applies to the final reviewed implementation. PHPUnit setup/evidence and unrelated changes in `319f033` remain outstanding review issues.
- No branch/worktree/commit/push was performed by this evidence update. Keep `status: ready`, `attempt: 2`, `executor: null`, `claimed_at: null`, `execution_mode: developer`, and `completion_mode: developer`; developer completion and downstream dependency promotion are **not authorised**.

## Architect Review

### Review Status

Changes Requested — this explicit completion request cannot pass because live integration/checkout-outage evidence and the remaining plugin validations are outstanding; no prior accepted review exists. The task was returned to `ready` with executor/claimed_at cleared and attempt unchanged at 1.

### Review Notes

Scope reopened from Superseded only for the 20 October 2026 WooCommerce checkout/order capture exception. Historical supersession remains in Git. No architectural acceptance of implementation is implied.

### Reviewed Files

Reviewed the published checkout capture/publisher/key/snapshot implementation, API client/runtime wiring, focused test file, and published API activity schema. Implementation task commit: `5c4df4c`.

### Validation Reviewed

PHP lint passed; production build passed with bundle-size warnings; focused PHPUnit passed (5 tests, 44 assertions); full PHP suite passed (125 tests, 878 assertions). Plugin JS, live WordPress integration, and package smoke validation remain outstanding.

### Architecture Conformance

Not accepted. The implementation uses the existing API client and Action Scheduler and avoids checkout-path HTTP. PHPUnit and production build pass, and implementation publication is verified; required live integration, outage proof, JS, and package validation remain outstanding.

### Developer Self-Review - Changes Requested

1. Add and run a WordPress/WooCommerce integration check proving Classic and Checkout Blocks guest and logged-in checkout updates emit valid `woo.activity.v1` events, preserve checkoutKey through HPOS order metadata, and continue checkout during API failure while retrying the identical event.
2. Run the plugin JS test suite and the ZIP/plugin smoke test; record exact commands and results.
3. Update the Work Items, Acceptance Criteria, and Validation checkboxes only after the corresponding evidence passes. Then submit the task for review again. Do not increment attempt in this review; the next claim performs the single increment.

The explicit completion request was not accepted. Task state is `ready`; executor and claimed_at are null; attempt remains 1. No downstream dependency-frontier reconciliation was performed because the task did not complete.

### Follow-up

None.

### Review Evidence Reconciliation — 2026-10-20

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

The focused checkout-only validation is now evidenced as PASS, so do **not** rerun that long integration exercise solely to restate the same result if the implementation and fixture remain unchanged. The separate full WordPress runner failure requires the following bounded correction/reconciliation before an Accepted review:

1. Inspect the Action Scheduler `moda-interact-activity` group and pending checkout actions after the full runner's connection and plugin reactivation setup; identify why the WP-CLI action runner reports the group absent although checkout events are queued. Fix the test/environment issue or demonstrate a concrete production defect before changing publisher behaviour. Supply a passing full-run log or explicit evidence and architect disposition of any unrelated suite failure.
2. Reconcile test-only harness changes and the implementation branch HEAD/working-tree state with the passing checkout-only log. Record which exact test/code revisions were run, and preserve dedicated worktree evidence. Do not assume the `attempt3`/`attempt4` patch filenames imply task-claim or review acceptance.
3. Reconcile the focused PHPUnit/setup limitation using the last accepted unchanged-source evidence, or rerun the affected PHP tests if final reviewed source changed. Do not repeat unrelated previously passing suites without a changed baseline.
4. Separate the unrelated `319f033` billing/usage-history/workspace/recovery-knowledge/JS changes into their owning scope or obtain an explicit architecture-approved amendment. Do not rewrite published task history or force-push to conceal that drift.

**Disposition:** `Changes Requested` remains in force, with task state `ready` and recorded attempt 2 unchanged. No new developer claim, formal architect acceptance, task completion, index changes or dependency promotion is implied by the evidence addendum.
