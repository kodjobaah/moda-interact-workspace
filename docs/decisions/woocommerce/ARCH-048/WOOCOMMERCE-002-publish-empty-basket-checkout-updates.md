---
id: ARCH-048-WOOCOMMERCE-002
architecture_id: ARCH-048
title: Publish complete Woo checkout updates including cleared baskets
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 25
executor: null
claimed_at: null
attempt: 2
depends_on:
- ARCH-035-WOOCOMMERCE-007
- ARCH-035-API-008
enables:
- ARCH-048-BACKGROUND-003
- ARCH-048-SYSTEM-TEST-001
created: '2026-10-23'
updated: '2026-10-27'
---

# ARCH-048-WOOCOMMERCE-002 — Publish complete Woo checkout updates including cleared baskets

## Architecture

Architecture ID: `ARCH-048`

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`

Coordinator: `moda_architect`

Portable **proposed** definition based on the uploaded 2026-10-23 18:50 snapshot; no branch, task worktree, implementation commit, accepted review or release is claimed. Check actual canonical task state before materialisation.

## Objective

Make every meaningful checkout basket-clear/refill transition observable through the existing authenticated outbound activity route, without exposing a WordPress read endpoint.

## Context

`CheckoutSnapshot::fromCart()` currently returns null for an empty cart, and `CheckoutCapture` then publishes no checkout update. API ingress already accepts `CHECKOUT_UPDATED` containing `items: []`. The publisher queues a stable event ID for retries through Action Scheduler.

## Scope

- Publish `CHECKOUT_UPDATED` with explicit `items: []` for an observed nonempty-to-empty transition of an already keyed checkout.
- Capture relevant cart/checkout changes through existing supported Classic/Blocks hooks, including checkout-origin basket changes where supported.
- Avoid false empty events for never-active carts and preserve Woo checkoutKey across legitimate clear/refill of the same checkout.
- Emit well-formed millisecond UTC occurrence times without inventing a new contract field.
- Preserve queued eventId and exact payload across retry; limit repeat no-op empty notifications.
- Distinguish unknown/oversized items (absent `items`, including more than 50 rows) from verified empty (`items: []`).

## Out of Scope

- No new WordPress REST routes, guest-session lookup, server-initiated remote reads, background scheduling, database schema or consent mutation.

## Requirements

- Only observed meaningful activity changes affect abandonment timing; missing `items` must never be interpreted as empty.
- Out-of-order/timestamp tie safety is owned by BACKGROUND-001; this task does not claim that timestamps alone provide perfect causal ordering.
- Use approved existing Woo API activity schema; no arbitrary new JSON fields or event types.

## Work Items

- [x] Cover Classic and Blocks empty/refill transitions and cart changes after checkout starts.
- [x] Add 51+ item, invalid snapshot, unchanged empty and transport retry/idempotency cases.
- [x] Verify actual Woo hooks and existing API payload validator integration.

## Interfaces / Contracts

- Produces existing `woo.activity.v1` / HTTP `woo.activity.v2` checkout payload through `CheckoutActivityPublisher` and existing POST `/v1/woocommerce/activity`.
- Consumes existing checkoutKey/session state only locally in event capture; no remote guest read.

## Dependencies

- `ARCH-035-WOOCOMMERCE-007`
- `ARCH-035-API-008`

## Enables

- `ARCH-048-BACKGROUND-003`
- `ARCH-048-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Genuine empty basket publishes `items: []`, once per meaningful transition, and no unexpected recovery is scheduled from a vanished/oversized snapshot.
- [x] Empty-to-refilled checkout creates a newer ordinary event; Woo and Moda existing checkout identity remain consistent.
- [x] Existing valid checkout/order publisher and 20-locale UI behaviour are unchanged; no HTTP endpoint is introduced.

## Validation

- [x] Focused PHPUnit/plugin Classic/Blocks/cart mutation and Action Scheduler retry tests.
- [x] API event-parser fixture validation for empty vs absent items, plugin declared lint/build scripts and `git diff --check`.
- [x] Exercise the Classic and Store API clear/refill assertions through the full local WordPress HTTP integration runner; record all five ARCH-048 PASS markers and cleanup.
- [x] Independently confirm that the WordPress environment used for the recorded test run was disposable before finalizing the acceptance of this live validation. Developer confirmed on 2026-10-27 that the wp-env was disposable and no valuable existing data or shared installation was at risk.

## Stop Condition

After only this task's work, criteria and required validation, complete the Completion Report with the launcher-resolved dedicated parent and implementation worktree paths, isolation, start-of-attempt synchronisation and repository revision evidence. Change to `review`, return to `moda_architect` and **STOP**. Do not start dependent work. Superseded tasks must not be claimed.

## Implementation Notes

- Do not write UI or session restoration functionality as a side effect.
- Security boundary: all new behaviour is outbound Woo → existing Moda API only.

- Use `/moda-task` preparation with the real developer workspace before code execution. Do not treat the snapshot as a Git branch; do not edit any `docs/decisions/**/_index.md` during this architecture session. Validate actual repository scripts rather than guessing commands. Respect assigned repository and task-document ownership.

## Completion Report

### Status

Developer Self-Review Passed — Attempt 2, claimed at `2026-10-27T10:35:37Z`; parent claim commit `b0752ac3` is present on `task/ARCH-048-WOOCOMMERCE-002`. Both declared dependencies are Complete. The launcher-resolved parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-048-WOOCOMMERCE-002` is clean at `0c33e2d44439b25b54e7bab33a726bc4553fdf78`, equal to `origin/task/ARCH-048-WOOCOMMERCE-002`. The implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-048-WOOCOMMERCE-002` is clean at `e075813fa94871b62bbbae07c2106957d34b43ff`, equal to `origin/task/ARCH-048-WOOCOMMERCE-002`. Parent startup synchronization and recursive submodule checks are preserved in the **Developer Attempt 2 Claim and Preparation** subsection below. The Attempt 1 Changes Requested record remains historical. The live integration scenarios and independently rerun focused checks pass; the developer confirmed that the wp-env was disposable. The task is in `review`, awaiting explicit developer completion because `completion_mode: developer`.

### Files Changed

- `includes/Checkout/CheckoutActivityPublisher.php`
- `includes/Checkout/CheckoutCapture.php`
- `includes/Checkout/CheckoutSnapshot.php`
- `tests/CheckoutCaptureTest.php`
- `tests/integration/checkout-hook-audit.md`
- `tests/integration/action-scheduler-sql.mjs`
- `tests/integration/action-scheduler-sql.test.mjs`
- `tests/integration/run-wordpress.mjs`
- `tests/integration/scenarios/checkout-wordpress.mjs`
- `tests/integration/scenarios/checkout-clear-refill-wordpress.mjs`
- `tests/integration/scenarios/checkout-clear-refill-wordpress.test.mjs`

### Work Completed

Published checkout capture changes to represent an observed keyed checkout becoming empty as `items: []`, preserve its checkout key on refill, ignore repeated no-op empty observations, register Classic and Store API hooks, and format `occurredAt` with millisecond UTC precision. A follow-up cleanup commit removed an unrelated `typescript` artifact from the implementation task branch.

Attempt 2 adds real HTTP-driven Classic/Store API clear/refill coverage for guest and customer checkouts, a supported Woo hook signature/ordering audit, and stable all-status Action Scheduler publication-history assertions that do not mistake retries for new events. Pending-only queries remain used for explicit retry tests. The latest modular implementation is reported committed and pushed at `e075813f`, with no new implementation changes during the developer claim.

### Validation Results

Start-of-attempt route, branch, worktree and recursive submodule synchronization checks passed.

- **PASS** — `vendor/bin/phpunit tests/CheckoutCaptureTest.php`: 12 tests, 109 assertions.
- **PASS** — `composer test`: 187 tests, 1,414 assertions.
- **PASS** — `composer lint`: all declared PHP syntax checks passed.
- **PASS** — `git diff --check origin/main...HEAD` and direct `php -l` on all four changed PHP files.
- **PASS** — API owner command `npm run test:arch035-woo-activity:unit`: 21 tests, including empty `items: []`, optional/absent items, and the 51-item limit.
- **PASS (recorded live integration)** — The full `npm run test:integration:wordpress` run is documented below with all five ARCH-048 PASS markers and fixture shutdown. The developer confirmed during review that the wp-env used was disposable and no valuable existing data or shared installation was at risk. The captured log has no numeric exit status, so none is claimed.

Attempt 2 evidence supplements, and does not replace, the Attempt 1 baseline:

- **PASS** — `npm run test:js:node` focused Node/integration-helper assertions reported 38/38 passed; checkout-focused subset 19/19 passed; JavaScript syntax and patch/diff checks passed.
- **PASS (independently rerun during review)** — `composer test`: 187 tests and 1,414 assertions; `composer lint`: all declared PHP syntax checks passed.
- **PASS (independently rerun during review)** — `npm run test:js:node`: 66 tests passed, 0 failed.
- **PASS (independently rerun during review)** — `npm run test:arch035-woo-activity:unit`: 21 tests passed, 0 failed.
- **PASS (observed test scenarios)** — `set -o pipefail; npm run test:integration:wordpress 2>&1 | tee arch048-woocommerce-002-attempt2-final-validation.log` exercised the real local WordPress HTTP server, including never-active empty suppression and guest/customer Classic/Store API clear-once, repeat-no-op and refill-with-same-key scenarios. All five `ARCH-048 ... PASS` markers appear in the uploaded `arch048-woocommerce-002-attempt2-final-validation(1).log` together with ARCH-035 regressions, WOO-003/007/008/014 checks, and successful fixture shutdown (`✔ Stopped WordPress.`). No assertion or uncaught exception is reported.
- **QUALIFICATION** — The terminal transcript does not include an explicitly printed numeric process exit status; do not assert that `echo $?` was captured. The test command completed and returned to the shell prompt without a reported failure.
- **SAFETY CONFIRMED** — The developer confirmed on 2026-10-27 that the Docker-backed local wp-env used for the live run was disposable and that no valuable existing data or shared installation was at risk. No rerun was needed solely to prove disposability.

### Deviations

- During Attempt 1, PHPUnit coverage alone did not establish actual WooCommerce HTTP hook invocation. Attempt 2 addresses that evidence gap using real Classic and Store API requests; see the Attempt 2 validation markers above.
- The full wp-env run is evidenced by the developer's terminal output, not reproduced during this review. Environmental disposability was confirmed by the developer on 2026-10-27.

### Assumptions

The latest uploaded workspace ZIP is a source snapshot, not necessarily the developer's latest task branches. The developer reports `ARCH-046-BACKGROUND-004` complete after the ZIP; verify its accepted implementation for consumer integration, without reopening it.

### Unresolved Issues

The API-008 parser accepts explicit empty `items` and preserves absent items as unknown; its focused contract suite passed. No new cross-repository contract gap was identified.

No unresolved implementation, validation, or safety issue blocks developer review. Explicit developer completion remains pending by design because `completion_mode: developer`.

### Architectural Concerns

See the parent architecture for the explicitly acknowledged event-only missed-event limitation.

## Architect Review

### Review Status

Pending — no implementation reviewed.

### Review Notes

None.

### Reviewed Files

None.

### Validation Reviewed

None.

### Architecture Conformance

Not assessed.

### Follow-up

None.

## Execution Ownership Amendment

- Date: 2026-10-26
- Change: The developer explicitly invoked `/moda_developer_create` for this ready agent-owned task. Execution ownership is transferred to the developer, and completion is set to developer review.
- Preserved: `assigned_agent: moda_woocommerce`, coordinator, repository, task scope, acceptance criteria and validation requirements.
- Claim state: Developer Attempt 1 was claimed after confirming both dependencies complete and preparing the canonical parent and implementation worktrees.

## Developer Self-Review - Changes Requested

### Review Decision

Attempt 1 is returned to `ready`. The focused and full PHPUnit suites, declared PHP lint, diff checks, and API-008 activity contract tests pass. The required live Woo hook behavior and end-to-end clear/refill evidence are not established, so this is a validation gap rather than a claim that the implementation behavior failed.

### Required Corrections

- Add and run a disposable WordPress integration scenario that exercises actual Classic and Store API clear/refill requests. Assert that a previously keyed non-empty checkout emits exactly one `CHECKOUT_UPDATED` with `items: []`, repeated empty requests emit no duplicate, refill emits a newer event with the same checkout key, and a never-active empty cart emits no event. Record the exact command and PASS output. Use only a disposable wp-env; do not set `MODA_CHECKOUT_TEST_DISPOSABLE=1` for an unverified existing site.
- Verify the current PHP/Woo hook signatures and invocation ordering for `woocommerce_cart_item_removed`, `woocommerce_cart_emptied`, `woocommerce_store_api_checkout_update_order_from_request`, and `woocommerce_store_api_cart_update_customer_from_request` against the supported WooCommerce versions. Update the real integration scenario to exercise those routes rather than only asserting hook registration in PHPUnit.

### Evidence Reviewed

- Implementation task branch `e021a17292c8e1f193cddaf443ebeaadb8e10174` equals `origin/task/ARCH-048-WOOCOMMERCE-002`; implementation worktree is clean.
- Parent claim is published at `1908523d97a46c069ff5e65c554723ee261ef311`; parent worktree is clean before this review update.
- Focused checkout PHPUnit: 12/12 tests, 109 assertions.
- Full PHP suite: 187/187 tests, 1,414 assertions.
- Declared `composer lint`, changed-file PHP syntax checks, and `git diff --check`: passed.
- API-008 Woo activity contract suite: 21/21 tests passed.
- WordPress integration terminal output did not provide a reliable final result; no pass is claimed.

### Attempt State

Attempt remains 1. No Attempt 2 claim is created by the Attempt 1 review. The next `/moda_developer_create ARCH-048-WOOCOMMERCE-002` invocation may claim Attempt 2 after the developer decides to continue.

## Attempt 2 Validation Evidence — Developer Reconciliation Handoff (2026-10-27)

This section is a **supplement** to the historical Attempt 1 Changes Requested
record above; it does not overwrite that review. The original portable evidence patch was prepared before Attempt 2 was claimed
and did not itself change execution state. The developer has since claimed
Attempt 2 at `2026-10-27T10:35:37Z` and published claim commit `b0752ac3`.
The current state is `in_progress`, `attempt: 2`, `executor: developer`;
the developer self-review transition remains pending the environment-safety gate.
Reconcile using `/moda_developer_update ARCH-048-WOOCOMMERCE-002` after confirmation.

### Corrective Work Delivered

- Retain the Attempt 1 production change in `CheckoutSnapshot.php`,
  `CheckoutCapture.php`, `CheckoutActivityPublisher.php` and its focused PHPUnit
  coverage: verified keyed empty carts publish `items: []`; never-active carts
  do not; refill reuses the checkout key; oversized/unknown snapshots omit
  `items`; retries preserve event payload/identity.
- Add a genuine HTTP-driven Classic and Store API clear/refill scenario, then
  align it with the modular integration suite under
  `tests/integration/scenarios/checkout-clear-refill-wordpress.mjs`.
- Use `tests/integration/action-scheduler-sql.mjs` to observe durable all-status
  Action Scheduler history for publication assertions (count first-attempt
  publications, not retries). Preserve pending-only queries for the explicit
  retry/transport tests. Add focused helper and scenario regression tests.
- Update the modular checkout scenarios and runner under
  `tests/integration/scenarios/checkout-wordpress.mjs` and
  `tests/integration/run-wordpress.mjs`. The new harness does not add a hosted
  API contract, WordPress REST endpoint, database migration or merchant-facing
  feature.
- `tests/integration/checkout-hook-audit.md` records upstream signatures and
  ordering for the cart-removal, cart-empty, Store API order-update and
  customer-update hooks against WooCommerce tags 11.0.1 and 11.1.2, including
  checkout draft/PATCH behaviour.

### Validation Results for Review

- **PASS (Attempt 1 baseline)** — Checkout PHPUnit: 12 tests, 109 assertions;
  full PHPUnit: 187 tests, 1,414 assertions; declared Composer PHP lint;
  changed-file syntax and diff checks.
- **PASS (Attempt 1 baseline)** — API activity contract suite: 21 tests,
  covering explicit `items: []`, omitted items and the 51-line bound.
- **PASS (Attempt 1 baseline)** — `npm run build` compiled the WordPress assets;
  webpack reported performance-size warnings, not a build failure.
- **PASS (Attempt 2 focused checks)** — Modular integration helper tests: 38/38;
  checkout-focused Node tests: 19/19; JavaScript syntax, patch-application and
  whitespace checks. These are developer/assistant checks from the submitted
  correction artifacts and do not replace live WordPress tests.
- **PASS (live WordPress scenarios)** — `set -o pipefail; npm run
  test:integration:wordpress 2>&1 | tee
  arch048-woocommerce-002-attempt2-final-validation.log` drove the real local
  WooCommerce/WordPress HTTP routes. The final 2026-10-27 log contains:
  - `ARCH-048 never-active empty Store API/Classic requests PASS`
  - `ARCH-048 guest Classic: clear once, repeat no-op, refill with same key PASS`
  - `ARCH-048 guest Store API: clear once, repeat no-op, refill with same key PASS`
  - `ARCH-048 customer Classic: clear once, repeat no-op, refill with same key PASS`
  - `ARCH-048 customer Store API: clear once, repeat no-op, refill with same key PASS`
  - All logged ARCH-035 Classic/Blocks checkout, placed/paid/cancelled,
    deduplication, retry and HPOS regressions also report PASS. Other Woo
    integration checks (WOO-003/007/008/014) report PASS.
  - The completed run cleans up fixture state and ends with
    `✔ Stopped WordPress.` without a reported assertion or uncaught exception.
    The shell transcript records command completion and a subsequent `exit`,
    but **does not print a numeric process exit status**. Do not claim that
    `echo $?` or an explicit numeric `0` was captured.
- An earlier command invocation was interrupted before completion; only the
  subsequent full run is used as successful scenario evidence.

### Review/Publication Checks Still Owned by Developer

- **CONFIRMED** — The developer confirmed on 2026-10-27 that the local `wp-env`
  used for the recorded full WordPress run was disposable and no valuable
  existing data or shared installation was at risk.
- **Developer-reported complete at claim** — The latest modular test corrections
  were committed and published as implementation HEAD
  `e075813fa94871b62bbbae07c2106957d34b43ff`, equal to remote task branch.
  The implementation worktree was clean at that point; independent remote
  verification remains part of the canonical developer reconciliation.
- **CLAIMED** — `/moda_developer_create ARCH-048-WOOCOMMERCE-002` completed
  with Attempt 2 and parent claim commit `b0752ac3` (developer report).
  Do **not** claim another attempt.
- **REVIEW PASSED** — Attempt 2 passed developer self-review and transitioned
  to `review`; `executor` and `claimed_at` are null, and `attempt` remains 2.
  With `completion_mode: developer`, explicit developer completion remains
  pending. No dependent task was started, and neither task branch was merged to
  `main`.
- Leave `## Architect Review`, domain `_index.md`, parent architecture and
  unrelated tasks unchanged.

### Developer Attempt 2 Claim and Preparation

- Claimed by `developer` at `2026-10-27T10:35:37Z`; lifecycle state is
  `in_progress`, attempt 2. `assigned_agent: moda_woocommerce`, task scope,
  acceptance criteria and developer completion mode are unchanged.
- Explicit dependencies rechecked in the canonical workspace:
  `ARCH-035-WOOCOMMERCE-007` and `ARCH-035-API-008` are both `complete`.
- Parent task worktree:
  `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-048-WOOCOMMERCE-002`.
  Merged current `origin/main` at
  `8956955d588ff34117c6fca73070017668b72ba9`; synchronized HEAD is
  `ea3e101905eaa2baa387ca66d8f35525c5ab9987`. Worktree is clean before this
  task-record update.
- Implementation worktree:
  `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-048-WOOCOMMERCE-002`.
  Current `origin/main` (`4f2d0db19931e14127a8399b3e4629ede3d2e280`) is an
  ancestor of task HEAD `e075813fa94871b62bbbae07c2106957d34b43ff`; HEAD equals
  `origin/task/ARCH-048-WOOCOMMERCE-002`. Worktree is clean and recursive
  submodule status is empty.
- The published implementation HEAD includes the Attempt 2 corrective files
  described above. No implementation files were changed by this claim.
- The submitted live WordPress scenario evidence is retained for review, but
  disposability of the wp-env used for that run was confirmed during Attempt 2
  reconciliation; no destructive test rerun was needed solely to prove it.

## Developer Self-Review Passed/Accepted — Attempt 2

### Review Decision

Attempt 2 passes developer self-review. Required work items, acceptance criteria
and validation are complete. Focused PHPUnit, declared PHP lint, Node integration
helper/scenario tests, and API activity contract tests pass. The recorded live
WordPress HTTP scenarios cover the required Classic and Store API clear/refill
behavior, and the developer confirmed the environment was disposable. No known
implementation or validation issue blocks review.

### Evidence Reviewed

- Parent task worktree is clean on `task/ARCH-048-WOOCOMMERCE-002` at
  `0c33e2d44439b25b54e7bab33a726bc4553fdf78`, matching
  `origin/task/ARCH-048-WOOCOMMERCE-002` before this report update.
- Implementation worktree is clean on `task/ARCH-048-WOOCOMMERCE-002` at
  `e075813fa94871b62bbbae07c2106957d34b43ff`, matching
  `origin/task/ARCH-048-WOOCOMMERCE-002`.
- `composer test`: 187 tests and 1,414 assertions passed; `composer lint` passed.
- `npm run test:js:node`: 66 tests passed; the API activity contract suite
  reported 21 tests passed.
- The recorded full WordPress run contains all five required ARCH-048 PASS
  markers and fixture shutdown. The developer confirmed on 2026-10-27 that the
  wp-env was disposable and no valuable existing data or shared installation was
  at risk. The log does not provide a numeric process exit code, which is not
  claimed as captured evidence.

### Attempt State

Transitioned to `review`; `executor: null`, `claimed_at: null`, `attempt: 2`.
Because `completion_mode: developer`, explicit developer completion remains
pending. No dependent task was started, and no branch was merged to `main`.
