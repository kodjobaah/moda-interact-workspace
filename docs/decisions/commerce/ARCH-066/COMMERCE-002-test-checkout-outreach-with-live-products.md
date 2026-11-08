---
id: ARCH-066-COMMERCE-002
architecture_id: ARCH-066
title: Test initial outreach using live checkout product data
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: developer
completion_mode: developer
status: pending
priority: 50
executor: null
claimed_at: null
attempt: 0
depends_on: ["ARCH-066-COMMERCE-001", "ARCH-066-BACKGROUND-002"]
enables: ["ARCH-066-SYSTEM-TEST-002"]
created: 2026-11-08
updated: 2026-11-08
---
# Test initial outreach using live checkout product data

## Scope and exact work
Read ARCH-066 and its two sequence diagrams. This task is definition only; implement only after dependencies complete, in canonical task worktrees. You are not alone in the codebase; preserve unrelated edits. No merchandise-specific assumptions or new per-category schema.

Own Commerce only. NEW `src/commerce/preview/initial-outreach/{contracts,service,checkout-reader,ports,presentation}.ts`; NEW authenticated route `src/app/api/studio/initial-outreach-preview/route.ts`; NEW `src/studio/test-conversations/initial-outreach-preview-panel.tsx`. Touch existing test-conversations screen/contracts, preview Redis store/activity, selected-shop authorization, provider adapters, package/lockfile and tests.

Expose a separate Initial outreach test purpose for genuine SUPER_ADMIN, matching current initial_outreach feature restrictions; development bypass is refused server-side. Subsequent conversation mode stays distinct. This task supports an existing same-shop CheckoutRecovery ID as the checkout source (no arbitrary JSON/synthetic checkout editor in this task). UI lists at most20 selected-shop checkouts ordered createdAt descending then id, using cursor pagination; server resolves environment and tenant, validates recovery ownership and 1..100 native-ID lines. Checkout status/attempt eligibility is shown as production-only/not evaluated, not bypassed for sending. No outreachAttempt is required or created. Missing IDs refuse with lineKey/reason; ask user to select a valid checkout, never infer IDs.

POST strict request {checkoutRecoveryId,requestId}; shop comes from existing authenticated selected-shop context, environment from server. Require existing same-origin/CSRF protections. Use existing preview reservation/idempotency/TTL/capacity/purge pattern with purpose INITIAL_OUTREACH and frozen checkout fingerprint/profile/template revisions; same requestId with different input conflicts, same input replays stored result. Re-read checkout fingerprint before publishing result; change => CHECKOUT_CHANGED refusal. Apply current preview execution policy and cancellation; record calls in tool activity. No new DB tables. Response uses existing accepted-run/poll mechanism with bounded ready/refused result, not a long untracked request.

Use Shared outreach evaluator and renderer through existing authorized read-only provider adapters. Always refresh exact checkout products/variants and current offer facts; historical checkout quantities/price shown separately. No catalogue search/substitution. Display line-level current title/options/availability/price, observation timestamps and limitations, checkout versus current merchandise totals, offer outcome, template name/locale/revision/header/parameters and final rendered initial message. Do not display customer contacts/tokens. Live mode makes real provider reads; fixture mode must be explicitly labelled and cannot be called live verification. Do not call Background service source or sending orchestration.

Read active initial-outreach template/header/media using existing read-only template configuration readers. Missing configuration refuses precisely. No conversation wrapper for outreach. Preview never creates recovery/attempt/customer/outbox rows, reserves credits, issues coupons, uploads media, registers templates or sends WhatsApp. Label admission/billing/window/Meta approval/delivery checks not evaluated. This task does not change production initial-outreach template schema.

Acceptance: Super Admin only including direct endpoint calls, cross-tenant checkout refused before provider I/O, exact live reads including NONE policy, stale/deleted/foreign variant refusal, price/offer changes, duplicate line preservation, no unrelated products, idempotency/cancel/capacity/purge, rendering parity with Background fixtures and side-effect spies. Update existing documentation and scoped UI/service tests; typecheck/lint pass.

## Completion report
Not started. Record implementation commit, scoped checks and parity evidence before completion. No production deployment or real message sending authorized.
