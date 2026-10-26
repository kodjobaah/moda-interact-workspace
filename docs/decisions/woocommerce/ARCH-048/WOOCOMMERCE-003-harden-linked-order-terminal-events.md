---
id: ARCH-048-WOOCOMMERCE-003
architecture_id: ARCH-048
title: Harden checkout-linked Woo paid and cancellation event coverage
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: review
priority: 26
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-035-WOOCOMMERCE-008
- ARCH-035-API-019
enables:
- ARCH-048-BACKGROUND-003
- ARCH-048-SYSTEM-TEST-001
created: '2026-10-23'
updated: '2026-10-26'
---

# ARCH-048-WOOCOMMERCE-003 — Harden checkout-linked Woo paid and cancellation event coverage

## Architecture

Architecture ID: `ARCH-048`

Architecture document: `docs/architecture/ARCH-048-woocommerce-checkout-recovery-pipeline.md`

Coordinator: `moda_architect`

Developer Attempt 1 is submitted for architectural review. The implementation was committed and pushed as `30360d3` on `moda-interact-woocommerce` branch `task/ARCH-048-WOOCOMMERCE-003` (per the developer terminal log). The existing Developer Execution Ownership Amendment below records the task claim, separate worktrees, and start-of-attempt synchronisation. Architect acceptance and the subsequent explicit developer completion decision remain outstanding.

## Objective

Ensure every confirmed checkout-linked order placement, paid transition and cancellation observed by the plugin is reliably published using existing event kinds.

## Context

`OrderLifecycleCapture` attaches `_moda_checkout_key` and currently observes order-processed, `woocommerce_payment_complete` and status change (cancellation) hooks. Some gateways can transition to a paid Woo order state without exercising the specific payment-complete hook. A missed event remains possible even after bounded Action Scheduler retries.

## Scope

- Audit HPOS-compatible status transitions and cover confirmed paid statuses through appropriate WooCommerce-supported hooks without inventing payment when merely placed/on-hold/failed.
- Keep exact `_moda_checkout_key` correlation for Classic and Blocks; no phone/email order matching and no new order identifiers.
- Retain distinct `ORDER_PLACED`, `ORDER_PAID` and `ORDER_CANCELLED` kinds, stable eventId and deduplicated Action Scheduler retry payloads.
- Avoid silently losing known terminal events on transport exhaustion: provide bounded non-PII failure evidence and safe retry/replay handling within existing publisher facilities.
- Handle duplicate payment callbacks, cancellation repeats, and changed status after cancellation without falsely reversing an observed paid outcome.

## Out of Scope

- No new provider status-polling endpoint, local guest-session verification, new Woo database table, unbounded retry loop, new API route or third-party customer-data exposure.

## Requirements

- Do not equate order placement with payment. A placed unpaid order suppresses abandoned-checkout reminders by default, pending any separately approved unpaid-order policy.
- Use existing outbound event contract and Woo order metadata; idempotency and at-least-once transport assumptions remain explicit.
- Exhausted retries are visible operational failures, not evidence that Moda learned the paid outcome.

## Work Items

- [x] Implement paid-state status-transition coverage using Woo order APIs and PHP lifecycle fixtures.
- [x] Extend fixture coverage for HPOS-compatible Woo APIs, Classic/Blocks linkage and gateway placed→paid→cancelled/failed/refunded branches.
- [x] Test duplicate callbacks, bounded retry exhaustion and explicit replay retaining the original event ID and checkout correlation.

## Interfaces / Contracts

- Existing `ORDER_PLACED`, `ORDER_PAID`, `ORDER_CANCELLED` payload shape and POST `/v1/woocommerce/activity`; consumer is ARCH-048-BACKGROUND-002.
- The source of truth for payment is the Woo order lifecycle, but Moda is aware only of authenticated events successfully delivered.

## Dependencies

- `ARCH-035-WOOCOMMERCE-008`
- `ARCH-035-API-019`

## Enables

- `ARCH-048-BACKGROUND-003`
- `ARCH-048-SYSTEM-TEST-001`

## Acceptance Criteria

- [x] Confirmed paid or cancelled Woo status transitions with `_moda_checkout_key` produce the existing bounded event even without a gateway `payment_complete` hook (fixture-verified).
- [x] No unproven `ORDER_PAID` signal, duplicate terminal action, unscoped order linkage or merchant WordPress checkout-reading route was introduced (source and fixture-verified).
- [x] Bounded retry exhaustion produces explicit Action Scheduler failure and privacy-safe diagnostics rather than being counted as successful delivery (fixture-verified).

## Validation

- [x] Woo PHPUnit/HPOS-compatible order-API, Classic/Blocks and gateway/status-transition fixtures: developer `npm run test:php` — **187 tests, 1,413 assertions, 0 failures** (PHP 8.5.11); this is fixture coverage, not a live WordPress HPOS end-to-end run.
- [x] Action Scheduler/API contract fixtures, focused checkout regressions and whitespace verification: PHP suite includes retry/exhaustion/replay tests; focused Node checkout regressions **11/11 passed** in the patch-authoring environment; patch-authoring `git diff --check` passed. No final `git diff --check` command from the developer's implementation worktree is captured in the terminal log.

## Stop Condition

After only this task's work, criteria and required validation, complete the Completion Report with the launcher-resolved dedicated parent and implementation worktree paths, isolation, start-of-attempt synchronisation and repository revision evidence. Change to `review`, return to `moda_architect` and **STOP**. Do not start dependent work. Superseded tasks must not be claimed.

## Implementation Notes

- Do not promise detection of a completely lost event; ARCH-048 explicitly acknowledges that limitation without provider lookup.

- Use `/moda-task` preparation with the real developer workspace before code execution. Do not treat the snapshot as a Git branch; do not edit any `docs/decisions/**/_index.md` during this architecture session. Validate actual repository scripts rather than guessing commands. Respect assigned repository and task-document ownership.

## Completion Report

### Status

Ready for Review — Developer Attempt 1. The implementation branch was committed and pushed. The parent task/report update must be committed and pushed separately. **Not architect-accepted and not developer-completed.**

### Files Changed

Implementation repository `moda-interact-woocommerce` (commit `30360d3`):

- `includes/Checkout/CheckoutActivityPublisher.php`
- `includes/Checkout/OrderLifecycleCapture.php`
- `tests/OrderLifecycleCaptureTest.php`
- `tests/integration/order-wordpress.mjs`

Parent workspace: this task definition and Completion Report only. No architecture, domain `_index.md`, or implementation gitlink modifications are included in the documentation patch.

### Work Completed

- Added status-transition observation for confirmed paid orders, complementing `woocommerce_payment_complete`. Woo's `wc_get_is_paid_statuses()`/`WC_Order::is_paid()` semantics are used with guards excluding known unpaid and terminal statuses; order placement alone does not assert payment.
- Preserved `_moda_checkout_key` linkage and the existing `ORDER_PLACED`, `ORDER_PAID` and `ORDER_CANCELLED` API event kinds, with stable event IDs and duplicate-callback suppression.
- Preserved actionable cancellation evidence when enqueue fails, and handled repeat cancellation callbacks safely.
- Ensured terminal delivery failures fail the Action Scheduler action with bounded diagnostic fields; explicit replay is constrained to a failed order action and the original installation/site identity, reusing its original payload and event ID.
- Added PHP lifecycle, duplicate-callback, retry/failure and replay fixtures, plus Node integration fixture coverage.
- Developer committed and pushed `30360d3` (`feat(arc-048-woocomerce-003)`) to `origin/task/ARCH-048-WOOCOMMERCE-003` in `moda-interact-woocommerce`, per the terminal log dated 26 October 2026.

### Validation Results

- **Developer environment:** `npm ci` succeeded; `npm run build` succeeded, including the twenty-language i18n source/translation verification (553 source messages, 19 translation packs). Webpack emitted three bundle/performance warnings, not errors.
- **Developer environment:** `npm run test:php` / `composer test` **passed all 187 tests and 1,413 assertions**, using PHP 8.5.11. The earlier two asset-enqueue fixture failures did not recur after building the Admin assets.
- **Patch-authoring environment:** focused PHP fixture runner **16/16 passed**; focused Node checkout regression tests **11/11 passed**; PHP/JS syntax checks and implementation diff whitespace validation passed.
- **Developer Git evidence:** `git commit` created `30360d3` (four files; 361 insertions, 31 deletions). Push output confirms `fe0c9de..30360d3` to `origin/task/ARCH-048-WOOCOMMERCE-003` in the WooCommerce repository. The untracked `typescript` terminal-log file was not included in that commit.
- **Task-start evidence:** the pre-existing Developer Execution Ownership Amendment below records the dedicated parent and implementation worktree locations, initial Git revisions, dependency checks, and `origin --prune` synchronization. The uploaded ZIP is not a substitute for independently inspecting the launcher's execution packet or current Git worktree registrations.
- **Not validated here:** live WordPress HPOS/Blocks with real payment gateways and Action Scheduler delivery/replay; full cross-service API/background system testing; a final implementation-worktree `git diff --check` after developer commit. These are not claimed as passing.
- **Non-blocking diagnostics:** `npm ci` reported 36 dependency advisories (3 low, 21 moderate, 10 high, 2 critical) and peer-dependency/install-script warnings. No dependency upgrades are included in this task; any security remediation needs separate review.

### Deviations

- An external, bounded Attempt 1 implementation patch was applied by the developer rather than authored entirely through the repository-specific agent. The task was explicitly taken over via `/moda_developer_create`, with `execution_mode: developer` and `completion_mode: developer`; original implementation ownership remains `moda_woocommerce`.
- The parent report patch is provided for application/commit/push in the dedicated parent worktree; no parent push, implementation merge or `main` update is claimed by this report.

### Assumptions

- The 26 October 2026 developer log and uploaded worktree snapshot represent the task's submission evidence. The reviewer must inspect the pushed implementation commit and authoritative task branch.
- Woo lifecycle tests use order-API fixtures rather than proving behaviour on a running HPOS/Blocks store.
- The existing `/v1/woocommerce/activity` API contract and prerequisite implementations remain unchanged.

### Unresolved Issues

- The reviewing architect should verify the recorded launcher worktree isolation and start-of-attempt synchronisation evidence, including recursive implementation-submodule preparation where applicable. The appendix documents the initial claim and concrete worktree revisions; no independent Git worktree inspection was possible from the archive.
- End-to-end HPOS/Blocks, Action Scheduler and cross-service delivery behaviour remains for live/integrated validation; determine whether specific pre-acceptance evidence or `ARCH-048-SYSTEM-TEST-001` should cover it.
- The parent `task/ARCH-048-WOOCOMMERCE-003` branch must receive this task report commit and push before review; preserve the developer-completion gate after architect acceptance.

### Architectural Concerns

- Transport retries and explicit replay do not guarantee recovery of an event that was never captured or enqueued locally. No new provider read endpoint was introduced for this case.
- The replay capability is an internal publisher mechanism, not a new public route. Authorised operational invocation should be checked during integrated validation.

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

## Developer Execution Ownership Amendment (Attempt 1)

- Invocation: `/moda_developer_create ARCH-048-WOOCOMMERCE-003` explicitly requested developer execution. `assigned_agent: moda_woocommerce` is unchanged; execution and completion modes are now `developer`.
- Claim: `status: in_progress`, `executor: developer`, `claimed_at: 2026-10-26T14:25:27Z`, `attempt: 1`.
- Dependency verification: `ARCH-035-WOOCOMMERCE-008` and `ARCH-035-API-019` both resolved `complete` before claim.
- Parent worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-048-WOOCOMMERCE-003`, branch `task/ARCH-048-WOOCOMMERCE-003`, clean at start revision `2624d6445e6d642568d521d18f3e277ea629950e`.
- Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-048-WOOCOMMERCE-003`, branch `task/ARCH-048-WOOCOMMERCE-003`, clean at start revision `fe0c9de7446082e276b589fc58756ea1ac9fb03a`.
- Synchronization: fetched `origin --prune` in both task worktrees. No remote task branch existed at preparation; both task branches start at current `origin/main`, which is an ancestor of each worktree HEAD. At preparation, no implementation changes had been made in this attempt.
