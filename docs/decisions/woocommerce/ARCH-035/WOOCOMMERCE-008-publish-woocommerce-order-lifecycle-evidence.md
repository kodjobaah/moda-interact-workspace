---
id: ARCH-035-WOOCOMMERCE-008
architecture_id: ARCH-035
title: Capture Woo order lifecycle events
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: complete
priority: 58
executor: null
claimed_at: null
attempt: 1
depends_on: [ARCH-035-API-019, ARCH-035-WOOCOMMERCE-007]
enables: [ARCH-035-BACKGROUND-002, ARCH-035-SYSTEM-TEST-002]
created: 2026-10-11
updated: 2026-10-21
---

# ARCH-035-WOOCOMMERCE-008: Capture Woo order lifecycle events

## Architecture

- Architecture: `ARCH-035`; document: `docs/architecture/ARCH-035-woocommerce-merchant-experience-parity.md`.
- Coordinator: `moda_architect`; baseline: `moda-interact-workspace(20261018-121025).zip`, revised 2026-10-20.
- Former task was superseded under the UI-only revision; this definition reopens only the explicitly approved **capture-only** scope. The task is materialised on its canonical parent task branch; developer Attempt 1 is claimed below.

## Objective

Emit authoritative placed, paid and cancelled Woo order events using the already accepted checkout identity and plugin publisher.

## Context

This task extends WOOCOMMERCE-007 without building a separate HTTP client or queue. Woo orders need source-of-truth hook observation and HPOS-compatible checkout-key correlation.

## Scope

- Observe authoritative Woo order placement, payment completion and cancellation using supported WooCommerce APIs and hooks.
- Retrieve the checkoutKey recorded by WOOCOMMERCE-007 from order metadata; use existing installation PHP API client and retry facility.
- Generate distinct stable event IDs per order event occurrence, and preserve them on delivery retries.
- Use the shared `/v1/woocommerce/activity` route with API-019 order event schema.

## Out of Scope

- Customer WhatsApp opt-in/consent forms, permission evidence or allowlist management.
- Recovery materialisation, scheduling, outreach, WhatsApp, AI, charging or offer selection.
- New Woo activity receipts/lineage tables, new Shared contracts or Shopify-event impersonation.
- Changes to another repository or any `docs/decisions/**/_index.md` file.
- Recovery completion, suppression or reopening, revenue attribution and refund reconciliation.

## Requirements

- Do not infer payment success from order creation or status strings alone; source events must reflect Woo evidence.
- Order ID and checkoutKey must stay tenant-scoped; never correlate by phone/address.
- Duplicate Woo hook invocation cannot create extra event identities for the same logical transition when source identity can be determined.
- API/network failure never breaks an order transition.

## Work Items

- [x] Implement narrow Woo order hook adapter, reusing existing publisher.
- [x] Add order fixture tests for HPOS, retry, placed/paid/cancelled and Woo status repetitions.
- [x] Validate order-first and checkout-first deliveries against API fixtures.

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

- `ARCH-035-API-019` — must be Complete and accepted before claiming.
- `ARCH-035-WOOCOMMERCE-007` — must be Complete and accepted before claiming.

## Enables

- `ARCH-035-BACKGROUND-002`
- `ARCH-035-SYSTEM-TEST-002`

## Acceptance Criteria

- [x] Placed, paid and cancelled order events carry matching checkoutKey and canonical orderId.
- [x] Repeated hook/retry does not create a new event for same transition.
- [x] Missing correlation is visible and not guessed from personal data.
- [x] Existing Woo checkout/order processing remains operational during Moda outage.

## Validation

- [x] PHPUnit and Woo HPOS integration tests; PHP lint/plugin build.
- [x] Real order lifecycle fixture or documented environment limitation.
- [x] Existing plugin regression suite and diff check.

## Stop Condition

After work items, acceptance criteria and required validation are satisfied, finish the Completion Report, transition the task to `review`, return it to `moda_architect`, and STOP. Do not proceed to enabled tasks.

## Implementation Notes

No new WordPress tables or custom recovery scheduler. Match hooks to actual Woo integration; avoid incorrect assumptions about Blocks event timing.

## Completion Report

### Status

Developer Self-Review Passed — Attempt 1 on 2026-10-21. The task is submitted for architect review; `completion_mode: developer`, so no completion decision is made here.

### Files Changed

Implementation branch `task/ARCH-035-WOOCOMMERCE-008`, commits `7ba87300d54e0ce91be6b243b14bba31f76a27a6` and formatting-only follow-up `c68c24a` (both pushed). The committed diff relative to `origin/main` changes exactly 11 files:

- `composer.json` — include new PHP source/test syntax checks.
- `includes/Api/ModaApiClient.php` — validate and publish checkout/order activity via the existing authenticated endpoint.
- `includes/Checkout/CheckoutActivityPublisher.php` — share enqueue/delivery/retry paths with bounded order events.
- `includes/Checkout/OrderLifecycleCapture.php` — new Woo order hook observer and HPOS-compatible persistent event identity.
- `includes/Plugin.php` — update HPOS compatibility documentation.
- `includes/Runtime.php` — register the order lifecycle observer with the existing publisher.
- `tests/OrderLifecycleCaptureTest.php` — focused PHP coverage of capture, deduplication and retry safety.
- `tests/integration/checkout-actions.test.mjs` — delivery-replay helper regression coverage.
- `tests/integration/checkout-wordpress.mjs` — integrate live order lifecycle assertions into checkout scenarios.
- `tests/integration/order-wordpress.mjs` — new isolated live placed/paid/cancelled and replay assertions.
- `tests/integration/run-wordpress.mjs` — validate bounded order payloads at the HTTPS fixture.

Git evidence: 11 files changed, 559 insertions and 17 deletions; no changed gitlink listed. Implementation checkout at `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-WOOCOMMERCE-008` is on the matching task branch, clean, with local HEAD equal to its `origin/task/ARCH-035-WOOCOMMERCE-008` ref.

### Work Completed

- Added `OrderLifecycleCapture` to observe Classic and Blocks order placement (`ORDER_PLACED`), explicit Woo payment completion (`ORDER_PAID`) and transitions into `cancelled` (`ORDER_CANCELLED`). Order placement/status alone is never treated as proof of payment.
- Preserved the WOOCOMMERCE-007 checkout key through HPOS-compatible `WC_Order` metadata. Durable per-occurrence event records retain the original `eventId` through hook repetition, enqueue failure, HTTP 503 and bounded Action Scheduler retry; a genuinely new cancellation after reopening receives a new event identity.
- Reused `/v1/woocommerce/activity`, the existing installation/site binding, Action Scheduler hook and retry path. Payloads are bounded and the plugin does not supply its own `shopId`.
- Added focused PHPUnit and live disposable WordPress integration coverage for duplicate callbacks, checkout-first/order-first delivery, guest and authenticated customers, placed/paid/cancelled events, HPOS correlation, no synchronous network calls during checkout/order transitions, and 503 retry with unchanged event identity.
- Corrected an Attempt 1 integration-harness omission by adding `deliverCapturedAction()` in the test fixture and a Node regression test. This correction changed only integration-test code; the previously tested PHP implementation remained unchanged.
- Made no database migrations, new recovery scheduler, WhatsApp/AI/billing side effects, Shared contract changes or cross-repository implementation changes.

### Validation Results

Evidence provided on 2026-10-21 (recorded tests executed in the developer's task worktree):

- Focused PHPUnit: **9 tests / 80 assertions PASS** (`OrderLifecycleCaptureTest` and `CheckoutCaptureTest`).
- Full PHPUnit regression: **130 tests / 924 assertions PASS** after running the build required by the existing admin asset tests. The first pre-build run had two unrelated asset-registration failures; the subsequent full run passed. Attempt 2's test-only helper correction did not alter PHP code.
- JavaScript unit tests: **361/361 PASS**; Node integration/helper suite: **52/52 PASS**. Focused `node --test tests/integration/checkout-actions.test.mjs`: **4/4 PASS**.
- Full disposable WordPress/WooCommerce integration: **PASS**, including `ARCH-035 Order guest: placed, payment, cancellation, replay, 503, HPOS PASS` and `ARCH-035 Order customer: placed, payment, cancellation, replay, 503, HPOS PASS`. Classic and Blocks checkout scenarios for guest/customer also passed; the fixture cleaned up temporary configuration and stopped WordPress. The integration was run again after formatting-only JS changes and returned to the shell prompt after cleanup.
- PHP syntax checks via `composer lint`: **PASS**. `npm run lint:js`: **PASS with zero errors and six pre-existing warnings** in `tests/js/billing-screen.test.js`. Production `npm run build`: **PASS** with bundle-size warnings, not build failures.
- Final committed range `git diff --check origin/main...HEAD`: **PASS**. Uncommitted diff whitespace check: **PASS**. Implementation worktree was clean and local/remote task commit equality was verified at final review commit `c68c24af1d4908ec8eb8c287ce9f760b87119429`.
- Review-time canonical checks confirmed the parent and implementation worktrees are dedicated, correctly mapped to `task/ARCH-035-WOOCOMMERCE-008`, clean after publication, and synchronized with their respective origin task refs. No gitlink or other-repository changes were made.

### Deviations

None from the authorised capture-only scope. An integration-fixture helper was omitted in the initial implementation and added in the second implementation patch; the final full WordPress run passed. Prior asset-loading failures were resolved by the required build before rerunning PHPUnit.

### Assumptions

- Canonical route and worktree isolation were verified during developer review; the task branches are the dedicated launcher-resolved parent and implementation worktrees.
- `ARCH-035-API-019` and `ARCH-035-WOOCOMMERCE-007` were both Complete at the recorded developer claim. The API owns validation and shop resolution; this task does not implement that hosted contract.

### Unresolved Issues

No outstanding implementation or test failure identified for ARCH-035-WOOCOMMERCE-008. The existing note about `ARCH-040-DATABASE-006` remains out of scope; no schema changes are inferred or introduced. Architect review and, after acceptance, explicit developer completion remain workflow actions, not missing feature work.

### Architectural Concerns

Capture-only is not permanent event archiving. Completed BullMQ jobs can expire; future recovery enablement must consider that captured past events may be unavailable. No recovery, consent, outreach, messaging or billing behaviour is authorised by this task.

## Architect Review

### Review Status

Pending.

### Review Notes

Scope reopened from Superseded only for the 20 October 2026 WooCommerce checkout/order capture exception. Historical supersession remains in Git. No architectural acceptance of implementation is implied.

### Reviewed Files

Pending architect review.

### Validation Reviewed

Pending architect review.

### Architecture Conformance

Pending architect review.

### Follow-up

None.

## Developer Execution Ownership Amendment

The developer invoked `/moda_developer_create ARCH-035-WOOCOMMERCE-008` for this ready agent-owned task, explicitly taking over implementation execution. `execution_mode` and `completion_mode` are now `developer`; `assigned_agent: moda_woocommerce`, repository ownership, task scope and dependencies are unchanged.

- Previous execution mode: `agent`
- Previous completion mode: `automatic`
- New execution mode: `developer`
- New completion mode: `developer`
- Amendment date: 2026-10-21

## Developer Claim — Attempt 1

**Claimed — 2026-10-21T15:40:53Z.** The developer invoked `/moda_developer_create ARCH-035-WOOCOMMERCE-008` from the canonical `ready` state. The task transitioned to `in_progress`, Attempt 1, `executor: developer`; `assigned_agent: moda_woocommerce` remains the logical owner.

- Dependency gate: `ARCH-035-API-019` and `ARCH-035-WOOCOMMERCE-007` both resolve `complete` through the canonical launcher.
- Parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-WOOCOMMERCE-008`, branch `task/ARCH-035-WOOCOMMERCE-008`, clean before claim and fast-forwarded from current `origin/main` to `88cc0a830518b3c07fbb143a7850ff91870412e3`. The branch's upstream was corrected from `origin/main` to `origin/task/ARCH-035-WOOCOMMERCE-008`; the task branch already matched its remote before mainline synchronization.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-WOOCOMMERCE-008`, branch `task/ARCH-035-WOOCOMMERCE-008`, created at `1a402a30c6d5fae0c9ccba898db5c5bd0da99015` from refreshed `origin/main`. No local or remote implementation task branch existed before preparation; this canonical branch will be published with the claim.
- Both worktrees were clean and correctly mapped before the task record was updated. No implementation changes have been made by this claim.
- Required validation remains: PHPUnit and Woo HPOS integration tests, PHP lint/plugin build, a real order lifecycle fixture or documented environment limitation, existing plugin regressions, and `git diff --check`.

## Developer Self-Review Passed — Attempt 1

- Review result: Passed on 2026-10-21. Scope, implementation, acceptance criteria and required validation were checked against the committed implementation; all Work Items and Acceptance Criteria remain evidenced as checked above.
- Implementation branch: `task/ARCH-035-WOOCOMMERCE-008`, final review commit `c68c24a` pushed; no pending implementation changes. Formatting follow-up was limited to the four task-owned JS integration/helper files and makes the declared JS lint pass.
- Validation: focused PHPUnit 9 tests/80 assertions; full PHPUnit 130 tests/924 assertions; JS 361/361 plus Node 52/52; full disposable WordPress/WooCommerce guest and customer lifecycle scenarios; `composer lint`; `npm run lint:js` (zero errors, six existing warnings); `npm run build`; and `git diff --check` all pass.
- Worktree evidence: canonical parent `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-035-WOOCOMMERCE-008` and implementation `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-035-WOOCOMMERCE-008` are the launcher-resolved dedicated worktrees, both on `task/ARCH-035-WOOCOMMERCE-008` and clean/synchronized with origin after publication.
- Lifecycle: `status: review`, `executor: null`, `claimed_at: null`, `attempt: 1` (unchanged). `completion_mode: developer`; explicit completion remains pending after architect review. No branch was merged to `main`, and no enabled task was started.

## Developer Completion Decision — Attempt 1

- Decision: Complete, explicitly authorized by the developer on 2026-10-21 after the durable Attempt 1 passing self-review.
- Completion checks: all Work Items and Acceptance Criteria are checked; implementation commits `7ba87300d54e0ce91be6b243b14bba31f76a27a6` and `c68c24af1d4908ec8eb8c287ce9f760b87119429` are pushed; the validation and review evidence above is accepted.
- Lifecycle: `status: complete`, `executor: null`, `claimed_at: null`, `attempt: 1` (unchanged). No branch was merged to `main`.
- Dependency frontier: `ARCH-035-BACKGROUND-002` is `ready` after confirming both declared dependencies (`ARCH-035-API-019` and this task) are complete; its canonical parent worktree was materialized from `origin/main` and its task record was updated on `task/ARCH-035-BACKGROUND-002`. Its implementation worktree is deferred until execution preparation. `ARCH-035-SYSTEM-TEST-002` remains pending under its manual gate and other incomplete prerequisites; it was not started.
