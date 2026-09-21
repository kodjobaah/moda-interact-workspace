---
id: ARCH-020-COMMERCE-015
architecture_id: ARCH-020
title: Provide trusted basket and product policy adapters
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: automatic
status: review
priority: 95
executor: copilot
claimed_at: 2026-09-21T01:13:16Z
attempt: 1
depends_on:
  - ARCH-020-COMMERCE-001
  - ARCH-020-DATABASE-001
  - ARCH-020-SHARED-001
enables:
  - ARCH-020-COMMERCE-012
  - ARCH-020-COMMERCE-007
  - ARCH-020-COMMERCE-013
  - ARCH-020-COMMERCE-016
  - ARCH-020-SYSTEM-TEST-001
created: 2026-09-21
updated: 2026-09-21
---

# Provide trusted basket and product policy adapters

## Architecture

ARCH-020. [Parent architecture](../../../architecture/ARCH-020-commerce-agent-studio-mcp-capabilities.md).
Binding [implementation contracts](../../../architecture/ARCH-020-implementation-contracts.md):
C4/C5/C7/C8/C9/C14/C16/C18 as applicable, and exact ownership/interfaces in **C19**.

## Objective

Own recovery.getBasket and shopify.searchProducts reusable policy operations and current variant facts for evaluation/recommendations.

## Context

This is the canonical narrowed definition from the 2026-09-21 task split, replacing
the former combined scope. No prior attempt or implementation is discarded. Normal
launcher/worktree/review policies apply. No task is claimed by this definition.

## Scope

Own recovery.getBasket and shopify.searchProducts reusable policy operations and current variant facts for evaluation/recommendations.

## Out of Scope

Other C19 owners' modules; new Shared wire versions or database schema; live
deployment/provider calls; unrelated refactors; cart/order writes or WhatsApp sends.
Do not implement missing dependencies or substitute production fixtures to finish.

## Requirements

Use accepted auth/Shared/database source, canonical types and C19 ports. Preserve
others' changes. Exact business names remain database-authored. Fixtures are injected
only by tests; production missing adapters fail closed. Each case below has an
expected side effect, not just a screenshot/typecheck. C19 assigns final wiring.

## Work Items

- [ ] Normalize accepted CheckoutRecovery.lineItems into C4 basket; every supported source shape has an explicit fixture, unknown/missing source remains unknown, never a fabricated basket.
- [ ] Implement bounded current product/variant search, decimal maximumPrice, availability/market/currency and safe shop URLs using privileged installation credentials only in these policy adapters.
- [ ] Bind opaque cursors to shop/query/expiry; cap20 variants/page,3 pages and common12-request/deadline budget. Deny wrong-shop IDs before provider I/O.
- [ ] Expose C19 ProductFactsPort.readVariants for exact proposal variants/collection membership; carry explicit unknowns/completeness for016/007. Never calculate discounts.
- [ ] Export operation descriptors with executable adapters and test request construction.013 registers them through014; no bespoke MCP endpoints or public-query compiler.

## Interfaces / Contracts

Own `src/commerce/products/`. Shared basket/product schemas are canonical; C19 ProductFactsPort supplies trusted current data to016/007.005 owns tokenless generic queries; no duplicated compiler or token lifecycle.


## Dependencies

- ARCH-020-COMMERCE-001
- ARCH-020-DATABASE-001
- ARCH-020-SHARED-001

All listed prerequisites must be Complete and architect-accepted before a claim.
Use dedicated launcher worktrees and accepted source; do not launch enabled work.

## Enables

- ARCH-020-COMMERCE-012
- ARCH-020-COMMERCE-007
- ARCH-020-COMMERCE-013
- ARCH-020-COMMERCE-016
- ARCH-020-SYSTEM-TEST-001

## Acceptance Criteria

- [ ] B01: each recovery snapshot source shape maps to strict Shared basket; zero lines/unknown prices are not live or free-basket facts.
- [ ] B02: search filters unavailable/unknown/market/currency cases and preserves decimal prices; cursors reject tampering/cross-shop/expiry.
- [ ] B03: exact variant/collection fact reads distinguish complete from partial results, including missing variant and provider failures; output is stable by variantId.
- [ ] B04: tenant checks, throttle/timeout/cancel and nested request ceiling have measured call counts; no provider mutation or credential leakage.

## Validation

Implement the named cases above as focused tests. Record case -> fixture -> command
-> expected/actual effects in the Completion Report. Check shared contract examples
where applicable; include malformed and denied inputs with zero side effects.
Run focused tests while developing, then typecheck/lint/build once before submission;
repeat broader checks only for new failures or changed concerns. Use actual repository
commands and record them. Local browser/component evidence is task-owned where a UI
is in scope. Follow agent-validation/live-validation policies; separate pending
required developer database/container evidence and never claim fixture tests prove
live service behavior. No minimum screenshot/test count substitutes for coverage.

## Stop Condition

After scoped work and agent-owned checks, update this task's execution/report fields, publish task-owned mirrored branches and return to review. Record exact pending developer validation where applicable. Stop; do not begin enabled tasks or mark your own task Complete. Publication tasks stop after release mechanics. System tests require explicit developer invocation even after becoming Ready.

## Implementation Notes

Normal execution uses /moda-task and scripts/start-agent-task.py preparation, dedicated parent and implementation worktrees, synchronization and recursive submodule initialisation. Follow docs/agent-vcs-ownership-policy.md, docs/agent-worktree-isolation-policy.md and docs/task-definition-materialization.md. The main-only exception applies to this review draft, not task execution. The COMMERCE route is registered in this packet; consume the accepted COMMERCE-001 foundation.

## Completion Report

### Status

Ready for Review.

### Files Changed

- `moda-interact-commerce/src/commerce/products/index.ts`: trusted recovery basket normalization, bounded Shopify product search, HMAC-bound cursors, ProductFactsPort, policy descriptors and fail-closed injected provider/authorization boundaries.
- `moda-interact-commerce/tests/products-policy.test.ts`: deterministic fixtures for supported/malformed baskets, authorization/recovery/provider failures, filtering, cursor tenant binding, variant completeness, bounds and cancellation.

### Work Completed

- Implemented `recovery.getBasket` and `shopify.searchProducts` adapters using the canonical Shared Commerce schemas and `commerce.v1` result union.
- Normalized supported array and `{lineItems}` recovery snapshots; omitted source fields remain explicit `unknownFields`, zero-line snapshots return `NOT_FOUND`, and no discount arithmetic or basket mutation is performed.
- Added bounded read-only provider requests: 20 variants/request, 3 search pages, shared injected request budget, deadline/cancellation checks, 103 unique variant IDs, 1000 collection IDs/variant, decimal maximum-price filtering, availability/market/currency filtering and HTTPS verified-shop URLs.
- Added cursor integrity/expiry/tenant/query binding and stable variant ordering/completeness results.
- Added immutable descriptors for the two owned C19 policy operations; production construction requires injected adapters and never installs fixtures.

### Validation Results

Agent-executed validation:

| Requirement | Fixture / expected side effect | Command | Result |
|---|---|---|---|
| B01 basket source normalization | Array and `{lineItems}` shapes; omitted facts stay unknown; zero lines are not free | `npm test -- tests/products-policy.test.ts` | **7 passed** |
| B02 product filtering and cursor safety | Decimal price, availability, currency, verified URL, cross-shop/tampered cursor | `npm test -- tests/products-policy.test.ts` | **7 passed** |
| B03 current variant facts | Missing variant, stable `variantId` ordering, explicit completeness/collection bounds | `npm test -- tests/products-policy.test.ts` | **7 passed** |
| B04 tenant/auth/bounds/fail closed | Denied/throwing auth, recovery/provider errors, cancellation, 20/3/12/103 bounds and zero provider calls on invalid input | `npm test -- tests/products-policy.test.ts` | **7 passed** |
| Repository lint and whitespace | Scoped source/test lint and patch whitespace | `npm run lint`; `git diff --check` | **Passed** |
| Production compilation | Prisma generation and Next production build | `npm run build` | **Passed** |
| Full Commerce tests | Existing repository regression suite | `npm test` | **98 passed, 2 pre-existing failures** in `auth-development-identity.test.ts` from `Prisma.sql is not a function` |
| TypeScript diagnostics | Full declared typecheck | `npm run typecheck` | **Blocked by the same pre-existing Prisma client baseline**: 5 errors in `lib/auth/development-platform-admin.ts` and `lib/server/connections.ts`; no Commerce-015 diagnostics remain |

Developer validation required:

- Live Shopify/provider validation against a configured development shop, installation credential and current API response remains pending. Fixtures prove deterministic policy behavior only and do not claim live execution.
- Developer-owned database/container/readiness and system validation remains pending where required by the repository workflow; this task introduced no schema or migration change.

### Deviations

Task definition authored on local main by explicit developer request. Normal execution policy remains unchanged.

### Assumptions

Use the parent architecture and actual accepted dependency revisions. Return contradictory source facts to moda_architect.

### Unresolved Issues

Commerce repository/submodule provisioning is complete; consume the accepted
COMMERCE-001 foundation. No additional provisioning prerequisite is introduced.

### Architectural Concerns

None newly reported.

### Git / VCS

Expected execution branch: `task/ARCH-020-COMMERCE-015`. Attempt: 1. Implementation worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-020-COMMERCE-015`; parent task worktree: `/Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-020-COMMERCE-015`. Both branches are mirrored and will be committed/pushed for review. The nested database submodule pin is unchanged. No parent service gitlink, main branch, Architect Review text or enabled task was modified.

## Architect Review

### Review Status

Pending.

### Review Notes

No implementation submitted. This task is a reviewable definition.

### Reviewed Files

None for implementation review.

### Validation Reviewed

None for implementation review.

### Architecture Conformance

Awaiting implementation.

### Follow-up

Reconcile task/index/frontier after review; preserve the terminal/manual system-test gate.
