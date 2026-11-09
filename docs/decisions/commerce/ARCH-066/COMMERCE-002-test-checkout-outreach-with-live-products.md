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
status: blocked
priority: 50
executor: null
claimed_at: null
attempt: 1
depends_on: ["ARCH-066-SHARED-005", "ARCH-066-COMMERCE-001", "ARCH-066-BACKGROUND-002", "ARCH-066-SHARED-012", "ARCH-066-SHARED-014", "ARCH-066-ADMIN-001"]
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
### Status
Blocked — partial source/route/UI/service/storage foundation published; genuine runtime composition unavailable pending canonical public configured-sender projection.
### Files changed / implemented foundation
- Exact public Shared5.9.0 package/lock pin, requested integrity verified in lock.
- New initial-outreach contracts/checkout-reader/ports/presentation/service. Shared normative input/result/render types and evaluator/frozen renderer imported from public subpath; no copied evaluation/render algorithm.
- Actual list/start/status/cancel Next route handlers and HTTP/runtime modules, explicit Origin enforcement on both POSTs, genuine Super Admin/bypass denial and current selected-shop authorization. Strict body only requestIdUUID+checkoutRecoveryId; query shopId is an untrusted selector resolved server-side.
- In-memory and Redis existing coordinator extensions with distinct INITIAL_OUTREACH run kind and shared slots/quotas/idempotency/owner fencing. Physical Redis records use existing managed toolTests inventory so existing Admin purge enumeration does not orphan records; no new Admin edits.
- Separate Initial outreach UI mode/panel, same-shop keyed state reset, full typed result and final body/provenance/parameters display, explicit Simulation and NOT_EVALUATED labels. Ordinary conversation bundle loader rejects server-marked purpose composition, including mixed initial+ordinary selection; initial feature removed from conversational feature choices.
### Validation actually executed
- `node node_modules/vitest/vitest.mjs run tests/feature-preview-composition.test.ts tests/arch066-initial-outreach-preview.test.ts tests/arch066-initial-outreach-store.test.ts tests/arch066-initial-outreach-ui.test.tsx`: PASS4files25tests, zero skips/failures. Actual handlers test401/403 including bypass, same-origin rejection, selected-shop denial, strict request202/409; reader cursor/native IDs/lineKey/refingerprint; injected service both-provider NONE2reads and duplicate preservation, full frozen body/parity facts, source-change refusal. Real disposable local Redis2client replay/conflict/quota/cancel flag/stale-owner/lease TTL/inventory tests ran (not skipped), cleanup completed.
- `node node_modules/vitest/vitest.mjs run tests/arch066-initial-outreach-ui.test.tsx tests/test-conversations-screen.test.tsx tests/preview-store.test.ts tests/preview-redis-lua.test.ts`: PASS4files49tests; old conversational/store regressions preserved.
- Final keyed-shop panel rerun: PASS1file2tests after actual lint correction (no synchronous state reset in effect).
- `node node_modules/typescript/bin/tsc --noEmit -p tsconfig.build.json`: final PASSexit0, logempty.
- Focused ESLint on all new initial-outreach runtime/route/UI source: final PASSexit0/logempty. Full repository lint not claimed.
- `git diff --check`: PASS. Published dependency install and Prisma generation succeeded; existing npm audit35 dependency issues noted, no unrelated remediation.
- All Node checks used exact canonical bootstrap-resolved runtime; no live provider/model/Meta/database environment validation performed.
### Parity evidence and limits
Test-only frozen inputs reproduce Background source0a601031 `tests/unit/services/recovery-template-integration/arch066-production-none.test.ts`: both platforms, duplicate pair quantities2+1, historical12.50/current12.00GBP, subtotal36.00, saved brand and approved no-offer projection. Actual Shared evaluation/render via injected Studio service yields full exact body `Saved Merchant saved 2 × Live shirt (Blue) and 1 × Live shirt (Blue) for Test customer. Continue https://shop.example/checkout` and expected provenance fields. No Background runtime imports. This is deterministic same-input fixture evidence, NOT real provider validation, independently executed Background production test, or complete parameters/header/media parity acceptance.
### Architectural blocker / unresolved implementation
Default `getInitialOutreachPreviewService` deliberately returns503 CONFIGURATION/SENDER_UNAVAILABLE. There is NO production outreach host factory yet: real active profile/policy/instruction/model resolution, credential-backed local/MCP tool integration, trusted sender/catalogue/template selection, approved ready media/saved-brand projection composition and full template revision handling remain UNIMPLEMENTED. Test injection is explicit Simulation; it is not a live fallback.

Exact blocker: currently configured WABA exists only in secret `messaging.sender`. Admin `src/lib/admin/platform-configuration/secrets-contracts.ts` declares secret payload accessToken,phoneNumberId,businessAccountId. Background service decrypts the whole sealed payload with canonical AAD before returning identity; Commerce existing configuration allowlist has no public sender projection. WABA cannot be inferred from saved template variants. Architect explicitly prohibited new Commerce sending-credential decrypt access, and is defining Shared013/014 contract/publication plus Admin001 atomic public-projection writer with source-version fencing. No correction task implementation or unapproved correction branch publication performed here.

Other required acceptance remains pending: complete genuine host composition and template/media parity; full actual provider-adapter side-effect-spy matrix; UI/route positive production readiness; comprehensive cancel/deadline terminal lifecycle, result-overflow paths and exact Admin purge execution; all stale/deleted/foreign/price/offer/native bound matrices. Existing store tests prove cancel flag/owner fencing/TTL only, not complete service cancellation acceptance. Historical test title implying cancellation was corrected. No task checklist marked complete merely for foundation tests.
### Safety / deviations
Blocked partial implementation retained rather than infer sender from assignment, decrypt unrelated secrets, add arbitrary renderer callback, fabricate production identity, claim sending eligibility or invoke real provider/model calls. No recovery/attempt/customer/credit/outbox/template/media mutations added. No live setup/migration, Meta upload/register/send, activation, deployment, package release or follow-on task execution.
### Git / VCS
Task branch task/ARCH-066-COMMERCE-002 in both repositories.
Canonical workspace /Users/kwadwoadomafriyie/project/moda-interact-workspace.
Parent worktree /Users/kwadwoadomafriyie/project/moda-interact-workspace-task-ARCH-066-COMMERCE-002; implementation worktree /Users/kwadwoadomafriyie/project/moda-interact-workspace.worktrees/ARCH-066-COMMERCE-002. No shared/default checkout or another task path mutated.
Launcher Attempt1 claim48855cc8dfbbab31a4636bf952bd94413be23e4b pushed2026-11-09T00:11:19Z; dependencies passed. Parent reused/implementation created; remote task fast-forward not-needed, origin/main already-current both. Recursive sync/update passed, database039778a4a472db7d09e6b077bb8c8d7c82a58129 ready.
Implementation078f67a2187ba4701e2fbbf49fa2185837ae9bf7 committed/pushed and remote hash verified. Parent report commit follows this edit on same task branch. No gitlink staged/main merge. Completion mode developer preserved; no Accepted/Complete claim.


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


## Architect Review
### Review Status
Blocked
### Review Notes
Reviewed actual implementation078f67a2187ba4701e2fbbf49fa2185837ae9bf7 and reporte6e2a911f. Physical task isolation/preparation packet conforms. Source is clean and remotely published. Current production runtime explicitly throws503 CONFIGURATION/SENDER_UNAVAILABLE; the positive host is injected SIMULATION, so the feature does not yet satisfy live preview acceptance. Do not grant Commerce sender-secret decryption or infer configured WABA from template assignment. Independently inspected Admin secret-service transaction198–238, sealed/disabled discriminator and numeric4..32 sender validator.
### Reviewed Files
lib/preview/initial-outreach-runtime.ts; initial-outreach-http.ts; actual collection/status/cancel routes; src/commerce/preview/initial-outreach/{service,contracts,ports,presentation,checkout-reader}.ts; preview store/Redis changes; tests/arch066-initial-outreach-preview.test.ts; separate UI and frozen fixture.
### Validation Reviewed
Focused4files25PASS; existing conversation/store4files49PASS; keyedUI2PASS. Real local Redis2client tests executed without skips. Final TypeScript and scoped ESLint exit0; no full repository lint or live provider verification claimed. Independently verified implementation remote hash and clean state. Exact Shared5.9.0 pinned; fixture both-platform NONE two reads/full frozen body/current versus historical facts preserved. Cancellation test title corrected: only source-change is proven there.
### Architecture Conformance
Partial repository-owned foundation conforms; required end-to-end capability remains absent. No Accepted/Complete disposition. Status Blocked at unchanged Attempt1, claim cleared; completion authority remains developer. Correction dependencies added, SYSTEM-TEST002 remains gated. Checkout-led withdrawals and concurrent task statuses preserved.
### Follow-up
SHARED013 strict public configured-sender schema → SHARED014 exact publication → ADMIN001 atomic projection writer/current-active source-version fence. Definitions are materialized and locally committed only; new correction-branch publication rejected by automatic approval review and awaits explicit authorization. No implementation of correction tasks began. After prerequisites Complete, return this SAME Commerce task to Ready for rework: consume published projection without secret values; complete production profile/policy/template/ready-media/local and isolated-MCP provider composition, tool activity and all original missing live/refusal/offer/price/side-effect matrices; prove complete cancellation/deadline/overflow/purge behavior. Never waive original unchecked criteria because dependency contracts exist.


## Correction definition publication reconciliation — 2026-11-09
Developer explicitly authorized publishing the three prepared definition branches after the earlier automatic approval rejection. Normal pushes succeeded and exact remote hashes verified: SHARED013201f3922e06c59a3387e78b509821a562a9f4b25 (ReadyAttempt0/unclaimed), SHARED014af5e4bc6afa25fdc3d92147e2054f8e26a8e9c23 (PendingAttempt0/unclaimed), ADMIN00190e6bb38d7677a9f691ef0e85960921a9b362a05 (PendingAttempt0/unclaimed). Historical local-only/publication-blocked notes above are superseded only as to definition availability. No implementation worktree/claim/release/follow-on started. Commerce002 remains BlockedAttempt1, claim cleared; all outstanding live and lifecycle acceptance remains required. Next authorized execution entrypoint is /moda-task ARCH-066-SHARED-013.
