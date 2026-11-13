---
id: ARCH-053-WOOCOMMERCE-009
architecture_id: ARCH-053
title: Correct cart restoration test hook dispatch
task_kind: implementation
domain: woocommerce
repository: moda-interact-woocommerce
assigned_agent: moda_woocommerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 10
executor: codex
claimed_at: 2026-11-13T15:17:25Z
attempt: 1
depends_on:
  - ARCH-053-WOOCOMMERCE-006
  - ARCH-053-WOOCOMMERCE-008
enables: []
created: 2026-11-13
updated: 2026-11-13
---

# Correct cart restoration test hook dispatch

## Architecture

ARCH-053; docs/architecture/ARCH-053-woocommerce-checkout-recovery-links-and-cart-restoration.md; coordinator moda_architect.

## Objective

Make cart-restoration test doubles exercise and remove the actual canonical WordPress hook registry used by the test bootstrap.

## Context

User explicitly requests testing and fixing remaining changes before integration. All12 primary Woo follow-up edits already match accepted main; no duplicate feature implementation is needed. Independent exact-main verification initially found two plugin asset failures attributable to not-yet-built ignored output and one coupon test fixture failure. RestoreTestCart::apply_coupon reads legacy arch053/arch046 registries instead of tests/bootstrap.php's moda_interact_test_filters. Conditional remove_filter also ignores the canonical registry. Root requires post-build baseline confirmation before execution; generated-asset absence must not become a product source patch.

## Scope

The tests/CheckoutCartRestorerTest.php fake cart/filter cleanup and directly necessary regression assertions, using the unchanged canonical tests/bootstrap.php contract. A genuinely required bootstrap-only test helper correction may be included with explicit evidence; production PHP/JS remains unchanged.

## Out of Scope

Already merged follow-up UI/contracts, product coupon behavior changes, new hook framework, generated build artifact commits, credentials/live calls, package/schema changes or main integration.

## Requirements

- Confirm current-main baseline after declared production asset build. Show the remaining specific coupon failure and inspect canonical bootstrap registry semantics before editing. If no failure/coverage gap remains, report that fact instead of manufacturing churn.
- Fake apply_coupon must dispatch the same active registered callbacks as the bootstrap and preserve hook priority/arguments/order where the test contract requires them. Do not simply add another registry that leaves conflicting cleanup semantics.
- remove_filter must remove callbacks from that same canonical storage and not clear unrelated callback registrations. Preserve unrelated error notices and all existing coupon conflict/restore assertions.
- Add meaningful behavior proof that the restoration-owned coupon-error suppression exists only while installed and is absent after normal/exception cleanup. Do not weaken assertions, bypass production callbacks or fake the expected result directly.
- Production source is not authorized. If actual product behavior is defective rather than the fixture, return precise evidence to moda_architect before expanding scope.
- Use a fresh normal launcher-prepared dedicated task worktree from accepted main. Preserve root's full backup, primary local changes and newer main behavior. No unrelated source adoption.

## Work Items

- [x] Confirm built exact-main remaining failure and canonical hook semantics.
- [x] Correct only the fixture/cleanup behavior and regression assertions.
- [x] Run required checks, publish source/report and return review.

## Interfaces / Contracts

Existing WordPress filter semantics and tests/bootstrap.php canonical registry. ARCH053WOOCOMMERCE006/008 production behavior remains accepted authority. No new cross-repository contract or Shared release.

## Dependencies

ARCH-053-WOOCOMMERCE-006, ARCH-053-WOOCOMMERCE-008 (both Complete/Accepted).

## Enables

None

## Acceptance Criteria

- [x] Canonical hook dispatch and selective cleanup execute actual production callback behavior.
- [x] Normal/exception cleanup and unrelated notices/callbacks remain covered without product changes.
- [x] Required full verification passes with actual built asset prerequisites; exact isolation/sync/source/report evidence is recorded and primary/backup preserved.

## Validation

- [x] Focused red/green cart/coupon fixture and cleanup tests, full declared PHP suite and PHP lint.
- [x] Existing JS/full build checks relevant to the accepted Woo baseline; no ignored artifact commit. Any remaining failure is explained/fixed only within scope or returned to owner.
- [x] Diff/privacy and changed-file whitelist checks.

## Stop Condition

Publish matching task source and parent report branches, set review and return to moda_architect. Do not self-accept, merge/deploy, alter live stores or begin follow-on tasks.

## Implementation Notes

You are not alone; preserve others' work. Normal launcher owns canonical matching worktrees/synchronization/claim. The user authorized failed-test corrections; root owns main integration. This is a bounded fixture correction, not a duplicate implementation of local follow-up functionality already merged.

## Completion Report

### Status

Ready for Review

### Files Changed

- Implementation: tests/CheckoutCartRestorerTest.php only.
- Parent: this task file only.

### Work Completed

The fake cart dispatches the existing bootstrap's canonical moda_interact_test_filters registry; its remove_filter selectively removes only the requested callback from that same registry. Removed the inactive duplicate add_filter fallback. Test setup snapshots/restores the registry. Added actual production-restorer regressions proving normal and exceptional cleanup, unrelated callback preservation and later ordinary coupon errors remaining visible. Production PHP/JS, dependencies and bootstrap remain unchanged.

All 12 original primary local Woo follow-up edits were byte-identical to accepted origin/main 95cffb4e9f95427d02073f7bb04841ca3c2a5776 (feature merged through PR45/ad1085a383cc3254ddbf81798547b5732f4bf184). No duplicate feature port was made. Root's external backup and primary originals were preserved.

### Validation Results

- Built exact-main baseline: PHP341 tests/2581 assertions, one coupon fixture failure. The two earlier asset failures disappeared after the declared production build; no product patch for ignored asset absence.
- New focused regressions RED before fixture correction:9 tests/44 assertions/3 failures. GREEN after correction:9 tests/49 assertions.
- composer test:343 tests/2590 assertions PASS.
- composer lint and changed-file php -l:PASS.
- npm run test:js:unit:65 files/482 tests PASS; npm run test:js:node:128 PASS.
- npm run build:PASS; three existing webpack size warnings.
- Whole JS lint has309 unchanged accepted-main errors (258 Prettier,48 curly,3 other existing rules). No JS source/config/dependency changes; root/architect explicitly excluded mass formatting from this functional reconciliation. Full JS lint is not claimed green.
- git diff --check PASS. Source whitelist is one test file. Production includes/src, package manifests/locks and Vitest config compare unchanged to origin/main. No credentials, customer data or generated output added.

Validation used copied vendor dependencies and an existing identical-lock node_modules symlink in the isolated worktree; declared build regenerated ignored assets. Detailed logs are in the root-owned external backup's verification/woo009-logs directory. No live calls or Docker integration tests were needed for this test-only correction.

### Isolation and Publication

Normal launcher prepared canonical dedicated parent moda-interact-workspace-task-ARCH-053-WOOCOMMERCE-009 and implementation moda-interact-workspace.worktrees/ARCH-053-WOOCOMMERCE-009, both task/ARCH-053-WOOCOMMERCE-009. Dependency gate passed, repositories synchronized with origin/main and recursive submodules verified. Durable claim:973003c79b18def4e84d121a4a5d9fade60e78b9, attempt1/executor codex. Implementation source afb321fe164aefa026061d560cc307db984da976 is committed and pushed on the matching task branch. Parent report is published on the matching task branch. Neither main branch was merged or pushed by this agent.

### Deviations

No product changes. Existing whole-JS lint baseline remains disclosed rather than widening scope.

### Assumptions

Canonical bootstrap retains its existing callback-array ordering contract; no new hook abstraction or priority model is introduced.

### Unresolved Issues

Existing whole-JS lint baseline remains outside this fixture task. Root owns final integration and primary-checkout reconciliation.

### Architectural Concerns

None. No cross-repository contract, package publication or deployment required.

## Architect Review

### Review Status

Pending

### Review Notes

None

### Reviewed Files

None

### Validation Reviewed

None

### Architecture Conformance

Pending

### Follow-up

Root retains final integration; no live or full architecture acceptance claim.
