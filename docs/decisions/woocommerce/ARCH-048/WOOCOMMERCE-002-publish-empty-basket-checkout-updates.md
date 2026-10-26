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
status: ready
priority: 25
executor: null
claimed_at: null
attempt: 1
depends_on:
- ARCH-035-WOOCOMMERCE-007
- ARCH-035-API-008
enables:
- ARCH-048-BACKGROUND-003
- ARCH-048-SYSTEM-TEST-001
created: '2026-10-23'
updated: '2026-10-26'
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

- [ ] Cover Classic and Blocks empty/refill transitions and cart changes after checkout starts.
- [ ] Add 51+ item, invalid snapshot, unchanged empty and transport retry/idempotency cases.
- [ ] Verify actual Woo hooks and existing API payload validator integration.

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

- [ ] Genuine empty basket publishes `items: []`, once per meaningful transition, and no unexpected recovery is scheduled from a vanished/oversized snapshot.
- [ ] Empty-to-refilled checkout creates a newer ordinary event; Woo and Moda existing checkout identity remain consistent.
- [ ] Existing valid checkout/order publisher and 20-locale UI behaviour are unchanged; no HTTP endpoint is introduced.

## Validation

- [ ] Focused PHPUnit/plugin Classic/Blocks/cart mutation and Action Scheduler retry tests.
- [ ] API event-parser fixture validation for empty vs absent items, plugin declared lint/build scripts and `git diff --check`.

## Stop Condition

After only this task's work, criteria and required validation, complete the Completion Report with the launcher-resolved dedicated parent and implementation worktree paths, isolation, start-of-attempt synchronisation and repository revision evidence. Change to `review`, return to `moda_architect` and **STOP**. Do not start dependent work. Superseded tasks must not be claimed.

## Implementation Notes

- Do not write UI or session restoration functionality as a side effect.
- Security boundary: all new behaviour is outbound Woo → existing Moda API only.

- Use `/moda-task` preparation with the real developer workspace before code execution. Do not treat the snapshot as a Git branch; do not edit any `docs/decisions/**/_index.md` during this architecture session. Validate actual repository scripts rather than guessing commands. Respect assigned repository and task-document ownership.

## Completion Report

### Status

Changes Requested — Developer Self-Review of Attempt 1. Dependencies ARCH-035-WOOCOMMERCE-007 and ARCH-035-API-008 are confirmed complete. Canonical parent worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-048-WOOCOMMERCE-002` was synchronized from `origin/main` at `2624d6445e6d642568d521d18f3e277ea629950e`; canonical implementation worktree `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-048-WOOCOMMERCE-002` was synchronized from `origin/main` at `fe0c9de7446082e276b589fc58756ea1ac9fb03a`, with recursive submodules verified. Attempt 1 implementation is published at `e021a17292c8e1f193cddaf443ebeaadb8e10174` on `origin/task/ARCH-048-WOOCOMMERCE-002`. The task is returned to `ready`; the next developer-create invocation claims Attempt 2.

### Files Changed

- `includes/Checkout/CheckoutActivityPublisher.php`
- `includes/Checkout/CheckoutCapture.php`
- `includes/Checkout/CheckoutSnapshot.php`
- `tests/CheckoutCaptureTest.php`

### Work Completed

Published checkout capture changes to represent an observed keyed checkout becoming empty as `items: []`, preserve its checkout key on refill, ignore repeated no-op empty observations, register Classic and Store API hooks, and format `occurredAt` with millisecond UTC precision. A follow-up cleanup commit removed an unrelated `typescript` artifact from the implementation task branch.

### Validation Results

Start-of-attempt route, branch, worktree and recursive submodule synchronization checks passed.

- **PASS** — `vendor/bin/phpunit tests/CheckoutCaptureTest.php`: 12 tests, 109 assertions.
- **PASS** — `composer test`: 187 tests, 1,414 assertions.
- **PASS** — `composer lint`: all declared PHP syntax checks passed.
- **PASS** — `git diff --check origin/main...HEAD` and direct `php -l` on all four changed PHP files.
- **PASS** — API owner command `npm run test:arch035-woo-activity:unit`: 21 tests, including empty `items: []`, optional/absent items, and the 51-item limit.
- **UNVERIFIED** — `npm run test:integration:wordpress` was started, but the captured terminal output did not provide a reliable final result; do not treat it as passing.
- **NOT RUN** — `npm run test:integration:wordpress -- --checkout-only` requires explicit confirmation that the existing wp-env site is disposable. No such confirmation was available, so the potentially destructive checkout integration mode was not enabled.

### Deviations

- The implementation's PHPUnit tests assert hook registration and invoke the capture methods directly; they do not prove that actual Woo Classic and Store API requests trigger the clear/refill hooks.
- No real WordPress clear/refill integration evidence was captured during this review cycle.

### Assumptions

The latest uploaded workspace ZIP is a source snapshot, not necessarily the developer's latest task branches. The developer reports `ARCH-046-BACKGROUND-004` complete after the ZIP; verify its accepted implementation for consumer integration, without reopening it.

### Unresolved Issues

The API-008 parser accepts explicit empty `items` and preserves absent items as unknown; its focused contract suite passed. No new cross-repository contract gap was identified.

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

Attempt remains 1. No Attempt 2 claim is created by this review. The next `/moda_developer_create ARCH-048-WOOCOMMERCE-002` invocation may claim Attempt 2 after the developer decides to continue.
