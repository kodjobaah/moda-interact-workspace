---
id: ARCH-066-COMMERCE-002
architecture_id: ARCH-066
title: Test initial outreach using live checkout product data
task_kind: implementation
domain: commerce
repository: moda-interact-commerce
assigned_agent: moda_commerce
coordinator: moda_architect
execution_mode: agent
completion_mode: developer
status: in_progress
priority: 50
executor: codex
claimed_at: 2026-11-09T00:11:19Z
attempt: 1
depends_on: ["ARCH-066-SHARED-005", "ARCH-066-COMMERCE-001", "ARCH-066-BACKGROUND-002", "ARCH-066-SHARED-012"]
enables: ["ARCH-066-SYSTEM-TEST-002"]
created: 2026-11-08
updated: 2026-11-09
---
# Test initial outreach using live checkout product data

## Scope and exact work
Read ARCH-066 and its two sequence diagrams. This task is definition only; implement only after dependencies complete, in canonical task worktrees. You are not alone in the codebase; preserve unrelated edits. No merchandise-specific assumptions or new per-category schema.

Own Commerce only. NEW `src/commerce/preview/initial-outreach/{contracts,service,checkout-reader,ports,presentation}.ts`; NEW authenticated route `app/api/studio/preview/initial-outreach/route.ts`; NEW `src/studio/test-conversations/initial-outreach-preview-panel.tsx`. Touch existing test-conversations screen/contracts, preview Redis store/activity, selected-shop authorization, provider adapters, package/lockfile and tests.

Expose a separate Initial outreach test purpose for genuine SUPER_ADMIN, matching current initial_outreach feature restrictions; development bypass is refused server-side. Subsequent conversation mode stays distinct. This task supports an existing same-shop CheckoutRecovery ID as the checkout source (no arbitrary JSON/synthetic checkout editor in this task). UI lists at most20 selected-shop checkouts ordered createdAt descending then id, using cursor pagination; server resolves environment and tenant, validates recovery ownership and 1..100 native-ID lines. Checkout status/attempt eligibility is shown as production-only/not evaluated, not bypassed for sending. No outreachAttempt is required or created. Missing IDs refuse with lineKey/reason; ask user to select a valid checkout, never infer IDs.

POST strict request {checkoutRecoveryId,requestId}; shop comes from existing authenticated selected-shop context, environment from server. Require existing same-origin/CSRF protections. Use existing preview reservation/idempotency/TTL/capacity/purge pattern with purpose INITIAL_OUTREACH and frozen checkout fingerprint/profile/template revisions; same requestId with different input conflicts, same input replays stored result. Re-read checkout fingerprint before publishing result; change => CHECKOUT_CHANGED refusal. Apply current preview execution policy and cancellation; record calls in tool activity. No new DB tables. Response uses existing accepted-run/poll mechanism with bounded ready/refused result, not a long untracked request.

Use Shared outreach evaluator and renderer through existing authorized read-only provider adapters. Always refresh exact checkout products/variants and current offer facts; historical checkout quantities/price shown separately. No catalogue search/substitution. Display line-level current title/options/availability/price, observation timestamps and limitations, checkout versus current merchandise totals, offer outcome, template name/locale/revision/header/parameters and final rendered initial message. Do not display customer contacts/tokens. Live mode makes real provider reads; fixture mode must be explicitly labelled and cannot be called live verification. Do not call Background service source or sending orchestration.

Read active initial-outreach template/header/media using existing read-only template configuration readers. Missing configuration refuses precisely. No conversation wrapper for outreach. Preview never creates recovery/attempt/customer/outbox rows, reserves credits, issues coupons, uploads media, registers templates or sends WhatsApp. Label admission/billing/window/Meta approval/delivery checks not evaluated. This task does not change production initial-outreach template schema.

Acceptance: Super Admin only including direct endpoint calls, cross-tenant checkout refused before provider I/O, exact live reads including NONE policy, stale/deleted/foreign variant refusal, price/offer changes, duplicate line preservation, no unrelated products, idempotency/cancel/capacity/purge, rendering parity with Background fixtures and side-effect spies. Update existing documentation and scoped UI/service tests; typecheck/lint pass.

## Completion report
Not started. Record implementation commit, scoped checks and parity evidence before completion. No production deployment or real message sending authorized.

## Normative review correction
[Outreach contract](../../../architecture/ARCH-066-initial-outreach-contract.md) is mandatory. Use evaluateInitialOutreach and shared frozen-template rendering; no duplicated algorithm or arbitrary render callback. Preserve historical/current prices and checkout-only restriction. Production ALTERNATIVE_PRODUCT_PROMOTION is explicitly refused for this initial path; preserve historical receipt parsing and conversational recommendations. Ready media only in Studio; IMAGE unavailable selects approved TEXT fallback or refuses.

## Exact HTTP and checkout mapping
Use actual Next app directory `app/`, not nonexistent src/app. Implement GET/POST `app/api/studio/preview/initial-outreach/route.ts`, GET `app/api/studio/preview/initial-outreach/[runId]/route.ts`, POST `app/api/studio/preview/initial-outreach/[runId]/cancel/route.ts`. GET collection lists checkout IDs, createdAt, currency, itemCount only, selected tenant filter and opaque nextCursor; cursor is validated createdAt/id, reject foreign/invalid cursor. POST accepts requestId UUID plus checkoutRecoveryId string only, returns202 {runId,status}; result GET returns existing bounded status plus evaluation/render projection, cancel uses existing cancellation semantics. Unknown fields reject400, unauthenticated401, non-super-admin403, absent/foreign checkout404 (no identity leak), reservation saturation429, idempotency mismatch409. Reuse existing preview same-origin protections and per-user run ownership; changing selected shop cannot read another shop's run.

Checkout reader maps CheckoutRecovery.id/shopId/platform/generation/currency/lineItems and existing trusted checkout URL source. For each raw line map productId,variantId,quantity,price->checkoutUnitPrice; lineKey line-0001 onward in persisted order; title is not an ID fallback. Use existing checkout URL trust rules and fail closed if absent/invalid. Policy and active purpose profile/instructions come from read-only current server resolvers, not posted values. Use `src/commerce/preview/{store,redis-store}.ts` for run reservation/fencing/cancel/TTL/usage; separate purpose namespace INITIAL_OUTREACH under existing preview purge coverage, no live Conversation rows. New store interface methods have in-memory and Redis implementations/tests. Freeze selected source fingerprint and profile/template revisions; repeat same requestId replays, never refetch/recharge invisibly. Before result commit re-read source fingerprint and reject CHECKOUT_CHANGED. UI remains two separate modes; no mixing initial_outreach into conversational feature composition.

## Deterministic implementation checklist
- [ ] Normative outreach input/result/reason types imported from Shared, not redefined in Commerce. Only HTTP list/start/status/cancel wrappers and storage envelope are local Zod types. Map ready evaluation to frozen approved initial-template render projection after read-only catalogue/ready-media checks.
- [ ] Tests/arch066-initial-outreach-preview.test.ts covers actual route handlers, service and UI; tests/arch066-initial-outreach-store.test.ts covers idempotency/ownerToken/purge/TTL with Redis. Status route refuses foreign admin/shop; list never includes contact details or foreign checkout cursor.
- [ ] Add panel to existing test-conversations-screen and drawer with separate purpose selection; SUPER_ADMIN server enforcement on list/start/poll/cancel, not UI hiding alone. Initial purpose cannot be mixed with conversational features and cannot run without selected checkout.
- [ ] Ready display contains snapshot quantities/prices and distinct current facts/subtotal, rendered initial message and frozen template provenance/parameters/header; refused display includes stage/reason/lineKey and expandable bounded tool activity, never raw HTTP bodies. Persist result under existing cap or refuse storage overflow; no silent truncation or force capacity increase.
- [ ] Live local adapter uses actual selected-shop credential resolver, standalone MCP mode uses existing published authorization path, fixture mode labelled simulation; all routes share same source/identity/limit checks. No attempt/credit/outbox/Meta/media writes in any mode.

## Release dependency reconciliation — 2026-11-08

SHARED-005 is Complete at accepted Attempt1, with accepted immutable `@modainteract/moda-interact-shared@5.7.0` and integrity `sha512-2/Ew2Blo83eY/LKthULJh84kHoJfq701e3RCpjPEQNXYnSai6IEQO08n4QNct1QzwWGyNxf9M2lokLlCHKyoXg==` (source `09e249c5717c8866996624f8855a7d649dfd2c43`). Use this exact artifact and canonical consumer contract; never guess/latest/ranges. Remaining explicit blockers: ARCH-066-COMMERCE-001 and ARCH-066-BACKGROUND-002. Status Pending, unchanged Attempt0/unclaimed. No implementation, deployment or task claim is started by reconciliation.

## Corrected publication / readiness handoff — 2026-11-08
All explicit prerequisites Complete: Shared005/012, Commerce001 canonical remote181bd35f at Attempt3, Background002 AcceptedAttempt2 explicitly completed. Ready at unchanged Attempt0/unclaimed; execution/completion developer retained. Use `/moda_developer_create ARCH-066-COMMERCE-002` when ready; no execution occurs here.
Current corrected consumer pin is exactly @modainteract/moda-interact-shared5.9.0, integritysha512-mGjw3KY2iLCGXGS5K7ZjHrsHM6mbooi5Qmcl08zXWlZxLjaL38HY74EUGqMdT79VPGQ1EBsKNnfH9RTI+hY1GA==, superseding historical0055.7pin. Complete012explicitly added as correction publication prerequisite. Existing initial-outreach contract requires strict preparedBrand five same-shop savedcolumns/nulls and fixed authorized READY logo/squareLogo/coverImage media slots; IMAGE/CHECKOUT_PRODUCT header independent, no genericname/rawURL fallback. Reuse recorded Background002 full same-input frozen body/parameters/provenance fixture for independently reviewed Studio parity. No source copy from service/internalShared imports, real send/media mutation or implicit acceptance. Preserve checkout-led/isolated synthetic preview boundaries and real same-shop checkout outreach; system tests remain terminal/manual-gated.

## Execution ownership amendment — 2026-11-09
Developer explicitly invoked agent implementation via moda-task and authorized synchronization plus claim/source/report publication. Current canonical task is ReadyAttempt0/unclaimed and clean, all explicit prerequisites Complete per published handoff; no existing implementation edits to discard. Agent execution authorized, developer completion retained. Exact5.9.0 pin/current strict brand-media contract and original HTTP/owner/Redis/UI/no-side-effect acceptance remain governing. No production provider/model/customer/Meta mutation, deployment/activation, main or follow-on work authorized; configured read-only validation fixtures and local testports only. Canonical prepare owns new worktrees/claim, no manual attempt increment here.
